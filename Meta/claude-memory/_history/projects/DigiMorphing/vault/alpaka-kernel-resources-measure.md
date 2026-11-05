---
name: alpaka-kernel-resources-measure
description: "CMSSW Alpaka kernels: measure shared memory and registers with cuobjdump -res-usage and alpaka::getFunctionAttributes; if-constexpr discarded branches still cost shared memory; serial backend hides register-limit launch failures"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 22d46732-dd3b-4677-a150-f59e2fdd5237
  modified: 2026-10-23T14:02:29.084Z
---

Measured 2026-10-23 while building Phase-2 digi morphing (FindClus, CMSSW_20_1_X IB):

1. **Discarded `if constexpr` branches still reserve shared memory.** The Phase-2 FindClus got Phase-1's
   two `uint32_t[2080]` bitmaps (16,640 B) that sit in `if constexpr (not isPhase2)`. Every FindClus also
   carries ~2.9 KB not in any declared variable. Fix pattern: declare one shared buffer with the same type
   for all instantiations, outside the branches.
2. **Registers cap the block size before shared memory does.** At 143 regs/thread the T4 (sm_75) allows only
   384 threads/block; 448 gave `cudaErrorLaunchOutOfResources`. The serial CPU test passed, so a
   CPU-only pass proves nothing about GPU launch.

**Why:** both of my paper estimates were wrong (33 KB predicted vs 52.6 KB linked; 448 threads "should fit").

**How to apply:** after any FindClus-style change, read `cuobjdump -res-usage -arch sm_75 <plugin .so>`
(nvlink also errors with "uses too much shared data (… 0xc000 max)"), and in unit tests print
`alpaka::getFunctionAttributes<Acc1D>(device, kernel, args...)` (numRegs, maxThreadsPerBlock). Run GPU tests
under `compute-sanitizer` on lxplus-gpu, see [[Meta/claude-memory/_history/workflow/vault/lxplus-gpu-interactive|lxplus-gpu-interactive]]. Related:
[[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-morphing-shared-mem-budget|phase2-morphing-shared-mem-budget]], [[Meta/claude-memory/_history/workflow/vault/control-must-be-able-to-falsify-setup|control-must-be-able-to-falsify-setup]].
