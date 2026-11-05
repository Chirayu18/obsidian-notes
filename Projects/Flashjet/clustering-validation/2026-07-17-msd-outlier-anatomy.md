---
tags: [reference]
status: active
date: 2026-07-17
source: lxplus
---

# m_SD outlier anatomy — why 4.4% of jets differ by >0.5 GeV (and why that's NanoAOD, not us)

Context: after the raw-to-raw + C/A-tree fixes, flashjet reproduces CMS `FatJet_msoftdrop`
with median Δ = −0.004 GeV, but ~4.4% of jets sit outside |Δm| > 0.5 GeV. This note
documents the full attribution (scripts: `outliers.py` → HTCondor 9098953,
`analyze_outliers.py`, `analyze_outliers2.py`, `rerun_rest.py`, `make_outlier_plot.py`,
all in `/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`).

## The setup

QCD JMENano, 20 000 events → 19 695 tagged jets. Nominal pass + two "precision
bootstrap" passes (every constituent multiplied by (1+ε), ε ~ U(−u/2, u/2) with u =
one ulp of the measured storage precision), plus 200 jitter replicas of the
*reference* m(raw SubJet1+SubJet2).

**Measured storage precision** (trailing-zero mantissa bits, `qcd_jmenano_150x.root`):

| branch | eff. mantissa | rel. precision |
|---|---|---|
| `PFCand_pt` / `PFCand_mass` | ~9–10 bits | ~1×10⁻³ |
| `PFCand_eta` / `PFCand_phi` | ~11–12 bits | ~2×10⁻⁴ |
| `SubJet_pt` / `SubJet_mass` | ~9 bits | ~1×10⁻³ |
| `SubJet_rawFactor` | **~5 bits** | **~2×10⁻²** |

CMS ran FastJet on **full-precision** candidates; we can only ever see the rounded ones.

## Attribution of the 867 outliers

1. **50% — soft constituents missing from `FatJetPFCand`** (the dominant, one-sided part).
   The stored table has an effective **~0.1 GeV weighted-pt floor** (min linked
   `PFCand_pt` = 0.094 GeV; 1st percentile 0.30 GeV). CMS's SoftDrop clustered the
   *uncut* PUPPI list. Mass is quadratically sensitive to a lost soft wide-angle
   candidate (δm² ≈ p_T^jet · p_T^lost · ΔR²: 0.5 GeV at ΔR=0.6 in a 500 GeV jet ⇒
   δm ≈ 0.5 GeV at m=95) while jet p_T moves only ~10⁻⁴ — which is exactly why p_T
   matches "exactly" but m_SD grows a small one-sided tail. **Proof** (`rerun_rest.py`):
   this population's groomed vector p_T sits below the subjet-pair p_T (median
   −0.43 GeV vs −0.04 for core), corr(δp_T, Δm) = 0.42, median Δm² = 127 GeV²,
   and 94% have Δm < 0 (our mass low).
2. **23% — within 3σ of storage rounding** (per-jet σ from SubJet-branch jitter ⊕
   constituent jitter).
3. **20% — rounding-sensitive C/A trees**: a half-ulp input jitter moves their groomed
   mass appreciably (bimodal "tree flip", not Gaussian; a soft branch migrates between
   kept/dropped prongs, moving m at ~1% while z_g/R_g barely change).
4. **7% — genuine prong flips** near the threshold (|z − z_cut| small; 14× enriched
   over core, where the different-prong rate is only 0.5%).

## The right way to state the agreement

- The fixed 0.5 GeV window mostly selects **high-mass jets** (outlier median m = 105 GeV
  vs core 29 GeV). The **relative** agreement is flat: median |Δm|/m ≈ **0.08–0.15%
  in every mass bin**; the "outlier rate" rises with m only because the cut is absolute.
- Median signed offset −0.004 GeV; 95.6% within 0.5 GeV; core scatter fully consistent
  with the storage-noise bootstrap.

## Verdict

There is **nothing to fix in flashjet**: the residual tail is a property of the NanoAOD
inputs (constituent-table floor + reduced-mantissa storage), not of the clustering or
grooming. The only "fix" would need inputs CMS doesn't store (full-precision, uncut
PUPPI candidates — i.e. MiniAOD `packedPFCandidates` + per-candidate PUPPI weights).
Plot: `outlier_anatomy.png` (in the deck as "CMS (2b)").
