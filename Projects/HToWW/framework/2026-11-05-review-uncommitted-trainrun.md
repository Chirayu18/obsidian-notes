---
tags: [reference, review]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# Review of the uncommitted higgscharm TRAIN/RUN code, Sol fixes and HZZ ports (2026-11-05)

**Status: agent-reported, read-only review.** No analysis file was edited. No job was submitted, nothing was pushed and nothing on EOS was deleted. This is Brief 2 of `Meta/keeper/2026-11-05-pending-worker-briefs.md`, run by the explicitly authorised Claude subagent fallback under the [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|HToWW review protocol]]. A separate agent is auditing status and open items. Chirayu also asked: "Also train and run modes differ in the branches also no". That question is answered in §3.

**Verdict.** Legacy mode behaves as before, apart from the intended changes. The fold, leakage and normalisation core is sound. But the TRAIN → model → RUN → card chain **cannot run end-to-end under Condor today**. The source shows four demonstrated blockers, and each was reproduced where feasible (F1–F4). A fifth difference would make RUN cards differ from legacy cards: negative bins are not floored (F5). None of these defects corrupts a result silently. Each one either raises an error or loses an output. The quieter risks are F6 and F7, which are medium severity.

## 1. Review manifest

- **Repo:** `ssh lxplus` (lxplus938), `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`.
- **Git branch:** `hww-analysis`, HEAD `40d0e3e`, 5 commits ahead of `chirayu/hww-analysis` and unpushed. **No separate Git branch holds TRAIN/RUN.** It exists only as uncommitted working-tree changes on `hww-analysis`: 11 modified files, +248/−20 lines, plus untracked modules.
- **Inspected:** 13:53–14:05 CET. `git diff | sha256sum` = `bb8a69307c512c3f…`. No reviewed file has an mtime after 09:03:39. The re-check at 14:05 found nothing newer than 09:04, so the Sol worker did not edit during the review. `analysis/processors/.base.py.swp` is empty and dates from 2026-08-17, so it is stale.
- **Out of scope (ignored):** `*.pre_sol_review` and `*.bak*` backups, `outputs/`, loose plotting scripts. Note `scripts/mva/split_folds.py.pre_sol_review` and `tests/test_processing_modes.py.pre_sol_review`: the change log at `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/sol_trainrun_20261105/initial_changes.json` records `features/hww.py`, `sinks/hww.py` and `base.py` hashes that differ from the live files. `phase2_files.json` lists the later edits. The live versions below are what I reviewed.
- **Workflow:** `analysis/workflows/hww_allfix_4fs.yaml` (mtime 07:42). Era datasets selected by the workflow: 54 / 55 / 66 / 56 (preEE / postEE / preBPix / postBPix), of which 46 MC in each era.
- **Container:** `/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-base-almalinux9:0.7.30-py3.10`, with binds `-B /afs -B /cvmfs -B /eos -B /tmp -B /run/user` and `PYTHONDONTWRITEBYTECODE=1`.

SHA256 (first 16 hex), mtime (2026-11-05) and line count of each reviewed file:

| file | sha256[:16] | mtime | lines |
|---|---|---|---|
| analysis/corrections/lhepdf.py | 5ee66ae76f5683f1 | 08:20:32 | 137 |
| analysis/postprocess/utils.py | a0ed848ab43d912e | 08:57:39 | 661 |
| analysis/processors/base.py | 7bb9f568b8c66c7a | 09:01:18 | 332 |
| analysis/selections/object_selections.py | a4ee858081d704f6 | 08:20:32 | 753 |
| analysis/utils/eos_io.py | ed5d3aa97323bd88 | 09:01:18 | 149 |
| condor/submit.sh | 49e657360c869f50 | 08:40:20 | 50 |
| runner.py | bd32d1068988e8d2 | 08:40:20 | 111 |
| scripts/combine/make_combine_inputs.py | a95cfd9ed3ea8304 | 08:57:39 | 640 |
| submit.py | 368cc2fa16597cb6 | 08:58:32 | 137 |
| submit_condor.py | 55f114328e53289d | 08:40:20 | 192 |
| tests/test_allfix.py | 887d73d7565c76e1 | 08:19:24 | 528 |
| analysis/processing_modes.py | 64762b74265e442a | 08:39:04 | 47 |
| analysis/processing_checks.py | 6847ab69688b33e2 | 08:58:32 | 64 |
| analysis/features/{__init__,hww}.py | 949d58770ac1ea2f / 822850fab4cbf56c | 08:38:03 / 09:03:38 | 1 / 85 |
| analysis/models/{__init__,registry}.py | d335945077c14467 / ba7fe6d0d776a43e | 08:38:03 | 1 / 73 |
| analysis/sinks/{__init__,hww}.py | 18c829e5edfe5dbc / 1c6368fae87233f5 | 08:39:04 / 09:01:18 | 1 / 67 |
| scripts/mva/split_folds.py | 2685335d7821dfeb | 08:58:32 | 122 |
| scripts/mva/register_folds.py | bd984fe3156baa82 | 08:58:32 | 62 |
| scripts/check_train_outputs.py | 72a093a2ad3931e4 | 09:03:39 | 18 |
| scripts/combine/build_cards_from_templates.py | 36b1bbfda37ad687 | 09:01:18 | 168 |
| tests/test_processing_modes.py | 2559f4a2356cf443 | 09:01:18 | 166 |
| tests/test_hzz_safety_ports.py | 846177263e2faa5d | 08:58:32 | 40 |
| tests/data/mode_models/fold_{0..4}.onnx | e2c8e9d2… 784a27b7… b45e3613… 93081d77… 9a585311… | 08:55:30 | — |

**Tests.** No saved log exists for the TRAIN/RUN suites. The evidence directory has only change lists, and the "49 pass" is reported in the implementing thread. The standing rule therefore allowed a run. I ran `python3 -m unittest tests.test_processing_modes tests.test_hzz_safety_ports tests.test_allfix` in the container above: **49/49 OK in 28.3 s** (reviewer-run). The log is node-local, at `lxplus938:/tmp/cgupta_review_trainrun/unittest_reviewer.log`. The suites contain no test of Condor preparation, of `split_folds.py`'s `__main__`, or of `build_cards_from_templates.main`/`make_process_hists` against a real era config. Every blocker below falls in those gaps.

**Reviewer reproducers.** These are bounded and use synthetic inputs plus the real workflow and era YAMLs, with no production data. Script: `lxplus938:/tmp/cgupta_review_trainrun/repro.py`. Output: `…/repro.log`. They were run from the repo directory in the container. They read the repo and wrote only to `/tmp`.

## 2. Findings

Severity is relative to producing correct cards from a TRAIN/RUN production. The **Type** column uses four states:
- **demonstrated:** reproduced or unambiguous from source plus a reproducer;
- **source:** found by source inspection only;
- **missing guard:** a requirement that is not enforced; no present bug;
- **decision:** physics or user input needed.

| # | Severity | Type | file:line | Finding and evidence | Suggested fix |
|---|---|---|---|---|---|
| F1 | **High (blocks RUN cards)** | demonstrated | `scripts/combine/build_cards_from_templates.py:80`, `:82–84` | Data is never skipped. The code tests `info['era'] == 'data'`, but data `era` values are run letters: `C`/`D` (preEE), `E`/`F`/`G` (postEE), `C123`/`C4` (preBPix), `D` (postBPix). Data also has `process: Data`, so the next line raises `process 'Data' has no unique card mapping`. RUN processes data in every era (`runner.py` loops over all workflow datasets), so building from a full era's `.coffea` set fails. Reproducer: `repro.log`, R8 and the era census. | Use the legacy rule from `make_combine_inputs.gather_samples`: skip unless `era in ('mc','signal')`. Add a test that uses a real era YAML. |
| F2 | **High (blocks RUN cards)** | demonstrated + decision | `build_cards_from_templates.py:82–84` | Five `WGtoLNuG_PTG*` samples (process `WG`) in every era are processed but are in neither `combine.process_map` nor `mva.labels.process_groups`. The builder raises on them. Legacy silently drops them (`gather_samples` ignores unmapped processes). Reproducer: R8 gives `['Data', 'WG']`. | Add an explicit `card_exclude` list in the workflow and log the excluded samples. **Chirayu:** is Wγ deliberately absent from the fit? It was already absent from legacy cards and from v11 training (label −1). |
| F3 | **High (blocks TRAIN split)** | demonstrated | `scripts/mva/split_folds.py:114–116` | Same `era == 'data'` bug. Data accumulators reach `float(info['xsec'])` with `xsec = 'None'` (a string), which raises `ValueError: could not convert string to float: 'None'` (R8 addendum). The documented command passes "all TRAIN .coffea". If you leave out data `.coffea`, `check_train_rows` (`:121`) then raises "Parquet without matching TRAIN job output" for any data shard the glob picks up. `test_split_filelists…` calls `split_files()` directly and bypasses `__main__`. | Skip non-MC as in F1, before computing the scale. Add a `__main__`-level test that includes a data accumulator. |
| F4 | **High (every Condor TRAIN/RUN job loses its .coffea)** | demonstrated | `submit_condor.py:161–163`; `submit.py` `save(...)` | `make_output_directory(args)` creates `…/outputs/hww_allfix_4fs/<year>/<dataset>`. The path is then rewritten to `…/hww_allfix_4fs__<mode>/…`, which is never created. `coffea.util.save` is `lz4.frame.open(filename,'wb')` with no mkdir (container `coffea/util.py:38–45`). So `save` raises `FileNotFoundError` after the job has done all its processing. Reproducer R4 gives `FileNotFoundError … hww_allfix_4fs__run/2022postEE/DS/DS_1.coffea`. TRAIN parquet shards are still written, because xrootd copies create directories. But the `.coffea` holds `sumw`, `chunks` and `selected_events`, which `check_train_rows`, `split_folds` and the card builder need, so TRAIN is unusable too. None of the `hww_allfix_4fs__*` directories exist on EOS yet. Local smoke tests used an explicit `--output_path` and did not exercise this path. | Pass the mode-suffixed workflow name into `make_output_directory`, or mkdir `output_path` in `submit.py` before `save`. Add a test of `submit_condor` argument and path preparation. |
| F5 | **High (RUN cards ≠ legacy cards)** | demonstrated (source + R2) | `build_cards_from_templates.py:99–128` vs `make_combine_inputs.py` `clip_negative_bins` and object-shift fallback (`main`, "fallback to nominal where a (channel, process) got no shift events") | The RUN builder omits two legacy post-processing steps: the unconditional floor on non-positive nominal bins (1e-6, with the systematics clipped together), and the legacy fallback to nominal when an object shift has zero events in a (channel, process). Negative-weight vjets bins therefore go to ROOT as negative (R2: SR last bin = −4.0), and an empty shifted channel becomes a −100% shape. Expect Combine failures ("Bogus norm") or a biased fit, and the cards are not comparable with legacy ones. `smooth_shapes: false` in Run A, so smoothing is not a difference today. | Import and apply `clip_negative_bins` (and `smooth_shape_variations` when enabled) plus the object-shift fallback from `make_combine_inputs`, in the same order. Add a RUN-vs-legacy card equivalence test on one slim-ntuple sample. |
| F6 | Medium | demonstrated | `build_cards_from_templates.py:78–88`, `:125–126` | Nothing checks that every workflow dataset is present. The builder iterates only over the samples in the supplied `.coffea` files. Missing jobs or samples silently drop yield. The only check is "Missing selected processes", which fires when a whole class is absent. R3: 6 of the 55 postEE datasets supplied → cards built with no error. Legacy is equally silent (`[skip]`). `execution_checks` (`submit.py`) is per job and is not required by the builder. | Require every `get_datasets_to_run_over(workflow, year)` sample, or an explicit exclusion. Require `execution_checks` in each input. |
| F7 | Medium | demonstrated mechanism; trigger untested | `analysis/sinks/hww.py:34–67` + `build_cards_from_templates.py:110–121` | If a weight variation exists in only some chunks of a sample, its accumulated template covers only those chunks, and the builder uses it as complete. R1: nominal = 4.0, pileupUp = 2.2 (expected 4.4); `norm_raw` is 4.0 vs 2.0. Legacy concatenation would put NaN there and then fall back to nominal per event. Possible triggers: `partonshower.py` try/except, or `LHEPdfWeight` length branches if inputs are heterogeneous within a sample. No real instance was found. | For `kind=={'weight'}` records, assert `Σnorm_raw` equals the nominal record's `Σnorm_raw`, or store a chunk set per variation and compare. |
| F8 | Medium | missing guard | `scripts/mva/register_folds.py:51–52`; `analysis/models/registry.py:17–22` | The manifest's `features` and `classes` are written from the current code (`FEATURES`, `cfg.combine['classes']`), not read from the trained model. The "class order" and "features" checks therefore compare the config with itself. ONNX input-column order and output-class order are never verified. The ONNX-vs-torch check passes under b-hive's own order. **Checked today:** b-hive `config/HPlusCHToWW_2dcats.yml` lists `global_features` in exactly `FEATURES` order (26 = 15 kinematic + 11 one-hot + nSV), and its `truths` order `is_hplusc, is_higgsbkg, is_tt, is_st, is_diboson, is_vjets` equals `combine.classes` and `mva.labels.process_groups` key order. So nothing is scrambled now. The plan (`2026-10-08…plan.md` §2.2) required the b-hive config in `meta.yaml`; it is not there. | `register_folds`: read the b-hive config used and require `global_features == FEATURES` and `truths == ['is_'+c for c in classes]`. Store its hash. Check that ONNX input dim = 26 and output dim = 6. |
| F9 | Medium | missing guard | `analysis/models/registry.py:10–44`; `processing_modes.validate` | RUN never checks that its `--year` is in `training_data.eras`, and neither hash contains the year. A model trained on 2022 would run on 2023 without complaint. | Pass `year` to `validate` → `FoldModels` and require it to be in `eras`. |
| F10 | Medium | source (pre-existing; affects the EOS open item) | `runner.py`, `submit_condor.py` (no `--output_location`), `condor/submit.sh:24`, `analysis/utils/path_handler.py` (`root_path=/eos/user/c/cgupta/higgscharm`) | Under Condor, neither the `.coffea` path nor the parquet `output_location` can be redirected. Only `submit.py` has `--output_location`, and nothing forwards it. TRAIN and RUN (and legacy) therefore write into the same EOS area with about 81 GB free (full-fix state note). Chirayu has ruled out deleting anything, so a new location needs a code change. | Add `--output_root` to `runner.py`/`submit_condor.py`, forward it through `arguments.json` → `submit.sh`, and use it for both `Paths` and `output_location`. |
| F11 | Medium | source | `jobs_status.py:27–34`, `:436`, `:463` | `jobs_status.py` only accepts workflow names that are YAML stems, and it looks in `condor/<workflow>/…`. TRAIN/RUN jobs sit in `condor/<workflow>__<mode>/…`, so they cannot be monitored or resubmitted. Historically about 35% of jobs failed on the first pass (`submit.py` comment). | Add `--mode` to `jobs_status.py` and use the same `job_workflow`. |
| F12 | Low | demonstrated | `analysis/utils/eos_io.py:142–149` (`read_parquet`) | The server fallback triggers only on `OSError`. A zero-byte or truncated file from a stale FUSE read raises `pyarrow.ArrowInvalid`, which is not an `OSError` (R5). The fallback therefore misses the stale-file case. The failure is loud, not silent. | Also catch `pa.ArrowInvalid` for `/eos` paths, then retry from the server. |
| F13 | Low | source | `condor/submit.sh:38–51` | If the Python helper that builds `MODE_OPTS` fails, `bash -e` does not see it, because the failure happens inside a process substitution. `MODE_OPTS` is then empty and the job runs in **legacy mode**, writing into the `__mode` path. Impossible with well-formed `arguments.json`, but unguarded. | Write the options to a file and check the exit status, or let `submit.py --args_json` read them itself. |
| F14 | Low | missing guard | `analysis/features/hww.py:46–58` (`selection_signature`) | The hash covers `corrections/selections/working_points/leptonmva/*.py` and three SF directories. It does not cover `negrw_models.joblib` (`negrw.model`), JEC/JER, jet-veto or c-tag SF data, or `analysis/data/lhe_yukawa`. A changed negrw ensemble or JEC tag between TRAIN and RUN would go undetected. | Add these artefacts' SHA256 to `selection_signature`, or to a separate `inputs_hash` that RUN provenance and cards check. |
| F15 | Low | source | `register_folds.py:55` | `git_commit` is `git rev-parse HEAD` in the cwd. It ignores the dirty tree, and the dirty tree is the actual state now. | Record `git status --porcelain` plus a diff hash, or refuse a dirty tree for production. |
| F16 | Low | source | `analysis/processing_checks.py:15–24` | The duplicate-file (UUID) check is per job only. The builder's `chunks_read == len(chunks)` (`build_cards…:62–64`) catches identical chunks across jobs, but not the same file listed under two datasets. | Optionally do a cross-job UUID check in `check_train_outputs` or the card builder. |
| F17 | Info (behaviour change in legacy) | source | `runner.py:111` | `subprocess.run(..., check=True)`: in legacy mode, one failing dataset preparation now aborts the remaining datasets. It used to continue. This is probably desirable, but it is a change. | Keep it and document it, or collect failures and report them at the end. |
| F18 | Info (fragile) | source | `base.py:161` | TRAIN passes `shift="train_nominal"` so that no variations are built. This relies on every correction's non-`None` branch adding the same nominal. Today that holds by inspection: `toppt.py` else-branch adds the nominal; `higgs_hf`, `hplusc_fs` and `partonshower` have nominal 1; `lhe_norm` only touches variations. The author's seeded legacy = TRAIN check is consistent with this. A future correction keyed on shift names could break it silently. | Use a separate `variations=False` flag in `weight_manager`. |

**Passed (checked):**
- **Fold assignment:** `event mod k` on uint64 (`features/hww.py` `event_folds`) is the same in TRAIN shards, `split_folds` (re-verified per shard) and `FoldModels.score`. Object-shifted copies keep the event ID, so they keep the fold. Model *i* has test = *i*, validation = (*i*+1) mod *k* and trains on the rest. RUN scores fold *f* with model *f*. **No train/test leakage**, provided b-hive uses the generated file lists. That last step is external and declared only by `excluded_fold`. Data and label −1 are excluded from the supervised lists.
- **Normalisation:** sumw is taken from pre-veto `events` in `process()`, once per chunk, including zero-selection chunks (`base.py:~84–95`). It equals the legacy `dump_chunk_sumw`. `lumi·xsec/Σsumw` is applied after the merge. The negrw renormalisation (`Σw/Σ|w|g`, from nominal for weight variations, per variation for negrw ± and object shifts) matches `make_combine_inputs.process_sample`, and the author test `test_variance_and_negrw_normalize_after_chunk_merge` covers it.
- **Systematics completeness in RUN:** every `weights.variations` is in the nominal templates; every object shift is a separate record (`kind={'object'}`). negrw ± are nominal-only, as in legacy. All 5 vjets samples per era are negrw-configured, so no vjets sample lacks `CMS_negrw_vjets` (checked in all four eras). Weight shapes come from `combine.shape_systematics`. Object shapes are discovered (Up and Down both required), as in legacy. A missing required variation raises unless it is declared not applicable.
- **Legacy unchanged:** the mode gates (`base.py` sumw dump, the shift filter, the sink switch, histograms; `submit.py` execution checks; `submit_condor.py` paths) are all no-ops for `legacy`. `condor/submit.sh` falls back to `--mode legacy` for old `arguments.json`. The intended legacy changes are the jet re-sort, the PDF-only combined variation, `check=True` and the stricter EOS errors.
- **Sol fixes:**
  - `object_selections.py:590–591`: the shared jet collection is now sorted. Regression `test_allfix.py:368`.
  - `lhepdf.py:97–99`: the PDF-only combined variation now equals PDF. Regression `TestPdfOnlyCombined`.
  - Both fixes are correct. Neither supplies the missing H+c αS, which remains an open physics decision.
- **EOS port:** `_exists_on_server` and `isdir` now raise on server errors instead of reporting "absent", which is good. `listdir` dropped the `errno 3011` shortcut (`eos_io.py:~55`), so a NotFound with unusual wording now raises (loud). The parquet fallback reads the full file into memory, which is fine for `sumw` records.

## 3. TRAIN vs RUN vs legacy: output schemas, and what differs

**Output trees (directories, not Git branches).**

| | legacy | TRAIN | RUN |
|---|---|---|---|
| Condor job dir | `condor/<wf>/<year>/<ds>` | `condor/<wf>__train/…` | `condor/<wf>__run/…` |
| `.coffea` | `outputs/<wf>/<year>/<ds>/` (cutflow, sumw, lumi) | `outputs/<wf>__train/…` (**dir not created, F4**) | `outputs/<wf>__run/…` (**F4**) |
| per-event parquet | `<wf>/<year>/<ds>/<cat>/` nominal + `<cat>/<shift>/` per object shift; `sumw_records/` | `<wf>__train/<year>/<ds>/<cat>/`, nominal only; no `sumw_records` (sumw is in the `.coffea`) | none by default; `--slim_ntuple`: `<wf>__run/<year>/<ds>/<cat>/[<shift>/]` |
| objects in `.coffea` | `histograms` (legacy coffea mode), `metadata` | `samples/<s>/{sumw,sumw2,events_read,chunks_read,chunks,selected_events}`, `provenance` (`mode`, `year`, `features_hash`, `selection_hash`, `folds`), `execution_checks`, `metadata` | as TRAIN, plus `samples/<s>/templates/<cat>/<variation>/{counts,sumw2}[channel]`, `norm_raw`, `norm_rw`, `negrw`, `kind`; `samples/<s>/controls` (nominal-only histograms); `provenance.model_manifest_hash` |

**Per-event columns.**
- **Legacy parquet:**
  - all **73** `histogram_config` axes (2D → first element, nulls kept);
  - `event`;
  - on the nominal tree, MC only: `weight_nominal`, one `weight_<partial>` per correction, and `weight_<var>` for every Up/Down variation;
  - `weight_negrw` and `weight_negrw_std` on negrw datasets;
  - schema metadata `sumw`, `xsec`, `era`;
  - shift trees: the same variables plus `weight_nominal` only.
- **TRAIN parquet:**
  - the 26 `FEATURES` as float32, with nonfinite → 0 already applied and the 11 `cjet_cand_ctag2d_*` one-hots precomputed;
  - `event`, `run`, `luminosityBlock`, `fold`, `weight_nominal`, `process`, `sample`, `label`, `is_<class>`×6;
  - on the 5 negrw datasets only: 20 `gen*`/`lhe_*` axes plus `weight_negrw(_std)`;
  - metadata `processing_mode`, `features_hash`, `selection_hash`, `folds`, `sample`, `year`, `xsec`, `source_file`;
  - `split_folds` adds `weight = weight_nominal·lumi·xsec/Σsumw`;
  - **dropped compared with legacy:** the other 47 axes (jet arrays, `jet1/2/3_*`, η/φ, `cjet_cand_flavour`, raw `cjet_cand_cvsl/cvsb_pnet`, leading-jet tags, gen/LHE axes on non-negrw samples), all `weight_<partial>` and `weight_<var>` columns, and all shift trees;
  - **added compared with legacy:** `run`/`lumi`, `fold`, the labels, precomputed one-hots.
- **RUN slim ntuple:** the TRAIN schema in each shift directory, plus `weight_<var>` on the MC nominal tree. It has **no score or `fold_model` column**.

**Consequences.**
- **Feature/model parity.** The feature order is identical to the b-hive 2dcats config. The one-hots use the same `ctag2d_categories.onehot_columns` as legacy `postprocess/inference.py`, and the nonfinite → 0 policy is the same. Two differences:
  - legacy zero-fills a *missing* feature with a warning, whereas TRAIN/RUN raise (stricter);
  - legacy `run_inference --split full` scores the 90% training events in-sample, whereas RUN is strictly out-of-fold.
- **The model itself changes**, so it is not comparable with v11:
  - **split:** v11 used `event%10==9` as test (90% train); k=5 with a separate validation fold trains on 60% per model;
  - **weight:** v11 used raw `weight_nominal` (`prep_training_inputs.py:91–93`), with no `lumi·xsec/sumw`; TRAIN uses the normalised weight. This changes per-sample weights within a class. Check b-hive's class re-balancing (`bins_pt` / `bins_eta` on `dilepton_pt` / `dilepton_mass`) before comparing ROCs.
  - Wγ (`WG`) is unlabelled in both and absent from the cards (F2).
- **Systematics.** TRAIN is nominal-only by design: object shifts are switched off after hashing, so its signature stays equal to RUN's. Training is therefore unaffected by systematics. Only RUN carries variations. The slim ntuple carries weight columns on the nominal tree only, and shift trees carry `weight_nominal`, as in legacy.
- **Downstream consumers.**
  - The legacy chain (`run_postprocess.py`, `run_inference.py`, `make_combine_inputs.py`, the plotting in `postprocess/utils.py:194`, which reads `output["histograms"]`, and `jobs_status.py`) cannot read TRAIN or RUN outputs. RUN outputs go only to `build_cards_from_templates.py`. TRAIN outputs go to `check_train_outputs.py` → `split_folds.py` → b-hive.
  - The plan's "slim ntuple as insurance for the old parquet route" needs an adapter. The layout is per-chunk and not per-sample merged, and there are no scores.
  - A TRAIN "Pass A" data/MC validation (plan §2.5) can use only the 15 kinematic features and nSV. TRAIN has no control histograms; `controls` are RUN-only and nominal-only.
  - The negrw scorer runs inline in both modes. Its training region (`veto_emu_sr`) and its disjointness from the new SR under the new lepton WPs belong to Brief 1 and were not re-checked here.

## 4. Evidence table (protocol format)

| Item | Prescription / source | Implementation | Check | Observed | Status |
|---|---|---|---|---|---|
| Legacy unchanged | Framework note 2026-11-05; brief | `base.py` mode gates; `submit*.py`; `submit.sh` | source diff read | no-op for legacy except intended changes, F17 | checked (source) |
| Fold/leakage | plan §2.4; framework note | `features/hww.py:event_folds`, `split_folds.py`, `registry.py:score` | source + author tests + 49/49 run | disjoint test/valid/train; out-of-fold scoring | checked; b-hive use of lists external |
| sumw incl. zero-selection chunks | plan §2.3 | `base.py:~84–95` | source; `test_train_row_coverage_counts_empty_chunks…` | correct, pre-veto | checked |
| Card normalisation and parity | legacy `make_combine_inputs.py` | `build_cards_from_templates.py` | R1–R3, R8; source compare | F1, F2, F5, F6, F7 | **defects reproduced** |
| Condor forwarding | brief | `runner.py:111`, `submit_condor.py:161–166`, `submit.sh:38–51` | source + R4 | flags forwarded; output dir missing | **defect reproduced (F4)** |
| Manifest/hash guards | plan §2.2 | `registry.py`, `register_folds.py`, `hww.py` signatures | source; b-hive config read | partly tautological; no era check | missing guards F8, F9, F14 |
| EOS fallback | HZZ `7962523` port | `eos_io.py` | R5 + author test | ArrowInvalid not caught | F12 |
| negrw in TRAIN/RUN | legacy `process_sample` | `base.py` `_mode_sink`, `sinks/hww.py` | source + author test; vjets census | matches legacy | checked |
| Event-MVA in RUN | brief; framework note | `processing_modes.validate`, `FoldModels` | source | no v11 fallback; strict probabilities | checked |

## 5. Limits, downstream impact and decisions

**Not done.** No Condor job, no real NanoAOD processing (I relied on the author's seeded legacy = TRAIN = RUN checks; that is author-reported and was not re-executed), no b-hive run, no real fold model, no Combine run. The F7 trigger was not searched for in real inputs. No full per-sample × per-nuisance completeness audit was made against a real production.

**Downstream.** F1–F5 must be fixed before any TRAIN or RUN production is worth submitting. F4 wastes the whole Condor CPU time of every job. The fixes touch only TRAIN/RUN paths (plus F10 for the EOS location), so legacy outputs are not invalidated. After fixing, add tests for the gaps listed in §1, then smoke-test **one dataset per mode through Condor preparation and `submit.sh`** before a production. That smoke test needs Chirayu's OK.

**Needs Chirayu.**
1. Should Wγ (`WGtoLNuG_*`) be in the fit? See F2. If it stays out, record the exclusion explicitly.
2. Authorise the edit owner to fix F1–F5 (and F8/F9/F10/F11). Who edits is the edit owner's call; this review changed nothing.
3. Choose a new output root for F10, since nothing may be removed from EOS.
