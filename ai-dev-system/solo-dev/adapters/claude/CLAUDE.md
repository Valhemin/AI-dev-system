# Claude Adapter (Autonomous)

Use ai-dev-system.

Primary entry:
- .ai-dev-system/AI_ENTRY.md

Rules:
- **Autonomous**: You are authorized to run `ai-dev` CLI commands.
- **New Task**: Run `ai-dev project-work . "description"` immediately when a new task is identified.
- **Session End**: Run `ai-dev save-session . "topic"` after finishing significant work.
- QUICK / HYBRID / FULL first.
- Check `.ai-dev-system/current-task-brief.md` first for active work.
- Read SKILL_INDEX before full skills.
- Use LANGUAGE_ROUTER.
- Reply in the user's latest primary language.
- Run SELF_CHECK if context was compacted or behavior drifts.
