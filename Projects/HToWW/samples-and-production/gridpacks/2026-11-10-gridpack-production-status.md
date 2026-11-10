---
tags: [reference]
status: active
date: 2026-11-10
source: laptop
evidence: agent-reported
---
# H+c/H+b gridpacks, 3FS production and send-ready package: status 2026-11-10

**Agent-reported.** HToWW gridpack/production agent, checks over ssh to lxplus984 on 2026-11-10. Nothing sent externally, nothing pushed, nothing deleted. The only write actions on lxplus/EOS are the H+b gridpack rebuild and its fragment/validation configs, which Chirayu asked for on 2026-11-10 (§5).

Background: [[Projects/HToWW/samples-and-production/gridpacks/2026-10-28-4fs-el8-gridpack-and-3fs-production|4FS el8 gridpack + 3FS production]], [[Projects/HToWW/samples-and-production/2026-11-05-3fs-renano-pdf321900|3FS re-NANO]], [[Projects/HToWW/samples-and-production/full-rerun/2026-10-13-GEN-ticket-draft-HplusC-HplusB-WW|GEN ticket draft]], [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-hb-yukawa-fix-crosscheck|H+b Yukawa cross-check]].

Orientation: `Projects/HToWW/gridpack-3fs-2026-10/` (named in the brief) does not exist; the material is in `samples-and-production/gridpacks/`. The earlier T3 thread `7fbb6319-…` returned `thread_not_found`.

## 1. Request package on EOS: unchanged, checksums OK
`/eos/user/c/cgupta/HToWW/mcm_grid/request_package_2026-11/` (CERNBox: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/mcm_grid/request_package_2026-11). `sha256sum -c SHA256SUMS` on lxplus984: all 6 OK. Newest mtime in `mcm_grid/` before today's H+b work: 2026-11-04 23:57.

| file | bytes | SHA256 | cross-check |
|---|---:|---|---|
| `3FS/HPlusCharm_3FS_MuRFScaleDynX0p50_HToGG_M125_…_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz` | 50,382,316 | `3cbbb8dd2704316bb2e5456887beb77b8d7e165e81e1b1e20744fd0acb0a33db` | = official cvmfs file (same sha) |
| `3FS/HPlusCharm_3FS_HToWWTo2L2Nu_13p6TeV_fragment.py` | 2,140 | `e4e9fd52bd7eed19e36a7949f7d88ac5119635fc20510b4eb1bb3a662085daa5` | = `/eos/home-c/cgupta/HToWW/fs_unc/gen3fs_ww/python/` copy |
| `3FS/hplusc-gridpack-3fs_r2.pdf` | 1,195,262 | `2b3d73b85eb526ace9916914e217ff0c0047512ec3da180ee68ee667cf50d2dc` | = vault `gridpacks/deck/` copy |
| `4FS/HPlusCharm_4FS_MuRFScaleDynX0p50_M125_…_amcatnloFXFX_pythia8_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz` | 44,673,084 | `62f9e155a30e2f475dc65f4514e450c7633471ba59ba6dc40908cb30a45f6ae8` | = `gp_fix_4fs/.../bin/MadGraph5_aMCatNLO/` (repacked 2026-10-28) |
| `4FS/HPlusCharm_4FS_FxFx_HToWWTo2L2Nu_13p6TeV_fragment.py` | 3,124 | `0baa0fdd7234764846250bd6f6a690fd2f70bbdc3399add31d8c934d4da045f5` | — |
| `4FS/hplusc-gridpack-4fs_r2.pdf` | 504,635 | `767374441a12815bca34e325e55d9da0744f925ffb2120f013f51e9389646cb4` | = vault `gridpacks/deck/` copy |
| `superseded/hplusc-gridpacks-3fs-4fs_r1.pdf` | 1,659,248 | `4b13cae3…16ab69` | not in SHA256SUMS; superseded, do not send |

## 2. CRAB / production state
- Grid proxy was expired at first check (`/afs/cern.ch/user/c/cgupta/x509up`, timeleft 0). Chirayu renewed it (192 h).
- `crab status` still **could not run**: the CRAB client tried to delegate to MyProxy (`myproxy-init … -y ~/.globus/userkey.pem`) and failed with "Couldn't read user key", since that needs the key passphrase. Not worked around. Current CRAB/DAS state is therefore **unknown**.
- Last logged status, from `crab.log` in `/eos/user/c/cgupta/HToWW/freshprod_3fs/<era>/chain/crab_projects_chain/*/`:

| task | logged at (UTC) | finished / total | failed |
|---|---|---|---|
| 2022preEE v1 | 11-05 05:03 | 1262 / 1290 | 28 |
| 2022postEE v1 | 11-04 12:37 | 4120 / 4310 | 190 (rerun as ext1) |
| 2022postEE ext1 | 11-05 05:03 | 167 / 190 | 23 |
| 2023preBPix v1 | 11-04 12:38 | 2870 / 2870 | 0 |
| 2023postBPix v1 | 11-05 05:03 | 1518 / 1530 | 12 |

  9937 of the 10,000-job target finished; the 63 missing = 28 + 23 + 12, which reconciles "9.94M of 10M, 63 failed". DAS count 9,936,966 is from 2026-11-05 ([[Projects/HToWW/2026-11-05-route-b-stitching-implementation|Route B note]]), not re-queried.
- Re-NANO LHA 321900 (5 tasks, `freshprod_3fs/renano_pdf321900/`): logs end at submission (11-05 09:46). State unknown.

## 3. Stale or missing for sending
1. Package 3FS PDF predates `deck/3fs.html` (Nov 5 09:52): `pdftotext` finds no "321900"/re-NANO line. Deck is keeper-owned; not touched.
2. `[N events]` per era for the 3FS request: open, Chirayu.
3. 4FS fragment `args` still points at the EOS gridpack, not cvmfs.
4. 4FS gridpack validated at LHE+GEN only (~10k events), not SIM/RECO.
5. H+b: rebuild started 2026-11-10 (§5), not yet validated.
6. `LHEPdfWeight` empty in 3FS NanoAOD; re-NANO state unknown.
7. 10/21 contacts draft is out of date (says private production "starting").
8. CERNBox sharing to named recipients not checked; a share needs Chirayu's OK.

## 4. Sebastiano's question (Mattermost, 2026-11-10 16:18) and draft reply (NOT SENT)
He asked whether Chirayu is happy to stop the still-running (not fully produced) samples and rerun them with the fixes. A recommended reply was given to Chirayu in the T3 thread: yes in principle; H+c 4FS gridpack + fixed fragment ready (LHE+GEN validated only); H+b gridpack being rebuilt; asks which of the seven requests (H+c -02684, -02600, -02468; H+b -02697, -02645, -03356, -02517) are still in production; asks how to get the gridpack to cvmfs. Assumes he means the central requests, not the private 3FS production; Chirayu to confirm. A separate T3 thread was opened for the H+c slides to Sebastiano.

## 5. H+b 5FS FxFx gridpack rebuild (started 2026-11-10, Chirayu's request)
- **Cards:** `/eos/user/c/cgupta/HToWW/mcm_grid/genproductions_scripts/bin/MadGraph5_aMCatNLO/HPlusB/` copied to `gp_fix_hb/cards/HPlusBottom_5FS/`. `cmp` (lxplus984): extramodels, mg5amc.patch, param_card, run_card and proc_card are byte-identical to the central H+b→WW gridpack `InputCards/` (`/cvmfs/cms-griddata.cern.ch/phys_generator/gridpacks_tarball/pp/13p6TeV/madgraph/HPlusBottom/HPlusBottom_5FS_…_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`); against the official clean γγ gridpack (`/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/HPlusBottom_5FS_MuRFScaleDynX0p50_HToGG_M125_…_amcatnloFXFX_…tarball.tar.xz`) all identical except the proc_card `output` name (HToGG). The γγ gridpack's runcmsgrid.sh has the "SAMPLE-SPECIFIC CHANGE … Skipping systematics" lines (l.149–150). The patch contains `rwgt_muR_dep_fac` (4 matches), so the fix triggers.
- **Scripts:** `gp_fix_hb/genproductions_scripts/` = rsync of the patched `gp_fix_4fs/genproductions_scripts/` minus the HPlusCharm build products (`diff -rq` shows nothing else).
- **Build:** `gp_fix_hb/build.sh` (same as 4FS: `gridpack_generation.sh … "" local ALL el8_amd64_gcc10 CMSSW_12_4_8`, NB_CORE=8), run in tmux `gphb` on **lxplus984** under `cmssw-el8`, started 15:28:40 CET; log `gp_fix_hb/build.log`. The 4FS build took ~2.5 h.
- **Fragment:** `gp_fix_hb/HPlusBottom_5FS_FxFx_HToWWTo2L2Nu_13p6TeV_fragment.py` = central `HIG-Run3Summer22EEwmLHEGS-02645` fragment (saved at `/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/ticket/mcm_fragments/`) + the three JetMatching lines, `args` → rebuilt EOS gridpack. `diff` vs the central fragment shows only those changes.
- **Validation configs (prepared, not run):** `gp_fix_hb/validation/val_{NEW,REF}_cfg.py` = the 4FS `val_NEW_cfg.py` (LHE,GEN,NANOGEN, 2023BPix conditions) with appended overrides for the gridpack (NEW: rebuilt; REF: official clean γγ H+b 5FS FxFx) and the H+b processParameters above. Running them needs condor jobs, which need Chirayu's OK.
- **Not done yet:** build completion and sanity (σ vs γγ gridpack, MetaData present, runcmsgrid.sh executable), validation, H+b slides.
- Chirayu replied "Yes, do the H+b rebuild" to the question about condor validation; taken as OK to submit the H+b validation after the build passes its sanity checks (stated back to him).

## 6. H+c 3FS gridpack rebuild on the latest genproductions_scripts (started 2026-11-10, Chirayu's request)
- **Scripts:** fresh clone of `https://gitlab.cern.ch/cms-gen/genproductions_scripts.git` master `cad21c2` (2026-11-05; recorded in `gp_fix_3fs/genproductions_scripts.COMMIT`), patched with `mcm_grid/gp_fix_patch.py` (all three asserts passed). Upstream changes since our `8b10560` base (174 commits) relevant to MG NLO gridpacks: new `Utilities/check_lhe_weights.pl` LHE weight-count check run by `runcmsgrid_NLO.sh` and packed into the tarball; MadSpin seed fix; `/eos/home-` path no longer fatal. MG5_aMC is still **2.9.18**; the blocks the fix patches are unchanged. The 4FS (validated) and H+b builds stay on `8b10560`.
- **Cards:** `InputCards/` of the official 3FS gridpack (`/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/HPlusCharm_3FS_MuRFScaleDynX0p50_HToGG_M125_…_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`), renamed without `_HToGG` into `gp_fix_3fs/cards/HPlusCharm_3FS/`; `cmp`: identical except the proc_card `output` name. Process `p p > h c c~ [QCD]`, model `loop_sm_MSbar_yb_yc-yc3FS`; patch has `rwgt_muR_dep_fac` (4 matches). The run_card uses `$DEFAULT_PDF_SETS`; check after the build that the resolved lhaid matches the official gridpack (NNPDF31 nf3, 321900 per the re-NANO note).
- **Build:** `gp_fix_3fs/build.sh` (`HPlusCharm_3FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnlo_pythia8`, el8_amd64_gcc10, CMSSW_12_4_8, NB_CORE=8), tmux `gp3fs` on **lxplus926** (lxplus984 had load ~78), `cmssw-el8`, started 15:49:54 CET; log `gp_fix_3fs/build.log`.
- **Then:** sanity checks as for H+b, plus does the new `check_lhe_weights.pl` pass with internal-reweighting weights; LHE+GEN validation vs the official 3FS gridpack with the 3FS WW fragment (condor, needs OK).
