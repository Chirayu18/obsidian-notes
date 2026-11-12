---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: executed-recovery
---

# A fold startup recovery and completed Combine diagnostics

Chirayu: **“Relaunch A before I close the laptop and inform me when the combine stuff is done”**. This authorizes the A relaunch, superseding the earlier read-only restriction for this bounded recovery. No delegate used. Follows [[2026-11-12-ab-grid-monitor-1840]] and [[Projects/HToWW/talks/2026-11-12-evening-results-and-restart-handoff]]. The failed original A DAG remains a failed run, not retroactively accepted training.

## Observed defect and fix

All original A nodes9706909–9706913 exited1 almost immediately; original DAG9706908 stopped18:43:34, zero successful nodes. Empty output/error logs and the startup wrapper locate failure before the first host/start echo. `set -e` plus sourcing the personal `.bashrc` exits reproducibly during the system profile scripts on lxplus. Batch's exact failing line remains hidden by the old wrapper's redirects.

Isolated recovery directory: `~/bhive_prod_20261112_sol/A/relaunch_20261112_startup1/`. Its `fold_job.sh` bypasses the personal login profile and initializes the established micromamba executable/root directly, activates the same b_hive environment, and sources the same b-hive setup. Adds an early host/fold message and ERR trap and removes setup output suppression. Original wrapper, recipe, generated fold commands, seeds, input/split manifests and failed logs preserved. The shared launcher used by B is unchanged; B therefore still has the related startup risk and needs the equivalent recovery before accepting its training result.

CPU-only check of the replacement environment initialization reached `STARTUP_PASS`, importing torch/law with `/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python`, torch2.5.1, rc0. No GPU test, unit-test repeat or actual training was run by that check.

| Prescription | Implementation/check | Saved evidence | Boundary |
|---|---|---|---|
| Bypass demonstrated login-profile startup failure | Direct micromamba hook, same environment/setup, visible error trap | staged wrapper; original copy `fold_job.original.sh`; CPU-only STARTUP_PASS | Batch startup still to be observed |
| Reuse complete prepared A inputs | Assert ready.json true, analysis71eef55; record readiness/command SHA256 | `preflight.json` | No repeated full coverage validation |
| Preserve successful-output guards | Check all generated dataset/training/test versions across DatasetConstructorTask/TrainingTask/InferenceTask | preflight clashes=[] | No cache deletion or bypass |
| Relaunch only once | Fresh owner queue JSON guard for A fold Args and A Iwd; no existing stage DAG log | `submit.log` | Later job success not implied |
| Valid submit files | bash syntax, fold condor dry-run, DAG no-submit | `fold.dryrun.ads`, `preflight.json` | Checks do not execute GPU training |

New isolated A DAG **9706925** submitted successfully using `condor_submit_dag -f folds.dag` from the recovery directory. Five nodes F0–F4 use its isolated fold.sub/wrapper. This is a new submitted workflow, not a completed training claim. Condor owns execution independently of the laptop connection. No held job released/removed, inputs modified, credentials/services changed or push performed.

Verified at **18:55:59 CET**: DAG9706925 JobStatus2; folds0–4 **9706926–9706930**, all JobStatus1 (idle). No duplicate A fold jobs appeared. Startup on a batch node and training success remain pending.

## Combine finished before laptop closure

Direct saved-log read from `~/htoww_submit_logs/higgs_scale_20261112/{V1,V2}.limit.log`:

- V1: median expected703;16/84%469.0242/1106.5151;2.5/97.5%337.7695/1726.8495.
- V2: median expected691;16/84%461.0181/1093.1359;2.5/97.5%332.0039/1715.3190.
- V0 unchanged baseline691 was reproduced according to recovered prior parent history; not rerun here.

V1 removes inclusive rate changes from higgsbkg scale templates while retaining the existing rate term. V2 also applies this to st/diboson/vjets. Source scripts `~/htoww_submit_logs/{run_higgs_scale.sh,higgs_scale_variants.py}`; node-local files `/tmp/cgupta_higgs_scale_20261112/`. All are blind Asimov old-card diagnostics. They are not corrected A/B production results or proof that a final systematic prescription is scientifically complete. No Combine completion schedule is needed because both requested diagnostic variants have finished and the user is informed in this turn.

Slide storyline and remaining results are preserved in [[Projects/HToWW/talks/2026-11-12-november-update-slide-plan]] and [[Projects/HToWW/talks/2026-11-12-evening-results-and-restart-handoff]]. Next priority after successful folds is checked export and the unfinished TRAIN-to-template scorer for the merged-SR A/B result. Final full-systematics cards retain the intended two Nc-jet SRs. G3 fit-bin closure remains scientifically open.
