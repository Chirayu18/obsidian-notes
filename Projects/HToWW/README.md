---
tags: [index]
status: active
date: 2026-11-05
source: laptop
---

# HToWW

Status: [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|Independent review]] reports two tested fixes on top of analysis commits `0850e51` and `40d0e3e`; Run A is not submitted and Run B stitching is not implemented.
Validation: The review reports 35/35 tests and single-file smoke checks; this establishes their software-check boundary, not a production or physics validation. Results remain agent-reported.
Needs Chirayu: signal PDF/αS prescription, lepton-SF provenance and retraining, reproducibility/CPU choices and output space; see the [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|current handoff]]. NNLO, lepton working points and the Run B radius/acceptance are already recorded decisions.

## Workstreams

- [[Projects/HToWW/analysis-strategy/README|analysis-strategy]]: Sensitivity strategy, precedent, systematics audits and measured card changes.
- [[Projects/HToWW/combine-systematics/README|combine-systematics]]: Statistical model, MC statistics, nuisance inventory and limit diagnostics.
- [[Projects/HToWW/selection-and-mva/README|selection-and-mva]]: Selections, lepton/c-tag calibration, MVA loss, acceptance and closure studies.
- [[Projects/HToWW/negative-weights/README|negative-weights]]: Generator-level reweighting, algebra, training and closure decisions.
- [[Projects/HToWW/samples-and-production/README|samples-and-production]]: Background replacements, signal production, gridpacks, flavour schemes and full reruns.
- [[Projects/HToWW/framework/README|framework]]: Analysis runbook, optimization and captured framework documentation.
- [[Projects/HToWW/analysis-note/README|analysis-note]]: Analysis-note writing, review and author tasks.
- [[Projects/HToWW/talks/README|talks]]: Analysis overview, Athens talk and historical c-tag/negrw presentations.

## Shared records

- [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun|TRAIN/RUN code review: reproduced Condor, data and card-building blockers]] — 49 tests pass but do not cover these integration paths; analysis code unchanged.
- [[Projects/HToWW/2026-11-05-status-audit-retraining|Status audit: MVA retraining, negrw overlap risk and open-item dependencies]] (agent-reported; code review complete below)
- [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|Independent review of the unpushed full-fix work]]
- [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|Adopted review protocol and evidence requirements]]
- [[Projects/HToWW/links|HToWW — links]]
- [[Projects/HToWW/plots|HToWW — plots]]

Combine-assistant work: [[Projects/CombineAgent/README|CombineAgent]].
