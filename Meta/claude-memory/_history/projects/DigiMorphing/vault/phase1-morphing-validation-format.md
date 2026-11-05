---
name: phase1-morphing-validation-format
description: Phase-1 HLT digi morphing PRs and validation decks people have seen; Phase-2 talks must mirror their plots
metadata:
  type: reference
---

The user's Phase-1 HLT digi morphing work is cms-sw/cmssw#48734 (merged Sep 2025) and the race-condition fix with
the 2-buffer scheme, #49991 (merged Feb 2026; backport #50045). Earlier #48342/#48343 ("Pixelimage morphing") were
superseded.

Validation decks the tracker community has already seen:
- #49991 PR body: `_Validation_PR.pdf` (github user-attachments 24969377). It shows the count difference between
  old and new, cluster size (without, with, overlapped, difference), event displays, and a fake-digi table
  (FakeDigisPerEvent, PerModule, ModulesWithFakeDigis, NFakeDigisBarrel, Layer1-4).
- H. Petersen et al., Tracker DPG meeting 13 Aug 2025, Indico 1567986, the HLT_digi_morphing_validation.pdf linked
  from #48734. It shows RecHit vs SimHit position, resolution, error and pull in a muon gun, central and forward,
  baseline vs target.

**Why:** the user asked that Phase-2 morphing slides mirror these plots, because people have already seen them.
**How to apply:** for any morphing validation talk, show the same quantities in the same order first, then add
the new checks. Related: [[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-morphing-shared-mem-budget|phase2-morphing-shared-mem-budget]].
