# AI System

Portable, project-aware AI development system for real repositories.

[![Portable](https://img.shields.io/badge/portable-project--ready-1f6feb)](#what-you-copy-into-a-project)
[![Project Aware](https://img.shields.io/badge/context-project--aware-2da44e)](#what-gets-generated-per-project)
[![ECC First](https://img.shields.io/badge/upstream-ECC--first-f59e0b)](#upstream-collection-strategy)
[![Docs](https://img.shields.io/badge/docs-English%20%7C%20Vietnamese-7c3aed)](#)

GitHub description:
`A portable project-aware AI dev system with curated skills, task briefs, frozen upstream metadata, and zero ai-repos dependency in day-to-day project use.`

For the Vietnamese guide, see [README_VI.md](README_VI.md).

## At A Glance

- Copy only `ai-dev-system/` into a project and start using it immediately.
- Build project-aware context from the real repo instead of relying on generic prompting.
- Keep upstream inspiration and traceability without carrying `ai-repos/` into every codebase.
- Route to the smallest useful set of skills, workflows, and roles instead of loading everything.
- Support both solo execution and team-style orchestration with the same portable core.

## Feature Highlights

- Project-aware memory, routing, task briefs, and local skill indexing
- Frozen upstream metadata for portable installs
- ECC-first curated collection strategy
- Built-in commands for project init, sync, health, memory, docs, and session continuity
- Support for project-local custom skills without polluting the global core
- Roles and workflows for architecture, implementation, review, accessibility, performance, and E2E work

## Good Fits

- Personal repositories where you want a reusable AI system without central-machine dependency
- Client projects where you want portable AI context but do not want to ship upstream source repos
- Long-lived codebases where project conventions, architecture, and task continuity matter
- Teams that want a lighter-weight alternative to sprawling agent setups

## Quick Start

If you only want the shortest practical version:

1. Copy `ai-dev-system/` into your repository root.
2. Run `./ai-dev-system/bin/ai-dev project-setup all`
3. Run `./ai-dev-system/bin/ai-dev project-work "describe the task"`
4. Ask your AI to work from the repo root and use the generated project context

That is enough to get most of the value out of the system.

## Why This Exists

Most AI setups are either:

- too generic to understand a real codebase
- too tied to one central machine
- too noisy, with too many rules, agents, and commands active at once

This repository takes a different approach:

- keep a compact, curated `ai-dev-system/`
- make it project-aware after installation
- freeze upstream references into local metadata
- copy only `ai-dev-system/` into each real project

The result is a system that stays portable, focused, and useful inside actual repositories.

## What You Copy Into A Project

For normal day-to-day use inside a project, copy only:

- `ai-dev-system/`

You do not need to copy:

- `ai-repos/`
- the root `scripts/` folder
- any top-level wrapper scripts from this source repository

Why this works:

- `ai-dev-system/bin/ai-dev` already uses internal scripts from `ai-dev-system/shared/scripts/`
- frozen upstream metadata already lives inside `ai-dev-system/shared/sources/upstream/`
- upstream collection and curation happen on your main machine, not inside every client or personal repo
- this repository no longer expects project copies to include duplicate top-level `.sh` helpers

## Real Usage

### New Project

If you are starting a new repository:

1. Copy `ai-dev-system/` into the repo root.
2. Run:

```bash
./ai-dev-system/bin/ai-dev project-setup all
```

3. Check what the system discovered:

```bash
./ai-dev-system/bin/ai-dev project-health
```

4. Before the first real task, create a task brief:

```bash
./ai-dev-system/bin/ai-dev project-work "describe the product or the first feature"
```

This creates project-aware context before the AI starts making assumptions.

### Existing Project

If the repository already has a real codebase:

1. Copy `ai-dev-system/` into the repo root.
2. Initialize it:

```bash
./ai-dev-system/bin/ai-dev project-setup all
```

3. Sync project-specific context:

```bash
./ai-dev-system/bin/ai-dev project-health
```

4. Review what was detected:

```bash
./ai-dev-system/bin/ai-dev project-status
```

5. Before a medium or large task:

```bash
./ai-dev-system/bin/ai-dev project-work "describe the task"
```

This is where the system becomes most useful:

- better repo-specific routing
- fewer wrong assumptions about conventions
- better continuity across longer tasks
- less context waste

## How To Use It With AI

Do not treat the AI like a blank prompt box after setup.

Once `project-setup` is done, let the AI work from the project root where `ai-dev-system/` exists, and use the installed project instructions:

- Claude: `CLAUDE.md`
- Cursor: `.cursorrules`
- Copilot: `.github/copilot-instructions.md`
- ChatGPT or custom project prompting: files under `.ai-dev-system/`

Recommended flow for real work:

1. initialize the project once
2. run `project-health` when the repo changes meaningfully
3. run `project-work` for non-trivial tasks
4. ask the AI to work from the repo root
5. let it use `.ai-dev-system/` as the source of project memory, routing, and task context

Example prompts:

- `Read the project context and implement the checkout fix.`
- `Use the current task brief and update the API error handling flow.`
- `Review this repo using the project conventions before suggesting changes.`

## Default CLI Behavior

When `ai-dev-system/` lives inside a project, `ai-dev` automatically treats the parent directory as the current project.

That means these work without passing a project path:

```bash
./ai-dev-system/bin/ai-dev project-setup all
./ai-dev-system/bin/ai-dev project-work "fix checkout voucher bug"
./ai-dev-system/bin/ai-dev project-status
```

You can still pass an explicit path when needed, but it is no longer required for normal use.

## What Gets Generated Per Project

Each initialized project gets a local project-aware layer under `.ai-dev-system/`:

- `project-manifest.json`
- `project-memory.json`
- `custom-skill-index.json`
- `project-profile.md`
- `project-commands.md`
- `project-architecture.md`
- `project-conventions.md`
- `project-customizations.md`
- `project-routing.md`
- `current-task-brief.md`
- `skills/`

These files are what make the system adapt to the repo instead of acting like a generic assistant.

## Recommended Commands

Daily commands:

```bash
./ai-dev-system/bin/ai-dev project-setup all
./ai-dev-system/bin/ai-dev project-work "task description"
./ai-dev-system/bin/ai-dev project-health
./ai-dev-system/bin/ai-dev project-status
```

Useful project commands:

```bash
./ai-dev-system/bin/ai-dev update-project-memory
./ai-dev-system/bin/ai-dev update-docs-from-source
./ai-dev-system/bin/ai-dev project-doc-health
./ai-dev-system/bin/ai-dev project-dedupe-report
./ai-dev-system/bin/ai-dev save-session "checkout bugfix" "re-run verification after the pricing fix"
./ai-dev-system/bin/ai-dev resume-session
./ai-dev-system/bin/ai-dev scaffold-project-skill "domain rules" "Project-specific business rules for checkout flow"
```

System commands:

```bash
./ai-dev-system/bin/ai-dev doctor
./ai-dev-system/bin/ai-dev registry-health
./ai-dev-system/bin/ai-dev system-refresh
./ai-dev-system/bin/ai-dev portable-release
./ai-dev-system/bin/ai-dev search-skill "database migration"
./ai-dev-system/bin/ai-dev search-role "security review"
./ai-dev-system/bin/ai-dev search-workflow "verify"
./ai-dev-system/bin/ai-dev freeze-sources
```

## Portable Upstream Model

On your main machine, where you keep upstream reference repos, you can refresh and curate the system with a single command:

```bash
./ai-dev-system/bin/ai-dev system-refresh
```

When you want to prepare a fresh portable copy for distribution or copying into projects, run:

```bash
./ai-dev-system/bin/ai-dev portable-release
```

This:

- copies referenced upstream source files into `ai-dev-system/shared/sources/upstream/repos/`
- rewrites local source metadata to use the frozen copies
- keeps original upstream paths for traceability
- allows copied project installs to work without `ai-repos/`

In practice:

- main machine: keep `ai-repos/`, curate, refresh, freeze
- project repos: copy only `ai-dev-system/`

## Professional Defaults

This system is already tuned around a few important constraints:

- same-language final responses
- project-first routing before generic skills
- smallest sufficient set of skills, roles, and workflows
- post-compaction recovery of goal, plan, touched files, verification, and risks
- frozen upstream traceability without dragging full source repos into each project

## Team Roles And Workflow Coverage

Role files live in [ai-dev-system/team-dev/roles](ai-dev-system/team-dev/roles).

Current role coverage includes:

- `orchestrator`
- `explorer`
- `architect`
- `tech-lead`
- `project-planner`
- `product-manager`
- `frontend-engineer`
- `frontend-specialist`
- `backend-engineer`
- `backend-specialist`
- `database-architect`
- `qa-engineer`
- `qa-automation`
- `reviewer`
- `security-auditor`
- `security-reviewer`
- `devops-engineer`
- `code-archaeologist`
- `a11y-architect`
- `e2e-runner`
- `build-error-resolver`
- `doc-updater`
- `code-explorer`
- `code-reviewer`
- `performance-optimizer`
- `debugger`
- `documentation-writer`
- `mobile-developer`

See [AGENT_SELECTION.md](ai-dev-system/team-dev/orchestration/AGENT_SELECTION.md) for role selection guidance.

## Upstream Collection Strategy

The system follows an `ECC-first` collection strategy without hard-locking everything to a single source.

Current intent:

- preferred upstream: `ai-repos/everything-claude-code`
- secondary sources: `openai-skills`, `antigravity-kit`, `agent-skills`
- large catalogs are used mainly for discovery, not as the default active core
- project-local skills are still allowed when the repo has unique domain rules

Integrated ECC-focused additions include:

- task skills: `accessibility`, `e2e-testing`
- roles: `a11y-architect`, `e2e-runner`, `code-explorer`, `code-reviewer`, `doc-updater`, `build-error-resolver`
- upgraded roles: `project-planner`, `performance-optimizer`
- workflows: `code-review`, `update-docs`, `build-fix`, `test-coverage`

The policy file lives at [source-strategy.json](ai-dev-system/shared/registry/source-strategy.json).

## Main-Machine Maintenance

These are mainly for the machine where you keep `ai-repos/` and curate the system itself:

```bash
./ai-dev-system/bin/ai-dev system-refresh
./ai-dev-system/bin/ai-dev portable-release
./ai-dev-system/bin/ai-dev doctor
```

The root `scripts/` folder is optional convenience tooling for maintaining this repository itself. It is not required inside copied project repos.

There are no required top-level wrapper scripts anymore. Maintenance helpers live under `scripts/`, and portable project usage lives entirely inside `ai-dev-system/`.

See [scripts/README.md](scripts/README.md) for the short maintenance-vs-portable split.

## Repository Layout

```text
.ai-system/
├── ai-dev-system/
│   ├── AI_ENTRY.md
│   ├── bin/ai-dev
│   ├── solo-dev/
│   ├── team-dev/
│   ├── shared/
│   └── packs/
├── ai-repos/
└── scripts/
```

Main entry points:

- [AI_ENTRY.md](ai-dev-system/AI_ENTRY.md)
- [AI_DEV.md](ai-dev-system/solo-dev/AI_DEV.md)
- [AI_TEAM.md](ai-dev-system/team-dev/AI_TEAM.md)
- [ai-dev](ai-dev-system/bin/ai-dev)

## Publishing Guidance

Usually safe to publish:

- `ai-dev-system/`
- `README.md`
- `README_VI.md`
- root `.gitignore`
- root maintenance scripts, if they do not contain secrets

Usually better not to publish:

- `ai-repos/`
- private project copies that include business-specific `.ai-dev-system/` data
- session history, temporary task briefs, or private project memory
- any file containing secrets, tokens, internal URLs, or client-specific architecture

Safest publishing model:

- publish the reusable system
- keep upstream clones local
- keep per-project generated context private unless intentionally curated
