---
tags: [reference, talk]
status: active
date: 2026-10-16
source: laptop
---

# Talk script: "Constraints on Higgs-charm couplings at CMS" (Higgs 2026)

Script for the deck at commit 97ea1da (15 main slides, 12 backup). Slot is 15+5 min; the time budgets below add up to about 13.5 min, leaving a minute of slack for pauses and the pointer. Speaking pace assumed: about 140 words per minute. Every number in the script is on the slide and was checked against its paper in the reviews ([[2026-10-15-slide-review]], [[2026-10-16-slide-review]]).

Each slide has three parts. **Say** is the spoken text. **Understand** explains the physics or statistics behind the slide in a few sentences, so you can answer follow-ups. **Read** names the paper sections that go deeper; section numbers were taken from the arXiv full texts on 16 Oct. The PRL letters (HIG-21-008, HIG-21-012, HIG-24-018) have no numbered sections, so for those the pointer is to the relevant paragraphs and the Supplemental Material.

A suggested reading order for the whole talk is at the end.

---

## Slide 1: Title (15 s)

**Say.** Good morning. I am Chirayu Gupta from the Vrije Universiteit Brussel, and on behalf of the CMS Collaboration I will review how CMS constrains the coupling of the Higgs boson to charm quarks. The two diagrams already show the two handles we have: the charm Yukawa in the production of a Higgs boson together with a charm quark, on the left, and in the decay of the Higgs boson into a charm–anticharm pair, on the right.

**Understand.** The orange vertex is κc in both diagrams. Keep this picture in mind: the whole talk is "κc in decay" (slides 4 to 7), "κc in production" (slides 8 to 10) and "κc through rates and widths" (slide 11).

---

## Slide 2: Why the Higgs-charm coupling? (60 s)

**Say.** Since the discovery in 2012, ATLAS and CMS have measured the Higgs couplings to the top and bottom quarks and to the tau lepton, and we have evidence for the coupling to muons.(Question: reference for this, just for me to read) All of them agree with the Standard Model, as the plot on the right shows: the couplings scale with the particle mass. The second-generation quarks are the open frontier, and charm is the most accessible of them(Why?). It is still hard: the branching fraction to charm pairs is about 2.9 percent, twenty times below bottom, and charm jets are difficult to separate from bottom and light jets in a large QCD background. We describe the coupling with κc, the charm Yukawa divided by its Standard Model value, so κc equals one in the SM. Flavour-compatible extensions, for example spontaneous flavour violation(Reference? with link and sections), allow |κc| of about three, and our sensitivity is now entering that region. The question behind all of this: does the Higgs mechanism also give the second-generation quarks their mass?

**Understand.** The κ framework rescales each SM coupling by a modifier κ, keeping the SM Lorentz structure; κ = 1 is the SM. The point for charm on the plot is not part of the combined fit: it is the separate ttH+VH result, overlaid. Spontaneous flavour violation (the theory paper on the slide) is a two-Higgs-doublet construction in which the light-quark Yukawas can be enhanced without large flavour-changing neutral currents, which is why |κc| of a few is allowed.

**Read.**
CMS Higgs combination, Rep. Prog. Phys. 89 (2026) 087801, arXiv:2602.18611 (HIG-21-018): Sec. 5.2 "Signal yield parametrization" for how κ enters rates, and Sec. 9 "Interpretation of measurements in the coupling modifier framework" (9.1 resolved loops, 9.2 effective loops); the plot is supplementary Fig. 11.
Spontaneous flavour violation, arXiv:2410.05236 ("How charming can the Higgs be?"): Sec. 2 "Spontaneous Flavor Violating 2HDM" for the model, Sec. 5 "Higgs precision and Yukawa Coupling measurements" for why |κc| of a few survives. Its Table 3 also lists theorists' recasts of LHC data ("CMS |κc| < 2.92"); those are not CMS results, but someone may quote them.
Background on the κ framework: LHC Higgs Cross Section Working Group, CERN Yellow Report 4, arXiv:1610.07922, the chapter on coupling modifiers.

---

## Slide 3: How CMS probes κc (45 s)

**Say.** CMS attacks κc in four ways. Direct searches for H to charm pairs, where the rate goes as κc squared over the total width; here the best result is the ttH plus VH combination, |κc| below 3.5, with 2.7 expected. Associated production of a Higgs boson with a charm quark, where κc enters the production vertex; the combination gives |κc| below 47. Indirect constraints from Higgs rates and the Higgs width, which reach between about three and eight depending on the assumptions. And rare exclusive decays to J/ψ plus a photon, which are sensitive to the sign of κc. Throughout, μ is the signal strength relative to the SM, limits are at 95 percent confidence level, observed with expected in brackets. All κc results so far use Run 2 data; Run 3 has so far delivered better triggers, which I will show at the end.

**Understand.** Why "κc²/ΓH": the branching fraction is B(H→cc) = Γcc/ΓH. Γcc scales as κc², but ΓH also grows with κc because charm is part of the total width: in the paper's model B = κc² B_SM / (1 + (κc² − 1) B_cc + (κb² − 1) B_bb). At large κc the branching fraction saturates, which is why decay-based limits flatten out. This is also why production (slide 8) is a genuinely different handle.

**Read.**
ttH+VH combination, PRL 136 (2026) 011801, arXiv:2509.22535: Eq. (3) and the paragraph around it give the branching-fraction model with the width.

---

## Slide 4: Direct H→cc: VH(H→cc) (75 s)

**Say.** The most sensitive single channel of Run 2 is VH, where the W or Z decays to zero, one or two leptons. There are two topologies: resolved, with two separate charm jets, and merged, where the Higgs is boosted and both charm quarks end up in one large-radius jet, identified with ParticleNet, a graph neural network tagger. The method is validated on the same final state with a Z boson instead of a Higgs: VZ with Z to charm is observed at 5.7 standard deviations, and you see its peak near 90 GeV in the middle plot. For the Higgs we set μ below 14, with 7.6 expected; on the right are the limits per channel. In κc this gives 1.1 < |κc| < 5.5. The lower edge looks odd, because it excludes κc of one: that comes from an upward fluctuation, the best fit μ is 7.7, and it is mostly in the merged-jet category, as the backup shows.

**Understand.** The κc interval comes from a profile-likelihood scan, −2ΔlnL versus κc, with the 95% CL boundary at 3.84. When the data fluctuate up, the minimum of the scan moves away from κc = 1 and the SM can fall outside the 95% interval; this is what "observed excludes κc = 1" means, not evidence against the SM. The excess is about 1.9σ above μ = 1 if you estimate it from the quoted uncertainty; the paper calls it "a small upward statistical fluctuation". Merged-jet μ̂ = 8.7 (+4.6 −4.0), resolved μ̂ = −9.5 ± 9.6.

**Read.**
VH(H→cc), PRL 131 (2023) 061801, arXiv:2205.05550 (HIG-21-008): read the whole letter, it is short; the key parts are the description of the resolved and merged-jet selections, the ParticleNet tagger and its calibration, the VZ(Z→cc) validation, and the κc interpretation (Eq. 1). The public results page has the supplementary κc scan and the per-category best fits (Additional Tables 5 and 6).
ParticleNet: H. Qu and L. Gouskos, Phys. Rev. D 101 (2020) 056019, arXiv:1902.08570, for how a graph network on jet constituents works.

---

## Slide 5: Direct H→cc: boosted H (40 s)

**Say.** At very high Higgs transverse momentum, above 450 GeV, the search is dominated by gluon fusion. The Higgs boson is again a single large-radius jet, identified with a double-charm tagger, DeepDoubleX, and the signal is extracted from a fit to the jet mass. The big peak you see in the passing region is not the Higgs: it is the Z boson decaying to charm, observed here for the first time in Z plus jets at high pT, with a signal strength of one. For the Higgs the limit is μ below 47, with 39 expected. The paper gives no κc interpretation, so this is an independent high-pT handle rather than a κc number.

**Understand.** The Z→cc peak is the standard candle: it calibrates the double-charm tagger and the jet-mass scale in situ. Note the difference from slide 4: "VZ(Z→cc) observed at 5.7σ" is VZ production; this one is Z+jets. Both are 2023 papers.

**Read.**
Boosted H→cc, PRL 131 (2023) 041801, arXiv:2211.14181 (HIG-21-012): the paragraphs on the DeepDoubleX tagger and its calibration, the passing/failing region fit, and the Z+jets result μZ = 1.00 (+0.17 −0.14 syst ± 0.08 theo ± 0.06 stat).

---

## Slide 6: ttH(H→cc): a new channel (75 s)

**Say.** The newest direct channel is the Higgs produced with a top-quark pair. The top pair decays to zero, one or two leptons, and the events contain many jets of all flavours, so every jet is placed in two-dimensional tagging categories from ParticleNet, separating b, c and light jets, and a transformer event classifier, ParT, separates ttH to charm, ttH to bottom, ttZ and top-pair plus heavy flavour. ttH to charm, ttH to bottom and ttZ are fitted simultaneously, with the top-pair plus charm and plus bottom backgrounds constrained in control regions. As a check, ttZ with Z to charm is measured at μ = 1.0 ± 0.8. The result is μ below 7.8, with 8.7 expected, and |κc| below 3.0, with 3.3 expected, for κb fixed to one; if κb is fitted from ttH to bottom, |κc| is below 4.2. So this is a second direct channel with expected sensitivity comparable to VH.

**Understand.** The simultaneous fit is what makes ttH special: the same events constrain bottom and charm, so you can fit κb and κc together (backup p20). The 2D tagging plane has two axes, b+c versus light and b versus c (backup p19). The dominant systematics are tt+c and tt+light modelling (about 32% and 29% of the total), but statistics still dominate (74%).

**Read.**
ttH(H→cc), PRL 136 (2026) 011801, arXiv:2509.22535 (HIG-24-018): the main-text paragraphs on event categories and the ParT classifier, and the Supplemental Material sections "Simulated samples", "Baseline event selection", "Neural network event classifier", "Systematic uncertainties" (experimental and modelling), and "Validation of the background model".
Particle Transformer: H. Qu, C. Li, S. Qian, "Particle Transformer for jet tagging", arXiv:2202.03772.

---

## Slide 7: Combination of ttH and VH (60 s)

**Say.** Combining ttH and VH, the H to charm signal strength is below 9.3, with 5.6 expected, assuming SM production. The expected limit is 26 percent better than VH alone and 36 percent better than ttH alone. In κc, with κb equal to one, we get |κc| below 3.5, with 2.7 expected. Notice on the scan in the middle that ttH alone, at 3.0, is tighter than the combination on observed: that is the VH upward fluctuation pulling the combined minimum away from one. So the honest statement is: the expected reach, 2.7, is now below the BSM-motivated value of about three; it is the best expected direct sensitivity to date.

**Understand.** The combination correlates the common experimental uncertainties except jet flavour tagging, which uses different algorithms in the two analyses; theory uncertainties in Higgs production and decay for the same processes are correlated. It assumes SM production cross sections for ttH and VH, and only the branching fraction changes with κc through Eq. (3). The middle plot shows −2ΔlnL versus |κc| for ttH, VH and the combination, solid observed and dashed expected; the combined observed minimum sits near |κc| ≈ 2.2, again because of VH.

**Read.**
arXiv:2509.22535: the combination paragraph ("The expected 95% CL upper limit on μ(H→cc), assuming SM production rates for ttH and VH, is 5.6, representing a 36% (26%) improvement...") and Supplemental Material "Additional results" (Figs. B12, B13).
Statistics background: the Combine documentation (cms-analysis.github.io/HiggsAnalysis-CombinedLimit), the pages on CLs upper limits and on likelihood scans, to be able to explain why μ limits (CLs) and κc intervals (profile likelihood) are different constructions.

---

## Slide 8: H + charm production (60 s)

**Say.** The second handle puts κc in the production vertex: a charm quark and a gluon produce a Higgs boson and a charm quark, independent of the H to charm decay. That means we can use clean Higgs decays, photons or W pairs, and require a charm-tagged jet. The price is a tiny rate: the cH cross section is about 90 femtobarn, so about 0.2 femtobarn in the diphoton channel and 20 in WW. There are three challenges: Higgs plus charm also comes from gluon splitting in gluon fusion, which does not depend on κc and has the same final state; the charm jets are soft and often forward; and the modelling depends on the flavour scheme, which Tiziano Bevilacqua will discuss in the next talk. To turn a cH limit into κc we use the "flat direction": κc is varied while all other Higgs rates are kept at their SM values, so only cH production changes.

**Understand.** The flat direction (Coyle, Wagner, Wei) rescales all other Higgs couplings by a common κH(κc), chosen so that the signal strengths of every other Higgs process stay exactly one as κc grows; this cancels the width growth for the other channels. The CMS papers give the explicit κH(κc, B_cc^SM) formula (2503.08797 Eq. 1). Without it, large κc would inflate ΓH and suppress every other Higgs rate, which data forbid. The H+c idea itself is from Brivio, Goertz, Isidori.

**Read.**
cH(H→γγ), JHEP 11 (2025) 060, arXiv:2503.08797 (HIG-23-010): Sec. 1 "Introduction" for the physics case and the κc-independent backgrounds, Sec. 9 "Results" for the flat-direction formula (Eq. 1).
Theory: I. Brivio, F. Goertz, G. Isidori, PRL 115 (2015) 211801, arXiv:1507.02916 (H+charm as a κc probe); N. M. Coyle, C. E. M. Wagner, V. Wei, PRD 100 (2019) 073013, arXiv:1905.09360 (the flat direction).

---

## Slide 9: cH(H→γγ) (45 s)

**Say.** The first cH search used the diphoton channel with the full Run 2 dataset. Two boosted decision trees, trained without charm-tagging inputs, separate cH from gluon fusion, the largest resonant background, and from the continuum diphoton background; this gives nine categories per year, and the signal comes from fits to the diphoton mass. In the plot, the peak at 125 GeV is fully explained by the other Higgs processes, mostly gluon fusion; nothing is left for cH, and the best fit is negative, about minus 230. The limit is μ below 243, with 355 expected, and |κc| below 38, with 73 expected. So we are at about 40, not 3: the rate is tiny, and gluon fusion with a charm jet mimics the signal.

**Understand.** Observed (38) is much better than expected (73) because μ̂ is negative. The bottom panel of the plot ("all background subtracted") is where you see that no cH signal remains. The BDTs leave out charm-tagging information on purpose: then the ratio of ggH + c jet to ggH + light jet does not vary with the BDT output, and the heavy-flavour modelling uncertainty can be applied to the overall ggH normalisation (2503.08797 Sec. 6).

**Read.**
arXiv:2503.08797: Sec. 5 "Event selection", Sec. 6 "Event categorization" (the two BDTs), Sec. 7 "Signal and background modeling", Sec. 8 "Systematic uncertainties", Sec. 9 "Results" (Fig. 6).

---

## Slide 10: cH(H→WW) and the γγ + WW combination (60 s)

**Say.** The WW channel uses an electron, a muon, missing energy and a charm jet, with signal regions of one or more charm jets and two BDTs against non-Higgs and other Higgs backgrounds. The κc-independent Higgs plus charm background is fixed to the SM, so the cH signal strength is the only parameter of interest; floating it as well is in backup. WW alone gives μ below 1065 and |κc| below 211. Combined with the diphoton channel we get μ below 257 and |κc| below 47, with 51 expected. The combined observed limit is weaker than diphoton alone, 38, because WW fluctuated up: the best fit is plus 390 in WW versus minus 230 in diphotons. This is κc from production alone, statistics-limited, and independent of the decay to charm.

**Understand.** 1 POI versus 2 POI: in the 2-POI fit the κc-independent H+c background floats too, it anticorrelates with cH (−87%), and the limit weakens to 1804; the combination uses the 1-POI fit. The μ-to-κc mapping in the flat direction is strongly nonlinear (243 → 38, 257 → 47, 1065 → 211), so κc is not simply √μ.

**Read.**
cH(H→WW), JHEP 08 (2026) 051, arXiv:2508.14988 (HIG-24-009): Sec. 4 "Event reconstruction and selection", Sec. 5 "Analysis strategy" (signal and control regions, the two BDTs), Sec. 7 "Results" (1-POI vs 2-POI fits, the flat-direction translation, and the γγ+WW combination).

---

## Slide 11: Indirect constraints on κc (75 s)

**Say.** κc can also be constrained without tagging a single charm jet. A large κc adds charm-initiated Higgs production and increases the total width, and on-shell four-lepton rates are sensitive to both. κV here are the modifiers of the Higgs couplings to Z and W bosons. With |κZ = κW| below one, the on-shell analysis gives κc between −3.7 and 3.2. The new result adds off-shell four-lepton production, which breaks the degeneracy between κV and the width: with |κV| below one, κc is between −3.3 and 2.8; with κZ and κW completely free it is between −8.6 and 7.5. The width measurement itself was in Filippo Errico's talk on Tuesday. Finally, the exclusive decay to J/ψ plus photon gives −166 to 208, which Jas Bierkens covers on Thursday. With |κV| below one, the four-lepton result matches the direct searches, under different assumptions.

**Understand.** The on-shell rate goes as κV²κf²/ΓH, so a larger width (from large κc) can be hidden by a larger κV; that is the degeneracy. Off-shell production does not depend on ΓH, so it fixes κV and breaks it. Careful with the plot: the curves are labelled as in the paper's Fig. 8 (|κZ = κW| ≤ 1 versus κZ ≠ κW), while the intervals quoted in the text are from its Table 3, which is "obtained without imposing custodial symmetry". The small asymmetry of the intervals is not a sign measurement: it comes from charm-loop interference in ggH and H→gg, and the constraint is essentially on κc². For J/ψγ the direct amplitude (∝ κc) interferes with the indirect H→γγ*→γJ/ψ amplitude (∝ κγ), which is where the sign sensitivity comes from.

**Read.**
γH + on-shell H→4ℓ, PRD 112 (2025) 112001, arXiv:2502.05665 (HIG-23-011): Sec. 8 "Analysis of the light-quark Yukawa couplings" and 8.2 "Results for light-quark Yukawa couplings" (Table 3 has the scenarios); Sec. 7 for the γH part.
Off-shell + on-shell H→4ℓ, arXiv:2607.23352 (HIG-25-003): Sec. 1 "Introduction" (why custodial symmetry and |κZ| ≤ 1 were dropped), Sec. 6 "Implementation of fitting and associated uncertainties", Sec. 9 "Constraints on Higgs boson Yukawa couplings to light quarks" (Fig. 8, Table 3), Sec. 12 "Measurement of the Higgs boson width from the combination".
H→J/ψγ, PLB 865 (2025) 139462, arXiv:2411.15000 (SMP-22-012): "Introduction" for the interfering amplitudes, and the κc/κγ interpretation in the results (observed (−157, 199) for κc/κγ; (−166, 208), expected (−128, 169), for κγ = 1).
Higgs pT spectrum (backup p23), JHEP 04 (2026) 093, arXiv:2504.13081 (HIG-23-013): Sec. 7, the κ-framework interpretation (it uses γγ, ZZ and resolved ττ; WW and boosted ττ are excluded). Theory idea: F. Bishara, U. Haisch, P. F. Monni, E. Re, PRL 118 (2017) 121801, arXiv:1606.09253.

---

## Slide 12: Where we stand (50 s)

**Say.** This table collects all CMS constraints on κc, with the assumptions behind each. The direct searches assume κb equal to one, SM production and no BSM decays; the combination gives 3.5, ttH alone 3.0, VH alone the interval from 1.1 to 5.5. The four-lepton results allow BSM width and profile the other light-quark couplings; with |κV| below one the new on- plus off-shell result gives −3.3 to 2.8, and without any assumption on κZ and κW about ±8. cH uses the flat direction and gives 47; J/ψγ gives −166 to 208. The rows use different coupling models, so they are not directly comparable. The message: direct searches and the four-lepton result both reach |κc| of about three, where flavour-compatible BSM scenarios live.

**Understand.** The indirect rows are the more general ones (they allow ΓBSM ≥ 0 and float other light Yukawas); the direct rows are stronger under stronger assumptions. This slide is the reference table for the day: the afternoon plenaries (Cabrera Urban on H+c, D'Eramo on H→cc, Tarek on off-shell) will quote these numbers.

**Read.** Nothing new; the assumptions column is drawn from 2509.22535 Eq. (3), 2607.23352 Table 3, 2502.05665 Sec. 8, 2508.14988 Sec. 7 and 2411.15000.

---

## Slide 13: Toward Run 3 (45 s)

**Say.** All the κc results I showed use Run 2 data. What Run 3 has delivered so far are better tools. On the left: machine-learning b and c tagging now runs in the high-level trigger, and in simulation the trigger efficiency for ttH to charm rises strongly from 2018 to the 2022 to 2024 triggers; the HLT taggers were in Jessy Daniel's talk on Monday. On the right: the main background to ttH to charm, top pairs with additional charm quarks, has now been measured with Run 2 data, 680 femtobarn. So Run 3 searches start with higher trigger efficiency and a measured tt+cc background.

**Understand.** Part of the trigger gain is rate budget, not only the tagger: the 2018 trigger ran at 10 Hz, the Run 3 ones at 60, 115 and 170 Hz in 2022, 2023 and 2024. The tt+cc cross section is 680 ± 40 (stat) +130 −100 (syst) fb at parton level (PAS Table 8).

**Read.**
HLT flavour tagging, arXiv:2608.18331 (BTV-25-002): Sec. 5 "Jet flavour identification in the HLT" (5.1 small-radius jets, 5.2 large-radius jets), Sec. 7 "New heavy-flavour jet triggers in Run 3", Sec. 8 "Impact on the CMS physics programme".
tt+b/c cross sections, CMS-PAS-TOP-26-003: the results section and Table 8 (parton-level cross sections), Fig. 9.

---

## Slide 14: Prospects at the HL-LHC (50 s)

**Say.** Looking further ahead, the ATLAS and CMS input to the European Strategy update, with 3 inverse attobarn per experiment at 14 TeV, expects about 1.6 standard deviations for VH to charm and |κc| below 1.5 at 95 percent confidence level. That is 30 percent better than the 2019 Yellow Report projection, thanks to improved charm tagging; it is extrapolated from an ATLAS VH study and assumed for both experiments. The bar chart puts it in context: Run 2 observed 3.5, expected 2.7, HL-LHC expected 1.5, with the SM at one. Every bar still includes κc equal to zero. Further gains will come from Run 3 data, machine-learning tagging and the detector upgrades, and theory modelling and tagger calibration will become limiting. κc of order one is where we first become sensitive to whether the Higgs gives charm its mass.

**Understand.** An upper bound |κc| < 1.5 does not exclude κc = 0; establishing a nonzero charm Yukawa needs more than the HL-LHC projection shows. The 1.5 is an expected sensitivity, not a measurement. The paper does not name the S2/S3 systematics scenario for charm, so do not quote one.

**Read.**
HL-LHC projections, arXiv:2504.00672 (ATL-PHYS-PUB-2025-018, CMS-HIG-25-002): Sec. 2 "Precision Higgs boson physics and rare decays", the charm paragraph ("a 1.6σ significance ... κc can be constrained to |κc| < 1.5 at 95% CL, improving the previous projection from direct searches by 30% [3]"); ref. [11] there is the ATLAS VH study (ATL-PHYS-PUB-2025-012).
2019 Yellow Report: M. Cepeda et al., CERN Yellow Rep. Monogr. 7 (2019) 221, arXiv:1902.00134, the charm-Yukawa section.

---

## Slide 15: Summary (40 s)

**Say.** To summarise. The charm Yukawa is the most accessible second-generation quark coupling, and CMS probes it in decay, in production and indirectly. The ttH plus VH combination gives |κc| below 3.5, with 2.7 expected: the most stringent direct constraint and the best expected sensitivity. Higgs plus charm production gives 47, independent of the decay. The on- plus off-shell four-lepton analysis gives −3.3 to 2.8 with |κV| below one, about eight without. All of this is Run 2; Run 3 starts with better triggers and a measured top-pair plus charm background. So, does the Higgs give charm its mass? Today we are at |κc| of three to three and a half, entering BSM-motivated territory; the HL-LHC is expected to reach 1.5, approaching but not yet reaching sensitivity to κc equal to zero. Thank you.

---

## Backup slides: what to say if asked

**p17 VH categories.** The excess sits in the merged-jet category (μ̂ = 8.7), the resolved category is low (−9.5 ± 9.6). μ limits are CLs, κc intervals are profile-likelihood scans.

**p18 ttH yields.** The ttH(cc) best fit is −1.6 ± 4.5: compatible with zero and with the SM (about 0.6σ from one).

**p19 ttH flavour tagging.** Each jet gets ParticleNet scores; the plane (b+c vs light, b vs c) is cut into categories; ttZ(cc) is the standard candle; ttH(bb) is measured on the side at 4.4σ.

**p20 (κb, κc) plane.** Orange observed, blue expected; the simultaneous fit constrains both Yukawas, which gives the "κb fitted" number on slide 6.

**p21 cH(WW) post-fit.** μ̂ = 390 (+380 −270), within 1.5σ of the SM; statistics-limited, then flavour-scheme and ggH heavy-flavour modelling.

**p22 floating H+c background.** 2 POI: the κc-independent H+c floats too, anticorrelated at −87%, limit 1804; the combination uses 1 POI.

**p23 Higgs pT spectrum.** 2D (κb, κc) contours only, no 1D κc interval; inputs are γγ, ZZ and resolved ττ.

**p24 J/ψγ.** Interference of direct and indirect amplitudes gives sign sensitivity; 95% CL κc ∈ (−166, 208), expected (−128, 169); 123 fb⁻¹.

**p25 HLT tagging.** Light (solid) and b (dashed) misidentification versus c efficiency; VBF H→cc trigger efficiency vs offline ParticleNet score.

**p26 likely questions.** The VH excess, what limits the direct searches, ATLAS, why cH is weaker, the negative γγ best fit, boosted without κc, trigger gain vs rate budget, sign sensitivity of 4ℓ.

**ATLAS, if asked.** VBF+VH(cc), arXiv:2511.21911: |κc| < 4.7 (3.9 expected), same assumptions as CMS (other couplings SM, no BSM decays), so 4.7 (3.9) vs 3.5 (2.7) is like-for-like; its VBF part includes 51.5 fb⁻¹ of Run 3 data at 13.6 TeV, and ATLAS VH alone gives |κc| < 4.2 (4.1). Read its introduction and the κc interpretation section.

---

## Concepts to have straight

**Signal strength μ.** Observed rate divided by the SM prediction, σB/(σB)_SM. μ < 14 means the data allow at most 14 times the SM rate at 95% CL.

**CLs versus profile likelihood.** The μ upper limits use the CLs method (asymptotic formulae). The κc intervals are profile-likelihood scans: the 95% CL interval is where −2ΔlnL < 3.84, with all nuisance parameters profiled. The cH κc bounds are translated from the CLs μ limit through the flat direction. They are different constructions, which is one reason the table rows are not directly comparable.

**Width dependence.** In decay, B(H→cc) = Γcc/ΓH and ΓH contains Γcc, so B saturates at large κc. In production (cH) under the flat direction, the other rates are held at SM values by construction.

**Custodial symmetry.** κZ = κW. The older on-shell analysis assumed it together with |κZ| ≤ 1; the new on+off-shell paper drops it (Table 3), which is why "|κV| ≤ 1" and "|κZ = κW| ≤ 1" are not the same condition.

**Flavour schemes.** H+c can be simulated with massive charm (3FS/4FS, charm produced in the hard process) or massless charm with a charm PDF (4FS/5FS); the predictions differ, which is a modelling systematic for cH. Bevilacqua's talk right after yours is about exactly this.

---

## Suggested reading order

Read the PRL letters first, because they are short and carry the headline numbers: arXiv:2205.05550 (VH), arXiv:2509.22535 with its Supplemental Material (ttH and the combination), then arXiv:2211.14181 (boosted). Next the production papers, arXiv:2503.08797 Sec. 1, 6 and 9, then arXiv:2508.14988 Sec. 5 and 7, plus the two theory papers on H+c and the flat direction (1507.02916, 1905.09360). Then the indirect papers, arXiv:2607.23352 Sec. 1 and 9 and arXiv:2502.05665 Sec. 8, and the J/ψγ introduction (2411.15000). Finish with the outlook: arXiv:2608.18331 Sec. 7 and 8, PAS TOP-26-003 Table 8, arXiv:2504.00672 Sec. 2 (charm paragraph). For context, the κ framework in arXiv:2602.18611 Sec. 9 and Yellow Report 4. If you have time for one theory paper, take arXiv:2410.05236 Sec. 5.
