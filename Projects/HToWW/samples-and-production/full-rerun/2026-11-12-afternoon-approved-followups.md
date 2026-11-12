---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: authorization-and-agent-dispatch
---

# Afternoon follow-ups authorized and dispatched

Chirayu's exact instruction on 12 November 2026, following the proposed Summer23 v14-v2 H→ττ replacement and negrw provenance/reporting changes: **“Yes do all that, I need things done soon”**. This resolves the authorization block recorded in [[Projects/HToWW/negative-weights/2026-11-12-negrw-review-followup-proposal]]; it does not establish that the proposed changes are implemented or validated.

Three fresh background workers were accepted as running by T3, all Claude Opus 5.5 on Claude 1 (`claudeAgent`), high effort:

- Sample replacement and A/B coverage: task suffix `d9470788-8796-43f2-9940-7c96eef5c428`. Verify 125.09 GeV normalization, smoke-test the selected Summer23 v14-v2 sample, then submit only its replacement TRAIN partitions. Preserve the 401 already-submitted retries and all original inputs/outputs. Return a revised expected-partition manifest because replacing two files with 31 can change the campaign totals.
- negrw G1/G2 provenance and corrected uncertainty reporting: `e9268642-d697-43e9-98b7-5f9170591bfe`. Scope is the concrete proposal above. Model selection/config stays unchanged; G3 closure in the final fit bins remains open.
- b-hive validation duplication and GPU readiness: `f574d05e-e11b-4001-b920-82b091c4d94b`. Parent chooses to correct the repeated partial validation/inference batches before production, under Chirayu's earlier instruction to take routine decisions and make training reproducible. This can change the selected epoch relative to v11. Tests must establish exactly-once validation/inference rows and unchanged training batch carry. Parent accepts the proposed final registry folder `/eos/user/c/cgupta/higgscharm/outputs/hww_mva_models/<workflow>__bhive5fold_<date>`.

The completed b-hive result is recorded in [[Projects/HToWW/framework/2026-11-12-bhive-pipeline-c1-resume]] (vault commit `d5548d4`, analysis commit `0bd528c`). Its CPU reproducibility, export and one-file RUN results are agent-reported; full model training was not launched. GPU check 9704454 was pending in that result. The duplication finding was newly delivered with that completion and is being corrected as a routine bug, not asserted to have been explicitly discussed in Chirayu's preceding approval.

Existing read-only grid monitoring remains enabled (schedule `3969fcfa-d977-455e-b3d6-0042bd1df669`, 20-minute interval; returned next run 13:58:12 CET). Its prompt now identifies the three worker ownership boundaries and requires the replacement manifest when available. It authorizes no duplicate submissions or analysis edits. Worker completion notifications, rather than delegate polling, return results to the parent.

## Shared-vault sync evidence before writing

The preceding worker reported `Cannot rebase onto multiple branches`. Parent inspected `scripts/sync-on-start.sh`, which already documents concurrent FETCH_HEAD writes as a possible cause; this observation alone does not prove the cause of that particular failure. Current `git status` shows no rebase/merge in progress; `git stash list` is empty. `git rev-list --left-right --count '@{u}...HEAD'` returned **0 behind, 67 ahead** of the locally recorded `ssh/keeper/vault-organised-20261105` upstream. Current FETCH_HEAD has one merge candidate, not multiple. No outstanding incoming commit is recorded in these refs. No pull/rebase/stash/config change was performed; the keeper-owned dirty edits and all local commits remain intact. This is a local ref check, not proof of freshly fetched remote state.

No production model training, RUN campaign, negrw switch, data deletion, credential renewal, job release/removal, push, Meta/README/deck edit or shared-tree consolidation was performed by this dispatch.
