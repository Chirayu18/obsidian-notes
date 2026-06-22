---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# H+c → WW combine — full findings (v11 & v32, 2022postEE)

**What:** expected 95% CL upper limit on the H+c signal strength r, 2022postEE (26.7 fb⁻¹), 1POI,
blind Asimov, asymptotic CLs. Benchmark: **AN-23-102 Run-2 1POI expected limit = 505 @ 138 fb⁻¹**.
Full doc on EOS: `b-hive/docs/combine_findings_v11_v32.md`; systematics: `b-hive/docs/systematics_reference.md`.
Plots: see `plots.md` (`#plot` entries).

## 1. Headline results

| analysis | stat-only | full r₉₅ (median) | ±1σ | vs AN 505 |
|---|---|---|---|---|
| **v11** (6-class CE, argmax winner-score) | 771 | **1742** | 1175 / 2714 | 3.4× |
| **v32** (13-class kHCE, argmax-with-prior, log-L) | **584** | 1919 | 1302 / 2982 | 3.8× |
| **AN-23-102** (138 fb⁻¹) | ~330 | **505** | — | 1× |

**AN √L-scaled to our 26.7 fb⁻¹:** with-syst = 505·√(138/26.7) = **1148**; stat-only = 387·√… = **879**.
- v32 has the best **stat floor (584)**; v11 has the best **full limit (1742)** — v32's separation gain is
  eaten by larger systematic inflation (×3.27 vs ×2.24, tt-heavy SR).
- **Our stat-only bars (771, 584) BEAT the AN's scaled stat-only (879)** — statistically competitive.
  The whole gap is systematics.

## 2. Why scaling to AN lumi does NOT reach 505 (key result)

Naive √L scaling is **invalid** — we're systematics-limited. Split r₉₅ ≈ 1.64·σ_r:

| | σ_stat | σ_syst | r₉₅ | % stat |
|---|---|---|---|---|
| v11 @ 26.7 fb⁻¹ | 461 | **923** | 1742 | 20% |
| v11 scaled → 138 fb⁻¹ | 203 | **923** | **~1550** | 5% |
| AN @ 138 fb⁻¹ | 201 | **170** | 505 | ~60% |

σ_stat scales and **agrees with the AN** (461→203 ≈ 201). σ_syst is a **fractional floor — lumi-independent**
(stays 923), so v11 **plateaus at ~1550, never 505**. The entire residual gap is σ_syst: 923 vs 170 (×5.4),
untouched by luminosity. You are **80% systematics-limited**; the AN is **60% statistics-limited**.

## 3. What drives σ_syst — autoMCStats, not theory (freeze breakdown)

| frozen group | v11 r₉₅ | \|Δr\|/r | v32 |
|---|---|---|---|
| nominal | 1742 | — | 1919 |
| **MC-stat (autoMCStats)** | **1032** | **40.8%** | **42.3%** |
| signal theory (4FS5FS+PDF+αs+BR) | 1546 | 11.3% | 11.8% |
| Scale+PS | 1643 | 5.7% | 8.1% |
| Bkg-Higgs (ggH flavour) | 1725 | 1.0% | ~0 |
| lepton/JES/pileup/tt-norm/other | ~1740 | <0.4% | <5% |
| stat-only (all frozen) | 771 | — | 584 |

**MC statistics (Barlow-Beeston bin-by-bin) is 73% of the systematic inflation** — confirmed in the
CMS-style impact plots where the top nuisances are `prop_binSR_hplusc_bin5/6/7` (autoMCStats), above
ps_fsr/ggH-flavour/scalevar. vs AN Table 18: **our MC-stat 41% vs AN's 6.2%** (6.6× bigger), and our
**Bkg-Higgs ~1% vs AN's 21.4%** (their BDT kills tt → Higgs-bkg is their irreducible competitor; our SR is
tt-dominated so Higgs-bkg is 0.7%).

## 4. Same S/B, 5× the σ_syst — why

Integrated S/B is the same for both (~10⁻⁵; AN's is even worse). But **σ_syst is a *shape* quantity, not
set by integrated S/B.** Signal as a sharp spike in a low-background tail bin (AN) → smooth systematics
can't fake it → small σ_syst. Signal smeared *under the background peak* (us — v11 SR signal peaked in bins
8–10 exactly where background peaked) → background shape/MC-stat moves under the signal → large σ_syst.
Same fact = the stat shape-gain (AN ×2.6 vs our ×1.18) and σ_syst (170 vs 923): both measure **signal
localization**, which integrated S/B is blind to.

## 5. Tested and ruled out (dead ends)

| attempt | result |
|---|---|
| tt rateParam from CR_tt (35k tt, ~1.2% constraint) | **worse** (floating norm ±36 SR events ≫ 0.2 signal) |
| top-group rateParam {tt,st} | worse |
| coarser binning (4 bins) | **worse** (2042) |
| tail-merge / finer binning | null / worse — MC-stat is distributed, not one bin |
| LOWESS smoothing of *variations* | null — autoMCStats is from the *nominal* sumw² |
| discriminant/collapse (kappa-D, LR, argmax-prior, P(hplusc)) | all a wash (shape Z ≈ 0.005) |

**tt is OVER-constrained:** postfit `rate_tt = 1.000 ± 1.2%` vs AN's 0.77–0.91 ± ~5%. Tighter because we
dropped tt theory + lack c-tag + one combined CR; sits at 1.0 because blind Asimov (data≡MC) can't see the
AN's real ~15% tt over-prediction. The tt CR has 3.18M raw tt events → constraint is *not* the issue; even
a perfect 0.5% constraint leaves ±36 SR tt events ≫ the 0.2 signal (S/B-limited, not constraint-limited).

## 6. Actual fixes (leverage order)

1. **Cross-era MC template averaging** (AN §6.1/7.2.1): build bkg templates from all eras' MC → smaller
   autoMCStats. Headroom: freeze-autoMCStats = 1032, so ~1742 → ~1300–1400. **Highest leverage, uses
   existing MC, no retraining.**
2. **Smooth the *nominal* templates** (+ bin errors from merged template) — the piece variation-smoothing missed.
3. **Better localization** (multi-category + k-means yield-balanced binning) — shrinks σ_syst.
4. **Luminosity** — only the ~20% statistical floor.
5. Irreducible: signal 4FS/5FS theory (~11%) — shared with the AN.

## 7. v32 specifics (13-class kappa-HCE, v9 model)

- Model `hwwcom_kappahce_v32_v9`. Final-layer cosine auto-grouping:
  - **Higgs cluster (+cos to signal):** ggH +0.74, hplusb +0.69, vbf +0.66, zh +0.60, wh +0.46, ggzh +0.39
  - **Top cluster (−cos):** tt −0.77, st −0.82, **tth −0.2/−0.3 (clusters with top, NOT Higgs)**
  - diboson ≈ 0; vjets +0.52 (near Higgs cluster)
- **Channelization = argmax-with-prior** (collapse 13→6, route by argmax(Pᵢ/priorᵢ), D = log10(P(hplusc)/prior)).
  Replaces the cascade+T_opt+adaptive-binning hack, fills all 6 CRs. Raw 13-class argmax never picks the
  signal (P tiny) → need the prior.
- **Discriminant collapse is a wash:** kappa-D, soft-kappa, LR-vs-top, P/prior, P(hplusc) all give shape
  Z ≈ 0.0050 (κ_tt=0 so tt isn't suppressed).

## 8. Bottom line

S/B, the classifier, the discriminant, the binning, and the tt constraint are **not** the problem (all
tested). You are **systematics-floored at ~1550 regardless of lumi**, dominated by **MC statistics**
(reducible via cross-era template averaging) on top of an irreducible signal-theory floor — and
structurally by weaker **signal localization** than the AN's multi-category BDT. Your statistical floor is
genuinely competitive with (better than) the AN's at equal lumi.
