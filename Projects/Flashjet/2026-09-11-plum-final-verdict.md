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


## RETRACTED: the "wrong splitting set" audit was WRONG (measured on real jets)

I claimed our splitting selection diverged from the paper's, based on synthetic jets with
80-128 constituents. **Real JetClass jets have ~35-50 constituents.** Measured on 100k real
jets from `JetClass_test_mod/file_0.lz4`:

| class | nconst | full-tree splits | %>48 |
|---|---|---|---|
| QCD | 35.1 | 22.5 | 5% |
| **Hbb** | **43.5** | **28.9** | **5%** |
| Hcc | 39.6 | 26.8 | 3% |
| Hgg | 58.9 | 42.9 | 28% |
| **H4q** | **49.9** | **35.2** | **9%** |
| Tbqq | 51.4 | 36.3 | 11% |

**Our full-tree construction gives Hbb 5% / H4q 9%, ratio 1.93. The paper reports
9% / 17%, ratio 1.9.** The ratio matches almost exactly, and the mean counts (29, 35)
sit in the 30-40 band a 48-cap implies. The residual ~1.8x in absolute rate is
consistent with their jets having modestly higher multiplicity (pT range / preprocessing),
not a different algorithm.

The Lund-TREE variants I implemented to "fix" this give ~8-14 splittings and **0% over
48** at every threshold tested (0/2/5/10% of jet pT) -- as far off as the primary plane.
**The proposed fix was worse than what we have.**

### What was wrong in my reasoning

Every step downstream of the synthetic multiplicity was invalid:
- "100% of jets exceed 48" -> actually **5%** for Hbb
- "our set is definitely not theirs" -> it matches on the only checkable statistic
- "their set must be an intermediate ~30-40" -> it is, and **we already compute that**
- the 1.9x prong-scaling argument is real, but our flat full-tree ALREADY reproduces it,
  because H4q jets simply have more constituents (49.9 vs 43.5) and so more merges

**Lesson: measure on real data before building inference on simulated proxies.**
The lz4 reader (below) was the blocker and should have been solved first.

### Reading JetClass lz4 shards (this was previously unavailable)

```python
import lz4.frame, numpy as np
with lz4.frame.open(path, mode="r") as fh: raw = fh.read()
s = np.frombuffer(raw, dtype=np.float32).copy()
s = s[2:].reshape(-1, int(s[1]), order="C")     # s[1] = row width
labels = s[:, -(10+1):-1]                        # 10 truth labels
feats  = s[:, :-(10+2)]                          # trailing: process, labels, weight
cpf    = feats[:, :128*23].reshape(-1, 128, 23)  # part_px/py/pz/E at 12:16
```
`file_0.lz4` = 233 MB compressed -> 1.19 GB, 100,000 jets, row width 2971.
Scripts: `~/flashjet_condor/truncation_test.py`, `lund_tree.py`.

## Standing conclusions after the audit

1. **PLuM implementation is correct.** Coordinates match the paper to ~0.1%
   (z, kT, dR conventions all verified numerically); the Lund path was live
   (`input_bn.num_batches_tracked` = 73,874, running stats physically sensible);
   splitting selection reproduces the paper's truncation ratio. **No bug found.**
2. **The null result stands as a result about the physics**, not about our code.
3. **Our baseline is ~2x theirs** on every Table I number -- our plain ParT already
   beats their PLuM. This remains the most striking unexplained difference and is
   independent of the token question.
4. Remaining setup differences: **binary vs 10-class**, and **10 seeds vs 1**.


## Systematic paper-matching audit (2026-09-11)

Every quantitative claim in the paper that we can check, checked.

### 1. Parameter count -- EXACT MATCH

| | paper | ours |
|---|---|---|
| ParT baseline | 2.14 M | **2.1439 M** |
| PLuM | 2.19 M | **2.1944 M** |
| delta | +0.05 M | **+0.0505 M** |

Three numbers agreeing to the paper's quoted precision. Same MLP dims [64,256,128],
same 48 splittings, same backbone. **The architecture reproduction is faithful.**

### 2. Truncation fraction -- RATIO MATCHES

Real JetClass jets (100k, `JetClass_test_mod/file_0.lz4`):

| class | nconst | splits | %>48 |
|---|---|---|---|
| Hbb | 43.5 | 28.9 | 5% |
| H4q | 49.9 | 35.2 | 9% |
| Hgg | 58.9 | 42.9 | 28% |
| Tbqq | 51.4 | 36.3 | 12% |

Ours Hbb/H4q = 5%/9%, **ratio 1.93**; paper 9%/17%, **ratio 1.9**. Residual ~1.8x in
absolute rate is consistent with modestly higher multiplicity in their sample.

### 3. Lund feature distributions vs the TRAINED model's input_bn -- 2 of 3 confirm

| feature | valid tokens only | incl. padded zeros | **model running_mean** |
|---|---|---|---|
| ln(1/dR) | **+2.300** | +1.478 | **+2.264** <- matches valid-only |
| ln z | **-1.239** | -0.796 | **-1.144** <- matches valid-only |
| ln kT | -3.607 | -2.317 | **-0.636** <- **UNEXPLAINED, off by ~3** |

dR and z confirm the clustering and token pipeline against what the model actually saw.
**ln kT carries an unexplained ~3-unit (x22) offset.** Ruled out: a train/test pT-scale
difference (train 662 GeV vs test 677 GeV mean jet pT -- 2%, not 22x). Candidates not yet
isolated: a training-time momentum rescale hitting only the dimensionful feature, or
unconverged BN momentum on the widest-tailed input. **Low consequence** -- BN absorbs a
constant shift, and dR/z rule out a clustering difference since all three come from the
same clustering.

### 4. Training volume -- WE TRAIN LESS THAN THEY DO

| | paper | ours |
|---|---|---|
| schedule | 50 epochs x 16M jets, batch 256 | 1M iters, batch 512 |
| **optimizer steps** | **3.125 M** | **1 M** |
| jet-presentations | 800 M | 512 M |
| seeds | **10** (max & mean reported) | **1** |

**They take 3.1x more gradient steps and see 1.6x more data.** Previously I had only
guessed at this; it is now computed. This is a real, unexamined difference -- our arms may
simply be less converged, though note all four of OUR arms share the identical schedule,
so the CROSS-ARM comparison remains valid.

### Bottom line of the audit

Architecture: exact. Splitting selection: ratio-matched. Two of three Lund features:
confirmed against the trained model. One feature offset: unexplained but low-consequence.
**No bug found. The null stands as a physics result.**

Unexplained differences that remain, in order of likely importance:
1. **Our baseline is ~2x theirs** on every Table I number (our plain ParT beats their PLuM)
2. **3.1x fewer optimizer steps** than they take
3. binary vs 10-class
4. 1 seed vs 10


## Hbb vs Tbqq with Poisson errors -- the Tbqq "gain" is NINE JETS

The ratio's uncertainty is set by the surviving-background count. Made explicit
(discriminant (a), 2,004,925 QCD jets):

### @50% signal efficiency

| class | arm | bkg surviving | rejection | ratio | Poisson err | sigma from 1 |
|---|---|---|---|---|---|---|
| Hbb | baseline | 174 | 11522.6 | -- | +-7.6% | |
| Hbb | PLuM | 177 | 11327.5 | 0.983 | +-0.105 | 0.2 |
| Hbb | CA5 | 177 | 11327.3 | 0.983 | +-0.105 | 0.2 |
| Hbb | subjet | 171 | 11725.1 | 1.018 | +-0.110 | 0.2 |
| **Tbqq** | baseline | **70** | 28641.8 | -- | +-12.0% | |
| **Tbqq** | **PLuM** | **61** | 32868.2 | **1.148** | **+-0.201** | **0.7** |
| Tbqq | CA5 | 53 | 37829.0 | 1.321 | +-0.240 | 1.3 |
| Tbqq | subjet | 70 | 28642.7 | 1.000 | +-0.169 | 0.0 |

**Every @50% ratio is consistent with 1.0.** PLuM's Tbqq 1.148 is 61 vs 70 surviving
background jets -- a difference of **nine jets** -- with a 1-sigma band of 0.95-1.35.

### @90% signal efficiency (thousands of jets survive; errors ~2%)

| class | arm | bkg surviving | rejection | ratio | Poisson err |
|---|---|---|---|---|---|
| Hbb | PLuM | 3366 | 595.7 | **0.983** | +-0.024 |
| Tbqq | PLuM | 3783 | 530.0 | **0.995** | +-0.023 |

**Both classes flat and both slightly BELOW 1, with 4x smaller errors.** This is the
statistically meaningful measurement and it shows no gain on either class.

### Why the "gain" shows up on Tbqq and not Hbb

Tbqq's rejection is 2.5x higher than Hbb's (28,642 vs 11,523), so only 70 background
jets survive vs Hbb's 174 -- making the Tbqq ratio nearly **twice as noisy**. The
apparent gain appears where the statistics are thinnest, not where the physics differs.
This is the same mechanism behind CA5's 1.068 -> 1.321 wander between checkpoints.

### Implication for the paper's claims

- Their **Tbqq 1.072**: their rejection 13,422 on 2M -> ~149 surviving jets -> ~+-11%.
  Their claim is ~0.7 sigma from unity. **Not distinguishable from no effect, or from ours.**
- Their **Hbb 1.120**: rejection 5,864 -> ~341 surviving jets -> ~+-7.7%, so ~1.6 sigma.
  The only claim with enough statistics to be meaningful -- and the one we most clearly
  fail to reproduce (0.983 +- 0.105 @50%, **0.983 +- 0.024 @90%**).

**The @90% numbers are where this study has real power, and they are unambiguous: no
gain on either class, under either discriminant.**


## All classes @ 70% -- the decisive flat table

| class | base bkg | base rej | PLuM | CA5 | subjet |
|---|---|---|---|---|---|
| **Hbb** | 586 | 3421.4 | **0.933 +-0.054** (1.2s) | 0.953 +-0.055 | 0.967 +-0.056 |
| Hcc | 2025 | 990.1 | 0.984 +-0.031 | 0.966 +-0.030 | 0.974 +-0.030 |
| Hgg | **45516** | 44.0 | **1.001 +-0.007** | 0.999 +-0.007 | 0.997 +-0.007 |
| H4q | 4847 | 413.6 | 1.020 +-0.021 | 0.977 +-0.020 | 0.986 +-0.020 |
| Zqq | 21194 | 94.6 | 0.996 +-0.010 | 0.994 +-0.010 | 0.992 +-0.010 |
| Wqq | 16411 | 122.2 | 0.991 +-0.011 | 0.988 +-0.011 | 0.998 +-0.011 |
| **Tbqq** | 370 | 5418.7 | **1.022 +-0.076** (0.3s) | 0.997 +-0.073 | 0.964 +-0.070 |

(Hqql, Tbl: 0 surviving background -> infinite rejection, excluded)

**Nothing reaches 2 sigma in 21 measurements.** Largest is 1.2 sigma.

**Hgg is the most precise point in the whole study** -- 45,516 surviving background jets,
+-0.7%, and all three arms land at 0.997-1.001. Where the statistics are genuinely good,
every arm is EXACTLY flat. That is the cleanest single demonstration that these features
do nothing.

**The paper's two classes are the two noisiest usable ones** (586 and 370 surviving jets,
the smallest counts outside the saturated Hqql/Tbl). Hbb and Tbqq have the highest
rejection, so the fewest background jets survive, so their ratios fluctuate most. **The
paper's claims live exactly where measurement is hardest.**

PLuM is below 1 on five of seven classes; mean ratio ~0.993, consistent with the -0.006
aggregate accuracy.

### Working-point scan, PLuM (shows the wander)

| eff | Hbb | Tbqq |
|---|---|---|
| 50% | 0.983 +-0.105 | 1.148 +-0.201 |
| 60% | 1.067 +-0.082 | 1.114 +-0.126 |
| 70% | 0.933 +-0.054 | 1.022 +-0.076 |
| 80% | 0.980 +-0.039 | 0.985 +-0.043 |
| 90% | 0.983 +-0.024 | 0.995 +-0.023 |

Non-monotonic, oscillating about 1 with amplitude shrinking as statistics improve --
the textbook signature of noise, not of an effect.

**Note:** CA5's Hbb @60% is **1.122 +-0.088**, numerically almost exactly the paper's
claimed 1.120 -- produced by the arm that performs WORST overall. An illustration of how
readily a 1.12-sized number appears by chance in this regime.

### The sharpest statement for the talk

At 90% efficiency, where both we and the paper have real statistics:

| | paper claims | we measure |
|---|---|---|
| Hbb | 1.031 | **0.983 +- 0.024** (~2 sigma below) |
| Tbqq | 1.066 | **0.995 +- 0.023** (~3 sigma below) |

This disagreement does not depend on discriminant choice, does not rest on tail noise,
and is the most statistically meaningful comparison available between the two studies.


## ACCIDENTAL SECOND SEED -- the missing systematic (2026-09-11)

A misconfigured "480k inference" job (9291649) silently ran **training** for 9.5h instead
of inference: its staging dir lacked `model_480000.pt`, so luigi judged TrainingTask
incomplete and trained from scratch. Killed at 120k. **It wrote to
`b_hive_paper_plum_1_at480k`, NOT the real `b_hive_paper_plum_1` -- the 1M run and its
final inference are intact (all 50 checkpoints, metrics stamped 00:31).**

The accident produced something we never had: **a second PLuM seed**, identical config and
data, different initialisation.

| iter | seed A (real) | seed B (accidental) | B - A | baseline |
|---|---|---|---|---|
| 20k | 81.736 | 81.207 | **-0.529** | 81.765 |
| 40k | 83.493 | 83.407 | -0.086 | 83.466 |
| 60k | 84.360 | 84.294 | -0.066 | 84.059 |
| 80k | 84.462 | 84.517 | +0.056 | 84.372 |
| 100k | 84.754 | 84.710 | -0.045 | 84.658 |
| 120k | 84.850 | 84.936 | +0.086 | 84.764 |

**Seed-to-seed spread: mean |diff| 0.145, sd 0.203, max 0.529.**
**The PLuM-vs-baseline effect we measured: +0.044.**

### What this does and does not show

**Does NOT refute the validation effect.** Our claim comes from the 800k+ window where
the within-run noise floor is 0.088, and it rests on **11/11 consecutive positive
checkpoints** (p~1e-4), not on any single point. Seed spread also shrinks with
convergence: 0.529 at 20k, but 0.045-0.086 by 100-120k (excluding the 20k outlier,
late-point mean |diff| 0.068, sd 0.075).

**DOES show the single-seed design cannot establish the result robustly.** The paired
t-test controls for WITHIN-run noise across checkpoints. It does NOT control for a
BETWEEN-run systematic -- whether PLuM's seed happened to initialise better than
baseline's. That systematic is plausibly +-0.1 or larger, i.e. **2x+ our effect**, and is
invisible to our design.

**Limitation:** seed B only reached 120k, so there is no comparison in the 800k+ window
where the claim lives. Suggestive, not decisive.

**This is precisely why the paper trains ten seeds and reports max AND mean.** Our
critique of their top-5-of-10 selection stands, but our own single seed is the mirror-image
weakness. The right framing for the talk: *neither study has the seed statistics to
resolve an effect of this size; ours at least measures it at a working point (90% eff)
where the per-class errors are +-2%.*

### Operational lesson (repeat offender)

**Always verify a staged checkpoint dir contains the ITERATION-NAMED file matching
`--TrainingTask-total-iterations`.** Without it luigi trains instead of inferring, silently,
for hours. I documented this failure mode earlier in the session and then still failed to
check for it when the job started running -- I reported "mid-inference, 17 GB resident"
when the memory growth was training memory. Check `condor_tail` for "Global number = N"
(training) vs "Start inference on cuda" (inference) before trusting a running job.


## BINARY Hbb-vs-QCD runs submitted (2026-09-11, condor 9297236)

Reproduces the paper on the **task axis** -- the main remaining configuration
difference. One seed each of baseline and PLuM, 200k iterations, sequentially in
one condor job.

### The trap that had to be avoided

`LZ4Dataset` sets `truths = np.zeros(...)` then reassigns only rows whose label is
in `model_classes`. **A plain 2-class {QCD, Hbb} dict would silently label the other
EIGHT signal classes as QCD** -- a background ~9x contaminated with Hcc/Hgg/H4q/
Zqq/Wqq/Tbqq/Tbl, which is not the paper's task and would give a meaningless
rejection number.

Fix: `utils/torch/BinaryFilteredLZ4Dataset.py` drops out-of-task rows *before* any
truth assignment. Selected via `dataset: BinaryFilteredLZ4Dataset` in the binary configs.

### What was added

| file | purpose |
|---|---|
| `utils/models/binary_hbb.py` | 2-class subclasses of paper-ParT and PLuM |
| `utils/torch/BinaryFilteredLZ4Dataset.py` | drops the other 8 classes |
| `config/jet_class_binary.yml` | baseline + dataset override |
| `config/jet_class_plum_binary.yml` | PLuM (all 6 lund keys) + dataset override |
| `utils/models/models.py` | registry: enum + match cases (backup `.bak_binary`) |
| `utils/torch/DatasetLoader.py` | registry (backup `.bak_binary`) |
| `~/flashjet_condor/run_binary.sh`, `binary.sub` | one job, both arms |

### Smoke test BEFORE submitting (all passed)

- both models instantiate, `classes = ['QCD','Hbb']`, **`fc` out_features = 2**
- params 2.1425M (baseline) / 2.1929M (PLuM) -- vs 10-class 2.1439/2.1944
- filtered dataset on a real shard: **only truth values {0,1}**, other 8 classes gone
- PLuM binary config retains all 6 `lund_*` keys

### Caveat stated up front

**One seed each.** The accidental second seed measured seed-to-seed spread at
mean |diff| 0.145 / sd 0.203 -- larger than the +0.044 effect we are chasing. A
single-seed binary run can show a LARGE effect (the paper claims +12% rejection,
which would be unmistakable) but **cannot establish a small one**. If the binary
result comes back near null, the honest conclusion is "no large effect", not
"no effect".


## MAJOR RESULT (2026-09-11): the gain is REAL EARLY and DECAYS with training

100k-iteration inference on the full 20.05M-jet test set, both arms, matched checkpoint.

| | paper | ours @100k | ours @1M |
|---|---|---|---|
| Hbb @50% | **1.120** | **1.193 +-0.108** | 0.983 +-0.105 |
| **Hbb @90%** | **1.031** | **1.037 +-0.022** | **0.983 +-0.024** |
| Tbqq @50% | 1.072 | 1.145 +-0.130 | 1.148 +-0.201 |
| Tbqq @90% | 1.066 | 1.026 +-0.018 | 0.995 +-0.023 |

Overall accuracy: @100k PLuM **+0.065**; @1M PLuM **-0.006**.

**Hbb @90% is the decisive number** -- best statistics (~4,600 surviving background
jets, +-2%), and at 100k it matches the paper to **0.006** (1.037 vs 1.031). The same
quantity at 1M is 0.983, i.e. **2.3 sigma below the 100k value**.

### Interpretation

**PLuM buys convergence SPEED, not final performance.** The tokens help while the
baseline is still learning the pairwise Lund kinematics that `PairEmbed` can derive
from the four-vectors on its own; once it has, the advantage is gone. This is the
arity/redundancy argument with a time axis: the information is not new, it is EARLY.

**It also reconciles our result with the paper without either being wrong.** They train
50 epochs x 16M jets at batch 256 = **3.125M optimizer steps** on BINARY tasks (8M+8M
per epoch). Where that sits on the convergence curve relative to our 10-class 1M-step
runs is not determinable from the paper -- but our implementation demonstrably
reproduces their numbers at some point on that curve.

### Caveats (stated plainly)

- At 100k the two PLuM SEEDS differ by 0.132 in validation accuracy, comparable to the
  +0.065 accuracy difference here. Hbb@90% at +-0.022 is tighter than that, but we have
  no second seed's INFERENCE to confirm the ratio.
- Baseline @100k -> @1M gains **x1.53** on Hbb@50% and **x2.37** on Tbqq@50%. A 1.19
  ratio sits well inside the movement ordinary convergence produces -- WHICH CHECKPOINT
  you evaluate matters more than the feature does.
- 100k is 1/10 of the trained model. Nobody ships a tagger there.

### Revised framing for the talk

NOT "PLuM does not work". Instead:

> **PLuM reproduces Gouskos & Maier's H->bb gain at early training (1.037 +-0.022 vs
> their 1.031 at 90% efficiency) and that gain decays to nothing by 1M iterations
> (0.983 +-0.024). The feature buys convergence speed, not final performance --
> at 1.58x the training cost per step.**

This supersedes the earlier flat-null reading. The 800k+ validation result (+0.044,
11/11) and the flat 90%-efficiency per-class table remain correct AS STATEMENTS ABOUT
THE CONVERGED MODEL; they were simply measured where the effect has already decayed.

### Baseline convergence calibration (same batch)

| | 100k | 1M | gain |
|---|---|---|---|
| overall acc | 84.632 | 86.212 | +1.579 |
| Hbb rej @50% | 7,536 | 11,523 | **x1.53** |
| Tbqq rej @50% | 12,075 | 28,642 | **x2.37** |

10x more training buys +53% Hbb rejection; the paper claims +12% from Lund tokens.
Independently confirms the magnitude calibration: +1.579 acc -> +53% rejection is
~34% per accuracy point (earlier estimate from baseline-vs-CA5: ~30% per point).


## Error model: are Poisson bands right? (checked, 2026-09-11)

**Mostly yes.** Three concerns, in order of size:

1. **Binomial vs Poisson** -- k ~ Binomial(N, eps) with N ~ 2.005M fixed, but
   eps ~ 1e-4, so the (1-eps) correction is 0.01%. Irrelevant.
2. **Correlation between arms** -- I expected this to be the flaw (same jets, two
   models -> correlated fluctuations -> independent formula overstates the ratio
   error). **It does not apply**: the two arms are evaluated on DIFFERENT jet
   subsets. Baseline has 2,004,925 QCD jets, PLuM has 2,004,959; only **10.9% of
   positions agree**. The dataloader shuffles and drops a partial final batch per
   shard, so each run sees a slightly different draw. A PAIRED bootstrap is
   therefore impossible. *(Side effect worth knowing: every arm-to-arm comparison
   in this study carries a small extra sampling variance from this.)*
3. **Signal-threshold error** -- the working point is a quantile of the SIGNAL
   sample and has its own finite-sample error. Poisson omits it; a bootstrap
   includes it.

**Verified by bootstrap** (200 replicas, resampling signal and background, no
distributional assumption):

| Hbb @100k | ratio | bootstrap 68% | analytic Poisson |
|---|---|---|---|
| @50% | 1.195 | +0.101/-0.117 | +-0.108 |
| @70% | 1.118 | +0.052/-0.060 | +-0.054 |
| @90% | **1.032** | **+0.022/-0.024** | +-0.021 |

| Tbqq @100k | ratio | bootstrap | Poisson |
|---|---|---|---|
| @50% | 1.150 | +0.151/-0.107 | +-0.130 |
| @90% | 1.026 | +0.016/-0.016 | +-0.017 |

Agreement to ~10%, with mild asymmetry the analytic form cannot represent.
**Use the bootstrap for plots; Poisson is fine as a quoted formula.**

Note Hbb @90% at 100k: **1.032 +0.022/-0.024** vs the paper's **1.031**.

## Binary run: 80% of I/O is wasted (measured)

`BinaryFilteredLZ4Dataset` reads every shard and keeps only QCD + Hbb. Measured on
a real shard:

```
one shard: 2.6 s -> 27 batches of 512 (13,824 jets kept of 100,000)
-> 10.4 batches/s
-> 741 shards, ~32 min of pure dataloading, for the FIRST 20k-iteration checkpoint
```

So a binary job showing no checkpoint after ~50 min is **on schedule, not stuck**.
The design is correct (merging the other 8 classes into QCD would give a 9x
contaminated background) but wasteful: the filtering happens after decompression.

**If this is repeated**, pre-build a filtered dataset once rather than filtering at
load time -- 5x the training throughput for one up-front pass.


## Best single slide: `roccmp_Hbb.png` (100k solid vs 1M dotted)

One frame, four ROC curves + a ratio panel:
- **100k (solid)**: PLuM clearly above baseline from 0.3 to ~0.95 efficiency -- a broad,
  coherent effect, not a tail excursion.
- **1M (dotted)**: the two arms superimposed; ratio hugs 1.0, dipping slightly below
  between 0.4 and 0.8.
- Both 1M curves sit above both 100k curves -- that gap is the TRAINING gain, which
  visibly dwarfs the PLuM gain.

| | ratio @90% (bootstrap 68%) |
|---|---|
| 100k | **1.032 +0.017/-0.024** |
| 1M | **0.985 +0.020/-0.027** |

## Binary run: STOPPED by user request (2026-09-11)

condor 9299319 removed after 1 checkpoint. What it established before stopping:

- **The binary pipeline works end to end** -- models register and instantiate with
  `fc` out_features=2, `BinaryFilteredLZ4Dataset` drops the other 8 classes (verified:
  only truth values {0,1}), dataset symlinks resolve, 2,142,454 parameters.
- **binary baseline @20k: 97.972% val accuracy, loss 0.056** -- sane for a balanced
  2-class task (50% floor), and far easier than the 10-class problem (81.8% at 20k).
- **PLuM's binary arm never started**, so there is NO binary comparison.

Cost that made it impractical: ~60 min per 20k checkpoint => ~10 h/arm, ~20 h for the
pair, because `BinaryFilteredLZ4Dataset` discards 80% of every shard after
decompression (measured: 2.6 s/shard -> 27 usable batches of 512).

**To resume**: everything is in place (`config/jet_class_{binary,plum_binary}.yml`,
`utils/models/binary_hbb.py`, `utils/torch/BinaryFilteredLZ4Dataset.py`, registries
patched with `.bak_binary` backups, `~/flashjet_condor/run_binary.sh` + `binary.sub`).
Pre-build a filtered dataset first for 5x throughput.
