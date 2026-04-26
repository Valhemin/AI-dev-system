#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path


def git_changed_files(project_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "status", "--short"],
            capture_output=True,
            text=True,
            check=False,
        )
        files = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            files.append(line[3:].strip())
        return files
    except Exception:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Save project session summary.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--next-step", default="Review changed files and continue from the current task context.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    sessions_dir = ai_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now(dt.UTC)
    stamp = now.strftime("%Y-%m-%d-%H%M%S")
    changed = git_changed_files(project_root)
    session = {
        "saved_at": now.isoformat(),
        "project_root": str(project_root),
        "topic": args.topic,
        "changed_files": changed,
        "next_step": args.next_step,
    }
    json_path = sessions_dir / f"{stamp}-session.json"
    md_path = sessions_dir / f"{stamp}-session.md"
    json_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    md_path.write_text(
        (
            f"# Session {stamp}\n\n"
            f"- Topic: {args.topic}\n"
            f"- Saved at: {now.isoformat()}\n"
            f"- Project: `{project_root}`\n\n"
            "## Changed Files\n"
            + ("\n".join(f"- `{x}`" for x in changed) if changed else "- No changed files detected")
            + f"\n\n## Exact Next Step\n- {args.next_step}\n"
        ),
        encoding="utf-8",
    )
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
