---
tags: [reference, plan]
status: active
date: 2026-10-29
source: laptop
---

# Personal AI orchestrator for CMS research, with the cern-slides workflow

**Built 2026-10-29, with two changes to this plan:** no Claude bridge (Claude runs in native Claude Code, launched by `ai`; omp handles every other provider), and CERN-hosted models are last in every route, used only for restricted tasks. How to use it: `2026-10-29-ai-orchestrator-usage.md`.

This plan merges the OMP orchestrator design (reviewed with ChatGPT on 2026-10-29) with the `cern-slides` skill in `~/slide-review/skills/cern-slides`. The orchestrator is the general system; cern-slides becomes its first specialised workflow and the model for how every part of the system learns from me.

Earlier research behind it: `Projects/AgentHarness/reports/Letta Code versus alternatives.md` and the notes in `Projects/AgentHarness/research_notes/`.

## 1. What the system must do

I open one OMP terminal, say what I want, and the system decides which task it belongs to, which model should do it, what prior context it needs, and whether to resume, delegate or ask me. It respects provider rules, never spends the team budget, keeps restricted material at CERN, and learns only from my own corrections, never from its own output.

Six requirements follow. Automatic model selection. Task continuity, so a follow up resumes the right session instead of opening a new one. Shared long term memory through my Obsidian retrieval. Efficient delegation that protects the primary agent's prompt cache. Reliability and control: provider restrictions, usage limits, restricted material, spending. And specialised workflows, starting with slide review, that plug into the same routing, policy and memory instead of carrying their own.

## 2. Design principles

These are shared by the orchestrator and cern-slides, and every new component has to follow them.

1. **Cheapest and most certain layer first.** Deterministic rules before any model, a small local model before a large remote one. In cern-slides, `cern_checks.py` runs before PPTEval and the reviewers. In the orchestrator, the policy controller runs before Arch-Router.
2. **Rules decide what is allowed; models only choose among allowed options.** Neither the router nor a reviewer can relax a privacy rule.
3. **Model findings are candidates until verified against source.** Reviewer claims need file:line, a URL or a page image. A worker's summary is never evidence.
4. **Learn only from my own words.** The personal slide reviewer learns from my reviews and reactions. The router learns from my overrides. Memory updates need my approval. Agent output never becomes training data on its own.
5. **Every addition must beat the simpler baseline on a blind test.** The personal reviewer had to beat a generic control (16 of 29 of my points against 10 of 29). Router, delegation and any learned context selector face the same test.
6. **The primary agent owns its session.** The orchestrator routes around it instead of rewriting its context, because the Claude bridge rewrites the whole Claude session when history diverges.

## 3. Architecture

| Layer | Components | Runs on |
|---|---|---|
| Interface | OMP TUI, `omp -p` for headless jobs, a thin launcher that resolves the task before OMP opens | laptop |
| Orchestration extension | task resolver, session registry, model router, policy controller, workflow dispatcher | laptop (TypeScript extension plus a small Python sidecar) |
| Execution | claude-bridge (Claude Sonnet, Opus), Codex sign in (ChatGPT Plus), CERN AI Gateway with my own key (free Qwen; metered GPT only on approval), lxplus GPU node via ssh tunnel, NIM for public material only | external and CERN |
| Workflows | cern-slides (beamer, pptagent underneath); later Combine debugging, CMSSW and Alpaka recipes | invoked as skills and subagents |
| Memory | Obsidian retrieval as an MCP server; OMP transcripts for working memory; SQLite for operational state | laptop |
| Learning and evaluation | decision log, my overrides, cern-slides `reactions.jsonl` and checklist re-learning, nugget evals | laptop and lxplus |

There is no permanently running orchestrator LLM. The extension handles control flow; Arch-Router-1.5B (laptop Ollama) is called only when a model must be chosen.

## 4. Request flow

Every request goes through three decisions in order.

**Task identification.** The resolver ranks existing tasks by workspace path, explicit project names, recency and Obsidian similarity. A clear match resumes that session, a clearly new request creates a task, and a genuine tie shows me a compact choice. The task registry stores pointers, not transcripts: task id, project, OMP session id, primary model, state, workspace and worktree, related note paths, last outcome and next action, classification, and update time. OMP's `SessionManager` and `/resume` provide the session side; the resolver is the new part, built as a controller around those APIs, because an input hook alone cannot safely swap live sessions.

**Primary model selection.** Continuing tasks keep their model unless there is a reason to escalate. New tasks go through the three routing layers in section 5.

**Execution and delegation.** The chosen model runs in OMP and spawns short lived subagents only when that saves time, saves money or gives independent verification. Specialised work is handed to a workflow (section 6).

## 5. Routing and policy

**Layer A, hard policy.** Restricted material (frontmatter `sensitivity: cms-internal`, analysis and EOS data paths, the per project forbidden patterns already kept in cern-slides `slide-review.json`, e.g. `fs_ratio_` and the private 3FS/4FS results) goes only to CERN hosted or local models. Ordinary CMS development is not automatically restricted from Claude. NIM receives public material only. Metered CERN GPT requires my explicit approval with a cost estimate, and no fallback chain may reach it. Only my personal gateway key is used. Switching between my two Claude subscriptions stays manual. A usage-limit failure can pick another allowed model but can never override a restriction. The policy controller checks before dispatch and again in `before_provider_request` and on tool outputs, because a datacard can enter the context halfway through a task. Tool network access is restricted too, since a shell or Python tool can leak data without any model request.

**Layer B, Arch-Router-1.5B.** Classifies the request against routes I write in plain English. Starting preferences:

| Task | Preferred | Alternative |
|---|---|---|
| Difficult physics analysis, Combine debugging | Claude Opus | Claude Sonnet |
| Substantial coding, GPU implementation | Claude Sonnet | Codex |
| Independent code review | Codex | Claude |
| Routine coding, boilerplate | CERN Qwen | Codex |
| Simple explanation or summary | CERN Qwen | Claude Sonnet |
| Complex technical research | Claude Sonnet | Codex |
| Public documentation processing | CERN Qwen | NIM |
| Slide review or slide writing | cern-slides workflow on Claude | cern-slides on aigw Qwen when content must stay at CERN |
| Restricted material | CERN Qwen or lxplus GPU model | none outside CERN |

**Layer C, availability and quality.** If the chosen model is unavailable, pick another allowed one or ask me. If an agent repeatedly fails a verification check, escalate to a stronger model in a separate delegated session with a summary of the failures, never by switching the primary model mid conversation.

## 6. Workflows: cern-slides as the first one

A workflow is a skill with its own interview, config file and layers that uses the orchestrator's router, policy controller, retrieval and learning loop instead of hard coding them. cern-slides already has this shape.

| cern-slides today | In the orchestrator |
|---|---|
| Entry points: "start a slide review", "remember my review", quick "is this public safe" | Router route "slide review"; the resolver ties the review to the deck's task (e.g. the Higgs 2026 H-charm talk) so a follow up resumes it |
| Interview writes `slide-review.json` (mode public, own or internal; audience; minutes; focus; forbidden patterns; backend) | `slide-review.json` becomes the task-level config. Its `forbidden_patterns` and `backend: aigw` feed Layer A directly, so the policy controller enforces them for every model call in that task, not only inside the skill |
| Layer 1 `cern_checks.py`, deterministic CMS checks | Unchanged; runs locally first, blockers are facts |
| Layer 2 PPTEval via `claude -p` (about 90 calls for a 45 page deck) or aigw Qwen | Model chosen by the router within the policy. Default `--pages` for quick looks; full deck only on request, because per slide calls do not share a cache |
| Layer 3 reviewers (claim verifier, figure and caption, statistics, expert audience) as Claude Code Agent subagents | OMP `task` subagents, read only, no worktree. The claim verifier uses the shared Obsidian MCP and combine-mcp. The statistics reviewer may use Codex for an independent view |
| Verification rule: per slide findings are candidates until the rendered page is viewed; Qwen misread c-bar as "ee" | Kept as a hard rule. Vision findings from aigw Qwen always need confirmation by a stronger vision model or by me |
| Personal reviewer learning from my reviews only; blind leave-half-out eval against a generic control | Becomes the template for every learning component (section 9) |
| Report saved next to the deck; "save your opinions?" at the end of every review | Report path recorded in the task registry; reactions feed the shared learning store |

Porting needs checking. OMP is said to read skills from other tools without conversion, but cern-slides calls Claude Code specific tools: AskUserQuestion (OMP has its own `ask` tool) and the Agent tool (OMP uses `task`). Either add a thin adapter section to SKILL.md or keep a Claude Code path for slide review until the OMP path passes the same eval. The `claude -p` calls inside the skill run real Claude Code on my subscription, which is fine, but they are invisible to the router, so route PPTEval's backend through the orchestrator's choice instead of hard coding it.

**Token cost is the main caveat of cern-slides and must be fixed before it moves.** PPTEval calls `claude -p` twice per slide with only `--tools Read` restricted, so every call also loads Claude Code's full default system prompt, the vault CLAUDE.md and MEMORY.md (about 16 kB of text when run from the vault), the skills list, configured MCP and connector tool schemas, and the SessionStart hooks. A 45 page deck repeats that overhead about 90 times, and the four layer-3 reviewers each read the deck again. Fixes, in order of expected saving: give each call a short `--system-prompt`, `--setting-sources ""` (no hooks), `--strict-mcp-config` and `--disable-slash-commands`, and run it from a neutral directory so CLAUDE.md and auto memory are not loaded (`--bare` cannot be used because it ignores subscription logins); merge the describe and score stages into one call; batch several slides per call; send the text layer instead of an image for slides without figures; on a re-review, only revisit slides changed since the last reviewed commit; extract the deck once and give the reviewers a shared compact outline plus only the page images they need; make PPTEval opt in, since the personal reviewer and the claim verifier are where the value showed up. Measure first: one lean call against one current call with `--output-format json` to read the token and cache counts, then a three page run, logged per layer in the decision log so layers that find nothing can be dropped.

The same pattern fits later workflows. Combine debugging: combine-mcp plus combine-run-mcp, the eval suite from combine-assistant-evals as its test. CMSSW Python and Alpaka/GPU work: build and validation recipes with compute-sanitizer and profiling, which the reviewer must actually run.

## 7. Memory

| Memory | Store | Purpose |
|---|---|---|
| Working | OMP session transcript | current conversation and tool state |
| Long term knowledge | Obsidian | notes, decisions, investigations, references, slide review reports |
| Operational | SQLite task registry | which task belongs to which session, model and workspace, and what is left |
| Preferences and corrections | cern-slides `personal/` data, router overrides, a few Sharpshooter constraints | how I want things done, learned only from me |

The Obsidian MCP exposes `search_notes(query, scope, limit)`, `read_note(path)`, `related_decisions(topic)` and `propose_memory_update(task_id, content)`. Writes are proposals I approve; agent conclusions never become permanent facts silently. Sharpshooter, if used, holds only a few short project constraints, not a copy of the vault.

**Retrieval change.** The current keyword arm is ripgrep, which has no term weighting or length normalisation. Replace it with proper BM25, as combine-mcp uses (`rank_bm25`), with title and heading boosts and code-aware tokenisation so identifiers like `make_combine_inputs` stay whole. Keep bge-m3, RRF fusion, tier weights, the 120 day recency half life and superseded demotion. On lxplus, where there is no Ollama, BM25 alone replaces plain grep. I have not seen evidence that BM25 alone beats the hybrid on this vault, so test before switching: about 30 vault queries with known answers, recall at 5 and MRR, comparing today's ripgrep plus semantic, BM25 alone, and BM25 plus semantic. Keep the winner.

The learned context selector is not in the first version. Pinned constraints, recent turns verbatim and retrieved evidence come first; the selector is considered only if the decision log shows context loss that rules cannot fix.

## 8. Claude bridge and cache rules

Another turn in the same Claude task continues the existing session. A new unrelated task gets a new session. Small independent subtasks and Codex reviews run as separate sessions. A Claude rate limit pauses or delegates instead of silently replacing history. A bridge failure falls back to native Claude Code. Compaction happens only when needed, and its rewrite cost is measured. The ChatGPT advisor is off by default and runs manually or at task completion until the bridge debug log (`CLAUDE_BRIDGE_DEBUG=1`, "Case 3" reuse against "Case 4" rewrite) shows advisor notes do not trigger rewrites. Use the 200k window variants unless a task needs 1M. The bridge drives genuine Claude Code through Anthropic's Agent SDK, which is a terms of service grey area; native Claude Code stays a working fallback.

## 9. One learning loop for everything

cern-slides already has the loop I want everywhere: my own judgements are recorded, a component is re-derived from them, and a blind test against a simple control decides whether the new version replaces the old one.

| Component | My signal | Re-learned artefact | Blind test |
|---|---|---|---|
| Personal slide reviewer | my `S<n>:` reviews, `reactions.jsonl` agree, disagree, partly | `personal/checklist.md` | leave-half-out per deck against a generic control |
| Router | `/route` overrides, escalations, my rating of outcomes | route descriptions and preferences | replay of logged tasks: my choice against the router's |
| Task resolver | corrections when it resumed the wrong task | matching weights and thresholds | held out follow up requests |
| Memory | approved or rejected `propose_memory_update` items | what gets proposed | precision of proposals I accept |
| Retrieval | queries where the right note was missing | ranking settings | the 30 query benchmark |

All signals land in one SQLite store with the decision log, so a later learned router or context selector has data from day one.

## 10. Where things run

Laptop CPU: OMP, the extension, SQLite, the Obsidian MCP, `cern_checks.py`. Laptop GPU (6 GB): bge-m3 and Arch-Router through Ollama, loaded on demand; measure swapping cost and fall back to CPU routing if it is annoying. CERN AI Gateway: free Qwen, metered models only with approval, reachable from lxplus or eduVPN. lxplus GPU node: optional self-hosted models, bulk labelling, and aigw-backend slide reviews when content must stay at CERN. External: Claude bridge, Codex, NIM for public material. LiteLLM is optional; keep it only if its logging and per-key limits are worth maintaining, and verify that its budget enforcement is backed by its database before relying on it.

## 11. Commands

A normal prompt does everything automatically. `/tasks` lists tasks by state. `/route` shows or overrides the routing. `/why` explains the current model choice. `/newtask` forces a new task. `/resume` is OMP's picker. `/review` requests an independent review. `/memory` searches related notes and decisions. `/slides` starts the cern-slides interview for a deck, and "remember my review" keeps working as the cern-slides entry point.

## 12. Build order and gates

| Phase | Build | Pass |
|---|---|---|
| 1 | Pin OMP; claude-bridge, Codex, aigw with my own key; fix the compound shell and URL read problems found in the eval; policy controller with Layer A | each provider works alone; no restricted test prompt reaches a non-CERN endpoint, tested deliberately |
| 2 | Task registry, resolver, `/tasks` | follow ups resume the right session on a set of repeat-work prompts, no duplicates |
| 3 | Router: policy filter, Arch-Router, availability, escalation, `/why` | matches my own choice on at least 80 percent of 50 logged tasks at no extra cost |
| 4 | Obsidian MCP with BM25 arm and the 30 query benchmark | no regression against today's hybrid; consistent results across agents |
| 5 | cern-slides on OMP: adapter for ask and task, router-chosen PPTEval backend, policy fed from `slide-review.json` | the OMP path matches the Claude Code path on the existing personal eval (at least 16 of 29) and finds the same layer-1 blockers |
| 6 | Delegation and review recipes for Combine, CMSSW Python, Alpaka | delegation improves quality or time against a single agent |
| 7 | Telemetry, advisor automation, learned components | each addition beats its simpler baseline on real tasks |

## 13. Success criteria

Manual model selection is rare for ordinary tasks, searching for old sessions is rare, and duplicate sessions are minimised. Task resumption is correct on repeat work. Route overrides decrease over time. There are no avoidable Claude cache rewrites from routine routing. Task quality is at least as good as when I chose the agent myself. Retrieval does not regress. There are zero unauthorised provider or metered calls in controlled tests. Slide reviews keep or improve their score against my own reviews, and no restricted pattern ever leaves CERN in a slide review. The real test: one terminal all day without remembering which agent was doing what.
