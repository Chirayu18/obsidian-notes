---
tags: [reference, howto]
status: active
date: 2026-10-29
source: laptop
---

# Using the ai orchestrator

Built on 2026-10-29 from `2026-10-29-orchestrator-plan.md`, simplified on the same day: no Claude bridge (Claude runs in native Claude Code on your subscription), no data-sensitivity layer and no sandbox (Claude already handles CERN work), and CERN-hosted models used only as a last resort. Code: `~/ai-orchestrator` (local git repo). Codex reviewed it twice as an advisor.

## Daily use

Type what you want, from the directory you want the work to happen in:

```bash
ai "the ctag2d category edges are still wrong for 2023, fix them"
```

`ai` checks whether this continues an existing task (bge-m3 similarity to the task's title and notes). A clear match in the same directory resumes that session; a possible match, or a match in another directory, asks you; anything else starts a new task. For a new task, Arch-Router (local, 1.5B, about a second) decides what kind of work it is, and the first available model for that kind of work starts: Claude Code for Claude, omp for Codex and everything else. Before Claude starts, `cswap auto --once` switches your Claude account if the active one is at 90 percent of its 5 hour or weekly limit.

The model is chosen once per task and stays for the whole session, so routing never breaks the prompt cache. (OpenSquilla, by contrast, routes every turn and calls its cache continuity best effort; its "sticky tier" rule against mid-conversation downgrades ships switched off.)

| Command | Does |
|---|---|
| `ai "..."` | route automatically: resume or new task |
| `ai -n "..."` | force a new task |
| `ai -m opus "..."` / `-m sonnet` / `-m codex` / `-m qwen` | choose the model yourself (always a new task; logged as an override) |
| `ai --dry-run "..."` | show the decision without starting anything or writing state |
| `ai tasks` / `ai tasks --all` | list tasks with their model |
| `ai resume <id> ["..."]` | resume a task by id prefix, optionally with a new prompt |
| `ai note <id> "next: rerun impacts"` | record progress; improves future matching |
| `ai done <id>` / `ai pause <id>` | change task state |
| `ai why [<id>]` | why that model was chosen, and what was skipped |
| `ai routes` | routes, candidates, which are available right now |
| `ai log` | recent decisions |

Inside omp, `/tasks` and `/why` show the same.

## Routes

Edit `~/ai-orchestrator/config.toml`; `ai routes` shows the result.

| Route | Order of candidates |
|---|---|
| physics analysis debugging | Claude Opus, Claude Sonnet, Codex, GPU node, CERN Qwen |
| substantial coding | Claude Sonnet, Codex, GPU node, CERN Qwen |
| code review | Codex, Claude Sonnet, GPU node, CERN Qwen |
| routine coding, explanation, research, slides, other | Claude Sonnet, Codex, GPU node, CERN Qwen |
| public documentation | NIM, Claude Sonnet, Codex, GPU node, CERN Qwen |

## Shared vault search

The vault is available to every agent through the `vault` MCP server (`scripts/rag/vault_mcp.py`), registered for Claude Code (user scope) and omp (`~/.omp/agent/mcp.json`). Tools: `search_notes`, `read_note`, `related_decisions`, `propose_memory_update`. Proposals land in `Proposals/` with `status: proposed`; nothing edits existing notes.

`vault-search` now uses BM25 as its keyword arm (`--keyword rg` for the old one). On the 16 labelled queries from the August RAG evaluation (`scripts/rag/bench.py`):

| Arm | recall@5 | MRR |
|---|---|---|
| ripgrep alone | 0.50 | 0.38 |
| BM25 alone | 0.69 | 0.51 |
| semantic + ripgrep (before) | 0.81 | 0.48 |
| semantic + BM25 (now) | 0.81 | 0.52 |

## Things you still need to do once

1. **Codex in omp.** `omp login openai-codex` (browser sign in with ChatGPT Plus), then `omp models openai-codex` and put the strongest id in `config.toml` under `[candidates.codex] model = "openai-codex/<id>"`.
2. **Always-on account switching (optional).** `ai` already checks before each Claude launch. To also switch during long sessions, run `cswap auto` in a spare terminal, or as a user service: create `~/.config/systemd/user/cswap-auto.service` with `ExecStart=<path of cswap> auto --interval 60 --threshold 90` and run `systemctl --user enable --now cswap-auto`.
3. **CERN AI Gateway, personal key (optional, rarely used).** Create a key in your own sandbox team at aigw.cern.ch, `keyring set aigw_personal cgupta`, and check its limits for free with `curl -s -H "Authorization: Bearer $(keyring get aigw_personal cgupta)" https://aigw.cern.ch/key/info`. Only the free Qwen is configured.
4. **NIM (optional).** `keyring set nvidia_nim cgupta` with an nvapi key.
5. **GPU node (optional).** A llama.cpp or vLLM server on an lxplus-gpu node, tunnelled to `127.0.0.1:18080`.

## Files

| Path | What |
|---|---|
| `~/ai-orchestrator/` | launcher, config, omp commands extension (local git) |
| `~/.local/share/ai-orchestrator/` | task database, decision log, omp sessions per task |
| `~/.omp/agent/` | omp 18.13.3: `config.yml` (updates off, telemetry off, approvals for writes, Anthropic provider disabled), `models.yml`, `mcp.json`, `agents/` (planner, worker, reviewer, researcher), `extensions/` |
