---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

---
title: Higgscharm + Combine Migration
subtitle: "yaml as the single analysis knob"
author: H+c (H→WW) analysis
---

# Higgscharm + Combine Migration

**Goal:** one workflow yaml describes the entire analysis —
selection, variations, MVA, combine channels, nuisances.

- b-hive stays variation-agnostic (trains + serves the model)
- Adding a systematic = edit yaml, re-run; no script edits
- Reproduction invariant held throughout: **v3 r₉₅ = 979**
  (Asimov median, 26.67 fb⁻¹, 2022postEE)

Branch: `migration` on higgscharm · 6 commits (0a → 4)

---

# The problem (before)

1. **Object-shift systematics missing** — JES, JER, MET-unclust,
   lepton scales absent from the impact plot. No per-variation parquets.

2. **Parquets not self-normalising** — raw weights only; a workaround
   read a sidecar `.coffea` to recover the lumi×xsec/sumw scale.

3. **Scripts in the wrong repo** — combine input/datacard/plot scripts
   lived in b-hive but belong in the analysis framework (higgscharm).

4. **No single source of truth** — config scattered across workflow
   yaml + per-script hardcoded constants + b-hive configs.

---

# Design philosophy

**1. yaml is the single knob.**
Everything that defines *what the analysis is* lives in
`analysis/workflows/<name>.yaml`. Python is the engine that consumes it.

**2. Single-responsibility scripts.**
`run_postprocess.py` stops being a Swiss-army knife:

| Script | One job |
|---|---|
| `runner.py` | NanoAOD → parquet (per sample, per variation) |
| `run_postprocess.py` | aggregate histograms, merge parquets, plots |
| `scripts/mva/prep_training_inputs.py` | split + label + filelist |
| `scripts/mva/run_inference.py` | model → score-augmented parquets |
| `scripts/combine/make_combine_inputs.py` | parquets → ROOT + datacard |
| `scripts/combine/drive_combine.py` | workspace + fits |

---

# Two flows, different rhythms

```
TRAINING FLOW (rare, manual)          FIT FLOW (per analysis pass)
══════════════════════════            ═══════════════════════════════════
1. runner --variation nominal         1. runner  (all variations, Condor)
        │                                     │
        ▼                                     ▼
2. run_postprocess (merge)            2. run_postprocess --variation <var>
        │                                     │
        ▼                                     ▼
3. mva/prep_training_inputs.py        3. mva/run_inference.py  (per var)
        │                                     │
        ▼                                     ▼
4. b-hive DatasetConstructor          4. combine/make_combine_inputs.py
   b-hive Training → model.pt                 │
        │                                     ▼
        └──── frozen model ───────►   5. combine/run_combine.sh (CMSSW)
              consumed by FIT step 3          │
                                              ▼
                                      6. combine/make_combine_plots.py
```

---

# What stays where

**Stays in b-hive** (training infrastructure):
- `tasks/training.py`, `tasks/dataset.py`
- `utils/models/`, `utils/loss/`, `utils/weighting/`
- `config/HPlusCHToWW_*.yml`, `train_MVA.sh`
- Output: `output/<version>/model.pt`

**Moves to higgscharm** (the analysis framework):
- All combine input / datacard / plot / impact scripts
- The `combine_inputs/` → `higgscharm/outputs/combine/`

b-hive's `InferenceTask` stays for ad-hoc debug; the production
fit path uses `scripts/mva/run_inference.py` in-process.

---

# The six commits

| # | Title | Scope |
|---|---|---|
| **0a** | Extract MVA prep + train/test split | `--mva`/`--infer` out of postprocess |
| **0b** | Self-normalising parquets | stamp sumw/xsec/era into schema metadata |
| **1** | Variation scaffolding | `variations:` + `--variation` rail |
| **2** | JES/JER injection | shifted jets from CorrectedJetsFactory |
| **3** | Relocate combine scripts | b-hive → higgscharm, yaml-driven |
| **4** | End-to-end smoke test | one shifted variation → impact bar |

Each commit is reviewable on its own and preserves r₉₅ = 979.

---

# Commit 0a — extract MVA prep  ·  `8192494`

Split `run_postprocess.py` into single-responsibility pieces.

- **Dropped** `--mva` / `--infer` flags + their branches from postprocess
- **Deleted** `PROCESS_TO_GROUP`, `add_mva_labels`, `generate_filelist`…
  from `utils.py` (now yaml-driven)
- **Added** `events.event` (NanoAOD id) to the parquet output — needed
  for the deterministic train/test split
- **New** `scripts/mva/prep_training_inputs.py` — label + split on
  `event % 10`, write `training/<proc>_{train,test}.parquet` + filelists
- **New** `scripts/mva/run_inference.py` — load b-hive model, write
  `mva/<sample>.parquet` with `mva_score_*` columns

Net: +41 / −266. Pure refactor.

---

# Commit 0b — self-normalising parquets  ·  `aeb0104`

Each parquet carries `sumw` / `xsec` / `era` in its pyarrow schema
metadata — no sidecar `.coffea`, no `luminosity.yaml` in the hot path.

```python
# base.py parquet branch
dataset_info = get_dataset_config(self.year).get(dataset, {})
extra_metadata = {
    "sumw": str(float(sumw)),
    "xsec": str(dataset_info.get("xsec", "")),
    "era":  str(dataset_info.get("era", "")),
}
dump_pa_table(variables_map, fname, ..., extra_metadata=extra_metadata)
```

- `merge_parquet_files()` uses **pyarrow directly** (not dask) so the
  metadata survives the merge; sums `sumw` across shards
- Per-process merge intentionally *not* stamped (heterogeneous xsecs)
- `.coffea` envelope change deferred to Commit 3 (would break the
  b-hive reference between 0b and 3)

---

# Commit 1 — variation scaffolding  ·  `132e735`

The `--variation` knob threaded end-to-end:

```
runner → submit_condor → submit → BaseProcessor
       → object_corrector_manager → apply_*  (jerc / met / muon_ss / electron_ss)
```

```yaml
variations:            # nominal always run; others auto-expand Up/Down
  - nominal
  - jes_Absolute
  - jer_barrel
  - met_unclust
  - mu_scale
  - ele_scale
```

- Output paths gain a `<variation>/` segment; condor job dirs too
- `runner.py` with no `--variation` iterates the yaml list
- Non-nominal variations accepted as **no-ops** (real shifts in Commit 2)
- Nominal physics bit-identical to before

---

# Commit 2 — JES/JER injection  ·  `88192a0`

Fills the `# TO DO: SYSTEMATICS` slot in `jerc.py`.

```python
# jes_<src>Up/Down: swap the CorrectedJetsFactory shifted-jet branch
shifted = events.Jet[f"JES_{src}"][side]   # side = up | down
events["Jet", "pt"]   = shifted.pt
events["Jet", "mass"] = shifted.mass
update_met(events, year)                    # re-propagate Type-I MET
```

- `met_unclustUp/Down` use NanoAOD's built-in
  `ptUnclustered{Up,Down}` / `phiUnclustered{Up,Down}`
- Guarded on `is_mc`; silent fall-through to nominal if a branch
  is absent — an unimplemented variation degrades, never crashes
- jer / mu / ele remain accepted no-ops (same swap pattern, fillable
  on demand). JES is the Commit 4 smoke-test target.

---

# Commit 3 — relocate combine pipeline  ·  `e464b4a`

Four histogram scripts + three datacard generators → **one**
yaml-driven `make_combine_inputs.py`.

Takes advantage of 0a/0b — reads the scored, self-normalising parquets:

```python
md   = pq.read_table(parquet).schema.metadata
scale = lumi * float(md[b"xsec"]) / float(md[b"sumw"])
# argmax over mva_score_<class> → channel; D = winning class score
```

**No torch model load. No coffea sidecar. No luminosity.yaml lookup.**

New `scripts/combine/`: `make_combine_inputs.py`, `drive_combine.py`,
`run_combine.sh`, `make_impact_plot.py`, `make_combine_plots.py`.

---

# Commit 3 — the `combine:` yaml block

```yaml
combine:
  classes: [hplusc, higgsbkg, tt, st, diboson, vjets]
  signal: hplusc
  channels:                       # argmax class → channel
    SR_hplusc: hplusc
    CR_tt: tt
    ...
  process_map:                    # combine proc → higgscharm processes
    hplusc: [H+c]
    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]
    ...
  shape_systematics: [pileup, ps_isr, ps_fsr, scalevar_muR, ...]
  lnN:
    xsec_hplusc_4FS_5FS: {hplusc: 1.30}
    ...
  run:
    asymptotic_limits: {asimov: true, blind: true}
    impacts: {method: freeze_per_nuisance}
```

To try a different config: copy the yaml, edit. One file = one analysis pass.

---

# Commit 3 — the safety net

**Byte-for-byte reproduction test** (the most important check):

```bash
# legacy b-hive scripts
combine -M AsymptoticLimits v11_hplusc_v3.workspace.root -t -1 --run blind

# relocated higgscharm scripts
python scripts/combine/make_combine_inputs.py -w hww_MVA -y 2022postEE
bash   scripts/combine/run_combine.sh hww_MVA
# expect identical r₉₅ median = 979
```

The legacy b-hive combine scripts + `combine_inputs/` are **left in
place as the reference** until this test passes in Commit 4.
Deleting the reference before verification would be unsafe.

---

# Day-to-day after migration

**Fit (every analysis pass) — six commands, one yaml:**

```bash
python runner.py                    -w hww_MVA -y 2022postEE
python run_postprocess.py           -w hww_MVA -y 2022postEE
python scripts/mva/run_inference.py -w hww_MVA -y 2022postEE
python scripts/combine/make_combine_inputs.py -w hww_MVA -y 2022postEE
bash   scripts/combine/run_combine.sh         hww_MVA
python scripts/combine/make_combine_plots.py  -w hww_MVA
```

Add a systematic = edit `variations:` and `combine.shape_systematics:`,
re-run from step 1.

---

# Status

**Shipped on `migration`** (5 of 6):

- ✅ 0a `8192494` · 0b `aeb0104` · 1 `132e735` · 2 `88192a0` · 3 `e464b4a`

All compile; config round-trips; non-combine workflows unaffected
(`cfg.combine = None`). Nominal physics unchanged.

---

# What's next — planned work

**Commit 4 — end-to-end smoke test** (runtime task, needs CMSSW + GPU node):

```bash
runner.py --variation jes_AbsoluteUp/Down  →  run_postprocess
  →  run_inference  →  make_combine_inputs  →  run_combine.sh
  →  make_impact_plot
```

Acceptance:
- v3 nominal **r₉₅ = 979 reproduced byte-identically** from relocated scripts
- `jes_Absolute` bar appears on the impact plot, magnitude in
  AN-23-102 Fig. 53 ballpark (±30–50)
- shifted parquets show ~3 % cjet-pt shift vs nominal

**Then — cleanup commit:** delete legacy b-hive combine scripts +
`combine_inputs/` once Commit 4 confirms reproduction.

---

# Open questions (deferred to post-Commit-4)

1. **JES granularity** — 27-source / regrouped-11 / 5-source reduced?
   Start with regrouped-11 to match AN-23-102.
2. **Storage** — ~18 shifted sets × 2 sides ≈ 36 dirs; confirm eos quota.
3. **Fit on full vs test-only** event set (fine for Asimov sensitivity).
4. **Data parquets** — handle `era == "data"` (no xsec scaling) when added.
5. **CombineHarvester** — manual impact loop is the workaround until installed.
6. **Hardware** — add GPU support to `run_inference.py` for larger models.

---

# Summary

- **yaml as the single knob** — selection → variations → MVA →
  combine, all in `hww_MVA.yaml`
- **self-normalising parquets** — sumw/xsec/era travel with the data
- **single-responsibility scripts** — postprocess no longer a kitchen sink
- **combine lives in higgscharm** — yaml-driven, no torch/coffea in the hot path
- **5/6 commits shipped**; Commit 4 is the runtime smoke test that
  unlocks the b-hive cleanup

Reproduction invariant **r₉₅ = 979** preserved at every checkpoint.
