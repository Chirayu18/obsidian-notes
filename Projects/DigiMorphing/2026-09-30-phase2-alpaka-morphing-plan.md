---
tags: [reference]
status: active
date: 2026-09-30
source: lxplus
---

# Phase-2 digi morphing in the Alpaka clusterizer: survey and plan

Surveyed on **cms-sw/cmssw master `cfc33e9`** (2026-09-30), sparse checkout at
`/eos/user/c/cgupta/cmssw-master/cmssw`. All paths below are relative to
`RecoLocalTracker/SiPixelClusterizer/plugins/alpaka/` unless stated otherwise.

## 1. What the code does today

**Phase 2 has no morphing, and no duplicate removal either.**

- `PixelClustering.h:281-492`: duplicate removal *and* the whole morphing block are
  wrapped in `if constexpr (not isPhase2)`. Phase 2 skips both.
- `pixelStatus` (`PixelClustering.h:28-106`) hard-codes the Phase-1 module size,
  160 × 416 pixels. That gives a 1-bit image plus a 1-bit temp bitmap in shared
  memory, 2 × 2080 words = **16.6 KB**.
- `SiPixelRawToClusterKernel.dev.cc:694-714` (`makePhase2ClustersAsync`) launches
  `FindClus` with `enableDigiMorphing=false`, `nullptr`, `0`, `0`, an empty fakes
  collection, and `maxElementsPerBlock`. It uses **4000 blocks, one per module**,
  where Phase 1 uses 64 blocks that loop over modules.
- `Geometry/CommonTopologies/interface/SimplePixelTopology.h:548`:
  `Phase2::maxPixInModuleForMorphing = 0`. The histogram has no room for fakes.
- `SiPixelPhase2DigiToCluster.cc` has no `DoDigiMorphing`, `MaxFakesInModule` or
  region parameters. It also has **no cabling map**, so the Phase-1 way of picking
  morphing modules (`cablingMap_->det2fedMap()` + `skipDetId`,
  `SiPixelRawToCluster.cc:278-304`) can't be reused. It does fill
  `rawIdArr = detid` (`:164`), so the device-side binary search on raw IDs
  (`isMorphingModule`) works as it is.

**The FindClus logic after morphing is already generic.** The fake-pixel storage,
the histogram IDs (`>= maxPixInModule` means a fake), the neighbour search, the
union-find with `numElements + i` IDs, and dropping fakes before the output all
work for any topology. The Phase-1-specific part is the step that *generates* the
fakes.

## 2. Reference algorithm (what "the same thing" means)

The Phase-1 GPU algorithm is a morphological **closing** that is used only to
bridge clusters:

1. Remove duplicates, then treat duplicate positions as empty.
2. **Dilate** with a 3×3 kernel. `temp` = empty pixels that have any of their 8
   neighbours set.
3. **Erode** with a plus-shaped kernel. A candidate fake stays only if its
   left, right, above and below neighbours are all in image ∪ temp.
4. Fakes go into `fakes_view`. They only merge cluster IDs and are **not**
   written to the output, so they add no charge.

Edge rule to keep: at a module edge in **x (row)**, the missing neighbour counts
as *present* (`edge = 1`, `:405` and `:458`). At an edge in **y (column)** it
counts as *absent* (`above`/`below` = 0). The two directions are handled
differently.

The legacy CPU `RecoLocalTracker/SiPixelDigiReProducers/plugins/SiPixelDigiMorphing.cc`
uses the same kernels (`kernel1={7,7,7}` for dilation, `kernel2={2,7,2}` for
erosion). It is set by `nrows/ncols/nrocs` parameters, so it can run on Phase-2
digis. But it differs in two ways:
- **It adds fakes as real digis** (`fakeAdc=100`, flag 1), so they add charge.
  Compare the two on *which real pixels end up in the same cluster*, not on
  cluster charge.
- It requires `ncols/nrocs + 2*iters <= 64`, and it uses one `nrows/ncols` per
  instance. Phase-2 module types of different sizes each need their own
  instance or a region split.

## 3. Why a straight port doesn't work: the bitmap is too big

A Phase-2 IT module is much larger than a Phase-1 module. CROC chip: 432 × 336
pixels. Quad module: about 580k pixels, whichever way the 25×100 µm pitch is
oriented. **Step 0 below confirms the real dimensions.** At about 580k pixels:

| | Pixels | 2 × 1-bit buffers |
|---|---|---|
| Phase 1 (160×416) | 66,560 | 16.6 KB |
| Phase-2 quad (about 580k) | ~35× more | **~145 KB** |

That is above the 48 KB of static shared memory CUDA allows by default. Only an
opt-in on A100/H100 would go that high, and that is not something to rely on in
CMSSW. Copying the Phase-1 bitmap with larger constants will not compile to
anything that can launch.

## 4. Design options

**A. Sparse morphing on the column histogram (recommended).**
FindClus already builds `hist`, binned by column `yy`, with all real pixels of the
module in shared memory. Every step of the morphing can be answered from it
without a bitmap:
- `isReal(x,y)`: scan bin `y` for `xx == x`.
- `inDilated(x,y)`: any real pixel within Chebyshev distance 1, using bins `y-1..y+1`.
- Generate fakes: for each real pixel `p`, loop over its 8 neighbours `c`. Keep
  `c` if it is inside the module, is not real, and `p` is its **canonical
  generator**, meaning the smallest real pixel in `c`'s 3×3 neighbourhood by
  (y, x). This gives no duplicate fakes, needs no atomics except the fake
  counter, and gives the same fake set on every run. Then apply the plus-erosion
  test through `inDilated` on the 4 neighbours of `c`, with the edge rule from §2.
- Then **rebuild the histogram** with real + fake pixels (zero, count, finalize,
  fill), because `HistoContainer` can only be filled once. The rest of FindClus
  stays the same.

Cost scales with column occupancy, not module area. It needs no new shared
memory, works for any module size, and is well suited to Phase-2's low occupancy.
Cons: it is new logic, so it has to be *shown* equal to the bitmap version (see
validation). It also scans up to 5 bins per candidate, which is slow in very
dense modules. `maxFakesInModule` already puts a limit on that.

**B. Dense bitmap in global memory.** Template `pixelStatus` on the module size
and point `image`/`temp` at a per-block global scratch buffer. The Phase-1 bit
logic is reused unchanged, so it is the same by construction and the diff is the
smallest. Cons: 145 KB × 4000 blocks = 580 MB, so the Phase-2 launch has to drop
to around 64–128 blocks looping over modules, as Phase 1 does. Each morphing
module also needs a 145 KB clear and global atomics. Much more memory traffic
than A.

**C. Bounding-box bitmap in shared memory, with B as the fallback.** This is
the fastest when occupancy is low, but it needs two code paths and a size limit
to tune. Not worth it unless A turns out to be slow.

**Recommendation:** build **B first**, as a correctness reference that is short
and obviously correct. Then build **A** as the production version and require
the two to agree bit for bit on the fake set. If A is fast enough, B can be
dropped or kept behind `GPU_DEBUG`.

## 5. Implementation plan

**Step 0: measure, don't assume.**
- In `SiPixelPhase2DigiToCluster::beginRun`, which already loops over IT
  `detUnits`, record `nrows/ncols` per module type from the
  `PixelTopology`. Confirm `max ncols < clusterBinning (1000)`, which the
  histogram requires.
- Pick a physics target. For Phase 1, morphing is on for L1/L2 high-|z|
  modules only, to recover long clusters split at high |η|. For Phase 2,
  check how often clusters split, per layer/ring, on a ttbar PU200 sample
  with the CPU `SiPixelDigiMorphing` configured for Phase-2 sizes. This
  decides the default regions. The default should stay **off**.

**Step 1: topology constants.**
- `SimplePixelTopology.h`: set `Phase2::maxPixInModuleForMorphing` to a
  non-zero value, for example `maxPixInModule * 2 / 5` as in Phase 1. Check
  shared memory (histogram content goes from 6000 to 8400 × uint16) and the
  size of `nn[maxIter][8]` on the serial CPU backend. For Phase 1 that is
  already 9216 × 8 × 2 B, and Phase 2 comes out the same.
- Add module-size constants, or pass them at run time from beginRun if module
  types differ (bounds only matter for the edge rule and for option B).

**Step 2: producer (`SiPixelPhase2DigiToCluster.cc`).**
- Add `DoDigiMorphing` (default `false`), `MaxFakesInModule`,
  `barrelRegions`, `endcapRegions`, with the same guard against
  `maxPixInModuleForMorphing` as `SiPixelRawToCluster.cc:213`.
- Choose morphing modules in **beginRun** from `trackerGeometry.detUnits()` and
  `TrackerTopology`, instead of the cabling map. Sort, then copy to a device
  buffer once. Move `parseRegions`/`skipDetId` out of `SiPixelRawToCluster`
  into a shared header so the two producers share one copy.
- **Check the endcap fields:** Phase-2 TFPX/TEPX have side/disk/ring/panel/module.
  Confirm what `pxfBlade` returns for Phase-2 detids before using the Phase-1
  `disk,blade,side,panel` region format as is.
- Pass `SiPixelMorphingConfig` and the device pointer into
  `makePhase2ClustersAsync`, which needs a matching signature change in
  `SiPixelRawToClusterKernel.h`.

**Step 3: launch (`makePhase2ClustersAsync`).**
- Use `maxElementsPerBlockMorph` when morphing is on.
- **Fakes buffer size:** the current indexing `firstFake = maxFakesInModule * block`
  with 4000 blocks gives 4000 × 2400 × ~24 B ≈ **230 MB per event**. Index by
  the module's position in the morphing-module list instead: change
  `isMorphingModule` so it returns the binary-search index. Then allocate
  `numMorphingModules × maxFakesInModule`. Each module goes to exactly one
  block, so the slot is unique. Phase 1 can use the same change.

**Step 4: kernel (`PixelClustering.h`).**
- Move the Phase-1 bitmap block into a helper, `morphPhase1Bitmap(...)`, so the
  code is split by topology rather than wrapped in one large `if constexpr`.
- Add `morphSparse(...)` (option A), and for B, `morphBitmapGlobal(...)`.
- Phase-2 duplicates: sim digis shouldn't have any, but real Phase-2 data might.
  Decide whether to add duplicate removal. In the sparse version it can be done
  by scanning the same histogram column. At minimum, add a `GPU_DEBUG` count.
- Order: fill hist with real pixels, then morph, then clear and refill hist
  with real + fakes, then the existing nn/union-find. The Phase-1 path keeps
  its current order.

**Step 5: configuration.**
- `siPixelClustersPreSplitting_cff.py:58` already builds the Phase-2 Alpaka
  clusterizer from `(alpaka & phase2_tracker)`. Add
  `(alpaka & phase2_tracker & siPixelDigiMorphing).toModify(..., DoDigiMorphing=True, barrelRegions=[...])`.
- Check that the HLT Phase-2 menu (`HLT_75e33`) copy of the module picks up the
  new parameters with their defaults and doesn't change.

## 6. Validation

1. **Unit test on synthetic digis.** Test holes of 1 pixel in x, in y and
   diagonally, clusters in an L shape, and pixels on all four module edges (for
   the edge rule). Check the fake set and the merged cluster IDs against a
   simple host implementation. Run on the serial CPU backend and on CUDA/ROCm.
2. **A vs B** on real PU200 events: the same fake set in every module, and the
   same cluster membership.
3. **GPU vs legacy CPU:** `SiPixelDigiMorphing` (with Phase-2 `nrows/ncols/nrocs`)
   followed by the legacy Phase-2 clusterizer. Compare *cluster membership of
   real pixels*, not charge (see §2).
4. **Defaults unchanged:** with morphing off, clusters must be identical to the
   current master (the Phase-2 relvals and the HLT_75e33 workflow).
5. **Physics:** number of clusters and cluster size vs η per layer, and pixel
   track efficiency and fake rate, with and without morphing on PU200 ttbar.
6. **Timing:** FindClus time in the Phase-2 HLT, with morphing on the chosen
   regions vs off.

## Open questions for Chirayu
- Which Phase-2 regions (physics motivation, same as for Phase 1?), or is this
  first a "make it possible" PR with the default off?
- Is B worth writing, or should A be validated directly against the CPU
  `SiPixelDigiMorphing` plus a synthetic unit test?
- Phase-2 duplicate removal: include it, or leave it for a separate PR?
