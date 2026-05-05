#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


DOC_NAMES = {"SKILL.md", "AGENTS.md", "README.md", ".cursorrules"}
DOC_SUFFIXES = (".instructions.md", ".prompt.md", ".chatmode.md")
PACKS = ["frontend", "backend", "fullstack", "product", "security", "devops", "testing", "workflows", "roles", "rules"]

SOURCE_PRIORITIES = {
    "antigravity-kit": 95,
    "everything-claude-code": 90,
    "agent-skills": 85,
    "openai-skills": 80,
    "skills": 80,
    "awesome-copilot-for-testers": 75,
    "claude-skills": 70,
    "awesome-cursorrules": 65,
    "python-refactoring-skills": 65,
    "agent-nestjs-skills": 65,
    "claude-debug-and-refactor-skills-plugin": 60,
    "awesome-copilot": 55,
    "antigravity-awesome-skills": 45,
}

STACK_KEYWORDS = {
    "python": ["python", ".py", "fastapi", "django", "pydantic", "pytest", "asyncio"],
    "typescript": ["typescript", ".ts", "tsconfig", "type-safe", "tsx"],
    "javascript": ["javascript", "node", "npm", "browser", "js"],
    "go": ["golang", " go ", "go module", "go test"],
    "rust": ["rust", "cargo", "borrow", "tokio"],
    "java": ["java", "spring", "maven", "gradle"],
    "cpp": ["c++", "cpp", "cmake", "gtest"],
    "csharp": ["c#", ".net", "xunit", "asp.net"],
    "php": ["php", "laravel", "symfony"],
    "ruby": ["ruby", "rails", "gemfile"],
    "sql": ["sql", "database", "migration", "postgres", "mysql", "sqlite"],
    "react": ["react", "hooks", "useeffect", "jsx"],
    "nextjs": ["next.js", "nextjs", "app router", "server component"],
    "vue": ["vue", "nuxt", "composition api"],
    "angular": ["angular", "rxjs", "ngrx"],
    "svelte": ["svelte", "sveltekit"],
    "nestjs": ["nestjs", "provider", "module", "controller"],
    "docker": ["docker", "container", "compose", "dockerfile"],
    "playwright": ["playwright", "locator", "e2e"],
    "selenium": ["selenium", "webdriver", "browser automation"],
}

INTENT_KEYWORDS = {
    "bug_fix": ["bug", "debug", "fix", "error", "failure", "regression"],
    "feature_dev": ["feature", "implement", "build", "app", "scaffold"],
    "refactor": ["refactor", "clean code", "complexity", "maintainability"],
    "code_review": ["review", "audit", "checklist", "quality"],
    "testing": ["test", "testing", "tdd", "qa", "playwright", "e2e"],
    "documentation": ["documentation", "readme", "docs", "guide"],
    "architecture": ["architecture", "design", "pattern", "adr"],
    "security_review": ["security", "auth", "token", "vulnerability", "secrets"],
    "deployment": ["deploy", "ci/cd", "release", "production", "vercel"],
    "incident_debug": ["incident", "outage", "rollback", "production"],
    "product_planning": ["product", "prd", "roadmap", "requirements"],
    "orchestration": ["orchestrate", "orchestration", "multi-agent", "parallel", "team", "delegate"],
    "preview": ["preview", "dev server", "localhost", "start server"],
    "quality_gate": ["quality gate", "verify", "verification", "lint", "typecheck", "coverage"],
    "context_budget": ["context", "token", "budget", "compact", "summarize"],
    "legacy_discovery": ["legacy", "archaeology", "brownfield", "discovery", "explore"],
}

PACK_KEYWORDS = {
    "frontend": ["react", "next", "vue", "angular", "svelte", "ui", "css", "web-design"],
    "backend": ["api", "database", "sql", "python", "node", "nestjs", "django", "fastapi"],
    "fullstack": ["fullstack", "app", "feature", "next", "react", "api"],
    "product": ["product", "prd", "roadmap", "requirements", "analytics"],
    "security": ["security", "auth", "vulnerability", "secrets", "permission"],
    "devops": ["deploy", "docker", "ci/cd", "terraform", "kubernetes", "release"],
    "testing": ["test", "testing", "qa", "playwright", "e2e", "tdd"],
    "workflows": ["workflow", "command", "orchestrate", "quality gate", "verify", "preview", "plan"],
    "roles": ["agent", "specialist", "reviewer", "architect", "engineer", "orchestrator"],
    "rules": ["rule", "rules", "coding style", "security", "testing", "performance"],
}

ROLE_KEYWORDS = {
    "orchestrator": ["orchestrator", "orchestrate", "multi-agent", "parallel agents", "coordination"],
    "explorer": ["explorer", "explore", "discovery", "code archaeologist", "archaeology", "legacy"],
    "planner": ["planner", "plan", "project planner", "prd", "requirements"],
    "frontend": ["frontend", "react", "ui", "ux", "web", "component", "layout"],
    "backend": ["backend", "api", "server", "service", "endpoint"],
    "database": ["database", "schema", "migration", "sql", "query"],
    "qa": ["qa", "test", "testing", "e2e", "coverage"],
    "security": ["security", "audit", "vulnerability", "pentest", "auth"],
    "devops": ["devops", "deploy", "ci/cd", "docker", "infrastructure"],
    "performance": ["performance", "optimize", "slow", "latency"],
    "product": ["product", "owner", "manager", "roadmap", "mvp"],
    "documentation": ["documentation", "docs", "writer", "readme"],
}

WORKFLOW_NAMES = {
    "plan",
    "create",
    "debug",
    "test",
    "preview",
    "deploy",
    "orchestrate",
    "quality-gate",
    "verify",
    "context-budget",
    "multi-plan",
    "multi-execute",
}

SKIP_PATH_PARTS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".cache",
    "cache",
    "logs",
    "history",
    "backups",
    "session-data",
    "paste-cache",
    "conversations",
    "implicit",
    "metrics",
}

EXPECTED_ACTIVE = {
    "task:bug-fix": {
        "positive": ["debug", "bug", "reproduce", "root cause", "fix", "error"],
        "negative": ["pytorch", "cuda", "tensor", "training", "neural"],
    },
    "task:refactor": {
        "positive": ["refactor", "clean", "maintain", "structure", "behavior"],
        "negative": ["asp.net", ".net", "c# 12"],
    },
    "language:go": {
        "positive": ["go", "golang", "idiomatic"],
        "negative": ["google workspace", "gmail", "drive", "sheets", "gws "],
    },
    "problem:api-debug": {
        "positive": ["api", "endpoint", "request", "response", "status"],
        "negative": ["test suite only", "contract tests only"],
    },
    "problem:database-debug": {
        "positive": ["database", "migration", "query", "transaction", "index"],
        "negative": ["erd only"],
    },
    "problem:auth-security": {
        "positive": ["security", "auth", "authorization", "token", "permission"],
        "negative": ["nestjs best practices"],
    },
}

ROUTING_EVAL = [
    {
        "name": "go-build-error",
        "prompt": "fix Go compile error in module import",
        "expect": ["task:bug-fix", "language:go", "problem:build-error"],
        "reject": ["google-workspace", "pytorch"],
    },
    {
        "name": "api-500",
        "prompt": "debug API 500 endpoint response mismatch",
        "expect": ["task:bug-fix", "problem:api-debug"],
        "reject": ["api-test-suite-builder"],
    },
    {
        "name": "react-ui-review",
        "prompt": "review React UI for accessibility and layout issues",
        "expect": ["task:code-review", "framework:react"],
        "reject": [],
    },
    {
        "name": "playwright-test",
        "prompt": "write Playwright end to end test for login flow",
        "expect": ["task:testing", "framework:playwright"],
        "reject": [],
    },
    {
        "name": "database-migration",
        "prompt": "debug database migration lock and missing index",
        "expect": ["task:bug-fix", "problem:database-debug"],
        "reject": ["schema-designer-only"],
    },
    {
        "name": "docker-deploy",
        "prompt": "fix Docker deployment CI/CD production env failure",
        "expect": ["framework:docker", "problem:deployment-debug"],
        "reject": [],
    },
    {
        "name": "security-auth",
        "prompt": "review auth token permission security bug",
        "expect": ["problem:auth-security"],
        "reject": [],
    },
    {
        "name": "team-orchestration",
        "prompt": "orchestrate frontend backend and testing agents for a fullstack feature",
        "expect": ["workflow:parallel-agents", "role:orchestrator"],
        "reject": [],
    },
    {
        "name": "quality-gate",
        "prompt": "run quality gate with lint typecheck tests and coverage",
        "expect": ["workflow:quality-gate"],
        "reject": [],
    },
    {
        "name": "preview-web-app",
        "prompt": "preview web app on local dev server and check localhost",
        "expect": ["workflow:preview"],
        "reject": [],
    },
    {
        "name": "context-budget",
        "prompt": "reduce context tokens and keep only task critical routing info",
        "expect": ["workflow:context-budget"],
        "reject": [],
    },
    {
        "name": "legacy-discovery",
        "prompt": "explore legacy brownfield codebase before refactor",
        "expect": ["role:explorer"],
        "reject": [],
    },
]


def norm_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def trim(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "..."


def activation_rank(item: dict) -> int:
    rank = 0
    if item.get("active"):
        rank += 100
    if item.get("category") in {"task", "workflow", "problem"}:
        rank += 15
    if item.get("category") in {"language", "framework", "role"}:
        rank += 10
    if item.get("health") == "ok":
        rank += 12
    else:
        rank -= 18
    if item.get("duplicate"):
        rank -= 30
    rank += min(35, len(item.get("stacks", [])) * 4)
    rank += min(20, len(item.get("intents", [])) * 3)
    rank += min(15, len(item.get("roles", [])) * 3)
    rank += int(item.get("source_priority", 0)) // 5
    return rank


def read_text(path: Path, limit: int | None = None) -> str:
    data = path.read_text(encoding="utf-8", errors="ignore")
    return data if limit is None else data[:limit]


def load_source_strategy(root: Path) -> dict:
    path = root / "shared/registry/source-strategy.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end]
    out: dict[str, str] = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.+)$", line)
        if m:
            out[m.group(1)] = norm_scalar(m.group(2))
    return out


def is_runtime_or_state_path(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return bool(parts & SKIP_PATH_PARTS) or path.suffix.lower() in {".log", ".jsonl", ".pb", ".lock"}


def doc_type(path: Path) -> str | None:
    name = path.name
    parts = [p.lower() for p in path.parts]
    parent_names = set(parts)
    stem = path.stem.lower()
    if name == "SKILL.md":
        return "skill"
    if name in {"AGENTS.md"}:
        return "agent"
    if "agents" in parent_names and name.endswith(".md") and name.lower() not in {"readme.md", "template.md"}:
        return "agent"
    if "commands" in parent_names and name.endswith(".md") and name.lower() != "readme.md":
        return "workflow"
    if "workflows" in parent_names and name.endswith(".md") and name.lower() != "readme.md":
        return "workflow"
    if stem in WORKFLOW_NAMES and name.endswith(".md"):
        return "workflow"
    if ("rules" in parent_names or ".cursor" in parent_names) and (name.endswith(".md") or name.endswith(".mdc")):
        return "rule"
    if name.endswith(".chatmode.md"):
        return "agent"
    if name.endswith(".prompt.md"):
        return "prompt"
    if name.endswith(".instructions.md") or name == ".cursorrules" or name.endswith(".mdc"):
        return "rule"
    if name == "README.md":
        return "doc"
    return None


def repo_for(path: Path, repos: Path) -> tuple[str, Path]:
    rel = path.relative_to(repos)
    repo = rel.parts[0]
    return repo, Path(*rel.parts[1:])


def source_priority(repo: str, strategy: dict | None = None) -> int:
    override = (strategy or {}).get("source_priorities", {})
    if repo in override:
        return int(override[repo])
    return SOURCE_PRIORITIES.get(repo, 40)


def detect_many(text: str, mapping: dict[str, list[str]]) -> list[str]:
    hay = f" {text.lower()} "
    found = []
    for key, words in mapping.items():
        if any(w in hay for w in words):
            found.append(key)
    return found


def detect_roles(text: str) -> list[str]:
    return detect_many(text, ROLE_KEYWORDS)


def infer_category(path: Path, text: str, item_type: str) -> str:
    hay = f"{path.as_posix()} {text}".lower()
    if item_type == "agent":
        return "role"
    if item_type == "workflow" or any(k in hay for k in ["workflow", "command", "prompt"]):
        return "workflow"
    if item_type == "rule":
        if any(k in hay for k in ["python", "typescript", "javascript", "golang", "rust", "java", "c++", "csharp", "ruby", "php"]):
            return "language"
        if any(k in hay for k in ["react", "next", "vue", "angular", "svelte", "django", "fastapi", "nestjs", "docker", "playwright"]):
            return "framework"
        return "other"
    if any(k in hay for k in ["review", "test", "debug", "feature", "refactor", "documentation"]):
        return "task"
    if any(k in hay for k in ["react", "next", "vue", "angular", "svelte", "django", "fastapi", "nestjs", "docker", "playwright"]):
        return "framework"
    if any(k in hay for k in ["python", "typescript", "javascript", "golang", "rust", "java", "c++", "csharp", "ruby", "php"]):
        return "language"
    if any(k in hay for k in ["security", "api", "database", "deploy", "performance", "git", "dependency"]):
        return "problem"
    return "other"


def stable_id(repo: str, rel: Path, category: str) -> str:
    raw = rel.as_posix()
    digest = hashlib.sha1(f"{repo}/{raw}".encode()).hexdigest()[:10]
    name = rel.parent.name if rel.name == "SKILL.md" else rel.stem
    return f"{category}:{slug(repo)}-{slug(name)}-{digest}"


def active_skill_category(path: Path, root: Path) -> tuple[str | None, str | None]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None, None
    parts = rel.parts
    # Support solo-dev/skills
    try:
        i = parts.index("solo-dev")
        if parts[i + 1] == "skills" and parts[-1] == "SKILL.md" and len(parts) == i + 5:
            return parts[i + 2], parts[i + 3]
    except Exception:
        pass
    # Support packs/
    try:
        i = parts.index("packs")
        if parts[-1] == "SKILL.md":
            # packs/category/skills/name/SKILL.md
            return parts[i + 1], parts[i + 3]
    except Exception:
        pass
    if rel.as_posix().endswith("shared/skill-spec/skill-template/SKILL.md"):
        return "other", "skill-template"
    return None, None


def active_doc_category(path: Path, root: Path) -> tuple[str | None, str | None, str | None]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None, None, None
    parts = rel.parts
    if len(parts) == 3 and parts[0] == "team-dev" and parts[1] == "roles" and path.suffix == ".md":
        return "role", path.stem, "agent"
    if len(parts) == 3 and parts[0] == "shared" and parts[1] == "workflows" and path.suffix == ".md":
        return "workflow", path.stem, "workflow"
    return None, None, None


def infer_source_repo_from_detail(src: str, upstream: str = "") -> str:
    for raw in (src, upstream):
        if not raw or raw in {"manual-or-patched", "local"}:
            continue
        path = Path(raw)
        parts = path.parts
        if len(parts) >= 2 and parts[0] == "ai-repos":
            return parts[1]
        marker = ("shared", "sources", "upstream", "repos")
        for idx in range(0, max(0, len(parts) - len(marker))):
            if tuple(parts[idx : idx + len(marker)]) == marker and len(parts) > idx + len(marker):
                return parts[idx + len(marker)]
    return ""


def load_source_map(root: Path) -> dict[str, tuple[str, str, str, str]]:
    mapping = {}
    tsv = root / "shared/registry/imported-skills.tsv"
    if not tsv.exists():
        return mapping
    for line in tsv.read_text(encoding="utf-8", errors="ignore").splitlines():
        cols = line.split("|")
        if len(cols) < 4:
            continue
        skill_id, dest, status, src = cols[:4]
        upstream = cols[4] if len(cols) >= 5 else ""
        mapping[dest] = (skill_id, status, src, upstream)
        if src:
            mapping[src] = (skill_id, status, src, upstream)
        if upstream:
            mapping[upstream] = (skill_id, status, src, upstream)
        try:
            rel = Path(dest).relative_to(root).as_posix()
            mapping[rel] = (skill_id, status, src, upstream)
        except ValueError:
            pass
    return mapping


def scan_catalog(root: Path, repos: Path) -> list[dict]:
    active_sources = set()
    source_map = load_source_map(root)
    source_strategy = load_source_strategy(root)
    for _dest, (_skill_id, _status, src, upstream) in source_map.items():
        if src and src != "local":
            active_sources.add(str(Path(src)))
        if upstream and upstream != "local":
            active_sources.add(str(Path(upstream)))

    items = []
    seen = set()
    if not repos.exists():
        return items

    for path in sorted(repos.rglob("*")):
        if not path.is_file() or is_runtime_or_state_path(path):
            continue
        dtype = doc_type(path)
        if dtype is None:
            continue
        try:
            repo, rel = repo_for(path, repos)
        except ValueError:
            continue
        text = read_text(path, 12000)
        fm = frontmatter(text)
        name = fm.get("name") or (rel.parent.name if path.name == "SKILL.md" else path.stem)
        desc = fm.get("description") or ""
        body = f"{name}\n{desc}\n{rel.as_posix()}\n{text[:3000]}"
        category = infer_category(rel, body, dtype)
        stacks = detect_many(body, STACK_KEYWORDS)
        intents = detect_many(body, INTENT_KEYWORDS)
        packs = detect_many(body, PACK_KEYWORDS)
        if category in {"language", "framework"} and not packs:
            packs = ["frontend"] if any(s in stacks for s in ["react", "nextjs", "vue", "angular", "svelte"]) else ["backend"]
        if "testing" in intents and "testing" not in packs:
            packs.append("testing")
        if "security_review" in intents and "security" not in packs:
            packs.append("security")
        if "deployment" in intents and "devops" not in packs:
            packs.append("devops")

        summary_source = desc or re.sub(r"^---.*?---", "", text, flags=re.S).strip().splitlines()[0:3]
        if isinstance(summary_source, list):
            summary_source = " ".join(summary_source)
        summary = trim(str(summary_source), 180)
        trigger = trim(desc or f"Use for {name}.", 220)
        content_hash = hashlib.sha1(f"{name}|{desc}".lower().encode()).hexdigest()[:12]
        dedupe_key = f"{slug(name)}:{content_hash}"
        duplicate = dedupe_key in seen
        seen.add(dedupe_key)

        src_path = path.as_posix()
        active = src_path in active_sources or str(path) in active_sources
        priority = source_priority(repo, source_strategy)
        roles = detect_roles(body)
        if dtype == "agent" and "roles" not in packs:
            packs.append("roles")
        if dtype == "workflow" and "workflows" not in packs:
            packs.append("workflows")
        if dtype == "rule" and "rules" not in packs:
            packs.append("rules")
        score = priority + len(stacks) * 3 + len(intents) * 2 + len(roles) * 2 + (10 if dtype == "skill" else 0) + (8 if dtype in {"agent", "workflow"} else 0) - (20 if duplicate else 0)
        issues = []
        if not desc and dtype == "skill":
            issues.append("missing-description")
        if not desc and dtype in {"agent", "workflow"}:
            issues.append("missing-trigger")
        if dtype == "workflow" and any(x in body.lower() for x in ["claude-only", "claude code", "$arguments", "subagent"]):
            issues.append("tool-specific-review")
        if len(text) > 30000:
            issues.append("long-skill")
        if len(trigger) < 18:
            issues.append("vague-trigger")

        items.append(
            {
                "id": stable_id(repo, rel, category),
                "active": active,
                "type": dtype,
                "category": category,
                "stacks": stacks[:8],
                "intents": intents[:8],
                "roles": roles[:8],
                "risk": "high" if any(i in intents for i in ["security_review", "deployment", "incident_debug"]) else "medium",
                "source_repo": repo,
                "source_path": rel.as_posix(),
                "source_status": "community-source",
                "source_priority": priority,
                "summary": summary,
                "trigger": trigger,
                "health": "review" if issues else "ok",
                "issues": issues,
                "score": score,
                "duplicate": duplicate,
                "duplicate_key": dedupe_key,
                "packs": packs[:6],
                "name": name,
            }
        )
        items[-1]["activation_rank"] = activation_rank(items[-1])
    items.sort(key=lambda x: (-int(x["active"]), -int(x["score"]), x["source_repo"], x["source_path"]))
    return items


def active_registry(root: Path) -> list[dict]:
    source_map = load_source_map(root)
    source_strategy = load_source_strategy(root)
    skills = []
    for path in sorted(root.rglob("SKILL.md")):
        category, slot = active_skill_category(path, root)
        if category is None:
            continue
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        fm = frontmatter(text)
        name = fm.get("name") or slot
        desc = fm.get("description") or f"Use for {category}:{slot}."
        skill_id, status, src, upstream = source_map.get(
            str(path),
            source_map.get(rel, (f"{category}:{slot}", "local-manual", "manual-or-patched", "")),
        )
        source_repo = infer_source_repo_from_detail(src, upstream)
        body = f"{name}\n{desc}\n{text[:5000]}".lower()
        issues = []
        if "Use this compact fallback" in text or status == "generated-fallback":
            issues.extend(["placeholder-or-compact-fallback", "generated-fallback-review-needed"])
        if name.startswith(("'", '"')) or desc.startswith(("'", '"')):
            issues.append("quoted-frontmatter")
        rule = EXPECTED_ACTIVE.get(skill_id)
        if rule:
            positives = [p for p in rule["positive"] if p in body]
            negatives = [n for n in rule["negative"] if n in body]
            if not positives:
                issues.append("semantic-mismatch-no-positive-signal")
            if negatives:
                issues.append("semantic-mismatch-negative-signal:" + ",".join(negatives[:3]))
        stacks = detect_many(f"{name} {desc} {rel}", STACK_KEYWORDS)
        intents = detect_many(f"{name} {desc}", INTENT_KEYWORDS)
        skills.append(
            {
                "id": skill_id,
                "name": name,
                "description": trim(desc, 240),
                "trigger": trim(desc, 220),
                "path": rel,
                "category": category,
                "slot": slot,
                "stacks": stacks,
                "intents": intents,
                "roles": [],
                "risk": "high" if "security_review" in intents or "deployment" in intents else "medium",
                "source_status": status,
                "source_detail": src,
                "source_upstream": upstream,
                "source_repo": source_repo or "active-core",
                "health": "review" if issues else "ok",
                "weak": bool(issues),
                "issues": issues,
            }
        )
        skills[-1]["source_priority"] = source_priority(source_repo, source_strategy) if source_repo else 100
        skills[-1]["active"] = True
        skills[-1]["activation_rank"] = activation_rank(skills[-1])
    for path in sorted(root.rglob("*.md")):
        category, slot, dtype = active_doc_category(path, root)
        if category is None:
            continue
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        fm = frontmatter(text)
        name = fm.get("name") or slot
        desc = fm.get("description") or trim(" ".join(line.strip("# ").strip() for line in text.splitlines()[:6] if line.strip()), 240) or f"Use for {category}:{slot}."
        skill_id, status, src, upstream = source_map.get(
            str(path),
            source_map.get(rel, (f"{category}:{slot}", "local-manual", "manual-or-patched", "")),
        )
        source_repo = infer_source_repo_from_detail(src, upstream)
        body = f"{name}\n{desc}\n{text[:5000]}"
        roles = detect_roles(body)
        stacks = detect_many(body, STACK_KEYWORDS)
        intents = detect_many(body, INTENT_KEYWORDS)
        issues = []
        if len(desc) < 18:
            issues.append("vague-trigger")
        if dtype == "workflow" and any(x in body.lower() for x in ["claude code", "$arguments", "subagent"]):
            issues.append("tool-specific-review")
        skills.append(
            {
                "id": skill_id,
                "name": name,
                "description": trim(desc, 240),
                "trigger": trim(desc, 220),
                "path": rel,
                "category": category,
                "slot": slot,
                "type": dtype,
                "stacks": stacks,
                "intents": intents,
                "roles": roles,
                "risk": "high" if "security_review" in intents or "deployment" in intents else "medium",
                "source_status": status,
                "source_detail": src,
                "source_upstream": upstream,
                "source_repo": source_repo or "active-core",
                "health": "review" if issues else "ok",
                "weak": bool(issues),
                "issues": issues,
            }
        )
        skills[-1]["source_priority"] = source_priority(source_repo, source_strategy) if source_repo else 100
        skills[-1]["active"] = True
        skills[-1]["activation_rank"] = activation_rank(skills[-1])
    return skills


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_registry(root: Path, repos: Path) -> tuple[list[dict], list[dict]]:
    reg = root / "shared/registry"
    reg.mkdir(parents=True, exist_ok=True)
    skills = active_registry(root)
    catalog = scan_catalog(root, repos)

    write_json(reg / "skills.json", skills)
    write_json(reg / "catalog.json", catalog)

    compact = [
        "# Skill Index",
        "",
        "Lean active-core index. Load one selected SKILL.md only. If no active skill fits, search shared/registry/catalog.json or pack catalog.",
        "",
    ]
    for s in skills:
        if s["category"] == "other":
            continue
        health = "" if s["health"] == "ok" else " [review]"
        compact.append(f"- {s['id']}: {s['trigger']} ({s['path']}){health}")
    (reg / "SKILL_INDEX.md").write_text("\n".join(compact) + "\n", encoding="utf-8")

    health_items = [s for s in skills if s["issues"]]
    health = ["# Skill Health Report", "", "Generated by registry refresh.", "", "## Active skills needing review", ""]
    for s in health_items:
        health += [
            f"- {s['id']}",
            f"  - name: {s['name']}",
            f"  - path: {s['path']}",
            f"  - source: {s['source_status']}",
            f"  - source_detail: {s['source_detail']}",
            f"  - issues: {', '.join(s['issues'])}",
            "",
        ]
    bad_catalog = sum(1 for item in catalog if item["health"] != "ok")
    health += [
        "## Summary",
        "",
        f"- Active skills: {len(skills)}",
        f"- Active skills needing review: {len(health_items)}",
        f"- Catalog items: {len(catalog)}",
        f"- Catalog items needing review: {bad_catalog}",
    ]
    (reg / "SKILL_HEALTH.md").write_text("\n".join(health) + "\n", encoding="utf-8")

    for pack in PACKS:
        items = [item for item in catalog if pack in item.get("packs", [])]
        slim = [
            {
                "id": item["id"],
                "type": item["type"],
                "category": item["category"],
                "stacks": item["stacks"],
                "intents": item["intents"],
                "source_repo": item["source_repo"],
                "source_path": item["source_path"],
                "summary": item["summary"],
                "score": item["score"],
                "active": item["active"],
                "roles": item.get("roles", []),
            }
            for item in items[:500]
        ]
        write_json(root / f"packs/{pack}/catalog.json", slim)
        readme = root / f"packs/{pack}/README.md"
        if not readme.exists():
            readme.write_text(f"# {pack} Pack\n\nGenerated catalog for {pack} items. Route first; load leaf files only when selected.\n", encoding="utf-8")

    write_json(
        root / "shared/router/STACK_KEYWORDS.json",
        {k: v for k, v in sorted(STACK_KEYWORDS.items())},
    )
    write_json(
        root / "shared/router/PROBLEM_KEYWORDS.json",
        {
            "api-debug": ["api", "endpoint", "request", "response", "500", "404", "401", "403"],
            "database-debug": ["database", "migration", "transaction", "index", "query", "orm"],
            "dependency-debug": ["dependency", "provider", "import", "circular", "module"],
            "build-error": ["build", "compile", "bundler", "tsconfig", "vite", "webpack", "ci"],
            "performance-debug": ["slow", "timeout", "memory leak", "high cpu", "performance"],
            "auth-security": ["auth", "token", "session", "cookie", "permission", "security"],
            "git-workflow": ["git", "rebase", "merge conflict", "detached head", "force push"],
            "deployment-debug": ["deploy", "docker", "ci/cd", "env", "production", "rollback"],
            "async-debug": ["async", "await", "coroutine", "event loop", "thread", "deadlock"],
            "orchestration": ["orchestrate", "multi-agent", "parallel", "team", "delegate"],
            "quality-gate": ["quality gate", "verify", "lint", "typecheck", "coverage"],
            "context-budget": ["context", "token", "budget", "compact"],
            "preview": ["preview", "dev server", "localhost"],
        },
    )
    write_json(root / "shared/evaluation/routing-eval.json", ROUTING_EVAL)
    write_health_reports(root, skills, catalog)
    return skills, catalog


def write_health_reports(root: Path, skills: list[dict], catalog: list[dict]) -> None:
    reg = root / "shared/registry"
    strategy = load_source_strategy(root)
    active_source_mix = dict(
        sorted(
            Counter(skill.get("source_repo", "active-core") for skill in skills).items(),
            key=lambda row: (-row[1], row[0]),
        )
    )
    report = {
        "generated_at": Path(__file__).stat().st_mtime,
        "preferred_upstream": strategy.get("preferred_upstream", strategy.get("primary_upstream", "")),
        "active_skills": len(skills),
        "catalog_items": len(catalog),
        "active_review_count": sum(1 for skill in skills if skill.get("health") != "ok"),
        "catalog_review_count": sum(1 for item in catalog if item.get("health") != "ok"),
        "top_active": sorted(
            (
                {
                    "id": skill["id"],
                    "path": skill["path"],
                    "category": skill["category"],
                    "activation_rank": skill.get("activation_rank", 0),
                    "health": skill["health"],
                }
                for skill in skills
            ),
            key=lambda item: (-int(item["activation_rank"]), item["id"]),
        )[:20],
        "top_catalog": sorted(
            (
                {
                    "id": item["id"],
                    "source_repo": item["source_repo"],
                    "source_path": item["source_path"],
                    "category": item["category"],
                    "activation_rank": item.get("activation_rank", 0),
                    "health": item["health"],
                    "active": item["active"],
                }
                for item in catalog
            ),
            key=lambda item: (-int(item["activation_rank"]), not bool(item["active"]), item["id"]),
        )[:40],
        "review_hotspots": sorted(
            (
                {
                    "id": item["id"],
                    "source_repo": item.get("source_repo", "active-core"),
                    "path": item.get("source_path", item.get("path", "")),
                    "issues": item.get("issues", []),
                    "activation_rank": item.get("activation_rank", 0),
                }
                for item in [*skills, *catalog]
                if item.get("health") != "ok"
            ),
            key=lambda item: (-int(item["activation_rank"]), item["id"]),
        )[:40],
        "pack_pressure": dict(
            sorted(
                Counter(pack for item in catalog for pack in item.get("packs", [])).items(),
                key=lambda row: (-row[1], row[0]),
            )
        ),
        "active_source_mix": active_source_mix,
    }
    write_json(reg / "activation-report.json", report)

    lines = [
        "# Activation Report",
        "",
        "Generated by registry refresh. Use this to keep expansion broad while keeping default activation narrow.",
        "",
        "## Summary",
        "",
        f"- Active skills: {report['active_skills']}",
        f"- Catalog items: {report['catalog_items']}",
        f"- Active review count: {report['active_review_count']}",
        f"- Catalog review count: {report['catalog_review_count']}",
        f"- Preferred collection upstream: {report['preferred_upstream'] or 'not-set'}",
        "",
        "## Active Source Mix",
        "",
    ]
    for repo, count in list(report["active_source_mix"].items())[:10]:
        lines.append(f"- {repo}: {count}")
    lines += [
        "",
        "## Top Active Skills",
        "",
    ]
    for item in report["top_active"][:12]:
        lines.append(f"- {item['id']} [{item['category']}] rank={item['activation_rank']} ({item['path']})")
    lines += ["", "## Review Hotspots", ""]
    if report["review_hotspots"]:
        for item in report["review_hotspots"][:12]:
            issue_text = ", ".join(item["issues"]) or "review-needed"
            lines.append(f"- {item['id']} rank={item['activation_rank']} [{item['source_repo']}] {issue_text}")
    else:
        lines.append("- none")
    lines += ["", "## Pack Pressure", ""]
    for pack, count in list(report["pack_pressure"].items())[:10]:
        lines.append(f"- {pack}: {count}")
    (reg / "ACTIVATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def registry_health(root: Path) -> int:
    report_path = root / "shared/registry/activation-report.json"
    if not report_path.exists():
        print("Missing activation-report.json. Run refresh first.", file=sys.stderr)
        return 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(f"active_skills\t{report.get('active_skills', 0)}")
    print(f"catalog_items\t{report.get('catalog_items', 0)}")
    print(f"active_review_count\t{report.get('active_review_count', 0)}")
    print(f"catalog_review_count\t{report.get('catalog_review_count', 0)}")
    print(f"preferred_upstream\t{report.get('preferred_upstream', '')}")
    for repo, count in list(report.get("active_source_mix", {}).items())[:5]:
        print(f"source_mix\t{repo}\t{count}")
    for item in report.get("review_hotspots", [])[:10]:
        print(
            "review\t{rank}\t{item_id}\t{source}\t{issues}".format(
                rank=item.get("activation_rank", 0),
                item_id=item.get("id", ""),
                source=item.get("source_repo", ""),
                issues=",".join(item.get("issues", [])),
            )
        )
    return 0


def score_skill_for_query(skill: dict, query: str) -> int:
    hay = f"{skill.get('id','')} {skill.get('name','')} {skill.get('description','')} {skill.get('trigger','')} {' '.join(skill.get('stacks', []))} {' '.join(skill.get('intents', []))}".lower()
    words = [w for w in re.split(r"[^a-z0-9+#.]+", query.lower()) if w]
    q = query.lower()
    skill_id = skill.get("id", "").lower()
    score = 0
    for word in words:
        if word in hay:
            score += 5
        if word and word in skill_id:
            score += 24
    exact_boosts = {
        "language:go": ["go", "golang"],
        "language:javascript": ["javascript", "js"],
        "language:typescript": ["typescript", "ts"],
        "framework:react": ["react"],
        "framework:nextjs": ["next", "nextjs", "next.js"],
        "framework:docker": ["docker", "container", "dockerfile", "compose"],
        "framework:playwright": ["playwright"],
        "framework:fastapi": ["fastapi"],
        "problem:api-debug": ["api", "endpoint", "500", "404", "request", "response"],
        "problem:database-debug": ["database", "migration", "transaction", "index", "query"],
        "problem:deployment-debug": ["deploy", "deployment", "ci/cd", "production", "rollback"],
        "problem:build-error": ["build", "compile", "compiler", "tsconfig"],
        "problem:auth-security": ["auth", "token", "permission", "security"],
        "task:bug-fix": ["fix", "debug", "bug", "error", "failure"],
        "task:code-review": ["review", "audit"],
        "task:accessibility": ["accessibility", "a11y", "wcag", "aria"],
        "task:e2e-testing": ["e2e", "end-to-end", "playwright", "user journey"],
        "task:testing": ["test", "testing", "e2e"],
        "workflow:parallel-agents": ["orchestrate", "multi-agent", "parallel", "team", "agents"],
        "workflow:intelligent-routing": ["route", "routing", "select skill", "select agent"],
        "workflow:quality-gate": ["quality gate", "lint", "typecheck", "coverage"],
        "workflow:preview": ["preview", "localhost", "dev server"],
        "workflow:context-budget": ["context", "token", "budget", "compact"],
        "role:orchestrator": ["orchestrate", "multi-agent", "team", "coordinate"],
        "role:explorer": ["explore", "legacy", "brownfield", "discovery"],
        "role:security-auditor": ["security", "audit", "vulnerability"],
        "role:a11y-architect": ["accessibility", "a11y", "wcag", "aria"],
        "role:e2e-runner": ["e2e", "end-to-end", "playwright", "journey"],
        "role:frontend-specialist": ["frontend", "ui", "react"],
        "role:backend-specialist": ["backend", "api", "server"],
    }
    for target_id, aliases in exact_boosts.items():
        if skill_id == target_id and any(alias in q for alias in aliases):
            score += 50
    if skill_id == "role:orchestrator" and any(alias in q for alias in ["orchestrate", "orchestration", "multi-agent", "parallel", "team"]):
        score += 90
    if skill_id == "workflow:parallel-agents" and any(alias in q for alias in ["orchestrate", "multi-agent", "parallel", "team"]):
        score += 70
    if skill.get("category") == "role" and skill_id not in {"role:orchestrator", "role:explorer"} and any(alias in q for alias in ["orchestrate", "orchestration", "multi-agent"]):
        score -= 30
    for intent, keys in INTENT_KEYWORDS.items():
        if any(k in q for k in keys) and intent in skill.get("intents", []):
            score += 12
    for stack, keys in STACK_KEYWORDS.items():
        if any(k.strip() and k.strip() in q for k in keys) and (stack in skill.get("stacks", []) or stack in skill.get("id", "")):
            score += 15
    score += min(40, int(skill.get("activation_rank", 0)) // 4)
    if skill.get("health") != "ok":
        score -= 20
    return score


def route(root: Path, query: str) -> list[dict]:
    skills_path = root / "shared/registry/skills.json"
    if not skills_path.exists():
        return []
    skills = json.loads(skills_path.read_text(encoding="utf-8"))
    scored = [(score_skill_for_query(skill, query), skill) for skill in skills if skill.get("category") != "other"]
    scored = [(s, item) for s, item in scored if s > 0]
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    chosen = []
    used_categories = set()
    for score, item in scored:
        category = item["category"]
        group = "stack" if category in {"language", "framework"} else category
        if group in used_categories:
            continue
        used_categories.add(group)
        chosen.append({"score": score, **item})
        if len(chosen) >= 4:
            break
    return chosen


def eval_routes(root: Path) -> int:
    failures = []
    for case in ROUTING_EVAL:
        chosen = route(root, case["prompt"])
        chosen_ids = {item["id"] for item in chosen}
        chosen_text = " ".join(f"{item['id']} {item.get('name','')} {item.get('description','')}" for item in chosen).lower()
        missing = [expected for expected in case["expect"] if expected not in chosen_ids]
        rejected = [bad for bad in case.get("reject", []) if bad and bad.lower() in chosen_text]
        if missing or rejected:
            failures.append({"case": case["name"], "missing": missing, "rejected": rejected, "chosen": sorted(chosen_ids)})
    out = ["# Routing Eval", ""]
    if failures:
        out.append("Status: FAIL")
        out.append("")
        for failure in failures:
            out.append(f"- {failure['case']}: missing={failure['missing']} rejected={failure['rejected']} chosen={failure['chosen']}")
    else:
        out.append("Status: PASS")
        out.append("")
        out.append(f"- Cases: {len(ROUTING_EVAL)}")
    report = root / "shared/evaluation/ROUTING_EVAL.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    if failures:
        print(report.read_text(encoding="utf-8"))
        return 1
    print(f"Routing eval passed: {len(ROUTING_EVAL)} cases")
    return 0


def search(root: Path, query: str, limit: int, item_type: str = "") -> int:
    catalog_path = root / "shared/registry/catalog.json"
    active_path = root / "shared/registry/skills.json"
    items = []
    if active_path.exists():
        for item in json.loads(active_path.read_text(encoding="utf-8")):
            item = dict(item)
            item["source_repo"] = "active-core"
            item["source_path"] = item.get("path", "")
            item["score"] = 200
            item["active"] = True
            item["activation_rank"] = max(int(item.get("activation_rank", 0)), 120)
            items.append(item)
    if catalog_path.exists():
        items.extend(json.loads(catalog_path.read_text(encoding="utf-8")))
    scored = []
    q = query.lower()
    words = [w for w in re.split(r"[^a-z0-9+#.]+", q) if w]
    for item in items:
        if item_type and item.get("type", item.get("category")) != item_type:
            continue
        hay = f"{item.get('id','')} {item.get('name','')} {item.get('summary','')} {item.get('trigger','')} {item.get('source_repo','')} {item.get('source_path','')} {' '.join(item.get('stacks', []))} {' '.join(item.get('intents', []))}".lower()
        score = int(item.get("score", 0))
        score += min(50, int(item.get("activation_rank", 0)) // 3)
        item_id = item.get("id", "").lower()
        for word in words:
            if word in hay:
                score += 20
            if word and word in item_id:
                score += 80
        if item.get("active"):
            score += score_skill_for_query(item, query)
        if all(word in hay for word in words):
            score += 60
        if score > int(item.get("score", 0)):
            scored.append((score, item))
    scored.sort(key=lambda x: (-x[0], not bool(x[1].get("active")), x[1].get("source_repo", ""), x[1].get("source_path", "")))
    for score, item in scored[:limit]:
        marker = "active" if item.get("active") else "leaf"
        print(f"{score}\t{marker}\t{item.get('id')}\t{item.get('source_repo')}:{item.get('source_path')}\t{item.get('summary') or item.get('description')}")
    return 0


def write_source_catalog(root: Path, repos: Path) -> None:
    strategy = load_source_strategy(root)
    entries = []
    for repo_dir in sorted(p for p in repos.iterdir() if p.is_dir()):
        docs = 0
        skills = 0
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            dtype = doc_type(path)
            if dtype:
                docs += 1
                if dtype == "skill":
                    skills += 1
        entries.append(
            {
                "repo": repo_dir.name,
                "local_path": repo_dir.as_posix(),
                "priority": source_priority(repo_dir.name, strategy),
                "skill_count": skills,
                "doc_count": docs,
            }
        )
    write_json(root / "shared/registry/source-catalog.json", entries)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["refresh", "search", "eval", "health"])
    parser.add_argument("--root", default="ai-dev-system")
    parser.add_argument("--repos", default="ai-repos")
    parser.add_argument("--query", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--type", default="")
    args = parser.parse_args(argv)

    root = Path(args.root)
    repos = Path(args.repos)
    if args.command == "refresh":
        skills, catalog = write_registry(root, repos)
        if repos.exists():
            write_source_catalog(root, repos)
        print(f"Active skills: {len(skills)}")
        print(f"Catalog items: {len(catalog)}")
        print(f"Registry: {root / 'shared/registry'}")
        return 0
    if args.command == "search":
        if not args.query:
            print("ERROR: --query is required", file=sys.stderr)
            return 2
        return search(root, args.query, args.limit, args.type)
    if args.command == "eval":
        return eval_routes(root)
    if args.command == "health":
        return registry_health(root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
