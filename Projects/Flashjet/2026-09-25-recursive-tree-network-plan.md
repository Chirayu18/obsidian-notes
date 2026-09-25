---
tags: [plan]
status: active
date: 2026-09-25
source: lxplus
---

# Plan: recursive merge-embedding network (RecTree ParT)

Why this, now: [[2026-09-25-part-pairbias-anatomy-and-tree-substitution]].
- ParT's pairwise bias is about 80% a function of each pair's **C/A common-ancestor node**. Replacing it by f(LCA ln kT, ln Δ, ln m², z) inside the trained ParT recovers 82% of the Z/W/Hcc/Hgg loss.
- **C/A is the best tree**; learned trees do not help. So the lever is **how the tree is used**, not a better tree.
- Per-particle tree summaries cannot carry pairwise information (arm C: −1.35 points).
- A subjet arm with the pair bias on was null (86.191 vs 86.212), so subjet information is redundant *given* the bias.

**Goal:** a network where the C/A tree itself builds the representation, so ParT **without** the O(N²) pair bias recovers most of the gap between C (84.6 test) and A (86.2 test), especially for Zqq, Wqq, Hcc, Hgg and H4q.

## 1. Architecture

**Tree.** flashjet C/A with R = 10 (one tree per jet), computed in the forward pass with no gradients and excluded from torch.compile. Cost: about 4 ms per 512 jets (Triton).

**Leaves.** e_i = ParT's own token embedding of particle i (128-d). Gradients flow into it.

**Merge recursion.** Bottom-up, in C/A merge order:

    e_p = e_a + e_b + λ · MLP([e_a, e_b, φ_s]),   a = harder child, b = softer child
    φ_s = (ln kT, ln z, ln ΔR, ln m_p, ln pT_p/pT_jet, ln m_a, ln m_b)   (LayerNorm)

- This is the "carried state" of the LM-kT spec, made nonlinear (no IRC requirement).
- With λ = 0 it is exact subtree sums, which the test pins. λ starts at 0.1, which keeps 127 levels stable.
- It is implemented as a replay over **slots**, like the clustering loop: at most N−1 batched steps, and autograd keeps only (B, d) tensors.

**v1: node tokens.** Add K node tokens: the root plus the K−1 internal nodes with the largest ln kT (the hardest splittings), each with a type embedding. Every particle token also gets a projection of its **nearest selected ancestor's** embedding ("which hard subtree am I in").
- No pair bias anywhere, so attention stays flash compatible.
- The class-attention blocks read particles and nodes.

**v2: hybrid.** v1 plus a **tree positional encoding** for every particle: its root-to-leaf path, with one slot per depth for the hard splittings, carrying ±(which child) × v(split features). Then q_i·k_j can recover "at which node, and at what scale and mass, did i and j split" for **every** pair (full-tree common-ancestor information at O(N·d)). v1 delivers only the top-K nodes.

**What even v2 does not deliver:** exact particle-pair kinematics (ln kT_ij, ln Δ_ij, ln m²_ij) inside the attention. That is the part the pair bias pays O(N²) for, roughly the ~18% the substitution test did not recover.

## 2. Status of the code

| piece | where | state |
|---|---|---|
| recursion, context, node selection, nearest-ancestor | b-hive `utils/flashjet_tree_embed.py` (new, uncommitted) | **written and tested** |
| tests (additive = subtree sums; batched == per-jet recursion; ancestor lookup) | `/eos/user/c/cgupta/flashjet/lmkt/test_tree_embed.py` | **pass** |
| flashjet `_pseudojet_p4` padding fix (needed by the above) | flashjet `lmkt` branch, `46e566d` | done; see [[2026-09-25-flashjet-pseudojet-p4-padding-bug]] |
| b-hive model `ParticleTransformer_RecTree_JetClass` | b-hive `utils/models/particletransformer_rectree.py` | **to do** |
| config / runner / condor submit | `config/jet_class_rectree.yml`, `run_paper_rectree.sh`, `condor/paper_rectree.sub` | **to do** |

The model subclasses the no-pair model (`particletransformer_nopair.py`). It uses the **plain `jet_class` inputs**, with no dataset changes and no C/A columns. The tree is computed from the cpf four-vector columns.

## 3. Checks before any long run

1. **Gradient check:** the loss backpropagates into the token embedding through the recursion (a nonzero gradient on e_i for particles deep in the tree).
2. **Smoke test:** 20 iterations on real JetClass, for both eager and torch.compile. The loss must drop and accuracy must rise above random (capair's smoke run stayed at 0.10).
3. **Timing and memory** on an H100 (condor) or the T4 (lxplus905): iterations per second against arm C (11.3 it/s), plus the recursion's share of the step. If the recursion costs more than about 40% of the step, apply CUDA graphs to the loop, or batch merges by tree depth.
4. **Show the user** the smoke, timing and memory numbers **before launching**.

## 4. Experiment ladder

Every run matches arm A/C settings: JetClass_train_100_mod, batch 512, Ranger with learning rate 1e-3, the same schedule, torch.compile, and val = JetClass_val_mod.

| run | what | question | cost |
|---|---|---|---|
| **R0** | pure recursive network: classify from the root embedding only (standalone, T4, about 2M jets) | how much does the recursion alone capture? | a few hours on the T4 |
| **R1** | no-pair ParT + v1 node tokens (K = 16) | does it close the C→A gap? | 200k iterations first (~6 h), then 1M |
| **R2** | no-pair ParT + v2 hybrid (node tokens + tree positional encoding) | does full-tree LCA information add over top-K? | 200k, then 1M |
| R3 (optional) | paper ParT (bias on) + v1 node tokens | does the recursion add anything *on top of* the bias? (the arm D analogue) | 1M |

**Short-run decision rule:** compare validation accuracy at 200k iterations against the **existing** A and C curves (checkpoints every 20k, `~/flashjet_condor/summary.py`), so no baseline reruns are needed.
- Gap closed f = (R − C)/(A − C), averaged over the late checkpoints.
- **f ≥ 0.3:** extend to 1M.
- **f < 0.1:** stop and report.
- In between: run the cheapest ablation (K or v2) before deciding.

**Ablations** (only for whichever of R1/R2 wins):
- K ∈ {4, 8, 16, 32};
- node selection: top-kT vs groomed (z > 0.1) declustering;
- λ = 0 frozen, i.e. pure pooling, which isolates the value of the nonlinear merge;
- tree C/A vs kt vs LM-kT (the substitution test predicts C/A is best).

**Final metrics:**
- test accuracy and per-class AUC vs QCD, with deltas against A in units of 1e-4 (noise floor about 10);
- Herwig robustness (JetClass_herwig_test_mod);
- cost: iterations per second, memory, and inference latency.

## 5. Risks and mitigations

- **Loop speed.** Up to 127 sequential steps. Mitigation: CUDA graphs, depth batching, or capping the recursion at the hardest M merges (merge soft stuff additively).
- **torch.compile would unroll the 127-step loop** (long compile time). Mitigation: `torch._dynamo.disable` on the recursion, as for the clustering, and compile the rest.
- **Deep gradients** through 127 levels. The sum + small-λ correction form is stable; check gradient norms in the smoke run.
- **The padding-at-end assumption** is asserted in `tree_context`. JetClass is padded at the end.
- **flashjet version.** b-hive imports the working tree, now on the `lmkt` branch with the pseudojet fix. Record the flashjet commit in every run log.

## 6. Parked (not dropped)

- Truncation check (substitution with the tree cut at K = 2/4/8/16).
- Subjet-token arm (option 1).
- G2 rank-K membership.
- Gen-tree v3: full Pythia history.
- Quantify the pseudojet bug's impact on arms C/D/F/subjet.
- The v2 ancestry-label Pythia generation (`lmkt/data2/`, running in tmux `lmktgen2` on lxplus914).

## 7. Open decisions for the user

1. **v1 first, or go straight to v2 (hybrid)?** Recommendation: build v1 plus the smoke and timing checks. If that is cheap, run R1 and R2 at 200k in parallel.
2. K = 16 as the default?
3. Compute: condor H100 (matches A and C, but queues) or the lxplus905 T4 (immediately available, but a T4 run is not comparable in iterations per second)? Recommendation: condor for R1/R2, the T4 for R0 and the smoke tests.
