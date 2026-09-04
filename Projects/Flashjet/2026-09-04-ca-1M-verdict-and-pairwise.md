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

**3 REDUNDANCY** — `share_bp` density **9.6%** (was 0.000%). I first reported
linear R^2 = 0.158 as "not recoverable from what the model already sees".
**That was wrong, and the error was mine**: `share_bp` is a binary at ~8%
prevalence, where R^2 is close to meaningless — a predictor can rank almost
perfectly while explaining little variance. Measured properly (AUC), see the
kill-check below.

Live-module verification after patching: group size 4.77, share_bp 8.79%,
0 NaN / 0 Inf.

Also fixed a latent bug in the same loop: `alive = step & ~at_root` should be
`step & ~found`, so particles never actually stopped once found. Present in the
original per-particle module too.

## The two kill-checks — RULE C DOES NOT SURVIVE THEM

Run before spending GPU-hours, precisely because "it passes the pre-flight
checks" had already been wrong twice. 1536 jets, 1.37M pairs.

### A. Nonlinear redundancy — can ParT already compute share_bp?

| predictor (from the 4 paper pairwise features) | AUC |
|---|---|
| linear | **0.8659** |
| 2x64 MLP | **0.8664** |

`share_bp` is recovered at **AUC 0.87 from what the model already sees**. The
MLP adds nothing over linear (+0.0005), so the relationship is essentially
linear in those features — the information is present, not hidden behind a
nonlinearity attention would have to discover.

This also retro-invalidates the "check 3 passes" verdict above: R^2 = 0.158 and
AUC = 0.866 are the *same fit*, and only the second one answers the question.

### B. Multiplicity control — is the class separation just n_const?

```
corr(groups/jet, n_const) = +0.9227
```

The headline separation (Tbqq 3.97 .. Hcc 10.12, raw spread 6.15) is **92%
correlated with constituent count**, which ParT observes directly. At fixed
n_const the spread collapses:

| n_const bin | njets | groups/jet spread | share_bp density spread |
|---|---|---|---|
| [0,25) | 249 | 1.22 | 9.93 pp |
| [25,35) | 377 | 1.39 | 5.36 pp |
| [35,45) | 361 | 0.86 | 2.23 pp |
| [45,200) | 549 | 2.51 | 1.66 pp |

The pairwise density holds up better (corr with n_const only −0.37) and keeps
real spread in LOW-multiplicity jets, but fades to ~1.7 pp by the highest bin.
One stable non-multiplicity effect: **Tbl is the lowest-density class in every
bin** — though Tbl already sits at AUC 0.99997 and needs no help.

### Verdict

Estimate for rule C helping at 1M: **10-15%** (down from ~30% before these
checks). The smoke test (cluster 9265167) was killed while still idle.

**Mechanism for the whole three-attempt null result:** the C/A tree, summarised
either per-particle or per-pair, is largely reconstructible from the pairwise
kinematics ParT's attention already computes. That is *why* every encoding has
landed at parity — not a bug in any of them.

## The defensible result for the talk

The negative is quantified and genuinely interesting, which the raw
"no improvement" was not:

> C/A merge-history features do not improve ParT on JetClass. The attention
> mechanism already reconstructs equivalent information from raw pairwise
> kinematics — a 4-input MLP recovers the C/A same-prong flag at AUC 0.87 — and
> the apparent class discrimination of tree-derived features is ~92% explained
> by constituent multiplicity, which the model observes directly.

Supporting evidence: matched 480k test-set comparison (all nine classes within
±0.0004 AUC), 1M training curves at parity-minus-0.14, and the measured
group-size failure of the original encoding.

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


## Direction 2: SUBJET-level features — the one encoding that passes

Reasoning after the three failures: every encoding so far reduced the tree to
something evaluated on ONE pair or ONE particle, and a pair-local summary is
measurably a near-function of that pair's own kinematics. A **subjet invariant
mass is a sum over a SET the model must first identify** — a different kind of
object, not obviously a function of any pair's Lund variables.

Construction: decluster with a hard k_T cut; each constituent's subjet is the
node it reaches before the next merge would exceed the cut. Per-particle
targets are then broadcast (`sj_lnm`, `sj_lnptfrac`, `sj_nconst`).

### Redundancy probe — predict the target from ParT's own per-particle inputs

Inputs: the particle's 19 token features + pooled n_const + ln jet p_T.
A **control** (the particle's own ln p_T fraction, a literal input column)
calibrates what "redundant" looks like on this data.

| target | linear R² | MLP R² |
|---|---|---|
| **CONTROL** own ln p_T frac | 1.0000 | **0.9461** |
| **subjet ln mass** | 0.0443 | **0.0519** |
| subjet ln p_T frac | 0.1924 | 0.1904 |
| subjet n_const | 0.0498 | 0.0642 |

Subjet mass at R² = 0.05 against a control of 0.95: essentially unrecoverable.
Contrast `share_bp` at AUC 0.87.

### k_T-cut scan — the result is robust, not tuned

| k_T cut | subjets/jet | subjet ln m (MLP R²) | corr(lead m, n_const) |
|---|---|---|---|
| 5 GeV | 8.17 | 0.0507 | +0.14 |
| 10 GeV | 6.24 | 0.0519 | +0.19 |
| **20 GeV** | **5.06** | **0.0509** | **+0.23** |
| 40 GeV | 3.73 | 0.0391 | +0.27 |

R² sits at 0.04–0.05 at *every* cut. Multiplicity correlation rises with the
cut but stays far below the +0.92 that killed `groups/jet`.

### Class separation survives the multiplicity control

Lead-subjet mass at fixed n_const, k_T = 20 GeV:

| n_const bin | spread | high | low |
|---|---|---|---|
| [0,25) | 44.6 GeV | Tbqq 85.5 | Hbb 40.9 |
| [25,35) | 37.7 GeV | Tbqq 91.6 | QCD 53.9 |
| [35,45) | 42.7 GeV | Tbqq 96.2 | Hbb 53.5 |
| [45,200) | 43.8 GeV | Hgg 101.9 | Tbqq 58.1 |

**Tbqq tops three of four bins**, at 85–96 GeV — a hadronic top's leading
subjet carrying the W mass is exactly the expected physics, and it sharpens as
the cut hardens (85–112 GeV at 40 GeV). Unexplained: the highest-multiplicity
bin inverts at every cut (Hgg/QCD above Tbqq).

### Scorecard vs the killed encodings

| criterion | share_bp (killed) | subjet mass |
|---|---|---|
| recoverable by MLP? | AUC 0.87 | **R² 0.05** |
| multiplicity proxy? | corr +0.92 | **corr +0.19** |
| robust to threshold? | n/a | **yes, 4 cuts** |

### Caveats before spending compute

- The probe is **per-particle**. A set model — which ParT's attention
  effectively is — could recover subjet mass better than a per-particle MLP.
  This is the honest limit of what has been tested, and it is the same class of
  argument that was wrong twice tonight.
- The measured form is the **per-particle broadcast** (3 columns). The
  subjet-*token* architecture sketched earlier is a different, unvalidated
  configuration.
- One seed per arm still cannot resolve a sub-1-point effect. 3 seeds at 400k
  is the right configuration, not 1 seed at 1M.

Scripts: `/tmp/check_subjet.py` (probe + scan), `~/cawork/` for the earlier
harnesses.


## SET-MODEL PROBE — the outstanding objection, finally tested

Every redundancy probe up to here fed a SINGLE particle's features to an MLP.
But ParT's attention **pools over all 128 constituents**, so "a per-particle MLP
can't predict it" was the wrong bar — and that exact gap is what made the
`share_bp` verdict wrong twice.

Fair test: a DeepSets-style permutation-invariant model with access to the whole
constituent set. A lower bound on what attention could learn, from the same
information ParT has.

| model | test R² |
|---|---|
| per-particle MLP | 0.0719 |
| **DeepSets (pooled context)** | **0.1079** |
| DeepSets (+ relative to pooled mean) | 0.1067 |
| *CONTROL: own ln p_T frac, a literal input column* | *0.95* |

Full-set access raises recovery from 0.07 to **0.11**. Pooling barely helps.
Subjet mass is genuinely not computable from what ParT sees.

### Final scorecard

| criterion | share_bp (killed) | subjet mass |
|---|---|---|
| per-particle recovery | AUC 0.87 | R² 0.07 |
| **set-model recovery** | *never tested* | **R² 0.11** |
| multiplicity proxy | corr +0.92 | corr +0.19 |
| threshold-robust | n/a | yes, 4 cuts |

## IMPLEMENTATION (built, verified, smoke-testing)

`utils/flashjet_subjet_features.py` — `N_SUBJET_FEATURES = 3`, `KT_CUT = 20.0`:

| column | meaning |
|---|---|
| `part_sj_lnm` | ln mass of my subjet |
| `part_sj_lnptfrac` | ln (my subjet p_T / jet p_T) |
| `part_sj_nconst` | constituents sharing my subjet |

Subjet = the node a constituent reaches before the next merge would exceed
`KT_CUT`. **No missing-value category** — every real constituent belongs to
exactly one subjet, so unlike the branch-point features there is no "real but
zero" colliding with padding.

`utils/models/base_model.py` — `ca_feature_length()` and `get_inpt` now handle
`subjet_features` alongside `ca_features` (both gated on config, concatenated
before the trailing 4-vector so the ParT positional contract holds).

`config/jet_class_subjet.yml` — `ca_features: false`, `subjet_features: true`,
`subjet_kt_cut: 20.0`. Dataset symlinks created under
`output/DatasetConstructorTask/jet_class_subjet/`.

Verified:

```
jet_class          cpf_dim=21  embed_in=17  params=2,143,486
jet_class_subjet   cpf_dim=24  embed_in=20  params=2,143,882   (+396)
NaN 0  Inf 0  padded-slot nonzeros 0  median subjet mass 12.9 GeV
```

Exactly +3 columns; token inputs differ from baseline by precisely these three.

## STATUS AT COMPACTION (Fri 2026-09-04 07:24)

| cluster | job | state |
|---|---|---|
| 9259275 | CA5 per-particle 1M | **R** — 620k/1M, 85.68%, best 85.71% @ 600k, ETA ~14:00 |
| 9265169 | subjet smoke test (`smoke_subjet_kt20`) | **I** — queued 07:17 |

Killed while idle, no GPU time spent: 9265165 (CAPair 1M), 9265166 (sparsity,
moved to CPU), 9265167 (rule-C smoke). ~37 GPU-hours saved.

### Next steps

1. Wait for smoke 9265169 to pass — do **not** launch 1M before it does.
2. Then submit the 1M subjet run: copy `paper_capair.sub` pattern, config
   `jet_class_subjet`, model `ParticleTransformer_Paper_JetClass`,
   training-version e.g. `b_hive_paper_subjet_1`, H100-pinned, 16 threads,
   100 GB, `nextweek`.
3. Estimate for it helping: **50-55%**. Necessary-but-not-sufficient: the
   information is unavailable to the model, but a feature can be novel and
   still irrelevant. Physics case is strong — Tbqq's leading subjet sits at
   85-96 GeV, the W mass, exactly the top-tagger discriminant.
4. **Seed caveat unchanged**: one seed per arm cannot resolve a sub-1-point
   effect (~1.3-point spread from the unseeded dataloader RNG). 3 seeds at 400k
   remains the right configuration over 1 seed at 1M.

### Scripts (all CPU, minutes to run — use these before spending GPU time)

| path | what |
|---|---|
| `/tmp/check_subjet.py` | subjet redundancy probe + k_T scan |
| `/tmp/check_setmodel.py` | DeepSets set-model probe |
| `/tmp/check_hard.py` | nonlinear redundancy + multiplicity control |
| `/tmp/check_ruleC.py` | the three rule-C checks |
| `/tmp/twv.py` | walk-termination variant comparison |
| `~/cawork/validate_ca_values.py` | per-particle C/A value assertions |
| `~/cawork/jetclass_roc.py` | per-class JetClass ROC from `prediction.npy` |
| `/eos/user/c/cgupta/flashjet/full_cmp.py` | matched training-curve comparison |

**Offline-analysis gotcha**: the lz4 layout is `[15 global | 128x23 cpf | ...]`.
Slice `arr[:, 15:15+128*23]`. Slicing from 0 silently yields garbage — it cost
several wrong conclusions tonight. Authoritative source:
`model.create_feature_shapes()` → `feature_edges [15, 2959, ...]`.

## 2026-09-04 08:40 — subjet smoke test: verified, and a timing correction

The condor smoke test (9265169) never ran — the pool was saturated and it was
killed. Ran it instead on the lxplus **login node, CPU only**, which is legitimate
here: 20 iterations at batch 512 with no `--use-torch-compile` needs no GPU.

**The login-node run hit its 3000 s timeout after ONE iteration** (`Global number
= 1.0`, RC=124). I initially read the process telemetry (worker PID recycling,
RSS dropping 19 GB → 2.3 GB) as "training loop finished, now validating" and
reported the forward path proven. **That was wrong** — it was still on iteration 1
the whole time. The 1M job had already been submitted on that false premise.

Isolated the cost properly instead of inferring it from `ps`:

| what | batch 512, 16 CPU threads |
|---|---|
| `subjet_features_from_cpf` alone | **2.1 s** (4.1 ms/jet) |
| `jet_class` full step (get_inpt + fwd + bwd) | **18.3 s** |
| `jet_class_subjet` full step | **20.2 s** (get_inpt 3.24 s) |

So a full training step is **~20 s on CPU**, not 50 min. The smoke test was slow
because of dataloader startup over the 100M-jet EOS dataset plus contention on a
shared login node — **not** the model and **not** the features. The tell I
misread: workers at 0.5–3% CPU while `law` held 1400% is I/O starvation, not
compute.

**Feature overhead: ~3.2 s/batch = 6.3 ms/jet on CPU, ~11% of the step.** Worth
quoting as the CPU figure; the GPU number will be much smaller.

**Verdict: forward path verified for both configs.** The positional contract holds
— `base_model.get_inpt` concatenates as `cpf[..., :-4] + _sj + cpf[..., -4:]`, and
`particletransformer_paper.forward` splits at exactly `[:, :, :-4]` / `[:, :, -4:]`.
`cpf_dim` 21 → 24, params 2,143,486 → 2,143,882 (+396).

### Gotchas found while timing (for whoever writes the next probe)
- On-disk row width is **2971** = 15 global + 2944 cpf + 12 trailing (10 one-hot
  labels + 2). `get_inpt` wants `x[:, :2959]`.
- `get_inpt` returns **`(tensors_tuple, truth)`** — `inpt[1]` is truth, not cpf.
- `forward` takes the tuple, indexing `inpt[0]`/`inpt[1]` as glob/cpf.

### Job status
- **9265170** — subjet 1M, submitted 07:45, idle. Args diffed against
  `run_paper_baseline.sh`: identical except `--config` / `--training-version`.
- **9259275** — CA5 at 640k, val 85.67%, best 85.71% @ 600k. Curve flat across the
  last 60k (85.67–85.71); train has edged above val. ETA ~14:20.
- **9265169** — condor smoke, removed as redundant.

### Queue: the wait is priority, not hardware
Five H100 NVL slots FIT the request and sit **Unclaimed**, yet `condor_q -analyze`
reports "0 slots match". Cause: **effective priority 3,863,990** (real 38.64 ×
factor 100,000), 3,524 weighted GPU-hours used, 34 CPUs currently held by CA5.
Fair-share throttling, not saturation — I had misread this as a busy pool.

`RequestCpus` is **34**, not the 16 in the submit file; the site expands it. Both
arms are affected identically, so it is left alone.

**Do not shrink `request_memory`.** CA5 reports `MemoryUsage = 146485` MB against
its 102000 MB request — it is 44 GB over and surviving only because the node does
not enforce. Dropping to 80 GB to widen the pool would risk a mid-run kill.
