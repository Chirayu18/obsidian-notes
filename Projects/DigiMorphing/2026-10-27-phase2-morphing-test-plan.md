---
tags: [reference, todo]
status: active
date: 2026-10-27
source: lxplus
---

# Phase-2 digi morphing: what to test and what to ask

This note covers branch `Chirayu18/cmssw:phase2-digimorphing` (commits 15e2048e532 and 7dd02b835e3). Every measured
number below comes from the 100 PU200 TTbar events in D128 described in [[2026-09-30-phase2-alpaka-morphing-plan]].
The deck with these items is in `~/Documents/Codex/2026-10-27/continue-the-slides-from-here-https/outputs/phase2-morphing/`.
Its slides 20 to 22 summarise this note.

## Measured on 2026-10-27

**Compiled `FindClus` resources** (`cuobjdump -res-usage`, IB release vs branch):
- Phase-2 shared memory is the same in master and the branch: 35,728 B on sm_75, 80 and 89, and 36,752 B on sm_90,
  100 and 120. Master already reserves the Phase-1 bitmaps in the Phase-2 kernel, so sharing the buffers adds no
  shared memory.
- Phase-2 registers go up on every architecture, even with morphing off. By architecture (master → branch):

  | Arch | sm_75 (T4) | sm_80 | sm_89 | sm_90 | sm_100 | sm_120 |
  |---|---|---|---|---|---|---|
  | Registers | 128 → 143 | 119 → 127 | 105 → 127 | 79 → 93 | 85 → 107 | 89 → 109 |

- Phase 1 is identical in registers and shared memory on all 6 architectures.
- On the T4 at 384 threads, both 128 and 143 registers allow one block per SM. That is computed, not timed.

**Active strips per module** (the kernel's skip rule applied to the sim digis; script `/eos/user/c/cgupta/phase2morph/active_strips.py`):

| Region | Active strips (mean / total) | Module-events with every strip active |
|---|---|---|
| TBPX L1 | 4.99 / 5 | 99.3% |
| TBPX L2 | 9.61 / 10 | 70% |
| TBPX L3 | 9.59 / 10 | 68% |
| TBPX L4 | 8.68 / 10 | 28% |
| TFPX/TEPX | 9.69 / 10 | 77% |

At PU200 the skip is correct but barely saves anything in L1. The cost per L1 module is about 5 full strip passes.

**Caps:**
- The busiest IT module has 1,534 real digis (5,000 slots in morphing modules).
- The most fakes in one L1 module is 536 (1,000 slots). The fake mean is 78.5 per module.

## Why the current parameter values

**`DoDigiMorphing = False`**
- No existing workflow changes until the physics validation is done.
- Morphing off is bit-identical to master: 100 of 100 events, 56,142,094 digis.

**`MaxFakesInModule = 1000`**
- The fakes share the 6000-entry histogram, `maxPixInModule`. The block size is
  round_up(histogram entries / `maxIterClustering` = 16, 64). Enlarging the histogram for 1000 fakes (7000 entries)
  raises the block from 384 to 448 threads. At 143 registers the T4 allows 384, so the launch fails with
  `cudaErrorLaunchOutOfResources`. Phase 1 can enlarge its histogram (6000 + 2400, `maxIterClustering` = 24) and
  still get 384 threads.
- Every fake slot is therefore one fewer real slot.
- 1000 is 1.9 times the largest number of fakes seen (536). It leaves 5,000 real slots, 3.3 times above the busiest
  module seen (1,534).
- Phase 1 uses 2400 (= 2/5 of 6000) in an enlarged histogram.
- Revisit with high-occupancy and irradiated samples. Raise the cap only if fakes overflow it.

**`barrelRegions = "1,1-99,1-99"`**, which is all 216 TBPX L1 modules:
- L1 is where the 3D sensors take the highest fluence and the signal comes closest to the threshold: about 5 ke vs
  1 ke after 10^16 (Magherini).
- This is a first test region, **not an optimised choice**.
- Phase 1 chose L1 rings 1, 2, 7 and 8 plus L2 rings 1 and 8, to fix long clusters at high |η| (#48734).
- The Phase-2 choice should come from per-ring and per-|η| cluster-splitting rates with degraded thresholds.

**`endcapRegions = []`**: the Phase-1 syntax `disk,blade,side,panel` has not been checked against TFPX/TEPX detids.

**`stripCols = 44`, `halo = 2`, `maxRows = 1376`** are compile-time values derived from the design, not tuning
parameters:
- (S + 4) × ⌈1376/32⌉ ≤ 2080, the Phase-1 buffer size, gives S = 44.
- The halo must be 2 because eroding column c reads the dilation of c+1, which reads the image at c+2.

## To test

### Timing
- [ ] Measure `FindClus` kernel time for master vs morphing off vs morphing on: same events, same GPU, warmed up,
  repeated (nsys). Use a T4 and the Phase-2 HLT GPU type.
- [ ] Check whether morphing off is slower than master: registers went from 128 to 143 on the T4.
- [ ] Measure time vs number of active strips, real digis and fakes. L1 is about 5 of 5 strips active, so expect
  roughly 5 × (clear + load + dilate + erode, with 4 barriers each), plus a second histogram fill.
- [ ] Measure the cost of allocating the per-event fakes buffer (216 × 1000 slots, about 4.5 MB).
- [ ] Measure `HLT_75e33` throughput with morphing on L1.

### Edge cases and races (lesson from #49991)
The Phase-1 race came from reading and writing the same buffer within one pass. The 2-buffer scheme fixed it.
Phase 2 keeps that scheme but adds a new hazard: the buffers are cleared and refilled for every strip. A missing
barrier would let the next strip's clear overwrite words that are still being eroded.
- [ ] Run `compute-sanitizer --tool racecheck` and `--tool synccheck` on the unit test and on PU200 events.
  (memcheck was clean.)
- [ ] Run the same events N times and check that fakes and clusters are bit-identical.
- [ ] Compare SerialSync, CUDA and ROCm (warp of 64) on full events, not only on the unit test.
- [ ] Force overflow with `MaxFakesInModule = 20` to 50. The atomic slot order is not deterministic, so check
  whether the clusters change from run to run.
- [ ] Test boundaries with exact coordinate sets:
  - columns 43/44 and 87/88
  - rows 31/32 and 63/64
  - the partial last strip: 216 = 4 × 44 + 40, and 434 = 9 × 44 + 38
  - `nRows % 32 != 0` (only 100 rows is covered so far)
  - big-pixel seams
  - modules with 0 or 1 digi
- [ ] Inject more than 5,000 real digis into a morphing module: check the truncation and the printout, and
  measure the real-digi loss vs master.
- [ ] Phase-2 duplicate digis: Phase 1 removes them, the Phase-2 path does not. Count them, and decide how they
  should be handled.
- [ ] Run-3 regression: compare Phase-1 output with the shared kernel code against master, with Phase-1 morphing on
  and off. Resources are already shown to be identical.

### Physics, as in the Phase-1 validation (H. Petersen, DPG 13 Aug 2025)
- [ ] Muon gun at pT = 10 GeV, central (|η| < 2) and forward (2 < |η| < 3), morphing off vs on.
- [ ] RecHit vs SimHit in x and y: position, resolution, error and pull, per layer and ring.
- [ ] On-track RecHits; tracking efficiency and fake rate (CA, mkFit, LST).
- [ ] Crossing-cluster merges (display 3): how often they happen, and what they do to the CPE.
- [ ] Repeat with a degraded-threshold or irradiated digitizer setting. That is where morphing should help.
- [ ] Cluster-splitting rate per ring and per |η|, to choose the default regions.

## To ask
- **Bocci / Musich:** Which GPU will run the Phase-2 HLT? Is +15 registers on `FindClus` acceptable? Would they
  prefer an enlarged histogram plus a register-reduced kernel over the 5000/1000 split?
- **IT DPG (Magherini et al.):** Which rings or modules suffer most from cluster splitting? Is there a digitizer
  configuration for end-of-life thresholds?
- **Mersi / IT unpacker:** Can Phase-2 digis contain duplicates? Are they guaranteed to be in sensor coordinates?
- **Bartosik / Mersi:** Is the big-pixel x pitch 87.5 or 112 µm? It doesn't matter for morphing, but it does for the
  CPE.
- **Phase-1 morphing authors (Roguljic, Ferencek):** The CPU `SiPixelDigiMorphing` was built for Phase 1:
  160 × 416 modules in 8 chunks of 52 columns, one per ROC, each with 1 borrowed column per side (`iters = 1`). So
  in Phase 1 its chunk edges are the ROC boundaries inside the module, not module edges. Within a chunk it dilates
  and erodes, so eroding an edge column cannot see a pixel 2 columns across the boundary. On Phase-2 L1 (8 chunks of
  27 columns) this gives all 55,407 chunk-edge differences. Is missing those recoveries at ROC boundaries intended
  in Phase 1?
- **Reviewers:** Should the region syntax for TFPX/TEPX use Phase-2 ring and disk fields?

Related: [[phase1-morphing-validation-format]], [[plots]].
