---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# Migration-v2 — State of the Higgscharm + Combine Analysis

Authoritative status doc for the `migration-v2` branch. Supersedes the
original `docs/migration_plan.md` (which targeted the now-superseded
`migration` branch). Last updated 2026-06-05.

---

## 0. TL;DR

- Active branch: **`migration-v2`** in
  `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
- Based on **`uacms/MVA`** (the upstream line that HAS the object-shift
  systematics, `process_shift` / `object_shifts`) + merged `uacms/main`.
- The **nominal analysis is end-to-end ready** (produces r₉₅, the v3 result).
- Object-shift parquets are produced/merged/scored; the only remaining wiring
  is folding their templates into the combine datacard as shape rows.

---

## 1. The two upstream lines (important context)

There are **two divergent MVA branches**; they split at `ea4faf8`:

| | `uacms/MVA` (our base) | `tvl/MVA` = theumesvl/ua-cms-higgscharm |
|---|---|---|
| object-shift systematics (`process_shift`/`object_shifts`) | **YES** (PR #19) | **NO** |
| MVA variables | 42 | **53** |
| per-category postprocessing (`combined_` prefix) | no | yes |
| combine pipeline | no (we added it) | no |

`migration-v2` = **`uacms/MVA`'s systematics line** + the valuable *content*
cherry-picked from `tvl/MVA` (53 variables, muon fix, failsafes). The
class order is **`[hplusc, higgsbkg, tt, st, diboson, vjets]`** (confirmed
correct by the user; matches the v11 model). Note Thomas's `utils.py` used
`[higgsbkg, hplusc, ...]` — do NOT copy that ordering.

Remotes:
- `uacms` = git@github.com:ua-cms/higgscharm.git  (MVA = systematics line)
- `origin` = git@github.com:theumesvl/higgscharm.git (origin/MVA == uacms/MVA)
- `tvl` = https://github.com/theumesvl/ua-cms-higgscharm.git (Thomas's 53-var line)

---

## 2. Commits on `migration-v2` (on top of `uacms/MVA`)

From `uacms/main` (merged in):
- `7b3de52` add rucio utils
- `91949e3` update JERC correction files  ← affects the JES/JER shift inputs
- `9631eda` update T2_IN_TIFR sites
- `31e98bf` fix down variation typo (plotter)

Our migration work:
- `d100f0f` **parquet plumbing** — self-normalising sumw/xsec/era metadata
  (was 0b) + the `dump_parquet` else-branch that writes object-shift parquets
  + `event` id column.
- `2c79ae6` **MVA prep** (was 0a) — strip `--mva`/`--infer` from
  `run_postprocess`; add `scripts/mva/{prep_training_inputs,run_inference}.py`;
  add `mva`/`inference`/`combine` config fields; **migrate hww_MVA.yaml
  corrections schema** to upstream's `object`/`jet`/`muon`/`electron` +
  `object_shifts` (upstream had left hww_MVA.yaml broken against the new builder).
- `bfd20bd` **combine pipeline** (cherry-pick of migration 3) — `scripts/combine/`
  + `combine:` yaml block.
- `1c10c31` **shift-merge** — `merge_shifted_parquets_by_sample` →
  `<year>/<shift>/<sample>.parquet`.

Cherry-picked from `tvl/MVA` (Thomas Van Laer's content):
- `909e5a4` 53 MVA variables (cherry-pick `c31be62` into hww.yaml + mirror into
  hww_MVA.yaml).
- `4082c26` muon pt_resol clamp (cherry-pick `c7e06f7`).
- `0684b66` empty-parquet failsafes (selective port of `2d8ed33`) + **drop SR
  category** (single-category analysis).

DROPPED from the original `migration` branch (superseded by upstream):
- old commit 1 (`--variation` rail) and 2 (hand-wired JES) — upstream's
  `object_shifts: true` does this in one job per dataset.

---

## 3. What is / isn't in vs the other lines

**Missing from `uacms/main`:** nothing (fully merged).

**Missing from `tvl/MVA` (intentionally NOT taken):**
- per-category postprocessing layout (`<category>/`, `combined_` prefix) — only
  relevant with multiple categories; we use one (`base`).
- 6-class `PROCESS_GROUPS` in utils.py — superseded by yaml `mva.labels`.
- `f871b1a` switch private samples postEE→**preEE** — OPTIONAL dataset choice,
  user said "fine" to leave as postEE.
- `d4eb786` Thomas's rucio_utils — we have main's version.
- `4108e12` revert jetvetomaps — backwards; skip (we have main's newer).

---

## 4. The variations mechanism (how shifts run in 1 job)

`object_shifts: true` in `hww_MVA.yaml` `corrections:` is the single knob.
Upstream's `object_corrector_manager` builds a list of `(collections, shift)`
tuples in one NanoAOD read; `BaseProcessor.process` loops
`process_shift(update(events, collections), shift)`, emitting nominal + every
shift from a single Condor job per dataset. Our else-branch in `dump_parquet`
writes each shift to `<dataset>/<category>/<shift>/`; `merge_shifted_parquets_by_sample`
collapses to `<year>/<shift>/<sample>.parquet`.

Jobs = N datasets (not N×variations). Old approach was N×23 jobs.

---

## 5. End-to-end commands

### Pre-flight (once)
```bash
! voms-proxy-init --voms cms --valid 192:00
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
ln -sfn /eos/user/c/cgupta/higgscharm/outputs outputs
```

### Fit flow (nominal → r₉₅; the working end-to-end path)
```bash
# 1. parquets (Condor). object_shifts: false = nominal only; true = + JES/JER shifts
python runner.py            -w hww_MVA -y 2022postEE --output_format parquet --eos --submit
watch condor_q
# 2. merge (base env)
python run_postprocess.py   -w hww_MVA -y 2022postEE --postprocess --output_format parquet
# 3. inference -> mva_score_* columns
python scripts/mva/run_inference.py        -w hww_MVA -y 2022postEE
# 4. ROOT + datacard
python scripts/combine/make_combine_inputs.py -w hww_MVA -y 2022postEE
# 5. fits (CMSSW; wrapper sources it)
bash   scripts/combine/run_combine.sh         hww_MVA
# 6. plots
python scripts/combine/make_combine_plots.py  -w hww_MVA
python scripts/combine/make_impact_plot.py    -w hww_MVA
```

### Training (only if retraining on the 53 variables)
```bash
# after step 2 on nominal:
python scripts/mva/prep_training_inputs.py -w hww_MVA -y 2022postEE   # split + labels + filelists
cd /eos/home-c/cgupta/HToWW/b-hive && ./train_MVA.sh                  # b-hive DatasetConstructor + Training
# then set inference.model_path in hww_MVA.yaml to the new best_model.pt
```

### Environment note
Steps 2–4 run in the base (coffea/torch) env; ONLY step 5 is inside CMSSW.

---

## 6. The ONE remaining piece

`scripts/combine/make_combine_inputs.py` processes **one variation per run**
(`--variation`, default nominal) and builds the **weight-based** shape
systematics (12 `weight_*Up/Down`) + 9 lnNs into the datacard. To get
**object-shift** (JES/JER) shape rows, it needs to also loop the
`<year>/<shift>/mva/` dirs and emit those templates as shape lines.

- Nominal limit + weight systematics: **ready now.**
- Object-shift shape templates: **produced & scored, not yet folded into the
  datacard** — this is the last wiring step (the "Commit 4" smoke-test work).

Reproduction invariant to check on the first full run: **v3 r₉₅ = 979**
(Asimov median, 26.67 fb⁻¹, 2022postEE) for the nominal datacard.

---

## 7. Key config facts (`analysis/workflows/hww_MVA.yaml`)

- `corrections.object: [jet, muon, electron]`, `object_shifts: false` (toggle).
- `event_selection.categories`: **`base` only** (SR removed). `base` now
  requires **`atleast_one_cjet`** (the H+c signal object) — note this moves
  the nominal limit off the old no-cjet r₉₅=979 baseline.
- 53 histogram variables.
- `mva.labels.process_groups`: 6-class, order `[hplusc, higgsbkg, tt, st, diboson, vjets]`.
- `inference`: v11 model at
  `/eos/user/c/cgupta/EPR_task/b-hive/output/TrainingTask/HPlusCHToWW_multiclass/hww_multiclass_v11/.../best_model.pt`.
- `combine`: 6 argmax channels (SR_hplusc + 5 CRs), 12 shape systs, 9 lnNs,
  output to `outputs/combine/v11_hplusc_v3.{root,txt}`.
