---
tags: [reference, review]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# TRAIN/RUN blocker fixes and single-owner b-hive validation (2026-11-05/06)

**Status: agent-reported.** The code was implemented and tested by this worker, but Chirayu or an independent reviewer has not validated it. No Condor/CRAB job, real training, production or Combine run was made. Nothing was pushed, merged or deleted. The analysis changes stay **uncommitted** in the lxplus working tree for the edit owner and reviewer. Only this note and its evidence folder are committed, locally.

**Authorisation (Chirayu, 2026-11-05, verbatim):** "Launch opus to do this fix and also work towards fixing the blocker" and "Delegate to a new agent not a subagent". Later in the same session: "After you are done update the keeper and ask it to update the slides", "And ask the keeper to make more detailed slides on this btw once you done", "Yes detailed and more human readable slides". Resumed 2026-11-06 on Chirayu's instruction via the conductor, after a laptop battery interruption.

Starting evidence: [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun|the TRAIN/RUN review]] (F1–F18) and [[Projects/HToWW/2026-11-05-status-audit-retraining|the status audit]]. That review stays unchanged as the historical record. One of its statements is corrected in §1.3.

## 0. Manifest and interruption record

- **Repo:** `lxplus:/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `40d0e3e` (unchanged).
- **State before any edit:** `git diff | sha256sum` = `bb8a69307c512c3f…`, identical to the review's. No file was newer than the review. The hashes of all 13 relevant pre-existing files matched the review's table.
- **State after:** `git diff | sha256sum` = `310d5e5750a3f916…`. The full-tree diff still includes the earlier workers' dirty changes; I did not commit or reset them. The `*.pre_sol_review` backups (13) and the fileset `.bak` files (4) are intact (re-checked 2026-11-06).
- **Only my changes:** [worker_changes_only.patch](review/evidence/trainrun-blockerfix-20261106/worker_changes_only.patch) (sha256 `6003421fe9b89ba5…`, 19 files, +1025/−90, file list in its README). Its base was reconstructed by reversing my exact edits; all 13 reconstructed pre-edit files reproduce the review's recorded pre-edit SHA256 prefixes, and the 4 that were clean come from `git show HEAD`. Per-file SHA256 and mtimes of the edited files: [SHA256SUMS_after.txt](review/evidence/trainrun-blockerfix-20261106/SHA256SUMS_after.txt). All edits fall between 2026-11-05 14:37 and 14:46, and nothing in the repo is newer.
- **Interruption (2026-11-05 ~14:50).** The laptop battery died while I was surveying data files for F14, a read-only step. On resuming, I found no half-written file, no file newer than my last edit, and no partial vault note. The 2026-11-05 snapshot tarball and logs were in node-local `/tmp` on lxplus938. That node now refuses host-key verification, and I did not modify `known_hosts`. I therefore regenerated all evidence on 2026-11-06 on lxplus977 and saved it in the vault folder below. The 2026-11-05 runs gave the same results; that statement rests on session output, not on a surviving log.
- **Environment:** `apptainer exec -B /afs -B /cvmfs -B /eos -B /tmp -B /run/user --env PYTHONDONTWRITEBYTECODE=1 /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-base-almalinux9:0.7.30-py3.10`. Commands were run from the repo root.

## 1. Validation split: before, after and why

### 1.1 Before (integration defect, confirmed by source)

- `scripts/mva/split_folds.py` wrote three lists per model *i*:
  - `test` = fold *i*;
  - `valid` = fold (*i*+1)%5;
  - `train` = the other three folds (60%).
- b-hive `train_v11_2dcats.sh` passes only `TRAIN_FILELIST` to `DatasetConstructorTask`/`TrainingTask`. It never reads `valid.txt`.
- `TrainingTask` (`tasks/training.py`, `train_val_split` default 0.85) shuffles the *constructed* LZ4 files and holds out the last 15% for validation.

So the advertised 60/20/20 split did not happen. The reserved fold went unused, and b-hive split the 60% again, giving about 51/9 with 20% thrown away.

### 1.2 After (one validation owner)

| per model *i* (k = 5) | events | used by |
|---|---|---|
| `model_i/train.txt` | the 4 folds ≠ *i* (80%) | b-hive `DatasetConstructorTask` → `TrainingTask`; b-hive alone splits these into train and validation (default 0.85/0.15) |
| `model_i/test.txt` | fold *i* only (20%) | a separate b-hive test dataset for `InferenceTask`/ROC; RUN scores fold *i* with model *i* only |

- **Approximate fractions:** about 68/12/20. The 68/12 part is a fraction of constructed files inside the 80%; it is not an exact event count.
- **What changed in `split_folds.py`:**
  - no `valid.txt` is written;
  - the manifest has `schema_version: 2` and a `validation` block (owner, mechanism, default 0.85, approximate fractions and what they are fractions of);
  - per model it records `test_fold`, `train_folds`, row counts and the SHA256 of each list.
- **What changed in `register_folds.py`:** it refuses schema-1 manifests and requires every model to hold out exactly its fold.

### 1.3 Contamination review (train/test and preprocessing)

**Fixed transformations, fine to apply to every fold:**
- the event%k fold assignment;
- the nonfinite→0 policy;
- the c-tag one-hot edges;
- the `weight` normalisation lumi·xsec/Σsumw. This is a per-sample constant from generator weights; it is not fitted on labels or features.

**Fitted outside this training, a separate risk:** the negrw g(x). It is fitted elsewhere, and its overlap with the new SR is the audit's open item N1, unchanged here.

**Fitted inside b-hive:**
- **Class-abundance weights** (`reweighting_mode: class`). These come from unweighted counts over the whole `train.txt`, so they include b-hive's internal validation share but **never the test fold**. They contain no feature information. The only consequence is a mild coupling into validation loss and best-epoch selection. I judged this acceptable and changed nothing.
- **BatchNorm:** learned on training batches only.
- **Feature standardisation:** none.

**Contamination hazards found and closed in the handoff, with no b-hive edit:**
1. **Dataset caching.** b-hive stores a constructed dataset at `$DATA_PATH/DatasetConstructorTask/<config>/<dataset_version>`. `filelist` is `significant=False`, so it is not in that path. Reusing a version across folds would make law treat fold 0's dataset as complete for fold 1. Model 1 would then be trained on events from its own test fold.
2. **Hard-coded test dataset.** The stock driver hard-codes `TEST_DATASET_VERSION`, so every fold after the first would evaluate on the first fold's test set.

`scripts/mva/bhive_fold_commands.py` (new) writes, but never runs, a `run_folds.sh`:
- a unique `dataset_version`, `test_dataset_version` and `training_version` per fold and per split hash;
- a guard that refuses to start if a target dataset directory already exists;
- a check that the list hashes still match the manifest;
- explicit `--train-val-split 0.85`.

It also writes `bhive_runs.json` for `register_folds --bhive_runs`. I verified the parameter names against b-hive source: the `DatasetDependency`, `TestDatasetDependency` and `TrainingDependency` mixins and `TrainingTask.train_val_split`. `InferenceTask` takes neither `train_val_split` nor `loss_weighting`. **A `law ... --help` parse was not run:** I found no b-hive conda environment on lxplus. Evidence: [bhive_handoff_check.txt](review/evidence/trainrun-blockerfix-20261106/bhive_handoff_check.txt).

**Correction to the review (§3, "weight").** b-hive `HPlusCHToWW_2dcats` reads **no event-weight column**:
- `LZ4TTCCProcessor` reads only `global_features` and `truths`;
- `merge_datasets` writes `weight = class_weight[truth]`.

So neither v11's `weight_nominal` nor TRAIN's normalised `weight` affects training. Every MC event, including negative-weight NLO events, enters with weight 1 times its class weight. This is pre-existing (v11 is the same) and is recorded in the manifest (`consumed_by_bhive_2dcats: false`). Whether training should use physics weights is a physics decision (§5).

**Not changed in b-hive, but noted:** `TrainingTask.run` calls `np.random.shuffle(files)` without seeding; only `DatasetConstructorTask` seeds. The internal train/validation file split, and so the best-epoch choice, is not reproducible. Seeding it is a one-line b-hive change. It is deferred because the brief asked to avoid b-hive changes unless needed for correctness.

## 2. Findings F1–F18: disposition

| # | disposition | change (file) | test / check |
|---|---|---|---|
| F1 | **fixed** | `processing_checks.sample_kind`: MC iff `era ∈ {mc, signal}`; data iff `process == 'Data'`; anything else raises. The card builder skips data, which gets Asimov `data_obs` in cards, and logs it in `template_policy.json` | era census of all 4 eras: data = run letters, MC = `mc` (`test_every_era_entry_is_mc_or_data`); chain repro |
| F3 | **fixed** | `split_folds.normalization` (the `__main__` path) skips data before reading `xsec`; data shards are label −1 and stay out of all lists | `test_normalization_skips_real_data_eras…` with a real era-E data sample |
| F2 | **fixed (recorded decision applied)** | `hww_allfix_4fs.yaml`: `WG` added to `mva.labels.process_groups.diboson` and `combine.process_map.diboson`, citing Chirayu 2026-10-02 | every MC process in every era maps to exactly one card class, identical to its label (`test_all_workflow_mc_processes_map…`); WG yield lands in `CR_diboson`/diboson |
| F4 | **fixed** | `submit_condor.py` creates `outputs/<wf>__<mode>/<year>/<ds>` via `make_output_directory(args, workflow_name=job_workflow)`, replacing the string rewrite; `submit.py` also runs `mkdir -p` before `save` | real `submit_condor.py` run in a scratch cwd with a stub proxy, then real `condor/submit.sh` with a stub `submit.py` that saves: the `.coffea` lands in the created mode directory (`test_prepared_job_saves_into_created_mode_directory`) |
| F5 | **fixed (policy parity)** | `build_cards_from_templates.finalize_templates` applies the approved legacy final-template policy in the legacy `main()` order. Signed per-chunk records stay signed; only final summed templates are floored. Details below | parity test vs the legacy sequence, with and without smoothing: bit-identical arrays; review R2's −4.0 SR vjets bin → 1e-6 |
| F6 | **fixed** | `check_dataset_coverage`: every MC sample the workflow runs over must be present, unless excluded with a reason in a YAML (stale exclusions and extra samples are errors). Every fileset-JSON file of each sample must appear in the outputs' `execution_checks.files`, compared by `/store/` path. `merge_outputs` refuses inputs without that record. Used by both the card builder and `split_folds` | unit tests + chain repro: missing WG sample → error; with exclusion → OK; one unprocessed file → error |
| F7 | **fixed** | `base.py` stores `chunks` per template record; the builder requires each weight variation (including negrw ±) to cover exactly the nominal's chunks | `test_partial_weight_variation_raises` |
| F8 | **fixed** | `register_folds --bhive_config` (required): `global_features == FEATURES`, `truths == is_<classes>`; config SHA256 stored and the config copied into the frozen model; ONNX input dim 26 and output dim 6 checked; label order == `combine.classes` checked in `register_folds`, `split_folds` and RUN `validate` | real b-hive config passes; reordered truths/features fail; ONNX fixtures (26→6) pass, a wrong class count fails |
| F9 | **fixed** | `FoldModels(year=…)` refuses an era not in `training_data.eras`; RUN `validate` requires the year; all callers pass `args.year` | `test_run_refuses_untrained_era` |
| F10 | **fixed (configurable; no root chosen)** | `--output_root` / `--output_root_url` on `runner.py` → `submit_condor.py` → `arguments.json` → `submit.sh` → `submit.py --output_location`. `.coffea` goes to `<root>/outputs/<wf>[__mode]/…`; parquet goes to the same root (`/eos/user/*` via eosuser xrootd; other `/eos` roots need an explicit URL; relative roots are rejected). Unset = unchanged default | Condor-prep test with a scratch root; `test_output_root_rules` |
| F11 | **fixed** | `jobs_status.py --mode/--output_root` monitors `condor/<wf>__<mode>`, resubmits `<wf>__<mode>_<ds>.sub`, and requires each prepared `arguments.json` to have the same mode and `output_path`. `--reset` is refused for TRAIN/RUN (it would rerun without mode/model options) | `test_prepared_job_mode_and_output_must_match` |
| F12 | **fixed** | `eos_io.read_parquet` also retries `/eos` paths from the server on `pyarrow.ArrowInvalid` (zero-byte or truncated FUSE view); non-EOS paths still raise | `test_truncated_eos_file_retries_from_server` |
| F13 | **fixed** | `submit.sh` writes the mode/output options to a file through a checked heredoc; the old process substitution hid failures and fell back to legacy mode | real `submit.sh` with a non-string manifest fails before `submit.py` runs |
| F15 | **fixed** | `register_folds` records `git_dirty` and the `git diff HEAD` SHA256, and refuses a dirty tree unless `--allow_dirty` | source; not separately unit-tested |
| F14 | **deferred** | Inputs missing from `selection_signature`: the negrw model, JEC/JER, jet-veto, c-tag SF data, `lhe_yukawa`. A complete fix needs a decision on which artefacts define model validity (many live under `analysis/data/*` or `/cvmfs`). It must happen **before TRAIN**, because changing the hash later invalidates models | — |
| F16 | **deferred** | Cross-dataset duplicate-file UUID check. Fold assignment is by event number, so a duplicated event keeps the same fold and cannot leak across folds; the risk is a double-counted yield, not contamination | — |
| F17 | **kept, documented** | `runner.py` `check=True` stops the remaining dataset preparations after a failure, intentionally | — |
| F18 | **deferred** | TRAIN's reliance on `shift="train_nominal"` producing nominal weights; still holds by inspection; a `variations=False` flag would be a refactor of `weight_manager` | — |

**F5 policy detail.** Legacy reference: `make_combine_inputs.main`, which runs (a) the empty object-shift fallback, then (b) `clip_negative_bins` (floor 1e-6, coordinated with the systematics), then (c) `smooth_shape_variations` and a re-floor when `smooth_shapes` (Run A: false). RUN reuses the same functions in the same order. Two deliberate differences, so that missing systematics and real migrations are not masked blindly:
1. **Unevaluated object shift.** RUN now records which object shifts were evaluated on each chunk (`evaluated_shifts`, before any selection). A shift that was never evaluated for a sample raises an error unless it is declared not applicable. It then uses nominal and logs the use. Partial evaluation always raises.
2. **Evaluated shift with no surviving events.** A sample whose shift was evaluated on every chunk but kept no events contributes a genuine **zero**. Only at the final (channel, process) level does the legacy rule turn an empty shift with nominal > 0 into nominal. Every such application is listed in `template_policy.json`, and `combine.object_shift_empty_fallback: error` turns it into an error instead.

## 3. Evidence (all re-run 2026-11-06 on lxplus977; logs in the vault)

Folder: `Projects/HToWW/framework/review/evidence/trainrun-blockerfix-20261106/`.

| check | command | result | log |
|---|---|---|---|
| new + affected suites, after | `python3 -m unittest -v tests.test_trainrun_blockers tests.test_processing_modes tests.test_hzz_safety_ports` (container above) | **31/31 OK**, 13.8 s | [unittest_after.txt](review/evidence/trainrun-blockerfix-20261106/unittest_after.txt) |
| the same new tests on the reconstructed **pre-edit** tree | same, in `/tmp/cgupta_blockerfix_20261106/pre_tree` | 17/17 fail as expected. Behavioural failures: WG has no card mapping (F2); `valid.txt` still written (split defect). The rest are missing APIs | [unittest_before_pre_tree.txt](review/evidence/trainrun-blockerfix-20261106/unittest_before_pre_tree.txt) |
| synthetic end-to-end card build | [chain_repro.py](review/evidence/trainrun-blockerfix-20261106/chain_repro.py): 46 expected 2022postEE MC samples + 1 data sample, real fileset JSON, real ROOT/datacard writing | cards built; 1626 histograms; data skipped; negative SR vjets bin → 1e-6; JES row present; missing WG sample → error; with exclusion → OK; one unprocessed file → error | [chain_repro.txt](review/evidence/trainrun-blockerfix-20261106/chain_repro.txt) |
| b-hive handoff | synthetic 200-event split → `bhive_fold_commands.py` → `bash -n` | 160/40 rows per model; script syntax OK; unique versions | [bhive_handoff_check.txt](review/evidence/trainrun-blockerfix-20261106/bhive_handoff_check.txt) |
| `tests.test_allfix` | **not re-run**: it imports none of the changed modules | author/reviewer log, not re-executed: [unittest_reviewer.txt](review/evidence/trainrun-20261105/unittest_reviewer.txt) | — |

**Not run:**
- any real NanoAOD processing. The `base.py` additions (`chunks` per record, `evaluated_shifts`) are covered only by source inspection and by the downstream builder tests that consume them. A one-dataset RUN smoke needs a VOMS proxy (a credential) and was outside the brief;
- `law` parameter parsing;
- Combine;
- real b-hive training or ONNX export.

## 4. Downstream impact

- **TRAIN/RUN only.** Legacy processing is unchanged, except:
  - `jobs_status.py --reset` is now refused for non-legacy modes;
  - legacy `make_combine_inputs.py` cards built from this workflow will now **include WG in diboson**, because `process_map` is shared. This follows the retraining decision. If legacy v11 cards must stay WG-free for comparison, use a copy of the workflow for them.
- **No hash change.** `selection_signature`/`signature` inputs are unchanged, so nothing here invalidates a future TRAIN. The `mva` and `combine` blocks are not hashed.
- **Not covered by the new guards.** RUN outputs from before this fix lack `evaluated_shifts`, record `chunks` and `execution_checks.files`, and are refused. No such production exists (the `hww_allfix_4fs__*` directories were absent on EOS per the review).

## 5. Remaining physics / input decisions (for Chirayu)

1. **Output root for F10.** It is configurable but no location was chosen or created. The placeholder is `--output_root <ABSOLUTE_ROOT>` (+ `--output_root_url` if not under `/eos/user`). Unset = current `/eos/user/c/cgupta/higgscharm` default (≈81 GB free per the audit).
2. **Event weights in training.** b-hive 2dcats ignores generator/normalisation weights, as v11 did. Keep this, or pass `weight` (needs a b-hive change)?
3. **Empty-shift fallback.** Keep the legacy fallback to nominal (logged), or set `object_shift_empty_fallback: error` and review each case?
4. **F14 scope.** Which artefacts (negrw model, JEC/JER, jet-veto, c-tag SF, lhe_yukawa) join the model-validity hash? Decide before TRAIN.
5. **b-hive seeding** of the internal validation split (one line; reproducibility, not correctness).
6. The audit's other pre-TRAIN items (PDF/αS, SF factorisation, RNG, c-tag edges, N1) are unchanged by this work.

## 6. Reproducible next steps (each needs Chirayu's approval; nothing here was run)

1. Edit owner/reviewer: review [the patch](review/evidence/trainrun-blockerfix-20261106/worker_changes_only.patch), then commit explicit paths, not `*.pre_sol_review`.
2. Smoke-test one dataset per mode through Condor (needs a proxy and approval):
   `python3 submit_condor.py -w hww_allfix_4fs -y 2022postEE -d <DS> --mode train --output_root <ROOT> --submit`
   then
   `python3 jobs_status.py -w hww_allfix_4fs -y 2022postEE --mode train --output_root <ROOT>`.
3. Full TRAIN, then:
   `python3 scripts/check_train_outputs.py --coffea … --parquets …`
   `python3 scripts/mva/split_folds.py -w hww_allfix_4fs --coffea <ROOT>/outputs/hww_allfix_4fs__train/*/*/*.coffea --inputs '<parquet glob>' --output <SPLIT> [--exclusions excl.yaml]`
4. `python3 scripts/mva/bhive_fold_commands.py --split <SPLIT> --output <CMDS>`, then in b-hive (`source setup.sh`): `bash <CMDS>/run_folds.sh`. **This is model training.**
5. Export each fold's `best_model.pt` to ONNX and record the torch/ONNX difference per fold, then:
   `python3 scripts/mva/register_folds.py -w hww_allfix_4fs --split_manifest <SPLIT>/split_manifest.json --models fold_{0..4}.onnx --eras … --validation export.json --bhive_config <b-hive>/config/HPlusCHToWW_2dcats.yml --bhive_runs <CMDS>/bhive_runs.json --output <MODEL>`
6. RUN with `--model_manifest <MODEL>/meta.yaml --output_root <ROOT>`, then:
   `python3 scripts/combine/build_cards_from_templates.py -w hww_allfix_4fs -y <era> --inputs … --output <CARDS> [--exclusions …] [--not_applicable …]`. Review `template_policy.json`.
