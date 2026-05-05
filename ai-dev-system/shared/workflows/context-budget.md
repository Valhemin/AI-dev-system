---
name: context-budget
description: Portable context economy workflow for reducing token usage while preserving routing and task-critical facts.
---

# context-budget

Portable context economy workflow for reducing token usage while preserving routing and task-critical facts.

Source: shared/frozen-sources/repos/everything-claude-code/commands/context-budget.md (upstream: ai-repos/everything-claude-code/commands/context-budget.md)

## Portable Protocol

1. **Audit**: Check current token usage (if available) or conversation length.
2. **Prune**: Remove redundant file reads or old reasoning blocks.
3. **Summarize**: Replace long chat history with a "State Summary" (Goal, Progress, Next Step).
4. **Compact**: Use `context-pruning` skill to clean up the environment.
5. **Verify**: Ensure critical facts (architecture, conventions) are still present.

## Context Rule

Do not paste or load full source workflow content unless this active workflow is insufficient.
Use the source path or catalog item as leaf context only when needed.
