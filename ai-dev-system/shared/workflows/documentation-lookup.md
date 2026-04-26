---
name: documentation-lookup
description: Portable workflow for answering framework and library questions from current primary-source documentation instead of stale memory.
---

# documentation-lookup

Portable workflow for current documentation lookup.

Source: shared/frozen-sources/repos/everything-claude-code/skills/documentation-lookup/SKILL.md (upstream: ai-repos/everything-claude-code/skills/documentation-lookup/SKILL.md)

## When To Use

- The request depends on exact library or framework behavior
- The user asks for setup, configuration, API usage, or version-specific guidance
- A package, SDK, framework, or hosted platform is named explicitly
- Accuracy matters more than speed

## Source Priority

1. Local project docs and lockfiles
2. Official documentation
3. Official source repository
4. Trusted primary examples

Do not rely on recollection alone for version-sensitive answers.

## Workflow

1. Identify the exact library, framework, or platform.
2. Detect version from the repo when possible.
3. Query primary-source docs for the exact question.
4. Cross-check examples against the detected project version.
5. Answer with:
   - the current recommended approach
   - version notes when relevant
   - minimal working example
   - source link or citation

## Guardrails

- Prefer official docs over blog posts.
- Mention uncertainty if version cannot be confirmed.
- Redact secrets from queries and examples.
- Keep copied snippets short and adapt them to the user's stack.
