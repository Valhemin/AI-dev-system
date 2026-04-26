---
name: test-coverage
description: Portable workflow for analyzing coverage gaps and prioritizing missing tests. Prefer this when quality gates mention coverage or when critical flows lack tests.
---

# test-coverage

Portable workflow for coverage analysis and targeted test planning.

Source: shared/frozen-sources/repos/everything-claude-code/.opencode/commands/test-coverage.md (upstream: ai-repos/everything-claude-code/.opencode/commands/test-coverage.md)

## Portable Protocol

1. Run the project's real coverage command when available.
2. Identify low-coverage areas and rank by risk:
   - auth/security
   - payments/financial logic
   - core business flows
   - reusable utilities
3. Propose or add tests for the highest-value uncovered paths first.
4. Prefer meaningful assertions over chasing raw percentages.
5. Report remaining gaps and the next best test targets.

## Guardrails

- Coverage is a signal, not the goal by itself.
- Prefer critical-path tests over broad low-value snapshot churn.
