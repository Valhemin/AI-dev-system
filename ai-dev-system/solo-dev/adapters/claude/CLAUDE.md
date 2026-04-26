# Claude Adapter

Use ai-dev-system.

Primary entry:
- AI_ENTRY.md

Important:
- QUICK / HYBRID / FULL first.
- Do not load all files.
- Check `.ai-dev-system/project-profile.md` and related project docs when present.
- Check `.ai-dev-system/project-memory.json` for stable project facts when present.
- Check `.ai-dev-system/project-routing.md` to decide which project docs to read first when present.
- Check `.ai-dev-system/current-task-brief.md` first when present for non-trivial active work.
- Check `.ai-dev-system/custom-skill-index.json` before loading project-local skills.
- Prefer `.ai-dev-system/skills/*/SKILL.md` over generic leaf skills only when the task is clearly project-specific.
- Read SKILL_INDEX before full skills.
- Load selected skill only.
- Use LANGUAGE_ROUTER.
- Reply in the user's latest primary language.
- Run SELF_CHECK if context was compacted or behavior drifts.
