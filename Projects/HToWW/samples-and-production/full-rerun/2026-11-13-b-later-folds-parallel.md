---
tags: [reference, production, decision]
status: superseded
superseded_by: "[[2026-11-13-b-folds-2-3-interactive]]"
date: 2026-11-13
source: laptop
evidence: executed-submission
---

# B later folds moved to parallel jobs, later folds first

Chirayu: **“Can you submit b's fold 2,3,4 in parallel such that they won't conflict with currently running folds 2,3,4 ?”**, then **“Submit later folds first...”**. This supersedes the all-five-sequential scheduling decision in [[2026-11-12-b-fold-startup-fix]] for folds2–4 only. No delegates or extra training recipe changes.

## State before handoff

At05:52:54CET, B job9706954 runs **fold1 DatasetConstructorTask**, dataset versionhwwBv2sol_46deafa8_f1_train. Fold0 training and inference completed; its training record04:22:17–04:39:49CET shows17m32s training. The overall B job began01:36:58CET, so the dominant first-fold time was preparation/conversion of many EOS shards. Later fold dataset/training/inference outputs were absent, and no separate B2/B3/B4 jobs existed in the queue.

A's original five-fold replacement DAG9706925 completed all five nodes successfully02:39:27CET, with no failed nodes. All five training records say completed and their best checkpoint hashes match. A export via the unchanged `scripts/mva/export_fold_onnx.py` is running independently of this B scheduling change; no completed export/registration/limit claimed here.

## Conflict prevention and implementation

Work directory `~/bhive_prod_20261112_sol/B/parallel_later_20261113/` preserves `serial.before.sh`, the new parallel `fold_job.sh`, `fold.sub`, dry-run ads/logs, `ownership.json`, per-fold submit logs and `submissions.json`.

1. Copied the checked B startup wrapper unchanged into the parallel directory. Existing cache guards, ready.json check, fold extraction, training recipe/seeds and environment remain intact.
2. Atomically updated only the original serial launcher's file `B/startup_fix_20261112/fold_job.sh` to **skip folds2,3,4 before startup**, logging that ownership has transferred to the parallel jobs. Its already-running fold1 invocation retains its old script handle and continues unaffected; future serial child invocations open the new dispatch gate. Did not alter live model/data outputs or stop the current job.
3. Verified the serial skip for4,3,2 by executing that early-return path: rc0 and the expected skip message each time. Ran shell syntax checks and Condor submit dry-runs for all three new jobs. Rechecked the live queue and all three folds' dataset/training/inference version paths before submission: no clashes.
4. Submitted **4, then3, then2** as separate jobs, one GPU each, same4CPU/24GB/tomorrow resource request. Set per-job priority to fold number (4>3>2) to express the same preference within the owner's queue; actual scheduling remains Condor's decision.

| Fold | New job | Execution ownership |
|---|---|---|
|4|9708299.0|new parallel wrapper, original serial skips |
|3|9708300.0|new parallel wrapper, original serial skips |
|2|9708301.0|new parallel wrapper, original serial skips |
|1|9706954.0|existing running serial job |
|0|completed within9706954.0|saved outputs preserved |

**Completion accounting:** the original DAG now represents the serial-owned work (0/1 and explicit skips), not proof that all five B folds finished. Its original wrapper may print “all folds completed” after the skip calls; that line alone must not be used for B acceptance. Require actual completed training/inference outputs and provenance for all five fold versions, plus successful separate jobs, before export/registration. A and B version prefixes remain distinct. No successful output overwritten, guard bypassed, held job released/removed, credentials/services changed or data deleted. No push.

The previous12–16h estimate assumed sequential execution of the remaining folds and is superseded as a current ETA by this scheduling change. Remaining time now depends on GPU queue wait and the slowest parallel fold; no guaranteed completion time is established.
