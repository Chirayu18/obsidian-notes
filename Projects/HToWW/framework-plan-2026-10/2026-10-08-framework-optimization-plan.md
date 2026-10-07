---
tags: [reference]
status: active
date: 2026-10-08
source: lxplus
---
# higgscharm framework: final fixes and re-architecture plan (2026-10-08)

This is a plan only. No repo file was edited, nothing was committed or submitted, and nothing on EOS was deleted.

- **Repo:** `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` (branch `hww-analysis`, uncommitted fixes).
- **Prior context:** [[2026-10-01-full-rerun-plan-and-findings]] and [[2026-10-06-independent-review]].
- **Scripts and raw outputs:** `/eos/user/c/cgupta/higgscharm/runall/plan/` (and `plan/tthmva/` for the lepton-MVA benchmark).

**Tags on numbers.** **[M]** means measured in this session. **[L]** means read from existing logs or outputs. **[E]** means an estimate or extrapolation; the basis is given.

---

## 0. Summary

1. **The event loop is CPU-bound, not I/O-bound.**
   - A TTto2L2Nu job used 9 h 01 min of CPU in 5 h 13 min of wall time with 2 workers, which is 87% of 2 cores **[L]**.
   - On a local file, decompression is 0.7 s of a 39 s chunk **[M]**.
   - 89% of processor time goes to re-running the full selection, weights and output for each of the 14 object-shift passes **[M]**.
2. **38% of processor CPU is spent on one avoidable step.** `pa.Table.from_pydict()` receives awkward arrays and converts them element by element: 14.8 s of a 38.9 s chunk **[M]**. Converting the columns with `ak.to_numpy` first is 447× faster for that step **[M]**. This is a one-line class of fix, and it also helps train mode.
3. **The downstream round trip costs 1.5–2.5 h per era and about 70% of the EOS footprint.** Per era: merge 27–65 min, inference 8–23 min, card build 12–43 min **[L]**. `hww_combine_full` plus `_ttsyst` occupy 266 GB **[M]**, of which:
   - shards: 39 GB in postEE;
   - merged shift trees: 38 GB in postEE, about half of it a full copy written again under `mva/`;
   - EOS atomic-version files: 13%.

   Run mode (inline scoring, histograms out) removes the merge and inference steps entirely.
4. **GPUs do not help this analysis today.**
   - The v11 MLP has 14.9k parameters. It scores 0.9 M events/s on one CPU thread **[M]** and trains at 0.4–0.6 M events/s on CPU **[M]**.
   - The event loop is awkward/Python overhead on small arrays (see item 1).
   - GPUs are worth booking only for bigger models, ensembles or hyper-parameter scans.
5. **Thomas's ttH lepton-MVA can be scored without a cache, about 140× faster than a cache miss and about 60× faster than a cache hit.** Measured on 20k real 2022postEE tt events (~50k leptons), §4.
   - His evaluator **disagrees with TMVA itself** for 3.3% of electrons (by up to 0.032) and 0.04% of muons (by up to 0.0014). The cause is a split-convention bug: he uses `>`, TMVA uses `>=`.
   - My 2026-08-12 ONNX conversion (`BRANCH_LEQ`) has **the same bug**. With `BRANCH_LT` it matches TMVA to 1e-6 **[M]**.
6. **Two decisions must be made before the next production so it runs once.**
   - **(a) Selection-changing fixes:** third-lepton veto, mT cut, Type-1 MET jet selection, jet-veto map, and whether Thomas's ttH-MVA lepton working points are adopted.
   - **(b) Production strategy (recommended):** first a cheap nominal-only TRAIN-mode pass, which costs about 14% of a full pass per chunk **[M]**; retrain and freeze the model; then a single full RUN-mode production with the frozen model inline. That production also writes a slim per-shift feature ntuple as insurance against a later retrain.

---

## 1. Map of the current framework

### 1.1 Data flow

```
NanoAOD (xrootd, ~35.7k files / 4 eras)                         [L: partitions.json]
  └─ condor: 1 job / partition (2476 jobs main + 152 ttsyst; workers=2, chunksize 100k)
      runner/submit.py → BaseProcessor.process(chunk)
        dump_chunk_sumw (pre-selection sumw record)
        object_corrector_manager: JEC/JER/Type-1 MET (+JES, JER, MET-uncl shifts),
                                  muon SS (+4 shifts), electron SS (+4 shifts) → 15 (collections, shift)
        for each of 15 passes: ObjectSelector → PackedSelection → weight_manager
                               → eval(axis expressions) → negrw score (vjets)
                               → dump_parquet  (nominal: 127 cols incl. 53 weight_*; shift: 75 cols)
  └─ EOS: <sample>_<N>/base/[<shift>/]*.parquet + sumw_records/
run_postprocess.py --postprocess    → merged <sample>.parquet and <shift>/<sample>.parquet   (per era)
scripts/mva/run_inference.py        → <…>/mva/<sample>.parquet (FULL dataframe rewritten + 6 scores)
make_combine_inputs_full.py (wrapper: era renames, tt alt-sample ratios from the _ttsyst workflow)
  → scripts/combine/make_combine_inputs.py → ROOT templates + datacard
combineCards → run_limit.sh (AsymptoticLimits ×3: full / stat-only / freeze autoMCStats)
```

### 1.2 Where the CPU goes (processor), measured

**Setup.** One chunk of 20,000 TTto2L2Nu 2022postEE events. The file was copied to node-local `/tmp`, run on lxplus988 in the `b_hive` environment (coffea 0.7.22), single process, with timing wrappers and cProfile.

**Script and outputs.** Script: `plan/profile_processor.py`. Outputs: `plan/profile/profile_TTto2L2Nu_20000*.{json,txt}`. Selected rows: 749 nominal (3.7%).

| stage | time [s] **[M]** | share |
|---|---|---|
| `process()` total | 38.9 | 100% |
| object corrections, once per chunk (JERC 1.68, muon SS 0.34, electron SS 0.09) | 2.1 | 5% |
| 15 × `process_shift` (nominal 3.3 s, each shift 2.31–2.42 s) | 36.5 | 94% |
| — of which `dump_parquet` (15 calls) | 14.8 | **38%** |
| — of which `ObjectSelector.select_objects` (15 calls) | 11.3 | 29% |
| — of which `weight_manager` (15 calls) | 2.8 | 7% |
| — remainder: event-selection `eval`, axis-expression `eval`, cutflow | ~7.6 | 20% |
| file open | 0.5 | |

**cProfile top internal costs [M].**

- `builtins.dir` is called 1.08 M times (7.8 s). The calls come from per-element `awkward.highlevel.__getitem__` / `__getattr__` (1.06 M calls, 14.5 s cumulative), and all of them originate in `pa.Table.from_pydict(awkward)` in `analysis/utils/parquet_writer.py:52`.
- `correctionlib.from_file` is called 109 times (1.35 s). JSONs are re-parsed on every shift pass.
- LZMA decompression is only 0.72 s.

**Microbenchmark** (`plan/dump_microbench.py`, on the 749 × 127 output shard) **[M]**:

- `from_pydict(awkward columns)` takes **1.020 s**.
- `from_pydict(numpy columns)` takes **0.0023 s**, i.e. 447× faster.
- The tables were not `.equals()`-identical. Option and nullable types differ, so the fix needs a schema check (§5, P1-perf).

**Production scale, from condor logs [L]** (`plan/condor_stats.py`; terminated attempts including failures; main workflow):

| era | attempts | rc=0 | CPU-h total | median CPU-h/attempt | max | memory median / max [MB] |
|---|---|---|---|---|---|---|
| 2022preEE | 627 | 463 | 291 | 0.26 | 7.0 | 1739 / 3100 |
| 2022postEE | 1475 | 1016 | 678 | 0.27 | 9.1 | 1750 / 3746 |
| 2023preBPix | 769 | 616 | 394 | 0.39 | 3.5 | 1894 / 3261 |
| 2023postBPix | 480 | 383 | 208 | 0.36 | 4.1 | 1850 / 3170 |
| **sum** | 3351 | 2478 | **~1570** | | | |

- The `_ttsyst` workflow adds about 54 CPU-h.
- A single TT job is 88 chunks, 5 h 13 min wall time and 9.0 CPU-h, i.e. about 3.7 ms CPU per event **[L]**.
- **Jobs request 1 CPU but use 1.98** (workers=2) **[L]**. That over-commits the slot and is worth fixing either way.
- **Input volume** (from chunk entry ranges in shard and sumw_record names) **[M]**: MC 2.42 G events (preEE 816 M, postEE 444 M, preBPix 439 M, postBPix 725 M); data about 1.89 G. Data is counted from chunks with ≥1 selected event, so it is a lower bound. The MC count may include renamed or resubmitted chunks, so treat it as about ±20% **[E]**.

### 1.3 Where the wall time goes downstream [L]

From the pipeline logs (`logs_runall/pipeline_2022.log`, `pipeline_2023.log`; each pipeline ran as a single condor job):

| step | 2022preEE | 2022postEE | 2023preBPix | 2023postBPix |
|---|---|---|---|---|
| postprocess merge | 32 min | 65 min | 40 min (+10 ttsyst) | 27 min (+6) |
| inference | 9 min | 23 min | 14 min (+3) | 8 min (+2) |
| card build | 18 min | 43 min | 31 min | 12 min |
| limits (×3 fits) | 8 min | 4 min | 4 min | 6 min (after a resume) |

Combined: 2022 took 9 min. The Run 3 combination took 33 min. End to end for two eras downstream was about 3.5 h.

Other costs on top of that:

- **Failures.** First-pass failure rates were 25–34%. The causes were dead or slow xrootd sites and a 60 s timeout. There was also one corrupted ROOT histogram from an EOS write glitch.
- **Production wall time.** About 1–2 days for 4 eras.
- **Tail latency.** It is set by the longest jobs: TT jobs run 88 chunks in 5 h.

### 1.4 Where EOS goes [M]

From `eos quota`: 864 GB logical of 1 TB used, 2.33 M files. The `higgscharm/outputs` tree holds 417 GB:

| dir | GB |
|---|---|
| `hww_combine_full` | 198 (postEE 91.7, preBPix 52.0, preEE 28.5, postBPix 26.1) |
| `hww_combine_2dcat` (July, superseded; cleanup is the user's call) | 179 |
| `hww_combine_full_ttsyst` (nominal-only alt tt!) | 68 (postEE 31.6) |
| `ztomumu`, `hww_genrw_train`, other small | ~1.3 |
| `combine/` | 27 |

Breakdown of `hww_combine_full/2022postEE` (91.7 GB):

| component | GB |
|---|---|
| per-job shards `<sample>_<N>/` | 39.0 (needed only until the merge) |
| merged shift dirs (14) | 38.0 (about half is the `mva/` re-write) |
| merged nominal | 6.3 |
| `mva/` nominal | 5.5 |
| `parquets_<sample>/` | 2.9 |

**Notes.**

- **Duplication from inference.** `inference.py:171-176` rewrites the **entire** dataframe with the 6 scores added. For example, TT JES-Up is 0.96 GB merged plus a 1.05 GB `mva` copy, and TT nominal is 1.90 GB plus 1.99 GB.
- **Version files.** EOS `.sys.v#.*` atomic-version files from overwrites/resubmits are 3.2 GB of 25.1 GB in 2022preEE (13%) **[M]**.
- **Column waste.**
  - The 53 `weight_*` columns are about 50% of the nominal-shard bytes.
  - 20 gen/LHE columns, needed only for V+jets negrw, are written for every sample.
  - Shift trees carry 54 kinematic columns where the fit needs 26 features plus the weight **[M]** (`plan/colcensus.py`).

---

## 2. Target architecture

### 2.1 Principles

1. **One shared feature module.** Training and fitting must compute the MVA inputs with the **same Python function**.
2. **Fail loud.** A missing input, column, key, PD name, cross section or weight variation is an exception, never a fallback. This is the recurring root cause behind 8 of the bugs in the log and review. Allowed exceptions are an explicit allow-list in config, e.g. "diboson has no LHE weights → those rows are `-` in the card".
3. **Validate the config before submission.** Validation runs on the submit host, not in 2500 jobs.
4. **One processor, two modes.** Corrections, selection and weights are shared. Only the "sink" differs: histograms in run mode, nominal feature ntuples in train mode.
5. **Shift-aware evaluation.** Recompute only what a shift changes. Lepton shifts do not need jet re-selection; JES/JER/unclustered shifts do not need lepton re-scoring. This is an optimisation for after the restructure, not before it.

### 2.2 Modules to add or change

| new / changed | content |
|---|---|
| `analysis/features/hww.py` (new) | `FEATURES = [...]` (ordered, 26 for v11) and `def compute(objects, events) -> dict[str, np.ndarray]`, vectorised. It includes the **c-tag 2D one-hot** (edges `X_HFVLF=[0,.25,.452,.808,1]`, `Y_BVC=[0,.006,.017,.055,.761,.944,.985,.995,1]`, logic ported from `b-hive/scripts/append_onehot.py:25-56`), plus `FEATURES_HASH` (sha256 of names, order, dtypes and one-hot edges). The YAML references a feature set by name instead of 26 `eval` strings. |
| `analysis/models/registry.py` (new) | Loads `models/<name>/<version>/{model.onnx or model.pt, meta.yaml}`. `meta.yaml` holds: features (ordered), `features_hash`, classes, k-fold scheme, training data manifest (workflow, eras, git hash, file-list hash), b-hive config and metrics. **Hard check:** `meta.features_hash == features.FEATURES_HASH`, else raise. |
| `analysis/config/validate.py` (new) | Runs in `runner.py` before submission. See §2.6. |
| `BaseProcessor` | A `mode` switch, `run` or `train`. Per-dataset `object_shifts` (shift datasets). Correctionlib sets cached at module level. |
| sinks: `analysis/sinks/{hist_sink.py, ntuple_sink.py}` | `hist_sink`: coffea/hist accumulator (extends the existing `output_format: coffea` path in `hist_filler.py`, which already has a `variation` StrCategory axis). `ntuple_sink`: numpy-backed `pa.Table` writer (fixes the 38% hotspot). |
| `scripts/combine/build_cards.py` | Reads summed histograms, not parquets. Replaces `make_combine_inputs.py` and the `make_combine_inputs_full.py` wrapper. Era renames come from config, not a monkey-patch. |

### 2.3 RUN mode (production for the fit)

Per chunk:

1. Write the pre-selection sumw record as today. In run mode it is also an accumulator in the output, so no sidecar glob is needed (removes the "sumw trap" class).
2. Apply corrections once. This produces the nominal plus the shifted collections, as today.
3. For each pass (nominal, 14 object shifts):
   1. Select objects and events.
   2. Build the weights container.
   3. `X = features.compute(...)`.
   4. Score with the registered model (fold = `event % k`, see §2.5). Use ONNX Runtime or torch CPU. Both exist in the job image: onnxruntime 1.23.2 and torch 2.4.1 **[M]**.
   5. Set `ch = argmax`, `D = max score`.
   6. Fill `templates[dataset, channel, D, variation]`:
      - **nominal pass:** variation = `nominal` plus every `weights_container.variations` entry (all 53 weight columns become histogram slices; no per-event weight columns stored);
      - **shift pass:** variation = the shift name, nominal weight only.
   7. Fill control histograms: the ~53 plotting variables, nominal plus a configurable short variation list.

**Output per job.** One `.coffea` with the accumulators. Summing is trivial and takes seconds. Size estimate [E]: 6 channels × 10 bins × ~80 variations × ~60 datasets ≈ 3 M doubles ≈ 25 MB uncompressed for templates, plus control plots. The current full-era coffea with all variables is 319 MB for postEE **[L]**. The total stays far below the current 266 GB of parquet.

**Cost [E].** Inline MLP scoring of about 750 selected events × 15 passes per 20k chunk is about 12 ms on CPU (0.9 M ev/s **[M]**), i.e. negligible. Dropping `dump_parquet` saves about 38% of processor CPU **[M]**. Caching correctionlib saves about 3% **[M]**. The merge, inference and parquet-card steps (1.5–2.5 h per era **[L]**) disappear. Card building from summed histograms is a few minutes per era [E].

**How the pieces fit in run mode:**

- **Negative-weight reweighting (`negrw`).** g(x) needs the 20 gen features. They are computed inside the job, as today in `base.py:143-147`, but no longer written out.
  - The card applies a yield-preserving renormalisation per sample: `Σw / Σ|w|g` over all selected events of the sample (`make_combine_inputs.py:282-290`).
  - Histograms therefore accumulate, per sample and per variation:
    - **(i)** the histogram filled with `|w|·g`;
    - **(ii)** the scalars `Σw` and `Σ|w|g`;
    - **(iii)** the std-variation histograms filled with `|w|·clip(g±g_std)` plus their `Σ|w|g±`.
  - The card builder then applies `renorm = Σw/Σ|w|g` after summation. This is exactly equivalent to today's per-sample computation, because the sums are additive.
  - Keep the anchored dataset gate (`_dataset_matches`). Add a validation rule that every negrw dataset has the model's training features.
- **c-tag one-hot.** Computed in `features/hww.py` from `cjet_cand_cvsl_pnet` / `cvsb_pnet`. This closes review A2. The 2D c-tag SF stays as-is (expert check pending); only its plumbing as a weight variation moves into the histogram axis.
- **Alternative-sample systematics** (tt hdamp/mtop/UE, and later CR1/CR2 and V+jets alternatives). Declared in the era YAML, per dataset:
  ```yaml
  TTto2L2Nu_Hdamp158: {key: tt, shift_of: TTto2L2Nu, shift: tt_hdampDown, object_shifts: false}
  ```
  - The processor runs these nominal-only and fills `variation=tt_hdampDown` under their own dataset.
  - The card builder forms `ratio = alt / TTto2L2Nu(nominal)` per channel and bin, with the existing 10%-stat integrated fallback, and applies it to the whole `tt` process. This ports `make_combine_inputs_full.py` lines 35-99 into config.
  - `hww_combine_full_ttsyst.yaml` is then deleted.
  - Validation rule: every `shift_of` exists and every shift has an Up and a Down.
- **Card builder.** It reads histograms and fails loud:
  - any `shape_systematics` entry missing for a process marked "1" raises;
  - "not applicable" is an explicit per-process list in YAML (diboson LHE weights);
  - `xsec ≤ 0` for a carded sample raises;
  - after writing, every ROOT histogram is read back and checksummed (the 2023postBPix corrupted-histogram incident);
  - the era-tag substitution (`_2022` → `_2023`) moves from the wrapper monkey-patch (`make_combine_inputs_full.py:43-48`) into config.

### 2.4 TRAIN mode

- **Pass structure.** Nominal pass only: no object shifts and no weight variations except `weight_nominal`. The MC-signal theory weights are kept only if they are needed as training weights.
- **Sink.** `ntuple_sink` with the numpy fix. Columns: `FEATURES` + `weight_nominal` + `event` + `run/lumi` + `process` + `label` (from `mva.labels.process_groups`) + fold id. Gen features are written only for negrw-training datasets.
- **Cost [E].**
  - From the profile, nominal pass plus corrections is 3.3 + 2.1 = 5.4 s of 38.9 s, i.e. **~14% of a full pass** per chunk **[M]**. Making corrections lighter (no shift collections) and skipping weight variations brings it lower.
  - I/O and decompression are unchanged; they are small at 0.7 s per 20k events **[M]**.
  - Output is about 25% of today's nominal shard bytes: 54 of 127 columns and no weight columns **[M, colcensus]**.
- **Training** (b-hive or a slim trainer):
  - **k-fold by `event % k`** (k = 5 recommended). This replaces `event % 10 == 9` and removes the "2022postEE backgrounds overlap the training events" caveat without losing fit statistics: in run mode each event is scored by the model that did not see it.
  - Labels: 6 classes, with **WG added to diboson** (user decision 2026-10-02). This requires the gen-photon overlap removal against W+jets first (§5, P1-8).
  - Inputs: central signal, corrected MET, all 4 eras.
- **Registry.** The output is `models/hww_v12/<k-fold>/{fold_i.onnx}`, `meta.yaml` and `features_hash`. Export to ONNX for inference; `b-hive/scripts/convert_model_to_onnx.py` exists. Validate the ONNX export against torch on 10k events, max |Δ| < 1e-5.

### 2.5 How the "reprocess only once" requirement is met

The new model has to be trained on the corrected production, and run mode needs that model. So:

1. **Pass A, TRAIN mode, all 4 eras, MC + data, nominal only.** About 14–20% of a full production [E].
   - Use it for: retraining; data/MC validation of the selection fixes (slope study, preEE deduplication check); and a stat-only expected-limit check with the new model (stat-only needs no shifts).
2. **Freeze model v12** in the registry.
3. **Pass B, RUN mode, the only full production.** Histograms out, plus an **opt-in slim fit-ntuple safety net**:
   - nominal: `FEATURES` + 53 `weight_*` as float32;
   - shifts: `FEATURES` + `weight_nominal`.

   About 30–40% of today's bytes [E]. The safety net lets a later retrain or rebin be re-scored without Pass B, using the old parquet route. Drop it once the result is final.

The alternative of doing everything in one pass and keeping the parquet route for this production also works. It keeps all of today's merge, inference and EOS costs for this round and defers run mode to the following one.

### 2.6 Config validation (`validate.py`, before any submission)

- Every dataset key in the workflow resolves in the era YAML. Every carded sample has `xsec > 0`. `era ∈ {data, mc, signal}`.
- Every data PD name maps to a key of `hlt_paths` through `get_dataset_name` (would have caught A1). PD masks are mutually exclusive.
- Every `shape_systematics` entry has a producing correction for at least one carded process. Explicit `not_applicable` per process.
- `features_hash` of the registered model equals the code.
- negrw: the model file is readable in the image, its sklearn version matches the image (the July blocker), and its features are computable.
- Correctionlib file paths exist. Tag names exist in each JSON (JER split-tag case: check that the `systematic` input exists or that the `SFUncertainty` tag exists).
- `lhe_renorm_datasets` and `shift_of` targets exist.
- **Runtime counterpart:** a per-job event-count check (entries processed == file entries). `jobs_status.py` counts jobs, not events.

---

## 3. GPUs: where they help and where they don't

### 3.1 What I measured

| question | measurement | result |
|---|---|---|
| Is the event loop I/O-bound? | condor TT job: 9 h 01 min CPU / 5 h 13 min wall with 2 workers **[L]**; local profile: LZMA 0.72 s of 38.9 s **[M]** | **No.** It is CPU-bound in awkward/Python overhead. |
| MLP inference cost | v11: 26→128→64→32→6 with BatchNorm, 14,889 params; 1 M events in 1.09 s at 1 thread, 0.55 s at 4 threads **[M]** (`plan/mlp_cpu_bench.py`) | All selected events × 15 passes for a whole era is a few minutes of CPU. Not worth a GPU. |
| MLP training cost | same architecture, Adam, batch 1024: 393k ev/s at 1 thread, 560k at 4, 590k at 8 **[M]** (`plan/mlp_train_bench.py`) | 30 epochs × 5 M rows ≈ 4–6 min on CPU [E]. Data loading and b-hive preprocessing dominate, not the GPU-able part. |
| Lepton MVA (500 BDT trees) | ONNX Runtime 8.8 µs/lepton on 1 thread **[M]** | CPU is fine (§4). |

### 3.2 Where a GPU does help

- Larger models: the v32/kappa-HCE 13-class model; per-jet/particle-level networks if c-jet constituents are used; transformers.
- Hyper-parameter scans.
- k-fold × ensemble training: 5 folds × several seeds is about 25 trainings, and a GPU turns about 2 h of CPU into minutes [E].
- The negrw ensemble, if moved from sklearn HistGBDT to XGBoost or torch. It runs on CPU today and is fine there.

### 3.3 Where a GPU does not help

- The coffea 0.7 / awkward 1 event loop: no GPU backend. Awkward 2's CUDA backend is not production-ready for NanoEvents, and correctionlib is CPU-only.
- Condor CPU workers: no GPUs on the slots.
- Inline inference of a 15k-parameter MLP: kernel-launch latency would exceed the compute.

### 3.4 What GPU resources would require, from existing notes

- **lxplus-gpu interactive.** Kerberos hop from lxplus, pin the node, hold the ssh session (tmux dies at logout). This is fine for training a few-minute model.
- **Condor GPU (EosSubmit pool):**
  - request A100/H100 or MIG slices, **not V100S** (the per-GPU CPU/memory floor of ≥5 CPU / 15 GB cannot be met on V100S slots);
  - add `requirements = … && (TARGET.InStagedDrain =!= true)`;
  - check `condor_q -better-analyze` before waiting;
  - GPU-hours are scarce and queue waits of hours are normal.
- Neither is on the critical path for this analysis.

**Conclusion.** Spend the effort on the CPU event loop (§5 perf items, run mode) and use CPU for training. Revisit GPUs only if the model grows.

---

## 4. Thomas's ttH lepton-MVA: integration plan, with a cache-vs-recompute benchmark

### 4.1 What his branch does (`tvl/MVA`, read with `git show`, not merged)

- **Models.** `analysis/tthMVA/evaluator.py` `TMVAGradBDT` holds the TMVA BDTG with 500 trees (depth ≤ 8, no input transformations, all nodes `cType=1`), converted to nested JSON dicts. Evaluation is a Python `while` walk per tree, per lepton, using `if value > cut: right`.
- **Scoring.** `cache.py` `_calculate_scores` loops over (event, lepton) pairs and indexes NanoEvents per lepton with `events.Muon[i, j]`, reading 13 scalars with `float()`.
- **Cache.**
  - `get_scores` keeps one parquet per NanoAOD file under `/eos/user/<u>/higgscharm/.../tthMVA_cache/<dataset_partition>/`, keyed `(run, lumi, event, lepton index)`.
  - On a miss it computes, writes a temp file and merges under a `FileLock`. On every call it rereads the whole file cache, builds a Python `set` and `dict`, and loops over every event to assemble the output.
  - The cache directory is keyed by **his condor partition names**, which differ from ours.
  - The cwd-to-userpath logic mis-derives the path when run from `/eos/home-c/...`. Measured here: it printed `/eos/user/cgupta/higgscharm/higgscharm/...`.
  - Scores are computed on `self.events.Muon` **after** muon scale/smearing (`object_selections.py` `select_muons`). TMVA was trained on NanoAOD-level inputs.
- **Working points.**
  - Muons: `muon_promptMVA` tight_HWW = `tthMVA > 0.67`.
  - Electrons: `electron_promptMVA` ttHMVA_Run3 = `tthMVA > 0.9` plus dxy/dz/convVeto. A pT-split "HWW" variant uses 0.35 / 0.9.
- **SFs.** The newest consistent config is `hww_HWWmuonelectronWPs_withBothTTHmvaSFs.yaml`: muon `tight_HWW` with `promptMVA` SF, electron `Medium` with `promptMVA` SF. The SFs come from the latinos JSONs added in `analysis/data/.../muon_HWW/*_muonSF_latinos_HWW.json` and `electron_HWW/*_electron_cleanedLayout.json`. That config has **no object shifts** and uses stored `PuppiMET`.

### 4.2 Benchmark (scripts in `/eos/user/c/cgupta/higgscharm/runall/plan/tthmva/`)

**Input.** The 2022postEE `TTto2L2Nu` file `07a6b4e8-a99d-4cd4-8ab0-9a51635f6a6f.root`, the first file of partition `TTto2L2Nu_1`. It was read via `root://eoscms.cern.ch//eos/cms/...` because the grid proxy had expired (see §8). Events 0–2000 and 0–20000. Single thread, lxplus988, `b_hive` env.

**Scripts.**

| script | role |
|---|---|
| `bench_tthmva.py` | runs his `_calculate_scores` and his `get_scores` unchanged. `cache_base` is redirected into `out/cache_sim/`; his EOS cache is never touched. |
| `tthmva_vec.py` | vectorised flat-array tree walk, built from the TMVA XML (independent of his JSON) |
| `bench_fast.py` | numpy, numba and onnxruntime evaluators. The ONNX graphs are the August files plus a `BRANCH_LT`-patched copy. |
| `tmva_ref_real.py` | the real `TMVA::Reader` (CMSSW_14_1_0_pre4) on all tie-sensitive leptons plus 200–300 random ones |
| `cache_hit_real.py` | times a cache hit on 2 real cache files downloaded from his public CERNBox share |

**Timings, 20,000 events [M]** (2,000-event run in `out/bench_2000.json`; same picture):

| | muons (24,484) | electrons (25,713) |
|---|---|---|
| his `_calculate_scores` (= cache-miss compute) | 18.39 s (feature loop 12.76 + dict trees 5.64) | 20.06 s (13.85 + 6.20) |
| his `get_scores`, **cache miss** (compute + temp write + lock + merge + lookup) | **31.20 s** (1.27 ms/lepton) | **31.67 s** (1.23 ms/lepton) |
| his `get_scores`, **cache hit** (read + key set + dict + per-event loop) | **12.78 s** (0.64 ms/event) | **11.97 s** (0.60 ms/event) |
| vectorised feature building, all leptons at once | 0.004 s | 0.003 s |
| numpy flat-tree walk (chunk 1000) | 0.565 s | 0.587 s |
| numba flat-tree walk | 0.409 s (16.7 µs/lepton) | 0.442 s (17.2 µs/lepton) |
| **ONNX Runtime, `BRANCH_LT`** (1 thread) | **0.216 s (8.8 µs/lepton)** | **0.227 s (8.8 µs/lepton)** |
| speed-up of ONNX vs his miss / his hit | **144× / 59×** | **140× / 53×** |

**Cache-hit fixed cost on REAL cache files [M].** This cost is paid on every `get_scores` call (= per chunk × per particle × per pass), before the per-event loop.

| cache file | size | rows (μ / e) | events | read + key set + dict per call |
|---|---|---|---|---|
| `TTtoLNu2Q_4/e63e11e1…root.parquet` | 18.3 MB | 2,154,479 (951,898 / 1,202,581) | 943,465 | 1.70 s (μ), 2.18 s (e) |
| `094c4f8e…root.parquet` (top level) | 2.0 MB | 183,426 | 123,232 | 0.45 s, 0.17 s |

**Numerical equivalence, all against `TMVA::Reader` itself [M]** (`out/tmva_ref_{2000,20000}.txt`, `out/lep_*_fast.json`):

| implementation | max \|Δ\| vs TMVA, random sample | max \|Δ\| on tie-sensitive leptons |
|---|---|---|
| vectorised numpy / numba, float32 `>=` | 3.3e-16 | 3.3e-16 (all 861 e + 11 μ) |
| ONNX `BRANCH_LT` (float32 output) | ≤ 1.0e-6 | ≤ 1.0e-6 |
| **his evaluator (`>`)** | | **1.38e-3 (μ), 3.24e-2 (e)** |
| **August ONNX (`BRANCH_LEQ`)** | | 1.38e-3 / 3.24e-2 (reproduces his to 1e-6) |

Notes on the tie-sensitive leptons:

- **Mechanism.** TMVA `DecisionTreeNode::GoesRight` is `x >= cut` in single precision. When an input sits **exactly** on a split value, `>` sends it the other way.
- **Electrons: 861 / 25,713 = 3.3%.** NanoAOD `Electron_mvaIso` is stored at reduced precision and clusters just below 1 (0.99999881, 0.99999851, …). Those values are themselves TMVA split thresholds.
- **Muons: 11 / 24,484.** Here it is `jetBTagDeepFlavB` (e.g. 0.00183105) or `segmentComp`.
- **Working-point flips in this sample:** μ 0 (at 0.67); e 1 of 25,713 (at 0.9) and 0 (at 0.35). The effect on the selection is small, but the evaluator is not TMVA-exact, and the August validation note's "exact" claim only held for random continuous inputs.

### 4.3 Extrapolation [E]

The per-lepton and per-event rates are from §4.2. The per-file case is the real TTtoLNu2Q cache file above (943k events, 2.15 M leptons).

| | per file (943k events) | full 4-era production (≈4.3 G events, ≈1.1e10 leptons at the tt multiplicity of 2.51/event: an upper estimate) |
|---|---|---|
| his cache miss (first production) | ≈2.15 M × 1.25 ms ≈ **45 min** | ≈1.35e7 s ≈ **3,750 core-h** |
| his cache hit, per pass | 943k × 1.24 ms ≈ 19.5 min + ~10 chunk calls × 3.9 s fixed ≈ **20 min** | ≈5.3e6 s ≈ **1,480 core-h**. ×15 if called in each object-shift pass, as `select_objects` is in our `process_shift`. |
| vectorised + ONNX, per pass | 2.15 M × 8.8 µs ≈ **19 s** (numba ≈ 37 s) | ≈9.5e4 s ≈ **26 core-h**, about 1.7% of today's ~1,570 core-h production |
| cache storage | 18 MB per such file | 114 GB on EOS (his share) vs **0** |

For scale, today's whole main production logged about 1,570 CPU-h **[L]**. A cache hit alone would roughly double that per pass. Recomputing with ONNX adds under 2%. **The cache has negative value at every point**, including the steady state where every lookup hits. On top of that it adds a 114 GB EOS dependency, file locks across hundreds of workers, and partition-name coupling.

### 4.4 How to integrate it

**Do:**

1. **`analysis/leptonmva/tth.py`** with `lepton_features(events, "Muon"|"Electron")`, ported from `plan/tthmva/tthmva_vec.py:lepton_features`.
   - It is fully vectorised. The jet b-tag uses a guarded global index: `jetIdx > -1`, flattened jet offsets.
   - It computes on **NanoAOD-level inputs** (uncorrected `pt`), as TMVA was trained, **once per chunk before object corrections**. The result is attached as `Muon.tthMVA` / `Electron.tthMVA`, so every shift pass reuses it and nothing is cached.
   - Decide explicitly, with Thomas, whether the scale-corrected pT should be used. The training used NanoAOD pT, so the default is no.
2. **Evaluator.**
   - Preferred: ONNX with `BRANCH_LT`, regenerated by the August converter with the mode fixed. Ship the .onnx with a `meta.yaml` holding the variable list and XML sha256.
   - **Image caveat [M]:** in the job image, importing `onnxruntime` *before* `pyarrow` (or sklearn/hist) breaks those imports (`GLIBCXX_3.4.32 not found`). Import pyarrow first, at module top, or use the numba evaluator (17 µs/lepton) to avoid the issue.
3. **Validation** (a script kept in the repo, run in CI and before every production):
   - TMVA::Reader vs ONNX on ≥1000 real leptons per flavour **including all tie-sensitive ones**; require ≤ 1e-6;
   - per-era spot check on one file;
   - the floor policy for `log|dxy|`/`log|dz|` at 0: TMVA sees `-inf`. No zeros occurred in this file, but the policy must be decided and documented.
4. **Keep from his branch:**
   - the XMLs (identical md5 to `/eos/user/c/cgupta/HToWW/leptonmva/`);
   - the WP definitions in `working_points.py` (`muon_promptMVA`, `electron_promptMVA`), re-pointed at our attached field;
   - the SF code paths `add_promptMVA_weights` in muon.py/electron.py and the latinos SF JSONs. Their binning and provenance (which WP, which ID baseline, which eras) must be checked against the WPs actually used; there is one JSON per era for 2022–23;
   - his small `jerc.py` fixes (`Path.exists()`, `import warnings`, `raise ValueError`). These coincide with our review B10.
5. **Drop:**
   - `cache.py`, `TMVAGradBDT` (dict walk, `>` convention) and `convert_xml_to_json.py`;
   - the cwd/userpath logic and FileLock usage;
   - his `jerc.py`/`correction_manager.py` structure (pre-fix Type-1 MET and no-op JER, per the brief).

   Port only the lepton-MVA pieces onto our branch. Do not merge the ~28 overlapping files.
6. **Reprocessing implication.** Adopting ttH-MVA working points changes the lepton selection and adds new SFs and a new systematic. It also changes MVA inputs indirectly, through the selected population. **If it will be in the final result, it must be in Pass A and Pass B.** If not decided by then, it means another full production later.

---

## 5. Remaining correctness fixes

**Reprocessing (R) column:**
- **all** = every MC + data job;
- **MC** = MC only;
- **none** = card-level or inference-level only;
- **sel** = changes the selection (decide before Pass A).

Pass B regenerates everything, so "R" here says what is *wrong in the existing outputs*, not extra work. File:line refers to the current working tree.

### P0: must be in the code before Pass A

| # | issue (source) | where | proposed change | R |
|---|---|---|---|---|
| P0-1 | **preEE SingleMuon/DoubleMuon not recognised**: 6.0% duplicate data rows; masks fall back to the MC OR (review A1) | `analysis/selections/trigger.py:125` (`dataset_masks.get(dataset_name, all_combined_mask)`); `analysis/filesets/utils.py:81-86` | Map `SingleMuon` → `Muon` logic. Give `DoubleMuon` a zero mask, or drop it from the fileset. **Raise** on an unknown data PD; the MC path uses an explicit `is_mc` branch. | data 2022C |
| P0-2 | **c-tag one-hots never computed**, so the MVA saw zeros (A2) | `analysis/postprocess/inference.py:137-144` (missing → 0 with a warning); `:146-151` (NaN → 0) | `features/hww.py` computes them in the processor. Inference raises on any missing feature; NaN is allowed only for listed features. | none (inference) |
| P0-3 | **WH→WW xsec 0.0** for `WminusH_WtoLNu_Hto2Wto2L2Nu`, `WplusH_Wto2Q_Hto2Wto2L2Nu` (A3) | `2022postEE_nanov12.yaml:544,550`; `2022preEE:549,555`; `2023preBPix:566,572`; `2023postBPix:548,554`; silent at `scripts/combine/make_combine_inputs.py:85` | Set 0.004214 / 0.013708 pb from the YAML's own decomposition (review A3). Better: take them from the LHCHWG table with the user. `read_scale` raises on `xsec ≤ 0`; config validation as well. | none |
| P0-4 | **Already fixed in code, not yet reprocessed:** JER split-tag no-op; top-pT missing in shift trees; Type-1 sign/double counting; dead `CMS_res_e`; WH→ττ PDF blow-up (cap); central-signal LHE renorm; lhescale w4³ | `jerc.py`, `toppt.py`, `electron_ss.py`, `lhepdf.py`, `lhe_norm.py`, `lhescale.py` (see the log) | Commit them (the branch is uncommitted, with only `.bak` files) and tag the commit used for Pass A/B. | all |
| P0-5 | **Type-1 MET sums over all jets**, including lepton-dominated and EM jets; JER smearing of the lepton energy leaks into MC MET (A4) | `analysis/corrections/jerc.py:393` (nominal metinfo), `:442-455` (JES), `:496-509` (JER) | Restrict Σ(nano − new) to jets with new pT > 15, (chEmEF + neEmEF) < 0.9 and no overlap with a PF muon (or muon-subtracted pT). **Decide with the user** whether JER smearing propagates to MET at all. Validate against stored PuppiMET in data, where the difference should be ~0. | all |
| P0-6 | **Jets not re-sorted after JEC/JER**; `jet_pt/eta/phi` = first, not leading (B6) | `analysis/selections/object_selections.py:589-590` (sorted `jets` overwritten by `ak.pad_none(self.objects['jets'])`) | Sort `objects['jets']` once after selection and use it everywhere. | all |
| P0-7 | **Jet veto map not applied**; mandatory for 2022EE/2023BPix (B11) | `hww_combine_full.yaml:174-177` (no `jetveto`); the implementation exists in `correction_manager.py:67-75` and `jetvetomaps.py` | Enable it. Before enabling, check `jetvetomaps.py` against the Run 3 rule: the PF-muon overlap ΔR < 0.2 term is missing there, and the PU-ID term should be a no-op for Puppi. Apply to data and MC. | all |
| P0-8 | **Muon scale/smearing JSON pinned to the buggy 2025-08-14 version**; non-initialised RNG seed (B1) | `analysis/corrections/correctionlib_files.py:50-53` | Point to the 2026-04-28 release (all four Run 3 eras). Re-check that `filter_boundaries` (`muon_ss.py:191-210`, no correction outside 26–200 GeV, printed for ~45k muons/chunk **[L]**) still matches the official MuonScaRe code of that release. | MC |
| P0-9 | **Card builder silent fallback to nominal** for missing weight columns (B4/D) | `scripts/combine/make_combine_inputs.py:294-295`; the NaN fallback at `:301-303` is acceptable but must be counted and reported | Raise unless (process, syst) is in an explicit `not_applicable` list. Same in the new histogram card builder. | none |
| P0-10 | **Selection decisions needed**: no third-lepton veto (B5); mT cuts defined but not in `base` (B5) | YAML `event_selection` (`hww_combine_full.yaml:150-172`); `object_selections.py:519` `select_hww_ll_pair` | User decision. Recommended: veto any additional loose lepton (standard in HWW). The mT cut can stay off if the MVA uses mT. | sel |
| P0-11 | **ttH-MVA lepton WP adoption?** | §4 | User decision. If yes, it goes in now (§4.4). | sel |
| P0-12 | **Wγ overlap** with jet-binned W+jets, needed when WG enters training/card (C3) | `analysis/selections/event_selections.py:59` `get_stitching_mask` (unused) | Gen-prompt-photon (pT > 10) overlap removal on W+jets. It must exist in Pass A because WG enters the training. | MC (W, WG) |
| P0-13 | **Fail-loud sweep** | `toppt.py:72` (catch-all except), `partonshower.py:25` (bare except), `lhescale.py` (print on non-9 vectors), `event_selections.py:54` (skips missing MET-filter flags), `jerc.py:298` (`raise (f"...")` can never fire; precedence), `jerc.py:274` (`Path.exists` without `()`), missing `import warnings` in `jerc.py` | Raise everywhere. Keep an explicit allow-list (e.g. PSWeight absent in diboson → declared). | none by itself |
| P0-14 | **Completeness by events**, not jobs | `jobs_status.py` | Per-job check that processed entries == file entries (sum of chunk ranges vs the uproot entry count). Flag xrootd-truncated files. | none |

### P1: should be in before Pass B; cheap, or affects the result

| # | issue | where | change | R |
|---|---|---|---|---|
| P1-1 | NNLOPS applied to aMC@NLO `GluGluHto2Tau` (powheg splines) (B2) | `analysis/corrections/correction_manager.py:135` (`dataset.startswith("GluGluH")`) | Use the per-dataset generator from the YAML (`nnlops: powheg|mcatnlo|none`) and raise if it is missing for `GluGluH*`. | MC (1 sample) |
| P1-2 | Muon ID/ISO SF = 1 for 10 < pT < 15 (B7) | `analysis/corrections/muon.py:152,233` | Use the MUO low-pT (J/ψ) SFs, or raise the subleading-muon threshold to 15. Decide with the user. | MC |
| P1-3 | Electron ID SF evaluated with `eta`, not SC eta (B8) | `analysis/corrections/electron.py:158` (`get_id_weights_run3`) | `eta + deltaEtaSC`, as already done for the masks (`:150`). | MC |
| P1-4 | JEC compound evaluated with NanoAOD-corrected pT, not raw (B9; −0.13% at most) | `analysis/corrections/jerc.py:350` | Set `j["pt"] = j["pt_raw"]` before `get_corr_inputs`. | all |
| P1-5 | Lepton scale/resolution shifts do not propagate to MET (log item 6) | `update_met` imported but unused: `muon_ss.py:8`, `electron_ss.py:5` | Decide. Standard practice propagates them. Cheap. | MC |
| P1-6 | Diboson theory shapes are no-ops (no LHE weights); YAML comment wrong; **no gg→WW sample** (B3) | `hww_combine_full.yaml` (comment `no_scalevar`); filesets | Request or add powheg `WWto2L2Nu` + `GluGluToContinToWW` (DAS check first). Declare diboson `not_applicable` for LHE shapes. The sample lead time means starting now. | MC (new samples) |
| P1-7 | ZH double counting; ggH 13 TeV xsec (C1, C2) | era YAMLs (`ZH_ZtoAll_Hto2Wto2L2Nu` 0.021559; `GluGluHto2Wto2L2Nu` 1.0825) | User decision, against the LHCHWG 13.6 TeV table. | none |
| P1-8 | 2022postEE muon ISO SF 0.74–0.80 at low pT, barrel (C4) | official JSON | One question to MUO; no code change. | none |
| P1-perf | **Parquet writer 447× hotspot** (§1.2); correctionlib re-parsed 109×/chunk; jobs over-using CPU | `analysis/utils/parquet_writer.py:41-52`; correction modules call `CorrectionSet.from_file` per pass; `submit.py:105` (workers=2) vs request 1 CPU | (a) `ak.to_numpy` / `ak.fill_none(…, nan)` per column before `from_pydict`, with an explicit schema and a test that the output schema is identical; (b) module-level `lru_cache` on `from_file`; (c) `request_cpus = 2` (or workers=1); (d) partition TT into ≤ 30 chunks per job to cut tail latency (5 h jobs today); (e) gen/LHE columns only for negrw datasets. | none |
| P1-xrd | First-pass failures 25–34% (dead sites); no replica failover | `submit.py` / `partitions.json` | At job start, `xrdfs stat` the replica, with fallback to the global redirector and other Rucio replicas. Keep `xrootdtimeout=600`. | none |

### P2: card and design level (no reprocessing), before the final fit

| # | item | change |
|---|---|---|
| P2-1 | `scalevar_muR`, `_muF`, `_muR_muF` are three independent nuisances (over-counting) | Use muR + muF (or a 6-point envelope) and decorrelate per process. ggH scale ±24% from the NLO sample is far above the N3LO uncertainty: use the inclusive normalisation from the xsec table plus a shape-only variation. |
| P2-2 | Theory nuisances correlated across all processes | Decorrelate per process group (signal vs backgrounds). |
| P2-3 | `CMS_scale_j/res_j` shared between preEE and postEE | Decorrelate by era (different JEC campaigns). |
| P2-4 | JES = Total only | Consider regrouped sources if Run 3 recommendations exist. This is a processor change (more shift passes), so it is cheap only if decided before Pass B. |
| P2-5 | Plot band mirrors the fit | Drop tt normalisation theory from the band (rate_tt floats). |
| P2-6 | Flavour scheme | Planned 3FS/4FS c-hadron-pT **shape** systematic. Implement it as a weight variation in the processor (a lookup by gen c-hadron pT) so it lands in the histograms. Needs the weight map before Pass B, otherwise it is a card-level re-weight of a stored variable. |
| P2-7 | Signal xsec placeholders (central H+c/H+b) | XSDB values from the user. Normalisation only. |
| P2-8 | H+c central has no αS members | Keep `lhe_alphaS` = 1 for that sample, declared in `not_applicable`. |

The c-tag 2D SF is out of scope (expert check). Only its plumbing moves into the histogram variation axis.

---

## 6. Phased implementation plan

All effort numbers are estimates **[E]** for one person who knows the code.

### Phase 0: decisions (≤ 1 day, user)

Needed from the user:
- third-lepton veto;
- mT cut;
- Type-1 MET recipe and JER-in-MET;
- ttH-MVA adoption (and its SF provenance);
- NNLOPS scope;
- WH/ZH/ggH/signal cross sections;
- muon 10–15 GeV SF handling;
- gg→WW samples;
- WG in training;
- k for k-fold;
- whether Pass B keeps the slim ntuple safety net.

**Output:** the frozen list of P0 items.

### Phase 1: correctness and fail-loud in the current framework (3–5 days)

Scope: P0-1 … P0-14, P1-1 … P1-5, P1-perf (a, b, c, e), P1-xrd, and the config validator (§2.6).

**Validation:**
1. Unit tests:
   - trigger PD exclusivity on one file per PD: 0 duplicate (event, lepton-pT) rows across PDs in preEE (the review method);
   - `xsec > 0`;
   - feature hash;
   - writer schema identical before and after the numpy fix (byte-identical values on one shard).
2. Smoke runs, 1 file per sample type, inside the condor image (`runall/localtest_fix.sh` pattern, `validate_smoke.py`):
   - JER Up ≠ Down;
   - MET from re-correction on data ≈ stored PuppiMET (median |Δ| < 0.5 GeV);
   - leading-jet ordering 100%;
   - veto-map efficiency 4–7% (as measured in the review);
   - the processor wall time per chunk drops by about a third (target: 39 → ~24 s on the 20k-event profile above, `plan/profile_processor.py`).
3. A diff report of nominal yields per sample, before vs after, with each change attributed (e.g. preEE data −6%, WH→WW ×~2.2).

**Risk:** the Type-1 jet-selection change is the most delicate. Validate on data first, where it must reproduce stored PuppiMET.

### Phase 1b, only if ttH-MVA is adopted (2–3 days, plus SF provenance with Thomas)

Scope: §4.4 (vectorised features, ONNX `BRANCH_LT`, NanoAOD-input policy, WPs, SF port).

**Validation:**
- TMVA-exact test (≤ 1e-6 including tie leptons);
- per-era SF coverage;
- lepton efficiency and selected-yield comparison vs the cut-based ID on tt and DY.

### Phase 2: shared feature module, train mode and registry (3–4 days)

Scope: `features/hww.py` (26 features + one-hots), `ntuple_sink`, `mode: train`, `models/registry.py`, k-fold labels, ONNX export.

**Validation:**
1. Feature parity: on 2022postEE, `features.compute` reproduces today's parquet columns, plus `append_onehot.py` for the one-hots, to float precision on every event.
2. **Re-score parity:** the July v11 model scored through the registry or ONNX reproduces the stored `mva_score_*` when the one-hots are zeroed (exactly as the review reproduced them), and the review's restored-one-hot fractions (H+c SR 0.894, tt 0.160) when they are filled.

### Phase 3: Pass A, train-mode production (wall ~0.5 day [E])

All 4 eras, data + MC, nominal only.

**Validation:**
- data/MC on deduplicated preEE and on postEE; rerun the slope study;
- event-count completeness 100%;
- sumw records consistent with the Runs-tree `genEventSumw` (< 0.5%).

**Retrain** v12: 6 classes plus WG, k-fold, central signal, all eras.

**Gate:**
- ROC/AUC per class ≥ v11 on the same test folds;
- **stat-only expected limit** from Pass A with v12 vs v11 on the same events. Stat-only needs no shifts. Pre-fix Run 3 stat-only reference: 338.5.

### Phase 4: run mode (5–7 days, can overlap Phase 3)

Scope: inline scoring in `process_shift`; `hist_sink` with (dataset, channel, D, variation) plus negrw accumulators; shift datasets (per-dataset `object_shifts`, `shift_of`/`shift`); `build_cards.py` from histograms (ratio logic for alt samples, era renames, fail-loud, ROOT read-back); delete `hww_combine_full_ttsyst.yaml`.

**Validation, the key closure test:**
1. Take 2022preEE, the July v11 model, today's (pre-fix) code otherwise, and a subset of about 1 file per sample.
2. Produce templates (a) via the parquet route and (b) via run mode.
3. Require **identical templates bin by bin** (relative ≤ 1e-6) for every (channel, process, variation), including negrw and the tt alt-sample ratios, and an identical `AsymptoticLimits` result.
4. Then repeat with v12 on the Pass-A model.

This proves run mode is a pure refactor before it touches physics.

### Phase 5: Pass B, the only full production (wall 1–1.5 days [E])

Run mode, all 4 eras, with the slim ntuple safety net. Then cards, combineCards, limits.

**Validation:**
- completeness by events;
- every histogram readable;
- nuisance sanity scan: no Up == Down == nominal except the declared ones (catches the dead-nuisance class from 2026-10-01);
- per-change yield attribution vs the pre-fix reference: Run 3 full 691 / stat-only 338.5 / freeze-autoMCStats 616. Expected movements, in sign only:
  - JER shapes become non-trivial (+ syst);
  - WH→WW ×2.2;
  - preEE data −6%, which does not affect the Asimov limit;
  - MET changes from Type-1 / veto / sort;
  - new MVA.

### Phase 6: after the production (optional)

- Thomas's ttH-MVA, if deferred.
- Shift-aware recomputation: lepton shifts skip jet re-selection, JES/JER skip lepton work. About a 2× further speedup [E].
- Card-level P2 items.
- Remove the slim ntuples once final.
- EOS cleanup with the user (2dcat 179 GB, version files about 13%).
- coffea 2025 / awkward 2 migration only if it is maintained upstream for this group's tools. Not needed for this round.

### What must happen before vs after the next production

| before Pass A | before Pass B | after Pass B |
|---|---|---|
| Phase 0 decisions; all P0 code fixes; validator; writer fix; WG overlap; ttH-MVA (if adopted); feature module + train mode | v12 trained and frozen; run mode closure-validated; shift datasets; P1-1…5; P2-4 and P2-6 if they change the processor | card-level P2; P1-7/P1-8 numbers (normalisation only); cleanup; further speed work |

### Expected end state [E]

| metric | today | after |
|---|---|---|
| processor CPU per production | ~1,570 core-h (4 eras, logged incl. failures) | ~700–900 core-h. Writer fix −38% of processor time; run mode removes the remaining parquet I/O. |
| downstream per era | merge 27–65 + inference 8–23 + cards 12–43 min | histogram sum + cards: minutes |
| EOS per full production | 266 GB (full + ttsyst) | < 5 GB histograms (+ optional slim ntuple ≈ 60–90 GB, dropped once final) |
| silent fallbacks | ≥ 8 known paths | 0 by construction (validator + raises + nuisance scan) |

---

## 7. Measurement provenance (all in `/eos/user/c/cgupta/higgscharm/runall/plan/`)

| file | what |
|---|---|
| `eos_breakdown.sh`, `eos_versions.sh` | EOS size by component, version-file overhead |
| `condor_stats.py` | CPU-h, memory, return codes from condor logs |
| `count_events.sh` | input events from chunk ranges |
| `profile_processor.py`, `profile/` | per-stage processor profile + cProfile |
| `dump_microbench.py`, `colcensus.py` | writer hotspot; column/byte census |
| `mlp_cpu_bench.py`, `mlp_train_bench.py` | MLP inference / training throughput |
| `img_pkgs.py` | job-image package check (`img_order.py` import-order test, run from `/tmp`) |
| `tthmva/` | `bench_tthmva.py`, `tthmva_vec.py`, `bench_fast.py`, `tmva_ref_real.py`, `tie_which.py`, `cache_hit_real.py`; results in `tthmva/out/` (`bench_*.json`, `lep_*_fast.json`, `tmva_ref_*.txt`, fixed `*_BRANCH_LT.onnx`) |

## 8. Caveats

- **Expired grid proxy.** `x509up_u151861` showed `timeleft 0:00:00`. It was not renewed (renewal was requested from the parent). All NanoAOD reads in this session used `eoscms.cern.ch` (native `/eos/cms`, Kerberos). Pass A/B and any resubmission need a valid proxy.
- **Profile environment.** Profiles ran in the `b_hive` env (coffea 0.7.22), not in the condor image (0.7.30). Relative shares should transfer; absolute times on condor nodes differ (3.7 ms/event on condor [L] vs 1.9 ms/event locally [M]).
- **Production-scale numbers.** Lepton multiplicity (2.51/event) is from tt and overestimates other samples. The production-scale ttH-MVA numbers are therefore upper bounds for both approaches; the ratio between them is what matters.
- **August ONNX note is wrong for ties.** [[2026-08-12-lepton-mva-onnx-conversion]] states the ONNX conversion is exact. That holds only for inputs off the split values; `BRANCH_LEQ` must be `BRANCH_LT`. That note should be corrected.
