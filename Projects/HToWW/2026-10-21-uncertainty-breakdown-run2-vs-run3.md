---
tags: [reference]
status: active
date: 2026-10-21
source: lxplus
---

# Uncertainty breakdown: Run 2 (HIG-24-009 Table 3) vs our Run 3 card

Our numbers come from the PRE-FIX Run 3 card `outputs/combine/full/v12_hplusc_full_run3.txt` (61.9 fb⁻¹, 2026-10-07), which still carries the old global LHE fix and the 2026-10-06 audit bugs. Blind Asimov r = 1, MultiDimFit singles on r, nominal σ(r) = 299.8. Each group is frozen in turn. Condor cluster 9566340; script `~/pipeline_condor/breakdown_job.sh`; output `outputs/combine/full/plots_work/breakdown/breakdown.json`.

Two conventions are given for ours. "Quad" is √(σ² − σ_frozen²)/σ, and "lin" is (σ − σ_frozen)/σ. For the statistical row, both are σ_stat/σ. Run 2's rows do not add up in quadrature to its 60% statistical share, so its convention is not obviously either one. Compare rankings, not exact sizes.

| source | Run 2 1POI | ours quad | ours lin | our group |
|---|---:|---:|---:|---|
| Statistical (data) | 60.0 | 57.2 | 57.2 | allConstrainedNuisances |
| cH modelling | 22.1 | 25.0 | 3.2 | xsec_hplusc_4FS_5FS (30%) |
| scale / PDF / PS (all processes except tt) | in cH modelling | 46.1 | 11.3 | scalevar_*, lhe_pdf, lhe_alphaS, ps_isr/fsr |
| H-bkg | 21.4 | 7.3 | 0.3 | higgs_plus_c (±50% HF ggH/VBF), xsec_higgsbkg, BR_* |
| Other backgrounds | 4.5 | 0.0 | 0.0 | xsec_diboson/st/vjets, CMS_negrw_vjets |
| tt modelling | in other backgrounds | 23.2 | 2.7 | top_pt, tt_hdamp, tt_mtop, tt_tune |
| MC statistical | 6.2 | 44.9 | 10.6 | prop_bin.* |
| Pileup | 4.3 | 0.5 | 0.0 | CMS_pileup* |
| Lepton efficiencies (ours incl. scale/res) | 4.6 | 26.0 | 3.4 | CMS_eff_*, CMS_scale/res_e/m |
| JES/JER (ours incl. MET unclustered) | 6.0 | 17.4 | 1.5 | CMS_scale_j*, CMS_res_j*, CMS_met_unclustered* |
| c-tagging | 5.9 | 23.5 | 2.8 | CMS_ctag2d* |
| tt normalisation | 5.6 | 0.0 | 0.0 | rate_tt_* |
| Luminosity | n/a | 3.1 | 0.0 | lumi_* |

In quadrature our systematics sum to about 83%, consistent with √(1 − 0.572²) = 82%.

Caveats:
- `scale_pdf_ps` includes the signal scalevar, which the old global-division LHE fix biases by −6 to −10% one-sided (see [[2026-10-13-central-signal-lhe-and-fxfx-issue]]). Expect this row to change after the per-event fix.
- JES/JER is understated, because JER was a no-op in these cards (2026-10-06 audit).
- c-tag at 23.5 is consistent with the flagged `CMS_ctag2d_2022` Up raising SR signal by +43%, which still needs verification.
- Run 2 is at 138 fb⁻¹ and ours at 61.9 fb⁻¹, so the statistical share is not like for like.
