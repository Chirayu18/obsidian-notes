---
tags: [reference, presentation, decision]
status: active
date: 2026-11-13
source: laptop
---

# Explain what A and B do; scope the first limit correctly

Chirayu: **“Okay, so we need to show other plots and results for A/B and make it clear in the slides on which flavour scheme treatment does what and give an estimate on the limit etc”**, then **“Tell me A vs B also, explain”**. This updates the interpretation of the stat-only A/B slide in [[2026-11-12-november-update-slide-plan]]. It is not a cancellation of the requested stat-only calculation or permission to invent a full-systematics result.

## Physics distinction to explain

**A: 4FS central prediction plus an explicit scheme shape nuisance.** All central H+c signal events come from the4FS sample. Nominal scheme weight1. The Up weight is the ratio of normalized3FS/4FS spectra in leading GEN charm-hadron pT; Down mirrors it as2−Up. This creates a3FS-like deformation of the4FS prediction, not a replacement by genuine3FS events in all observables. The inclusive ratio construction is shape-only, but selection/category acceptance can change. Current implementation `analysis/corrections/hplusc_fs.py`, nuisance `xsec_hplusc_3FS_4FS`.

**B: stitched central prediction using genuine4FS and3FS events in complementary regions.** Keep4FS events with zero accepted GEN c-jets and3FS events with at least one. Current `hww_routeb_3fs4fs.yaml` uses strict pT>10GeV, |eta|<2.5, AK4 GenJets and per-era fractions/normalization. Signed preselection bookkeeping and stitching scales combine the two regions; this is not simply adding both inclusive samples. A's ratio nuisance is disabled in B to avoid double-counting that treatment. Stitching does not establish that no residual scheme/theory uncertainty remains: the scale/PDF normalization and correlation checks remain open.

The generator-level stitching split is **different from** the reconstructed Nc-jet1/≥2 SR split. Both arms retain the analysis reconstruction selection; do not present B as requiring a different reconstructed charm-jet multiplicity.

Source-inspected13Nov: actual A module and B YAML in analysis5b25295. No physics/config edit made for this explanation.

## First limits: useful scope, no overclaim

The new TRAIN-based Asimov result compares the statistical sensitivity and checks the complete central A/B recipes (each with its own retrained MVA). It retains finite-MC statistics through autoMCStats and the shared free tt rateParam. The optional rate-systematics variant adds configured lnN terms. Neither includes A's3FS/4FS shape or the other missing systematic templates.

Therefore this first result **cannot quantify the gain from replacing A's scheme nuisance with B stitching**, isolate stitching independently of retraining, or establish which treatment wins after full uncertainties. Earlier wording making this the definitive headline A/B physics comparison is superseded. Slide caption: **“A/B expected sensitivity: statistical uncertainties only; modelling-systematic comparison pending.”**

For a controlled comparison, verify common luminosity, corrected input conventions, reconstruction selection, class order, event fold scheme, binning, merged-SR/CR layout, background model and fit settings. Both arms use current negrw v2; G3 closure remains scientifically open. The first new limits use one merged SR; future full-systematics limits use the intended two reconstructed Nc-jet SRs.

## Plot/result checklist for the keeper

1. A ratio construction: leading GEN c-hadron pT spectra, normalized3FS/4FS ratio and Up/Down definition. Show affected selected signal/template response only from actual saved variations; today's nominal TRAIN files do not supply that shape nuisance.
2. B construction: GEN c-jet regions, retained4FS/3FS fractions and signed normalization closure. Overlay central reconstructed distributions to show what actually changes.
3. Like-for-like A/B signal kinematics, normalized preselection yields/composition, and later matched MVA-category templates. Preserve the same weighting/normalization convention on both plots.
4. Held-out ROC/AUC, confusion matrices and training curves. A is ready in [[Projects/HToWW/framework/2026-11-13-a-performance-plots]]; B awaits completed folds. Clearly label unweighted MC performance versus luminosity-weighted physics yields. No v11 improvement claim without a matched comparison.
5. Expected-limit bands/per-era and combined results when actually fitted: stat-only and separately rate-systematics variants, explicit merged-SR scope. Full-systematics treatment/impact comparison remains pending. Do not display invented pulls/impacts or copy old ranks as current.

“Estimate on the limit” means a labelled numerical estimate supported by stated inputs/assumptions, or the first checked expected-limit fit. **No new numerical A/B limit estimate is available yet.** October691 and the old-card V1=703/V2=691 diagnostics remain historical context, not forecasts of the new corrected limits. Explain each modelling choice and its remaining uncertainties alongside any preliminary number. Keeper owns the actual deck; this is an ordinary slide-decision note only.
