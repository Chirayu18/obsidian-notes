---
tags: [reference, draft]
status: active
date: 2026-10-13
source: lxplus
---

# DRAFT: GEN ticket for the central H+c / H+b → WW (FxFx) samples

> Draft only, not sent. Addressees: Sebastiano Quinto (HIG/HWW GEN contact) and the GEN conveners. It could be filed on the mccm issue (cms-gen/mccm#1235 and the HPlusB issue) or as a cms-gen/genproductions_scripts issue, with a pointer to the other.
> Figures: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/ticket

---

**Title:** Central H+c/H+b → WW 4FS/5FS FxFx samples (Run3Summer22/22EE/23/23BPix): broken LHE scale/PDF weights and a misconfigured FxFx merging

Hi Sebastiano, dear GEN conveners,

While validating the central H+c → WW signal samples (requests from cms-gen/mccm#1235 and the HPlusB requests; gridpack cards in cms-gen/genproductions_cards!93) against the central H+c → γγ sample and the Run 2 UL18 H+c → WW sample, we found two independent problems. Both trace back to the production setup, not to the physics cards. The cards themselves (same as the Run 2 `HPlusHF` cards) are fine.

## Affected requests

| sample | era | GEN request |
|---|---|---|
| HPlusCharm-4FS…HToWWTo2L2Nu…amcatnloFXFX | 2022 | HIG-Run3Summer22wmLHEGS-02684 |
| | 2022postEE | HIG-Run3Summer22EEwmLHEGS-02600 |
| | 2023BPix | HIG-Run3Summer23BPixwmLHEGS-02468 |
| HPlusBottom_5FS…HToWWTo2L2Nu…amcatnloFXFX | 2022 | HIG-Run3Summer22wmLHEGS-02697 |
| | 2022postEE | HIG-Run3Summer22EEwmLHEGS-02645 |
| | 2023 | HIG-Run3Summer23wmLHEGS-03356 |
| | 2023BPix | HIG-Run3Summer23BPixwmLHEGS-02517 |

Reference (correct) sample: HIG-Run3Summer22EEwmLHEGS-01159 (HPlusCharm_4FS…HTo2G…amcatnloFXFX).

## Problem 1: LHE scale and PDF weights miss the running-Yukawa factor

- **Symptom** (Fig. 1):
  - Every scale variation of H+c → WW is about ×2 the nominal, in both directions (μR×0.5 1.89, μR×2 2.38 inclusive).
  - The mean of the PDF replicas over member 0 is about 2.26 per event, instead of 1.
  - Member 0 and the (1,1) scale weight equal the nominal. The nominal itself is correct.
  - H+c → γγ and Run 2 H+c → WW have r = 0.999 and variations of a few percent.
- **Cause:**
  - The `_mg5amc.patch` in the HPlusHF card set implements the MS-bar running charm (bottom) Yukawa in `rwgt_muR_dep_fac` (`reweight_xsec.f`), i.e. inside MG5_aMC's Fortran event-by-event reweighting.
  - The current `genproductions_scripts` master NLO workflow (`Utilities/gridpack_helpers.sh: prepare_run_card`) appends `reweight_scale = False`, `reweight_PDF = False`, `store_rwgt_info = True`, and `runcmsgrid_NLO.sh` computes the weights with the python `systematics` module.
  - That module does not know about the patched factor, so all variations miss (m_c(μR)/m_c,in)² ≈ 0.44 (event-dependent).
  - The official H+c → γγ gridpacks avoid this with a manual, sample-specific change in their runcmsgrid (`SAMPLE-SPECIFIC CHANGE to runcmsgrid_NLO.sh --> Skipping execution of "./bin/aMCatNLO systematics .."`), and keep `reweight_scale/PDF = True`, `store_rwgt_info = False`. That change lives only inside the tarball, not in the cards. So following the standard instructions with the same cards reproduces the bug.
- **Proposed fix:** for samples carrying an `rwgt_muR_dep_fac` patch (HPlusHF, and any other process using it), the master NLO workflow should:
  - not append those three lines;
  - fill the PDF placeholders with `reweight_PDF = True`;
  - not run the `systematics` module.

  This reproduces the official γγ run cards exactly (4FS: lhaid 325500, maxjetflavor 4; 3FS: 321900, maxjetflavor 3). Ideally master would detect such patches automatically, or at least document the incompatibility.

## Problem 2: FxFx merging misconfigured in the request fragment

- **Symptom** (Figs. 2, 4):
  - In H+c → WW, one-jet (H+j Born) events with the leading parton at |η| > 2.5 are 7× rarer than in γγ and Run 2: 0.98% vs 6.8% / 6.6% of all events.
  - Zero-jet events with a hard parton (pT > qCut = 30 GeV) at |η| > 2.5, which the FxFx veto should remove, are 10× more frequent: 1.9% vs 0.16% / 0.19%.
  - Central events agree. The event-class mix shifts accordingly (0-jet 80% vs 73%).
- **Cause:**
  - The fragments of all seven GEN requests above lack three lines that the γγ fragment (HIG-Run3Summer22EEwmLHEGS-01159), the Run 2 UL18 WW fragment and CMSSW's standard FxFx hadronizer configuration all contain:

    ```
    'JetMatching:jetAlgorithm = 2',
    'JetMatching:etaJetMax = 999.',
    'JetMatching:coneRadius = 1.',
    ```

  - Without them Pythia uses its defaults: CellJet, etaJetMax = 2.5, coneRadius = 0.7. For the MadGraph scheme only particles within etaJetMax enter the merging, so the FxFx veto acts only on the central region.
  - Confirmed in the MiniAOD provenance of all three H+c eras and in the McM fragments of all seven requests (decoded copies in `ticket/mcm_fragments/`).
  - All other merging and shower settings are identical to the γγ sample (qCut 30, qCutME 10, nJetMax 1, nQmatch, pTmaxMatch, global recoil, …).
- **Proposed fix:** add the three lines to the fragments.

## Impact

- **Problem 1** can be corrected per event in the analysis. The patch's own running is used to restore the factor, and it agrees with the clean samples to ≲1% for events with the same kinematics. A re-production would make the correction unnecessary.
- **Problem 2** cannot be corrected: events vetoed (or not vetoed) at the shower step cannot be restored by reweighting.
  - Even after correcting the weights, the normalised scale-variation shapes differ from both clean references by 1–5%, which is significant with 3M events (Fig. 3).
  - With the references reweighted to our event mix, the remaining difference sits in the one-jet H-event class (Fig. 5).
  - Forward-jet modelling and the nominal 0/1-jet composition are affected.

## Request

1. Re-produce the H+c and H+b → WW samples with
   - (a) the gridpack rebuilt from the same cards without the python systematics step (I can rebuild both gridpacks on el8 as before), and
   - (b) the fragments completed with the three JetMatching lines.
2. Consider guarding the master NLO workflow against `rwgt_muR_dep_fac` patches. Other processes with a running-Yukawa patch (e.g. bbH) may be affected too.
3. Check other FxFx fragments derived from the same template for the missing JetMatching lines.

Before submitting, we propose validating a small test sample against the γγ reference:
- r ≈ 1;
- 1-jet share ≈ 27% and forward 1-jet share ≈ 6.7%;
- ≈1.4% of one-jet H-events at MG's 1 GeV scale floor, with constant μR×0.5 = 6.199.

I'm happy to provide the gridpacks, scripts and more details.

Best regards,
Chirayu

---

### Figures (attach)
1. `fig1_weights.png`: per-event mean(PDF replicas)/member 0, and the inclusive scale-variation ratios (raw NanoAOD; WW vs γγ vs Run 2).
2. `fig2_merging_eta.png`: |η| of the leading LHE parton, for 1-jet events and for 0-jet events with a parton pT > 30 GeV.
3. `fig3_scale_shape_higgs_pt.png`: normalised scale-variation shapes vs Higgs pT after the weight correction (3M events each, jackknife errors).
4. `fig4_nominal_comparison.png`: nominal event-class mix, Higgs pT, jet scale and c-jet pT.
5. `fig5_mixmatched_class.png`: per-class shapes with the references reweighted to our mix.

### Notes for me (not for the ticket)
- **H+b:** fragments verified (all four lack the lines). The weight offset was seen earlier with the same pattern, but the H+b gridpack's runcmsgrid/run_card has not been inspected directly. Check it before sending.
- **Scope of the evidence:** the η test and the weight figures use 2022postEE files. The provenance check covers 2022, 2022postEE and 2023BPix.
- **Fig. 3 caveat:** the reference curves include their own small (~2σ) disagreements. γγ vs Run 2 is shown as grey pulls in the high-stat plots.
