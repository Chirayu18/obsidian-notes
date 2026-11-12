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

## Step 1: split → commands → bash -n → law parse (2026-11-12, resumed session)

- Repo HEAD is now `eaab247` (Route B stitching; touches `analysis/processors/base.py`, filesets).
  Recomputed at `eaab247`: `features_hash 36f655f4…c976e`, `selection_hash 80e75bca…f584`,
  **still equal to the TRAIN v2 parquet metadata** (neither `base.py` nor filesets are hashed).
  Production `split_folds`/`register_folds` must run with these hashes unchanged.
- The split must live on EOS for a Condor GPU job, and its lists hold absolute paths whose
  sha256 is in the manifest, so it was **regenerated, not copied-and-edited**: the container ran
  `subset_split.py` with `-B /tmp/…/eosout:/eos/user/c/cgupta/HToWW/b-hive/output` (no `-B /eos`),
  then the directory was copied to EOS. Same rows as before (`check_train_rows PASS: 324612 rows
  in 13 samples`; per model ≈256k train / ≈64k test). Rows per label
  `{-1 (data): 4348, hplusc: 5468, higgsbkg: 12975, tt: 191586, st: 107746, diboson: 2339, vjets: 150}`
  (subset, not representative; vjets is tiny).
  Split: `/eos/user/c/cgupta/HToWW/b-hive/output/test_20261112_split_v1sub` (filelist tag `05d7e0f8`).
- `bhive_fold_commands.py` (real script) on the EOS split:
  `test_20261112_cmds_v1sub/run_folds.sh` (no seed) and `test_20261112_cmds_v1sub_seed/run_folds.sh`
  (`--split_seed 20261112`): **`bash -n` OK both**; the seeded one has 10 `--split-seed` flags
  (TrainingTask + InferenceTask × 5) and is otherwise byte-identical to the unseeded one.
  List sha256 on EOS equal the manifest (model_0/train.txt `7d624520…`).
- `law` parse (b_hive env, `parse_test.sh`, log `/tmp/cgupta_bhivetest_20261112/parse_test.log` on lxplus914):
  every generated command run with `--print-status 0` (instantiates the task and its output targets,
  runs nothing). `DATA_PATH after setup.sh: /eos/user/c/cgupta/EPR_task/b-hive/output` →
  **`setup.sh` ends with `source local_setup.sh`, which points DATA_PATH at the v11 (EPR_task) output;
  every test/production shell must `export DATA_PATH=…` after `source setup.sh`.** With the override
  all targets resolve under `/eos/user/c/cgupta/HToWW/b-hive/output/{DatasetConstructorTask,TrainingTask,InferenceTask}/HPlusCHToWW_2dcats/test_20261112_05d7e0f8_f<i>…`,
  unique per fold (results line below).

## Seeding change in the HToWW b-hive copy (`/eos/user/c/cgupta/HToWW/b-hive`, uncommitted, like its other local diffs)

Originals backed up to `output/test_20261112_scratch/bhive_orig/` (sha256 `734d58c8…` training.py,
`524d672d…` parameter_mixins.py).
- `tasks/parameter_mixins.py` `TrainingDependency`: new `split_seed = luigi.IntParameter(default=20261112)`
  (shared by TrainingTask and InferenceTask; not in `store_parts`, so output paths are unchanged).
- `tasks/training.py`: `np.random.shuffle(files)` (unseeded global RNG) replaced by
  `seeded_train_val_split(files, train_val_split, split_seed, n_train_files)`: shuffles a copy with
  `np.random.default_rng(split_seed)`; slicing identical to the original (incl. the old
  `n_val == 0 → validation = all files` quirk). `write_split_record` writes
  `<training dir>/train_val_split.json` (seed, counts, sha256 and full lists of training/validation files).
- Unit check in b_hive (py 3.11.10, torch 2.5.1, numpy 1.23.5, onnx 1.14.1, onnxruntime 1.17.3):
  same seed → identical split; other seed → different; lists disjoint and complete; input list
  and global `np.random` state untouched (so `LZ4Dataset`'s per-epoch shuffle keeps its old
  behaviour). **Not reproducible yet:** torch weight init and per-epoch file order are still unseeded
  (out of scope; only the split was asked for).

## Analysis-repo changes (`scripts/mva/*`, tests), uncommitted at this point

- `bhive_fold_commands.py`: `build(..., split_seed=None)`; CLI `--split_seed` (default 20261112;
  negative = omit for an older b-hive). Passed to TrainingTask and InferenceTask, recorded in `bhive_runs.json`.
  `None` reproduces the old command line exactly.
- `register_folds.py`: `--diagnostic_only` (TEST ONLY). Writes `diagnostic_only: true` (RUN then needs
  `--allow_diagnostic_model`, and that is refused with `--submit`); a split with non-current hashes is
  recorded (`training_data.split_features_hash/split_selection_hash/split_matches_workflow`) instead
  of refused. Without the flag: unchanged (still refuses).
- New `export_fold_onnx.py` (run in b_hive): loads each fold's `best_model.pt` exactly like
  `analysis/postprocess/inference.py`, exports `softmax(model.net(x))` (one float32 `(N,26)` input,
  6 probabilities; valid because `n_cpf = n_npf = 0`), and compares onnxruntime with the original
  `model((X, zeros(N,0,0), zeros(N,0,0)))` call on that fold's held-out test shards; writes
  `export_validation.json` with `max_abs_onnx_torch_diff` (k values, tolerance 1e-5) for `register_folds --validation`.
  No fill/clipping (b-hive and the legacy path feed raw features; TRAIN writes nonfinite as 0; nonfinite → error).
- New `tests/test_mva_bhive.py` (5 tests). Container run: `tests.test_mva_bhive` + `tests.test_trainrun_blockers`
  → 21 tests, all pass except one skipped (torch+onnx export test; container has torch but no onnx)
  and `test_bhive_config_and_onnx_io_checks`, which fails only because `/eos/user` is unreadable in the
  container on lxplus914 (`PermissionError`); with the config bound from a /tmp copy it passes (`Ran 6 tests … OK (skipped=1)`).

## Step 2: one fold on GPU (Condor)

- Submitted cluster **9701591** from `~/bhive_test_20261112` (`fold0.sub`, `fold0_job.sh`): 1 GPU (any,
  AlmaLinux9), 4 CPU, 16 GB, `workday`, `getenv=True`. Runs only the guard + model 0 block of
  `test_20261112_cmds_v1sub_seed/run_folds.sh` with `--epochs 2`, each `law run` timed, then re-runs the
  block to check the guard refuses.
