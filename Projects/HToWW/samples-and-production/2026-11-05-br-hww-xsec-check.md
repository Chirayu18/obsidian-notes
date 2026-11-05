---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---

# BR(H→WW), WH cross sections and H+c NNLO normalisation: check against primary sources

Task HTOWW-BR-HWW-CHECK, asked for by Chirayu on 2026-11-05 ("Spawn a agent to check this"). The
consumer is the FULLFIX worker ([[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|2026-11-05-fullfix-rerun-run-a-state]]).
This was a read-only check: nothing in the higgscharm repo was changed. All arithmetic is
**agent-computed** with `python3`. The BR values were read directly from the sources listed below.

## Sources read
- **LHCHWG BR twiki**, `https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR`, "SM Higgs Branching Ratios and Total Decay Widths (update in CERN Report4 2016)", revision r23 (2023-12-21). Fetched 2026-11-05.
- **CERN Yellow Report 4**, arXiv:1610.07922v2, Appendix A "Tables of branching ratios". Table 176 (H→gg, H→γγ) is on PDF page 698. Table 177 (H→Zγ, H→WW) is on PDF page 699.
- **LHCHWG-2024-001**, arXiv:2402.09955, Table 3: "WH cross sections at the LHC at 13.6 TeV … pp → WH (NNLO QCD + NLO EW)".
- **LHCHWG-2026-007**, arXiv:2608.26863, Table 3 (p. 18), §4 (setup), §5.3. Local copy: `References/HToWW/2026-LHCHWG-2026-007_Hc_flavour_schemes_arXiv2608.26863.pdf`.
- **Pythia 8.311 default decay table**, `/cvmfs/cms.cern.ch/el9_amd64_gcc12/external/pythia8/311-e8371124d820e9d028397ca36ea65b12/share/Pythia8/xmldoc/ParticleData.xml`, particle id 25. Read on lxplus.

## 1. BR(H→WW) and BR(H→γγ)

The YR4 PDF and the twiki give the same values.

| mH [GeV] | BR(H→WW) | BR(H→γγ) | source row |
|---|---|---|---|
| 125.00 | **2.137E-01** | **2.270E-03** | YR4 Tables 177 / 176, row "125.0"; twiki "Higgs → 2 gauge bosons" tables, row "125.00" |
| 125.09 | **2.152E-01** | **2.270E-03** | YR4 Tables 177 / 176, row "125.09"; twiki, row "125.09" |

- **0.2152 is the mH = 125.09 value.** The worker paired it with the LHCHWG-2024-001 Table 3 cross sections at mH = 125.09, so that set is mass-consistent.
- BR(γγ) is the same, 2.270E-03, at both masses.
- For reference, the twiki "H → llll, lνlν" table gives BR(H→ℓνℓν) with ℓ = e, μ, τ: 2.338E-02 at 125.00 and 2.354E-02 at 125.09. These are higher than BR(WW) × 0.3258² = 0.02268 / 0.02284. The likely reason is that the 4-fermion table also includes ZZ→ℓℓνν and interference; that explanation is not checked. **Do not use them as BR(WW) × BR(W→ℓν)².**

LHCHWG-2024-001 Table 3, the W±H rows used below:

| mH | σ(WH) [pb] | W⁺H [pb] | W⁻H [pb] |
|---|---|---|---|
| 125 | 1.457 | 0.8889 | 0.5677 |
| 125.09 | 1.453 | **0.8870** | **0.5664** |

## 2. Per-sample WH cross sections

Formula: σ(W±H) × BR(H→WW) × BR(W→ℓν)² × BR(W_assoc). The inputs are BR(W→ℓν) = 0.3258 (ℓ = e, μ, τ), so BR(W→ℓν)² = 0.106146, and BR(W→qq) = 0.6741. These two W branching fractions were taken from the task brief. I did not re-fetch them from the PDG.

| sample | current | 125.09 consistent (0.2152) | Δ | 125.00 consistent (0.2137) | Δ | mixed: σ@125.09 × BR@125.00 | Δ |
|---|---|---|---|---|---|---|---|
| `WminusH_WtoLNu_Hto2Wto2L2Nu` | 0.004215 | 0.004215 | +0.01% | 0.004195 | −0.46% | 0.004186 | −0.69% |
| `WplusH_Wto2Q_Hto2Wto2L2Nu` | 0.013659 | 0.013658 | −0.01% | 0.013592 | −0.49% | 0.013563 | −0.70% |
| `WplusH_WtoLNu` | 0.006625105011 | 0.006601 | **−0.36%** | 0.006569 | **−0.84%** | 0.006555 | −1.06% |
| `WminusH_Wto2Q` | 0.008719124529 | 0.008722 | +0.03% | 0.008681 | −0.44% | 0.008661 | −0.67% |

- The two new values, 0.004215 and 0.013659, are exactly the mH = 125.09 consistent set.
- Changing to a consistent mH = 125.00 set lowers all four by −0.44% to −0.49%. That is just under 0.5% for the new values and `WminusH_Wto2Q`. For `WplusH_WtoLNu` the change is **−0.84%**, which is over 0.5%, because that value already sits 0.36% above the 125.09 set.
- The two older high-precision values, 0.006625105011 and 0.008719124529, do not come out of either consistent set. I could not find where they came from; they predate the 2026-08-12 audit ([[Projects/HToWW/samples-and-production/2026-08-12-postEE-background-audit-vs-AN|2026-08-12-postEE-background-audit-vs-AN]]). The FULLFIX note says they "agree with these to within 0.3%". The correct figure is **0.36%** for `WplusH_WtoLNu` and 0.03% for `WminusH_Wto2Q`.
- The 125.00 rows apply only if the analysis moves to mH = 125.00 throughout. The mixed column is what you get by using σ at 125.09 with BR(WW) = 0.2137. It is the only combination that moves the values by more than 0.5% for every sample, and it should be avoided.
- **Recommendation:** keep the 125.09 set as it is. Optionally, set `WplusH_WtoLNu` to 0.006601 for consistency (−0.36%).

## 3. H+c NNLO normalisation (LHCHWG-2026-007)

LHCHWG-2026-007 Table 3 (p. 18): "Integrated cross sections [fb] for pp → H(γγ)cc̄ production at 13.6 TeV, including the Higgs boson branching factor". No cuts column:

| row | σ×BR(γγ) [fb] |
|---|---|
| MINNLOPS (4FS) | 0.1664 (+4.4% / −2.7%) |
| NLO (4FS) | 0.2216 (+10.2% / −7.0%) |
| NLO (3FS) | 0.1248 |
| NLO+bbHfact (4FS) | 0.1690 |
| NLO+bbHfact (3FS) | 0.1630 |

**Which BR(γγ) the paper used: it does not say.**
- The paper says only "In all simulations PYTHIA is used to decay the Higgs boson to a pair of photons" (§4) and gives mH = 125 GeV (§4, parameter list). No numerical BR(γγ) appears anywhere in the text.
- Two readings are possible:

| assumed BR(γγ) | NLO 4FS inclusive σ | MINNLOPS 4FS inclusive σ |
|---|---|---|
| YR4, 2.270E-03 (same at 125.00 and 125.09) | 97.62 fb | **73.30 fb** |
| Pythia 8.311 default, 0.0028438 | 77.92 fb | 58.51 fb |

**Does 0.0022141 pb match NLO 4FS?** Yes, if the YR4 BRs at mH = 125.00 are used:
- 0.0022141 / (0.2137 × 0.106146) = **97.61 fb**, against 97.62 fb for NLO 4FS. The two agree to 0.01%.
- With BR(WW) = 0.2152, the implied value is 96.93 fb, 0.7% off.
- Read the other way, NLO 4FS 97.62 fb × 0.2137 × 0.106146 = 0.0022144 pb.
- So the current central sample xsec is the LHCHWG NLO 4FS value, at mH = 125 with YR4 BRs.
- This is an inference: the 0.0022141 value predates the paper (it is already in [[Projects/HToWW/combine-systematics/2026-07-24-systematics-master-list|2026-07-24-systematics-master-list]] §2c, which credits it to the `amcatnloFXFX` sample). It probably comes from the same group's calculation, presented in Bevilacqua's 23-06-26 talk. It is not verified against the sample's GenXSecAnalyzer output.
- Unresolved: the Table 3 row is labelled "NLO (4FS)". The text of §5.3 compares "4FS with FxFx merging" without saying clearly whether this row is FxFx-merged. The earlier note ([[Projects/HToWW/samples-and-production/flavour-schemes/2026-09-29-fs-3FS-4FS-status|2026-09-29-fs-3FS-4FS-status]]) read it as FxFx.

**Absolute NNLO σ × BR(H→WW→2ℓ2ν)**, using the YR4 BR(γγ):

| BR(WW) used | NNLO σ×BR(WW→2ℓ2ν) [pb] |
|---|---|
| 0.2137 (mH = 125.00, the paper's mass) | **0.0016628** |
| 0.2152 (mH = 125.09; mixes the paper's 125 with 125.09) | 0.0016744 (+0.7%) |

**Ratio method:** 0.1664 / 0.2216 = **0.75090**, and 0.0022141 × 0.75090 = **0.0016626 pb**. The worker's numbers are confirmed.

**Recommendation: use the ratio method, giving 0.0016626 pb.**
- The unknown BR(γγ) cancels exactly in the ratio, because both rows share the same decay, the same mH = 125 and the same Pythia setup.
- The ratio also keeps whatever BR(WW) convention is already built into 0.0022141.
- It agrees with the consistent absolute value (mH = 125.00, YR4) to 0.01%.
- The absolute route depends on assuming YR4 BR(γγ). With the Pythia 8 default it would be about 20% lower (0.0013389 pb using Pythia's BR(WW) = 0.2155720). It also invites the +0.7% mass mix if BR(WW) = 0.2152 is used.
- If an absolute value is ever quoted, quote 0.0016628 pb (mH = 125.00), not 0.0016744 pb.
- Caveat: the MINNLOPS 4FS cross section is NNLO for the y_c² ccH term only. Whatever normalisation the analysis adopts still needs Chirayu's decision 6 ("we use NNLO normalisation now", 2026-11-04) applied. The scale uncertainty of the stitched sample replaces the dropped 30% lnN.

## Status
- **Recorded and agent-computed. Not validated.** Nothing has been implemented in the repo.
- Reproduce: the BR rows come from `pdftotext -layout` of arXiv:1610.07922v2 (grep `^125.0[9 ]`) and from the twiki HTML tables. The arithmetic is in the formulas above.
