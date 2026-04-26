---
name: codebase-onboarding
description: Analyze an unfamiliar codebase and produce a compact onboarding guide with architecture map, entry points, conventions, and next-step commands.
category: task
intent:
  - architecture
  - documentation
  - legacy_discovery
roles:
  - explorer
  - planner
mode: hybrid
risk: low
source_repo: everything-claude-code
source_path: skills/codebase-onboarding/SKILL.md
confidence: high
---

# Codebase Onboarding

Use this skill when opening an unfamiliar repository, inheriting a legacy codebase, or when the user asks to understand the project before making changes.

## Goals

1. Build a reliable map of the repo without reading everything.
2. Identify the real entry points, not just config files.
3. Detect conventions that should shape future edits.
4. Produce a short onboarding artifact that speeds up later sessions.

## Selective Reading Rule

Start broad and cheap:

- Detect manifests first: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`
- Detect framework markers: `next.config.*`, `vite.config.*`, `angular.json`, Django settings, FastAPI app, NestJS modules
- Snapshot the top 2 levels of the tree
- Find test locations, CI configs, Docker files, lint configs, env examples

Read implementation files only after the surface scan reveals where real execution starts.

## Phase 1: Reconnaissance

Collect these signals in parallel where possible:

- Package manifests and lockfiles
- App entry points like `main.*`, `index.*`, `app.*`, `server.*`, `cmd/`, `src/main/`
- Top-level folders and their likely responsibility
- Test runners and test directory structure
- Build, lint, typecheck, preview, and deploy commands
- CI/CD and environment conventions

## Phase 2: Architecture Mapping

Summarize:

- Languages, frameworks, major libraries, and databases
- App shape: monolith, monorepo, service split, CLI, library, or full-stack app
- Request or data flow from entry point to business logic to persistence
- Shared layers such as `lib/`, `services/`, `core/`, `db/`, `api/`, `components/`

For web apps, trace one real user flow or request path.
For backends, trace one endpoint from router to handler to persistence.
For libraries, trace the public API to core modules.

## Phase 3: Convention Detection

Record only conventions with evidence:

- Naming: kebab-case, PascalCase, snake_case, test file suffixes
- Error handling style
- Validation approach
- State management or dependency injection patterns
- Test strategy and coverage expectations
- Commit or branch conventions if git history is available

If a convention is unclear, say so explicitly instead of guessing.

## Phase 4: Output Artifacts

Produce a compact onboarding guide containing:

- What this project does
- Main stack
- Key entry points
- Directory map
- Request or execution lifecycle
- Commands to run locally
- Conventions to preserve
- Recommended first files to read for future tasks

If the repo has a project instruction file already, update it carefully.
If not, propose a minimal starter instruction file rather than a long handbook.

## Output Template

```md
# Onboarding Guide: <project>

## Overview
- What the project does
- Primary users or system boundary

## Stack
- Languages and frameworks
- Data stores
- Build and test tooling

## Entry Points
- Runtime entry
- API entry
- UI entry
- Background jobs or scripts

## Directory Map
- `src/...` -> purpose
- `apps/...` -> purpose
- `packages/...` -> purpose

## Execution Flow
- Request or feature path from input to output

## Conventions
- Naming
- Validation
- Error handling
- Testing

## Common Commands
- Dev
- Build
- Test
- Lint

## Where To Start
- 3-5 files or folders worth reading first
```

## Guardrails

- Do not read the whole repo line by line.
- Do not copy the README as the onboarding guide.
- Do not invent architecture labels without evidence.
- Keep the final guide scannable in under 2 minutes.
