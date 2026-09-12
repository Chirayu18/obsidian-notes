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
