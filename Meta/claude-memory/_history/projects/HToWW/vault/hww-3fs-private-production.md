---
name: hww-3fs-private-production
description: Private Run 3 3FS H+c->WW production (started 2026-10-21): reuses the official 3FS HToGG gridpack (H undecayed, clean weights) through the freshprod 4FS chain; configs in freshprod_3fs/<era>; CRAB test passed
metadata:
  type: project
---

No Run 3 3FS H->WW exists in DAS (see [[Meta/claude-memory/_history/general/vault/hc-das-inventory-minnlo-3fs|hc-das-inventory-minnlo-3fs]]); the postdoc wants a 3FS sample for eventual stitching.
- **Gridpack:** the official `HPlusCharm_3FS_MuRFScaleDynX0p50_HToGG_M125_..._slc7_amd64_gcc10_CMSSW_12_4_8` tarball. Proc card is
  `p p > h c c~ [QCD]` (H undecayed, no MadSpin, MG 2.9.9), and its runcmsgrid SKIPS python systematics, so its weights are clean.
  No new gridpack is needed; only the Pythia decay changes (25 -> 24 -24, 24 -> 11 13 15, same as the 4FS WW chain).
- **Configs:** `/eos/home-c/cgupta/HToWW/freshprod_3fs/{2022preEE,2022postEE,2023preBPix,2023postBPix}`, copied from the CLEAN
  private 4FS chain (`freshprod`, which used the official gg FxFx gridpack WITH the JetMatching lines) by `freshprod_3fs/make3fs.py`.
  step1 swaps the tarball and replaces the 12 JetMatching lines with `TimeShower:nPartonsInBorn = 2`. Request names `HPlusC3FS_*`,
  primary dataset `HPlusCharm_3FS_HToWW_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8`, work areas `crab_projects_<era>_3fs`.
  1M events per era (as for 4FS) and NOT yet submitted as of 2026-10-21.
- **CRAB test PASSED 2026-10-21** (1 job, 1000 events, 2023BPix, `crab_projects_2023postBPix_3fs_test`):
  - sigma 54.97 fb; 39.1% negative weights; H->WW 100%; e/mu/tau equal shares.
  - Scale sigma ratios: muR2 0.80, muR0.5 1.22, opposite directions. PDF replica-mean/member0 = 1.000, spread 1.6%.
  - Took ~80 min per 1000 events.
  - Checker: `freshprod_3fs/2023postBPix/check_test_output.py`.
- Use private 3FS vs private 4FS (both clean) for the Run 3 N-jet check, NOT the central 4FS (FxFx merging bug).

Contacts message draft: vault `Projects/HToWW/fs-unc-2026-09-29/2026-10-21-message-HToWW-contacts-3FS-and-scalevar.md`.
Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-fs-decision-shape-only|hww-fs-decision-shape-only]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-central-signal-lhe-weights-broken|hww-central-signal-lhe-weights-broken]].

**2026-10-23: production design changed to a SINGLE-JOB chain** (the user chose it to save space; 10M events kept in every step would be ~30 TB).
- Measured MB/event: GEN-SIM 0.55, DR 1.8-2.0, RECO 0.36-0.47, Mini 0.06, Nano 0.002. 3FS has no FxFx, so all 10M events go through every step.
- `freshprod_3fs/make_chain.py` writes `<era>/chain/`, and `run_chain.sh` (CRAB scriptExe) runs all 5 steps per job and deletes each intermediate.
  - Outputs: Nano (published) + miniaod.root (extra output, not published).
  - The step1 output is named nanoaod.root so CRAB expects the final Nano under that name.
  - 2022 switches to CMSSW_13_0_13 (postEE) / 13_0_17 (preEE) for MiniAOD/Nano inside the job.
  - 4 threads, 10000 MB; fresh DIGI/RECO seeds per job.
- Split by lumi: preEE 1.29M, postEE 4.31M, 2023 2.87M, BPix 1.53M (10M total).
- Submit 2022 from cmssw-el8 + freshprod/2022postEE/CMSSW_12_4_20; 2023 from el9 + freshprod/<era>/CMSSW_13_0_17.
- 4 one-job TEST tasks (100 events) submitted 2026-10-23 14:01, work area `<era>/chain/crab_projects_chain`.
- EVENTS_PER_JOB is to be set from the CHAIN_TIMING lines in the job logs.

2026-10-23:
- 2022 TEST jobs passed: 100 events each, Nano published in phys03 (dataset names `cgupta-TEST-Run3Summer22[EE]NanoAODv13-...-3FS-<hash>`),
  miniaod_1.root + nanoaod_1.root at IIHE, nTrueInt 36.9, 30-41 min wall, 4.7 GB peak.
- FULL 2022 SUBMITTED 2026-10-23 16:59 CEST with 1000 events/job and 7000 MB:
  - `261023_145941:cgupta_crab_HPlusC3FS_HToWW_chain_2022preEE_v1` (1.29M);
  - `261023_145954:..._2022postEE_v1` (4.31M).
- 2023: the preBPix TEST is running; the postBPix TEST is stuck at the CRAB schedd with no status (CRAB-side). Submit both 2023 eras once preBPix passes.

2026-10-28:
- 2022 status: preEE 1253/1290 and postEE 4120/4310 finished+published.
  - The failures: 131 at exit -1, 41 at 60322, 12 at 50660 (memory), 3 at 60328, 2 at 80000, 1 at 50115.
  - Resubmitted with --maxmemory 9000 --maxjobruntime 2750.
- 2023 TEST: the chain completed (CHAIN_TIMING steps 1-4 in ~50 min for 100 events) and failed only in the ASO transfer, Vanderbilt temp -> IIHE (60322).
- FULL 2023 SUBMITTED 2026-10-28 with 9000 MB:
  - `261028_091908:..._2023preBPix_v1` (2.87M);
  - `261028_091918:..._2023postBPix_v1` (1.53M).

2026-10-28 later:
- The 2022postEE task stayed FAILED after two `crab resubmit` calls (190 jobs 'unsubmitted'; the 2022preEE resubmit worked).
- So I submitted `261028_110524:..._2022postEE_ext1`: 190k events, its own tag `...-3FS_ext1`, 7000 MB.
- The framework must list BOTH postEE datasets.

2026-10-29:
- A wave of stage-out failures (60326/60327 'recoverable stageout exception') hit ~half the 2023 jobs and the ext1 task. IIHE writes test fine.
- `crab resubmit --maxmemory 9000` WORKED for the 2023 tasks and 2022postEE_ext1.
- Once a task's scheduler is FAILED, resubmit is silently ignored (seen twice). Remedy: an _ext1 task with its own tag for the missing events.
- `261029_091926:..._2022preEE_ext1`: 37k events, 9000 MB.
- The framework must list the v1 AND _ext1 datasets for 2022preEE and 2022postEE.

2026-11-02: all four tasks reached scheduler FAILED with the leftovers.
- Published jobs: preEE 1262/1290; postEE 4120 + ext1 61 of 190; 2023 2220/2870; BPix 1295/1530.
  That is 8.96M of 10M events (~1000 events/job, ~3 h/job).
- Failures were stage-out (60326/60327/60324) plus 50115 'BadFWJRXML'.
  The 50115 jobs' attempt-0 logs show the chain completed with exit 0, so the failure sits in the CRAB retry/postjob, not in run_chain.sh.
- Resubmitted all four with --maxmemory 9000 --maxjobruntime 2750 at 01:00.
