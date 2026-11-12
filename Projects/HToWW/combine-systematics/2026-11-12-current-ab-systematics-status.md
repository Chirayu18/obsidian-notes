---
tags: [reference, review]
status: active
date: 2026-11-12
source: laptop
evidence: source-inspection
---

# Current A/B systematic inventory and remaining fit checks

Requested by Chirayu: “What is the status of all the systematics, break down each one for me”. Read-only inventory of analysis HEAD71eef55, current A/B workflow YAMLs, `build_cards_from_templates.py`, shared `make_combine_inputs.write_datacard`, correction manager and individual correction modules. No systematic/config/code edits or new fits were performed for this inventory. Implemented does not mean validated in the new production fit: production MVA/RUN/cards/impacts are not yet available.

This current inventory supersedes the **current-status interpretation** of the historical July master list, not its recorded July measurements. [[2026-11-12-final-cards-todo]] contains useful open items but predates the completed negrw v2 switch, G2 guard, Summer23 replacement and tau alignment; its old “no alphaS source” wording is qualified by [[2026-11-12-hplusc-alphas-rate-sources]].

## Experimental and detector effects

| Source / nuisance | Current implementation | Status / remaining check |
|---|---|---|
| Luminosity | `configure_era`:2022 1.4%,2023 1.3%, all MC except floated tt | Configured. Name shared within calendar year, separate2022/2023; detailed official common-component luminosity correlation model not implemented here. |
| Pileup `CMS_pileup_<year>` | MC weight Up/Down from calibration | Implemented; new fit-bin effects pending. |
| Muon ID `CMS_eff_m_id_<year>` | HWW tight-ID SF | Implemented; producer factorization checked10Nov, not re-measured. |
| Muon isolation `CMS_eff_m_iso_<year>` | tight PF iso conditional SF | Implemented; same producer chain. |
| Muon prompt MVA `CMS_eff_m_promptMVA_<year>` | HWW ttH-MVA SF after ID×iso | Implemented; same producer chain. |
| Electron ID `CMS_eff_e_id_<year>` | POG Medium | Implemented; matches producer combination. |
| Electron prompt MVA `CMS_eff_e_promptMVA_<year>` | Medium+ttH-MVA conditional factor | Implemented; producer multiplies this with Medium ID and separate reco. |
| Electron reco below20 | `CMS_eff_e_reco_below20_<year>` | Implemented, pT-specific variation. |
| Electron reco20–75 | `CMS_eff_e_reco_20to75_<year>` | Implemented, pT-specific variation. |
| Electron reco above75 | `CMS_eff_e_reco_above75_<year>` | Implemented, pT-specific variation. |
| Muon momentum scale | `CMS_scale_m_<year>` object shifts | Implemented; nominal and shifted selection/features recomputed. Full production migration checks pending. |
| Muon resolution | `CMS_res_m_<year>` object shifts | Implemented with deterministic correction path recorded by prior work; new output checks pending. |
| Electron scale | `CMS_scale_e_<year>` | Implemented. |
| Electron resolution | `CMS_res_e_<year>` | Implemented; old nominal-only-smearing-key defect was corrected in prior work. |
| JES | `CMS_scale_j_<year>`, Total source | Implemented, including MET propagation. No full regrouped-source decomposition. |
| JER | `CMS_res_j_<year>` | Implemented, including MET propagation. |
| Unclustered MET | `CMS_met_unclustered_<year>` | Implemented in jerc.py; no longer missing as in July inventory. |
| c-tag | `CMS_ctag2d_<year>` Total Up/Down | Implemented, **physics-provisional**: Chirayu10Nov says calibration is wrong for now, Livio update pending. No guessed changes. Changing category edges can require retraining/reprocessing. |
| Muon/electron trigger SF | Both `trigger:false` | Deliberately disabled under existing decision; no active trigger-efficiency nuisance. Not equivalent to a measured zero uncertainty. |
| PU jet ID | No separate active nuisance found | Not in current model; whether appropriate depends on selected Run3/PUPPI jet definition, not automatic inheritance from Run2. |
| L1 prefiring | No active Run2 prefiring nuisance | Not part of this Run3 model. |

Seven paired kinematic shift sources are JES,JER,muon scale/resolution,electron scale/resolution,unclustered MET. A separate seventh/eighth “lepton ONNX uncertainty” is not created: inference parity tests validate software, not a new physics nuisance.

**Lepton provenance correction:** [[Projects/HToWW/2026-11-10-lepton-sf-provenance-check]] matched all8analysis JSONs to latinos and matched muon ID×iso×promptMVA and electron Medium×promptMVA×reco. The earlier double-counting concern is not supported by that evidence. Producer measurement definitions remain less documented. Analysis keeps component nuisances separate; latinos combines several uncertainties. Keep their correlation treatment distinguished from nominal factorization.

## Theory, modelling and negative weights

| Source | Current implementation | Status / remaining check |
|---|---|---|
| ISR `ps_isr` | PS weight pair | Active except tt via `no_theory:[tt]`. Same nuisance name across active processes/eras, not process-decorrelated. New templates pending. |
| FSR `ps_fsr` | PS weight pair | Same scope/status as ISR. |
| μR `scalevar_muR` | ×2/×0.5 LHE ratios; nominal factor1 | Active except tt; running-Yukawa correction for configured central H+c/H+b. New fit-level effects pending. |
| μF `scalevar_muF` | ×2/×0.5 LHE ratios | Same scope/status. |
| μR and μF together `scalevar_muR_muF` | paired coherent variation | Same scope/status; three separate nuisance directions, not a newly adopted single7point-envelope model. |
| PDF shape `lhe_pdf` | Central H+c/H+b generator-level member normalization and Hessian prescription; Route B3FS override uses replica dispersion | Implemented. Rate/acceptance/shape and correlations must be checked on final outputs. Removing inclusive member rate does not force every selected SR-bin integral to nominal: acceptance can change. |
| H+c inclusive PDF | `xsec_hplusc_PDF=1.074` in both arms | Configured. Saved13.6TeV4FS gridpack result7.43%±0.14%stat; old Run2 6% is not current value. Transfer to stitched B remains an explicit modelling assumption. |
| αS shape `lhe_alphaS` | Event-weight path where actual members exist | H+c4FS325500 has **no αS pair**, so listing this nuisance does not supply a nonzero signal αS uncertainty. No fabricated pair. |
| H+c inclusive αS | No dedicated rate lnN | **Missing process-specific value.** Old Run3flat3% has historical provenance as upper endpoint of generic Run2Table16 range, not an established H+c scan. See alphaS sources note. |
| H+b inclusive PDF⊕αS | No separate implemented contribution in current lnN | Candidate+3.36%/−3.44% in final-cards note; needs per-channel H+b contribution inside mergedhiggsbkg and overlap check with generic5% term. |
| top-pT `top_pt` | tt nominal correction, Down=no correction, Up symmetric full correction | Implemented and nominal retained under object shifts. New fit impact pending. |
| Higgs+charm `higgs_plus_c` | ±50% on ggH/VBF events with a GEN c-jet pT>25,absη<2.5 | Replaces old flat40% on entirehiggsbkg. Implemented. Code includes VBF as well as ggH; scope vs AN's ggH wording remains a physics distinction. |
| A flavour scheme `xsec_hplusc_3FS_4FS` | central4FS leading GEN c-hadron-pT shape, Up=3FS-like, Down=2−Up | Implemented in A only. No oldflat30% lnN in current config. Final templates pending. |
| B flavour-scheme treatment | complementary4FSzero-cjet and3FS≥1-cjet regions, per-era stitching | Implemented; A's separate FS-shape nuisance disabled to avoid duplicating the comparison. Missing-rate/shape coverage and scale/PDF consistency still need card checks. |
| B3FS PDF rate-vs-shape | 3FS not in `lhe_renorm_datasets`, unlike central4FS | Potential overlap with separate7.4%signal PDF rate; resolve/check at card stage, don't silently count both. |
| B scale normalization | stitched regions originate in distinct schemes with different normalization handling | Open consistency check, not closed by marker completeness. |
| negrw `CMS_negrw_vjets` | v2 production model, ensemble-spread pair on V+jets, per-era/sample yield-preserving renormalization | Implemented, G1/G2/statistics completed. **Fit-bin closure open**: review found shape biases not generally covered by this ensemble band. User explicitly chose v2 despite this outstanding check. |
| tt hdamp / UE tune / alternative generator | No separate active card rows or new-builder alternative-sample operation found | Not covered by merely having ISR/FSR. Requires an explicit alternative-sample prescription if needed. |

The card writer's `no_theory` exception covers **scalevar/ps** ontt, not every theory-named nuisance. PDF/αS rows are not removed by this flag. It writes most configured shape rows across all card process classes; actual applicability is determined by produced modifiers and explicit not-applicable declarations, so nominal-equal shapes must be inspected rather than counted as nonzero coverage.

## Rates, fit freedom and finite MC statistics

| Source | Current setting | Status |
|---|---|---|
| Single top cross section |0.9873/1.0167 |−1.27%/+1.67%, inherited prescription; configured. |
| Diboson cross section |1.037 |3.7% on merged diboson; configured. |
| V+jets cross section |1.027 |2.7% on mergedV+jets; configured. |
| Higgs-background production |1.05 |5% on mergedhiggsbkg; coarse process grouping/overlap must be reviewed when adding specific H+b theory. |
| BR(H→WW) |1.01 onhplusc **and entirehiggsbkg** |Configured but merged-background scope is broader than H→WW components; component-aware effect needed for final treatment. |
| BR(H→ττ) |1.01 on **entirehiggsbkg** |Same grouping issue; this is not a1% effect restricted toττ yields. |
| tt normalization |shared `rate_tt rateParam * tt 1.0 [0,5]` |Free fit parameter constrained by CR/SR data model; not a fixed Gaussian percentage. |
| Finite MC statistics |`autoMCStats 10` per channel |Configured; bin uncertainties derive from sumw2. Not a global10% uncertainty. Fresh impact ranking unavailable. |

## Final-card and validation limitations

- No new nuisance impact ranking or numerical limit exists yet; July impact numbers refer to a different model and cannot be presented as current results. Use actual Combine impacts after the new cards, not only freeze-one-nuisance shortcuts.
- Era naming groups detector nuisances by2022/2023, correlating pre/post suberas within eachyear. Theory names are generally shared. Fine-grained JES/c-tag decomposition and a full component correlation matrix are not implemented.
- The current builder defaults an **evaluated but empty final object-shift template to nominal**, logs it, and floors non-positive final bins. The delegated stop-and-review choice requires `object_shift_empty_fallback:error` before final cards; not set in current YAML. Missing required variations otherwise fail unless explicitly not-applicable.
- `smooth_shapes:false`; no additional smoothing introduced. Empty templates, bin floors and declared inapplicability require inspection of `template_policy.json`.
- All these final-shape/card checks remain downstream of production MVA/RUN. Passing unit/smoke tests establishes code paths, not the correctness of the final all-era fit.

Sources: current remote repoHEAD71eef55; [[2026-11-12-final-cards-todo]], [[2026-11-12-hplusc-alphas-rate-sources]], [[Projects/HToWW/2026-11-10-lepton-sf-provenance-check]], [[Projects/HToWW/negative-weights/2026-11-12-negrw-g1-g2-provenance-and-corrected-stats]], [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-direct-continuation-training-launch]]. All statements remain agent-reported/source-inspected unless a specific executed check is named.
