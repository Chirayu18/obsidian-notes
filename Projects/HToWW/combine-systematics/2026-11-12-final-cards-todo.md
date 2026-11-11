---
tags: [reference, todo]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# To do before the final HToWW cards (Run A and Route B)

Chirayu, 2026-11-12: "For things for the final cards, record them and keep them do to". These items do not affect TRAIN or RUN processing. They are applied when the cards are built from RUN templates (`build_cards_from_templates.py`), unless a line says otherwise.

## Rate uncertainties: option (a)

Chirayu chose (a) on 2026-11-10 and asked for Run 3 numbers on 2026-11-11.

- [x] **H+c PDF rate:** lnN `xsec_hplusc_PDF: {hplusc: 1.074}`, in `hww_allfix_4fs.yaml`, commit `0d4a035`. The value is the Hessian PDF uncertainty of the inclusive 13.6 TeV H+c 4FS FxFx cross section, NNPDF31 nf4 325500, computed as √Σ(σᵢ−σ₀)²/σ₀ = **7.43% ± 0.14% (stat)**. Source: the clean el8 gridpack validation, `/eos/user/c/cgupta/HToWW/mcm_grid/gp_fix_4fs/validation/out/val_NEW_*.root`, 10,370 events. The official H→γγ gridpack gives 7.49%. The Run 2 AN-23-102 used 6%.
- [ ] **H+c αS rate:** no Run 3 source exists. LHCHWG-2026-007 gives none, and the 4FS set has no αS members. **Chirayu to decide:** estimate it ourselves, e.g. by generating with an αS-varied set, or use a stated proxy. The old 3% has no recorded source.
- [ ] **H+b PDF⊕αS rate:** **+3.36% / −3.44%** from LHCHWG-2025-011 (arXiv:2510.18815) Table 1: 13.6 TeV, mH = 125.09 GeV, NLO+NNLLpart+ybyt matched, linear interpolation. The older LHCHWG-2024-001 Table 9 block B gives +2.0/−2.0% for PDF+αS+mb. H+b sits inside the merged `higgsbkg` process, so apply it per channel as an asymmetric lnN scaled by H+b's share of the `higgsbkg` nominal yield in that channel, measured from the RUN templates. Do not stack it on `xsec_higgsbkg` 5% without checking for overlap.
- The `lhe_pdf` and `lhe_alphaS` shapes stay shape-only for H+c and H+b, because `lhe_norm.py` removes their rate. Check this on the RUN templates: the Up/Down integrals over all channels should equal nominal before selection effects.

## Signal-region split (Nc-j)

- [x] SR split into `SR_hplusc_1cj` / `SR_hplusc_2cj` (AN-23-102 lines 337–338), commit `9802054`.
- [ ] Check the per-channel yields and the background composition against AN-23-102 Table 12 (in Run 2, the Nc-j > 1 SR had about 6% of the Nc-j = 1 signal).
- [ ] The c-tag working point and SFs are provisional until Livio's update, and the Nc-j counting depends on them. If the category edges in `ctag2d_categories.py` change, both training and RUN must be redone.

## Route B only

- [ ] **3FS PDF variation.** `lhepdf.py` applies the Hessian formula, which is wrong for the 3FS MC-replica set 321900. The Route B agent fixes it in `base.py` (replica standard deviation). Verify on the RUN templates.
- [ ] **3FS PDF shape vs rate.** The 3FS sample is not in `lhe_renorm_datasets`, so its `lhe_pdf` carries a rate as well as a shape. Under option (a) the H+c rate is covered by the 7.4% lnN. For consistency, normalise the 3FS PDF variation to shape-only at card stage, or justify the overlap.
- [ ] **Scale variations.** The scale-variation normalisation must be consistent between the 4FS (0 c-jet) and 3FS (≥ 1 c-jet) regions. Open since the proposal.
- [ ] Run A's `xsec_hplusc_3FS_4FS` shape is removed in Route B, since stitching replaces it. Confirm that the cards carry no flavour-scheme term twice and none is missing.

## Other card-stage items

- [ ] `combine.object_shift_empty_fallback: error`: this was the delegated choice ("stop for review"). Set it in the workflow's `combine` block, which is not hashed, before building cards. Review every case listed in `template_policy.json`.
- [ ] The negrw model will be switched to the retrained v2 (in progress) before RUN. The `negrw.model` path is recorded but not hashed (commit `f84d311`).
- [ ] mH = 125.09 GeV normalisation conventions for all Higgs processes (Chirayu, 2026-11-10). Per the 5 Nov check, BR(H→WW) and WH already comply; the remaining processes still need checking.
- [ ] Lepton SFs: provenance checked against latinos on 2026-11-10 (same files, same combination). The per-component uncertainty split is a choice; keep it or merge to match latinos.
- [ ] `GluGluHto2Tau` 2023preBPix: one corrupt file removed, and the sample is Run3Winter23, not Summer23. Swap it when a Summer23 sample exists.
- [ ] Impacts: rank nuisances with a real `combineTool.py -M Impacts` fit, with a wide r range, rather than the current `impacts: freeze_per_nuisance` shortcut. Saranya's HZZ README shows the shortcut can reorder the rankings and wrongly give a nuisance zero impact. Source: [[Projects/HToWW/framework/2026-11-12-saranya-hczz-zx-estimation-ideas]].
- [ ] Rule for new backgrounds: no freely floating normalisation unless a control region in the fit constrains it, and no silent fallback when an input is missing (Saranya, commit `fac4bf1`). Optional: a read-only audit of the card builder for silent fallbacks.
