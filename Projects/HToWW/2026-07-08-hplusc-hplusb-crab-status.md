---
tags: [reference]
status: active
date: 2026-07-08
source: lxplus
---

# HPlusC / HPlusB CRAB production status (run_steps* sweep)

Ran the `run_steps*` / `run_workflow.sh` chains for **hplusc** (charm) and **hplusb**
(bottom) across all campaigns. The scripts are idempotent: per step they check CRAB
status, skip completed steps, and only submit the *next* not-started step.

Workspaces under `/eos/home-c/cgupta/HToWW/freshprod/`.

## Result per workspace

| Campaign | Sample | Driver | Result |
|---|---|---|---|
| 2022postEE | hplusc | `run_steps123` + `run_steps45` | ✅ **ALL 5 STEPS COMPLETED** (NanoAODv13 published) |
| 2022postEE | hplusb | `hplusb/run_steps123` | ✅ **ALL 5 STEPS COMPLETED** |
| 2022preEE  | hplusc | `run_steps123` | ✅ **ALL 5 STEPS COMPLETED** |
| 2022preEE  | hplusb | `hplusb/run_steps123` | ✅ **ALL 5 STEPS COMPLETED** (step5 reuses tvanlaer's NanoAOD) |
| 2023preBPix | hplusc | `run_workflow.sh` | ✅ **ALL 5 STEPS COMPLETED** |
| 2023postBPix | hplusc | `run_workflow.sh` | ⛔ step1 crab dir exists from a *failed* delegation → "Working area already exists"; never actually submitted |
| 2023postBPix | hplusb | `hplusb/run_workflow.sh` | ⛔ step1 NOT_STARTED → submit failed: **Problems delegating My-proxy** |
| 2023preBPix | hplusb | `hplusb/run_workflow.sh` | ⛔ step1 NOT_STARTED → submit failed: **Problems delegating My-proxy** |

**Bottom line:** all 2022 samples (c + b, pre + post) and 2023preBPix charm are fully
done. The **three remaining 2023 submissions are blocked by an expired CRAB myproxy**,
not by any config problem.

## Root cause of the 2023 blocks: expired myproxy

A local grid proxy exists (`voms-proxy-init -voms cms` was done; `voms-proxy-info` shows
~191h left). But CRAB's first submit **delegates a long-lived myproxy** to
`myproxy.cern.ch`, and that credential is expired:

```
myproxy-info -s myproxy.cern.ch -l 81e20e4ae67b2089f71293220f37b00971e33c59
  owner:   .../CN=cgupta/...
  timeleft: 0:00:00          <-- EXPIRED
```

Renewing it runs `myproxy-init ... -C ~/.globus/usercert.pem -y ~/.globus/userkey.pem`,
which must **read the encrypted userkey.pem and therefore prompts for the GRID pass
phrase**. That prompt cannot be answered from a non-interactive Claude/ssh session
(`Couldn't read user key ... grid-proxy-init failed`), so every fresh CRAB submit aborts
with *"Problems delegating My-proxy."*

The `2023postBPix` charm step1 crab dir
(`crab_HPlusC_HToWW_Step1_GEN_SIM_2023BPix_v1`) is a *leftover from a failed delegation*
on 2026-07-07 — the task never reached the grid, but the dir now blocks resubmit.

## What Chirayu needs to do (one interactive step)

In a real terminal on lxplus, with the CMSSW_13 env + crab-setup sourced:

```bash
# 1. fresh local proxy (192h)
voms-proxy-init -voms cms -rfc -valid 192:00

# 2. (re)delegate the CRAB myproxy — THIS prompts for the GRID pass phrase
#    Easiest: just re-run a crab submit; crab does the myproxy-init for you.
#    Or force it explicitly:
myproxy-init -d -n -s myproxy.cern.ch \
  -C ~/.globus/usercert.pem -y ~/.globus/userkey.pem \
  -x -R '.../CN=Robot: cms crab...' -x -Z '.../CN=Robot: cms crab...' \
  -l 81e20e4ae67b2089f71293220f37b00971e33c59 -t 168 -c 720:00
```

Then the three blocked submits go through. For **2023postBPix charm**, first clear the
dead step1 dir (it was never submitted) so the workflow can resubmit:

```bash
rm -rf /eos/home-c/cgupta/HToWW/freshprod/2023postBPix/crab_projects_2023postBPix/crab_HPlusC_HToWW_Step1_GEN_SIM_2023BPix_v1
cd /eos/home-c/cgupta/HToWW/freshprod/2023postBPix        && bash run_workflow.sh   # hplusc
cd /eos/home-c/cgupta/HToWW/freshprod/2023postBPix/hplusb && bash run_workflow.sh   # hplusb
cd /eos/home-c/cgupta/HToWW/freshprod/2023preBPix/hplusb  && bash run_workflow.sh   # hplusb
```

Each `run_workflow.sh` submits only step1; re-run later to chain steps 2→5 as each
completes.

## Log
- 2026-07-08: swept all 8 workspaces. 5 fully complete, 3 (2023 postBPix c+b, preBPix b)
  blocked on expired myproxy — needs one interactive `myproxy-init` from Chirayu.
