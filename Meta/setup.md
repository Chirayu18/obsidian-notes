---
tags: [meta, setup]
status: active
date: 2026-11-05
---

# Agent setup (single source of truth)

Everything about how the agents work lives in this vault. Change it here.

## Roles
| Role | Where it runs | Instructions |
|---|---|---|
| Conductor: routing, what's running, needs-you | pinned T3 thread, Claude Sonnet/low, cwd `~/obsidian-notes`, started with its role brief | [[Meta/roles/conductor]] |
| Worker: one task at a time, writes notes, commits, no push | T3 top-level thread, cwd `~/obsidian-notes` | vault `CLAUDE.md` |
| Keeper: organise, decks, lint, index, review + push | pinned T3 thread, Codex Sol/high, cwd `~/obsidian-notes`, on demand | [[Meta/roles/keeper]], style: [[Meta/roles/update-slide-style]] |

## Machine configuration (laptop)
| Piece | State |
|---|---|
| `~/.claude/settings.json` | model `opus`; SessionStart hook `~/bin/lxplus-session-start.sh` (lxplus connect + mounts). No Hindsight hooks. |
| Vault `.claude/settings.json` | `autoMemoryEnabled: false`; SessionStart `scripts/sync-on-start.sh` (fetch; pull --rebase on normal branches). Index rebuild moved to the keeper. |
| Vault `.claude/settings.local.json` | local permission allowlist (not synced). |
| MCP servers (Claude) | `vault` only (`scripts/rag/vault_mcp.py`). Removed: hindsight, peer, home-assistant/ha-mcp, legacy conductor. |
| Search index | `scripts/rag/` — tiers notes + papers; code tier off (`VAULT_INDEX_CODE=1` re-enables). Needs Ollama `bge-m3`. |
| Obsidian Git plugin | auto-pull every 5 min and on boot; **auto-commit off** (2026-11-05); auto-push off. |
| Services | `lxplus-eos.service` on (EOS mount). `hindsight-api.service` stopped + disabled; data kept on disk. |
| Quota helpers | `cswap list --json` (Claude accounts), `omp usage` (Codex). |

## Rules in one place
- Vault is the record. One worker at a time. Only the keeper pushes, after reviewing.
- No merge, job submission, data deletion or service restart without Chirayu's OK.
- Workers are top-level threads (sub-agents die when their parent thread restarts).

## History
- `~/ai-orchestrator`: no longer used (2026-11-05); safe to remove once Chirayu decides.
- 2026-11-03/04: Hindsight-based setup with per-project leads — retired 2026-11-05.
  Export: `Meta/_history/hindsight-export-20261105/`; old roles: `Meta/_history/Conductor-20261103/`.
- Backups of pre-revert configs: `~/setup-backup-20261105/` (laptop only). Git tag
  `pre-revert-20261105` in the vault and `~/ai-orchestrator`.
