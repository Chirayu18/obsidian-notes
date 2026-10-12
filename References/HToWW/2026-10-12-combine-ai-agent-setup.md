---
tags: [reference]
status: active
date: 2026-10-12
source: lxplus
---

# CMS Combine "AI agent" (combine-assistant) — setup handoff

Handoff note so a fresh agent can continue setting up Galli's Combine AI assistant.
Full machine-specific plan lives at
`/home/cgupta/agenthon_hacathon/combine/SETUP_PLAN.md` (laptop). This note is the
portable summary + next actions.

- **Tutorial:** https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/tutorial_ai_agent/ai_agent_tutorial/
- **Repo (Galli):** https://github.com/maxgalli/combine-assistant (MIT, v0.5.4, ~123 KB)
- **Server repos:** https://github.com/maxgalli/combine-mcp (retrieval) · https://github.com/maxgalli/combine-run-mcp (execution)

## What it is

Experimental (NOT official CMS) chat assistant for CMS Combine. It (a) answers Combine
questions **with citations** and (b) **runs Combine commands** to reproduce / diagnose /
confirm results. Two ways to drive it:

- **Claude Code** — open the repo in `claude`; uses Claude's own model, **no API key**.
  Recommended path for Chirayu.
- **`combagent`/opencode** — pick a provider; default is CERN `aigw` gateway, which needs
  e-group `cms-combine-agent-users` + a personal `AIGW_API_KEY`.

## How the code works (read from source)

Three repos, **no custom model, no RAG embeddings**:

1. **combine-assistant** = pure config/glue. `.mcp.json` registers two **remote HTTP** MCP
   servers (`combine` and `combine-run-remote`, both at `*.app.cern.ch`).
   `config/opencode.json` = providers + model list + a bash allow-list (auto-runs only
   `combine`, `text2workspace.py`, `combineCards.py`; `combineTool.py` + everything else
   prompt). `config/AGENTS.md` = persona/system prompt. `config/skills/combine/SKILL.md` =
   routing brain. Claude Code gets `AGENTS.md` + `.claude/skills` as symlinks into `config/`.
2. **combine-mcp** = retrieval server (Python, `uv`). **BM25 keyword search (`rank_bm25`),
   explicitly "no embeddings."** Tools `search_docs` + `fetch_doc` (projection modes:
   markdown/outline/sections/post). Five sources: `combine-docs`, `combine-code` (pinned
   v11.1.0), `combine-paper` (arXiv:2404.06614), `combine-forum`, `combine-hypernews`.
3. **combine-run-mcp** = execution server on CERN PaaS. Tool `run_combine` runs ONE command
   in an isolated sandbox; datacard via `files`, ROOT shape files via `files_b64`.

**Routing (key design point):** the skill runs `command -v combine` first. On PATH → run in
the **real shell** against real files (preferred, no size cap, outputs persist). Not on PATH
→ remote sandbox. Hard-coded anti-hallucination: cite returned URLs verbatim, admit gaps,
never fabricate run results.

**CAVEAT:** the two forum corpora are CERN-authenticated/CMS-restricted and the public
`combine-mcp` server is restricted to the CERN network. Docs/code/paper retrieval is public;
forum search + the remote exec server appear **CERN-gated** → the assistant likely works
properly only from lxplus/CERN, not the bare laptop.

## Verified environment (as of 2026-10-12)

- **Laptop (Linux, zsh):** `/usr/bin/python3` = 3.14.4. NO combine/CMSSW/conda/root/cvmfs.
  `claude` IS at `/home/cgupta/.local/bin/claude`; `git` at `/usr/bin/git`.
- **lxplus:** ssh ControlMaster socket + `~/mnt/lxplus` sshfs mount are LIVE (zero re-auth;
  re-establish with `python3 ~/bin/lxplus-connect.py`). **Combine already BUILT:** source at
  `~/CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit`, binary at
  `~/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/combine`. **No scram rebuild needed.**
- `combine-assistant` repo **not yet cloned** on lxplus.
- `hww_athens/.../Combine` = only PNG plots (LaTeX/beamer repo); no datacards, no workspace.
  **No `datacard.txt` found anywhere** — needed to test the execution path.

## Next actions (for the continuing agent)

Recommended: run Claude Code on lxplus so it sees the built Combine + real files.

1. Confirm lxplus up: `ssh lxplus 'echo ok; which git'` (if fail: `python3 ~/bin/lxplus-connect.py`).
2. Clone repo on lxplus: `ssh lxplus 'cd ~ && git clone https://github.com/maxgalli/combine-assistant.git'`.
3. Check `claude` is installed ON lxplus: `ssh lxplus 'bash -lc "command -v claude || echo NO-CLAUDE"'`.
4. Launch: `ssh -t lxplus 'cd ~/CMSSW_14_1_0_pre4/src && cmsenv && cd ~/combine-assistant && claude'`.
5. First test (retrieval, no datacard needed): ask "How do I compute an expected
   AsymptoticLimit from a datacard, and what does the output mean? Cite the docs."
6. Execution test needs a `datacard.txt` in the cwd — obtain one (see open questions).

Optional aigw/combagent path needs: join e-group `cms-combine-agent-users`, log in once at
https://aigw.cern.ch, make a key at https://aigw.cern.ch/ui/api-keys (team `cms-combine-agent`),
then `export AIGW_API_KEY=<key>` (NEVER store the key in a file).

## Open questions for Galli

1. Claude Code vs combagent+aigw — which does he recommend?
2. Is the public `combine-mcp` reachable off the CERN network at all, or lxplus/CERN only?
3. An example `datacard.txt` to exercise execution (Chirayu has none locally).
4. Is `claude` installed on lxplus where the built Combine lives?

_Constraints honored this session: nothing installed, no keys entered, no jobs started,
nothing under `hww_athens` modified. Track-1 areas untouched._
