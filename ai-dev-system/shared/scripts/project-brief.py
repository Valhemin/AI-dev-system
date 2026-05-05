#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


GENERIC_TOKENS = {
    "project",
    "specific",
    "rules",
    "rule",
    "workflow",
    "custom",
    "local",
    "system",
    "feature",
    "task",
}

BUNDLE_RULES = [
    ("project-aware-core", ["workflow:task-briefing", "task:codebase-onboarding", "task:repo-scan-lite"]),
    ("implementation-core", ["task:feature-dev", "task:bug-fix", "task:refactor"]),
    ("quality-suite", ["task:accessibility", "task:code-review", "task:e2e-testing", "task:testing", "workflow:quality-gate", "role:reviewer"]),
    ("architecture-and-adr", ["task:architecture", "task:architecture-decision-records", "role:architect"]),
    ("performance-and-debug", ["problem:performance-debug", "workflow:debug", "role:debugger", "role:performance-optimizer"]),
    ("docs-and-handoff", ["task:documentation", "workflow:working-memory", "role:documentation-writer"]),
    ("mobile-delivery", ["framework:react-native", "role:mobile-developer"]),
    ("team-orchestration", ["workflow:parallel-agents", "role:orchestrator", "role:project-planner"]),
]


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def load_registry_module(system_root: Path):
    path = system_root / "shared" / "scripts" / "ai-dev-registry.py"
    spec = importlib.util.spec_from_file_location("ai_dev_registry", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def similarity_score(text: str, name: str, description: str) -> int:
    hay = f"{name} {description}".lower()
    tokens = [
        token
        for token in re.split(r"[^a-z0-9]+", text.lower())
        if len(token) >= 4 and token not in GENERIC_TOKENS
    ]
    score = 0
    for token in tokens:
        if token in hay:
            score += 5
    phrase = " ".join(tokens)
    if phrase and phrase in hay:
        score += 8
    return score


def classify_complexity(task: str) -> str:
    q = task.lower()
    if any(word in q for word in ["delete production", "drop database", "rotate secret", "incident", "rollback", "payment", "auth", "security", "migration"]):
        return "critical"
    if any(word in q for word in ["architecture", "refactor", "deploy", "performance", "checkout", "contract", "multi", "orchestrate", "monorepo"]):
        return "complex"
    if any(word in q for word in ["bug", "fix", "review", "test", "docs", "implement"]):
        return "moderate"
    return "simple"


def recommend_docs(manifest: dict, task: str) -> list[str]:
    docs = [
        ".ai-dev-system/project-routing.md",
        ".ai-dev-system/project-profile.md",
        ".ai-dev-system/project-memory.json",
    ]
    q = task.lower()
    for route in manifest.get("project_context_routes", []):
        hay = f"{route.get('title', '')} {route.get('keywords', '')}".lower()
        if any(token in hay for token in re.split(r"[^a-z0-9]+", q) if len(token) >= 4):
            docs.append(route.get("file", ""))
    if any(word in q for word in ["command", "run", "dev server", "build", "test", "lint"]):
        docs.append(".ai-dev-system/project-commands.md")
    if any(word in q for word in ["architecture", "system", "flow", "design", "module"]):
        docs.append(".ai-dev-system/project-architecture.md")
    if any(word in q for word in ["style", "convention", "naming", "format"]):
        docs.append(".ai-dev-system/project-conventions.md")
    return [doc for i, doc in enumerate(docs) if doc and doc not in docs[:i]][:8]


def recommend_local_skills(custom_index: dict, task: str) -> list[dict]:
    scored = []
    for skill in custom_index.get("skills", []):
        score = similarity_score(task, skill.get("name", ""), skill.get("description", ""))
        if score > 0:
            scored.append((score, skill))
    scored.sort(key=lambda row: (-row[0], row[1].get("name", "")))
    return [{"score": score, **skill} for score, skill in scored[:3] if score >= 8]


def top_scored(skills: list[dict], registry, task: str, category: str, limit: int = 1) -> list[dict]:
    scored = []
    for skill in skills:
        if skill.get("category") != category:
            continue
        score = registry.score_skill_for_query(skill, task)
        if score > 0:
            scored.append({"score": score, **skill})
    scored.sort(key=lambda item: (-int(item["score"]), item["id"]))
    return scored[:limit]


def find_skill(skills: list[dict], skill_id: str) -> dict | None:
    return next((skill for skill in skills if skill.get("id") == skill_id), None)


def infer_task_ids(task: str) -> list[str]:
    q = task.lower()
    picks = []
    if any(word in q for word in ["fix", "error", "fail", "broken", "healing"]):
        picks.append("autonomous:self-healing")
    if any(word in q for word in ["pr", "pull request", "commit", "changelog"]):
        picks.append("autonomous:pr-architect")
    if any(word in q for word in ["audit", "smell", "solid", "debt"]):
        picks.append("autonomous:tech-debt-audit")
    if any(word in q for word in ["mcp", "model context protocol", "mcp server"]):
        picks.append("anthropic:mcp-server-gen")
    if any(word in q for word in ["excel", "csv", "dataset", "data analysis", "pandas"]):
        picks.append("anthropic:complex-data-analysis")
    if any(word in q for word in ["accessibility", "a11y", "wcag", "aria", "screen reader", "keyboard navigation"]):
        picks.append("task:accessibility")
    if any(word in q for word in ["bug", "debug", "fix", "broken", "error"]):
        picks.append("task:bug-fix")
    if any(word in q for word in ["review", "audit"]):
        picks.append("task:code-review")
    if any(word in q for word in ["e2e", "end-to-end", "playwright journey", "user journey", "critical flow"]):
        picks.append("task:e2e-testing")
    if any(word in q for word in ["test", "qa", "coverage", "playwright"]):
        picks.append("task:testing")
    if any(word in q for word in ["docs", "documentation", "readme", "runbook", "handoff"]):
        picks.append("task:documentation")
    if any(word in q for word in ["refactor", "cleanup", "simplify"]):
        picks.append("task:refactor")
    if any(word in q for word in ["implement", "build", "create", "add feature"]):
        picks.append("task:feature-dev")
    if any(word in q for word in ["architecture", "design", "adr"]):
        picks.append("task:architecture")
    return picks[:2]


def infer_problem_id(task: str) -> str:
    q = task.lower()
    if any(word in q for word in ["auth", "token", "permission", "security"]):
        return "problem:auth-security"
    if any(word in q for word in ["database", "migration", "sql", "query", "index", "prisma"]):
        return "problem:database-debug"
    if any(word in q for word in ["api", "endpoint", "request", "response", "http", "graphql"]):
        return "problem:api-debug"
    if any(word in q for word in ["build", "compile", "bundl", "typecheck", "tsc"]):
        return "problem:build-error"
    if any(word in q for word in ["dependency", "import", "module", "circular"]):
        return "problem:dependency-debug"
    if any(word in q for word in ["performance", "slow", "memory", "latency"]):
        return "problem:performance-debug"
    if any(word in q for word in ["deploy", "production", "rollback", "docker", "ci", "release"]):
        return "problem:deployment-debug"
    if any(word in q for word in ["async", "await", "event loop", "deadlock", "thread"]):
        return "problem:async-debug"
    return ""


def infer_workflow_ids(task: str, complexity: str) -> list[str]:
    q = task.lower()
    picks = ["workflow:task-briefing"]
    if complexity in {"complex", "critical"} or any(word in q for word in ["reasoning", "think deep", "complex bug"]):
        picks.append("anthropic:advanced-reasoning-cot")
    if any(word in q for word in ["context", "token", "prune", "clean history"]):
        picks.append("context:context-pruning")
    if any(word in q for word in ["e2e", "end-to-end", "playwright", "user journey"]):
        picks.append("workflow:test")
    elif any(word in q for word in ["accessibility", "a11y", "wcag", "aria"]):
        picks.append("workflow:code-review")
    if any(word in q for word in ["build", "typecheck", "compile", "tsc", "module not found", "import error"]):
        picks.append("workflow:build-fix")
    elif any(word in q for word in ["debug", "bug", "fix", "error"]):
        picks.append("workflow:debug")
    elif any(word in q for word in ["review", "audit", "pr review"]):
        picks.append("workflow:code-review")
    elif any(word in q for word in ["test", "qa", "coverage"]):
        picks.append("workflow:test-coverage" if "coverage" in q else "workflow:test")
    elif any(word in q for word in ["deploy", "release"]):
        picks.append("workflow:deploy")
    elif any(word in q for word in ["docs", "documentation", "readme", "runbook", "guide"]):
        picks.append("workflow:update-docs")
    elif any(word in q for word in ["plan", "architecture", "design"]):
        picks.append("workflow:plan")
    if complexity in {"complex", "critical"}:
        picks.append("workflow:working-memory")
    return picks[:2]


def infer_role_ids(task: str) -> list[str]:
    q = task.lower()
    picks = []
    if any(word in q for word in ["accessibility", "a11y", "wcag", "aria", "screen reader", "keyboard"]):
        picks.append("role:a11y-architect")
    if any(word in q for word in ["e2e", "end-to-end", "playwright", "user journey", "critical flow"]):
        picks.append("role:e2e-runner")
    if any(word in q for word in ["build", "typecheck", "compile", "tsc", "import error", "module not found"]):
        picks.append("role:build-error-resolver")
    elif any(word in q for word in ["debug", "bug", "error"]):
        picks.append("role:debugger")
    if any(word in q for word in ["docs", "documentation", "readme", "runbook", "handoff"]):
        picks.append("role:doc-updater")
    if any(word in q for word in ["performance", "slow", "latency", "memory"]):
        picks.append("role:performance-optimizer")
    if any(word in q for word in ["mobile", "ios", "android", "react native", "expo", "flutter"]):
        picks.append("role:mobile-developer")
    if any(word in q for word in ["plan", "planning", "requirements", "roadmap", "architecture", "design", "adr"]):
        picks.append("role:project-planner")
    if any(word in q for word in ["architecture", "design", "adr"]):
        picks.append("role:architect")
    if any(word in q for word in ["review", "audit"]):
        picks.append("role:code-reviewer")
    if any(word in q for word in ["explore", "map codebase", "trace flow", "understand codebase", "investigate area"]):
        picks.append("role:code-explorer")
    return picks[:2]


def infer_framework_id(task: str, manifest: dict) -> str:
    q = task.lower()
    frameworks = set(manifest.get("frameworks", []))
    if "react-native" in frameworks and any(word in q for word in ["mobile", "react native", "expo"]):
        return "framework:react-native"
    if "nextjs" in frameworks and "next" in q:
        return "framework:nextjs"
    if "react" in frameworks and any(word in q for word in ["react", "component", "ui", "voucher", "checkout"]):
        return "framework:react"
    if "playwright" in frameworks and "playwright" in q:
        return "framework:playwright"
    return ""


def pick_bundles(task: str, recommended_items: list[str], manifest: dict) -> list[str]:
    chosen = []
    joined = " ".join(recommended_items)
    q = task.lower()
    for bundle, triggers in BUNDLE_RULES:
        if any(trigger in joined for trigger in triggers):
            chosen.append(bundle)
    if "react-native" in ",".join(manifest.get("frameworks", [])).lower() and "mobile-delivery" not in chosen:
        chosen.append("mobile-delivery")
    if any(word in q for word in ["readme", "docs", "runbook", "handoff", "onboarding"]) and "docs-and-handoff" not in chosen:
        chosen.append("docs-and-handoff")
    if any(word in q for word in ["performance", "slow", "latency", "memory"]) and "performance-and-debug" not in chosen:
        chosen.append("performance-and-debug")
    if any(word in q for word in ["architecture", "adr", "design"]) and "architecture-and-adr" not in chosen:
        chosen.append("architecture-and-adr")
    if any(word in q for word in ["review", "test", "qa", "verify"]) and "quality-suite" not in chosen:
        chosen.append("quality-suite")
    if any(word in q for word in ["parallel", "orchestrate", "split across roles"]) and "team-orchestration" not in chosen:
        chosen.append("team-orchestration")
    if "project-aware-core" not in chosen:
        chosen.insert(0, "project-aware-core")
    return chosen[:4]


def format_markdown(task: str, complexity: str, docs: list[str], core: list[dict], local: list[dict], roles: list[dict], workflows: list[dict], bundles: list[str], commands: dict, bundle_defs: dict) -> str:
    lines = [
        "# Current Task Brief",
        "",
        f"Task: {task}",
        f"Complexity: {complexity}",
        "",
        "## Read First",
        "",
    ]
    for doc in docs:
        lines.append(f"- {doc}")
    lines += ["", "## Recommended Core", ""]
    for item in core:
        lines.append(f"- {item['id']}: {item.get('description', item.get('trigger', ''))}")
    if local:
        lines += ["", "## Relevant Project-Local Skills", ""]
        for item in local:
            lines.append(f"- {item['name']} ({item['path']})")
    if workflows:
        lines += ["", "## Suggested Workflows", ""]
        for item in workflows:
            lines.append(f"- {item['id']}: {item.get('description', '')}")
    if roles:
        lines += ["", "## Suggested Roles", ""]
        for item in roles:
            lines.append(f"- {item['id']}: {item.get('description', '')}")
    lines += ["", "## Suggested Bundles", ""]
    for bundle in bundles:
        description = bundle_defs.get(bundle, {}).get("description", "")
        lines.append(f"- {bundle}: {description}".rstrip(": "))
    lines += ["", "## Verification", ""]
    if commands:
        for key, value in commands.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- Verify against the project's normal build/test/lint path.")
    lines += ["", "## Working Memory", ""]
    if complexity in {"complex", "critical"}:
        lines.append("- Use workflow:working-memory and keep this brief updated during execution.")
    else:
        lines.append("- No persistent task brief needed unless the scope grows.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a project-aware task brief with minimal recommended context.")
    parser.add_argument("--system-root", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args()

    system_root = Path(args.system_root).resolve()
    project_root = Path(args.project_root).resolve()
    ai_dir = project_root / ".ai-dev-system"
    manifest = read_json(ai_dir / "project-manifest.json", {})
    memory = read_json(ai_dir / "project-memory.json", {})
    custom_index = read_json(ai_dir / "custom-skill-index.json", {"skills": []})
    skills = read_json(system_root / "shared" / "registry" / "skills.json", [])
    bundle_defs = read_json(system_root / "shared" / "registry" / "bundles.json", {}).get("bundles", {})
    registry = load_registry_module(system_root)

    complexity = classify_complexity(args.task)
    docs = recommend_docs(manifest, args.task)
    role_scored = []
    for role_id in infer_role_ids(args.task):
        item = find_skill(skills, role_id)
        if item:
            role_scored.append({"score": 999, **item})
    if not role_scored:
        role_scored = top_scored(skills, registry, args.task, "role", limit=2)

    workflow_scored = []
    for workflow_id in infer_workflow_ids(args.task, complexity):
        item = find_skill(skills, workflow_id)
        if item:
            workflow_scored.append({"score": 999, **item})
    if not workflow_scored:
        workflow_scored = top_scored(skills, registry, args.task, "workflow", limit=2)

    local = recommend_local_skills(custom_index, args.task)

    core = []
    for task_id in infer_task_ids(args.task):
        item = find_skill(skills, task_id)
        if item:
            core.append({"score": 999, **item})
    if not core:
        core.extend(top_scored(skills, registry, args.task, "task", limit=2))

    framework_id = infer_framework_id(args.task, manifest)
    if framework_id:
        item = find_skill(skills, framework_id)
        if item:
            core.append({"score": 900, **item})

    problem_id = infer_problem_id(args.task)
    if problem_id:
        item = find_skill(skills, problem_id)
        if item:
            core.append({"score": 900, **item})
    seen_core = set()
    core = [item for item in core if not (item["id"] in seen_core or seen_core.add(item["id"]))]

    recommended_items = [item["id"] for item in core] + [item["id"] for item in workflow_scored[:2]] + [item["id"] for item in role_scored[:2]]
    bundles = pick_bundles(args.task, recommended_items, manifest)
    commands = memory.get("preferred_commands", {})
    markdown = format_markdown(
        args.task,
        complexity,
        docs,
        core,
        local,
        role_scored[:2],
        workflow_scored[:2],
        bundles,
        commands,
        bundle_defs,
    )

    target = ai_dir / "current-task-brief.md"
    target.write_text(markdown, encoding="utf-8")

    print(f"Task\t{args.task}")
    print(f"Complexity\t{complexity}")
    print(f"Bundles\t{', '.join(bundles)}")
    print(f"Core\t{', '.join(item['id'] for item in core)}")
    if local:
        print(f"Local\t{', '.join(item['name'] for item in local)}")
    print(f"Brief\t{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
