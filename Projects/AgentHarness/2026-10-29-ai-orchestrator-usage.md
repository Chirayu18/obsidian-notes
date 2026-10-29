---
tags: [reference, howto]
status: active
date: 2026-10-29
source: laptop
---

# Using the ai orchestrator

Built on 2026-10-29 from the plan in `2026-10-29-orchestrator-plan.md`, with one change: there is no Claude bridge. Claude runs in native Claude Code on the subscription (the account `cswap` currently has active), and omp handles every other provider. Code: `~/ai-orchestrator` (local git repo). Codex reviewed it twice as an advisor and its findings were fixed.

## Daily use

Type what you want, from the directory you want the work to happen in:

```bash
ai "the ctag2d category edges are still wrong for 2023, fix them"
```

`ai` then does four things. It checks whether this continues an existing task (bge-m3 similarity to the task's title and notes); a clear match in the same directory resumes that session, a possible match or a match in another directory asks you, anything else starts a new task. It classifies the data: `restricted` (matches your private patterns or words like unpublished), `cms` (CMS terms or analysis paths), or `public`. For a new task it asks Arch-Router (local, 1.5B, about a second) which kind of work this is. And it starts the first allowed and available model for that kind of work: Claude Code for Claude, omp for Codex, NIM, the GPU node or CERN Qwen.

CERN's models come last in every route. They are only reached when a task is restricted, because Claude and Codex are not allowed for that class.

| Command | Does |
|---|---|
| `ai "..."` | route automatically: resume or new task |
| `ai -n "..."` | force a new task |
| `ai -m opus "..."` / `-m sonnet` / `-m codex` / `-m qwen` | choose the model yourself (always a new task; logged as an override, which is how the routing improves) |
| `ai --restricted "..."` | force the restricted class (CERN Qwen or the GPU node only) |
| `ai --dry-run "..."` | show the decision without starting anything |
| `ai tasks` / `ai tasks --all` | list tasks with their model and class |
| `ai resume <id> ["..."]` | resume a task by id prefix, optionally with a new prompt |
| `ai note <id> "next: rerun impacts"` | record progress; also improves future matching |
| `ai done <id>` / `ai pause <id>` | change task state |
| `ai why [<id>]` | why that model was chosen, and what was skipped |
| `ai routes` | routes, candidates, which are available right now |
| `ai log` | recent decisions |

Inside omp, `/tasks` and `/why` show the same. Inside Claude Code nothing changes, except that in sessions started by `ai` a prompt containing a restricted pattern is blocked before it is sent.

## Routes

Edit `~/ai-orchestrator/config.toml` to change them; `ai routes` shows the result.

| Route | Order of candidates |
|---|---|
| physics analysis debugging | Claude Opus, Claude Sonnet, Codex, GPU node, CERN Qwen |
| substantial coding | Claude Sonnet, Codex, GPU node, CERN Qwen |
| code review | Codex, Claude Sonnet, GPU node, CERN Qwen |
| routine coding, explanation, research, slides, other | Claude Sonnet, Codex, GPU node, CERN Qwen |
| public documentation | NIM, Claude Sonnet, Codex, GPU node, CERN Qwen |

Claude subscription limits are not detected automatically. When Claude says the limit is reached, switch account with `cswap` as usual, or run `ai -m codex "..."`.

## Shared vault search

The vault is available to every agent through the `vault` MCP server (`scripts/rag/vault_mcp.py`), registered for Claude Code (user scope) and omp (`~/.omp/agent/mcp.json`). Tools: `search_notes`, `read_note`, `related_decisions`, `propose_memory_update`. Proposals land in `Proposals/` with `status: proposed`; nothing edits existing notes. The server hides notes above the session's data class: a public session (which might be on NIM) does not see CMS notes, a CMS session does not see restricted ones. A note can declare its class with `sensitivity: restricted`, `cms` or `public` in the frontmatter.

`vault-search` now uses BM25 as its keyword arm (`--keyword rg` for the old one). On the 16 labelled queries from the August RAG evaluation, `scripts/rag/bench.py` gives:

| Arm | recall@5 | MRR |
|---|---|---|
| ripgrep alone | 0.50 | 0.38 |
| BM25 alone | 0.69 | 0.51 |
| semantic + ripgrep (before) | 0.81 | 0.48 |
| semantic + BM25 (now) | 0.81 | 0.52 |

BM25 alone matters on lxplus, where there is no Ollama.

## Things you still need to do once

1. **Codex in omp.** Run `omp login openai-codex` (browser sign-in with your ChatGPT Plus account), then `omp models openai-codex` and put the strongest model id in `config.toml` under `[candidates.codex] model = "openai-codex/<id>"`. Also turn off model training in ChatGPT's Data Controls and in Codex settings if you want CMS work to go there.
2. **CERN AI Gateway, personal key.** Log in at aigw.cern.ch, create a key in your own sandbox team (not `cms-combine-agent`), and store it with `keyring set aigw_personal cgupta`. Then check its limits without spending anything: `curl -s -H "Authorization: Bearer $(keyring get aigw_personal cgupta)" https://aigw.cern.ch/key/info`. Only the free Qwen is configured; metered GPT models are deliberately absent. Needs eduVPN off site.
3. **NIM (optional).** `keyring set nvidia_nim cgupta` with an nvapi key, for public documentation only.
4. **GPU node (optional).** Run a llama.cpp or vLLM server on an lxplus-gpu node on port 18080 and tunnel it to the laptop on `127.0.0.1:18080`; `ai routes` shows it as available while the tunnel is up.

## What is enforced and what is not

The launcher never starts a model the data class forbids, refuses to resume a task with a prompt above its class, and fails closed if the private patterns file is missing. Inside omp the guard replaces any request to a forbidden provider with a "blocked by policy" notice (tested: the model never saw the test secret) and filters subagent models. In Claude Code the prompt hook blocks restricted prompts in orchestrated sessions. None of this confines tools: a shell command, an MCP server or a web fetch can still send data out. For truly restricted work use `ai --restricted` and keep web tools off. A network sandbox (bubblewrap with a domain allowlist, as OpenSquilla does) is the next step if this needs to be airtight.

## Files

| Path | What |
|---|---|
| `~/ai-orchestrator/` | launcher, config, omp guard, Claude hook (local git) |
| `~/.config/ai-orchestrator/restricted-patterns.txt` | private patterns, never shared with any model |
| `~/.local/share/ai-orchestrator/` | task database, decision log, guard log, omp sessions per task |
| `~/.omp/agent/` | omp 18.13.3: `config.yml` (updates off, telemetry off, approvals for writes, Anthropic provider disabled), `models.yml`, `mcp.json`, `agents/` (planner, worker, reviewer, researcher), `extensions/` |
| `~/.claude/settings.json` | added the UserPromptSubmit guard (backup `settings.json.bak-2026-10-29`) |
