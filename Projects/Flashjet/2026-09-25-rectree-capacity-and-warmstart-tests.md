---
tags: [reference]
status: active
date: 2026-09-25
source: lxplus
---

# RecTree cheap tests: capacity ceiling (test 1) and warm-start fine-tune (test 2)

Context: [[2026-09-25-recursive-tree-network-plan]], [[2026-09-25-part-pairbias-anatomy-and-tree-substitution]].
Asked for as a cheap alternative to waiting on 200k-iteration from-scratch runs.

## Test 1: can v1 / v2 express ParT's pair bias? (done)

Frozen arm A (best_model), the same 50k test jets as the substitution test, logit AUCs. U^h is replaced by what each design can represent. The tree is RecTree's own (flashjet C/A, R = 10).
Script `lmkt/capacity_ceiling.py`; log `lmkt/logs/capacity_ceiling.log`; results `lmkt/results/capacity_ceiling.json`.
"Recovered" is the fraction of the flat-bias loss recovered: in AUC on Zqq+Wqq+Hcc+Hgg, and in accuracy.

| variant | acc | Zqq | Wqq | Hcc | Hgg | recovered (AUC) | recovered (acc) |
|---|---|---|---|---|---|---|---|
| baseline (true U) | 0.862 | 0.9756 | 0.9781 | 0.9944 | 0.9719 | 1 | 1 |
| flat | 0.529 | 0.9354 | 0.9376 | 0.9711 | 0.9469 | 0 | 0 |
| full tree, LCA oracle (sanity: = earlier C/A 77%) | 0.808 | 0.9667 | 0.9708 | 0.9906 | 0.9629 | 0.77 | 0.84 |
| v1 block oracle K=4 | 0.705 | | | | | 0.50 | 0.53 |
| v1 block oracle K=8 | 0.793 | | | | | 0.77 | 0.79 |
| v1 block oracle K=16 | 0.836 | | | | | 0.91 | 0.92 |
| v1 block oracle K=32 | 0.850 | | | | | 0.95 | 0.96 |
| **v1 realisable (rank-16 bilinear of ancestor-node features), K=16** | 0.614 | 0.9339 | 0.9330 | 0.9759 | 0.9519 | **0.03** | 0.25 |
| **v2 realisable (rank-16 bilinear of tree positional encoding), M=16** | 0.707 | 0.9508 | 0.9555 | 0.9803 | 0.9532 | **0.38** | 0.54 |
| v2 realisable, M=32 | 0.701 | | | | | 0.37 | 0.52 |
| v2 realisable, M=all nodes | 0.693 | | | | | 0.35 | 0.49 |

Fit R² per head: v1 0.17–0.33; v2 0.30–0.54, **except h3 ≈ 0 in every v2 fit.** h3 is an important far head (flattening it costs 10 accuracy points).

**Reading:**
1. **The block oracles are not a fair ceiling.** They average the true U per jet over (K+1)² blocks: about 290 blocks at K=16, for jets of about 40–60 particles. That is close to a lookup of U itself. Only the realisable (fitted, shared across jets) rows count.
2. **Pairwise, v1 carries almost nothing (3%).** "Which hard subtree is each particle in" cannot reproduce the bias through a q·k form. v1's other channel, particles attending *to* node tokens, is not a pair bias and is not measured here. The v1 training run tests that channel.
3. **v2 recovers about 37%,** 10× v1 and about half of the arbitrary f(LCA) function's 77%.
4. **More nodes do not help v2** (M = 16, 32 and all are the same). The limit is the **rank-16 bilinear form of a summed path encoding**, not tree depth. An arbitrary function of the LCA kinematics reaches 77%; a q·k of per-particle encodings reaches about 37%.
5. **This is a lower bound for the real network.** The fits see only tree information (no particle features), use one layer and a fixed rank. In the trained model the encoding mixes with particle features across 8 layers.

**Implication:** v2 is clearly better than v1 as a carrier of the pair bias, but even v2 is unlikely to match A through the attention logits alone. If v2 is built, the encoding should be richer than a single signed sum: per-depth slots (concatenated, not summed), so that q·k can pick out the LCA depth.

## Test 2: warm-start fine-tune (done 2026-09-26)

Script `lmkt/finetune_warm.py`, runner `~/flashjet_condor/run_finetune_warm.sh`, submit file `finetune_warm.sub`, condor cluster **9456493** (proc 0 = control, proc 1 = RecTree). Outputs in `lmkt/finetune/{warm_control,warm_rectree}/hist.json`.
- Both runs start from arm C `best_model.pt` and train 40k iterations: batch 512, AdamW, lr 1e-4 (10× for the new tree parameters), 1k warmup then cosine, bf16, seeded identical data order. **BatchNorm running statistics are frozen**; without that, 20 steps at batch 64 dropped accuracy from 0.856 to 0.73 in both arms.
- RecTree uses an opt-in **node gate**: a learnable per-layer, per-head attention bias on the node-token columns, initialised at −4. With it, the model starts at 0.8568 against arm C's 0.8555 on the same 4k validation jets; without it, it started at 0.65. In this mode the class blocks read the particles only. The gate is off by default, so the from-scratch v1 job is unaffected.
- Validation: 200k fixed val jets every 5k iterations; final: 50k test jets.
- Measure: RecTree − control at matched iterations.

**Result** (200k val jets; control / RecTree):

| iteration | acc | Zqq | Wqq | ΔAUC Z / W (1e-4) |
|---|---|---|---|---|
| 0 | 0.8475 / 0.8471 | 0.9720 / 0.9719 | 0.9756 / 0.9755 | −1.1 / −0.9 |
| 20k | 0.8446 / 0.8447 | 0.9717 / 0.9719 | 0.9752 / 0.9753 | +2.4 / +1.2 |
| 40k | 0.8453 / 0.8463 | 0.9718 / 0.9721 | 0.9753 / 0.9755 | +3.6 / +2.4 |

On 50k test jets: acc 0.8470 → 0.8476; Zqq +1.3e-4, Wqq +2.4e-4. The gain is consistent in sign from 15k iterations on, but it is small: about +0.1 accuracy points and +3e-4 on Z/W, **about 10% of the A−C gap**.

## From-scratch v1, 1M iterations (cluster 9455884, done)

Full JetClass test set (20M jets), logit AUCs, via `~/flashjet_condor/rectree_auc.py` (reuses final_auc.py):

| | acc | Hcc | Hgg | H4q | Zqq | Wqq | Tbqq |
|---|---|---|---|---|---|---|---|
| A (pair bias) | 86.212 | 0.99465 | 0.97194 | 0.99393 | 0.97567 | 0.97899 | 0.99862 |
| C (no pair, C/A cols) | 84.862 | 0.99278 | 0.97031 | 0.99268 | 0.97253 | 0.97592 | 0.99825 |
| **RecTree v1** | **84.955** | 0.99333 | 0.97039 | 0.99284 | 0.97365 | 0.97692 | 0.99817 |
| R − C (1e-4; acc in points) | +0.09 | +5.5 | +0.8 | +1.6 | **+11.2** | **+10.0** | −0.8 |
| A − C | +1.35 | +18.7 | +16.3 | +12.4 | +31.4 | +30.7 | +3.7 |

- **Gap closed:** 7% in accuracy; about 35% on Zqq and Wqq (the target classes), but only at the ~10e-4 noise floor; 29% on Hcc; about 0 on Hgg and H4q.
- Validation curve: f = (R − C)/(A − C) = 0.13 averaged over 120–200k iterations and 0.09 over 820k–1M. By the §4 rule (< 0.1: stop), this is a stop.
- **Cost: 9.6 it/s, slower than arm A (11.2) and C (20.8)** on the H100 (28.8 h vs 24.9 h vs 13.4 h for 1M). So v1 is neither better nor cheaper than the pair bias.

**Verdict on v1:** a small, consistent gain concentrated where the pair bias matters (Z/W, Hcc), which matches the capacity test (v1 carries about 3% of the pair bias pairwise; the rest must come from node-token attention). It does not justify its cost. Test 1 says v2 carries about 10× more; building v2 is the only remaining RecTree option, and even that is capped at about 37% by the q·k form.

## RecTree v2 submitted (2026-09-29)

At the user's request, v2 was submitted directly. The per-depth capacity re-test (the proposed step 1) was skipped.
- **Model:** `ParticleTransformer_RecTree2_JetClass`, b-hive `utils/models/particletransformer_rectree2.py`. It is v1 plus a **per-depth tree positional encoding**: for each particle, its chain of selected ancestors (the M = 32 hardest splittings) from the root; slot d = ±(harder/softer child) × g(φ of the depth-d node); 16 slots, rank 16, **concatenated**, then a zero-initialised Linear to d = 128, added to the particle token. At initialisation it is exactly v1. v2 − v1 isolates the encoding.
- **Tests:** `lmkt/test_rectree2.py`: every (particle, slot) entry matches a brute-force per-jet walk of the tree (M = 8/32, D = 16/4). The v1 tests (`test_tree_embed.py`) still pass.
- **Smoke (T4, batch 128):** v2 learns both eager and compiled (loss about 2.6 → 2.25); the gradient reaches `pe_proj`. The first compiled step took 5.5 s from recompiling on per-batch ints, so the encoding now runs outside torch.compile (`@torch._dynamo.disable`). After the fix: 333 ms per step, with no recompiles (the T4 was shared, so the relative timings are not meaningful).
- **Condor cluster 9472742:** `~/flashjet_condor/paper_rectree2.sub` → `run_paper_rectree2.sh`, version `b_hive_rectree_v2`, config `jet_class_ca`, 1M iterations, identical to v1 and arm C otherwise. Compare with A / C / v1 using `~/flashjet_condor/rectree_auc.py` (add the v2 arm).

## B2 (pair features + common-ancestor bias) vs earlier arms: checked 2026-09-30

The proposed B2 is arm A plus an additive attention bias T[layer, head, LCA(i, j)] over the exact full C/A tree. Its closest precedent is **CAPair** ([[2026-09-11-plum-final-verdict]], [[2026-09-04-ca-1M-verdict-and-pairwise]]). Differences, read from `utils/flashjet_ca_pair_features.py`:
- **CAPair's "LCA" is not the pair's lowest common ancestor.** Each particle has one branch point (rule C: climb until the soft branch holds ≥ 3 constituents). The pair value is taken at the *deeper of the two particles' own branch points* ("exact whenever the two leaves are in the same prong ... a conservative upper bound otherwise"). For a cross-prong pair, it therefore points inside one prong, not at the node where the two prongs split. Pairs where either particle lacks a branch point get 0: channel density 59.4%.
- **CAPair's channels:** share_bp, ln kT at that node, and log1p(depth), fed through the same pair MLP as the 4 kinematic inputs; one static bias for all layers. B2 would use the node's full φ (including mass and child masses) plus the current layer's subtree token sum, per layer and head.
- **CAPair never reached convergence.** Cluster 1123266 wrote checkpoints to 80k only (last file 2026-09-16 02:23; val accuracy vs baseline −0.239, −0.264, −0.090, −0.041 pp at 20–80k). No later checkpoint and no test inference exist; why it stopped is not recorded.
- **PLuM** (Lund splitting tokens, pair bias on) is a different mechanism: tokens rather than a bias, and 2-body splitting kinematics. At 1M: −0.006 test accuracy vs baseline.
