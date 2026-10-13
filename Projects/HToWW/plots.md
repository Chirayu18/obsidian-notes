---
tags: [reference]
status: active
date: 2026-07-12
source: lxplus
---

# HToWW — plots

Plot links for the H+c (H→WW) analysis. Large PNGs stay on EOS; only link entries live here.

---

### 2D-CTAG plane with frozen bins + flavour composition

tags: [plot]
Date: 2026-07-19
Description: The 2D-CTAG plane (HFvLF vs BvC) with the 11 official SFbc-2D frozen bins overlaid on
2022postEE MC density (tt+H+c+DY+ST+WW, candidate c-jet, 845k jets), plus zoom insets for the
thin C4/C3/C2 and B1–B4 bands and a per-bin flavour-composition table. Shows that B1–B4 are
empty for the charm-selected candidate. See [[2026-07-19-ctag2d-full-documentation]].
Path: /eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.png

---

### 2D-cat MVA retrain — ROC curves (hplusc vs backgrounds)

tags: [plot]
Date: 2026-07-12
Description: ROC curves for the v11 MVA retrained with the 11 one-hot 2D-CTAG categories
(`cjet_cand_ctag2d_*`) replacing the raw PNet cvsl/cvsb scores. 6 plots: hplusc vs
all / higgsbkg / tt / st / diboson / vjets. AUC(hplusc_vs_all)=0.932 vs baseline 0.928.
Compare with the baseline `hwwcom_multiclass_v11` ROCs in the sibling directory.
Path: /eos/user/c/cgupta/EPR_task/b-hive/output/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/EPR_task/b-hive/output/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/

## Lepton MVA (mvaTTH) 2022EE — ONNX conversion #plot

tags: [plot]
Date: 2026-08-12
Description: ONNX vs TMVA::Reader validation (corr = 1.0000000000); prompt-vs-nonprompt
separation on the eµ selection; and the prompt/nonprompt ROC with working-point markers.
Path: /eos/home-c/cgupta/HToWW/leptonmva
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/leptonmva

- `plot_validation.png` — ONNX vs TMVA::Reader, both flavours, max |Δ| = 2e-07
- `plot_separation.png` — score distributions, prompt vs nonprompt (log y)
- `plot_roc.png` — prompt eff vs nonprompt eff, markers at score > 0.0 / 0.4 / 0.8

### H+c 3FS/4FS-FxFx ratio — MiniAOD exact Higgs-constituent subtraction
- tags: [plot]
- Date: 2026-09-30
- Description: 3FS vs 4FS FxFx, official GenJets with Higgs-descendant constituents subtracted, c-jet pT>10; per sample + Run-3 eras / Run-2 γγ vs WW / Run-2 vs Run-3 comparisons. R(≥1c) ≈ 0.66 everywhere.
- Path: /eos/user/c/cgupta/HToWW/fs_unc/plots/stitch_mini
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/stitch_mini

### H+c FS shape systematic (3FS vs 4FS FxFx, c-hadron pT) — GEN + Run 2 WW reco validation
- tags: [plot]
- Date: 2026-09-30
- Description: shape weights at equal inclusive σ (eras, γγ vs WW, Run 2 vs Run 3, T5 vs T10) and Run 2 UL18 H→WW SR closure vs real 3FS. Caveat: covers only the scheme difference, not NLO vs NNLO normalisation.
- Path: /eos/user/c/cgupta/HToWW/fs_unc/plots/fs_shape
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/fs_shape

### H+c FS shape weights — Run 2 H→γγ vs H→WW with ratio and ±1/2σ stat bands
- tags: [plot]
- Date: 2026-10-01
- Description: decay-independence plot for the FS shape systematic (justifies using Run 3 H→γγ weights for H→WW); `gg_vs_ww_run2_ratio` and `_withRun3` (shows the 20–30 GeV tension is a Run 2 γγ fluctuation).
- Path: /eos/user/c/cgupta/HToWW/fs_unc/plots/fs_shape/gg_vs_ww_run2_ratio.png
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/fs_shape

### Data/MC uncertainty-band breakdown — all four Run 3 eras (pre-fix production)
- tags: [plot]
- Date: 2026-10-08
- Description: share of the plotter band variance by source (MET; same in mTll/Njets) and band half-width now vs without the tt μR/μF scale variations, which the fit does not use (rate_tt floats). tt scale 54–72%, c-tag 2D SF 15–38%, PDF/αS 7–9%. Per-era per-bin stacked plots in `<era>/band_breakdown/`.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/band_overview_allEras.png
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full

### Combine plots — v12 full cards, all eras + Run 3 (pre-fix)
tags: [plot]
- Date: 2026-10-09
- Description: blind Asimov results for the pre-fix v12 cards. `limits_summary.png`: expected 95% CL limit with ±1σ/±2σ bands, plus stat-only and MC-stat-frozen medians, for every era card, 2022, 2023 and Run 3 (691; stat-only 338.5 at 61.9 fb⁻¹). `impacts_run3.png`: top-30 impacts out of 55 (Asimov r=1, manual MultiDimFit --algo impact, prop_bin excluded; CMS_eff_e_reco_below20_2022 tree unreadable). tt μR/μF scale (scalevar_muR_muF, scalevar_muF) and the four rate_tt params lead. `prefit/prefit_<era>.png`: FitDiagnostics prefit MVA-score shapes per channel with the full correlated prefit band. The cards carry no real data (data_obs = background sum), so no data is drawn.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/combine_plots
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/combine_plots

### H+c LHE scale-weight fix — WW vs clean γγ shapes (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: normalised LHE scale-variation shapes (each variation / nominal per bin, normalised to its integral, so any common factor cancels) vs Higgs pT, LHE NpNLO and leading gen c-jet pT. Compares our central H+c→WW 4FS FxFx sample, with a common factor (= the old global-division fix) and with the new per-event running-Yukawa fix, against the CLEAN γγ 4FS FxFx sample (22EE, ~140k events each). The per-event fix matches γγ within ≲2–4% for μF and the up variations; the down family is off up to ~10% in sparse tails (high Higgs pT, NpNLO=1). The common factor is off 10–35%. `scale_shape_vs_gg_summary.png` shows the max deviation per panel (stat errors not included).
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix

### H+c LHE fix — one-jet H-events: scale rebuild, unmixing, γγ spike (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: four plots for NpNLO=1 H-events (22EE, 3 WW vs 3 γγ files; `runall/plot_unmix.py`, arrays in `*_arrays.npz`).
  - `scale_from_partons.png`: the scale implied by the weights (from r) vs MadGraph's FxFx rule computed from LHEPart. S-events peak at 1; one-jet H-events are a two-scale mixture.
  - `npnlo1H_vs_gg_by_scale.png`: median and genW-mean of μR×0.5 / μR×2 in bins of the real-emission scale, for the WW per-event fix, the WW two-piece unmixing and clean γγ (with and without the constant-ratio events). Medians agree to ≤0.3%. The lowest bin (10–15 GeV) holds 0.2% of WW events and is driven by single events.
  - `gg_constant_ratio_events.png`: the γγ spike at 6.198 / 0.308 (297 events, 7.1% of the class weight), which is independent of kinematics and absent in WW.
  - `unmix_closure.png`: the two-piece model predicts the stored broken weights to ~0.05–0.5%.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix

### H+c LHE fix — scale shapes vs γγ with the spike events removed (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: same as `scale_shape_vs_gg_*`, with the 233 γγ constant-ratio events removed (grey open circles = old reference including them). The per-event fix agrees within ≲5%. NOTE: the clean Run 2 UL18 WW sample shows the same spike, so the spike is standard behaviour of the older MG versions; our MG 2.9.18 WW sample is the outlier (see the main log).
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/scale_shape_vs_gg_nospike_higgs_pt.png
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/scale_shape_vs_gg_nospike_higgs_pt.png

### H+c LHE fix v2 — ours vs Run 3 γγ and Run 2 WW (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: normalised scale-variation shapes vs Higgs pT, class (0j/1j × S/H) and gen c-jet pT, plus the inclusive normalisation of each variation. Ours uses the updated per-event fix (tables down to MG's 1 GeV scale floor; floor events exact). References: the clean Run 3 γγ (MG 2.9.9) and Run 2 UL18 WW (MG 2.6.5) samples, which agree with each other. Shapes agree within ~0.04. The one-jet H class and the inclusive muR-down (1.017 vs 1.048) differ because our sample has fewer one-jet and floor events (a generation difference).
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix

### H+c LHE fix — high-stat jackknife comparison, raw and mix-matched (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: `scale_shape_jk_{higgs_pt,cls,cjet_pt}.png`: ours (2.94M, fixed) vs Run 3 γγ (3.06M) vs Run 2 WW (3.9M), with jackknife stat errors and pulls. `scale_shape_jk_mixmatched_{hpt,cls}.png`: the references reweighted to our class × Higgs-pT mix; μF agrees within ≤1% and everything above 60 GeV agrees. The residual is in the one-jet H class / Higgs pT 20–60 GeV, from our sample having half as many 1 GeV scale-floor events. Pull panels are clipped at ±8.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix

### GEN ticket figures — H+c/H+b → WW production issues (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: figures for the GEN ticket draft (`full-rerun-2026-10-01/2026-10-13-GEN-ticket-draft-HplusC-HplusB-WW.md`).
  - fig1: broken LHE weights (PDF replicas/central ≈ 2.26; scale variations ≈ ×2).
  - fig2: the FxFx veto only acts at |η| < 2.5 (missing JetMatching lines).
  - fig3–5: impact on the scale shapes and the nominal mix.
  - `mcm_fragments/`: the official fragments of all requests.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/ticket
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/ticket

### H+c scale variations in the analysis-like region (2026-10-13)
tags: [plot]
- Date: 2026-10-13
- Description: scale-variation shapes (Higgs pT, c-jet pT, n-jets, class) and the acceptance per variation for ≥1 gen c-jet (pT>20, |η|<2.4). Ours (per-event fix) vs Run 3 γγ and Run 2 WW, 0.9–1.5M region events each, jackknife errors. Inside the region ours agrees with the references at the 1–2% level, within the spread between the two references. muR-down acceptance is about 1 point high. γγ is not usable for the c-jet/n-jet axes because GenJets include the photons.
- Path: /eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/region
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/region
