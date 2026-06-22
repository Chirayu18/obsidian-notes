---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

---
title: "Combine for H+c (H→WW): results so far + integration plan"
subtitle: "v1 / v2 / v3 fits at 2022postEE, and the higgscharm integration in progress"
author: "Chirayu Gupta"
date: "2026-05-13"
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-size: 20px;
    padding: 40px 50px;
    justify-content: flex-start;
  }
  section h1 { font-size: 1.6em; margin-bottom: 0.3em; }
  section h2 { font-size: 1.25em; margin: 0.2em 0 0.4em; }
  section p, section li { line-height: 1.35; margin: 0.25em 0; }
  section table { font-size: 0.85em; border-collapse: collapse; }
  section th, section td { padding: 3px 8px; }
  section pre, section code { font-size: 0.8em; line-height: 1.2; }
  section pre { padding: 0.4em 0.6em; }
  section img { max-height: 380px; height: auto; }
  /* tighten the side-by-side comparison grids */
  section div[style*="grid"] { gap: 0.6em !important; align-items: start; }
  section div[style*="grid"] img { max-height: 300px; }
  /* dense slide opt-in: <!-- _class: dense --> */
  section.dense { font-size: 17px; }
  section.dense table { font-size: 0.78em; }
---

# Combine for H+c (H→WW)

**Two-part status update**

1. What we've fit so far — combine v1, v2, v3 at 26.67 fb⁻¹ (2022postEE)
2. What's currently being built — combine pipeline integrated into the higgscharm framework, with per-variation parquets for object-level systematics

---

## Pipeline today

```
higgscharm  ──▶  .coffea  (postprocessor → control plots)
            ──▶  .parquet ──▶ b-hive InferenceTask ──▶ prediction.npy
                                                            │
                                                            ▼
                                  b-hive scripts/make_combine_*
                                                            │
                                                            ▼
                                     CMSSW combine v10.6.0 / fits
```

- **MVA**: v11 (6-class flat CE on `v4_hplusc_higgsbkg`), AUC(hplusc-vs-all) = 0.966
- **Discriminant**: `D = P(hplusc)` (uniform κ = 1)
- **Inputs**: 156 TH1Ds per channel × 26 variations (nominal + 12 weight systs × Up/Down)
- **Datacard**: 2 generations: 1-channel (v1, v2) and 6-channel argmax (v3)

---

## Combine v1 — first-pass r-fit (stat-only)

- Single channel, 20-bin `D = P(hplusc)`, 12 weight-based shape systs, `autoMCStats 10`
- Asimov `data_obs = Σ backgrounds`
- POI = `r` (signal strength); r → κc² reinterpretation

| Metric | Value |
|---|---|
| `AsymptoticLimits` median r_95 | **943** |
| ±1σ band | [653, 1394] |
| ±2σ band | [479, 1987] |
| Significance @ r=1 | 0.0036σ |

**Comparison**: AN-23-102 1POI = 431 at 138 fb⁻¹; scaled to 27 fb⁻¹: 968.
→ v1 matches AN's 1POI to **3 %** at matching lumi — stat-dominated regime as expected.

---

## Combine v2 — rate-only lnNs from AN-23-102

Nine lnN nuisances added (Table 16 of AN-23-102 + LumiPOG):

| Nuisance | Value | Procs |
|---|---|---|
| `lumi_13p6TeV` | 1.4 % | all |
| `xsec_st` | +1.67/−1.27 % | st |
| `xsec_diboson` | 3.7 % | diboson |
| `xsec_vjets` | 2.7 % | vjets |
| `xsec_higgsbkg` | 5 % | higgsbkg |
| `BR_HtoWW` | 1 % | signal + higgsbkg |
| `xsec_hplusc_PDF` | 6 % | signal |
| **`xsec_hplusc_4FS_5FS`** | **30 %** | signal (dominant) |
| `alphaS_PDF` | 3 % | all |

→ r_95 = **1055** (+12 % vs v1). Driven by the 30 % flavour-scheme uncertainty on signal.

---

## Combine v3 — 6-channel argmax (HIG-24-018 style)

- Per event: `c* = argmax(softmax)` → 6 mutually exclusive channels
- `SR_hplusc` (argmax = hplusc) + 5 CRs (one per bkg)
- Fit variable per channel: `D = P(c*)`, 20 bins
- Same 12 shape systs + 9 lnNs as v2, `autoMCStats 10` per channel

| Metric | v3 | v2 | Δ |
|---|---|---|---|
| Median r_95 | **979** | 1055 | −7 % |
| ±1σ band | [651, 1553] | [696, 1694] | tighter |
| ±2σ band | [467, 2454] | [495, 2711] | tighter |
| S/√B in SR_hplusc | 0.0030 | 0.00086 | **3.5× better single-bin** |

→ Scaled to 138 fb⁻¹: **r_95 = 433 vs AN-23-102's 431 → +0.5 % match.**
**Statistically equivalent to AN-23-102 1POI at matching lumi.**

---

## Pre-fit `SR_hplusc` distribution

![w:880](plots/combine_prefit_SR_hplusc.png)

Signal (×1000 for visibility) peaks high in `D`; S/B ratio panel shows the discriminant is doing its job (max S/B ≈ 10⁻³ in the top bin).

---

## Yields per channel — 6-channel argmax (v3)

![w:1020](plots/combine_yields_per_channel.png)

Argmax categorisation works: signal lands 81 % in `SR_hplusc`; each background concentrates 28–85 % in its own CR (`tt` 56 % in `CR_tt`, etc.).

---

## Expected limit on r — v1 / v2 / v3 vs AN-23-102

![w:1100](plots/combine_r95_brazil.png)

- v1 (stat) and v3 (6-ch argmax) bracket the AN-23-102 1POI scaled to my lumi (red dashed = **974**)
- v3's median **979** ≈ AN's **974** → frame is now competitive

---

## Side-by-side: our v1/v2/v3 vs AN-23-102 Fig. 49

<div class="grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em;">

**This work (27 fb⁻¹, 2022postEE)**
![w:560](plots/combine_r95_brazil.png)
median r_95: v1=943, v2=1055, **v3=979**

**AN-23-102 Fig. 49, p. 64 (138 fb⁻¹, Run 2)**
![w:560](plots/an_fig49_p64-064.png)
run2 1POI = **431**, run2 2POI = **969**

</div>

→ scaling AN 1POI to our lumi: **974**; v3 = 979 (+0.5 %). v2 = 1055 (+9 %) consistent with conservative lnNs.

---

## Likelihood profile — stat-limited

![w:1000](plots/combine_nll_scan.png)

`2·ΔNLL < 2×10⁻⁴` over `r ∈ [−5, 5]` for both v2 and v3.
→ At 27 fb⁻¹ the shape constraint is **negligible**; the limit is set by the asymptotic distribution at `r_95`.

---

## Side-by-side: NLL scan vs AN-23-102 Fig. 54

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em;">

**This work (27 fb⁻¹) — flat**
![w:560](plots/combine_nll_scan.png)
2·ΔNLL stays below 2×10⁻⁴ → no shape constraint

**AN-23-102 Fig. 54 — 1POI scan on r_H+c (138 fb⁻¹)**
![w:560](plots/an_fig54_p68-068.png)
Visible parabola; 68% CL at r ≈ ±200, 95% CL ≈ ±400

</div>

→ Once we hit 5× the lumi the parabola sharpens; until then, expect the flat profile to persist. The AN's red curve (stat-only) is the limit we're stat-bound to.

---

## What's brewing — v3.2 / v32 ideas

Brainstorm in `combine.md`, in rough priority order:

**Model swap.** v32 (13-class kappa-HCE, AUC 0.975) replaces v11. Best `hplusc_vs_all` currently. Caveat: raw 13-class `argmax` never picks `hplusc` (8 Higgs sub-classes share features) → must collapse 13 → 6 before argmax, **or** use a `P(hplusc) > T_opt` threshold.

**Channel structure.** Options being weighed:
- A: 6 channels, argmax over collapsed 6-class softmax (= v3 layout, v32 inputs)
- **B: Cascade with optimised threshold** —
  `SR_hplusc = P(hplusc) > T_hplusc`,
  `CR_tt = P(tt) > T_tt`,
  `CR_st = P(st) > T_st`,
  `CR_vjets = P(vjets) > T_vjets`,
  `CR_diboson = P(diboson) > T_diboson`,
  `CR_higgsbkg = P(higgsbkg) > T_higgsbkg`
- D: 13 channels, one per v32 class — 78-column datacard, stats-thin per CR

---

## v3.2 ideas (cont.) — discriminant + rate model

**Discriminant choices** in the SR:
- (i) **`D = P(hplusc)`** ← **used in v3** (κ_j = 1 collapses kappa-discriminant to raw `P(hplusc)`)
- (iii) κ-weighted `D = P(hplusc) / Σ κ_j P(j)` with κ_j = max(0, cos(W_hplusc, W_j)) — 9/13 κ's clamp to 0; survivors with κ > 0 group as "signal-like"
- (iv) α-weighted `D = P(hplusc) / Σ α_j P(j)` with α_j = sigmoid(cos/τ) — quantity the kappa-HCE loss uses at training

**Rate model** — closing the rate gap to AN:
- Keep `higgsbkg` as 1 process (v3 style) — minimal complexity
- **Split using κ > 0** → `higgs_clike` (κ_j > 0 sub-classes: H+b, ggH, VBF) + `higgs_other` (κ_j = 0 sub-classes: ZH, ggZH, WH, ttH*). Enables `BR_HtoTauTau` (1 %), `ggH_HF` (50 %) lnNs → closes 3–5 % of the v2→AN gap.
- Full per-sub-class (8 Higgs procs) — maximally clean but heavy bookkeeping

---

## v3.2 ideas — rateParams

**RateParams to add** (the main v3→v4 win):
- `tt` rateParam on `CR_tt` — unlocks the v3 CR's normalisation-pinning power that's currently unused
- `vjets`, `diboson` rateParams — smaller effects, same pattern
- Drops corresponding `xsec_*` lnNs once each CR has stat power

---

## What we're targeting — AN-23-102 Table 17 (Δr/r breakdown, 1POI)

| Source | 1POI Δr/r (%) | Status in v3 |
|---|---|---|
| Statistical | 73.8 | dominant |
| MC stat (bin-by-bin) | 5.4 | ✓ (`autoMCStats`) |
| cH/bH theory | 8.5 |  |
| Bkg-Higgs theory | 7.6 | ✓ (`xsec_higgsbkg` lnN) |
| Other bkg theory | 1.4 | ✓ (`xsec_*` lnNs) |
| Jet energy scale + resolution | 1.1 | ⊘ |
| Charm tagging | 1.1 | ⊘ |
| Missing energy scale | 0.4 | ⊘ |
| tt̄ normalisation | 0.7 | ⊘ (v3.2: rateParam) |
| Pileup, lepton, trigger | < 0.5 each | partial (✓ pileup + lepton, ⊘ trigger) |

This table is the **specification** of what the framework integration is meant to add.

---

## Uncertainties: what's in v3 vs what AN has

<!-- _class: dense -->

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em;">

**In v3 datacard**

- 12 weight-based shape systs:
  `pileup`, `ps_isr`, `ps_fsr`,
  `scalevar_muR/muF/muR_muF`,
  `muon_id`, `muon_iso`,
  `electron_id`,
  `electron_reco_RecoBelow20/Reco20to75/RecoAbove75`
- 9 rate-only lnNs:
  `lumi_13p6TeV` 1.4 %,
  `xsec_st` ±1.6 %,
  `xsec_diboson` 3.7 %,
  `xsec_vjets` 2.7 %,
  `xsec_higgsbkg` 5 %,
  `BR_HtoWW` 1 %,
  `xsec_hplusc_PDF` 6 %,
  `xsec_hplusc_4FS_5FS` 30 %,
  `alphaS_PDF` 3 %
- `autoMCStats 10` per channel

**Missing — phase plan**

| Group | Items | Add via |
|---|---|---|
| Object-shape | JES, JER, MET_unclust, mu/ele scale, HEM, L1 prefire | shifted parquets |
| SF weights | **ctag**, btag, mistag, trigger, muon_reco, electron_iso, pujetid, pileup_profile | upstream weight columns |
| Theory weights | PDF replicas, αs, UE_tune, mH, top_pt_reweight, EWK_NLO | weight columns |
| Alt MC | hdamp, mtop, colour-reconnect, DR_vs_DS | re-process alt samples |
| Decomposition | tt_HF, ggH+HF, BR_HtoTauTau, BR_Hcc | gen-flavour split + `higgsbkg` split |

</div>

---

## κc interpretation & 2D scan — AN Fig. 56 / 57

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em;">

**AN Fig. 56 (p. 69) — 2D scan: r_H+c vs r_bkg-H+c**

![w:560](plots/an_fig56_p69-069.png)

2POI fit, 1σ/2σ contours; SM marker at (1,1). Maps to our **v3.2 plan**: needs `higgsbkg` decomposition.

**AN Fig. 57 (p. 70) — κc likelihood scan**

![w:560](plots/an_fig57_p70-070.png)

Flat-direction approximation: κc_95 ≈ 35 (1POI), 77 (2POI). Maps to our **κ-framework workspace step**; with v3's r_95 = 979, naive √r → κc_95 ≈ 31; AN's flat-direction formula → 76.

</div>

→ Once v3.2 has `higgsbkg` split + κ-framework workspace, both panels are directly reproducible at our lumi.

---

# Part 2 — Integration plan in progress

**Currently being built**: per-variation parquet production in higgscharm + combine pipeline relocated under higgscharm.

Goal: get object-level shape systematics (JES, JER, MET_unclust, lepton scales) into the datacard. These are the largest remaining gap to AN-23-102 — they need shifted parquets from higgscharm, which means the histogram and datacard scripts should live where the parquets are produced.

---

## What we're aiming for

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

- MVA training & inference stay in b-hive (single frozen v11 — or v32 — model)
- Parquet production, histogram building, datacard, workspace all move under higgscharm
- One frozen MVA, many shifted inputs, identical downstream

---

## Parquet vs coffea — how higgscharm handles outputs today

higgscharm's processor emits **both** in one pass:

| output | format | content | who reads it |
|---|---|---|---|
| `<sample>.coffea` | coffea hist | binned histograms on `hww_MVA.yaml` axes | postprocessor → control plots, cutflows |
| `<sample>.parquet` | pyarrow | per-event MVA inputs + 26 weight columns + truth | b-hive InferenceTask + combine histogram script |

- **Coffea** = standard higgscharm output, used for AN-style plots
- **Parquet** = combine path; per-event MVA output + per-event reweighting for the 12 weight systs

Shifted variations: **parquet only** — MVA inputs + `weight_nominal` + truth, ~30–40 % the size of nominal.

---

## Per-variation directory layout

```
/eos/.../hww_MVA/2022postEE/v5_combine/
├── nominal/             # full schema, .coffea AND .parquet
├── jes_AbsoluteUp/      # MVA inputs + weight_nominal + truth (parquet only)
├── jes_AbsoluteDown/
├── jes_BBEC1Up/
├── ...
├── jer_barrelUp/
├── met_unclustUp/
├── mu_scaleUp/
└── ele_scaleUp/
```

Variation name = the string combine expects (`<proc>_<variation>{Up,Down}`).

**Currently testing**: producing `jes_AbsoluteUp/` end-to-end as the smoke test before scaling out.

---

## What's changing in higgscharm

Plumbing a `variation=` knob through `correction_manager.py`:

```
object_corrector_manager(events, year, dataset, workflow_config, variation="nominal")
        │
        ├── apply_jerc_corrections(..., variation=...)       # jerc.py
        ├── apply_met_phi_corrections(..., variation=...)    # met.py
        ├── apply_muon_ss_corrections(..., variation=...)    # muon_ss.py
        └── apply_electron_ss_corrections(..., variation=...) # electron_ss.py
```

Runner gets a `--variation` flag (default `nominal`), output goes to `<output_root>/<variation>/<sample>/`.

Variation list lives in `analysis/workflows/hww_MVA_variations.yaml` — a single config drives the Condor submission.

---

## Parallelising inference (benchmarking)

`InferenceTask` is one `law` task per `test_dataset_version`. Three layers:

| layer | how | when |
|---|---|---|
| **1. DataLoader workers** (intra-task) | `n_threads = 8` already set | always on |
| **2. Luigi `--workers N`** (one node) | `law run InferenceTask --workers 4` | development / few variations on local GPU |
| **3. Condor sandbox** (cluster) | `law` HTCondor backend; one job per (sample, variation) | production at scale |

**Key**: only **object-shift** variations need re-inference (JES, JER, MET, lepton scales, HEM, prefire). Weight-based systs just **swap the weight column** in the histogram script and reuse nominal `prediction.npy`.

→ Inference budget set by ~36 object shifts, not the full nuisance count.

---

## Summary

- **Combine v1 / v2 / v3** at 27 fb⁻¹ are in; v3 matches AN-23-102 1POI (scaled to lumi) within 0.5 %. Frame is competitive.
- **Likelihood profile is flat** → fit is stat-limited at this lumi. Adding shape systs and rateParams reshapes the band, not the median.
- **Next experimental step (v3.2)**: v32 model + threshold cascade or higgsbkg κ > 0 split, with rateParams on tt / vjets / diboson.
- **Next pipeline step**: per-variation parquets from higgscharm, combine scripts relocated under higgscharm, parallel inference scaling to ~36 object-shift variations.
