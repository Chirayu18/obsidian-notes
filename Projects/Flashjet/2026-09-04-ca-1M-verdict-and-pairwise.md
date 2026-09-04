---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# C/A on JetClass: the 1M verdict, why it failed, and the pairwise redesign

Supersedes the optimistic reading in [[2026-09-01-sd-run-and-convergence]].
Implementation background: [[2026-08-28-part-ca-features-implementation]].

## TL;DR

Per-particle C/A features give **no gain** on JetClass with paper ParT. The
earlier +1.3 and the 20k-iteration "all nine classes improve" result were both
transients, not durable effects. Feature *values* are provably correct — the
problem is that they carry **zero** prong-grouping information: measured group
size is exactly 1.00, because the ascending walk terminates at each particle's
own first merge. A pairwise redesign was built and then cancelled unrun, since
the same defect makes its `share_bp` channel a constant zero. The fix is
identified but not yet implemented.

## The matched test-set comparison (the decisive number)

Both arms at the **same 480k checkpoint**, same 20,049,152-jet JetClass test set.

| metric | baseline | C/A (5 per-particle) | Δ |
|---|---|---|---|
| test accuracy | **85.6251%** | 85.5235% | **−0.1016** |
| test loss | 0.4034 | 0.4062 | +0.0028 |
| mean 1-vs-QCD AUC | **0.98981** | 0.98970 | **−0.00011** |

Per-class AUC — **all nine worse**, including every decay-structure class:

| class | baseline | C/A | Δ |
|---|---|---|---|
| Tbl | 0.99997 | 0.99997 | 0.00000 |
| Hqql | 0.99990 | 0.99989 | −0.00001 |
| Hbb | 0.99888 | 0.99885 | −0.00003 |
| Tbqq | 0.99843 | 0.99837 | −0.00006 |
| H4q | 0.99344 | 0.99339 | −0.00005 |
| Hcc | 0.99416 | 0.99400 | −0.00016 |
| Wqq | 0.97790 | 0.97773 | −0.00017 |
| Zqq | 0.97464 | 0.97445 | −0.00019 |
| Hgg | 0.97100 | 0.97061 | −0.00039 |

This **directly contradicts** the 20k-iteration result recorded in
[[2026-09-01-sd-run-and-convergence]] (all nine improving, Tbqq rejection
1.75×). That was a real measurement of a transient: early in training the two
arms converge differently, and the difference vanishes as both train out.

Magnitudes are tiny and well inside the ~1.3-point seed spread, so the honest
claim is **"indistinguishable from baseline, with a consistent negative sign
across all nine classes and both metrics"** — not "C/A is worse".

## Why it fails: the features carry no grouping

Validated the actual feature *values* on 8192 real jets (never done before —
only the code path had been checked). `~/cawork/validate_ca_values.py`.

**Correctness: PASS.**
- 0 soft-side violations in 274,192 valid entries (`ln z` capped at exactly
  ln 0.5 = −0.693) — this is the assertion that would catch an inverted
  soft/hard assignment.
- No NaN/Inf; padded slots exactly zero.
- `ln z` mean −1.47 (z ≈ 0.23), physically sensible for soft emissions.

**But two structural problems:**

1. ~~22% of real particles have no branch point~~ — **WITHDRAWN.** That figure
   came from an offline script that sliced the lz4 file from column 0. The
   b-hive layout is `[15 global | 128x23 cpf | ...]` (authoritative:
   `model.create_feature_shapes()` gives `input_dims [(1,15),(128,23),...]`,
   `feature_edges [15, 2959, ...]`), so every offline diagnostic was misaligned
   by 15 columns and was clustering garbage. With the correct offset the inputs
   are clean: m^2 ~ +0.048 with 99.4% non-negative, constituents at dR mean
   0.198 / p95 0.580 from the jet axis, jet pt ~607 GeV, and **R=0.8 gives ONE
   C/A tree for 88-89% of jets**. The **training code was never affected** —
   `get_inpt` uses `x.split(self.feature_lengths)`, which strips the globals
   correctly, so the 1M results stand exactly as measured.
2. **Group size is exactly 1.00 — there is NO grouping at all.** This one
   survives the offset fix: re-measured on correctly-sliced data, rule A still
   gives group size 1.00 (32.9 groups for 32.9 particles). It was the right
   diagnosis, reached partly via wrong intermediate numbers.

   **Mechanism, traced leaf by leaf:** nearly every constituent is the *softer
   child at its very first merge* —
   ```
   leaf 3 : 3->54S    leaf 4 : 4->40S
   leaf 5 : 5->55S    leaf 7 : 7->43S
   ```
   In a C/A tree a single particle almost always merges into something larger
   than itself, so "am I the softer child?" is true immediately. The walk
   terminates at that particle's *own* first merge node, which is unique to it
   by construction. Two particles can never share one. Recording the parent
   (merge node) instead of the child does **not** help — still 1.00.

   The design assumed the walk would climb several levels and land on a shared
   prong-level node. **It never climbs at all.** The feature therefore never
   encoded "these were emitted together" — in either the per-particle or the
   pairwise formulation.

## Training-curve evidence, for the record

Matched validation accuracy, C/A − baseline, over 29 checkpoints:

```
-1.30 -0.46 +0.06 -0.78 -0.43 -0.10 -0.04 +0.02 -0.21 -0.06 +0.15 -0.05 -0.20
-0.22 -0.19 +0.18 -0.07 -0.03 -0.30 -0.10 -0.11 -0.58 -0.09 -0.03 -0.14 -0.10
-0.04 -0.02
```

Post-80k mean **−0.137 ± 0.200**, negative at **23 of 26** checkpoints. The
early convergence (−1.30 → parity by ~180k) is real but stops there; it
converges to *parity-minus-0.14*, not parity.

C/A is also behind on **training** accuracy at every recent checkpoint. That
matters diagnostically: a model with strictly more input information that were
merely harder to optimise should still eventually fit the training set as well.
Being behind on *fit* is the signature of features not being used.

C/A also runs ~1.8× noisier than baseline at matched iterations (detrended
residual std 0.456 vs 0.258; 2 of 8 checkpoint-to-checkpoint drops vs 0 of 8).
Consistent with the zero-spike: the fraction of `has_bp=0` particles varies
batch to batch, moving the BatchNorm statistics.

## The pairwise redesign (built, cancelled unrun)

Prong membership is not a per-particle quantity — "was this constituent emitted
in the same subjet as that one" is a statement about a **pair**. ParT already
has the right channel: `pair_embed` maps per-pair kinematics to (B,H,P,P) which
is **added to the attention logits of every block**.

`utils/flashjet_ca_pair_features.py` — widens the paper's 4 pairwise inputs
(ln kt, ln z, ln Δ, ln m²) to 6:

- **`share_bp`** — 1.0 if i and j merge into the harder core at the same C/A
  branch point. **MEASURED IDENTICALLY ZERO** (see the group-size finding
  above): with group size 1.00 no pair ever shares a branch point, so this
  channel is a constant-zero input. Dead as designed.
- **`lnkt_pair`** — ln k_T at the node where the two separate. **This one is
  fine.** Correlation against the paper's existing pairwise features is modest,
  so it is not redundant:

  | vs | r |
  |---|---|
  | `paper_lnkt` | +0.29 |
  | `paper_lndelta` | +0.28 |
  | `paper_lnm2` | −0.21 |
  | `paper_lnz` | −0.18 |

`utils/models/particletransformer_ca_pair.py` —
`ParticleTransformer_CAPair_JetClass`, subclasses the paper model.

**Clean single-variable test:** `cpf_dim` stays **21** — token inputs are
byte-identical to baseline (`ca_features: false` in `config/jet_class_capair.yml`).
Only +132 params (the two extra channels into `pair_embed`'s BatchNorm and first
Conv1d). C/A enters *only* through the attention bias.

Smoke test passed on real data (20 iters, `Normal termination`, luigi clean).

**The 1M CAPair run (cluster 9265165) was submitted and then KILLED while still
idle**, on discovering `share_bp` is constant zero — half its new signal was
dead, so it was not worth 37 GPU-hours. No GPU time was spent.

## The fix: RULE C (implemented, measured, smoke-testing)

Stop terminating at the first soft-side node. Climb until the soft branch holds
**>= 3 constituents** (`MIN_GROUP` in `utils/flashjet_ca_pair_features.py`), and
record the **parent** merge node so every constituent of that branch shares it.

Termination rules compared on 512 correctly-sliced jets:

| rule | %with bp | groups/jet | **mean group size** | max |
|---|---|---|---|---|
| A first soft (shipped) | 96.5% | 32.9 | **1.00** | 1 |
| B soft-child>=2 | 78.8% | 10.3 | 2.70 | 11 |
| **C soft-child>=3** | **65.4%** | **5.0** | **4.88** | **18** |
| D both-children>=2 | 77.5% | 9.3 | 2.96 | 11 |
| E kt>1GeV | 72.2% | 7.3 | 3.49 | 19 |
| F fixed depth 3 | 90.1% | 11.6 | 2.67 | 11 |

### The three pre-flight checks, rule C

**1 SPREAD** — group size 4.82, 6.5 groups/jet, 73.6% coverage,
**0 / 26279** violations of ln z <= ln 0.5.

**2 DISCRIMINATION** — passes, but *inverted* from the naive prediction. I
expected multi-prong classes to show MORE groups; they show **fewer**:

| class | grp/jet | vs QCD | mean lnkt |
|---|---|---|---|
| Tbqq | 3.97 | −2.92 | −2.99 |
| H4q | 4.47 | −2.42 | −2.09 |
| Zqq | 4.85 | −2.04 | −2.72 |
| **QCD** | **6.89** | — | −2.35 |
| Wqq | 8.47 | +1.58 | −1.46 |
| Hcc | 10.12 | +3.23 | −0.78 |

On reflection this is the right physics: a genuine 3-prong top has three
**coherent, massive** subjets, so the >=3 condition is met early at a few big
nodes; QCD is a diffuse soft cascade that fragments into many small clumps.
**Fewer, cleaner groups = real decay structure.** (Wqq at +1.58 breaks the
pattern and is unexplained.)

**3 REDUNDANCY** — `share_bp` density **9.6%** (was 0.000%), and linear
R^2 predicting it from all four of ParT's existing pairwise features is
**0.158**: not recoverable from what the model already sees. Per-class density
tracks the physics — H4q 13.50%, Tbqq 13.40% highest; Hcc 6.51%, Tbl 7.17%
lowest, QCD 7.87%.

Live-module verification after patching: group size 4.77, share_bp 8.79%,
0 NaN / 0 Inf.

Also fixed a latent bug in the same loop: `alive = step & ~at_root` should be
`step & ~found`, so particles never actually stopped once found. Present in the
original per-particle module too.

### Superseded reasoning

The earlier plan here — climb to a node with >=2 constituents "or a kt/mass
threshold" — is what became rule C, with >=3 chosen on the measurements above.
The LCA-matrix idea (ln kt at the lowest common ancestor, an ultrametric that
determines the tree exactly) was built and abandoned: its apparent failure
(76% of pairs "unjoined", 12/400 ultrametric violations) was **entirely the
column-offset bug**, so it is worth revisiting if rule C underdelivers. Code:
both formulations assumed all along.

Testable in minutes on CPU: `flashjet.cluster(..., backend="auto")` falls
through to the pure-torch backend with no CUDA, so the whole measurement runs
on an lxplus login node — no GPU, no queue. Harness:
`~/cawork/measure_pair_sparsity.py`.

## Two bugs caught before they cost anything

1. **69 GB allocation.** The obvious lowest-common-ancestor formulation compares
   every pair's ancestor path against every other: `(B,P,D,D)` bool = 69 GB at
   batch 512. Replaced with an O(B·N) form taking the deeper of the two branch
   points — *exact* for same-prong pairs (the case the feature targets), a
   conservative upper bound otherwise. Now 0.1 GB, smaller than the attention
   mask itself.
2. **Autograd graph through the tree walk.** `ca_pair_context` runs inside
   `forward`, so autograd recorded up to 128 loop iterations of gathers for
   gradients never used. Memory climbed 14 MB → 20.3 GB → 24.9 GB and was still
   rising when the job hit its wall clock. Fixed with `@torch.no_grad()` on both
   C/A functions — the tree has no learnable parameters.

## Standing caveat: the experiment cannot resolve small differences

The unseeded dataloader RNG (`utils/torch/LZ4Dataset.py:__iter__` calls
`np.random.permutation` / `np.random.rand` in workers with no per-worker seed
derived from `--seed`) gives a **~1.3-point run-to-run spread**. Baseline
plateau alone is 85.99 ± 0.22, peak-to-peak 0.62.

**With one seed per arm, nothing below ~1 point is resolvable in either
direction.** Fixing that seeding is a few lines and is the prerequisite for any
claim about a sub-point effect. 3–5 seeds per arm is the proper fix.

## Paths

Repo `/eos/user/c/cgupta/flashjet/b-hive` (commits `a28b40b` colleague's paper
ParT, `51db2c2` per-particle C/A; pairwise not yet committed).

Condor: `~/flashjet_condor/` (AFS), snapshot at
`/eos/user/c/cgupta/flashjet/flashjet_condor_afs_backup`.

ROC outputs @ 480k:
```
output/ROCCurveTask/jet_class/JetClass_train_100_mod/JetClass_test_mod/b_hive_paper_compile_4_at480k/...
output/ROCCurveTask/jet_class_ca/JetClass_train_100_mod/JetClass_test_mod/b_hive_paper_compile_4_ca_at480k/...
```

**Inferring any mid-run checkpoint without disturbing a live job:** copy
`model_N.pt` into a separate `<version>_atNk/` dir as both `model_N.pt` and
`best_model.pt`, then `law run ROCCurveTask --training-version <version>_atNk
--TrainingTask-total-iterations N`. luigi sees training as complete and goes
straight to InferenceTask → ROCCurveTask. (`InferenceTask` always loads
`best_model.pt` and requires a *complete* `TrainingTask`, so this is the way in.)

## Baseline reference numbers (1M, paper ParT)

Test accuracy **86.2117%**, macro OvR AUC (10-class) **0.98797**, mean of the
nine 1-vs-QCD AUCs **0.99029**. Reproduces the published ParT result (~86.1%
test, arXiv:2202.03772) on a genuine like-for-like basis.

From 480k → 1M the baseline gained only **+0.0005 mean AUC** — per-class
discrimination is near-saturated by 480k, so matched comparisons there are
already meaningful.
