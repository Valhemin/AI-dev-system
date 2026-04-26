Use ai-dev-system.

Primary entry:
- AI_ENTRY.md

Rules:
- choose QUICK / HYBRID / FULL first
- check `.ai-dev-system/project-profile.md` and related project docs when present
- check `.ai-dev-system/project-memory.json` for stable project facts when present
- check `.ai-dev-system/project-routing.md` to decide which project docs to read first when present
- check `.ai-dev-system/current-task-brief.md` first when present for non-trivial active work
- check `.ai-dev-system/custom-skill-index.json` before loading project-local skills
- prefer `.ai-dev-system/skills/*/SKILL.md` only for repo-specific behavior not covered by active core
- use LANGUAGE_ROUTER
- answer in user's latest primary language
- keep code/logs/commands/paths/package names unchanged
- route, select skills, then execute with minimal context
