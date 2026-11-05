---
name: conductor-check-listagents-too
description: "As conductor, \"what's running?\" needs BOTH conductor agents and ListAgents; agents alone only shows ones this conductor spawned"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87f9ee22-1510-4715-ac7b-c58b4af775eb
  modified: 2026-11-03T05:54:05.884Z
---

When asked what agents are running (or before saying nothing is running / picking a next task), call BOTH `mcp__conductor__agents` and `ListAgents`. The conductor `agents` tool only lists agents this conductor spawned and returns empty otherwise. `ListAgents` shows the user's other local sessions (e.g. flashjet-research-setup, digimorphing, track1-coding-public) and Remote Control sessions.

**Why:** On 2026-11-03 I answered "no agents are running" from `agents` alone; the user had 5 background sessions live and had to point it out ("cant you see running agents?").

**How to apply:** Run both in parallel at the start of any turn that depends on what is running. Report conductor-spawned and peer sessions separately, and never say "none running" until both have been checked. `ListAgents` is a deferred tool in some sessions, so load it via ToolSearch if needed.
