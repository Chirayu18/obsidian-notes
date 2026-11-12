---
tags: [reference]
status: active
date: 2026-11-13
source: lxplus
---

# Post-fix data/MC (TRAIN v2, Arm A): preselection, all four eras

**Status: agent-reported.** Made interactively on lxplus on 2026-11-12/13 for the 13 Nov talk. Nobody has reviewed the plots yet.
Compare with the October (pre-fix) plots: [[2026-10-06-independent-review]] and the `oct-datamc` / `oct-band` / `oct-slope` slides.

## Bottom line

1. **The large October band cannot be redrawn yet.** TRAIN v2 is **nominal only**, so the new plots show the **MC-statistics band only**. Its mean half-width is 0.5–1.1% per era. The October band was 18–20% (mean relative half-width), and 54–72% of its variance came from the tt μR/μF scale, which the fit does not use. The new band is smaller because **systematics are not in it**, not because they shrank. A post-fix systematic band needs a RUN-mode production with shifts.
2. **The MET slope is still there in 2022postEE.** The data/MC fit slope is −0.097 ± 0.008 per 100 GeV (October: −0.098). The ratio goes from 0.95 at 45–55 GeV to 0.85 at 300–350 GeV. In **2023 it is gone**: preBPix −0.002 ± 0.010 (October −0.076), postBPix −0.007 ± 0.013 (October −0.065). 2022preEE: −0.039 ± 0.014 (October −0.051, and the October preEE data still had the duplicated events).
3. **The lepton–MET transverse-mass slopes are much reduced in 2022postEE.** mT(ℓ1): −0.045 → −0.010 ± 0.005 per 100 GeV (2σ from zero). mT(ℓ2): −0.055 → −0.008 ± 0.008 (consistent with zero).
4. **The overall normalisation deficit remains.** Data/MC is 0.926 (2022preEE), 0.918 (2022postEE), 0.964 (2023preBPix) and 0.968 (2023postBPix); 0.941 for all eras. The MC is about 87% tt in every era. The October yields are **not like-for-like**. `diff` of the object/event-selection blocks of `hww_combine_full.yaml` vs `hww_allfix_4fs.yaml` shows:
   - muons `tight` ID/iso → `tight_HWW` ID/iso + `promptMVA tight_HWW`;
   - electrons `wp80iso` → `Medium` + `promptMVA ttHMVA_Run3`;
   - the `tthMVA` and `jetveto` (Run-3 jet veto maps) corrections were added;
   - no change to the event-selection cuts.
   
   The trigger-dataset dedup is a code fix (review A1), not a YAML change. 2022postEE data went from 108,000 events (October, `hww_combine_full/2022postEE/slope_study/summary.json` `data_total`) to 72,139. Compare **shapes and slopes** only.

## Plots

EOS `/eos/user/c/cgupta/HToWW/datamc_postfix_20261113/<era>/postfix_datamc_<var>_<era>.png`, for `<era>` = 2022preEE, 2022postEE, 2023preBPix, 2023postBPix, and `allEras/postfix_datamc_<var>_2022+2023.png` (61.9 fb⁻¹).
Variables: `met_pt`, `mtl1`, `mtl2`, `dilepton_mass`, `dilepton_pt`, `lepton1_pt`, `lepton2_pt`.
CERNBox: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/datamc_postfix_20261113

The style follows the framework plotter (`analysis/postprocess/plotter.py`, `style.yaml`, `process_color_map.yaml`): the stack is sorted by yield, Events/GeV, log y, data/pred in 0.5–1.5, H+c ×10⁴ is overlaid, and under/overflow is dropped (`flow="none"`). The **binning is identical to October**: I compared the `hww_allfix_4fs.yaml` and `hww_combine_full.yaml` edges for met_pt, mtl1, mtl2, dilepton_mass, dilepton_pt and lepton1_pt. The band legend reads "MC stat. unc. only (no syst.)". The in-plot text says "nominal only; band = MC stat."

**No mTll (dilepton transverse mass) plot.** The TRAIN parquets do not store it, and it is not reconstructible without the sign of Δφ(ℓ,MET). The like-for-like lepton–MET comparison uses `mtl1`/`mtl2`, which both productions have.

## What the band contains, and what it does not

- **Contains:** MC statistics, √Σw² per bin after normalisation (H+c signal excluded), in the main and ratio panels.
- **Does not contain:** object shifts (JES/JER/MET-unclustered/lepton scale), weight systematics (pileup, lepton/trigger SF, c-tag 2D SF, top-pT, μR/μF, PDF, PS) and lnN rates. TRAIN parquets store only `weight_nominal`.
- **The only stored variation** is `weight_negrw_std`, the negrw ensemble spread on V+jets. **I did not add it.** It covers only V+jets, which is under 0.4% of the MC, and adding it would suggest a "systematic band" that is not one.
- **No October shift templates were reused.**

## Inputs and method

- Repo `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` @ `5b25295` (`hww-analysis`), read-only. Run in the job container `coffeateam/coffea-base-almalinux9:0.7.30-py3.10`, binding the Kerberos ccache so it can read `/eos/user`. Host python could not unpickle the negrw model (numpy version mismatch).
- Script: `lxplus:~/htoww_submit_logs/datamc_postfix_20261113/datamc_postfix.py` (wrapper `run.sh`, driver `run_all.sh`). Logs `run_<era>.log`, `run_combine.log`. October-metric script `october_metrics.py` with output `/eos/.../datamc_postfix_20261113/october_metrics.json`. Slope fits: `slope_err.py` → `slope_fit_stat.json`.
- **MC inventory:** `lxplus:~/bhive_prod_20261112_sol/A/inputs.json` (workflow `hww_allfix_4fs`, created 2026-11-12T16:20:46, analysis_head `71eef55`, sha256 `e0411f09ab1871cd…1b03da`). It has 2437 markers / 22,613 parquets in total. Per era (markers / parquets): preEE 454/3001, postEE 1085/10185, preBPix 551/6096, postBPix 347/3331. Every marker passed expected == processed entries and LFNs == partition. `check_dataset_coverage` passed with 46 MC samples per era. Parquet rows == marker `selected_events` for every sample.
- **Data** (`/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train/<era>/`): every condor partition in `condor/hww_allfix_4fs__train/<era>/<DataDS>/` was checked. Markers exist, expected == processed entries, LFNs == partition, the union of LFNs == the fileset for that dataset, the dataset list == the workflow's data datasets, parquet rows == `selected_events`, (run, lumi, event) is unique across Muon/EGamma/MuonEG/DoubleMuon/SingleMuon, and every weight == 1. **PASS in all four eras:**

  | era | partitions | files | rows | duplicates |
  |---|---|---|---|---|
  | 2022preEE | 52 | 719 | 24,772 | 0 |
  | 2022postEE | 103 | 1510 | 72,139 | 0 |
  | 2023preBPix | 91 | 1260 | 59,543 | 0 |
  | 2023postBPix | 46 | 621 | 32,279 | 0 |

- **Normalisation** is the card-builder path (`scripts/combine/build_cards_from_train.py` + `build_cards_from_templates.normalize_record`). The scale is lumi × σ / Σw. Σw is summed over all TRAIN markers of the sample and era, σ comes from the era dataset config, and lumi from `make_combine_inputs.load_lumi`: 7980.4 / 26671.7 / 17794.0 / 9450.0 pb⁻¹. Route B is off for this workflow.
- **negrw v2** (model `negrw_models_v2_20261112.joblib`, sha256 `af53567c…155cb`) is applied to `DYto2L_2Jets_{10to50,50}` and `WtoLNu_2Jets_{0J,1J,2J}`. They are rescored from the stored gen/LHE columns; the stored `weight_negrw` is ignored. The weight is |w|·g, renormalised per sample and era by Σw / Σ|w|g.
  - Renorm factors for 2022postEE: DY10to50 0.764, DY50 1.023, W0J 1.082, W1J 1.047, W2J 0.886.
  - **Flag:** 2023preBPix `WtoLNu_2Jets_0J` has factor −0.844, from 2 raw events and Σw = −5.4 ± 7.1. That is negligible here (0.01% of the MC), but the card builder does the same thing for small samples.
- **Cross-check:** the per-process integrated yields (no binning) agree with the independent `~/htoww_submit_logs/yields_A_train_20261112.json` to float precision. Example for 2022postEE: tt 68620.94 vs 68620.94, DY 2133.60 vs 2133.60, V+Jets 220.09 vs 220.09. This validates lumi·σ/Σw and the yield-preserving negrw renormalisation. It cannot validate the negrw *shape*, because both paths preserve integrals by construction.

## Numbers: post-fix vs October (same bins, same definitions)

The October values were recomputed from `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/<era>/<era>_processed_histograms.coffea` (the input of `band_breakdown.py`) by `october_metrics.py`, nominal only. The slope is a weighted linear fit of data/MC vs bin centre, in units per 100 GeV. Post-fix errors are statistical (data Poisson ⊕ MC stat). "Band" is the mean relative half-width over populated bins.

**MET (`met_pt`, 19 bins, 0–350 GeV; first populated bin 45–55):**

| era | data/MC (Oct → new) | ratio first → last bin, new (Oct) | slope /100 GeV, Oct → new | MC-stat band Oct → new | October full plotter band |
|---|---|---|---|---|---|
| 2022preEE | 1.009* → 0.926 | 0.94 → 1.17 (1.07 → 1.08) | −0.051 → −0.039 ± 0.014 | 1.32% → 1.03% | 18.7% |
| 2022postEE | 0.923 → 0.918 | 0.95 → 0.85 (1.01 → 0.87) | −0.098 → **−0.097 ± 0.008** | 0.74% → 0.55% | 20.1% |
| 2023preBPix | 0.984 → 0.964 | 0.96 → 0.86 (1.03 → 0.87) | −0.076 → **−0.002 ± 0.010** | 0.95% → 0.76% | 17.5% |
| 2023postBPix | 0.991 → 0.968 | 0.95 → 0.97 (1.00 → 0.82) | −0.065 → **−0.007 ± 0.013** | 1.22% → 1.07% | 18.0% |
| all eras | — → 0.941 | 0.96 → 0.91 | — → −0.046 ± 0.005 | — → 0.39% | — |

\* October 2022preEE data included the duplicated events (review A1); with them removed it was 0.948.

**mT(ℓ1) / mT(ℓ2), slope per 100 GeV, October → new:**

| era | mtl1 | mtl2 |
|---|---|---|
| 2022preEE | −0.021 → +0.001 ± 0.009 | −0.014 → +0.014 ± 0.015 |
| 2022postEE | −0.045 → **−0.010 ± 0.005** | −0.055 → **−0.008 ± 0.008** |
| 2023preBPix | +0.024 → −0.013 ± 0.006 | +0.031 → +0.026 ± 0.010 |
| 2023postBPix | +0.069 → −0.006 ± 0.008 | +0.032 → +0.026 ± 0.014 |

m(ℓℓ) is flat after the fix (slope 0.000 ± 0.005 in 2022postEE).

All χ² values (stat only, normalisation not floated) remain large because of the overall 4–8% deficit. In 2022postEE MET: Oct 1000/18, new 759/18. These are not shape tests and should not be compared with the slope-study χ² (different binning).

## Interpretation (agent's reading, not validated)

- The October correction campaign removed the 2023 MET slope and strongly reduced the 2022postEE mT slopes. In 2022postEE about 10% per 100 GeV of MET slope remains. Before the fix it was common to both 2022 eras; now it is mostly a 2022postEE effect, with a 2.8σ remnant in preEE.
- It is not explained by MC statistics. Without shifts, this production cannot say whether JES/JER/unclustered-MET or the tt μR/μF / top-pT variations cover it. The next check is a RUN production with shifts and a real band.

## Needs Chirayu

- Decide whether the talk shows only the MC-stat band, with the statement "systematics not yet available post-fix".
- A RUN-mode (shifted) production is needed for a post-fix systematic band. That is a Condor submission, so it needs his OK.
