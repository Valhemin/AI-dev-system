# Router

## Mandatory order

1. Use LANGUAGE_ROUTER.
2. Use MODE_ROUTER to select QUICK / HYBRID / FULL.
3. **Complexity Check**: If task involves architecture, security, or >3 files, trigger `advanced-reasoning-cot`.
4. **Autonomous Ops**: 
   - If build/test fails, trigger `self-healing`.
   - If task is complete, trigger `pr-architect`.
   - If code quality is a concern, trigger `tech-debt-audit`.
5. **Context Check**: If history > 10k tokens, trigger `context-pruning`.
5. Respect explicit user request.
6. Detect intent, stack, and problem.
7. Read SKILL_INDEX.
8. Select:
   - max 1 task skill
   - max 1 stack skill
   - max 1 problem skill
   - max 1 role for FULL/team mode
9. If request says plan, orchestrate, team, multi-agent, review, test, preview, quality gate, verify, or context budget, inspect workflow/role packs before leaf inventory.
10. Load full SKILL.md or active role/workflow only after selection.

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

