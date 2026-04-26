---
name: multi-execute
description: Portable coordinated execution workflow for independent tasks, role handoffs, and final synthesis.
---

# multi-execute

Portable coordinated execution workflow for independent tasks, role handoffs, and final synthesis.

Source: shared/frozen-sources/repos/everything-claude-code/commands/multi-execute.md (upstream: ai-repos/everything-claude-code/commands/multi-execute.md)

## Portable Protocol

1. Classify the request and confirm this workflow is selected.
2. Load only relevant active skills, roles, pack catalogs, or leaf files.
3. Translate source-specific commands into the current AI/runtime capabilities.
4. Execute the smallest useful workflow slice.
5. Verify with concrete checks and report residual risk.

## Context Rule

Do not paste or load full source workflow content unless this active workflow is insufficient.
Use the source path or catalog item as leaf context only when needed.
