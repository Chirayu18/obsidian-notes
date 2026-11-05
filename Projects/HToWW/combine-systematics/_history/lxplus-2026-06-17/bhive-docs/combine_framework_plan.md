---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# Integrating the combine pipeline into higgscharm

Goal: move the combine-input production (currently `b-hive/scripts/
make_combine_histograms_v11*.py` + `make_datacard_v11*.py`) into the
higgscharm framework, and design the parquet layout so object-level
variations can be propagated without touching b-hive's MVA model.

The MVA training and inference stay in b-hive. The split is:

```
higgscharm ──(per-variation parquets)──▶ b-hive InferenceTask
       ▲                                        │
       └──────(prediction.npy per variation)────┘
                              │
                              ▼
          higgscharm: histogram + datacard scripts
                              │
                              ▼
                       combine / fits
```

---

## 1. Per-variation parquet layout

**Decision: one parquet directory per variation, identical schema to
nominal.** This is the right choice because:

- b-hive's `InferenceTask` runs unchanged — it just loads a parquet, reads
  the MVA input columns, writes `prediction.npy` + `truth.npy`. No model,
  config, or input list changes per variation.
- Storage cost is paid only on the kinematic + jet-tag columns; flat weight
  columns can be omitted from shifted files since the **shape** is what
  changes (the weight stays nominal — that's the whole point of an object
  variation).
- Easy to parallelise on Condor: one job per (sample, variation) tuple.

### Directory convention

```
/eos/user/c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/
└── v5_combine/                              # new top-level for combine pipeline
    ├── nominal/                             # current per-sample parquets live here
    │   ├── hplusc/part-*.parquet
    │   ├── tt/part-*.parquet
    │   └── ...
    ├── jes_AbsoluteUp/
    │   ├── hplusc/part-*.parquet            # SAME columns as nominal, shifted jet pT
    │   ├── tt/part-*.parquet
    │   └── ...
    ├── jes_AbsoluteDown/
    ├── jes_BBEC1Up/
    ├── ...
    ├── jer_barrelUp/
    ├── met_unclustUp/
    ├── mu_scaleUp/
    └── ele_scaleUp/
```

Each variation directory has **the same per-sample sub-structure** as
nominal, so b-hive can point at `<variation>/` with no other change.

### What goes in each parquet

| column kind | nominal | object-shift variation | weight variation |
|---|---|---|---|
| MVA inputs (`lep1_pt`, `mtl1`, `cjet_cand_cvsl_pnet`, ...) | nominal values | **shifted** for affected objects | nominal values |
| `weight_nominal` | nominal | **nominal** (object shift does not change the weight) | nominal |
| `weight_<syst>{Up,Down}` columns | present | **omitted** (we already have these in nominal) | present in the nominal parquet only |
| truth label, event id | yes | yes | yes |

Object-shift variations therefore only need MVA inputs + `weight_nominal` +
truth — no need to recompute the 12 weight-based shape systematics in
every shifted file (they already live in nominal).

### Naming of variations

Use the **same string** combine expects in `<proc>_<variation>{Up,Down}`
histograms. E.g. `jes_Absolute`, `jer_barrel`, `met_unclust`, `mu_scale`,
`ele_scale`, `ele_smear`, `hem2022`, `l1prefire`. So
`jes_AbsoluteUp/` directory → `<proc>_jes_AbsoluteUp` TH1D.

---

## 2. Higgscharm changes to produce shifted parquets

### 2.1 Variation plumbing in `correction_manager.py`

The function `object_corrector_manager(events, ...)` already calls
`apply_jerc_corrections(events, year, dataset)` etc. Add a `variation`
parameter and forward it down:

- `jerc.py:apply_jerc_corrections(events, year, dataset, variation=...)`
- `met.py` (for `met_unclust*`)
- `muon_ss.py:apply_muon_ss_corrections(events, year, variation=...)` — knob already exists for "nominal", extend to `{mu_scale,smear}{Up,Down}`
- `electron_ss.py:apply_electron_ss_corrections(events, year, variation=...)` — same pattern

Each variation mutates `events.Jet.pt`, `events.PuppiMET.pt`, etc., **before**
the object selection runs, so the same downstream pruning produces the
shifted event set.

### 2.2 Runner: variation loop

The current `analysis/runner.py` runs one configuration per call. Two options:

**(a) External driver (simpler).** A shell/Python wrapper loops over the
variation list and submits one runner job per variation, passing
`--variation jes_AbsoluteUp` etc. on the command line. The runner reads
the flag and forwards it to `object_corrector_manager`. Output directory
is `<output_root>/<variation>/<sample>/`.

**(b) Internal loop.** Single processor run produces all variations at
once. Saves on event reading but ~30× memory, and one bad variation
crashes them all. Not recommended.

Go with **(a)**. Implementation:

- `analysis/runner.py` accepts `--variation` flag, defaults to `nominal`.
- New driver `scripts/run_all_variations.py` (in higgscharm) generates the
  list of variations from a config and submits Condor jobs.
- Variation list lives in a single yaml, e.g.
  `analysis/workflows/hww_MVA_variations.yaml`:
  ```yaml
  variations:
    - nominal
    - jes_Absolute
    - jes_BBEC1
    - jes_FlavorQCD
    - jer_barrel
    - jer_endcap1
    - met_unclust
    - mu_scale
    - ele_scale
    - ele_smear
    - hem2022
  ```
  Each non-nominal entry expands to `<name>Up` + `<name>Down`.

### 2.3 Output schema

For non-nominal variations, parquets carry only:
- MVA input columns (the list b-hive's `v4_hplusc_higgsbkg` training reads)
- `weight_nominal`, `truth`, `event`, `run`, `lumi`

No `weight_<syst>{Up,Down}` columns in shifted parquets — they live in
nominal only.

---

## 3. b-hive integration (no code changes needed, but new tasks)

b-hive's `InferenceTask` is variation-agnostic by construction: point its
input at `<variation>/` and it produces a `prediction.npy` + `truth.npy`
under a tagged output directory. Add a wrapper task that loops:

```
for variation in variations:
    InferenceTask(
        input  = "/eos/.../v5_combine/<variation>/",
        output = "/eos/.../v5_combine/<variation>/inference/",
        model  = "v11",  # frozen, single training
    )
```

Two practical notes:
- Use the **same** trained v11 model for every variation. Do **not** re-train.
- Make sure `InferenceTask` writes per-sample `prediction.npy` (it already
  does) so the histogram script can pair (sample, variation) → D
  distribution.

The b-hive side of this plan is one short shell script and no code change.

---

## 3a. Parallelising inference across variations

`InferenceTask` is a `law`/luigi task keyed on `test_dataset_version` (and
training). Treating each variation directory as its own
`test_dataset_version` gives one task instance per variation — that's the
unit of parallelism.

### Three layers of parallelism, in order of effort

1. **Intra-task: DataLoader workers.** Already happening — `InferenceTask`
   builds the `DataLoader` with `num_workers=self.n_threads`. Bump
   `n_threads` for shifted runs; the GPU pass is the bottleneck, not data
   loading, so 4–8 is usually enough.

2. **Inter-task: luigi worker pool.**
   ```bash
   law run InferenceTask \
       --test-dataset-version "jes_AbsoluteUp,jes_AbsoluteDown,jer_barrelUp,..." \
       --workers 4
   ```
   Runs 4 InferenceTask instances concurrently in one process. Bound by
   **GPU memory**: each instance loads a copy of the v11 model and its
   batches. On a single A100 / H100, ~4–8 concurrent forward passes is
   feasible; on a 12 GB consumer card, 1–2. Cheap to set up, no submitter
   needed.

3. **Cluster: one job per (sample, variation).** Best scaling. b-hive uses
   `law`, which has a Condor sandbox; route InferenceTask through it so
   each (sample, variation) becomes one Condor job with its own GPU
   request. This is the right mode for 36+ variations.
   - Sketch: `law run InferenceTask --workflow htcondor --pilot-tasks 50`
     style, or wrap with a small driver that iterates over
     `(sample, variation)` and submits one Condor job each.
   - Each job: one variation × one sample (or one variation × all samples
     if a single GPU can handle it in <1 h).
   - Output collected into the same `<variation>/inference/<sample>/`
     layout the histogram script expects (§4.1).

### Pinning down "what does parallel inference cost"

Useful numbers to gather before scaling out (run during the §6 step-5
smoke test):

| metric | how to measure | use |
|---|---|---|
| GPU time per sample per variation | `inference_time.npy` already written by InferenceTask | sizing Condor request |
| Peak GPU memory | `nvidia-smi` during a run | how many `--workers` per GPU |
| End-to-end per variation, 1 GPU | wall-clock of one full sample loop | extrapolate total job count |
| Disk read throughput from EOS | iostat / parquet IO timer | decide if EOS is the bottleneck |

If GPU time per variation × N_samples is < 30 min, luigi `--workers` on a
single node is enough. If it's hours, go to Condor.

### Variations whose inference can be **skipped**

- **Weight-only systematics** (`pileup`, `ps_isr/fsr`, `scalevar_*`,
  `muon_id/iso`, `electron_id/reco_*`, future `pdf`, `alphaS`, `trigger`,
  `ctag`, …) **do not need re-inference** — they reuse the nominal
  `prediction.npy`. The histogram script just swaps the weight column.
- **Object-shift systematics** (JES, JER, MET_unclust, mu_scale,
  ele_scale, ele_smear, HEM, L1_prefire) **do** need re-inference — they
  change MVA input values.

So the parallel inference budget is set by the object-shift count (the
~36 number), not by the total nuisance count.

---

## 4. Move the combine scripts into higgscharm

Currently in b-hive:
- `scripts/make_combine_histograms_v11.py`
- `scripts/make_combine_histograms_v11_lumi.py`
- `scripts/make_combine_histograms_v11_v3.py`
- `scripts/make_datacard_v11.py`
- `scripts/make_datacard_v11_v3.py`

Relocate to `higgscharm/scripts/combine/` (or
`higgscharm/analysis/postprocess/combine/`). Same code, but:

### 4.1 Input contract changes

Today the scripts read parquets at a hardcoded path and `prediction.npy`
at another. Generalise to:

```python
build_inputs(
    parquet_root="/eos/.../v5_combine/",
    inference_root="/eos/.../v5_combine/",   # same root, <variation>/inference/
    variations=[...],
    samples=[...],
    process_map={...},
)
```

The script's outer loop becomes:

```
for variation in variations:
    for proc, samples in process_map.items():
        for sample in samples:
            pq = read_parquet(f"{parquet_root}/{variation}/{sample}/")
            pred = np.load(f"{inference_root}/{variation}/inference/{sample}/prediction.npy")
            D = discriminant(pred)
            if variation == "nominal":
                fill_hist(f"{proc}")                                   # nominal
                for syst in weight_systs:
                    fill_hist(f"{proc}_{syst}Up",   weights=pq[f"weight_{syst}Up"])
                    fill_hist(f"{proc}_{syst}Down", weights=pq[f"weight_{syst}Down"])
            else:
                # object-shift variation: weight stays nominal, D is shifted
                fill_hist(f"{proc}_{variation}",    weights=pq["weight_nominal"])
```

Where `variation` for object shifts is already suffixed `Up`/`Down` (the
directory name `jes_AbsoluteUp`).

### 4.2 Datacard generator

Same script, just relocated. The lnN list and rateParam list live in a
yaml `higgscharm/analysis/workflows/combine_datacard.yaml` so non-code
changes don't require touching the generator.

### 4.3 Output layout in higgscharm

```
higgscharm/outputs/combine/
├── v11_hplusc.root              # nominal-binned 1-channel histograms
├── v11_hplusc_v3.root           # multi-channel (argmax) version
├── v11_hplusc.txt               # datacard
└── v11_hplusc.workspace.root    # text2workspace output
```

`combine` itself still runs from CMSSW (no change).

---

## 5. Why per-variation files beats per-event-shifted columns

Briefly recording the trade-off so this doesn't get re-litigated:

| approach | parquet layout | b-hive code change | storage | parallelism |
|---|---|---|---|---|
| **per-variation directories** (recommended) | N directories, identical schema | none | linear in N, but only MVA inputs duplicated | trivial — one job per (sample, variation) |
| per-event-shifted columns in nominal | nominal parquet carries `lep1_pt_jesAbsoluteUp` etc. | b-hive must read 2N MVA-input variants and run inference 2N times per event | smaller (one event id per row) | hard — InferenceTask would need a "which columns to read" knob |
| separate trained models per variation | one parquet per variation, N trained models | retrain N times | medium | medium |

Per-variation directories: b-hive InferenceTask never knows the variation
exists — it just reads a parquet and writes a prediction. That's the
property worth preserving.

---

## 6. Execution order

1. **Variation contract.** Pin the exact list of object-level variations
   we'll produce. Phase 1: `jes_Absolute`, `jer_barrel`, `met_unclust`,
   `mu_scale`, `ele_scale`. Add the rest after the pipeline is proven.
2. **Plumb `variation=` in higgscharm corrections** (`jerc.py`, `met.py`,
   `muon_ss.py`, `electron_ss.py`).
3. **Runner flag + driver script** to submit per-variation jobs.
4. **Re-produce nominal parquets** under `v5_combine/nominal/` with the
   new directory convention — sanity check that combine v3.5 from this
   directory reproduces combine v3 from the old `v4_hplusc_higgsbkg/`.
5. **Produce one shifted set** (e.g. `jes_AbsoluteUp/Down`) end-to-end:
   higgscharm → b-hive inference → histogram script → datacard → combine
   fit. Smoke test the wiring before scaling to all variations.
6. **Relocate combine scripts** into higgscharm and parametrise inputs
   per §4.1.
7. **Scale out** — run remaining variations on Condor.

---

## 7. Open questions

1. **JES granularity.** Full 27-source, regrouped 11, or 5-source reduced
   set? Affects N by ~5×.
2. **Storage.** 11 JES × 2 + 3 JER × 2 + 4 lepton/MET × 2 = ~36 shifted
   parquet sets. With MVA-input columns only, each is ~30–40 % of nominal
   per-sample size. Estimate before committing the eos quota.
3. **Where does combine fit run?** CMSSW build at
   `/afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4/` is current. Keep the
   build out of higgscharm; just have higgscharm produce the inputs.
4. **Per-sample vs per-process parquets in shifted dirs.** Today nominal
   is per-sample; the histogram script aggregates. Keeping per-sample in
   shifted dirs is consistent and avoids re-doing the aggregation logic.
