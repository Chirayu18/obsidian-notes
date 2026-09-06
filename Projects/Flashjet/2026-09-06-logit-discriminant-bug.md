---
tags: [reference]
status: active
date: 2026-09-06
source: lxplus
---

# BUG: rejection numbers computed on raw logits — all earlier 1/eps_B values invalid

## What was wrong

`InferenceTask` saves `prediction.npy` as **raw logits**, not probabilities.
Verified: row sums range −39 to +31, individual values −14 to +23.

Every rejection calculation used

```python
d = pred[:, c] / (pred[:, c] + pred[:, 0])      # WRONG on logits
```

which is only meaningful for non-negative probabilities. With negative logits the
denominator can approach zero or flip sign, so the ordering is scrambled.

**Correct discriminant** (2-class softmax, equivalently sigmoid of the logit difference):

```python
d = 1.0 / (1.0 + np.exp(-(pred[:, c] - pred[:, 0])))
```

## How much it mattered — Tbqq @ 50% eff, baseline 480k

| | rejection | CA5/baseline |
|---|---|---|
| buggy (logit ratio) | 759 | **0.636** |
| correct (sigmoid diff) | **21,325** | **1.068** |

**Factor 28 in the rejection, and the ratio flips sign** (CA5 36% worse → 7% better).
Rank agreement between the two discriminants is only **0.77** — genuinely different
orderings, not a monotone rescaling.

Corrected 480k summary: CA5 median ratio **0.995**, ahead 2/6 well-resolved classes
— i.e. parity, NOT the "CA5 is 0.64–0.95× baseline" I reported.

## What this invalidates

- `perclass.py` output from 2026-09-04 (same formula) — the whole per-class rejection
  column, including the Tbqq 0.636 quoted repeatedly as evidence of no top-specific gain
- the first `rej_from_pred.py` run
- the claim that the ROCCurveTask grid was "quantizing badly and produced a spurious 1.321"

**AUC numbers are unaffected** — AUC is rank-based and was read from the task's own
`AUC_*.npy`, not recomputed.

## Correction about the ROC grid

I claimed the `ROCCurveTask` grid was broken because it gave Tbqq CA5/bl = 1.321 where
"the correct" calculation gave 0.636. Backwards: the grid gave **1.321**, the genuinely
correct calculation gives **1.068** — same sign, same direction. **The grid was closer to
right than my replacement.** What it was really showing is that Tbqq @ 50% is
**tail-limited**: only **94 background jets** pass threshold.

## The real improvement: report `n_bkg_pass`

Both scripts now print how many background jets survive the threshold per class, and
flag `<-- TAIL-LIMITED` below 100. At 20M test jets with 2M QCD:

- **Hqql and Tbl @ 50% eff: ZERO background jets pass** → rejection is unmeasurable,
  not infinite. Never quote `inf` as a result.
- Tbqq @ 50%: 94 jets — quote with a caveat or move to 70% eff.
- Hgg, Zqq, Wqq: thousands of jets — well resolved at any working point.

**Rule: quote rejection only where `n_bkg_pass >= 100`, and prefer 70% efficiency where
the tail is thin.**

## Fixed

Both `~/flashjet_condor/rej_from_pred.py` and `~/flashjet_condor/perclass.py` patched
(grep `softmax on LOGITS`). Related: [[2026-09-04-subjet-verdict]],
[[2026-09-04-herwig-dataset-plan]].
