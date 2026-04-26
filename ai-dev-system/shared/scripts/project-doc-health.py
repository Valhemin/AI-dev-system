#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


CORE_DOCS = [
    "project-manifest.json",
    "project-memory.json",
    "custom-skill-index.json",
    "project-profile.md",
    "project-commands.md",
    "project-architecture.md",
    "project-conventions.md",
    "project-customizations.md",
    "project-routing.md",
]

WATCH_FILES = [
    "package.json",
    "tsconfig.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    "CODEOWNERS",
]


def max_mtime(paths: list[Path]) -> float:
    values = [p.stat().st_mtime for p in paths if p.exists()]
    return max(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Check project-local AI docs health.")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    if not ai_dir.exists():
        print("Status: FAIL")
        print("- Missing `.ai-dev-system/`. Run `ai-dev install` or `ai-dev intake-project` first.")
        raise SystemExit(2)

    missing = [name for name in CORE_DOCS if not (ai_dir / name).exists()]
    doc_paths = [ai_dir / name for name in CORE_DOCS if (ai_dir / name).exists()]
    watch_paths = [project_root / name for name in WATCH_FILES if (project_root / name).exists()]
    docs_mtime = max_mtime(doc_paths)
    repo_mtime = max_mtime(watch_paths)

    custom_index = ai_dir / "custom-skill-index.json"
    custom_skill_paths = list((ai_dir / "skills").glob("*/SKILL.md")) if (ai_dir / "skills").exists() else []
    stale_custom_index = custom_index.exists() and custom_skill_paths and custom_index.stat().st_mtime < max_mtime(custom_skill_paths)
    docs_stale = bool(repo_mtime and docs_mtime and repo_mtime > docs_mtime)

    status = "PASS"
    findings: list[str] = []
    if missing:
        status = "WARN"
        findings.append("Missing docs: " + ", ".join(missing))
    if docs_stale:
        status = "WARN"
        findings.append("Project manifests/configs are newer than `.ai-dev-system` docs. Re-run `ai-dev intake-project`.")
    if stale_custom_index:
        status = "WARN"
        findings.append("`custom-skill-index.json` is older than project-local skills. Re-run `ai-dev intake-project` or scaffold again.")

    manifest_path = ai_dir / "project-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            rec = manifest.get("recommended_core_skills", [])
            findings.append(f"Recommended core skills tracked: {len(rec)}")
        except Exception:
            status = "WARN"
            findings.append("`project-manifest.json` exists but could not be parsed.")

    print(f"Status: {status}")
    if not findings:
        print("- Project-local AI docs look healthy.")
    else:
        for item in findings:
            print(f"- {item}")


if __name__ == "__main__":
    main()
