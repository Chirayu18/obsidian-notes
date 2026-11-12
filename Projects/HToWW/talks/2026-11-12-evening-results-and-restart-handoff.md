---
tags: [reference, presentation]
status: active
date: 2026-11-12
source: laptop
evidence: mixed-direct-and-recovered
---

# Evening results and restart handoff

The main talk plan remains [[2026-11-12-november-update-slide-plan]]. Chirayu now plans to close the laptop, return in a few hours, and focus on the A/B result and finishing slides before tomorrow. This note records later requests and the latest operational boundary; it supersedes the queued-A status in [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-ab-grid-monitor-1840]], not its earlier measured snapshot.

## Results requested for slides

- Present the August→October developments, then the October pre-fix four-era full-systematics691 reference, then later updates. Preserve the distinction between historical and corrected production.
- Immediately after691, show the Higgs-scale treatment diagnostic: V0 unchanged; V1 make higgsbkg scale shapes shape-only while retaining its separate rate term; V2 also treat st/diboson/vjets that way. Source scripts `~/htoww_submit_logs/{run_higgs_scale.sh,higgs_scale_variants.py}`, logs `~/htoww_submit_logs/higgs_scale_20261112/`, node-local work `/tmp/cgupta_higgs_scale_20261112/`. Recovered parent history says V0 reproduced691. Direct V1 log read18:47 gives median703, expected16/84%469.0242/1106.5151. V2 still running at18:51; no result claimed. These are old-card diagnostics, not the corrected A/B limits or a validated final uncertainty prescription.
- New yields per era/process for A/B. A JSON exists at `~/htoww_submit_logs/yields_A_train_20261112.json` (18:34); numbers not reviewed here. Local script `/tmp/htoww-edits/train_yields.py`. B yields follow its preparation.
- New data/MC plots of MVA inputs; revisit the old broad bands and MET slope. Recovered earlier explanation attributes much of the plotted band to tt scale variations excluded from the fit; verify that statement on actual plotting configuration before presenting it as established current behaviour.
- A/B/v11 MVA performance: ROC/AUC per class, training curves, held-out scoring. Requires successful folds.
- A/B stat-only+autoMCStats and separate rate-uncertainty variants from TRAIN. Offline scorer/template tool remains unfinished per recovered history. Design: [[Projects/HToWW/framework/2026-11-12-train-stat-only-limit]]. Current TRAIN files require a merged SR. The intended full-systematics new result uses **two SRs, Nc-jet=1 and Nc-jet≥2**.
- Chirayu requested adding the **lepton-MVA alternative** immediately before quota failure. Exact alternative/comparison definition is not established by the recovered request; do not invent a working point or claim implementation.
- Preserve systematic explanations/check plots, signal-sample issues and GEN/conveners questions, Route A ratio vs B stitching, negrw v2 limitations, gridpack validations, and framework storage/failure-handling story from the main plan. Legacy-slim remains a proposal, not measured completed production. hDamp remains parked/uncompleted. Keeper owns the actual deck.

## New A training failure, found18:49–18:51

Direct `A/folds.dag.dagman.out` reports all five nodes failed with exit1; DAG exited18:43:34. No successful node. Fold0 event log records execution18:43:30 on b9pgpun205, assigned H100 MIG GPU, termination18:43:31, zero reported CPU time. All five stdout/stderr files are zero bytes. This supersedes the18:40 queued snapshot. It happened remotely before laptop closure, not because of suspension.

`~/bhive_prod_20261112_sol/fold_job.sh` enables `set -e`, then changes to b-hive, sources `~/.bashrc` with stdout/stderr suppressed, activates micromamba and sources setup before its first diagnostic echo. Read-only reproduction `bash -exc "source /afs/cern.ch/user/c/cgupta/.bashrc; echo STARTUP_REACHED"` on lxplus terminates inside `/etc/profile.d/kde.sh` at `grep -qs '^PRELINKING=yes' /etc/sysconfig/prelink`; STARTUP_REACHED is absent. This demonstrates a startup/errexit incompatibility on lxplus and strongly explains the batch symptom; the exact batch failing line was hidden and is not independently established. No GPU computation failure, OOM or trained-model corruption is evidenced. Recovery must diagnose/fix startup with visible logging before resubmission; this monitoring scope made no code/job changes.

## Laptop closure boundary

B `prepare.py` PID1314527 remains alive on lxplus901 at18:49 (elapsed2:11), under an SSH-session shell, with no ready.json. A separate existing remote loop PID1354640 on the connected lxplus host waits for B readiness and submits its folds; it was read, not created or polled as a delegate. It has a finite~110min bound from18:23, and survives only if its remote process/session survives. Both arms share fold_job.sh, so B has the same potential startup defect. No safe unattended completion claim follows.

V2 Combine likewise remains under an SSH-session shell. Existing completed files/notes are persistent; active SSH-owned preparation, submission helper and Combine are not guaranteed to survive laptop suspension. Condor jobs generally do not depend on the laptop, but A's jobs have already failed. No new watcher, credential operation, mutation, submission/release/removal, delegate or push was performed. No permission to silently change this read-only monitoring scope is inferred from the status questions.
