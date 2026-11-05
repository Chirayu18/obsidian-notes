---
source: Hindsight mental model user-preferences (LLM-synthesised summary)
exported: 2026-11-05
status: superseded
---

## Coding style

- Prefers thin integrations (e.g., a Pi extension or Letta Code plugin calling an external library) over patching core repositories, to avoid approval friction and keep core repos thin (2026-10-08).

- Designs experiments with pre-registered go/no-go decisions and requires a control that can falsify the setup. Tests use 3–5 real historical questions in fresh contexts with the same model. Retention isolation is verified first, since `retainSessions: true` can store test answers, and the Obsidian arm must exclude automatic Hindsight injection (2026-10-08; 2026-11-04).

- Keeps new features off by default and preserves existing configuration syntax: the Phase-2 morphing parameters reuse Phase-1 region syntax, and the feature is disabled by default (`DoDigiMorphing = False`), with output bit-identical to master when off (2026-11-02).

- Keeps test and smoke-run outputs out of production areas: workers run in the designated notes directory, not the orchestrator repository, and conductor code is edited by absolute path. Backs up derived files with a dated `.bak` suffix and diffs them afterward. Stops test threads only when asked, verifies the stop, and reports a possibly stuck thread as possibly stuck until confirmed (2026-11-03).

- Records design decisions as vault specs (e.g., `Projects/Conductor/2026-11-03-project-leads-spec.md`) that an agent implements after its current change, rather than having the conductor do the work. Approved sending the spec to a running agent instead of starting a new one (2026-11-03).

- Runs one worker at a time and never several in parallel, which avoids concurrent vault edits. Keeps one edit owner per shared file: no edits to a file while another thread is editing it, and implementation waits until that thread finishes or the user agrees (2026-11-03; 2026-11-05).

- Avoids building new harnesses, watchers, schedulers, custom API clients, or permission/spending self-expansion to simulate automation. Scheduling must use existing native T3 tools; role files alone are never claimed to provide background execution (2026-11-03; 2026-11-04).

- Agents may message each other but must avoid loops. Assigns one edit owner per shared repository: the lead owns the coordination file, workers report updates to it, and two edit agents must never modify the same files (2026-11-03). Before replacing a full operational document, reads it; after writing, reads it back before claiming success, and inspects unknown timeout outcomes before retrying, since no verified transactional lock exists (2026-11-04). Prefers a single central coordinator and single writer; parallel work is limited to independent, read-only, quickly verifiable tasks (2026-11-04).

- Leaves changes intentionally uncommitted in the working tree when asked, and makes no commit, push or job submission without explicit user approval, including after a fix is corrected (2026-07-08; reaffirmed for Flashjet F1/F2/F3 before the 2026-07-15 push; 2026-11-04).

## Tooling and model routing

- Routing is driven by sensitivity and capability, not price. Sensitive data goes only to self-hosted models; cloud endpoints stay forbidden for sensitive data until CMS and CERN policy is confirmed (2026-10-08). CERN-hosted models are a last resort, never the default (MEMORY.md).

- Question routing (2026-11-05): factual recall goes to the keeper (answer from memory with links); conceptual 'why' walkthroughs go to an explainer worker on Codex; code, configuration and output analysis go to an analyst worker on Claude (Opus, or Sonnet at high effort); questions about an active task go to that task's worker. Answer workers are top-level threads, read-only and small; the keeper asks first before lxplus runs, job submission, long Opus use or high quota.

- Inside T3, Codex runs only through the Pi (omp) provider as `openai-codex/gpt-6.1-sol` or `openai-codex/gpt-6-luna`, never the T3 `codex` provider or `codex exec`; visible Codex explanations use pi/openai-codex and no Claude bridge is used. Claude workers use T3's `claudeAgent` provider (2026-11-03). External ChatGPT web/app conversations are not supported by the installed T3 thread tools (2026-11-03).

- Hidden background `claude -p` / `omp -p` processes are retired in favour of visible T3 threads. A worker has one session, and replacing it requires confirming that the previous run has stopped (2026-11-03). Workers must be separate top-level threads rather than sub-agents, because sub-agents died when their parent thread restarted (2026-11-05).

- Retain and consolidation use `openai-codex/gpt-5.6-luna`; reflect uses Claude Haiku (2026-11-03).

- Dispatch is quota-aware: `cswap list --json` for Claude and `omp usage` for Codex. It prefers Codex when Claude is near its limits and never counts two Codex agents as two model families (2026-11-03).

- Grid job submission safeguards: the grid proxy must be live using the node-local AFS copy `private/x509up_u151861` rather than `cms.proxy`; submission runs from `tmux`, not `nohup`; the memoryless blacklist in `jobs_status.py` is maintained because it can re-admit failed sites (2026-08-12).

- Conductor and project leads run Sonnet at low effort by default, raising thread effort only when deeper reasoning is needed rather than adding a permanent agent (2026-11-03; 2026-11-04).

- At about 70% context usage an agent checkpoints and hands over at a safe turn boundary, preserving task, approvals, evidence and unresolved review findings, showing the successor link, and never running two successors on the same work (2026-11-03).

- Coordination follows the native T3 workflow note, avoids quota-failing turns, and never bypasses native permission ceilings (2026-11-03).

- Subagents launch in auto mode: `runtimeMode: auto` with `interactionMode: default`, while keeping read-only and no-push, merge, job-submission, deletion and restart limits (user request, 2026-11-04).

- Keeps approval-required mode even when it causes repeated prompts: read-only Hindsight tools (`get_document`, `list_documents`, `recall` and similar) are allowed, while writes, `reflect` and Bash stay disallowed (2026-11-04).

- Agent-tooling preferences (2026-11-04; 2026-11-05): one place to see tasks, running agents and memory; no harness to maintain; auto mode without approval prompts; Codex for explanations; no parallel work when explicitly disallowed; one-word status; the ability to 'stop and record'. Prefers one operational task ledger and review queue separate from research knowledge, flattened delegation, and evidence before adding coordination layers. Treats the two Claude accounts as one until evidence shows otherwise.

- Memory: prefers Markdown or small plain files in Git as the source of truth, one file per claim, task or know-how item, readable without a server. Keeps one incremental, source-linked daily note system rather than a second maintained copy. The keeper never deletes information, marks old values as superseded, and avoids large summary rewrites, which lose detail. Prefers a disposable local search index (`vault-search` scored 13/16 vs Hindsight 6/16 on the user's own set; self-authored, so provisional). Hindsight is liked but judged unsuited to single-user research, since it targets multi-user autonomous agents. Wants memory written only at task or conversation boundaries, selective retrieval with source and version pointers, explicit retirement of superseded state, and tools that run locally and do not save chatter. Evaluation uses the same 16 queries plus 4 trick questions before freezing the memory side. When asked something absent from memory, the keeper launches a worker to compute the answer once and stores it as agent-reported (2026-11-04; 2026-11-05).

- Markdown pages are the vault's source of truth for notes. Generated HTML such as `dashboard.html` is built from them and never edited by hand; Reveal.js decks are the exception, living editable HTML that holds exact research records (2026-11-04; 2026-11-05).

- Vault is organized by subproject, each with its own notes, figures and deck, rather than by date or file type. Flashjet's existing 57 notes stay unchanged; the keeper only adds to them and builds decks on top (2026-11-05).

- The conductor routes requests, starts workers, and reports what is running or blocked and remaining quota. It never writes to the vault or relays messages. Commits stay local, and pushing requires the user's approval (2026-11-04).

## Review preferences

- Reviewers must run the build and validation recipes (e.g., compute-sanitizer and profiling for GPU/Alpaka work); reading code is not enough (2026-10-29 plan). Example outcome: code-checks clean, compute-sanitizer memcheck, synccheck and initcheck clean, racecheck hazards triaged as pre-existing or test-only, and an end-to-end `runTheMatrix` run before submission.

- Privacy and permission rules are non-negotiable: models may choose only among allowed options and may not widen permissions, spending, or data access. Consequential actions require explicit user approval; approval is attached to the specific action, not to shell access (2026-11-03).

- Consequential actions such as spawning runs need an explicit user prompt (`requiresUserInteraction`). Approval must not be self-attested through a tool argument such as `approved_by_user` (2026-11-03 Round 2 review).

- Verification is labelled honestly: read-only code checks are reported separately from runtime checks, and anything not run is marked UNVERIFIED (2026-11-03). Review capacity, not agent count, is the bottleneck, so the user keeps review of results manageable (2026-11-04).

- No standing reviewer is added by default; consequential work is checked by its author and by any reviewer the user explicitly requests. A requested Codex reviewer that cannot run is marked missing, never substituted with Claude (2026-11-03; 2026-11-04).

- Verifies the live baseline before dispatching any worker: the lead reads the original project notes first. Setup never starts analysis or submits jobs by itself (2026-11-03; 2026-11-04).

- Reports GPU-only tests as skipped with the reason, never as passing, and keeps GPU-node validation as an explicit follow-up (e.g., 85 passed and 13 skipped for CUDA-only tests in the `b_hive` micromamba environment).

- For historical status audits, uses Hindsight records only as evidence (exact status documents and relevant `night-log:*` records), not vault Markdown, Archive/, live jobs or repositories, and not Markdown checkboxes. Separates “confirmed unfinished” from “not recorded as closed”, citing source dates. Audit workers are read-only and make no writes, tests or job submissions (2026-11-03; 2026-11-04).

- Accepts a fix only after checking it against real files, not just unit tests (2026-11-04). Computed answers are labelled `agent-reported` until user or later-check confirmation makes them `validated` (2026-11-05).

- Evaluations must be fair: every candidate setup is tested under the same conditions, failure modes are documented before results are analysed, and tools that cannot run under the user's rules count as results. The user trusts only test runs on their own notes over vendor benchmark numbers. Tests written and judged by the same agent after seeing results are not accepted as fair (2026-11-05).

- Prefers a deterministic, non-AI, read-only lint to prove a vault is complete: every original section and number cited or archived, byte-identical sources, valid links, sourced claims, no duplicate or conflicting values, and no stale current results. It also reports per-page word counts and warns above 200 words for `HOME.md` or 600 words for any page. Build, lint and fix repeat until the lint reports zero errors, and completeness is claimed only from that report (2026-11-05).

- Rejects vault output padded with irrelevant material.

- Checks rendered output, not only bytes.

- Results carry a lifecycle status (recorded, implemented, tested or validated) and are marked current or superseded with a `superseded_by` link; superseded text is kept. Recording a result does not show it was implemented or validated, and agent claims stay agent-reported until confirmed (2026-11-05).

- Personal work-update decks are distinct from CMS public slides and talks, so CMS public-slide review preferences are not applied to them; the personal reviewer in `cern-slides` is used instead (2026-11-05).

## Communication and framing

- Prefers proactive operation with minimal interruption and low usage. Notifications only when the user needs them; no periodic inactivity reminders or polling (2026-10-08; 2026-11-03; 2026-11-04; 2026-11-05). Sends no progress ping when nothing needs attention; when input is needed, asks one concise consolidated keep/resume/pause/archive question (2026-11-04).

- Prefers a two-agent model (2026-11-05): a conductor for active work and user-attention items, and a keeper for memory, overall project state and what is missing. The conductor speaks only when action is needed or requested; the user talks directly to task agents. The keeper is the sole writer and point of contact for the vault and readable layer; workers send short checkpoint files to `inbox/` only, and the keeper replies to each input with a one-line receipt (e.g., `Recorded → decisions.md: …`). The user's own words are saved verbatim as dated notes (`said by Chirayu, 2026-11-05`) and outrank agent results; corrections are added as new notes that supersede old values without deleting history.

- Prefers on-demand curated views that take seconds to scan: Today (tasks needing the user, current and finished work, remaining quota), Project state (confirmed results, open decisions, superseded items), a weekly diff of claims and decisions, and a review queue for agent-reported claims (2026-11-05). Wants a short read-only briefing per project (about 300 words, updated at each checkpoint) in which every line links to its source and keeps its date; superseded items stay visible but struck through (2026-11-05).

- Readable layer: a per-project `HOME.md` of 200 words or fewer that only the keeper writes; each fact appears once, links to its exact source note and heading, and is labelled current or superseded and as recorded, implemented, tested or validated. Conflicting values are shown side by side with dates. Originals are copied unchanged into `sources/`, and omissions are listed with reasons in `archive_only.md` (2026-11-05).

- Asks for explicit say-so before cancelling threads or stopping quota-heavy workers. When nothing needs a decision, updates are reduced to one line (2026-11-04; 2026-11-05).

- Prefers bounded, smaller scopes.

- Prefers research records as living, editable Reveal.js HTML decks per project or subproject, exported to PDF weekly, rather than a single dashboard. Decks hold stable slide IDs, plots, current vs superseded status, validation level (recorded, implemented, tested or validated), decisions, open questions, and backup slides with exact tables, commands and sources. A subproject gets its own deck only when its work stream has its own results; smaller streams stay in the parent deck. Decks are built lazily, one subproject at a time, and updated daily only when changed. Story-changing results go on main slides and important new results in backup. The keeper updates slides by stable ID rather than rebuilding the deck. Decks stay internal, and CMS rules apply before any slide is shared (2026-11-05).

- Attributes recurring problems to system design rather than prompt quality, and wants the design itself fixed (2026-11-05).

- Slide-making goes only through the Keeper, the sole owner of slide preferences and deck updates; the user does not coordinate slide work with other agents (2026-11-05).

- Slide feedback is saved verbatim with its date, condensed into concise rules in `_meta/slide-style.md`, and newer contradictory rules override older ones. Each change gets a one-line receipt. The existing `cern-slides` skill and its personal reviewer are reused rather than rebuilt (2026-11-05).

- Rollout is lazy and incremental: the old multi-agent setup is frozen and kept as history rather than patched, and projects move into the new system one subproject at a time when first touched or requested. A big-bang migration and an immediate HToWW pilot were rejected. After a one-week check the setup is frozen for two weeks, with proposed changes queued for weekly review rather than live redesign (2026-11-05).

- Design judgment (2026-11-04): flatten routine delegation, require evidence before adding coordination layers, keep one operational task ledger and review queue separate from research knowledge, and measure success by validated research results per day alongside quota and user minutes. Agent-tooling evaluation should cover provenance, staleness, distractors and cost per completed research task. Prefers a short read-only HToWW briefing (about 2 minutes to find the next action and owed decision) as the first step, before changing orchestration.

