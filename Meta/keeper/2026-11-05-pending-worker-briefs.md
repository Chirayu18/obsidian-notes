---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---

# Pending worker briefs (2026-11-05): HToWW status audit and code review

> Completed through Chirayu-authorised Claude subagents on 2026-11-05. Results: [[Projects/HToWW/2026-11-05-status-audit-retraining]] and [[Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun]]. Briefs below are retained as the original assignment; do not relaunch them. Analysis code was not changed.

Chirayu asked the keeper to launch two Claude Code agents as top-level threads. Every launch attempt (`t3_thread_launch` ×2, `create_threads` ×1) failed with the T3 error `parent_not_active` ("The calling provider no longer owns an active thread run"). Neither thread exists. Paste each brief below into a new top-level thread to start it.

## Brief 1 — HToWW · status audit vs slides, open items, retraining (read-only)

You are a WORKER (vault CLAUDE.md is your standing instruction). Task from Chirayu, 2026-11-05: check the HToWW status as stated on the internal slides against reality, look closely at every open item, and find things we have NOT considered.

Start from:
- Deck: `Projects/HToWW/samples-and-production/full-rerun/deck/index.html` (r5, 8 slides; read the HTML sections, especially `status`, `result-pdf-alphas`, `result-routeb`, `open` and `backup-sources`).
- Notes:
  - `Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state.md` (current-state box at the top);
  - `Projects/HToWW/2026-11-05-sol-review-unpushed-work.md` (findings table and "Needs Chirayu");
  - `Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run.md`;
  - `Projects/HToWW/2026-11-05-route-b-stitching-implementation.md`;
  - `Projects/HToWW/samples-and-production/2026-11-05-3fs-renano-pdf321900.md`.
- Use `scripts/rag/vault-search` for older context (negrw, v11 MVA, training region, b-hive, fakes, tt CR).
- Repo (read-only): `ssh lxplus`, `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis` (HEAD `40d0e3e` plus the uncommitted TRAIN/RUN work).

Questions:
1. **Event MVA (v11, `hwwcom_multiclass_v11_2dcats`):** does it need retraining? Chirayu thinks yes, because of the new lepton working points AND the changed signal (running-Yukawa scale fix, NNLO normalisation, other full-fix changes). Confirm or refute with evidence: what it was trained on vs what changed.
2. **negrw** (`negrw_models.joblib`, `base.py::_score_negrw`, the `negrw:` block in the workflow): does it need retraining? Check its training region, selection, samples and features against the full-fix changes (leptons, JEC/MET, jet veto, jet re-sort, trigger, etc.).
3. **Open items, closely:** for EACH open item on the slides and in the notes, give:
   - its current real state;
   - what exactly is needed to close it;
   - who must act (Chirayu, Thomas or an agent);
   - whether it blocks Run A;
   - any hidden dependency on other items.

   The items include at least:
   - the signal PDF/αS prescription (H+c has no αS members);
   - lepton-SF factorisation (the question for Thomas);
   - event-MVA retraining;
   - muon RNG seeding and CPUs per job;
   - EOS space (~81 GB free vs ~266 GB needed; nothing may be removed from EOS, so a new output location is needed);
   - one mH for all Higgs cross sections (125.00 vs 125.09);
   - committing the uncommitted code;
   - silent nominal fallbacks in `make_combine_inputs.py`;
   - older JEC `pt_raw` and diagnostic issues;
   - Route B (parked; to be compared with A later) and the 3FS re-NANO (submitted, pending);
   - the scale-variation normalisation, if Route B returns.

   Check each against the code and notes; do not just restate the slides.
4. Is every slide claim and number still accurate?
5. What has not been considered anywhere? For example: other trained or derived inputs that depend on changed selections, fake/non-prompt estimates, tt rateParam and CR definitions, ctag2d SF validity under the new selection, sumw/normalisation, datacard nuisances, era coverage. Rank by impact on Run A.

Rules:
- Read-only: no edits to the analysis repo, no job submission, no EOS deletion, no credential changes, no push.
- Do not rerun unit tests that already have logs on unchanged code (standing rule, `Projects/HToWW/2026-11-05-decision-review-trust-test-logs.md`).
- Another agent reviews the uncommitted code in parallel, and the Sol worker may still be editing the repo; do not touch it.
- Everything you report is agent-reported.

Output:
- Write `Projects/HToWW/2026-11-05-status-audit-retraining.md`: frontmatter per CLAUDE.md, every number with its source, and an open-items table with columns state / needed to close / owner / blocks Run A / dependencies.
- Commit locally with "laptop: HToWW status audit, open items, MVA/negrw retraining". Do not push.
- Reply to Chirayu in at most 15 lines: retraining verdicts (MVA, negrw), the open items that block Run A and what each needs, slide claims that are wrong, and the top new items.

## Brief 2 — HToWW · review uncommitted higgscharm code (read-only)

You are a WORKER and independent code REVIEWER (vault CLAUDE.md is your standing instruction). Task from Chirayu, 2026-11-05: review the uncommitted code in the higgscharm repo.

Repo (read-only): `ssh lxplus`, `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `40d0e3e`.

Review `git diff` of the 11 modified files:
- `analysis/corrections/lhepdf.py`
- `analysis/postprocess/utils.py`
- `analysis/processors/base.py`
- `analysis/selections/object_selections.py`
- `analysis/utils/eos_io.py`
- `condor/submit.sh`
- `runner.py`
- `scripts/combine/make_combine_inputs.py`
- `submit.py`
- `submit_condor.py`
- `tests/test_allfix.py`

Also review the new untracked modules:
- `analysis/processing_modes.py`
- `analysis/processing_checks.py`
- `analysis/features/`
- `analysis/models/registry.py`
- `analysis/sinks/`
- `scripts/mva/split_folds.py`
- `scripts/mva/register_folds.py`
- `scripts/check_train_outputs.py`
- `scripts/combine/build_cards_from_templates.py`
- `tests/test_processing_modes.py`
- `tests/test_hzz_safety_ports.py`

Ignore the `*.pre_sol_review` backups, `*.bak*`, `outputs/` and the loose plotting scripts.

What the code is:
- two review fixes (shared jet ordering, PDF-only combined variation);
- TRAIN/RUN processing modes, with deterministic event-mod-k folds and inline ONNX scoring;
- two ports from Saranya's HZZ branch (input-completeness checks, EOS read fallback).

Context:
- `Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run.md`
- `Projects/HToWW/2026-11-05-sol-review-unpushed-work.md`
- `Projects/HToWW/framework/optimization/2026-10-08-framework-optimization-plan.md`

Use the HToWW review protocol, `Projects/HToWW/framework/2026-11-05-htoww-review-protocol.md` (skill `htoww-review`). Focus on correctness:
- legacy mode stays unchanged in behaviour;
- fold assignment, and leakage between train/validation/test;
- normalisation in RUN templates and in `build_cards_from_templates` (sumw over all chunks, including zero-selection ones);
- completeness of shifts and systematics in RUN;
- argument forwarding through Condor;
- the manifest and hash guards;
- edge cases in the EOS fallback;
- consistent handling of negrw scoring and the event MVA in TRAIN/RUN;
- anything that would silently produce wrong cards.

Rules:
- Read-only: no repo edits or commits, no job submission, no EOS deletion, no push.
- Do not rerun unit tests that already have logs on unchanged code; cite the logs (standing rule, `Projects/HToWW/2026-11-05-decision-review-trust-test-logs.md`). Small new checks in node-local `/tmp` are fine.
- The Sol worker may still be editing this tree, so record the mtime/SHA of each file you reviewed.
- A separate agent audits status and open items in parallel; stay on the code.

Output:
- Write `Projects/HToWW/framework/2026-11-05-review-uncommitted-trainrun.md` with a findings table (severity, file:line, evidence, suggested fix).
- Commit locally with "laptop: review of uncommitted higgscharm TRAIN/RUN code". Do not push.
- Reply to Chirayu in at most 12 lines, blocking findings first.
