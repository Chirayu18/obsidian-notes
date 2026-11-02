---
tags: [reference, todo]
status: active
date: 2026-11-02
source: lxplus
---

# Draft PR to cms-sw/cmssw: Phase-2 pixel digi morphing in the Alpaka clusterizer

PR branch: **`Chirayu18/cmssw:phase2-digimorphing-squashed`**, one commit 3ad40f2527f on cms-sw master 43790760906
(the base of CMSSW_20_1_X_2026-10-29-2300). It has the same tree as the 4-commit history `phase2-digimorphing-pr`
(147cd3c1710, e29ba092d3c, f87ef412a97, 6228b2026f5) in `/eos/user/c/cgupta/phase2morph/pr/CMSSW_20_1_X_2026-10-29-2300/src`,
where it was built and validated; `scram b code-checks` and `code-format` give no changes. The old fork branch
`phase2-digimorphing` (3 commits on a19318d617f) is left as it was. Codex review:
`~/Documents/phase2-morphing-pr-review-codex.md` (no production bug; its cleanups are included).
Target branch: `master`. Open from https://github.com/Chirayu18/cmssw/pull/new/phase2-digimorphing-squashed and paste
the text below.

Title: **Phase-2 pixel digi morphing in the Alpaka clusterizer**

Text to paste (everything below the line). Condensed by Codex on 2026-11-02 from the longer version further down, with the slides announced and the timing deferred; paragraphs are on single lines because GitHub renders single newlines as line breaks. Attach the slides PDF to the PR.

---

#### PR description:

This PR adds Run 3 HLT pixel digi morphing (#48734, #49991) to the Phase-2 Alpaka clusterizer `SiPixelPhase2DigiToCluster`. A 3x3 dilation followed by plus-shaped erosion recovers missing pixels before clustering to avoid splitting clusters at under-threshold pixels. It is **off by default**, with bit-identical output when off.

Phase-2 modules are processed in 44-column strips with 2 halo columns on each side, reusing the Phase-1 shared buffers to keep `FindClus` within 48 kB. Shared-memory usage is unchanged. Recovered pixels are stored per morphing module. `MaxFakesInModule` reserves 1000 of the 6000 histogram entries by default, leaving room for 5000 valid pixels. Enlarging the histogram would increase the block size from 384 to 448 threads, preventing launch on a Tesla T4 at 143 registers per thread.

New parameters, with the Phase-1 region syntax: `DoDigiMorphing = False`, `MaxFakesInModule = 1000`, `barrelRegions = ["1,1-99,1-99"]` (all of TBPX L1) and `endcapRegions = []`.

The Phase-1 region parsing and selection move unchanged into `SiPixelMorphingRegions.h`; this refactor is behaviour-neutral. The new `testPhase2DigiMorphing` compares clusters and recovered pixels against a whole-module host reference, covering random broken tracks, strip/word/module boundaries, single-pixel modules, overflow, valid-pixel truncation and storage in the correct module.

Slides with implementation details and validation plots are attached. Physics validation and the choice of default Phase-2 regions will follow; this PR does not change any workflow.

#### PR validation:

Phase-2 validation uses 100 to 200 TTbar PU200 events in D128 (`RelValTTbar_14TeV`, CMSSW_20_1_0_pre3), on a Tesla T4 and SerialSync.

**Morphing off:** bit-identical to master for 100/100 events and 56,142,094 digis.

**Morphing on in TBPX L1:** exact agreement with the whole-module CPU reference over 100 events, with 1,696,444 recovered pixels and 0 differences. Repeated runs, 1 and 4 threads, and CUDA and SerialSync are bit-identical over 200/200 events, with 3,364,152 recovered pixels. Maximum module occupancy is 536 recovered pixels (limit 1000) and 1,534 valid pixels (limit 5000).

**Phase 1:** identical clusters to master with morphing off and on over 1000 `/ZeroBias/Run2026D-v1/RAW` events.

Code checks and formatting pass. The unit test passes on SerialSync and CUDA; memcheck, synccheck and initcheck are clean. Racecheck reports a hazard also present in master and an overflow-test clamp hazard matching the Phase-1 pattern.

`runTheMatrix.py -l 38434.402 --nEvents 10` passes all steps on T4 in CMSSW_20_1_X_2026-10-29-2300; step 3 also runs with morphing enabled in TBPX L1.

Phase-2 `FindClus` register use increases (T4: 128 to 143); Phase-1 register and shared-memory usage are unchanged. Dedicated kernel-level timing and HLT throughput measurements will be done soon and reported in this PR.

#### If this PR is a backport please specify the original PR and why you need to backport that PR. If this PR will be backported please specify to which release cycle the backport is meant for:

Not a backport, and no backport is foreseen.

---

## Longer version (superseded, kept for reference)

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
valid pixels. It also checks that each module recovers the same pixels as the reference, each stored once in the
slots of its own module.

#### PR validation:

All on 100 to 200 TTbar PU200 events in D128 (`RelValTTbar_14TeV`, CMSSW_20_1_0_pre3), on a Tesla T4 and on the
SerialSync backend.

With morphing off, the output of the branch is bit-identical to master (100/100 events, 56,142,094 digis).

With morphing on in TBPX L1, the GPU result matches a whole-module CPU reference implementation of the same
algorithm exactly (100 events, 1,696,444 recovered pixels, 0 differences). It is bit-identical between repeated runs, between 1 and 4 threads, and between CUDA and
SerialSync (200/200 events, 3,364,152 recovered pixels, about 78 per L1 module). The largest number of recovered
pixels in one module is 536 (limit 1000), and the busiest morphing module has 1,534 valid pixels (limit 5000).

`scram b code-checks` and `code-format` give no changes. The unit test passes on SerialSync and CUDA (T4), and is clean
under `compute-sanitizer` memcheck, synccheck and initcheck. racecheck reports a hazard between the assert in
`OneToManyAssocRandomAccess::finalize` and `warpPrefixScan`, which is also present in master, and, in the overflow test
only, a write-after-read on the clamp of the recovered pixel count (the same pattern as the Phase-1 clamp), whose read
side is attributed to threads that do not execute that branch.

Run 3: the Phase-1 Alpaka clusterizer on 1000 events of `/ZeroBias/Run2026D-v1/RAW` gives identical clusters in master
and in the branch, with morphing both off and on.

Registers of `FindClus` for Phase 2 increase (sm_75 128 to 143, sm_80 119 to 127, sm_89 105 to 127, sm_90 79 to 93,
sm_100 85 to 107, sm_120 89 to 109), while the shared memory is unchanged; Phase 1 is unchanged in both. The
producer time per event (T4, FastTimerService) is the same within 0.4 ms for master, morphing off and morphing on.

`runTheMatrix.py -l 38434.402 --nEvents 10` (TTbar D128, pixel-only Alpaka) passes all steps on a T4 in
CMSSW_20_1_X_2026-10-29-2300, and its step 3 also runs with `DoDigiMorphing = True` in TBPX L1.

The physics validation (RecHit residuals with respect to the SimHits, tracking efficiency, end-of-life thresholds)
and the choice of the default regions for Phase 2 will follow; this PR does not change any workflow.

#### If this PR is a backport please specify the original PR and why you need to backport that PR. If this PR will be backported please specify to which release cycle the backport is meant for:

Not a backport, and no backport is foreseen.
