---
tags: [reference]
status: superseded
superseded_by: "[[2026-09-12-event-regime-sweep-run]]"
date: 2026-09-12
source: lxplus
---

# TODO — event-regime timing sweep (for ML4Jets backup slide)

**Ask (Chirayu, 2026-09-12): launch an event-regime job later today.**

## Why

The ML4Jets deck times **jet-based** clustering only (one timed unit = one large-$R$
jet, 24–123 constituents; `us_per_jet = dt / B` in both `sweep_flashjet.py` and
`sweep_fastjet.py`, so the 39–99x speedup ratio is denominator-independent).

The **event regime** appears in the deck only for *correctness* (the ~600-cluster
ATLAS RecoJets_R4 match). There is no event-regime **timing** in the deck, and the
audience question "and for a full event?" is currently unanswered.

Alex's 19 Jun 2026 A100 report has event numbers (Table 3: 8 us -> 11 ms/event as
N goes 512 -> 16384; throughput 47 -> 1.1 Mpart/s) but that is a *synthetic* N-sweep,
not the ATLAS Open Data events, and has no FastJet baseline.

## What does NOT already exist

`bench_atlas/event_matrix.py` is **CPU-only and correctness-only** — no timing loop,
no GPU, no FastJet timing. It cannot be reused as-is. The event-regime timing sweep
must be **written**, as the event analogue of `sweep_flashjet.py` + `sweep_fastjet.py`.

## What to build

- `sweep_event_flashjet.py` / `sweep_event_fastjet.py`, mirroring the jet-regime pair:
  warmup, `torch.cuda.synchronize()`, ITERS-averaged, **both sides reading the same
  saved ragged file**, and an agreement check (timing without agreement is meaningless).
- Input: `data/opendata/opendata_constit_atlasevent_ak4.npz`
  (built by `dump_atlas_jetreco.py`; one row = one whole event, ~590 clusters,
  mean 10.96 jets/event). Regenerate with more events if 5000 is too few.
- Report **both** `us_per_event` and `Mpart_per_s` — per-unit cost is not comparable
  across regimes (a jet and an event are different units), but **Mpart/s is**.
  That cross-regime comparability is the whole point of the slide.

## The slide this feeds

Pairs the two regimes into one story: thousands of small jets launch thousands of
independent Triton programs and fill the GPU; one big event is a single serial
program that starves it. That is the same effect the H100 ncu backup already shows
at N=2048 (**0.32 waves/SM, 128 blocks on a 132-SM device**) — two scales of one story.
It also justifies *why* the tagging regime is the one the library targets.

## Submission

Model on `bench_atlas/condor/atlas.sub`:
`request_GPUs=1`, `request_CPUs=16`, `request_memory=32GB`, `getenv=True`,
requires `NVIDIA H100 NVL || NVIDIA A100-PCIE-40GB`, AlmaLinux9.
Pythons: `$BH` = b_hive env (flashjet), `$FJ` = fjbench env (fastjet) — see
`run_atlas_sweep.sh`. Needs a **tmux** session for submission (grid proxy is
node-local; see the lxplus-proxy-and-tmux memory).

## Caveats to carry onto any slide

- Quote the GPU actually used. Deck main slides say "V100-class" by disclosure
  policy; if this runs on H100/A100 the number is **not** comparable to the
  V100 jet-regime plot. Either rerun the jet regime on the same device or label
  both clearly.
- Event regime is `O(N^2)` per event and single-program — expect it to look *bad*
  per-particle next to the jet regime. That is the point of the slide, not a defect.
