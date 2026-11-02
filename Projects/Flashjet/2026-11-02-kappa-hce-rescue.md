---
tags: [reference]
status: active
date: 2026-11-02
source: lxplus
---

# kappa-HCE rescue: diagnosis, v2 loss, pre-registered test

Follows [[2026-10-07-kappa-hce-assessment]] (replica results f3a2509, checks 2510567).
Code: `/eos/user/c/cgupta/flashjet/kappa_hce/htoww_replica/` (`kappa_v2.py`, `test_kappa_v2.py`, `train_rescue.py`).

## Why v1 loses to plain CE on the replica (measured, existing runs)

1. **Early stopping does not rescue it.** Validation (200k held-out jets, prior-weighted Hcc vs all, mean of 3 seeds) peaks at 0.9765 for kappa (80k iterations) against 0.9830 for CE (70k). Kappa trails CE from the first checkpoint.
2. **The cosine neighbourhood collapses.** At the end of training the signal's cosine with every other class is at most 0.06 in all three seeds (Hbb -0.004, 0.056, -0.026). The positive group of L_group is therefore the signal alone, and L_group is inverse-frequency CE, the arm that overfits most (train-test gap 0.054).
3. **It misses its own goal.** Hcc vs Hbb (balanced test AUC): CE 0.974, kappa 0.943. Hcc vs QCD: CE 0.985, kappa 0.978.
4. **Per-jet weights are extreme.** Inverse frequency gives a signal jet about 1400x a QCD jet. L_sig takes the mean over the batch's signal jets with lam 25; the batch holds 0.57 signal jets on average, so one signal jet carries weight 25, about 25,000x a jet in a CE mean. The 2257 signal jets, each seen 30 times, are memorised (train-test gap 0.018 vs CE 0.008).
5. **The signal term is not a proper score.** log(1+D) on background is bounded by log 2. Its minimiser at signal fraction f is D = f/(1-2f), which saturates at f = 1/2.

## v2 (`kappa_v2.KappaHCEv2`)

L = L_ce + k_fine L_fine + lam L_sig, every term a sum of per-jet terms divided by the constant B E[w], so a jet's weight never depends on what else is in its batch.

- **Weights:** tempered, w_c = (n_max/n_c)^beta. beta = 0 is the natural prior, which is the mix S/sqrt(B) is evaluated at. beta = 0.5 gives the signal 37.5x a QCD jet (instead of 1400x).
- **Neighbourhood:** data-driven confusability instead of weight cosines. c_j is an EMA of the mean p_signal on jets of true class j (detached), and alpha_j = c_j / max c. A background the model currently mistakes for signal gets alpha near 1. L_fine is the conditional CE over the alpha-weighted classes, each jet weighted by alpha of its true class.
- **Signal term:** binary cross-entropy on p_signal (proper).
- **Check:** with beta 0, k 0, lam 0 it is exactly nn.CrossEntropyLoss (unit test).

## Pre-registered test (fixed before any result)

Replica protocol unchanged: same data (2257 Hcc in 4,076,514 jets), ParT NoPair, 30 epochs, batch 1024, seeds 0-2, H100 NVL.

| arm | loss |
|---|---|
| ce_es | plain CE (v2 with beta 0, k 0, lam 0) |
| k2n | v2, beta 0, k_fine 1, lam 1 |
| k2t | v2, beta 0.5, k_fine 1, lam 1 |

**Model selection (all arms alike):** validation every 10k iterations. The raw score p_s and the prior-corrected score (logits minus log w_c; identical to raw for beta 0) are both computed, and the (checkpoint, score) with the best validation M1 is the one test result reported. The final weights are also evaluated, as a secondary result.

**Metrics:** M1 = prior-weighted Hcc vs all AUC, M2 = S/sqrt(B) at 50% signal efficiency (`metrics_replica.py`), mean over 3 seeds, error = seed spread / sqrt(3).

**Verdicts:**
- **RESCUED:** the better v2 arm has M1 >= ce_es M1 - 0.0010 and M2 >= ce_es M2 - 0.5, and Hcc vs Hbb not worse than ce_es by more than 0.005.
- **BEATS CE:** M1 above ce_es by more than 2 combined errors.
- **NOT RESCUED:** anything else.

Expectation stated in advance: at natural priors the minimiser of every v2 term is the same posterior plain CE estimates, so the realistic hope is parity with CE, keeping kappa's structure, plus better Hcc vs Hbb. Beating CE would need the fine term to help with only 2257 signal jets.

## Runs

Unit tests pass (`test_kappa_v2.log`). T4 smoke (600 iterations) ran both new arms end to end; alpha already ranked Hbb as the main look-alike (1.0, QCD 0.03). Submitted 2026-11-02 as condor cluster 9659969 (`~/flashjet_condor/kappa_rescue.sub`, outputs `htoww_replica/runs_rescue/`).

## Results

(pending)
