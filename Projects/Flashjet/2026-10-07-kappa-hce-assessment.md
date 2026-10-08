---
tags: [reference]
status: active
date: 2026-10-07
source: lxplus
---

# kappa-HCE for JetClass jet tagging: assessment (verdict: no-go)

Source: `/eos/user/c/cgupta/flashjet/kappa_hce/ref/kappa-hce-math.pdf`. This is the PDF of our own HToWW note [[2026-07-01-kappa-hce-loss-math]] (v32 H+c MVA loss).
Question: can it help jet tagging on top of ParT v2 (`ParticleTransformer_RecTree2_JetClass`, jet_class_ca)? See [[2026-09-25-rectree-capacity-and-warmstart-tests]] for v2's numbers and [[2026-09-06-logit-discriminant-bug]] for why we use logit differences.

## What the method is

It is mainly a **training objective**, with a post-hoc discriminant added on top. It is built for **one signal class s**.
- Groups: cosine c_j between the final-layer class rows W_s and W_j. They are recomputed every step (detached), with soft membership alpha_j = sigmoid(c_j / tau), tau = 0.3.
- L = L_group + k_fine * L_fine + lambda * L_sig:
  - L_group: inverse-frequency-weighted NLL after merging every class with c_j >= 0 into one column.
  - L_fine: alpha-gated conditional CE, with events weighted by alpha of their true class.
  - L_sig: batch-mean of -log D on signal and log(1 + D) on background, where D = p_s / (p_s + sum_{j != s} alpha_j p_j).
- Inference: the eq. 11 score D_sig, with kappa taken from alpha or optimised per working point (the paper reports about +1.2% S/sqrt(B) over uniform kappa).
- Cost is negligible: a 10x10 cosine matrix and a few reductions per step, with no new parameters.
- Assumptions: one signal of interest, heavy class imbalance, and a final `nn.Linear` whose rows act as templates. In HToWW, flat CE collapsed (AUC 0.51) because of a 2k-vs-4M imbalance. Most of the gain over flat CE comes from fixing that collapse. Over the previous best loss (v20) the gain is only 0.973 to 0.975.

## Post-hoc probe on v2's saved test logits (measured)

Script: `flashjet/kappa_hce/probe/kappa_probe2.py`, log `kappa_probe2.log`. It is a copy of `kappa_probe.py` with all classes, an extra D(e_QCD) column and the fitted kappas printed; the old log is kept.
- Data: a 30% random subset of the 20M test jets; kappa fit on 10% of that, evaluation on the other 90% (n = 5.41M).
- Columns: D(alpha) uses kappa = sigmoid(c/0.3) from v2's templates; D(unif) uses all kappa = 1; D(kfit) uses kappa fitted to maximise AUC; D(e_QCD) keeps only QCD in the denominator.

**s vs QCD (our metric), AUC**

| s | logit diff | D(e_QCD) | D(alpha) | D(unif) | D(kfit) |
|---|---|---|---|---|---|
| Hbb | 0.99886 | 0.99886 | 0.99731 | 0.99744 | 0.99886 |
| Hcc | 0.99387 | 0.99387 | 0.98625 | 0.98720 | 0.99387 |
| Hgg | 0.97081 | 0.97081 | 0.94706 | 0.94933 | 0.97081 |
| H4q | 0.99322 | 0.99322 | 0.98762 | 0.98880 | 0.99322 |
| Hqql | 0.99990 | 0.99990 | 0.99968 | 0.99973 | 0.99871 |
| Zqq | 0.97461 | 0.97461 | 0.94984 | 0.94810 | 0.97411 |
| Wqq | 0.97778 | 0.97778 | 0.96383 | 0.96217 | 0.97775 |
| Tbqq | 0.99832 | 0.99832 | 0.99715 | 0.99717 | 0.99683 |
| Tbl | 0.99997 | 0.99997 | 0.99986 | 0.99990 | 0.99996 |

**Why "fitted kappa = logit difference" holds (checked, not assumed).** With only QCD in the denominator, D = sigmoid(z_s - z_QCD - log kappa_QCD). That is a monotone function of the logit difference, so the AUCs are identical (the D(e_QCD) column matches to 5 digits).
- For Hbb, Hcc, Hgg, H4q, Zqq and Wqq, the optimiser drives the non-QCD kappas to at most 3e-2 relative to kappa_QCD (most are below 1e-3). It rediscovers the logit difference. The one exception is kappa_Tbl = 0.26 for Wqq, which has no effect because p_Tbl is about 0 on Wqq and QCD jets.
- For Hqql, Tbqq and Tbl the AUC is about 0.9999, so the smooth-AUC surrogate is flat. The fit wanders, and D(kfit) ends slightly below the logit difference.
- No kappa beats the logit difference on any class. This is expected: for calibrated CE posteriors, z_s - z_QCD is the log likelihood ratio, which is Neyman-Pearson optimal for s vs QCD.

**One-vs-rest (s vs all 9 others).** The roles flip. D(unif) = p_s/(1-p_s) is the one-vs-rest likelihood ratio at the training priors, and it is the best column for every class (for example Zqq: D(unif) 0.96528, D(alpha) 0.96453, logit difference 0.84924). D(alpha) never beats D(unif). So eq. 11 is just "choose the background mixture", and the trained posteriors already give the optimum for whichever mixture you pick. It adds no information.

## Can the training loss change what v2 learns? (argument, not measured)

1. The trick that delivered the HToWW gain does nothing here. JetClass is balanced, so every inverse-frequency weight is 1, and flat CE does not collapse (v2 reaches 85.4%).
2. It is single-signal, but we need 9 taggers from one network. L_group merges the s-like classes into one column, so it removes the gradient that separates them, which those classes' own taggers need. For s = Hgg the merged group is {Hgg, Hcc, H4q} (QCD sits at c = -0.00). The loss would trade Hcc and H4q performance for Hgg.
3. On our hardest pair the loss is close to plain CE. For s = Zqq, v2's P-group is empty: every c_j < 0, including QCD (c = -0.02, alpha = 0.48). So L_group is exactly 10-class CE. L_fine becomes CE with alpha in 0.24–0.48, a mild reweighting. L_sig only adds pressure on D_Zqq against a mixture that is not our metric (our metric is Zqq vs QCD only).
4. CE is a strictly proper loss. With 100M balanced training jets, the remaining gap to arm A (Zqq 0.97441 vs 0.97567) is a capacity or architecture gap. A loss reweighting can at best move capacity between class pairs, and will not close that gap.

**Cheapest test, designed but not run.** Warm-start from v2's `best_model.pt` with two arms that are identical except for the loss: (a) CE + 1.0 * L_fine(s = Zqq) + 1.0 * L_sig(s = Zqq), with tau = 0.3; (b) plain CE as the control. Copy `lmkt/finetune_warm.py` and run the same number of steps and the same learning rate. Evaluate on the full test set.
- Go threshold: Zqq-vs-QCD AUC above the control by more than 0.002 (2x the late-training noise sd), with no other class's AUC falling by more than 0.001.
- Given points 1–4, the expected outcome is a trade-off, not a net gain. That is why the test was not run.

## Verdict

**No-go.**
- Post-hoc: measured, no gain on any class. Our logit difference is already the optimal s-vs-QCD score, and eq. 11 with any fitted kappa reproduces it or comes out worse.
- Training: the mechanisms that helped HToWW (imbalance handling, single-signal focus) are absent here or work against a 9-signal tagger. Nothing was implemented in b-hive and no condor job was submitted.

## Measured A/B result (2026-10-08): NO-GO confirmed

Condor cluster 9502481. Both arms warm-start from v2 best_model and train 40k iterations with identical settings. Arms: plain CE, against CE + 1.0·L_fine(Zqq) + 1.0·L_sig(Zqq) with τ = 0.3, all fixed before running. Full JetClass test set, 20.0M jets, logit-difference AUCs vs QCD (from the job logs; `compare_ab.py` bootstrap not run).

| | acc | Zqq | Wqq | Hcc | Hgg | H4q | Hbb | Tbqq |
|---|---|---|---|---|---|---|---|---|
| v2 at iteration 0 (eval-path check) | 85.398 | 0.974400 | 0.977682 | 0.993836 | 0.970889 | 0.993182 | 0.998832 | 0.998314 |
| CE control, 40k | 85.240 | 0.974147 | 0.977378 | 0.993698 | 0.970640 | 0.993074 | 0.998809 | 0.998272 |
| **kappa-HCE (Zqq), 40k** | **84.286** | 0.974125 | 0.977389 | 0.993686 | 0.970649 | 0.993068 | 0.998807 | 0.998263 |
| kappa − CE | **−0.954 pts** | −0.2e-4 | +0.1e-4 | −0.1e-4 | +0.1e-4 | −0.1e-4 | −0.0e-4 | −0.1e-4 |

- **Eval-path check passes:** v2 at iteration 0 gives 85.398%, against 85.403% from b-hive inference (20.0M vs 20.05M jets).
- **Go rule fails:** Zqq-vs-QCD AUC changes by −0.00002, where the rule required more than +0.002. Every s-vs-QCD AUC moves by at most 2e-5.
- **10-class accuracy drops by 0.95 points.** L_sig reshapes how Zqq scores against the other classes, which moves the argmax without improving any signal-vs-QCD separation. Validation agrees: 0.8436 vs 0.8518 at 40k.
- Both fine-tunes end slightly below v2 itself (CE 85.24 vs 85.40), as in the earlier warm-start study; the comparison is between the two arms.

**Conclusion:** on balanced 10-class JetClass, kappa-HCE gives no measurable signal-vs-QCD gain and costs about 1 point of accuracy. This matches the analysis above: the method's HToWW benefit came from fixing class-imbalance collapse, which JetClass does not have.
