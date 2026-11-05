---
tags: [index]
status: active
date: 2026-11-05
source: laptop
---

# framework

Analysis runbook, optimization and captured framework documentation.

Status: TRAIN/RUN and the HZZ ports remain uncommitted; the independent review reproduced production blockers. Speed-up patches 01–04 are recorded in analysis commit `40d0e3e`.
Validation: [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun|Review]] records 49/49 unit tests and integration reproducers; no end-to-end production validation. Findings remain agent-reported.
Needs Chirayu: authorise analysis-owner fixes and choose an output root; physics/training dependencies are in the [[Projects/HToWW/2026-11-05-status-audit-retraining|status audit]].

Organization and links were checked by the keeper. This does not independently validate scientific claims in the source notes.

- [[Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run|How to run the framework: legacy, TRAIN, RUN (current)]]

## Records

- [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun|Independent TRAIN/RUN review: integration blockers, schemas and test evidence]] — not ready for production; fixes require analysis-owner authorisation.
- [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|Adopted HToWW correctness-review protocol]]
- [[Projects/HToWW/framework/review/htoww-review/SKILL|HToWW review skill]] — domain review criteria, not additional execution authority.
- [[Projects/HToWW/framework/2026-11-05-jfc-code-survey|JFC code inspection, useful practices and adoption limits]]
- [[Projects/HToWW/framework/2026-11-05-saranya-hczz-branch-comparison|Saranya HcZZ comparison and recorded follow-ups]]
- [[Projects/HToWW/framework/optimization/2026-11-05-speedup-patches|Speed-up proposals, checks and later application]]
- [[Projects/HToWW/framework/2026-07-24-run-analysis-steps|(superseded) HToWW H+c — run the whole analysis (with negrw + native 2D c-tag SF)]]
- [[Projects/HToWW/framework/optimization/2026-10-08-framework-optimization-plan|higgscharm framework: final fixes and re-architecture plan (2026-10-08)]]
- [[Projects/HToWW/framework/optimization/deck/2026-10-09-framework-plan-deck|higgscharm framework: the next plan]]

## Existing decks and documents

- [[Projects/HToWW/framework/optimization/deck/2026-10-09-framework-plan-deck.pdf|2026-10-09-framework-plan-deck.pdf]]

## Keeper framework deck

Three-slide review: [open](deck/index.html) · [[Projects/HToWW/framework/deck/CHANGELOG|changes]]. This covers framework-core modes and integration; the existing optimization deck stays with its own workstream.

![[Projects/HToWW/framework/deck/framework_r1.pdf]]
