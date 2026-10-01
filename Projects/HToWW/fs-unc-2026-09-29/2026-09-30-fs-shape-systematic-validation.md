---
tags: [reference]
status: active
date: 2026-09-30
source: lxplus
---
# H+c flavour-scheme SHAPE systematic — derivation and validation (2026-09-30)

Implements the decision in [[2026-09-29-fs-3FS-4FS-status]] (box "DECISION (user, 2026-09-30)"): 4FS FxFx nominal unchanged;
the 30% `xsec_hplusc_4FS_5FS` lnN is replaced by a **3FS/4FS shape systematic**. Everything standalone in
`/eos/user/c/cgupta/HToWW/fs_unc/` — framework and parquets untouched.

> **⚠️ Caveat — must appear on every slide / AN paragraph:** this uncertainty covers ONLY the 3FS–4FS flavour-scheme
> difference. It does NOT cover the difference between the NLO normalisation of the nominal sample and higher-order
> predictions (LHCHWG-2026-007 Table 3: NNLO/MiNNLOPS ~25% below NLO inclusively at 13.6 TeV).

## Definition
- Leading GEN c-hadron: weakly-decaying open-charm hadron (NanoAOD `GenPart`, status 2; charmonium excluded; not from a
  b-hadron), |η| < 2.5. Threshold T = 5 GeV (10 GeV as variation). Script `gen/derive_chad.py`.
- **Both schemes at the same inclusive σ** → weights are pure fraction ratios, normalisation-free:
  w(bin) = [σ3FS(bin)/σ3FS,incl] / [σ4FS(bin)/σ4FS,incl]; events with no c-hadron > T get w0.
  Inclusive σ is unchanged; what changes is how events are distributed → the selection efficiency.
- **Up = w (3FS-like), Down = 2 − w (mirror).** Weight table: Run 3, 4-era combined (H→γγ), `fs_shape/weights.md`;
  correctionlib `fs_shape/hplusc_fs_shape_correctionlib.json` (input `gen_chad1_pt`, −1 if none; syst nominal/up/down).

| leading c-hadron pT [GeV] | none (0c) | 5–10 | 10–15 | 15–20 | 20–30 | 30–45 | 45–60 | 60–80 | 80–110 | >110 |
|---|---|---|---|---|---|---|---|---|---|---|
| **w_up (Run 3 comb.)** | 0.776 | 1.410 | 1.231 | 1.106 | 1.052 | 1.047 | 1.077 | 1.076 | 1.151 | 1.183 |

## GEN-level validation (official NanoAOD; all files, 0 skipped)
| comparison | χ²/ndf (0c + 9 pT bins) | comment |
|---|---|---|
| Run 3 eras (6 pairs) | 6.2–10.0 / 10 | consistent |
| Run 2 H→γγ vs H→WW | 18.9/10 | decay independence; one 2.9σ bin (20–30 GeV, 1.10 vs 1.05) |
| Run 2 vs Run 3 (γγ) | 43.8/10 | 13 vs 13.6 TeV differ by 2–5% (0c 0.757 vs 0.776; 10–15 GeV 1.29 vs 1.23) — Run 3 analysis uses Run 3 weights |
| T = 5 vs 10 GeV | — | identical above 10 GeV; w0 0.776 → 0.948 |

## Reco-level validation — real Run 2 UL18 H→WW samples (3FS: 5.0M events, 4FS FxFx: 19.8M)
Standalone approximation of the selection (OS eμ + kinematic cuts; SR adds ≥1 DeepJet-medium c-tag as UL18 stand-in for PNet).
All at equal inclusive σ. Script `gen/reco_ana.py`, table `fs_shape/reco_run2_WW.md`.

| region | real 3FS / 4FS | 4FS × w_up (γγ Run 3 weights) | (WW-derived) | (γγ Run 2) | stitched / 4FS |
|---|---|---|---|---|---|
| preselection | 1.041 ± 0.010 | 0.998 | 0.998 | 0.999 | 1.013 |
| **SR (≥1 c-tag)** | **1.063 ± 0.023** | **1.073** | 1.079 | 1.090 | 0.998 |

- **SR yield: the systematic (±7.3%) covers the real 3FS sample (+6.3 ± 2.3%) and closes within 0.5σ** — vs Run 2's flat 30%.
- γγ-derived (Run 3) weights reproduce the WW-derived result (1.073 vs 1.079) → decay transfer holds at reco level.
- Honest detail: the closure in SR is partly a compensation — 3FS has +4% more events at preselection (not modelled by
  the c-hadron weights, which give 0.998) and a smaller c-tag gain than the weights (+2% vs +7.5%).
- **SR shapes:** 3FS and 4FS agree within statistics in all observables (c-jet pT/η, mll, pTll, mT, lepton pT, MET,
  c-tag scores, N c-tags) **except N jets (pT>30): χ² 23/5, not covered** — 3FS has more 0-jet (0.512 vs 0.471) and
  fewer 2-jet (0.082 vs 0.100, −18%) events. The c-hadron weights move N jets by only ±1%.
- **Cost of stitching instead** (SR): 7-point scale envelope 4FS FxFx +13.4/−9.5% vs 3FS +16.7/−17.9% vs stitched
  +14.1/−14.8%; MC stat Neff 4FS 55,971 vs 3FS 2,265 (25× fewer effective events per sample-size, 40% negative weights).

## Open item
N-jet shape difference 3FS vs 4FS FxFx in the SR (up to −18% at 2 jets) is not covered by the c-hadron-pT weights.
Options (user to decide): (a) add an N-jet component to the FS shape systematic, derived from Run 2 WW reco 3FS/4FS
(Run 3 has no 3FS WW); (b) check whether N jets enters the MVA/fit strongly enough to matter; (c) document as a limitation.

## Plots
- GEN: `fs_unc/plots/fs_shape/` — shape_run2_GG_vs_WW_T{5,10}, shape_run3_eras_T*, shape_run3_vs_run2_{GG,WW}_T*, shape_T5_vs_T10_run3comb
- Reco (Run 2 WW SR): `fs_unc/plots/fs_shape/reco_run2_WW/sr_*.png`
- [CERNBox](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/fs_shape)

## The 20–30 GeV γγ-vs-WW bin (investigated 2026-10-01)
Per-file, 1 GeV-binned rerun (`fs_unc/gen/perfile_chad.py`, `gen/bin2030_ana.py`, outputs `fs_unc/bin2030/`).
- **Not a narrow spike:** in 2 GeV bins the Run-2 γγ weight is ~5–6% above WW coherently over 22–32 GeV (each bin −1.2…−2.3σ).
- **Run 2 γγ is the outlier, not WW:** Run 3 H→γγ (22postEE, 40/60 files) gives 1.02–1.06 there, agreeing with Run 2 WW
  (1.03–1.07) → same decay as the outlier, so **not a decay effect**. Run 3 combined 20–30: 1.052 vs WW 1.048.
- **No bad file:** per-file χ² of the 20–30 fraction is fine (γγ 3FS 49/71, γγ 4FS 80/119); jackknife-by-file error (0.067%)
  ≤ sum-w² error (0.085%) → errors not underestimated.
- Run 2 γγ 3FS is the smallest sample (2M events, 40% negative weights). Look-elsewhere: P(≥1 bin at ≥2.9σ in 10) = 3.7%.
- **Verdict:** statistical fluctuation of the Run 2 γγ 3FS sample; no impact on the Run 3 weights.
- Side observation (cancels in w): Run 2 WW samples are ~1–3% softer than γγ in pT(H) and c-hadron pT in BOTH schemes
  (3–4σ), identically in the WW nominal and ext1 productions (agree within 2σ). User confirms same generator setup;
  origin not identified. It cancels in the 3FS/4FS ratio except where the 3FS fluctuation sits.
