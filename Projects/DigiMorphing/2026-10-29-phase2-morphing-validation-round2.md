---
tags: [reference]
status: active
date: 2026-10-29
source: lxplus
---

# Phase-2 digi morphing: validation round 2 (sanitizers, reproducibility, timing, Run-3 regression)

This note continues [[2026-10-27-phase2-morphing-test-plan]] for branch `Chirayu18/cmssw:phase2-digimorphing`. The
work area is `/eos/user/c/cgupta/phase2morph/CMSSW_20_1_X_2026-10-20-2300` and the outputs are in
`/eos/user/c/cgupta/phase2morph/val2/` (scripts `gpu_runs.sh`, `gpu_runs2.sh`, `compare_runs.py`, `duplicates.py`,
`run3_cfg.py`, plus the logs). All GPU runs used lxplus905 (Tesla T4). The PU200 input is a skim of 200 TTbar D128
events that keeps only the pixel digis (`val2/pixdigis_pu200_numEvent200.root`).

## Bug found and fixed: race after the strip loop

`compute-sanitizer --tool synccheck` on the extended unit test reported divergent barriers at the barrier after the
per-strip clear (`PixelClustering.h:568`). `racecheck` reported the cause, a write to `hist.off` while other threads
read it (line 679 against line 556). A thread that skips the last strip leaves the strip loop without passing a
barrier, then clears `hist.off` for the second histogram fill. Threads in slower warps are still evaluating the
skip condition for that last strip from the same `hist.off`, so they can read half-cleared values, take a
different decision and enter the strip barriers alone. It only happens when the last strip of a module is skipped.
At PU200 that is rare in L1 (99.3% of L1 module-events have every strip active), which is why the earlier PU200
validation did not see it. The single-pixel module of the new boundary test triggers it every time.

The fix is one `alpaka::syncBlockThreads(acc)` after the strip loop, before the clamp and the histogram clear. The
registers are unchanged on every architecture (sm_75 143, sm_80 127, sm_89 127, sm_90 93, sm_100 107, sm_120 109).
The fix is in the lxplus working tree, uncommitted, and is not pushed. On the 200 PU200 events the output with the
fix is bit-identical to the output without it, so the race was not hit there.

## Unit test extended

`testPhase2DigiMorphing.dev.cc` now has four sections, all compared with the whole-module host reference.

| Section | What it checks | Result (T4 and serial) |
|---|---|---|
| random broken tracks | the original 6 modules | passes |
| strip, word and module boundaries | single missing pixels at columns 1, 43, 44, 45, 87, 88, 131, 132, 175, 176, 214 of a 672 x 216 module, a 2-pixel gap across 43/44, rings around 43, 44, 87, 88, 175, 176, 214, row gaps at 1, 31, 32, 63, 64, 670, tracks along the first and last column; a 1354 x 434 module (rows % 32 = 10, last strip 38 wide) with gaps at rows 1343, 1344, 1351, 1352 and columns 395, 396, 397, 431, 432; a 1-pixel module, a 2-pixel corner module, and a morphing raw id without digis | passes; morphing changes 47 → 31 and 19 → 12 clusters, so the check is not vacuous |
| more recovered pixels than `MaxFakesInModule` (5) | the clusters lie between the unmorphed and the fully morphed ones, in two runs | passes |
| more valid pixels than kept (5500 in a morphing module) | the first 5000 are clustered as the reference, the other 500 get the invalid module and cluster ids | passes |

Sanitizers on the unit test after the fix: memcheck, synccheck and initcheck report 0 errors. racecheck reports one
remaining write-after-read on `fakePixels`, only in the overflow section. The write is the clamp
`fakePixels = maxFakesInModule` inside `once_per_block` (line 680), and the reads are attributed to line 679 from
threads 31 and 383. Those threads do not execute that branch, so the read looks like a load the compiler hoisted out
of the branch, whose value is discarded. The Phase-1 code uses the same clamp. It does not change any result, but a
clean racecheck would need the clamp done without a shared write, for example each thread taking
`min(fakePixels, maxFakesInModule)` after the barrier.

## cmsRun sanitizers (3 PU200 events)

synccheck reports 0 errors with morphing on. racecheck reports hazards between the assert at `OneToManyAssoc.h:229`
(reading `off` in `finalize`) and the write in `warpPrefixScan` (`prefixScan.h:37`). The same hazard appears in master
(3 reports) and in the branch with morphing off (3); with morphing on there are 6, because the morphing modules
finalize the histogram twice. It is a pre-existing hazard in the `HistoContainer` finalize, not in the morphing code.

## Reproducibility (200 PU200 events, morphing on in all of TBPX L1)

| Comparison | Identical cluster ids | Identical recovered pixels |
|---|---|---|
| GPU run 1 vs runs 2 and 3, 1 thread | 200/200 | 200/200 |
| GPU 1 thread vs GPU 4 threads/streams | 200/200 | 200/200 |
| GPU vs SerialSync on full events | 200/200 | 200/200 |
| without vs with the barrier fix | 200/200 | 200/200 |
| `MaxFakesInModule = 30`, three GPU runs pairwise | 3 to 9 of 200 | 0/200 |

There are 3,364,152 recovered pixels in total, 16,821 per event. With the cap at 30, every run keeps the same number
of recovered pixels (1,291,696), but which ones fill the slots depends on the atomic order. That changes the
clusters of about 10,400 digis in about 755 of the 43,200 L1 module-events from run to run. With the default cap of
1000, no overflow was printed in any of the 200 events.

The digi SoA dump has one element more than the digis, and it is never written: its content differs between runs.
`compare_runs.py` drops it. It is not a morphing issue.

## Duplicate digis

There are 0 duplicate (detId, row, column) digis in 20 PU200 events (11.2 M IT digis). The simulation does not
produce them, so the open question for real data from the unpacker remains.

## Run-3 regression (Phase-1 path shares the kernel)

The Phase-1 Alpaka clusterizer ran on 1000 events of `/ZeroBias/Run2026D-v1/RAW` (run 403433), Run3_2026 era,
`auto:run3_data_prompt`, with the default Phase-1 morphing regions. Master and branch give identical cluster ids in
1000/1000 events with morphing off and 1000/1000 with morphing on. Morphing on vs off differs in 121 module-events
(359 digis), so the comparison could have caught a change.

## Timing

nsys on lxplus905 is a stub ("Nsight Systems 2026.1.3 hasn't been installed with CUDA Toolkit 13.3"), and the
NsightSystems on `/cvmfs/sft.cern.ch` is the 2021 version, too old for CUDA 13. Instead I timed the producer with the
FastTimerService, 1 thread, `CUDA_LAUNCH_BLOCKING=1` so that the module time includes its kernels and copies, over
200 events, 3 repetitions each.

| Configuration | `gpuClusters` real time per event (ms) | Mean |
|---|---|---|
| master | 9.58, 9.97, 9.86 | 9.80 |
| branch, morphing off | 10.03, 9.86, 9.94 | 9.95 |
| branch, morphing on (L1) | 10.04, 10.01, 9.94 | 10.00 |

The differences are within the spread between repetitions, about 0.4 ms. At this resolution morphing on L1 costs
less than about 0.3 ms per event at the module level, and the 15 extra registers do not show either. The module time
is dominated by the host-to-device copy of about 550 k digis per event. A kernel-level number for `FindClus` still
needs a working nsys or ncu.

## Still open

The kernel-level FindClus timing, HLT_75e33 throughput, the physics validation (muon gun RecHit vs SimHit, on-track
hits, tracking efficiency and fake rate, degraded thresholds), and the choice of regions all remain open. So do the
ROCm run on a real AMD GPU, the clamp rewrite to get racecheck fully clean, and the open questions to the experts
listed in the test plan.
