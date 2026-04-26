---
name: build-fix
description: Portable workflow for fixing build and typecheck failures with minimal diffs. Prefer this when compilation, imports, config, or dependency errors block progress.
---

# build-fix

Portable workflow for getting builds green quickly and safely.

Source: shared/frozen-sources/repos/everything-claude-code/.opencode/commands/build-fix.md (upstream: ai-repos/everything-claude-code/.opencode/commands/build-fix.md)

## Portable Protocol

1. Run the real build/typecheck path and collect all errors.
2. Categorize:
   - type errors
   - import/module errors
   - config errors
   - dependency resolution errors
3. Fix with the smallest safe diff first.
4. Re-run checks after each meaningful fix.
5. Stop when the build is green or when the remaining issue requires architectural change.

## Guardrails

- No broad refactor while in build-fix mode.
- No speculative improvements.
- Preserve behavior unless the error itself requires logic correction.
