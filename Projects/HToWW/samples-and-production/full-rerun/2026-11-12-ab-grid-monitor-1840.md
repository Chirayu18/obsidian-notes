---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: direct-read-only-check
---

# A/B read-only monitoring, 18:40–18:45 CET

Continues [[2026-11-12-direct-continuation-training-launch]] and [[2026-11-12-event-mva-gpu-relaunch]]. This snapshot updates the operational state in [[2026-11-12-ab-grid-check-1359]]; historical snapshots there remain historical evidence.

## Completed TRAIN marker inventory

Read installed `condor/<workflow>/<era>/<dataset>/jobnum.txt` in `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, and fresh direct-server `eos root://eosuser.cern.ch find -f` listings under `/eos/user/c/cgupta/higgscharm/outputs/<workflow>/<era>/`. All eight listings succeeded. Only `.coffea` end markers count, including the established single-partition fallback.

- A (`hww_allfix_4fs__train`): 506/506 preEE, 1188/1188 postEE, 642/642 preBPix, 393/393 postBPix; **2729/2729** total.
- B (`hww_routeb_3fs4fs__train`): 523/523 preEE, 1246/1246 postEE, 681/681 preBPix, 414/414 postBPix; **2864/2864** total.

The remaining four data-only gaps from the 16:06 snapshot now have markers. Both retry4 ggH→WW partitions and all six replacement H→ττ partitions are included in these installed expectations. This establishes marker completeness, not independent payload/file/hash validation.

Queue join uses exact workflow UserLog paths and the first Args token. No duplicate live partition identities. The only original TRAIN queue entry is held `9701317.23`, partition24, with its existing successful marker and unchanged AFS transfer error; untouched. Diagnostic GPU test `9701591.0` remains transfer-held, also untouched.

## Production event-MVA state

At 18:40:07 CET, `condor_q -name bigbird28.cern.ch cgupta -af ClusterId ProcId JobStatus Args HoldReason` reports A DAG **9706908.0 running**, fold jobs **9706909–9706913**, folds0–4, **all idle**. No production fold is running or held in this snapshot. Saved A `folds.dag.dagman.out` at18:37 likewise reports five idle, zero successful/failed; five fold event logs exist,265bytes each.

`~/bhive_prod_20261112_sol/A/ready.json` records `ready:true`, timestamp18:18:33CET, analysis71eef55, **2437 MC markers,22613 parquets,6959308 rows**, feature hash36f655f4… and selection80e75bca…. Its five held-out fold row counts sum consistently to that total. This is the preparation program's saved PASS artifact, read directly; this monitor did not repeat its validation.

B `ready.json` is absent. A read-only nested SSH process check on **lxplus901** finds PID1314527 running `prepare.py B`, elapsed2:02:23,55.4%CPU, RSS3333456KiB. Its interactive stdout still has only the16:38 start line; stderr tail was empty. No B fold jobs appear in the owner queue. Lack of a readiness file is not a failure diagnosis while the process is alive.

Saved earlier `retry4_sol/validate_A.log` and `validate_B.log` end with `ready:false`; A has selected_rows PASS but dataset_file_coverage_and_scales FAIL. As the direct-continuation note explains, those standalone inventories predate late markers and require reconciliation; they are not silently relabelled PASS. A's later preparation artifact is separate evidence. No duplicate full-coverage validation was launched.

A `combine -M AsymptoticLimits ... -n _V1` process was also visible on the connected lxplus host (PID1390567, elapsed1:40 at18:40). It is the separate Higgs-scale diagnostic from the handoff, not a completed full-systematics A/B result. No result is claimed. Bounded Condor history query returned no rows before its15second timeout, so this check does not establish terminal exit codes or a fresh failure census from history.

## Boundary and next check

Current negrw configuration remains v2 (analysis71eef55), tau normalizationsb6d52ea. G3 fit-bin closure remains scientifically open. Keep the existing monitor enabled while A can be scheduled and B preparation can progress; no schedule change was needed. Parent owns direct recovery, validation, training, export and RUN. This monitor submitted/released/removed nothing, changed no analysis inputs/code/outputs, read no delegates, repeated no GPU test/unit test, and changed no credentials/services. Only this ordinary note is recorded and committed locally; no push. Preserve unrelated dirty files.
