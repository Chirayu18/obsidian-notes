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


## THE PRACTICAL VERDICT: PLuM@100k vs baseline@300k

The question a would-be adopter actually asks: **is the feature a substitute for
training?** Answer: no, and not close.

**Overall accuracy: PLuM@100k 84.697 vs baseline@300k 85.407 -- PLuM 0.709 BEHIND.**

| class | eff | PLuM@100k | base@300k | ratio | |
|---|---|---|---|---|---|
| Hbb | 50% | 8,988.7 | 9,322.9 | 0.964 +-0.092 | -- |
| Hbb | 70% | 2,441.5 | 2,831.1 | **0.862 +-0.044** | baseline better |
| Hbb | 90% | 446.0 | 520.5 | **0.857 +-0.019** | baseline better |
| Tbqq | 50% | 13,824.0 | 18,389.2 | **0.752 +-0.095** | baseline better |
| Tbqq | 70% | 2,669.1 | 3,789.1 | **0.704 +-0.040** | baseline better |
| Tbqq | 90% | 304.0 | 393.2 | **0.773 +-0.014** | baseline better |
| Hcc | 90% | 84.7 | 97.6 | **0.869 +-0.008** | baseline better |
| H4q | 90% | 53.6 | 58.6 | **0.913 +-0.007** | baseline better |

**Baseline@300k beats PLuM@100k on 11 of 12 measurements**, most by many sigma.
Tbqq is worst: PLuM@100k keeps only **70-77%** of baseline@300k's rejection.

### The cost comparison makes it worse

PLuM is **1.58x slower per step**, so:
- PLuM@100k costs the same wall-clock as **baseline@158k**
- baseline@300k costs only **~1.9x** what PLuM@100k costs

For under 2x the compute, plain training buys **+15-30% rejection**. The feature buys
**+3.7%** at 90% eff at matched iterations, decaying to zero by 1M.

### Statement for the talk

> **The Lund tokens are not a substitute for training.** At matched iterations they give
> a small early gain that vanishes by convergence. At matched COST they lose outright:
> the same GPU-hours spent on plain baseline training give substantially better tagging
> at every working point and every class tested.

This is stronger and more useful than "the effect decays", because it answers the
adoption question directly.


## The decay is FAST: dead by 300k, flat thereafter

PLuM@300k vs baseline@300k, matched checkpoint, 20.05M test jets:

**Overall accuracy: PLuM 85.405 vs baseline 85.407 -- difference 0.002.**

| class | eff | PLuM@300k | base@300k | ratio |
|---|---|---|---|---|
| Hbb | 50% | 9411.3 | 9322.9 | 1.009 +-0.098 |
| Hbb | 70% | 2734.8 | 2831.1 | 0.966 +-0.051 |
| **Hbb** | **90%** | 512.6 | 520.5 | **0.985 +-0.022** |
| Tbqq | 90% | 391.2 | 393.2 | 0.995 +-0.020 |
| Hcc | 90% | 96.5 | 97.6 | 0.989 +-0.010 |
| H4q | 90% | 59.8 | 58.6 | 1.020 +-0.008 |

### The decay curve (Hbb @90%, the best-measured point)

| stage | ratio |
|---|---|
| 100k | **1.032** +0.018/-0.022 |
| **300k** | **0.985 +-0.022** |
| 1M | **0.985** +0.020/-0.027 |

**300k is already statistically identical to 1M.** The gain does not decay gradually --
it is gone within the first few hundred thousand iterations and never returns. "PLuM
buys convergence speed" is therefore too generous: it buys a head start that the
baseline erases early, and after that the arms are indistinguishable.

500k inference cancelled (condor 9300151 removed) -- with 300k == 1M there was nothing
left to map between them. **40k inference submitted instead** (condor 9302099) to test
whether the gain is LARGER before 100k, which would bound its true size before decay.

**Caveat for the 40k point:** seed spread is largest early. The accidental second seed
differed from the first by 0.086 in validation accuracy at 40k. A large 40k ratio
measures one seed's head start, not a guaranteed property of the method.


## All classes at 100k / 300k / 1M -- and what explains it

Ratios @90% signal efficiency (best-measured working point):

| class | 100k | 300k | 1M |
|---|---|---|---|
| **Hbb** | **1.037 +-0.022** | 0.985 +-0.022 | 0.983 +-0.024 |
| **Hcc** | **1.027 +-0.009** | 0.989 +-0.010 | 1.001 +-0.011 |
| **Hgg** | **1.022 +-0.003** | 1.016 +-0.004 | 1.000 +-0.004 |
| **H4q** | **1.012 +-0.007** | 1.020 +-0.008 | 1.005 +-0.008 |
| **Tbqq** | **1.026 +-0.018** | 0.995 +-0.020 | 0.995 +-0.023 |
| Zqq | 1.002 +-0.004 | 0.999 +-0.004 | 1.000 +-0.004 |
| Wqq | 1.001 +-0.004 | 1.003 +-0.004 | 0.999 +-0.004 |

Overall accuracy delta: **+0.065 (100k) -> -0.002 (300k) -> -0.006 (1M)**.

**Five of seven classes gain at 100k and return to ~1.0 by 300k.** Several are
individually significant at 100k: Hgg 1.022 +-0.003 (7 sigma), Hcc 1.027 +-0.009,
Tbqq 1.026 +-0.018. **Zqq and Wqq never gain at any stage** (1.002, 1.001, to +-0.004).

### Explanation -- what is and is NOT established

**Established:** the gain is BROAD, not b-specific. Hgg -- no b-content at all -- has the
most significant gain in the entire study. That is incompatible with the paper's stated
mechanism (b-hadron displaced decays producing distinctive soft/wide-angle radiation),
which predicts gains on Hbb and Tbqq specifically.

**Tested and NOT established -- substructure complexity.** Hypothesis: the gain scales
with how much clustering structure a jet has. Against measured splittings/jet
(Hgg 42.9, Tbqq 36.3, H4q 35.2, Hbb 28.9, Hcc 26.8, Zqq 23.4, Wqq 21.6):

- Pearson r = **0.43** on 7 points -- **not significant** (p ~ 0.34)
- weighted fit predicts the endpoints well (+0.002 at Wqq, +0.022 at Hgg)
- but **Hbb is a large outlier**: biggest gain (+0.037) with below-median splittings

**The b-content hypothesis is not dead either**: b-jets average +0.0315 vs +0.0128 for
non-b. Real, in the paper's direction, but resting on 2 classes -- and it cannot explain
Hgg at 7 sigma.

**With one seed and seven classes these cannot be separated.** I initially presented the
complexity story as the explanation; that overstated the evidence.

### What survives regardless of mechanism

1. The gain appears at 100k across most classes -- **including ones the paper says
   should not gain**.
2. It is **gone by 300k** and identical to 1M thereafter.
3. **Zqq and Wqq -- the simplest two-prong light-quark topologies -- never gain**, to
   +-0.004.

Defensible reading: **the tokens supply structure the model can otherwise learn for
itself, so they help only before it has learned it.** Supported by the timing and the
breadth; the precise class-ordering mechanism is not established.


## 40k added: the effect is GENERIC, and two earlier claims were wrong

Four-stage table, @90% signal efficiency (PLuM/baseline):

| class | **40k** | 100k | 300k | 1M |
|---|---|---|---|---|
| Hbb | 1.009 +-0.019 | **1.037 +-0.022** | 0.985 | 0.983 |
| Hcc | 1.027 +-0.008 | 1.027 +-0.009 | 0.989 | 1.001 |
| Hgg | 1.009 +-0.003 | **1.022 +-0.003** | 1.016 | 1.000 |
| H4q | **1.037 +-0.007** | 1.012 +-0.007 | 1.020 | 1.005 |
| **Tbqq** | **1.095 +-0.016** | 1.026 +-0.018 | 0.995 | 0.995 |
| Zqq | **1.011 +-0.004** | 1.002 | 0.999 | 1.000 |
| Wqq | **1.036 +-0.004** | 1.001 | 1.003 | 0.999 |

Overall accuracy delta: **-0.003 (40k) -> +0.065 (100k) -> -0.002 (300k) -> -0.006 (1M)**

### CORRECTION 1: "Zqq and Wqq never gain" was WRONG

I stated this from the 100k/300k/1M table. With 40k included: **Wqq is 1.036 +-0.004
(9 sigma) and Zqq 1.011 +-0.004 at 40k.** They are flat from 100k onward but they DO
gain early. I should have hedged a claim about "never" when I had only late stages.

### CORRECTION 2: the mechanism stories are both dead

**Every class gains at 40k.** Not b-jets (kills the paper's displaced-decay mechanism),
not complex-substructure jets (kills the complexity story I floated -- Wqq has the
FEWEST splittings, 21.6, and one of the largest 40k gains). The effect is **generic**.

### Tbqq is the largest effect in the study

**1.095 +-0.016 (6 sigma) at 40k**, 1.224 +-0.051 at 70% eff, decaying monotonically
1.095 -> 1.026 -> 0.995 -> 0.995.

### The accuracy row is the giveaway

At 40k the accuracy delta is **-0.003** despite large per-class rejection gains. PLuM is
not classifying better overall there; it has shaped the discriminant TAILS differently.
The accuracy delta peaks at 100k (+0.065) and dies by 300k.

### Revised, simpler reading

**PLuM helps early, on everything, and the help is gone by 300k.** Different classes peak
at different stages (Tbqq and Wqq at 40k; Hbb and Hgg at 100k), all converging to 1.0.
No class-specific mechanism is needed or supported by the data.


## Sitian's "Lund attention share" hypothesis — tested, NOT supported (2026-09-14)

**The hypothesis** (Sitian, ML4Jets 2026): PLuM is not new information, it is an
*inductive bias* — it re-directs ParT's attention toward the Lund plane. So the gain
should scale with the **"loss of Lund attention share"**: classes where the baseline
under-attends Lund structure should gain most. He named **Hbb, Tbqq, H4q, Hcc** as the
largest-loss classes and read them as the fast-converging ones.

This is worth taking seriously: it *predicts* the decay we measured (the baseline
eventually learns the allocation itself), rather than being retrofitted to it.

**Test.** Early gain vs C/A splittings per jet — the available proxy for "how much Lund
structure is there to attend to". Both quantities were already measured (gains @90 %
eff; splittings on 100k real JetClass jets). Plot:
`analysis/make_gain_vs_splittings.py` (numbers inline, regenerates in ~1 s).

| | Pearson $r$ | $1/\sigma^2$-weighted $r$ | Spearman |
|---|---|---|---|
| 40k | +0.19 | **−0.42** | +0.04 |
| 100k | +0.43 (p~0.34) | **+0.87** | +0.43 |

**The verdict is the instability, not either number.** The weighted correlation swings
**−0.42 → +0.87 between two adjacent checkpoints**, and the per-class gain ordering
**anti-correlates with itself across those checkpoints: Spearman = −0.32**.

- 40k ranking: Tbqq, H4q, **Wqq**, Hcc, Zqq, **Hbb**, **Hgg**
- 100k ranking: **Hbb**, Hcc, Tbqq, **Hgg**, H4q, Zqq, **Wqq**

Hbb goes 6th → 1st; Wqq goes 3rd → last; Hgg goes last → 4th. A mechanism tied to a
*fixed structural property of each class* cannot produce an ordering that reverses in
60k iterations. The +0.87 at 100k is the kind of number that looks like support if you
only measure at one checkpoint — 40k is what kills it.

**On the four named classes**: they do average higher than the rest (+0.023 at 40k,
+0.017 at 100k), so the intuition is not baseless. But **Wqq — the fewest splittings
(21.6) — gains 1.036 ±0.004 (9σ) at 40k**, and **Hgg — the most (42.9) — gains least**
at 40k. The separation is carried by which checkpoint you look at, not by structure.

**This supersedes nothing above** — it is the same conclusion as "CORRECTION 2: the
mechanism stories are both dead", reached against a new and better-motivated
hypothesis. Recorded because the hypothesis will come up again.

### What would actually test it (not done)

The proxy is the weak link: splittings/jet measures *available* Lund structure, not
*attention share*, which is the real claim and is directly measurable on checkpoints
we already have.

1. attention mass on the 48 Lund tokens, per class, at 40k / 100k / 1M — his mechanism
   needs it high early and decaying. If it is flat, the mechanism fails regardless.
2. in the **baseline**, attention concentration on the pairs that are the hard
   splittings — that is the "loss" quantity that should predict per-class gain.

Both are a day on existing checkpoints. Caveat that applies to any such ranking:
**one seed per arm**, and two PLuM seeds differ by 0.132 in val accuracy at 100k —
comparable to the whole effect. A 7-class ordering is not seed-stable either.


## Lund ATTENTION measured directly — the mechanism's premise fails (2026-09-14)

The splittings-vs-gain test above used a *proxy*. This measures the thing Sitian's
hypothesis is actually about: **how much of ParT's attention lands on the 48 Lund
tokens**, per class, at 40k / 100k / 300k / 1M.

Scripts: `analysis/measure_lund_attention.py` (condor 9314077, 5120 jets per
checkpoint, ~4 min each on 8 CPU), `analysis/plot_lund_attention.py`.
Raw numbers: `analysis/lund_attention_cpu.json`.

**Method.** Each block's `nn.MultiheadAttention` is wrapped in a shim forcing
`need_weights=True` — the checkpoint is the trained artefact and is not edited.
Two quantities: **CLS attention** in the 2 class-attention blocks (the jet-level
decision) and **encoder self-attention** averaged over particle queries.

**The normalisation is the whole point.** The 48 Lund tokens are **~46 % of the
sequence** (measured: 46.6 valid lund vs 59.0 valid particles). A model attending
*at random* would put ~46 % of its mass on them. So the raw share is meaningless;
everything below is **measured / uniform**, with padded particles and invalid lund
slots excluded from both numerator and null, per jet.

### Result 1 — the tokens are attended FAR LESS than chance, always

CLS attention / uniform:

| class | 40k | 100k | 300k | 1M |
|---|---|---|---|---|
| TTBarLep | 0.480 | 0.399 | 0.290 | 0.236 |
| HToWW4Q* | 0.437 | 0.329 | 0.264 | 0.217 |
| HToCC* | 0.408 | 0.371 | 0.288 | 0.230 |
| HToGG | 0.418 | 0.377 | 0.277 | 0.223 |
| ZJetsToNuNu | 0.440 | 0.413 | 0.305 | 0.262 |
| ZToQQ | 0.336 | 0.309 | 0.236 | 0.193 |
| WToQQ | 0.372 | 0.292 | 0.232 | 0.196 |
| **mean** | **0.413** | **0.356** | **0.270** | **0.222** |

**Every entry is below 1.** At its peak the jet-level decision gives Lund tokens
under **half** the attention their token count alone would warrant. They are 46 %
of the input and never win more than ~22 % of CLS attention (raw: 15-22 % at 40k,
9-12 % at 1M).

### Result 2 — CLS attention decays monotonically, −46 %

Mean 0.413 → 0.222, **monotone in all 7 classes**, no exceptions. This is the decay
Sitian predicted, and it is real.

### Result 3 — but encoder self-attention RISES over the same window

Self-attention / uniform, mean: **0.26 → 0.28 → 0.31 → 0.37**, also monotone, also
every class. The two panels move in **opposite directions**.

### What this means for the hypothesis

**The prediction is confirmed and the mechanism is still not supported.** Sitian
predicted decaying Lund attention; CLS attention decays 46 %. But the mechanism
requires the tokens to be *attended more than the model would otherwise* — an
inductive bias that redirects attention *toward* the Lund plane. They are attended
**2-5x LESS than chance at every checkpoint**, including the earliest one where the
gain is largest. You cannot explain a gain by a redirection that never happens.

The rising self-attention is the more likely story: the encoder is **integrating**
the lund information into the particle representations over training, after which
CLS reads it from the particles instead of from the tokens. That is consistent with
"the tokens supply structure the model can otherwise learn for itself" (above) — but
it is a *redundancy* account, not an *attention-share* one.

### Caveats

- **5120 jets/checkpoint**, no error bars. The trends are large (46 % decay, monotone
  in 7/7 classes) and will not be overturned by statistics, but per-class *ordering*
  here is not resolvable — the same limitation as the gain ranking.
- **Three classes (HToBB, TTBar, HToWW2Q1L) are missing — a SAMPLING BUG, not
  statistics.** Within each shard the jets are sorted by class in contiguous blocks
  (verified: rows 0-1000 of `file_0.lz4` are all class 3). The sampler took the
  leading rows of every shard, so it only ever saw whichever class sits first.
  **HToBB is Sitian's headline class**, so the per-class read above is incomplete
  and the 7 classes shown are not a random sample of the 10.
  Fixed in `measure_lund_attention.py` (random permutation within each shard);
  rerun is condor 9314110 (8k jets), GPU 20k run 9314058 still queued.
  **The three headline results are unaffected** — every one of the 7 measured
  classes is below uniform at every checkpoint, CLS decays monotonically in 7/7,
  self-attention rises in 7/7. A missing class could change the per-class ordering,
  not a 2-5x effect that holds without exception in everything measured.
- Attention share is not the same as *causal* importance. A token can be attended
  little and still matter. The decisive follow-up is **ablating the lund tokens at
  each checkpoint** and measuring the accuracy drop.

### ABLATION (2026-09-14): the tokens ARE load-bearing — attention share was the wrong proxy

Attention share says where attention *goes*, not whether the model *depends* on it.
Masking the 48 Lund tokens out of attention entirely and re-running the same
checkpoint on the same jets measures the dependence directly.
Script: `analysis/ablate_lund_tokens.py`.

**Smoke test, 512 jets, 40k checkpoint** (condor 9314117 running this at 8000):

| | intact | ablated | drop |
|---|---|---|---|
| **overall** | 85.55 % | 80.47 % | **+5.08** |
| **HToBB** | 88.10 % | 66.67 % | **+21.43** |
| TTBarLep | 81.63 % | 73.47 % | +8.16 |
| HToWW4Q | 76.09 % | 69.57 % | +6.52 |
| HToWW2Q1L | 80.65 % | 74.19 % | +6.45 |
| ZToQQ | 97.14 % | 91.43 % | +5.71 |
| HToGG | 67.35 % | 63.27 % | +4.08 |
| TTBar | 80.00 % | 76.67 % | +3.33 |
| HToCC | 98.28 % | 96.55 % | +1.72 |
| ZJetsToNuNu | 68.42 % | 68.42 % | 0.00 |
| WToQQ | 100.00 % | 100.00 % | 0.00 |

**This overturns the natural reading of the attention result.** The tokens are
attended 2-5x LESS than chance and yet removing them costs 5 accuracy points at
40k — and **21 points on HToBB, Sitian's headline class**. Low attention share is
NOT low importance: attention is a weighted average, and a small weight on a large,
distinctive value vector still moves the output.

**So the correct statement is narrower than "the mechanism fails."** What the
attention measurement rules out is the specific claim that the gain comes from
*re-allocating attention mass* toward the Lund plane — that allocation never
happens. It does NOT rule out the tokens mattering, and they clearly do.

**And HToBB ranking first here is the first evidence FOR Sitian's per-class
intuition** that has survived a test. His four named classes (HToBB, TTBar,
HToWW4Q, HToCC) are not cleanly on top — HToCC is near the bottom at +1.72 — but
HToBB leading by 3x is exactly what he predicted, and it is absent from the gain
ranking where checkpoint noise dominated.

Caveats: 512 jets, ~30-80 per class, no error bars — HToBB's +21.4 rests on 42
jets and could move several points. The 8000-jet run settles it. The decisive
number is the **drop at 40k vs at 1M**: the redundancy account predicts it shrinks
as the encoder folds the information into the particle representations (which is
what the rising self-attention shows).

### Attention rerun with the sampling bug fixed — all 10 classes (2026-09-14)

condor 9314110, 8192 jets/checkpoint, ~800 per class, random permutation within
each shard. `analysis/lund_attention_cpu2.json`. **Supersedes the 7-class numbers
above for per-class reading; the three headline results are unchanged.**

| | 40k | 100k | 300k | 1M |
|---|---|---|---|---|
| CLS ratio, mean over 10 classes | 0.410 | 0.346 | 0.265 | **0.214** |
| self ratio, mean over 10 classes | 0.253 | 0.266 | 0.303 | **0.363** |

- **Below uniform everywhere**: max CLS ratio anywhere is **0.478**. Confirmed on
  all 10 classes, all 4 checkpoints.
- **CLS decays −47.8 %**, and is **strictly monotone in 10/10 classes**.
- **Self-attention rises +43.9 %**, monotone in **8/10**. ZToQQ (0.231 → 0.231) and
  WToQQ (0.270 → 0.265) are flat-or-slightly-down over the first step, then rise.
  Earlier "7/7 monotone" for self-attention was true of the biased sample only —
  **the correct claim is 8/10, with two flat first steps.**

**The sampling bug cost coverage, not accuracy.** Every class present in both runs
agrees to ≤0.004 in CLS ratio at 40k (e.g. TTBarLep 0.480 → 0.478, ZToQQ 0.336 →
0.338). So the earlier conclusions were not distorted, they were just drawn from 7
of 10 classes.

**HToBB, the class Sitian named**: CLS ratio 0.406 → 0.323 → 0.244 → **0.195**, the
**lowest of all 10 at 1M**. It is not attended more than the others at any stage —
it ends up attended least. Whatever makes HToBB special (and the ablation says
something does), it is not a larger share of attention.

### ABLATION at 8k: the drop GROWS with training — my redundancy account is FALSIFIED

condor 9314117, 8192 jets per checkpoint. `analysis/lund_ablation_cpu.json`.

| | 40k | 100k | 300k | 1M |
|---|---|---|---|---|
| intact | 83.643 | 83.997 | 85.828 | 86.389 |
| ablated | 76.819 | 69.250 | 69.434 | **61.145** |
| **drop** | **+6.82** | **+14.75** | **+16.39** | **+25.24** |

**I predicted this would SHRINK.** The redundancy account said the encoder folds the
Lund information into the particle representations (which the rising self-attention
shows), so by 1M the tokens should be removable at little cost. The opposite
happened: removing them costs **4x more** at 1M than at 40k.

So the trained model is **more** dependent on these tokens the longer it trains,
while simultaneously **gaining nothing** from them on the test set (-0.006). Those
two facts together are the real puzzle, and neither Sitian's account nor mine
explains them.

### Is the ablation off-manifold? Partly — and this is the key caveat

HToWW4Q at 1M drops to **3.95 %**, *below* the 10 % random baseline. A model that had
merely lost useful information would degrade toward chance, not below it. Masking all
48 tokens is an input the model **never saw in training** (real jets always have
splittings), so the residual stream lands off-distribution.

Diagnostic (`analysis/ablation_diagnostic.py`, 2048 jets, 1M):

| predicted class | intact | ablated |
|---|---|---|
| TTBarLep | 173 | **326** |
| TTBar | 118 | **328** |
| HToWW4Q | 141 | **7** |
| HToBB | 136 | **29** |
| ZToQQ | 289 | 100 |
| WToQQ | 356 | 369 |

Largest single predicted class: **18.0 % ablated vs 17.4 % intact** — so it is *not*
a total collapse onto one class, which is what a pure off-manifold artifact usually
looks like. But the redistribution is systematic: the model stops predicting HToWW4Q
and HToBB almost entirely and over-predicts the two top classes.

**Rai & Ganguly hit this exact problem** ([2605.09881], §4): they document "a
structural incompatibility between off-manifold (Gaussian) corruption and the
standard recovery-score formulation ... for any kinematically narrow physics
dataset", and use **on-manifold corruption** instead — patching in activations from
a *different real jet* rather than zeroing.

**Therefore the +25.24 number is not interpretable as "dependence".** It mixes real
dependence with off-manifold breakage, and the two cannot be separated by this
measurement. The honest statement:

- The tokens are **not** freely removable at any checkpoint — that much is solid.
- The *magnitude* and the *growth with training* are confounded by the corruption
  being off-manifold, and the growth may simply reflect a sharper, more confident
  model being easier to push off-distribution.

**What would fix it:** on-manifold ablation — replace the 48 Lund tokens with those
from a *different randomly chosen jet of the same class* (preserving the input
statistics the model expects), or with the class-mean token block. That is a small
change to `ablate_lund_tokens.py` and is the correct next measurement.

**Status of the mechanism: OPEN.** Neither account survives. What is measured and
safe: the features are redundant in content (PairEmbed computes the same three
functions per pair), the tokens are attended far below chance and decreasingly so,
the gain decays to null by 300k, and the tokens cannot be zeroed without damage.
Why a model that gains nothing from them also cannot lose them is **unexplained**.

## The noise floor is LARGER than the between-arm spread (2026-09-14)

Measured while preparing the CAPair run. This is the sharpest quantitative
statement in the study, and it reframes every arm comparison.

Validation accuracy over the **last 10 saved checkpoints** of each 1M run
(saves are 20k iterations apart, so these are late-training points at
convergence):

| arm | mean (last 10) | sd | min | max | vs baseline |
|---|---|---|---|---|---|
| baseline | 0.86148 | 0.00100 | 0.85952 | 0.86230 | — |
| ca (per-particle) | 0.86100 | 0.00108 | 0.85847 | 0.86194 | **-0.00048** |
| subjet | 0.86147 | 0.00110 | 0.85910 | 0.86233 | **-0.00001** |
| plum | 0.86196 | 0.00090 | 0.85987 | 0.86266 | **+0.00048** |

**Typical within-run late sd = 0.00102. Total between-arm spread = 0.00080.**

The noise a single run shows *against itself* between adjacent late checkpoints
is larger than the entire difference between the four arms. Every arm-to-arm
difference is well under 1 sigma.

### Two corrections this forces

1. **Stop quoting `best_acc`.** Comparing maxima over 50 noisy samples is biased
   upward and rewards whichever run happened to fluctuate highest -- that, not
   any property of the features, is why PLuM looked "best" at 0.8627 vs baseline
   0.8623. On late-training *means* the ordering is plum > baseline ~ subjet > ca,
   all within noise. I had quoted the maxima earlier in this session.
2. **A single run cannot resolve an effect of this size.** Consistent with the
   accidental-second-seed section above (seed-to-seed |diff| mean 0.145 pp at
   early iterations, 0.068 pp late) -- that was a BETWEEN-run estimate, this is a
   WITHIN-run one, and they agree that the design is underpowered for ~0.05 pp
   effects.

### Why this STRENGTHENS the null

"Three encodings gave no gain" was an eyeballed claim. It is now quantitative:
**all differences lie below a measured noise floor.** That is a claim a referee
cannot wave away, and it needs no seed replicates -- the within-run variance is
a legitimate noise estimate from data already on disk.

It also sets the bar for CAPair: to be visible at all, depth would have to clear
roughly **0.002** (2 sigma). A returned value of 0.8630 would NOT be
distinguishable from noise, and should not be reported as a gain.

## CAPair arm: depth channel added, submitted as cluster 1118678 (2026-09-14)

The pairwise-bias arm was **already built on 2026-09-04** (commit e0ad1cf,
`utils/models/particletransformer_ca_pair.py`) and never trained past a smoke
test -- baseline and PLuM both went to 1M, this one has only `smoke_capair_v1`.
Its two channels are `share_bp` (same branch point) and `lnkt_lca`.

**Added a third channel, `pair_ca_depth_lca`** (commit 507e7c9). Rationale: the
existing two describe the branch point's KINEMATICS, which pair momenta partly
determine, whereas depth counts TREE STEPS -- a property of the whole event's
clustering that `PairEmbed` provably cannot reconstruct from a pair's
four-vectors. This is the one respect in which CAPair differs in KIND from the
three null arms, all of which supplied kinematic functions ParT already
computes pairwise.

Validated on 1024 real JetClass jets, all 10 classes:

| channel | density | unique | note |
|---|---|---|---|
| `share_bp` | 10.7% | 2 | matches the 9.6% the Rule C comment records |
| `lnkt_lca` | 59.4% | 5305 | |
| `depth_lca` | 59.4% | 16 | range [0, 2.83] in log1p |

`depth` vs `share_bp` \|r\|=0.28, vs `lnkt_lca` \|r\|=0.21 -- **not redundant**.
Model builds at `pairwise_lv_dim` 4+3=7 (BatchNorm1d(7), 2.144 M params);
fwd/bwd on a real batch gives loss 2.333 ~ ln(10), gradnorm 6.49.

### Two traps hit on the way (both would have wasted days)

1. **Hand-slicing the shard was wrong.** Each row is
   `[15 global | 128 x 23 cpf | 10 labels | 2 trailing]` = 2959 feature columns.
   Slicing from column 0 shears every particle by 15 floats: it reported 18.4
   "valid" constituents (vs the true 38.0) and 0.2% feature density, which looked
   exactly like a degenerate feature and produced a spurious `depth`-vs-`share_bp`
   \|r\|=0.965 "redundant" verdict. **Drive `model.get_inpt(raw)` instead of
   rebuilding the layout by hand.**
2. **`torch.compile` would have killed the job** (commit bbc2606). `ca_pair_context`
   calls `flashjet.cluster`, whose triton-large backend does
   `mask.contiguous().view(torch.uint8)` -- inductor cannot lower it
   (`torch.bool is not supported by torch.iinfo`), surfacing as
   `BackendCompilerFailed`. This is the SAME failure a22ae1c fixed for PLuM
   (job 9281282, rc=40) in a different file; CAPair predates that fix and never
   got the guard. **All four earlier checks passed EAGER and none could have
   caught it.** Fixed with `torch._dynamo.disable`; compiled fwd+bwd now
   completes. NB verified on CPU, not the triton-large GPU backend.

### Expectation

**~15% chance of a gain that survives**, unchanged by any of the above work --
fixing the crash only buys the right to get a number. Three encodings of the same
information already came out null, and the noise-floor section above shows depth
must clear ~0.002 to be visible at all. The run's value is closing the obvious
referee objection: *"you never tested information the architecture provably
lacks."* A clean negative there makes the null materially stronger.

Submit dir is `/eos/user/c/cgupta/flashjet/condor/` -- the EosSubmit schedd
rejects any submit file with AFS exec/log/output paths, so `~/flashjet_condor`
cannot be used for GPU jobs.

## depth_lca SURVIVES two falsification tests (2026-09-14)

Run before spending a GPU on CAPair, to test the premise the whole arm rests on:
*depth is information `PairEmbed` cannot reconstruct from pair kinematics.*
Decision rule fixed BEFORE seeing results (R^2 > 0.8 kill the job, 0.4-0.8
limited headroom, < 0.4 genuinely new).

### Test 1 -- linear probe on the TRAINED 1M baseline's attention bias

Checkpoint verified (`acc_val=0.8623`, 0 missing / 0 unexpected keys; an earlier
attempt unwrapped the wrong key and left `pair_embed` RANDOMLY INITIALISED --
caught only by an assert). Probe: 8 bias channels -> CA feature, 1800 jets.

| channel | R^2 |
|---|---|
| `share_bp` | **+0.322** |
| `lnkt_lca` | +0.004 |
| `depth_lca` | **+0.039** |

`share_bp` scoring highest is the sanity check: it is the most kinematically
determined of the three, so partial recoverability there is what a working probe
should show.

### Test 2 -- can an MLP predict depth from PairEmbed's own four inputs?

Given (ln kT, ln z, ln delta, ln m^2) per pair -- exactly what `PairEmbed` sees:

```
linear             R^2 = +0.038
MLP(4->64->64->1)  R^2 = +0.062
```

**The two tests corroborate independently: 0.039 (trained model) vs 0.062
(proxy MLP).** Different method, different data, same answer.

### Test 3 -- does depth discriminate classes at all?

Per-jet mean of each channel, 1-D AUC class-vs-rest, 4800 balanced jets:

| class | share_bp | lnkt_lca | **depth_lca** |
|---|---|---|---|
| QCD | 0.302 | 0.549 | **0.271** (0.729 inverted) |
| Hgg | 0.290 | 0.560 | **0.701** |
| H4q | 0.448 | 0.612 | **0.693** |
| Tbqq | 0.462 | 0.476 | **0.690** |
| Wqq | 0.598 | 0.474 | 0.381 |
| Zqq | 0.580 | 0.459 | 0.396 |

A single scalar reaches AUC 0.69-0.73 on Hgg / H4q / Tbqq / QCD, and the sign
is physical: multi-prong decays separate LATE in the tree, QCD early.

### What this does and does not establish

**Does:** depth is (a) not in the trained model, (b) not computable from
`PairEmbed`'s inputs, (c) class-discriminating on its own. This is the FIRST
result in the study that supports running an arm. It also quantifies why the
other arms failed -- `share_bp`, a kinematic quantity, is 32% recoverable from
the trained bias; the three null arms supplied exactly that kind of feature.

**Does NOT:** discriminating is not the same as ADDITIVE. ParT is at 86.2%
using everything else; the real question is whether depth is *conditionally*
novel given 2.1M trained parameters, which none of these tests can answer. A
linear probe is also only a LOWER bound on what the model encodes.

**Unexplained:** `lnkt_lca` at R^2=0.004 on the trained probe. It is an
explicitly kinematic quantity and should have been MORE recoverable than
`share_bp`, not less.

**Estimate revised 15% -> ~40%.** The noise floor still binds: depth must clear
~0.002 to be visible at all. Recommendation: let cluster 1118678 run. A null now
means something far stronger than the previous three, because we can say we
tested information the architecture demonstrably lacks.

Scripts: `~/flashjet_condor/check_disc.py`, `check_probe.py` (lxplus AFS).

## Why the `ca` arm failed: NOT redundancy (2026-09-14)

Prompted by the user pointing out that `ca` already shipped `part_ca_depth` --
which it did, and which I had failed to check before recommending a depth-based
arm. Chasing that down overturned the standing interpretation of this arm.

### Four facts, all measured

| question | answer | evidence |
|---|---|---|
| did the features reach the model? | **yes** | `input_bn` width **22** vs baseline **17** = exactly +5 |
| are they informative? | **yes** | depth alone: AUC **0.810** (Hgg), 0.733 (H4q), 0.710 (Tbqq) |
| can ParT compute them itself? | **NO** | R^2 **0.33-0.44**, controls 1.000 / -0.001 |
| what did they do? | **HURT early** | **-1.302 pp @ 20k** -> -0.105 @ 1M, monotone |

Probe detail (ParT's own 17 token features -> each CA column, MLP 17->64->64->1):

```
part_ca_lnkt    0.440      tok[0] control   1.000  OK
part_ca_has_bp  0.417      tok[6] control   1.000  OK
part_ca_lnz     0.351      noise  control  -0.001  OK
part_ca_lndR    0.345
part_ca_depth   0.330
```

A first version of this probe reported similar numbers with a BROKEN control
(-0.008): it was asked to predict `px`, which the `[..., :-4]` split had already
removed from its inputs. Numbers from that run are void. The rerun above uses
in-block controls plus a noise control, and all three behave correctly.

### What this rules out, and what it implies

**The arity argument does NOT explain this arm.** ParT cannot compute these
columns from its own per-particle inputs -- nothing reaches 0.7. The features
were novel, informative, and correctly delivered, and the model still ended up
marginally worse.

**The early-damage curve identifies the mechanism.** Compare the three arms as
pp vs baseline:

| | ~20k | ~40k | ~100k | ~300k | 1M |
|---|---|---|---|---|---|
| **ca** | **-1.302** | -0.458 | -0.433 | -0.225 | -0.105 |
| subjet | +0.224 | +0.065 | -0.068 | +0.010 | +0.010 |
| plum | -0.029 | +0.027 | +0.096 | +0.033 | +0.113 |

A redundant input is IGNORED and sits flat -- that is `subjet` at +0.01. An
input costing **1.3 pp at 20k (13x the noise floor)** is one the model must
spend capacity learning to **suppress**, converging back to neutral once it has.
That is a PRESENTATION failure, not a content failure.

Two candidate defects, both flagged as risks in the original plan file:
1. **raw integer `depth`** (max 20, heavy tail) dropped into a block of
   log-scaled O(1) features;
2. **the all-zeros sentinel** -- `has_bp=0` sets ALL FIVE columns to zero, and
   zero is a legitimate value for `lnz` (z->1) and for `depth`, so "missing"
   is indistinguishable from "measured".

### BOTH presentation hypotheses are FALSIFIED (measured immediately after)

| hypothesis | prediction | measured | verdict |
|---|---|---|---|
| H2' zeros collision | "missing" collides with real values | sentinel rows 2.85%, **collisions 0.000%** | **REJECTED** |
| H3 conditioning | depth is badly scaled vs ParT's inputs | depth \|max\|/sd **9.55** vs ParT mean 7.89, ParT **worst 25.69** | **REJECTED** |

The zero convention the plan file chose actually works: `lnz` is bounded above
by 0 but never reaches it on real jets, so "missing" stays distinguishable.
And depth is 2.7x BETTER conditioned than ParT's own worst column, before
`input_bn` even normalises it.

**So the presentation story is wrong too.** That is the THIRD mechanism proposed
for this study and falsified by measurement (redundancy -> falsified by the Lund
ablation; presentation -> falsified here).

### What actually survives: an unexplained result

- features arrived (input_bn 22 vs 17) OK
- features are informative (depth AUC 0.810) OK
- features are NOT redundant (R^2 <= 0.44, controls clean) OK
- features are well conditioned (9.55 vs ParT's 25.69) OK
- sentinel convention is clean (0.000% collisions) OK
- and `ca` still cost **-1.302 pp @ 20k**, decaying to -0.105 @ 1M

Novel, informative, correctly delivered, well-scaled information made the model
measurably WORSE early and neutral late. **No mechanism currently explains this.**

One observation, offered as a lead rather than an answer: the early cost may
simply scale with the NUMBER of added columns -- `subjet` added 3 and cost
+0.22/-0.02 at 20k/40k, `ca` added 5 and cost -1.30. That would be a
capacity/optimisation effect, not an information one, and it predicts the early
penalty tracks column count rather than feature content. PLuM is not a clean
comparison (it adds TOKENS, not columns). A cheap test would be a 1-column
variant of `ca` at 40k.

### Consequence for the talk

"All three arms are explained by redundancy" is **too strong**, and I helped
build that claim. It holds for PLuM -- whose tokens really are a kT-ordered
subsample of what `pairwise_lv_fts_paper` computes per pair -- but for `ca` it
is measurably wrong. That arm failed for an engineering reason.

This also reopens CAPair, which I had recommended killing on the grounds that
`ca` "already tested depth". It did not test it fairly: CAPair log1p-scales
depth, puts it in the pairwise channel, and has no all-zeros collision. No
revised probability until the presentation defects are quantified -- this number
has moved twice today already, both times prematurely.
