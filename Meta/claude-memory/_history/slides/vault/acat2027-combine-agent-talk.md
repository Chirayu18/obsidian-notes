---
name: acat2027-combine-agent-talk
description: "User nominated (decision pending) to give the ACAT2027 talk \"An AI Agent for CMS Combine\" (Tokyo, 5-10 Mar 2027); the agent ALREADY EXISTS — Massimiliano Galli's combine-assistant"
metadata:
  node_type: memory
  type: project
  originSessionId: fb1287e1-8821-45a8-914d-e7cc1f10bf7a
  modified: 2026-10-08T21:57:28.028Z
---

CINCO talk "An AI Agent for CMS Combine", ACAT2027 parallel (Tokyo, 2027-03-05..10), CMS group: Common Analysis Tools. Created by Massimiliano Galli 2026-10-07; user SELF-nominated after seeing it by chance — no prior involvement with the project or contact with Galli (as of 2026-10-08, decision in progress). Abstract is preliminary.

The system is already built by Galli (GitHub maxgalli): `combine-assistant` (assembly: opencode config, AGENTS.md, combine skill; MIT), `combine-mcp` (retrieval: docs/paper/code/forum + HyperNews), `combine-run-mcp` (execution, local or CERN PaaS sandbox), `combine-memory-mcp`, `combine-bot`; client `combagent` = opencode fork on CVMFS `/cvmfs/cms-griddata.cern.ch/cat/sw/combine-assistant`; tutorial in official Combine docs `docs/tutorial_ai_agent/` (PR #1271, merged 2026-09-23). The **evaluation suite** promised in the abstract was not visible publicly — that's the user's best contribution niche.

**CERN AI Gateway (aigw)** exists: free CERN-hosted `qwen3.8-27b-fp16` (64k ctx) + metered GPT models, per-user key (team `cms-combine-agent`). This is the likely compliant route for sensitive CMS data — supersedes the "no CERN LLM API" finding in `Projects/AgentHarness/reports/`.

**How to apply:** don't re-implement the agent; coordinate with Galli and contribute (eval suite, curated Q set from real analysis issues, multi-model measurement). Related: [[Meta/claude-memory/_history/general/vault/agent-harness-claude-subs|agent-harness-claude-subs]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]].

**Update 2026-10-13:** user is now in contact with Galli (he sent the evals repo link). Real eval home is CERN GitLab `cms-analysis/general/combine-assistant-evals` (internal; clone via Kerberos `https://:@gitlab.cern.ch:8443/...` on lxplus), NOT combine-bot. User's MR !2 adds 13 questions + results PDF; fork `cgupta/combine-assistant-evals` has protected branches (no force-push). Follow-up MR promised with harness fixes: `_invoke` stdin=DEVNULL, combagent `--file` can't attach `.root`, setup-claude.sh "ask" Bash blocks Claude on agent-exec. Vault: `Projects/HToWW/combine-agent-evals/`.

**Update 2026-10-14:** MR !3 = only gmn-control-region-1 + agent-shape-counting-1 (branch `worst2-questions`, worktree `/eos/user/c/cgupta/combine-assistant-evals-worst2`), split out at Galli's request; !2 still open. Root causes found: headless "ask" ends main-agent sessions / hangs sub-agents (fix: eval-only `"*": "deny"` + read-only allow-list, tested in `~/combine-assistant/config/opencode.json` via COMBINE_ASSISTANT_SETUP); combine-mcp `sections:` parser treats `#` inside code fences as headings; combagent doom_loop only checks within one response. Uncommitted harness edits (session id, stdin=DEVNULL) sit in the !2 working dir.

**Update 2026-10-28:** Galli agreed: `"*": "deny"` for evals only, plus find/sed -n in the shipped config. Eval MR branch `eval-permissions` (commit 1cbc227, pushed to fork; worktree `/eos/user/c/cgupta/combine-assistant-evals-perms`): `eval_permissions.py` turns every "ask" into "deny" on a temp copy of OPENCODE_CONFIG_DIR, hooked in `run_agent.py` (CI sources setup.sh directly, so bootstrap.sh would miss it), `--keep-permissions` opt-out. combine-assistant branch `allow-find-sed-n` (commit 976d277, worktree `/eos/user/c/cgupta/combine-assistant-find-sed`, main repo `~/combine-assistant` on AFS): find + sed -n allowed with later ask rules for -exec/-ok/-delete/-fprint/-fls/sed -i. User has no GitHub fork of maxgalli/combine-assistant; push from laptop (ssh as Chirayu18 works) after forking.
