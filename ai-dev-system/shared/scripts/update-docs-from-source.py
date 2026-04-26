#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def extract_env_rows(path: Path) -> list[tuple[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        rows.append((key.strip(), value.strip()))
    return rows


def find_api_source(project_root: Path) -> str:
    for name in ["openapi.yaml", "openapi.yml", "swagger.json"]:
        if (project_root / name).exists():
            return name
    return ""


def infer_api_summary(project_root: Path) -> list[str]:
    api_source = find_api_source(project_root)
    if api_source:
        return [f"Primary API schema file detected: `{api_source}`"]
    routes = []
    for rel in ["src/app/api", "pages/api", "api", "server/routes"]:
        if (project_root / rel).exists():
            routes.append(rel)
    return [f"Likely API route directory: `{x}`" for x in routes] or ["No explicit API schema detected automatically."]


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update project docs from source-of-truth files.")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    docs_dir = project_root / ".ai-dev-system"
    docs_dir.mkdir(parents=True, exist_ok=True)

    pkg = read_json(project_root / "package.json") if (project_root / "package.json").exists() else {}
    scripts = pkg.get("scripts", {})
    script_rows = "\n".join(
        f"| `npm run {name}` | {command} |" for name, command in sorted(scripts.items())
    ) or "| _none_ | _no package scripts detected_ |"

    env_path = None
    for name in [".env.example", ".env.template", ".env.sample"]:
        candidate = project_root / name
        if candidate.exists():
            env_path = candidate
            break
    env_rows = []
    if env_path:
        env_rows = extract_env_rows(env_path)
    env_table = "\n".join(
        f"| `{key}` | {'Yes' if value == '' else 'No'} | `{value or '<set value>'}` |"
        for key, value in env_rows
    ) or "| _none_ | - | - |"

    api_lines = "\n".join(f"- {line}" for line in infer_api_summary(project_root))
    infra = []
    for name in ["Dockerfile", "docker-compose.yml", "compose.yml"]:
        if (project_root / name).exists():
            infra.append(name)
    infra_lines = "\n".join(f"- `{name}`" for name in infra) or "- No Docker/compose source detected."

    write_markdown(
        docs_dir / "source-reference.md",
        f"""
# Source Reference

## Commands

| Command | Source |
|---------|--------|
{script_rows}

## Environment Variables

Source file: `{env_path.name if env_path else 'none detected'}`

| Variable | Required | Example/Default |
|----------|----------|-----------------|
{env_table}

## API

{api_lines}

## Infrastructure

{infra_lines}
        """,
    )

    write_markdown(
        docs_dir / "runbook.md",
        f"""
# Runbook

## Development
- Start from `.ai-dev-system/project-commands.md` and `.ai-dev-system/source-reference.md`
- Verify actual command behavior before using destructive or release workflows

## Deployment Inputs
{infra_lines}

## API Inputs
{api_lines}

## Environment
- Review `.ai-dev-system/source-reference.md` for tracked env variables
        """,
    )

    print(docs_dir / "source-reference.md")
    print(docs_dir / "runbook.md")


if __name__ == "__main__":
    main()
