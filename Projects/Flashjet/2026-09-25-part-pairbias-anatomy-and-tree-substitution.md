---
tags: [reference]
status: active
date: 2026-09-25
source: lxplus
---

# What ParT's pair bias does, and whether a merge tree can carry it

> **Corrected 2026-09-25:** all AUCs below use the **logit difference** (as b-hive's final_auc.py; see [[2026-09-06-logit-discriminant-bug]]) and arm A's `best_model.pt`, on 50k JetClass test jets. An earlier version used softmax-probability differences and `model_1000000.pt`; its substitution fractions were about 5 points too high (C/A 82–83% → 77%). The conclusions did not change.
> Logs: `lmkt/logs/{part_head_ablation_logit,tree_subst_logit}.log`; results `lmkt/results/*_logit.json`.

Context: the goal is a cheap clusterer (flashjet) whose tree replaces ParT's O(N²) pairwise attention bias. Arm C (no pair bias) is 1.35 points below arm A (86.21 test). See [[2026-09-24-nopair-arms-final]] and [[2026-09-24-lmkt-gnn-ceiling]].
All studies use arm A: ParT paper model, 1M iterations, `b_hive_paper_compile_4`, JetClass test.
Scripts are in `/eos/user/c/cgupta/flashjet/lmkt/`: `part_attn_tree.py`, `part_head_anatomy.py`, `part_head_ablation.py`, `tree_subst.py`.

## Where the pair bias wins (A vs no-bias arms, test AUC ×1e-4)

| class | C | E | F |
|---|---|---|---|
| Zqq | −31 | −27 | −26 |
| Wqq | −31 | −27 | −26 |
| Hcc | −19 | −16 | −15 |
| Hgg | −16 | −13 | −17 |
| H4q | −12 | −10 | −12 |

Hbb, Tbqq, Hqql and Tbl are within noise. So the target is the two-prong light-flavour classes.

## Head anatomy

U^h is the per-head pair bias, U^h = MLP(ln kT, ln z, ln Δ, ln m²). The same U^h is added to head h in all 8 particle layers.

**What each head responds to.** Every head is a smooth function of a single pair scale. For hard pairs, ln Δ, ln kT and ln m² are interchangeable (|Spearman| 0.84–0.98), and ln z is ignored.
- **Local heads** (larger U for close pairs): h4, h6, h7.
- **Far heads** (larger U for distant, high-mass pairs): h0, h2, h5, and weakly h1 and h3.

**Trees built from U^h** (pure linkage, JetClass label-free mass windows):
- The local heads give trees about as good as C/A and kt, but different trees: only 18–31% of jets have identical groomed prongs. Heads 6 and 7 are best on W/Z mass.
- The far heads give poor trees that sculpt QCD.
- No head beats C/A on top W pairing (0.30–0.43 vs 0.38). The truth-trained GNN tree reaches 0.58.

**Ablation** (flatten one head in the trained model; accuracy points, and AUC ×1e-4):

| head | type | acc | Zqq | Wqq | Hcc | Hgg | H4q |
|---|---|---|---|---|---|---|---|
| h5 | far | −14.0 | −178 | −142 | −50 | −74 | −71 |
| h0 | far | −11.1 | −141 | −134 | −34 | −125 | −105 |
| h6 | local | −10.3 | −60 | −62 | −81 | −40 | −49 |
| h3 | far | −10.0 | −125 | −165 | −178 | −147 | −71 |
| h1 | far | −4.5 | −47 | −43 | −19 | −27 | −34 |
| h7 | local | −2.9 | −41 | −49 | −25 | −36 | −33 |
| h2 | far | −1.1 | −22 | −25 | −19 | −9 | −7 |
| h4 | local | **0.0 (unused)** | 0 | 0 | 0 | 0 | 0 |

Flattening all heads costs 38.7 points. That measures how much the trained model depends on the bias, not how much information the bias holds; arm C, trained without it, loses only 1.35.

## Tree substitution (the key result)

Replace all U^h by a function of each pair's lowest common ancestor (LCA) in a tree, inside the trained ParT, with no retraining. 50k test jets.

| variant | acc | Zqq | Wqq | Hcc | Hgg | H4q | Z/W/Hcc/Hgg flat-loss recovered |
|---|---|---|---|---|---|---|---|
| true U (baseline) | 0.862 | 0 | 0 | 0 | 0 | 0 | 100% |
| flat | 0.530 | −398 | −403 | −233 | −248 | −514 | 0% |
| **C/A, node-mean of U (oracle)** | **0.808** | −89 | −74 | −38 | −90 | −49 | **77%** |
| **C/A, f(LCA ln kT, ln Δ, ln m², z)** | **0.803** | −88 | −78 | −39 | −90 | −51 | **77%** |
| GNN pure tree, f | 0.801 | −98 | −92 | −41 | −98 | −57 | 74% |
| GNN LM-kT, f | 0.797 | −116 | −100 | −45 | −101 | −60 | 72% |
| kt, f | 0.790 | −129 | −124 | −72 | −124 | −81 | 65% |
| each head's own U-tree (oracle) | 0.578 | −252 | −239 | −77 | −189 | −193 | 41% |

In accuracy, C/A with f recovers (80.3 − 53.0)/(86.2 − 53.0) = **82%** of the flat-bias loss.
Fit quality R² of f(LCA kinematics) per head: C/A 0.45–0.83, GNN pure 0.30–0.79, LM-kT 0.37–0.77, kt 0.21–0.71.

**Caveat on the percentages:** this is a *frozen* trained model. The flat-bias loss (−33 points) measures how much this model depends on its bias, not how much information the bias carries; arm C, trained without it, is only 1.2 points below A on the same jets. So "77%" means "the trained model's bias is mostly a function of the C/A common ancestor", not "a tree recovers 77% of the A−C gap".

## Conclusions

1. **ParT's pair bias is, to about 77% (AUC) / 82% (accuracy), a function of the pair's C/A common-ancestor node:** "how high, and at what mass, did i and j split". The far heads are "attend across high C/A nodes", the local heads "within low ones".
2. **The realisable encoding** (a function of LCA kinematics) loses almost nothing relative to the node-mean oracle.
3. **The clusterer choice matters little, and C/A is best.** Learned trees (LM-kT, GNN) do not help. The answer is a better *use* of the tree, not a better tree. This is consistent with LM-kT improving top (where the bias doesn't matter) and not Z/W.
4. **Why arm C failed:** it gave per-particle branch-point features. Pairwise LCA information cannot be expressed by q·k of per-particle embeddings.
5. **GNN v3** (jet pT and mass as IRC-safe inputs) improves the pair model (val loss 0.147 → 0.124) but not the tree (top W pairing 0.655 → 0.660). The tree-building step is the bottleneck, not the pair model.

## Next (proposed 2026-09-25, awaiting go)

- **Truncation check:** substitution with the tree cut at K = 2/4/8/16 subjets, to choose between a single cut and multi-scale.
- **Subjet-token ParT arm** (user's idea: "merge the inputs by the tree"): arm C + K C/A subjet tokens (pooled members) with a subjet-pair bias, plus particle↔subjet membership. O(N·K + K²). Compare with A (86.2) and C (84.6).
- Also on hold: G2 (rank-K membership bias), and gen-tree v3 (full Pythia history with the hadronization rule).
