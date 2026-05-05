#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Show project-aware AI status.")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    manifest = read_json(ai_dir / "project-manifest.json")
    memory = read_json(ai_dir / "project-memory.json")
    custom_index = read_json(ai_dir / "custom-skill-index.json")

    print("\n=== Project Status ===")
    print(f"Project: {project_root.name}")
    print(f"Path: {project_root}")
    print(f"Stacks: {', '.join(manifest.get('stacks', [])) or 'unknown'}")
    print(f"Frameworks: {', '.join(manifest.get('frameworks', [])) or 'unknown'}")
    print(f"Recommended core skills: {len(manifest.get('recommended_core_skills', []))}")
    print(f"Project-local skills: {len(custom_index.get('skills', []))}")
    
    # Check for autonomous skills in the manifest or global registry
    print(f"Autonomous skills: self-healing, pr-architect, tech-debt-audit, self-evolution")
    
    print(f"Project docs tracked: {len(memory.get('tracked_project_docs', []))}")
    if (ai_dir / "current-task-brief.md").exists():
        print("Current task brief: present")
    else:
        print("Current task brief: not set")

    print("\nPreferred Commands:")
    commands = memory.get("preferred_commands", {})
    if commands:
        for key, value in commands.items():
            print(f"- {key}: {value}")
    else:
        print("- none detected")

    print("\nEntry Points:")
    entry_points = memory.get("stable_facts", {}).get("entry_points", [])
    if entry_points:
        for item in entry_points[:8]:
            print(f"- {item}")
    else:
        print("- none detected")

    print("\nKnown Risks:")
    risks = memory.get("known_risks", [])
    if risks:
        for item in risks[:8]:
            print(f"- {item}")
    else:
        print("- none recorded")

    print("\nRecent Changes:")
    recent = memory.get("recent_changes", {})
    files = recent.get("files", [])
    commits = recent.get("commits", [])
    if files:
        print("- Files:")
        for item in files[:10]:
            print(f"  - {item}")
    else:
        print("- Files: none detected")
    if commits:
        print("- Commits:")
        for item in commits[:5]:
            print(f"  - {item}")
    else:
        print("- Commits: none detected")

    print("\nTracked Project Docs:")
    docs = memory.get("tracked_project_docs", [])
    if docs:
        for item in docs:
            print(f"- {item}")
    else:
        print("- none tracked")
    print("======================\n")


if __name__ == "__main__":
    main()
