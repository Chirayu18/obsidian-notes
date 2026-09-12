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
