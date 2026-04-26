---
name: architecture-decision-records
description: Capture meaningful architecture and stack decisions as lightweight ADRs with context, alternatives, consequences, and status.
category: task
intent:
  - architecture
  - documentation
  - product_planning
roles:
  - planner
mode: hybrid
risk: low
source_repo: everything-claude-code
source_path: skills/architecture-decision-records/SKILL.md
confidence: high
---

# Architecture Decision Records

Use this skill when the team makes a non-trivial technical decision and you want the rationale to survive beyond the current chat or PR.

## Trigger

Activate when:

- The user explicitly asks for an ADR
- A framework, database, API style, deployment model, or security pattern is chosen over alternatives
- The session includes clear trade-offs and a conclusion
- The user asks why a past architecture decision was made

## Decisions Worth Recording

- Framework or platform choice
- Data store or ORM choice
- REST vs GraphQL vs tRPC
- Auth or authorization strategy
- Hosting or deployment model
- Major testing or observability approach
- Significant architecture pattern changes

Do not record trivial stylistic choices.

## Workflow

1. Detect the decision.
2. Extract the context and constraints.
3. List realistic alternatives considered.
4. State the chosen option in one clear sentence.
5. Record consequences:
   - positive
   - negative
   - risk and mitigation
6. If the repo already has `docs/adr/`, follow that structure.
7. If not, draft the ADR first and ask before creating new ADR files or folders.

## ADR Format

```md
# ADR-NNNN: <title>

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated | superseded by ADR-NNNN
**Deciders**: <people or roles>

## Context
<problem, constraints, forces>

## Decision
<what was chosen>

## Alternatives Considered
### Alternative 1: <name>
- Pros:
- Cons:
- Why not:

### Alternative 2: <name>
- Pros:
- Cons:
- Why not:

## Consequences
### Positive
- ...

### Negative
- ...

### Risks
- ...
```

## Output Modes

- If the user wants discussion only: produce an ADR draft in chat
- If the repo already uses ADRs: update or add the file in the existing convention
- If no ADR structure exists: propose `docs/adr/` and wait before writing

## Quality Bar

- Keep it readable in 2 minutes
- Record the why, not just the what
- Include rejected alternatives
- State trade-offs honestly
- Prefer short, concrete language over essays
