---
tags: [reference, conductor, decision]
status: superseded
date: 2026-11-03
source: laptop
superseded_by: "[[2026-11-03-native-workflow]]"
---

> [!warning] Superseded (2026-11-03, later the same day)
> Chirayu does not want to maintain the orchestrator harness. The accepted native-first contract is [[workflow]], with rationale in [[2026-11-03-native-workflow]]. Do not implement this old spec in conductor_mcp.py.

# Conductor + project leads: spec (decided by Chirayu, 2026-11-03)

Decided in a design discussion with Chirayu on 2026-11-03. This is the task for the
agent that is rewriting the conductor so its workers become T3 threads. Do it **after**
the current T3-thread change and build on it. No push or merge without Chirayu's OK.

Related: the independent Codex survey `Projects/Conductor/survey-2026-11-03.md`. It
found the effective conductor effort is `medium`, not low, and that `ai:641` defaults
to `opus`. Fix both as part of this work.

## Roles

### Main conductor (switchboard)
- Claude **Sonnet**, low effort. Lives in `/home/cgupta/ai-orchestrator`.
- Only does these things:
  - shows the list of running leads and their workers, grouped by project, with a hop link to each thread
  - routes Chirayu's messages to the right lead
  - notify/pending
- Talks to **leads only**. It never messages a lead's workers directly (one control path per worker).
- It does not answer substantive questions itself. Remove `consult`, `relay` and its own
  evidence-reading from `conductor.md`, in particular:
  - "Your value is judgement… checking them"
  - rule 3's "read the cited files yourself"
  - the confidence-reporting section
  - "Read, Grep, Glob to check evidence yourself"

### Project lead (one per active project)
- **Claude Sonnet**. Leads exist only for projects with work going, not one per folder.
  Candidates by recent activity: HToWW, Flashjet, DigiMorphing, Agenthon/AgentHarness, Conductor.
- Visible top-level T3 thread, **pinned**, titled `◆ Lead · <Project>`, cwd `/home/cgupta/obsidian-notes`,
  and its brief points to `Projects/<Project>/`. Unpin it when the project goes quiet.
- Main job: **reporting status and coordinating** its own project's workers. It starts,
  messages and tracks them. It answers status questions itself.
- **Explanations go through Codex.** When Chirayu asks to explain something ("explain",
  "why", "what does this mean", walkthroughs of code, results or plots), the lead calls
  `explain_with_codex` / `ask_codex` (peer MCP, through omp) with the relevant transcript or files,
  and shows Codex's answer **unchanged, labelled "Explained by Codex"**, plus at most one line on where the source is.
- **No standing reviewer.** A Claude-vs-Codex cross-check happens only when Chirayu asks for it.
- Writes its project's section of the Night log in `Daily/YYYY-MM-DD.md` (local commit only,
  never push night logs) and saves verified results to Hindsight with provenance.
- Unchanged: no push, merge, job submission or data deletion without Chirayu's explicit OK.

### Workers
- Visible top-level T3 threads titled `<Project> · <task>`, cwd `/home/cgupta/obsidian-notes`
  unless Chirayu names another directory. Only their lead starts them.

## Enforcement
- `ai-orchestrator/.claude/settings.json`: add a **deny** list so the conductor can't answer.
  Deny:
  - Read/Grep/Glob
  - the vault search/read tools
  - Hindsight recall/reflect
  - `consult`/`relay`
  - any T3 thread-launch path that could start a thread outside obsidian-notes
- The thread-spawn tool always uses cwd `/home/cgupta/obsidian-notes` (hard-coded default,
  not instruction-only).

## Acceptance
Show with a test or demo that:
1. a spawned lead appears as a pinned top-level sidebar thread `◆ Lead · <Project>` in obsidian-notes,
   and a worker it starts appears as `<Project> · <task>`;
2. the conductor's tool list no longer contains the denied tools;
3. the conductor's agent list shows each lead (and its workers) with a hop link;
4. an "explain" request to a lead returns a labelled Codex answer.

Report back with the files you changed and a diff summary.
