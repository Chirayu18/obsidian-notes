---
tags: [reference]
status: active
date: 2026-09-08
source: lxplus
---

# PLuM arm launched (4th arm) — condor 9283169

Implements [[2026-09-07-plum-reproduction-plan]] Phase 3, as a **full 10-class**
training rather than the paper's binary mode.

## What is running

```
config      jet_class_plum
model       ParticleTransformer_PLuM_JetClass
version     b_hive_paper_plum_1
1M iterations, batch 512, Ranger, lr 1e-3, batch_exp_decay, save every 20k
```
Identical hyperparameters to the baseline / CA5 / subjet arms — only the config
and model differ. Script `~/flashjet_condor/run_paper_plum.sh`. Clusters 9277912 (removed, AFS-idle theory that turned out to be plain queue contention) and 9278718 (HELD, 91 GB) preceded this one.

Dataset symlinks created at `output/DatasetConstructorTask/jet_class_plum/`
(train 1000 files, val 50, test 200, herwig 200 — all resolve).

## Deviation from the paper, stated in advance

Gouskos & Maier train **binary** (8M signal + 8M background per epoch, 10 seeds,
top-5 quoted). We train the **full 10-class** problem so the arm is comparable
with our three existing arms. A binary H->bb tagger can spend its whole capacity
on b-fragmentation; **10-class is the harder test**, and if the gain fails to
reproduce, "different task" is a confound that cannot be separated from "the
gain is not real". Decided before launch, not after seeing the result.

## Engineering findings

**1. The token module was rewritten before this run — the per-jet decode was
both wrong and ruinously expensive.** The first submission (9278718) was HELD by
condor: *"gone over cgroup memory limit of 48000 MB, last measured usage 91135
MB"*. That was **host** RAM; the GPU was healthy throughout at 31 GB / 98% util.

Cause: the module built the full `(B, J, S, 6)` output of
`lund_coordinates_from_history` and argmaxed over the jet axis — materialising
every jet in order to use one. At B=512 x J~21 x S~110, times 16 dataloader
workers, that is the 91 GB. The other three arms never hit it: `ca_features`
and `subjet_features` call `_pseudojet_p4` directly, which is `(B, 2N, 4)`.

The per-jet framing was wrong on physics too. A JetClass entry is **already one
jet** — 128 constituents of a single R=0.8 anti-kT jet, and the label describes
that jet. Re-clustering returns ~1.08 jets/event only because the beam distance
shakes loose one- or two-particle fragments at the cone edge: clustering
artifacts, not physics objects. The right operation is **take the 48 hardest
splittings by kT**; the fragments contribute 0-1 splittings at tiny kT and fall
below the cut on their own. That is also the most faithful reading of the paper
("up to 48 splittings are considered per jet", no jet selection mentioned).

Since the per-splitting channels are computed *before* any jet grouping in
`history.py` (`chans`, `(B, N, 6)`), replicating that and doing a top-k removes
the J axis entirely. Committed as `ca783af`. Validated on 2000 real jets:

| | per-jet decode | top-k rewrite |
|---|---|---|
| top-48 kT multiset | — | **matches 200/200 jets** |
| jets with zero splittings | 300/4000 | **0** |
| slots sorted by kT | 0.56 (C/A) | **1.000** |
| peak GPU @ B=512 | — | **81.5 MB** |
| host RAM | **91 GB → killed** | O(B·N) |
| time/batch @ B=512 | ~240 ms | **21.7 ms** |

**2. `_pseudojet_p4` cost — my earlier 240 ms figure was wrong, twice over.**
I first measured it on a *shared* lxplus-gpu T4 with 12.8 of 14.57 GB held by
four other users; kernel-launch latency is exactly the quantity that inflates
under contention. It was also measuring the wasteful per-jet path. The honest
numbers, from the arms' own checkpoint timestamps (20k iterations each):

| arm | per 20k | per step | vs baseline |
|---|---|---|---|
| baseline | 44 min | 132 ms | — |
| CA5 | 57 min | 170 ms | +38 ms (+29%) |
| subjet | 62 min | 187 ms | +55 ms (+42%) |

So the flashjet feature path costs **38-55 ms/step**, not 240. `_pseudojet_p4`
does still loop over all 128 merge steps in Python (`history.py:277`) with a
host sync each, and that is plausibly most of the 38-55 ms — but it is a
tolerable cost, not the crisis I described. **This run's first 20k block gives
the clean number for the token arm.**

**3. `torch.compile` tripped an inductor lowering bug** —
`TypeError: torch.bool is not supported by torch.iinfo` — from re-deriving the
dtype when padding the attention bias. Fixed with `attn_mask.new_zeros` /
`new_full` so the dtype stays tied to the tensor. The script attempts compiled
first and **falls back to uncompiled** rather than killing a multi-day job;
the log prints `UNCOMPILED_FALLBACK=1` if that happens, and training uncompiled
would be a real difference from the other three arms that must be reported.

**4. Parameter count matches the paper.** Ours **2,193,930** vs their stated
**2.19M** (baseline 2.143M vs their 2.14M). The paper's numbers are 3
significant figures, so this is consistency rather than proof — but the piece
they specify exactly, the [64, 256, 128] MLP from 3 inputs, is 49,792 params
and ours adds 50,411. The 619 difference is the LayerNorm/BatchNorm in b-hive's
`Embed` wrapper; the MLP dimensions themselves match exactly. Whether their
splitting embedding is normalised is not stated in the paper.

## Memory: this arm needs the 100 GB request, like the other trainings

Three submissions before one stuck:

| cluster | request | outcome |
|---|---|---|
| 9277912 | 32 GB | removed — I misread queue contention as an AFS-requirements bug |
| 9278718 | 32 GB | **HELD** at 73 GB (cgroup limit 48 GB) |
| 9280189 | 32 GB | removed at 73 GB before it could be held; rewritten module |
| **9281282** | **100 GB** | current |

**The token module was not the main cost.** The `(B, J, S, 6)` allocation was a
real bug and the top-k rewrite (`ca783af`) genuinely fixed correctness, but both
the old and the new module climb to ~73 GB. The dominant consumer is the **16
dataloader workers** (`--n-threads 16`), whose working set *grows through the
epoch* — 41.5 GB at 15 min, 73.2 GB at 45 min, verified live on the worker
(67.8 GB summed RSS), not a stale condor attribute.

**The request was mis-sized from the start.** `run_paper_plum.sub` was built by
copying an *inference* submit file's resource block (32 GB / 4 CPUs) while
taking the 16-CPU pattern from the run script. The established full-training
files here — `smoke.sub`, `smoke_ca.sub`, the only two with
`request_CPUs = 16` — both ask for **100 GB**. Use
`~/flashjet_condor/run_paper_plum_100g.sub` for this arm.

Note condor grants headroom above the request (the 32 GB job was enforced at
48 GB, and Herwig inference 9274984 requested 33 GB and used 44 GB), so a job
can exceed its request for a long time before dying. **Do not read a few equal
`MemoryUsage` samples as a plateau** — I called it "flat" twice from readings
taken inside an early plateau, and it then doubled.

## Validation: the tokens are physically correct

Run 2026-09-08 on 20,000 real JetClass jets (`~/flashjet_condor/test_lund_physics.py`).
This is the check that catches a wrong tree walk, which none of the plumbing
tests would.

**Hard kinematic prediction — dR of the hardest splitting vs 2m/pT.** For a
boosted two-body decay the opening angle is dR ~ 2m/pT. Nothing about a buggy
walk reproduces this by accident:

| class | jet mass | dR measured | 2m/pT | ratio |
|---|---|---|---|---|
| Wqq | 88.8 GeV | 0.309 | 0.294 | **0.97** |
| Hbb | 122.2 GeV | 0.427 | 0.404 | **0.99** |
| Tbqq | 172.2 GeV | 0.494 | 0.570 | 0.85 |

The recovered jet masses (W 88.8 vs PDG 80.4, H 122.2 vs 125, top 172.2 vs
172.7) confirm the momenta are read from the right columns and the walk finds
the actual decay. Tbqq's 0.85 is expected: a top is three-body, so 2m/pT
overestimates the hardest sub-splitting's angle. QCD's 0.83 is meaningless --
QCD has no decay scale.

**Ordering test — PASS.** Hardest-splitting ln kT relative to QCD:
Tbqq **+1.51**, Hbb +1.15, Wqq +0.75. Symmetric-splitting fraction rises with
prong count: QCD 0.355 -> Wqq 0.447 -> Tbqq 0.545.

**One prediction of mine was wrong, and it was the prediction not the code.**
I expected Tbl (leptonic top) to look most QCD-like as "1-prong"; it came out
at +1.22, above Hbb. A leptonic top still has a real b quark and a W decaying
to lepton+neutrino, so the jet has genuine hard structure. The "1-prong" label
was my oversimplification.

Together with the other checks the arm is validated as far as possible without
training: compiled vs eager match to **7.153e-07**, top-48 kT multiset matches
the per-jet decode **200/200 jets**, **zero** jets with no splittings,
no sentinels or NaN, ln z <= ln 0.5 everywhere, params **2,193,930**.

## Running: cluster 9283169, timing measured

Started 14:16:54 on b9pgpun015, compiled (`use_torch_compile=True`, no fallback).

| checkpoint | wall time | val acc |
|---|---|---|
| model_20000 | 15:31:54 (75 min, incl. startup+compile) | 81.736 |
| model_40000 | 16:41:24 (69.5 min) | 83.493 |

**Steady state ~70 min per 20k = ~210 ms/step.** This supersedes every earlier
overhead figure I quoted (+272%, 6x) -- those were measured at B=16 on a
contended shared T4 and on the pre-rewrite code path.

| arm | per 20k | per step | vs baseline |
|---|---|---|---|
| baseline | 44 min | 132 ms | — |
| CA5 | 57 min | 170 ms | +29% |
| subjet | 62 min | 187 ms | +42% |
| **PLuM** | **~70 min** | **~210 ms** | **+59%** |

Consistent with the mechanism: 48 extra tokens make attention (176/128)^2 ~ 1.9x
costlier, partly offset by compile. **Projection ~2.4 days to 1M iterations**,
comparable to the other arms.

**Memory sits at 122 GB against the 100 GB request** — over, but flat and
tolerated by condor's headroom (the same behaviour that let the 32 GB job run to
73 GB). Each of the 16 dataloader workers holds ~5.2 GB, up from ~3.0 GB
uncompiled: `reduce-overhead` CUDA graphs cost ~2 GB per worker on the host
while *reducing* device memory (31 GB -> 18 GB). If a future submission is held,
the lever is `--n-threads 8`, which halves worker memory and does not change the
learned function.

**First comparison at the matched 20k point** (nothing readable yet -- the gap
is ~1/10 of the 0.377-point noise floor at this stage):

| arm | acc@20k | loss@20k |
|---|---|---|
| subjet | 81.989 | 0.5063 |
| **PLuM** | **81.736** | **0.5088** |
| baseline | 81.765 | 0.5109 |
| CA5 | 80.463 | 0.5430 |

## Interim result at 260k (26% of 1M) — null on level, weak hint on SPEED

**Accuracy vs baseline, 13 matched checkpoints:**

| metric | mean Δ | ahead | noise floor | S/N |
|---|---|---|---|---|
| validation acc | **+0.023** | 8/13 | 0.364 | 0.06 |
| training acc | **+0.086** | 9/13 | 0.787 | 0.11 |
| validation loss | −0.0012 | 8/11 | 0.0100 | 0.12 |
| training loss | −0.0025 | 7/11 | 0.0228 | 0.11 |

All four favour PLuM slightly; all four sit at S/N ~0.06–0.12. Paired t on loss:
train t=−1.95 (p=0.080), val t=−1.01 (p=0.337) — neither significant, and
consecutive checkpoints are correlated so the effective n is below 11.

**The mean is DECAYING as points accumulate** — validation +0.095 (6 pts) →
+0.040 (12) → +0.023 (13). A real effect holds its size as n grows; this is
what a null looks like. The early +0.301 at 60k was an excursion.

**Pre-registered 200k test: FAILED** (−0.067). This is the same iteration where
subjet's apparent +0.125 at 140k collapsed to −0.364.

### The one statistic that favours PLuM: threshold-crossing speed

The user asked whether the arm at least *converges faster*. Tested horizontally
(iterations to first reach a given accuracy) rather than vertically, over 66
thresholds in 82.0–85.35:

**PLuM earlier at 16, later at 2, same checkpoint at 48.**
84.80 at 120k vs baseline 140k; 85.00 at 160k vs 180k — both 20k earlier.

Three caveats, all material:
- **Granularity is 20k**, so "earlier" means one checkpoint. Only 18 of the 66
  thresholds are informative, not 66.
- **It inverts at the top.** 85.10 is reached 40k *later*; at 85.30 baseline has
  arrived and PLuM has not. The advantage lives in the 84.8–85.0 band, below
  where the arms now train.
- **CA5 shows the same pattern and is a known deficit** (−0.041 at 800k+,
  t=−4.65). Early threshold order does not predict the final verdict.

"Same endpoint, fewer iterations" would be a legitimate and useful result if it
survived — but it needs the late window and ideally a second seed, and the
top-of-range behaviour currently points the other way. Re-run
`~/flashjet_condor/conv.py` at 800k+.

### Also checked: are PLuM's losses just baseline spiking?

Tested (`~/flashjet_condor/spike.py`): **no.** corr(Δ, baseline excursion) =
**+0.128** — near zero and the wrong sign; if baseline spikes drove the losses
it would be strongly negative. corr(Δ, PLuM excursion) = **+0.423**, three times
larger, so the deltas track PLuM's own wobbles more. At 140k (the biggest loss)
baseline sat at +0.003 of its local trend while PLuM fell −0.443.
Control: the same test on CA5 gives corr=+0.645, *higher* than PLuM, so this
metric does not separate real effects from noise either way.

## Guards in the script (all passed at submit)

`N_LUND_FEATURES=3`, `M_SPLITS_DEFAULT=48`, `lund_algorithm=kt`,
`lund_zero_pair_bias=true`. The last one matters most: `false` pads the
attention bias with `finfo.min`, which masks every splitting token out of
attention and silently reproduces the baseline — a bug that would look like a
null result. See [[2026-09-07-plum-paper-vs-our-result]].

## What to compare against when it lands

In-domain @980k, 20,046,720 test jets: baseline **86.211**, subjet 86.190,
CA5 86.156. Paper's claim to reproduce: **+12% Hbb rejection at 50% eff**
(5864 -> 6567) and +7% t->bqq — measured in binary mode on top-5-of-10 seeds,
with no per-seed spread published.

**Pre-registered:** report either way. One seed cannot resolve an effect near
the 0.088-point checkpoint noise floor, so a small positive result is a hint,
not a reproduction.
