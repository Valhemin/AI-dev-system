# Language Router

This rule is mandatory.

For every request:

1. Detect the user's primary language.
2. If not English:
   - internally translate only routing-relevant phrases into English
   - use that English meaning to map intent, mode, role, skill, workflow, risk
3. Keep code, logs, stack traces, commands, paths, package names, APIs, identifiers unchanged.
4. Final answer must be in the same primary language as the user's latest request, unless explicitly requested otherwise.

Do not expose internal translation unless the user asks.

