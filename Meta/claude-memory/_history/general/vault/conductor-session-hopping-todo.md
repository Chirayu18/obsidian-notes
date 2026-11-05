---
name: conductor-session-hopping-todo
description: "User wants the conductor to let them jump directly into any agent/session and back, continuously; deferred feature for ~/ai-orchestrator"
metadata:
  node_type: memory
  type: project
  originSessionId: f4831488-5e23-4cfa-81f9-c3f0096db6eb
  modified: 2026-11-03T07:15:17.659Z
---

Requested 2026-11-03 ("I need a way in the conductor to directly jump to any session... continuously hopping in and out of sessions through you... modify the conductor accordingly (do later)"). Not built yet.

Facts found while answering: `ai` has no attach-to-named-agent command; conductor omp agents can be resumed interactively with `omp --session-dir ~/.local/share/ai-orchestrator/conductor/<name>/session --model <model> --continue` (flags from conductor_mcp.py:277, minus -p); Claude agents via `claude --resume <session-id>`. User did exactly this with paper-codex on 2026-11-03 and the conductor did not notice the new turns (they are not in conductor.db). Design needs: an `ai attach <name>` (or conductor `open(name)`) that marks the agent as user-held so the conductor won't send concurrently, and on return ingests the turns the user had into the message log. Peer Claude sessions too (ListAgents/watch.py). See [[Meta/claude-memory/_history/general/vault/conductor-autonomous-notify|conductor-autonomous-notify]].

**Dashboard direction (user, 2026-11-03, later):** build it as a dashboard for attaching to sessions, with everything else controlled by the conductor. Base it on a fork of "agent deck" (an existing session-manager TUI; exact repo not yet verified), but the AI layer (routing, conductor, notify, cross-family review, memory) stays ours. The dashboard is only the view-and-attach shell.

**More requirements (user, 2026-11-03):**
- **Hopping is the conductor's PRIMARY job.** When the user asks something, the conductor should first point them to, or hop them into, the session that owns that topic; doing/dispatching work comes second.
- **Usage-aware dispatch:** the conductor must know the user's limits and current usage per account/provider (Claude subs via cswap, ChatGPT/Codex, others) and pick models accordingly. See [[Meta/claude-memory/_history/general/vault/cswap-service-pr|cswap-service-pr]], [[Meta/claude-memory/_history/general/vault/agent-harness-claude-subs|agent-harness-claude-subs]], [[Meta/claude-memory/_history/general/vault/ask-before-aigw-spend|ask-before-aigw-spend]] (aigw still needs asking).
- **More models in the mix** (beyond Claude + Codex), CERN models still last per [[Meta/claude-memory/_history/general/vault/omp-harness-decision|omp-harness-decision]].
- **Portable conductor handoff:** if the Claude limit runs out, the conductor must be continuable elsewhere (e.g. a Codex/omp conductor reading the same conductor.db, handoff note and memory).
