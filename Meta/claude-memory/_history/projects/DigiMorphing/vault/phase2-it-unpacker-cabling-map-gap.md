---
name: phase2-it-unpacker-cabling-map-gap
description: "WITHDRAWN: the cabling failure was a MISSING PACKAGE (CondCore/SiPhase2TrackerPlugins), not a map gap; with it the branch runs clean"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T23:02:47.692Z
---

> **WITHDRAWN (2026-09-22).** The conclusion below — that the cabling map lacks
> D112 IT modules — is **WRONG**. The cause was a missing package:
> `git cms-addpkg CondCore/SiPhase2TrackerPlugins`, whose single file does
> `REGISTER_PLUGIN(TrackerDetToDTCELinkCablingMapRcd, TrackerDetToDTCELinkCablingMap)`.
> Without it the `.db` payload has no registered deserializer, so lookups fail with
> "DetId not present in the map" even though the entries exist. Adding that one
> package took the job from "cannot process event 1" to a clean `rc=0` run.
> Si Hyun gave this exact fix to Ian Tomalin on the BES Slack channel
> ("git cms-addpkg CondCore/SiPhase2TrackerPlugins" / "that fixes the crash for me").
> **The control run was right that it was not instrumentation-induced, but both the
> control and the instrumented run were missing the same package.** A control that
> shares your setup error reproduces your error — it isolates the variable you
> changed, not the ones you never had.
> See [[Meta/claude-memory/_history/general/vault/phase2-it-moduleid-measured-in-range|phase2-it-moduleid-measured-in-range]] for what the fixed run measured.

Si Hyun Jeon's Phase-2 IT Alpaka unpacker (`sihyunjeon/cmssw`,
`feature/it_alpaka_tests` @ `3354683874a`) **builds cleanly but cannot process a
single event** of the RelVal its own test cfg is configured to read.
Measured 2026-09-22 on `CMSSW_16_0_0_pre1`, el9_amd64_gcc13, `accelerator=cpu`.

**Stock cfg, no instrumentation** (`Phase2ITUnpackAlpaka_cfg.py accelerator=cpu maxEvents=2`):

```
Begin processing the 1st record. Run 1, Event 9201, LumiSection 93
----- Begin Fatal Exception -----
category: 'TrackerDetToDTCELinkCablingMap has been asked to return
           ModuleInfo for a DetId not present in the map.'
   [2] Calling method for module PixelToBitStreamProducer
Exception Message:  DetId = 303042565
rc=65
```

An instrumented run hit the same root cause one guard earlier, via the
ESProducer's own throw (`Phase2ITModuleMapESProducer.cc:57-58`,
"No ModuleInfo in cabling map for detId 303042581").

**The failure is NOT instrumentation-induced** — that is what the control run
established. It fails in `PixelToBitStreamProducer`, one of the branch's own
modules, on the packing side.

Both detIds decode to `det=1, subdet=1` = **PixelBarrel** (genuine Inner Tracker),
and are only 16 apart — consistent with a contiguous block of IT modules missing
from the map, not one stray entry.

**Likely cause: geometry mismatch.** The cfg loads
`GeometryExtendedRun4D112Reco_cff` (`Phase2ITUnpackAlpaka_cfg.py:61`), while
`ClusteringConstants.h:26` documents D110 ("D110 has 4000 modules"). The shipped
`OTandITDTCCablingMap.db` appears to have been built for a different geometry
than the test configures. NOT yet confirmed — no D110 run attempted.

**Consequence for the study:** the headline `moduleId` range measurement cannot
be taken as configured. The unpacker throws before producing any digi, so there
is no distribution to observe. It also raises a question about the ~7x speedup
claim presented to Tracker DPG 2026-09-02: if this cfg cannot read this RelVal,
those numbers came from a different input, cabling map, or geometry.

**Why:** three sessions spent a long time on the theory that `moduleId` might
exceed its array bound. That may still be true, but it is unobservable on this
configuration — the job dies at the cabling map, well upstream of the clusterizer.

**How to apply:** run the stock cfg as a control BEFORE attributing any runtime
failure to your own instrumentation. Here the instrumented and stock runs failed
at different modules with different detIds, which looked like an instrumentation
artifact until the control showed the same root cause. See
[[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-it-unpacker-base-release|phase2-it-unpacker-base-release]] for the base-release work that got this far.
