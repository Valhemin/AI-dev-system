---
name: e2e-testing
description: Portable end-to-end testing skill for critical user journeys. Use when creating, fixing, or reviewing Playwright-style E2E coverage, flaky tests, or browser-based regression checks.
---

# E2E Testing

Portable E2E testing guidance for critical user flows, with Playwright-oriented patterns and flaky-test hygiene.

Source: shared/frozen-sources/repos/everything-claude-code/skills/e2e-testing/SKILL.md (upstream: ai-repos/everything-claude-code/skills/e2e-testing/SKILL.md)

## When to Use

- Add or fix end-to-end tests
- Cover login, checkout, payments, CRUD, search, or onboarding
- Investigate flaky browser tests
- Improve artifact capture, retries, or CI reliability

## Core Protocol

1. Start from the user journey, not the DOM tree.
2. Prefer stable selectors such as `data-testid`.
3. Wait for conditions or network effects, never arbitrary sleeps.
4. Keep tests isolated and repeatable.
5. Capture artifacts on failure: screenshot, trace, video, or HTML report.

## Default Coverage Priorities

- Authentication and session flows
- Revenue or checkout flows
- Critical CRUD flows
- Error states that affect user trust

## Common Anti-Patterns

- `waitForTimeout()` as a synchronization strategy
- Shared mutable state between tests
- CSS selectors tightly coupled to styling
- Large end-to-end suites for behavior better covered by integration tests

## Output

When using this skill, return:

- critical journeys covered
- gaps still uncovered
- flake risks or environment assumptions
