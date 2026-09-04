---
tags: [reference, review]
status: active
date: 2026-08-21
source: laptop
---

# Referee report — AN H+c, H→WW: new sections (blue text, Sec. 10–18, pp. 28–66)

Scope: only the blue-coloured material was reviewed (Sec. 10 Signal Sample Production
through Sec. 18 Results, plus the References). Black/red/magenta text was not reviewed.

Overall: the new sections are well organised and the physics arguments are, for the most
part, stated rather than asserted — the κ-HCE derivation and the negative-weight
reweighting section in particular read as genuine derivations. The main weaknesses are
(a) several numbers that do not close or are internally inconsistent, (b) an
under-justified statistical model, and (c) a results section that quotes a limit of
r ≈ 1000 without ever confronting the reader with what that means physically.

Comments are graded:
  **[MAJOR]**  must be addressed before this can go forward
  **[MINOR]**  should be fixed
  **[CLARITY]** correct as far as one can tell, but needs more explanation

---

## A. Cross-cutting / highest priority

**A1 [MAJOR] The headline result is never put in physical terms.** The whole note
quotes limits as "1034", "1164", "1150" in units of r, with r = 1 defined at
σ×B = 2.214×10⁻³ pb (Sec. 10.5). An expected limit of r ≈ 1000 means the analysis
is sensitive to ~1000× the SM rate, i.e. σ×B ≲ 2.3 pb, and at 26.7 fb⁻¹ the SM signal
is ~59 events before any selection efficiency. This should be said explicitly, once,
in Sec. 18.1: the reader needs to know the analysis is nowhere near SM sensitivity and
that the exercise is a method/limit-setting demonstration on one era. As written, the
tables of "∆ = 78 units", "costs 33 units" invite the reader to treat these as
meaningful physics gains when they are all deep in the no-sensitivity regime. Also
state the signal yield in the SR (events at r = 1) — it does not appear anywhere.

**A2 [MAJOR] Only 2022postEE is used, but this is never stated up front.** Sec. 10
says signals were produced "for all four Run 3 campaigns", Table 21 shows five of eight
samples exist, Table 40's caption says "2022postEE, 26.7 fb⁻¹", and the nuisance names
are `CMS_ctag2d_2022`. The reader has to reverse-engineer that every result in
Sec. 13–18 is a single-era 26.7 fb⁻¹ result. Add an explicit statement at the start of
Sec. 16 (or 18): *"All results below use 2022postEE only; the other campaigns are not
yet included."* Also say what the plan is for combining eras and whether the MVA will
be retrained or the 2022postEE network applied to other eras.

**A3 [MAJOR] The note is blind (Asimov, `observation -1`) — say so prominently and
state the unblinding plan.** This is only visible as a row in Table 35. It belongs in
the introduction to Sec. 18 with a sentence on what the unblinding criteria are.

**A4 [CLARITY] No control-region validation against data anywhere.** Every plot in
Sec. 16–18 is prefit/postfit MC. For a blind analysis this is expected for the SR, but
the five control regions — especially CR_tt at 94% purity and CR_vjets — should show
data/MC agreement. Without a single data/MC comparison the reader has no evidence that
the simulation describes the phase space at all, which undercuts everything downstream
(the MVA is trained on it, the categories are defined by it, the ctag SFs are validated
on it). This is the single largest gap in the new material. If data/MC plots exist,
they must go in; if they do not, that should be stated as a to-do.

---

## B. Section 10 — Signal Sample Production

**B1 [MAJOR] The cross section (Sec. 10.5) has no provenance.** σ×B = 2.214×10⁻³ pb
is quoted bare. State: (i) the order of the calculation (this is presumably the LO/NLO
MadGraph 4FS number from the gridpack, not an LHCHWG recommendation — say which);
(ii) the H→WW→2ℓ2ν branching fraction used and its source; (iii) whether it is the
H+c cross section with a pT/η requirement on the charm quark, or fully inclusive. Since
r is defined relative to this number, *every* limit in the note is only as well-defined
as this one line. Given Table 38 assigns it a 30% 4FS/5FS uncertainty and a 6% PDF
uncertainty, the central value clearly deserves more than one sentence.

**B2 [MAJOR] No sample-validation material for the private production.** Privately
produced signal samples with no central counterpart require evidence they are correct.
At minimum: a comparison of a few generator-level distributions (Higgs pT, charm-jet
pT/η, ΔR(H,c)) against expectation or against the Run 2 central sample; confirmation
that the H→WW branching and decay chain in Pythia is as intended; and a statement that
the pileup profile and the conditions GT match the central 2022postEE campaign. As
written, the section documents *how* the samples were made but gives no evidence that
*what* came out is right. This will be the first question from the ARC.

**B3 [MINOR] Sample sizes are small and unequal, and the consequence is not discussed.**
277k events for H+c 2022postEE. After the eµ selection + ≥1 c-tag, what is the signal
MC statistical uncertainty in the SR template? Table 22 says only 2257 H+c events reach
the MVA training set — if the SR template is built from O(10²) weighted events, the
signal `autoMCStats` terms could matter and the shape could be unstable. Quote the
signal SR raw and effective event count.

**B4 [MINOR] Table 21 lists three of four campaigns for H+c and two for H+b; the text
says the rest are "in production."** Give a date or a milestone. Also, H+b 2022preEE
has 810k events against 298k for postEE — nearly 3× — with no comment. If those are to
be combined, the per-era statistical weights will be very uneven; say whether that is
intentional.

**B5 [CLARITY] Sec. 10.1–10.2 read as an operations log, not an AN section.** The
lxplus8/lxplus9 architecture anecdote and the DRPremix memory tuning (4.3–8.1 GB vs
4 GB, "2500 MB/core policy limit") are useful internally but are not physics and do not
belong in an analysis note — they belong in a twiki or a production log. Recommend
compressing Sec. 10.1–10.2 to: generator, tune, flavour scheme, scale choice, mH,
CMSSW/gridpack version, and the campaign chain (Table 20). Conversely, what *is*
missing and should be added: the PDF set used, the matching/merging scheme and merging
scale (FxFx implies a merging scale — quote it), and the number of additional jets in
the matrix element.

**B6 [MINOR] "µR,F scaled by 0.50" with a dynamical scale — say what the dynamical
scale is** (HT/2? sum of transverse masses?) and why 0.50 was chosen. This is the
central scale to which the 8.7%-impact `scalevar_muF` nuisance (Table 42) is applied,
so it is not a detail.

**B7 [MINOR] Sec. 10.4 (Access).** The XRootD redirector failure and the IIHE endpoint
are, again, operations. One sentence is fine; the `[3011] No servers are available`
error string is not AN material.

---

## C. Section 11 — MVA Training

**C1 [MAJOR] Table 22 does not close.** The listed classes sum to 3.79×10⁶
(t̄t 3.18×10⁶ + single top 4.99×10⁵ + ggZH 1.05×10⁵ + H+c 2257) against a stated total
of 4.08×10⁶ — a shortfall of ~2.9×10⁵ events (7%). Either classes are missing from the
table (diboson and V+jets are in the six-class scheme but absent from the table; only
one Higgs mode, ggZH, is listed) or the total is wrong. Give the full composition, all
six (or thirteen) classes, or state explicitly that the table is a partial listing.

**C2 [MAJOR] 2257 signal training events is very few.** With a 80:20 split that is
~1800 for training, against 3.18×10⁶ t̄t — a 1:1400 imbalance handled by
inverse-frequency weighting. Two things must be shown: (i) that the quoted AUCs are not
overfit — the test-set AUC is quoted but no train-vs-test comparison is given, and with
1800 signal events and a 128-64-32 MLP overtraining is a real risk; (ii) the statistical
uncertainty on AUC = 0.966 given ~450 signal test events. Please add train/test ROC
overlay and a k-fold or bootstrap uncertainty on the AUC. Related: were the signal
events weighted by their MC weight in training, or treated as unweighted?

**C3 [MAJOR] The MVA input variables are never listed.** Fig. 1 is captioned
"Distributions of the MVA input variables" but the text never enumerates them.
Sec. 13.5 mentions the 11 one-hot c-tag categories bring the count "to 26", implying 15
kinematic inputs, but they are nowhere named. A table of the input features, with a
one-line motivation for each, is mandatory. Also state whether any input is
mass-correlated or could sculpt the background, and whether the network sees the
c-tagging one-hot *before* or *after* the SFs are applied.

**C4 [MAJOR] Train/test splitting is described but the more important issue is not.**
"80:20 by deterministic hash of the NanoAOD event identifier" is good practice. But the
categories used in the fit (Sec. 16) are defined by the argmax of this same network,
and the fit templates are built from *all* events, including the 80% used in training.
This is the classic overtraining leak: any overtraining sculpts the template shapes and
is not covered by any nuisance. Either use a k-fold scheme so every event is scored by
a network that did not see it, or demonstrate explicitly that the SR template shapes
built from train-only and test-only events agree. This needs to be addressed.

**C5 [MINOR] The v10 failure ("AUC ≈ 0.51") is asserted, not diagnosed.** "Extreme
class imbalance across thirteen targets" is a plausible story, but v32 also has thirteen
classes and works. The distinguishing factor is the loss, not the class count, so the
explanation as given contradicts the later section. Rephrase: flat CE over 13 classes
with this imbalance failed; the hierarchical loss recovers it.

**C6 [MINOR] Table 24 / Table 26 discrepancy in the argument.** Sec. 11.5 says v32
"gives the better raw signal discrimination" (0.975 vs 0.966) but v11 is used. The
justification — that six classes map one-to-one onto the six datacard processes — is
reasonable but should be quantified: what would the limit be using a v32-derived
categorisation? An AUC gain of 0.009 may be worth more than the convenience of a
one-to-one mapping, and the note should show that it is not. As written, the better
classifier is discarded on aesthetic grounds.

**C7 [CLARITY] "AUC(hplusc vs higgsbkg) = 0.882 ... sets the ceiling on the achievable
sensitivity."** This is the most interesting physics statement in Sec. 11 and it is one
sentence. Expand: which Higgs mode is the actual limiting one (ggH+HF? VBF?), and is the
irreducibility kinematic or purely a matter of c-tagging? Given that `higgsbkg` is
13.1% ggH but 29% VBF (Sec. 17.4), the claim that ggH+HF is the limiting background
should be demonstrated, not assumed.

**C8 [MINOR] Table 23: hyperparameters are given but no optimisation is described.**
Say whether these were scanned or taken as defaults, and whether early stopping was
used (30 vs 50 epochs for v11/v32 with no stated criterion looks arbitrary).

---

## D. Section 12 — The κ-HCE Loss

This is the most carefully written section in the new material and the derivation is
followable. Comments are mostly about justification and validation rather than
correctness.

**D1 [MAJOR] The section derives a novel loss but never demonstrates it was worth it.**
The only quantitative payoff quoted is AUC 0.966 → 0.975 (Table 26), and v32 is then
*not used for the fit* (Sec. 11.5). So an entire section derives a method that
contributes nothing to the result. Either (i) show a limit obtained with v32 so the
method has a physics payoff, or (ii) move Sec. 12 to an appendix and state plainly that
it is a methodological study retained for future use. As currently placed — a full
section between the MVA and the c-tagging — it reads as more central than it is.

**D2 [MAJOR] No ablation.** The loss has three terms and two hyperparameters
(λ = 1, τ = 0.3, plus k_fine which is never given a value). Table 26 gives one number
for the whole construction. Needed: AUC (or better, limit) with λ = 0 (no significance
term), with the fine term off, and for τ ∈ {0.1, 0.3, 1.0}. Without this the reader
cannot tell whether the gain comes from the hierarchy, the significance term, or simply
from training 50 epochs instead of 30. **The 30 vs 50 epoch difference between v11 and
v32 (Table 23) is a genuine confound for the 0.966 → 0.975 comparison and must be
controlled.**

**D3 [MINOR] k_fine is defined in the notation table and appears in Eq. 12.4 but its
value is never given.** Sec. 12.4 lists λ, τ, batch size, lr, epochs — but not k_fine.
Add it.

**D4 [CLARITY] The claim that detaching c_j "avoids the collapse (κ→0) and saturation
(κ→1) pathologies of earlier learned-κ losses" needs support.** Which earlier losses?
Is there a reference, or an internal study? If it is the latter, show the failure mode
(e.g. the κ trajectory with and without the detach) — this is the central design claim
of the section and it is currently an assertion.

**D5 [CLARITY] Eq. 12.10: D is claimed to lie in (0,1].** With α_s = σ(1/τ) ≈ 0.966,
not 1 — the signal class's own α does not appear in the denominator (j ≠ s), so D = 1
only when p_s = 1. Fine. But Table 25 lists α = 0.966 for H+c with cos θ = +1.000,
which suggests α_s *is* being computed and used somewhere. Clarify whether the j ≠ s
exclusion in Eq. 12.10 is exact in the implementation.

**D6 [MINOR] Eq. 12.2 defines the hard split at c_j ≥ 0, i.e. exactly orthogonal
templates land in the signal-like group.** Sec. 11.4 says "diboson is approximately
orthogonal" — so diboson's group membership can flip epoch to epoch on numerical noise.
Is the group assignment stable at the end of training? Show the c_j trajectories
(the text says they were looked at; put the plot in).

**D7 [MINOR] Table 25 lists only 5 of 13 classes.** Give all thirteen, or say the table
is a selection. In particular t̄t and single top are discussed in the text ("strongly
negative similarity") but their values are not shown.

**D8 [CLARITY] The merging argument in Sec. 12.3.1** ("a merged column contributes no
gradient that pushes the P templates apart") is a nice observation but is asserted.
A one-line gradient argument would make it convincing.

**D9 [MINOR] Eq. 12.7: the inverse-frequency weight is written `invfreq(j) = ΣᵢNᵢ/Nⱼ`
and then "normalised so that max_j = 1".** With inverse frequency, max is attained by
the *rarest* class, so normalising to max = 1 means the rarest class gets weight 1 and
everything else is suppressed. That is the intended behaviour but the phrase "normalised
so that max_j = 1" is ambiguous — state which class attains the max.

**D10 [CLARITY] Notation: the note uses both k_fine (Eq. 12.4, notation table) and
K_fine (Sec. 11.4).** Unify. Similarly Sec. 11.4 writes "L = L_group + K_fine L_fine +
λ L_sig" and Sec. 12.3 repeats it — fine, but keep the symbols identical.

---

## E. Section 13 — Charm Tagging

**E1 [MAJOR] "It has been verified that the two axes CvL and CvB are sufficient ... and
that no third discriminant is required."** Verified how? By whom? This is a strong
statement (it is effectively a claim about the completeness of the ParticleNet output
basis) presented with no evidence and no reference. Either cite the BTV documentation
where this is established, or show the study, or delete the sentence.

**E2 [MAJOR] The single-nuisance treatment of the whole 2D plane is not defensible as
final and the note should say what the plan is.** Sec. 13.3 acknowledges "a
decomposition into independent components remains to be done" — good — but
`CMS_ctag2d_2022` is the 5th-largest impact in Table 42 (70 units, 6.8%). Treating 11
categories as 100% correlated in a single up/down is an aggressive assumption that can
either over- or under-estimate the uncertainty depending on how the migrations
cancel across categories. State which direction the current treatment is expected to
err in, and give a timeline. Recommend at least a 2-component split (c-vs-light and
c-vs-b axes) as an interim check to bound the effect.

**E3 [MINOR] Table 27 tabulates 5 of 11 categories and says 7 are populated.** Show all
seven. C4 in particular is missing and the text says only B1–B4 are empty — so C4 and
B0 should be in the table.

**E4 [MINOR] The occupancy statement is a red flag worth expanding.** "Only seven of
eleven categories are populated ... the b-rich B1–B4 categories are empty." In an eµ
+ ≥1 jet selection dominated by t̄t (82% of the SR!) it is surprising that the *b-rich*
categories are empty. t̄t final states are full of b jets. This suggests either that the
jet entering the c-tag categorisation is explicitly the non-b jet, or that a b-veto is
applied upstream, or that the category is assigned per-event from a selected jet. The
note never says *which jet* the category refers to. This must be specified — it is
central to interpreting Table 27 and Fig. 4.

**E5 [MAJOR] Fig. 7 is captioned "Closure of the two-dimensional scale factors: ratio
of corrected simulation to data" but the closure is never discussed in the text and no
number is quoted.** If this is a data/MC closure it is the only data comparison in the
new material — it deserves a paragraph. Quote the residual non-closure and say whether
it is covered by the assigned uncertainty.

**E6 [MINOR] "degrades the expected limit by 14 units, as it must: a scale factor
introduces an additional nuisance parameter."** Two issues. (i) A scale factor also
changes the *central* prediction, so the limit could move in either direction; the
"as it must" is too strong. Table 28 shows stat-only also moves (668 → 676), which is
precisely the central-value effect and disproves the "purely an extra nuisance" reading.
(ii) The frozen-autoMCStats column moves by 25 while the full moves by 14 — worth a
sentence, since it implies the SF and the MC-stat terms interact.

**E7 [CLARITY] Sec. 13.5: one-hot c-tag categories as MVA inputs.** Feeding an
11-category one-hot to the network means the *category* is a training input while the
*scale factor* for that category is a nuisance. Confirm that the SF is applied as an
event weight after scoring (so it does not change the score) — the note implies this
but does not say it. If the SF were applied before scoring the object-shift argument of
Sec. 16.4 would apply here too.

---

## F. Section 14 — Negative-weight reweighting

The derivation (Eqs. 14.5–14.11) is clean and correct, and the honesty about where the
approximation enters (Sec. 14.4) is commendable. Comments concern validation.

**F1 [MAJOR] The renormalisation in Sec. 14.6 quietly breaks the exactness claim, and
the note under-states this.** Table 30 shows the W→ℓν closure is 1.122 — a 12%
non-closure in the signal region. The fix is a per-dataset renormalisation to the
nominal yield. But: (i) 12% is large; (ii) the renormalisation restores the integral,
not the shape, and the shape is what the fit uses. The note asserts "the variance
reduction ... is unaffected" but says nothing about whether the *shape* is right after a
12% pull. Required: a comparison of the reweighted-and-renormalised template shape
against the nominal signed-weight template shape in the SR, with a χ²/ndf or a
bin-by-bin ratio. If the shape moves, that is a systematic that is currently unassigned.

**F2 [MAJOR] The uncertainty is almost certainly under-estimated.** `CMS_negrw_vjets`
is the 20-model *ensemble spread* (mean δg = 0.006) and "profiles to a negligible
impact." An ensemble of 20 HistGradientBoostingClassifiers trained on the same data with
the same features measures only the seed/initialisation variance — it does not cover the
dominant error, which is the systematic mismodelling of P₊ from a finite feature set
(20 aggregate generator-level features cannot fully determine the sign probability).
The 12% W→ℓν non-closure of Table 30 is direct evidence that the true error is far
larger than δg = 0.006. Recommend either (i) taking the SR non-closure itself as the
uncertainty, or (ii) a feature-subset / alternative-model variation, or (iii) at minimum
an explicit statement that δg is a lower bound and why the residual is believed covered.
As it stands the method removes a statistical uncertainty and replaces it with a
systematic that has been assigned as negligible — that trade needs to be justified.

**F3 [MINOR] The DY vs W→ℓν closure difference is unexplained.** 1.013 vs 1.122 for
two processes reweighted by the same ensemble. Why is W so much worse? This is
diagnostic information — if the classifier was trained on a mixture dominated by DY,
say so.

**F4 [MINOR] Consistency check on the negative-weight fractions.** Sec. 14.1 quotes
16.4% negative in "the V+jets samples used here", and ⟨g⟩ = 0.672 = 2(0.836) − 1 is
consistent. But Sec. 15 replaces the inclusive W sample (16.1% negative) with jet-binned
samples whose event-weighted negative fraction is ~20.9% (10.2/25.7/34.7% for 0J/1J/2J).
So after the Sec. 15 change the global negative fraction is *higher*, and the 16.4%
figure and the ⟨g⟩ = 0.672 number in Sec. 14.3 are presumably pre-replacement. State
which sample set Sec. 14's numbers refer to, and whether the ensemble was retrained on
the jet-binned samples. If it was not, the classifier is being applied out of its
training domain.

**F5 [MINOR] "one DY bin was measured at 0 ± 41 events from ±79 000 weights
cancelling."** Excellent, concrete motivation — keep it. But say which bin, in which
region, so the reader can see whether it is a bin the fit actually uses.

**F6 [CLARITY] Sec. 14.5, the training region.** The argument that the eµ veto makes
the sets disjoint and therefore no overfitting bias arises is correct as far as it goes,
but disjointness in events is not sufficient — a classifier overfit to the training
region will still be biased when applied to a kinematically different region. The note
half-acknowledges this ("interpolated ... rather than extrapolated") and then does not
verify it. Show the coverage: the distributions of the 20 input features in the training
region and in the SR, overlaid, so the reader can see the SR support is contained.

**F7 [CLARITY] AUC = 0.829 on a stochastic target.** The statement that a perfect
classifier cannot exist is correct but the reader cannot calibrate 0.829 against the
achievable maximum. Quote the reference: what AUC would a perfect P₊ estimator give,
given the measured overlap? Fig. 8 (P₊ for true-positive vs true-negative events) should
let you extract this.

**F8 [MINOR] Anchored vs substring dataset match (Sec. 14.7).** The WH near-miss is a
good catch, but again this is implementation detail. One clause, not three lines.

**F9 [MINOR] Ref. [2] is given as a bare arXiv number with no author list, and Ref. [1]
is empty.** Fix the bibliography. Also Sec. 14.8 says the method "follows" Ref. [2] —
be explicit about what is taken from it and what is new here, since the note elsewhere
presents the derivation as its own.

---

## G. Section 15 — W+jets sample choice

**G1 [MAJOR] Table 32's "Combined 29.8 fb⁻¹" is wrong, or at least misleading.** The
per-sample equivalent luminosities (7.7, 13.0, 9.1) have been added. Adding equivalent
luminosities is only valid if the three samples describe the *same* process over the
*same* phase space, which is exactly what they do not — they are exclusive jet bins.
The physically meaningful combination is Σneff / Σσ = 8.5 fb⁻¹, not 29.8. Note that the
realised gain in the SR (Table 33: neff 280 → 1170, a factor 4.2) matches
8.5/1.9 = 4.5, and does *not* match 29.8/1.9 = 15.7. So the table's own combined number
is contradicted by the analysis's own result two tables later. Either recompute or
explain what "Combined" means; as written a reader will quote 29.8 fb⁻¹.

**G2 [MAJOR] The V_pT > 100 GeV gap is stated and then dropped.** "This means the
region VpT > 100 GeV is not covered by the additional statistics." That is a real
acceptance-relevant hole: the SR requires ≥1 c-tagged jet and is presumably not
concentrated at low V_pT. Quantify: what fraction of the SR V+jets yield has
V_pT > 100 GeV, and what is neff in that subset? If the high-V_pT tail is where the
signal lives, the improvement is smaller than Table 33 suggests. Also explain *why* the
pT-binned samples were not stitched in, given AN-23-102 does exactly that (the note
cites this as motivation and then does not follow it).

**G3 [MINOR] "The sum of the jet-binned cross sections exceeds the inclusive value by
1.6%, consistent with the expected spread from NLO merging and not indicative of double
counting."** Assertion. 1.6% is plausible but the "not indicative of double counting"
conclusion needs support beyond a plausible size — e.g. show that the 0J/1J/2J LHE jet
multiplicity distributions are exclusive and non-overlapping (the note does this only
for V_pT in the 0J sample). Also: is the 1.6% excess absorbed anywhere, or does the
total W+jets normalisation now sit 1.6% high relative to the inclusive prediction?

**G4 [MINOR] "all other processes change by less than 13% and in both directions,
consistent with the templates having been rebuilt."** 13% is a large change to wave
through as a rebuild artefact. What causes a 13% change in, say, the diboson yield when
only the W+jets sample is swapped? If it is MC statistics in the rebuild, say so and
quote the expected size. If it is the free-floating t̄t rate re-adjusting, say that.

**G5 [CLARITY] "the 2J sample contributes 69% of surviving SR events."** Good
observation. It also means the analysis is now dominated by the sample with the worst
negative-weight fraction (34.7%) and worst neff/N (0.094). Worth one sentence on the
interaction between Sec. 14 and Sec. 15 — the reweighting is doing most of its work on
the 2J sample.

**G6 [MINOR] Only 2022postEE samples are tabulated (Table 31 caption).** Confirm the
replacement is applied consistently and that the other eras will follow.

---

## H. Section 16 — Statistical model

**H1 [MAJOR] Argmax categorisation: orthogonality is claimed, statistical independence
of the *shape* is not addressed.** "The regions are orthogonal by construction and every
selected event is used" — true. But the discriminant in each region is *the winning
score*, i.e. a variable whose range is bounded below by 1/6 and whose distribution is
sculpted by the argmax operation. This is unusual and needs justification: (i) show the
binning and the score range per category; (ii) confirm the 10 bins are equal-width in
the winning score or quantile-based, and how the binning was chosen; (iii) confirm that
no bins are empty or near-empty for the signal (this drives the autoMCStats behaviour
noted in Sec. 18.4). None of this is currently stated.

**H2 [MAJOR] The control regions do not control what their names say.** Table 34:
CR_higgsbkg is 86.4% t̄t, CR_st is 87.6% t̄t, CR_diboson is 72.4% t̄t. These are not
control regions for the Higgs background, single top, or diboson — they are four
additional t̄t regions with different score shapes. The note defends this ("expected
rather than a deficiency ... t̄t is dominant everywhere") but the defence misses the
point: a CR is useful if it *constrains* something. Show the constraint: give the
pre- and post-fit uncertainty on each background normalisation, and demonstrate that
CR_st actually constrains single top. If it does not, say so, and consider whether the
five CRs are earning their systematic cost. Note Table 42 shows `rate_tt` freezing moves
the limit by only 23 units — i.e. the t̄t normalisation, which is the one thing the CRs
demonstrably constrain, is nearly irrelevant to the result.

**H3 [MINOR] The single free-floating `rate_tt` across all six channels assumes the t̄t
*shape* is correct and that one normalisation describes t̄t in all regions.** Given the
regions are defined by MVA argmax, and t̄t populates them all, a single scale factor is a
strong assumption — a mismodelled t̄t score shape will be absorbed into it and bias the
SR. Test: allow independent t̄t rates per channel (or in SR vs CRs) and show the limit
does not move. Also: `rate_tt` has range [0,5] with a postfit value of 1.000 ± 0.017 —
a 1.7% constraint on t̄t from CR_tt. That is a *very* tight constraint to place on a
theory-uncertainty-free floating parameter; it means any t̄t mismodelling at the >2%
level is not covered anywhere in the model, since t̄t carries no cross-section lnN and no
hdamp/mtop variations (Sec. 17.6). This is a genuine hole. **t̄t is 82% of the SR and
currently carries essentially no theory uncertainty at all.** This should be flagged as
a limitation and probably fixed before unblinding.

**H4 [MINOR] `autoMCStats 10`: the threshold and the resulting behaviour need one more
sentence.** Sec. 18.4 reveals a bin with neff = 2.1. How many bins fall below threshold,
and in which channels? If the SR signal template has low-neff bins, quote them.

**H5 [MINOR] Table 35 "Histograms 1626".** The number is a bookkeeping count, not
physics, and is given with no explanation. It does in fact reconcile exactly —
6 channels × 6 processes × (1 nominal + 2 × 22 shape) = 1620, plus 6 data histograms =
1626 — which is a useful completeness check. Say that in one clause, otherwise the number
is noise to the reader.

**H6 [CLARITY] Sec. 16.3, the `read_scale` / sumw discussion.** The physics point —
that Σw must be accumulated before selection, and that reading it from output metadata
undercounts — is correct and important, and the resulting 18.4% signal shift (Sec. 18.2)
shows it mattered. But it is written as a code note. Recommend: state the definition
(Eq. 16.1), state that the denominator is the pre-selection sum of generator weights,
and put the implementation detail in a footnote. Also confirm this is now validated,
e.g. by reproducing a known cross section.

**H7 [MINOR] Sec. 16.4: twelve shifted directories for JES/JER/electron/muon scale+res.**
JES is applied as a single "total" (Table 37). For an analysis whose leading jet-related
observable is a c-tagged jet, a total JES is a coarse approximation; the JES source
decomposition (or at least a check that the total is conservative) should be mentioned
as future work. JER has only one variation listed — is that η-inclusive?

---

## I. Section 17 — Systematic uncertainties

**I1 [MAJOR] t̄t is excluded from every theory shape nuisance** (Table 36: ps_isr/fsr,
scalevar, lhe_pdf, lhe_alphaS all read "all except t̄t"), carries no cross-section lnN
(Sec. 16.2), no lumi (Table 38 says lumi applies to "all except t̄t"), and no
hdamp/mtop (Sec. 17.6). Its only freedom is a single floating normalisation constrained
to 1.7%. For a process that is 82% of the SR this is a serious under-coverage. The
free-floating rate justifies dropping the *normalisation* uncertainty, not the *shape*
ones — parton-shower and scale variations change the MVA score distribution and hence
the t̄t shape in every channel, and none of that is currently in the model. **This is
probably the most important physics issue in Sec. 17.** Please either add the t̄t shape
variations (decorrelated from the rate) or justify their omission quantitatively.

**I2 [MAJOR] `xsec_hplusc_4FS_5FS = 1.30` is "a placeholder" (Sec. 18.3) and is the
single largest nuisance impact (113 units, 10.9%).** The note correctly flags this, but
a placeholder driving the leading systematic cannot survive review. Give a timeline and
a strategy for the derivation. Also: 30% is a scheme-matching uncertainty — is it meant
to cover the 4FS/5FS difference in the *rate* only, or also the shape? Currently it is
a rate lnN, so any 4FS/5FS shape difference in the charm-jet kinematics — which is
precisely where the schemes differ most — is uncovered.

**I3 [MINOR] Top-pT reweighting (Sec. 17.3) is applied to the nominal with a one-sided
variation to "no correction", symmetrised.** Two problems. (i) The stated Run 2
parameterisation `0.103 e^(−0.0118 pT) − 1.34×10⁻⁴ pT + 0.973` is the NNLO/NLO
data-independent form; applying it to the *nominal* and taking the full correction as
the uncertainty is a defensible convention, but it should be stated whether the CMS TOP
POG recommendation for Run 3 is to apply it at all — most recent CMS analyses apply the
top-pT reweighting as a *systematic only*, not to the nominal. State the recommendation
being followed and cite it. (ii) "No cap is applied at high pT, the functional form
being well behaved" — this checks out (the weight evaluates to 0.89 at 1 TeV and 0.85 at
1.5 TeV, monotonic and never negative), but quote a number so the reader does not have to
verify it themselves. (iii) The "Run 3 rescaling" factor (0.991 + 7.5×10⁻⁵ pT) needs a
citation.

**I4 [MINOR] Sec. 17.4, the ggH heavy-flavour composition weight.** The argument for a
per-event flavour-keyed weight over a flat group lnN is good and correct. But: (a) the
component fractions given (ggH 13.1 + VBF 29.0 + ggZH 23.3 + ZH 21.0 + WH 9.1) sum to
95.5% — 4.5% is missing (t̄tH? bbH?). State what it is. (b) The ±50% is applied to *any*
event with a generator-level c-jet, in *all* higgsbkg components, not just ggH — but the
50% uncertainty is a statement about ggH+HF specifically. VBF with a charm jet is not
uncertain at the 50% level. As implemented the note applies the ggH uncertainty to VBF,
ZH, WH and ggZH as well, which over-covers. Either restrict the weight to the ggH
component or justify the extension. (c) The nuisance is called
`flavor_composition_ggH` with value 1.066 in Table 38 (a *rate* lnN) while Sec. 17.4
describes a *shape* weight — these appear to be two different things with the same name.
Clarify which is in the card, or if both, why.
(d) The nHF definition uses genJets with |hadronFlavour| = 4 — should the b-flavour
(=5) case also be considered for the H+b-like component?

**I5 [MINOR] Table 38: `BR_HtoWW, BR_Htautau` at 1.01 applied to hplusc.** The signal
is H→WW→2ℓ2ν; why does an H→ττ branching uncertainty apply to the signal? Presumably
τ→ℓ contamination enters the selection. If so, say so and quote the τ contribution to
the signal yield. If not, remove it.

**I6 [MINOR] `lumi_13p6TeV = 1.014` applies to "all except t̄t".** Correct given the
floating t̄t rate, but note this means the luminosity uncertainty does not cancel between
the signal and the dominant background in the way the reader might assume — worth a
clause.

**I7 [MINOR] PS weights: `ps_isr, ps_fsr` from "LHE parton-shower weights".** For
Pythia8 the ISR/FSR variations are PS weights, not LHE weights. Check the wording. Also
state whether the reduced or full variation set is used, and whether the known
overestimation of FSR variations is addressed.

**I8 [CLARITY] Sec. 17.5, MET.** Only the unclustered-energy shift is mentioned. What
about the propagation of JES/JER to MET — is it included in the JES/JER templates
(it should be, if MET is recomputed on shift) or missing? One sentence. Also, is MET
even used in the selection/MVA? If it is not, the whole subsection may be moot; if it
is, it should be in the input-variable table (comment C3).

**I9 [MINOR] Sec. 17.6 is a good table and should be kept.** But "Muon reconstruction
SF — no reco key exists in the POG inputs for Run 3" is a statement about a JSON file,
not about physics. The physics statement is that the muon reconstruction efficiency
uncertainty is expected to be negligible/covered by the ID SF — say that instead, and
if it is not known to be negligible, assign something.

**I10 [MINOR] No trigger uncertainty appears anywhere.** An eµ analysis uses dilepton or
single-lepton triggers with a measured efficiency and an associated uncertainty. Neither
the efficiency nor its uncertainty appears in the new sections. If it is in the black
part of the note, add a cross-reference; if not, it is missing.

---

## J. Section 18 — Results

**J1 [MAJOR] "Freezing all constrained nuisances moves the limit from 1034 to 641, so
62% of the limit is statistical in origin and 38% systematic."** This arithmetic is not
right. 641/1034 = 62%, but that is the *ratio of the limits*, not a decomposition of the
limit into statistical and systematic "origins". Limits do not decompose additively, and
the conventional statement is either (i) the stat-only limit is 641 and the full limit
is 1034, or (ii) the systematic component taken in quadrature is
√(1034² − 641²)/1034 = 78%, a very different number. The phrase "38%
systematic" will be read as a quadrature fraction and is wrong under that reading.
Rephrase to state the two limits and let the reader compare, or define the
decomposition explicitly. The same issue infects Table 42's "% of 1034" column.

**J2 [MAJOR] Table 42 is presented with a caveat but the caveat does not go far
enough.** The note correctly says the entries overlap and are not additive. But it then
sums to 38% and quotes percentages, inviting exactly the additive reading it disclaims.
Recommend replacing the "% of 1034" column with the limit values only, and adding the
standard impact plot (Fig. 24 exists — refer to it in the text and discuss it; it is
currently never mentioned).

**J3 [MAJOR] Sec. 18.5, the Run 2 comparison, is not a fair comparison and the note
half-admits it.** 503 × √(138/26.7) = 1144 vs 1034 obtained here. Problems: (i) √L
scaling is only valid in the background-dominated, statistics-limited regime — the note
notes Run 2 is 73.8% statistical and concludes "the correctly scaled value would be
somewhat larger", i.e. the comparison flatters this analysis. Do the scaling properly:
scale the stat and syst parts separately and quote a range. (ii) More importantly,
AN-23-102 is a Run 2 analysis at 13 TeV with a different signal cross section (13 vs
13.6 TeV) and possibly a different r normalisation — if the two r's are not defined
against the same σ×B, the numbers are not comparable at all. State explicitly that the
normalisations match, or convert both to σ×B. (iii) Was AN-23-102's 503 an eµ-only
number or a combination of channels? If it includes more final states, the comparison
is not like-for-like. Given the note's own framing that beating the scaled Run 2 result
is the headline claim, this section needs to be airtight and currently is not.

**J4 [MINOR] Sec. 18.2, Table 41.** The "Early card 1371 — superseded" row plus two
"superseded" caveats in the text make the cascade hard to read. Recommend removing
superseded rows entirely and presenting the cascade only from the first valid
configuration (1150). Keep the description of what changed (the sumw normalisation, the
LOWESS removal) as text.

**J5 [MINOR] The LOWESS smoothing removal deserves more than a clause.** "Template
smoothing was disabled, since the negative-weight reweighting already removes the MC
statistical variance at source and the two treatments were being applied together."
Quantify: how much did the limit move when smoothing was disabled? It is bundled into
the 1371 → 1150 step together with the normalisation fix, so its individual effect is
unknown. Also confirm that no *other* template still benefits from smoothing (V+jets is
reweighted, but is diboson? single top?).

**J6 [MINOR] Sec. 18.4: "all Gaussian nuisances are found at zero pull with
approximately unit post-fit width, as expected."** On an Asimov dataset this is a
tautology — Asimov pulls are zero by construction. The informative content is the
*constraint*: which nuisances are constrained to well below unit width (indicating the
data — here, the Asimov MC — is over-constraining a systematic)? Quote the most
constrained nuisances and their post-fit widths. Any nuisance constrained to ≪1 should
be examined, especially the theory shapes and `CMS_ctag2d_2022`.

**J7 [MINOR] The likelihood-scan crossings.** "−2ΔlnL = 1 crossing at r ≈ 525 and
−2ΔlnL = 3.84 at r ≈ 1075, the latter close to the quoted CLs limit of 1034 as
expected." Note that for an *upper limit* the relevant comparison is one-sided; the
agreement between the two-sided 3.84 crossing and the one-sided CLs limit is a
coincidence of the well-separated regime, and the note says as much — but 1075 vs 1034
is a 4% difference that should be attributed (CLs vs CLs+b? asymptotic accuracy?).
Minor, but state it.

**J8 [MINOR] No observed limit, no expected ±1σ/±2σ bands.** Table 40 gives a single
number. The standard presentation is the median expected with 68%/95% bands. Add them —
they also let the reader judge the fit stability.

**J9 [CLARITY] Fig. 23 ("Development of the expected upper limit") and Fig. 24
(impacts) and Fig. 27 (prefit/postfit SR) are never discussed in the text.** Every
figure needs at least one sentence of interpretation. Fig. 27 in particular: does the
postfit SR show any large pull in the templates?

---

## K. Presentation, references, and consistency

**K1 [MINOR] Reference [1] is empty and [2] has no author list.** Fix the bibliography.
AN-23-102 is cited by number in Sec. 15.1 and 18.5 but does not appear in the reference
list at all.

**K2 [MINOR] Several tables list a subset of rows without saying so** (Table 22, 25, 27,
31). Add "(selected categories)" or give the full listing.

**K3 [MINOR] Units on the limit are never given.** "1034", "∆ = 78 units". Say once
that limits are quoted on the signal strength r (dimensionless, relative to the
Sec. 10.5 cross section), and then drop the word "units" — "the limit degrades by 14"
is clearer than "by 14 units".

**K4 [MINOR] Notation drift:** `κ` vs `α`, `k_fine` vs `K_fine`, `invfreq` typeset
inconsistently, `neff` vs `n_eff`. Also Eq. 14.10 uses a `=̂` symbol that is never
defined.

**K5 [MINOR] The note repeatedly documents implementation paths** (`utils/loss/
HierarchicalCrossEntropyLoss.py`, `config/HPlusCHToWW_kappa_hce.yml`, `CTag2DCorrector`,
`kappa_hce_forward`). One or two are fine for reproducibility; a dozen makes the AN read
as a code manual. Consider collecting them into a single "software" appendix.

**K6 [CLARITY] Figure captions are doing work the text should do.** Fig. 7 (SF closure),
Fig. 11 (closure after renormalisation), Fig. 13 (neff gain), Fig. 14 (neff before/after)
all present results that are never quantified in the text. Every quantitative claim
shown in a figure should also appear as a number in the text.

---

## L. Summary of the must-fix list

1. **Sec. 17/16:** t̄t (82% of the SR) carries no shape theory uncertainty, no
   cross-section uncertainty, and no hdamp/mtop — only a 1.7%-constrained floating rate.
   (I1, H3)
2. **Sec. 11:** the fit templates are built from events the network was trained on;
   no k-fold or train/test template comparison. (C4)
3. **Sec. 14:** `CMS_negrw_vjets` is an ensemble-seed spread (δg = 0.006) assigned as
   negligible, while the SR closure for W→ℓν is 12% off. (F1, F2)
4. **Sec. 15:** Table 32's "Combined 29.8 fb⁻¹" is an invalid combination and is
   contradicted by the analysis's own SR neff gain of 4.2×. (G1)
5. **Sec. 18.1/18.3:** the "62% statistical / 38% systematic" decomposition is not a
   valid decomposition. (J1)
6. **Sec. 18.5:** the Run 2 comparison needs the r normalisations shown to be
   equivalent, and proper (non-√L) scaling. (J3)
7. **Sec. 10:** the signal cross section — the definition of r and hence of every limit
   in the note — has no provenance; the private samples have no validation. (B1, B2)
8. **Sec. 17.2:** the leading systematic is an admitted placeholder. (I2)
9. **Throughout:** no data/MC comparison in any control region. (A4)
10. **Sec. 11:** the MVA input variables are never listed. (C3)

---

## M. Addendum — post-review verification against source (2026-08-21)

After Htoww_local actioned the report, the following items were re-checked against the
card and the analysis code rather than against the AN prose. Files cited are on lxplus.

**M1 — Item I1/L1 was partly WRONG; corrected.** Read directly from the card that
produced the 1034 limit, `/eos/home-c/cgupta/higgscharm/outputs/combine/v11_hplusc_2dcat.txt`
(Aug 14 15:54). The process ordering in each channel block is
`hplusc, higgsbkg, tt, st, diboson, vjets` (line 17), so the third column of every
six is t̄t. Reading the nuisance rows:

| Nuisance | line | t̄t column | Verdict |
|---|---|---|---|
| `lhe_pdf` | 44 | `1` in all 36 | **t̄t IS covered** |
| `lhe_alphaS` | 45 | `1` in all 36 | **t̄t IS covered** |
| `ps_isr`, `ps_fsr` | 32–33 | `-` | t̄t excluded |
| `scalevar_muR/muF/muR_muF` | 34–36 | `-` | t̄t excluded |
| `lumi_13p6TeV` | 22 | `-` | t̄t excluded |

My claim that t̄t was excluded from `lhe_pdf` and `lhe_alphaS` was incorrect. I read the
AN prose ("all except t̄t" in Table 36), not the card; the prose was wrong and my review
inherited the error. **Lesson: card-level claims must be verified against the card.**

The finding survives in narrowed form and remains the top item: what t̄t lacks is the
parton-shower and renormalisation/factorisation scale variations — precisely the sources
that redistribute events across the MVA score. PDF and αS are the smallest theory
sources and do not cover shape redistribution. At 82% SR purity in a shape fit, that gap
is still the most important physics issue in the new material.

**M2 — Item D2 (epoch confound) was WRONG; withdrawn.** `train_v11_2dcats.sh:22`,
`train_v32.sh:18` and `train_v32_sub.sh:18` all set `EPOCHS=30`. The AN's claim of 50
epochs for v32 (Table 23) was a prose error. The 0.966 → 0.975 AUC comparison is *not*
confounded by training length. The rest of D2 stands: there is still no ablation over
λ, τ and k_fine.

**M3 — k_fine confirmed missing from the note, value found.** `k_fine: 7.0`, at
`/eos/home-c/cgupta/HToWW/b-hive/config/HPlusCHToWW_kappa_hce.yml:124` (`tau: 0.3` at
line 119). D3 stands — the note must state it.

**M4 — Item E4 (empty B categories) was WRONG as a physics puzzle; withdrawn, and the
real explanation is stronger than the one offered.** Verified chain:
- `analysis/workflows/hww_combine_2dcat.yaml:95` — the `cjets` collection requires
  `working_points.jet_ctagging(events, 'medium', year)`.
- `analysis/selections/object_selections.py:563-566` — `candidate_cjet` is
  `argmax(cjets.btagPNetCvL)`, i.e. selected *within* the already-medium-tagged set.
- `analysis/working_points/utils.py:40` — for PNet the medium mask is
  `(btagPNetCvB > cvsb_wp) & (btagPNetCvL > cvsl_wp)`.

The medium WP cuts in **both** dimensions. Since the B categories occupy the low-CvB
(b-like) region, requiring CvB above the medium threshold makes B1–B4 geometrically
unreachable — not merely disfavoured. So the empty categories are a hard selection
effect, not a physics anomaly. My "t̄t is full of b jets" instinct was correct physics
applied to the wrong object: the categorisation describes the *candidate c-jet*, which
by construction has already passed a c-tag, not a generic jet in the event.

This does raise a **new** point worth noting: because the selection lives entirely
inside the medium-WP region, the 2D calibration is being used over a small corner of the
plane it was derived for. Comment E2 (single nuisance across all categories) should be
read in that light — the correlation assumption spans far fewer categories than the
scheme's eleven, which may make the single-nuisance treatment more defensible than I
implied, but it also means the L0/C0 scale factors are applied to a population the
untagged region was not meant to describe. Worth one line in Sec. 13.2.

**M5 — Items confirmed correct on recheck, no change:** the Table 32 combination error
(sum(neff)/sum(σ) = 8.51 fb⁻¹, and the 4.5× vs realised 4.2× consistency check confirms
it against 29.8's implied 15.7×); the 62/38 non-decomposition; the higgsbkg 95.5% gap
(t̄tH + H+b); E6 "as it must" (Table 28's stat-only 668→676 is the counter-evidence);
the 1626 histogram reconciliation.

**M6 — On not stating what r ≈ 1000 means (A1).** Htoww_local declined pending the
σ×B convention TODO. That is the right call in the strict sense — an interpretation
written on an unverified normalisation is worse than none. But the *conditional*
statement costs nothing and should go in now: "with the current normalisation
convention (Sec. 10.5, under verification), r = 1 corresponds to ≈59 signal events
before selection at 26.7 fb⁻¹, so the quoted limits are far from SM sensitivity." The
reader needs the order of magnitude even while the convention is being pinned down;
otherwise a table of "∆ = 78 units" reads as a meaningful sensitivity gain.
