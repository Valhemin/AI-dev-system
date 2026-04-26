---
name: accessibility
description: Portable accessibility skill for auditing and implementing WCAG 2.2 AA improvements across web UI. Use when a task involves a11y, keyboard navigation, focus flow, ARIA, semantics, contrast, or inclusive UX.
---

# Accessibility

Portable skill for improving accessibility without turning every UI task into a full design audit.

Source: shared/frozen-sources/repos/everything-claude-code/skills/accessibility/SKILL.md (upstream: ai-repos/everything-claude-code/skills/accessibility/SKILL.md)

## When to Use

- Accessibility audit or review
- ARIA and semantic HTML fixes
- Focus management in modals, menus, and dialogs
- Keyboard navigation and target size issues
- Contrast, labels, hints, and live regions

## Core Protocol

1. Prefer native semantic elements before custom roles.
2. Check keyboard flow and visible focus before polishing visuals.
3. Add accessible names for icon-only and non-text controls.
4. Fix dynamic announcements with `aria-live` or equivalent status regions.
5. Verify the user journey, not just isolated elements.

## Minimum Checklist

- All interactive controls have a clear accessible name.
- Focus order is logical and trapped where required.
- Keyboard-only use is possible for the target flow.
- Contrast is acceptable for text and UI states.
- Error and status messages are announced clearly.
- Tap and click targets are not too small.

## Common Anti-Patterns

- Clickable `div` instead of native button or link
- Icon-only buttons without labels
- Modal focus escaping to background content
- Status indicated only by color
- Hidden text or placeholders used as the only label

## Output

Return:

- the user-facing issue
- the concrete fix
- any residual accessibility risk
