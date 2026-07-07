---
tags: [reference]
status: active
date: 2026-07-08
source: lxplus
---

# HPlusC / HPlusB CRAB production — datasets & run steps

**8 samples** = hplusc (charm) + hplusb (bottom), each in 4 campaigns
(2022preEE, 2022postEE, 2023preBPix, 2023postBPix).
**5 complete** (all steps published to DAS), **3 pending step1**.

Workspaces: `/eos/home-c/cgupta/HToWW/freshprod/<campaign>[/hplusb]/`
DAS UI: https://cmsweb.cern.ch/das/  · query with `instance=prod/phys03`.

---

## Completed samples — published datasets (per step)

DAS link = `https://cmsweb.cern.ch/das/request?input=<dataset>&instance=prod/phys03`

### hplusc 2022postEE
| Step | Dataset |
|---|---|
| 1 GEN-SIM  | `/HPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/cgupta-Run3Summer22EEwmLHEGS-HToWW-124X_mcRun3_2022_realistic_postEE_v1-v1-961d567f3b28739d7d3304cf1c19e16d/USER` |
| 2 DRPremix | `/HPlusCharm_.../cgupta-Run3Summer22EEDRPremix-HToWW-124X_mcRun3_2022_realistic_postEE_v1-v1-31b3ee15c0b04cb98bdf3666445e3e75/USER` |
| 3 RECO     | `/HPlusCharm_.../cgupta-Run3Summer22EEDRPremix-HToWW-RECO-124X_mcRun3_2022_realistic_postEE_v1-v1-4cb6268f68760f7ffbcfed10319ec573/USER` |
| 4 MiniAOD  | `/HPlusCharm_.../cgupta-Run3Summer22EEMiniAODv4-HToWW-130X_mcRun3_2022_realistic_postEE_v6-v1-0fd187a8655a412b0c23134e39ea2b39/USER` |
| 5 NanoAOD  | `/HPlusCharm_.../cgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78/USER` |

### hplusc 2022preEE
| Step | Dataset |
|---|---|
| 1 GEN-SIM  | `/HPlusCharm_.../cgupta-Run3Summer22wmLHEGS-HToWW-124X_mcRun3_2022_realistic_v12-v6-f04f7d9f45dbc50cf6f740b9d47c558e/USER` |
| 2 DRPremix | `/HPlusCharm_.../cgupta-Run3Summer22DRPremix-HToWW-124X_mcRun3_2022_realistic_v12-v6-b722d1cf11a99a4476f09a94f34c768e/USER` |
| 3 RECO     | `/HPlusCharm_.../cgupta-Run3Summer22DRPremix-HToWW-RECO-124X_mcRun3_2022_realistic_v12-v6-0190a31f56290269056b5583a84fa4cc/USER` |
| 4 MiniAOD  | `/HPlusCharm_.../cgupta-Run3Summer22MiniAODv4-HToWW-130X_mcRun3_2022_realistic_v5-v6-3c2e9ed2594fb101fac62691334d2f84/USER` |
| 5 NanoAOD  | `/HPlusCharm_.../cgupta-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v4-8653679c76b04a5edd42171c9a5e3f96/USER` |

### hplusc 2023preBPix
| Step | Dataset |
|---|---|
| 1 GEN-SIM  | `/HPlusCharm_.../cgupta-Run3Summer23wmLHEGS-HToWW-130X_mcRun3_2023_realistic_v15-v1-64a3e6699f1fcde747888ed384bf5a6b/USER` |
| 2 DRPremix | `/HPlusCharm_.../cgupta-Run3Summer23DRPremix-HToWW-130X_mcRun3_2023_realistic_v15-v1-c8a51e44625b3c15c549596559b6ff82/USER` |
| 3 RECO     | `/HPlusCharm_.../cgupta-Run3Summer23DRPremix-HToWW-RECO-130X_mcRun3_2023_realistic_v15-v1-93541c315341c0b0958208c5a365b22c/USER` |
| 4 MiniAOD  | `/HPlusCharm_.../cgupta-Run3Summer23MiniAODv4-HToWW-130X_mcRun3_2023_realistic_v15-v1-d64cae098ec4867fb5ede51e14ecff7d/USER` |
| 5 NanoAOD  | `/HPlusCharm_.../cgupta-Run3Summer23NanoAODv13-HToWW-133X_mcRun3_2023_realistic_ForNanov13_v1-v1-666a5f9beb603dd857705c0ae1d4d5d7/USER` |

### hplusb 2022postEE
| Step | Dataset |
|---|---|
| 1 GEN-SIM  | `/HPlusBottom_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/cgupta-Run3Summer22EEwmLHEGS-HToWW-124X_mcRun3_2022_realistic_postEE_v1-v1-c654de23a73dda62a53feebc8f86aea4/USER` |
| 2 DRPremix | `/HPlusBottom_.../cgupta-Run3Summer22EEDRPremix-HToWW-124X_mcRun3_2022_realistic_postEE_v1-v1-31b3ee15c0b04cb98bdf3666445e3e75/USER` |
| 3 RECO     | `/HPlusBottom_.../cgupta-Run3Summer22EEDRPremix-HToWW-RECO-124X_mcRun3_2022_realistic_postEE_v1-v1-4cb6268f68760f7ffbcfed10319ec573/USER` |
| 4 MiniAOD  | `/HPlusBottom_.../cgupta-Run3Summer22EEMiniAODv4-HToWW-130X_mcRun3_2022_realistic_postEE_v6-v1-0fd187a8655a412b0c23134e39ea2b39/USER` |
| 5 NanoAOD  | `/HPlusBottom_.../cgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78/USER` |

### hplusb 2022preEE  (step5 published by tvanlaer)
| Step | Dataset |
|---|---|
| 1 GEN-SIM  | `/HPlusBottom_.../cgupta-Run3Summer22wmLHEGS-HToWW-124X_mcRun3_2022_realistic_v12-v1-9dfa018e54fff8405c257c1f94e11cf5/USER` |
| 2 DRPremix | `/HPlusBottom_.../cgupta-Run3Summer22DRPremix-HToWW-124X_mcRun3_2022_realistic_v12-v1-b722d1cf11a99a4476f09a94f34c768e/USER` |
| 3 RECO     | `/HPlusBottom_.../cgupta-Run3Summer22DRPremix-HToWW-RECO-124X_mcRun3_2022_realistic_v12-v1-0190a31f56290269056b5583a84fa4cc/USER` |
| 4 MiniAOD  | `/HPlusBottom_.../cgupta-Run3Summer22MiniAODv4-HToWW-130X_mcRun3_2022_realistic_v5-v1-3c2e9ed2594fb101fac62691334d2f84/USER` |
| 5 NanoAOD  | `/HPlusBottom_.../tvanlaer-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v1-8653679c76b04a5edd42171c9a5e3f96/USER` |

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
