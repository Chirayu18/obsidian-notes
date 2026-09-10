---
tags: [reference]
status: active
date: 2026-09-11
source: lxplus
---

# PLuM final verdict: validation gain is real, test-set reproduction FAILS

Supersedes [[2026-09-08-plum-arm-launched]] (which recorded the 260k interim state).
Closes the plan in [[2026-09-07-plum-reproduction-plan]] and answers the question posed
in [[2026-09-07-plum-paper-vs-our-result]].

**Arm:** 48 kT-ordered Lund splitting tokens, reproducing Gouskos & Maier
(arXiv:2605.26821), as a **full 10-class** ParT training rather than their binary mode.
condor 9283169, 1M iterations, 2d10h wall.

## The one-line answer

PLuM gives a **small but statistically robust validation improvement (+0.044, 11/11
checkpoints, p~1e-4) that does NOT survive to the test set (-0.006) and does NOT
reproduce the paper's H->bb claim in sign or magnitude**, at **1.58x** the training cost.

## Final test set (20.05M jets, best_model, one checkpoint each)

| arm | overall acc | vs baseline |
|---|---|---|
| baseline | 86.212 | -- |
| PLuM | 86.206 | -0.006 |
| subjet | 86.191 | -0.021 |
| CA5 | 86.156 | -0.056 |

**The paper's two classes, background rejection @50% signal efficiency:**

| class | paper | PLuM | CA5 | subjet |
|---|---|---|---|---|
| **Hbb** | **1.120** | **0.983** | 0.983 | 1.018 |
| **Tbqq** | **1.072** | **1.148** | 1.321 | 1.000 |

@90% efficiency: Hbb paper 1.031 -> PLuM 0.983; Tbqq paper 1.066 -> PLuM 0.995.

Control classes (Hcc, Hgg, H4q, Zqq, Wqq) mean 1.000, spread 0.991-1.005 -- flat, as
the paper predicts. Hqql and Tbl excluded: infinite rejection (0 QCD background passes).

Per-class AUC differences are 1e-5..1e-4 across every arm and class -- negligible.

### Why Tbqq 1.148 is NOT a positive result

1. **CA5 scores 1.321 on the same metric** -- and CA5 is definitively the WORST arm
   (lowest test accuracy, significantly worse on validation p=0.0008). An arm that is
   bad everywhere else cannot be producing a real +32% top-tagging gain.
2. **It wanders.** CA5's Tbqq @50% went 1.068 at 480k -> 1.321 at 980k while that arm
   did nothing. The paper's claimed 1.072 sits inside that noise range.
3. **It is a tail quantity.** Tbqq rejection ~28,000 on 2M jets means the denominator is
   a handful of surviving QCD jets. Single-seed variance is enormous.
4. **It vanishes at 90% eff** (0.995), where statistics are ample.

**Hbb is the class that matters and it fails**: 0.983, a 1.7% LOSS against a claimed
+12% gain, wrong sign at both working points.

## Validation (15M jets, 50 paired checkpoints) -- the gain that IS real

Pre-registered 800k+ window, n=11: mean **+0.044**, **11/11 positive**.

| arm | mean d | ahead | p |
|---|---|---|---|
| **PLuM** | **+0.044** | **11/11** | ~1e-4 |
| subjet | -0.004 | 7/11 | 0.61 |
| CA5 | -0.047 | 1/11 | 0.0008 |

Tight regime (700k+, n=16):

| metric | mean d | ahead | p |
|---|---|---|---|
| validation acc | +0.063 | **16/16** | 0.001 |
| validation loss | -0.0014 | **16/16** | 0.001 |
| training acc | -0.023 | 6/16 | 0.52 |
| training loss | +0.0004 | 9/16 | 0.69 |

Full run n=50: val acc +0.048 (p=0.003), train acc -0.001 (p=0.97).

**Both validation metrics unanimous across 16 consecutive checkpoints; both training
metrics coin flips.** The effect is entirely on the validation side.

### Best-of table (the ranking inverts)

| arm | best train | @ | best val | @ | gap |
|---|---|---|---|---|---|
| baseline | **86.658** | 900k | 86.230 | 980k | +0.428 |
| PLuM | 86.468 | 920k | **86.266** | 960k | **+0.202** |
| CA5 | 86.451 | 940k | 86.194 | 980k | +0.257 |
| subjet | 86.488 | 980k | 86.233 | 960k | +0.255 |

PLuM has the LOWEST best training accuracy of all four arms and the HIGHEST best
validation -- and its best val exceeds every other arm's full-run peak.

**Do not over-read this as regularization.** I tested that hypothesis directly
(gap = val_loss - train_loss, compared across arms per checkpoint) and got **p=0.269**.
Comparing two p-values (one significant, one not) is not a test of the difference
between them. The descriptive statement -- effect on validation, not on training --
is what the data supports; the mechanism is not established.

## Why validation and test disagree (they don't, actually)

- Validation: **+0.044 points**, averaged over 11-16 paired checkpoints -> noise beaten down.
- Test: **-0.006 points**, ONE checkpoint, no averaging. Baseline's own checkpoint-to-
  checkpoint |step| at 800k+ is 0.088 -- larger than the entire effect.

A +0.04 effect is simply not resolvable in a single-checkpoint test comparison. Both
numbers are correct.

## Why it cannot reach the paper's magnitude

**Magnitude calibration** (from baseline-vs-CA5 on the same 20M test jets): roughly
**30% Hbb rejection change per 1.0 accuracy point**. The paper's +12% therefore needs
about **+0.40 accuracy points**. PLuM delivers **+0.04** -- an order of magnitude short.

**Dilution does not rescue it.** 10-class accuracy averages a 2-class effect over ten
classes (~5x). Even crediting the full 5x, +0.04 -> +0.20 effective, still 2x short.

**The arity argument stands** (the talk's spine): Lund coordinates (ln z, ln kT, ln dR)
at a splitting are **2-body**, and ParT's `PairEmbed` already computes exactly these for
every particle pair. PLuM is handing the model a coarser, pre-clustered version of
information it already has at full resolution. A subjet mass is n-body and genuinely
outside PairEmbed's reach -- which is why subjet was the more interesting arm a priori,
though it too came out null.

## Cost

| arm | median block (20k iters) | ms/step | vs baseline | full run | extra |
|---|---|---|---|---|---|
| baseline | 43.7 min | 131.2 | 1.00x | ~36.4 h | -- |
| CA5 | 53.3 min | 159.9 | 1.22x | ~44.4 h | +8.0 h |
| subjet | 62.2 min | 186.7 | 1.42x | ~51.8 h | +15.4 h |
| **PLuM** | **69.3 min** | **207.9** | **1.58x** | **~57.8 h** | **+21.4 h** |

Measured from checkpoint mtimes (consecutive exactly-20k gaps under 6h, to drop
restarts). Block = train + 15M-jet validation + checkpoint, so not pure training
overhead. Arms ran on different GPUs at different times -- contention contributes.

PLuM's ordering is what the feature cost predicts: kT clustering + up to 48 splittings
extracted + **176 tokens instead of 128** through the transformer (1.375x sequence).

Inference is hit too: measured 480k test-set inference, baseline **28 min** vs
CA5 **75 min** (2.7x) -- clustering runs per batch at inference exactly as in training.

## Verdict for the talk

All three feature arms are **nulls or worse on the test set**. The defensible claims:

1. C/A features (CA5): significantly WORSE (-0.047 val, p=0.0008; -0.056 test).
2. Subjet features: null (-0.004 val, p=0.61; -0.021 test).
3. PLuM: small real validation gain (+0.044, p~1e-4) that does not survive to test,
   at +58% training cost. **Does not reproduce Gouskos & Maier's Hbb result.**

The arity argument explains 1 and 3 and predicted them in advance.

## Operational lessons (this session)

- `micromamba activate` is an **alias** -- a no-op in non-interactive shells. Leaves
  system python on PATH, dies with ModuleNotFoundError into an EMPTY log. Condor jobs
  escape this via `getenv = True`; interactive/lxplus-gpu scripts must set
  `PATH=$MAMBA_ROOT_PREFIX/envs/b_hive/bin:$PATH` explicitly.
- **lxplus interactive nodes silently kill long processes** (~40 min observed).
  `setsid` does not prevent it. Long inference must go through condor.
- luigi `TrainingTask` completeness needs the **iteration-named** checkpoint
  (`model_<N>.pt`), not just `best_model.pt` -- otherwise it starts TRAINING.
- `law index` hangs for minutes rewriting `.law/` on EOS; the index already exists, skip it.
- Do not use `condor_q` emptiness as a liveness signal -- an expired AFS token or an
  unreachable schedd both return empty. Use **checkpoint file age** instead.
- `condor_history` needs >120s; run it backgrounded.
- Nested quotes in f-strings passed through ssh heredocs mangle. Write the script
  locally and `scp` it.

## Where things live

- Training output: `/eos/user/c/cgupta/flashjet/b-hive/output/TrainingTask/jet_class_plum/JetClass_train_100_mod/b_hive_paper_plum_1/ParticleTransformer_PLuM_JetClass/epochs_0/nominal/`
- Test inference: `.../InferenceTask/jet_class_plum/JetClass_train_100_mod/JetClass_test_mod/b_hive_paper_plum_1/...`
- Analysis scripts: `~/flashjet_condor/{cmp_plum,cmp_train,cmp_loss,ttest_now,bestsofar,besttrain,perclass_best,perclass_n,magnitude,timing,gaptest}.py`
- Per-class JSON: `~/flashjet_condor/perclass_results/pythia_480k_narm.json`
  (**filename says 480k but contains the FINAL 1M results** -- `K` only feeds the
  filename in `perclass_best.py`, the paths use the plain best_model dirs)


## Why the paper sees a gain and we do not -- candidate explanations

### CORRECTION (2026-09-11): the "they lack displacement inputs" claim was WRONG

I earlier asserted the paper's baseline had no displacement information and built a
"displacement headroom" hypothesis on it. **That was not supported.** Checking the PDF:

- **They train on JetClass** (paper, sec. III: "trained for 50 epochs in binary
  classification mode on the JetClass [2] dataset"). Same dataset we use.
- They call their baseline "**the default ParT configuration**" -- default ParT on
  JetClass uses the full standard feature set, which INCLUDES `part_d0val`,
  `part_d0err`, `part_dzval`, `part_dzerr`.
- The paper **never lists its input features and never mentions dropping any**.

The quote I relied on is narrower than I made it:

> "...whether the observed gains persist in experimental settings including realistic
> **secondary-vertex information** and detector effects. This was not checked because of
> the absence of reliable **secondary vertex** features in the fast simulation framework."

That is about **reconstructed secondary vertices**, which Delphes does not provide well
and which JetClass also lacks. **Neither setup has SV. Both very likely have the same
track impact parameters.** SV != displacement; I conflated them.

**Consequence: our setup is CLOSER to theirs than I claimed, which makes the
discrepancy harder to explain, not easier.**

### Remaining real differences

| axis | paper | ours |
|---|---|---|
| task | **binary** (signal vs QCD) | 10-class |
| seeds | **10 trained, max & mean reported** | 1 |
| schedule | 50 epochs x 16M jets, batch 256 | 1M iters, batch 512 |
| dataset | JetClass | JetClass -- **same** |
| inputs | JetClass standard -- **likely same** | JetClass standard |

### Hypothesis B -- redundancy with PairEmbed (the arity argument)

Lund coordinates (ln z, ln kT, ln dR) are **2-body**. ParT's `PairEmbed` already
computes ln dR, ln kT, ln z, ln m^2 for all 128x128 pairs at full resolution. PLuM's 48
tokens are a coarser, pre-selected subset of information the model already has. Predicts
a small effect -- which is what we measure (+0.044 val). Predicted CA5's outcome in
advance (CA5 came out significantly WORSE, p=0.0008).

Note the paper argues directly against this (sec. VI): it claims Lund information is
"not uniformly reconstructed from particle-level inputs alone, even in highly expressive
transformer architectures." Our result is evidence on the other side, in 10-class mode.

### Hypothesis C -- binary vs 10-class capacity

**Now the main remaining axis.** A dedicated binary Hbb-vs-QCD network allocates all
capacity to one boundary; ours serves ten. NOT dilution -- dilution affects aggregate
accuracy (~5x) but Hbb rejection is measured per class and is not diluted.

### Hypothesis D -- seed variance / selection

They train **10 copies** and report max and mean. Our own data bounds how much a max-of-N
can inflate: CA5's Tbqq rejection wandered 1.068 -> 1.321 between two checkpoints of an
arm that was doing nothing. We have **1 seed**; we cannot rule out that our PLuM run is a
below-median draw.

### The experiment that would discriminate

**Binary Hbb-vs-QCD, keeping d0/dz** (do NOT strip them -- they likely match the paper).
Baseline + PLuM. That isolates the task axis, the main remaining difference. Multiple
seeds would also address D, at linear cost.

**None of B-D is established.** One seed per arm. The defensible statement is that our
setup does not reproduce their result, not that their result does not exist.


## IMPORTANT (2026-09-11, post-hoc audit): we likely built the WRONG SPLITTING SET

Triggered by re-reading the paper for results I had missed. **Our per-splitting
coordinates and plumbing are correct, but the SELECTION of which splittings become
tokens probably is not.**

### The evidence

Paper, sec. V (H->4q discussion): "**about 17% of signal jets exceed the 48-splitting
input cap, compared to about 9% in H -> bb**".

Our implementation (`utils/flashjet_lund_tokens.py`) takes the **top 48 by kT out of the
full clustering tree**. Clustering N particles gives N-1 pairwise merges, and a JetClass
jet has ~50-130 constituents -> ~50-130 splittings. Measured with our own code path:
**100% of jets exceed 48**, at every multiplicity tested (nconst 60/90/120 -> mean
58/88/118 splittings).

**9% cannot be reconciled with a full-tree count.** For only 9% of jets to have >48
splittings, the splitting set must be ~10-20 per jet -- which is the size of the
**primary Lund plane**: iteratively decluster following the HARDER branch only, recording
one emission per step. That is the standard Lund-plane construction (Dreyer/Salam/Soyez).

### What the paper actually says

Only "Up to 48 splittings are considered per jet" (sec. IV) and that nodes are
"individual branchings" with edges following "the clustering history" (sec. II). **It
never states which 48.** The 9%/17% truncation statistic is the only discriminating
evidence, and it points to primary-branch, not full-tree.

### Why this plausibly matters for the null

Our top-48-by-kT from the full tree is dominated by soft wide-angle merges deep in the
tree, many between already-merged pseudojets that are not resolvable emissions off the
hard core. The primary Lund plane instead traces the hard branch's emission history --
the object that encodes two-prong H->bb structure and the b-hadron decay pattern their
own mechanism argument (sec. V) depends on.

**Status: strong inference, not certainty.** We infer their construction from a
truncation statistic, not a stated definition.

### What else the paper reports (I had missed these)

- **FIG. 2**: per-epoch ACCURACY curves for four binary channels (top, Hbb, Hcc, H4q),
  max over 10 trainings with bands to the mean. Directly analogous to our validation
  tracking. Numbers are in the plot, not the text.
- **HH(4b), the abstract's headline**: "at a 25% di-Higgs efficiency working point, PLuM
  achieves **25% higher background rejection**". This is an EVENT-level di-Higgs result,
  not in Table I.
- **FIG. 4**: mean score difference vs ParT score.
- **NO AUC anywhere in the paper** (verified exhaustively). Table I is rejection-only.

### Baseline strength -- ours is ~2x theirs on the same dataset

| | their ParT | our baseline | ratio |
|---|---|---|---|
| Hbb @50% | 5,864 | **11,523** | **1.96x** |
| Hbb @90% | 386 | 606 | 1.57x |
| Tbqq @50% | 13,422 | **28,642** | **2.13x** |
| Tbqq @90% | 331 | 533 | 1.61x |

**Our plain ParT baseline already beats their PLuM on all four numbers.** Their +12%
takes ParT 5,864 -> 6,567, still only 57% of our baseline without any Lund tokens.
Caveats: 10-class per-class discriminant vs their binary tagger is not perfectly
apples-to-apples; and their 50 epochs x 16M at batch 256 is ~3.1M steps, MORE than our
1M at batch 512, so "under-trained" is not obviously the explanation.

### Revised next step

**Do NOT launch the binary run yet.** Fix the splitting selection first -- a binary run
on the wrong token set answers nothing. Order:
1. Implement primary-Lund-plane declustering (follow harder branch, one emission/step).
2. Verify the truncation fraction reproduces ~9% (Hbb) / ~17% (H4q).
3. THEN decide binary vs 10-class.
