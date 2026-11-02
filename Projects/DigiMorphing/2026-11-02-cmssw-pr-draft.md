---
tags: [reference, todo]
status: active
date: 2026-11-02
source: lxplus
---

# Draft PR to cms-sw/cmssw: Phase-2 pixel digi morphing in the Alpaka clusterizer

Branch: `Chirayu18/cmssw:phase2-digimorphing` (commits 15e2048e532, 7dd02b835e3, e4299b3e587, on a19318d617f).
Rebased test area: `/eos/user/c/cgupta/phase2morph/pr/CMSSW_20_1_X_2026-10-29-2300`, branch `phase2-digimorphing-pr`
(cherry-picks clean on cms-sw master 43790760906). Target branch: `master`. Validation in
[[2026-10-29-phase2-morphing-validation-round2]] and [[2026-10-27-phase2-morphing-test-plan]].

Title: **Phase-2 pixel digi morphing in the Alpaka clusterizer**

Text to paste (everything below the line):

---

#### PR description:

This PR adds the pixel digi morphing, already used at the HLT in Run 3 (#48734, #49991), to the Phase-2 Alpaka
pixel clusterizer `SiPixelPhase2DigiToCluster`. The morphing recovers pixels missing inside a cluster before the
clustering, by dilating the image of the pixels with a 3x3 kernel and eroding it with a plus-shaped kernel, so that
clusters broken by under-threshold pixels are not split. It is **off by default** (`DoDigiMorphing = False`), and with
it off the output is unchanged.

The Phase-1 implementation keeps two 1-bit bitmaps of a whole module in shared memory. Phase-2 modules are much
larger (672 x 216 pixels in TBPX L1, up to 1354 x 434 in a quad module with the big pixels), and the static shared
memory of `FindClus` must stay within 48 kB. The Phase-2 path therefore reuses the two Phase-1 buffers and processes
each module in strips of 44 columns, with 2 halo columns on each side: (44 + 4) x ceil(1376 / 32) = 2064 words, which
fits the existing 2080-word buffers. Strips with no pixel within one column are skipped. The buffers are now declared
outside the `if constexpr` branches, so that the Phase-2 kernel does not reserve a second pair; the shared memory of
`FindClus` is unchanged for all trackers.

Phase 2 runs one block per module, so the recovered pixels are stored per morphing module (found by a binary search
in the sorted list of morphing raw ids) instead of per block. They share the `maxPixInModule` histogram with the valid
pixels: in a morphing module `MaxFakesInModule` (default 1000) of the 6000 entries are reserved for them, and at most
5000 valid pixels are kept. Enlarging the histogram instead would raise the block size from 384 to 448 threads, which
does not launch on a Tesla T4 at the 143 registers per thread of `FindClus`.

New configuration parameters of `SiPixelPhase2DigiToCluster`: `DoDigiMorphing` (default `False`),
`MaxFakesInModule` (default 1000), `barrelRegions` (default `["1,1-99,1-99"]`, all of TBPX L1) and `endcapRegions`
(default empty), with the same syntax as the Phase-1 producer. The region parsing and selection move from
`SiPixelRawToCluster` to a shared header, `SiPixelMorphingRegions.h`, without changes. The size of each morphing module
is taken from the geometry and passed to the kernel, which checks it against the supported range at `beginRun`.

A new unit test, `testPhase2DigiMorphing`, compares the clusters found by `FindClus` with a whole-module host reference
on random broken tracks, on exact pixel patterns across the strip, word and module boundaries (including 216 and
434 columns and 1354 rows), on single-pixel modules, on overflow of `MaxFakesInModule`, and on the truncation of the
valid pixels.

#### PR validation:

All on 100 to 200 TTbar PU200 events in D128 (`RelValTTbar_14TeV`, CMSSW_20_1_0_pre3), on a Tesla T4 and on the
SerialSync backend.

With morphing off, the output of the branch is bit-identical to master (100/100 events, 56,142,094 digis).

With morphing on in TBPX L1, the GPU result matches a whole-module CPU reference implementation of the same
algorithm exactly (100 events, 1,696,444 recovered pixels, 0 differences). It is bit-identical between repeated runs, between 1 and 4 threads, and between CUDA and
SerialSync (200/200 events, 3,364,152 recovered pixels, about 78 per L1 module). The largest number of recovered
pixels in one module is 536 (limit 1000), and the busiest morphing module has 1,534 valid pixels (limit 5000).

The unit test passes on SerialSync and CUDA, and is clean under `compute-sanitizer` memcheck, synccheck and initcheck.
racecheck reports a hazard between the assert in `OneToManyAssocRandomAccess::finalize` and `warpPrefixScan`, which is
also present in master, and, in the overflow test only, a write-after-read on the clamp of the recovered pixel count,
whose read side is attributed to threads that do not execute that branch.

Run 3: the Phase-1 Alpaka clusterizer on 1000 events of `/ZeroBias/Run2026D-v1/RAW` gives identical clusters in master
and in the branch, with morphing both off and on.

Registers of `FindClus` for Phase 2 increase (sm_75 128 to 143, sm_80 119 to 127, sm_89 105 to 127, sm_90 79 to 93,
sm_100 85 to 107, sm_120 89 to 109), while the shared memory is unchanged; Phase 1 is unchanged in both. The
producer time per event (T4, FastTimerService) is the same within 0.4 ms for master, morphing off and morphing on.

`runTheMatrix.py -l 38434.402` runs on a T4, and its step 3 also runs with the morphing switched on in L1.

The physics validation (RecHit residuals with respect to the SimHits, tracking efficiency, end-of-life thresholds)
and the choice of the default regions for Phase 2 will follow; this PR does not change any workflow.

#### If this PR is a backport please specify the original PR and why you need to backport that PR. If this PR will be backported please specify to which release cycle the backport is meant for:

Not a backport, and no backport is foreseen.
