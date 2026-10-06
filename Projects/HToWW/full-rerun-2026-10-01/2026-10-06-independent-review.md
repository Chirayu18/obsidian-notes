---
tags: [reference]
status: active
date: 2026-10-06
source: lxplus
---
# Independent review of `hww_combine_full` before the 4-era reprocessing (2026-10-06)

Read-only review of the repo `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` (branch `hww-analysis`, today's uncommitted fixes included), the 2022 outputs and the card wrapper. All numbers come from the existing (pre-fix) 2022 parquets or from small NanoAOD samples. Scratch scripts are in `/eos/user/c/cgupta/higgscharm/runall/review/`: `dup*.py`, `norm*.py`, `onehot_test.py`, `veto.py`, `metlep.py`, `jecinput.py`, `muiso.py`, `wcols.py`, `sort.py`.

Ranked by impact. Each finding is marked **CONFIRMED** (measured, or read unambiguously in the code) or **SUSPECTED**.

---

## A. High impact

### A1. CONFIRMED: 2022preEE data is double-counted, and the preEE "flat ≈1.0" result comes from that
- **Where:** `analysis/selections/trigger.py:155` (`return dataset_masks.get(dataset_name, all_combined_mask)`) together with `analysis/filesets/utils.py:81-86`.
- **What is wrong:** the 2022preEE fileset contains `SingleMuonRun2022C` and `DoubleMuonRun2022C`, both with key `muon`. `get_dataset_name` returns `"SingleMuon"` / `"DoubleMuon"` for them, which are not keys of `hlt_paths` (`MuonEG`, `Muon`, `EGamma`). The lookup then silently falls back to the MC mask, i.e. the OR of every trigger, so these PDs keep MuEle- and Ele30-triggered events that MuonEG and EGamma already hold.
- **Evidence:** matching on `(event, round(lepton1_pt))` across the eight preEE data parquets finds 2243 extra rows out of 37373 (6.0%):
  - 1484 rows in both SingleMuon and MuonEG
  - 343 rows in DoubleMuon, MuonEG and SingleMuon
  - 32 rows in DoubleMuon and MuonEG
  - 30 rows in DoubleMuon and SingleMuon
  - a few with EGamma

  The matched events have identical kinematics to within float precision; jet multiplicity is identical in 99.8% of them.
- **Impact:** preEE data/MC drops from 1.009 to **0.948** once the duplicates are removed. After the removal, preEE also shows a slope:

  | preEE, after removal | lowest bin | highest bin |
  |---|---|---|
  | MET | 1.00 | 0.89 |
  | mTll | 0.95 | 0.91 |
  | Njets | 0.96 | 0.87–0.93 |

  This is the same pattern as postEE (0.923; MET 1.00 → 0.83). **The argument "same tt sample, slope only in postEE, so the cause is era-specific JEC/JER/pileup" no longer holds.** The slope is mostly common to both eras, which points back to MC modelling (tt, MET resolution) plus a smaller postEE-specific part. The Asimov limit is unaffected, because it uses no data. Any data fit, CR normalisation or unblinding is affected.
- **Fix:**
  - In `trigger_mask`, map `SingleMuon` to the `Muon` logic (`SingleMu & ~MuEle`).
  - Give `DoubleMuon` a zero mask, since no DiMu path is used. Alternatively, drop `DoubleMuonRun2022C` from the fileset.
  - Raise an error for any data PD name that is not a key of `hlt_paths`, instead of returning the OR.
  - Only the two 2022C data PDs need reprocessing.

### A2. CONFIRMED: the MVA has received no c-tag input since the switch to `hww_combine_full`
- **Where:** `analysis/postprocess/inference.py:137-144`, which fills missing features with 0, and `runall/pipeline_2022.sh:24`.
- **What is wrong:** the v11_2dcats model takes 26 features. Eleven of them are one-hot columns, `cjet_cand_ctag2d_{L0,C0..C4,B0..B4}`. The processor never writes these. In July they were added by hand with `b-hive/scripts/append_onehot.py` before rescoring (the docstring warns that the model "silently sees an all-zero category vector" otherwise). The new pipeline skips that step.
- **Evidence:**
  - `logs_runall/inf2_full_2022postEE.log` and the earlier `inf_hww_combine_full_*` logs contain 7843 warnings: all 11 features are missing in all 713 files.
  - The stored scores are reproduced exactly with zeros in those columns.
- **Impact (postEE, re-scored with the one-hots restored):** argmax fractions move by only 0–3 points.

  | sample | in SR, as run | in SR, one-hots restored |
  |---|---|---|
  | H+c | 0.897 | 0.894 |
  | tt | 0.168 | 0.160 (about −5% tt in SR) |
  | tW | 0.177 | 0.170 |
  | WW | 0.280 | 0.274 |

  So the model barely uses the c-tag categories. The limit effect is small but in the favourable direction. The setup is still wrong: the card's `CMS_ctag2d` SF acts on a variable that the classifier never sees.
- **Fix:**
  - Compute the one-hots in the processor (new histogram axes from `cvsl`/`cvsb`, using the `append_onehot.py` edges), or add the append step to the pipeline.
  - Make `inference.py` raise on a missing feature instead of warning.

### A3. CONFIRMED: two of the four WH→WW samples have `xsec: 0.0`, so more than half of WH→WW is missing
- **Where:** all four era yamls, entries `WminusH_WtoLNu_Hto2Wto2L2Nu` and `WplusH_Wto2Q_Hto2Wto2L2Nu` (`xsec: 0.0   # UNVERIFIED ... must be set before use`). The 2022postEE yaml has them around lines 539-550.
- **What is wrong:** both samples are processed (12.5k and 14.6k selected events in postEE), but `read_scale` turns xsec 0 into a scale of 0 without any warning.
- **Evidence:** the postEE WH→WW yield is 7.6 events (W⁺ℓν 2.68, W⁻qq 4.91). The yaml's own decomposition gives:
  - W⁻ℓν = 0.012934 × 0.3258 = 0.004214 pb, which adds about 1.7 events;
  - W⁺qq = 0.020335 × 0.6741 = 0.013708 pb, which adds about 7.7 events.

  WH→WW should therefore be about 2.2 times larger.
- **Impact:** about +3% on higgsbkg (around 9 events on roughly 330 in postEE). Small for the limit; it is a clear bug.
- **Fix:** set the two cross sections. Make `read_scale` raise on `xsec <= 0` for any sample listed in the process map.

### A4. SUSPECTED (partly measured): the Type-1 re-correction sends JER smearing of lepton-dominated jets into MC MET
- **Where:** `analysis/corrections/jerc.py`, the metinfo for nominal, JES and JER (about lines 360-372 and 405-460).
- **What is wrong:** today's fix gets the sign right. However, the sum Σ(nano − new) runs over **all** jets. That includes jets with EM fraction > 0.9, jets whose energy is mostly the selected electron or muon, and jets without muon subtraction. The NanoAOD Type-1 recipe excludes all of these. In MC the new pT includes the stochastic and scaling JER smearing, so the lepton energy inside those jets gets smeared into the MET. Data is not smeared.
- **Evidence (6000 tt events and 6000 MuonEG 2022F events, ≥2 leptons):**

  | quantity | tt MC | data |
  |---|---|---|
  | total MET change from re-correction, median / 90% | 3.95 / 14.0 GeV | 1.0 / 3.9 GeV |
  | part from jets within ΔR<0.4 of a selected lepton, median / 90% | 1.4 / 3.7 GeV | 0.44 GeV median |
  | lepton-overlapping jets with EMF > 0.9 or muEF > 0.8 | 68% | — |

- **Impact:** extra MET resolution in MC only. This pushes MC into the MET tail, the same direction as the observed data/MC slope. It was not present in the July (stored PuppiMET) runs, which also had a slope, so it is not the root cause. It will add to the slope after reprocessing and changes an MVA input relative to training.
- **Fix:**
  - In the Type-1 sum, use only jets with new pT > 15, (chEmEF + neEmEF) < 0.9 and ΔR > 0.4 to the selected leptons (or muon-subtracted pT).
  - Decide explicitly whether JER smearing should be propagated to PuppiMET at all.
  - Validate the reprocessed MET with a data/MC check that compares against the stored PuppiMET.

---

## B. Medium or low impact, CONFIRMED

1. **Muon scale/smearing JSON pinned to a buggy version.** `correctionlib_files.py` `muon_ss` points at `MUO/.../2025-08-14` for all Run 3 eras. The MUO changelog for 2026-04-28 (all four eras) says: "produced again to fix a bug ... random (deterministic) seed not properly initialised ... muons with same properties would end up having the same random number ... introducing a bias".
   - Fix: point to `2026-04-28` or `latest` (`muon_Z` 2026-06-18 changes only the HLT SFs and the inf encoding).
   - Impact: small bias in MC muon pT smearing; it enters lepton pT, mT and MET-based inputs.
2. **NNLOPS weights applied to an aMC@NLO sample.** `correction_manager.py` applies `add_nnlops_weight(generator="powheg")` to every `GluGluH*` dataset. `GluGluHto2Tau` is `amcatnloFXFX` (mean weight 0.963), so it gets powheg splines. `GluGluHto2Wto2L2Nu` is powheg-jhugen, which is fine.
   - Fix: use the `mcatnlo` splines for the 2Tau sample, or skip it.
   - Impact: about 4% on 46 events.
3. **Diboson theory shapes are no-ops.** WW, WZ and ZZ are inclusive pythia8 samples with no LHEScaleWeight or LHEPdfWeight, so `weight_scalevar_*` and `weight_lhe_*` are absent. The builder silently falls back to nominal. The yaml comment ("diboson scalevar now ENABLED = theo_vv") is therefore wrong.
   - The only diboson uncertainty is `xsec_diboson` 3.7%.
   - There is also no gg→WW sample in any fileset; that background is missing (a few % of WW).
   - Consider powheg `WWto2L2Nu` plus `GluGluToContinToWW` samples.
4. **The builder still degrades silently.** `make_combine_inputs.py:283-284` (`w = df[col] if col in df.columns else nominal_w`) is the same pattern as the Oct-1 dead-nuisance bug.
   - Fix: warn per sample, and raise if a shape systematic is missing in every sample of a process that the card marks with "1".
   - Similar silent paths: `toppt.py` and `partonshower.py` use catch-all `except` that only prints; `lhescale.py` only prints for vectors whose length is not 9; `get_metfilters_mask` skips missing flags; `inference.py` fills missing features with 0 (see A2).
5. **No third-lepton veto.** `select_hww_ll_pair` takes the two leading tight leptons; `one_ll_pair` therefore just means "at least 2 leptons". WZ/ZZ 3- and 4-lepton events enter (WZ is 304 events in postEE). The selection defines `one_electron`/`one_muon` but does not use them.
   - Recommendation: veto any additional loose lepton (standard in HWW).
   - Also: `transverse_mass_*` cuts are defined but not in the `base` category, so no mT cut is applied. The analysis log says otherwise.
6. **Jets are not re-sorted after JEC/JER.** `object_selections.py` `select_leading_jets` sorts `jets` and then overwrites the result with `ak.pad_none(self.objects['jets'], ...)`, which is unsorted.
   - Measured: jet2_pt > jet1_pt in 1.7% of tt events and 0.45% of data events (the asymmetry comes from MC smearing).
   - The parquet `jet_pt`, `jet_eta` and `jet_phi` columns are `ak.firsts`, i.e. the first jet, not the leading one.
   - Fix: use the sorted variable and sort `objects['jets']` once after selection.
7. **Muon ID/ISO SFs are skipped below 15 GeV.** `muon.py:152,234` gives SF = 1 for muons with 10 < pT < 15, which the selection allows as the subleading lepton. Small.
8. **Electron ID SF uses `eta`, not SC eta.** `electron.py:get_id_weights_run3` passes `eta` instead of `eta + deltaEtaSC`. Small.
9. **JEC compound evaluated with the wrong input pT.** `jerc.py` evaluates `L1L2L3Res` with `JetPt` = NanoAOD-corrected pT instead of raw pT. Measured effect on the factor: −0.13% (15–30 GeV) to −0.02% (> 50 GeV). Negligible. Fix it anyway with `j["pt"] = j["pt_raw"]` before `get_corr_inputs`.
10. **Small `jerc.py` defects.**
    - `Path(_jersmear_path).exists` is missing its `()`, so it is always true.
    - `warnings` is used but not imported.
    - The JEC-tag sanity check (`raise (f"...")` with wrong precedence) can never fire.

    None of these change results today.
11. **Full jet-veto-map prescription.** Any jet with pT > 15, tight ID, EMF < 0.9 and no muon overlap, at any η, vetoes the event. Measured on 40k NanoAOD events: 4.0% of MuonEG 2022F/G and 7.1% of TTto2L2Nu events are vetoed. The slope study's leading-jet-only veto removes 1.3–1.7%.
    - In eμ + MET > 45: data 3.6–7.4% (about 110 events, so low statistics) vs MC 6.8%.
    - There is no sign of a strong MET dependence. The rule is mandatory for 2022EE/2023BPix, so apply it.

## C. SUSPECTED (cross sections and modelling)

1. **ZH double counting.** `ZH_ZtoAll_Hto2Wto2L2Nu` xsec 0.021559 = 0.944 pb × 0.02284. 0.944 pb is the 13.6 TeV *total* ZH (qq + gg). ggZH (0.1355 pb) is added separately, so qqZH is about 17% high and ggZH is counted twice. Check against the LHCHWG 13.6 TeV table (qqZH ≈ 0.808 pb).
2. **ggH cross section looks like a 13 TeV value.** `GluGluHto2Wto2L2Nu` xsec 1.0825 pb. 52.23 pb (13.6 TeV N3LO) × 0.02284 = 1.193 pb, about 10% higher. VBF (0.09305) does match 13.6 TeV.
3. **Wγ overlap.** Wγ samples (`WGtoLNuG_PTG*`) overlap with the jet-binned W+jets samples (prompt photon pT > 10). When WG enters the card at retraining, implement gen-photon overlap removal on W+jets. `get_stitching_mask` exists but is unused.
4. **Large 2022postEE muon ISO SF.** `NUM_TightPFIso_DEN_TightID` for |η| < 1.2 is 0.74–0.80 at pT 16, 0.88 at 27 and 0.92 at 35 GeV. preEE is 0.96–0.99. The values are identical in the 2025-08-14 and 2026-06-18 JSONs, so they are official.
   - Measured effect: −4.6% on postEE MC normalisation.
   - It is flat in mTll, MET and Njets, so it is **not** the slope.
   - Worth one question to MUO, because a wrong SF here would shift the postEE normalisation by about 5%.
5. **Remaining overall deficit.** With duplicates removed, both eras are about 5–8% low in data, with a common slope. The candidates that survive this review:
   - eμ trigger efficiency (no trigger SFs; MC efficiency is typically 1–3% above data, more at the thresholds);
   - tt modelling: top-pT, hdamp/ISR, and the scale Down variations that improved χ² in the slope study;
   - the MC-only MET smearing from A4.

   After the reprocessing, redo the slope study on deduplicated preEE data and compare the eras before concluding that the effect is era-specific.

## D. Card and wrapper (beyond the known design points)

- **Missing columns:** the `weight_*` fallback to nominal (B4) still applies to every shape row.
- **Scale normalisation on signal:** `scalevar_*` act on signal and backgrounds including their normalisation (H+c muR Up/Down = 1.031 / 0.842; ggH ±24%). This is shared across processes and eras. Already noted as a design point; the ggH ±24% from the NLO sample is far above the N3LO uncertainty.
- **Object-shift trees:** weights in the shift trees now carry nominal top-pT; lhescale/lhepdf/PS/higgs_hf add nominal 1 under shifts; pileup, lepton SFs, ctag2d and nnlops are applied. Consistent.
- **tt alternative samples:** all at xsec 98.578 = nominal, so the ratio carries only acceptance. Fine, since `rate_tt` floats. mtop ±1 GeV is used unscaled (conservative).
- **Two workflows in sync:** `hww_combine_full_ttsyst.yaml` differs from the main yaml only in datasets and `object_shifts`.

## E. Checked and found clean

- **Today's fixes:**
  - JER split SF ± absolute SFUncertainty, and the JER JSON tags exist for every era (JRV2 for 2022, JRV3 Cv1234 / RunD for 2023).
  - The Type-1 sign: coffea computes met + Σ(jet_pt − jet_pt_orig) and the code passes (nano, new). Correct.
  - toppt nominal under shifts.
  - electron_ss `smear_up`/`smear_down`: keys and input order match the JSON; scale_up/down are multiplicative factors 1 ± unc.
  - lhepdf cap (WminusHTo2Tau pdfUp/nom was 22.8 pre-fix, as expected).
- **JEC tags in `jec_params_correctionlib.yaml`:** they match the `latest` JSONs (V4 MC/DATA, with a run input for data). The data JEC raises MuonEG 2022F jets by about +1% at 15–50 GeV relative to NanoAOD, while MC moves by about 0.
- **Lumi:** 7980.4 / 26671.7 / 17794 / 9450 pb⁻¹; 1.4% for 2022 and 1.3% for 2023.
- **Golden JSONs and pileup keys** per era.
- **MET filters:** standard Run 3 list, the same for data and MC.
- **NanoV12 jet ID** workaround.
- **Other trigger PD logic:** MuonEG / Muon / EGamma (and 2023 Muon0/1, EGamma0/1) are exclusive. The postEE data has 0 duplicate rows.
- **sumw records:** filenames are deterministic (partition key), so retries overwrite instead of double-counting. `skipbadfiles` is off, so jobs fail loudly.
- **Stitching:**
  - W jet bins 0J/1J/2J and DY mass bins are exclusive by construction.
  - TTto2L2Nu / TTtoLNu2Q / TTto4Q are exclusive.
  - The `-ext` samples (key `tt-ext`) are not processed, so there is no double counting.
- **Electron SS EtDependent:** input order (`syst, run, ScEta, r9, pt, seedGain` / `syst, pt, r9, ScEta`) is correct.
- **Muon ID/ISO JSON η convention:** symmetric in 2022 and signed in 2023; the code passes |η| for ID and signed η for ISO. Correct for 2022; for 2023 the ID uses |η|, which loses the small η asymmetry. Minor.
- **Silent `negrw` substring catch:** the dataset match is anchored, so the WH signal is not reweighted.
