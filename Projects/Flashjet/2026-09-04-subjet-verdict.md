---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# Subjet arm: pre-registered test FAILED — both arms are nulls

## The verdict

Threshold set **before** 180k/200k landed: *subjet ahead across the fresh
checkpoints, both metrics, paired mean over ~10 checkpoints clearing **+0.05***.

**Result at 200k: mean −0.0348, t = −0.50, ahead 5/10 → FAIL.**
Val loss agrees independently (+0.0009, t = +0.56, same 5/10).

| iter | val_bl | val_sj | Δval | Δvloss |
|---|---|---|---|---|
| 20k | 81.765 | 81.989 | +0.224 | −0.0046 |
| 40k | 83.466 | 83.531 | +0.065 | −0.0010 |
| 60k | 84.059 | 84.197 | +0.138 | −0.0042 |
| 80k | 84.372 | 83.900 | −0.471 | +0.0096 |
| 100k | 84.658 | 84.590 | −0.068 | +0.0015 |
| 120k | 84.764 | 84.754 | −0.010 | +0.0006 |
| 140k | 84.832 | 84.957 | +0.125 | −0.0027 |
| 160k | 84.894 | 84.916 | +0.022 | −0.0000 |
| 180k | 85.014 | 85.005 | −0.009 | +0.0007 |
| 200k | 85.157 | 84.793 | **−0.364** | +0.0086 |

## Both arms, side by side

| arm | paired mean vs baseline | n | reading |
|---|---|---|---|
| **CA5** | −0.124 full run; **+0.006** at 700k+ | 43 | slower convergence, ends at parity |
| **subjet** | −0.035 | 10 | parity |

CA5's full-range deficit is **significant** (t = −3.12; val loss agrees, t = +2.98,
both 9/43). It shrinks monotonically — last-20 −0.024 (t = −1.41), 700k+ **+0.006**
(t = +0.20) — so the honest statement is *C/A converges more slowly and ends level*,
**not** that it hurts at convergence. Report both ranges; quoting only the endgame
would be cherry-picking.

**Subjet's null is the cleaner one**: it does not pay the early-convergence cost.
Over the same ≤200k range CA5 is **−0.330** while subjet is −0.035. That gap is the
one large, consistent, real effect in the whole comparison.

## THE NOISE FLOOR — the methodological lesson

**Baseline's own mean |step| between checkpoints over 20k–200k is 0.377.**
Every subjet delta discussed all day, including the "encouraging" +0.125 at 140k,
sits far inside that. I had been quoting ~0.09, which is the *endgame* figure where
the LR has decayed and curves are flat — noise in the early/mid regime is **~4×
larger**. Single checkpoints below ~200k simply cannot resolve effects of this size.

Concretely: I called +0.125 at 140k "encouraging and monotone". 160k gave +0.022,
180k −0.009, 200k −0.364. It was one high draw.

**Rule going forward: never read a single checkpoint below 200k. Only paired means
over ≥10 matched checkpoints.**

### Prior-movement log (a caution about my own updates)
20% → 30% → 35% across one afternoon, each move tracking the latest checkpoint.
That is noise-following, not evidence accumulation. The pre-registered threshold is
what stopped it; without it, 180k (subjet's best-ever 85.005) would have read as
"almost there" instead of "inside the noise band".

## Why this is a good result, not a failed experiment

A theoretically-motivated prediction, confirmed by independent routes:

1. **The arity argument.** Lund coordinates at a splitting (ln z, ln kT, ln ΔR) are
   **2-body** — built from two 4-vectors. ParT's `PairEmbed` already computes exactly
   this for every pair, by construction. Predicted redundant → measured significantly
   negative over 43 checkpoints.
2. **Lim's S₂ sufficiency** (arXiv:1807.03312, 1904.02092) supplied the prior *before*
   any run: the leading nontrivial term of the functional Taylor expansion is the
   two-point correlation spectrum, and MLP+S₂ matches CNN-on-images.
3. **The probe** (`prong.py`, val only): Tbqq vs Wqq+Zqq —
   multiplicity floor 0.8036, **2-body control 0.9617**, subjet alone 0.9553,
   control+subjet 0.9694. Subjets add **+0.0077**, ~8% of remaining headroom.
4. **The n-body extension.** A subjet mass is n-body — a sum over a set the model must
   first *identify* — so `PairEmbed` does **not** compute it by construction, and the
   arity argument did **not** predict a subjet null. Running it was the right call;
   the null it returned sharpens the finding rather than repeating it.

**Probe signal does not imply trainable gain.** This inference failed three times
today: `share_bp` recoverable at AUC 0.87 → CA5 significantly negative; DeepSets
R² 0.232 read as "hard to compute, therefore useful" → it wasn't; subjet +0.0077 →
parity. A probe measures whether information is present and accessible *to a small
model*; it does not measure whether a transformer with full pairwise attention over
128 constituents, trained on 100M jets, already reaches it internally.

## Endgame note for the 1M comparison

**Use ~960–980k, NOT the literal final checkpoint.** Baseline drops 86.230 @ 980k →
85.952 @ 1M, and CA5 shows the same dip at 840k — an LR-schedule artifact present in
both arms. Decided *before* seeing CA5's endpoint.

CA5 endgame Δ (baseline − CA5): 860k −0.06, 880k −0.04, 900k −0.02, 920k −0.10,
940k −0.03. Scatter around a small negative, no trend.

## Still open

**Herwig generator robustness** — a separate question from in-domain accuracy, and now
the one live avenue. Dataset built and validated (see
[[2026-09-04-herwig-dataset-plan]]); inference deferred to the 1M checkpoints per
user. Prior **~25–30%**, report either way.
