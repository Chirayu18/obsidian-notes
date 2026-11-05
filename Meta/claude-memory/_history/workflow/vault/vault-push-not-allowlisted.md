---
name: vault-push-not-allowlisted
description: "git push to the obsidian vault WORKS as of 2026-09-12 (was blocked 2026-08-25); verify with git rev-list before claiming either way"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4db6d519-db7e-48c1-bf6c-462be8c901de
  modified: 2026-09-12T16:48:49.575Z
---

**`git push` in `~/obsidian-notes` now succeeds.** On 2026-09-12 Chirayu said "try the
push anyway" and it went through clean: `686e0ea..56402e0 master -> master`, rc=0.

This reverses the earlier state. On 2026-08-25 `git push` was NOT allowlisted and every
attempt was denied; I recorded that, and then kept repeating "I cannot push" for weeks
after the permission was evidently granted. Both errors have the same shape: **asserting
a permission state from memory instead of checking it.**

The repo is **public** — still flag that once when committing anything unpublished.

**How to apply:** just push when asked. If you need to know the sync state, run
`git rev-list --count origin/master..master` — do not narrate a belief about whether
pushing works. There are also automated `vault backup: <timestamp>` commits under
`chirayu.gupta@vub.be` (mine use `chirayu.gupta@gmail.com`), so a pushed vault is not
proof that I pushed it. See `[[vault-send-workflow]]` (unresolved historical reference; source absent from imported corpus).
