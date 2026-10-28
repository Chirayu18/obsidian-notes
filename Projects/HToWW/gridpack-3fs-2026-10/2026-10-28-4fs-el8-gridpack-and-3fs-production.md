---
tags: [reference]
status: active
date: 2026-10-28
source: lxplus
---
# H+c 4FS el8 gridpack rebuild and private 3FS H→WW production

## 4FS FxFx gridpack (el8), validated

The broken scale and PDF weights of our earlier el8 H+c 4FS FxFx gridpack came from the build scripts alone. The physics cards are byte-identical to those of the official clean H→γγ gridpack.

The cause has two parts:
- `prepare_run_card` in genproductions_scripts appends `False = reweight_scale`, `False = reweight_PDF` and `True = store_rwgt_info` to every NLO run card.
- `runcmsgrid.sh` then computes the variations with the python systematics module, which does not include the running charm Yukawa factor that the `_mg5amc.patch` puts into MG5_aMC's internal reweighting.

The patched copy of the scripts is in `/eos/user/c/cgupta/HToWW/mcm_grid/gp_fix_4fs/genproductions_scripts`, made by `mcm_grid/gp_fix_patch.py`. When the cards carry an `rwgt_muR_dep_fac` patch, it keeps the internal reweighting and uses a runcmsgrid that skips the systematics step, exactly as the official gridpack does. Every other process builds as before.

The gridpack was built on el8 with CMSSW_12_4_8. The integrated σ is 155.5 ± 0.4 fb, identical to the official gridpack. Two packaging mistakes were caught in testing and fixed:
- The first build lacked the MetaData folder.
- The template for runcmsgrid.sh was not executable, so the tarball was repacked on 2026-10-28 with the same file list and the execute bit set.

The validated gridpack is
`/eos/user/c/cgupta/HToWW/mcm_grid/gp_fix_4fs/genproductions_scripts/bin/MadGraph5_aMCatNLO/HPlusCharm_4FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`.

The validation against the official gridpack, with the same H→WW fragment and about 10k events each, agrees within statistics in all quantities (see [[plots]]).

## Private 3FS H→WW production (10M events)

No Run 3 3FS H→WW sample exists centrally. The official Run 3 3FS H+c gridpack has an undecayed Higgs and clean weights, so it is reused with an H→WW decay in Pythia.

To save space, each CRAB job runs the whole chain on the worker and keeps only MiniAOD and the published NanoAOD:
- the chain is LHE+GEN+SIM, DR+Premix, RECO, MiniAOD, NanoAOD;
- 1000 events per job;
- the 2022 jobs switch to CMSSW_13_0_13 (postEE) or 13_0_17 (preEE) for MiniAOD and Nano;
- the scripts are `freshprod_3fs/make_chain.py` and `freshprod_3fs/run_chain.sh`.

The events are split by luminosity. Status on 2026-10-28:

| era | events | status |
|---|---|---|
| 2022preEE | 1.29M | 1253/1290 jobs published, the rest resubmitted |
| 2022postEE | 4.31M | 4120/4310 published; the task's resubmission did not take, so the missing 190k events run as `…-3FS_ext1` |
| 2023preBPix | 2.87M | submitted 2026-10-28 |
| 2023postBPix | 1.53M | submitted 2026-10-28 |

The published datasets are `/HPlusCharm_3FS_HToWW_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8/cgupta-<era tag>-3FS-<hash>/USER` in prod/phys03.
