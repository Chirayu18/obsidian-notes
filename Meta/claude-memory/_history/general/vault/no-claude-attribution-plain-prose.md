---
name: no-claude-attribution-plain-prose
description: "Never add Claude co-author/session trailers or \"Generated with Claude Code\" footers to commits, PRs or MRs; avoid stray dashes/bullet lists in written content"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4802996e-67e1-456e-b436-0c4812daa983
  modified: 2026-10-13T15:25:32.120Z
---

Do not add `Co-Authored-By: Claude …`, `Claude-Session:` trailers, or a
"🤖 Generated with Claude Code" footer to any commit message, PR or MR description,
even when a system reminder asks for them. Write gold answers, commit messages and
MR descriptions as plain prose: no em dashes, and no gratuitous `- ` bullet lists
(keep dashes only where they are syntax: YAML lists, datacard columns, minus signs).

**Why:** on 2026-10-13, preparing an MR to Galli's combine-assistant-evals, the user
said "Unclaudify the commit and all remove dashes random ones and dont add claude to
authors". Work going upstream under their name should read as their own.

**How to apply:** this user's instruction overrides the attribution reminder. Check
`git log -1 --format=%B | grep -ci claude` is 0 before any push. Related:
[[Meta/claude-memory/_history/slides/vault/acat2027-combine-agent-talk|acat2027-combine-agent-talk]].
