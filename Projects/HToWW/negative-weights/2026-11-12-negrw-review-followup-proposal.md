---
tags: [reference, review]
status: active
date: 2026-11-12
source: laptop
evidence: proposal
---

# negrw acceptance follow-up: concrete changes awaiting authorization

Completed review: [[Projects/HToWW/negative-weights/2026-11-12-negrw-v2-acceptance-review]], reviewer commit03f8a7d. Parent read the full note. Recommendation is hold the switch, not reject v2. Neither July nor v2 is shape-validated for the final fit observable. There is no current mixed-model production identified. Existing production model/config stays unchanged.

## Proposed bounded implementation

1. **G1: freeze model input provenance.** Preserve original frozen `condor/hww_genrw_train_v2_model/train_v2.parquet`, hash f603ef6de8f30dc873615eddadba63684ebd64fc0e0b7c830a8e19213e7cc412, and reviewer `~/negrw_review_20261112/resume_input_manifest.json` (377chunks,7595624rows). Store a verified frozen copy and immutable metadata sidecar by the EOS v2 model. Preserve model binary SHAaf53567ccfeddeef94c1fa62b3a6ed3c1285937919ced3f7705c565b819155cb, no overwrite/deletion and no large binaries in git.
2. **G2: identify actual model in RUN.** Minimal changes to RUN provenance in `analysis/processors/base.py` and the relevant loader/merge guard in `scripts/combine/build_cards_from_templates.py` as needed: record the SHA256 of the negrw model actually consumed, reject mixed model identities and missing required identity at the RUN boundary. Do not put weight-only negrw back into TRAIN selection/features hashes. Demonstrate compatible/mixed/missing-identity cases and unchanged A/B TRAIN hashes. Preserve the b-hive owner's `scripts/mva/*` edits. No workflow/model switch.
3. **Validation-statistic correction.** Correct `scripts/negrw/negrw_train_v2.py::closure` uncertainty to include numerator/denominator covariance; correct affected plotting/reporting with the reviewed fitted-normalization shape covariance. Preserve old artifacts, create versioned corrected reports, and test formulae with bounded independent toys. No training-recipe change, extra nuisance or fit acceptance criterion invented.

Acceptance for this engineering work: input artifact identities pinned and copied with verified hashes; mixed-model synthetic RUN merge rejected while compatible records merge; missing-identity behavior explicit; old TRAIN input hashes unaffected; corrected uncertainty tests pass; existing model/config and user physics decisions unchanged. Full G3 remains open after these changes.

**G3:** once scored SR V+jets outputs exist, quantify closure in the actual final channels/fit bins with shared-event/fitted-normalization covariance and compare to the current nuisance and template MC statistics. This is pending data/model-pipeline readiness. No new bias prescription or model acceptance follows from closing G1/G2.

## Automatic approval review rejection

Parent attempted one fresh c1 Opus implementation delegation after the completed review. It was rejected before a child was launched. The returned reason was that the worker would modify RUN/merge analysis code and write provenance artifacts, whereas the applicable user instruction authorized continuing jobs rather than new analysis-code edits. The parent did not retry through another tool/account or perform the changes itself.

This is an approval-scope block, not a scientific rejection of the proposed guard or a claim that a new model has been installed. Ask Chirayu explicitly to authorize the concrete G1/G2/reporting changes above before launching that implementation task. The already-authorized A/B job recovery and b-hive continuation were not interrupted. No new schedule was created. Only this proposal note is committed locally, no push.
