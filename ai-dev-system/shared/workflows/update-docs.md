---
name: update-docs
description: Portable workflow for updating documentation alongside code changes. Prefer this when README, guides, runbooks, API docs, or generated project docs need to match implementation.
---

# update-docs

Portable workflow for keeping documentation in sync with code changes.

Source: shared/frozen-sources/repos/everything-claude-code/.opencode/commands/update-docs.md (upstream: ai-repos/everything-claude-code/.opencode/commands/update-docs.md)

## Portable Protocol

1. Identify changed code and source-of-truth files first.
2. Find the smallest relevant docs set: README, runbook, guides, API docs, codemaps.
3. Update docs from implementation reality, not guesses.
4. Verify commands, examples, paths, and links where practical.
5. Report what changed and any stale docs that still need manual review.

## Context Rule

Prefer project-local docs and `.ai-dev-system/` docs before broad repo-wide doc edits.
