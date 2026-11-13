---
tags: [reference, presentation, decision]
status: active
date: 2026-11-13
source: laptop
---

# Explicit NNLO normalization statement for the November slides

Chirayu, 2026-11-13: **“Tell that also to keeper to explicityly add that to the slides that now we use NNLO xs”**.

Keeper slide action: explicitly state **“Both A and B now use the NNLO H+c cross-section normalization.”** The adopted signal cross section including the configured decay branching fractions is **0.0016626 pb**. A uses the 4FS central sample; B normalizes the combined complementary 4FS/3FS stitched prediction to this same total, rather than assigning the full total independently to each component. This is a normalization statement, not a claim that the event samples or all differential distributions have NNLO accuracy.

Sources: [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train]] and [[Projects/HToWW/samples-and-production/2026-11-05-br-hww-xsec-check]]. Implementation status here follows the recorded source inspection; a fresh SSH check in this discussion failed on local SSH configuration permissions, so no fresh remote validation is claimed.

For comparison with historical limits, show the reference convention explicitly. The former NLO value was 0.0022141 pb; the adopted NNLO value is approximately 0.7509 times it. With otherwise identical templates, this normalization change alone raises the numerical limit on signal strength r by approximately 33.2%. Today's A stat-only median 493.1641 would correspond to approximately 370.3 on the former NLO reference. This is a reference conversion, not a measured attribution of the old/new sensitivity difference. The user recalled an earlier 385; the located October record instead gives 338.5 stat-only. Do not label either comparison as controlled until the exact earlier result and settings are identified.

Current actual A result: [[Projects/HToWW/framework/2026-11-13-a-limit-plots]] (493.1641 statistical model; 505.3711 with configured rates; both merged SR, not full systematics). This result supersedes the “no new numerical A/B limit estimate is available yet” availability statement in [[2026-11-13-ab-physics-comparison-slide-decision]] for A; B remains pending. The physics interpretation boundaries in that note remain applicable.

This ordinary note is the keeper handoff; no keeper-owned deck files were edited.
