---
name: lxplus-gpu-profiling-and-racecheck
description: lxplus905 nsys/ncu are stubs (no profiler), cvmfs NsightSystems is 2021; time via FastTimerService + CUDA_LAUNCH_BLOCKING; racecheck finalize/prefixScan hazard pre-exists in master
metadata:
  type: reference
---

Measured 2026-10-29 on lxplus905 (Tesla T4), CMSSW_20_1_X IB with CUDA 13.4.

**No working profiler.** `/usr/local/cuda*/bin/nsys` fails with "Nsight Systems 2026.1.3 hasn't been installed with CUDA Toolkit 13.3". The NsightSystems on `/cvmfs/sft.cern.ch/lcg/releases` is the 2021 version, too old for CUDA 13. For module-level GPU timing, use the FastTimerService JSON (`writeJSONSummary`) with `CUDA_LAUNCH_BLOCKING=1`, 1 thread. The resolution is about 0.4 ms/event for the Phase-2 clusterizer, whose time is dominated by host-to-device copies.

**compute-sanitizer is in the CMSSW cuda external** (`scram tool info cuda` → CUDA_BASE/bin). Racecheck on any FindClus reports a hazard between `OneToManyAssoc.h:229` (an assert in `finalize`) and `prefixScan.h:37`. It is present in master too, so a control run is needed before blaming new code. See [[Meta/claude-memory/_history/workflow/vault/control-must-be-able-to-falsify-setup|control-must-be-able-to-falsify-setup]] and [[Meta/claude-memory/_history/projects/DigiMorphing/vault/alpaka-kernel-resources-measure|alpaka-kernel-resources-measure]].

**Why it matters:** synccheck plus racecheck on a unit test with edge-case modules found a real Phase-2 morphing race (a thread leaving the strip loop after skipping the last strip clears `hist.off` while others still read it). The 400k module-event PU200 comparison had missed it.

**How to apply:** for any block-level loop with a uniform `continue`, run synccheck on inputs where the *last* iteration is skipped.
