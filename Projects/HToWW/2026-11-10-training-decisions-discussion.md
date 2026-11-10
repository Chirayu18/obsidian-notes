---
tags: [reference, decision]
status: active
date: 2026-11-10
source: laptop
---

# Training decisions from the HToWW discussion, 10 November 2026

## Chirayu's exact wording

> NO no the current train and scoring scheme is fine. Class weights only is fine. FOr that part I think the ReNano of the 3FS samples should have been done bu now. Explain more the issue. Use the best you think as of now. Make reproduceable. Explain. Use the current folder no, and higgs mass, use 125.09 conventions everythere , also explain.

This follows his clarification request about decisions before full training. The previous concern about using full RUN events is resolved by accepting the existing scheme: all selected RUN events contribute, each scored by the model that held out its fold.

## Confirmed decisions and interpretation

- Keep the current five-fold training/scoring scheme. Outer test fold is event % 5; b-hive owns internal validation within the other four folds. All selected RUN events contribute to templates.
- Keep class weights only in the present b-hive 2dcats training; do not add physics/event weights to the training loss.
- Require reproducibility. Intended implementation includes event-deterministic muon randomness and a seeded, recorded b-hive internal validation split. Neither has been implemented or tested in this discussion.
- Keep the current output folder. Interpretation: retain the existing default output root `/eos/user/c/cgupta/higgscharm`, with the mode-specific directories already described in the runbook. This is not a new space measurement, permission to overwrite outputs or permission to delete data. Distinct run versions remain necessary.
- Adopt mH = 125.09 GeV conventions for all Higgs normalisations. Preserve the prior NNLO H+c choice. Re-derive production cross sections and decay branching fractions consistently for every Higgs process; do not apply one common factor to every process. This normalisation convention does not change the mass used to generate existing events.
- Chirayu delegates remaining suitable technical defaults with “Use the best you think as of now.” This does not resolve missing calibration provenance or provide numerical theory uncertainties without evidence.

## Discussion partner's selected direction under delegated judgment

These are recommendations/defaults selected for future implementation, distinguished from Chirayu's explicit choices above:

- Signal PDF/alphaS: prefer explicit, sourced inclusive cross-section uncertainties with consistently defined shape-only residuals, avoiding double counting. Supply a justified alphaS normalisation uncertainty where event-level alphaS members are absent. No numerical uncertainty is selected here; the appropriate process/flavour-scheme source and the residual-shape construction must be checked before implementation. Do not substitute 3FS replicas for the 4FS uncertainty or invent absent alphaS shapes.
- Empty object-shift template: prefer stop-and-review for an evaluated shift that becomes empty at the final template level; explicit, justified not-applicable declarations remain separate. This avoids silently replacing a real migration with nominal. No code/config change made.
- Model validity: fingerprint the external inputs that determine selection, features or training construction, including the recorded negrw/calibration inputs. Preserve separate provenance for template-only normalisation/uncertainty settings so that a pure rate convention need not unnecessarily force retraining. A dependency audit and current signature constraints still need review; do not weaken existing guards by assumption.
- CPU allocation: match the existing two processing workers with two requested CPUs, and record software versions, seeds, input-list hashes, code state and model/config hashes. This is a proposed resource setting, not a submission.
- Lepton SFs and c-tag: retain adopted working points while obtaining the missing denominator/calibration provenance. Do not drop or multiply SF components, change category edges or fill placeholder cells by guesswork. Unresolved provenance/validation remains a pre-production gate.

## Why 3FS re-NANO does not close the current signal uncertainty issue

The re-NANO recovers the missing 321900 PDF weight group from private 3FS MiniAOD into NanoAOD. The saved local test reported 101 members. The latest completion evidence read in this discussion is the 5 November audit: four of five datasets complete and the fifth at about 99%; it does not establish completion on 10 November or validate production-output PDF contents. No fresh DAS/CRAB or ROOT-file check was made here.

Run A remains 4FS-only; Route B is parked. The central 4FS H+c sample already has 101 PDF members (325500), but lacks alphaS members. Separately, the current per-member normalisation removes inclusive member-rate changes. Recovering 3FS PDF replicas does not supply the missing 4FS alphaS pair and does not decide how to separate inclusive and shape uncertainties. H+b's normalisation issue must also be treated on its own evidence.

## Evidence and boundaries

- [[Projects/HToWW/framework/2026-11-05-trainrun-blocker-fixes]]: validation ownership, class-only training, current output-root default, remaining policies and saved synthetic checks.
- [[Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run]]: TRAIN/RUN flow and held-out model assignment.
- [[Projects/HToWW/2026-11-05-status-audit-retraining]]: 5 November DAS counts, SF/c-tag/JEC/negrw gates, Higgs-mass inconsistency and historical space estimate.
- [[Projects/HToWW/2026-11-05-sol-review-unpushed-work]]: PDF/alphaS findings and sourced Higgs branching-fraction conventions. The recorded BR(H to WW) changes from 0.2137 at 125.00 GeV to 0.2152 at 125.09 GeV, about +0.7%; this is a branching-fraction comparison, not a universal cross-section rescaling.
- [[Projects/HToWW/samples-and-production/2026-11-05-3fs-renano-pdf321900]]: re-NANO purpose, local test and submitted tasks.

Only this decision note was written. No analysis code edits, remote checks, workers, training, job submission, credential/service changes, data deletion or push occurred. Existing dirty vault setup files were preserved. The implementation remains agent-reported pending independent review and real-processing validation. This discussion does not establish production readiness or launch authorisation.
