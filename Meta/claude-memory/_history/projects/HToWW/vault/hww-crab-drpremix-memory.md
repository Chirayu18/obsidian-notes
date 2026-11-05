---
name: hww-crab-drpremix-memory
description: HToWW 2023 CRAB step2 DRPremix OOMs at 4GB config — fix via resubmit @5GB or 3-core config; CMS 2500MB/core policy
metadata: 
  node_type: memory
  type: project
  originSessionId: 3bcca172-c813-41fc-bf5f-cbd3eb2b65c4
---

HToWW 2023 signal production: CRAB **step2 (DRPremix)** in `multicrab_workflow_2023.py`
was configured `memory: 4000 / cores: 2`, but DRPremix jobs peak at **4.3–8.1 GB RSS**
(avg 4.2) → 42–70% die with **exit 50660** ("killed by HTCondor due to excessive memory use").

**Why:** CMS caps memory at **2500 MB/core** (https://cmssi.docs.cern.ch/policies/memory/),
so a 2-core job's ceiling is **5000 MB**. `crab resubmit --maxmemory=6000` is **rejected**;
resubmit can raise memory but **cannot change cores**.

**How to apply:**
- Recover failed jobs (keeps finished ones): `crab resubmit -d <task> --maxmemory=5000`
  (source cmsenv first: `cd CMSSW_13_0_17/src && eval $(scramv1 runtime -sh)`, else
  "CMSSW is missing" error).
- For >5 GB headroom, must bump cores BEFORE a fresh submit — done 2026-07-13: step2 + step3
  set to `memory: 7500 / cores: 3` in all 4 `2023*/[hplusb/]multicrab_workflow_2023.py`
  (backups `*.bak-precore`). 3-core ceiling = 7500 MB.

Two more submit gotchas (hit 2026-07-15 chaining step3):
- **`SCRAM_ARCH` drift → `No module named 'FWCore'`.** 2023 releases are `el9_amd64_gcc11`
  but login shell defaults `gcc12`; `scramv1 runtime -sh` then silently exports NOTHING
  (empty `CMSSW_BASE`) and pset import dies. `run_workflow.sh` now `export
  SCRAM_ARCH=el9_amd64_gcc11` after cmsset (backups `*.bak-arch`).
- **`numCores` (config) must == `numberOfThreads` (pset).** Only bump a step's `cores` in
  `multicrab_workflow_2023.py` if you also edit its pset threads. step3 was reverted to
  `4000/2` to match `step3.py` (`numberOfThreads=2`); step2 stays `7500/3`.
- Driver treats a step DONE as soon as ANY output dataset publishes (partial=done), so it
  auto-advances even before 100% — resubmit stragglers first if every event matters.

Workspaces: `/eos/home-c/cgupta/HToWW/freshprod/2023{pre,post}BPix/[hplusb/]`.
Full log in vault `Projects/HToWW/2026-07-08-hplusc-hplusb-crab-status.md`.
Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-negweight-reweight-fix|hww-negweight-reweight-fix]], [[Meta/claude-memory/_history/workflow/vault/lxplus-coffea-env|lxplus-coffea-env]].
