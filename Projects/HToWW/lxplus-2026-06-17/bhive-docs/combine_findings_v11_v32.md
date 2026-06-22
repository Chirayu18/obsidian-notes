---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# H+c → WW combine: full findings (v11 & v32, 2022postEE)

**Scope:** expected 95% CL upper limit on the H+c signal strength r, 2022postEE (26.7 fb⁻¹), 1POI
(r_hplusc floats, Higgs background fixed to SM). Blind Asimov, asymptotic CLs
(`AsymptoticLimits --run blind -t -1`, median = "Expected 50%"). Benchmark: **AN-23-102 Run-2
1POI expected limit = 505 @ 138 fb⁻¹**.

Figures: `docs/plots/combine_final/{limit_comparison,likelihood_scan,impacts_v11,impacts_v32,breakdown_vs_AN}.png`.
Raw results: `combine_inputs/results/{v11,v32}/`.

---

## 1. Headline results

| analysis | stat-only | **full r₉₅ (median)** | −1σ / +1σ | −2σ / +2σ | vs AN 505 |
|---|---|---|---|---|---|
| **v11** (6-class CE, argmax winner-score) | 771 | **1742** | 1175 / 2714 | 857 / 4227 | 3.4× |
| **v32** (13-class kHCE, argmax-with-prior, log-L) | **584** | **1919** | 1302 / 2982 | 944 / 4587 | 3.8× |
| **AN-23-102** (138 fb⁻¹) | ~330 | **505** | — | — | 1× |

**AN √L-scaled to our 26.7 fb⁻¹:** with-syst = 505·√(138/26.7) = **1148**; stat-only = 387·√(138/26.7) = **879**.
Note: our **stat-only bars (771, 584) beat the AN's scaled stat-only (879)** — our statistical floor is
competitive — but our **with-syst bars (1742, 1919) are far above the AN's scaled with-syst (1148)**.
The whole gap is the systematic inflation. (See `limit_comparison_4bar.png`.) The CMS-style impact plots
(`impacts_cms_{v11,v32}.png`) make the cause explicit: the **top-ranked nuisances are `prop_binSR_hplusc_*`
(autoMCStats), not theory** — MC statistics dominates the impacts.

- **v32 has the best statistical floor (584, 1.3× better than v11)** — the 13-class kappa-HCE model + argmax-with-prior + log-likelihood discriminant genuinely separates better.
- **v11 has the best full limit (1742)** — v32's separation gain is *more than eaten* by a larger systematic inflation (×3.27 vs ×2.24), because its argmax-prior SR is tt-dominated.
- Both are systematics-dominated; neither beats v11 v3's earlier 1693 by much.

---

## 2. Why scaling to AN lumi does NOT reach 505 (the key result)

Naive √L scaling (1742 × √(26.7/138) = 766) is **invalid** — it assumes pure statistics. Split
r₉₅ ≈ 1.64·σ_r, σ_r² = σ_stat² + σ_syst²:

| | σ_stat | σ_syst | r₉₅ | % statistical |
|---|---|---|---|---|
| **v11 @ 26.7 fb⁻¹** | 461 | **923** | 1742 | **20%** |
| **v11 scaled → 138 fb⁻¹** | 203 | **923** | **~1550** | 5% |
| **AN @ 138 fb⁻¹** | 201 | **170** | 505 | ~60% |

- **σ_stat scales and agrees with the AN** (461 → 203 ≈ 201). The statistical physics is identical.
- **σ_syst is a fractional floor — lumi-independent.** It stays 923 at any luminosity, so v11 **plateaus at ~1550**, never reaching 505.
- **The entire residual gap is σ_syst: 923 (you) vs 170 (AN), ×5.4** — untouched by luminosity.

You are **80% systematics-limited**; the AN is **60% statistics-limited** (their Table 18). More
luminosity barely helps you (1742 → ~1550); the lever is **σ_syst**.

---

## 3. What drives σ_syst — autoMCStats, not theory (v11 freeze breakdown)

| frozen group | r₉₅ | \|Δr\| | \|Δr\|/r |
|---|---|---|---|
| nominal | 1742 | — | — |
| **MC-stat (autoMCStats)** | **1032** | **710** | **40.8%** |
| signal theory (cH/bH: 4FS5FS+PDF+αs+BR) | 1546 | 196 | 11.3% |
| Scale+PS | 1643 | 99 | 5.7% |
| Bkg-Higgs (ggH flavour + xsec) | 1725 | 17 | 1.0% |
| JES/JER, lepton, pileup, tt-norm, other-bkg | ~1740 | ≤6 | <0.4% |
| **stat-only (all frozen)** | **771** | — | — |

**MC statistics (bin-by-bin Barlow-Beeston) is 73% of the systematic inflation.** Versus AN Table 18:

| source | **you (v11)** | AN (Table 18, 1POI) |
|---|---|---|
| MC-stat | **40.8%** | 6.2% |
| signal theory (cH/bH) | 11.3% | 22.1% |
| Bkg-Higgs | ~1.0% | 21.4% |
| JES/JER | 0.1% | 6.0% |
| charm-tag | **absent** | 5.9% |
| tt-norm | 0.1% | 5.6% |

Two structural differences:
1. **Your MC-stat is 6.6× the AN's** and dominates — because the 0.17-event signal sits where the
   background MC is thinnest (high-discriminant tail), so any per-bin MC-stat (~2-3%) = tens of events ≫ signal.
2. **Your Bkg-Higgs is ~1% vs the AN's 21.4%** — their BDT kills tt, leaving the Higgs background
   (and its 50% ggH-flavour theory) as the irreducible competitor; **your SR is tt-dominated** (Higgs bkg
   is only 0.7% of it), so that theory is negligible for you. Same root cause — *localization* — seen in the
   systematic budget's shape.

---

## 4. Why same S/B but 5× the σ_syst

Integrated S/B is the same for both (~10⁻⁵, AN's is even worse). But **σ_syst is a shape quantity,
not set by integrated S/B.** Same total S and B, two layouts:
- **AN:** signal a sharp spike in a tail bin where background is tiny → smooth background systematics
  can't fake a spike → small σ_syst.
- **You:** signal spread *under the background peak* (v11 SR peaked in bins 8–10 exactly where the
  background peaked) → background shape/MC-stat moves right under the signal → fakes it → large σ_syst.

Same fact appears in the stat shape-gain (AN ×2.6 over counting vs your ×1.18) and σ_syst (170 vs 923) —
both measure signal **localization**, which integrated S/B is blind to.

---

## 5. What was tested and ruled out (dead ends)

| attempt | result |
|---|---|
| tt rateParam from CR_tt (35k tt, ~0.5–1.2% constraint) | **worse** (floating norm ±36 SR events ≫ 0.2 signal) |
| top-group rateParam {tt,st} | worse, same reason |
| coarser binning (4 bins) | **worse** (2042) — lost resolution, didn't even remove starved bin |
| tail-merge (8 bins) | null (1745) — the MC-stat isn't one bin, it's distributed |
| finer binning | predicted worse (more bins → worse autoMCStats) |
| LOWESS smoothing of systematic variations | null (1742→1742) — autoMCStats is from the *nominal* sumw², not the variations |
| discriminant/collapse (kappa-D, likelihood-ratio, argmax-prior, P(hplusc)) | all a wash (shape Z ≈ 0.005) |

**tt is *over*-constrained, not under:** measured postfit `rate_tt = 1.000 ± 1.2%` vs AN's
0.77–0.91 ± ~5%. Mine is tighter because I dropped tt theory + lack c-tagging + use one combined CR;
and it sits at 1.0 because a blind Asimov fit (data≡MC) can't see the AN's real ~15% tt over-prediction.

---

## 6. The actual fixes (in leverage order)

1. **Cross-era MC template averaging** (AN §6.1/7.2.1): build background templates from all eras'
   MC (postEE+preEE+2023) → more effective stats/bin → smaller autoMCStats. Headroom: freeze-autoMCStats
   = 1032, so ~1742 → ~1300–1400. Highest-leverage, uses existing MC, no retraining.
2. **Smooth the *nominal* templates** (+ take bin errors from the merged template) — the piece the
   variation-smoothing missed.
3. **Better localization** (multi-category + k-means yield-balanced binning) — shrinks σ_syst by
   concentrating signal where background (and its systematic) is small. The AN's structural advantage.
4. **Luminosity** — only attacks the statistical floor (the smaller, ~20% part for you).
5. **Irreducible:** signal 4FS/5FS theory (~11%) — shared with the AN, leave it.

---

## 7. v32 specifics (13-class kappa-HCE, v9 model)

- **Model:** `hwwcom_kappahce_v32_v9`. Final-layer cosine structure (auto-grouping):
  - **Higgs cluster (+cos to signal):** ggH +0.74, hplusb +0.69, vbf +0.66, zh +0.60, wh +0.46, ggzh +0.39
  - **Top cluster (−cos):** tt −0.77, st −0.82, **tth −0.2/−0.3 (clusters with top, NOT Higgs)**
  - diboson ≈ 0 (orthogonal); vjets +0.52 (sits near Higgs cluster)
- **Channelization:** argmax-with-prior (user's suggestion) — collapse 13→6, route by argmax(Pᵢ/priorᵢ),
  SR discriminant D = log10(P(hplusc)/prior). Replaces the cascade+T_opt+adaptive-binning hack and fills
  all 6 CRs. Raw argmax never picks the signal in 13-class (P tiny); the prior fixes that.
- **Discriminant collapse is a wash:** kappa-D (κ=max(0,cos)), soft-kappa, LR-vs-top, P/prior, P(hplusc)
  all give shape Z ≈ 0.0050 — the cosine-weighted denominators don't beat plain P(hplusc) (κ_tt=0 so tt
  isn't suppressed).
- **Result:** best stat floor (584) but worse full limit (1919); systematic inflation ×3.27 (tt-heavy SR).

---

## 8. Pipeline / files

- v11: `higgscharm/scripts/combine/make_combine_inputs.py` + `analysis/workflows/hww_combine_fixed.yaml`
  (`combine:` block) → `outputs/combine/v11_hplusc_v4.{txt,root}`.
- v32: `b-hive/scripts/make_combine_histograms_v11_v32.py` (v9 model, argmax-prior, flooring, smoothing
  flag) + `make_datacard_v11_v32.py` → `b-hive/combine_inputs/v11_hplusc_v32_v9.{txt,root}`.
- Results driver: `b-hive/scripts/combine_full_results.sh`; plots: `b-hive/scripts/plot_combine_final.py`.
- Earlier v11-only write-up: `docs/combine_v11_study.md`.

**Bottom line:** S/B, the classifier, the discriminant, the binning, and the tt constraint are **not**
the problem (all tested). You are **systematics-floored at ~1550 regardless of lumi**, dominated by
**MC statistics** (reducible via cross-era template averaging) on top of an irreducible signal-theory
floor — and structurally by weaker **signal localization** than the AN's multi-category BDT.
