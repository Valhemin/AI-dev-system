# Router

## Mandatory order

1. Use LANGUAGE_ROUTER.
2. Use MODE_ROUTER to select QUICK / HYBRID / FULL.
3. Respect explicit user request:
   - if user says solo-dev, avoid FULL unless high-risk
   - if user says team-dev, use FULL or HYBRID-team depending on scope
4. Detect intent.
5. Detect stack.
6. Detect problem.
7. Detect optional workflow and role.
8. Read SKILL_INDEX.
9. Select:
   - max 1 task skill
   - max 1 stack skill: language or framework
   - max 1 problem skill
   - max 1 role for FULL/team mode
   - optional workflow
10. If request says plan, orchestrate, team, multi-agent, review, test, preview, quality gate, verify, or context budget, inspect workflow/role packs before leaf inventory.
11. If no active core item fits, inspect relevant packs/*/catalog.json.
12. Load leaf inventory item only after pack catalog selection.
13. Load full SKILL.md or active role/workflow only after selection.

## Intent list

- bug_fix
- feature_dev
- refactor
- code_review
- testing
- documentation
- architecture
- product_planning
- incident_debug
- security_review
- deployment
- orchestration
- preview
- quality_gate
- context_budget
- legacy_discovery

## Overengineering guard

Default to QUICK when safe.
Use HYBRID when change touches a few files but remains one layer.
Use FULL only when scope/risk requires it.

