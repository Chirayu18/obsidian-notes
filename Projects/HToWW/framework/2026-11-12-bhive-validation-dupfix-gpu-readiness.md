---
tags: [reference, production]
status: active
date: 2026-11-12
source: lxplus
evidence: agent-reported
---

# b-hive validation/inference duplication fix, GPU reproducibility and A/B launch readiness (12 Nov 2026, afternoon)

**Status: agent-reported.** This continues [[2026-11-12-bhive-pipeline-c1-resume]] after the Claude 1 quota failure recorded in [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-afternoon-approved-followups]]. It was run on Claude 2. It updates that note's gates 2–5; its launch plan §5 otherwise stands.

The parent decided to fix the duplication before production. That was a routine decision under Chirayu's "make reproducible" / "do all that" instructions, and it changes best-epoch selection relative to v11.

All checks are **diagnostic**: stale TRAIN v1 subset, fold 0, new versions only. No production training, no GPU job, no Condor submission. No job release/removal/edit (held 9701591 left as is: status 5, hold code 12). No deletion, no credential renewal, no push.

## c1 partial state (inspected before editing)

c1 left **no partial changes**:
- b-hive `tasks/training.py` `30491b5b…`, `tasks/parameter_mixins.py` `2b541721…` and `tests/test_htoww_reproducibility.py` `b4bc0483…` match the c1-resume record.
- `utils/torch/LZ4Dataset.py` equalled HEAD (`667903a4…`).
- No b-hive file outside `output/` changed after 13:40.
- The analysis repo was at `0bd528c` with clean tracked files.

Backups: `/eos/user/c/cgupta/HToWW/b-hive/output/test_20261112_scratch/bhive_pre_dupfix/` (incl. `git_diff_HEAD.patch` `6bf9edd7…`) and `~/bhive_test_20261112/analysis_pre_dupfix/`.

## GPU same-seed result (cluster 9704454, pre-fix code)

Read from `~/bhive_test_20261112/c1repro/gpu_cmp.out` and `gpu_job.9704454.out`:
- Host b9g57n0024, **NVIDIA A100-PCIE-40GB**, 2 epochs × 2 runs (`c1repro_gpu_{a,b}_e2`), both rc 0.
- **`bitwise_identical_weights: True`, max |Δw| 0.0.**
- val loss 0.0032909818952536127 for both.
- seeds 20261112/20261112, matmul precision `medium`, best `461cc7978d00`, config `2024ecc54491`, input list `f45b8bd6fb8a`, train list `e935d77ff416`.
- Deterministic-algorithm warnings: 0 in each log (`grep -c "does not have a deterministic implementation"`).

Scope:
- This holds for the same GPU type and stack. It ran on the pre-fix LZ4Dataset.
- The fix changes only the validation rows, not the training path (shown below), so no new GPU run was made.
- Any GPU-to-GPU statement for production is limited to this A100 result. Pin the GPU model if bitwise re-reproduction will be needed.

## Fix (implemented, tested)

b-hive commit **`195fd67`** (local, on `ce3bdd5`, not pushed). Only my 5 files are in it. Other agents' dirty files are untouched and still uncommitted: configs, `train_MVA.sh`, `utils/loss/HierarchicalCrossEntropyLoss.py`, `utils/models/base_model.py`.

- `utils/torch/LZ4Dataset.py` (`ecfd729f…`):
  - `leftover_data = None` right after the test-mode partial-batch `yield`;
  - module marker `TEST_LEFTOVER_EMITTED_ONCE = True`;
  - no other change. Training-mode carry, permutation, batching and weighted sampling are as before.
- `tasks/training.py` (`c2886e6b…`): provenance pins the actual code (schema 2).
  - `lz4dataset_sha256` added to `PROVENANCE_KEYS`. The cache guard therefore **refuses any run directory made with other LZ4Dataset code**, which includes all pre-fix `c1repro_*` and test directories. Legacy directories without a record keep the old behaviour.
  - `software.code_sha256` for `tasks/training.py`, `tasks/parameter_mixins.py`, `utils/torch/LZ4Dataset.py` and `utils/models/base_model.py`.
  - `bhive_git_dirty_files`, and `lz4dataset_test_leftover_emitted_once`, read from the module via `importlib` (`utils.torch` re-exports the class under the module's name).
  - The full `git diff HEAD` is saved as `bhive_git_diff_HEAD.patch` in the run directory; its sha is `bhive_git_diff_sha256`.
- `tests/test_lz4dataset_leftover.py` (new, `a5b219a3…`) and `tests/test_htoww_reproducibility.py` (`e1b4fb5f…`).
- No change to class weights, features, architecture, precision ("medium" matmul stays), split recipe or seeds.

Analysis repo commit **`8535275`** on `hww-analysis` (local, parent `0bd528c`, not pushed). Only 3 files:
- `export_fold_onnx.py` (`0420aee4…`) records `lz4dataset_sha256`, the fix flag and the b-hive diff sha per fold.
- `register_folds.py` (`f644f0e7…`): **production** registration now refuses a fold trained without the fix, without the LZ4Dataset hash, or with LZ4Dataset code that differs from the other folds'. Diagnostic registration is unchanged.
- `tests/test_mva_bhive.py` (`23a83fd9…`).

## Tests run

- **b-hive unit tests** (`b_hive` env after `source setup.sh`): `python -m unittest tests.test_lz4dataset_leftover tests.test_htoww_reproducibility` → **9/9 OK**.
  - Fixture: 9 LZ4 files of 300/1000/37/1024/2049/5/700/128/511 rows, batch 256. These include partial batches, a file smaller than a batch, exact multiples and a tiny file.
  - Each row carries a unique id in feature 0, weight = id+1 and process = file index. Truths, weights and process are checked to stay aligned with the ids.
  - **Exactly once:** `validation` and `inference`, each with direct iteration and DataLoader workers 0/2/3. Every id is emitted exactly once, and no batch exceeds 256 rows.
  - **Sensitivity:** the HEAD code (`git show HEAD:…`) emits more than N rows for the same input.
  - **Training unchanged:** fixed vs HEAD code, same seed, workers none/0/2/3 → bitwise-identical batch sequences. All batches are full and no id repeats. Partial batches are carried across files; only each worker's final tail is dropped.
  - **Provenance:** the LZ4Dataset sha is pinned, the saved diff's hash equals the recorded one, the fix flag is True, and a stored `pre-fix` hash is refused.
- **Analysis:**
  - container `coffea-base-almalinux9:0.7.30-py3.10`, `python3 -m unittest tests.test_mva_bhive tests.test_trainrun_blockers` → **29 OK, 1 skipped**;
  - `b_hive` env, `TestOnnxExport` + `TestExportRecordChecks` → **6/6 OK**, including the new cases: pre-fix training, missing LZ4Dataset hash, mixed LZ4Dataset code.
- **Bounded CPU regression on real data** (lxplus932, 15:13–15:14). Script `~/bhive_test_20261112/c1dupfix/run.sh`, logs `train.log`, `infer.log`, checks `check.py/.out`, `check2.py/.out`, `training_record.out`.
  - Run: new version `c1dupfix_cpu_e1`, 1 epoch, fold-0 constructed datasets read-only. TrainingTask rc 0, then InferenceTask rc 0.
  - InferenceTask: **64,073 prediction rows = 64,073 held-out events** (pre-fix: 170,465).
  - Truth counts are 1084 / 2478 / 38387 / 21639 / 457 / 28. hplusc 1084 and vjets 28 equal the parquet counts in the c1-resume note.
  - 64,067 distinct prediction rows. The 6 repeats come from **6 identical rows already in the test LZ4 input** (64,073 rows, 64,067 distinct full rows), not from the loader.
  - Validation emission on this run's 129 validation files: fixed code **38,700 rows = 38,700 rows**; HEAD code 103,980 (2.69×).
  - **Training unchanged on real data:** epoch-0 `model_0.pt` is bitwise identical to the pre-fix `c1repro_cpu_a` (23 tensors, max diff 0.0).
  - val loss 0.0049125 vs pre-fix 0.0045238. The validation sample changed; the training did not.
  - Provenance `completed`, schema 2, `lz4dataset_sha256 ecfd729f…`, fix flag True, saved patch hash matches, `best_model` `799b883d…`. The recorded `code_sha256` equal the committed files.
  - `export_fold_onnx.training_record` on this checkpoint returns the fix flag and LZ4Dataset hash.

Keep: `c1dupfix_cpu_e1` Training/Inference directories and `~/bhive_test_20261112/c1dupfix/`. They are **diagnostic only**.

## A/B launch readiness

The procedure is that of [[2026-11-12-bhive-pipeline-c1-resume]] §5, with these updates:
- **Code:**
  - analysis repo at **≥ `8535275`**, no tracked changes;
  - b-hive at **`195fd67`** plus the other agents' uncommitted diff. That diff is saved per fold as `bhive_git_diff_HEAD.patch` and hashed.
  - `config/HPlusCHToWW_2dcats.yml` is untracked in b-hive; its sha (`2024ecc5…`) is pinned in provenance and in registration.
- **Recipe:** class weights only (`--loss-weighting`, `reweighting_mode: class`), inner b-hive split 85/15 (`split_seed` 20261112), `training_seed` 20261112, epochs 30. Outer folds `event % 5`; RUN scores all events with the held-out fold model.
- **Fresh versions:** prefix `hww<P>v2`, new `prod_<D>_<P>_*` directories. The guards refuse any existing or pre-fix directory.
- **Registry (parent accepted):** `/eos/user/c/cgupta/higgscharm/outputs/hww_mva_models/<workflow>__bhive5fold_<D>`. Not created yet. `register_folds.py --output` creates it at registration.
- **GPU:** one job per fold, `request_GPUs = 1`, no output transfer. Optionally pin `TARGET.GPUs_DeviceName` to an A100 type to match the tested reproducibility.

**Gates:**
1. **BLOCKED (sample worker / parent):** complete, validated TRAIN v2 coverage for A `hww_allfix_4fs` and B `hww_routeb_3fs4fs` in all four eras.
   - Requires a `check_train_outputs` pass against the revised expected-partition manifest (remaining jobs + Summer23 v14-v2 H→ττ replacement).
   - Requires parquet hashes: A `36f655f4…/80e75bca…`, B `36f655f4…/24b63ba3…`.
   - No production training before this.
2. **Open, physics:**
   - The **125.09 GeV** normalization is **not globally validated**; it is the sample worker's task and has not been checked here.
   - **negrw G3** closure in the final fit bins is still open. No negrw model/config switch.
3. Done: GPU same-seed check (A100 bitwise); duplication fix with exactly-once tests; registry location; b-hive and analysis commits (local).
4. Production launch itself: after gate 1, plus Chirayu or the parent confirming gate 2 is not a blocker for training.

## Needs you / next action

- Nothing needs Chirayu for the code.
- `195fd67` (b-hive, EOS checkout) and `8535275` (analysis) are local commits only. Pushing either repo needs Chirayu's OK.
- Production training waits on TRAIN v2 coverage (gate 1).
