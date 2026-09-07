---
tags: [reference]
status: active
date: 2026-09-08
source: lxplus
---

# PLuM arm launched (4th arm) — condor 9277912

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
and model differ. Script `~/flashjet_condor/run_paper_plum.sh`.

Dataset symlinks created at `output/DatasetConstructorTask/jet_class_plum/`
(train 1000 files, val 50, test 200, herwig 200 — all resolve).

## Deviation from the paper, stated in advance

Gouskos & Maier train **binary** (8M signal + 8M background per epoch, 10 seeds,
top-5 quoted). We train the **full 10-class** problem so the arm is comparable
with our three existing arms. A binary H->bb tagger can spend its whole capacity
on b-fragmentation; **10-class is the harder test**, and if the gain fails to
reproduce, "different task" is a confound that cannot be separated from "the
gain is not real". Decided before launch, not after seeing the result.

## Two engineering findings from the pre-launch profiling

**1. flashjet's `_pseudojet_p4` is launch-latency bound.** `history.py:277` loops
over all 128 merge steps in Python, each launching tiny GPU ops with a
`bool(pair.any())` host sync. Measured **flat in batch size**:

| B | `_pseudojet_p4` | per jet |
|---|---|---|
| 16 | 236 ms | 14761 us |
| 64 | 240 ms | 3749 us |
| 256 | 243 ms | 950 us |
| 512 | 243 ms | 474 us |

It is **98.5% of the token cost** (825 of 837 ms in the decode); the clustering
it depends on is only **2.8 ms**. At B=64 this made PLuM 6x slower per step than
baseline (177 -> 1086 ms). At the real B=512 the fixed ~243 ms amortises over 8x
more jets — **the per-step timing in this run is the measurement** that decides
whether flashjet wants the segment-scan rewrite. Could not be measured
beforehand: the shared lxplus-gpu T4 had 12.8 of 14.57 GB taken by other users
and OOM'd at B=512.

This is a **flashjet** finding, not a b-hive one, and it affects the CA5 and
subjet feature paths too (both go through `lund_coordinates_from_history` /
`groom_from_history`). Potentially a talk point: the clustering headline number
is 2.8 ms, but the history decode downstream users actually call is 243 ms.

**2. `torch.compile` tripped an inductor lowering bug** —
`TypeError: torch.bool is not supported by torch.iinfo` — from re-deriving the
dtype when padding the attention bias. Fixed by using `attn_mask.new_zeros` /
`new_full` so the dtype stays tied to the tensor. The script attempts compiled
first and **falls back to uncompiled** on any failure rather than killing a
multi-day job; the log prints `UNCOMPILED_FALLBACK=1` if that happens. Training
uncompiled would be a real difference from the other three arms and must be
reported if it occurs.

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
