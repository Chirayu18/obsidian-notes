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
| B3 | **4-process CMS Open Data sweep**, R=0.4 and 0.8 | H100 **MIG 1g.12gb** (~1/7 card) | **8–13×** vs vectorised FastJet, ~100 % agreement (see table below) |
| B4 | GPU backend sweep (synthetic), B=1024 | T4 | triton-large up to 176× over torch backend |
| B5 | Throughput/latency sweep | A100 | 130–145 Mpart/s, 0.08–0.76 µs/jet (jet regime); event regime falls 47→1.1 Mpart/s with $O(N^2)$ |
| B6 | nsys kernel breakdown | A100, H100 MIG | `_cluster_large_kernel` **96–99.6 %** of GPU time; decode 0.3–1.5 %; no steady-state H↔D traffic |
| B7 | ncu microarchitecture | **T4 only** | L1/occupancy-bound, not DRAM-bound; 168 reg/thread caps occupancy at 37.5 % |

### B3 detail — CMS Open Data (UL16 MINIAOD), anti-$k_t$ R=0.4

| dataset | jets | ⟨n⟩ const | flashjet µs/jet | FastJet awkward | FastJet classic | speedup | agreement |
|---|---|---|---|---|---|---|---|
| DY+jets | 30 000 | 10.8 | 0.603 | 6.50 | 36.87 | 11× | 100 % |
| W+jets | 30 000 | 15.1 | 1.068 | 8.82 | 47.95 | 8× | 100 % |
| $t\bar t$ (hadronic) | 30 000 | 22.2 | 1.331 | 15.14 | 71.06 | 11× | 99.997 % |
| QCD (470–600) | 28 250 | 34.0 | 1.929 | 24.65 | 108.26 | 13× | 100 % |

R=0.8 gives the same picture (9–13×). **These are on ~1/7 of an H100** — a floor,
not the headline. Full-A100/H100 runs are queued.

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

### C4. ncu on modern hardware
Only ever collected on a T4. Alex's report says the T4 profile "does not transfer to
the A100". Blockers now understood: DCGM is absent on lxplus GPU nodes (good), but
**ncu cannot lock clocks on a MIG slice** — needs a full card (`--clock-control none`
as fallback). So the standing optimisation advice (reduce register pressure) is
unverified on A100/H100.

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
