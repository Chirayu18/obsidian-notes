---
tags: [reference, review]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# negrw v2 acceptance review: interrupted handoff, not an acceptance

The bounded c1 Opus review stopped at its five-hour account limit on 12 November ~02:06 CET. Native notice: reset at **05:00 Europe/Brussels**. No replacement or account fallback was started before the reset. There is no completed acceptance recommendation or reviewer note from the child.

The new model remains **not adopted**. Existing model/configuration is unchanged; neither the old nor new model is declared shape-validated by this handoff. Author claims in [[Projects/HToWW/negative-weights/2026-11-12-negrw-retraining]] remain agent-reported and have not been promoted to independent validation.

## Review scope and saved state

The assigned task was a read-only acceptance review under [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol]] and the htoww-review skill, not retraining or a production/config change. Original training and saved artifacts are linked in the worker note.

Review thread: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3Ac185fc50-2415-4b0f-b864-f696a60303be%3Adelegate-task%3A3c30e37a-be89-4cf4-9f19-acf37854cb40>.

Parent recovered its native source reads and executed diagnostic output through activity position75 after the failure. The child made no accepted model switch. No analysis/config/model edits were authorized by its review brief.

Saved reviewer scratch on lxplus: `~/negrw_review_20261112/`, including `shape_after_renorm.py` and `shape_after_renorm_out.json`. The final numerical command completed before rate limiting; do not rerun it blindly. Inspect saved output and the full preceding activity before planning the remaining work.

## Partial observations: not final reviewed findings

| item | partial evidence | remaining check / boundary |
|---|---|---|
| Approved per-sample normalization | Reviewer followed both RUN and legacy paths, including object/weight variations, and reported per-(era,dataset) normalization across selected channels | Complete prescription-to-output evidence table; no broad physics acceptance follows from restoring totals |
| negrw model identity in RUN | Reviewer source reads found SHA256 in `external_inputs(cfg)['weights']`, recorded at fold registration, but not in the RUN output provenance shown in `base.py` | Candidate guard gap: establish actual consumers and demonstrate whether mixing chunks scored with different models can pass. Do not call it reproduced yet |
| Partial training inputs | Worker used complete chunks from two jobs that failed later on XRootD expiry | Review exact shard manifest, reproducibility, duplicate prevention and representative-sample assumptions; completeness of every intended input is not automatically required for an intentionally sampled training set |
| Shape residual diagnostic | Reviewer executed `shape_after_renorm.py` on held-out rows, comparing reweighted-vs-signed distributions and negrw Up variation | Diagnostic normalizes within the displayed variable range and treats the fitted normalization as fixed in its per-bin variance. Check these choices and covariance before using pulls/chi2 as an acceptance statistic or claiming a discrepancy significance |
| Support / overlap | Worker supplied marginal min/max and event-number-plus-kinematics diagnostics | Finish assessment of actual physical identity, lepton/veto construction, shifted selections and joint/conditional support; marginal range inclusion is insufficient for a blanket no-extrapolation claim |

Do not treat the interrupted review's tentative source comments or raw numerical output as final findings. In particular, adding reconstructed dilepton mass to a mostly pairless generator-only training region is not an approved fix; any feature/sample-conditioning change needs a separate justified prescription.

## Resume after quota availability

Start a **new** bounded c1 Opus review task (fresh delegate, prior brief/findings/objections), per orchestration rules. Read the failed review thread and saved scratch first. Do not send a fresh re-check to the old thread, duplicate author unit tests on unchanged code, or start full jobs/retraining. Check whether the saved diagnostics support the approved normalization and statistical model, then finish a clear adopt/hold/reject recommendation with evidence and unresolved gates. The current model stays unchanged pending that result.

Routine grid monitoring can continue on the parent; it is independent of this review pause. No permission to delete scratch or replace models is inferred. This handoff note is committed locally only, with no push.


## Automatic resumption was not scheduled

Parent attempted a 05:05 fixed-time schedule whose prompt would disable itself on its first run. Automatic approval review rejected it: fixed-time schedules may recur and could create persistent unattended delegate/commit actions without explicit user authorization. **No new resumption schedule was created.** Do not work around that rejection through a different scheduler or the existing grid monitor. Existing grid monitoring remains read-only and active. A review-resumption schedule now needs explicit approval; manual review continuation after c1 availability remains possible on a new applicable request.
