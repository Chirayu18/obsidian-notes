---
name: agent-harness-claude-subs
description: "User has TWO Claude subscriptions and wants Claude as the main model for their personal agent/memory system; subs only usable via Claude Code (claude -p), not third-party harnesses"
metadata:
  node_type: memory
  type: project
  originSessionId: fb1287e1-8821-45a8-914d-e7cc1f10bf7a
  modified: 2026-10-08T21:23:07.752Z
---

User is building a personal agent system (fresh context per turn, trainable history-selection classifier, state card, vault RAG, orchestrator/worker/reviewer). Research + report: `Projects/AgentHarness/reports/Letta Code versus alternatives.md` (2026-10-08).

They have **two Claude subscriptions** and consider Claude the strongest model, so Claude is the primary backend.

**Why:** Claude Pro/Max is reportedly barred from third-party harnesses (Hermes, opencode, Letta) since 2026-01 — only Claude Code/claude.ai. Earlier advice to avoid Claude entirely was wrong for them.

**How to apply:** own the memory layer in Python; call Claude via `claude -p` (one session per turn) with a per-account `CLAUDE_CONFIG_DIR`; split the two accounts by purpose/data, not to pool rate limits. Never put subscription auth behind a message-rewriting proxy. Hermes only matters for non-Claude models. Sensitive CMS data question applies to Claude too. See [[Meta/claude-memory/_history/slides/vault/hww-fs-private-results-not-for-ppt|hww-fs-private-results-not-for-ppt]].
