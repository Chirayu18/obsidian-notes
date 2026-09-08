---
tags: [reference]
status: active
date: 2026-09-08
source: lxplus
---

# PLuM arm launched (4th arm) — condor 9280189

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
