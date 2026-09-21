---
tags: [reference]
status: active
date: 2026-09-21
source: laptop
---

# IT Unpacker GPU (Alpaka) — code + benchmark review

Review of Si Hyun Jeon's Tracker DPG talk `20260902_trackerdpg_unpackergpu.pdf`
and the code at `github.com/sihyunjeon/cmssw` branch `feature/it_alpaka_tests`
(HEAD `3354683874a`; true base **CMSSW_16_0_0_pre1**, merge-base `dd7156a9fb`,
2025-10-03. It builds there — but cannot process an event of its own test cfg).

Read via a proper release area, not a raw clone:
`lxplus:/afs/cern.ch/user/c/cgupta/CMSSW_16_0_9/src` (SCRAM_ARCH `el9_amd64_gcc13`),
`git cms-init` + his fork as remote `sihyun`. Files read with
`git show sihyun/feature/it_alpaka_tests:<path>`.

**True base: `CMSSW_16_0_0_pre1`** (merge-base `dd7156a9fb`), not 16_0_9 — which is why
the topology constants below differ from current, and part of why it does not build on
16_0_X. Against that base the branch is **73 added / 27 deleted / 20 modified**.

## Shape of the port (`git diff --name-status dd7156a9fb <branch>`)

- **New Alpaka unpacker** (`EventFilter/Phase2PixelRawToDigi/plugins/alpaka/`, 5 files):
  `Phase2ITUnpackerKernels.{h,dev.cc}`, `Phase2ITRawToBitStreamProducer.cc`,
  `Phase2ITBitStreamToPixelProducer.cc`, `Phase2ITModuleMapESProducer.cc`.
- **New host-side chain** (same package, `plugins/`): `PixelToBitStreamProducer`,
  `BitStreamToRawProducer`, `RawToBitStreamProducer`, `BitStreamToPixelProducer`,
  `RawToPixelProducer` (fused), `BitStreamToAuroraProducer`, `Phase2ITElinkAnalyzer`;
  plus `interface/` headers (`Phase2ITUnpacker.h`, `Phase2AuroraPacker.h`,
  `Phase2DAQFormatSpecification.h`, `SLinkModuleMap.h`, `ELinkChipMap.h`,
  `Phase2ITModuleMapRecord.h`). Deletes `Phase2ITQCoreProducer.cc`.
- **New DataFormats package** `Phase2ITBitStreamSoA` (16 files): the chip-bitstream and
  module-map SoAs, their alpaka collections, and the cuda/rocm ROOT dictionaries.
- **`Phase2TrackerDigi`**: adds `ChipModuleMap.h`, `Phase2ITBitReader.h`,
  `Phase2ITBitBuffer.h`, `Phase2ITAuroraBitStream.h`; modifies `Phase2ITChip`,
  `Phase2ITQCore`, `Phase2ITChipBitStream` and both `classes*` dictionaries.
- **Conditions**: `TrackerDetToDTCELinkCablingMap` gains the IT module info (`subtype`);
  `DTCCablingMapProducer`/`TestReader` updated; two new IT cabling cfgs; a committed
  `OTandITDTCCablingMap.db` sqlite payload in the test dir.
- **Large OT-side rewrite** — `EventFilter/Phase2TrackerRawToDigi`, and the bulk of the
  27 deletions: removes the whole legacy FED-buffer stack
  (`Phase2TrackerFEDBuffer/Header/DAQHeader/DAQTrailer/Channel/RawChannelUnpacker/ZSChannelUnpacker`,
  `utils.h`, `Phase2TrackerDigiProducer`, `Phase2TrackerCommissioningDigiProducer`, their
  `_cfi.py`s and the old doc/html), replacing it with `SensorHybrid.h`, `TrackerBlock.h`,
  `ChannelsOffset.h`, `DTHOrbitFieldSizes.h`, `RawToClusterProducer`,
  `ClusterToRawProducer`, `DTHDAQToFEDRawDataConverter`.
- **Test/benchmark harness**: `Phase2ITUnpackAlpaka_cfg.py`, `Phase2ITDigiCompare.cc`,
  `Phase2ITDigiRecovery.cc`, `Phase2ITUnpackScan.sh`, `Phase2ITBlockScan.sh`, the two
  scan plotters, `Phase2ITRecoveryPlot.py`.
- **Also modified**: `DataFormats/FEDRawData/FEDRawDataCollection` (+ the stale
  `RawDataBuffer.cc` noted below).

**Not touched by him:** `SimplePixelTopology.h`, `ClusteringConstants.h`,
`PixelClustering.h`, `SiPixelDigisSoA.h`. Where those differ from 16_0_9 it is upstream
drift since his base, not his edit.

**Every claim below is labelled MEASURED / SOURCE-READ / INFERRED.** This area was
never compiled; a separate build was attempted on EOS and **failed to compile** (see
below), so no claim here is a runtime result from executing the unpacker. MEASURED
means observed — a build error, or a machine's load — not a physics output.

## His two questions

### Q1 — "Is my understanding of SiPixelDigisSoA columns correct?"

Mostly, with one column wrong in a way that matters.

`DataFormats/SiPixelDigiSoA/interface/SiPixelDigisSoA.h` (SOURCE-READ) —
7 columns: `clus, pdigi, rawIdArr, adc, xx, yy, moduleId`.

| Column | His slide | Verdict |
|---|---|---|
| `clus` | 0 placeholder | OK, but see below — 0 is a *valid* cluster id |
| `pdigi` | row/col/ToT/flag | Correct |
| `rawIdArr` | detId | Correct |
| `adc` | ToT, duplicated? | Correct field, but **not** a duplicate — see below |
| `xx`/`yy` | row/col, duplicated? | Correct, genuinely redundant with `pdigi` |
| `moduleId` | "index 0–3999" | Range correct on his base; but **his code writes the wrong index** |

**`adc` is not a duplicate of `pdigi.adc`.** It is the field the calibration step
rewrites in place. `RecoLocalTracker/SiPixelClusterizer/plugins/alpaka/CalibPixel.h`
`CalibDigisPhase2` (SOURCE-READ) converts raw ToT to electrons —
`adc_int * ElectronPerADCGain`, kink correction, `+ Phase2DigiBaseline`, clamped to
uint16 max. `pdigi` is left alone. So after calibration the two disagree *by design*:
`adc` is electrons, `pdigi`'s packed field is still raw ToT. Keeping them equal at
unpack time is right; expecting them to stay equal is not.

**`clus = 0` is not a safe placeholder.** The consumer
`SiPixelDigisClustersFromSoAAlpaka.cc` (SOURCE-READ) skips digis on
`clus() == invalidClusterId`, and treats `clus() < 0` as an error. `0` is a real
cluster id, so placeholder digis look like members of cluster 0. Harmless while the
unpacker output is only compared digi-by-digi; wrong the moment it is fed to the
clusterizer. `pixelClustering::invalidClusterId` is the honest placeholder.

**`moduleId` — the substantive finding.** The range claim is fine; the *provenance* is not.

*Range — his slide is correct for his own base; the concern is forward-compatibility.*
**Corrected 2026-09-22.** An earlier draft of this note said the range was 4000 for
`Phase2` and 6872 for `Phase2OT`. That is true of **stock CMSSW_16_0_9**, but *not* of
the tree his branch is built on. His true base is **CMSSW_16_0_0_pre1**
(merge-base `dd7156a9fb`), and he does **not** touch `SimplePixelTopology.h`,
`ClusteringConstants.h` or `PixelClustering.h` at all — they differ from 16_0_9 purely
through upstream evolution since his base (354/108, 2/1 and 134/141 lines respectively).
So this was never his edit; it is base drift. On his base:

| | His base (16_0_0_pre1) | Stock 16_0_9 |
|---|---|---|
| `phase2PixelTopology::numberOfModules` | 4000 | `nModulesPix` = 4000 |
| `nModulesOT` / `nModulesTot` | *absent* | 2872 / 6872 |
| `Phase2OT` traits | *absent* | present, shadows to 6872 |
| `pixelClustering::maxNumModules` | 5000 | 6872 |

So **"moduleId: index 0–3999" is right on his base** — there is no OT extension there
and no second traits struct. Withdraw the "wrong range" criticism.

What survives is a forward-compatibility note, not an error: his branch is based on an
older tree than current 16_0_X, where the CA extension added `Phase2OT` with
`numberOfModules = 6872` and raised `maxNumModules` from 5000 to 6872. When this port is
rebased — which it must be, see the blocking section — the bound stops being a literal
4000 and becomes `TrackerTraits::numberOfModules`. Worth writing that way now.

**A loose end worth one slide-line: the constant, its comment, and the test geometry
are three different things.** On his branch `ClusteringConstants.h:26` reads
`maxNumModules = 5000` justified by the comment *"D110 has 4000 modules"*, while the
test cfg loads **D112** (`GeometryExtendedRun4D112Reco_cff`, cfg `:61`, and the RelVal
sample is `Run4D112`). Whether D112's IT module count still fits under 4000 — and
therefore whether the 5000 ceiling has the headroom the comment claims — is not
derivable from the cff files; it comes from the geometry XML. This is not a new bug so
much as the reason the runtime measurement is the only thing that settles the range.

*Provenance — the likely bug.* `Phase2ITModuleMapESProducer.cc` (SOURCE-READ) fills
the field from the **TrackerGeometry** det-unit index:

```cpp
modGeomIdx.push_back(static_cast<uint16_t>(det->index()));   // det = geom->idToDetUnit(DetId(detId))
```

which `ChipFillKernel` copies to `c.moduleId()` and `DigiFillKernel` writes into the
SoA. But `TrackerGeometry::addDetUnit` does `setIndex(theDetUnits.size())` —
a running insertion counter over **every det unit in the tracker, IT and OT together**,
in build order. That is not the dense pixel index the clusterizer requires, and
nothing in `SimplePixelTopology.h` bounds it.

Two failure modes, neither caught at runtime in a release build:
- index ≥ `numberOfModules` (4000 on his base) → `clus_view[moduleId]` indexes out of
  bounds; `maxNumModules` is only 5000 there, so there is little headroom.
- index > 65535 wraps silently to a small, plausible, wrong module.

**The producer validates the det but never the index.** It throws if the cabling map
has no `ModuleInfo` (`:57-58`) and throws again if `idToDetUnit` returns null
(`:60-61`) — then casts `det->index()` to `uint16_t` at `:65` with no bound check at
all: not against `numberOfModules`, not `maxNumModules`, not 65535. The author
explicitly handled two failure
modes and threw on both, which makes the missing third one read as an oversight rather
than a considered trust assumption. That is the cleanest statement of the finding.

*(An earlier draft claimed `GeomDet::m_index` could arrive as its `-1` default and cast
to 65535 — slipping past the 65534 sentinel. **Retracted:** the null check at `:60`
means any det reaching the cast is registered, and `addDetUnit` sets its index. Verified
first-hand in the source.)*

The only guard is `ALPAKA_ASSERT_ACC(thisModuleId < TrackerTraits::numberOfModules)`
(`PixelClustering.h:212` on the branch, in `FindClus`; a second one at `:164` in
`CountModules`) — **compiled out in release builds**. The harmful write is
`clus_view[thisModuleId].clusInModule()` at `:801`. The `static_assert`s bound the
traits constant, not the runtime value. The unpacker is the trust boundary and must
guarantee the invariant itself.

> **All `PixelClustering.h` line numbers here are branch-relative and were corrected
> on 2026-09-22.** An earlier draft cited `:327` for the assert, which came from
> *stock* 16_0_9; the branch rewrites that file (141 insertions / 134 deletions, 275
> lines differing), and its `:327` is a closing brace. A reader checking `:327` in
> either tree finds no assert and could reasonably conclude the finding was fabricated.
> Verified on the branch: `grep ALPAKA_ASSERT_ACC.*numberOfModules` returns exactly
> `:164` and `:212`.

*(Range/provenance analysis cross-checked by a second reviewer against the same tree.
It remains SOURCE-READ: nobody has yet run an event to print the actual max. That
measurement is in progress — see Open items.)*

**This is a pattern, not a one-off — `subtype` has the same defect.** (SOURCE-READ,
verified first-hand. Found by a second reviewer; the reference comparison is mine.)

`hitToRowCol` indexes a flattened quadrant table with a cabling-derived integer:

```cpp
constexpr int8_t kQuadX[13][4] = {...};   // ":111  index 0 unused (subtype is 1..12)"
const int rowOffset = (kQuadX[subtype][chipId] > 0) ? ... ;   // :148, no bound check
```

`subtype` travels `TrackerDetToDTCELinkCablingMap.h:45` (`uint8_t subtype = 0`,
**default 0**) → ESProducer `:64` → SoA → kernel `:346` → `kQuadX[subtype][chipId]`,
with **no range check at any hop**. A subtype of 13..255 reads off the end of a 52-byte
constexpr array. An *uninitialised* cabling entry gives subtype 0 — the row the author's
own comment marks unused — and `kQuadX[0]` is `{0}`, zero-filled, so it silently yields
offset 0 rather than any error.

**The CPU reference validates what the port does not.** `ChipModuleMap.h:69-75`
`quadrantOf()` looks the subtype up in a `std::map` and throws
`"unknown Module_SubType"` on a miss, *and* throws again if the chip index is out of
range for that subtype. The port flattened that map into a fixed `[13][4]` array and
dropped **both** checks. The second one matters independently: subtypes 1 and 5 have
only 1 and 2 chips (`CHIP_QUADRANT` `:23,:27`), but every `kQuadX` row is 4 wide, so an
out-of-range `chipId` reads a neighbouring subtype's data and returns a plausible wrong
offset instead of throwing.

So `moduleId` and `subtype` are the same defect: **cabling/geometry-derived integers
used as array indices without validation, in code ported from a reference that
validated them.** Worth presenting to him as one systemic point rather than two bugs —
it is harder to wave off, and the fix is the same in both places.

**Why validation missed it (SOURCE-READ).** `test/Phase2ITDigiCompare.cc` keys on
`(rawIdArr, xx, yy, adc)` only. `moduleId`, `clus` and `pdigi` are **never compared**.
And the legacy CPU producer emits `DetSetVector<PixelDigi>` keyed by detId — it has no
`moduleId` concept at all, so the round trip *structurally cannot* test it. The green
ΔADC plot on slide 17 is real but covers 4 of 7 columns. Worth saying out loud in the
next talk.

### Q2 — "Is lxplus-gpu good enough, or is there a dedicated machine?"

**No — lxplus-gpu is not a benchmarking platform.** This is MEASURED, not opinion.

`lxplus-gpu.cern.ch` round-robins across nodes in wildly different states. Sampled
2026-09-21, all 28-core, Tesla T4 16 GB:

| Node | load (1/5/15 min) | load/core | GPU util | VRAM used |
|---|---|---|---|---|
| lxplus909 | 6.5 / 6.7 / 7.4 | 0.24× | 0 % | 123 MiB |
| lxplus908 | 30.8 / 30.9 / 30.9 | 1.10× | 0 % | 0 MiB |
| lxplus902 | 49.1 / 49.1 / 49.3 | **1.76×** | **69 %** | **11.5 GB** |

Consecutive `ssh lxplus-gpu` calls landed on three different hosts, one of which was
running someone else's GPU job at 69% utilisation with 11.5 GB resident. Repeat
points in a scan are therefore not comparable — they may not even be the same machine.
Note the load is *batch/system* work: `who` showed **zero** logged-in users on the
quiet node, so "looks idle" is not a usable check.

Compounding it: the slide says **128 threads** on a 28-core node — 4.6×
oversubscription before anyone else's load. `Phase2ITUnpackScan.sh` runs points
sequentially with **no repeats** and no machine-exclusivity check, so there is no
spread to reveal any of this.

**Where to ask for proper hardware.** The CMS Phase-2 HLT/GPU performance TWiki
documents the accepted methodology — a *dedicated full node*, jobs pinned, T4 as the
standard reference:
<https://twiki.cern.ch/twiki/bin/view/CMSPublic/PhaseIIHLTRecoAndGPUPerformance>

Routes worth naming to him:
- **CMS Patatrack / heterogeneous computing group** — owns the `cmg-gpu*` dev boxes and
  is the normal channel for reproducible GPU benchmarking slots. Ask on the
  heterogeneous-computing / Patatrack mattermost or via the CMSSW Alpaka conveners.
- **HLT integration** — the benchmark nodes behind the TWiki above; the right ask if
  the number is destined for a TDR or a DPS note.
- **CERN IT GPU service / batch** — `request_gpus` in HTCondor gives an *exclusive*
  slot, which alone fixes most of the contention even without a dedicated box.
- A single-user institute box (BU) is fine too — the requirement is exclusivity and
  a pinned clock, not exotic hardware.

## Benchmarking methodology — beyond the shared node

**The headline ~7× probably excludes the device-to-host transfer.** (SOURCE-READ,
from his own comments.) In `Phase2ITUnpackAlpaka_cfg.py`, `timing=1` drops the
comparison analyzer, and the cfg says the analyzer *"is what pulls the digi SoA back
off the device; without it the transfer never happens at all."* `timing=2` keeps it.

So at `timing=1` the GPU never returns its output while the CPU reference has its
`DetSetVector` fully materialised — and slide 19 notes the payload **grows** across
the step, 1.044 MB/event in → 10.10 MB/event out. A ~10 MB D2H transfer per event is
not a rounding error against 8.58 ms. **If 8.58 ms came from `timing=1`, the ~7× is
inflated and the honest figure is the `timing=2` one.** He should quote both and say
which is which. To his credit the knob is documented and opt-in — this is a
presentation problem, not a hidden one.

Other methodology points:
- **No repeats, no uncertainties.** Every point is one run. A 12% block-size "spread"
  (slide 19) is meaningless without a run-to-run error bar — on a shared node the
  noise plausibly exceeds it. The non-monotonic bump at 512 threads/block is more
  likely contention than occupancy. Fix: ≥5 repeats, quote median + spread.
- **`syncForTiming` serialises the queue** and is valid only at `threads=1` (his own
  comment says so). Scans with and without it must never be mixed — worth stating on
  the slide which mode produced the numbers.
- **CPU reference is not thread-scaled.** "CPU 57.4 ms vs GPU 8.58 ms" compares one
  GPU against *one CPU stream*, but the real question for HLT is per-node throughput:
  one GPU against all 28 cores. A throughput-per-node plot would be far more
  persuasive to the DPG than a per-event ratio, and would likely shrink the factor.
- **Sample provenance.** Sample produced under CMSSW_14_0_X, unpacked under 16_0_X.
  Fine for timing, but worth one line confirming the DAQ format didn't change between.

## Blocking: the branch does not build on any released CMSSW

**MEASURED** (build attempted by a second reviewer on `/eos/user/c/cgupta/phase2build`,
commit `3354683874a`, `el9_amd64_gcc13`; cvmfs greps verified first-hand here).

```
DataFormats/Phase2ITBitStreamSoA/interface/Phase2ITModuleMapHost.h:8
  error: 'PortableHostCollection2' does not name a type;
         did you mean 'PortableHostCollection'?
```

`PortableHostCollection2` / `PortableCollection2` exist in **exactly one** release.
Occurrences in `DataFormats/Portable/interface/PortableHostCollection.h`:

| Release | `PortableHostCollection2` | `PortableHostMultiCollection` |
|---|---|---|
| 16_0_9 | 0 | 0 |
| **16_1_0_pre1** | **1** | **30** |
| 16_1_0_pre2 | 0 | 0 |
| 16_1_3 | 0 | 0 |

**Corrected 2026-09-22 — the direction of this was wrong in an earlier draft.** At his
merge-base `dd7156a9fb` (2025-10-03) the template **was present**: 1 occurrence of
`PortableHostCollection2` over 19 of `PortableHostMultiCollection`. By 16_0_9 both are
**0**. So he did not reach for a nonexistent or unreleased API — *upstream removed it
after he branched*. The earlier framing ("needs a newer release") was backwards.

Consequences, in order of importance:

1. **The port cannot be integrated into current CMSSW as written** — not because the
   API was exotic, but because it was deleted underneath him. Migrating
   `Phase2ITModuleMapHost` / `Phase2ITModuleMapDevice` onto whatever replaces the
   multi-collection template is a prerequisite for upstreaming, independent of whether
   the physics is right. That is a rebase cost he has not yet paid, not a design error.
2. **His slide 10's "based on CMSSW_16_0_X" is true of his base but misleading now** —
   his base is `CMSSW_16_0_0_pre1`, and no *current* 16_0_X release has the template.
3. It builds cleanly on `CMSSW_16_0_0_pre1` (MEASURED — see below), so this is a
   rebase blocker, not a "the code is broken" blocker.

A second, independent error — `RawDataBuffer.cc:34: 'memcpy' was not declared`, missing
`#include <cstring>` — is **not his bug and self-resolves**: `16_1_0_pre1` already has
that include at line 11. His branch carries a stale copy of a file upstream had fixed.

## It builds — and then cannot process a single event of its own test cfg

**MEASURED 2026-09-22** (second reviewer; build at
`/eos/user/c/cgupta/phase2build/CMSSW_16_0_0_pre1`, exact branch tree, **no patches**,
asserts ON, CPU backend).

The build succeeds: `rc=0`, zero errors, on `CMSSW_16_0_0_pre1` — his true merge-base.
Then the stock cfg, with no instrumentation, dies on the **first event**:

```
Begin processing the 1st record. Run 1, Event 9201, LumiSection 93
category: 'TrackerDetToDTCELinkCablingMap has been asked to return ModuleInfo
           for a DetId not present in the map.'
   [2] Calling method for module PixelToBitStreamProducer
Exception Message:  DetId = 303042565            rc=65
```

It fails in **his own packing module**, upstream of anything GPU. An instrumented run
hit the same root cause one guard earlier, in the ESProducer's `:57-58` throw, with
detId `303042581`. Both decode to `det=1, subdet=1` — PixelBarrel, genuine IT — and are
only 16 apart, so this looks like a contiguous block of IT modules missing from the
shipped cabling map rather than one stray entry. A control run without instrumentation
confirms this is **not** an artefact of the added analyzer.

**Likely cause (INFERRED, not confirmed): geometry mismatch.** The cfg loads
`GeometryExtendedRun4D112Reco_cff` (`:61`) and the RelVal is `Run4D112`, while the
committed `OTandITDTCCablingMap.db` appears to have been built for a different
geometry — `ClusteringConstants.h:26` documents D110. Nobody has tried D110, because
that changes the configuration under test.

Two consequences, both worth putting to him directly:

1. **The `moduleId` measurement is unobtainable as configured.** The job dies at the
   cabling map, far upstream of the clusterizer, so there is no distribution to measure.
   The provenance bug may well be real — it is simply *not reachable* on this cfg.
2. **Which input produced the DPG numbers?** If this cfg cannot read this RelVal, then
   the slide-18 timings came from some other combination of input, cabling map or
   geometry. That is the single most useful question to ask him, because it determines
   whether the ~7× is reproducible at all.

## Decode path (Huffman / hitmap) vs the in-tree CPU reference

The Alpaka decode is an **independent reimplementation** of the CPU decoder in
`DataFormats/Phase2TrackerDigi/` (`Phase2ITQCore.cc`, `Phase2ITBitReader.h`), so
diffing the two is a genuine cross-check — no RD53B spec reading needed. (Note the CPU
round trip *alone* is not such a check: `encodeQCore` and `decodeHitmap` are methods of
the same class sharing one Huffman tree definition, so they mirror each other by
construction. It is the Alpaka-vs-CPU comparison that has value.)

**Finding — the ported `BitReader::next()` lost its bounds check.** (SOURCE-READ,
verified first-hand.)

```cpp
// reference, Phase2ITBitReader.h:14-20
bool next() {
  if (pos_ >= nBits_) return false;                    // GUARD
  const bool b = (bytes_[pos_ / 8] >> (7 - pos_ % 8)) & 1;
  ++pos_; return b; }

// alpaka, Phase2ITUnpackerKernels.dev.cc:38-42
ALPAKA_FN_ACC bool next() {
  const bool b = (bytes[pos >> 3] >> (7 - (pos & 7))) & 1;   // reads FIRST, no guard
  ++pos; return b; }
```

No live out-of-bounds path found: every current caller guards at the call site —
`nextOr0()` checks `pos < len`, `bits(n)` has it in the loop condition, and `decPair`
checks before each `next()`. But the guarantee now lives in the callers rather than the
reader, unguarded `next()` is public on the struct, and the comment at `:32` claims it
is *"clamped like binaryToInt"* — a safety property the code no longer has. In GPU code
an OOB read is silent. Restoring the guard is two lines and one predictable branch.

**Checked and correct, recorded so nobody re-derives it:**
- `decPair` matches `decPairBits` at every branch including both end-of-stream returns;
  the `first<<1|second` packing is consistent throughout.
- `decChunk8` unrolls the reference's generic `decChunk` for n=8 and reproduces its
  active-set evolution exactly. Only fragility: `act2[4]` is sized for exactly n=8, so a
  larger chunk would overflow silently. The name signals the constraint; low priority.
- **`bitOffset` is byte-aligned by construction** — `ChipFillKernel:275` computes
  `(fedByteBase + payloadWord * 4) * 8`, a byte quantity times 8, so `>>3` in the
  `BitReader` constructor is exact and cannot misalign the stream. Raised as a possible
  decode-corrupting bug; **not one**.

## Other kernel findings

(SOURCE-READ, second reviewer's survey. Priority order; none measured.)

**MEDIUM — `digis[cursor++]` is an unbounded write.** `DigiFillKernel:348-354` takes
`cursor = offsets[c]` and increments per hit with no check against
`digis.metadata().size()`. Correctness rests entirely on the count and fill passes
decoding byte-identically — they share `decodeChip`, so it holds normally. But any
divergence between the passes (the unguarded `BitReader::next()` above is one candidate)
writes into the next chip's range or past the collection end. Not a demonstrable bug;
it is an unbounded write whose only guard is a cross-kernel behavioural invariant.
One-line fix: `ALPAKA_ASSERT_ACC(cursor < digis.metadata().size())` — free in release,
and it traps in exactly the asserts-on build being used for the runtime check.

**LOW — silent module loss on malformed input.** Two self-documented FIXMEs:
- `:171` *"malformed offsets are clamped and the module dropped silently"* —
  `moduleSpan` sets `s.start = s.end = 0` with no counter and no `LogWarning`. A corrupt
  FED loses modules invisibly. Fine in a unit test; a different statement entirely in a
  DQM context, where "we drop bad modules silently" is the kind of thing that needs a
  monitoring hook before data-taking.
- `:250` *"chips per module is static, so this count could be built once per IOV"* —
  performance, not correctness.

**LOW — zero-size chip truncates a module quietly.** `forEachChip:196` flags
`sizeWords == 0 && endBit != 0` as overrun, but `sizeWords == 0 && endBit == 0` falls
through to a zero-length stream; the cursor then advances 1 word into mid-payload, the
next `readWord` fails the magic check, and the module ends early with no diagnostic.
Self-limiting — the walk is bounded by `chipId >= CHIPS_PER_MODULE` (=4) — so it is
neither a hang nor unbounded, just a malformed-data path that produces no message.

**Checked and correct** (recorded so nobody re-derives): the `moduleSpan` 128-bit
padding arithmetic matches the legacy CPU path line for line; the spare-row zeroing is
`once_per_grid`-guarded and targets `size()-1`; and the overrun test correctly bounds
against the FED body rather than the module span.

## What is genuinely good

Worth saying plainly — this is well-built code, and the review above is mostly about
claims, not craft.

- **Two-pass count/fill with prefix sums** is the correct pattern for variable-length
  output. Each chip gets a private output range, so the fill kernels need **no atomics**.
- **Clean host/device split.** Cabling map and geometry flattened once per IOV in an
  ESProducer, not per event.
- **Buffers cached and reused** across events, growing only when needed.
- **Malformed data handled without UB**: spans clamped, chip walk bounded by
  `CHIPS_PER_MODULE`, overrun payloads handed an empty stream, `BitReader` clamped at
  `len`. The `FIXME` about silently dropped modules is honestly flagged.
- **`checkBlockSize`** validates against the real device limit and warns on non-multiples
  of the warp size.
- **`Phase2ITUnpackScan.sh` log validation is better than most**: it requires the
  `T---Report end!` marker, rejects zero-event jobs, and deliberately keeps numbers from
  jobs that died *after* a complete report. That reasoning is correct and well commented.

## Recommended fixes, in priority order

0. **Say which input, cabling map and geometry produced the slide-18 numbers.** The
   committed cfg + committed `.db` + the RelVal it names cannot process one event, so
   the published timings came from a combination that is not in the branch. Everything
   else is secondary until this is answered.
0b. **Ship a cabling map matching the cfg's geometry** (or point the cfg at the geometry
   the map was built for). Currently the test is unrunnable as committed.
0c. **Rebase off `PortableHostCollection2` / `PortableCollection2`.** Upstream deleted
   the multi-collection template after he branched, so this is a rebase cost, not a
   design error. Also drop the stale `RawDataBuffer.cc` and take upstream's.
1. **Validate cabling/geometry-derived indices before using them as array indices** —
   `moduleId` *and* `subtype`, which are the same defect.
   - `moduleId`: map detId → dense pixel index (the one `layerStart` partitions over
     `[0, nModulesPix)`), not `GeomDet::index()`. Range-check in the ESProducer — throw
     there, where it is cheap and catchable, rather than relying on a device assert that
     vanishes in release. Check **before** the `uint16_t` cast; afterwards the evidence
     is gone. The producer already throws on two other bad-input cases, so this matches
     its own style.
   - `subtype`: reject anything outside 1..12 in the ESProducer, and bound `chipId`
     against the actual chip count for that subtype. The CPU reference
     (`ChipModuleMap::quadrantOf`) throws on both; the port dropped both.
2. **Add `moduleId`/`clus`/`pdigi` to `Phase2ITDigiCompare`**, or state clearly that the
   round trip does not cover them.
3. **Use `invalidClusterId`, not 0**, for the `clus` placeholder.
4. **Restore the bounds check in `BitReader::next()`** to match the in-tree reference,
   or fix the comment that claims it is already there.
5. **Re-quote timings with `timing=2`**, or label the current number
   "unpacking only, excludes D2H".
6. **Repeat every timing point ≥5×** and show a spread.
7. **Get an exclusive machine** before any number goes in a note, and record
   `uptime` + `nvidia-smi` per point regardless.
8. Consider whether `TrackerTraits` should be a template parameter, so `Phase2` vs
   `Phase2OT` bounds follow the sequence instead of being assumed.

## Open items (not yet measured)

- **Max `moduleId` actually emitted on a real event**, plus counts ≥4000 (his base's
  `numberOfModules`) and ≥5000 (his base's `maxNumModules`); ≥6872 too, for the
  post-rebase bound.
  This converts finding #1 from suspected to confirmed. Build in progress on
  `/eos/user/c/cgupta/phase2build`.
  **Method matters:** the stored `uint16_t` *cannot* reveal truncation, because
  truncation is exactly what hides it. The test must compute `det->index()` on the host
  as an `int` and compare it against the stored value per detId. A report quoting only
  post-cast `geomIdx` leaves the >65535 question open no matter what the numbers say.
- **`timing=1` vs `timing=2` delta** — quantifies how much of the ~7× is the missing
  D2H transfer.

## Gotchas hit along the way (lxplus)

- `ssh lxplus` with a **login** shell (`bash -lc`) launches zellij and returns
  terminal-attribute garbage. Use `ssh lxplus 'bash -c "..."'`, no `-l`.
- `scram list` returns nothing non-interactively; list releases with
  `ls /cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/cmssw/`. Only `el9_amd64_gcc13` has 16_0 builds.
- **AFS home is at 93%** (~730 MB free of 10 GB) — cannot host a CMSSW build.
  No work volume exists. EOS works for building (symlinks/hardlinks/chmod all fine)
  but small-file I/O is ~640× slower, so a checkout takes ~33 min.
