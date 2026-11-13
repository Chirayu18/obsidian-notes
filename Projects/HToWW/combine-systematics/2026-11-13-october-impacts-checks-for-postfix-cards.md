---
tags: [reference]
status: active
date: 2026-11-13
source: lxplus
---

# October (pre-fix) impact ranking: what looked odd, to re-check on the post-fix cards

**Status: agent-reported.** These are read-only inspections of the October v12 cards and impacts, made on 13 Nov 2026 while discussing them with Chirayu. Nothing was refitted.
Chirayu (13 Nov): the SR being tt-dominated is **expected**. What is not expected is the **impact ranking**. Look into it after the fixes; the post-fix production is still running.

Sources:
- impacts: `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/combine_plots/impacts_run3.json` (Asimov r = 1, 55 nuisances; `CMS_eff_e_reco_below20_2022` failed);
- card: `/eos/user/c/cgupta/higgscharm/outputs/combine/full/v12_hplusc_full_run3.txt`, templates `v12_hplusc_full_<era>.root`;
- scripts: `lxplus:~/htoww_submit_logs/datamc_postfix_20261113/{scalevar_sizes,tt_templates,hpc_templates}.py`. `hpc_templates.py` double-counts the nominal in its per-process sums, so read 0% for "−50%". The per-bin and higgsbkg numbers below are corrected.

## October top 20 (impact on r; post-fit ±1σ in units of the input uncertainty)

| # | nuisance | impact | post-fit | | # | nuisance | impact | post-fit |
|---|---|---|---|---|---|---|---|---|
| 1 | scalevar_muR_muF | 90 | −0.61/+0.54 | | 11 | CMS_eff_e_id_2023 | 37 | ±0.90 |
| 2 | scalevar_muF | 81 | ±0.65 | | 12 | CMS_eff_e_reco_below20_2023 | 26 | ±0.72 |
| 3 | rate_tt_2022preEE | 57 | ±4% | | 13 | CMS_eff_e_id_2022 | 24 | ±0.92 |
| 4 | rate_tt_2023postBPix | 51 | ±4% | | 14 | CMS_met_unclustered_2023 | 23 | ±0.50 |
| 5 | rate_tt_2022postEE | 48 | ±4% | | 15 | CMS_scale_j_2023 | 21 | −0.37/+0.29 |
| 6 | tt_tune | 48 | ±0.28 | | 16 | lhe_pdf | 21 | −0.80/+0.50 |
| 7 | CMS_ctag2d_2023 | 47 | −0.39/+0.23 | | 17 | ps_isr | 19 | ±0.76 |
| 8 | rate_tt_2023preBPix | 44 | ±4% | | 18 | higgs_plus_c | 17 | ±1.0 |
| 9 | CMS_eff_e_reco_20to75_2022 | 43 | ±0.94 | | 19 | CMS_eff_e_reco_above75_2023 | 15 | ±0.81 |
| 10 | tt_mtop | 41 | ±0.30 | | 20 | CMS_eff_e_reco_20to75_2023 | 14 | ±0.93 |

Further down: `scalevar_muR` #30 (8.5), `CMS_ctag2d_2022` #48 (1.9, post-fit **±0.02**), `xsec_hplusc_4FS_5FS` #55 (0.05).

## Checks for the post-fix cards

1. **Scale nuisances on top.** `scalevar_muR`, `_muF` and `_muR_muF` are three independent nuisances on the H+c signal, Higgs backgrounds, single top, diboson and V+jets in all 24 channels (tt has "-", which is correct, since `no_theory: [tt]`).
   - μR×μF is not independent of μR and μF, so the scale is partly counted twice. For single top, adding them in quadrature gives about 6.4% vs about 5.4% for one envelope.
   - On the October signal the variations were one-sided from the old global-division LHE fix:
     - μF Up and Down both −6 to −8%;
     - μR×μF −15% / +1%;
     - μR Down −14 to −16%.
     
     See [[Projects/HToWW/samples-and-production/2026-10-13-central-signal-lhe-and-fxfx-issue]]. Run A uses the per-event `lhe_yukawa_fix.py` instead.
   - Check: does the ranking survive with one scale scheme (6-point envelope, or μR and μF only) and the per-event signal fix?
2. **Strong constraints in an Asimov fit:**
   - `CMS_ctag2d_2022`: ±0.02. The 2023 nuisance is −0.39/+0.23, about 15 times looser, which the luminosity difference doesn't explain. A single "Total" nuisance whose Up raises tt by +11 to +15% in both SR and CR_tt.
   - tt_tune ±0.28 and tt_mtop ±0.30, although their tt templates change yields by under 2% (SR and CR_tt).
   - JES 2023: −0.37/+0.29.
3. **tt normalisation spread over many nuisances.** One `rate_tt` per era multiplies tt in all 6 channels of that era, range [0, 5]. Its post-fit ±4% is far looser than the CR_tt MC statistics (0.10–0.19%), because these nuisances also act on tt mostly as normalisation:
   - c-tag 2D: +11 to +15% / −3 to −5%;
   - `lhe_pdf`: ±1.9%, flat, in SR and CR_tt;
   - top-pT: ±1.7% in CR_tt;
   - electron reco SF: ±1%.
   
   Impacts are not exclusive, so the same tt-normalisation freedom appears under several names. Check: make PDF, αS and c-tag shape-only for tt, and see whether `rate_tt` and these nuisances stop ranking as separate large sources.
4. **`higgs_plus_c` is the Higgs+HF composition uncertainty on the Higgs backgrounds,** not the signal theory uncertainty. It is a per-event weight ported from HiggsDNA `Higgs_plus_HF_syst` and replaced the AN's 50% lnN on ggH (`hww_combine_full.yaml` comments).
   - The card lists it on all six processes, but only `higgsbkg` templates move (about ±7% integrated). The signal template equals the nominal in every SR bin.
   - The 30% signal theory uncertainty is `xsec_hplusc_4FS_5FS` (lnN 1.30, signal only). At r = 1 it can only rescale r itself, hence rank 55.
   - Suggestion: rename the nuisance (for example `higgsbkg_HF`) and remove the inert entries.
5. **Electron SFs** are 6 of the top 20; muon SFs are not in the top 20. Check whether that persists with the new ttH-MVA lepton SFs.

## Context

- Expected limit (October Run 3, Asimov) 691; stat-only 338.5.
- SR (`SR_hplusc`, all eras): tt 42,682 (80% of the background), single top 3794, V+jets 5101, diboson 1626, higgsbkg 385, signal 0.82, so S/B = 2×10⁻⁵. Chirayu says the tt dominance is expected.
