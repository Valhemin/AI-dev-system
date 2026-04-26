#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def newest_session(sessions_dir: Path) -> Path | None:
    files = sorted(sessions_dir.glob("*-session.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume from latest project session summary.")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    sessions_dir = project_root / ".ai-dev-system" / "sessions"
    if not sessions_dir.exists():
        print("No session directory found. Save a session first.")
        raise SystemExit(2)

    latest = newest_session(sessions_dir)
    if latest is None:
        print("No saved sessions found.")
        raise SystemExit(2)

    data = json.loads(latest.read_text(encoding="utf-8"))
    print(f"SESSION LOADED: {latest}")
    print("=" * 56)
    print(f"PROJECT: {data.get('project_root')}")
    print(f"TOPIC: {data.get('topic')}")
    print("CHANGED FILES:")
    changed = data.get("changed_files", [])
    if changed:
        for item in changed:
            print(f"- {item}")
    else:
        print("- No changed files recorded")
    print("NEXT STEP:")
    print(f"- {data.get('next_step')}")


if __name__ == "__main__":
    main()
