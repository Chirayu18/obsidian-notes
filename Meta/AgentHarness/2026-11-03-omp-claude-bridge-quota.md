---
tags: [reference]
status: active
date: 2026-11-03
source: laptop
---

# OMP Claude bridge quota and delegation

## Findings

OMP 18.13.3 had `retry.usageAwareFallback: false` and an empty `retry.fallbackChains`. The saved session used `claude-bridge/claude-opus-5-5` and received the reported five-hour quota error. It switched to `openai-codex/gpt-6-luna` only after a manual model change. OMP did not have a configured bridge-to-Codex fallback.

The session transcript shows Claude bridge usage reporting cache writes around 568k tokens on one turn, with later turns around 590k–675k total tokens. The bridge was carrying a very large accumulated session context; this is the strongest observed explanation for rapid Claude quota use. It is evidence of unusually large submitted context, not a measured attribution of the provider's quota accounting.

Hindsight retain and consolidation are configured for `openai-codex/gpt-5.6-luna`; recent Hindsight operation logs show Codex consolidation/extraction. Reflect and mental-model refresh are configured for Claude Haiku, but no recent reflect operation was observed in the sampled operation list. The failed Qwen fallback cannot fit available system RAM. Do not claim Hindsight caused the Claude quota exhaustion from the available evidence.

OMP did delegate two background researcher agents during the initial orchestrator survey. Task delegation is available; OMP does not fan out every prompt automatically. The active task settings and role definitions were not blocking delegation. A smoke run using OMP's task tool spawned `ArithmeticSmokeCheck` and returned `4`.

## Current workflow decision

The user stopped custom OMP migration development. The final arrangement is one persistent Sonnet conductor inside T3, with its home at `/home/cgupta/hindsight-workspace`, while workers keep `/home/cgupta/obsidian-notes` as their home and their existing CERN/lxplus setup. The conductor workspace imports `/home/cgupta/ai-orchestrator/conductor.md` and adds Hindsight memory and usage-aware dispatch instructions. Its directory-local conductor MCP starts through `uv --directory /home/cgupta/obsidian-notes run --script /home/cgupta/ai-orchestrator/conductor_mcp.py`, preserving worker/consultant directory defaults without changing the runner. `ai -c sonnet` remains a terminal fallback, not the normal entry point for the new T3 conductor.

The OMP extension was restored to its committed pre-migration version: Claude SessionStart/SessionEnd command hooks, directory memory index, and the legacy `/tasks` and `/why` commands. Today's custom quota-switching, notification, and Claude-context workaround code is no longer active. The restored extension does not forward PreCompact. OMP remains available for Codex, including `ai explain "what was unclear"`, which opens Codex with the latest interactive Claude transcript from the current directory.

At the user's selection, OMP's advisor was enabled with `openai-codex/gpt-6.1-sol`. A print-mode startup returned `ok`; a live advisor review was not verified. OMP's bridge compaction threshold remains `70%`; this is compaction, not the old conductor's successor-agent handover.

The native OMP fallback configuration was also changed during the stopped migration: bridge models fall back to Codex Sol, then Luna; Codex Sol falls back to Luna, then bridge Sonnet; Luna falls back to bridge Sonnet. Usage-aware fallback was enabled. These settings were not reverted with the extension. A quota-triggered fallback was not verified, and bridge quota is not directly visible to OMP.

Bridge compatibility failures were measured during the migration: a Claude main session answered, but Claude bridge task agents failed with a missing API-key error. In the tested plugin/OMP combination, prompt capture showed `ctxFiles=0` and Claude did not receive OMP's appended instructions or vault CLAUDE.md. Enabling the bridge's own auto-memory restored the Claude memory index, but did not fix the other missing context. The custom workaround was removed at the user's request; no claim of a complete Claude-to-OMP migration is valid.

OMP's documented native features cover persistent task agents, Agent Hub hopping, advisors, compaction and configured fallback chains. Auto-prewalk is a bounded planning-to-implementation handoff, not a general prompt-to-model router. The vault now has project `.omp/config.yml` selecting native Hindsight memory, API `http://127.0.0.1:8888`, bank `research`, global bank scoping, auto-recall and auto-retain. The global OMP default was not changed. A real Codex/Luna print-mode worker recalled the normalization trap, `5.37×`, and its source note with no tool call.

## T3 Code installation

Installed the official stable T3 Code CLI, version `0.1.6`, then its official systemd user service for persistence. The dashboard is `http://127.0.0.1:3773/`. A previously running server was not replaced; after it stopped, the service was installed. T3 had already imported some native Claude conversations, including the old conductor, but imported visibility does not mean its messages are synchronized with the old conductor registry. The new dedicated thread is `mcp:697dcee6-fcd5-4adf-9f8d-869ac4ba947e`, titled `Conductor`, in the new workspace project. Browser verification showed Claude Sonnet 5.5, Low; the thread was pinned, automatic settling disabled, and native resume-at-reset enabled. Its first model request hit Claude's five-hour limit (reported reset 17:20 Europe/Brussels); it has not yet answered the readiness request. The T3 UI did show successful Hindsight UserPromptSubmit recall before that quota failure. No custom scheduler or bridge was added. T3's native Codex provider currently reports its CLI unavailable; the conductor's existing OMP-based ChatGPT worker path is separate and remains supported.


## Hindsight migration status

The Hindsight 1.1.0 local service and `research` bank are live. Added OMP's `hindsight` HTTP MCP connection at `http://127.0.0.1:8888/mcp/research/`, preserving the existing vault and peer servers. A headless OMP run queried Hindsight recall and returned the expected source note `Projects/HToWW/combine-systematics/2026-07-31-sumw-normalization-trap.md` with the measured 5.37× WtoLNu shard-metadata undercount. A direct recall smoke also surfaced the sidecar-vs-parquet normalization evidence. This validates one retrieval path, not corpus-wide quality.

The original HToWW import completed with 99 documents and no pending/failed operations. The official `@vectorize-io/hindsight-obsidian@0.4.0` importer then reconciled the remaining active vault notes: 110 added, 103 unchanged, zero deleted; Archive, Templates, scripts and .trash were excluded. A second source import added 66 documents from the existing Claude vault memory directory under the `claude-vault-memory` namespace. Source files were kept intact. These reconcile results mean accepted ingestion, not completed extraction; the server is processing the new documents asynchronously.

Installed the maintained `@vectorize-io/hindsight-coding-agents@0.8.4` integration for Claude Code only. Its standard SessionStart, UserPromptSubmit and Stop hooks were merged into user settings without removing the lxplus hook. The user-level Hindsight MCP now uses the integration's stdio server. `/home/cgupta/.hindsight/coding-agent.json` opts in only the conductor workspace and the vault, mapping both to `research`. It uses retrieval-only auto-injection (`recall`), enables live session retention, disables Git ingestion, cold-repo seeding and codebase surveys, and leaves bank configuration untouched. No old conversation archive or analysis repository was imported. Claude auto-memory writing is disabled in both project settings, while original memory files remain intact. The old OMP extension still exposes its historical memory index alongside the native Hindsight backend.

Verified the official recall hook with a real HToWW query in the conductor directory; it returned a Hindsight memory context block. Verified the conductor MCP reports Connected from that directory. Ran the existing lxplus session-start script: SSH connection, AFS mount and EOS mount were all already up. The conductor instructions require `cswap list --json` and `omp usage` before substantial dispatch, prefer Codex workers when Claude quota is scarce, and do not claim cross-family review when only one family can run. Source verification of `conductor_mcp.py:_cmd` confirms Codex workers launch via `omp -p --session-dir … --model …`, with `--continue` on follow-ups, not `codex exec`.
