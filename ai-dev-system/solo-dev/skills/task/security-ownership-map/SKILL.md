---
name: security-ownership-map
description: Analyze git history to identify security-sensitive code ownership, bus-factor hotspots, orphaned areas, and CODEOWNERS drift.
category: task
intent:
  - security_review
  - legacy_discovery
  - architecture
roles:
  - security
  - explorer
mode: full
risk: high
source_repo: openai-skills
source_path: skills/.curated/security-ownership-map/SKILL.md
confidence: high
---

# Security Ownership Map

Use this skill when the user wants a security-oriented ownership analysis grounded in git history, not just a maintainer list.

## Trigger

Activate for questions like:

- Which sensitive areas have low bus factor?
- Who actually owns auth or crypto code?
- Where does CODEOWNERS differ from reality?
- Which security-sensitive files are effectively orphaned?

Do not use this for generic contributor summaries.

## Core Questions

1. Which files or modules are security-sensitive?
2. Who has touched them most and most recently?
3. Are there hotspots owned by one person only?
4. Are there stale sensitive files with weak ownership?
5. Do actual commit patterns disagree with CODEOWNERS?

## Lightweight Workflow

1. Define scope and time window.
   - default to the last 12 months unless the repo history is sparse
2. Identify sensitive paths.
   - `auth/`, `crypto/`, `secrets/`, `permissions/`, `payments/`, key management, certs, infra access
3. Use git history to extract:
   - top contributors by sensitive area
   - recency of touches
   - single-owner or low-owner hotspots
4. Cross-check with `CODEOWNERS` if present.
5. Report:
   - orphaned sensitive code
   - hidden owners
   - bus-factor hotspots
   - ownership drift

## If Full Tooling Is Wanted

Primary source skill supports richer graph output with CSV/JSON and graph tooling.
Use that deeper path only when the user explicitly wants exports, visualization, or repeated ownership analysis.

## Output Format

```text
Security Ownership Map
- Scope:
- Sensitive areas reviewed:

Hotspots
- <path>: bus factor, primary owners, last sensitive touch

Ownership drift
- <area>: CODEOWNERS says X, history suggests Y

Orphaned sensitive code
- <path>: stale since <date>, low ownership depth

Recommended actions
- ...
```

## Guardrails

- Ground findings in git history, not intuition
- Mention the time window used
- Separate recent ownership from historical ownership
- Avoid overclaiming exact control percentages unless computed
- Treat this as sensitive analysis and keep outputs concise by default
