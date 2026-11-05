---
name: phase2-it-watchruns-not-a-crash
description: "MEASURED: edm::stream producers DO get beginRun called without the WatchRuns marker -- the reported null-deref does not exist"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T23:18:07.151Z
---

Ian Tomalin reported (BES Slack, 2026-09-19) that the Phase-2 IT+OT unpackers'
EDProducers "are using beginRun(), but they were not declared with the
WatchRuns template parameter, so this function will never be called." A code
review escalated that to a null `unique_ptr` dereference, since `slinkMap_` is
assigned only in `beginRun` and dereferenced unconditionally in `produce`.

**Measured 2026-09-22 (CMSSW_16_0_0_pre1, CPU, 2 events, fprintf at the top of
each `beginRun`): it is entered in all three producers.**

```
PROBE_IN_BINARY=3
WATCHRUNS_PROBE BitStreamToRawProducer one_HAS_WatchRuns    ENTERED   <- control
WATCHRUNS_PROBE RawToBitStreamProducer stream_NO_WatchRuns  ENTERED
WATCHRUNS_PROBE RawToPixelProducer     stream_NO_WatchRuns  ENTERED
TOTAL: legacy 1021985, soa 1021985, only-legacy 0, only-soa 0     rc=0
```

**Mechanism** (verified in `FWCore/Framework/interface/stream/implementors.h:305-314`):
`WatchRuns` is an **empty marker class** — its `beginRun` signature is a
commented-out line, so there is no virtual to dispatch through. For
`edm::stream` modules the framework calls `beginRun` regardless; the marker
governs synchronisation/ordering, not invocation.

**Unchecked:** whether the same holds for `edm::one` modules, where semantics
may genuinely differ. If the original OT report concerned `one::` producers it
may still stand there — worth asking which was tested.

**Still worth fixing, but as hygiene:** two `edm::stream::EDProducer<>` classes
override `beginRun` without declaring `WatchRuns` while a third `edm::one::`
producer declares it correctly. Relying on an empty marker's incidental
behaviour is fragile. It is a maintainability defect, **not** a crash.

**Why:** a declaration-level reading said "never called"; it was reasonable and
it was wrong. The same session retired two other source-read findings the same
way — see [[Meta/claude-memory/_history/general/vault/phase2-it-moduleid-measured-in-range|phase2-it-moduleid-measured-in-range]].

**How to apply:** when a framework-contract claim rests on a template parameter
or marker type, read the marker's definition before concluding what it enforces,
then measure. See [[Meta/claude-memory/_history/workflow/vault/control-must-be-able-to-falsify-setup|control-must-be-able-to-falsify-setup]] for the probe
methodology — the first two attempts produced false negatives that looked like
confirmation.
