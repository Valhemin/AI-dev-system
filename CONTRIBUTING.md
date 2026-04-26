# Contributing

Thanks for contributing to AI System.

This repository is meant to stay portable, practical, and easy to copy into real projects, so contributions should improve usefulness without making the system noisy or bloated.

## Principles

- Prefer the smallest sufficient change.
- Keep portable project use as the default experience.
- Favor project-aware behavior over generic prompt sprawl.
- Do not add new skills, roles, or commands unless they solve a clear gap.
- Prefer curated, reusable improvements over one-off complexity.

## What Makes A Good Contribution

- Better project-aware routing, memory, or task-brief behavior
- Improvements to `ai-dev-system/bin/ai-dev` or internal scripts
- Higher-quality imported skills or role curation from upstream sources
- Better documentation for real project usage
- Safer maintenance flows for refresh, freeze, and portability

## Before You Add A New Skill, Role, Or Command

Check these first:

- Does something similar already exist in the active core?
- Can this be handled by project docs or a project-local skill instead?
- Is it broadly reusable, or only useful for one narrow case?
- Will it improve routing quality, or just increase catalog size?

If the answer is mostly "more surface area" instead of "better decisions", it probably should not be added.

## Recommended Workflow

1. Make the smallest practical change.
2. Keep edits inside `ai-dev-system/` unless you are working on source-repo maintenance.
3. Update `README.md` if the public workflow changes.
4. Update `README_VI.md` when the Vietnamese guide should stay aligned.
5. Run the relevant verification commands.

## Useful Commands

Project-facing checks:

```bash
./ai-dev-system/bin/ai-dev doctor
./ai-dev-system/bin/ai-dev eval-routing
./ai-dev-system/bin/ai-dev registry-health
```

Main-machine maintenance:

```bash
./ai-dev-system/bin/ai-dev update-repos
./ai-dev-system/bin/ai-dev refresh-catalog
./ai-dev-system/bin/ai-dev freeze-sources
```

## Pull Request Guidance

- Explain the problem being solved.
- Keep change scope focused.
- Mention any routing, portability, or maintenance tradeoffs.
- Include command results when relevant.
- Note whether the change affects copied project installs, main-machine maintenance, or both.

## Scope Boundaries

Usually in scope:

- improvements to `ai-dev-system/`
- internal script quality
- curation quality
- docs quality

Usually out of scope:

- checking in `ai-repos/`
- publishing private project-generated `.ai-dev-system/` artifacts
- adding heavy dependencies without a strong reason

## Questions To Ask Before Merging

- Does this make copied project installs better?
- Does this preserve the "copy only `ai-dev-system/`" workflow?
- Does this reduce confusion or increase it?
- Does this help the AI choose better, not just know more?
