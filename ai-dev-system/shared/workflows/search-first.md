---
name: search-first
description: Portable research-before-build workflow. Check the repo, available skills, packages, and primary-source docs before writing custom code or adding a new abstraction.
---

# search-first

Portable research-before-build workflow.

Source: shared/frozen-sources/repos/everything-claude-code/skills/search-first/SKILL.md (upstream: ai-repos/everything-claude-code/skills/search-first/SKILL.md)

## When To Use

- Starting a new feature that might already have an established solution
- Considering a new dependency or tool
- About to create a helper, utility, wrapper, or custom integration
- Evaluating whether existing repo code can be reused

## Workflow

1. Search the current repo first.
   - Look for existing modules, tests, scripts, patterns, and utilities.
   - Prefer reuse over reinvention.
2. Search current project capabilities.
   - Existing skills
   - Existing plugins or MCP tools
   - Existing package dependencies
3. Search external primary sources.
   - Official docs
   - Official package registries
   - Maintained source repos
4. Score options.
   - Exact fit
   - Maintenance quality
   - License
   - Dependency weight
   - Upgrade risk
5. Choose one path.
   - Adopt as-is
   - Wrap or extend
   - Compose small building blocks
   - Build custom only if needed

## Decision Rules

- If the repo already has a working pattern, follow it.
- If a mature lightweight dependency solves the problem, prefer adoption.
- If a package is huge for a tiny use case, reconsider.
- If official docs are weak or maintenance is stale, avoid locking in.

## Output Format

```text
Search-first result
- Need:
- Existing repo option:
- External options considered:
- Recommendation: adopt / wrap / build
- Why:
- Risks:
```
