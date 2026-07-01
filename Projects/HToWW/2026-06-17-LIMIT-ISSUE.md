---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# H+c → WW — THE LIMIT ISSUE (read this first)

Self-contained summary of *why our combine limit is worse than AN-23-102* and what is/isn't the fix.
Full detail: [[2026-06-17-combine-v11-v32-findings]], [[2026-06-17-systematics-reference]].
**Root cause nailed (2026-06-23):** [[2026-06-23-automcstats-rootcause]] — autoMCStats = DY (vjets) SR undersampling (freeze SR autoMCStats: 1742→1069); + xsec/sumw audit (TbarBQ/TBbarQ xsec=0 bug).
Plots: [[combine-plots]]. Benchmark paper: `References/HToWW/AN-23-102.pdf`.

## The numbers (2022postEE, 26.7 fb⁻¹, 1POI, blind Asimov)

| | stat-only | full r₉₅ | 
|---|---|---|
| **v11** (6-cls CE, argmax winner-score) | 771 | **1742** |
| **v32** (13-cls kHCE v9, argmax-with-prior, log-L) | **584** | 1919 |
| **AN-23-102** @138 fb⁻¹ | ~330 | **505** |
| AN √L-scaled → 26.7 fb⁻¹ | **879** | **1148** |

## THE ISSUE — in one paragraph

We are **systematics-limited, not statistics-limited.** Our **stat-only floors (771, 584) BEAT the AN's
scaled stat-only (879)** — at equal lumi our statistical sensitivity is *better* than theirs. But our
**full limits (1742, 1919) are far above the AN's scaled full (1148)**. The whole gap is the systematic
uncertainty, and crucially **σ_syst is a fractional floor that does NOT scale with luminosity** — so more
data does almost nothing: v11 would plateau at **~1550 even at full Run 2**, never reaching 505.

## The decomposition (why √L scaling is invalid)

r₉₅ ≈ 1.64·σ_r, σ_r² = σ_stat² + σ_syst²:

| | σ_stat | σ_syst | r₉₅ | %stat |
|---|---|---|---|---|
| v11 @ 26.7 fb⁻¹ | 461 | **923** | 1742 | 20% |
| v11 scaled → 138 fb⁻¹ | 203 | **923** (unchanged) | **~1550** | 5% |
| AN @ 138 fb⁻¹ | 201 | **170** | 505 | 60% |

σ_stat scales and **matches the AN** (203 ≈ 201). σ_syst is lumi-independent and **5.4× the AN's** (923 vs
170). That ×5.4 is the entire problem.

## What dominates σ_syst — autoMCStats (MC statistics), NOT theory

Freeze-group breakdown (|Δr|/r): **MC-stat (autoMCStats) = 41% (v11) / 42% (v32)**, signal theory 11%,
scale+PS 6%, everything else <5%. The CMS-style impact plots show the top nuisances are
`prop_binSR_hplusc_bin5/6/7` (autoMCStats), towering over theory.

**Why:** the signal is **0.17 events**. A *normal* per-bin MC-stat (~2–3% on a ~1500-event background bin)
= ~40 events ≫ the signal. autoMCStats dominates because the signal is tiny and sits where the background
MC is thinnest (the high-discriminant tail). vs AN's MC-stat = 6.2%.

## Root cause — signal localization (same S/B, 5× the σ_syst)

Integrated S/B is the **same** for us and the AN (~10⁻⁵; AN's is even worse). But σ_syst is a **shape**
quantity, not set by integrated S/B. AN's BDT puts signal in a **sharp tail bin where background is tiny**
→ smooth systematics can't fake it. Our signal is **smeared under the background peak** (v11 SR signal
peaks in bins 8–10 exactly where the background peaks) → background shape + MC-stat move right under the
signal → large σ_syst. Same fact = stat shape-gain (AN ×2.6 vs us ×1.18).

## RULED OUT (do not re-try — all tested this session)

- tt rateParam from CR_tt → **worse** (floating norm ±36 SR events ≫ 0.17 signal; tt has 3.18M raw events,
  constraint is *not* the issue — it's S/B). Top-group {tt,st} rateParam → also worse.
- Coarser binning (4 bins) → worse; tail-merge (8) → null; finer → worse. **Binning is a dead end.**
- LOWESS smoothing of systematic *variations* → null (autoMCStats is from the *nominal* sumw², not the variations).
- Discriminant/collapse (kappa-D, soft-kappa, LR-vs-top, P/prior, P(hplusc)) → all a wash (shape Z ≈ 0.005).
- S/B itself → not the differentiator (same as AN).

## THE FIXES (leverage order)

1. **Cross-era MC template averaging** (AN §6.1/7.2.1): build background templates from ALL eras' MC
   (postEE+preEE+2023) → more effective stats/bin → smaller autoMCStats. **#1 lever**, uses existing MC,
   no retraining. Headroom: freeze-autoMCStats = 1032, so ~1742 → ~1300–1400.
2. **Smooth the NOMINAL templates** (+ take bin errors from the merged template) — the piece my
   variation-smoothing missed.
3. **Better localization** — multi-category + k-means yield-balanced binning (AN's structural advantage);
   shrinks σ_syst directly. Hard (needs analysis restructure).
4. **Luminosity** — only helps the ~20% statistical part; will NOT get us to 505 alone.
5. **Charm-jet tagging** is the biggest MISSING systematic (no weight column; needs upstream PNet SF).
   Adding it *raises* the limit (more honest) — required for correctness, not improvement.
6. Irreducible: signal 4FS/5FS theory (~11%) — shared with the AN, leave it.

## Key files (for re-pull / continuation)

- v11 pipeline: `higgscharm/scripts/combine/make_combine_inputs.py` + `analysis/workflows/hww_combine_fixed.yaml` (`combine:` block) → `outputs/combine/v11_hplusc_v4.{txt,root}`.
- v32 pipeline: `b-hive/scripts/make_combine_histograms_v11_v32.py` (v9 model, argmax-prior) + `make_datacard_v11_v32.py` → `b-hive/combine_inputs/v11_hplusc_v32_v9.{txt,root}`.
- Results driver: `b-hive/scripts/combine_full_results.sh`; plots: `plot_combine_final.py`, `plot_refined.py`.
- combine: `/afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4/`. Env: `micromamba activate b_hive`.
- Full docs on EOS: `b-hive/docs/combine_findings_v11_v32.md`, `systematics_reference.md`.

## One line
**Limit is autoMCStats-dominated and systematics-floored (~1550, lumi-independent); fix = cross-era MC
template averaging, not binning/discriminant/lumi. Our statistical floor already beats the AN's.**
