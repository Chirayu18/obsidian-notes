---
tags: [reference, combine-agent, evals]
status: active
date: 2026-10-21
source: laptop
---

# Knowledge Bases and Agents for CERN (19-23 Oct 2026): what matters for the Combine agent

Workshop: https://indico.cern.ch/event/1716863/contributions/. Slides were read from the public attachments on 2026-10-21. Related: [[2026-10-14-nugget-evaluation-research]], [[2026-10-13-claude-vs-qwen-results]].

## 1. Same evaluation scheme as our nuggets (CMS CompOps, contribution 33)

"Evaluation of AI assistance for CMS Computing Operations" (H. Öztürk for CMS CompOps and the Archi team) uses essentially our nugget scheme.

**Method:**
* 42 real operator questions; each reference answer is cut into "required facts", 225 in total.
* Every fact is reviewed by hand and traced to a source (ticket, doc, code, git commit or live query).
* An LLM judge marks each fact as stated, not mentioned or contradicted. The judge never sees which setup answered. A second judge from another family (Opus 5.5) agrees on 95-97%.
* Two headline metrics: facts stated (a failed try counts 0) and the share of answers with at least one wrong fact.
* 5 tries per question with 95% CIs. With 42 questions they resolve 3-point gaps for the strong models and 8-9 points for the noisy ones.

**Findings:**
* Bigger model, better answers; open models state more wrong facts.
* **The agent framework barely matters.** Same model in LangChain, a bare loop, or Claude Code: no detectable difference.
* Grep beats vector search.
* Live tools matter.
* Most tool errors are the model's own (wrong parameters, invented methods). The fix belongs in the tools: timeouts, output caps, errors that name the bad argument. This matches our combine-mcp `fetch_doc` findings.
* A production setup that looked fine was well behind; "without a fact-checked evaluation we would not have seen it".

They compared CERN models too (qwen3.8-27b, glm-5.3-flash, gemma-4-12b) against GPT-6 luna/sol/astra.

The plenary (contribution 62, J. Mohoney) gives four rules for the question set:
1. Hard.
2. Verifiable: each question lists the facts a correct answer must contain.
3. Cheap to run.
4. Relevant: written by the people who do the work.

It also says to start human review where the judges disagree, and to snapshot live systems because reference answers drift.

**For us:**
* Our nugget scheme is what CMS CompOps already uses in production; cite them.
* Add a second, cross-family judge and report its agreement.
* Report a contradiction rate next to facts stated.
* Use 5 tries rather than 3 if quota allows.
* The "framework barely matters" result is a useful prior for the opencode vs omp comparison.

## 2. omp and aigw (contributions 60 and 64)

**J. Bendavid, "AI for Fun and Physics" (60):**
* Lists **Oh My Pi (omp.sh)** first among documented front-ends for the CERN AI Gateway, with a `~/.omp/agent/models.yml` example (baseUrl https://aigw.cern.ch/v1, api openai-completions). This is the same setup we built.
* Describes the EP/IT **PIONEER pilot** of large open-weight models on aigw, available to specific teams:
  * CMS-PIONEER: Kimi-K3-FLATIRON and MiMo-V2.6-Pro-MOPD-FLATIRON;
  * NGT-PIONEER: GLM-5.2-NGT and MiMo-V2.6-Pro-MOPD-NGT.

  All have 1M context and tool calling. These would be the strongest CERN-side models for the Combine agent.
* On CritPT, Qwen3.8 27B scores 5.4% against about 32% for the frontier models.
* Cost: in agentic coding, 98.6% of tokens are cache reads, so prompt caching dominates cost.

**AIGW talk (64):**
* aigw is LiteLLM with "MCP and agent gateway support", described as "infrastructure for management of AI agents, MCP servers, tools, skills".
* Roadmap:
  * host MCP servers, tools and skills;
  * validate tools for agent evaluation;
  * document how to use our models with agentic tools.

This is most likely what Galli means by "AI Gateway Agents": the combine MCP servers and skill could be hosted and versioned by aigw instead of by us.

## 3. Other useful talks

* **31, MLflow for agentic applications:** version the harness, skills and MCP server together with evaluation datasets; LLM judges plus human-in-the-loop evaluation.
* **42, "Agents gone wild" (security):**
  * least permissions;
  * privileged actions in MCP, outside the model;
  * sandboxes (microsandbox, nono);
  * an MCP gateway that decides "am I allowed?".

  This backs our deny-by-default permission change.
* **58, WisDQM, and 35, CMS DQM VLM benchmark:** a golden set of "atoms" judged one by one (the same idea again). They evaluate harness plus model as one unit, with Claude Code, Codex and LangGraph clients over LiteLLM and MCP.
* **68, verifiable agentic HEP analysis (MIT):** a proposed common HEP agentic benchmark in which the agent performs the task and separate, unbiased LLM evaluators grade it.
* **24, AI-assisted workflows with resonance searches (CMS, N. Saoulidou):** the benchmark tasks include limit setting and significance with Higgs Combine. This is a potential user and source of questions.
* **30, RooAgent:** ROOT analysis agent exposed as an MCP server for Claude/Codex CLI.
* **27, Agent-driven HEP analysis (LHCb):** harness changes are run against a golden benchmark and discarded if they move observables away.
* **Discussion sessions (22 Oct):** shared tools (MCPs, KBs, harnesses) and agent benchmarking. Worth checking the minutes once posted.
