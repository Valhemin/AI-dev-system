---
name: async-debug
description: async/await, coroutine, event loop, threading, deadlock, GUI async integration, and concurrency bugs.
---

# async-debug

## Purpose

Use this compact fallback skill when no suitable community skill is imported.

## Workflow

1. Identify event loop ownership.
2. Identify sync/async boundary.
3. Find blocking calls.
4. Check awaited vs unawaited coroutines.
5. Check cancellation and cleanup.
6. Check thread safety.

## Constraints

- Watch coroutine was never awaited, event loop already running, blocking IO, unsafe GUI thread update.

## Output

1. Routing
2. Reasoning summary
3. Action / plan
4. Verification
5. Risk
