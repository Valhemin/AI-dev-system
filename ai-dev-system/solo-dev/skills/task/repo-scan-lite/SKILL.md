---
name: repo-scan-lite
description: Lightweight repository asset audit for ownership, dead weight, vendored code, duplicated modules, and refactor candidates without requiring external repo-scan tooling.
category: task
intent:
  - legacy_discovery
  - architecture
  - code_review
roles:
  - explorer
mode: hybrid
risk: low
source_repo: everything-claude-code
source_path: skills/repo-scan/SKILL.md
confidence: medium
---

# Repo Scan Lite

Use this skill when you need a fast structural audit of a repo before refactor, takeover, or cleanup, but do not want to install external tooling.

## Goals

- Estimate what code is project-owned vs vendored vs generated
- Find suspiciously large or stale directories
- Detect duplicated wrappers or near-identical modules
- Surface dead-weight build artifacts committed to the repo
- Produce a short verdict per module or area

## Fast Audit Workflow

1. Enumerate the repo surface.
   - top-level directories
   - unusually large directories
   - generated or build artifact folders
2. Classify files into rough buckets:
   - project code
   - third-party or vendored code
   - generated/build artifacts
   - docs/config/scripts
3. Identify risk signals:
   - duplicated modules
   - vendored libraries with old version markers
   - committed build output
   - stale subsystems with no recent touches if git history is available
4. Group findings by subsystem.
5. Assign one verdict:
   - core asset
   - extract and merge
   - rebuild
   - deprecate

## Heuristics

Look for:

- directories like `vendor/`, `third_party/`, `dist/`, `build/`, `coverage/`, `generated/`
- repeated file names or wrappers across multiple packages
- lockfiles or config indicating split ownership patterns
- license files or headers suggesting vendored code
- asset weight that is large relative to source code

## Output Format

```text
Repo Scan Lite
- Scope:
- Major areas:
- Project-owned code:
- Vendored/third-party code:
- Generated/build artifacts:

Module verdicts
- <module>: core asset | extract and merge | rebuild | deprecate

Top risks
- ...

Refactor opportunities
- ...
```

## Guardrails

- Prefer cheap file-system and grep signals first
- Do not claim exact ownership percentages unless measured
- Be explicit when a verdict is inferred rather than proven
- Escalate to deeper audit only if the lightweight scan finds real risk
