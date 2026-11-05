---
tags: [reference, conductor, decision, "project:Conductor"]
status: superseded
date: 2026-11-03
source: laptop
superseded_by: "Hindsight research document workflow:current"
---

# Decision: role files, not a harness

Historical decision, superseded by Chirayu's later choice: Hindsight for coordination/memory and editable slide decks for exact research records. Read Hindsight `workflow:current`; the older Obsidian-canonical statements below are preserved history, not active instructions.

Chirayu's final clarification: "just keep a claude.md for all the different roles ... lead and the main conductor mainly ... no new harness or code to invent." This narrows the earlier staged implementation proposal. The active instructions are the four role files listed in [[workflow]]. The old [[2026-11-03-project-leads-spec]] is superseded and must not be implemented in conductor_mcp.py.

The latest clarification makes the Sonnet/low orchestrator a task keeper and continuation manager: track unfinished work and resume authorized tasks in their existing threads, not answer them. Chirayu talks directly to task agents. Project leads are also low effort and remain idle except for genuinely complex coordination; they are not a mandatory relay hop. Use compact meaningful checkpoints, not polling or routine summary turns. Workers and Codex explanation threads remain top-level in the vault. No standing reviewer. Keep one edit owner, Hindsight memory, original source records, local-only Night logs and explicit approval for push/merge/submission/deletion.

Codex continued setup because Claude was quota-exhausted. Four role contracts were written; the vault startup instructions select the matching one. The conductor's native effort was set/read back as low. Five Claude Sonnet/low leads were registered and pinned idle, without model turns. No new code, watcher, service, scheduled task, provider retry or custom API client was created. Experimental conductor permission rules were removed and the prior project settings restored. No Git mutation or service restart was performed.

Obsidian stays canonical; Hindsight is complementary agent memory and reflection, not a replacement for exact notes, PDFs, results or version history. This matches the maintained [Hindsight Obsidian integration](https://hindsight.vectorize.io/sdks/integrations/obsidian): one-way sync, citations, content hashes and document upserts. Its CLI was already installed here; the existing sync scope/index was not changed.

The discussion exposed native limits, not reasons to build another supervisor: T3/Pi can leave a finished answer marked running; native messages respect runtime ceilings; role instructions do not enforce filesystem locks. A full-access Claude deny-rule smoke and away-time notification delivery remain unverified because Claude quota stopped the former and the user being active suppressed the latter. No claim that role files fix either issue.

The earlier Opus handoff did not run. Chirayu subsequently assigned implementation directly to this Codex worker; no additional Opus implementation agent is needed. The preserved legacy code/state remains untouched as source/fallback, not a new dependency of the role files.

The continuation record now requires a stable task identity, one coordinator, one source-note writer, current checkpoint/evidence, exact next action and approval boundary. Duplicate checkpoints must not trigger another turn. Native messaging must work in both directions and the previous worker turn must be closed before continuation; the present full-access conductor versus approval-required leads mismatch is not resolved by changing prose. Automatic wakeup, native provider closure and away notifications remain separate runtime prerequisites.
