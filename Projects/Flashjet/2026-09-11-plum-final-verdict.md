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

**Verified fact, from the paper's own conclusions (p.~end, near FIG. 4):**

> "Future studies should assess whether the observed gains persist in experimental
> settings including realistic secondary-vertex information and detector effects.
> **This was not checked because of the absence of reliable secondary vertex features
> in the fast simulation framework used in this study.**"

**Verified fact, our config** (`b-hive/config/jet_class.yml`, `cpf_candidates`):
`part_d0val`, `part_d0err`, `part_dzval`, `part_dzerr` are present.

**Careful with the wording:** neither setup has true reconstructed secondary vertices --
JetClass has no SV block either. The asymmetry is that **we have per-track impact
parameters (d0, dz) and they have no displacement information at all.**

### Hypothesis A -- displacement headroom (best fit to the Hbb pattern, UNTESTED)

Their baseline cannot see displacement, so it must infer b-content from kinematics and
substructure alone. Lund tokens encode the soft/wide-angle radiation that displaced
heavy-hadron decay produces -- the paper argues exactly this mechanism itself. That
leaves real headroom. Our baseline already sees d0/dz per track, so that information is
already present and more directly. Predicts our worst result on the class where our
displacement advantage is largest -- and **Hbb (0.983) is our worst result**.

### Hypothesis B -- redundancy with PairEmbed (the arity argument)

Lund coordinates (ln z, ln kT, ln dR) are **2-body**. ParT's `PairEmbed` already
computes ln dR, ln kT, ln z, ln m^2 for all 128x128 pairs at full resolution. PLuM's 48
tokens are a coarser, pre-selected subset of information the model already has -- they
can act as a prior on which pairs matter, not as new information. Predicts a small
effect, which is what we measure (+0.044 val). Predicted CA5's outcome in advance
(CA5 came out significantly WORSE, p=0.0008).

### Hypothesis C -- binary vs 10-class capacity

Not dilution (dilution affects aggregate accuracy ~5x, but Hbb rejection is measured
per class and is NOT diluted). Rather: a dedicated binary Hbb-vs-QCD network allocates
all capacity to one boundary; ours serves ten.

### Hypothesis D -- seed selection in the paper

They report **top-5 of 10 seeds averaged**. That is a selection procedure that inflates
effect sizes. Our own data bounds how large that inflation can be: CA5's Tbqq rejection
wandered 1.068 -> 1.321 between two checkpoints of an arm that was doing nothing. Their
Tbqq +7.2% sits inside that wander. Their Hbb +12% is larger and harder to dismiss so.

### The experiment that would discriminate

Binary Hbb-vs-QCD ParT, with and without PLuM tokens, on a baseline with **d0/dz
stripped**. Matches their configuration on all three axes at once. One training pair,
binary task -- much cheaper than the 4-arm 10-class study just completed.

**None of A-D is established.** We have one seed per arm. The defensible statement is
that our setup does not reproduce their result, not that their result does not exist.
