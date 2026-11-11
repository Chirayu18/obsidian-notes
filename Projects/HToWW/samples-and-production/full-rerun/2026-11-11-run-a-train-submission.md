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

### Second pass (11 Nov, ~17:20)

Completeness before the second pass (`jobs_status.py ... --hours_ago 48`, answering no):

| era | finished / expected |
|---|---|
| 2022preEE | 486/506 |
| 2022postEE | 1157/1188 |
| 2023postBPix | 316/393 |

Failures were again site errors: NCHC Taiwan, Rutgers, UFL `[3010]`, and KFKI timeouts. No jobs were queued (`condor_q -name bigbird28.cern.ch cgupta`: 0), so the missing jobs had all failed. All of them were resubmitted with the failing sites blacklisted: 2022preEE 20, 2022postEE 31, 2023postBPix 77. Logs: `~/htoww_submit_logs/resubmit2_<era>_20261111.log`.

2023preBPix needed two separate fixes:

- **`DYto2L_2Jets_10to50` was never submitted.** The 10 Nov run was cut off while preparing it, which left an empty condor directory. `submit_missing.py` then counted it as done. I removed the two empty directories and submitted it: 44 jobs, cluster 9697156.
- **One bad input file in `GluGluHto2Tau`.** A `ValueError: ListArray64 ... index out of range` in `jerc.py:377` (`events.GenJet[genjetidx]`), from a jet whose `genJetIdx` points past the GenJet list in file `.../40000/1d4e1a08-9b2c-4366-86f0-972e4ed0a8dc.root`. This is a property of the file, not of the site serving it.
  - I removed that file from `fileset_2023preBPix_nanov12_lxplus.json` (backup `.bak-20261111-ggHtautau`) and resubmitted the sample, which now has 1 file: 1 job, cluster 9697157.
  - `jerc.py` was deliberately not patched. It is part of `selection_signature`, so editing it would invalidate the TRAIN outputs already produced.
  - Normalisation uses the sumw of the processed files, so the sample is consistently halved.
  - **Flag:** this 2023preBPix sample is `Run3Winter23NanoAOD ... 126X_mcRun3_2023_forPU65`, not Summer23. That predates this work, but it should be replaced by the Summer23 sample when one exists.
- **2023preBPix second pass (11 Nov evening):** 263/640 finished, 377 missing. The 333 failures outside the two in-flight samples were resubmitted, with failing sites blacklisted, by `~/htoww_submit_logs/resubmit_except.py 2023preBPix DYto2L_2Jets_10to50 GluGluHto2Tau` (the jobs_status flow minus in-flight datasets). The fileset was restored afterwards to 95 datasets. DY 10to50 uses 657 files, equal to the live list at submission; the 3 Nov backup had 658.
- Earlier note, superseded by the line above: the 2023preBPix completeness check has not been rerun yet. It must wait until the DY and H→ττ jobs have written output; otherwise `jobs_status.py` would resubmit them a second time. I stopped my own loop before it reached that era.

### `jobs_status.py` truncates the fileset JSON

Each fileset regeneration runs `fetch.py --samples <group>`, and that rewrites `fileset_<era>_nanov12_lxplus.json` with only the requested datasets. After the second pass, 2022preEE, 2022postEE and 2023postBPix each held 1 dataset. The many 1-entry `.bak*` files show this has happened before.

- Running jobs were not affected, because each job reads its own `partitions.json`.
- The later coverage check (F6) and any new submission do need the full list.
- **Restored** with `/tmp/cgupta_rebuild_filesets.py`, copied to `~/htoww_submit_logs/`. Each list was rebuilt from `.bak-20261103` with every workflow dataset replaced by the union of its submitted `partitions.json`. Result: 92, 93 and 84 datasets. The truncated files are kept as `.bak-20261111-truncated`.
- The backup's DY entries were stale. The live era YAML queries newer DY versions (2022preEE: 10to50 `-v4`, MLL-50 `-v5`; 2022postEE: `-v5`; 2023postBPix: `-v4`). Each sample uses exactly one version, so there is no double counting.
- The jobs_status/fetch.py bug itself is not fixed. Rerun the restore after any future blacklist round, or fix `fetch.py` so it merges instead of overwriting.

## Nc-j split implemented (11 Nov)

- Commit `9802054` (fixture update in `ff35a19`) adds `combine.channel_splits`. In `hww_allfix_4fs` the SR becomes `SR_hplusc_1cj` (`cjet_multiplicity` = 1) and `SR_hplusc_2cj` (≥ 2); the CRs are unchanged.
- It is used by RUN templates (`analysis/sinks/hww.py`, `base.py`) and `build_cards_from_templates.py`. Legacy builders still see the unsplit `combine.channels`.
- Each event in the class is checked to land in exactly one sub-channel, and an uncovered event raises an error.
- The model and selection hashes are unchanged (`sinks/`, `processors/` and the `combine` block are not hashed), so the running TRAIN is unaffected.
- Tests: `tests/test_channel_split.py` 4/4; full suite 76/77 (the remaining error is the container's `/eos/user` read).

## Option (a): candidate sources found (not chosen, not implemented)

- **H+b:** LHCHWG YR4 13 TeV page, bbH at mH = 125.09 GeV: σ = 0.5265 pb, THU +9.3%, **PDF+αS+mb +3.3% / −3.5%** (combined, no separate PDF/αS split). Source: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt13TeV, read 2026-11-11. The 13.6 TeV page (LHCHWG136TeVxsec, rev 45) defines the format but publishes no bbH numbers.
- **H+c:** LHCHWG-2026-007 gives scale and flavour-scheme uncertainties only, with no PDF/αS. The Run 2 AN (AN-23-102 §7.1.1 and Table 14, from AN-22-064) uses **6% PDF** with NNPDF31 nf4 325500, the same set as our 4FS sample, and no separate αS. The pre-August config had 6% PDF + 3% αS; the source of that 3% is not recorded.
- Proposed for Chirayu: H+b lnN 1.033/0.965 (PDF+αS combined); H+c PDF 6% (AN-23-102). For H+c αS, either an inclusive estimate from the private clean 4FS gridpack (325500 has no αS members, so this needs another set) or a stated proxy. Awaiting his choice.

## Not done yet

- Route B: still the parked proposal ([[Projects/HToWW/2026-11-05-route-b-stitching-implementation]]). It needs integration into the live processor and a check that the 3FS samples and re-NANO are complete before its TRAIN.
- Option (a): Chirayu to confirm the numbers above; then add the lnN rows.
- 2023preBPix completeness check after its DY/H→ττ jobs finish.
- b-hive seeding of the internal validation split; empty-shift fallback set to `error`. Both happen after TRAIN (training and card stage).
- After TRAIN completes: `check_train_outputs.py` → `split_folds.py` → b-hive per-fold training.

## TRAIN v2 (12 Nov)

- **Why:** commit `f84d311` moved the negrw model from the hashed selection inputs to weight provenance, because b-hive ignores event weights and Chirayu asked for negrw to be retrained. That changed the features and selection hashes once, so the v1 TRAIN was stopped:
  - 52 running jobs were removed (`condor_rm`, clusters 9701186–9701214).
  - v1 outputs were moved, not deleted, to `/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train_v1_20261110/`, and the condor and log dirs to `condor/[logs/]hww_allfix_4fs__train_v1_20261110`.
- **Same commit:** `jobs_status.py` now merges the regenerated filesets instead of letting `fetch.py` truncate them (`tests/test_jobs_status_merge.py` 3/3).
- **v2 submitted 12 Nov**, all datasets via `~/htoww_submit_logs/submit_missing.py`, rc=0:

  | era | datasets | jobs |
  |---|---|---|
  | 2022preEE | 54 | 506 |
  | 2022postEE | 55 | 1188 |
  | 2023preBPix | 66 | 640 |
  | 2023postBPix | 56 | 393 |

  Queue right after submission: 2446 jobs (575 running).
