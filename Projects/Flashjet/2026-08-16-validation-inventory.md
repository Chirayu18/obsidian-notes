---
tags: [reference]
status: active
date: 2026-08-16
source: lxplus
---

# flashjet — what is tested, what is missing (for Alex & Sitian)

Written to answer Alex's request: *"list all the items (benchmarks, cross checks,
evaluation) already tested and which ones you think are missing"*, so he and Sitian
can advise on the relevant tests and we can wrap up conference material.

Related: [[2026-07-31-ml4jets-abstract]], [[2026-07-13-cms-validation]],
[[2026-07-17-msd-outlier-anatomy]], [[Status]].

---

## A. DONE — correctness

| # | check | reference compared against | result |
|---|---|---|---|
| A1 | Unit tests, full suite | independent NumPy tree-walks | **129 passed** on GPU (was 85 passed + 13 CUDA-skipped; the 13 CUDA tests ran for the first time on 2026-08-15) |
| A2 | Clustering vs FastJet, jet-by-jet kinematics | scikit-hep `fastjet` 3.5.1.3 | exact (`test_reference_vs_fastjet`, `test_kinematics_vs_fastjet`) |
| A3 | Reclustered $p_T$ vs CMS stored `FatJet_pt` | CMS NanoAOD (FastJet-produced) | ratio **1.000000**, σ=2.5e-4 |
| A4 | Soft-drop mass vs CMS `msoftdrop` | CMS NanoAOD | median Δ = **−0.004 GeV** |
| A5 | $R_g$ jet-by-jet | CMS stored subjets | Δ ≤ 2e-4, 99.2 % below 0.01 |
| A6 | $z_g$ | CMS | \|Δ\| = 6.9e-5 |
| A7 | Residual $m_{SD}$ tail anatomy (4.4 % of jets) | — | attributed ~50 % soft-candidate table floor, ~23 % storage rounding, ~20 % rounding-sensitive C/A trees, ~7 % $z\approx z_{cut}$ prong flips |
| A8 | $n_{jets}$ agreement on identical events | FastJet | **100.00 %** (16384/16384 HLT ttbar; 7 of 8 Open Data runs 100 %, one 99.997 %) |
| A9 | Substructure decoders vs independent walk | NumPy | F1/F2/F3 pinned; d-channel ties exactly to `splitting_scales` |
| A10 | Physics closure on toys | analytic LL predictions | $z_g$ on the $1/z$ curve, anti-kt jet areas, Lund triangle flat interior, β-ordering |

## B. DONE — performance

| # | benchmark | hardware | result |
|---|---|---|---|
| B1 | flashjet vs FastJet, real ttbar (HLT ntuple, 16 384 jets) | Tesla T4 | ~11× vs vectorised FastJet, 100 % agreement |
| B2 | Same, re-measured 2026-08-15 | **full A100-PCIE-40GB** | **0.24 µs/jet vs 7.23 (awkward) → ~30×**; classic 39.6 µs/jet |
| B3 | **4-process CMS Open Data sweep**, R=0.4 and 0.8 | **H100 NVL** (full card) | **65–97×** vs vectorised FastJet, ~100 % agreement |
| B3b | same sweep | **A100-PCIE-40GB** (full card) | **25–41×** |
| B3c | same sweep | H100 **MIG 1g.12gb** (~1/7 card) | **8–13×** — useful as a shared-GPU / partitioned-deployment point |
| B4 | GPU backend sweep (synthetic), B=1024 | T4 | triton-large up to 176× over torch backend |
| B5 | Throughput/latency sweep | A100 | 130–145 Mpart/s, 0.08–0.76 µs/jet (jet regime); event regime falls 47→1.1 Mpart/s with $O(N^2)$ |
| B6 | nsys kernel breakdown | A100, H100 MIG | `_cluster_large_kernel` **96–99.6 %** of GPU time; decode 0.3–1.5 %; no steady-state H↔D traffic |
| B7 | ncu microarchitecture | T4 (2026-06) | L1/occupancy-bound, not DRAM-bound; 168 reg/thread caps occupancy at 37.5 % |
| B7b | **ncu on H100 NVL** (NEW, 2026-08-16) | H100 NVL, B=128 N=512 | **collected successfully** — see below. This is the measurement Alex's report could not obtain |

### B3 detail — CMS Open Data (UL16 MINIAOD), anti-$k_t$ R=0.4

µs per jet; speedup quoted against the **vectorised (awkward)** FastJet interface,
which is the fair Python baseline.

| dataset | jets | ⟨n⟩ const | **flashjet H100 NVL** | **flashjet A100** | FastJet awkward | FastJet classic | speedup (H100) | agreement |
|---|---|---|---|---|---|---|---|---|
| DY+jets | 30 000 | 10.8 | **0.081** | 0.223 | 6.20 | 32.43 | **77×** | 100 % |
| W+jets | 30 000 | 15.1 | **0.137** | 0.373 | 9.67 | 44.84 | **71×** | 100 % |
| $t\bar t$ (hadronic) | 30 000 | 22.2 | **0.170** | 0.373 | 13.46 | 59.95 | **79×** | 99.997 % |
| QCD (470–600) | 28 250 | 34.0 | **0.249** | 0.549 | 24.24 | 91.64 | **97×** | 100 % |

R=0.8 gives the same picture (H100 65–96×, A100 25–41×), so the result is not an
R artifact. Speedup **grows with multiplicity** — flashjet's per-jet cost rises far
more slowly than FastJet's, which is the physics-independent statement worth showing.

A full H100 NVL is ~**8× faster than one of its own MIG 1g.12gb slices**
(0.081 vs 0.603 µs/jet on DY), consistent with the slice being ~1/7 of the card.

Plots: `bench_speed_R{0.4,0.8}_{A100_PCIE_40GB,H100_NVL}.png` and
`bench_scaling_*` in `/eos/home-c/cgupta/flashjet/bench_opendata/`.

### B6/B7b detail — profiling on modern hardware (NEW)

**nsys** (`_cluster_large_kernel` share of GPU time): A100 **97.6 %**, H100 MIG
**97.8 %**, decode 1.5 % in both. The kernel-bound picture from the T4 era holds
on current hardware — any further speedup must come from that one kernel.

**ncu on H100 NVL**, `_cluster_large_kernel`, B=128 N=512:

| metric | H100 NVL | T4 (2026-06) |
|---|---|---|
| Duration | 1.53 ms | 11.31 ms |
| DRAM throughput | **0.02 %** | 0.36 % |
| Memory throughput | 17.25 % | — |
| Compute (SM) throughput | **15.42 %** | 39.4 % |
| Registers / thread | **168** | 168 |
| Theoretical occupancy | **18.75 %** | 37.5 % |
| Achieved occupancy | **6.25 %** | 33.2 % |
| Waves per SM | **0.32** | 1.07 |

**Reading:** the T4 conclusion *does not* carry over unchanged, and the situation on
H100 is worse in the way that matters. Register pressure is unchanged (168/thread)
but on H100 that caps theoretical occupancy at **18.75 %**, and achieved occupancy
is only **6.25 %**. With **0.32 waves/SM** the kernel does not even fill the GPU
once — at this shape H100 is largely idle. DRAM is essentially untouched (0.02 %),
so this is *not* a bandwidth problem: it is occupancy/parallelism starvation.

Actionable consequences:
1. **Register pressure is now the top optimisation lever** (it was already suspected
   on T4; on H100 it costs proportionally more). This is direct evidence for the
   `tune_large.py` crossover re-measurement the 2026-07-01 audit asked for.
2. Grid size 128 with block size 128 is far too small for an H100 — the **auto-dispatch
   thresholds are tuned for older, smaller GPUs** and should be re-derived per device.
3. Caveat: measured with `--clock-control none` (clocks not locked, see below), so
   absolute values are indicative; the occupancy/register figures are structural and
   not clock-dependent.

**Tooling notes (resolves a long-standing blocker).** Alex's June report could not
collect ncu because DCGM held the performance counters. On lxplus GPU workers
**DCGM is absent** (`nv-hostengine`/`dcgm-exporter` not running, `RmProfilingAdminOnly=0`),
so that blocker does not apply. A *different* one does: **ncu cannot lock clocks on a
MIG slice** (`Cannot lock GPU clock frequencies on MIG!`), so profiling must target a
full card, optionally with `--clock-control none`.

---

## C. MISSING — my ranking of what matters

### C1. C++ FastJet baseline — **the biggest gap**
Every timing number so far compares against the **Python** `fastjet` binding. CMSSW
uses **FastJet 3.4.1 C++**. The honest baseline is the vectorised (awkward) interface,
but a reviewer will still ask "is this just Python overhead?" Until we answer with C++,
every speedup is quotable only with a caveat. *This is the single most valuable next test.*

### C2. CMSSW integration + realistic in-job timing
Timing outside the framework ignores the real cost structure (product handling,
H↔D transfer per event, one event at a time vs a large batch). The batch advantage
is exactly what a per-event framework may not be able to exploit — this needs to be
measured, not assumed. Setup started: IB `CMSSW_20_1_X_2026-08-16-0000` (see [[2026-08-16-cmssw-integration-plan]]).

### C3. Full-GPU numbers on A100 + H100 NVL for the Open Data sweep
Queued. Needed so the headline is not a MIG slice.

### C4. ~~ncu on modern hardware~~ — **DONE 2026-08-16** (see B7b)
Collected on H100 NVL. Result is actionable and *changes* the T4 conclusion:
occupancy 6.25 % achieved / 18.75 % theoretical, 0.32 waves/SM, DRAM 0.02 % — the
kernel starves the GPU rather than saturating memory. Register pressure (168/thread)
is confirmed as the top lever, and the auto-dispatch thresholds look mistuned for
H100-class devices. **Still missing:** the same ncu pass on A100, and a large-N shape
where scratch may spill past cache and DRAM could start to matter.

### C5. Event-regime (large-N) validation and profiling
Almost everything is the jet regime (small N, large batch). The event regime is
$O(N^2)$ and 10–100× lower throughput; its scaling has not been re-checked recently,
and the ncu caveat "re-check at much larger N where scratch spills past cache and
DRAM may dominate" was never followed up.

### C6. Physics coverage gaps
- Only **anti-$k_t$** is benchmarked. $k_t$ and C/A are implemented and unit-tested but never timed.
- Only R=0.4/0.8. No R-scan.
- No **pileup-dependence** study (throughput and agreement vs $N_{PU}$ / $\rho$).
- Grooming/Lund are validated against CMS but never *timed* as part of the pipeline.

### C7. Numerical robustness
- float32 GPU vs float64 reference — pinned by match-fraction/determinism tests, but no systematic study of where float32 starts to matter (very soft constituents, near-degenerate $d_{ij}$).
- Determinism is documented as fragile at $B\ge256$ in the kernel hot loop. Not re-tested recently.

### C8. Multi-GPU / concurrency
Nothing measured: multiple jobs sharing a GPU (relevant given MIG), or streams/overlap.

---

## D. Suggested questions for Alex & Sitian

1. Is a **C++ FastJet** baseline the right next step, or is the awkward-vectorised comparison acceptable for the conference?
2. For CMSSW: is a **minimal EDProducer** the right first target (C2), or do you want the CUDA/Alpaka path from the start?
3. Which physics axis matters most for the talk — **pileup dependence**, an **R-scan**, or **$k_t$/C-A timing**?
4. Do we want the **event regime** (full-event clustering) in the talk at all, or keep it to the jet/tagging regime where flashjet is strongest?
5. Is the MIG result (8–13× on 1/7 of an H100) worth showing as a shared-GPU deployment point, or a distraction?

---

## E. Conference submission status

Abstract drafted for **ML4Jets 2026** (14–18 Sep, Vienna): [[2026-07-31-ml4jets-abstract]].
Framed library-level (GPU-native clustering as a FastJet substitute in ML pipelines),
deliberately free of experiment/hardware specifics. Two versions (~210 w and ~120 w)
plus a provenance table for every number.

**Open decision:** the abstract currently says "the standard CPU implementation"
rather than naming FastJet. Naming it sharpens the claim; a two-word edit either way.

**Numbers in the abstract still trace to the June A100 report**, which predates the
substructure features landing (`2e912ef`). The re-measurement now in progress (B2/B3)
supersedes them and should be folded in before submission.
