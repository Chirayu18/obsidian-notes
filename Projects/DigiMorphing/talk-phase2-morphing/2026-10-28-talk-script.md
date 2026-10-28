---
tags: [reference, talk]
status: active
date: 2026-10-28
source: laptop
---

# Talk script: Pixel digi morphing for Phase 2

This script goes with `phase2-morphing-light.pdf`: 21 main slides and a backup section, about 24 minutes. The deck is
in `~/Documents/Codex/2026-10-27/continue-the-slides-from-here-https/outputs/phase2-morphing/`. Times are guides. The
numbers in the text are the ones on the slides.

## 1. Title (0:30)

Today I'll show the work on bringing pixel digi morphing to Phase 2, in the Alpaka pixel clusterizer that runs at
the HLT. We already use this tool in Run 3, so I'll start from there, then explain what changes for Phase 2, how I
implemented it, and how I validated it.

## 2. Outline (0:30)

There are five parts. First a short recap of what morphing does. Then why Phase 2 needs it, and what we learned at
the Tracker DPG workshop. Then the implementation, which is mostly about fitting into GPU memory. Then the
validation, where I redo the checks you already saw for Phase 1. And finally what still has to be tested.

## 3. Recap: what digi morphing does (2:00)

Morphing exists to repair clusters that broke because a connecting pixel fell below threshold.

The picture is a small example computed with exactly the rules of the kernel.
- **Dilation.** We take the hit pixels and mark every empty pixel that touches one of them, including diagonally.
  Those are the orange candidates.
- **Erosion.** We keep only the candidates whose four direct neighbours are all either real pixels or candidates.
  Those survive as the green recovered pixels.

The result: the broken track on the left becomes one cluster, while the isolated pixel three columns away stays
separate.

The recovered pixels are only used to link pixels during clustering. They are dropped before the output, so they
never add charge.

This is the algorithm in the Run-3 HLT, from #48734 and the race-condition fix #49991, which introduced the two
buffers. At the DPG meeting in August it improved the layer-1 hit resolution.

## 4. Why Phase 2 needs cluster recovery (1:00)

This is the Run-3 timeline that Jan Schulz showed at the workshop. In 2025, degraded charge collection gave us broken
clusters at the HLT, and digi morphing was the fix. We faced this problem in Run 3, so we had better be ready for it
in Phase 2, and the Alpaka Phase-2 clusterizer had no morphing at all.

## 5. GPU basics (1:45)

The constraints are all GPU constraints, so here is the minimum we need. A kernel launch has a number of blocks, and
each block has a number of threads. One block runs on one streaming multiprocessor, and its threads work together.

There are two kinds of fast storage.
- **Shared memory** is common to the whole block. At the Phase-2 HLT the budget is 48 KB per block, the same as in
  Run 3. In our clusterizer one block handles one module, so the column histogram and the morphing bitmaps for that
  module must fit in those 48 KB.
- **Registers** are each thread's private working variables. The register file of a multiprocessor is shared by all
  its threads, so the more registers each thread needs, the fewer threads fit in a block.

In the morphing, each thread handles one 32-bit word of the bitmap, which is 32 rows of one column. The steps are
separated by barriers: clear, load, dilate, erode.

## 6. Workshop inputs that shaped the implementation (2:00)

Several things from the workshop fixed the design.
- **Andrea Bocci** confirmed the 48 KB budget. That is why the module is processed in strips. Here "strip" means a
  band of 44 pixel columns, not strip sensors.
- **Nazar Bartosik's geometry** has different module sizes, with big pixels at the chip seams, so the module size has
  to come from the geometry.
- **Giovanni Mersi** showed that chip and sensor coordinates differ. Morphing must look at real neighbours on the
  sensor, and that's what the clusterizer already receives.
- **The occupancy** in layer 1 is about 2×10⁻³ hits per pixel per bunch crossing.
- **The HLT clustering** still runs on simulated digis, so that's what I validated on.
- **The clusters** feed all of HLT tracking, so in the end we must check hits and tracks, not only clusters.

## 7. Module size sets the memory problem (1:15)

This is the problem in numbers. A Phase-1 module is 160 × 416 pixels, and its two bitmaps take 16.6 KB. In Phase 2
the layer-1 module is 672 × 216, a dual module is 672 × 434, and a quad is 1354 × 434. For a quad the two bitmaps
alone would be 149 KB, three times the whole budget, and the histogram also has to fit.

So the module size becomes a run-time input, and we reuse a small pair of buffers.

## 8. Work division of FindClus (1:00)

FindClus is the GPU kernel that groups each module's pixels into clusters.
- **Phase 1** runs 64 blocks, and each one loops over many modules.
- **Phase 2** already ran one block per module in master, and I kept that.

The one consequence for us is where the recovered pixels are stored. They go to global memory, not to the 48 KB, and
one slot set per morphing module is enough: 216 × 1000 slots, about 4.5 MB. Indexing by block would have needed 18
times more.

## 9. A 44-column strip with two-column halos (2:15)

This is the core of the implementation. Instead of the whole module, I morph 44 columns at a time. For each strip I
also load two extra columns on each side. That gives 48 columns, and I emit recovered pixels only for the 44 in the
middle. A layer-1 module needs five strips, and the bigger modules need ten.

Why 44? The largest module has 1354 rows, which is 43 words of 32 bits per column. The Phase-1 buffer holds 2080
words. 48 × 43 is 2064, which fits; 49 columns would not. So 44 is the widest strip that reuses the Phase-1 buffers
as they are, with no extra shared memory.

Why two columns of halo? Eroding the last column of the strip needs the dilated value of the next column, and that
in turn depends on the image one column further out. With only one column of halo you miss recoveries at every strip
edge.

## 10. Skipping empty strips (1:00)

A strip is skipped if there is no real pixel within one column of it, because then nothing can be recovered there.
One column is enough to decide whether a candidate can exist. The second halo column is only needed to decide
whether to keep it.

In practice, at PU200, this rarely helps. In layer 1, 99% of modules have all five strips active, and in the outer
layers and disks about 9 of 10 strips are active. So the cost is really the full number of strip passes.

## 11. Resources and capacity: measured (1:30)

I measured the compiled kernel.
- **Shared memory** is exactly the same as master, 35,728 bytes, because the buffers are shared with Phase 1.
- **Registers** for the Phase-2 kernel go from 128 to 143 per thread. That is also true with morphing off, since it is
  the same compiled kernel.
- **On the T4** we still run 384 threads per block and one block per multiprocessor, so I don't expect an occupancy
  change. But timing is not measured yet, and that's the first item on the to-do list.
- **The Phase-1 kernel is unchanged** on all six GPU architectures.

On capacity: in morphing modules, 5000 slots are for real digis and 1000 for recovered ones. In this sample the
busiest module has 1,534 real digis, and the most recovered pixels in one module is 536. Neither limit is close.

## 12. Configuration, and why these values (1:30)

Four parameters, with the same names as in Phase 1.
- **DoDigiMorphing** is false by default, so nothing changes in any workflow until the physics validation is done.
- **MaxFakesInModule is 1000.**
  - The recovered pixels share the 6000-entry histogram, because a bigger histogram would need 448 threads, and on
    the T4 this kernel is limited to 384.
  - 1000 is about twice the maximum I saw, and still leaves 5000 slots for real digis.
- **barrelRegions** selects all of layer 1, the 216 modules. That is where the 3D sensors see the highest fluence and
  the smallest signal over threshold. It's a first test region, not an optimised choice. Phase 1 used specific
  high-|η| rings.
- **endcapRegions** stays empty, because the Phase-1 region syntax has not been checked for the forward detids.

## 13. Validation: the Phase-1 checks, redone for Phase 2 (1:30)

For validation I took the checks you saw for Phase 1 and redid them. The table pairs each Phase-1 check with its
Phase-2 version. The count difference, cluster size, displays and fake-digi table are done. The RecHit versus SimHit
study with a muon gun is still to do.

The plots use the same formats as #49991, but note the comparison: there it was the code before and after the race
fix, while here cluster size and fakes compare morphing off against morphing on.

I also added a check that is new for Phase 2: an exact reference. That is the same rules applied to the whole module
at once, on the CPU, with no strips.

The unit test has a control: if I deliberately reduce the halo to one column, the test fails. So it really catches
strip-boundary bugs.

The sample is 100 TTbar PU200 events in D128, run on a Tesla T4.

## 14. Count difference: this branch vs master (0:45)

First, with morphing off, does anything change? No. In 400,000 module-events not a single one has a different number
of pixels or clusters, and all 100 events are bit-identical to master. So the default is untouched.

## 15. Cluster size without and with morphing (1:30)

This is the same four-panel plot as in the Phase-1 PR: without morphing, with morphing, both overlaid, and the
per-module difference.

The number of layer-1 clusters drops by 3.3%, from 927,589 to 897,298, and the mean size goes from 5.70 to 5.89
pixels. Per module, the mean cluster size goes up by 0.25 pixels, and no module gets smaller clusters.

## 16. Morphing with and without (1:00)

Here's what that looks like. On the left there are four pieces of one track, and after morphing it's one cluster.
The GPU boxes and the CPU crosses mark the same recovered pixels.

Recovery happens only in the configured layer-1 region. Outside it, nothing changes.

## 17. Recovery can also merge distinct clusters (1:00)

But fewer clusters is not automatically better. Here a short cluster crossing a long one gets joined to it. The CPU
version does the same, so this is the algorithm, not my port. It's the main reason we need the hit-resolution and
tracking studies before enabling it by default.

## 18. Fake digis (1:00)

This is the same table as in the Phase-1 PR. "Fake" here means the temporary connecting pixels: they are dropped
from the output, and they are not fake hits.
- There are about 17,000 per event, 78 per module on average.
- They appear in all 216 layer-1 modules and nowhere else.
- That is 32% of the real layer-1 digis, because they fill the steps of long clusters along the 25 µm rows.

For scale, the Run-3 table had about 3,700 per event. That's a different sample with different regions, so it's for
scale only.

## 19. Exact-reference agreement (1:15)

Now the main correctness result. Comparing the GPU strips with the whole-module reference, there are zero
differences in recovered-pixel coordinates: 1,696,444 recovered pixels in all 21,600 layer-1 module-events. The
reference uses the same rules, so it tests the strips, not the rules.

For the rules, I also compared with the existing CPU morphing. That code was built for Phase 1 and works in 52-column
chunks. It is identical to ours except at its own chunk edges and on the first and last row, where the conventions
differ. The details are in backup.

## 20. What to test next (1:30)

Four groups.
- **Timing:** FindClus time for master, morphing off and morphing on, and the HLT menu throughput. The open question is
  whether the 15 extra registers matter on the Phase-2 HLT GPU.
- **Edge cases and races:** in Run 3 we had a read/write race, so I want GPU race checks, repeated runs that are
  bit-identical, CPU and GPU backends agreeing, and forced overflow of the caps.
- **Physics, as for Phase 1:**
  - the muon-gun RecHit versus SimHit study
  - on-track hits, tracking efficiency and fakes
  - truth matching, to separate real repairs from merges of different particles
  - a degraded-threshold scenario, where morphing should actually help
- **Parameters:** the regions and the cap. Two questions for the experts here: which rings suffer most, and whether
  Phase-2 data can contain duplicate digis.

## 21. Status and next steps (0:45)

To summarise: the Phase-2 port reproduces the intended morphology in the tested layer-1 sample, with exact agreement
in all 21,600 module-events. It handles variable module sizes with 44-column strips and keeps the existing bit
logic. Next are timing, the edge-case and race tests, and the RecHit and tracking validation, as for Phase 1. It
stays off by default until then. Thank you.

## Backup, for questions

Backup starts at slide 22.

- **Slide 23:** the Phase-1 HLT results. The y residual Std Dev went from 420 to 285 for initial RecHits, and from 264
  to 215 on track.
- **Slide 24:** the longer Phase-2 motivation, including the charge sharing and the 5 ke vs 1 ke threshold.
- **Slide 25:** the comparison with the CPU morphing.
  - The CPU code borrows only one column per 52-column chunk.
  - In Phase 1 those chunks are ROC boundaries inside the module, not module edges.
  - Whether missing recoveries there is intended is a question for its authors.
- **Slide 26:** active strips per layer.
- **Slide 27:** how registers cap threads, and threads cap the histogram size.
- **Slides 28 to 31:** the code: module selection, layout and strip loop, dilation, recovery.
- **Slides 32 and 33:** the files changed, and `git diff --stat`.
- **Slide 34:** the IT unpacker code review.
- **Likely questions:**
  - **Is the sample irradiated?** Not knowingly. It tests the implementation; the benefit needs a degraded-threshold
    sample.
  - **Is the exact reference independent?** It uses the same rules, so it checks the strips, and the CPU comparison
    checks the rules.
  - **Do the extra registers cost time with morphing off?** Not expected on the T4 by calculation, but it is the first
    thing to measure.
