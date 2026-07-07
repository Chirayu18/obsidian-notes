---
tags: [reference]
status: active
date: 2026-07-07
source: lxplus
---

# Trigger efficiency — H+c (H→WW), 2022postEE

Computed from the higgscharm cutflow that the `base` workflow writes per sample.

**Source cutflow:** `/eos/user/c/cgupta/higgscharm/outputs/hww/2022postEE/base/cutflow_base.csv`
(+ per-sample `cutflow_base_<sample>.csv` / `.coffea`). The `trigger` and `met_filters`
rows are all that's needed — the efficiency below is derived from them (see snippet).

## Definition

`trigger_eff = N(after "trigger") / N(after "met_filters")` — `met_filters` is the step
**immediately before** `trigger` in the cutflow. Counts are weighted (MC: Σ `weight_nominal`;
Data: raw events). Full cut order:

```
goodvertex → lumimask → met_filters → trigger → met_45 → one_ll_pair → one_muon_one_electron
```

HLT paths (from `analysis/selections/trigger_flags.yaml`, 2022): SingleMu `IsoMu24`,
SingleEle `Ele30_WPTight_Gsf`, DiMu `Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`,
DiEle `Ele23_Ele12…` / `DoubleEle25_CaloIdL_MW`, MuEle `Mu23…Ele12…` / `Mu12…Ele23…_DZ`.

## Results (2022postEE)

| sample | before trigger | after trigger | trigger eff |
|---|---:|---:|---:|
| ggZH | 76.6 | 40.8 | **53.3%** |
| Data | 1.346e9 | 6.137e8 | **45.6%** |
| ZH | 538.5 | 231.8 | **43.0%** |
| **H+c (signal)** | 54.9 | 20.6 | **37.5%** |
| ttHnonBB | 487.2 | 114.3 | 23.5% |
| VBF | 8964.7 | 2071.6 | 23.1% |
| ttHtoBB | 8674.5 | 2002.5 | 23.1% |
| tt | 2.406e7 | 5.465e6 | 22.7% |
| V+Jets | 1.757e9 | 3.839e8 | 21.8% |
| ggH | 1.061e5 | 2.018e4 | 19.0% |
| WW | 3.198e6 | 5.906e5 | 18.5% |
| **Total Background** | 2.537e9 | 4.576e8 | **18.0%** |
| Single Top | 8.503e6 | 1.229e6 | 14.4% |
| WZ | 1.425e6 | 1.983e5 | 13.9% |
| ZZ | 4.395e5 | 4.227e4 | 9.6% |
| WG | 1.741e7 | 1.649e6 | 9.5% |
| DY+Jets | 7.246e8 | 6.453e7 | 8.9% |
| WH | 0 | 0 | n/a (no events) |

## Caveats

- **This is the trigger firing *before* the offline dilepton selection** (`one_ll_pair` /
  `one_muon_one_electron` come *after* `trigger` in the cutflow). So it is the trigger
  efficiency on events with only good-vertex + MET-filters, **not** ε given a clean
  2-lepton offline selection. That inflates the denominator with leptonless events →
  low absolute numbers (DY 8.9% vs signal 37.5%). For the analysis-grade number
  (ε on offline-selected dilepton events) the trigger would have to be applied *after*
  the pair selection — not available from this cutflow ordering.
- **MC selection efficiency only — no trigger SF applied.** There is no `weight_trig`
  column in the parquets; trigger eff is currently absorbed into the ~4.6% lepton
  systematic. See [[ElectronMuonWP status]] (MC/data 1.18 in high-mass CR; proper
  triggers + trigger SFs flagged as a to-do).
- **Data ≈ 45.6%** reflects the trigger-enriched primary datasets (Muon/EGamma/MuonEG),
  not a physics efficiency — data is not a clean denominator at this stage.
- **2022postEE only.** 2022preEE has no cutflow CSV (that era wasn't run with the
  cutflow); rerun the `base` workflow on preEE to produce it.

## How to reproduce (b_hive env has coffea 0.7 + pandas)

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(micromamba shell hook --shell bash)"
micromamba activate b_hive        # coffea 0.7.22, pandas
python - <<'PY'
import pandas as pd
D="/eos/home-c/cgupta/higgscharm/outputs/hww/2022postEE/base"
df=pd.read_csv(D+"/cutflow_base.csv",index_col=0)
steps=list(df.index); before=steps[steps.index("trigger")-1]
eff=df.loc["trigger"]/df.loc[before]
print(eff.sort_values(ascending=False))
PY
```

Related: [[2026-06-17-systematics-reference]] · [[Analysis QUICKSTART]]
