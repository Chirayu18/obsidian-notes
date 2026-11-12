---
tags: [reference, theory]
status: active
date: 2026-11-12
source: laptop
---

# Where an H+c alphaS rate uncertainty comes from

Literature check answering Chirayu: "where do ppl usually get H+c alpha S rate uncertainity?" No uncertainty value was chosen for the analysis, no generator/integration job was run, and no configuration or analysis code was changed.

## Standard source and procedure

The standard calculation propagates the uncertainty in alphaS(MZ) into the predicted process cross section. Use PDFs fitted at the corresponding varied alphaS values and the same alphaS in the hard cross section. For the symmetric prescription, the relative rate uncertainty is abs(sigma_plus - sigma_minus)/(2 sigma_central). A PDF-provider's alphaS variation members supply the inputs; the percentage is calculated for the process, not read as a universal LHAPDF constant.

Primary sources:
- [PDF4LHC15 recommendations, section6.2](https://arxiv.org/html/1510.03865v2): eq26 assumes alphaS(MZ)=0.1180 +/-0.0015 at68%CL; eq27 takes half the difference between cross sections at0.1195 and0.1165; eq28 combines PDF and alphaS in quadrature. The hard calculation and PDFs must use matching alphaS.
- [PDF4LHC21 recommendations, section6.3.3](https://arxiv.org/html/2203.05506#S6.SS3.SSS3): eq6.6 instead uses0.1180 +/-0.0010 at68%CL; eq6.7 uses0.119 and0.117; eq6.8 combines uncertainties. These conventions must be named, not silently interchanged.
- PDF4LHC21 table6.1 explicitly lists four-active-flavour variants with alphaS members, including `PDF4LHC21_40_pdfas_nf4` (members41/42 at0.117/0.119) and `PDF4LHC21_mc_pdfas_nf4` (members101/102). Their existence does not establish an automatic replacement prescription for this analysis's NNPDF3.1 nominal family.

In practice, obtain the variation cross sections from the theory calculation/authors supplying the H+c normalization, or evaluate them with an appropriate generator/fixed-order setup. Maintain the same signal definition, energy, flavour scheme, perturbative order, mass and Yukawa convention. A dedicated inclusive rate calculation does not require detector-level reprocessing just to obtain its normalization response.

## Specific to this H+c setup

[LHCHWG-2026-007](https://arxiv.org/html/2608.26863v1) section4.3 explicitly identifies the7-point muR/muF variation as its perturbative scale uncertainty; the percentages in table3 are not a supplied alphaS-parametric uncertainty. Section2.3 correlates charm-Yukawa evolution with the running strong coupling. A compatible alphaS scan should therefore document how the reference charm mass/Yukawa is held fixed and evolved, rather than varying only explicit matrix-element powers by hand.

The preferred source is a process-consistent variation of that H+c normalization calculation (or a supplied result from its authors). Borrowing ggH or bbH percentages without demonstrating transfer is a proxy, not an established H+c prediction. No universal H+c alphaS percentage was established by this literature check.

The current 4FS sample's325500 member group contains no alphaS pair ([[Projects/HToWW/2026-11-05-sol-review-unpushed-work]]). This limits what can be extracted from its existing NanoAOD; it does not make a dedicated cross-section alphaS calculation impossible. Re-NANO of the3FS321900 PDF replicas does not manufacture the4FS alphaS variations.

## Previous CMS H+c WW paper

The published [CMS HIG-24-009 paper](https://arxiv.org/pdf/2508.14988), section6, describes PDF normalization effects up to6% for cH. The text checked here does **not** supply a dedicated cH alphaS rate number. Do not reinterpret its6% PDF statement as a separately sourced alphaS uncertainty. This agrees with the existing vault warning that the old3% alphaS value has no recorded justification; this check did not establish one.

## Analysis boundary

Chirayu already chose shape-only event variations plus separately justified inclusive rate uncertainties. This note supplies the literature path for the still-missing H+c alphaS number; it does not select PDF4LHC15 vs21, change PDF families or flavour schemes, change nuisance correlations, set a percentage, adopt a proxy or authorize new jobs. A future calculation must keep rate and acceptance/shape components distinct and avoid counting a combined PDF+alphaS uncertainty again as a separate alphaS rate.


## Run 2 provenance follow-up (12 November)

Question: "How did run2 get it?" Read the local `References/HToWW/AN-23-102.pdf` directly with pdftotext, including complete physicalPDFpages58–59 (§7.1/§7.1.1) and61(Table16, printedp59); rendered/visually inspected the full table page. Also checked the local paper-v15 uncertainty paragraph and the public published paper. This is source tracing, not an independent regeneration of Run2 cross sections or a review of its actual cards.

- AN-23-102§7.1.1, lines568–579: H+c/H+b prescriptions were adopted from **AN-22-064§5**. For H+c it names `NNPDF31_nnlo_as_0118_nf_4_mc_hessian`,100variations, yielding **6% PDF** effect. This does not document a separate alphaS scan.
- Table16 has a dedicated **signal(H+c) PDF6%** row and a separate generic **alphaS+PDF1–3%** normalization row. The table does not supply a process-applicability matrix showing whether that generic row also applies to cH, nor a dedicated H+c alphaS number or derivation.
- Ref45 of the AN is Butterworth et al., PDF4LHC RunII recommendations (arXiv1510.03865), cited in its general PDF paragraph. Ref18 is the internal particle-level H+c study AN2022/064. That second note is not present in the local References/HToWW inventory checked here; its section5 and/or actual Run2 datacards are the next decisive sources for the cH-specific alphaS treatment.
- The public CMS paper§6 describes up to6% PDF for cH without a dedicated cH alphaS rate value; that supports the documented PDF treatment but cannot prove no separate alphaS nuisance existed in the implementation.

### Correction: the old Run 3 flat3% has a recorded provenance

The initial source search focused on current notes and overstated the absence of any recorded source. The old3% **does** have documentary provenance, though no process-specific H+c alphaS calculation has been established:

- [[Projects/HToWW/combine-systematics/_history/lxplus-2026-06-17/bhive-docs/combine]], subsection "combine v2 — rate-only lnNs aligned with AN-23-102 (2026-05-13)", explicitly lists `alphaS_PDF`3% on allMC, sourced to **AN-23-102Table16, top of1–3%range**. It describes choosing a conservative range endpoint, not measuring or calculating a new H+c alphaS response.
- [[Projects/HToWW/analysis-strategy/2026-08-11-provenance-audit]]§B records the same1.03 value and flags flat application of the upper range endpoint to all processes.

Thus distinguish **Run2's documented6% H+cPDF**, **the generic Run2 table row**, and **our later Run3 flat3% interpretation**. Do not present the last as the actual Run2 H+c alphaS calculation, or treat6%PDF as including alphaS without further evidence. This corrects the earlier broad "source not recorded" wording; the remaining gap is applicability and a dedicated derivation. No physics value/config/code was changed and no jobs were launched.
