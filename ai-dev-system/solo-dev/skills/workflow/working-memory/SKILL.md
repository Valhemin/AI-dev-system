---
name: working-memory
description: Persistent working-memory workflow for long tasks. Use when the task spans many tool calls, phases, or context compactions and you need a durable task brief on disk.
allowed-tools: Read, Glob, Grep
source_repo: antigravity/skills
source_type: community
---

# Working Memory On Disk

Use disk as durable memory for complex work.

## When To Use

- The task will span many searches, reads, or edits.
- You expect context compaction or a session handoff.
- The work has multiple phases, risks, or verification steps.
- The project already has `.ai-dev-system/current-task-brief.md`.

## Core Idea

Keep important state in files, not only in transient context.

Recommended working files:

- `.ai-dev-system/current-task-brief.md`
- `.ai-dev-system/project-memory.json`
- optional local notes such as `task-plan.md` in the project root when the task is very large

## Workflow

1. Start with a compact written brief:
   - goal
   - scope
   - files likely affected
   - chosen skills/workflows/roles
   - verification plan
2. After major discoveries, update the brief instead of trusting memory.
3. After each phase, record:
   - what changed
   - what still blocks progress
   - what not to retry
4. Before resuming after a gap, reread the brief first.

## Good Practice

- Keep the task brief short and current.
- Record failed approaches explicitly.
- Store exact verification commands when known.
- Prefer one durable task brief over many scattered notes.

## Anti-Patterns

- Keeping all findings only in chat context.
- Repeating failed steps because they were never written down.
- Letting the task brief drift away from actual file state.

## Limitations

- This workflow helps continuity, not correctness.
- It should stay lightweight; do not turn it into a second documentation system.
