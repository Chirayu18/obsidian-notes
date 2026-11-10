---
tags: [reference]
status: active
date: 2026-11-02
source: lxplus
---

# kappa-HCE rescue: diagnosis, v2 loss, pre-registered test

Follows [[Projects/Flashjet/kappa-hce/2026-10-07-kappa-hce-assessment|2026-10-07-kappa-hce-assessment]] (replica results f3a2509, checks 2510567).
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

## Amendment 2026-11-03, before any rescue result was read: held-out sets with the training balance

The validation and test sets above were the balanced JetClass sets (10% Hcc each) reweighted to the training priors. On request, no held-out set may have a different class balance from the training set. Validation with 20k Hcc jets also made checkpoint selection far better informed than a held-out split of the HToWW training data could be.

- **Test:** subsamples of the JetClass test set with class counts exactly proportional to the training counts, unweighted. QCD binds (r = 0.6289): 2,563,755 jets, 1419 Hcc. Twenty subsamples (`check/rescore_natural.py`, seeds 20261103+k), every run scored on the same ones.
- **Validation:** all QCD jets of JetClass_val, the other classes subsampled to the exact training proportions (`train_rescue.py` load_natural), about 355 Hcc. A checkpoint is saved at every validation point.
- **Metrics:** M1 = plain AUC of Hcc vs all background (one-vs-rest logit), M2 = S/sqrt(B) at 50% signal efficiency scaled to the training normalisation. Primary value = mean over the 20 test subsamples; error = seed spread / sqrt(3). The subsample spread is reported alongside.
- **Runs:** the 6 rescue runs that finished used the old validation for selection, so all 9 are rerun with the new validation (outputs `runs_rescue2/`). Their final weights, and all 15 original replica runs, are re-scored on the new test subsamples as a secondary, selection-free comparison.
- **Verdict rule:** unchanged (RESCUED / BEATS CE / NOT RESCUED as above), applied to the selected checkpoints of `runs_rescue2/`.

## Runs

Unit tests pass (`test_kappa_v2.log`). T4 smoke (600 iterations) ran both new arms end to end; alpha already ranked Hbb as the main look-alike (1.0, QCD 0.03). Submitted 2026-11-02 as condor cluster 9659969 (`~/flashjet_condor/kappa_rescue.sub`, outputs `htoww_replica/runs_rescue/`).

## Interim results (secondary, 2026-11-03)

Selection-free comparison: final weights, scored on the 20 training-balance test subsamples (`check/rescore_natural.json`). Mean over seeds; error is the seed spread / sqrt(n). The subsample spread in M1 is 0.0011 to 0.0024. The original 15 runs have 3 seeds, the first rescue runs 2 (seed 2 never ran under the first protocol).

| arm | weights | n | M1 | M2 | Hcc vs Hbb | Hcc vs QCD |
|---|---|---|---|---|---|---|
| ce | final | 3 | 0.98227 ± 0.00044 | 14.16 ± 0.45 | 0.9740 | 0.9848 |
| wce | final | 3 | 0.94342 ± 0.00309 | 6.93 | 0.9532 | 0.9698 |
| hier | final | 3 | 0.96331 ± 0.00058 | 8.11 | 0.9632 | 0.9731 |
| v20 | final | 3 | 0.97043 ± 0.00056 | 8.48 | 0.9241 | 0.9581 |
| kappa v1 | final | 3 | 0.97611 ± 0.00019 | 10.31 | 0.9437 | 0.9777 |
| ce_es | final | 2 | 0.98250 ± 0.00039 | 14.46 | 0.9741 | 0.9851 |
| k2n | final | 2 | 0.97576 ± 0.00006 | 11.44 | 0.9702 | 0.9793 |
| k2t | final | 2 | 0.96735 ± 0.00255 | 9.60 | 0.9621 | 0.9767 |
| ce_es | selected on old balanced val | 2 | 0.98337 ± 0.00059 | 14.80 | 0.9753 | 0.9857 |
| k2n | selected on old balanced val | 2 | 0.98321 ± 0.00027 | 14.45 | 0.9749 | 0.9856 |
| k2t | selected on old balanced val | 2 | 0.97764 ± 0.00061 | 11.52 | 0.9683 | 0.9832 |

**Findings:**
1. **The earlier conclusions survive.** The training-balance test reproduces the reweighted numbers (ce 0.98227 vs 0.98234 before; kappa v1 0.97611 vs 0.97609).
2. **v2 at natural priors (k2n) still overfits late.** It matches CE up to about 60k iterations (validation 0.9831 vs 0.9833, mean of 2 seeds), then falls to 0.9752 while CE stays at 0.9825. Its final weights are no better than kappa v1's.
3. **Why.** The confusability alpha settles on Hbb (2681 jets) as the signal's look-alike (alpha 1.0; QCD 0.02 to 0.09). So L_fine is effectively a second Hcc vs Hbb loss on about 5000 jets, and L_sig counts the signal again. Signal jets are counted about three times, a milder version of the same memorisation. Any term that adds emphasis on the 2257 signal jets overfits them.
4. **With early stopping, k2n reaches parity with CE** (0.98321 vs 0.98337) but does not beat it, and does not improve Hcc vs Hbb. Tempering (k2t, beta 0.5) is worse with or without early stopping.

These selected rows used the old balanced validation. The pre-registered verdict waits for `runs_rescue2/` (cluster 9662686, training-balance validation, 3 seeds).

## Results

(pending: runs_rescue2)


## 2026-11-10 — completed rescue2 scoring and verdict (agent-reported)

All nine runs have selected/final logits, truth and selection metadata. The Condor event log `~/flashjet_condor/output/kappa_rescue2.9662686.log` records normal termination, return value 0, for processes 000–008. A fresh `condor_q 9662686` returns no jobs. The completed `condor_history 9662686 -limit 9` query subsequently returned all nine completed records (see addendum below). No submission, resubmission or authentication renewal was performed in this continuation.

Scoring completed at 16:32 CET, 10 November, according to `/tmp/score_rescue2.json` mtime; `/tmp/score_rescue2.log` ends `DONE`. Preserved artifacts: [[Projects/Flashjet/kappa-hce/scoring/score_rescue2.py|scorer]] and [[Projects/Flashjet/kappa-hce/scoring/score_rescue2.json|all per-seed/per-subsample metrics]]. Inputs: `/eos/user/c/cgupta/flashjet/kappa_hce/htoww_replica/runs_rescue2/{arm}_s{seed}/`, files `hist.json`, `test_truth.npy`, `test_logits_selected_fp16.npy`, `test_logits_fp16.npy`.

The scorer uses the amended twenty paired training-balance subsamples (RNG 20261103+k), with r=0.6289096561845247 and counts [2000000,1686,1419,17908,43928,116323,23957,6770,37938,313826]. Per seed, average the twenty subsamples; then average the three seed values. Errors below are sample seed SD / sqrt(3), not uncertainty from independent test datasets. Subsamples overlap.

| Selected arm | M1 | M2 | Hcc vs Hbb | Hcc vs QCD |
|---|---|---|---|---|
| ce_es | 0.98305796 ± 0.00025549 | 14.51549374 ± 0.30565143 | 0.97457358 ± 0.00129747 | 0.98551326 ± 0.00016727 |
| k2n | 0.98272494 ± 0.00027264 | 14.01099157 ± 0.21560959 | 0.97472629 ± 0.00108331 | 0.98530288 ± 0.00022592 |
| k2t | 0.98010669 ± 0.00033646 | 12.43811055 ± 0.10802960 | 0.96837776 ± 0.00120331 | 0.98319390 ± 0.00018395 |

Selected iterations from `hist.json`: ce_es [90000,90000,60000], k2n [70000,60000,60000], k2t [50000,60000,60000]. ce_es/k2n use raw scores; k2t uses logits minus log(w), w=(max count/count)^0.5. Selected saved logits are raw, so this correction is applied once by the scorer. Selection remains by validation M1, as preregistered, not by test M2.

**Verdict: NOT RESCUED under the exact preregistered rule.** Better v2 arm k2n passes M1 (delta −0.00033302, allowed −0.0010) and Hcc-vs-Hbb (delta +0.00015271, allowed −0.005), but misses M2: 14.0109915741 versus CE 14.5154937362, delta −0.5045021621, allowed −0.5. The miss beyond the boundary is only 0.0045021621. This is a narrow rule failure, not strong evidence of a meaningful physical difference. Rounding M2 before applying the rule would hide the failure. k2t fails all three rescue conditions. Neither v2 arm beats CE on M1.

Subsample SD ranges across the three seeds: M1 ce_es 0.00112–0.00130, k2n 0.00105–0.00121, k2t 0.00134–0.00137; M2 ce_es 0.754–0.929, k2n 0.635–0.708, k2t 0.495–0.650. See JSON for secondary final-weight metrics.

### Evidence checks and scope

| Prescription | Implementation / check | Saved evidence | Status |
|---|---|---|---|
| Training-balance test; twenty shared subsamples | `score_rescue2.py`, same draws/counts as `check/rescore_natural.py`; truth-order assertion for every run | JSON r, take and twenty values per metric | Agent-reported; source inspected, scoring execution recovered |
| Validation-selected checkpoint / score | `train_rescue.py` saves raw selected logits; scorer consults `hist.json.selected` and applies k2t correction | JSON `sel` per run | Checked from source and recorded metadata |
| All nine completed | Parse Condor 005 normal-termination events | Event log path above, 000–008 exit 0 | Checked read-only on 10 November |
| Exact verdict | Aggregate seed means, sample SD/sqrt(3), compare unrounded deltas | JSON and table above | Checked locally; 21 score variants × twenty finite values for each of four metrics |

Remote/local scorer SHA256: `8caf371f0672aa62ea96788c13ee91fea73afc33edf1353b35d33b73dc66aab5`. JSON SHA256: `71e396273448253333d6430ee1bb502a9b86a1d9a9c495f6676dd88429714e7b`. Scorer avoids torch and reproduces the recorded numpy/sklearn metrics; no independent full rescoring or unit-test rerun was performed. Scores derive from saved fp16 logits, as specified by the available artifacts.

### HToWW event-weighted significance: separate, unresolved

Chirayu clarified on 10 November that the relevant HToWW metric is the **event-weighted S/sqrt(B) ratio**. This supersedes the older raw-count metric for answering that HToWW question. The Flashjet verdict above does not establish that kappa-HCE is worse on HToWW's intended metric.

The existing July mathematics note explicitly defines raw-count significance; the older assessment's HToWW audit likewise describes raw-count v20/v32 results and their shared training/evaluation events. Fresh source inspection in `/eos/user/c/cgupta/HToWW/b-hive` (HEAD `ce3bdd5e083b547450eee6a7513043be9e993b5b`, dirty checkout left untouched) finds `scripts/compare_significance.py` accepts weights but its main routine supplies inverse-frequency class-balancing weights. Its configured versions are v11 and two v18 arms, not a v20/v32 or working plain-CE comparison. `scripts/plot_v32_all.py` uses counts. These do not demonstrate the requested physics-event-weighted ratio.

Required evidence: intended saved comparison or definition of its ratio/reference and working points, plus corresponding held-out predictions and event weights. For a weighted comparison, S(t)=sum(signal passing weights), B(t)=sum(background passing weights); the signal-efficiency convention and weight signs/normalisation must follow the actual analysis prescription. Do not silently use class weights, raw counts, or a test-optimised threshold in its place. Even an in-sample weighted improvement would remain descriptive until checked on held-out events.

**Needs Chirayu:** identify the intended weighted plot/script or comparison versions (asked in-thread). No resubmission is needed. CMSSW use-case motivation and the requested b-hive PR remain pending this evidence; no claim of superiority, remote checkout edit, push or PR was made here. Training loss class weights and evaluation physics weights are separate choices; this clarification does not authorize changing the current class-only training scheme.


### 2026-11-10 follow-up — HToWW weighted comparison recovered

The unresolved HToWW artifact search above is superseded by [[Projects/HToWW/selection-and-mva/2026-11-10-kappa-hce-weighted-significance-recovery|the weighted-significance recovery]]. The saved v32-v9 versus CE v11 weighted cache favours κ-HCE (+14.42% Z ratio at nominal 50% count efficiency). It is a full-sample historical, 13-versus-six-class configuration comparison with signed weights and unresolved normalization/held-out provenance, not a matched loss-only validation. The Flashjet NOT RESCUED verdict is unchanged. Agent-reported.


### 2026-11-10 addendum — completed Condor history query

The background read-only command `ssh -o BatchMode=yes lxplus 'klist; tail -5 /tmp/score_rescue2.log; ls -l /tmp/score_rescue2.json; condor_q 9662686; condor_history 9662686 -limit 9'` completed with exit 0. Its final history output corroborates all nine runs as `C` (completed), all on 3 November. This corrects the earlier interim statement that history supplied no records; that statement preceded completion of the query. Event-log exit-zero checks and the scoring verdict remain unchanged. Agent-reported from the completed command output supplied in-thread.

| Condor process | Arm / seed | Completed 2026-11-03 (history display time) |
|---|---|---|
| 9662686.0 | ce_es 0 | 09:56 |
| 9662686.1 | k2n 0 | 09:54 |
| 9662686.2 | k2t 0 | 10:16 |
| 9662686.3 | ce_es 1 | 10:15 |
| 9662686.4 | k2n 1 | 10:18 |
| 9662686.5 | k2t 1 | 12:39 |
| 9662686.6 | ce_es 2 | 12:56 |
| 9662686.7 | k2n 2 | 13:18 |
| 9662686.8 | k2t 2 | 13:19 |
