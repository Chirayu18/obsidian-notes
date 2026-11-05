---
name: phase2-it-moduleid-measured-in-range
description: "MEASURED: the Phase2 IT unpacker's moduleId is IN RANGE -- max 3999 vs bound 4000, zero truncation; the suspected out-of-bounds bug does not fire"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T23:07:05.441Z
---

The suspected `moduleId` buffer overrun in Si Hyun Jeon's Phase-2 IT Alpaka
unpacker **does not occur**. Measured 2026-09-22, instrumented run, `rc=0`.

Setup: `sihyunjeon/cmssw` `feature/it_alpaka_tests` @ `3354683874a`, built on
**CMSSW_16_0_0_pre1** (matches the branch's merge-base `dd7156a9fb9`),
`el9_amd64_gcc13`, asserts ON (`-UNDEBUG -DALPAKA_DEBUG=1`), `accelerator=cpu`,
D112 geometry, exact branch tree + `CondCore/SiPhase2TrackerPlugins`.

```
nModules                  = 4000
stored geomIdx  min/max   = 0 / 3999
host index()    min/max   = 0 / 3999
count index() >= 4000     = 0      <- numberOfModules, the assert bound
count index() >= 6872     = 0
count index() >= 65536    = 0      <- uint16_t truncation
count index() <  0        = 0
count stored != cast(idx) = 0      <- per-detId host-int vs stored-uint16
count null detUnit        = 0
nTrackerDetUnits (all)    = 30400
nPixelDetUnits (IT only)  = 4000
max index() over IT dets  = 3999
subtype min/max           = 1 / 12
count subtype == 0        = 0
count subtype >  12       = 0
```

**Why the code is safe despite the unguarded cast.** The concern was real on its
face: `Phase2ITModuleMapESProducer.cc:65` does
`modGeomIdx.push_back(static_cast<uint16_t>(det->index()))` with no bound check,
and `GeomDet::index()` IS a tracker-wide counter — 30,400 det units here, far
above the 4000 bound and above `uint16_t`. But the **Inner Tracker modules occupy
indices 0–3999**, the first contiguous block of that enumeration, and the cabling
map only ever asks for IT detIds. So values stay in range by construction.
`max index() over IT dets = 3999` is the number that settles it.

The bound is still only enforced by `ALPAKA_ASSERT_ACC` at
`PixelClustering.h:212` (not `:327` — that citation was wrong), which compiles
out in a release build. The code is correct for this geometry; it is not
*defended* against a geometry where IT det units were not enumerated first.

**Why:** three sessions spent most of a study on a source-read hypothesis that a
single measurement disproved. The provenance reasoning was sound and the missing
bound check is real — but "unvalidated" is not "wrong", and only the run could
tell them apart.

**How to apply:** when a defect hypothesis depends on a *value* rather than a
*structure*, measure before writing it up. Source reading establishes that a
guard is missing; it cannot establish that the guard would ever have fired.
See [[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-it-unpacker-cabling-map-gap|phase2-it-unpacker-cabling-map-gap]] for the withdrawn finding that
blocked this measurement, and [[Meta/claude-memory/_history/general/vault/review-read-the-branch-not-head|review-read-the-branch-not-head]].
