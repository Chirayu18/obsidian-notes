---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# b-hive 5-fold training pipeline test (TRAIN v1 subset), 2026-11-12

**Status: agent-reported, in progress.** Test-only run on stale TRAIN v1 ntuples so the
production 5-fold event-MVA training can start once TRAIN v2 is complete. No production
training launched. Runbook: [[2026-11-05-run-framework-legacy-train-run]], handoff
[[2026-11-05-trainrun-blocker-fixes]].

Where: analysis repo `lxplus:/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
(branch `hww-analysis`), b-hive checkout `/eos/user/c/cgupta/HToWW/b-hive` (env `b_hive`,
micromamba under `/eos/user/c/cgupta/EPR_task/b-hive/micromamba`). Scratch on lxplus914
`/tmp/cgupta_bhivetest_20261112`; test outputs `/eos/user/c/cgupta/HToWW/b-hive/output/test_20261112_*`.

## Step 0: state inherited from the first attempt (stopped 2026-11-12 ~00:30 to move accounts)

- v11 provenance: trained from `/eos/user/c/cgupta/HToWW/b-hive` with env `b_hive`, Condor
  `~/submitter_mva_2dcats.sub` (H100, `nextweek`, `getenv=True`), `DATA_PATH` →
  `/eos/user/c/cgupta/EPR_task/b-hive/output` (set by `local_setup.sh`).
- TRAIN v2 parquet (`hww_allfix_4fs__train/2022postEE`, one DY shard) carries
  `features_hash 36f655f4…`, `selection_hash 80e75bca…` = repo HEAD `f84d311` at the time.
- TRAIN v1 (`hww_allfix_4fs__train_v1_20261110`) hashes differ (`3b912cbb…`/`caa0f7a2…`): test-only.
- v1 2022postEE is internally inconsistent: `MuonEGRun2022E` (and G) have parquet
  partitions but no `.coffea`; `scripts/check_train_outputs.py` on the full era fails (rc=1),
  as it should.
- `split_folds.normalization` → `get_dataset_config` resolves paths relative to cwd: run from the repo root.
- Subset split (13 samples, all 6 classes + one data sample) built with a test driver
  `subset_split.py` (bypasses only the hash-equality and full-coverage checks):
  `check_train_rows PASS: 324612 rows in 13 samples`; per model ≈256k train / ≈64k test rows.
- No Condor jobs, no b-hive test outputs existed when resumed.

(Steps below are appended as they run.)
