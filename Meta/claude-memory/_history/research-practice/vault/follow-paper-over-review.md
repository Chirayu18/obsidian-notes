---
name: follow-paper-over-review
description: "When applying slide-review fixes, the paper is the authority; a review finding that conflicts with the paper's own wording loses"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 44979bb5-dbf6-44f6-80e6-8765822550fa
  modified: 2026-10-16T09:42:55.520Z
---

When applying fixes from a slide review (cern-slides output) and a finding conflicts with the source paper (figure legend, table label, caption), follow the paper, not the review. Check the paper text before applying any wording-level finding.

**Why:** On the Higgs 2026 deck (2026-10-16) the review told me to caption HIG-25-003 Fig. 8's red curve as "|κV| ≤ 1"; the figure legend says |κZ = κW| ≤ 1 and the paper's Table 3 numbers come from a different (no custodial symmetry) configuration. Chirayu: "follow the paper not the review".

**How to apply:** grep the arXiv full text for the exact label/assumption before editing; when figure and table configurations differ, say so in the caption rather than merging them. Related: [[Meta/claude-memory/_history/projects/HToWW/vault/an-review-verify-against-source|an-review-verify-against-source]], [[Meta/claude-memory/_history/general/vault/review-findings-phrasing|review-findings-phrasing]].
