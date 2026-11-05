---
name: review-read-the-branch-not-head
description: "When reviewing a feature branch, read every cited file with `git show BRANCH:path` and diff it first — HEAD's line numbers AND constant values both drift"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 91388281-cecf-4de2-8f19-6b5975a2a1c0
  modified: 2026-09-21T22:26:08.964Z
---

Reviewing Si Hyun's `feature/it_alpaka_tests` in Sept 2026, I twice sourced claims
from the **stock release** file instead of the branch copy, and both reached a
committed review under someone else's name.

1. Cited `PixelClustering.h:327` as the assert bounding `moduleId`. On the branch
   the guards are `:164` and `:212`; the files differ by 275 lines.
2. Worse: asserted `SimplePixelTopology.h` and `ClusteringConstants.h` were
   "unmodified by the branch, so the line numbers should be safe". They are not —
   462 lines changed, 356 deletions. On the branch there is **no `Phase2OT`, no
   `nModulesTot`, no 6872**; `numberOfModules = 4000` and `maxNumModules = 5000`.
   My entire opening finding ("two traits structs disagree, 4000 vs 6872, the
   slide is half right") described a tree the author never touched. The slide was
   correct on its own base, and the finding was withdrawn.

**Why:** the checkout is sparse (see [[Meta/claude-memory/_history/workflow/vault/lxplus-cmssw-build-location|lxplus-cmssw-build-location]]), so reading
via `git show HEAD:path` *works* and returns plausible, well-formed code — there
is no error to alert you. The failure is silent. And the partial instinct is the
trap: I did think "diff before quoting line numbers" but exempted **values**, as
if constants were more stable than coordinates. On a branch rewriting 356 lines of
a topology header, constants are exactly what moved.

**How to apply:** when reviewing any branch, before quoting a file — number *or*
value — run `git diff --stat HEAD <branch> -- <path>`. If it appears at all, read
it with `git show <branch>:<path>` and re-derive everything. State which tree a
finding came from when handing it to someone else; a peer who propagates your
numbers cannot check a provenance you never gave them. Related:
[[Meta/claude-memory/_history/projects/HToWW/vault/an-review-verify-against-source|an-review-verify-against-source]].

**In the writeup, add a standing note** naming the tree citations are relative to.
Both errors above were already committed when caught, and a reader checking `:327`
in *either* tree finds something that is not an assert — from which the reasonable
conclusion is that the whole finding was invented. The note is what keeps a
corrected review credible.
