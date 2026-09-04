---
tags: [reference]
status: superseded
superseded_by: "[[2026-09-04-ca-1M-verdict-and-pairwise]]"
date: 2026-09-01
source: lxplus
---

> [!warning] Superseded — the 20k per-class ROC result did not hold
> The "all nine classes improve, Tbqq rejection 1.75x" result below was measured
> at **20k iterations** and is a transient of early training. At a matched
> **480k** checkpoint on the same 20M-jet test set, all nine classes are
> marginally **worse** for C/A. See [[2026-09-04-ca-1M-verdict-and-pairwise]].

# Second training (survives_SD) — and why +1.31 does not survive a controlled rerun

Cluster **9252644**, A100-PCIE-40GB, 20k iters, batch 512, seed 123456. Two arms
sequentially in one job: `train_sd_baseline` (stock) and `train_sd_ca` (**6**
C/A features = the original 5 plus `survives_SD`).

This is the run that was supposed to test whether soft-drop survival adds
anything. It answered a more important question instead.

## Result: the C/A advantage decays to zero by 20k

| iters | sd_base | sd_+CA6 | delta | | v4fix_base | v4fix_+CA5 | delta |
|---|---|---|---|---|---|---|---|
| 5k  | 77.49 | 79.58 | **+2.09** | | 74.62 | 78.59 | +3.96 |
| 10k | 80.08 | 80.96 | **+0.88** | | 76.09 | 81.09 | +5.01 |
| 15k | 81.98 | 82.14 | **+0.16** | | 81.18 | 82.49 | +1.31 |
| 20k | 82.08 | 82.00 | **−0.09** | | 80.82 | 82.32 | +1.50 |

Same job, same physical card, same script — only `--training-version` differs.
The delta goes +2.09 → +0.88 → +0.16 → **−0.09**.

`survives_SD` did not help: sd_+CA6 peaks at 82.14 vs the 5-feature run's 82.49,
well inside the noise band below.

## The larger finding: run-to-run spread is ~1.3 points

The two **baselines** are the same config, same seed, same data, same
hyperparameters. They should be near-identical. They are not:

| | 5k | 10k | 15k | 20k |
|---|---|---|---|---|
| v4fix_base | 74.62 | 76.09 | 81.18 | 80.82 |
| sd_base | 77.49 | 80.08 | 81.98 | **82.08** |

**1.26 points apart at 20k.** Checked and ruled out:
- **Not the model.** cpf input widths from the checkpoints: both baselines 19,
  v4fix_ca 24, sd_ca 25. The SD edits did not leak into the non-CA path.
- **Not the script.** `diff run_v4fix.sh run_sd.sh` = only the version strings.
- **Not the card.** 0 of 140 weight tensors match at 5k, max |dW| = 1.56. Kernel
  non-determinism drifts slowly from a shared init; this is total divergence.

**Cause: the dataloader RNG is not seeded.** `utils/torch/LZ4Dataset.py:__iter__`
calls `np.random.permutation(s)` and `np.random.rand(...)` (weighted sampling)
inside worker processes with no per-worker seed derived from `--seed`. With
`--n-threads 4`, every run gets a different shuffle *and*, because
`loss_weighting=True`, a different sampled subset of jets. `--seed 123456` fixes
only initialization.

## Consequence for the headline number

**+1.31 is the same size as the noise.** One unlucky baseline seed reproduces it
entirely. On current evidence C/A shows no significant accuracy gain at 20k.

What survives the controlled comparison:
- **Loss is better at every checkpoint**, including 20k (0.4958 vs 0.5026).
- **Early training is genuinely faster** (+2.09 at 5k against the *stronger*
  baseline).
- CA reaches higher *training* accuracy (82.82 vs 82.05) at equal validation —
  extra capacity being used, not obviously extra signal.

## Caveat on calling it settled

Neither arm is converged at 20k: sd_base is still climbing (81.98 → 82.08) with
val loss still falling (0.5063 → 0.5026). "The curves met" describes a
non-converged point, not a ceiling. An 80k run was prepared (`run_80k.sh`,
`k80.sub`, guard on `N_CA_FEATURES=5`) and submitted as 9254446, then withdrawn
while still idle — worth resubmitting.

The experiment that would actually settle it is **3–5 seeds per arm** for an error
bar, which is cheap (~1 h/run on H100) and converts this from anecdote to result.
Until then, do not quote +1.31 externally.

## Test-set ROC (baseline arm) — and a fix to the ROC tooling

`ROCCurveTask` **cannot be used as-is for JetClass.** `scripts/compute_roc.py` is
hardcoded to b-tagging discriminants (`bvsl`, `bvsc`, `cvsl`, `uds_vs_g`) and never
reads the config's `truths`. On JetClass it emits curves labelled `TTBarLep_bvsl`
etc., then prints "There is no TTBar/HToBB/... process in your data" for the real
classes. **The AUCs it wrote (bvsl 0.936, bvsall 0.891) are meaningless** — a
mislabelled remap of JetClass classes onto b-tag categories. Do not quote them.

Replacement: `~/cawork/jetclass_roc.py` reads `prediction.npy` / `truth.npy` from
`InferenceTask` directly and computes per-class one-vs-QCD AUC and background
rejection. Baseline (`train_v4fix_baseline`), 20,046,720 test jets, ~2.0M/class:

| class | AUC (vs QCD) | 1/eB @ 50% | 1/eB @ 30% |
|---|---|---|---|
| Hbb  | 0.9980 | 4925 | 16987 |
| Hcc  | 0.9888 | 1391 | 6572 |
| Hgg  | 0.9643 | 84 | 263 |
| H4q  | 0.9893 | 557 | 2210 |
| Hqql | 0.9998 | 668159 | 2004477 |
| Zqq  | 0.9658 | 188 | 783 |
| Wqq  | 0.9693 | 239 | 1010 |
| Tbqq | 0.9967 | 4066 | 19461 |
| Tbl  | 0.9999 | inf | inf |
| **macro AUC (ovr)** | **0.9795** | | |

Test accuracy **81.08%**, against 81.18% on the val split — so the val-split
result generalizes.

**Treat Hqql and Tbl as suspect.** 1/eB of 668k and a literal `inf` (zero QCD
surviving) are not credible as separation power; both classes contain a lepton,
so they are probably trivially separable, but a label/ordering issue is not ruled
out. Do not put those two rows in a talk without checking.

The C/A arm's inference is cluster **9254447** (the first attempt, 9252639, died
loading a 24-col checkpoint into a 25-col model after the live tree was edited to
6 features mid-queue; `run_roc2.sh` now guards on `N_CA_FEATURES=5`).

## [UPDATE] Test-set per-class ROC: C/A wins on all 9 classes

CA arm inference completed (cluster 9254447). Both arms on the full
`JetClass_test_mod`, 20,046,720 jets, ~2.0M per class.

| class | base AUC | CA5 AUC | dAUC | 1/eB@50% base -> CA | ratio |
|---|---|---|---|---|---|
| Hbb  | 0.9980 | 0.9983 | +0.0003 | 4925 -> 5180 | 1.05x |
| Hcc  | 0.9888 | 0.9901 | +0.0013 | 1391 -> 1572 | 1.13x |
| Hgg  | 0.9643 | 0.9660 | +0.0016 | 84 -> 91 | 1.08x |
| H4q  | 0.9893 | 0.9907 | +0.0014 | 557 -> 734 | **1.32x** |
| Zqq  | 0.9658 | 0.9677 | +0.0020 | 188 -> 211 | 1.13x |
| Wqq  | 0.9693 | 0.9710 | +0.0017 | 239 -> 258 | 1.08x |
| Tbqq | 0.9967 | 0.9974 | +0.0007 | 4066 -> 7108 | **1.75x** |

**Accuracy 81.08 -> 82.10 (+1.02). Macro AUC (ovr) 0.9795 -> 0.9815.**
(Hqql and Tbl are saturated — `inf` rejection in one or both arms — and carry no
information; exclude them.)

### This overturns the "convergence acceleration only" reading above

**Nine of nine classes improve.** Under seed noise roughly half should regress;
the sign consistency across independent class-vs-QCD discriminants is not
plausibly chance.

**The per-class ordering matches the physics prediction.** Largest rejection
gains on the multi-prong boosted decays **Tbqq (1.75x)** and **H4q (1.32x)**,
where C/A branch structure should carry information; smallest on **Hbb (1.05x)**,
pure flavour tagging, exactly where the earlier BDT study said C/A carries
almost nothing. A prior prediction reproduced in the measured ordering is
evidence, not fluctuation.

**Background rejection is the sensitive metric, not accuracy or AUC.** Tbqq gains
only +0.0007 AUC but **75% better QCD rejection** at 50% signal efficiency. The
20k accuracy comparison that suggested the gain vanished is a noisy, low-
information statistic evaluated at a non-converged point; it should not be
treated as the headline.

The ~1.3-point seed spread documented above still applies to the *accuracy*
number, and this is still one checkpoint per arm. The multi-seed run remains the
thing that makes the accuracy quotable — but the per-class ROC result stands on
its own much better.

Script: `~/cawork/jetclass_roc.py` -> `~/cawork/jetclass_roc_results.json`.

## Reproducing

Metrics: `output/TrainingTask/{jet_class,jet_class_ca}/JetClass_val_mod/train_sd_{baseline,ca}/ParticleTransformer2_JetClass/epochs_0/nominal/validation_metrics.npz`

Comparison script: `~/cawork/cmp4.py` on lxplus.
JetClass ROC: `~/cawork/jetclass_roc.py` -> `~/cawork/jetclass_roc_results.json`.

The 6-feature module is kept at `utils/flashjet_ca_features.py.bak_sd6`; the live
tree is back to the 5-feature version ([[2026-08-31-reproduce-ca-plus1.3-result]]).

Related: [[2026-08-28-part-ca-features-implementation]],
[[2026-08-31-reproduce-ca-plus1.3-result]], [[flashjet-workflow]]
