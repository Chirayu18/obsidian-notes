---
tags: [index]
status: active
date: 2026-11-05
source: laptop
---

# Full rerun

Status: `hww-analysis` at `0850e51` + `40d0e3e` (unpushed), plus uncommitted review fixes, TRAIN/RUN modes and HZZ ports (worker-reported: 35/35 and 49 tests); three smoke runs pass. How to run: [[Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run]]. Run A not submitted; Run B stitching not implemented.
Validation: [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun|TRAIN/RUN review]] reports 49/49 tests but reproduces Condor output, data handling and card-building blockers; no end-to-end production validation. Scientific claims remain agent-reported.
Needs Chirayu: signal PDF/αS (H+c has no αS members), lepton-SF question for Thomas and MVA retraining, muon RNG/CPUs, EOS space, one mH for all Higgs xsecs (125.00 vs 125.09); submission needs separate approval.

Latest audit: [[Projects/HToWW/2026-11-05-status-audit-retraining|MVA retraining, negrw checks and open-item dependencies]]. The audit reports 4/5 re-NANO datasets complete in DAS and the fifth near completion as of 13:57 CET; output PDF-member content is not yet checked.

Progress deck r6 (includes both audits): [open](deck/index.html) · [[Projects/HToWW/samples-and-production/full-rerun/deck/CHANGELOG|changes]] · [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|independent review]].
Route B (3FS+4FS stitching) is parked by Chirayu: proposal only, not live; to be compared with Run A later. 3FS PDF weights: re-NANO with LHA 321900 submitted 2026-11-05, pending ([[Projects/HToWW/samples-and-production/2026-11-05-3fs-renano-pdf321900|re-NANO note]]; [[Projects/HToWW/2026-11-05-route-b-stitching-implementation|proposal]]).

## Records

- [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|Current Run A / Run B state (current summary at top; earlier snapshot labelled)]]
- [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|Independent review of the unpushed work, 2026-11-05]]
- [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-hb-yukawa-fix-crosscheck|H+b Yukawa scale-fix cross-check]]
- [[Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings|Earlier plan, methods and dated findings]]
- [[Projects/HToWW/samples-and-production/full-rerun/2026-10-06-independent-review|Earlier independent audit and its evidence]]
- [[Projects/HToWW/samples-and-production/full-rerun/2026-10-13-GEN-ticket-draft-HplusC-HplusB-WW|Generator ticket draft]]

Related sample production and flavour-scheme work remains in the [[Projects/HToWW/samples-and-production/README|parent index]].

![[Projects/HToWW/samples-and-production/full-rerun/deck/full-rerun_r6.pdf]]
