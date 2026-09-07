---
tags: [reference]
status: active
date: 2026-09-07
source: lxplus
---

# Herwig generator-robustness result (980k, all three arms)

Executes the plan in [[2026-09-04-herwig-dataset-plan]]. Condor cluster **9274984**,
all three arms sequential, `JetClass_herwig_test_mod`, 20,046,720 jets each.
`ExitCode 0`, `NumJobStarts 1`, ran on `b9pgpun002`. ~50 min/arm.

Pre-registered before running: **prior 25–30%** that a real robustness gap appears,
**report either way**, metric is **Δ(degradation)** on 1/ε_B with tail-limited classes
dropped rather than quoted.

## Accuracy drop, Pythia → Herwig

| arm | Pythia | Herwig | drop | vs baseline |
|---|---|---|---|---|
| baseline | 86.211 | 83.337 | **2.875** | — |
| CA5 | 86.156 | **83.361** | **2.795** | −0.080 (more robust) |
| subjet | 86.190 | **83.368** | **2.822** | −0.053 (more robust) |

**The ordering inverts.** CA5 is *worst* in-domain and *best* under Herwig. Absolute
Herwig accuracy is subjet > CA5 > baseline — the only metric in the whole study where
baseline comes last.

## Rejection degradation

`deg = rej_pythia / rej_herwig` (>1 = worse under Herwig); `d_deg = deg_arm − deg_baseline`
(<0 = that arm more robust). Classes with n_bkg_pass < 100 dropped.

**At 70% efficiency:**

| class | deg_base | deg_ca5 | deg_subjet | d_ca5 | d_subjet |
|---|---|---|---|---|---|
| Hbb | 1.125 | 1.055 | 1.061 | **−0.070** | **−0.064** |
| Hcc | 1.285 | 1.270 | 1.246 | −0.015 | −0.039 |
| Hgg | 1.475 | 1.468 | 1.461 | −0.007 | −0.013 |
| H4q | 1.974 | 1.962 | 1.956 | −0.011 | −0.017 |
| Zqq | 2.197 | 2.192 | 2.187 | −0.005 | −0.010 |
| Wqq | 2.514 | 2.501 | 2.523 | −0.013 | +0.009 |
| Tbqq | 1.298 | 1.380 | 1.320 | **+0.082** | +0.022 |

CA5 more robust in 6/7 (median −0.011); subjet 5/7 (median −0.013).

**At 90% efficiency:** CA5 6/7 (median −0.003), subjet 6/7 (median −0.004). Largest
entries Wqq −0.021/−0.022 and Tbqq −0.037/−0.004. Hbb has deg < 1 for every arm —
rejection *improves* under Herwig there.

## How much of this is real

**Direction is consistent:** 23 of 28 class-comparisons favour the extra features,
across two working points and two arms. Consistency across independent classes is
harder to get by chance than a single number.

**Magnitude is not persuasive:**
- 0.080 accuracy points on a 2.875-point drop = **2.8% relative**. The measured
  checkpoint-to-checkpoint noise floor at 900k+ is **0.088 accuracy points** — the
  CA5 effect is *the size of one checkpoint's wobble*, and there is **n=1 checkpoint
  per arm**. Cannot separate "more robust" from "this checkpoint landed well".
- Tbqq@70% goes the *other* way for both arms (+0.082, +0.022) — and that is the
  class where the n-body argument predicts the largest gain if the story were true.
- The 90% medians (−0.003, −0.004) are near zero. Most of the 70% signal is Hbb;
  drop that class and the rest is noise.

**Posterior: ~40%** (was 25–30%). Sign consistency is genuine evidence; the effect
sits at the noise floor with one checkpoint per arm.

## What would settle it

Herwig inference at **900k and 940k** as well (checkpoints exist, ~50 min/arm).
Three matched points per arm turns one draw into something with an error bar.
**Not yet run.**

## Interesting alongside PLuM

[[2026-09-07-plum-paper-vs-our-result]] attributes its H→bb gain to displaced
heavy-hadron decay patterns. Our largest robustness effect is *also* Hbb (−0.070,
−0.064 at 70%). Whether these are the same underlying thing is unestablished.

## Reproduce

```bash
python3 ~/flashjet_condor/gen_rob.py _at980k 0.70,0.90
```

Discriminant is `sigmoid(logit_c − logit_QCD)` — see
[[2026-09-06-logit-discriminant-bug]] for why the naive ratio is wrong by ~28x.
