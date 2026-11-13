---
tags: [reference, production]
status: superseded
superseded_by: "[[2026-11-13-b-later-folds-parallel]]"
date: 2026-11-12
source: laptop
evidence: executed-check
---

# B launcher prepared while split preparation continues

Chirayu asked **“Why cant you do B now”**, following the explicitly requested A relaunch. Applied the same bounded startup recovery to B, without submitting incomplete inputs or duplicating preparation. This updates the earlier B-unfixed boundary in [[2026-11-12-a-fold-startup-relaunch]].

At19:00:08CET, B `ready.json` is still absent. Direct process read on lxplus901: PID1314527 `prepare.py B`, elapsed2:22:07, under the existing interactive apptainer/SSH process chain. Existing submission helper PID1354640 on lxplus932 waits for readiness and rc0, then submits B's five folds; not created/replaced by this action. No B fold/DAG in the owner queue, no existing B DAG execution log. A replacement DAG9706925 remains running with five idle folds9706926–9706930.

Created `~/bhive_prod_20261112_sol/B/startup_fix_20261112/`: wrapper byte-identical (SHA256 asserted) to the CPU-checked A recovery wrapper, original B submit-file backup `fold.sub.before`, syntax and Condor dry-run logs/ads, and `manifest.json`. Atomically updated **only the executable path** in `B/fold.sub` to this wrapper. Recipe, fold arguments, output paths, resources, commands/manifests and selection unchanged. Fresh queue guard found no B jobs, and no existing DAG execution log. `bash -n` and `condor_submit -dry-run` passed; no repeated GPU/unit test or environment check needed for identical wrapper bytes.

The existing helper references B/fold.sub and therefore will use the fixed launcher if preparation passes while it remains alive. No B training submission is claimed here. SSH-owned preparation/helper survival after laptop suspension remains unguaranteed; no service/credential change, detach/restart, new watcher or output deletion was performed. Do not confuse a corrected launcher with completed B preparation or successful batch training. No push; only this note committed locally.

## Requested single-job B submission, after19:21CET

Chirayu asked **“Can you submit all 5 B's fols as 1 job?”**, followed by whether closing the laptop would preserve B progress. B still has no readiness marker; preparation remains SSH-owned. No safe laptop-disconnect claim is established.

Prepared `B/single_job_20261112/all_folds.sh` to invoke the checked B fold launcher sequentially for folds0–4, failing immediately if a fold fails. One GPU with the same existing resources/flavour; training recipe, per-fold versions and guards unchanged. Five folds run sequentially, not simultaneously. Syntax, Condor submit dry-run and DAG no-submit all passed; logs/ads saved in that directory. Preserved the original five-node DAG as `folds.dag.before`. Fresh owner queue and absence of B DAG execution log confirmed no live B campaign before the change.

Atomically changed **B/folds.dag** to one node `ALL_FOLDS`, referencing `single_job_20261112/all_folds.sub`. The existing finite helper still waits for ready=True and prep rc0, then submits the current DAG. No additional watcher or incomplete-input submission. Latest queue check still has no B jobs; A has two running and three idle folds. Earlier wording about the helper submitting five independent jobs is superseded by this one-job request. No push, credentials/services change, deletion, release/removal or duplicate preparation.

## Preparation complete and B submitted: verified19:32:27CET

B preparation exited **rc0 at19:24:40CET**. Direct `B/ready.json` read: ready=true, workflowhww_routeb_3fs4fs, **6978013rows,2572markers,24598parquets**, feature36f655f4… and selection24b63ba3…. Completed split manifest exists (6900582bytes), SHA256f965d5752121568039c40db0f936eb3ebb059c4d569dcbddc2823e8725996ab3. This is the preparation program's saved PASS artifact, not a repeated independent validation.

Existing helper submitted the one-node DAG: **9706953 running**, **9706954 idle**, Args `B all`. This job runs the five folds sequentially using the corrected launcher. No duplicate B job in owner queue. A DAG9706925 remains running, folds9706926/9706927 running and9706928–9706930 idle. Batch startup/training success remains pending; queue state is not completed training.

The earlier laptop-closure blocker is now resolved: preparation is completed/persistent, and A/B are owned by Condor independently of laptop SSH. Chirayu can close the laptop without interrupting these submitted jobs. Combine diagnostics and all presentation decisions are already recorded; no further wait for the finite SSH helper is required.
