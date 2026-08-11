---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# The JES/JER merged-group bug: root cause, fix, and verification

Closes action item 1 of [[2026-08-10-analysis-strategy-from-AN]], which listed this as
*blocking everything shape-related*.

## Symptom

In the `hww_combine_2dcat` card built 2026-07-31, the object-shift templates were
impossible for the two **merged** process groups, while single-sample groups were fine:

| process | JES Up | JES Down | verdict |
|---|---:|---:|---|
| vjets (SR) | −71.01% | −71.92% | same sign, catastrophic |
| higgsbkg (SR) | −98.93% | −99.02% | same sign, catastrophic |
| diboson (SR) | +0.00% | +0.00% | frozen = identical to nominal |
| tt (SR) | +1.44% | −1.87% | physical |
| st (SR) | +1.93% | −2.73% | physical |

Both shifts moving the *same* way by −71%/−99% is impossible for a ±1σ scale variation.

## Root cause

**Inference had scored only 19 of 57 samples into the object-shift directories.**
`make_combine_inputs.py` sums a merged group over whatever constituent parquets exist in
each shift dir, so the varied template summed a *partial subset* while nominal summed all
of them — producing a spurious, one-directional yield drop.

This explains every symptom exactly:

- **vjets −71%** — `WtoLNu_2Jets` was missing from the shift dirs.
- **higgsbkg −99%** — `GluGluHto2Wto2L2Nu`, `VBFHto2Wto2L2Nu`, `ZH` were missing.
- **diboson frozen** — `WW` was missing, so the group total hit the
  `if c.sum() <= 0 < nom_c.sum()` fallback that copies the nominal histogram.
- **tt / st healthy** — their constituents happened to be among the 19 that were scored.

An earlier theory — that `hww_combine_fixed` was an incomplete tree — is **wrong**; that
tree was complete. The gap was in the *shift* directories, not the nominal one.

## Fix

Re-ran `run_inference.py` over the object-shift directories. All 12 shift dirs went from
**19 → 44** samples (EXIT=0).

Verified the 44 are the complete MC set, not a count coincidence. `mva/` lists 67 entries
vs 44 in each shift dir; the 23-entry difference is entirely benign:

- **12 data files** (`Data`, `EGammaRun*`, `MuonRun*`, `MuonEGRun*`) — data has no object shifts by design.
- **11 merged-group output files** (`V+Jets`, `tt`, `H+c`, `ggH`, …) — these are *products*
  written by the postprocess/card step, not inputs.

All three previously-missing culprits (`WtoLNu_2Jets`, `GluGluHto2Wto2L2Nu`, `WW`) are
present in every shift dir.

## Verification

Diagnostic checker `check_shifts.py` (reads a card, writes nothing) flags any template that
is frozen, same-sign-and-large, or >30%. Validated by reproducing the bug on the old card.

**Problem count: 126 (before) → 92 (after).** More important than the count is that the
*character* of the residual flags changed completely.

### Per-process, summed over all six channels — the decisive test

| process | nominal | JES Up | JES Down |
|---|---:|---:|---:|
| tt | 93461.9 | +1.52% | −1.89% |
| st | 7457.8 | +2.03% | −2.19% |
| **vjets** | 6674.4 | **+1.50%** | **−1.70%** |
| **higgsbkg** | 285.2 | **+2.73%** | **−2.67%** |
| **diboson** | 2137.3 | **+3.27%** | **−3.61%** |
| hplusc | 0.3 | +3.31% | −3.61% |

Every process now moves by a physical **±1.5–3.6% with clean opposite signs**. The two
broken groups and the frozen one are fully repaired.

### Why 92 flags remain — both benign

1. **18 "frozen"** are all `*_hplusc` in *background* CRs where the nominal yield is
   0.00. Signal is essentially absent there (7 events in 1.57M, per
   [[kin-cuts-vs-mva]]), so 0 → 0 under a shift is an empty template, not a misfiring
   fallback. The checker's `n == 0` guard uses exact zero and lets tiny-but-nonzero
   yields through.

2. **74 "same-sign"** are now *small and mixed in direction* (e.g. +8.74%/+4.42%,
   −4.07%/−7.41%), unlike the near-equal −71%/−72% of the bug. Since the channel totals
   above are conserved and physical, these are **migrations between channels**, not yield
   loss: a JES shift changes *which class wins argmax*, so events move between channels
   rather than across a cut boundary.

   This is the argmax migration exposure predicted in §2 of the strategy note — a real
   property of argmax-defined regions, and the reason the AN applies smoothing (v8
   changelog) and warns about artificial constraints (§7.2.1). It is a modelling question,
   not a bug.

**JER (`CMS_res_j`) is one-sided by construction** — a resolution *smearing* is symmetric,
so Up and Down both broaden the distribution and move yields the same way (−0.30% / −0.30%
for tt). Expected, not a defect.

## Follow-up

- The checker's zero-guard should use a small epsilon rather than exact 0 to avoid
  flagging empty signal templates in background CRs.
- Smoothing (action 5 of the strategy note) is now unblocked — it would have smoothed over
  a bug if applied before this fix.
