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

## Imbalanced-JetClass test (pre-registered 2026-10-08, before any result)

Question: does kappa-HCE help once the signal is rare, which is the regime where it helped in HToWW?

**Setup:**
- Signal s = Hcc.
- Hcc training rows are kept with probability f = 0.0045, which gives Hcc : all other classes ≈ 1 : 2000 (about 45k of 10M Hcc jets kept). All 9 other classes are kept in full.
- The drop is a per-row mask seeded by (20261008, file index). It is identical for every arm and does not depend on read order.
- Validation and test sets are untouched (balanced).

**Training (all arms):**
- ParT v2 (`ParticleTransformer_RecTree2_JetClass`, jet_class_ca) **from scratch**, same initial weights (seed 0), 200k iterations, batch 512.
- Optimizer as v2's b-hive run: Ranger (RAdam + Lookahead), lr 1e-3, eps 1e-5, wd 0.
- Schedule: 1k warmup, then cosine to 0.
- bf16, torch.compile, gradient clip 1, the same seeded data order, BatchNorm in normal train mode.

**Arms (identical except the loss):**
1. Plain CE.
2. Inverse-frequency weighted CE, with weights from the kept counts (max = 1). This is the baseline to beat.
3. Full kappa-HCE for s = Hcc: L_group + 1·L_fine + 1·L_sig, tau = 0.3, alpha from the detached fc weights at every step. The semantics follow the HToWW `_kappa_hce_forward`; unit tests agree with it to within 1e-7 relative (eps = 0).

**Evaluation (full balanced test set):**
- Hcc vs QCD: AUC of the logit difference.
- Hcc vs all backgrounds: AUC with two scores, the one-vs-rest logit z_s − logsumexp_{j≠s} z_j and the eq. 11 D score with kappa = alpha from each arm's own final fc weights. Both scores are reported for every arm.
- Background rejection 1/ε_B at 30% and 50% Hcc efficiency.
- The other 8 classes' vs-QCD AUCs, to catch trade-offs.
- Accuracy is reported but treated as secondary, because it depends on the class priors.

**Go rule:** kappa-HCE beats weighted CE on Hcc-vs-QCD AUC by **more than 0.002**, **and** loses no more than 0.001 on any other class vs QCD. Plain CE vs weighted CE is also reported.

**Code:** `flashjet/kappa_hce/`: `finetune_imb.py`, `kappa_hce_imb.py`, tests in `test_kappa_imb.py` (`test_kappa_imb.log`), evaluation in `compare_imb.py`. Condor files: `~/flashjet_condor/imb_kappa.sub` and `run_imb_kappa.sh`.

## Imbalanced-JetClass test: results (2026-10-28)

Condor cluster 9503546 (all three arms finished 2026-10-09/10). Each arm kept the same 45,175 Hcc training jets (1:2000). Full balanced JetClass test set, 20.0M jets; `kappa_hce/imb/compare_imb.py`, log `imb/compare_imb.log`, json `imb/compare_imb.json`.

| metric | plain CE | weighted CE | kappa-HCE | kappa − wCE |
|---|---|---|---|---|
| 10-class accuracy | 0.77406 | 0.80091 | 0.77382 | −0.02708 |
| **Hcc vs QCD AUC** | **0.98974** | 0.98905 | 0.98789 | **−0.00116** |
| Hcc vs QCD rejection at 30% / 50% eff | 8416 / 1726 | 4705 / 1311 | 3606 / 1060 | −23% / −19% |
| Hcc vs all AUC, p/(1−p) | 0.97467 | 0.97203 | 0.96668 | −0.00536 |
| Hcc vs all AUC, D (own α) | 0.97472 | 0.97206 | 0.96751 | −0.00455 |
| Hcc vs all rejection at 30% / 50% eff (D) | 2259 / 439 | 1789 / 349 | 1190 / 273 | |
| Zqq / Wqq | 0.97009 / 0.97331 | 0.96881 / 0.97195 | 0.96713 / 0.97039 | −0.00168 / −0.00156 |
| Hgg / H4q / Hbb | 0.96762 / 0.99113 / 0.99839 | 0.96658 / 0.99053 / 0.99826 | 0.96376 / 0.98917 / 0.99746 | −0.00282 / −0.00137 / −0.00079 |

Bootstrap (5 replicas) sd of the Hcc-vs-QCD deltas: 1.4e-5 (kappa − wCE) and 7e-6 (CE − wCE), so every difference above is far outside resampling noise. These runs are one seed per arm, and seed-to-seed spread was not measured.

**Pre-registered go rule: NO-GO.** kappa − wCE on Hcc vs QCD is −0.00116 (required > +0.002), and the worst other class is Hgg at −0.00282 (required ≥ −0.001).

**Reading:** the arms rank plain CE > weighted CE > kappa-HCE on every signal metric. Plain CE did not collapse: 45k signal jets are enough to learn from. This test therefore did not reproduce the HToWW regime (about 2k signal events, heterogeneous background class sizes, λ = 25, k_fine = 7). A faithful replica with v10/v20/v32 baselines and multiple seeds was started on 2026-10-28 (section "HToWW-regime replica", in progress).

## HToWW-regime replica (pre-registered 2026-10-28, before any result)

Question: does kappa-HCE beat the other HToWW losses when JetClass is cut to the HToWW training conditions (13-class profile, about 2.3k signal, one dominant dissimilar background)? The test is designed so a negative result is as reportable as a positive one. Nothing below was tuned on the test set, and nothing will be changed after results exist.

### What the HToWW trainings actually did (read from their files, 2026-10-28)

Sources: HToWW b-hive `/eos/user/c/cgupta/HToWW/b-hive` (read only), outputs under `/eos/user/c/cgupta/EPR_task/b-hive/output/`, and [[MVA]] / [[2026-07-01-kappa-hce-loss-math]].

| Item | Value | Source |
|---|---|---|
| Training data (v12 to v32) | dataset `hww_multiclass_v13`, one file `file_0.lz4`, 4,076,514 events | DatasetConstructorTask histogram.npy |
| Class counts | hplusc 2257, hplusb 2681, ggH 28476, vbf 69848, zh 54721, ggzh 104802, wh 25437, tthnonbb 37668, tthtobb 22657, tt 3180107, st 499001, diboson 38094, vjets 10765 | same |
| Model | SimpleMLP_MultiClass 17→128→64→32→13, BatchNorm, ReLU, dropout 0.2 (about 13k parameters) | `utils/models/simple_mlp_multiclass.py` |
| Optimizer | AdamW lr 1e-3, betas (0.95, 0.999), eps 1e-6; `epoch_lin_decay` (constant, then ×1e-2 over the last 30% of epochs); grad clip 1 | `tasks/parameter_mixins.py`, `SchedulerLoader.py`, `base_model.py` |
| Batch, epochs | 1024; 30 epochs for v10 to v30 (incl. v20), 50 for v31 and v32 | `train_MVA.sh`, output dirs |
| Weighting | `--loss-weighting`: per-class weights N_total/N_j normalised to max 1, inside the loss; plain CE uses `CrossEntropyLoss(weight, reduction="none").mean()` (divides by batch size, not by the weight sum) | `batches.py`, `training.py`, `base_model.py` |
| v18h (hierarchical) | groups higgs = {hplusc, hplusb, ggH, vbf, zh, ggzh, wh}, top = {tt, st, tthtobb, tthnonbb}, diboson, vjets; fine group higgs with λ = 2; significance λ = 0 | `config/HPlusCHToWW_hierarchical.yml` |
| v20 | same groups and fine λ = 2, plus mode `logB` λ = 1: summed −log D (signal) + log(1+D) (background), κ = softplus(r)·(1+cos)/2 with a learnable r per class | `config/HPlusCHToWW_logB.yml`, loss file |
| kappa-HCE as now configured | λ = 25, τ = 0.3, k_fine = 7, batch-mean L_sig | branch `kappa-hce-loss` 1be29da (2026-07-01) |
| Quoted metric | hplusc vs all background, AUC of p_s on raw counts; S/√B with raw counts (S out of 2257, B out of 4,074,257) at fixed signal efficiency | MVA.md; recomputed from prediction.npy: v32 0.97475, v20 0.97294 |

**Four findings change how the HToWW lineage reads:**

1. **The v10 "flat CE collapse" (AUC 0.51) was a bug, not class imbalance.** v10's dataset (`HPlusCHToWW_finegrained/hww_multiclass_v10`) has hplusb = 0 events. `compute_class_weights` divides by that zero, so the weights come out as `[0, nan, 0, …, 0]`. The stored training and validation loss is exactly 0.0 at every epoch, and the logits stay at initialisation scale. The network never trained. A weighted (or unweighted) 13-class flat CE on the real data was never run, so HToWW never showed that flat CE collapses.
2. **The quoted v20 and v32 numbers are in-sample.** `hww_multiclass_v13` is a single file. With one file, `training.py` sets n_val = 0 and uses the training file for validation too (`files[-0:]`). The inference test dataset is the same `hww_multiclass_v13`, and prediction.npy has exactly 4,076,514 rows. Training, `best_model` selection and the quoted AUC / S/√B all use the same events.
3. **The 0.975 did not come from λ = 25, τ = 0.3, k_fine = 7.** v32 was trained on 2026-03-17. The loss file was first committed on 2026-03-30 (ce3bdd5), so the exact code at training time is not recoverable. That nearest snapshot has λ = 1 in the config, summed L_sig, and no k_fine (= 1). Its `training.py` does not forward τ, so the loss used its default τ = 1.0 while the config said 0.3. The λ = 25 / k_fine = 7 / mean-L_sig version is from the June `hwwcom_*` runs and the July branch. At equal length, kappa-HCE v30 (30 epochs) gave 0.973, the same as v20 (30 epochs). v32's extra 0.002 came with 50 epochs.
4. **The v32 − v20 gap (0.0018) is within the statistical error.** With 2257 signal events, the Hanley–McNeil standard error at AUC 0.974 is about 0.0023 per model (estimate). It is also one seed per loss.

### Replica on JetClass

**Class roles (13 → 10).** Each HToWW class goes to one JetClass class, so the training counts are the HToWW counts exactly:

| JetClass | plays | train count |
|---|---|---|
| Hcc (signal) | hplusc | 2,257 |
| Hbb | hplusb | 2,681 |
| Hgg | ggH | 28,476 |
| H4q | vbf | 69,848 |
| Hqql | zh + ggzh + wh | 184,960 |
| Tbqq | tthnonbb + tthtobb | 60,325 |
| QCD | tt | 3,180,107 |
| Tbl | st | 499,001 |
| Zqq | diboson | 38,094 |
| Wqq | vjets | 10,765 |
| total | | 4,076,514 |

- **Why these roles:** the signal and its b-flavoured twin are the two rarest classes, which is the HToWW situation (hplusc and hplusb are the rarest). The dominant background is the one we always measure Hcc against (QCD stands in for tt at 78%). Top-like and diboson-like classes keep their physics analogues. The three VH processes merge into the leptonic Higgs class.
- **Manual groups:** the HToWW groups mapped by role: higgs = {Hcc, Hbb, Hgg, H4q, Hqql}, top = {QCD, Tbl, Tbqq}, diboson = {Zqq}, vjets = {Wqq}, with fine group higgs at λ = 2.
- **Subset:** one fixed subset from `JetClass_train_100_mod`, shared by every arm and seed. Each row gets a uniform u seeded by (20261028, file index). Candidates with u < 1.05·N_c/10M are kept, then the N_c smallest u per class, so the counts are exact. Script: `htoww_replica/make_subset.py`.

**Arms.** Only the loss differs. The HToWW loss and weighting files are byte-identical copies (`htoww_hce_copy.py` md5 7690b85d, `htoww_batches_copy.py` md5 0b3d6cd6), wired as `training.py` does it.
1. `ce`: unweighted CE, the v10 analogue as v10 was meant to be.
2. `wce`: inverse-frequency weighted CE (`loss_weighting`).
3. `hier`: hierarchical CE with the manual groups, the v18h config. It is the same as v20 without the significance term, so arms 3 and 4 isolate that term.
4. `v20`: hierarchical + logB discriminant-aware term, λ = 1, learnable r in the optimizer.
5. `kappa`: kappa-HCE with λ = 25, τ = 0.3, k_fine = 7 (the version being promoted now).

**Training (all arms):**
- Model: `ParticleTransformer_NoPair_JetClass` (jet_class_ca, about 2M parameters), from scratch with `torch.manual_seed(seed)`.
- Data: batch 1024 with the last partial batch dropped, 30 epochs = 119,400 iterations, and a seeded per-epoch permutation that is identical across arms for a given seed.
- Optimizer: Ranger lr 1e-3, eps 1e-5, wd 0, 1k warmup then cosine. Grad clip 1, bf16 model with an fp32 loss.
- No checkpoint selection: the final weights are evaluated.
- Seeds 0, 1, 2 for every arm (15 runs).
- **Deviations from HToWW, chosen for cost and stability, not for results:** a JetClass transformer replaces the 13k-parameter MLP on 17 event features. The optimizer is the one already proven on this model rather than AdamW. All arms run 30 epochs, the length of v20 and v30 (v32's 50 epochs would cost about 150 H100-hours). The test set is held out, unlike HToWW's in-sample numbers.

**Evaluation:** the full JetClass test set, 20M jets, balanced.
- **Primary (HToWW-style):**
  - Hcc vs all background, with test jets weighted per class by N_c(train) / n_c(test). The weighted test mixture then has HToWW's absolute yields.
  - Score p_s (the score behind the quoted 0.975).
  - M1 = weighted AUC; M2 = S/√B at 50% signal efficiency (S = 2257·ε, B = weighted background passing). S/√B is also reported at 30% and 70%.
- **Secondary:** the eq. 11 D score with κ = sigmoid(cos/0.3) from each arm's fc; balanced Hcc vs QCD and Hcc vs Hbb (logit differences); every class vs QCD; accuracy.
- Code: `metrics_replica.py`, `compare_replica.py`.

**Go rule (fixed now).** kappa beats both wce and v20 on both M1 and M2. For each of these four comparisons, mean(kappa) − mean(baseline) must exceed 2 × max(seed sd of the two arms) and a practical floor (M1 +0.001, M2 +1% relative). Anything less is no-go. A missing or crashed run is reported, not imputed. Plain CE and hier are reported for context.

**What I will not do:**
- Gate on flat CE collapsing. The brief asked for that as a fidelity check, but finding 1 shows HToWW never observed a real collapse, so there is nothing to reproduce. If flat CE trains normally here, that is a result, not a reason to change the class profile.
- Run a v32-as-trained arm (λ = 1, τ = 1, summed L_sig), the 50-epoch length, or the 2k-vs-10k dose-response. Each would be a separate pre-registered follow-up.

**Budget (estimate):** NoPair ran at 11.3 it/s at batch 512 on H100 NVL, so about 5.6 it/s at 1024. That gives about 6 h of training plus about 0.5 h of data load and test inference per run, so about 100 H100-hours for 15 runs.

**Files:**
- Code: `/eos/user/c/cgupta/flashjet/kappa_hce/htoww_replica/` (`replica_spec.py`, `make_subset.py`, `htoww_losses.py`, `test_htoww_losses.py`, `train_replica.py`, `metrics_replica.py`, `compare_replica.py`).
- Condor: `~/flashjet_condor/hww_replica.sub`, `run_hww_replica.sh`.
- **Unit test:** `logs/test_htoww_losses.log`, ALL PASS. Every arm equals the original HToWW modules exactly (max |diff| 0 for loss values and for gradients with respect to the logits, the fc weights and r) in batches with 0, 3 and 40 signal events. The kappa arm also agrees with the earlier flashjet log-space port to ≤ 3e-4 (log(p + eps) vs log-space).

### Replica run status (2026-10-29, interim: seed 0 only, NOT the verdict)

- **Subset:** built with exactly the target counts (4,076,514 jets in 41 shards, Hcc 2257; `data/manifest.json`).
- **Smoke:** all 5 arms ran end to end on the lxplus905 T4. That was 200 iterations at batch 256, because batch 1024 in fp32 does not fit in 15 GB.
- **Condor:** cluster **9612945**, 15 procs, H100 NVL.
- **Measured cost:** 0.071–0.077 s/it, i.e. about 2.5 h of training and 0.26 h of test inference per run. The full grid is therefore about 42 H100-hours, against the 100 h estimate.
- **Status:** seed 0 is done for all arms, plus ce seed 1. The other 8 runs were still queued or running when this was written.

**Seed 0, full test set**

| | ce | wce | hier | v20 | kappa |
|---|---|---|---|---|---|
| M1 prior-weighted AUC (p_s) | 0.9826 (s0, s1 mean; sd 0.0010) | 0.9496 | 0.9641 | 0.9704 | 0.9767 |
| M2 S/√B at 50% | 14.39 (sd 0.93) | 6.82 | 8.00 | 8.45 | 10.47 |
| Hcc vs QCD (balanced) | 0.9851 | 0.9711 | 0.9706 | 0.9731 | 0.9775 |
| Hcc vs Hbb (balanced) | 0.9747 | 0.9545 | 0.9630 | 0.9229 | 0.9461 |
| accuracy | 0.553 | 0.766 | 0.563 | 0.504 | 0.747 |

**What seed 0 suggests (no verdict yet):**
- At seed 0, kappa is well ahead of wce and v20 on both primary metrics.
- Unweighted plain CE is ahead of every other arm, kappa included, on every Hcc metric.
- The hierarchical and v20 arms nearly destroy Tbl vs QCD (0.17 and 0.03, against about 0.9999 for the other arms) and degrade Tbqq vs QCD. This happens because their manual "top" group puts QCD together with Tbl and Tbqq.
- If the seeds confirm this, kappa's win would be over the weighted baselines only, not over plain CE. That is consistent with HToWW never having had a working flat CE (finding 1).
- The go rule is evaluated only when all 15 runs exist (`compare_replica.py`).

### HToWW-regime replica: final results (2026-10-29)

All 15 runs finished (condor 9612945, no missing runs). Output of `htoww_replica/compare_replica.py`, saved as `htoww_replica/compare_replica_final.log` and `runs/compare_replica.json`. Values are mean ± sd over seeds 0, 1, 2 on the full test set. "prior" means test jets weighted to the training class yields (HToWW absolute yields).

| metric | plain CE | weighted CE | hier (v18h) | v20 | **kappa-HCE** |
|---|---|---|---|---|---|
| **M1** Hcc vs all AUC, p_s, prior | **0.98234 ± 0.00081** | 0.94310 ± 0.00568 | 0.96313 ± 0.00105 | 0.97052 ± 0.00083 | 0.97609 ± 0.00057 |
| S/√B at 30% eff | **19.58 ± 1.15** | 10.49 ± 0.11 | 10.18 ± 0.36 | 11.41 ± 0.10 | 14.56 ± 0.23 |
| **M2** S/√B at 50% eff | **14.13 ± 0.79** | 6.98 ± 0.24 | 8.00 ± 0.16 | 8.45 ± 0.10 | 10.22 ± 0.24 |
| S/√B at 70% eff | **9.05 ± 0.46** | 4.04 ± 0.22 | 5.45 ± 0.06 | 6.05 ± 0.06 | 6.89 ± 0.16 |
| background rejection at 50% eff | **640 ± 73** | 156 ± 11 | 205 ± 8 | 229 ± 5 | 334 ± 16 |
| Hcc vs all AUC, D score, prior | **0.98197 ± 0.00091** | 0.94097 ± 0.00625 | 0.96436 ± 0.00080 | 0.97090 ± 0.00065 | 0.97595 ± 0.00069 |
| Hcc vs QCD (balanced) | **0.98486 ± 0.00058** | 0.96962 ± 0.00172 | 0.97313 ± 0.00362 | 0.95821 ± 0.02452 | 0.97767 ± 0.00018 |
| Hcc vs Hbb (balanced) | **0.97424 ± 0.00211** | 0.95293 ± 0.00446 | 0.96280 ± 0.00039 | 0.92310 ± 0.00429 | 0.94286 ± 0.00354 |
| 10-class accuracy (balanced test) | 0.551 ± 0.008 | **0.765 ± 0.002** | 0.555 ± 0.034 | 0.500 ± 0.004 | 0.748 ± 0.001 |
| Tbqq vs QCD | **0.99595** | 0.99369 | 0.659 ± 0.232 | 0.640 ± 0.359 | 0.99401 |
| Tbl vs QCD | **0.99994** | 0.99987 | 0.439 ± 0.484 | 0.340 ± 0.542 | 0.99988 |

**Pre-registered verdict: GO.** All four comparisons pass:
- kappa − wCE: M1 +0.03299 (needed > 0.01136); M2 +3.24 (needed > 0.48).
- kappa − v20: M1 +0.00557 (needed > 0.00166); M2 +1.76 (needed > 0.48).

**What this shows, stated plainly:**
1. **Among the losses HToWW actually compared, kappa-HCE wins clearly and reproducibly** in the HToWW regime (2257 signal against 4.07M heterogeneous background). On held-out data it beats v20 by +0.0056 AUC and +21% S/√B at 50% efficiency, with seed spreads of about 0.0006–0.0008 AUC. It also avoids the manual-group damage: hier and v20 put QCD into the "top" group, which wrecks Tbqq/Tbl vs QCD (seed-unstable, down to 0.34). kappa keeps those classes at the plain-CE level.
2. **Unweighted plain CE beats every arm on every signal metric:** +0.0063 AUC and +38% S/√B at 50% over kappa, and about 1.9× kappa's background rejection. It does not collapse in this regime. Its only loss is 10-class accuracy on a balanced test (0.55), which is a prior effect that AUC and S/√B do not see.
3. **The baseline HToWW never had is the strongest one.** HToWW's v10 "collapse" was the hplusb = 0 weighting bug (finding 1 above), so a working flat CE was never compared. On this evidence, the case for kappa-HCE in HToWW rests on comparing it with weighted and hierarchical CE. The comparison an analysis should make is kappa-HCE against unweighted CE on held-out events.

**Caveats:** the model is a JetClass transformer (arm C), not the 13k-parameter event MLP, and all arms train 30 epochs. Whether plain CE also wins with the HToWW MLP on HToWW's own features is untested; the direct check is to retrain HToWW with unweighted 13-class CE on a held-out split.

Cleanup: the 8 GB candidate directory `htoww_replica/cand/` is no longer needed and can be deleted.

### HToWW-regime replica: evaluation check and overfitting measurement (2026-10-29)

Prompted by the user questioning how plain CE could beat weighted CE. Scripts and outputs: `htoww_replica/check/` (`prior_check.py` / `.json`, `train_vs_test.py`, `train_vs_test*.log` / `.json`).

**1. The class weights are wired correctly.** The wce weight vector equals sum/N_c normalised to max 1 for every class (Hcc 1.0, Hbb 0.842, QCD 0.00071, ...).

**2. The primary score was unfair to the weighted arms.** M1/M2 rank by p_s against background weighted to the training priors. A plain CE model's p_s is already calibrated to those priors. A model trained with inverse-frequency weights has posteriors for an effective prior of about uniform, so its p_s is the score for the wrong background mixture. With the Bayes prior correction (logits + log(π_c/π'_c), π' ∝ π_c·w_c):
- weighted CE: M1 0.9431 → 0.9650 ± 0.0022; M2 6.98 → 8.78 ± 0.36.
- For hier, v20 and kappa the same correction lowers the numbers (kappa 0.9761 → 0.9728). Their effective prior is not uniform, so their uncorrected p_s is the fairer number.
- Plain CE needs no correction: 0.9823.
- The balanced Hcc-vs-QCD logit difference is prior-independent and is unaffected (CE 0.9849, wCE 0.9696, kappa 0.9777).

**3. Overfitting, measured.** Each arm's final model was scored on its own training jets (all 2257 Hcc plus up to 40k per other class, weighted back to training yields) and on the held-out test set. Mean over 3 seeds:

| arm | Hcc vs all AUC, train | test | gap | Hcc vs QCD, train | test | gap | mean log p_s on Hcc, train → test |
|---|---|---|---|---|---|---|---|
| plain CE | 0.9901 | 0.9823 | +0.008 | 0.9912 | 0.9849 | +0.006 | −2.78 → −3.58 |
| weighted CE | **0.9971** | 0.9431 | **+0.054** | **0.9976** | 0.9696 | +0.028 | −0.18 → −2.24 |
| hier | 0.9695 | 0.9631 | +0.006 | 0.9769 | 0.9731 | +0.004 | −1.74 → −1.93 |
| v20 | 0.9924 | 0.9705 | +0.022 | 0.9885 | 0.9582 | +0.030 | −9.9 → −13.9 |
| kappa | 0.9937 | 0.9761 | +0.018 | 0.9929 | 0.9777 | +0.015 | −2.05 → −3.91 |

**Reading:**
- **In-sample, the ranking is the HToWW one:** weighted CE 0.9971 > kappa 0.9937 > v20 0.9924 > plain CE 0.9901 > hier 0.9695. The weighted losses look best on the events they were trained on.
- **On held-out events the inverse-frequency-weighted losses lose most:** about 1400× weight on 2257 signal jets, seen 30 times and evaluated at the final weights (no checkpoint selection, by design), memorises the signal (wCE gives its training Hcc jets mean p_s ≈ 0.84). Plain CE overfits least among the strong arms.
- **For HToWW,** whose v20/v32 numbers are in-sample (finding 2 above), this suggests the quoted AUCs flatter the weighted losses by a few hundredths. It also suggests their ordering might change on a held-out split.
- **What this does not show:** that weighting is useless. Weighted CE's validation Hcc vs QCD peaked at 0.980 near 40k iterations before declining to 0.971, so early stopping or regularisation would recover part of the gap. Even at its peak it was below plain CE at the same point (0.985).

**Corrected status of the GO:** the pre-registered GO stands as computed (kappa beats wCE and v20 on raw-p_s M1/M2). With the prior-corrected score for wCE, kappa still leads it (M1 0.9761 vs 0.9650; M2 10.22 vs 8.78). All of these are comparisons among losses that overfit the rare signal; unweighted CE remains best on held-out data. The decisive next test for HToWW is a held-out split with early stopping for every loss, plus a plain unweighted CE arm.
