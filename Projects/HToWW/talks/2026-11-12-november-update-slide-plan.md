---
tags: [reference, presentation]
status: active
date: 2026-11-12
source: laptop
evidence: slide-plan
---

# November analysis update: slide plan and systematic explanations

Internal research/group presentation draft for Chirayu's talk tomorrow. User asked for analysis updates since a presentation around8September, then stopped the slide subagent and requested discussion first. **No subagent or deck authoring restarted.** This is an ordinary planning note, not a keeper-owned deck edit. The actualSeptember presentation has not yet been compared, so do not label every item as new since that deck.

Latest explicit requests: **“implement hdamp also”**, **“add a detailed breakdown of each systematic and its implementation, with plots and results of checks where nessary”**, and **“also an explaination for each systematic on what it is etc in the slides”**.

## Storyline

1. Analysis/channel/four-era overview and current result boundary.
2. ArmA central4FS and ArmB stitched3FS/4FS: definitions, motivation, normalization and comparison.
3. Sample updates and process-specific125.09normalization, including H→ττ replacement; distinguish generated mass125 from normalization125.09.
4. Prompt-lepton MVA: Thomas's WPs, vectorized ONNX, reference validation and threshold-tie correction. This is separate from the event classifier. State remaining SF/calibration limitations.
5. Processing speedups: writer/caches/once-per-chunk evaluation, controlled-seed unchanged-output checks. Quote component/one-file benchmarks with their scope, never an unmeasured whole-campaign speedup.
6. Event-MVA classes/features/c-tag categories, fivefoldheld-out scoring, class-only weighting and b-hive85/15internal validation. Production state must be updated before presentation.
7. Reproducibility and validation: duplicated validation/inference batch fix, exactly-once tests, same-hardware GPU repeatability, current model/feature/input provenance.
8. negrwv2: motivation, recipe, corrected statistical comparison, production adoption, shape-bias limitation and fit-bin closure status.
9. Systematics overview: detector, modelling, normalization and finite-MC groups; no fabricated ranking before new impacts.
10. Dedicated hDamp explanation/check, once implemented and actual outputs exist.
11. Results: performance/templates/expectedlimits perera andcombinedA/B, populated only from newly produced checked artifacts. Otherwise show explicit current status instead of stale placeholders disguised as results.
12. Remaining physics questions and next checks.

Use detailed systematic pages as main material or backup according to available speaking time. Every systematic must have an explanation somewhere, even when its plot is in backup.

## Required contents on every systematic page

1. **What it is:** physical quantity/effect and what is uncertain, in plain language.
2. **Why it matters here:** acceptance, selected yield, category migration, discriminant shape or statistical precision.
3. **Prescription:** nominal reference and exact Up/Down or alternative-sample construction; distinguish a rate lnN from a template shape, acceptance variation, free rateParam and finite-MC nuisance.
4. **Applicability and correlations:** sample/process, era, A/B differences, sharedvsindependent nuisance names. An absent variation is not evidence of zero effect.
5. **Implementation:** calibration/model/generator source and the actual code/config path/revision. Keep internal filenames in small footnotes/notes rather than replacing the physics explanation.
6. **Evidence:** checks actually run, input/sample size and numerical result; plot showing the relevant response; mark author-run, source-inspected, provisional, pending or not-applicable.
7. **Limit implication:** measured new fit impact only when available. Otherwise say pending; do not reuseJuly impact rankings as current.

## Explanation and evidence checklist by source

| Systematic | Plain-language explanation | Implementation/evidence and useful plot |
|---|---|---|
| Luminosity | Uncertainty in how much collision data was collected; rescales expected simulated yields |2022/2023rates and correlation table. A rate table is clearer than an artificial shape plot. |
| Pileup | Uncertain distribution of extra collisions overlaid on each event |Calibration inputs, nominalvsvaried pileup weights; finalDshape/yield ratios. |
| Muon ID | Data/simulation difference in identifying a real muon |HWWtight-ID SF; SFvspt/eta and event-weight/selected-template response. |
| Muon isolation | Data/simulation difference in whether a real muon appears isolated |Conditional tightiso factor; explain ID×iso chain and show relevant SF/template response. |
| Muon prompt MVA | Efficiency uncertainty of selecting prompt muons with the adopted MVA threshold |PromptMVA SF afterID×iso, producer combination check; threshold efficiency/SF and variation response. |
| Electron ID | Data/simulation difference in Medium electron identification |POGMedium factor; pt/eta response and finaltemplate ratio. |
| Electron prompt MVA | Efficiency uncertainty of the added prompt-electron MVA requirement |Medium×promptMVA×reco chain and producer evidence; do not confuse ONNX numerical agreement with SF measurement. |
| Electron reconstruction below20,20–75,above75 | Probability of reconstructing the electron, measured in distinct momentum ranges |Explain why three sources are used; SF response, pt-boundary checks, finalyield/shape variations. |
| Muon momentum scale | Uncertainty in the absolute muon momentum calibration |Up/Downpt and mll response; selection/category migrations andDtemplates. |
| Muon momentum resolution | Uncertainty in momentum smearing needed to match data |Explain widthvsmean distinction; deterministic RNG check and shiftedselection response. |
| Electron energy scale | Uncertainty in the absolute electron energy calibration |Energy/mll and finaltemplate response; alleralabels. |
| Electron resolution | Uncertainty in extra energy smearing |Show that Up/Down genuinely differ; reference prior fixednominal-keybug accurately. |
| JES | Uncertainty in converting measured jet response into particle-level jet energy |TotalJEScurrently; jets/MET/cjetcategory migration andDresponse. Do not imply regrouped-source decomposition exists. |
| JER | Uncertainty in simulated jet-energy width relative to data |Smearing and propagatedMET response; nominalvsUp/Downshape andyield. |
| Unclustered MET | Uncertainty in the soft/unclustered energy contribution to missing momentum |ShiftedMET/mtl/Dresponse, selectionmigrations. This is now implemented. |
| c-tagging | Data/simulation difference in identifying charm/heavy-flavour categories |2DSFmap/categoryedges/Totalvariation, composition/yieldresponse; explicitlyprovisional pendingLivio, never claim finalcalibrationvalidation. |
| Trigger efficiency | Uncertainty in events passing the online selection |Explain that SFs are disabled byexistingdecision and noactive nuisance exists; do not use a nominal-equal plot to imply measuredzero. |
| ISR | Modelling of radiation from incoming partons |PSweightpair, affectedprocesses, D/yieldresponse; tt exclusionexplicit. |
| FSR | Modelling of radiation from outgoing partons |SeparatePSweightpair andscope; distinguish fromISR/hDamp. |
| muR | Choice of scale at which the strong coupling is evaluated in the hard calculation |ExactLHEindices×2/×0.5 andrunningYukawafix; responseperprocess, A/Bregions. |
| muF | Choice of factorization scale separating PDFs from the hard process |ExactLHEindices andresponse; distinguish frommuR. |
| muR/muF together | Coherent change of both hard-process scale choices |Show currentthree-directionprescription; do not relabel as a new7pointenvelope. |
| PDF shape/acceptance | Uncertain parton momentum/flavour distributions inside the proton |HessianvsMC-replica distinction; generator-rate normalization andselectedacceptance; memberbands/Dresponse and all-channelintegralchecks withcorrectinterpretation. |
| H+c PDF rate | PDF uncertainty of the inclusive signal prediction |Current7.4%sourcedRun3gridpackresult, uncertainty/statistics/source; separate from acceptance/shape. |
| alphaS | Uncertainty in the numerical strong-coupling input, distinct fromscalechoice |CentralH+cnoalphaSpair; dedicatedratevaluestillmissing. Explain missinginputhonestly, no invented3%result. |
| H+b PDF+alphaS | Theory-rate uncertainty of the H+b component |Candidate asymmetricvalue/source, dilutedbyactualH+b share inmergedgroup, overlapwithgenericHiggs5%mustbechecked. |
| top-pT | Modelling mismatch of the top-quark momentum spectrum |Nominalreweighting; Downoff, Upsymmetricfullcorrection; showttpt/Dresponses andnormalization interplay. |
| **hDamp** | POWHEG parameter controlling how hard real radiation is damped/divided relative to shower matching; probes hard-emission/matching modelling |Dedicated nominal/Up/Down tt samples, matcheddecay/gen/tune/era; normalizewiththeir ownfullsumw. Plotnominalandvariationsplusratio,Dandjetmultiplicity, acceptance/yieldchanges andstatisticalprecision. Showcoverageandzero-denominatorpolicy; pendingactualimplementation/results. Do not substitute a flatpercentage or claimISR/FSRalreadycoversit. |
| Higgs+heavyflavour | Uncertain fraction/kinematics of Higgs-background events produced with charm jets |Actual±50%affectedggH/VBFevents; showaffectedfractionandmergedhiggsbkgresponse; scopevsANwordingexplicit. |
| ArmAflavourscheme | Difference between3FS-likeand4FSsignal description |GENcharm-hadronptweights, Up/Downconstruction; spectrumandnormalizedDresponse; notoldflat30%. |
| ArmBstitching | How complementary3FS/4FSregions are combined |GENcjetdefinition/regiondiagram, keptfractions, signednormalizationclosure; PDF/scaleconsistencyandpotentialdoublecountseparate. |
| negrwmethod | Finite-model spread of the negative-weight reweighting prediction |Correctedclosure/shapeplotswithshared-eventcovariance; explainensemblebanddoesnotautomaticallycovermethodbias; actualfit-binclosurepending. |
| Cross-sectionrates | Uncertainty in inclusive background production predictions |st/diboson/V+jets/Higgsratetable, sources, processscope; explain mergedcomponentlimitations. |
| Higgsbranchingratios | Uncertainty in the Higgs probability to decay toWWortautau |1%termsandcorrectdecay-componentapplication; currentmergedgroupscopeproblemexplicituntilfixed. |
| ttfreerate | Fitted normalization constrained by the control region |ExplainrateParamratherthanGaussianprior; CR/SRyieldconstraint, correlation/pullonlywhenfitexists. |
| MCstatistics | Limited number and weight distribution of simulated events in each template bin |autoMCStatsisbin-dependent, not10%; showper-binrelativeuncertainty/Neff/sumw2 andnegative-weightcontribution. |
| Correlations | Whether sources move different eras/processes together |Nuisance-namecorrelationmatrix/table; pre/postwithin2022/2023grouping, theorysharednames, pendingfinegraineddecomposition. |

Only include PUjetID/prefiring/UE/othergenerator variations as explicit not-active/not-applicable/open coverage statements unless actually implemented and justified. hDamp now has an explicit implementation request; UEandtopmassare not automatically added by that request.

## Checks and plot presentation rules

- Show nominal/Up/Downwith lower ratio panels for true shape effects; include yieldratios and template MC statistics so noise is not mistaken for modelling response.
- For object shifts include acceptance/categorymigrations, not onlyweightplots.
- Keep rate-onlysources in a compact table. Foralternativesampleeffects showgenerator/decaymatching and normalizationchecks.
- Use currentcorrectednegrwplots from `negrw_out_img/v2_20261112/corrected_report_20261112/img`, not supersedederrorbars.
- ONNXpromptleptonparity and speedbenchmarks are software checks, distinctfromleptonSF/calibrationchecks. Quote testedleptons/tiecoverage andcomponentbenchmarkscope.
- Preserve signedweightsuntilapprovedfinaltemplatehandling. Reportbinsfloored/emptyshifts; do not hide transformations.
- Final pull/constraint/correlation/impactplots requirethe newfit. No inventedoutputs, oldlimitspresented asnew, orclaimedindependentvalidationfromauthorlogs.

Primary currentinventory: [[Projects/HToWW/combine-systematics/2026-11-12-current-ab-systematics-status]]. Promptleptonreference/benchmarks: [[Projects/HToWW/framework/optimization/2026-10-08-framework-optimization-plan]], [[Projects/HToWW/framework/optimization/2026-11-05-speedup-patches]], [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state]]. Latestproductionstate: [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-direct-continuation-training-launch]].

## Agreed talk structure (Chirayu, 12 Nov evening)

Baseline: the 19 August deck (`analysis-overview.pdf`: 2022postEE, expected UL 1034). Chirayu's wording: "we present this first after presenting what all we did to arrive till here... Then we present updates upon updates after that, particularly in the problems in the signal sample, our ratio method, stitching method and a stat only A vs B limit saying the full systematics limit is processsing .... Also the changes we need to cover regarding the speedup of the framework from legacy - legacy_slim". Also: "for the new limit we will produce, we will have 2 SR with the ncjet split".

1. **What we did to get here (August → October).** One era to four. August priorities: the 4FS/5FS treatment re-derived as a shape; trigger SFs kept off; `higgs_plus_c`, top-pT and MET unclustered activated; datasets added or replaced (jet-binned W+jets, WG, DY replacements). The August card's 7 no-op nuisances were found and fixed in the 1 Oct audit.
2. **The October four-era, full-systematics result (pre-fix reference).** Run 3, 61.9 fb⁻¹, blind Asimov:

   | | full | stat-only | autoMCStats frozen |
   |---|---|---|---|
   | Run 3 | **691** | 338.5 | 616 |
   | 2022 / 2023 | 905 / 1077 | | |
   | 2022preEE / 2022postEE / 2023preBPix / 2023postBPix | 1549 / 1076 / 1348 / 1689 | | |

   - Scaled to 138 fb⁻¹: 463, against the published HIG-24-009 expected 506 (about 9% better).
   - Source: [[Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings]].
   - Plots: `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full/combine_plots`.
   - The breakdown against Run 2 is in [[Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3]].
   - State the pre-fix caveats: JER was a no-op, the WH cross section was 0, the signal scale fix was partial, H+c was at NLO, and the FS treatment was a flat 30% lnN.
3. **Updates since October**
   - **Problems in the central signal samples:** the LHE weights miss the running-Yukawa factor, fixed with a per-event correction; the FxFx merging is misconfigured. A corrected el8 gridpack has been validated and a GEN request package is ready.
   - **The ratio method (Route A):** the 3FS/4FS leading c-hadron pT ratio weights as the flavour-scheme shape systematic.
   - **The stitching method (Route B):** 4FS for N_c = 0 and 3FS for N_c ≥ 1 (LHCHWG-2026-007 §4.4), normalisation closure, and the 3FS re-NANO with PDF weights.
   - **Normalisation and theory:** NNLO H+c, mH = 125.09, H+c PDF 7.4% at 13.6 TeV, H+b +3.36/−3.44%; H+c αS still open.
   - **Leptons and negrw:** Thomas's ttH-MVA WPs, SFs checked against latinos, and negrw v2.
   - **Stat-only A vs B limit:** from the TRAIN outputs and the new 5-fold models, with **one merged SR**, because the current TRAIN outputs do not store `cjet_multiplicity`. Say clearly that the full-systematics limit is processing.
   - **The new full limit will have 2 SRs**, split by c-jet count (Nc-j = 1 / > 1, AN-23-102 lines 337–338).
4. **Framework: from legacy to legacy-slim.**
   - Measured: the legacy tt̄ partition is 2,858 MB against 18.9 MB in TRAIN (about 150×). The factors are 15 shift trees, each repeating all 53 weight columns, plus float64.
   - Legacy-slim keeps a single pass with offline MVA: a nominal tree with the weight variations, plus slim shift trees.
   - Measured job times: median 18 min, p90 50 min; 11% failed (grid sites). The wall time was dominated by failures and retries.
   - Planned: automatic Condor retries and the global redirector.

Production state at 18:22 on 12 Nov: arm A preparation done (`ready.json` 18:18, 6,959,308 rows), and A's 5 GPU folds submitted (DAG 9706908, jobs 9706909–9706913). Arm B was still writing its split, with fold submission armed to follow automatically.

## Signal-sample communication (Chirayu, 12 Nov, for the talk)

Chirayu's message to Thomas (12 Nov, 13:45, his wording): "Not very major issues, the nominal version of the samples are fine... There are 2 issues which I found actually: 1) The scale variations are off by a factor of 2 (I came up with a workaroud for this , however it may not be the best way to deal with it) 2) FxFx merging is applied only upto eta 2.5 in our samples as opposed to the full eta range as done in Run2 and Run3 H to gamma gamma. Should not be a major issue for us since we do apply a eta cut , but this issue still exists in the samples itself. I have reported this to Sebastiano anyways, and he said he can try to reproduce those samples with increased priority... Meanwhile , I am also regenerating the correct gridpacks and compiling all the instructions to give to the conveners for producing these corrected samples. I also asked Gerrit and others for suggestions to deal with this but didn't get a clear understanding on how to proceed, so I was thinking that maybe we could present these issues to the conveners and see what they have to say about this? Along with our way of dealing with the flavour scheme uncertainity (as I wanted to avoid waiting for centrally produced 3FS samples)".

Status for Sebastiano, in Chirayu's words: "I have already sent the corrected H+c and H+b gridpacks (I will have some validation slides). I have also done for 3FS validation (slides should be there)". This supersedes the earlier vault statement that the request package had not been sent.

For the talk:
- In the signal-sample section, add the status: reported to GEN (Sebastiano, higher-priority reproduction), corrected H+c and H+b gridpacks sent, and validation slides for 4FS, H+b and 3FS (reuse `samples-and-production/gridpacks/deck/` and `slides-sebastiano-2026-11/`).
- Close with **questions for the conveners**: (1) how to treat the factor-2 scale variations in the existing samples, given our per-event running-Yukawa workaround; (2) FxFx merging only within |η| < 2.5 (≈1–2% inside our selection); (3) our flavour-scheme approach, ratio method (A) vs stitching (B), without waiting for central 3FS samples.
- Run A TRAIN v2 status at about 19:00: all four eras complete, data included (`jobs_status.py`: 0 missing jobs).
