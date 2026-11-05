---
name: gridpack-on-eos-fuse-fails
description: Never run cmsRun with ExternalLHEProducer (gridpack) with its cwd on EOS FUSE; untar is ~30x slow and the gridpack's final rm -rf fails, killing the job. Use a CRAB/condor test instead
metadata:
  type: feedback
---

MEASURED 2026-10-21 (3FS H+c test in `/eos/home-c/cgupta/HToWW/fs_unc/gen3fs_ww`): with cwd on EOS, the 4 concurrent
gridpack untars took >30 min, LHE generation itself then worked, but `run_generic_tarball_cvmfs.sh` cleanup hit
`rm: cannot remove 'lheevent/mgbasedir': Directory not empty` -> child exit 1 -> ExternalLHEProducer exception -> segfault,
and the cleanup deleted the LHE files too. The user did NOT want the test moved to node-local /tmp; a ONE-JOB CRAB test of
the real step1 config was the accepted route (worker-local disk, tests the production config exactly).

**How to apply:** for a gridpack/GEN test, propose a one-job CRAB (or condor) test up front, not a local EOS run. Never kill
the user's running jobs without asking first; they interrupted when I tried to kill and restart the EOS test.
`crab createmyproxy`/first CRAB submit needs the user's grid passphrase AND a cmsenv first (CMSSW 13_0_17 el9 area under
freshprod/2023postBPix works). Related: [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-3fs-private-production|hww-3fs-private-production]].
