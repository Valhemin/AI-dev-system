---
name: task-briefing
description: Lightweight pre-task briefing. Use before non-trivial work to classify task complexity, read the right project docs first, and choose the smallest sufficient set of skills, workflows, and roles.
allowed-tools: Read, Glob, Grep
source_repo: antigravity/skills
source_type: community
---

# Task Briefing

Use this workflow before moderate, complex, or risky work.

## When To Use

- The task touches multiple files, flows, or layers.
- The task mentions architecture, refactor, deploy, auth, payment, migration, or performance.
- The project has `.ai-dev-system/project-routing.md` or `docs/project-context/`.
- You want to avoid over-loading unrelated skills before starting.

## Do Not Use

- Tiny single-file edits with obvious scope.
- Simple factual questions.
- Straightforward follow-up work where the active context is already correct.

## Briefing Protocol

1. Classify the task as `simple`, `moderate`, `complex`, or `critical`.
2. Read the smallest useful project context first:
   - `.ai-dev-system/project-routing.md`
   - `.ai-dev-system/project-profile.md`
   - `.ai-dev-system/project-memory.json`
   - `.ai-dev-system/current-task-brief.md` when present and relevant
3. Select the smallest sufficient set:
   - 1 primary task skill
   - 0-2 stack/problem skills
   - 0-1 workflow
   - 0-2 roles only if the task really benefits from them
4. Name the likely verification path before coding.
5. Call out risks or stale assumptions before execution.

## Output Shape

Write or think in this compact structure:

```markdown
Task: <one-line summary>
Complexity: simple|moderate|complex|critical
Read First:
- <doc 1>
- <doc 2>
Use:
- <task skill>
- <stack/problem skill>
- <workflow or role if needed>
Verify:
- <command or check>
Risks:
- <main risk>
```

## Guardrails

- Prefer routing and project docs before loading generic leaf skills.
- If more than 4 skills/roles/workflows are selected, re-trim.
- If the task is project-specific, check local skills only after active core.
- If the task is critical, pause to confirm irreversible impact.

## Limitations

- This workflow improves selection quality, not execution quality by itself.
- It does not replace verification, testing, or project-specific validation.
