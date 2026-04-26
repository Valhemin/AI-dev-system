#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


GENERIC_TOKENS = {
    "project",
    "specific",
    "rules",
    "rule",
    "domain",
    "workflow",
    "local",
    "custom",
    "guide",
    "helper",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "project-skill"


def load_active_skills(system_root: Path) -> list[dict]:
    path = system_root / "shared" / "registry" / "skills.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def extract_frontmatter_value(text: str, key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip().strip("\"'")


def refresh_custom_skill_index(project_root: Path) -> None:
    skills_dir = project_root / ".ai-dev-system" / "skills"
    items = []
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        description = extract_frontmatter_value(text, "description")
        category = extract_frontmatter_value(text, "category") or "task"
        name = extract_frontmatter_value(text, "name") or path.parent.name
        items.append(
            {
                "name": name,
                "path": str(path.relative_to(project_root)),
                "description": description or "project-local skill",
                "category": category,
            }
        )
    out = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "skills": items,
        "policy": "Use project-local skills only for repo-specific behavior not already covered by active core.",
    }
    target = project_root / ".ai-dev-system" / "custom-skill-index.json"
    target.write_text(json.dumps(out, indent=2), encoding="utf-8")


def similarity_score(name: str, category: str, skill: dict) -> int:
    skill_id = skill.get("id", "").lower()
    skill_name = skill.get("name", "").lower()
    skill_desc = skill.get("description", "").lower()
    tokens = [
        t
        for t in re.split(r"[^a-z0-9]+", name.lower())
        if len(t) >= 4 and t not in GENERIC_TOKENS
    ]
    if not tokens:
        return 0
    score = 0
    for token in tokens:
        if token in skill_id:
            score += 4
        if token in skill_name:
            score += 5
        if token in skill_desc:
            score += 1
    phrase = " ".join(tokens)
    if phrase and phrase in f"{skill_id} {skill_name}":
        score += 8
    if skill.get("category", "") == category:
        score += 10
    elif category and skill.get("category"):
        score -= 6
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a project-local skill with duplicate checks.")
    parser.add_argument("--system-root", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--category", default="task")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    system_root = Path(args.system_root).resolve()
    project_root = Path(args.project_root).resolve()
    active = load_active_skills(system_root)

    scored = sorted(
        ((similarity_score(args.name, args.category, s), s) for s in active),
        key=lambda row: (-row[0], row[1].get("id", "")),
    )
    overlaps = [s for score, s in scored if score >= 6]
    if overlaps and not args.force:
        print("Refusing to scaffold because similar active core skills already exist:")
        for item in overlaps[:5]:
            print(f"- {item.get('id')}: {item.get('description')}")
        print("Use --force if this skill is truly project-specific.")
        sys.exit(2)

    skill_dir = project_root / ".ai-dev-system" / "skills" / slug(args.name)
    skill_dir.mkdir(parents=True, exist_ok=True)
    target = skill_dir / "SKILL.md"
    target.write_text(
        f"""---
name: {slug(args.name)}
description: {args.description}
category: {args.category}
intent:
  - documentation
mode: hybrid
risk: low
source_repo: project-local
confidence: medium
---

# {args.name}

Use this project-local skill only for repo-specific behavior that is not already covered well by active core skills.

## Purpose

{args.description}

## Project Context To Read First

- `.ai-dev-system/project-profile.md`
- `.ai-dev-system/project-architecture.md`
- `.ai-dev-system/project-conventions.md`
- any repo docs directly relevant to this skill

## Trigger

- <fill in project-specific trigger>

## Workflow

1. Confirm this is repo-specific and not already covered by active core.
2. Read only the project docs relevant to the task.
3. Apply the local convention or workflow.
4. Verify against real project files and commands.

## Guardrails

- Do not duplicate active core skills.
- Keep this skill narrowly scoped to this repository.
- Update this file when project rules change.
""",
        encoding="utf-8",
    )
    refresh_custom_skill_index(project_root)
    print(target)


if __name__ == "__main__":
    main()
