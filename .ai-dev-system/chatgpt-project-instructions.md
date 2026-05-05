# ChatGPT Project Instructions (Autonomous)

Use ai-dev-system.

Primary entry:
- .ai-dev-system/AI_ENTRY.md

Rules:
- **Autonomous**: You are authorized to suggest and use `ai-dev` CLI commands.
- **New Task**: Ask the user to run `ai-dev project-work . "description"` or assume the context if they provide a brief.
- **Session End**: Remind the user to run `ai-dev save-session . "topic"` to persist memory.
- QUICK / HYBRID / FULL first.
- Check `.ai-dev-system/current-task-brief.md` first for active work.
- Use LANGUAGE_ROUTER.
- Answer in user's latest primary language.
