---
tags: [slides, speaker-notes]
status: active
date: 2026-11-12
source: laptop
---

# November update r2: speaker notes

Internal CMS talk. The old-card reference and new-production status are explicitly separate. No new A/B limit is claimed.

## 1. Higgs + charm, H → WW

[Open slide](index.html#/title)

Internal CMS talk. The October result is a pre-fix reference. No new A/B limit or trained-model performance is claimed. Main status follows the saved 12 November 20:29 CET record.

## 2. The H+c analysis in Run 3

[Open slide](index.html#/analysis)

4FS and 3FS are defined on the signal-comparison slide before the detailed construction. The historical fit had a merged SR; the two-SR result is a future production result, not the October fit.

## 3. August → October: building the four-era analysis

[Open slide](index.html#/progress)

August reference is the 19 August analysis-overview deck as recorded in the agreed plan. Do not imply the decrease from1034 to691 measures only algorithmic improvements or only luminosity.

## 4. October reference: expected μ < 691

[Open slide](index.html#/historical-result)

Important pre-fix caveats: JER no-op, WH cross section zero, partial signal scale repair, NLO-like H+c normalization and flat30% scheme lnN. The stat-only and freeze-autoMCStats configurations are historical. Do not combine or subtract these as independent uncertainty components.

## 5. A diagnostic of the Higgs-background scale treatment

[Open slide](index.html#/higgs-scale)

V0=691 was recovered from parent history; the V1 log was directly read at18:47. V2 was still running at18:51 and no completion is asserted. The treatment has not been adopted as the final physics prescription.

## 6. Two issues in the central signal samples

[Open slide](index.html#/signal-samples)

User says nominal samples are usable and expects a small effect inside the central selection. The ≈1–2% statement is the communicated selection-level estimate, not a new measurement here. Do not imply the scale workaround fixes the fragment’s nominal-generation defect.

## 7. Corrected gridpack: checks against the clean reference

[Open slide](index.html#/gridpack-validation)

H+c numbers from existing validation slides:10370 vs10296 matched events, Higgs-pT χ²/ndf1.4/10. H+b sent status is Chirayu’s own report; do not transfer the H+c numerical validation to H+b. Three-flavour validation is in backup.

## 8. Flavour scheme: two complementary strategies

[Open slide](index.html#/arms)

Both arms use σ×BR=0.0016626pb. B does not automatically close scale/PDF overlap or missing-rate coverage questions; retain those as card-stage checks. This is not a new central3FS production claim.

## 9. Rates and sample coverage brought up to date

[Open slide](index.html#/samples)

The H→ττ update is complete; a global Higgs-rate validation is not yet claimed.

## 10. Prompt-lepton selection aligned with HWW

[Open slide](index.html#/leptonmva)

Muon maxdifference3.05e-7, electron3.27e-7 including threshold-tie coverage. SF factorization concern from the earlier review is not supported by the producer comparison. Measurement provenance/correlations and c-tag calibration are separate questions.

## 11. Negative weights: retraining the reweighting model

[Open slide](index.html#/negrw)

The estimator can be negative; do not call every output weight positive. Closure is a ratio of signed sums, with correlated delta-method errors in the corrected report. Shape agreement between two models is not proof of agreement with the original signed distribution.

## 12. Overall closure hides sample-level shape bias

[Open slide](index.html#/negrw-limits)

This is a limitation in both v2 and July; July shape χ²47.9/20 for the shown diagnostic. The band is ensemble spread, not an independently validated envelope of all method biases.

## 13. Systematics: implementation and physics scope

[Open slide](index.html#/syst-overview)

Full explanations and implementation/evidence status for every source are in backup. tt is excluded from configured scalevar/ps rows, not automatically from all theory-named nuisances. Trigger SFs remain disabled by decision; not a measured zero.

## 14. Framework optimization: remove repeated work

[Open slide](index.html#/speed)

Legacy stores nominal+15 shifts and all53weight columns; TRAIN is nominal-only. The proposed combined writer will store more than TRAIN: its size/runtime have not been measured. 16/16 and64/64parquet equality checks refer to the controlled optimization test.

## 15. A compact event record for offline iteration

[Open slide](index.html#/framework-flow)

Intended combined single-pass workflow, not claimed complete. The new model cannot be used before it is trained: store event inputs first, then score offline. The exact user wording is “a bit of refactoring”; this is his presentation preference, not an engineering-effort estimate. Automatic Condor retries/global redirector remain planned.

## 16. Event classifier: five held-out models per arm

[Open slide](index.html#/mva)

Features:14kinematic+11c-tagonehot+nSV. Cached constructed datasets use unique fold/split identities. RUN/registration guard feature/selection hashes, class order and provenance. Same test fold remains assigned for object-shifted copies.

## 17. A duplicated validation batch changed model selection

[Open slide](index.html#/mvacheck)

Inference fixture:170465emitted rows for64073events. Reproducibility boundary is same hardware/setup; do not claim universal cross-GPU bitwise equality. The v11 validation/inference was also affected, so its published internal metrics are not a clean baseline.

## 18. Fast iteration cards from the TRAIN event records

[Open slide](index.html#/results)

No production scoring or Combine run. Original stored July negrw weights are ignored and v2 rescored from generator columns; normalize after all shards merge. A merged-SR iteration result must not be compared as though identical to the intended split-SR full-systematics fit.

## 19. Production: complete inputs, training underway

[Open slide](index.html#/status)

Exact saved selected rows A6959308 B6978013. B single job9706954 underDAG9706953. Afolds9706926–9706928running,9706929–30idle. This slide is a dated saved record, not live queue monitoring. No new job operations performed by keeper.

## 20. Progress made, and questions for the conveners

[Open slide](index.html#/open)

Analysis follow-ups remain: provisionalc-tagcalibration, H+cαSrate, H+bPDF+αSoverlap, HiggsBRscope, ttHττcoverage, negrwfit-binclosure. hDamp is deferred by instruction; no alternative-sample template is claimed.

## 21. Backup

[Open slide](index.html#/backup)

Section divider.

## 22. Backup: definitions and fit conventions

[Open slide](index.html#/definitions)

Keep the statistical model and the saved-output schema attached to every result.

## 23. Normalisation: luminosity, pileup

[Open slide](index.html#/backup-syst-norm)

Implementation nuisance names: lumi_ , CMS_pileup_ . See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 24. Lepton efficiency scale factors

[Open slide](index.html#/backup-syst-lepsf)

Implementation nuisance names: CMS_eff_m_id_ , CMS_eff_m_iso_ , CMS_eff_m_promptMVA_ , CMS_eff_e_id_ , CMS_eff_e_promptMVA_ , CMS_eff_e_reco_{below20, 20to75, above75}. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 25. Lepton momentum scale and resolution

[Open slide](index.html#/backup-syst-lepscale)

Implementation nuisance names: CMS_scale_m_ , CMS_res_m_ , CMS_scale_e_ , CMS_res_e_ . See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 26. Jets, MET, c-tagging, trigger

[Open slide](index.html#/backup-syst-jets)

Implementation nuisance names: CMS_scale_j_ , CMS_res_j_ , CMS_met_unclustered_ , CMS_ctag2d_ , —. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 27. Theory: parton shower, scales, top pT

[Open slide](index.html#/backup-syst-theory)

Implementation nuisance names: ps_isr, ps_fsr, scalevar_muR, _muF, _muR_muF, top_pt, higgs_plus_c. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 28. PDF and αS

[Open slide](index.html#/backup-syst-pdf)

Implementation nuisance names: lhe_pdf, xsec_hplusc_PDF, lhe_alphaS, —, —. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 29. Signal flavour scheme and negrw

[Open slide](index.html#/backup-syst-scheme)

Implementation nuisance names: xsec_hplusc_3FS_4FS, —, CMS_negrw_vjets. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 30. Rates, fit freedom, MC statistics

[Open slide](index.html#/backup-syst-rates)

Implementation nuisance names: —, —, —, rate_tt, autoMCStats 10. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.

## 31. Backup: hDamp probes tt matching

[Open slide](index.html#/hdamp)

Configured samples are not an implemented or validated alternative-sample nuisance.

## 32. Backup: negrw in the selected eμ signal region

[Open slide](index.html#/backup-negrw-sr)

W+1J χ²139.4/20 v2185.5/20July, 120.1/155.6withnuisance in savedreport. The horizontal nuisanceband should not be represented as independent measurement errors.

## 33. Backup: c-tag categories enter the event MVA

[Open slide](index.html#/backup-ctag)

Tagger category consistency must be preserved through training, scoring and fitting.

## 34. Backup: scale and PDF weights after the rebuild

[Open slide](index.html#/backup-gridpack-weights)

Generation-level agreement supports the rebuilt setup; detector-level reproduction remains separate.

## 35. Backup: private 3FS validation

[Open slide](index.html#/backup-gridpacks)

Generator validation and central-sample reproduction are separate stages.

## 36. Backup: traceable inputs and output boundaries

[Open slide](index.html#/backup-production)

Timestamps, manifests and model identities travel with every later result.
