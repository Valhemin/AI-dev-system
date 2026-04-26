---
name: code-review
description: Portable workflow for reviewing changed code for bugs, security, and maintainability. Prefer this after meaningful code changes or before merge/release.
---

# code-review

Portable workflow for focused review of recent changes.

Source: shared/frozen-sources/repos/everything-claude-code/.opencode/commands/code-review.md (upstream: ai-repos/everything-claude-code/.opencode/commands/code-review.md)

## Portable Protocol

1. Gather the diff or changed files.
2. Read surrounding code, not only the patch.
3. Prioritize high-confidence findings:
   - bugs
   - regressions
   - security issues
   - missing tests
   - maintainability risks
4. Report findings by severity with concrete fix direction.
5. Keep style-only comments secondary unless they violate project conventions.

## Context Rule

Do not turn review into a generic rewrite plan. Focus on the current change set.
