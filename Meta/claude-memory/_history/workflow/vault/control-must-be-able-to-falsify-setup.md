---
name: control-must-be-able-to-falsify-setup
description: A control that can only confirm your hypothesis is not a control -- pick one that MUST produce output if the instrument works
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T23:17:54.426Z
---

When measuring whether something happens, the control has to be able to prove
the **instrument** works, not just the subject. Learned the hard way twice in
one session, 2026-09-22.

**Case 1 — the control shared my setup error.** A CMSSW job failed with "DetId
not present in the map". I ran the stock config without my instrumentation as a
control; it failed identically, so I concluded the defect was real and reported
it. Both runs were missing the same package
(`CondCore/SiPhase2TrackerPlugins`, which REGISTERs the cabling deserializer).
**A control isolates the variable you changed, not the ones you never had.**

**Case 2 — the failure mode looked like confirmation.** Testing whether
`beginRun` is called on producers lacking the `WatchRuns` marker, I added
`fprintf` probes. Twice they produced no output — which reads exactly like
"the function is never called", i.e. confirmation of the suspected bug. Both
times the instrument was broken: once `scram b` silently rebuilt nothing (and I
had truncated its output), once shell escaping through nested heredocs mangled
the injection so it never compiled and the stale `.so` ran.

What saved it: the control was a *third* producer that declares the marker
**correctly**, so it MUST print if the probes work. Its silence proved the
instrument was dead rather than the subject. The third run was only trusted
because a `PROBE_IN_BINARY=3` check ran *before* the job started.

**Why:** a null result is evidence for "it never happens" and evidence for "my
measurement is broken", and those are indistinguishable without a positive
control. When the broken-instrument case and the hypothesis-true case produce
the same output, silence will be read as confirmation every time.

**How to apply:**
- Pick a control that must produce *positive* output when the setup is sound,
  not merely one that should fail the same way.
- Verify the instrument reached the binary before trusting a null result
  (`strings <lib> | grep -c PROBE`), and never truncate build output when the
  build is the thing that might have silently done nothing.
- Inject instrumentation from a file, not through nested shell heredocs.
- Applies to whatever the [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]]-style pipelines do too: if a
  stage can silently no-op, an empty result is not a measurement.
