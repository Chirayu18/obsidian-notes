---
tags:
  - hww
status: waiting
date: 2026-02-19
---

# Instructions for job submission on Crab

---

## Commands

Path to files: 
`/eos/user/c/cgupta/HToWW/freshprod/2022postEE/hplusb`


```bash
#To run:
cmsrel CMSSW_12_4_20
cmsrel CMSSW_13_3_0

#Modify paths in run_steps123.sh and run_steps45.sh

./run_steps123.sh # - For steps 1-3 ( Run once per step until it is complete )
./run_steps45.sh # - For steps 4-5

#To modify number of events and other configs: edit multicrab_workflow_2022.py
```

---

## Tasks

- [ ] Upload to github
- [x] Check how to use custom grid packs
- [ ] Currently generated samples were for preEE

---

## Log


> [!bug] Issue — 2026-03-03
> **Issue:**
```
Error detected in sub-command output HPlusBottom_5FS_MuRFScaleDynX0p50_HToGG_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8 -nojpeg
write debug file MG5_debug
If you need help with this issue please contact us on https://answers.launchpad.net/mg5amcnlo
str : The OneLOop library 'libavh_olo.(a|dylib|so)' could no be found in path '/eos/home-c/cgupta/HToWW/mcm_grid/genproductions_scripts/bin/MadGraph5_aMCatNLO/HPlusBottom_5FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8/HPlusBottom_5FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8_gridpack/work/MG5_aMC_v2_9_18/HEPTools/lib'. Please place a symlink to it there.
quit
```
> -
> **Attempts:**
> -  Change name in proc card and rerun


### 2023 configs 
- Ready at `/eos/home-c/cgupta/HToWW/freshprod/2023preBPix`
- Ready at `/eos/home-c/cgupta/HToWW/freshprod/2023postBPix`
- Only require setup of `CMSSW_13_0_17`
- Only one script for all steps