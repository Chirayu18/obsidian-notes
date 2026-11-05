---
name: review-findings-phrasing
description: "Phrase a code-review finding so a reviewer checking current behaviour can't dismiss it — claim the narrowest thing that stays true, and report cleared leads as plainly as hits"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 91388281-cecf-4de2-8f19-6b5975a2a1c0
  modified: 2026-09-21T23:37:21.657Z
---

From the Phase-2 IT unpacker review (Sept 2026), two phrasing rules that each
saved a finding:

**1. Claim the narrowest version that survives a spot check.** A finding was
written as "the defaults for `handleGapPixels` disagree across components."
True, but a reviewer who checks today's behaviour finds it *correct* (both
values collapse to the same bool downstream) and then dismisses the whole item.
The durable claim was "the decoder cannot express a mode the encoder supports" —
still true today, and it states the actual structural gap. Say explicitly when
current behaviour is fine and confine the risk to what would break it.

**2. One counter-example refutes a universal.** Another finding claimed indices
were "unvalidated throughout." One CPU-side function (`ChipModuleMap::chipIndex`)
validated both of its indices and threw — which would have let a reader discard
the whole finding. The narrow version was both true and *stronger*: every
unvalidated index was on the ported GPU path, so the real claim is "the port
drops validation the reference performs." Before writing "throughout" / "never"
/ "any", go looking for the one place that does it right.

**Why:** a review's job is to survive a skeptical reader, not to sound severe.
An overreaching claim doesn't fail gracefully — it discredits the specific,
correct evidence underneath it.

**How to apply:** when handing findings to someone who will publish them, grade
your own confidence and say which claim would collapse under which check. Report
leads that came back clean as plainly as the hits — in that review, two cleared
items killed hypotheses the lead was hoping would pay off, and stating so
plainly is what kept the rest trustworthy. Related:
[[Meta/claude-memory/_history/general/vault/review-read-the-branch-not-head|review-read-the-branch-not-head]], [[Meta/claude-memory/_history/projects/HToWW/vault/an-review-verify-against-source|an-review-verify-against-source]].
