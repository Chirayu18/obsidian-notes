---
name: never-disrupt-running-jobs
description: "Never kill, restart or relaunch running evaluation jobs without explicit user approval"
metadata:
  node_type: memory
  type: feedback
  originSessionId: aa8f9519-67c8-4d6a-9ebd-3e82966c6ba2
  modified: 2026-10-01T11:09:59.714Z
---

Never kill, restart, relaunch or reconfigure an evaluation run that is already in progress unless the user explicitly says to. If a change would need a restart (e.g. more parallel slots), say so and ask; don't do it.

**Why:** The user strongly objected (2026-10-01) when I proposed restarting the running s1/s2 hold-out runs to give them more parallel slots; restarting loses in-progress unit work and muddles comparisons. They had earlier also rejected starting extra jobs that would compete with a running comparison.

**How to apply:** Apply changes only to NEW runs. Before launching anything, check what is already running (`ps`), and don't start jobs that compete with a running comparison without asking. Related: [[Meta/claude-memory/_history/projects/Agenthon/agenthon/agenthon-track1-project|agenthon-track1-project]].
