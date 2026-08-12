---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# Lepton MVA (mvaTTH) 2022EE: TMVA XML -> ONNX, validated

## What these files are

Two TMVA BDT weight files, **not** trigger scale factors (that was the initial
assumption and it was wrong -- there is no HLT path, no leg pT/eta efficiency
binning, no data/MC ratio anywhere in them).

They are the **ttH-multilepton lepton MVA** (`mvaTTH`): a per-lepton
prompt-vs-nonprompt discriminant separating leptons from W/Z/tau decays
("prompt") from leptons in b-hadron decays ("nonprompt").

| | |
|---|---|
| Creator / date | `cvico`, 2023-12-20 |
| Origin | `CMGTools/TTHAnalysis`, CMSSW_12_4_12, wz-run3 leptonMVA |
| Method | `BDT::BDTG`, 500 trees, MaxDepth 8, Shrinkage 0.1 |
| Classes | binary (Signal=prompt, Background=nonprompt) |
| Transforms | `NTransformations="0"` -- **no input preprocessing** |
| Training events | 879,894 (muon) |

## Why not the NanoAOD branch

`Muon_mvaTTH` / `Electron_mvaTTH` **do exist** in NanoAODv12 (verified on a
central `TTto2L2Nu` v12 file). They are not used: the stock branch is a Run 2
training, while these XMLs are a dedicated **2022EE** retraining. Same 13
variables, different weights -- so the stock branch is subtly, not obviously,
wrong. Per instruction, evaluate these weights, do not read the branch.

## Input variables (index order matters -- it is the ONNX column order)

| i | muon | electron |
|---|---|---|
| 0 | `pt` | `pt` |
| 1 | `eta` | `eta` |
| 2 | `pfRelIso03_all` | `pfRelIso03_all` |
| 3 | `miniPFRelIso_chg` | `miniPFRelIso_chg` |
| 4 | `miniPFRelIso_all - miniPFRelIso_chg` | same |
| 5 | `jetNDauCharged` | `jetNDauCharged` |
| 6 | `jetPtRelv2` | `jetPtRelv2` |
| 7 | `jetIdx>-1 ? Jet_btagDeepFlavB[jetIdx] : 0` | same |
| 8 | `min(1/(1+jetRelIso), 1.5)` | same |
| 9 | `sip3d` | `sip3d` |
| 10 | `log(abs(dxy))` | `log(abs(dxy))` |
| 11 | `log(abs(dz))` | `log(abs(dz))` |
| 12 | **`segmentComp`** | **`mvaIso`** |

All 13 branches for **both** flavours verified present in NanoAODv12 (0 missing).

## The response formula

TMVA `BoostType=Grad`, 2 classes:

```
raw   = sum_t res_t(x)              # leaf 'res' values, summed, NO extra factor
score = 2 / (1 + exp(-2*raw)) - 1   # in (-1, 1)
```

**Shrinkage is already folded into the stored leaf values** -- do NOT multiply by
0.1 again. Verified empirically: leaf `res` caps at 0.0999 ~= shrinkage, and
decays across the ensemble (tree 0 absmax 0.0999 -> tree 499 absmax 0.0224),
which is the expected boosting behaviour.

Tree structure: `IVar` = feature index, `Cut` = threshold, `nType=-99` = leaf,
`pos` = s/l/r. TMVA sends `var <= Cut` to the **left** child, which maps exactly
onto ONNX `BRANCH_LEQ` with `true_branch = left`.

## Validation -- the part that matters

Three independent implementations, same inputs:

1. **ONNX** (`TreeEnsembleRegressor` + closed-form squashing)
2. **numpy** recursive mask-based tree walk (`numpy_ref.py`)
3. **`TMVA::Reader`** via LCG view `LCG_104a/x86_64-el9-gcc12-opt` -- the
   reference implementation

| pair | N | max abs diff | corr |
|---|---|---|---|
| ONNX vs numpy (muon) | 2000 | 2.203e-07 | -- |
| ONNX vs numpy (elec) | 2000 | 2.870e-07 | -- |
| **ONNX vs TMVA::Reader (muon)** | 300 | **1.562e-07** | **1.0000000000** |
| **ONNX vs TMVA::Reader (elec)** | 300 | **2.228e-07** | **1.0000000000** |

That is float32 round-off. **The conversion is exact.**

> ONNX-vs-numpy alone would NOT have been sufficient: both encode the same
> reading of the XML format. Only `TMVA::Reader` can catch a misread convention
> (e.g. left/right inverted, or shrinkage double-applied). Always validate a
> converted model against the reference implementation, not against your own
> second implementation.

`TMVA::Reader` is slow (scalar API, ~500 trees): 2000 points times out at 2 min;
300 points is enough and takes well under a minute.

## Artifacts (EOS, durable)

```
/eos/user/c/cgupta/HToWW/leptonmva/
  onnx/muon_mvaTTH_2022EE.onnx        0.38 MB   <- use these
  onnx/electron_mvaTTH_2022EE.onnx    0.40 MB
  tmva_to_onnx.py         converter (validates Options, refuses transforms)
  numpy_ref.py            independent numpy evaluator
  tmva_reference.py       TMVA::Reader reference generator (needs LCG view)
  validate_vs_tmva.py     the comparison
  tmva_reference.npz      frozen reference inputs + scores
```

Re-run validation any time:

```bash
export MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
cd /eos/user/c/cgupta/HToWW/leptonmva
$MAMBA_EXE run -n b_hive python3 validate_vs_tmva.py
```

## Traps when wiring into the processor

1. **`jetIdx == -1`** -- mask BEFORE indexing `Jet_btagDeepFlavB`, else you
   silently read the last jet in the event. Use a guarded index.
2. **`log(abs(dxy))`** -- `dxy` can be exactly 0 -> `-inf`. Needs a floor, and
   the floor must match whatever the training producer used. **UNRESOLVED.**
3. **Session caching** -- build the `InferenceSession` once at module level, not
   per chunk, or it dominates runtime.
4. **float32** -- the graph input is typed float32; float64 raises.
5. Score is **per-lepton and jagged**: `ak.flatten` -> evaluate -> `ak.unflatten`.

## Status: converted and validated, NOT wired in

No production code touched. Open questions before any integration:

- **What are the scores for?** A tight-lepton cut (=> reprocessing + new lepton
  efficiency SFs + a new systematic) or an MVA input feature (=> retraining)?
- **Which working point?** Must come from whoever advised this; do not invent one.
- **Is the nonprompt background even significant here?** See
  [[2026-08-12-lepton-mva-nonprompt-diagnostic]].

## Context: no reference analysis of ours uses a lepton MVA

- **AN-23-102** (Run 2 predecessor): no lepton MVA.
- **HH->bbWW Run 3** (closest: same eu, 13.6 TeV): cut-based ID + PF rel-iso only.
- **ttH-multilepton (2011.03652)**: this IS the source analysis -- "tight leptons"
  are loose leptons passing the MVA cut.

ttH-multilepton lives in **same-sign 2l / 3l / 4l**, where nonprompt leptons are a
*leading* background. Our channel is **OS eu, 82% real tt**, both leptons genuinely
prompt. The technique is imported from a different topology, so the motivation
needs to be stated explicitly rather than assumed.

**Calibration cost** (ttH paper, efficiency section): once "tight" is defined by an
MVA cut, efficiency must be measured by tag-and-probe in Z->ll, cross-checked in an
**OS eu + >=2 jets tt CR** with nonprompt subtracted via an SS eu sideband, and the
DY-vs-tt difference taken as a **1-2% systematic**. That tt CR *is our signal
region*. SFs for these specific 2022EE weights are unlikely to exist publicly.
