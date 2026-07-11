---
tags: [reference]
status: active
date: 2026-07-08
source: lxplus
---

# HPlusC / HPlusB CRAB production — NanoAOD datasets & run steps

**8 samples** = hplusc (charm) + hplusb (bottom), each in 4 campaigns
(2022preEE, 2022postEE, 2023preBPix, 2023postBPix).
**5 NanoAOD published** (table below); the **other 3** (2023 postBPix c+b, preBPix b)
are mid-chain — step1 GEN-SIM published, **step2 DRPremix running** (2026-07-11).
Re-run `run_workflow.sh` to advance them 3→5.

Workspaces: `/eos/home-c/cgupta/HToWW/freshprod/<campaign>[/hplusb]/`
DAS UI: https://cmsweb.cern.ch/das/  · query with `instance=prod/phys03`.

---

## NanoAOD samples (final analysis inputs)

Event counts from `dasgoclient` (queried 2026-07-08). DAS links resolve on
`prod/phys03`. All datasets:
`/HPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/<processing>/USER` (and
`HPlusBottom_...` for hplusb).

| Sample | Campaign | Events | NanoAOD (`<processing>` tag) | DAS |
|---|---|---:|---|---|
| hplusc | 2022postEE | 277,345 | `cgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78` | [das](https://cmsweb.cern.ch/das/request?instance=prod/phys03&input=%2FHPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8%2Fcgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78%2FUSER) |
| hplusc | 2022preEE | 328,838 | `cgupta-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v4-8653679c76b04a5edd42171c9a5e3f96` | [das](https://cmsweb.cern.ch/das/request?instance=prod/phys03&input=%2FHPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8%2Fcgupta-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v4-8653679c76b04a5edd42171c9a5e3f96%2FUSER) |
| hplusc | 2023preBPix | 280,356 | `cgupta-Run3Summer23NanoAODv13-HToWW-133X_mcRun3_2023_realistic_ForNanov13_v1-v1-666a5f9beb603dd857705c0ae1d4d5d7` | [das](https://cmsweb.cern.ch/das/request?instance=prod/phys03&input=%2FHPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8%2Fcgupta-Run3Summer23NanoAODv13-HToWW-133X_mcRun3_2023_realistic_ForNanov13_v1-v1-666a5f9beb603dd857705c0ae1d4d5d7%2FUSER) |
| hplusb | 2022postEE | 298,177 | `cgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78` | [das](https://cmsweb.cern.ch/das/request?instance=prod/phys03&input=%2FHPlusBottom_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8%2Fcgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78%2FUSER) |
| hplusb | 2022preEE | 809,802 | `tvanlaer-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v1-8653679c76b04a5edd42171c9a5e3f96` | [das](https://cmsweb.cern.ch/das/request?instance=prod/phys03&input=%2FHPlusBottom_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8%2Ftvanlaer-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v1-8653679c76b04a5edd42171c9a5e3f96%2FUSER) |

`hplusb 2022preEE` NanoAOD was published by **tvanlaer** (not cgupta). The intermediate
step datasets (GEN-SIM → MiniAOD) are not listed — only the NanoAOD inputs are needed.

---

## 2023 chain progress (3 samples)

**Step1 (GEN-SIM): complete & published** (2026-07-08). A few jobs failed with exit
50664 (wall-clock timeout) but 96–100% published — good enough to chain on.
**Step2 (DRPremix): submitted 2026-07-11**, now running.

| Sample | Step1 GEN-SIM (published) | Step2 DRPremix (running) |
|---|---|---|
| hplusc 2023postBPix | `260707_231145:...HPlusC_..._Step1_GEN_SIM_2023BPix_v1` (100/100) | `260711_195727:...HPlusC_..._Step2_DRPremix_2023BPix_v1` |
| hplusb 2023postBPix | `260707_231145:...HPlusB_..._Step1_GEN_SIM_2023BPix_v1` (99/100) | `260711_195728:...HPlusB_..._Step2_DRPremix_2023BPix_v1` |
| hplusb 2023preBPix  | `260707_225850:...HPlusB_..._Step1_GEN_SIM_2023_v1` (96/100) | `260711_195728:...HPlusB_..._Step2_DRPremix_2023_v1` |

Step1 output datasets (DRPremix input):
- hplusc 2023postBPix: `/HPlusCharm_.../cgupta-Run3Summer23BPixwmLHEGS-HToWW-130X_mcRun3_2023_realistic_postBPix_v6-v1-dacb523b56f64076a1210fb7b5034c87/USER`
- hplusb 2023postBPix: `/HPlusBottom_.../cgupta-Run3Summer23BPixwmLHEGS-HToWW-130X_mcRun3_2023_realistic_postBPix_v6-v1-3c64e55b0564436e3344518b1f813480/USER`
- hplusb 2023preBPix:  `/HPlusBottom_.../cgupta-Run3Summer23wmLHEGS-HToWW-130X_mcRun3_2023_realistic_v15-v1-e3ed8bd4616088f541f67e6538a70fe4/USER`

Re-run each workspace's `run_workflow.sh` after step2 completes to chain 3→4→5.

### Gotchas hit while submitting these (fix before rerunning)
1. **Run submits detached.** A submit over a one-shot `ssh lxplus '<cmd>'` gets killed
   mid-submission when the session closes (task never registers, leaves an empty stub
   dir). Launch with `setsid nohup bash run_workflow.sh > submit.log 2>&1 < /dev/null &`
   and poll the log for `Task name:` + `.requestcache`.
2. **2023postBPix had no CMSSW release.** `2023postBPix/CMSSW_13_0_17` didn't exist →
   submits died with `ModuleNotFoundError: No module named 'FWCore'`. Created it to match
   the working 2023preBPix release's arch **`el9_amd64_gcc11`** (first tried el8 — wrong
   for el9 nodes). Recreate if missing:
   ```bash
   source /cvmfs/cms.cern.ch/cmsset_default.sh
   cd /eos/home-c/cgupta/HToWW/freshprod/2023postBPix
   export SCRAM_ARCH=el9_amd64_gcc11 && scramv1 project CMSSW_13_0_17
   ```
3. **Grid proxy expires between sessions.** `crab status`/`dasgoclient` both need a live
   voms proxy; when it lapses they prompt for the GRID passphrase (uncatchable here).
   Re-run `voms-proxy-init -voms cms -rfc -valid 192:00` in a real terminal. The myproxy
   (30-day) keeps *jobs* running regardless — only status queries need the local proxy.
- Failed/half submits leave a stub crab dir (empty `inputs/`+`results/`, no
  `.requestcache`) that blocks resubmit with *"Working area already exists"* — `rm -rf`
  it first.

---

## How to run each step

The `run_steps*` / `run_workflow.sh` scripts are **idempotent**: per step they check
CRAB status, skip completed steps, and submit only the *next* not-started step. Re-run
after each step finishes to advance the chain 1→2→3→4→5. All need a valid grid proxy +
delegated CRAB myproxy first.

**0. Proxy (once, in a real terminal — the myproxy prompts for the GRID pass phrase):**
```bash
voms-proxy-init -voms cms -rfc -valid 192:00
```

**2022 campaigns** — split by CMSSW version (steps 1-3 need CMSSW_12 el8 container,
steps 4-5 need CMSSW_13):
```bash
cd /eos/home-c/cgupta/HToWW/freshprod/<2022campaign>[/hplusb]
bash run_steps123.sh    # advances steps 1-3
bash run_steps45.sh     # advances steps 4-5
```

**2023 campaigns** — one script does all steps (CMSSW_13):
```bash
cd /eos/home-c/cgupta/HToWW/freshprod/<2023campaign>[/hplusb]
bash run_workflow.sh    # advances whichever step is next
```

**For the pending 2023postBPix charm:** its step1 crab dir is a leftover from a *failed*
myproxy delegation (never reached the grid) and blocks resubmit — remove it first:
```bash
rm -rf /eos/home-c/cgupta/HToWW/freshprod/2023postBPix/crab_projects_2023postBPix/crab_HPlusC_HToWW_Step1_GEN_SIM_2023BPix_v1
```
