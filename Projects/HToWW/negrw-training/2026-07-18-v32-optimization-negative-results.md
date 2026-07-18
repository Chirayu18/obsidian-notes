---
tags: [reference]
status: active
date: 2026-07-18
source: lxplus
---

# v32 optimization attempts — four negative results

**TL;DR — v32's `v9` configuration is at a local optimum. Four attempts to improve it
were tested and all made the limit WORSE or did nothing. Do not retry these without
new information. v11 (r95 = 1343) remains the better analysis; v32 baseline stays 1491.**

Context: after the [[negrw]] reweighting took v32 from 1935 → 1491 (−23%), this session
tried to close the remaining gap to v11. Everything below was measured, not argued.

## Reference numbers (unchanged, canonical)

| builder | full | freeze-autoMCStats | stat-only |
|---|---|---|---|
| v11 | **1343** | 1100 | 788 |
| v32 (`v9`) | **1491** | 1083 | 599 |

v32 has the better *discriminant* (stat-only 599 vs 788, −24%) but loses on the full
limit. It pays more at both stages: +484 for systematics, +408 for MC-stat
(v11: +312 / +243).

## ❌ 1. Pruning empty / low-N_eff bins

**Result: 1491 → 1512 (WORSE by 21).** stat-only 599→602, freeze-aMCS 1083→1094.

v32's SR leaves 14 of 20 bins identically empty (global binning, `lo` = 1st percentile
over all events; the SR is a high-D argmax selection). Hypothesis: those bins waste
autoMCStats DOF.

**The premise is false.** combine's `autoMCStats 10` applies `event-threshold=10` and
simply does not create nuisances for bins below it — empty bins cost nothing to begin
with. Pruning only removed weakly-constraining CR bins that *did* hold background,
degrading the CR normalization constraint slightly.

Kept in the builder behind `--prune` (opt-in, default OFF) so the negative result is
reproducible. See the comment block at `make_combine_histograms_v11_v32.py:~683`.

## ❌ 2. Rebinning / transforming the discriminant

**Result: no configuration beats the current one.**

A monotonic transform (log etc.) of D cannot change bin contents — it only relabels the
axis; with fixed bin *count* it is just rebinning. Scanned merges of adjacent SR bins
(sensitivity proxy Σ s²/(b + σ²_b)):

| config | stat sensitivity | with MC-stat | MC-stat penalty |
|---|---|---|---|
| **current (6 live bins)** | 0.00364 | **0.00257** | 29.4% |
| merge k=2 | 0.00340 | 0.00254 | 25.2% |
| merge k=3 | 0.00334 | 0.00246 | 26.2% |

Merging *does* lower the MC-stat penalty (29.4→25.2%) but destroys more raw sensitivity
than it recovers. The builder's own comment records the opposite direction also failing:
signal-quantile (finer) binning gave 1487→1515. **Binning is bracketed on both sides and
is optimal.**

## ❌ 3. "The MC-stat tax is in the CRs"

**Result: refuted. It is ~87% in the SR.** Per-channel autoMCStats freeze scan:

| freeze | limit | recovers (of 408) |
|---|---|---|
| SR_hplusc | **1137** | **354 (87%)** |
| CR_vjets | 1467 | 24 |
| CR_diboson | 1478 | 13 |
| CR_tt | 1488 | 3 |
| CR_higgsbkg / CR_st | 1489 | 2 |

Note the trap: SR *total-background* MC-stat error is only 1–3.4%, which made the SR look
healthy. But **vjets** in the signal-bearing bins has N_eff = 13 / 61 / 127. tt dominates
the yield and is well populated; vjets is what is starved where the signal actually lives.
**Judge SR health by the signal-weighted, per-process N_eff — not total background.**

## ❌ 4. tt rateParam (+ shape-only theory split)

**Result: 1491 → 1542 (WORSE by 51); with tt theory shapes also dropped, 1581 (+90).**

| config | full | freeze-aMCS | stat-only |
|---|---|---|---|
| baseline | **1491** | **1083** | 599 |
| + tt rateParam | 1542 | 1114 | 608 |
| + rateParam, tt theory dropped | 1581 | 1181 | 608 |

Motivation was a theory-group freeze scan (below) plus a rate/shape decomposition showing
tt's `scalevar_muR` is a **±10% pure rate** effect (shape RMS 0.05%, signal-weighted shape
shift −0.01%) sitting on the 72%-tt SR background.

**Why it failed:** tt appears in all six channels with a *correlated* nuisance, so the
CRs already constrain it well. A free `[0,5]` rateParam **removes** that cross-channel
constraint and hands the fit a parameter that can absorb signal-like variation in the SR.
The existing comment in the script (`RATE_PARAM_GROUPS = {}  # tt fixed to MC (rateParam
tested -> worse)`) was correct and still is, post-negrw and post-v9.

### Systematics group scan (MC-stat frozen; total syst tax = 1083 − 599 = 484)

| freeze group | limit | recovers |
|---|---|---|
| theory (scalevar + PS) | 768 | **315 (65%)** |
| rate lnN (xsec/lumi) | 959 | 124 (26%) |
| JES/JER | 1067 | 16 |
| lepton | 1081 | 2 |
| pileup / negrw method | 1083 | 0 |

**Important caveat learned the hard way:** *freezing* a nuisance is NOT the same as
*constraining it better*. Freezing asserts perfect knowledge, which no reconfiguration can
buy. The 315 measures how much freedom the fit currently uses for theory — it is **not**
315 of recoverable penalty. Every "fix" derived from reading it that way failed.

Not worth chasing: JES/JER + lepton + pileup = 18 of 484 total. (This is why the earlier
`--smooth` work never helped.)

## What is actually left

The deficit is **structural, not a tuning problem**: v32 concentrates signal into bins that
are ~72% tt, so every background uncertainty — MC-stat and normalization alike — acts
directly on top of the signal. Concentration is simultaneously why stat-only is excellent
(599) and why the full limit is not.

The one genuinely open lever is **more MC statistics for vjets (and tt) in the high-D
region** — which is exactly what negrw exploited to get 1935 → 1491. Rebinning and
nuisance reshuffling are exhausted.

Possible future work (untested):
- PCA over per-bin ensemble covariance (paper §IV D) — needs per-model P₊ re-dumped.
- `xsec_hplusc_4FS_5FS = 1.30` is a 30% *signal* normalization uncertainty and is part of
  the +124 lnN group; worth checking it is not double-counting against the reference
  cross-section the limit is quoted relative to.

## Files

Canonical, untouched: `/eos/user/c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc_v32_v9.{root,txt}`
(r95 = 1491, verified by re-running `text2workspace` + `AsymptoticLimits` after the prune revert).
All test workspaces/datacards/limit files from this session were deleted.

Related: [[RESUME-condor-retrain]], [[2026-07-17-closure-renormalization-decision]]
