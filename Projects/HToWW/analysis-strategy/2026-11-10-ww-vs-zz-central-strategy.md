---
tags: [reference]
status: active
date: 2026-11-10
source: laptop
evidence: agent-reported
---

# H+c WW versus ZZ: missing channel or missing strategy?

Chirayu confirmed the comparison is our H+c, H→WW analysis versus Saranya's H+c, H→ZZ→4ℓ, and asked whether we miss a channel or strategy used by the central H→WW analysts. Exact WW/ZZ limit artifacts and whether μ or κc are being compared were not supplied. Equality of the limits is therefore not verified here.

## Answer

Against the local central **H+c→WW** reference AN-23-102, there is no evidence of a missing lepton-flavour channel: it selects one electron and one muon, like us. The concrete differences concern categorisation, retaining discrimination against Higgs backgrounds, and background-template statistics/validation. This does not establish the scope of the latest inclusive Run 3 H→WW analysis, which is a different measurement.

The larger WW signal rate need not imply a stronger limit. Two neutrinos prevent a narrow fully reconstructed Higgs-mass peak; ZZ→4ℓ has one. The peak rejects continuum backgrounds, but cannot distinguish H+c from another Higgs production mechanism with a charm jet. Both analyses need charm/flavour discrimination and a treatment of Higgs backgrounds. This is a physics explanation for similar sensitivity, not a demonstrated numerical decomposition of the two results.

Public sources: [CMS WW description](https://cms.cern/index.php/book/export/html/1187), [CMS four-lepton description](https://cmsexperiment.web.cern.ch/node/2029).

## Direct check of the central H+c reference

Source: `References/HToWW/AN-23-102.pdf`, read with `pdftotext -layout References/HToWW/AN-23-102.pdf -` on 2026-11-10. PDF pages below count from the first PDF page. This local copy contains preliminary Asimov results and FIXME placeholders; do not present them as the latest published central results.

| Strategy | Central prescription / direct source | Our recorded status / implication |
|---|---|---|
| Lepton channel | §4.1, PDF p25, lines 327–338: one e, one μ, ≥1 c jet, MET>45 GeV | Same basic final state. ee/μμ are not a demonstrated missing channel relative to this reference. Semileptonic WW would be a separate analysis with different backgrounds. |
| Charm multiplicity | §4.1, PDF p25, lines 337–338: separate Nc-j=1 and Nc-j>1 SRs; reports 8% sensitivity improvement | August strategy audit lists this split as absent. Current implementation not inspected here. Test on corrected inputs; 8% is the reference's result, not a forecast for us. |
| Two discrimination tasks | §5.2, PDF p41, lines 444–465: BDT(H+c,Other Bkg) and BDT(H+c,Bkg-H), retain the plane with k-means bins | Our recorded multiclass model has separate probabilities, but uses argmax regions and one score per region. It is not established that this loses important information. Benchmark a fit retaining both discriminants on identical inputs. No need to assume two binary BDTs outperform a multiclass NN. |
| 1POI versus 2POI | §8, PDF p65, lines 655–665: flavour-split Higgs backgrounds; 1POI SR uses one BDT, 2POI uses clustered two-score information and floats bkg-H+c | Do not describe the 2D fit as required for every central result. Matched POI/nuisance definitions are essential to comparing limits. The draft reports 431 (1POI) versus 969 (2POI) at 138 fb⁻¹, line 669: different assumptions alone substantially change its result. These are historical draft values. |
| W+jets template precision | §6.1, PDF p56, lines 515–526: stitched jet/pT/HT samples, cross-period averaged shapes, smoothing | Our prior diagnostics identify weak effective V+jets MC statistics. negrw is a different proposed treatment; it needs closure and uncertainty validation. Smoothing cannot create independent events, and any era pooling needs a justified common shape. |
| CR fit | §8, PDF p65, lines 662–665: yield-only top CR, high-mll BDT shape, simultaneous fit | Our multiclass CR strategy already constrains top. The later local binning study found collapsing CR shapes worsened sensitivity. Do not prescribe central CRs or yield-only fits as an automatic improvement. |

## Existing WW work that takes priority over a channel expansion

- Retrain on final signal/selection/MET and all eras, with held-out or out-of-fold templates. The 2026-11-05 audit records private-signal training, older leptons/MET, postEE-only backgrounds, and training/fit overlap for v11. A fresh current output was not checked here.
- Resolve charm-category edge/SF provenance and large variations. Both discrimination and systematic templates depend on them.
- Validate V+jets/negrw closure and binwise effective statistics; compare adaptive binning and more appropriate MC inputs.
- Include WG at retraining per the existing decision; missing backgrounds improve completeness, not necessarily the expected limit.
- Resolve lepton-SF factorisation and trigger-efficiency treatment. Adding a missing uncertainty can weaken a limit while making it more reliable.

Sources: [[2026-08-10-analysis-strategy-from-AN]], [[2026-08-12-CR-structure-and-vjets-degeneracy]], [[Projects/HToWW/2026-11-05-status-audit-retraining]], [[Projects/HToWW/framework/2026-11-05-saranya-hczz-branch-comparison]]. October pre-fix uncertainty ranking: [[Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3]]. Historical diagnostics are not the current corrected card's measured losses.

## Decisive comparison

Obtain the exact WW and ZZ cards/results, luminosities, signal σ×BR convention, POI definition, and expected/observed status. On fixed corrected WW inputs compare baseline versus charm-multiplicity split, retained two-score fit, and MC-stat-aware binning, with full, MC-stat-frozen and stat-only expected limits. Verify template completeness and background-model closure. No new job, code change, unblinding, or limit was run here. No guaranteed gain or missing-channel explanation is established.

This note adds an interpretation and direct-source cross-check; it does not replace a numerical result in an earlier note.
