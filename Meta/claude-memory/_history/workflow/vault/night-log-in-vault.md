---
name: night-log-in-vault
description: Updates made while the user is away go into a "Night log" section of that day's Daily/YYYY-MM-DD.md note, committed locally, never pushed
metadata:
  node_type: memory
  type: feedback
  originSessionId: f4831488-5e23-4cfa-81f9-c3f0096db6eb
  modified: 2026-11-03T06:42:35.540Z
---

All "night mode" / away-from-keyboard progress goes into a vault page: a `## 🌙 Night log` section in that day's daily note `Daily/YYYY-MM-DD.md` (user moved it there 2026-11-03), with "Needs you" first as `- [ ]` tasks so they reach the Dashboard, each claim tagged with its basis, then per-project sections and a short log. Update it as agents finish and commit (prefix "laptop:"). NEVER push night logs (user, 2026-11-03: "don't push night logs"); commit locally only.

**Why:** user said 2026-11-03 "all the night mode or updates from when I'm away need to go as a page in my obsidian vault".

**How to apply:** whenever running autonomously ([[Meta/claude-memory/_history/general/vault/conductor-autonomous-notify|conductor-autonomous-notify]]), keep this page current instead of only reporting in chat.

**Codex edit pass (user, 2026-11-03):** before committing, pass the Night log section to a Codex editor agent to rewrite it clearer for the user (TL;DR, Needs-you tasks first, per-project meaning, every number/path/basis kept exactly), then check its rewrite kept the facts. Also in ~/ai-orchestrator/conductor.md.
