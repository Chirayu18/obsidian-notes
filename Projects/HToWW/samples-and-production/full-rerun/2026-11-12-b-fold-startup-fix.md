---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: executed-check
---

# B launcher prepared while split preparation continues

Chirayu asked **“Why cant you do B now”**, following the explicitly requested A relaunch. Applied the same bounded startup recovery to B, without submitting incomplete inputs or duplicating preparation. This updates the earlier B-unfixed boundary in [[2026-11-12-a-fold-startup-relaunch]].

At19:00:08CET, B `ready.json` is still absent. Direct process read on lxplus901: PID1314527 `prepare.py B`, elapsed2:22:07, under the existing interactive apptainer/SSH process chain. Existing submission helper PID1354640 on lxplus932 waits for readiness and rc0, then submits B's five folds; not created/replaced by this action. No B fold/DAG in the owner queue, no existing B DAG execution log. A replacement DAG9706925 remains running with five idle folds9706926–9706930.

Created `~/bhive_prod_20261112_sol/B/startup_fix_20261112/`: wrapper byte-identical (SHA256 asserted) to the CPU-checked A recovery wrapper, original B submit-file backup `fold.sub.before`, syntax and Condor dry-run logs/ads, and `manifest.json`. Atomically updated **only the executable path** in `B/fold.sub` to this wrapper. Recipe, fold arguments, output paths, resources, commands/manifests and selection unchanged. Fresh queue guard found no B jobs, and no existing DAG execution log. `bash -n` and `condor_submit -dry-run` passed; no repeated GPU/unit test or environment check needed for identical wrapper bytes.

The existing helper references B/fold.sub and therefore will use the fixed launcher if preparation passes while it remains alive. No B training submission is claimed here. SSH-owned preparation/helper survival after laptop suspension remains unguaranteed; no service/credential change, detach/restart, new watcher or output deletion was performed. Do not confuse a corrected launcher with completed B preparation or successful batch training. No push; only this note committed locally.
