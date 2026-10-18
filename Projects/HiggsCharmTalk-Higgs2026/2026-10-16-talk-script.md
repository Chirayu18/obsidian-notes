---
tags: [reference, talk]
status: active
date: 2026-10-16
source: laptop
---

# Talk script: "Constraints on Higgs-charm couplings at CMS" (Higgs 2026)

Script for the HTML deck, `html/deck.html` → `html/higgs2026_higgs_charm.pdf` (19 main slides, 15 backup; tt̄H is three slides (8 selection, 9 regions, 10 results); VH is split into strategy (5) and results (6), the c-tagging slide 3 is new, Run 3 prospects share slide 18 with the HL-LHC). Slot is 15+5 min; the time budgets below add up to about 14 min, leaving a minute of slack for pauses and the pointer. Speaking pace assumed: about 140 words per minute. Every number in the script is on the slide and was checked against its paper in the reviews ([[2026-10-15-slide-review]], [[2026-10-16-slide-review]]).

Each slide has three parts. **Say** is the spoken text. **Understand** explains the physics or statistics behind the slide in a few sentences, so you can answer follow-ups. **Read** names the paper sections that go deeper; section numbers were taken from the arXiv full texts on 16 Oct. The PRL letters (HIG-21-008, HIG-21-012, HIG-24-018) have no numbered sections, so for those the pointer is to the relevant paragraphs and the Supplemental Material.

A suggested reading order for the whole talk is at the end.

---

## Slide 1: Title (15 s)

**Say.** Good morning. I am Chirayu Gupta from the Vrije Universiteit Brussel, and on behalf of the CMS Collaboration I will review how CMS constrains the coupling of the Higgs boson to charm quarks. The two diagrams already show the two handles we have: the charm Yukawa in the production of a Higgs boson together with a charm quark, on the left, and in the decay of the Higgs boson into a charm–anticharm pair, on the right.

**Understand.** The orange vertex is κc in both diagrams. Keep this picture in mind: the whole talk is "κc in decay" (slides 5 to 11), "κc in production" (slides 12 to 14) and "κc through rates and widths" (slide 15).

---

## Slide 2: Why the Higgs-charm coupling? (60 s)

**Say.** Since the discovery in 2012, ATLAS and CMS have measured the Higgs couplings to the top and bottom quarks and to the tau lepton, and we have evidence for the coupling to muons. All of them agree with the Standard Model, as the plot on the right shows: the couplings scale with the particle mass. The second-generation quarks are the open frontier, and charm is the most accessible of them. It is still hard: the branching fraction to charm pairs is about 2.9 percent, twenty times below bottom, and charm jets are difficult to separate from bottom and light jets in a large QCD background. We describe the coupling with κc, the charm Yukawa divided by its Standard Model value, so κc equals one in the SM. Flavour-compatible extensions, for example spontaneous flavour violation, allow |κc| of about three, and our sensitivity is now entering that region. The question behind all of this: does the Higgs mechanism also give the second-generation quarks their mass? 

**Understand.** The κ framework rescales each SM coupling by a modifier κ, keeping the SM Lorentz structure; κ = 1 is the SM. The point for charm on the plot is not part of the combined fit: it is the separate ttH+VH result, overlaid. Spontaneous flavour violation (the theory paper on the slide) is a two-Higgs-doublet construction in which the light-quark Yukawas can be enhanced without large flavour-changing neutral currents, which is why |κc| of a few is allowed. The paper's concrete example is at the end of Sec. 3.3: "|λc| ∼ 0.2 is allowed and corresponds to an enhancement of Y_hcc about 3.7 times the SM value of y_c for cos(β − α) = 0.1" (middle panel of its Fig. 4). So "about three" on the slide is the conservative round number; 3.7 is the paper's example point.

Why charm is the most accessible second-generation quark: the Yukawa coupling is proportional to the mass, and charm is by far the heaviest of the second-generation quarks (running masses at the Higgs scale roughly 0.6 GeV for charm against 0.05 GeV for strange), so the H→cc rate is about a hundred times the H→ss rate. Charm jets can also be tagged, because charm hadrons fly a measurable distance before decaying and leave displaced tracks and vertices; a strange jet has no comparable signature. The muon is second generation too, but it is a lepton; it is the one second-generation coupling already seen (next point).

The muon evidence: CMS, JHEP 01 (2021) 148, arXiv:2009.04363 (HIG-19-006); now cited on the slide and covered on the new backup slide (see below).

**Read.**
H→μμ evidence, arXiv:2009.04363: the abstract (3.0σ, 2.5σ expected; μ = 1.19 +0.40 −0.39 stat +0.15 −0.14 syst) and Sec. 10, the κ-framework interpretation (κμ = 1.07, 0.59 < κμ < 1.50 at 95% CL).
CMS Higgs combination, Rep. Prog. Phys. 89 (2026) 087801, arXiv:2602.18611 (HIG-21-018): Sec. 5.2 "Signal yield parametrization" for how κ enters rates, and Sec. 9 "Interpretation of measurements in the coupling modifier framework" (9.1 resolved loops, 9.2 effective loops); the plot is supplementary Fig. 11.
Spontaneous flavour violation, arXiv:2410.05236 ("How charming can the Higgs be?"): Sec. 2 "Spontaneous Flavor Violating 2HDM" for the model, Sec. 5 "Higgs precision and Yukawa Coupling measurements" for why |κc| of a few survives. Its Table 3 also lists theorists' recasts of LHC data ("CMS |κc| < 2.92"); those are not CMS results, but someone may quote them.
Background on the κ framework: LHC Higgs Cross Section Working Group, CERN Yellow Report 4, arXiv:1610.07922, the chapter on coupling modifiers.

---

## Slide 3: Charm tagging (40 s)

**Say.** Everything that follows depends on finding charm jets. A charm hadron sits between light and b hadrons in mass and lifetime: it decays at a secondary vertex like a b, but closer to the primary vertex, so c jets are easily confused with light jets on one side and b jets on the other. CMS taggers went from likelihoods built on track impact parameters and secondary vertices, to deep networks on all jet constituents like DeepJet, to particle-cloud networks: ParticleNet, a graph network, and UParT, a transformer. The plot is Run 3 simulation: at the same charm efficiency, UParT v2 has the lowest misidentification rate for both b and light jets. In this talk: DeepJet in VH resolved and the cH searches, ParticleNet in VH merged and ttH, DeepDoubleX in the boosted search.

**Understand (architectures, as on the slide).** JP combines the impact-parameter probabilities of the tracks into a jet likelihood; CSV combines secondary-vertex and track variables with a likelihood ratio, and CSVv2 feeds them to a one-hidden-layer MLP; the Run 2 c tagger trains two gradient-boosted BDTs, CvsL and CvsB (all from CMS, JINST 13 (2018) P05011, arXiv:1712.07158). DeepCSV is a fully connected DNN with four hidden layers of 100 nodes and b/c/light outputs (same paper). DeepJet runs 1×1 convolutions on each charged, neutral and secondary-vertex candidate, then LSTMs over each list, then dense layers (JINST 15 (2020) P12012). ParticleNet treats the jet as an unordered "particle cloud" and uses a dynamic graph CNN (EdgeConv), so it respects permutation symmetry (PRD 101 (2020) 056019; DP-2025-081 glossary). ParT and UParT are transformers whose attention is augmented by pairwise interaction features between constituents and secondary vertices; UParT adds adversarial training for robustness against simulation mismodelling and is multi-task (b, c, s, τ and jet-energy regression) (arXiv:2202.03772; CMS-DP-2025-081). A one-line spoken version: "trees and likelihoods in Run 1, dense and recurrent networks in Run 2, graph networks and transformers on the raw particle list in Run 3."

**Understand.** The ROC plot (CMS-DP-2025-081, tt̄ simulation at 13.6 TeV, jets with pT > 30 GeV, |η| < 2.5) shows misidentification efficiency versus c-tag efficiency: solid lines are c vs b, dashed are c vs light (udsg); lower is better. It compares taggers on the same simulation, so it says nothing about data-to-simulation scale factors. The Run 2 analyses in this talk used DeepJet and ParticleNet, not UParT; UParT is the Run 3 tagger. The tagger-to-analysis mapping was checked in each paper: DeepJet in HIG-23-010 and HIG-24-009 (CvsL > 0.12, CvsB > 0.5 in WW) and in VH resolved; ParticleNet in VH merged and in ttH (AK4 ParticleNet categories); DeepDoubleX in HIG-21-012. The ICNFP talk used a bar chart from CMS-DP-2024-066; its public page is still a placeholder, so this deck uses the DP-2025-081 ROC curve. The DP-2025-081 bar chart (sl27) is for b tagging at ε_b = 70% and does not belong on a c-tagging slide.

**Read.**
CMS-DP-2025-081 (BTV public pages, Run 3 DP notes): the c-tagging ROC curves (sl14) and the tagger descriptions.
DeepJet: E. Bols et al., JINST 15 (2020) P12012, arXiv:2008.10519. ParticleNet: H. Qu and L. Gouskos, PRD 101 (2020) 056019, arXiv:1902.08570. Particle Transformer: H. Qu, C. Li, S. Qian, ICML 2022, arXiv:2202.03772.

---

## Slide 4: How CMS probes κc (45 s)

**Say.** CMS attacks κc in four ways. Direct searches for H to charm pairs, where the rate goes as κc squared over the total width; here the best result is the ttH plus VH combination, |κc| below 3.5, with 2.7 expected. Associated production(what is the rate proportional to here and how does it work?) of a Higgs boson with a charm quark, where κc enters the production vertex; the combination gives |κc| below 47. Indirect constraints from Higgs rates and the Higgs width, which reach between about three and eight depending on the assumptions. And rare exclusive decays to J/ψ plus a photon, which are sensitive to the sign of κc. Throughout, μ is the signal strength relative to the SM, limits are at 95 percent confidence level, observed with expected in brackets. All κc results so far use Run 2 data; Run 3 has so far delivered better triggers, which I will show at the end.

**Understand.** Why "κc²/ΓH": the branching fraction is B(H→cc) = Γcc/ΓH. Γcc scales as κc², but ΓH also grows with κc because charm is part of the total width: in the paper's model B = κc² B_SM / (1 + (κc² − 1) B_cc + (κb² − 1) B_bb). At large κc the branching fraction saturates, which is why decay-based limits flatten out. This is also why production (slide 12) is a genuinely different handle.

**Read.**
ttH+VH combination, PRL 136 (2026) 011801, arXiv:2509.22535: Eq. (3) and the paragraph around it give the branching-fraction model with the width.

---

## Slides 5–6: VH(H→cc): strategy, then results (75 s)

**Say.** The most sensitive single channel of Run 2 is VH, with the W or Z decaying to zero, one or two leptons; the main backgrounds, V plus jets and top pairs, are normalised in control regions. The analysis has two topologies, split at a Higgs-candidate pT of 300 GeV. In the resolved topology, which holds more than 95 percent of the signal, the two charm jets are reconstructed separately and tagged with DeepJet, and the fit is to a BDT. In the merged topology the Higgs is boosted into one large-radius jet. It is less than 5 percent of the signal, but the background is much lower there, and ParticleNet does both the charm-pair tagging, in three purity categories, and a regression of the jet mass; the fit is to that mass. The middle plot is the merged analysis only: in the bottom panel, after subtracting everything else, you see the VZ peak in grey near 90 GeV and the fitted VH in red. That VZ signal is the validation: Z to charm in VZ is observed at 5.7 standard deviations. For the Higgs we set μ below 14, with 7.6 expected, and |κc| between 1.1 and 5.5. The result is statistics-limited.

**Slide 6, how to read it.** Left: 95% CL limits on μ per category; the black dot is observed, the dashed line the median expected, green and yellow the 68% and 95% expected bands, and the red line μ = 1 (SM). The merged-jet category is the most sensitive (expected 8.75 vs 19.0 resolved), and the combination gives observed 14.4, expected 7.60. Right: q = −2Δln L as a function of |κc|; the 95% CL interval is where the curve lies below 3.84. The observed curve crosses at 1.1 and 5.5, the SM-expected curve at 3.4 (values read off the plot and matching the paper). Spoken: "the merged-jet category carries most of the sensitivity; the observed curve sits low near |κc| of 3, so the 95% interval is 1.1 to 5.5, against 3.4 expected."

**Understand.** Statistics-limited is from the paper's Table 1: the statistical uncertainty is 85% of the total; the largest systematics are the size of the simulated samples (37%, driven by negative weights in the NLO V+jets samples) and the c-tagging efficiencies (23%), with theory at 22%. The merged topology pays off because signal large-R jets have higher pT than the V+jets and tt̄ ones, so the background contamination is much lower (the paper's reason). ParticleNet improves the rejection of other jet flavours by a factor 4 to 7 over the previous DeepAK15 tagger, and its mass regression improves the large-R jet mass resolution by about 50%; the three working points have about 58, 40 and 16% cc efficiency. In the resolved topology a c-jet energy regression (adapted from the b-jet one), the recovery of FSR jets, and a kinematic fit in the 2L channel improve the m(H_cand) resolution by up to 20%. For the VZ validation the resolved BDTs were retrained with VZ as signal; the merged analysis needed no change because its BDTs do not use the mass; μ_VZ = 1.01 (+0.23 −0.21).

Both 2023 papers claim a first for Z→cc: the VH paper calls its VZ result the "first observation of Z→cc at a hadron collider", and HIG-21-012 (slide 7) says Z→cc is observed "for the first time" in Z+jets at high pT. The "first" claim is kept on slide 7 only, so the deck does not make two competing first-observation statements; if asked, both are true in their own wording.

Off the slide but good to know: the observed interval excludes κc = 1 because of an upward fluctuation. The best fit is μ = 7.7 (+3.8 −3.5), about 1.9σ above μ = 1 if estimated from the quoted uncertainty (the paper calls it "a small upward statistical fluctuation"), and it sits in the merged-jet category: merged μ̂ = 8.7 (+4.6 −4.0), resolved μ̂ = −9.5 ± 9.6 (backup p21). The κc interval is a profile-likelihood scan with the 95% CL boundary at −2ΔlnL = 3.84; when the data fluctuate up, the minimum moves away from κc = 1 and the SM can fall outside the interval, which is not evidence against the SM.

Your notes, sorted by where they can be used (verified against the PRL on 17 Oct):
Public, on slide 5 or backup p22: DeepJet for resolved and ParticleNet for merged; merged is under 5% of the signal but has much lower background; V+jets and tt̄ are the main backgrounds, normalised in control regions; resolved fits the BDT score and merged fits the regressed mass; three cc purity categories in merged; ParticleNet mass regression; the 300 GeV large-R (R = 1.5) jet split makes the two topologies orthogonal; the VZ validation retrains the resolved BDTs with VZ as signal. (The VH paper's "first observation of Z→cc at a hadron collider" is true but left off slide 5, since slide 7 carries the first-observation claim.) Also public, via the 2016 paper whose strategy the PRL says it follows (JHEP 03 (2020) 131): V+jets split by jet flavour and free rate parameters for the background normalisations.
Corrected: the analysis is statistics-limited (85% of the total uncertainty), not systematics-limited; the c-jet energy regression, FSR recovery and 2L kinematic fit are the resolution "recovery" you mention (up to 20% better mass resolution), and the paper's reason for the merged gain is lower background, not higher Higgs reconstruction efficiency.
Internal only (analysis note or approval talks; not in any public paper, keep out of the slides): control regions built by inverting the c-tag selections; the subleading-jet c-tag score fitted in the resolved control regions; the two topologies fitted simultaneously with rate parameters not shared, V+jets and tt̄ scale factors and c-tagging efficiencies uncorrelated between them and everything else correlated; VH(cc) fixed to the SM in the VZ fit.

**Read.**
VH(H→cc), PRL 131 (2023) 061801, arXiv:2205.05550 (HIG-21-008): read the whole letter, it is short; the key parts are the description of the resolved and merged-jet selections, the ParticleNet tagger and its calibration, the VZ(Z→cc) validation, and the κc interpretation (Eq. 1). The public results page has the supplementary κc scan and the per-category best fits (Additional Tables 5 and 6).
ParticleNet: H. Qu and L. Gouskos, Phys. Rev. D 101 (2020) 056019, arXiv:1902.08570, for how a graph network on jet constituents works.

---

## Slide 7: Direct H→cc: boosted H, ggF-enriched (20 s, flash)

**Say.** At very high Higgs pT, above 450 GeV, the Higgs is a single large-radius jet tagged with DeepDoubleX, with a data-driven QCD estimate from the failing region. The peak you see is Z to charm, observed here for the first time in Z plus jets. For the Higgs, μ is below 47; the paper gives no κc. So this is a complementary high-pT handle, and I move on.

**Understand.** Signal composition 55% ggF, 25% VBF, 20% VH (the paper's numbers), hence "ggF-enriched". The jet mass is the soft-drop mass (β = 0, z = 0.1). DeepDoubleX is decorrelated from the mass, which is what allows the failing region to predict the QCD shape in the passing region; QCD is more than 95% of the background. The Z+jets result is μZ = 1.00 (+0.17 −0.14 syst ± 0.08 theo ± 0.06 stat), "well over 5 standard deviations" in the paper's words. The VZ result on slide 5 and this Z+jets one are different production modes; the deck keeps the "first observation" wording here only.

Internal only: the pre-approval quoted an expected Z→cc significance of 11.4σ and the approval talk "11σ expected/observed"; the published paper and PAS say only "well over 5σ", so do not quote 11σ in the public talk.

**Read.**
Boosted H→cc, PRL 131 (2023) 041801, arXiv:2211.14181 (HIG-21-012): the paragraphs on the DeepDoubleX tagger and its calibration, the passing/failing region fit, and the Z+jets result μZ = 1.00 (+0.17 −0.14 syst ± 0.08 theo ± 0.06 stat).

---

## Slides 8–9: ttH(H→cc): selection and jet tagging (8), event classifier and regions (9) (65 s)

**Slide 8.** Three channels by top-pair decay: 0ℓ with at least seven jets (six above 40 GeV, H_T > 500 GeV), 1ℓ with one lepton and at least five jets, 2ℓ with two opposite-charge leptons and at least four jets (same-flavour pairs below 20 GeV or in the Z window vetoed). Every channel needs at least three b- or c-tagged jets, one of them b. ParticleNet puts every jet in one of 11 tagging categories. **Slide 9.** Because the many b and c jets make the top and Higgs reconstruction ambiguous, a ParT classifier works directly on the objects and gives 10 (9) class scores. D_ttX, the sum of the four signal scores, defines the regions: above 0.85 the four SRs, 0.6–0.85 the five CRs, 0.4–0.6 the validation region with the same structure. All from the PRL; the approval talk was only used as a guide to structure.

**Say.** The strategy is a simultaneous measurement: ttH to charm and ttH to bottom have essentially the same signature apart from the number of charm and bottom jets, so they are fitted together, and ttZ with Z to charm or bottom serves as a standard candle in its own regions. Every jet goes into one of eleven ParticleNet tagging categories, and a transformer event classifier, ParT, separates the four signals from five top-pair backgrounds. The leading background is top pairs with extra jets, split by the flavour of those jets, each part normalised in its own control region; QCD multijet is negligible even in the all-hadronic channel. The signal and control regions sit above 0.6 in the summed signal score; a validation band between 0.4 and 0.6 with the same structure checks the background model. The result: μ below 7.8, with 8.7 expected, and |κc| below 3.0 with κb fixed, 4.2 if κb is fitted. On the side, ttH to bottom comes out at 4.4 sigma and the ttZ candles agree with the SM. So a second direct channel with sensitivity comparable to VH.

**Understand.** Why QCD is negligible in 0L: the ParT classifier has a dedicated QCD-multijet output in that channel, and the cut D_QCD < 0.0001 suppresses QCD by nearly four orders of magnitude, to below 1% of tt+jets, so it is neglected; QCD simulation is only used to train the classifier (backup p25). The tt+jets components are tt+light, tt+c, tt+≥2c, tt+b, tt+≥2b (defined by the flavour of the extra jets, ghost-matched hadrons); tt+b and tt+≥2b come from a dedicated 4FS POWHEG tt̄bb̄ sample, the rest from the inclusive 5FS tt̄ sample, and all five normalisations float in the fit. The validation region is split into CR-like (0.40 to 0.58) and SR-like (0.58 to 0.60) parts with background purities matched to the analysis region. The 11 tagging categories are B0 to B4, C0 to C4 and L0 in the (b+c vs light, b vs c) ParticleNet plane (backup p24); ParticleNet rejects background jets up to twice as well as DeepJet. Best fits: ttH(bb) 0.91 (+0.26 −0.22), 4.4σ (4.5σ expected); ttH(cc) −1.6 ± 4.5; ttZ(bb) 1.47 (+0.45 −0.41), 3.5σ (2.4σ); ttZ(cc) 1.02 (+0.79 −0.84), 1.2σ (1.3σ). The simultaneous fit lets you fit κb and κc together (backup p26). Statistics dominate (74% of the total), then tt+c and tt+light modelling (about 32% and 29%).

**Read.**
ttH(H→cc), PRL 136 (2026) 011801, arXiv:2509.22535 (HIG-24-018): the main-text paragraphs on event categories and the ParT classifier, and the Supplemental Material sections "Simulated samples", "Baseline event selection", "Neural network event classifier", "Systematic uncertainties", "Validation of the background model" (Fig. B.6) and the QCD rejection (Fig. B.3).
Particle Transformer: H. Qu, C. Li, S. Qian, "Particle Transformer for jet tagging", arXiv:2202.03772.

---

## Slide 10: ttH(H→cc): results (post-fit in all regions, limits, best fits) (35 s)

**Note.** The deck now shows the strategy first (slide 8, with the categorisation tree) and the post-fit plot with the numbers second (slide 10). The limits and best-fit table moved to slide 10, so when you rehearse, say the numbers there rather than on slide 8.

**Say.** The newest direct channel is the Higgs produced with a top-quark pair. This one plot is the whole analysis: three channels, with zero, one or two leptons from the top pair, and in each of them five control regions for the top-pair background and four signal regions, all fitted together. The tree on the right is how events are sorted: a classifier's summed signal score sends the most signal-like events into one of four signal regions, ttH or ttZ, charm or bottom, and the next band into the control region of whichever top-pair background they look most like. Data and the fitted model agree across all of it.

**Understand.** Each bin of the post-fit plot is a bin of the ParT discriminant in one category; the p-value of the post-fit agreement is 0.85. D_ttX is the sum of the four signal scores (ttH(cc), ttH(bb), ttZ(cc), ttZ(bb)). Events with D_ttX > 0.85 go to a signal region, split first by D_ttH vs D_ttZ and then by D_X→cc vs D_X→bb; events with 0.6 < D_ttX < 0.85 go to the control region of the tt+jets class with the largest weighted score (weights 100, 12, 4, 2, 1 for tt+light, tt+c, tt+≥2c, tt+b, tt+≥2b; the paper does not explain the choice of weights). Before that, every event must pass D_tt+light < 0.05 (0.02 in 1L), and in 0L D_QCD < 0.0001. The c-enriched regions (ttH(cc), ttZ(cc), tt+≥2c) need at least two c jets, tt+c at least one.

**Read.** arXiv:2509.22535 Supplemental Material: Fig. 5 (the flowchart) and the text around it on the region definitions, Fig. 6 (the post-fit plot), Tables B.6 to B.10 for the post-fit yields per channel.

## Slide 11: ttH + VH combination (60 s)

**Say.** Combining ttH and VH, the H to charm signal strength is below 9.3, with 5.6 expected, assuming SM production. The expected limit is 26 percent better than VH alone and 36 percent better than ttH alone. In κc, with κb equal to one, we get |κc| below 3.5, with 2.7 expected. Notice on the scan in the middle that ttH alone, at 3.0, is tighter than the combination on observed: that is the VH upward fluctuation pulling the combined minimum away from one. So the honest statement is: the expected reach, 2.7, is now below the BSM-motivated value of about three; it is the best expected direct sensitivity to date.

**Understand.** The combination correlates the common experimental uncertainties except jet flavour tagging, which uses different algorithms in the two analyses; theory uncertainties in Higgs production and decay for the same processes are correlated. It assumes SM production cross sections for ttH and VH, and only the branching fraction changes with κc through Eq. (3). The middle plot shows −2ΔlnL versus |κc| for ttH, VH and the combination, solid observed and dashed expected; the combined observed minimum sits near |κc| ≈ 2.2, again because of VH.

**Read.**
arXiv:2509.22535: the combination paragraph ("The expected 95% CL upper limit on μ(H→cc), assuming SM production rates for ttH and VH, is 5.6, representing a 36% (26%) improvement...") and Supplemental Material "Additional results" (Figs. B12, B13).
Statistics background: the Combine documentation (cms-analysis.github.io/HiggsAnalysis-CombinedLimit), the pages on CLs upper limits and on likelihood scans, to be able to explain why μ limits (CLs) and κc intervals (profile likelihood) are different constructions.

---

## Slide 12: H + charm production (60 s)

**Say.** The second handle puts κc in the production vertex: a charm quark and a gluon produce a Higgs boson and a charm quark, independent of the H to charm decay. That means we can use clean Higgs decays, photons or W pairs, and require a charm-tagged jet. The price is a tiny rate: the cH cross section is about 90 femtobarn, so about 0.2 femtobarn in the diphoton channel and 20 in WW. There are three challenges: Higgs plus charm also comes from gluon splitting in gluon fusion, which does not depend on κc and has the same final state; the charm jets are soft and often forward; and the modelling depends on the flavour scheme, which Tiziano Bevilacqua will discuss in the next talk. To turn a cH limit into κc we use the "flat direction": κc is varied while all other Higgs rates are kept at their SM values, so only cH production changes.

**Challenges on the slide (sources).** (1) Tiny rate: σ_cH = 90 fb (both papers), about 0.2% of all Higgs production (JHEP 08 (2026) 051, introduction); σB ≈ 0.2 fb in γγ, ≈ 20 fb in WW. (2) κc-independent H+c: the H+c parts of ggH and other modes that do not depend on the charm Yukawa are treated as background (JHEP 11 (2025) 060, Sec. 3); the WW paper assigns a 50% uncertainty to heavy-flavour H-background modelling. (3) bH: σ_bH = 660 fb, modelled as a background in both analyses; c-vs-b separation (CvsB) is what keeps it under control. (4) Modelling: the flavour-scheme choice for cH (4FS massless vs 3FS massive c quarks) gives a typical 25–30% uncertainty and, with statistics, limits the γγ sensitivity (JHEP 11 (2025) 060, Secs. 3 and 8). "Soft, forward c jets" was dropped from the slide because neither paper states it.

**Understand.** The flat direction (Coyle, Wagner, Wei) rescales all other Higgs couplings by a common κH(κc), chosen so that the signal strengths of every other Higgs process stay exactly one as κc grows; this cancels the width growth for the other channels. The CMS papers give the explicit κH(κc, B_cc^SM) formula (2503.08797 Eq. 1). Without it, large κc would inflate ΓH and suppress every other Higgs rate, which data forbid. The H+c idea itself is from Brivio, Goertz, Isidori.

**Read.**
cH(H→γγ), JHEP 11 (2025) 060, arXiv:2503.08797 (HIG-23-010): Sec. 1 "Introduction" for the physics case and the κc-independent backgrounds, Sec. 9 "Results" for the flat-direction formula (Eq. 1).
Theory: I. Brivio, F. Goertz, G. Isidori, PRL 115 (2015) 211801, arXiv:1507.02916 (H+charm as a κc probe); N. M. Coyle, C. E. M. Wagner, V. Wei, PRD 100 (2019) 073013, arXiv:1905.09360 (the flat direction).

---

## Slide 13: cH(H→γγ) (45 s)

**Say.** The first cH search used the diphoton channel with the full Run 2 dataset. Two boosted decision trees, trained without charm-tagging inputs, separate cH from gluon fusion, the largest resonant background, and from the continuum diphoton background; this gives nine categories per year, and the signal comes from fits to the diphoton mass. In the plot, the peak at 125 GeV is fully explained by the other Higgs processes, mostly gluon fusion; nothing is left for cH, and the best fit is negative, about minus 230. The limit is μ below 243, with 355 expected, and |κc| below 38, with 73 expected. So we are at about 40, not 3: the rate is tiny, and gluon fusion with a charm jet mimics the signal.

**Understand.** Observed (38) is much better than expected (73) because μ̂ is negative. The bottom panel of the plot ("all background subtracted") is where you see that no cH signal remains. The BDTs leave out charm-tagging information on purpose: then the ratio of ggH + c jet to ggH + light jet does not vary with the BDT output, and the heavy-flavour modelling uncertainty can be applied to the overall ggH normalisation (2503.08797 Sec. 6).

**Read.**
arXiv:2503.08797: Sec. 5 "Event selection", Sec. 6 "Event categorization" (the two BDTs), Sec. 7 "Signal and background modeling", Sec. 8 "Systematic uncertainties", Sec. 9 "Results" (Fig. 6).

---

## Slide 14: cH(H→WW) and the γγ + WW combination (60 s)

**Say.** The WW channel uses an electron, a muon, missing energy and a charm jet, with signal regions of one or more charm jets and two BDTs against non-Higgs and other Higgs backgrounds. The κc-independent Higgs plus charm background is fixed to the SM, so the cH signal strength is the only parameter of interest; floating it as well is in backup. WW alone gives μ below 1065 and |κc| below 211. Combined with the diphoton channel we get μ below 257 and |κc| below 47, with 51 expected. The combined observed limit is weaker than diphoton alone, 38, because WW fluctuated up: the best fit is plus 390 in WW versus minus 230 in diphotons. This is κc from production alone, statistics-limited, and independent of the decay to charm.

**Understand.** 1 POI versus 2 POI: in the 2-POI fit the κc-independent H+c background floats too, it anticorrelates with cH (−87%), and the limit weakens to 1804; the combination uses the 1-POI fit. The μ-to-κc mapping in the flat direction is strongly nonlinear (243 → 38, 257 → 47, 1065 → 211), so κc is not simply √μ.

**Read.**
cH(H→WW), JHEP 08 (2026) 051, arXiv:2508.14988 (HIG-24-009): Sec. 4 "Event reconstruction and selection", Sec. 5 "Analysis strategy" (signal and control regions, the two BDTs), Sec. 7 "Results" (1-POI vs 2-POI fits, the flat-direction translation, and the γγ+WW combination).

---

## Slide 15: Indirect constraints on κc (75 s)

**Say.** κc can also be constrained without tagging a single charm jet. A large κc adds charm-initiated Higgs production and increases the total width, and on-shell four-lepton rates are sensitive to both. κV here are the modifiers of the Higgs couplings to Z and W bosons. With |κZ = κW| below one, the on-shell analysis gives κc between −3.7 and 3.2. The new result adds off-shell four-lepton production, which breaks the degeneracy between κV and the width: with |κV| below one, κc is between −3.3 and 2.8; with κZ and κW completely free it is between −8.6 and 7.5. The width measurement itself was in Filippo Errico's talk on Tuesday. Finally, the exclusive decay to J/ψ plus photon gives −166 to 208, which Jas Bierkens covers on Thursday. With |κV| below one, the four-lepton result matches the direct searches, under different assumptions.

**The formula box (new on the slide).** From arXiv:2607.23352 Eq. (1): σ_on ∝ g_p² g_d² / Γ_H and σ_off ∝ g_p² g_d², with g_p and g_d the production and decay couplings (for H→ZZ→4ℓ, g_d ∝ κZ). The full on-shell parametrisation is the paper's Eq. (11): σ(H→4ℓ) = [R_gg σ_ggH + Σ κq² σ_qq→H + σ_ttH + σ_tH + Σ κV² σ_VVH] × κZ² Γ^SM(H→4ℓ) / Γ_H, with Γ_H from Eq. (12), which contains κq² Γ(H→qq) for every light quark and Γ_BSM. Large κc enters twice: as κc² σ(cc→H) in production and as κc² Γ(H→cc) in Γ_H. The paper's own sentence for the problem: "a reduced on-shell cross section could be masked by an arbitrarily large κZ² in Eq. (11)"; and for the fix: "The off-shell parameterization, being independent of Γ_H … allows us to drop that constraint." Spoken version: "on-shell, a bigger width can be compensated by a bigger coupling to Z bosons; off-shell production does not care about the width, so it pins down κZ, and then the on-shell rate pins down the width and κc."

**F. Errico's talk.** "Measurements of the Higgs boson mass and width at CMS", Tue 27 Oct 14:20, https://indico.cern.ch/event/1668640/contributions/7213107/ . It covers the same off-shell measurement from the width side: HIG-25-003 combines ZZ and WW to get Γ_H = 5.1 (+2.0 −1.8) MeV and excludes no off-shell production at more than 5σ.

**Understand.** The on-shell rate goes as κV²κf²/ΓH, so a larger width (from large κc) can be hidden by a larger κV; that is the degeneracy. Off-shell production does not depend on ΓH, so it fixes κV and breaks it. Careful with the plot: the curves are labelled as in the paper's Fig. 8 (|κZ = κW| ≤ 1 versus κZ ≠ κW), while the intervals quoted in the text are from its Table 3, which is "obtained without imposing custodial symmetry". The small asymmetry of the intervals is not a sign measurement: it comes from charm-loop interference in ggH and H→gg, and the constraint is essentially on κc². For J/ψγ the direct amplitude (∝ κc) interferes with the indirect H→γγ*→γJ/ψ amplitude (∝ κγ), which is where the sign sensitivity comes from.

**Read.**
γH + on-shell H→4ℓ, PRD 112 (2025) 112001, arXiv:2502.05665 (HIG-23-011): Sec. 8 "Analysis of the light-quark Yukawa couplings" and 8.2 "Results for light-quark Yukawa couplings" (Table 3 has the scenarios); Sec. 7 for the γH part.
Off-shell + on-shell H→4ℓ, arXiv:2607.23352 (HIG-25-003): Sec. 1 "Introduction" (why custodial symmetry and |κZ| ≤ 1 were dropped), Sec. 6 "Implementation of fitting and associated uncertainties", Sec. 9 "Constraints on Higgs boson Yukawa couplings to light quarks" (Fig. 8, Table 3), Sec. 12 "Measurement of the Higgs boson width from the combination".
H→J/ψγ, PLB 865 (2025) 139462, arXiv:2411.15000 (SMP-22-012): "Introduction" for the interfering amplitudes, and the κc/κγ interpretation in the results (observed (−157, 199) for κc/κγ; (−166, 208), expected (−128, 169), for κγ = 1).
Higgs pT spectrum (backup p29), JHEP 04 (2026) 093, arXiv:2504.13081 (HIG-23-013): Sec. 7, the κ-framework interpretation (it uses γγ, ZZ and resolved ττ; WW and boosted ττ are excluded). Theory idea: F. Bishara, U. Haisch, P. F. Monni, E. Re, PRL 118 (2017) 121801, arXiv:1606.09253.

---

## Slide 16: Where we stand (50 s)

**Say.** This table collects all CMS constraints on κc, with the assumptions behind each. The direct searches assume κb equal to one, SM production and no BSM decays; the combination gives 3.5, ttH alone 3.0, VH alone the interval from 1.1 to 5.5. The four-lepton results allow BSM width and profile the other light-quark couplings; with |κV| below one the new on- plus off-shell result gives −3.3 to 2.8, and without any assumption on κZ and κW about ±8. cH uses the flat direction and gives 47; J/ψγ gives −166 to 208. The rows use different coupling models, so they are not directly comparable. The message: direct searches and the four-lepton result both reach |κc| of about three, where flavour-compatible BSM scenarios live.

**Understand.** The indirect rows are the more general ones (they allow ΓBSM ≥ 0 and float other light Yukawas); the direct rows are stronger under stronger assumptions. This slide is the reference table for the day: the afternoon plenaries (Cabrera Urban on H+c, D'Eramo on H→cc, Tarek on off-shell) will quote these numbers.

**Read.** Nothing new; the assumptions column is drawn from 2509.22535 Eq. (3), 2607.23352 Table 3, 2502.05665 Sec. 8, 2508.14988 Sec. 7 and 2411.15000.

---

## Slide 17: Toward Run 3 (45 s)

**Say.** All the κc results I showed use Run 2 data. What Run 3 has delivered so far are better tools. On the left: machine-learning b and c tagging now runs in the high-level trigger, and in simulation the trigger efficiency for ttH to charm rises strongly from 2018 to the 2022 to 2024 triggers; the HLT taggers were in Jessy Daniel's talk on Monday. On the right: the main background to ttH to charm, top pairs with additional charm quarks, has now been measured with Run 2 data, 680 femtobarn. So Run 3 searches start with higher trigger efficiency and a measured tt+cc background.

**Understand.** Part of the trigger gain is rate budget, not only the tagger: the 2018 trigger ran at 10 Hz, the Run 3 ones at 60, 115 and 170 Hz in 2022, 2023 and 2024. The tt+cc cross section is 680 ± 40 (stat) +130 −100 (syst) fb at parton level (PAS Table 8).

**Read.**
HLT flavour tagging, arXiv:2608.18331 (BTV-25-002): Sec. 5 "Jet flavour identification in the HLT" (5.1 small-radius jets, 5.2 large-radius jets), Sec. 7 "New heavy-flavour jet triggers in Run 3", Sec. 8 "Impact on the CMS physics programme".
tt+b/c cross sections, CMS-PAS-TOP-26-003: the results section and Table 8 (parton-level cross sections), Fig. 9.

---

## Slide 18: Run 3 and HL-LHC prospects (55 s)

**Say.** First Run 3. The direct searches are statistics-limited, 85 percent of the VH uncertainty is statistical, so more data helps directly; on top of that come the better taggers from slide 3, the higher trigger efficiency and the measured tt̄cc̄ background from slide 17. ATLAS has already included 51.5 inverse femtobarn of Run 3 data in its VBF H to charm search. Looking further ahead, the ATLAS and CMS input to the European Strategy update, with 3 inverse attobarn per experiment at 14 TeV, expects about 1.6 standard deviations for VH to charm and |κc| below 1.5 at 95 percent confidence level. That is 30 percent better than the 2019 Yellow Report projection, thanks to improved charm tagging; it is extrapolated from an ATLAS VH study and assumed for both experiments. The bar chart puts it in context: Run 2 observed 3.5, expected 2.7, HL-LHC expected 1.5, with the SM at one. Every bar still includes κc equal to zero. Further gains will come from Run 3 data, machine-learning tagging and the detector upgrades, and theory modelling and tagger calibration will become limiting. κc of order one is where we first become sensitive to whether the Higgs gives charm its mass.

**Understand.** There is no public CMS Run 3 κc projection, so the Run 3 half of the slide is qualitative on purpose; do not extrapolate a number by √L on the spot (that would be a private projection). An upper bound |κc| < 1.5 does not exclude κc = 0; establishing a nonzero charm Yukawa needs more than the HL-LHC projection shows. The 1.5 is an expected sensitivity, not a measurement. The paper does not name the S2/S3 systematics scenario for charm, so do not quote one.

**Read.**
HL-LHC projections, arXiv:2504.00672 (ATL-PHYS-PUB-2025-018, CMS-HIG-25-002): Sec. 2 "Precision Higgs boson physics and rare decays", the charm paragraph ("a 1.6σ significance ... κc can be constrained to |κc| < 1.5 at 95% CL, improving the previous projection from direct searches by 30% [3]"); ref. [11] there is the ATLAS VH study (ATL-PHYS-PUB-2025-012).
2019 Yellow Report: M. Cepeda et al., CERN Yellow Rep. Monogr. 7 (2019) 221, arXiv:1902.00134, the charm-Yukawa section.

---

## Slide 19: Summary (40 s)

**Say.** To summarise. The charm Yukawa is the most accessible second-generation quark coupling, and CMS probes it in decay, in production and indirectly. The ttH plus VH combination gives |κc| below 3.5, with 2.7 expected: the most stringent direct constraint and the best expected sensitivity. Higgs plus charm production gives 47, independent of the decay. The on- plus off-shell four-lepton analysis gives −3.3 to 2.8 with |κV| below one, about eight without. All of this is Run 2; Run 3 starts with better triggers and a measured top-pair plus charm background. So, does the Higgs give charm its mass? Today we are at |κc| of three to three and a half, entering BSM-motivated territory; the HL-LHC is expected to reach 1.5, approaching but not yet reaching sensitivity to κc equal to zero. Thank you.

---

## Backup slides: what to say if asked

**p21 VH categories.** The excess sits in the merged-jet category (μ̂ = 8.7), the resolved category is low (−9.5 ± 9.6). μ limits are CLs, κc intervals are profile-likelihood scans.

**p22 VH analysis details.** Everything about the method that does not fit on slide 5, all from the PRL (plus the 2016 paper for the control-region strategy): resolved tagging and resolution recovery, ParticleNet working points and mass regression, background normalisation, the VZ validation (4.4σ merged, 3.1σ resolved, 5.7σ combined), and the full uncertainty table (statistical 85%, simulation size 37%, c-tagging 23%, theory 22%).

**p23 ttH yields.** The ttH(cc) best fit is −1.6 ± 4.5: compatible with zero and with the SM (about 0.6σ from one).

**p24 ttH flavour tagging.** Each jet gets ParticleNet scores; the plane (b+c vs light, b vs c) is cut into categories; ttZ(cc) is the standard candle; ttH(bb) is measured on the side at 4.4σ.

**p25 ttH validation region and QCD rejection.** Post-fit validation region (0.4 < D_ttX < 0.6, same SR/CR structure) in good agreement; the 0L D_QCD < 10⁻⁴ cut that removes QCD to below 1% of tt+jets.

**p26 (κb, κc) plane.** Orange observed, blue expected; the simultaneous fit constrains both Yukawas, which gives the "κb fitted" number on slide 10.

**p27 cH(WW) post-fit.** μ̂ = 390 (+380 −270), within 1.5σ of the SM; statistics-limited, then flavour-scheme and ggH heavy-flavour modelling.

**p28 floating H+c background.** 2 POI: the κc-independent H+c floats too, anticorrelated at −87%, limit 1804; the combination uses 1 POI.

**p29 Higgs pT spectrum.** 2D (κb, κc) contours only, no 1D κc interval; inputs are γγ, ZZ and resolved ττ.

**p30 J/ψγ.** Interference of direct and indirect amplitudes gives sign sensitivity; 95% CL κc ∈ (−166, 208), expected (−128, 169); 123 fb⁻¹.

**p31 H→μμ.** Evidence at 3.0σ (2.5σ expected) with 137 fb⁻¹ in ggH, VBF, VH and ttH categories; μ = 1.19 +0.40 −0.39 (stat) +0.15 −0.14 (syst); κμ = 1.07 +0.22 −0.22 (68% CL), 0.59 < κμ < 1.50 at 95% CL, from a fit with six free κ and the total width fixed to the SM. The first evidence for a Higgs coupling to a second-generation fermion; charm is the quark counterpart. L. D'Eramo's plenary (Wed 17:00) covers rare decays including μμ.

**p32 HLT tagging.** Light (solid) and b (dashed) misidentification versus c efficiency; VBF H→cc trigger efficiency vs offline ParticleNet score.

**Why no ggH(H→cc) slide, if asked.** CMS has no public ggH(H→cc) result: the Run 3 analyses (HIG-25-001, HIG-25-017, HIG-26-003) were still not public on 17 Oct (404 on both public-results pages). The gluon-fusion-dominated public result is the boosted search on slide 7. Do not quote any Run 3 number from the Athens workshop; those are internal. A safe answer: "gluon fusion is the largest production mode but has no handle on the event besides the Higgs jet itself, so the backgrounds are enormous; the public result in that regime is the boosted search, and Run 3 analyses are in progress."

**p33 likely questions.** The VH excess, what limits the direct searches, ATLAS, why cH is weaker, the negative γγ best fit, boosted without κc, trigger gain vs rate budget, sign sensitivity of 4ℓ.

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

---

## Talks to read instead of the papers

Found on Indico on 17 Oct by searching each analysis ID. Two kinds, and the difference matters.

**Internal (CMS login needed).** Pre-approval and approval talks from the HIG, SMP, BTV and TOP meetings. They explain the method far better than the letters do (control regions, tagger calibration, systematics breakdown, the questions the conveners asked), and many have a recording attached on the same Indico page. They are for your own understanding only: never take a figure, number or statement from them into the Higgs 2026 talk unless it is also in the paper or PAS. Pre-approval is usually the more detailed method talk; approval has the final results and the answers to pre-approval comments.

| Slide | Analysis | Pre-approval | Approval |
|---|---|---|---|
| 4 | VH(cc), HIG-21-008 | [C. Li, 18 May 2021](https://indico.cern.ch/event/996931/contributions/4361753/attachments/2243311/3809918/vhcc_run2_preapproval.pdf) | [B. Burkle, 20 Jan 2022](https://indico.cern.ch/event/1114283/contributions/4682422/attachments/2374600/4059447/VHcc%20Full%20Run%202%20Approval_vFinal.pdf) |
| 5 | Boosted H→cc, HIG-21-012 (titled "Search for ggH, H→cc" internally) | [A. Novak, 14 Oct 2021](https://indico.cern.ch/event/1071751/contributions/4562961/attachments/2325238/3966861/2021_10_14_ggHcc_PreApproval.pdf) | [N. Smith, 3 May 2022](https://indico.cern.ch/event/1154424/contributions/4849345/attachments/2431700/4172913/ncsmith_hig-21-012_app_v3.pdf) |
| 6 to 8 | ttH(cc) + combination, HIG-24-018 | [I. Paraskevas, 10 Dec 2024](https://indico.cern.ch/event/1451200/contributions/6253349/attachments/2983951/5254841/HIG_24_018_PreApproval.pdf) | [S. Wuchterl, 25 Mar 2025](https://indico.cern.ch/event/1495540/contributions/6425146/attachments/3032687/5366393/2025_03_25_Approval_HIG_24_018.pdf) |
| 9, 10 | cH(γγ), HIG-23-010 | [X. Zhang, 5 Dec 2023](https://indico.cern.ch/event/1319600/contributions/5694955/attachments/2764717/4817168/Xuanhao_20231205.pdf) | [T. Bevilacqua, 9 Jul 2024](https://indico.cern.ch/event/1429005/contributions/6032192/attachments/2888399/5071481/HpC_approval_Tiziano_Bevilacqua.pdf) |
| 11 | cH(WW) + combination, HIG-24-009 | [M.-Y. Lee, 4 Feb 2025](https://indico.cern.ch/event/1495520/contributions/6347010/attachments/3008389/5303495/HIG-24-009-Preapp.pdf) | [M.-Y. Lee, 30 Apr 2025](https://indico.cern.ch/event/1495526/contributions/6484892/attachments/3054982/5409542/HIG-24-009-Approval_v2.pdf) |
| 12 | γH + on-shell 4ℓ light Yukawas, HIG-23-011 | [J. Davis, pre-approval reprise on light Yukawas, 16 Jul 2024](https://indico.cern.ch/event/1433234/contributions/6048301/attachments/2897045/5079725/Light_Yukawa_PreApproval_Reprise.pptx.pdf) | [J. Davis, 17 Sep 2024](https://indico.cern.ch/event/1451194/contributions/6122638/attachments/2922793/5143469/Approval_Talk.pdf) |
| 12, 13 | Off-shell + on-shell 4ℓ, HIG-25-003 | [A. Petkovic, 14 Oct 2025](https://indico.cern.ch/event/1583963/contributions/6730263/attachments/3154167/5601958/Preapproval_HIG-25-003.pdf) | [M. V. Srivastav, 5 Mar 2026](https://indico.cern.ch/event/1620561/contributions/6969499/attachments/3229277/5761458/HIG-25-003_Approval_3_6_2026.pdf) |
| 12 | H→J/ψγ, SMP-22-012 | [R. Ardino, κc interpretation at the Higgs combination meeting, 14 Nov 2023](https://indico.cern.ch/event/1319571/contributions/5668916/attachments/2752181/4790999/23_11_14__HComb__HToJPsiG_KappaC.pdf) | [R. Ardino, 20 Nov 2023](https://indico.cern.ch/event/1344769/contributions/5673179/attachments/2751893/4797451/23_11_20__SMP__SMP_22_012_approval__rardino.pdf) |
| backup p29 | Higgs pT combination, HIG-23-013 | [M. Galli, 23 Jan 2024](https://indico.cern.ch/event/1360899/contributions/5750357/attachments/2779350/4856476/240123_PreApp.pdf) | [M. Galli, 15 Jul 2024](https://indico.cern.ch/event/1433234/contributions/6040614/attachments/2891744/5078908/240715_Approval.pdf) |
| 14 | HLT flavour tagging, BTV-25-002 | [S. Mukherjee, 19 Jan 2026](https://indico.cern.ch/event/1621020/contributions/6862391/attachments/3196953/5702168/BTV_25_002_preapproval_presentation.pdf) | [A. Zaza, 6 May 2026](https://indico.cern.ch/event/1672122/contributions/7071918/attachments/3267043/5840127/BTV_25_002_approval_presentation.pdf) |
| 14 | tt+c/b cross sections, TOP-26-003 | [D. Kavtaradze, 1 Jul 2026](https://indico.cern.ch/event/1702002/contributions/7158578/attachments/3301174/5916171/pre_approval.pdf) | [D. Kavtaradze, 29 Sep 2026](https://indico.cern.ch/event/1732787/contributions/7286199/attachments/3347605/6009791/approval.pdf) |
| backup p31 | H→μμ, HIG-19-006 | (only a CADI link on Indico) | [S. Cooperstein, 22 Jul 2020](https://indico.cern.ch/event/938597/contributions/3950570/attachments/2075743/3490666/cooperstein_vbfhmm_approval_july222020.pdf) |

Slide 18 (HL-LHC, HIG-25-002) has no CMS approval talk on Indico; it was an ATLAS+CMS Strategy input, so read the paper's Sec. 2.

Also useful, internal: the Higgs-meeting unblinding talks (e.g. [HIG-21-008](https://indico.cern.ch/event/1071753/contributions/4604268/), [HIG-21-012](https://indico.cern.ch/event/1109092/contributions/4736970/), [HIG-24-018](https://indico.cern.ch/event/1495519/contributions/6320944/), [HIG-23-010](https://indico.cern.ch/event/1360952/contributions/5873410/), [HIG-25-003](https://indico.cern.ch/event/1583957/contributions/6822413/)) show the first look at data and the discussion around it, and the DeepDoubleX DP-note talk at BTV ([5 Sep 2022](https://indico.cern.ch/event/1197015/contributions/5032235/)) explains the slide 7 tagger.

**Public (no login; safe to quote).** Overview talks on CMS Higgs-charm results at conferences, newest first. These are the closest thing to your own talk, and anything in them was public when shown.

| Date | Talk | Speaker | Event |
|---|---|---|---|
| 25 Aug 2026 | [Search for H→cc at the CMS experiment](https://indico.cern.ch/event/1571736/contributions/7095496/) | L. Generoso | ICNFP 2026 |
| 1 Aug 2026 | [Constraints on Higgs-charm couplings](https://indico.cern.ch/event/1522800/contributions/6987290/) | F. Monti | ICHEP 2026 (closest to this talk) |
| 21 Aug 2025 | [Constraints on Higgs to heavy flavour couplings](https://indico.cern.ch/event/1446820/contributions/6592212/) | L. Giannini | SUSY 2025 |
| 5 Dec 2024 | [Higgs+charm CMS](https://indico.cern.ch/event/1389221/contributions/6225297/) | T. Bevilacqua | LHC Higgs WG workshop |
| 6 Nov 2024 | [Constraints on Higgs-charm couplings](https://indico.cern.ch/event/1391236/contributions/6095877/) | S. Wuchterl | Higgs 2024 |
| 19 Jul 2024 | [Status of Higgs-charm coupling measurements at CMS](https://indico.cern.ch/event/1291157/contributions/5888310/) | M. De Coen | ICHEP 2024 |

A good order: Monti (ICHEP 2026) for the overall story, then for each slide the pre-approval talk for the method and the approval talk for the final numbers, checking anything you want to say against the paper section listed under that slide above.
