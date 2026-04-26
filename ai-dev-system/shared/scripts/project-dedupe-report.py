#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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


def similarity_score(name: str, description: str, category: str, skill: dict) -> int:
    hay = " ".join(
        [
            skill.get("id", ""),
            skill.get("name", ""),
            skill.get("description", ""),
            skill.get("trigger", ""),
        ]
    ).lower()
    score = 0
    tokens = [
        token
        for token in re.split(r"[^a-z0-9]+", f"{name} {description}".lower())
        if len(token) >= 4 and token not in GENERIC_TOKENS
    ]
    for token in tokens:
        if token in hay:
            score += 4
        if token in skill.get("id", "").lower():
            score += 3
        if token in skill.get("name", "").lower():
            score += 5
    phrase = " ".join(tokens)
    if phrase and phrase in hay:
        score += 10
    if skill.get("category", "") == category:
        score += 12
    elif category and skill.get("category"):
        score -= 8
    if category == "task" and skill.get("category") == "role":
        score -= 10
    return score


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Report overlaps between project-local skills and active core skills.")
    parser.add_argument("--system-root", required=True)
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    system_root = Path(args.system_root).resolve()
    project_root = Path(args.project_root).resolve()
    active_path = system_root / "shared" / "registry" / "skills.json"
    custom_path = project_root / ".ai-dev-system" / "custom-skill-index.json"
    report_path = project_root / ".ai-dev-system" / "project-dedupe-report.json"

    active_skills = load_json(active_path, [])
    custom_index = load_json(custom_path, {"skills": []})
    local_skills = custom_index.get("skills", [])

    overlaps = []
    for local in local_skills:
        name = local.get("name", "")
        description = local.get("description", "")
        category = local.get("category", "task")
        scored = sorted(
            ((similarity_score(name, description, category, active), active) for active in active_skills),
            key=lambda row: (-row[0], row[1].get("id", "")),
        )
        matches = [
            {
                "id": skill.get("id", ""),
                "name": skill.get("name", ""),
                "description": skill.get("description", ""),
                "score": score,
                "path": skill.get("path", ""),
            }
            for score, skill in scored[:5]
            if score >= 14
        ]
        overlaps.append(
            {
                "name": name,
                "path": local.get("path", ""),
                "description": description,
                "category": category,
                "status": "review-overlap" if matches else "project-specific",
                "matches": matches,
            }
        )

    summary = {
        "project_root": str(project_root),
        "local_skill_count": len(local_skills),
        "overlap_count": sum(1 for item in overlaps if item["status"] == "review-overlap"),
        "items": overlaps,
        "policy": "Prefer local skills only for repo-specific behavior. Merge or delete local skills that overlap active core.",
    }
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"local_skills\t{summary['local_skill_count']}")
    print(f"overlaps\t{summary['overlap_count']}")
    for item in overlaps:
        if item["status"] != "review-overlap":
            continue
        match = item["matches"][0]
        print(f"overlap\t{item['name']}\t{match['id']}\t{match['score']}")
    print(f"report\t{report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
