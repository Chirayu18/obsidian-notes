---
tags: [reference, decision]
status: active
date: 2026-11-11
source: laptop
evidence: agent-reported
---

# Run A TRAIN submitted (10–11 Nov 2026), with pre-TRAIN reproducibility changes

**Status: agent-reported.** Code committed locally on lxplus, not pushed, not independently reviewed. TRAIN jobs are submitted; no training, RUN or Combine has happened yet.

## Chirayu's decisions (exact wording)

- 2026-11-10: "proxy done, I choose (a) . And OK to commit locally. Then run the A and B routes . Also set up the >1 jet channel for the analysis"
  - (a) = keep `lhe_pdf`/`lhe_alphaS` as shape-only and add a sourced fixed PDF+αS **rate** uncertainty for H+c and H+b (options as laid out in the 10 Nov HToWW discussion thread; background in [[Projects/HToWW/2026-11-10-training-decisions-discussion]]). The numbers are not yet chosen; they must be sourced and shown to Chirayu before use. They enter only at Combine, so TRAIN/RUN are unaffected.
- 2026-11-10: "Check the Run 2 analysis note for that" (about the >1 jet channel).
- 2026-11-10: "submit now no questions" (the planned one-dataset smoke test was skipped on this instruction).

## ">1 jet channel": what the Run 2 AN does

`References/HToWW/AN-23-102.pdf`, lines 337–338 and Table 11: the SR (≥1 c-jet, mTl2 > 30, mTll > 60, mℓℓ ≤ 72) is split into **Nc-j = 1** and **Nc-j > 1** (number of c-tagged jets), "due to different background composition, which improves the sensitivity by 8%". Table 12 yields (2018): tt 14738 vs 2116, H+c 0.169 vs 0.009. Plot labels say "nJet", but the text and tables mean c-tagged jets.

In our Run 3 setup the SR is the argmax channel `SR_hplusc` and `cjet_multiplicity` is already an output column, so the split is a RUN-template/card-builder change: no TRAIN reprocessing needed. **Not implemented yet.** It depends on the c-tag working point, which is provisional until Livio's update.

## Commits on lxplus (`hww-analysis`, not pushed)

| commit | content |
|---|---|
| `6451c52` | the uncommitted 5–6 Nov work (TRAIN/RUN modes, HZZ ports, Sol fixes, F1–F13/F15); 36 files. Its `git diff` sha256 prefix `310d5e5750a3f916` equals the [[Projects/HToWW/framework/2026-11-05-trainrun-blocker-fixes|6 Nov handoff]] state. Backups, CSVs, plotting scripts and compiled `lhe_yukawa/as2`, `tab` left untracked |
| `f1e2016` | (1) `analysis/corrections/event_rng.py`: per-object random numbers from (run, lumi, event, object index, purpose). These replace the unseeded `random()` in muon resolution smearing and the per-chunk `seed=42` electron smearing. (2) F14: `external_inputs()` in `analysis/features/hww.py`. JEC/JER, jet veto, muon/electron scale-smearing, lumimask, `lhe_yukawa` and the negrw model enter `selection_signature`. Weight-only files (SFs, pileup, c-tag, k-factors) are recorded in the model `meta.yaml` but not hashed. (3) `request_cpus = 2` in `condor/submit.sub` |

Tests in the coffea 0.7.30 container: 72/73 OK. The one error, `test_bhive_config_and_onnx_io_checks`, is the container being unable to read `/eos/user/.../HPlusCHToWW_2dcats.yml` on that node (PermissionError); it is not a code failure. New tests: `tests/test_event_rng.py` (chunk invariance, including the real 2022postEE muon correction split in different chunkings) and `tests/test_external_inputs.py`.

The MET-xy correction also uses an unseeded random run number, but it is imported and never called, so it is unchanged.

## Submission

- Command per era: `python3 runner.py --workflow hww_allfix_4fs --year <era> --submit --eos --mode train --folds 5` (memory 2000 MB, nfiles 15). Proxy: `~/private/x509up_u151861`.
- 2022preEE and 2022postEE: submitted 10 Nov ~18:00–18:05.
- 2023preBPix: interrupted after 22 of 66 datasets. The remaining 44 and all 56 of 2023postBPix were submitted on 11 Nov with `~/htoww_submit_logs/submit_missing.py`, which runs the same `submit_condor.py` arguments for datasets that have no prepared condor directory.
- 11 Nov result: 2023preBPix 44/44 and 2023postBPix 56/56 datasets submitted, rc=0. All 4 eras are now fully submitted.
- Logs: `lxplus:~/htoww_submit_logs/`.
- Output: `/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train/<era>/`; 567 MB after the first pass, so TRAIN space is not a concern.

### First-pass failures (2022)

- 2022preEE: 301/506 jobs finished, 205 missing (29/54 datasets).
- 2022postEE: 568 failed jobs.
- Causes, from `condor/logs/hww_allfix_4fs__train/<era>/*/*.err`:
  - mostly `XRootD error: [FATAL] Connection error` at `root://ruhex-osgce.rutgers.edu` (~600 hits in 2022preEE, ~1600 in 2022postEE);
  - `FileNotFoundError` redirects (UFL, NCHC and others).
- Action, 11 Nov: `jobs_status.py -w hww_allfix_4fs -y <era> --eos --mode train --hours_ago 48`, answering yes to fileset regeneration with failing sites blacklisted and to resubmitting only the missing jobs. Result (rc=0): 2022preEE 205/205 missing jobs resubmitted (29 datasets), 2022postEE 568/568 (40 datasets, 1188 expected in total). Logs: `~/htoww_submit_logs/resubmit_<era>_20261111.log`. The 2023 eras still need the same completeness check once their jobs finish.

## Not done yet

- Route B: still the parked proposal ([[Projects/HToWW/2026-11-05-route-b-stitching-implementation]]). It needs integration into the live processor and a check that the 3FS samples and re-NANO are complete before its TRAIN.
- Option (a) rate uncertainties: sourced numbers still to be found and shown to Chirayu.
- The Nc-j = 1 / > 1 SR split.
- b-hive seeding of the internal validation split; empty-shift fallback set to `error`. Both happen after TRAIN (training and card stage).
- After TRAIN completes: `check_train_outputs.py` → `split_folds.py` → b-hive per-fold training.
