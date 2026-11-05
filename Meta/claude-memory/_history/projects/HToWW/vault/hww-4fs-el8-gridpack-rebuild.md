---
name: hww-4fs-el8-gridpack-rebuild
description: Fixed el8 H+c 4FS FxFx gridpack rebuild (started 2026-10-23) in mcm_grid/gp_fix_4fs; patched genproductions keeps internal reweighting + skips python systematics when the cards carry rwgt_muR_dep_fac
metadata:
  type: project
---

The scalevar bug in our el8 4FS gridpack (MG 2.9.18) was purely the BUILD SCRIPTS.
- `bin/MadGraph5_aMCatNLO/Utilities/gridpack_helpers.sh: prepare_run_card` appends `False = reweight_scale`,
  `False = reweight_PDF` and `True = store_rwgt_info` for every NLO gridpack.
- `gridpack_generation.sh` copies `runcmsgrid_NLO.sh`, which runs the python `systematics` step.
- The physics cards (proc/run/param/patch/extramodels) are byte-identical to the official clean H->gg 4FS FxFx gridpack
  (MG 2.9.9, slc7). That gridpack also has the Higgs undecayed (`p p > h [QCD]` + `p p > h j [QCD]`), so it works for WW as is.

Fix:
- Patched copy at `/eos/user/c/cgupta/HToWW/mcm_grid/gp_fix_4fs/genproductions_scripts`, made by `mcm_grid/gp_fix_patch.py`.
  When `<name>_mg5amc.patch` contains `rwgt_muR_dep_fac`, it appends True/True/False instead, and copies a new
  `runcmsgrid_NLO_internalrwgt.sh` with the official "SAMPLE-SPECIFIC CHANGE ... Skipping systematics".
- Cards are in `gp_fix_4fs/cards/HPlusCharm_4FS`.
- Build: tmux `gp4fs` on lxplus966, `cmssw-el8`, CMSSW_12_4_8, NB_CORE=8, log `gp_fix_4fs/build.log`.
  Pass "" as the rundir: `readlink` turns /eos/user into /eos/home-c and the script refuses /eos/home-X.
- Validation plan: LHE+GEN on condor vs the official gg gridpack with the same (JetMatching-complete) fragment. Check:
  - weights: r ~ 1;
  - event-class mix: 1-jet share ~27%, forward 1-jet ~6.7%.

Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-central-signal-lhe-weights-broken|hww-central-signal-lhe-weights-broken]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-3fs-private-production|hww-3fs-private-production]].

**2026-10-23/28 outcome:**
- Build 1 lacked `MetaData/` (pdflist_4f_run3.dat): the pilot run crashed, but the script still said "success" and packed a 12 MB tarball. Copy the WHOLE repo layout (bin, MetaData, Utilities).
- Build 2 OK: sigma 155.5 ± 0.4 fb, identical to the official gg (155.5).
- BUT its runcmsgrid.sh was NOT EXECUTABLE (exit 126 'Permission denied'): Python write_text made the template mode 644.
  - Fixed: gp_fix_patch.py chmods it now.
  - The tarball was repacked on 2026-10-28 with the identical file list (incl. merge.pl) + exec bit; the old copy is kept as `*_noexec.tar.xz`.
- Repacked gridpack runs: local 300-event test, exit 0.
- Condor validation: REF done (cluster 9583652, ~1000 evts/job after FxFx); NEW resubmitted as cluster 9612149, ~10 jobs.
  - Each job xrdcp's the tarball into the scratch dir.
  - Analysis: `validation/compare.py` (b_hive env) writes plots/ + summary.md.

**VALIDATED 2026-10-28** (compare.py, ~10k events each after FxFx), rebuilt vs official:
- PDF replica/member0 0.999 in both;
- scale sigma ratios within 0.7%;
- 1-jet share 0.269 vs 0.268; forward 1-jet 0.066 vs 0.072 ± 0.005;
- matched sigma 97.4 ± 1.6 vs 96.5 ± 1.6 fb;
- all shapes chi2/ndf <= 1.
Plots were sent to the user; vault note `Projects/HToWW/gridpack-3fs-2026-10/`.
NanoAOD LHEScaleWeight order is (muR,muF) = (.5,.5)(.5,1)(.5,2)(1,.5)(1,1)(1,2)(2,.5)(2,1)(2,2), with index 4 the nominal. NOT MG order.
