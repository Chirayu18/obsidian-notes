---
tags: [reference]
status: active
date: 2026-10-12
source: lxplus
---

# CMS Combine "AI agent" (combine-assistant) — setup handoff

**Submitted 2026-10-13:** [combine-assistant-evals!2](https://gitlab.cern.ch/cms-analysis/general/combine-assistant-evals/-/merge_requests/2) (13 questions + results PDF; Galli notified). Harness improvements MR to follow.

**Submitted 2026-10-14:** [combine-assistant-evals!3](https://gitlab.cern.ch/cms-analysis/general/combine-assistant-evals/-/merge_requests/3) (only `gmn-control-region-1` and `agent-shape-counting-1`, split out of !2 at Galli's request so the Qwen failures can be debugged one question at a time; !2 stays open).

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
- `combine-assistant` repo (v0.5.4, official origin) now **cloned on BOTH** laptop
  (`/home/cgupta/agenthon_hacathon/combine/combine-assistant`) and lxplus (`~/combine-assistant`).
- ~~`claude` CLI is NOT installed on lxplus~~ **WRONG** — it is at `~/.local/bin/claude`. The
  `bash -lc` probe dies on the zellij login-shell launcher (ENOTTY) before `command -v` runs;
  probe with the explicit path instead. See Progress below.
- ~~No `datacard.txt` found anywhere~~ WRONG — see Progress below.

## Next actions (for the continuing agent)

Recommended: run Claude Code on lxplus so it sees the built Combine + real files.

1. Confirm lxplus up: `ssh lxplus 'echo ok; which git'` (if fail: `python3 ~/bin/lxplus-connect.py`).
2. ~~Clone repo on lxplus~~ DONE — `~/combine-assistant` already present (also cloned on laptop).
   **BLOCKER:** `claude` is NOT installed on lxplus — install Claude Code there, OR run `claude`
   on the laptop in the laptop clone (retrieval-only, likely docs/code/paper since forum + remote
   exec are CERN-gated).
3. Check `claude` is installed ON lxplus: `ssh lxplus 'bash -lc "command -v claude || echo NO-CLAUDE"'`.
4. Launch: `ssh -t lxplus 'cd ~/CMSSW_14_1_0_pre4/src && cmsenv && cd ~/combine-assistant && claude'`.
5. First test (retrieval, no datacard needed): ask "How do I compute an expected
   AsymptoticLimit from a datacard, and what does the output mean? Cite the docs."
6. Execution test needs a `datacard.txt` in the cwd — obtain one (see open questions).

Optional aigw/combagent path needs: join e-group `cms-combine-agent-users`, log in once at
https://aigw.cern.ch, make a key at https://aigw.cern.ch/ui/api-keys (team `cms-combine-agent`),
then `export AIGW_API_KEY=<key>` (NEVER store the key in a file).

## Progress — 2026-10-12 (continuation session)

- **Cloned** `~/combine-assistant` on lxplus (v0.5.4, `601e1a9`). `.claude/skills` symlink intact.
- **MCP reachability MEASURED:** both servers (`combine-mcp-git-combine-mcp.app.cern.ch`,
  `combine-run-mcp-git-combine-mcp.app.cern.ch`) answer MCP `initialize` **from lxplus**; from
  the laptop both **time out**. → CERN-network only, run it on lxplus. (Answers Q2 for us.)
- **`claude` on lxplus was broken:** `~/.local/bin/claude` → `versions/2.1.197`, which was
  exactly 208 MiB (truncated auto-update, AFS quota at 95%) → Bun "Bus error" at startup.
  Repointed symlink to intact `2.1.196`, deleted the truncated file (AFS now 93%).
  Run with `DISABLE_AUTOUPDATER=1` until quota is freed, or the next update can truncate again.
- **`claude` on lxplus is NOT logged in** (`-p` → "Not logged in · Please run /login").
  Needs one interactive `/login` by Chirayu. **This is the only blocker.**
- **Datacards DO exist** (the earlier "no datacard.txt anywhere" was wrong — it searched
  `hww_athens`): `/eos/home-c/cgupta/higgscharm/outputs/combine/*.txt`, e.g.
  `v11_hplusc_v4.txt` (6 channels, shapes in `v11_hplusc_v4.root` alongside).
- `combine` on PATH after `cmsenv` in `~/CMSSW_14_1_0_pre4/src` — **verified**.

Launch (after login):
```bash
ssh -t lxplus 'source /cvmfs/cms.cern.ch/cmsset_default.sh && cd ~/CMSSW_14_1_0_pre4/src && cmsenv \
  && cd ~/combine-assistant && DISABLE_AUTOUPDATER=1 claude'
```
Approve the two project MCP servers when prompted. Execution test: copy a card **and its
.root** to a scratch dir (don't run in the EOS outputs dir) and ask for an expected
AsymptoticLimit.

## Tutorial run — 2026-10-12, laptop on CERN eduVPN

**eduVPN fixes laptop access.** On VPN the laptop gets MCP `initialize` replies from both
servers and `aigw.cern.ch` → 307. (Off VPN: MCP = TLS with the generic `CN=www.cern.ch` cert,
then empty reply — intranet-only PaaS routes; aigw:443 silently dropped.) The VPN is split
tunnel: public IPv4 stays the home ISP, only CERN ranges go through it.

**Path 2 (Claude Code, laptop) — WORKING, all 3 tutorial prompts run:**
`cd ~/agenthon_hacathon/combine/combine-assistant && source bin/setup-claude.sh` →
run dir `/tmp/cgupta-combine-claude` (symlinked `.mcp.json`, skill, `CLAUDE.md` persona +
generated `settings.json`). Then `cd $COMBINE_CLAUDE_DIR && claude`.
1. `--robustFit` question → cited docs + tutorial + 2 cms-talk threads (forum corpus works
   over VPN); honestly flagged it couldn't open `FitterAlgoBase.cc`.
2. "Run an asymptotic limit on datacard.txt" (Combine tutorial
   `data/tutorials/counting/realistic-counting-experiment.txt`) → no local combine, so it used
   `combine-run-remote` (v11.1.0). **Cross-checked on lxplus with our own build: all 5 expected
   quantiles + observed identical** (exp median r<2.3281, obs r<1.6281).
3. FitDiagnostics covariance error → correct causes/fixes, cited forum posts, asked for the
   command + card rather than guessing.

**Path 1 (combagent + aigw, lxplus) — ready, needs the key at launch.** CVMFS setup
`/cvmfs/cms-griddata.cern.ch/cat/sw/combine-assistant/latest/bin/setup.sh` (v0.5.4) puts
`opencode`/`combagent` (build 0.0.0--202607211226) on PATH, config → `/tmp/cgupta-combine-assistant`
(node-local: re-source every login). **Gotcha:** don't pipe `source setup.sh | tail` — the pipe
runs it in a subshell and nothing lands on PATH. Tutorial card copied to
`/eos/user/c/cgupta/combine-agent-tutorial/datacard.txt`. Key lives in vault `.keys`
(chmod 600, git-ignored) — never commit it.

## Open questions for Galli

1. Claude Code vs combagent+aigw — which does he recommend?
2. ~~Reachable off CERN network?~~ Measured: no, lxplus only (see Progress).
3. ~~Example datacard~~ Not needed, own cards on EOS.
4. ~~claude on lxplus?~~ Yes (2.1.196), needs /login.

_Constraints honored this session: nothing installed, no keys entered, no jobs started,
nothing under `hww_athens` modified. Track-1 areas untouched._
