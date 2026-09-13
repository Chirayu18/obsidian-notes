---
tags: [reference]
status: active
date: 2026-09-12
source: lxplus
---

# Event-regime timing sweep — scripts written and submitted

Supersedes the TODO in [[2026-09-12-event-regime-timing-todo]] (that note says what
to build; this one says what was built and where it runs).

## What was written

All under `/eos/home-c/cgupta/flashjet/bench_event/`:

| file | what |
|---|---|
| `sweep_event_flashjet.py` | GPU timing, one **event** per unit, ITERS=20 |
| `sweep_event_fastjet.py` | FastJet on the **same saved ragged file**, ITERS=3, + agreement check |
| `run_event_sweep.sh` | runs both back to back |
| `event.sub` | condor submit, **pinned to Tesla V100S-PCIE-32GB** |
| `make_event_plots.py` | `event_abs_timing.png` + `regime_throughput.png` + text table |
| `smoke.sh` / `smoke.sub` | 40-event GPU smoke test (espresso flavour) |

Mirrors the jet-regime pair (`bench_atlas/sweep_{flashjet,fastjet}.py`) exactly:
warmup, `torch.cuda.synchronize()`, ITERS-averaged, both sides reading the same
file, agreement checked (n_jets + leading-jet pT within 1e-4).

Grid: 3 algorithms x 5 radii x 5 multiplicity bins on cluster count per event
(lo 150-400, mid 400-600, hi 600-800, vhi 800-1500, all).

## Input

`data/opendata/opendata_constit_atlasevent_ak4.npz` — **3000 events**, mean
**591.6** clusters/event, range 150-1431. Built by `bench_atlas/dump_atlas_jetreco.py`.

## Why V100S specifically

The jet-regime sweep already in the deck ran on **Tesla V100S-PCIE-32GB**
(verified by reading the `gpu` field out of `results_v100/*_flashjet.json`, not
assumed from the directory name). Pinning the same card is what makes the two
regimes comparable on one axis. The pool has ~19 V100S and 17 were free at submit
time, so pinning costs little queue time.

## Submission — EosSubmit, not the standard pool

Plain `condor_submit` **refuses** these submit files: *"Standard batch schedds
cannot use /eos paths directly."* Per [[lxplus-condor-eossubmit]]:

```bash
ssh lxplus 'source /etc/profile.d/modules.sh; module load lxbatch/eossubmit; \
            cd /eos/home-c/cgupta/flashjet/bench_event && condor_submit event.sub'
```

Submit files need `should_transfer_files = NO` and `getenv = False` (the runner
uses absolute interpreter paths, so nothing depends on inherited env).

`condor_q` only shows the pool currently loaded — **load the module or the jobs
look like they vanished.**

Note the grid proxy is expired (`voms-proxy-info -timeleft` = 0) but this does not
matter: the job reads only EOS, and the schedd accepts submission via Kerberos.

## Reading the results

**`Mpart_per_s` is the only cross-regime-comparable number.** A jet and an event
are different units, so `us_per_unit` must never be compared across regimes. The
scripts emit both; the plot script uses Mpart/s for the comparison axis.

Expect the event regime to look *worse* per particle — one big event is a single
serial Triton program that starves the GPU, while thousands of small jets fill it.
That contrast is the point of the slide, not a defect.

## Caveat for any slide

`ITERS=3` on the FastJet side (the classic per-event loop over ~590 clusters is
slow). Fine for a ratio, thin for a quoted absolute.

## Submitted 2026-09-12 ~21:45

| cluster | what | flavour |
|---|---|---|
| **1116228** | smoke: 40 events, anti-kt only, R=1.0 | espresso |
| **1116229** | full sweep: 3 algs x 5 radii x 5 bins, 3000 events | nextweek |

Both **idle at submit** behind ~9,400 other idle jobs in the EosSubmit pool
(3,242 running, 8,161 held pool-wide). 17 of ~19 V100S slots were free, so the
V100S pin is not the bottleneck — this is ordinary queue contention. Per
[[lxplus-condor-eossubmit]], do **not** start relaxing `requirements` over this.

### Checking on them

```bash
ssh lxplus 'source /etc/profile.d/modules.sh; module load lxbatch/eossubmit; \
            condor_q 1116228 1116229'
```

Output lands in `bench_event/condor/`; results JSON in `bench_event/results/`.
Success markers: `SMOKE_OK` for the smoke job, `DONE_ALL` for the sweep.

### When results land

```bash
ssh lxplus 'cd /eos/home-c/cgupta/flashjet/bench_event && \
  EVSCRATCH=$PWD/results /eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python make_event_plots.py'
```

That writes `event_abs_timing.png` and `regime_throughput.png` and prints the
per-bin table. **Check the `njet %` column first** — if agreement is not ~100 %,
the timing means nothing and the plots should not go near the deck.

For the comparison plot, the jet-regime side is already verified to load:
anti-kt R=1.0, boosted top, (N, Mpart/s) = (24.1, 57.3), (44.8, 96.6),
(74.7, 76.5), (123.1, 50.2). Peak throughput at N≈45.

## Status at 2026-09-13 ~00:15 — still queued, nothing has run

Both clusters are **still idle in the queue** (`JobStatus=1`). Their condor logs
contain only a "Job submitted" line — no execute, no terminate event — and
`results/` is empty. The pool backlog was still ~11,300 idle at last check.

**A monitor false alarm is recorded here so it is not mistaken for a result.**
An earlier watcher reported "SMOKE left the queue ... BOTH JOBS FINISHED". That
was wrong: its check treated *empty `condor_q` output* as *job finished*, so one
transient ssh/module-load failure looked identical to completion. Re-querying
showed both jobs present and idle. The replacement monitor requires three
consecutive empty results **and** corroborating files on disk before believing a
job is gone.

Lesson, same shape as the `git rev-list` one: **a failed query is not a negative
result.** Check the positive evidence (log events, output files), not the absence
of a row.

## 2026-09-13 — the V100S pin was unsatisfiable; repinned to A100

The first two clusters (1116228/1116229) sat idle ~26 h and **could never have
run**. `condor_q -better-analyze` was explicit: *"No machines matched the job's
constraints"*, 0 slots willing.

**Root cause: the pool rewrites CPU/memory to a per-GPU floor, and that floor
exceeds every V100S slot.**

- Submitted 16 CPU / 32 GB → queued as **6 CPU / 18000 MB**.
- Resubmitted 4 CPU / 14 GB → queued as **5 CPU / 15000 MB** (a *floor*, not a cap).
- V100S slots are **4 CPU / 16000 MB** at best (14 of ~20; the rest 4/10000 or 0/6000).

5 > 4, so no request can fit a V100S while asking for a GPU. **The V100S pin is
unsatisfiable on the EosSubmit pool, whatever the request.** Repinned to
**NVIDIA A100-PCIE-40GB** (free slots with 8-12 CPUs and 93-106 GB), which flipped
the analyzer from "No machines matched" / 0-0 to *9 slots reject / 20 would match
if drained* — i.e. a real queue wait rather than an impossibility.

### This changes a deck claim

`bench_atlas/condor/atlas.sub` requests **H100 NVL or A100** — but
`results_v100/*.json` says the sweep ran on **Tesla V100S-PCIE-32GB**, and
`bench_atlas/condor/output/` is **empty**. So the jet-regime sweep in the deck was
**not** run through that submit file; it was run interactively on a V100S node.

Consequence: the deck's "V100-class" label is correct, but the event-regime
numbers will come from an **A100**. Do **not** put the two absolute numbers on one
axis without saying so. Options: (a) label both plots with their device, (b) rerun
the jet regime on A100 interactively for a like-for-like pair. **(b) is the honest
one if the two ever share an axis** — Mpart/s across different silicon is not a
regime comparison, it is a hardware comparison.

### Also hit: expired AFS token

`condor_submit` failed with *"store_cred of Kerberos credential failed"*, alongside
`/afs/.../.bashrc: Permission denied` on every ssh. Fix is `aklog` (not kinit, not
reconnect) — see [[lxplus-afs-token-aklog]]. Every remote command in this workflow
should run `aklog` first; the monitor does.

### Current clusters

| cluster | what | submitted |
|---|---|---|
| **1117576** | smoke, 40 events, A100 | 2026-09-13 |
| **1117577** | full sweep, A100 | 2026-09-13 |

Old 1116228/1116229/1117575 removed.

## 2026-09-14 — A100 pin was also starved; widened to A100-or-H100

The A100 repin fixed the *impossibility* but not the wait. After 30 min:
*0 slots match and are willing*, **26 would match if drained**, negotiator logging
`Reason for last match failure: no match found`.

**Cause this time is different from the V100S one — and benign.** Checking the
free A100 slots showed `GPUs = 0`: the unclaimed *partitionable* slots have CPU
and memory left but **no free GPU**, because every A100 GPU in the pool is handed
out to a running job.

```
A100-PCIE-40GB : 20 slots with a free GPU,  0 unclaimed
H100 NVL       : 34 slots with a free GPU,  2 unclaimed
H200           : 17 slots with a free GPU,  1 unclaimed
```

So `GPUs >= 1 && State == Unclaimed` is the availability query that matters —
**not** `State == Unclaimed` alone, which counts slots whose GPUs are all busy and
is what made 15-17 "free" slots look available when none were.

Widened `requirements` to **A100-PCIE-40GB OR H100 NVL**; candidate slots went
9 → 26. Still 0 willing at submit (all GPUs busy), but this is now an ordinary
wait for a GPU to free, not a dead end.

The sweep scripts record `torch.cuda.get_device_name(0)` into every result JSON,
so whichever card it lands on is self-documenting — check the `gpu` field before
quoting any number.

### Current clusters

| cluster | what |
|---|---|
| **1117580** | smoke, 40 events, A100-or-H100 |
| **1117581** | full sweep, A100-or-H100 |

Superseded: 1116228, 1116229, 1117575, 1117576, 1117577 (all removed).

## 2026-09-14 — IT RAN. Event regime is 34-66x, not 1.4x

Cluster **1117580** (smoke, A100) returned `SMOKE_OK` with 100 % agreement — first
real GPU execution. Cluster **1117581** (full sweep) then ran on an
**NVIDIA H100 NVL**; flashjet side 75/75 complete.

### The smoke test's throughput number was wrong by ~40x — do not reuse it

| | µs/event | Mpart/s |
|---|---|---|
| smoke, **40 events**, A100 | 398.7 | **1.43** |
| sweep, **3000 events**, H100 | 4.9 (lo bin) | **66.7** |

40 events is too small a batch to fill the GPU, so the smoke run measured launch
overhead, not throughput. **A smoke test validates correctness, never performance.**
Agreement was 100 % in both, so the smoke test did its actual job.

### Real event-regime results (anti-kt R=1.0, H100 NVL, 3000 events)

| bin | ⟨N⟩ | µs/event | Mpart/s |
|---|---|---|---|
| lo | 325.4 | 4.9 | **66.69** |
| mid | 499.4 | 14.3 | 35.05 |
| hi | 692.5 | 20.6 | 33.54 |
| vhi | 935.2 | 39.5 | 23.68 |
| all | 591.6 | 22.8 | 25.98 |

Speedup vs vectorised FastJet, from 21 completed pairs: **34-66x**, with
**100 % n_jets agreement** at 20/21 points (one kt/R=0.4/mid point at 99.91 %).

### This weakens the intended slide, and that matters

The planned story was "jet regime fills the GPU, event regime starves it." But the
event regime gets **34-66x**, against the jet regime's **39-99x** — much closer than
expected. And the two were measured on **different hardware**:

| measurement | device |
|---|---|
| deck's jet-regime plot | Tesla V100S-PCIE-32GB (interactive) |
| smoke | A100-PCIE-40GB |
| **full event sweep** | **H100 NVL** |

**The regime gap and the hardware gap are currently confounded.** A same-card rerun
of the jet regime (H100 NVL) is the only way to separate them, and it is cheap —
`bench_atlas/sweep_{flashjet,fastjet}.py` already exist. **Do not put event and jet
numbers on one axis until that is done.**

## 2026-09-14 — jet-regime rerun on H100 submitted (cluster 1117583)

To decouple the regime gap from the hardware gap, the jet-regime sweep is being
rerun on the **same card the event sweep used (H100 NVL)**.

- runner `bench_atlas/run_atlas_h100.sh`, submit `bench_atlas/jeth100.sub`
- writes to **`bench_atlas/results_h100/`** — the 464 V100S files in
  `results_v100/` are **not** touched
- pinned to **H100 NVL only** (a like-for-like rerun must be the same card)
- reuses the existing `sweep_flashjet.py` / `sweep_fastjet.py` unchanged, so the
  only difference from the deck's plot is the GPU

Matchability checked at submit (the lesson from the V100S fiasco):
**1 slot willing**, 5 would match if drained, 3 free H100 NVL — it should start
promptly rather than sit unmatchable.

### What this enables

Once both finish there are three comparisons, and only the first two are honest:

1. **event vs jet, both on H100** — the real regime comparison, on one axis.
2. **jet on V100S vs jet on H100** — the hardware delta, useful on its own.
3. ~~event on H100 vs jet on V100S~~ — confounded; **do not plot**.
