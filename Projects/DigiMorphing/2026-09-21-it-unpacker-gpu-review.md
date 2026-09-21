---
tags: [reference]
status: active
date: 2026-09-21
source: laptop
---

# IT Unpacker GPU (Alpaka) — code + benchmark review

Review of Si Hyun Jeon's Tracker DPG talk `20260902_trackerdpg_unpackergpu.pdf`
and the code at `github.com/sihyunjeon/cmssw` branch `feature/it_alpaka_tests`
(HEAD `3354683874a`, base CMSSW_16_0_X).

Read via a proper release area, not a raw clone:
`lxplus:/afs/cern.ch/user/c/cgupta/CMSSW_16_0_9/src` (SCRAM_ARCH `el9_amd64_gcc13`),
`git cms-init` + his fork as remote `sihyun`. Files read with
`git show sihyun/feature/it_alpaka_tests:<path>`.

**Every claim below is labelled MEASURED / SOURCE-READ / INFERRED.** The area was
never compiled, so nothing here is a runtime result unless it says MEASURED.

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
| `moduleId` | "index 0–3999" | **Right shape, wrong range, and his code writes the wrong index** |

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

**`moduleId` — the substantive finding.** Two separate problems.

*Range.* `Geometry/CommonTopologies/interface/SimplePixelTopology.h` (SOURCE-READ):
`nModulesPix = 4000`, `nModulesOT = 2872`, `nModulesTot = 6872`. There are two
Phase-2 traits: `Phase2` (`numberOfModules = 4000`) and `Phase2OT`, which inherits
from it and *shadows* `numberOfModules = 6872`. So "0–3999" is correct only for
`Phase2`; under `Phase2OT` the valid range is 0..6871. The bound is
`TrackerTraits::numberOfModules`, not a fixed 4000.

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
- index ≥ 4000 (or ≥ 6872) → `clus_view[moduleId]` indexes out of bounds.
- index > 65535 wraps silently to a small, plausible, wrong module.

**The producer validates the det but never the index.** It throws if the cabling map
has no `ModuleInfo` (`:57-58`) and throws again if `idToDetUnit` returns null
(`:60-61`) — then casts `det->index()` to `uint16_t` at `:65` with no bound check at
all: not against 4000, not 6872, not 65535. The author explicitly handled two failure
modes and threw on both, which makes the missing third one read as an oversight rather
than a considered trust assumption. That is the cleanest statement of the finding.

*(An earlier draft claimed `GeomDet::m_index` could arrive as its `-1` default and cast
to 65535 — slipping past the 65534 sentinel. **Retracted:** the null check at `:60`
means any det reaching the cast is registered, and `addDetUnit` sets its index. Verified
first-hand in the source.)*

The only guard is `ALPAKA_ASSERT_ACC(thisModuleId < TrackerTraits::numberOfModules)`
(`PixelClustering.h:327`) — **compiled out in release builds**. The `static_assert`s
bound the traits constant, not the runtime value. The unpacker is the trust boundary
and must guarantee the invariant itself.

*(Range/provenance analysis cross-checked by a second reviewer against the same tree.
It remains SOURCE-READ: nobody has yet run an event to print the actual max. That
measurement is in progress — see Open items.)*

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

1. **Fix `moduleId`.** Map detId → dense pixel index (the one `layerStart` partitions
   over `[0, nModulesPix)`), not `GeomDet::index()`. Add an explicit range check in the
   ESProducer — throw there, where it is cheap and catchable, rather than relying on a
   device assert that vanishes in release. The producer already throws on two other
   bad-input cases, so this is consistent with its own style; check **before** the
   `uint16_t` cast, since afterwards the evidence is gone.
2. **Add `moduleId`/`clus`/`pdigi` to `Phase2ITDigiCompare`**, or state clearly that the
   round trip does not cover them.
3. **Use `invalidClusterId`, not 0**, for the `clus` placeholder.
4. **Re-quote timings with `timing=2`**, or label the current number
   "unpacking only, excludes D2H".
5. **Repeat every timing point ≥5×** and show a spread.
6. **Get an exclusive machine** before any number goes in a note, and record
   `uptime` + `nvidia-smi` per point regardless.
7. Consider whether `TrackerTraits` should be a template parameter, so `Phase2` vs
   `Phase2OT` bounds follow the sequence instead of being assumed.

## Open items (not yet measured)

- **Max `moduleId` actually emitted on a real event**, plus counts ≥4000 and ≥6872.
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
