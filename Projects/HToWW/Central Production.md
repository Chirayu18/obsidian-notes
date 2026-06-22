---
tags:
  - hww
status: active
---

# Central Production

### Crab job Time Taken
-  Step 1: 1 Day

## Commands

```
export SCRAM_ARCH=el8_amd64_gcc10
./gridpack_gen* NAMEOFGP CARDDIR
```

## TODO
- [x] Produce HPlusB gridpack [[Central Production]]
- [x] Reply to sebastian [completion:: 2026-04-15]
- [x] Monitor Sample Production(Step 1 submitted): [completion:: 2026-04-15]
- [ ] Monitor Sample prod 2023
---

## Gridpack Links

- **HPlusCharm gridpack (tarball):** [CERNBox](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/mcm_grid/genproductions_scripts/bin/MadGraph5_aMCatNLO/HPlusCharm_4FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz)
- **Shared link:** [CERNBox share](https://cernbox.cern.ch/s/SgY4MndL4cdsWSB)
- Link to PR: 

---

## Log

### lxplus9 Architecture Issue

Sebastiano flagged that the gridpack was produced on lxplus9 which is not supported. Both HPlusCharm and HPlusBottom gridpacks need to be remade using **lxplus8**. See the [OS selection guide](https://cms-generators.docs.cern.ch/how-to-produce-gridpacks/mg5-amcnlo/#selecting-the-right-os). This architecture mismatch was likely also causing the earlier environment issues.

### Resolution

- [x] Reproduce gridpack with lxplus8
- [x] Reproduce gridpack with new cards
- [x] Gridpack updated and uploaded

Waiting for Sebastian's reply

### Issue with Oneloop
The gridpack production was delayed because a CERN website hosting a required MadGraph dependency (OneLOop) was recently put behind SSO login. This
  broke the automated download during gridpack generation. The same setup worked fine for HPlusCharm in early February before this change was made. A
  workaround using a locally cached copy of the library is now in place.
  `gridpack_generation_fixed.sh` is the fixed script in place
  - Still failed , something wrong with the workaround, the cache directory wasnt populated
  - Failed again. Trying again lol



### 2022
#### postEE

- Done: /HPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/cgupta-Run3Summer22EENanoAODv13-HToWW-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v1-0a036fde9f2884965a184344aedbed78/USER
- HPLUSB: 


#### preEE
- previous postEE samples were actually preEE (350k done) : /HPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/cgupta-Run3Summer22NanoAODv13-HToWW-133X_mcRun3_2022_realistic_ForNanov13_v1-v4-8653679c76b04a5edd42171c9a5e3f96/USER
- hplusb submitted step 3 on 27/04


### 2023

#### post BPix

#### preBPix

- 280k preBPix events done till step4 . Step 5 submitted