---
tags: [reference]
status: active
date: 2026-07-08
source: lxplus
---

# HPlusC / HPlusB CRAB production — NanoAOD datasets & run steps

**8 samples** = hplusc (charm) + hplusb (bottom), each in 4 campaigns
(2022preEE, 2022postEE, 2023preBPix, 2023postBPix).
**5 NanoAOD published** (table below), **3 pending step1** (2023 postBPix c+b, preBPix b).

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

## Pending samples — step1 not yet submitted (3)

| Sample | Workspace |
|---|---|
| hplusc 2023postBPix | `2023postBPix/` |
| hplusb 2023postBPix | `2023postBPix/hplusb/` |
| hplusb 2023preBPix  | `2023preBPix/hplusb/` |

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
