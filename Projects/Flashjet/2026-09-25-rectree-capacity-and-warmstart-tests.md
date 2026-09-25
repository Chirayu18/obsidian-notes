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

## Test 2: warm-start fine-tune (running)

Script `lmkt/finetune_warm.py`, runner `~/flashjet_condor/run_finetune_warm.sh`, submit file `finetune_warm.sub`, condor cluster **9456493** (proc 0 = control, proc 1 = RecTree). Outputs in `lmkt/finetune/{warm_control,warm_rectree}/hist.json`.
- Both runs start from arm C `best_model.pt` and train 40k iterations: batch 512, AdamW, lr 1e-4 (10× for the new tree parameters), 1k warmup then cosine, bf16, seeded identical data order. **BatchNorm running statistics are frozen**; without that, 20 steps at batch 64 dropped accuracy from 0.856 to 0.73 in both arms.
- RecTree uses an opt-in **node gate**: a learnable per-layer, per-head attention bias on the node-token columns, initialised at −4. With it, the model starts at 0.8568 against arm C's 0.8555 on the same 4k validation jets; without it, it started at 0.65. In this mode the class blocks read the particles only. The gate is off by default, so the from-scratch v1 job is unaffected.
- Validation: 200k fixed val jets every 5k iterations; final: 50k test jets.
- Measure: RecTree − control at matched iterations.

From-scratch v1 (cluster 9455884) is **running** as of 2026-09-25 evening.
