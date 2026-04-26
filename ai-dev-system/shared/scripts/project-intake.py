#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    ".turbo",
    ".cache",
    "tmp",
    "logs",
}


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def list_top_dirs(project_root: Path) -> list[dict[str, str]]:
    rows = []
    for item in sorted(project_root.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_dir() or item.name in IGNORE_DIRS or item.name.startswith("."):
            continue
        purpose = infer_dir_purpose(item.name)
        rows.append({"name": item.name, "purpose": purpose})
    return rows[:20]


def infer_dir_purpose(name: str) -> str:
    n = name.lower()
    mapping = {
        "src": "main source code",
        "app": "application entry or app-router code",
        "apps": "multi-app workspace",
        "packages": "shared packages or monorepo modules",
        "libs": "shared libraries",
        "lib": "shared helpers or utility modules",
        "components": "UI components",
        "features": "feature-oriented modules",
        "server": "backend or server runtime code",
        "api": "API handlers or endpoint modules",
        "db": "database layer",
        "prisma": "database schema and migrations",
        "migrations": "database migrations",
        "tests": "test suites",
        "test": "test suites",
        "e2e": "end-to-end tests",
        "docs": "project documentation",
        "scripts": "automation scripts",
        "infra": "infrastructure or deployment config",
        "docker": "containerization assets",
        "config": "configuration files",
        "public": "static assets",
        "assets": "project assets",
    }
    return mapping.get(n, "project-specific area")


def detect_stacks_and_frameworks(project_root: Path) -> tuple[list[str], list[str], dict[str, str]]:
    stacks: set[str] = set()
    frameworks: set[str] = set()
    manifests: dict[str, str] = {}

    package_json = project_root / "package.json"
    if package_json.exists():
        manifests["package.json"] = "Node.js package manifest"
        pkg = read_json(package_json)
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        stacks.update({"javascript", "typescript"} if (project_root / "tsconfig.json").exists() else {"javascript"})
        if "next" in deps:
            frameworks.add("nextjs")
        if "react" in deps:
            frameworks.add("react")
        if "vue" in deps or "nuxt" in deps:
            frameworks.add("vue")
        if "@angular/core" in deps:
            frameworks.add("angular")
        if "@nestjs/core" in deps:
            frameworks.add("nestjs")
        if "@playwright/test" in deps or "playwright" in deps:
            frameworks.add("playwright")
        if "vite" in deps:
            frameworks.add("vite")
    if (project_root / "tsconfig.json").exists():
        manifests["tsconfig.json"] = "TypeScript config"
        stacks.add("typescript")
    if (project_root / "pyproject.toml").exists():
        manifests["pyproject.toml"] = "Python project manifest"
        stacks.add("python")
        text = (project_root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        if "fastapi" in text:
            frameworks.add("fastapi")
        if "django" in text:
            frameworks.add("django")
        if "pytest" in text:
            frameworks.add("pytest")
    if (project_root / "requirements.txt").exists():
        manifests["requirements.txt"] = "Python requirements"
        stacks.add("python")
        text = (project_root / "requirements.txt").read_text(encoding="utf-8", errors="ignore").lower()
        if "fastapi" in text:
            frameworks.add("fastapi")
        if "django" in text:
            frameworks.add("django")
    if (project_root / "go.mod").exists():
        manifests["go.mod"] = "Go module"
        stacks.add("go")
    if (project_root / "Cargo.toml").exists():
        manifests["Cargo.toml"] = "Rust crate manifest"
        stacks.add("rust")
    if (project_root / "pom.xml").exists() or (project_root / "build.gradle").exists():
        manifests["pom.xml" if (project_root / "pom.xml").exists() else "build.gradle"] = "Java build manifest"
        stacks.add("java")
    if (project_root / "Dockerfile").exists() or (project_root / "docker-compose.yml").exists() or (project_root / "compose.yml").exists():
        frameworks.add("docker")
    return sorted(stacks), sorted(frameworks), manifests


def detect_commands(project_root: Path) -> dict[str, str]:
    commands: dict[str, str] = {}
    package_json = project_root / "package.json"
    if package_json.exists():
        scripts = read_json(package_json).get("scripts", {})
        for key in ["dev", "build", "test", "lint", "typecheck", "start", "preview"]:
            if key in scripts:
                commands[key] = f"npm run {key}"
    if not commands and (project_root / "Makefile").exists():
        text = (project_root / "Makefile").read_text(encoding="utf-8", errors="ignore")
        for key in ["dev", "build", "test", "lint"]:
            if re.search(rf"^{re.escape(key)}\s*:", text, re.MULTILINE):
                commands[key] = f"make {key}"
    if "test" not in commands and ((project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists()):
        commands["test"] = "pytest"
    if "lint" not in commands and (project_root / "pyproject.toml").exists():
        text = (project_root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        if "ruff" in text:
            commands["lint"] = "ruff check ."
    return commands


def find_entry_points(project_root: Path) -> list[str]:
    candidates = [
        "src/main.ts",
        "src/main.py",
        "src/index.ts",
        "src/index.js",
        "src/app.ts",
        "src/app.py",
        "app/main.py",
        "app/page.tsx",
        "pages/index.tsx",
        "main.go",
        "manage.py",
        "server.js",
        "server.ts",
    ]
    found = [c for c in candidates if (project_root / c).exists()]
    if (project_root / "src").exists() and not found:
        found.append("src/")
    return found[:8]


def infer_naming_style(project_root: Path) -> str:
    names: list[str] = []
    for path in project_root.rglob("*"):
        if len(names) >= 200:
            break
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            names.append(path.name)
    counts = Counter()
    for name in names:
        stem = name.split(".")[0]
        if "-" in stem:
            counts["kebab-case"] += 1
        elif "_" in stem:
            counts["snake_case"] += 1
        elif stem[:1].isupper():
            counts["PascalCase"] += 1
        elif re.search(r"[a-z][A-Z]", stem):
            counts["camelCase"] += 1
    if not counts:
        return "unknown"
    return counts.most_common(1)[0][0]


def detect_project_signals(project_root: Path) -> dict[str, bool]:
    return {
        "has_codeowners": (project_root / "CODEOWNERS").exists() or (project_root / ".github" / "CODEOWNERS").exists(),
        "has_adr_dir": (project_root / "docs" / "adr").exists(),
        "has_project_docs": (project_root / "docs").exists(),
        "has_api_schema": any((project_root / name).exists() for name in ["openapi.yaml", "openapi.yml", "swagger.json"]),
        "has_domain_context": (project_root / "docs" / "project-context").exists(),
        "is_monorepo": (project_root / "packages").exists() or (project_root / "apps").exists(),
    }


def recommend_core_skills(stacks: list[str], frameworks: list[str], signals: dict[str, bool]) -> list[str]:
    rec: list[str] = ["task:codebase-onboarding", "workflow:search-first", "workflow:verify"]
    for item in frameworks:
        rec.append(f"framework:{item}")
    for item in stacks:
        rec.append(f"language:{item}")
    if signals["has_adr_dir"]:
        rec.append("task:architecture-decision-records")
    if signals["has_codeowners"]:
        rec.append("task:security-ownership-map")
    if signals["is_monorepo"] or signals["has_domain_context"]:
        rec.append("task:repo-scan-lite")
    return sorted(dict.fromkeys(rec))


def find_custom_skill_gaps(project_root: Path, signals: dict[str, bool]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if signals["has_domain_context"]:
        gaps.append({
            "name": "project-domain-rules",
            "reason": "Repo has domain documentation that can be turned into a project-local decision skill.",
        })
    if signals["has_api_schema"]:
        gaps.append({
            "name": "project-api-contracts",
            "reason": "Repo has API schema files and may benefit from project-specific API contract guidance.",
        })
    if signals["is_monorepo"]:
        gaps.append({
            "name": "workspace-navigation",
            "reason": "Monorepo structure usually benefits from a project-local workspace map and routing skill.",
        })
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        gaps.append({
            "name": "ops-runbook",
            "reason": "Project has operational scripts that can be wrapped in a project-specific runbook skill.",
        })
    return gaps


def build_project_context_routes(project_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    ctx_dir = project_root / "docs" / "project-context"
    if not ctx_dir.exists():
        return [], []
    routes = []
    source_files = []
    for path in sorted(ctx_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        stem = path.stem
        title = re.sub(r"^\d+[-_ ]*", "", stem).replace("-", " ").replace("_", " ").strip()
        keywords = ", ".join([token for token in re.split(r"[^a-z0-9]+", title.lower()) if token]) or title.lower()
        routes.append(
            {
                "file": str(path.relative_to(project_root)),
                "title": title.title(),
                "keywords": keywords,
            }
        )
        source_files.append(str(path.relative_to(project_root)))
    return routes, source_files


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def extract_frontmatter_value(text: str, key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip().strip("\"'")


def build_custom_skill_index(project_root: Path) -> dict:
    skills_dir = project_root / ".ai-dev-system" / "skills"
    items = []
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        name = extract_frontmatter_value(text, "name") or path.parent.name
        description = extract_frontmatter_value(text, "description")
        category = extract_frontmatter_value(text, "category") or "task"
        items.append(
            {
                "name": name,
                "path": str(path.relative_to(project_root)),
                "description": description or "project-local skill",
                "category": category,
            }
        )
    return {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "skills": items,
        "policy": "Use project-local skills only for repo-specific behavior not already covered by active core.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project-aware AI Dev docs and manifest.")
    parser.add_argument("--system-root", required=True)
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    system_root = Path(args.system_root).resolve()
    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    ai_dir.mkdir(parents=True, exist_ok=True)
    (ai_dir / "skills").mkdir(parents=True, exist_ok=True)

    stacks, frameworks, manifests = detect_stacks_and_frameworks(project_root)
    commands = detect_commands(project_root)
    entry_points = find_entry_points(project_root)
    top_dirs = list_top_dirs(project_root)
    naming = infer_naming_style(project_root)
    signals = detect_project_signals(project_root)
    recommended = recommend_core_skills(stacks, frameworks, signals)
    custom_gaps = find_custom_skill_gaps(project_root, signals)
    context_routes, context_source_files = build_project_context_routes(project_root)

    manifest = {
        "project_root": str(project_root),
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "stacks": stacks,
        "frameworks": frameworks,
        "manifests": manifests,
        "commands": commands,
        "entry_points": entry_points,
        "top_dirs": top_dirs,
        "naming_style": naming,
        "signals": signals,
        "recommended_core_skills": recommended,
        "custom_skill_gaps": custom_gaps,
        "project_context_routes": context_routes,
        "dedupe_policy": {
            "rule": "Prefer active core skills first. Create project-local skills only for repo-specific domain knowledge, workflows, or constraints not covered by active core.",
        },
    }
    (ai_dir / "project-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ai_dir / "custom-skill-index.json").write_text(
        json.dumps(build_custom_skill_index(project_root), indent=2), encoding="utf-8"
    )
    memory_path = ai_dir / "project-memory.json"
    if not memory_path.exists():
        memory = {
            "project_name": project_root.name,
            "last_updated": dt.datetime.now(dt.UTC).isoformat(),
            "stable_facts": {
                "stacks": stacks,
                "frameworks": frameworks,
                "entry_points": entry_points,
                "commands": commands,
                "naming_style": naming,
            },
            "current_focus": [],
            "known_risks": [],
            "preferred_commands": commands,
            "project_specific_rules": [],
            "notes": [
                "Update this file when the project gains new conventions, critical workflows, or known sharp edges."
            ],
        }
        memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")
    else:
        existing = read_json(memory_path)
        existing.setdefault("tracked_project_docs", [])
        memory_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    write_markdown(
        ai_dir / "project-profile.md",
        f"""
# Project Profile

## Stack
- Languages: {", ".join(stacks) or "unknown"}
- Frameworks/tools: {", ".join(frameworks) or "unknown"}

## Signals
- Monorepo: {"yes" if signals["is_monorepo"] else "no"}
- Project docs: {"yes" if signals["has_project_docs"] else "no"}
- ADR directory: {"yes" if signals["has_adr_dir"] else "no"}
- CODEOWNERS: {"yes" if signals["has_codeowners"] else "no"}
- API schema: {"yes" if signals["has_api_schema"] else "no"}

## Entry Points
{chr(10).join(f"- `{x}`" for x in entry_points) or "- none detected"}

## Recommended Core Skills
{chr(10).join(f"- `{x}`" for x in recommended)}

## Project-Local Rule
- Use active core first.
- Use `.ai-dev-system/skills/*/SKILL.md` only when the task is clearly project-specific and not already covered well by active core.
        """,
    )

    write_markdown(
        ai_dir / "project-commands.md",
        f"""
# Project Commands

## Recommended Commands
{chr(10).join(f"- `{k}`: `{v}`" for k, v in commands.items()) or "- no common commands detected automatically"}

## Notes
- Confirm generated commands against the actual repo scripts before using them in destructive or release workflows.
        """,
    )

    write_markdown(
        ai_dir / "project-architecture.md",
        f"""
# Project Architecture Snapshot

## Top-Level Areas
{chr(10).join(f"- `{row['name']}`: {row['purpose']}" for row in top_dirs) or "- no top-level directories detected"}

## Likely Entry Points
{chr(10).join(f"- `{x}`" for x in entry_points) or "- none detected"}

## Manifests
{chr(10).join(f"- `{k}`: {v}" for k, v in manifests.items()) or "- no common manifests detected"}
        """,
    )

    write_markdown(
        ai_dir / "project-conventions.md",
        f"""
# Project Conventions

## Naming Style
- Dominant file naming style: `{naming}`

## Working Rules
- Prefer matching existing project conventions over generic best practices when they conflict.
- Keep code, logs, commands, paths, package names, and APIs unchanged in user-facing output.
- Load only the project docs relevant to the current task.
        """,
    )

    gaps_md = "\n".join(f"- `{gap['name']}`: {gap['reason']}" for gap in custom_gaps) or "- No obvious custom skill gaps detected."
    write_markdown(
        ai_dir / "project-customizations.md",
        f"""
# Project Customizations

## Use Active Core First
- Reuse core skills before creating project-local skills.
- Create project-local skills only for repo-specific domain rules, workflows, or operational conventions.

## Suggested Custom Skill Gaps
{gaps_md}

## Dedupe Policy
- If a project-local idea overlaps an active core skill, extend the project docs first instead of creating a duplicate skill.
- Only scaffold a new custom skill when the value is mostly project-specific.
        """,
    )

    routing_lines = "\n".join(
        f"- `{row['title']}` -> read `{row['file']}` when the task mentions: {row['keywords']}"
        for row in context_routes
    ) or "- No `docs/project-context/` routing docs detected."
    source_lines = "\n".join(f"- `{path}`" for path in context_source_files) or "- No project-context files detected."
    write_markdown(
        ai_dir / "project-routing.md",
        f"""
# Project Routing Hints

## Purpose
- Use this file to decide which project docs to read first for a task.
- Prefer these docs before creating project-local duplicate skills.

## Available Project Context Docs
{source_lines}

## Routing Hints
{routing_lines}

## Working Rule
- Read the smallest useful set of docs for the current task.
- If a task maps to both domain docs and tracking/order/security docs, read both.
        """,
    )

    write_markdown(
        ai_dir / "skills" / "README.md",
        """
# Project-Local Skills

Put project-specific skills here:

- `.ai-dev-system/skills/<skill-name>/SKILL.md`

Use this layer for:

- business domain rules unique to this repo
- internal workflows and scripts
- project-specific architecture constraints
- deployment or operational runbooks unique to this repo

Do not duplicate active core skills. Reuse active core first, then extend with local docs or local skills only when needed.
        """,
    )

    print(f"Generated project-aware docs in: {ai_dir}")
    print("Files:")
    for name in [
        "project-manifest.json",
        "project-memory.json",
        "custom-skill-index.json",
        "project-profile.md",
        "project-commands.md",
        "project-architecture.md",
        "project-conventions.md",
        "project-customizations.md",
        "project-routing.md",
        "skills/README.md",
    ]:
        print(f"- {ai_dir / name}")


if __name__ == "__main__":
    main()
