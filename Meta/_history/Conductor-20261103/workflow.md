---
tags: [reference, conductor, decision]
status: superseded
date: 2026-11-03
source: laptop
superseded_by: "Hindsight research document workflow:current"
---

# Native T3 roles

This file is the historical Obsidian-era setup index, superseded by Hindsight `research` document `workflow:current`. Chirayu subsequently chose Hindsight for tasks, decisions and memory, and editable slide decks for exact research records. Do not maintain this Markdown file as a live workflow/task board; the active role files below load the new policy.

| Role | Canonical instructions | Responsibility |
|---|---|---|
| Main conductor | `/home/cgupta/ai-orchestrator/CLAUDE.md` | Sonnet/low task keeper: track state, resume unfinished authorized work, supply hop links; no substantive answers |
| Project lead | `Projects/Conductor/roles/lead/CLAUDE.md` | Claude Sonnet/low, normally idle; activate only for genuine multi-worker coordination |
| Worker | `Projects/Conductor/roles/worker/CLAUDE.md` | Execute the assigned task, respect file ownership, verify and report |
| Explainer | `Projects/Conductor/roles/explainer/CLAUDE.md` | Visible Codex/OMP explanation, source evidence, no implicit edits |

The user talks directly to task agents. There is no mandatory conductor → lead → worker relay. One coordinator owns a task and acts only on a meaningful state transition, continuation due or explicit request. No model polling, acknowledgment loops, routine summarizer or automatic reviewer. A worker leaves a compact checkpoint so the same thread can continue; orchestration stops when the task is done or needs the user.

## Task and continuation record

Task/continuation records now live in the exact Hindsight document `project:<Project>:status`, with one writer, stable task identity, native worker/coordinator links, evidence, next action and approvals. See `workflow:current` for the current contract. The prior Obsidian-status mirror design is retired; old imports remain historical evidence.

## Startup and limits


The vault's main `CLAUDE.md` tells native T3 threads how to select their role; launch briefs should name it explicitly. Role files outside a thread's cwd are not magically auto-loaded: the thread reads the named file on its first turn. Conductor instructions load from its own cwd normally. Existing idle leads have their role in the title and can identify it through native thread metadata.

No standing reviewer, hidden peer process, custom watcher, scheduler, session registry or API client is added. Respect native permissions rather than bypassing them. Role instructions are not a hard file lock or a repair for a T3/Pi stuck run. Do not pretend those limitations disappeared.

Editable slide decks now hold the exact research record, with source/configuration/provenance detail in appendices and notes. Hindsight holds coordination and memory and links to exact deck revisions/slides. No Obsidian dashboard, Markdown note maintenance or custom sync engine is required. Original references/data/code and historical vault content are preserved.

Bounded learning means remembering evidence-backed lessons and proposing better role wording, not changing permissions or rewriting infrastructure automatically. Push, merge, job submission and data deletion still require explicit OK; Night logs stay local; notify only when the user must act.

Legacy code, state and sessions are preserved. No service restart or mass archive/delete is part of writing role instructions. The experimental permission changes were restored; new behavioral permissions were not claimed to be enforced. See [[status]] for prepared native leads and actual remaining prerequisites.
