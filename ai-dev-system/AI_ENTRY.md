# AI_ENTRY

Lean default entry. Keep initial context near 1-2k tokens.

## Load order

1. shared/router/LANGUAGE_ROUTER.md
2. shared/router/MODE_ROUTER.md
3. shared/router/ROUTER.md
4. shared/registry/SKILL_INDEX.md
5. solo-dev/rules/CORE.md
6. selected SKILL.md only
7. Optional selected role/workflow only when routed
8. If no active skill fits: search shared/registry/catalog.json or relevant packs/*/catalog.json
9. solo-dev/rules/SELF_CHECK.md when context is compacted or drifting

## Decision

Choose one:

- QUICK: one file, isolated change, no architecture, low risk
- HYBRID: 2-3 files, one layer, clear change, low/medium risk
- FULL: many files, cross-layer, new screen/service/API, architecture, unclear scope, production/security/data/deployment risk

## Mapping

- QUICK -> solo-dev
- HYBRID -> solo-dev + compact review
- FULL -> team-dev with selected roles only

## Team / workflow routing

- Select at most 1 role: orchestrator, explorer, frontend, backend, database, QA, security, DevOps, or legacy discovery.
- Select at most 1 workflow: plan, create, debug, test, preview, deploy, orchestrate, quality-gate, verify, context-budget, multi-plan, or multi-execute.
- Use packs/roles, packs/workflows, and packs/rules only after active core is insufficient.

## Behavior

- Default to QUICK when safe.
- Do not over-engineer.
- Select skills by metadata first.
- Load full skill, role, or workflow only when selected.
- Prefer active core. Use pack catalog before leaf inventory.
- Always answer in the user's latest primary language.
- Keep code, logs, commands, paths, package names, and APIs unchanged.

## Default output

1. Mode: QUICK / HYBRID / FULL
2. Routing: selected skills/roles
3. Plan or root cause
4. Action / implementation
5. Verification
6. Risk

