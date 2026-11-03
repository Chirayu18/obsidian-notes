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

## Same setup for Claude and Codex

Launched from `~/obsidian-notes`, a Claude session is plain Claude Code in the vault, so it gets the vault CLAUDE.md, your Claude Code memory, the lxplus SessionStart hook, the vault's git pull and index refresh hooks, the MCP servers and your skills. A Codex session (omp) gets the same through the ai-orchestrator omp extension: omp reads CLAUDE.md as a context file, the extension runs your Claude Code SessionStart and SessionEnd hooks (user and project settings, with `CLAUDE_PROJECT_DIR` set), and it appends the directory's Claude Code memory index to the system prompt, with the memory files readable from `~/.claude/projects/<dir>/memory/`. Tested 2026-11-03: Codex in the vault quoted the sumw-trap memory and the vault-search instruction, and the index refresh ran at session end. Memory is per directory, as in Claude Code: launch from the vault to get the vault's memory.

## Claude and Codex talking to each other

The `peer` MCP server (`~/ai-orchestrator/peer_mcp.py`), registered in Claude Code and omp, gives each model a tool to consult the other: `ask_codex` in a Claude session, `ask_claude` in a Codex session, plus `list_threads`. Just ask in plain words, for example "ask Codex to review this diff before we commit", "discuss the limit discrepancy with Codex until you agree, then summarise", or in Codex "get Claude's opinion on this plan". Each thread is a persistent session per directory, so follow-ups continue the same conversation and stay cached. The consulted model works read-only in the same directory (it can read and grep, not edit) and cannot consult a third model in turn. `ask_codex` defaults to gpt-6.1-sol (`luna` for cheap questions); `ask_claude` defaults to Sonnet. Codex goes through your ChatGPT Plus in omp, Claude through Claude Code on the active cswap account. Tested 2026-11-03: Claude asked Codex through the bridge from the vault and got a file:line answer; follow-ups in a thread were remembered in both directions.

## Watching all agents

`ai watch` is a live view (refreshes every 3 s; `--once` for a snapshot, `--hours H` for the window, default 12) of every agent on the laptop: all Claude Code sessions in any directory, whether started by `ai` or not, omp sessions of `ai` tasks, and Claude↔Codex peer threads. Each row shows the state, time since the last activity, harness, model, directory and task name, then what it is doing now (last tool call or reply) and what it was last asked. States: WORKING (mid-turn and recently active), YOUR TURN (finished its reply and waits for you), STALLED? (still open mid-turn but silent), done (a finished headless or peer run), idle. The header shows both Claude accounts' usage and whether the cswap auto-switch service is active. It only reads transcripts and process lists; it never touches a session.

## Teams of Claude and Codex agents

`ai team "goal"` starts a team lead (Claude Opus by default, `-m sonnet` to change) in native Claude Code with Claude Code's agent teams switched on for that session only. The lead plans the work on a shared task list, spawns teammates, and teammates message each other and claim tasks; you can select any teammate in the panel below the prompt and talk to it directly. Besides Claude teammates, the lead can spawn two Codex teammate types defined in `~/.claude/agents/` (copies in `~/ai-orchestrator/claude-agents/`): `codex` (read-only research and review on gpt-6.1-sol) and `codex-coder` (Codex edits and writes files, no shell). Each is a thin Haiku relay that hands its work to a persistent Codex thread through the peer bridge and reports Codex's answer, so Codex is a full team member while the Claude cost stays small. The lead is told to mix families on purpose (Codex reviews Claude's work and the reverse), give implementers separate files, and never push, merge, submit jobs or delete data without asking you. Tested 2026-11-03 as subagents: `codex` answered a code question with a file:line reference, `codex-coder` fixed a bug in a scratch repo. Agent teams themselves only spawn in interactive sessions, so the full team has not been run headless. Agent teams are experimental and use many more tokens than one session.

## Routes

Edit `~/ai-orchestrator/config.toml`; `ai routes` shows the result.

| Route | Order of candidates |
|---|---|
| physics analysis debugging | Claude Opus, Claude Sonnet, Codex, GPU node, CERN Qwen |
| substantial coding | Claude Sonnet, Codex, GPU node, CERN Qwen |
| code review | Codex (gpt-6.1-sol), Claude Sonnet, GPU node, CERN Qwen |
| routine coding, explanation | Claude Sonnet, Codex Luna (gpt-6-luna), GPU node, CERN Qwen |
| research, slides, other | Claude Sonnet, Codex (gpt-6.1-sol), GPU node, CERN Qwen |
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

1. **Codex in omp: done 2026-10-29.** omp is signed in to ChatGPT Plus; `codex` = gpt-6.1-sol, `codex-luna` = gpt-6-luna, and omp's own roles use them (Sol for default, plan, review, research; Luna for workers, smol, commit). Tested: a Codex session in omp starts and resumes with its memory.
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
