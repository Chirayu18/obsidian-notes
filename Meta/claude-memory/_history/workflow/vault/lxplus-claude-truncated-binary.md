---
name: lxplus-claude-truncated-binary
description: "claude on lxplus \"Bun Bus error\" at startup = auto-update truncated by AFS quota; repoint ~/.local/bin/claude to an intact version"
metadata:
  node_type: memory
  type: project
  originSessionId: ff3c62fb-4b7f-495e-aa29-fc943200fca6
  modified: 2026-10-12T09:10:55.972Z
---

2026-10-12: `claude` on lxplus crashed in ~190ms with "panic: Bus error" (Bun). Cause:
`~/.local/share/claude/versions/2.1.197` was exactly 218103808 B (208 MiB, a round number),
a truncated auto-update written while AFS home was at 95% quota. Fixed by repointing
`~/.local/bin/claude` → `versions/2.1.196` and deleting the truncated file.

**Why:** AFS home is perpetually near-full (see [[Meta/claude-memory/_history/workflow/vault/lxplus-cmssw-build-location|lxplus-cmssw-build-location]]), so updates can silently truncate again.
**How to apply:** if claude dies instantly on lxplus, `ls -la ~/.local/share/claude/versions/` and look for a suspiciously round size; run with `DISABLE_AUTOUPDATER=1` until quota is freed. claude on lxplus also needed an interactive `/login` (not done as of 2026-10-12). Context: [[Meta/claude-memory/_history/slides/vault/acat2027-combine-agent-talk|acat2027-combine-agent-talk]].
