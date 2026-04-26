# Skill Spec

A skill is a reusable capability stored as:

```txt
skill-name/
  SKILL.md
  scripts/
  references/
```

Required frontmatter:

```md
---
name: skill-name
description: Clear trigger condition and task scope.
category: task|language|framework|problem|role|workflow|other
intent:
  - bug_fix
  - feature_dev
stacks:
  - typescript
roles:
  - implementer
mode: quick|hybrid|full
risk: low|medium|high
---
```

Rules:
1. Select by metadata first.
2. Load full SKILL.md only when selected.
3. Prefer community skill.
4. Use generated fallback only if no good community skill exists.
5. Keep fallback skills compact.
6. Do not load all skills into context.
7. Preserve scripts/, references/, and assets/ when importing community skills.
8. Reject or flag imported skills whose name/description do not match the target slot.

Recommended metadata:
- source_repo
- source_path
- source_commit
- source_license
- confidence: high|medium|low
- requires_approval: true|false
- tools
- inputs
- outputs

