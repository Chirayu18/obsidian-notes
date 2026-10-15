---
tags: [reference, agents]
status: active
date: 2026-10-15
source: laptop
---

# Agentic reviewer for CERN slides: what exists, and a proposed design

Goal: an agent framework that reviews my CMS slides (beamer PDF/tex, markdown decks) the way a hostile expert audience would, with every finding checked against the real analysis code, datacards and notes rather than against the slide prose.

## 1. What we already have

| Piece | Where | Reuse for slide review |
|---|---|---|
| Vault RAG (`vault-search`) over notes, papers, lxplus code | `scripts/rag/` | Per-claim context lookup ("what is the current limit", "which JER tag") with recency and superseded handling already built in |
| Review brief template | `Projects/HToWW/deck-overview-2026-08-17/REVIEW-HANDOFF.md` | Already the right spec: slide-by-slide, true/supported, necessary for the audience, missing, does the plot show what the caption says, most serious first, do not edit |
| My own review log | `Projects/Flashjet/SLides review.md` | Real examples of the feedback I give (ordering, undefined symbols like d_ij, plot too small, wordy statements). Use as rubric and few-shot examples |
| Verification habit | memory `an-review-verify-against-source` | Claims about cards and configs must be checked on lxplus, never against prose |
| Content guard | memory `hww-fs-private-results-not-for-ppt` | Private 3FS/4FS results must never reach slides. A deterministic check, not an LLM judgement |
| Eval methodology | `Projects/HToWW/combine-agent-evals/` (nugget evaluation, judge bias notes) | Same method to score the reviewer itself |
| Harness thinking | `Projects/AgentHarness/reports/Letta Code versus alternatives.md` | Conclusion stands: own the orchestration in Python or Claude Code, call models per turn |

## 2. CERN AI Gateway, measured today

Gateway is a LiteLLM proxy at `https://aigw.cern.ch/v1` (OpenAI compatible). Reachable from lxplus (and laptop only on eduVPN). My key is a team key (`cms-combine-agent`) restricted to `llm_api_routes`: `/v1/models` returns only `no-default-models`, `/model/info` is denied, and the key has **no MCP servers** attached (`/v1/mcp/tools` empty, access_denied). So the gateway gives models only, no tools.

| Model | Text | Image input | Notes |
|---|---|---|---|
| `qwen3.8-27b-fp16` | ok | **yes**, read axis labels correctly | free, CERN hosted, 64k ctx. Best default for internal material |
| `hf-qwen3-32b-awq` | ok | no ("not a multimodal model") | text only |
| `gpt-oss-20b` | ok | no (could not see the image) | text only |
| `gpt-5.6-luna-preview` | ok | yes | metered; check where it is hosted before sending internal content |
| `gpt-5.6-sol-preview` | ok | yes | same caveat |
| `gpt-5.6-terra-preview` | ok | not tested | |

Vision test used a synthetic matplotlib histogram, not a real analysis plot.

## 3. The combine agent (asked it directly)

`combagent run -m aigw/qwen3.8-27b-fp16` on lxplus listed its tools: the standard opencode set (bash, read incl. PDFs/images, grep, glob, edit, write, webfetch, task subagents, skills) plus two MCP servers. `combine` (`search_docs`, `fetch_doc`, BM25 over Combine docs, paper, code, forum, HyperNews) and `combine-run-remote` (`run_combine`, one command in a sandbox). For slide review the useful part is the `combine` MCP to ground statistics claims ("what does this option actually do") and running Combine to recheck a quoted limit or significance. Both MCP servers are CERN network only.

## 4. What exists online (checked 2026-10-15)

Nothing reviews HEP slides against the analysis that produced them. The useful building blocks:

| Repo | Stars, last push | What to take |
|---|---|---|
| [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent) (EMNLP 2025) | 5.1k, 2026-10-12 | **PPTEval** rubric: Content, Design, Coherence scored 1 to 5 with written feedback |
| [Noi1r/beamer-skill](https://github.com/Noi1r/beamer-skill) | 365, 2026-08-12 | Claude Code skill: compile, review, score beamer decks, TikZ audit. Closest existing tool |
| [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) | 1.7k, 2026-09-27 | Academic Claude Code template: specialist agents, quality score gate in a hook, critic and fixer loop |
| [pgarrett-scripps/PeerReviewAgents](https://github.com/pgarrett-scripps/PeerReviewAgents) | 5, 2026-10-13 | Structure worth copying: specialist reviewers, advocate vs skeptic debate, editor verdict |
| [archi-physics/archi](https://github.com/archi-physics/archi) (ex A2rchi, MIT subMIT) | 59, 2026-10-13 | RAG plus ReAct agent deployed in CMS CompOps and DQM ([arXiv:2606.04755](https://arxiv.org/abs/2606.04755)). Candidate backend if this grows into a group service |
| [maxgalli/combine-mcp](https://github.com/maxgalli/combine-mcp) | 0, 2026-10-14 | Statistics grounding, see section 3 |
| [karuboniru/inspire-mcp](https://github.com/karuboniru/inspire-mcp) | 0, 2026-08-01 | INSPIRE lookups: check cited results and numbers quoted from papers |
| [MohamedElashri/cds-mcp](https://github.com/MohamedElashri/cds-mcp) | 0, 2026-07-28, WIP | CDS search, e.g. is this PAS public yet |

Related HEP agent papers (context, not tools): RooAgent ([2605.17318](https://arxiv.org/abs/2605.17318)), AgentRivet ([2606.13535](https://arxiv.org/abs/2606.13535)), "AI Agents Can Already Autonomously Perform Experimental HEP" ([2603.20179](https://arxiv.org/abs/2603.20179)). No Indico MCP server found; Indico has a REST API and I already have a token (`~/.indico_token`).

## 5. Proposed design

Build thin, borrow rubrics. A Claude Code skill plus subagents, with model routing by sensitivity.

**Ingest.** `pdftoppm` each slide to PNG and `pdftotext` per page; attach the beamer or markdown source when present. Each slide becomes one record (image, text, source span, speaker notes).

**Deterministic checks first (no LLM).** Private result guard (strings and filenames from the forbidden list, e.g. `fs_ratio_`), "CMS Preliminary / Simulation / Private Work" label present on plots, lumi and energy labels, undefined symbols (math tokens on a slide not defined on that or an earlier slide), plot size relative to slide area, slide text density.

**Specialist reviewers, run in parallel per slide.**
1. Claim verifier. Extracts every number and factual claim, runs `vault-search` and greps the lxplus code, cards and configs, and returns verified, contradicted, or unverified, each with a file path. Contradicted needs a path, otherwise it is downgraded to unverified.
2. Plot and caption checker (vision). Does the figure show what the caption says (the `B3_shapes_SR_hplusc` mistake), are axes readable, and are the legend entries the processes that were claimed.
3. Statistics reviewer. Combine claims checked with the `combine` MCP and, where cheap, a rerun on lxplus.
4. Narrative and audience critic. Ordering, filler, missing obvious questions, using my Flashjet log and PPTEval Coherence as the rubric.
5. Hostile audience. Generates the three questions a convener would ask, then checks whether the deck answers them.

**Editor.** Deduplicates, ranks by severity, and drops anything without evidence. Output is the REVIEW-HANDOFF format: a numbered list keyed to slide number, most serious first. Optionally an advocate vs skeptic pass on the top findings only.

**Model routing.** Internal or unapproved material goes to `aigw/qwen3.8-27b-fp16` (CERN hosted, vision capable) or stays on lxplus. Public decks (e.g. the Higgs 2026 talk) can use Claude via `claude -p`. GPT-5.6 previews only once their hosting and data terms are confirmed.

**Learning loop.** Every time I write a manual review (like the Flashjet log), store it with the deck commit; that grows into an eval set. Score the reviewer with the nugget method from the combine evals: did it find the issues I found, and how many findings were false.

## 6. First steps

1. Build the ingest and deterministic checks as a script, and run them on the Flashjet ml4jets deck, where my manual review exists as ground truth.
2. Add reviewers 1, 2 and 4 as subagents behind a `/review-slides` skill, then compare with my Flashjet log.
3. Add the statistics reviewer and the INSPIRE MCP after that.

Open questions: which deck to pilot on (Flashjet is the best ground truth), and whether GPT-5.6 previews on aigw are cleared for internal CMS material.
