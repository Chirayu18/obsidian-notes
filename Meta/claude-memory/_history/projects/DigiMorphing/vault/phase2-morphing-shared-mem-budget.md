---
name: phase2-morphing-shared-mem-budget
description: "Phase-2 HLT kernels must stay within 48 KB STATIC shared memory (Bocci, 2026-10-15); IT ROC is 672x216, so whole-module morphing bitmaps (73/145 KB) are out; strip-tiled bitmaps chosen and built"
metadata:
  node_type: memory
  type: project
  originSessionId: 22d46732-dd3b-4677-a150-f59e2fdd5237
  modified: 2026-10-15T08:33:19.421Z
---

A. Bocci, asked by Chirayu at the Tracker DPG workshop on 2026-10-15: Phase-2 HLT
kernels stay within **48 KB of static shared memory, same as Run 3**. Dynamic shared
memory above that is not the plan.

Phase-2 IT sizes (T40 `pixelStructureTopology.xml`, Bartosik slide 12): ROC = 672 rows ×
216 cols (25×100 µm). Dual = 672×432 (73 KB for image+temp bitmaps), quad = 1344×432
(145 KB). Even one ROC (36 KB) does not fit next to the FindClus histogram.

**Why:** this rules out porting the Phase-1 per-module bitmap; Chirayu wanted the
budget settled before building Phase-2 digi morphing.

**How to apply:** Phase-2 morphing was built (2026-10-23) as the Phase-1 bit logic on 44-column strips,
sharing the Phase-1 bitmap buffers; see [[Meta/claude-memory/_history/projects/DigiMorphing/vault/alpaka-kernel-resources-measure|alpaka-kernel-resources-measure]] for the measured numbers. Full plan and sources in the vault note
`Projects/DigiMorphing/2026-09-30-phase2-alpaka-morphing-plan.md`. Related:
[[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-it-unpacker-base-release|phase2-it-unpacker-base-release]].
