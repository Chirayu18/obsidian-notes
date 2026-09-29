---
tags: [reference]
status: active
date: 2026-09-29
source: laptop
---

# H+c flavour-scheme (3FS/4FS) uncertainty — status & where everything is

Method: FS "stitching" (T. Bevilacqua, 23-06-26, [slides](https://indico.cern.ch/event/1645713/contributions/7018110/attachments/3301014/5905014/H+c_towards_a_more_precise_simulation_Tiziano_Bevilacqua_260623.pdf), slide 22):
≥1 GEN c-jet → 3FS, else 4FS. We measure R = σ(3FS)/σ(4FS) in the ≥1 GEN c-jet region,
binned, and propagate it as a per-event signal shape nuisance `xsec_hplusc_3FS_4FS`
(Up = R, Down = 2−R) replacing the flat `xsec_hplusc_4FS_5FS = 1.30` lnN.
GEN c-jet = GenJet hadronFlavour==4, pT>20, |η|<2.4.

## Gridpacks — no generation needed
Central, on cvmfs (non-FxFx pairs exist for both runs):
- Run 3: `/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/HPlusCharm_{3FS,4FS}_…_HToGG_…_amcatnlo_pythia8_…tarball.tar.xz`
- Run 2: `/cvmfs/…/UL/13TeV/madgraph/V5_2.6.5/HPlusCharm_{3FS,4FS}_…_{HToGG,HToWWTo2L2Nu}_…_amcatnlo_pythia8/v1/`

**Card-level check (done):** Run-2 HToGG ≡ Run-2 HToWW (proc/run/param/model cards and
patch byte-identical; decay is done in Pythia, not in the gridpack). Run-2 ≡ Run-3 except
`ebeam 6500→6800`. So the HToGG-labelled Run-3 gridpack is valid for our H→WW signal.

## Run-3 result (400k events per scheme, DONE)
| | 3FS | 4FS | R |
|---|---|---|---|
| σ incl | 54.9 fb | 83.2 fb | **0.659** |
| σ (≥1 GEN c-jet) | 14.5 fb | 18.3 fb | **0.789** |
| neg-weight frac | 39.6% | 13.1% | |

R vs leading GEN c-jet pT: 0.72, 0.85, 0.86, 0.83, 0.83, 0.77, 0.72 (bins 20/30/45/60/80/110/150/∞).
Inclusive 34% gap (AN: "~30%", its Table 1 → 38%); only **21%** in the ≥1c region.

## Running unattended on lxplus (started 2026-09-29 16:20, node lxplus966)
- `fschain` tmux → `logs/chain.log`: baseline card must equal production → baseline limit (1034?)
  → inject weights into a **copy** of the signal parquet → `fsunc` card → new limit.
- condor **9472750** (160 jobs): Run-2 HToGG & HToWW, 3FS & 4FS, 200k each.
- `fspost` tmux → `logs/post_r2.log`: waits for 9472750 → Run-2 ratios → comparisons
  (GG vs WW = decay independence; Run 2 vs Run 3 = energy) → plots → **`SUMMARY.txt`**.

**Read first:** `/eos/user/c/cgupta/HToWW/fs_unc/SUMMARY.txt`, plots in `…/fs_unc/plots/`.

## Caveats
- Signal weights use the **reco** candidate c-jet pT, as a proxy for GEN c-jet pT: the grid
  proxy had expired, so the exact GEN pass (`hww_2dcat_fsgen`, `select_gen_fs`) couldn't run.
  R is flat, so the proxy should matter little — needs `voms-proxy-init`, then one condor pass.
- The Run-2 gridpacks (CMSSW_10_6, gcc700/820) run inside CMSSW_12_4_26; this was NOT
  verified before submission. If jobs fail, SUMMARY shows 0 files → rerun in CMSSW_10_6.
- If tmux dies (node reboot / token expiry), rerun `bash …/fs_unc/gen/post_r2.sh` and
  `bash …/fs_unc/gen/chain.sh` — both are idempotent.

## Files
Scripts: `/eos/user/c/cgupta/HToWW/fs_unc/gen/` (derive_ratio, apply_weights, plot_ratio,
compare_ratios, chain.sh, post_r2.sh, job.sh, fragments). Condor: `~/fs_unc_condor/`.
Workflows (uncommitted, repo `hww-analysis`): `hww_2dcat_fs{base,unc,gen}.yaml`;
`select_gen_fs` added to `analysis/selections/object_selections.py`.
Mirror outputs: `outputs/hww_2dcat_fsunc` (symlinks to production; only the signal mva
parquet is a real copy). Production files are never written to.
