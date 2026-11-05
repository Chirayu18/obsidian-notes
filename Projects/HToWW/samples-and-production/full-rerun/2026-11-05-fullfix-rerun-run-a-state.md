---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
source_commit: f26a601058c7ef56d3bb5e2a82840c017a919383
keeper_review: "[[Meta/keeper/2026-11-05-fullfix-review]]"
---
# Full-fix rerun (Run A / Run B): state as of 2026-11-05

Task HTOWW-FULLFIX-RERUN-20261104.

The analysis-repository edits below are uncommitted and unvalidated by Chirayu. The worker reported no analysis submission, commit, push or deletion; the vault note itself was committed as `f26a601`. Every number is agent-reported.

Source: [worker handoff, 2026-11-05 04:17 UTC](t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:0a085f5f6123e902dae945a412fbaac27624ff7a2dd345a25861a529c4e14fb5). Keeper review checks the record and navigation, not the remote implementation or physics. Earlier context: [[Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings]] and [[Projects/HToWW/samples-and-production/full-rerun/2026-10-06-independent-review]].

## Where the files are
- **Repo:** lxplus `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `b7f67ef`. The working tree has uncommitted edits.
- **Backups:** `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/`. This directory holds:
  - the pre-edit diff, a snapshot tarball and the post-edit patch;
  - the `*.pre_whxsec` fileset copies;
  - `hww_allfix_4fs.yaml.pre_drop4fs5fs`.
- **Workflow for Run A:** `analysis/workflows/hww_allfix_4fs.yaml`, a copy of `hww_combine_full.yaml`, which is the latest workflow.

## Run A: what is in the code
- **Bug fixes:**
  - Trigger: SingleMuon 2022C is treated like Muon. DoubleMuon 2022C gets a zero mask, so it still runs but contributes nothing. That was Chirayu's decision 3, "as earlier"; the zero-mask reading is agent-interpreted.
  - c-tag 2D one-hots are derived at inference time.
  - Type-1 MET: the jet selection is fixed, and so is the sign. The 10-06 version anti-correlated with NanoAOD `PuppiMET_ptJESUp`: −0.48 before the fix, +0.48 after (+0.68 for the full pipeline).
  - Jets are re-sorted after JEC.
  - The jet-veto map is enabled.
  - A guard now rejects xsec ≤ 0.
- **3FS/4FS flavour-scheme shape:** `xsec_hplusc_3FS_4FS` applies to the central 4FS H+c. It uses `gen_chad1_pt` (leading c-hadron pT), Down is defined as 2 − Up, and it is shape-only. It changes the SR yield by about ±10.7% (`hplusc_fs.py` + `analysis/data/fs_shape/`).
- **Lnn removed:** the 30% `xsec_hplusc_4FS_5FS` lnN is dropped. Chirayu's decision 6 (2026-11-04): "we use NNLO normalisation now".
- **WH xsec:**
  - The previously zero entries are now filled in all 4 era YAMLs: `WminusH_WtoLNu_Hto2Wto2L2Nu` = 0.004215 pb and `WplusH_Wto2Q_Hto2Wto2L2Nu` = 0.013659 pb.
  - Source: LHCHWG-2024-001 (arXiv:2402.09955) Table 3, 13.6 TeV, mH = 125.09, multiplied by BR(H→WW) = 0.2152 (not re-verified), by BR(WW→2ℓ2ν) = 0.10615 and by BR(W).
  - The two WH entries that were already filled agree with these to within 0.3%, so they were left alone.
- **Unchanged:** JER is still propagated to MET (decision 4: keep it).
- **Tests:** `tests/test_allfix.py` has 31 unittest tests and passed on 11-04. They have not been re-run since the YAML and fileset edits of 11-04/05.
- **Smoke tests:** single-file runs of H+c, TTbar and SingleMuon 2022C passed on 11-04, before the lnN and WH edits.

## Open issues (Needs Chirayu)
1. **H+c normalisation does not look like NNLO.**
   - The fileset has `xsec: 0.0022141` pb (σ×BR(H→WW→2ℓ2ν)). That implies about 97 fb inclusive, which equals the NLO 4FS value of LHCHWG-2026-007 (arXiv:2608.26863, Table 3: 0.2216 fb in H→γγ, divided by BR(γγ)).
   - The NNLO MiNNLOPS 4FS value is about 73.3 fb, which gives about 0.00167 pb, roughly −24%.
   - This conversion is agent-derived. The open choice: either switch to NNLO, or keep NLO and restore a normalisation uncertainty.
2. **Run B stitching: jet radius and |η|.** The official split (LHCHWG-2026-007 §4.4) takes events with N(c-jets, pT > 10 GeV) = 0 from 4FS FxFx and events with ≥ 1 from 3FS. The whole sample is then rescaled to NNLO ccH. The note gives neither R nor |η| for the 10 GeV split. The proposal is R = 0.4 and |η| < 2.5, or ask the authors.
3. **Thomas's ttH lepton-MVA working points** (branch `tvl/MVA`, commits c2da77f … 089825a, not in HEAD): adopt them for Run A or not. This changes the lepton selection, and the v11 MVA was trained without them.
4. **Run A submit commands:** to be drafted after items 1–3, then Chirayu's OK.
5. **Speed-up work (worker's final handoff):** redo the interrupted output-writing assessment or leave it deferred? The worker proposed applying a parquet-output change only after a single-file comparison demonstrates identical output. This is an additional decision, not permission to apply it.

## Read-only helper runs (2026-11-04)
- **HTOWW-RUNB-INPUTS:** completed. It produced the WH and stitching numbers above.
- **HTOWW-TTHMVA-MERGE and HTOWW-FRAMEWORK-SPEEDUP:** both were interrupted at about 23:07Z on 11-04 before they reported.
  - No patches reached `proposals/` on EOS.
  - TTHMVA-MERGE had a port assembled in a scratch clone and 6 unit tests passing.
  - SPEEDUP had the `dump_parquet` patch applied to a copy.
  - Both scratch locations were node-local and are not recoverable from here.
- **Backup follow-up:** the worker's final handoff reports today's analysis-repo diff saved as `tracked_diff_20261105.patch` under the EOS backup directory above. The keeper has not inspected that patch.

## Run B (private 3FS + central 4FS)
- **Production:** 9,936,966 / 10M events in DAS. 2022postEE needs both the main dataset and `_ext1`.
- **Filesets:** none of the 3FS samples are in the higgscharm filesets yet.
- **Status:** on hold until the open issues above are settled.

## Read-only checks, 2026-11-05 (conductor handover items)

### 3FS CRAB tasks

`crab status` was run in a cmssw-el8 container, using CMSSW_12_4_20 from `freshprod/2022preEE`. DAS was queried with `instance=prod/phys03`.

The 3FS production is finished at 9,936,966 / 10M events. The published counts are unchanged since 11-04 12:41Z.

| task | scheduler | failed | published | DAS events |
|---|---|---|---|---|
| 2022preEE_v1 | FAILED (finished) | 28/1290 | 1262 | 1,261,997 |
| 2022preEE_ext1 | **SUBMITREFUSED** | n/a | none | no dataset |
| 2022postEE_v1 | n/a (from DAS) | n/a | 4120 | 4,119,986 |
| 2022postEE_ext1 | FAILED (finished) | 23/190 | 167 | 166,999 |
| 2023preBPix_v1 | n/a (from DAS) | 0 | 2870 | 2,869,993 |
| 2023postBPix_v1 | FAILED (finished) | 12/1530 | 1518 | 1,517,991 |

- No job is running. The 2022preEE `_ext1` resubmit (10-29) was refused by CRAB and never ran.
- Still missing: 28k events in 2022preEE, 23k in 2022postEE `_ext1` and 12k in 2023postBPix. A further resubmit needs Chirayu's OK.

### Scalevar ×2 issue
- **Analysis-side fix: wired in the working tree.** `lhe_norm.py` (Runs-tree mean normalisation) and `lhe_yukawa_fix.py` (per-event running Yukawa) are hooked into `correction_manager.py` and `lhescale.py`. They are enabled via `lhe_renorm_datasets` in `hww_allfix_4fs`.
  - On the 11-04 H+c smoke test the scalevar ratios are 0.91–1.10, not ×2.
  - **H+b is not validated (P0-16).**
- **Some of these files are untracked:** `lhe_norm.py`, `lhe_yukawa_fix.py`, `analysis/data/lhe_yukawa/` and `analysis/data/fs_shape/`. A baseline commit must include them.
- **Gridpack-side fix:** applies only to our private el8 4FS gridpack (`mcm_grid/gp_fix_4fs`). The central samples are still broken at source.
  - The GEN re-production request was drafted (10-13 ticket, 10-21 message). Whether it was sent is not recorded here.

### Conflict with an earlier decision
- The archived memory `hww-fs-decision-shape-only` (2026-09-30, Chirayu) says: keep the 4FS FxFx NLO cross section; no stitching, no NNLO normalisation, no normalisation lnN.
- Chirayu's 11-04 answer was "drop the 30% lnN, we use NNLO normalisation now", plus the official split for Run B.
- The fileset still has the NLO-like 0.0022141 pb.
- Needs Chirayu: confirm that 11-04 supersedes 09-30.

### Not yet checked
- **Saranya comparison follow-ups (10-23 to 10-29):** not checked.
- **"LHC paper" stitching alternative (10-28 sessions):** not found in the vault notes.
