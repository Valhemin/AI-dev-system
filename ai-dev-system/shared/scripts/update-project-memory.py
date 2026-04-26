#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def git_output(project_root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""


def recent_changed_files(project_root: Path, limit: int = 20) -> list[str]:
    out = git_output(project_root, ["diff", "--name-only", "HEAD~10..HEAD"])
    items = [line.strip() for line in out.splitlines() if line.strip()]
    deduped: list[str] = []
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped[:limit]


def recent_commits(project_root: Path, limit: int = 5) -> list[str]:
    out = git_output(project_root, ["log", f"-{limit}", "--pretty=format:%h %s"])
    return [line for line in out.splitlines() if line.strip()]


def tracked_docs(project_root: Path) -> list[str]:
    docs = []
    for rel in [
        ".ai-dev-system/project-profile.md",
        ".ai-dev-system/project-commands.md",
        ".ai-dev-system/project-architecture.md",
        ".ai-dev-system/project-conventions.md",
        ".ai-dev-system/project-customizations.md",
        ".ai-dev-system/project-routing.md",
        ".ai-dev-system/current-task-brief.md",
    ]:
        if (project_root / rel).exists():
            docs.append(rel)
    return docs


def detect_known_risks(manifest: dict, project_root: Path) -> list[str]:
    risks: list[str] = []
    signals = manifest.get("signals", {})
    if signals.get("has_codeowners"):
        risks.append("CODEOWNERS exists; keep ownership drift in mind for sensitive changes.")
    if signals.get("is_monorepo"):
        risks.append("Monorepo detected; verify package boundaries and affected apps before broad edits.")
    if signals.get("has_api_schema"):
        risks.append("API schema files exist; keep code and contract docs in sync.")
    if (project_root / "Dockerfile").exists():
        risks.append("Deployment/container config present; verify build/runtime impact for backend changes.")
    return risks


def main() -> None:
    parser = argparse.ArgumentParser(description="Distill fresh repository facts into project-memory.json")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    ai_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_json(ai_dir / "project-manifest.json")
    memory_path = ai_dir / "project-memory.json"
    memory = read_json(memory_path) if memory_path.exists() else {}

    preferred_commands = manifest.get("commands", {})
    stable_facts = memory.get("stable_facts", {})
    stable_facts.update(
        {
            "stacks": manifest.get("stacks", stable_facts.get("stacks", [])),
            "frameworks": manifest.get("frameworks", stable_facts.get("frameworks", [])),
            "entry_points": manifest.get("entry_points", stable_facts.get("entry_points", [])),
            "commands": preferred_commands,
            "naming_style": manifest.get("naming_style", stable_facts.get("naming_style", "unknown")),
        }
    )

    updated = {
        "project_name": memory.get("project_name") or project_root.name,
        "last_updated": dt.datetime.now(dt.UTC).isoformat(),
        "stable_facts": stable_facts,
        "current_focus": memory.get("current_focus", []),
        "known_risks": sorted(set(memory.get("known_risks", []) + detect_known_risks(manifest, project_root))),
        "preferred_commands": preferred_commands,
        "project_specific_rules": memory.get("project_specific_rules", []),
        "notes": memory.get("notes", []),
        "recent_changes": {
            "files": recent_changed_files(project_root),
            "commits": recent_commits(project_root),
        },
        "tracked_project_docs": tracked_docs(project_root),
    }

    memory_path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    print(memory_path)


if __name__ == "__main__":
    main()
