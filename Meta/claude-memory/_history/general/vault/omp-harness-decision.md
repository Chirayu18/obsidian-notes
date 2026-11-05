---
name: omp-harness-decision
description: User chose omp (oh-my-pi, can1357/oh-my-pi) as the orchestrator harness (2026-10-29); its Anthropic OAuth impersonates Claude Code so never log a Claude sub into omp; autoselect router + context selector are to be omp extensions
metadata:
  type: project
---

2026-10-29: user picked **omp** (oh-my-pi, Pi fork, MIT, TypeScript/bun+Rust, ~1800 commits/month so pin versions) for the personal orchestrator. They now have **ChatGPT Plus** too (omp `/login` OpenAI Codex OAuth is fine).

Source-verified (clone at commit 26bcaa61):
- `packages/ai/src/providers/anthropic.ts` + `claude-code-fingerprint` send a claude-cli User-Agent and X-Claude-Code-Session-Id: logging a Claude Pro/Max sub into omp is the barred third-party pattern. Keep Claude in Claude Code.
- Extension hooks: `context` (replace messages without persisting), `before_provider_request`, `before_subagent_spawn` -> {model}, `setModel`, `session_before_compact`. No automatic model router exists (only static `modelRoles`, per-agent `model: "@role"`, `retry.fallbackChains`).
- Memory backend `sharpshooter` keeps decisions/constraints/corrections files: the closest built-in to the PIN/state-card idea.
- Auto-QA grievance upload to qa.omp.sh is consent-gated; install-id goes to providers/gateways.

**Built 2026-10-29** as `~/ai-orchestrator` (`ai` launcher): NO bridge, Claude via native Claude Code; user wants CERN models used RARELY, so cern-qwen/lxgpu are last in every route (restricted tasks only) and never omp defaults. Usage note: Projects/AgentHarness/2026-10-29-ai-orchestrator-usage.md. Codex advisor = `/usr/lib/chatgpt/resources/codex exec -s read-only` (ChatGPT desktop bundle, logged in).

**Simplified 2026-10-29 at the user's request:** NO data-sensitivity classes, NO guards, NO sandbox ("I already use Claude for my CERN needs"); do not reintroduce them. Auto account switching: ai runs `cswap auto --once` before Claude; a persistent cswap-auto systemd service was blocked by the permission classifier, so the user enables it themselves.

**Codex goes through omp** (user, 2026-10-29: "no I want omp codex"): do NOT route ChatGPT to the native Codex CLI; the bundled codex binary is only for consulting it as an advisor.

**Conductor (2026-11-03):** `ai` with no flag opens the conductor (Claude Sonnet + conductor MCP: route/spawn/send/relay/check/agents/history/stop, one SQLite message log); `ai -d` is the old direct launch; `ai team` = Claude Code agent teams with Codex relay teammates. User's team default: exactly 2 Claude + 1 Codex teammate. Conductor defaults to Opus, effort LOW (user 2026-11-03: consult does the thinking) (user: "needs to be very sharp and consult ai where it can"); `consult` tool asks Claude+Codex in parallel; 70% context handover with successor agents.

**How to apply:** build the autoselect router and the history selector as omp extensions (Python classifier as a local sidecar). aigw: user wants their OWN key (sandbox team), never the cms-combine-agent team budget; per-user limits unknown until checked with the key. See [[Meta/claude-memory/_history/general/vault/agent-harness-claude-subs|agent-harness-claude-subs]], [[Meta/claude-memory/_history/general/vault/ask-before-aigw-spend|ask-before-aigw-spend]], [[Meta/claude-memory/_history/slides/vault/acat2027-combine-agent-talk|acat2027-combine-agent-talk]].
