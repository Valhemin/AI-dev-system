# Solo Core Rules

1. **Autonomous Briefing**: If the user describes a new task or change, immediately run `ai-dev project-work . "task description"` to sync context and update the brief before implementation.
2. **Context First**: Before any action, verify if current context is sufficient. Use `context-pruning` if history is too long.
3. **Inspect before editing**: Always read the file and its dependencies.
4. **Minimal diff**: Change only what is necessary.
5. **Reasoning Path**: For complex tasks, use `advanced-reasoning-cot` to explain the "Why" before the "How".
6. **Auto-Save**: After completing a significant change, run `ai-dev save-session . "topic"` to persist memory.
7. **Language**: Reply in the user's latest primary language.
8. **Integrity**: Keep code/logs/commands/paths/package names unchanged.
9. **Self-Correction**: If behavior drifts, run `SELF_CHECK.md` immediately.
