---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# Higgscharm + Combine Migration — Implementation Plan

Self-contained reference for the migration to "higgscharm yaml as the single
analysis knob" and integration of the combine pipeline into higgscharm.

Sibling docs:
- `docs/combine.md` — combine experiment log (v1 / v2 / v3 etc.)
- `docs/framework.md` — deeper architectural recommendations the parquet-
  metadata fix comes from
- `docs/combine_framework_plan.md` — original (less detailed) plan; this file
  supersedes it for execution

Repo paths used throughout:
- `B_HIVE      = /eos/home-c/cgupta/HToWW/b-hive`
- `HIGGSCHARM  = /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
- `EOS_OUT     = /eos/user/c/cgupta/higgscharm/outputs/hww_MVA/2022postEE`
- `CMSSW       = /afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4`

---

## 0. Context and goal

### What works today
- v1/v2/v3 combine fits run successfully from `b-hive/scripts/make_combine_*`.
  v3 gives `r_95 = 979` (Asimov median, 26.67 fb⁻¹), which scaled to 138 fb⁻¹
  matches AN-23-102's 1POI within 0.5 %.
- 4 result plots and a 21-nuisance impact plot are in
  `docs/plots/combine_*.png`.
- All combine inputs (datacard, workspace, fit ROOTs) live in
  `b-hive/combine_inputs/`.

### What's missing
1. **Object-shift systematics** (JES, JER, MET-unclust, lepton scales, HEM,
   prefire) — currently absent from the impact plot. Need per-variation
   parquets + re-inference.
2. **Self-normalising parquets** — today parquets carry raw weights without
   lumi×xsec/sumw scaling, forcing a workaround that reads a sidecar `.coffea`.
3. **Scripts in the wrong repo** — combine input/datacard/plot scripts live in
   b-hive but logically belong in higgscharm (the analysis framework).
4. **Single source of truth** — analysis configuration is scattered across
   workflow yaml + per-script hardcoded constants + b-hive configs. Should
   all live in one higgscharm workflow yaml.

### Goal
Get to a state where:
- One workflow yaml describes the entire analysis (selection, variations,
  combine channels, nuisances, discriminant).
- b-hive stays variation-agnostic (just trains and serves the model).
- Adding a systematic = edit the yaml, re-run; no script edits.
- The byte-identical v3 reproduction (`r_95 = 979`) is preserved through every
  intermediate commit.

---

## 1. Design philosophy

### 1.1 yaml is the single knob
Every choice that defines *what the analysis is* lives in
`higgscharm/analysis/workflows/<name>.yaml`. Python code is the engine that
consumes it. To change the analysis, edit yaml — not `.py`.

### 1.2 Single-responsibility scripts
Each Python entry point does exactly one thing:

| Script | One job |
|---|---|
| `runner.py` | NanoAOD → parquet (per sample, per variation) |
| `run_postprocess.py` | aggregate `.coffea` histograms, merge per-sample parquets, standard plots |
| `scripts/mva/prep_training_inputs.py` | split merged parquets into train/test + add labels + write filelists |
| `scripts/mva/run_inference.py` | load b-hive model + augment parquets with score columns |
| `scripts/combine/make_combine_inputs.py` | parquets → ROOT TH1s + datacard |
| `scripts/combine/run_combine.sh` | CMSSW shell wrapper: workspace + fits |
| `scripts/combine/make_combine_plots.py` | combine ROOT → PNG |

Postprocess stops being a Swiss-army knife.

### 1.3 Two flows with different rhythms

```
TRAINING FLOW (one-time)                     FIT FLOW (per analysis pass)
══════════════════════════                   ══════════════════════════════════════════════════════
1. Runner  --variation nominal               1. Runner  (all variations, parallel on Condor)
   --output_format parquet                      --output_format parquet
        │                                              │
        ▼                                              ▼
2. Postprocess  (merges parquets,            2. Postprocess  --variation <var>
   standard plots)                              (merges per variation)
        │                                              │
        ▼                                              ▼
3. scripts/mva/prep_training_inputs.py       3. scripts/mva/run_inference.py  (per variation)
        │                                              │
        ▼                                              ▼
4. b-hive: DatasetConstructorTask            4. scripts/combine/make_combine_inputs.py
        ↓                                              │
   b-hive: TrainingTask                                ▼
        ↓                                      5. scripts/combine/run_combine.sh   (CMSSW)
   model.pt  ───────────────────────┐                  │
                                    │                  ▼
                                    │          6. scripts/combine/make_combine_plots.py
                                    │
   (frozen model is consumed by FIT step 3)
```

- **Training**: rare, manual, runs on nominal only, produces frozen `model.pt`.
- **Fit**: every analysis pass, runs on every variation, produces fit results.

### 1.4 What stays in b-hive
- `tasks/training.py`, `tasks/dataset.py` — training infrastructure
- `utils/models/`, `utils/loss/`, `utils/weighting/`
- `config/HPlusCHToWW_*.yml` — training-time MVA configs
- `train_MVA.sh` — training entry point
- Output: `output/<version>/model.pt`

b-hive's `tasks/inference.py` (the `InferenceTask` law task) becomes
unused on the production combine path — `scripts/mva/run_inference.py` in
higgscharm uses the same logic in-process. Keep `InferenceTask` for
ad-hoc debug runs; don't depend on it for combine.

### 1.5 What moves to higgscharm
Everything currently in `b-hive/scripts/`:
- `make_combine_histograms_v11{,_v3,_v32,_lumi}.py`
- `make_datacard_v11{,_v3,_v32}.py`
- `make_combine_plots.py`
- `make_v3_impact_plot.py`
- `run_v3_impacts.sh`

Plus the entire `combine_inputs/` directory (datacard + workspace + fit ROOTs)
goes to `higgscharm/outputs/combine/`.

---

## 2. Final repository layout (after migration)

```
higgscharm/
├── runner.py
├── submit_condor.py
├── submit.py
├── run_postprocess.py                        # MVA flags removed (--mva, --infer)
├── analysis/
│   ├── workflows/
│   │   ├── hww_MVA.yaml                      # fit yaml: categories={base}, +variations:, +combine:
│   │   ├── hww_MVA_train.yaml                # training yaml: categories={train, test}
│   │   ├── hww_MVA_v32.yaml                  # alt fit config (κ-weighted)
│   │   └── ...
│   ├── corrections/
│   │   ├── correction_manager.py             # object_corrector_manager(variation=)
│   │   ├── jerc.py                           # extract shifted jets from CorrectedJetsFactory
│   │   ├── met.py                            # propagate jet shifts to MET, MET unclust
│   │   ├── muon_ss.py                        # mu_scale / mu_smear up/down
│   │   ├── electron_ss.py                    # ele_scale / ele_smear up/down
│   │   └── ...
│   ├── processors/
│   │   └── base.py                           # +variation= ctor arg, +schema metadata, output path includes <variation>/
│   ├── postprocess/
│   │   ├── postprocessor.py                  # keeps merging + std plots only
│   │   ├── utils.py                          # merge_parquets_by_sample stamps total sumw
│   │   ├── inference.py                      # MOVED OUT — used by scripts/mva/run_inference.py
│   │   └── ...
│   └── data/...
├── scripts/
│   ├── mva/
│   │   ├── prep_training_inputs.py           # NEW: split + label + filelist
│   │   └── run_inference.py                  # NEW: load model, write augmented parquets
│   ├── combine/
│   │   ├── make_combine_inputs.py            # MOVED from b-hive (parquet→ROOT+datacard)
│   │   ├── run_combine.sh                    # NEW: CMSSW wrapper, runs combine commands from yaml
│   │   ├── make_combine_plots.py             # MOVED from b-hive
│   │   ├── make_impact_plot.py               # MOVED from b-hive (was make_v3_impact_plot.py)
│   │   └── run_impacts.sh                    # MOVED from b-hive (was run_v3_impacts.sh)
│   └── inference/
│       └── run_all_variations.sh             # NEW (optional): loops variations:, calls scripts/mva/run_inference.py
└── outputs/
    └── combine/
        ├── v11_hplusc.root
        ├── v11_hplusc.txt
        ├── v11_hplusc.workspace.root
        ├── higgsCombine*.root
        └── v3_impacts/

b-hive/
├── tasks/
│   ├── training.py                           # unchanged
│   ├── dataset.py                            # unchanged
│   └── inference.py                          # unchanged but unused on prod combine path
├── utils/                                    # unchanged
├── config/HPlusCHToWW_kappa_hce.yml          # unchanged
├── train_MVA.sh                              # unchanged
├── output/<version>/model.pt                 # unchanged
└── scripts/                                  # emptied; everything moved to higgscharm
```

---

## 3. The single source-of-truth yaml

After migration, `analysis/workflows/hww_MVA.yaml` has these top-level blocks:

```yaml
datasets:           ...    # existing
object_selection:   ...    # existing
event_selection:    ...    # existing (categories: base)
corrections:        ...    # existing
histogram_config:   ...    # existing

mva:                                          # NEW: training preparation
  train_test_split:
    field: event                              # NanoAOD event id (present in all parquets)
    test_modulo: 10                           # ~10% test, ~90% train, deterministic
    test_remainder: 9
  labels:                                     # for prep_training_inputs.py
    process_groups:
      hplusc:   [HplusCharm_HtoWW]
      higgsbkg: [GluGluHto2Wto2L2Nu, VBFHto2Wto2L2Nu, ttHtoBB, ...]
      tt:       [TTto2L2Nu, TTtoLNu2Q, TTto4Q]
      st:       [...]
      diboson:  [WW, WZ, ZZ]
      vjets:    [DYto2L_2Jets_50, WtoLNu_2Jets, ...]

inference:                                    # NEW: how scripts/mva/run_inference.py finds the model
  framework: b-hive
  model_version: hww_multiclass_v32           # which trained model
  model_path: /eos/.../b-hive/output/hww_multiclass_v32/best_model.pt
  bhive_path: /eos/home-c/cgupta/HToWW/b-hive
  bhive_config: HPlusCHToWW_kappa_hce
  bhive_model_name: SimpleMLP_MultiClass
  batch_size: 4096

variations:                                   # NEW: which object-shift variations to produce
  - nominal
  - jes_Absolute
  - jes_BBEC1
  - jes_FlavorQCD
  - jer_barrel
  - jer_endcap1
  - met_unclust
  - mu_scale
  - mu_smear
  - ele_scale
  - ele_smear
  - hem2022
  - l1prefire
  # non-nominal entries are auto-expanded to <name>Up / <name>Down

combine:                                      # NEW: everything downstream of inference
  discriminant: P(hplusc)                     # or "log(P(hplusc)/P(tt))" for v3.2
  channels:
    SR_hplusc:   argmax_class == hplusc
    CR_higgsbkg: argmax_class == higgsbkg
    CR_tt:       argmax_class == tt
    CR_st:       argmax_class == st
    CR_diboson:  argmax_class == diboson
    CR_vjets:    argmax_class == vjets
  process_map:                                # combine process → list of higgscharm samples
    hplusc:   [HplusCharm_HtoWW]
    higgsbkg: [GluGluHto2Wto2L2Nu, VBFHto2Wto2L2Nu, ttHtoBB, HplusBottom_HtoWW, ...]
    tt:       [TTto2L2Nu, TTtoLNu2Q, TTto4Q]
    st:       [TWminusto2L2Nu, TbarWplusto2L2Nu, TQbartoLNu, TbarQtoLNu, ...]
    diboson:  [WW, WZ, ZZ]
    vjets:    [DYto2L_2Jets_50, WtoLNu_2Jets, ...]
  binning: {nbins: 20, start: 0.0, stop: 1.0}
  lnNs:                                       # rate-only nuisances
    lumi_13p6TeV:        {procs: all_mc,             value: 1.014}
    xsec_st:             {procs: [st],               value: 1.10}
    xsec_diboson:        {procs: [diboson],          value: 1.10}
    xsec_vjets:          {procs: [vjets],            value: 1.10}
    xsec_higgsbkg:       {procs: [higgsbkg],         value: 1.05}
    BR_HtoWW:            {procs: [hplusc, higgsbkg], value: 1.0153}
    xsec_hplusc_PDF:     {procs: [hplusc],           value: 1.027}
    xsec_hplusc_4FS_5FS: {procs: [hplusc],           value: 1.30}
    alphaS_PDF:          {procs: [hplusc],           value: 1.026}
  shapes:
    weight_based:                             # reuse nominal prediction; swap weight column
      - pileup
      - ps_isr
      - ps_fsr
      - scalevar_muR
      - scalevar_muF
      - scalevar_muR_muF
      - muon_id
      - muon_iso
      - electron_id
      - electron_reco_RecoBelow20
      - electron_reco_Reco20to75
      - electron_reco_RecoAbove75
    object_based:                             # need re-inference; names match variations:
      - jes_Absolute
      - jes_BBEC1
      - jer_barrel
      - met_unclust
      - mu_scale
      - ele_scale
  autoMCStats: 10
  run:
    asymptotic_limits: {asimov: true, blind: true}
    multidimfit_scan:  {algo: grid, range_r: [-5, 5], points: 41}
    impacts:                                  # manual (CombineHarvester not installed)
      method: freeze_per_nuisance
      nuisances: auto                         # = all from datacard
```

To try a different combine configuration (v3.2, v32, etc.), copy the yaml and
edit. One file = one full analysis pass.

---

## 4. Commit plan

Six commits, in order. Each is reviewable on its own; each preserves
v3 reproduction (`r_95 = 979`) at its checkpoint.

| # | Title | Repo | Scope |
|---|---|---|---|
| **0a** | Extract MVA prep + add train/test split | higgscharm | move `--mva` / `--infer` out of postprocess |
| **0b** | Self-normalising parquets | higgscharm | stamp sumw/xsec/era into parquet schema metadata |
| **1** | Variation scaffolding | higgscharm | `variations:` yaml block + `--variation` plumbing |
| **2** | JES/JER injection | higgscharm | extract shifted jets from `CorrectedJetsFactory` |
| **3** | Relocate combine scripts | b-hive → higgscharm | move 10 scripts, generalise paths via yaml |
| **4** | End-to-end smoke test | both | one shifted variation through to a fit + impact bar |

---

### Commit 0a — Extract MVA prep from postprocess + add train/test split

**Goal**: split `run_postprocess.py` into single-responsibility pieces.
- postprocess: aggregate `.coffea`, merge parquets, standard plots only
- `scripts/mva/prep_training_inputs.py` (new): split + label + filelist
- `scripts/mva/run_inference.py` (new): inference into augmented parquets

**Files to edit**

- `higgscharm/run_postprocess.py`
  - Drop `--mva` and `--infer` argparse flags (and their validation)
  - Drop the `args.mva` and `args.infer` branches
  - Keep merge call, keep standard plotting
- `higgscharm/analysis/postprocess/utils.py`
  - Move `add_mva_labels` and `generate_filelist` / `generate_all_filelists`
    → `scripts/mva/prep_training_inputs.py`
  - Keep `merge_parquets`, `merge_parquets_by_sample`
- `higgscharm/analysis/postprocess/postprocessor.py`
  - Remove the `add_mva_labels_flag` parameter from `save_histograms_by_sample`
    and `save_histograms_by_process`
- `higgscharm/analysis/postprocess/inference.py`
  - Keep the module but stop calling it from `run_postprocess.py`
  - Becomes a library used by `scripts/mva/run_inference.py`

**Files to create**

- `higgscharm/scripts/mva/prep_training_inputs.py` (~150 lines)
  - args: `--workflow`, `--year`
  - reads `workflow_config.mva.train_test_split` and
    `workflow_config.mva.labels.process_groups`
  - for each merged sample parquet:
    - read events
    - compute `is_test = (df[field] % test_modulo) == test_remainder`
    - add one-hot label columns from `process_groups`
    - write `<sample>_train.parquet` and `<sample>_test.parquet`
  - generate `filelists/train.txt`, `filelists/test.txt`
- `higgscharm/scripts/mva/run_inference.py` (~120 lines, reuses
  `analysis/postprocess/inference.py:run_inference`)
  - args: `--workflow`, `--year`, optional `--variation`
  - reads `workflow_config.inference.{model_path, bhive_path, bhive_config, ...}`
  - if `--variation` is set, runs once on that variation only; otherwise loops
    over `workflow_config.variations`
  - calls `run_inference()` for each variation, writing to
    `<output_dir>/<variation>/mva/<sample>.parquet`

**Yaml additions** — `hww_MVA.yaml` (and `hww_MVA_train.yaml`):

```yaml
mva:
  train_test_split: {field: event, test_modulo: 10, test_remainder: 9}
  labels:
    process_groups: {hplusc: [HplusCharm_HtoWW], higgsbkg: [...], ...}
inference:
  framework: b-hive
  model_version: hww_multiclass_v32
  model_path: /eos/.../b-hive/output/hww_multiclass_v32/best_model.pt
  bhive_path: /eos/home-c/cgupta/HToWW/b-hive
  bhive_config: HPlusCHToWW_kappa_hce
  bhive_model_name: SimpleMLP_MultiClass
  batch_size: 4096
```

**Verification**

1. Run old: `python run_postprocess.py --workflow hww_MVA --year 2022postEE --mva`
   on a fresh clone of pre-Commit-0a. Save outputs.
2. Run new:
   ```
   python run_postprocess.py            --workflow hww_MVA --year 2022postEE
   python scripts/mva/prep_training_inputs.py --workflow hww_MVA --year 2022postEE
   ```
3. Diff label columns + filelist contents. Should be identical except for
   the new `_train`/`_test` split.
4. Run `scripts/mva/run_inference.py --workflow hww_MVA --year 2022postEE --variation nominal`
   and confirm `<output_dir>/nominal/mva/*.parquet` exists with score columns.

**Risk**: low. Pure refactor. No physics change.

---

### Commit 0b — Self-normalising parquets

**Goal**: make parquets carry sumw + xsec + era in pyarrow schema metadata so
no consumer needs to look up `luminosity.yaml` or the fileset yaml.

References: `docs/framework.md` § 1–2.

**Scope note (decided during 0a/0b execution)**: the `.coffea` envelope
change originally bundled here is **deferred to Commit 3** because changing
`.coffea` shape would break the b-hive combine scripts
(`make_combine_histograms_v11_lumi.py`'s `sample_nominal_coffea_integral`)
between 0b and 3 and violate the v3 reproduction invariant. The relocated
Commit-3 scripts read parquet metadata directly, making the `.coffea`
sidecar unnecessary altogether — the envelope migration becomes a no-op
once Commit 3 lands.

**Files to edit**

- `higgscharm/analysis/processors/base.py` (around line 190-219, the parquet
  branch of `BaseProcessor.process`)
  - After building `variables_map`, before `dump_pa_table`:
    ```python
    table = ...                                # pyarrow Table being written
    dataset_xsec = self.dataset_config[dataset].get("xsec")
    dataset_era  = self.dataset_config[dataset].get("era", "")
    table = table.replace_schema_metadata({
        **(table.schema.metadata or {}),
        b"sumw": str(sumw).encode(),
        b"xsec": str(dataset_xsec).encode() if dataset_xsec else b"None",
        b"era":  dataset_era.encode(),
    })
    ```
  - May need to refactor `dump_pa_table` to accept extra schema metadata, or
    inline the write call here.
- `higgscharm/analysis/postprocess/utils.py`
  - `merge_parquets_by_sample` (and `merge_parquets`): when consolidating per-
    sample partitions, sum the `sumw` from each input parquet's schema metadata
    and stamp the **total sumw** onto the merged parquet's schema. xsec and era
    pass through (they're the same across partitions of one sample).

**Files to edit (consumer)**

- `higgscharm/analysis/postprocess/postprocessor.py`
  - `save_histograms_by_sample` (~line 137-144) — change save shape:
    ```python
    save({
        "histograms": scaled_histograms,
        "metadata":   {"sumw": metadata["sumw"], "lumi": luminosities[year],
                       "xsec": dataset_config[sample].get("xsec"),
                       "lumi_weight": weight,
                       "era":  dataset_config[sample]["era"]},
    }, Path(output_dir) / f"{sample}.coffea")
    ```
  - `save_cutflows` (utils.py:215-233) — keep unscaled cutflow alongside scaled.

- `higgscharm/analysis/postprocess/utils.py:load_processed_histograms`
  (~line 315-323)
  - Add backward-compat shim: if loaded file is a dict with `"histograms"` key,
    return `data["histograms"]`; else return `data` (old shape).

**Files that get simpler later** (Commit 3 will use this):
- The relocated `make_combine_inputs.py` will read `xsec`, `era`, `sumw`
  directly from each parquet's schema and compute
  `scale = LUMI[era] * xsec / sumw`. No more `.coffea` sidecar reads.

**Yaml additions**: none. Pure code change.

**Verification**

1. Re-run the runner on one sample (e.g. `HplusCharm_HtoWW`) with
   `--output_format parquet`.
2. ```python
   import pyarrow.parquet as pq
   t = pq.read_table("...HplusCharm_HtoWW.../0.parquet")
   print(dict(t.schema.metadata))
   # expect: {b"sumw": b"...", b"xsec": b"0.0022141", b"era": b"signal"}
   ```
3. Run `run_postprocess.py` end-to-end on 2022postEE. Confirm:
   - `<sample>.coffea` now loads as `{"histograms": ..., "metadata": ...}`
   - Existing plots still produced
   - Merged per-sample parquet carries the **total** sumw in its schema
     (sum of per-chunk sumw)

**Risk**: medium. The `.coffea` shape change is backward-incompatible without
the shim — must land the shim atomically.

---

### Commit 1 — Variation scaffolding

**Goal**: add the `--variation` rail end-to-end. Nominal output is bit-
identical to pre-Commit-1; non-nominal variations are wired but
**inactive** (just print a warning, fall back to nominal physics for now —
real physics shifts come in Commit 2).

**Files to edit**

- `higgscharm/analysis/workflows/hww_MVA.yaml`
  - Add top-level `variations:` block:
    ```yaml
    variations:
      - nominal
      - jes_Absolute
      - jer_barrel
      - met_unclust
      - mu_scale
      - ele_scale
    ```
  - Non-nominal entries are expanded to `<name>Up` / `<name>Down` by code.
- `higgscharm/analysis/workflows/config/__init__.py`
  (WorkflowConfigBuilder)
  - Expose `workflow_config.variations` (list of expanded variation strings).
- `higgscharm/runner.py`
  - Add `--variation` flag (str, default `"nominal"`).
  - If not provided, default behaviour iterates over `variations:` from yaml,
    submitting one job-set per variation.
  - Pass through to `submit_condor.py`.
- `higgscharm/submit_condor.py`
  - Accept `--variation`, forward into `arguments.json` and to `submit.py`.
- `higgscharm/submit.py`
  - Accept `--variation`, pass to `BaseProcessor` constructor.
- `higgscharm/analysis/processors/base.py`
  - `BaseProcessor.__init__` takes `variation: str = "nominal"`.
  - Store on self.
  - In `process()`:
    - Pass `variation=self.variation` to `object_corrector_manager`.
    - Output path: change subdirs from
      `[self.workflow, self.year, dataset, category]` to
      `[self.workflow, self.year, self.variation, dataset, category]`.
- `higgscharm/analysis/corrections/correction_manager.py`
  - `object_corrector_manager(events, year, dataset, workflow_config, variation="nominal")`
  - For now, if `variation != "nominal"`: log a one-line warning, then proceed
    with nominal physics. Forward `variation=` to apply_jerc_corrections etc.
    (the corrections themselves are no-ops on `variation` until Commit 2).
- `higgscharm/analysis/corrections/jerc.py`, `met.py`, `muon_ss.py`, `electron_ss.py`
  - Add `variation="nominal"` parameter to each public `apply_*` function.
  - Body unchanged — just acceptance.
- `higgscharm/run_postprocess.py`
  - Add `--variation` flag (default `"nominal"`).
  - If not provided, loop over `workflow_config.variations` and process each.
  - Output dir becomes `outputs/<workflow>/<year>/<variation>/`.

**Verification**

1. `python runner.py --workflow hww_MVA --year 2022postEE` (no `--variation`)
   should iterate variations in yaml. Confirm condor submission per variation.
2. Run one nominal job. Check output ends up in
   `<output_dir>/nominal/<dataset>/...`.
3. Compute md5 of one nominal parquet pre-Commit-1 vs post-Commit-1.
   **Must be identical** (modulo path).
4. Run with `--variation jes_AbsoluteUp` and confirm:
   - Output written to `<output_dir>/jes_AbsoluteUp/<dataset>/...`
   - Warning logged: `"variation jes_AbsoluteUp not yet implemented in apply_jerc_corrections, using nominal"`
   - Parquet content identical to nominal (Commit 2 will fix this)

**Risk**: low. Additive scaffolding only.

---

### Commit 2 — JES / JER / lepton-scale shift injection

**Goal**: make non-nominal variations carry real physics. Extract systematic-
shifted jets from the existing `CorrectedJetsFactory` (the `# TO DO:
SYSTEMATICS` comment at `jerc.py:227`), propagate to MET, similarly for
muon_ss / electron_ss.

**Files to edit**

- `higgscharm/analysis/corrections/jerc.py`
  - `apply_jerc_coffea(events, year, dataset, variation="nominal")`:
    - After `events["Jet"] = jec_factory.build(...)`, if `variation` is one of
      the JES sources, swap in the shifted jets:
      ```python
      if variation.startswith("jes_"):
          src = variation.removeprefix("jes_").rstrip("UpDown")
          side = "up" if variation.endswith("Up") else "down"
          shifted = events.Jet[f"JES_{src}"][side]   # CorrectedJetsFactory output
          events["Jet", "pt"]   = shifted.pt
          events["Jet", "mass"] = shifted.mass
      elif variation.startswith("jer_"):
          # JER barrel/endcap1/endcap2 split (regrouped)
          ...
      ```
    - Re-call `update_met(events, year)` after the swap so MET is propagated.
  - `apply_jerc_correctionlib(events, year, dataset, variation="nominal")`:
    similar logic, using the correctionlib JER smear systematic outputs.
- `higgscharm/analysis/corrections/met.py`
  - Add MET-unclust variation: `events["PuppiMET", "pt"] = events.PuppiMET.pt + signed * events.PuppiMET.MetUnclustEnUpDeltaX` etc.
- `higgscharm/analysis/corrections/muon_ss.py`
  - Already has `variation="nominal"` knob (per correction_manager.py:38).
    Extend to handle `mu_scaleUp/Down`, `mu_smearUp/Down`.
- `higgscharm/analysis/corrections/electron_ss.py`
  - Same pattern.

**Yaml**: `variations:` block from Commit 1 already lists what's needed. No
additions.

**Verification**

1. Run for `--variation jes_AbsoluteUp` on a single sample (e.g.
   `TTto2L2Nu`, ~1 file).
2. Compare against nominal:
   ```python
   import pyarrow.parquet as pq, numpy as np
   nom = pq.read_table(".../nominal/TTto2L2Nu/0.parquet").to_pandas()
   shi = pq.read_table(".../jes_AbsoluteUp/TTto2L2Nu/0.parquet").to_pandas()
   # weights should be identical:
   assert np.allclose(nom.weight_nominal, shi.weight_nominal)
   # jet pt-derived columns should differ:
   diff = (nom.cjet_cand_pt - shi.cjet_cand_pt).abs()
   print(diff.describe())  # expect ~1-3% mean shift
   ```
3. Sanity check MET: `met_pt` should also shift (Type-I propagation).

**Risk**: medium. CorrectedJetsFactory output schema can be finicky; expect
one or two iteration cycles. Reference:
https://github.com/scikit-hep/coffea/blob/master/src/coffea/jetmet_tools/CorrectedJetsFactory.py

---

### Commit 3 — Relocate combine scripts (b-hive → higgscharm)

**Goal**: move the 10 combine scripts from b-hive to
`higgscharm/scripts/combine/`. Generalise hardcoded paths/process maps to
read from `workflow_config.combine`. Reproduce v3 `r_95 = 979` from the new
location (bit-identical).

**Files to move** (b-hive → higgscharm):

| Old path | New path |
|---|---|
| `b-hive/scripts/make_combine_histograms_v11.py` | `higgscharm/scripts/combine/make_combine_inputs.py` ¹ |
| `b-hive/scripts/make_combine_histograms_v11_v3.py` | (folded into the above, switch via yaml) |
| `b-hive/scripts/make_combine_histograms_v11_v32.py` | (folded, switch via yaml) |
| `b-hive/scripts/make_combine_histograms_v11_lumi.py` | (folded; `lumi:` knob in yaml) |
| `b-hive/scripts/make_datacard_v11.py` | `higgscharm/scripts/combine/make_datacard.py` ² |
| `b-hive/scripts/make_datacard_v11_v3.py` | (folded) |
| `b-hive/scripts/make_datacard_v11_v32.py` | (folded) |
| `b-hive/scripts/make_combine_plots.py` | `higgscharm/scripts/combine/make_combine_plots.py` |
| `b-hive/scripts/make_v3_impact_plot.py` | `higgscharm/scripts/combine/make_impact_plot.py` |
| `b-hive/scripts/run_v3_impacts.sh` | `higgscharm/scripts/combine/run_impacts.sh` |
| `b-hive/combine_inputs/` (all root + datacard) | `higgscharm/outputs/combine/` |

¹ The 4 histogram scripts collapse to one — channelisation / discriminant /
lumi all become yaml knobs (`combine.channels`, `combine.discriminant`,
`combine.lumi_scale`).

² Same for datacard generators — the lnN list, the rateParams, the autoMCStats
threshold all live in `workflow_config.combine`.

**Files to create**

- `higgscharm/scripts/combine/run_combine.sh` — CMSSW wrapper:
  ```bash
  #!/usr/bin/env bash
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  cd $CMSSW_BASE/src && eval $(scram runtime -sh)
  cd $HIGGSCHARM/outputs/combine
  python3 $HIGGSCHARM/scripts/combine/drive_combine.py --workflow "$1"
  ```
- `higgscharm/scripts/combine/drive_combine.py`
  - reads `workflow_config.combine.run.*`
  - runs `text2workspace.py`, `combine -M AsymptoticLimits`, `combine -M
    MultiDimFit --algo grid`, and the manual impact loop

**Key code changes** (taking advantage of Commit 0b):

In `make_combine_inputs.py`, the per-sample lumi scale becomes:
```python
import pyarrow.parquet as pq
t      = pq.read_table(parquet_path)
meta   = t.schema.metadata
sumw   = float(meta[b"sumw"])
xsec   = float(meta[b"xsec"])
lumi   = LUMI_BY_ERA[meta[b"era"].decode()]
scale  = lumi * xsec / sumw
df     = t.to_pandas()
weight = df["weight_nominal"] * scale
```
No coffea sidecar lookup. The `sample_nominal_coffea_integral` helper from
`make_combine_histograms_v11_lumi.py:198` disappears entirely (the whole
"derive scale from coffea integral ratio" workaround is gone — Commit 0b
already stamps the canonical sumw/xsec/era into each parquet, so the
relocated scripts read the truth directly).

**Cleanup checklist for the four v11 histogram-script collapses**:
- Drop `sample_nominal_coffea_integral` and any `<sample>.coffea` reads.
- Drop the `coffea_load` import.
- Drop the "full_w_nom_sum / coffea_nom" two-pass scale derivation in
  `process_sample` (lumi script lines ~270-280). Replace with direct
  `scale = lumi * xsec / sumw` from parquet metadata.
- The `coffea.exists()` precondition on sample loops (lines ~180-185) is
  no longer needed.

**Yaml additions**: `combine:` block (see §3) becomes the source of truth for
all hardcoded constants from the old scripts.

**Verification — the byte-for-byte test**

This is the most important test in the entire migration:

```bash
# Pre-Commit-3 (b-hive scripts)
combine -M AsymptoticLimits b-hive/combine_inputs/v11_hplusc_v3.workspace.root \
        -t -1 --run blind > old.txt

# Post-Commit-3 (relocated higgscharm scripts)
python higgscharm/scripts/combine/make_combine_inputs.py --workflow hww_MVA
bash   higgscharm/scripts/combine/run_combine.sh         --workflow hww_MVA
diff old.txt higgscharm/outputs/combine/asymptotic_limits.log
# expect identical r_95 numbers (median 979)
```

If the diff is non-empty, the refactor is wrong. Back it out and try again.

**Risk**: medium-high. This is the most code being touched. The byte-identical
test is the safety net — don't merge without it.

---

### Commit 4 — End-to-end smoke test with one shifted variation

**Goal**: prove the whole loop works. Take one object-shift variation
(`jes_AbsoluteUp/Down`) all the way from NanoAOD to a new bar on the impact
plot. If the magnitude is in the ballpark of AN-23-102 Fig. 53, the
pipeline is proven; remaining variations are mechanical scaling.

**Execution**

1. `variations:` yaml block already lists `jes_Absolute` (from Commit 1).
   `combine.shapes.object_based` lists `jes_Absolute` (from Commit 3).
2. Run the full fit flow:
   ```bash
   python runner.py                       --workflow hww_MVA --year 2022postEE
   python run_postprocess.py              --workflow hww_MVA --year 2022postEE
   python scripts/mva/run_inference.py    --workflow hww_MVA --year 2022postEE
   python scripts/combine/make_combine_inputs.py --workflow hww_MVA
   bash   scripts/combine/run_combine.sh         --workflow hww_MVA
   python scripts/combine/make_combine_plots.py  --workflow hww_MVA
   ```
3. Check the impact plot now includes a `jes_Absolute` bar.
4. Compare its magnitude to AN-23-102 Fig. 53 ranking. Expected: in the top-5
   nuisances, Δr_95 in the range ±30–50.

**Acceptance criteria**

- jes_Absolute appears on the impact plot.
- v3 nominal `r_95` (median) is **unchanged** (still 979) after adding the
  shape line — adding a shape syst should not move the central limit much
  in a flat-NLL fit.
- The `jes_AbsoluteUp/Down` parquets carry the expected ~3% shift in cjet pt
  vs nominal.

**Risk**: low if Commits 1–3 verified. This is the integration test.

---

## 5. Day-to-day commands after migration

### Training (rare, manual)

```bash
# 1. Make sure nominal parquets are fresh (uses hww_MVA_train.yaml for train/test categories)
python runner.py            --workflow hww_MVA_train --year 2022postEE --variation nominal

# 2. Aggregate + merge
python run_postprocess.py   --workflow hww_MVA_train --year 2022postEE

# 3. Split, label, filelist
python scripts/mva/prep_training_inputs.py --workflow hww_MVA_train --year 2022postEE

# 4. Train in b-hive (DatasetConstructor + Training)
cd $B_HIVE && ./train_MVA.sh --version hww_multiclass_v33

# 5. Update hww_MVA.yaml: inference.model_version = hww_multiclass_v33
```

### Fit (every analysis pass)

```bash
# 1. Run all variations (iterates from variations: block, parallel on Condor)
python runner.py            --workflow hww_MVA --year 2022postEE

# 2. Merge per variation
python run_postprocess.py   --workflow hww_MVA --year 2022postEE

# 3. Inference per variation
python scripts/mva/run_inference.py --workflow hww_MVA --year 2022postEE

# 4. Build combine inputs (TH1Ds + datacard from all <var>/mva/*.parquet)
python scripts/combine/make_combine_inputs.py --workflow hww_MVA

# 5. Run combine (CMSSW)
bash   scripts/combine/run_combine.sh         --workflow hww_MVA

# 6. Plots
python scripts/combine/make_combine_plots.py  --workflow hww_MVA
python scripts/combine/make_impact_plot.py    --workflow hww_MVA
```

Six commands. All driven by one yaml. Add a systematic = edit the yaml's
`variations:` and `combine.shapes.object_based:` blocks, re-run from step 1.

---

## 6. Open questions to decide before scale-out

These are deferred to after Commit 4. List them somewhere visible (issue
tracker or `docs/combine.md` § open questions).

1. **JES granularity** — Full 27-source, regrouped 11, or 5-source reduced set?
   Affects total variation count by ~5×. Recommendation: start with regrouped
   11 to match AN-23-102, scale up later if needed.
2. **Storage budget** — Estimate per-variation parquet size. With MVA-input
   columns only (~17 floats × ~event count), each shifted directory is
   ~30–40 % of nominal. 11 JES + 3 JER + 4 lepton/MET = ~18 shifted sets ×
   2 sides = ~36 dirs. Confirm eos quota.
3. **Combine fit on full event set vs test-only** — train events contribute
   to the fit today (option B from earlier discussion). For Asimov sensitivity
   this is fine. For unblinded data fits it's irrelevant (data wasn't
   trained on).
4. **Data parquets** — currently parquet outputs are MC-only. If data
   parquets are added later (for control-region fits with real data), the
   self-normalising metadata change in Commit 0b needs to handle
   `era == "data"` (no xsec scaling).
5. **CombineHarvester** — manual impact loop will be replaced by
   `combineTool.py -M Impacts` if CH gets installed. Until then the loop in
   `run_impacts.sh` is the workaround.
6. **Hardware** — inference is currently CPU-friendly (small MLP). If a
   larger model is needed in v33+, add GPU support to
   `scripts/mva/run_inference.py` (batch size + cuda device, both in
   `inference:` yaml block).

---

## 7. Cross-references

- `docs/framework.md` § 1, § 2 — origin of the parquet self-normalisation fix
  (Commit 0b)
- `docs/combine_framework_plan.md` — original less-detailed plan, superseded
  by this file but kept for context (esp. §5 "per-variation files beats
  per-event shifted columns" trade-off discussion)
- `docs/combine.md` § Experiment log — v1 / v2 / v3 results, what the migration
  needs to reproduce
- `b-hive/scripts/make_combine_histograms_v11_v3.py` — current source of
  truth for v3 channelisation; the relocated `make_combine_inputs.py`
  must reproduce its output bit-identically
- `b-hive/scripts/run_v3_impacts.sh` — current source of truth for the
  manual impact loop
- AN-23-102 — comparison benchmark for impact magnitudes (Fig. 53 ranking
  for 1POI)

---

## 8. Quick-start for a fresh session

If picking this up cold in a new session:

1. Read this file end-to-end (~15 min).
2. Read `docs/framework.md` § 1, § 2 (Commit 0b context).
3. Pick the next commit in §4 sequence (start with 0a if nothing done yet).
4. Within that commit, read the "Files to edit" + "Files to create" list,
   make the changes, run "Verification".
5. Commit with subject `migration(<NN>): <title>` where NN is the commit
   number from §4 (e.g. `migration(0a): extract MVA prep + train/test split`).
6. Move to the next commit. Each is self-contained and can be reviewed
   independently.

The reproduction invariant — **v3 `r_95 = 979` (Asimov median)** — must
hold at every commit checkpoint until Commit 4 (where new shape lines
may shift it slightly).
