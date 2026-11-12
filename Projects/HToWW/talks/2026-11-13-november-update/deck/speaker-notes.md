---
tags: [slides, speaker-notes]
status: active
date: 2026-11-12
source: laptop
---

# November update r4: speaker notes

Internal CMS talk. The old-card reference and new-production status are explicitly separate. No new A/B limit is claimed.

## 1. Higgs + charm, H → WW

[Open slide](index.html#/title)

Internal CMS talk. The October result is a pre-fix reference. No new A/B limit or trained-model performance is claimed. Results are dated and source-linked; no unproduced A/B limit is implied.

## 2. The H+c analysis in Run 3

[Open slide](index.html#/analysis)

4FS and 3FS are defined on the signal-comparison slide before the detailed construction. The historical fit had a merged SR; the two-SR result is a future production result, not the October fit.

## 3. August → October: building the four-era analysis

[Open slide](index.html#/progress)

August reference is the 19 August analysis-overview deck as recorded in the agreed plan. Do not imply the decrease from 1034 to 691 measures only algorithmic improvements or only luminosity.

## 4. Central samples: full current-analysis inventory

[Open slide](index.html#/central-inventory)

Direct DAS summary census 22:02 CET, no failed queries. Current exact configured versions only;46 perera. Other Higgs (16) includes WH→WW, WH→ττ, ggH, VBF, ZH, ggZH and ttH components. Count one entry per dataset; all selected before cuts. Central H+c counts 1.010M,1.013M,1.005M,.922M. H+b1.006M,2.432M,1.863M,.898M. No model training or jobs run.

## 5. 2024: central background samples are available

[Open slide](index.html#/central-2024)

Broader DAS discovery 22:05 CET corrects missing 2024 samples from literal 2022 primary queries. Exact rawqueries/results preserved; selected 73 dataset options. Standard NanoAODv15 preferred per primary, latest processing and ext retained; exclude BTV/JME/FastSim. NLO DY unbinned e/μ/τ 10–50, >50; W in 14 pT bins/options; Higgs SM WW/ττ and ttH choices. ttHnonbb and individual decays may overlap: do not combine all. Single-top tchannel exactmatch gaps remain. This is not all CMSDAS and not a2024 processing claim.

## 6. October reference: four eras, expected μ < 691

[Open slide](index.html#/historical-result)

Historical card: partial signal scale correction, NLO signal normalization, flat 30% scheme term, no-op JER and missing WH contributions. All numbers are expected, not observed. L-label 62 on original plot is rounded 61.9. The 691→338.5 difference is not a quadrature uncertainty decomposition.

## 7. Higgs-background scale treatment: 691 → 703

[Open slide](index.html#/higgs-scale)

Directly read V1.limit.log and V2.limit.log from ~/htoww_submit_logs/higgs_scale_20261112. Combine 10.6 AsymptoticLimits CLs: V1 median 703,16/84%=469.0242/1106.5151;V2 median691,16/84%=461.0181/1093.1359. Build logs show nontrivial rescalings, diboson unchanged. These are tests on the historical card, not corrected A/B limits.

## 8. What drives the October fit?

[Open slide](index.html#/oct-impacts)

Nominal σ(r)=299.8; freeze groups one at a time. Do not compare these numerical fractions directly to Run2 table conventions. Card read confirms scalevar rows are dash for every tt entry. One electron-reco impact tree unreadable in saved report. The JER group understates actual uncertainty because old JER was a no-op.

## 9. October fit: leading individual nuisance impacts

[Open slide](index.html#/oct-impact-table)

Directly read JSON from October 9 plot folder: 55 nuisances, failed electron reconstruction entry listed separately. rate_tt values are scale factors with absolute errors, not Gaussian pulls. Other nuisance values/errors are in standard nuisance coordinates. Δr signed according to fixed nuisance down/up, so effects can reverse. No new fit run. Do not relabel as expected-limit impacts or r=0/median expected set.

## 10. October card: likelihood scan in μ

[Open slide](index.html#/oct-scan)

New fit, 13 Nov: MultiDimFit grid, 41 points, r in [-1000,1000], Asimov r=1, on the unchanged October workspace (pre-fix: old global LHE fix, JER no-op, provisional c-tag). Stat-only scan freezes allConstrainedNuisances from the total-fit snapshot. A −2ΔlnL=3.84 crossing is a likelihood interval, not CLs; its agreement with 691 is a consistency check. Not the corrected A/B result. Outputs: lxplus ~/htoww_submit_logs/scan_oct691_20261113/.

## 11. Uncertainty shares: our October card vs Run 2

[Open slide](index.html#/run2-compare)

Our values: blind Asimov r=1 on the pre-fix October card, nominal σ(r)=299.8, MultiDimFit singles with one group frozen at a time. Quad = sqrt(σ²−σ²_frozen)/σ, lin = (σ−σ_frozen)/σ; Run 2 caption says change of 1σ when fixed, but its rows are not additive in either convention. Caveats: our scale/PDF/PS includes the signal scalevar biased by the old global LHE fix; JES/JER understated because JER was a no-op in these cards; c-tag 23.5 consistent with the flagged 2022 Up (+43% SR signal); luminosity differs 138 vs 61.9 fb⁻¹ so statistical share is not like for like. Not the corrected A/B fit.

## 12. Data/MC: broad bands hid a visible shape trend

[Open slide](index.html#/oct-datamc)

These are actual data over MC, not blind Asimov shapes. Signal drawn scaled×10000 as labelled by original plot. Large plotting band includes MC statistics and weight variations; does not include object shifts or lnN rates. Observed postEE total ratio 0.923 in original band study. New-production closure has not been established here.

## 13. Where the large uncertainty band came from

[Open slide](index.html#/oct-band)

Checked band_breakdown.py: MC stat plus all stored weight variations, no object shifts and no lnN rates. Direct v12 combined-card inspection: scalevar_muR, muF, muR_muF are absent on tt. Free rate_tt alone would not justify dropping shape uncertainty; exclusion is the actual historical card prescription. Right-hand estimate assumes scale contribution is tt-dominated, not a fresh full band recomputation.

## 14. The MET-slope study exposed inconsistent variations

[Open slide](index.html#/oct-slope)

Original MET χ² values: nominal 418.7, top-pT off 497.1,JERUp/Down 497.1,JESDown 183.1. Separate band-breakdown shape fit 309/19 uses different binning/selection, so do not mix χ²s. Source is runall/slope_study.py. July stored-PuppiMET output already had a slope, ruling out the October Type1 bug as its sole cause.

## 15. What the data/MC investigation changed

[Open slide](index.html#/oct-corrections)

Dedup after removal MET ratio 1.00→0.89; postEE 1.00→0.83. Matching used(event, round(lepton1_pt)), not a complete modern run/lumi/event duplicate scan. The historical review was not independently repeated; new corrections have bounded tests, not a new all-era data/MC closure measurement. Old Asimov limit does not use data, so data duplicates alone did not change it.

## 16. Central signal samples: two independent production issues

[Open slide](index.html#/signal-samples)

Nominal samples remain usable provisionally. Yukawa patch is applied in Fortran but omitted by Python systematics. FxFx settings: etaJetMax999 and coneRadius1 absent; default 2.5/.7. Forward 1 jet fraction≈.98% central versus 6.6–6.8% clean. Corrected H+c/H+b gridpacks sent. GEN reproduction pending.

## 17. Per-event scale repair: check the selected phase space

[Open slide](index.html#/yukawa-check)

GEN-region proxy, not full reconstructed analysis selection. Single-scale events match patch<0.1%; real/counterterm two-scale treatment has≈1% residual. Inclusive reference discrepancies were traced to event-class mix and MG 1 GeV scale-floor events. H+b follow-up validation is separately recorded, not inferred from H+c.

## 18. Corrected gridpack: checks against the clean reference

[Open slide](index.html#/gridpack-validation)

H+c numbers from existing validation slides: 10370 vs 10296 matched events, Higgs-pT χ²/ndf 1.4/10. Do not transfer the H+c numerical validation to H+b. Three-flavour validation is in backup.

## 19. Corrected gridpacks sent to Sebastiano

[Open slide](index.html#/gridpack-handoff)

Corrected H+c and H+b gridpacks have been sent; 3FS validation slides exist. Sebastiano can try the reproduction with increased priority. Do not imply acknowledgement, new production completion or CMS approval.

## 20. Flavour scheme: baseline A, cross-check B

[Open slide](index.html#/arms)

Both arms use σ×BR=0.0016626 pb. B does not automatically close scale/PDF overlap or missing-rate coverage questions; retain those as card-stage checks. This is not a new central 3FS production claim.

## 21. Ratio-method validation: era consistency and decay transfer

[Open slide](index.html#/fs-validation)

Derived on official Run3γγ; no private exploratory γγ samples used. c-hadron threshold 5 GeV,|η|<2.5. Run2 WW/γγ χ² 18.9/10,9 of 10 bins within 1–2σ. The 20–30 GeV outlier was examined per-file and with Run3γγ; consistent with a Run2γγ fluctuation, not established decay dependence. Run3 weights 1.052 vsWW 1.048 in that bin.

## 22. Does the ratio cover a real 3FS H→WW sample?

[Open slide](index.html#/fs-reco)

Not the current Run3 MVA selection: standalone OS eμ with tight μ / WP80 e, 20/10 GeV, mll 12–72,mT cuts, DeepJet medium UL18 stand-in. Real 3FS SR yield versus 4FS +6.3±2.3%, variation+7.3%. Njets χ² 23/5 not covered;2jet3FS/4FS≈0.82. Historical “no 3FSWW inRun 3” reason to avoid stitching is now obsolete: private 3FS and re-NANO exist.

## 23. Rates and sample coverage brought up to date

[Open slide](index.html#/samples)

The H→ττ update is complete; a global Higgs-rate validation is not yet claimed.

## 24. Prompt-lepton selection aligned with HWW

[Open slide](index.html#/leptonmva)

Muon max difference 3.05e-7, electron 3.27e-7 including threshold-tie coverage. SF factorization concern from the earlier review is not supported by the producer comparison. Measurement provenance/correlations and c-tag calibration are separate questions.

## 25. Negative weights: retraining the reweighting model

[Open slide](index.html#/negrw)

The estimator can be negative; do not call every output weight positive. Closure is a ratio of signed sums, with correlated delta-method errors in the corrected report. Shape agreement between two models is not proof of agreement with the original signed distribution.

## 26. Overall closure hides sample-level shape bias

[Open slide](index.html#/negrw-limits)

This is a limitation in both v2 and July; July shape χ² 47.9/20 for the shown diagnostic. The band is ensemble spread, not an independently validated envelope of all method biases.

## 27. Systematics: implementation and physics scope

[Open slide](index.html#/syst-overview)

Full explanations and implementation/evidence status for every source are in backup. tt is excluded from configured scalevar/ps rows, not automatically from all theory-named nuisances. Trigger SFs remain disabled by decision; not a measured zero.

## 28. Normalisation: luminosity, pileup

[Open slide](index.html#/backup-syst-norm)

 Implementation nuisance names: lumi_ , CMS_pileup_ . See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 29. Lepton efficiency scale factors

[Open slide](index.html#/backup-syst-lepsf)

 Implementation nuisance names: CMS_eff_m_id_ , CMS_eff_m_iso_ , CMS_eff_m_promptMVA_ , CMS_eff_e_id_ , CMS_eff_e_promptMVA_ , CMS_eff_e_reco_{below20, 20to75, above75}. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 30. Lepton momentum scale and resolution

[Open slide](index.html#/backup-syst-lepscale)

 Implementation nuisance names: CMS_scale_m_ , CMS_res_m_ , CMS_scale_e_ , CMS_res_e_ . See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 31. Jets, MET, c-tagging, trigger

[Open slide](index.html#/backup-syst-jets)

 Implementation nuisance names: CMS_scale_j_ , CMS_res_j_ , CMS_met_unclustered_ , CMS_ctag2d_ , —. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 32. Theory: parton shower, scales, top pT

[Open slide](index.html#/backup-syst-theory)

ISR/FSR, top-pT and HF prescriptions follow the analysis sources, not universal uncertainty sizes. AN-23-102§7.1/Table16 sources 50%ggH+HF; extension toVBF is an analysis choice requiring review. LHE×2/.5 scales are generator variations; three independent directions and shared correlation are current analysis choices, not the paper seven-point-envelope prescription. Implementation nuisance names: ps_isr, ps_fsr, scalevar_muR, _muF, _muR_muF, top_pt, higgs_plus_c. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 33. PDF and αS

[Open slide](index.html#/backup-syst-pdf)

PDF/alphaS method: PDF4LHC15eq26–28 or 21 eq 6.6–6.8 with different αS steps, not interchanged. H+c7.43±.14% is our own clean 4FS gridpack Hessian calculation,10370 events, not a percentage fromthepaper. H+b +3.36/−3.44 is an interpolation ofLHCHWG 2025-011 Table 1 at 125.09, not yet installed. H+c alphaS process-specific number remains missing. Implementation nuisance names: lhe_pdf, xsec_hplusc_PDF, lhe_alphaS, —, —. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 34. Signal flavour scheme and negrw

[Open slide](index.html#/backup-syst-scheme)

Paper motivates flavour-scheme comparison andstitching; c-hadron shape ratio and mirrored Down are our analysis construction with official-sample checks. negrw ensemble spread is an implemented method uncertainty, not a paper-supplied universal coverage guarantee. Implementation nuisance names: xsec_hplusc_3FS_4FS, —, CMS_negrw_vjets. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 35. Rates, fit freedom, MC statistics

[Open slide](index.html#/backup-syst-rates)

Single top −1.27/+1.67%, diboson 3.7%, V+jets 2.7%, Higgs 5% are inherited AN prescriptions, not newly calculated 2024 or Run 3 theory errors. BR 1% is the current configured prescription; its merged-background scope is broader than the decay components. rate_tt and autoMCStats are fit/statistical model choices, not external theory uncertainties. Implementation nuisance names: —, —, —, rate_tt, autoMCStats 10. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 36. Framework optimization: remove repeated work

[Open slide](index.html#/speed)

Legacy stores nominal+15 shifts and all 53 weight columns; TRAIN is nominal-only. The proposed combined writer will store more than TRAIN: its size/runtime have not been measured. 16/16 and 64/64 parquet equality checks refer to the controlled optimization test.

## 37. A compact event record for offline iteration

[Open slide](index.html#/framework-flow)

Intended combined single-pass workflow, not claimed complete. The new model cannot be used before it is trained: store event inputs first, then score offline. The exact user wording is “a bit of refactoring”; this is his presentation preference, not an engineering-effort estimate. Automatic Condor retries/global redirector remain planned.

## 38. Event classifier: five held-out models per arm

[Open slide](index.html#/mva)

Features: 14 kinematic + 11 c-tag one-hot + nSV. Cached constructed datasets use unique fold/split identities. RUN/registration guard feature/selection hashes, class order and provenance. Same test fold remains assigned for object-shifted copies.

## 39. Proposed baseline and path to the result

[Open slide](index.html#/open)

No corrected limit exists yet: Arm A training and scoring are in production. Listed inputs are external or check items (Livio c-tag update; process-specific alphaS calculation; H+b overlap with the 5% Higgs rate; BR scope; ttH tau-tau coverage; negrw closure needs scored outputs; hDamp deferred). Do not present this as a result or as approval readiness.

## 40. Backup

[Open slide](index.html#/backup)

Section divider.

## 41. Backup: the ratio does not cover jet multiplicity

[Open slide](index.html#/backup-fs-njet)

Yield closure does not imply closure of every discriminating variable.

## 42. Backup: October MVA templates before the fit

[Open slide](index.html#/backup-prefit)

These templates belong to the historical 691 card, not the newly trained models.

## 43. Backup: validation duplication and model selection

[Open slide](index.html#/mvacheck)

Inference fixture: 170465 emitted rows for 64073 events. Reproducibility boundary is same hardware/setup; do not claim universal cross-GPU bitwise equality. The v11 validation/inference was also affected, so its published internal metrics are not a clean baseline.

## 44. Backup: definitions and fit conventions

[Open slide](index.html#/definitions)

Keep the statistical model and the saved-output schema attached to every result.

## 45. Backup: hDamp probes tt matching

[Open slide](index.html#/hdamp)

Configured samples are not an implemented or validated alternative-sample nuisance.

## 46. Backup: negrw in the selected eμ signal region

[Open slide](index.html#/backup-negrw-sr)

W+1J χ² 139.4/20 (v2) vs 185.5/20 (July); 120.1/155.6 with the nuisance in the saved report. The horizontal nuisanceband should not be represented as independent measurement errors.

## 47. Backup: c-tag categories enter the event MVA

[Open slide](index.html#/backup-ctag)

Tagger category consistency must be preserved through training, scoring and fitting.

## 48. Backup: scale and PDF weights after the rebuild

[Open slide](index.html#/backup-gridpack-weights)

Generation-level agreement supports the rebuilt setup; detector-level reproduction remains separate.

## 49. Backup: private 3FS validation

[Open slide](index.html#/backup-gridpacks)

Generator validation and central-sample reproduction are separate stages.

## 50. Minor updates: cross sections and normalization

[Open slide](index.html#/minor-rates)

Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.

## 51. Minor updates: samples and production inputs

[Open slide](index.html#/minor-samples)

Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.

## 52. Minor updates: correction details

[Open slide](index.html#/minor-corrections)

Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.

## 53. Minor updates: outputs and integrity checks

[Open slide](index.html#/minor-framework)

Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.

## 54. Minor updates: processing and remaining scope

[Open slide](index.html#/minor-operations)

Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.
