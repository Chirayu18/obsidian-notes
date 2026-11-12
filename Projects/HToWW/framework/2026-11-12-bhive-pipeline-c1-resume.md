---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# b-hive 5-fold pipeline: fold-0 completion, reproducible training, production plan (c1 resume, 12 Nov 2026)

**Status: agent-reported.** This resumes [[2026-11-12-bhive-training-pipeline-test]] after [[2026-11-12-bhive-pipeline-interrupted-handoff]]. It **updates** that note's "not reproducible yet" statement (keeper: consider marking it superseded). All checks below ran on the **stale TRAIN v1 subset** (13 samples, 2022postEE, 324,612 rows) with a **diagnostic** 2-epoch fold-0 model. No production training, no use of v1 or diagnostic models for production. No job release/removal, no data deletion, no credential renewal, no push.

Legend: **implemented** = code written; **tested** = I ran it and quote the result; **author log** = predecessor's log, trusted and not re-run; **unrun/pending** = not done.

## Snapshot before changes (13:07 CET)

- Analysis repo `lxplus:/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `0995853` (other agents committed since the predecessor's `eaab247`). Tracked dirty files: only my two (`scripts/mva/bhive_fold_commands.py` `2e02459f…`, `scripts/mva/register_folds.py` `60b8fab1…`). Untracked owned files: `export_fold_onnx.py` `533845b9…`, `tests/test_mva_bhive.py` `eb04f5bb…`. Backups: `~/bhive_test_20261112/analysis_pre_c1resume/`.
- b-hive `/eos/user/c/cgupta/HToWW/b-hive`, HEAD `ce3bdd5`. My files: `tasks/training.py` `6dd767ef…`, `tasks/parameter_mixins.py` `bc285971…`. Backups: `output/test_20261112_scratch/bhive_pre_c1resume/`. The pristine originals stay in `output/test_20261112_scratch/bhive_orig/`. Other agents' dirty b-hive files (configs, loss, `base_model.py` instrumentation) were not touched.
- Current workflow hashes (container, `0995853`; unchanged by my commit):
  - A `hww_allfix_4fs`: features `36f655f4724c…`, selection `80e75bca3f23…`, the same as TRAIN v2 metadata.
  - B `hww_routeb_3fs4fs`: features `36f655f4724c…`, selection **`24b63ba31bf6…`**.
  - Classes for both: `hplusc, higgsbkg, tt, st, diboson, vjets`.

## 1. Completed vs unfinished stages found (no reruns)

| stage | evidence | state |
|---|---|---|
| ONNX export unit tests 2/2 | predecessor activity 217 | author log (trusted) |
| v11 checkpoint export, about 3e-7 | `output/test_20261112_onnx_v11check/export_validation.json` (max 2.4–3.0e-7 per fold) | saved output exists |
| fold-0 GPU job 9701591 | `~/bhive_test_20261112/fold0.9701591.{out,err}`: rc 0 at 01:12:54; guard rerun rc 1. Times: train construction 3m14s, test 47s, TrainingTask (2 epochs) 1m50s, InferenceTask 18s | done; still **held** only by output transfer (`fold0.sh` was written to the b-hive dir, not the sandbox). Not released or removed |
| fold-0 artifacts | `TrainingTask/HPlusCHToWW_2dcats/test_20261112_05d7e0f8_f0_train/test_20261112_05d7e0f8_f0/SimpleMLP_MultiClass/epochs_2/nominal/`: `best_model.pt` `9873fe04…`, `model_{0,1}.pt`, `train_val_split.json` (seed 20261112, train `e935d77f…`, val `4743b72d…`); InferenceTask `prediction/truth/process/kinematics.npy` | preserved |
| fold-0 export, registration, RUN smoke | none before this session | **done now**, see §2 |

## 2. Fold-0 completion (tested, diagnostic only)

**Export and torch parity.** The fold-0 `best_model.pt` was given for all 5 fold slots.
- Command: `B_HIVE_DIR=/eos/user/c/cgupta/HToWW/b-hive python scripts/mva/export_fold_onnx.py --bhive_path /eos/user/c/cgupta/HToWW/b-hive --checkpoints <f0 best_model.pt ×5> --split …/test_20261112_split_v1sub --output …/output/test_20261112_onnx_f0diag`
- Environment: `b_hive` (torch 2.5.1, onnx 1.14.1, onnxruntime 1.17.3, numpy 1.23.5).
- Max |ONNX − torch| on held-out fold 0: **3.58e-7** (64,073 events). Folds 1–4: 2.4e-7, 3.6e-7, 2.1e-7, 2.1e-7.
- `export_validation.json` sha `945f2010…`. The five ONNX files are byte-identical (`301219b4…`).

**Independent check against b-hive's own pipeline** (`~/bhive_test_20261112/indep_check_f0.py`, `indep_nn_f0.py`, output `indep_nn_f0.out`):
- The 214 constructed LZ4 test files hold **64,073 rows = the 64,073 parquet held-out rows**. Per-column sorted features are identical (max diff **0.0**), so b-hive applies no feature transform. ONNX on parquet vs ONNX on LZ4 rows differ by 0.0.
- `InferenceTask` `prediction.npy` holds **logits** (softmax is applied later). After softmax, every b-hive prediction has an ONNX event within **1.3e-3**, and every ONNX event has a b-hive prediction within 1.3e-3. Median nearest distance is 7e-5.
- Cause of the gap: `utils/adversarial_attacks/attacks.py` calls `torch.set_float32_matmul_precision("medium")` at import, so b-hive GPU training and inference use reduced-precision (TF32/bf16) matmuls. The ONNX/CPU export is exact float32 (3.6e-7 vs torch CPU). This is the same as the v11 recipe; it is recorded in provenance and left unchanged.

**Finding (needs a decision, not fixed): b-hive validation/inference rows are duplicated.**
- `InferenceTask` wrote **170,465** prediction rows for **64,073** events; 53,874 distinct rows appear more than once.
- Truth counts are inflated about 2.4–2.7× per class (hplusc 2,780 vs 1,084; vjets 68 vs 28).
- Mechanism (`utils/torch/LZ4Dataset.py.__iter__`): in `test` mode (used for **validation** and inference), the leftover partial batch is yielded but `leftover_data` is not cleared, so those rows are prepended to the next file and emitted again.
- Training batches are unaffected (leftovers are carried over, not yielded). The **validation loss that selects `best_model.pt`** is computed on this duplicated, non-uniformly weighted sample. v11 had the same behaviour.
- One-line fix if wanted: `leftover_data = None` after the test-mode `yield`. This is outside my files and would change best-epoch selection relative to v11, so it is **Chirayu's decision** before production.

**Diagnostic registration** (container `coffea-base-almalinux9:0.7.30-py3.10`, binds `-B /afs -B /cvmfs -B /eos -B /tmp -B /run/user`):
- Without `--diagnostic_only` it was refused: `TRAIN split differs from current workflow features/selection`, and no output was created.
- With `--diagnostic_only` → `/eos/user/c/cgupta/HToWW/b-hive/output/test_20261112_model_f0diag/meta.yaml` (`d2e72584…`).
- Recorded fields: `diagnostic_only: true`, `split_features_hash 3b912cbb…`, `split_selection_hash caa0f7a2…`, `split_matches_workflow: false`, `git_commit 0995853`, `git_dirty: true`, eras `[2022postEE]`.
- The registry refuses this manifest without `--allow_diagnostic_model`, and `runner.py`, `submit.py` and `submit_condor.py` refuse that flag with `--submit`.

**One-file RUN smoke** (local, never submitted). Script `~/bhive_test_20261112/run_smoke/run.sh`, log `run.log`.
- Command: `submit.py --workflow hww_allfix_4fs --year 2022postEE --dataset HplusCharm_4FS_HToWWTo2L2Nu --mode run --folds 5 --slim_ntuple --model_manifest …/test_20261112_model_f0diag/meta.yaml --allow_diagnostic_model`
- Input: one FNAL NanoAOD file (`…/2520000/31b34d9b-fb15-46e2-8855-a6aae15278a8.root`), with the existing proxy (not renewed).
- Ran 13:24:42–13:26:55 on lxplus932, **rc 0**.
- Result: 15,154 input entries = processed entries; 90 selected events. 53 template variations: nominal + 38 weight + 14 object shifts.
- Output: `run_smoke/out/HplusCharm_4FS_HToWWTo2L2Nu.coffea` `aaeb64ac…`.

**Independent scored-template comparison** (`run_smoke/indep_templates.py`, output `indep_templates.out`):
- Method: the templates are rebuilt from the slim ntuples with independent code:
  - folds assigned as `event % 5`;
  - its own onnxruntime sessions on the frozen `fold_*.onnx`;
  - feature order taken from the frozen `bhive_config.yml`;
  - argmax / max-score discriminant histogrammed with numpy.
- Result: **318 comparisons** (all channels × all 53 variations), max relative difference **1.4e-15**, 0 failures.
- Limit: the SR Nc-j sub-split variable is not in the slim ntuple, so `SR_hplusc_1cj+2cj` was compared only as a sum.

## 3. Reproducible training (implemented + tested)

**b-hive** (uncommitted, like its other local diffs; `tasks/training.py` `30491b5b…`, `tasks/parameter_mixins.py` `2b541721…`, new `tests/test_htoww_reproducibility.py` `b4bc0483…`):
- New `training_seed` (default 20261112) next to `split_seed` in `TrainingDependency`. Both pass from InferenceTask to TrainingTask. Neither is in the output path.
- `seed_training()` runs before the first model is built. It seeds:
  - python `random`;
  - the global numpy RNG (per-epoch `shuffleFileList`);
  - torch CPU and all CUDA generators (init, dropout).

  It also sets `cudnn.deterministic`, `benchmark=False`, `torch.use_deterministic_algorithms(True, warn_only=True)` and `CUBLAS_WORKSPACE_CONFIG=:4096:8`, if not preset.
- Both DataLoaders get dedicated `torch.Generator().manual_seed(seed+1 / +2)`. torch then seeds each worker's random/torch/numpy state, which makes LZ4Dataset's per-file `np.random.permutation` reproducible.
- `training_provenance.json` is written at start (`status: started`) and at the end (`completed`, sha256 of every output). It records:
  - both seeds, the seeding/determinism flags and whether CUDA was already initialised;
  - python/torch/numpy/CUDA/cuDNN versions, device, GPU name and capability, `float32_matmul_precision`;
  - b-hive git commit + diff sha;
  - sha256 of `config/<config>.yml` and `config/default.yml`, of the input `processed_files.txt`, and of the train/val lists;
  - all task parameters; a resume flag.
- **Cache guard:** `TrainingTask.complete()` and `run()` refuse a run directory whose provenance differs in `split_seed`, `training_seed`, config sha, default-config sha or input file-list sha. This also applies when InferenceTask checks its requirement. Legacy directories without a record keep the old behaviour.
- Class-only weighting (`--loss-weighting`, `reweighting_mode: class`), architecture, features and the train/val split recipe are unchanged.

**Tests run:**
- b-hive unit tests (`python -m unittest tests.test_htoww_reproducibility`, `b_hive` env after `source setup.sh`): **4/4 OK**.
  - provenance missing / match / mismatch on each key;
  - same-seed DataLoader batches with 2 workers over 2 epochs identical, other seed differs;
  - same-seed model init identical, other seed differs;
  - seeding record.
- **End-to-end CPU, real `law run TrainingTask`** on the existing fold-0 constructed dataset (read-only), new versions `c1repro_cpu_{a,b}`, 1 epoch, lxplus932:
  - Both rc 0 (122 s, 76 s). **Bitwise-identical weights**; `best_model.pt` sha identical (`012b4c69…`); same val loss 0.0045237705.
  - Provenance `completed`, `float32_matmul_precision medium`.
  - Logs: `~/bhive_test_20261112/c1repro/cpu_{a,b}.log`.
- **Refusal:** rerunning `c1repro_cpu_a` with `--training-seed 99` exited **rc 50** with `refusing: … different training_seed (stored 20261112, requested 99)`. No training started; model and provenance hashes were unchanged (log `cpu_a_seed99.log`).
- **GPU same-seed check: submitted, pending.** Cluster **9704454** (`~/bhive_test_20261112/c1repro/gpu_job.{sh,sub}`, 1 GPU, `microcentury`, no output transfer).
  - It trains `c1repro_gpu_{a,b}_e2` (2 epochs, same seed, same GPU), then writes `gpu_cmp.out` and counts deterministic-algorithm warnings.
  - It was idle at 13:52 CET. The result is not established here.

**Determinism limits (recorded, not claimed away):**
- Same seeds give identical results only with the same inputs, config, `n_threads`, software stack and GPU type.
- Reduced-precision ("medium") matmuls and kernel choices differ between GPU models and MIG slices, so seeds alone do not reproduce bitwise across hardware.
- `warn_only` allows any op without a deterministic kernel; the GPU job counts such warnings.
- A **resumed** training does not restore RNG states.
- InferenceTask row order is still randomly permuted (not used for ONNX/RUN scoring).

## 4. Validated commands, guards and registry (tested)

**Analysis repo:** committed locally as **`0bd528c`** on `hww-analysis` (my 4 files only, not pushed; tracked tree now clean). Final shas: `bhive_fold_commands.py` `8918c33f…`, `register_folds.py` `0e624cb7…`, `export_fold_onnx.py` `bb85a2cb…`, `tests/test_mva_bhive.py` `57d0d974…`.

What changed:
- `bhive_fold_commands.py`:
  - `--training_seed` (default 20261112), passed with `--split-seed` to TrainingTask and InferenceTask only;
  - the script refuses to start unless `$DATA_PATH` and `$B_HIVE_DIR` equal `/eos/user/c/cgupta/HToWW/b-hive{/output,}`;
  - new `guard_run` refuses existing `TrainingTask`/`InferenceTask` directories, in addition to the dataset guard;
  - seeds and paths are recorded in `bhive_runs.json`.
- `export_fold_onnx.py`: refuses a `B_HIVE_DIR` other than `--bhive_path`. It records per fold the config/default-config sha and the training-provenance summary.
- `register_folds.py`:
  - **always**: a recorded per-fold `onnx_sha256` must equal the frozen file;
  - **production additionally**: full export record, the same split filelist sha, config sha = `--bhive_config`, a **completed** provenance whose `best_model` sha = the exported checkpoint, and identical seeds/default config across folds.
  - This does not bypass the full-coverage or hash gates; the diagnostic path is unchanged.

**Tests run:**
- Container: `python3 -m unittest tests.test_mva_bhive tests.test_trainrun_blockers` → **29 tests OK, 1 skipped** (the torch+onnx test, run below).
- `b_hive` env: `TestOnnxExport` + `TestExportRecordChecks` → **6/6 OK**.
- The new tests execute the generated script with a stub `law`:
  - 20 calls in the right environment;
  - wrong `DATA_PATH`/`B_HIVE_DIR` refused before any call;
  - existing Training/Inference directory refused at model 2 after 8 calls;
  - each production-record defect refused.
- **Real law parse:** `bhive_fold_commands.py` with the new code on the v1 subset split → `output/test_20261112_cmds_v1sub_c1parse/run_folds.sh` (`bash -n` OK, 10 `--training-seed` flags).
  - All 20 commands run with `--print-status 0` in `b_hive` → rc 0, 20 statuses, no error.
  - TrainingTask and InferenceTask show `split_seed=20261112, training_seed=20261112, loss_weighting=True` (TrainingTask), unique `test_c1parse_05d7e0f8_f<i>` paths, and no directories created.
  - Exporting the old `DATA_PATH` (EPR_task) was refused.
- The model config class/feature order is checked by `register_folds.check_bhive_config` (tested). The real `HPlusCHToWW_2dcats.yml` passed in the diagnostic registration (`bhive_config_sha256 2024ecc5…`).

Residual hazard (documented, not changed):
- InferenceTask cannot pass `--loss-weighting`/`--train-val-split`, so its TrainingTask requirement carries the defaults.
- This is harmless only because the script runs TrainingTask first under `set -e`. Never run InferenceTask for a fold whose TrainingTask is incomplete.

## 5. Production launch plan (prepared, **not launched**)

Run each workflow separately: **A = `hww_allfix_4fs`**, **B = `hww_routeb_3fs4fs`**. Eras: `2022preEE 2022postEE 2023preBPix 2023postBPix`. TRAIN roots: `/eos/user/c/cgupta/higgscharm/outputs/<W>__train/`. `<P>` = `A`/`B`, `<D>` = launch date.

1. Container, repo root at the committed HEAD (≥ `0bd528c`, no tracked changes):
   ```bash
   python3 scripts/check_train_outputs.py --coffea <ROOT>/<W>__train/*/*/*.coffea --parquets '<parquet glob of the same TRAIN>'
   python3 scripts/mva/split_folds.py -w <W> --inputs '<parquet glob>' --coffea <ROOT>/<W>__train/*/*/*.coffea \
     --output /eos/user/c/cgupta/HToWW/b-hive/output/prod_<D>_<P>_split --folds 5 [--exclusions <yaml>]
   python3 scripts/mva/bhive_fold_commands.py --split /eos/user/c/cgupta/HToWW/b-hive/output/prod_<D>_<P>_split \
     --output /eos/user/c/cgupta/HToWW/b-hive/output/prod_<D>_<P>_cmds --prefix hww<P>v2
   ```
   Defaults: epochs 30, batch 1024, lr 1e-3, train/val 0.85, 4 coffea workers, chunk 300, both seeds 20261112, DATA_PATH/B_HIVE_DIR checks. The parent's census must confirm the parquet glob.
2. One Condor GPU job **per fold** (5 for A, 5 for B), from a new directory `~/bhive_prod_<D>_<P>/`. Job script `fold_job.sh <CMDS> <i>`:
   ```bash
   #!/bin/bash
   C=$1; i=$2; S=${_CONDOR_SCRATCH_DIR:-$PWD}
   awk -v i="$i" 'BEGIN{h=1} /^# ---- model /{h=0; b=($0 ~ "^# ---- model " i ":")} h||b' $C/run_folds.sh > $S/fold$i.sh
   cd /eos/user/c/cgupta/HToWW/b-hive
   source /afs/cern.ch/user/c/cgupta/.bashrc >/dev/null 2>&1; micromamba activate b_hive
   source setup.sh; export DATA_PATH=/eos/user/c/cgupta/HToWW/b-hive/output
   echo "host $(hostname) fold $i start $(date -Is)"; nvidia-smi -L
   bash $S/fold$i.sh; rc=$?; echo "fold $i rc=$rc end $(date -Is)"; exit $rc
   ```
   Submit file:
   - `executable = fold_job.sh`, `arguments = <CMDS> $(fold)`, `queue fold in (0 1 2 3 4)`;
   - `getenv = True`, `request_GPUs = 1`, `request_CPUs = 4`, `request_memory = 24000`;
   - `requirements = (TARGET.OpSysAndVer =?= "AlmaLinux9")`, `+JobFlavour = "tomorrow"`;
   - output/error/log per fold; **no `transfer_output_files`** (avoids the 9701591 hold).

   Optional: pin a GPU model in `requirements` so that a later same-seed reproduction can use the same hardware.
3. Export (`b_hive` env), with checkpoints `$DATA_PATH/TrainingTask/HPlusCHToWW_2dcats/<dataset_version>/<training_version>/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` from `bhive_runs.json`:
   `B_HIVE_DIR=/eos/user/c/cgupta/HToWW/b-hive python scripts/mva/export_fold_onnx.py --bhive_path /eos/user/c/cgupta/HToWW/b-hive --checkpoints <f0…f4> --split <SPLIT> --output /eos/user/c/cgupta/HToWW/b-hive/output/prod_<D>_<P>_onnx`
4. Register (container, no `--allow_dirty`):
   `python3 scripts/mva/register_folds.py -w <W> --split_manifest <SPLIT>/split_manifest.json --models <ONNX>/fold_{0..4}.onnx --eras 2022preEE 2022postEE 2023preBPix 2023postBPix --validation <ONNX>/export_validation.json --bhive_config /eos/user/c/cgupta/HToWW/b-hive/config/HPlusCHToWW_2dcats.yml --bhive_runs <CMDS>/bhive_runs.json --output <MODEL>`
   - Proposed `<MODEL>` = `/eos/user/c/cgupta/higgscharm/outputs/hww_mva_models/<W>__bhive5fold_<D>`. No models directory exists yet; the parent or Chirayu chooses.
   - RUN then scores **every** event with its held-out fold model (`event % 5`), which is the current 5-fold scoring.

**Resource estimate per fold job.** Rates come from the fold-0 test (854 constructed files / 256k rows: construction 194 s, 2 epochs 110 s) and v11 (3.26M rows, 30 epochs = 375 s train + 134 s val on H100):

| step | 4M-row train list (a guess; real row counts come only from the split) |
|---|---|
| train construction | ≈ 50 min (≈1.3k rows/s) |
| test construction | ≈ 13 min |
| 30 epochs + validation | ≈ 10–20 min |
| inference | a few minutes |
| **total** | **≈ 1.5 h**, budget 3× → `tomorrow` flavour |

- EOS use: about 136 B/row × 5 datasets per event, i.e. about 4 GB per workflow for 6M rows.
- A and B are independent (10 GPU jobs); queue wait dominates, the test GPU job idled over 12 min.

## Gates: READY / BLOCKED

Pipeline code is ready for production **except the gates below**. No production launch was made.
1. **BLOCKED, parent/other agent:** complete, validated TRAIN v2 coverage for A and B in all 4 eras (`check_train_outputs` pass), with parquet `features_hash`/`selection_hash` equal to the current values above (A `36f655f4…/80e75bca…`, B `36f655f4…/24b63ba3…`).
2. **Pending:** GPU same-seed result of cluster 9704454. Read `~/bhive_test_20261112/c1repro/gpu_cmp.out` and `gpu_job.9704454.out` once it has run.
   - If the weights are not bitwise identical, production can still proceed. In that case, record that GPU reproduction holds only to the measured tolerance.
3. **Needs Chirayu (decision, not an authorization repeat):** keep or fix the LZ4Dataset validation/inference duplication before production. Fixing it changes best-epoch selection relative to v11.
4. **Needs parent/Chirayu:** model registry location under `/eos/user/c/cgupta/higgscharm` (proposal above).
5. **Optional:** commit the b-hive HToWW copy's `tasks/training.py`, `tasks/parameter_mixins.py` and the new test. Provenance records the diff sha either way.
6. **Not checked by me:** physics gates (Higgs 125.09 GeV normalization alignment, cards). Do not infer them from this note.

Keep (never delete): `test_20261112_*` datasets, models, ONNX and manifests; `c1repro_*` training versions; `~/bhive_test_20261112/`. `test_20261112_model_f0diag` is **diagnostic only**.
