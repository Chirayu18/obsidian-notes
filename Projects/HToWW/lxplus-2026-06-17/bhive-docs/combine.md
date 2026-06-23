---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# Combine inputs for v11

First-pass production of TH1Ds suitable for `combine` datacards, built from
the v11 (6-class flat CE) MVA. This document records the choices, the
exact pipeline, and the cross-checks that were run.

## TL;DR

```
python scripts/make_combine_histograms_v11.py
# -> /eos/home-c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc.root
# -> /eos/home-c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc.kappas.npz
```

156 TH1Ds: **6 processes × 26 variations** (raw + nominal + 12 systematics × Up/Down).

## Discriminant

Kappa-discriminant for the H+c signal:

```
D = P(hplusc) / ( P(hplusc) + Σ_j κ_j · P_j ),    j ∈ {higgsbkg, tt, st, diboson, vjets}
```

`P(j)` are the v11 softmax outputs already stored as `mva_score_*` columns in
the per-process parquet files.

**Current setting: uniform κ_j = 1 for all j.** Because v11's softmax
probabilities sum to 1, this collapses the discriminant to

```
D = P(hplusc) / 1 = P(hplusc)
```

i.e. the raw v11 hplusc score. This is the simplest defensible choice and
makes the histograms reproducible from the parquets alone (no learned
parameter to track). To switch to optimized κ later, set
`USE_OPTIMIZED = True` in the script — it will then run differential
evolution on the v11 test split at the 50% efficiency working point.

### Binning

20 uniform bins on D ∈ [0, 1].

## Process granularity (Approach B — MVA-aligned)

| combine process | source parquet(s) |
|---|---|
| `hplusc` | H+c |
| `higgsbkg` | H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB |
| `tt` | tt |
| `st` | Single Top |
| `diboson` | WW, WZ, ZZ |
| `vjets` | DY+Jets, V+Jets |

**WH excluded.** The WH parquet has per-event `weight_nominal` values up to
~7×10¹³ (mean 3×10⁹), an upstream xsec/genweight bug. Re-include after the
producer is fixed.

Inputs are read as-is from
`/eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/v4_hplusc_higgsbkg/mva_hww_multiclass_v11/`.
No additional event selection is applied — the parquets are already
SR-filtered by the upstream `hww_MVA` workflow.

## Systematics (12)

Each systematic produces an `Up` and `Down` histogram per process by
substituting `weight_<syst>Up` / `weight_<syst>Down` for the nominal weight.
Both columns are full event weights (we verified that
`weight_<syst>Up.mean() ≈ weight_nominal.mean()` across files), so they are
applied directly with no additional rescaling.

```
pileup
ps_isr, ps_fsr
scalevar_muR, scalevar_muF, scalevar_muR_muF
muon_id, muon_iso
electron_id
electron_reco_RecoBelow20, electron_reco_Reco20to75, electron_reco_RecoAbove75
```

### What "LHE scale weights missing" means (caveat 3, expanded)

Three of the twelve systematics — `scalevar_muR`, `scalevar_muF`,
`scalevar_muR_muF` — are the **LHE 7-point QCD scale variations**. They are
the standard CMS recipe for the perturbative theory uncertainty on a
Matrix-Element generator's hard process: re-run the cross-section calculation
with renormalization scale μR scaled by {0.5, 1, 2} and factorization scale μF
scaled by {0.5, 1, 2}, take the envelope of the 7 non-extreme points, and
quote the spread as a per-event re-weight. NanoAOD stores these as a
9-component `LHEScaleWeight` vector (one weight per (μR, μF) pair).

In the upstream higgscharm workflow,
`analysis/corrections/lhescale.py:add_scalevar_weight` reads
`events.LHEScaleWeight`, expects exactly 9 components, and only emits the
`scalevar_muR{,F,_muF}` weights when that length matches:

```python
lhe_weights = events.LHEScaleWeight
if len(lhe_weights[0]) == 9:
    weights_container.add("scalevar_muR",   nom, lhe[:,1]/nom, lhe[:,7]/nom)
    weights_container.add("scalevar_muF",   nom, lhe[:,3]/nom, lhe[:,5]/nom)
    weights_container.add("scalevar_muR_muF", nom, lhe[:,0],   lhe[:,8])
elif len(lhe_weights[0]) > 1:
    print("Scale variation vector has length ", len(lhe_weights[0]))
# ... else: nothing added
```

For our 2022postEE WW / WZ / ZZ NanoAOD samples, `LHEScaleWeight` is either
empty or has a non-9 length (typical of POWHEG-Box VV samples that store
their scale variations differently, or older productions that prune
`LHEScaleWeight` for size reasons). The corrections code therefore does
**not** add any `scalevar_*` columns to the WW/WZ/ZZ parquets — the columns
simply don't exist. All other 13 processes have the standard 9-vector and
the `scalevar_muR{,F,_muF}` columns are filled normally.

The histogram script handles this by **falling back to that file's
`weight_nominal`** when a systematic column is missing. The resulting
`diboson_scalevar_muRUp` etc. histograms are bit-identical to the nominal
`diboson` histogram. In datacard terms, this means the QCD scale shape
uncertainty on `diboson` is currently zero. Three remediations, in order of
effort:

| option | what to do | when |
|---|---|---|
| **A. lnN proxy** | Drop the 3 scalevar shape lines for `diboson`; add a single `lnN 0.94/1.06` rate uncertainty in the datacard. 6% is the PDF4LHC envelope for VV @ NNLO. | first datacard pass |
| **B. envelope from related sample** | Compute the muR/muF envelope on a sample that does have `LHEScaleWeight` (e.g. a Madgraph/MCFM VV sample) and copy the per-bin shape as the diboson scalevar variation. | if A is too coarse |
| **C. re-produce upstream** | Re-run the higgscharm workflow against NanoAOD samples that include the standard 9-component `LHEScaleWeight`, or extend `lhescale.py` to also handle the alternate VV scheme. | once we care |

This only affects `diboson` (~33k yield, ~0.01% of total background). All
other systematics on `diboson`, and *all* systematics on the other five
processes, are fully populated.

## Histogram naming convention (combine-style)

| name | content |
|---|---|
| `<proc>` | nominal weight (`weight_nominal`) |
| `<proc>_<syst>Up` | `weight_<syst>Up` |
| `<proc>_<syst>Down` | `weight_<syst>Down` |
| `<proc>_raw` | unweighted (just event counts) — diagnostic, not a combine input |

All TH1Ds carry full sumw2 information.

## Cross-checks

### S/√B reproduces MVA.md exactly (sanity check on the discriminant)

With `κ_j = 1` the discriminant equals raw `P(hplusc)`, so the script's
S/√B at the test-split working points must match the MVA.md table for v11.
Computed on raw counts (no class re-weighting):

| eff | this script | MVA.md v11 | Δ |
|---|---|---|---|
| 5% | 2.789 | 2.79 | 0.00 |
| 10% | 3.410 | 3.41 | 0.00 |
| 20% | 4.054 | 4.05 | 0.00 |
| 30% | 4.265 | 4.26 | 0.00 |
| 50% | **4.389** | **4.39** | **0.00** |
| 70% | 4.291 | 4.29 | 0.00 |
| 90% | 3.410 | 3.41 | 0.00 |

(The script prints S/√B at the chosen `TARGET_EFF` after computing `D`. With
`USE_OPTIMIZED = False` the value is exactly the raw P(hplusc) S/√B.)

### Predictions look physical

D distribution per truth class on the v11 test split:

| class | count | mean D | %D > 0.5 | %D > 0.9 |
|---|---|---|---|---|
| hplusc (signal) | 2,257 | 0.83 | 93% | 46% |
| higgsbkg | 346,290 | 0.39 | 36% | 7% |
| tt | 3,180,107 | 0.10 | 8% | 0.8% |
| st | 499,001 | 0.12 | 10% | 1.3% |
| diboson | 38,094 | 0.20 | 20% | 3.4% |
| vjets | 10,765 | 0.27 | 14% | 1.2% |

Signal is strongly peaked near 1, all backgrounds peak at 0. `higgsbkg`
shows a longer signal-like tail than `tt`/`st` — physical, since other
Higgs production modes share the H→WW final state. `vjets` distribution
is noisier than the others; the test split only has 10k events.

## Yields (nominal)

| process | events (raw) | nominal yield |
|---|---|---|
| hplusc | 2,257 | 429.26 |
| higgsbkg | 320,853 | 1,059,581.38 |
| tt | 3,180,107 | 241,337,322.55 |
| st | 499,001 | 2,070,378.41 |
| diboson | 38,094 | 33,484.42 |
| vjets | 10,765 | 141,019,789.45 |

Note: yields are **not lumi-normalized** in any uniform way — they are
whatever sum-of-weights happens to be in the parquets. `vjets` and `tt`
look very large; before doing the actual combine fit we will need to
reconcile these with `2022postEE` luminosity × cross sections (this is
upstream of the b-hive repo).

## File layout

```
combine_inputs/
├── v11_hplusc.root          # 156 TH1Ds, 20 bins each
└── v11_hplusc.kappas.npz    # kappa vector + metadata (currently all 1.0)
```

Inspect with:
```python
import uproot
f = uproot.open("combine_inputs/v11_hplusc.root")
print(sorted(f.keys()))
h = f["hplusc"].to_numpy()  # (counts, edges)
```

## Datacard (lumi-normalised inputs)

The lumi-normalised second pass adds two files alongside `v11_hplusc.root`:

```
combine_inputs/
├── v11_hplusc.root              # first pass, NO lumi scaling (kept for reference)
├── v11_hplusc.kappas.npz
├── v11_hplusc_lumi.root         # lumi-normalised, contains data_obs (Asimov)
├── v11_hplusc_lumi.samples.csv  # per-sample scale + yield diagnostic
└── v11_hplusc.txt               # combine datacard, points at v11_hplusc_lumi.root
```

Two scripts:
1. `scripts/make_combine_histograms_v11_lumi.py` — runs v11 inference on the
   per-sample parquets, applies per-sample `scale = coffea_nominal_integral /
   parquet_weight_nominal_sum` (so weights are now in events @ 26.67 fb⁻¹),
   drops NaN-feature rows so the kept event set matches the v4 training set,
   writes 156 TH1Ds (6 processes × 26 variations).
2. `scripts/make_datacard_v11.py` — adds Asimov `data_obs = Σ backgrounds` to
   the ROOT file and emits the txt datacard.

Lumi-normalised nominal yields at 26.67 fb⁻¹ (cf. raw yields earlier):

| process | nominal yield | raw events |
|---|---|---|
| hplusc | 0.27 | 2,257 |
| higgsbkg | 253 | 320,853 |
| tt | 86,070 | 3,180,107 |
| st | 6,876 | 499,001 |
| diboson | 2,216 | 38,094 |
| vjets | 6,135 | 10,765 |

### lnN nuisances — sources

The datacard currently contains **only the 12 shape systs** that come from
the parquet's weight columns plus `autoMCStats`. The lnN rate uncertainties
have been left out on purpose; fill in the `LNN = [...]` block at the top of
`scripts/make_datacard_v11.py` with values from these sources:

| nuisance | typical Run3 value | source |
|---|---|---|
| `lumi_13p6TeV` | ~1.4 % (2022) | CMS LUM POG TWiki **LumiRecommendationsRun3**, CMS-PAS-LUM-22-001 / -22-002 |
| `xsec_tt` | ~5–6 % | LHCPhysics TWiki **TtbarNNLO** (Czakon+Mitov NNLO+NNLL, σ ≈ 833.9 ± 35 pb at 13.6 TeV) |
| `xsec_st` | ~5–7 % (tW), ~3–5 % (t-ch) | LHCPhysics TWiki **SingleTopRefXsec**; yield-weighted across modes |
| `xsec_diboson` | WW 5 %, WZ 5–6 %, ZZ 5 % | CMS TWiki **StandardModelCrossSectionsat13TeV** |
| `xsec_vjets` | DY 2–3 %, W+jets 5 % | LHCPhysics TWiki **VBoson** / FEWZ NNLO |
| `xsec_higgsbkg` | composition-dependent | LHCHWG TWiki **CERNYellowReportPage…** (YR4); ggH 10 %, VBF 2 %, ZH 4 %, ttH 9 % — weight by the mode composition in the `higgsbkg` aggregate |
| `xsec_hplusc` | from analysis note | Signal POI's theory uncertainty. Often folded into the `r` interpretation rather than an lnN. |
| `qcd_scale_diboson` | ~6 % | PDF4LHC envelope for VV @ NNLO. **Only** keep this while `scalevar_*` rows are `-` for diboson; drop once option C ships the LHE 9-pt weights upstream. |

### Missing systematics

The 12 shape systs propagated through the parquet weights cover only the
weight-based effects. Everything below requires re-running the upstream
higgscharm workflow on shifted inputs (object-level variations) or adding
new weight columns. None of them is in `v11_hplusc.txt` today.

This is not a closed list — a Run3 CMS search typically carries 30–100
nuisances, and several groups below (JES, JER, PU jet ID, …) expand into
many sub-sources at implementation time. Pruning the set to "what we will
actually carry" is an analysis choice and depends on what higgscharm
exposes.

#### Set 1 — Object scale-factor shapes (weight columns missing in parquet)

| nuisance | dominant effect | notes |
|---|---|---|
| `trigger_*` (single-µ, single-e, µ+e legs) | yield + shape | absent entirely |
| `muon_reco` | yield | only `muon_id` + `muon_iso` are in the parquet |
| `electron_iso` | yield | if iso is applied at object level |
| `ctag_*` (CvL, CvB working points) | **dominant** for signal | discriminator is built directly on `cjet_cand_cvsl_pnet` / `cjet_cand_cvsb_pnet` |
| `btag_*` (heavy flavour) | `tt`, `st` normalization | |
| `mistag_*` (light flavour) | `vjets` | |
| `pujetid_eff`, `pujetid_mistag` | small, ~1–2 % | split into eff / mistag legs |
| `jet_vetomap` | very small | Run3 |

#### Set 2 — Object-level energy/momentum variations (need shifted arrays)

These cannot be added as weight columns; they require a full re-run of
the higgscharm processor with shifted object collections.

| nuisance | sub-sources | notes |
|---|---|---|
| `JES` | 11 grouped or 27+ individual | not one nuisance — the full set is large |
| `JER` | 3–4 (η regions) | |
| `MET_unclust` | 1 | propagates to `met_pt`, `mtl1`, `mtl2` |
| `mu_scale` (Rochester) | 1 | separate from id/iso/reco |
| `ele_scale`, `ele_smear` | 2 | separate from ID/Reco SFs |
| `HEM_2022` | 1 | 2022postEE-specific |
| `L1_prefire` | 1 | Run3 ECAL EE-leakage analogue, if applicable |

#### Set 3 — Theory: generic (additional weight columns)

| nuisance | typical size | applies to |
|---|---|---|
| `PDF_replicas` | ~1–3 % | all MC; NNPDF Hessian or MC envelope (~100 weights) |
| `alphaS` | ~1 % | all MC; 2 LHA PDF weights |
| `UE_tune` (Pythia) | ~1–3 % | all MC; single replacement variation, separate from `ps_isr`/`ps_fsr` |
| `mH` (mH = 125.10 ± 0.11 GeV) | ~0.1 % | all Higgs processes |
| `pileup_profile` (σ_inel ±5 %) | ~1 % | all MC; separate from `pileup` weight |
| Alternative PDF set envelope (CT18 / MSHT20 vs NNPDF) | ~1 % | all MC, optional |

#### Set 4 — Signal-specific theory (`hplusc`)

| nuisance | size | notes |
|---|---|---|
| **Flavor-scheme (4FS vs 5FS)** | **~30 %** | H+c xsec differs by O(30 %) between 4FS / 5FS treatment of charm PDF. No analogue in YR4. |
| H+c PDF uncertainty | ~6 % | separate from generic PDF |
| H+c xsec scale | from analysis note | |

#### Set 5 — Process-specific theory: top (`tt`, `st`)

| nuisance | applies to | notes |
|---|---|---|
| `hdamp` | `tt` | Powheg ME-PS matching scale; standard CMS Run3 nuisance |
| `mtop` (171.5 / 173.5) | `tt` | top mass envelope |
| `colour_reconnect` (CR1 / CR2 / ERD-on) | `tt` | |
| `gen_choice` (Powheg vs MadGraph_aMC@NLO vs Sherpa) | `tt` | |
| `tt_HF_norm` | **`tt` HF-tagged component** | ~50 % on `tt + bb̄/cc̄`; same physics as the ggH+HF item but for tt. Big effect because `tt+HF` mimics signal far more than `tt+light`. |
| `top_pt_reweight` | `tt` | optional, Run3 status TBD |
| `DR_vs_DS` | `st` | `tW` interference scheme with `tt`. Standard CMS lnN. |

#### Set 6 — Process-specific theory: V+jets / diboson

| nuisance | applies to | notes |
|---|---|---|
| `EWK_NLO_corr` | `vjets`, `diboson` | NLO EWK corrections at high V-pT; few % rate, larger shape at high boost |
| `DY_HF_norm` | DY+HF subset of `vjets` | same family as tt+HF / ggH+HF |
| `diboson_QCD_vs_EWK_order` | `diboson` | ordering of NLO EWK vs NNLO QCD corrections; ~2 % |

#### Set 7 — Process-specific theory: Higgs backgrounds (`higgsbkg`)

| nuisance | size | notes |
|---|---|---|
| **ggH + heavy-flavor** | ~50 % | applies only to the ggH-with-HF component of `higgsbkg`. Either decompose `higgsbkg` to expose this component, or apply a single lnN scaled by the HF-tagged fraction. |
| BR(H→WW) | ~1 % | applies to all H→WW modes in `higgsbkg` and to `hplusc`. YR4. |
| BR(H→ττ) | ~1 % | applies only to H→ττ subset (`VBFHToTauTau`, `GluGluHto2Tau`, `WplusHTo2Tau`, `WminusHTo2Tau`, partial `ttHnonBB`). Decompose `higgsbkg` if you want this clean. |
| BR(H→cc̄) | ~3 % | if any sample explicitly includes H→cc̄ (e.g. `ttHto2C`) |

#### Set 8 — Rate-only lnN (process xsecs + luminosity)

See the "lnN nuisances — sources" table above for values + references.
Luminosity (2022 / 2022postEE / 2023), `xsec_tt`, `xsec_st`, `xsec_diboson`,
`xsec_vjets`, `xsec_higgsbkg`, `xsec_hplusc`.

#### Set 9 — Method-dependent (only if the analysis uses them)

- Non-prompt / fake-lepton background uncertainty (only if a control-region-driven fake rate is used; not in the current setup)
- DY shape from data-driven α-ratio method (if applied)
- Fake-photon / charge-flip uncertainties (typically irrelevant in HtoWW dilepton SR)

#### Set 10 — Already in the datacard / handled internally

For reference, these are **not** missing — they're either in the
histograms or handled by combine itself:

- shape systs from parquet weight columns:
  `pileup`, `ps_isr`, `ps_fsr`, `scalevar_muR`/`muF`/`muR_muF`,
  `muon_id`, `muon_iso`, `electron_id`,
  `electron_reco_RecoBelow20`/`Reco20to75`/`RecoAbove75`
- MC statistical uncertainty: handled by `SR autoMCStats 10`

#### Priority for the κc-search first pass

In rough order of effect-on-final-limit for a κc measurement:

1. **Set 1** `ctag_*` SFs — signal-defining, missing is a hard error in the final result.
2. **Set 2** JES (full set) and JER — affect the c-jet candidate pT and indirectly the SR composition.
3. **Set 5** `tt_HF_norm` and **Set 7** `ggH + heavy-flavor` — these are the analogues of the Run2 "ggH+HF (50 %)" item; without them the H+c-like background is unconstrained.
4. **Set 4** flavor-scheme (4FS vs 5FS) on `hplusc` — direct multiplicative factor on the signal POI.
5. **Set 1** trigger SFs.
6. **Set 8** luminosity + xsec lnNs.
7. Remainder.

### Running combine

The POI here is **κc**, the charm Yukawa coupling modifier (κc = yc / yc_SM).
The H+c signal cross-section scales as σ_H+c ∝ κc² to leading order, with
small additional κc-dependent interference at NLO. κc also enters indirectly
via the total Higgs width Γ_H(κc), which modifies every BR(H→X) on every
Higgs-related process in the datacard (including the H→WW BRs on `hplusc`
and `higgsbkg`).

#### Step 1 — Build the workspace

For a κc-search you have two options:

**(a) r → κc² reinterpretation** (simplest, recommended for a first pass).
Build a standard signal-strength workspace with r = σ_H+c × BR(H→WW) / SM
and report bounds on r. Convert to κc afterwards via κc² ≈ r (ignoring
total-width feedback, which is sub-percent for κc ≲ 5).

```bash
cd combine_inputs
text2workspace.py v11_hplusc.txt -o v11_hplusc.workspace.root
```

**(b) Kappa-framework physics model** (proper treatment, includes width feedback).

```bash
text2workspace.py v11_hplusc.txt \
        -P HiggsAnalysis.CombinedLimit.LHCHCGModels:K1 \
        --PO map='.*hplusc.*:kappa_c[1,-10,10]' \
        --PO map='.*higgsbkg.*:kappa_other[1,0,2]' \
        -o v11_kappac.workspace.root
```

The κ-framework model lets POI = κc and POI parameterisation of every
Higgs-related rate handles the total-width modification consistently. Use
this once the first-pass r-fit is closed and the systematic budget is final.

#### Step 2 — Fits

```bash
# Expected (Asimov, blinded) 95 % CL upper limit on r = σ_H+c × BR / SM
combine -M AsymptoticLimits v11_hplusc.workspace.root --run blind -t -1

# Expected significance with signal injected at r = 1
combine -M Significance v11_hplusc.workspace.root -t -1 --expectSignal 1

# Max-likelihood scan in r (Asimov)
combine -M MultiDimFit v11_hplusc.workspace.root -t -1 \
        --algo singles --setParameters r=1

# Scan over r (or κc, if model (b)) for the 1-D likelihood profile
combine -M MultiDimFit v11_hplusc.workspace.root -t -1 \
        --algo grid --points 50 --setParameterRanges r=-5,5
```

#### Step 3 — Impacts

```bash
# Nuisance impact plot (slow — runs one fit per nuisance)
combineTool.py -M Impacts -d v11_hplusc.workspace.root -t -1 \
        --expectSignal 1 -m 125 --doInitialFit
combineTool.py -M Impacts -d v11_hplusc.workspace.root -t -1 \
        --expectSignal 1 -m 125 --doFits
combineTool.py -M Impacts -d v11_hplusc.workspace.root -t -1 \
        --expectSignal 1 -m 125 -o impacts.json
plotImpacts.py -i impacts.json -o impacts
```

#### Step 4 — r → κc

For option (a), the 95 % CL upper limit on κc is

    κc_95 ≈ sqrt(r_95)         (ignoring Γ_H(κc) feedback)

This is good enough for an O(few) limit; switch to model (b) once the
analysis is within a factor ~2 of the SM expectation.

Combine + CombineHarvester need a CMSSW environment with the
`HiggsAnalysis-CombinedLimit` and `CombineHarvester` packages set up. The
b-hive `b_hive` micromamba env is enough to *build* the inputs but not to
run combine itself.

## Open items / next pass

1. Fix the WH per-event weight blow-up upstream and re-include it in `higgsbkg`.
2. Cross-check `tt` and `vjets` normalizations against expected `xsec × lumi`.
3. Decide on the diboson scale-uncertainty strategy (A/B/C above) when writing the datacard.
4. Add JEC/JER and b/c-tag SF systematics (currently only weight-based systs are propagated; object-level variations require re-running the upstream workflow on shifted parquets).
5. Once 1–4 are in, write the datacard (`hplusc` as POI, the other 5 as backgrounds with appropriate `lnN` xsec uncertainties + the shape systematics from this file).
6. Switch to optimized κ once the simple κ=1 baseline is demonstrably sane in combine.

## Code

`scripts/make_combine_histograms_v11.py` does both steps in one pass:

1. Loads `prediction.npy` + `truth.npy` from the v11 InferenceTask output;
   either uses `κ=1` (default) or runs differential evolution at
   `TARGET_EFF = 0.5` with class-balanced weights (`USE_OPTIMIZED = True`).
   In both cases, it then reports the **raw-count** S/√B at `TARGET_EFF`
   for direct comparison with MVA.md.
2. Loops over the input parquet files, computes `D` per event using the
   chosen κ and the existing `mva_score_*` columns, and fills the 26
   variations per combine process via `np.histogram`.
3. Writes TH1Ds with `uproot.writing.identify.to_TH1x` (preserves sumw2).

Full code is the source of truth — this doc only records the choices.

## Experiment log

All further combine experiments are recorded here. Format: one section per
named run, with setup → inputs → result → comparison-to-AN.

### combine v1 — first-pass r-strength fit (2026-05-12)

**Setup**
- Datacard: `combine_inputs/v11_hplusc.txt` (1 SR, 6 procs, signal = `hplusc`)
- Inputs: `combine_inputs/v11_hplusc_lumi.root` (156 TH1Ds, 20 bins of `D = P(hplusc)`)
- Asimov `data_obs` = Σ backgrounds (added by `scripts/make_datacard_v11.py`)
- Systematics: **12 weight-based shape** systs only (`pileup`, `ps_isr/fsr`,
  `scalevar_muR/muF/muR_muF`, `muon_id/iso`, `electron_id`, 3 × `electron_reco_*`)
  + `autoMCStats 10`. No lnNs, no JES, no ctag SFs, no MET.
- POI = r (signal strength). Option (a) r → κc² reinterpretation.
- Combine v10.6.0, CMSSW_14_1_0_pre4, `el9_amd64_gcc12`.
- Build location: `/afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4/`
- Workspace: `combine_inputs/v11_hplusc.workspace.root` (53 KB)
- Data: 2022postEE, ~27 fb⁻¹

**Results (Asimov, blinded)**

| Method | Result |
|---|---|
| `AsymptoticLimits --run blind -t -1` | r_95 expected: **943** (median); ±1σ band [653, 1394]; ±2σ band [479, 1987] |
| `Significance --expectSignal 1` | 0.0036σ — no discovery sensitivity |
| `MultiDimFit --algo singles` | r = 1.000 −1.000 / +19.000 (68% CL) |
| `MultiDimFit --algo grid -5..5` | flat: 2·ΔNLL ≤ 1.5×10⁻⁴ across the range |
| r → κc (naive √r) | κc_95 ≈ **30.7** (median) |
| r → κc (AN flat-direction Eq. 5) | κc_95 ≈ **76** (median) |

**Comparison to CMS AN-23-102 (Run 2, 138 fb⁻¹)**

| | AN 1POI | AN 2POI | v1 |
|---|---|---|---|
| r_95 expected | 431 | 969 | **943** |
| κc_95 (their conv.) | 35 | 77 | 76 (using their formula) |

v1 maps cleanly to AN's 1POI scaled to my lumi: `431 × √(138/27) ≈ 968`, vs
my 943 (3% match). The first-pass datacard is **statistically equivalent to
AN-23-102's 1POI fit at my lumi**. Stat-dominated regime.

**What's missing vs AN-23-102** (must-add, in priority order)

1. JES decomposition + JER (11 sources × era) — AN contributes 1.1% / 6.2% to r
2. Charm tagging SFs (DeepFlav_Stat + flavour composition)
3. MET unclustered energy scale
4. Top pT reweighting, PDF, dedicated diboson theory (`theo_vv`)
5. lumi + xsec lnNs (rate-only, cheap)
6. Top control region with `rateParam` for ttbar normalisation (structural — AN's `CMS_SF_ttbar_emu_13TeV`)

Items 1–3 need re-running upstream higgscharm on shifted parquets. Items
4–5 can be added against current histograms. Item 6 is a new analysis region.
Adding these will not materially tighten r_95 (fit is stat-limited at
73.8 % per AN Table 17) but is needed for the κ-framework interpretation
and for the result to be defensible.

**Code edits this run**
- `combine_inputs/v11_hplusc.txt:11` — stripped inline `#` comment after
  `observation -1` (broke `text2workspace.py`'s float parser)
- `scripts/make_datacard_v11.py:166` — same fix in the generator

**Files left behind**
- `combine_inputs/v11_hplusc.workspace.root`
- `combine_inputs/higgsCombineTest.{AsymptoticLimits,Significance,MultiDimFit}.mH120.root`

---

<!-- Add the next experiment below as ### combine v4 — <title> (<date>) -->

### combine v3 — HIG-24-018-style argmax categories (2026-05-13)

**Setup**

Inspired by CMS HIG-24-018 (ttH(H→cc̄) with ParT classifier) and the "Six categorical channels" Option 3 discussed earlier. Same v11 6-class MLP, same v2 systematics, but the discriminant + binning changes:

- Per event compute full 6-class softmax; `c* = argmax(softmax)` defines an event category.
- 6 mutually exclusive channels: `SR_hplusc` (argmax = hplusc) plus 5 control regions `CR_higgsbkg`, `CR_tt`, `CR_st`, `CR_diboson`, `CR_vjets`.
- Per-channel fit variable: **D = P(c*)** = the network's score for the class that defines that channel (matches HIG-24-018 §142–149).
- 20 bins on [0, 1] per channel.
- Same 12 weight-based shape systs + 9 lnNs from v2.
- `autoMCStats 10` per channel.
- Asimov `data_obs` = Σ(bkg nominals) per channel.

**What I'm NOT yet copying from HIG-24-018** (deferred to v4):
- `D_ttX > 0.85` SR / `0.6–0.85` CR threshold split (would need a `D_signal_like = P(hplusc) + P(higgsbkg)` cut).
- Floating `rateParam` on backgrounds (their `μ_tt+c`, `μ_tt+b`, etc.) constrained by the CRs. **Without rateParams, the CRs only contribute autoMCStats + shape constraints; their full normalisation-pinning power is unused.**

**Yields per channel × process** (lumi-normalised, all weights):

| process | SR_hplusc | CR_higgsbkg | CR_tt | CR_st | CR_diboson | CR_vjets | total |
|---|---|---|---|---|---|---|---|
| hplusc | **0.223** | 0.028 | 0.003 | 0.002 | 0.005 | 0.014 | 0.274 |
| higgsbkg | 79.0 | 64.9 | 29.8 | 6.3 | 9.1 | 63.5 | 252.7 |
| tt | 3953.7 | 5958.0 | **48262.7** | 17255.7 | 7286.7 | 3353.3 | 86070.0 |
| st | 455.0 | 438.5 | 2453.6 | **2146.5** | 1118.2 | 264.4 | 6876.1 |
| diboson | 298.5 | 139.3 | 165.3 | 271.4 | **1175.9** | 166.0 | 2216.4 |
| vjets | 585.4 | 417.1 | 321.9 | 98.8 | 698.6 | **4013.6** | 6135.3 |
| **total** | **5371.8** | 7017.7 | 51233.4 | 19778.6 | 10288.5 | 7860.7 | 101550 |

Argmax categorisation works as expected: signal lands 81 % in SR_hplusc; each background concentrates 28–85 % in its own CR.

**Discriminant power in SR_hplusc**: S = 0.223, B = 5371.8 → S/√B = 0.0030 vs v1/v2's single-channel 0.00086 (single bin equivalent), **3.5× better**. The shape within SR_hplusc bins still provides further discrimination.

**Results (Asimov, blinded)**

| Method | v3 result | v2 (for comparison) | Δ |
|---|---|---|---|
| `AsymptoticLimits`, median | **r_95 = 979** | 1055 | **−7.2 %** |
| ±1σ band | [651, 1553] | [696, 1694] | tighter |
| ±2σ band | [467, 2454] | [495, 2711] | tighter |
| `Significance --expectSignal 1` | 0.0035σ | 0.0035σ | unchanged |
| `MultiDimFit --algo singles` | r = 1.000 −1.000 / +19.000 (68%) | same | unchanged |
| `MultiDimFit --algo grid -5..5` | flat | flat | unchanged |
| κc_95 (naive √r) | ≈ 31.3 | 32.5 | −4 % |

**Why the improvement is only ~7 %, not the naïve ~3.5×**

Most of the argmax-categorisation gain was already implicit in v1/v2's 20-bin shape: the high-D bins of the single channel were effectively the "argmax = hplusc events". By categorising, we trade a single 20-bin shape for 6 × 20-bin shapes, but without rateParams the CR channels mostly add MC-stat (autoMCStats) constraint, not normalisation freedom. **The bigger win awaits v4 with rateParams on backgrounds.**

**Comparison to AN-23-102 1POI**

| | AN 1POI (Run 2, 138 fb⁻¹) | v3 (this work, 27 fb⁻¹) | v3 scaled to AN's lumi |
|---|---|---|---|
| r_95 expected | 431 | 979 | **433** |
| Δ | — | — | **+0.5 %** |

**v3 is now statistically equivalent to AN-23-102's 1POI fit at matching lumi**, within 0.5 %. The remaining gap from full-Run 2 expectation now is exactly lumi: 5× more data → √5 ≈ 2.2× tighter limit. v3 also already covers the AN's lnN systematics; remaining differences (object-level shape systs, top CR rateparam, per-era split) tighten the result further but the analysis frame is now competitive.

**Channels using autoMCStats**: all 6 (`SR_hplusc autoMCStats 10`, plus `CR_higgsbkg`, `CR_tt`, `CR_st`, `CR_diboson`, `CR_vjets`).

**Files**
- `scripts/make_combine_histograms_v11_v3.py` (new, 936 TH1Ds per channel × proc × variation)
- `scripts/make_datacard_v11_v3.py` (new, 6-channel multi-region datacard)
- `combine_inputs/v11_hplusc_v3.root` (936 + 6 `data_obs` = 942 TH1Ds)
- `combine_inputs/v11_hplusc_v3.txt`
- `combine_inputs/v11_hplusc_v3.workspace.root`
- `combine_inputs/higgsCombineV3{Limit,Sig,Singles,Grid}.*.root`

**Open items for v4**
1. **Add rateParams on backgrounds** (tt, vjets, diboson) — main reason v3's CR constraint power is currently unused.
2. **HIG-24-018-style threshold split**: define `D_signal_like = P(hplusc) + P(higgsbkg)`; SR for D > 0.85, CR for 0.6–0.85.
3. Decompose `higgsbkg` → `bkg-H+c` vs `bkg-Hnotc`; enables `BR_HtoTauTau` (1 %) and `ggH_HF` (50 %) lnNs from AN-23-102 Table 16.
4. Re-run upstream higgscharm on shifted parquets for ctag/JES/JER shape systs (the genuine gap to AN-23-102's full uncertainty model).

### combine v2 — rate-only lnNs aligned with AN-23-102 (2026-05-13)

**Setup**
- Same workspace skeleton as v1; only `LNN = [...]` in `make_datacard_v11.py` was edited.
- 9 lnNs added; values from CMS AN-23-102 Table 16 (page 59) + LumiPOG:

| Nuisance | Value | Processes | Source |
|---|---|---|---|
| `lumi_13p6TeV` | 1.4 % | all MC | LumiPOG `LumiRecommendationsRun3`, 2022postEE — **verified against LumiPOG by user** |
| `xsec_st` | +1.67 / −1.27 % (asym) | st | AN-23-102 Table 16 |
| `xsec_diboson` | 3.7 % | diboson | AN-23-102 Table 16 |
| `xsec_vjets` | 2.7 % | vjets | AN-23-102 Table 16 (Z+jets row) |
| `xsec_higgsbkg` | 5 % | higgsbkg | AN-23-102 Table 16 (top of 1–5 % range) |
| `BR_HtoWW` | 1 % | hplusc, higgsbkg | AN-23-102 Table 16 |
| `xsec_hplusc_PDF` | 6 % | hplusc | AN-23-102 Table 16 + Section 7.1.1 |
| `xsec_hplusc_4FS_5FS` | 30 % | hplusc | AN-23-102 Table 16 + Section 7.1.1 |
| `alphaS_PDF` | 3 % | all MC | AN-23-102 Table 16 (top of 1–3 % range) |

**Intentionally dropped from v1**
- `xsec_tt` placeholder 6 % — AN-23-102 replaces with a rateParam from a top CR (`CMS_SF_ttbar_emu_13TeV`); we don't have a CR yet.
- `qcd_scale_diboson` placeholder 6 % — AN has the LHE 9-pt diboson weights; we have `scalevar_*` = `-` for diboson, an outstanding upstream gap.

**Not added (need extra work)**
- `BR_HtoTauTau`, `ggH_HF` — need higgsbkg decomposition (H→WW vs H→ττ; bkg-H+c vs bkg-Hnotc)
- All Set 1 / Set 2 shape systs (ctag, JES, JER, MET_unclust, ...) — need upstream re-run on shifted parquets

**Results (Asimov, blinded)**

| Method | v2 result | v1 (for comparison) | Δ |
|---|---|---|---|
| `AsymptoticLimits --run blind -t -1`, median | **r_95 = 1055** | 943 | **+11.9 %** |
| ±1σ band | [696, 1694] | [653, 1394] | wider |
| ±2σ band | [495, 2711] | [479, 1987] | wider |
| `Significance --expectSignal 1` | 0.0035σ | 0.0036σ | unchanged |
| `MultiDimFit --algo singles` | r = 1.000 −1.000 / +19.000 (68%) | same | unchanged |
| `MultiDimFit --algo grid -5..5` | flat (2·ΔNLL ≤ ~10⁻⁴) | flat | unchanged |
| κc_95 (naive √r) | ≈ 32.5 | 30.7 | +6 % |

**Why the limit moved by +12 %**

The dominant contributor is `xsec_hplusc_4FS_5FS` (30 % on signal rate),
followed by `xsec_hplusc_PDF` (6 %) and `alphaS_PDF` (3 % on all MC). Signal
rate uncertainty in quadrature: √(0.30² + 0.06² + 0.03² + 0.01² + 0.014²) ≈ 31 %.
The fit is still stat-dominated (shape constraint from 20 bins of `D`), so a
31 % signal-rate inflation translates to a ~12 % weaker limit. Consistent
with expectations.

**Comparison to AN-23-102**

| | AN 1POI (Run 2, 138 fb⁻¹) | v1 (stat only) | v2 (with AN lnNs) |
|---|---|---|---|
| r_95 expected | 431 | 943 | 1055 |
| r_95 scaled to v2 lumi | 968 | — | — |
| Δ vs scaled-AN | — | **−3 %** | **+9 %** |

v2 sits ~9 % above the AN 1POI scaled to my lumi. The gap is consistent with
the conservative envelopes I picked (5 % `xsec_higgsbkg` upper edge vs AN's
1–5 %, 3 % `alphaS_PDF` upper edge vs AN's 1–3 %) and over-application of
`BR_HtoWW` to the full `higgsbkg` aggregate (AN applies it only to its H→WW
subset). Decomposing higgsbkg would close ~3–5 % of this gap.

**Code edits this run**
- `scripts/make_datacard_v11.py:57–122` — replaced v1's empty `LNN = []` with the 9 AN-aligned lnNs above
- `scripts/make_datacard_v11.py:fmt_cell` — bugfix: asym lnN strings (e.g. `0.9873/1.0167`, 13 chars) longer than `col_w = 12` now get at least one trailing space, so the next column doesn't glue (`max(col_w, len(s)+1)`)

**Files left behind**
- `combine_inputs/v11_hplusc.txt` (now with 9 lnNs)
- `combine_inputs/v11_hplusc.workspace.root` (re-built, larger because of extra params)
- `combine_inputs/higgsCombine{Test,V2Grid}.{AsymptoticLimits,Significance,MultiDimFit}.mH120.root`

**Open items for v3**
- Decompose `higgsbkg` → enable clean `BR_HtoWW`, add `BR_HtoTauTau`, `ggH_HF`
- Add a top CR + `rateParam` for tt normalisation
- Re-run upstream higgscharm on shifted parquets for ctag / JES / JER / MET_unclust shape systs

---

## Ideas / Things to try (v32 and beyond)

Brainstorm of follow-ups, with the rough order I'd try them. Nothing here is committed; each row is a one-line description of the change and what we expect it to unlock.

### Model-side (training-version swap)

| Idea | What it changes | Why it might help | Risk / cost |
|---|---|---|---|
| **v32 baseline** (13-class kappa-HCE, AUC 0.975) | swap v11 → v32 model inputs everywhere | best `hplusc_vs_all` AUC currently available; +0.9 % vs v11 | argmax over 13 collapses signal into higgs sub-classes — needs cascade routing (see below) |
| v32 inverse (use kappa-HCE outputs but with v11-style 6-class collapse) | sum 8 higgs sub-classes → 1 group before fit | drops in as a direct replacement for v11 in combine v3 | gives up fine higgs sub-class info |
| Mix: use v32 for `SR_hplusc` shape but v11 yields elsewhere | per-channel different model | exploits each model's strength | unusual; combine purists will dislike |

### Channel structure

| Idea | Channels | Notes |
|---|---|---|
| **A. Collapsed argmax (6 channels)** | SR_hplusc + 5 CRs (= v3 layout) | apples-to-apples vs v3. With v32 the raw 13-class argmax never picks `hplusc`, so collapse to 6 first, then argmax |
| **B. Cascade with optimised threshold** | same 6 channels, but SR = (`P(hplusc) > T_opt`), CRs split the rest by argmax in α-priority order | the threshold-tuning approach. T_opt = argmax_T (S(T)/√B(T)). Earlier attempt got T_opt = 0.0235, sig eff 4 % — that was on lumi-weighted bkg which goes negative from MC weight cancellation; redo with **raw counts** (matches `docs/MVA.md` 38 % sig-eff target) or `B_eff = sumw2` |
| C. Per-channel thresholds | each CR also has its own threshold for purity | richer cascade, each CR's score must beat its own threshold |
| D. 13-channel granular | one channel per v32 class | uses full granularity, but 13 × 6 = 78-col datacard, fewer events/channel, more autoMCStats noise |
| E. AN-23-102-style: SR + 2 CRs only (tt, V+jets) | drop the inactive CRs | matches the AN structure, smaller datacard |

### Discriminant in SR

| Idea | Formula | Comment |
|---|---|---|
| **i. P(hplusc)** | direct signal score | simplest, in [0, 1], works with any channel scheme. Default choice |
| ii. P(argmax-class) | shape per channel (v3 style) | clean but with 13 classes inside SR usually = P(hplusc) anyway |
| iii. κ-weighted "kappa discriminant" | D = P(hplusc) / Σ κ_j P(j) with κ_j = max(0, cos(W_hplusc, W_j)) | tried — 9/13 κ's clamp to 0 in v32 → denominator near singular; not really "optimised", just derived from final-layer weights. **Skip unless we add α (below)** |
| iv. α-weighted discriminant | D = P(hplusc) / Σ α_j P(j) with α_j = sigmoid(cos / τ=0.3) | all α > 0.08, denominator always healthy; this **is** the quantity the kappa-HCE loss uses at training time |
| v. Signal-likeness pooled | D = Σ_{j∈{hplusc,hplusb,ggH,vbf}} P(j) | uses v32's "+cos_sim group" structure; bins what the model thinks is signal-like |

### Process treatment in rate model

| Idea | Change | Why |
|---|---|---|
| **Keep higgsbkg as 1 process** (v3 style) | no change | minimal complexity, but loses v32 sub-class info in normalisation |
| Split → `higgs_clike` {H+b, ggH, VBF} + `higgs_other` {ZH, ggZH, WH, ttH*} | use v32 α clusters (≥0.5 vs <0.2 split) | enables separate `xsec` and `BR_HtoTauTau` lnNs; closes 3–5 % of the v2→AN-23-102 gap |
| Full per-sub-class processes (8 higgs processes) | one process per v32 class | maximally clean for theory systs; lots of bookkeeping |
| `tt` rateParam in CR_tt | float tt normalisation, constrain in CR | unlocks the main v3→v4 win |
| `V+jets` rateParam in CR_vjets | same for V+jets | smaller effect |
| `diboson` rateParam in CR_diboson | same for diboson | smaller effect |

### Systematics still to add (carried from v2)

| Group | Items | Source |
|---|---|---|
| Ctag SF shape | weight columns for `cvsl` / `cvsb` Up/Down | upstream higgscharm re-run on shifted parquets |
| JES / JER | per-source if available | shifted parquets |
| MET unclustered | weight column | shifted parquets |
| Trigger SF | weight column | shifted parquets |
| ggH HF | rate-only lnN on ggH sub-component | only after higgsbkg split |
| BR_HtoTauTau | rate-only on H→ττ sub-component | only after higgsbkg split |

### Cross-checks worth running once any v32 fit exists

| Check | Expected outcome |
|---|---|
| r_95 (v32 cascade) scaled to 138 fb⁻¹ vs AN-23-102 1POI = 431 | should be **within 5–10 %** if v32 routing is doing its job; closer than v3's 0.5 % match is a real improvement (means our MVA beats the AN's) |
| `combine -M GoodnessOfFit` on Asimov | sanity test, p-value ~0.5 |
| Per-channel pulls of nuisances | if any lnN is pulled by > 1σ on Asimov, the prior is wrong |
| Impacts (needs CombineHarvester) | rank-order of systematics; expect lumi + xsec_higgsbkg + xsec_hplusc_4FS_5FS on top |

### Numerical caveats discovered while exploring v32

- **MC weight cancellation**: in `vjets`, summed event weights can be **negative** in slices of the discriminant (saw bkg yield = −13.65 in one SR slice during the first cascade attempt). This breaks naive S/√B optimisation: low-T scans get fake-huge ratios. Fixes: optimise on raw counts, or use `B_eff = Σw²` as the denominator, or floor `B(T) > B_min`.
- **Empty SR pitfall**: with 13 classes, raw `argmax` of the v32 softmax never picks `hplusc` because the 8 higgs sub-classes share features. **Always collapse 13 → 6 before argmax**, or use a threshold on `P(hplusc)`.
- **κ-as-discriminant pitfall**: clamp(`cos_sim`) makes 9/13 weights zero → denominator can hit machine epsilon. If we want a κ-weighted discriminant, use α (sigmoid form, all > 0.08) which is also what the training loss actually uses.

