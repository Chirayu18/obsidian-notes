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

## Decisions by Chirayu, 2026-11-05 (verbatim intent, recorded by the worker)
1. **H+c normalisation: use NNLO.** This supersedes the 2026-09-30 "shape-only, NLO, no NNLO normalisation" decision (`hww-fs-decision-shape-only`). The 30% `xsec_hplusc_4FS_5FS` lnN stays dropped.
2. **Thomas's ttH lepton-MVA working points:** adopt them for Run A, together with the ONNX evaluation from `framework/optimization`.
3. **Framework speed-ups:** to be done by a separate agent.
4. **Baseline commit on `hww-analysis`:** approved. It must include the untracked `lhe_norm.py`, `lhe_yukawa_fix.py`, `analysis/data/lhe_yukawa/` and `analysis/data/fs_shape/`.
5. **Run A submission:** OK.
6. **Run B stitching:** official LHCHWG-2026-007 split, with jet radius R = 0.4 and |η| < 2.5 for the 10 GeV c-jet split.
7. **Source paper for the split:** to be found online and catalogued.
8. **Private 3FS production: accepted as is,** 9,936,966 / 10M events. No resubmission of the 63 failed jobs or of the refused 2022preEE `_ext1`.
9. **BR(H→WW) = 0.2152** used for the WH cross sections: an agent checks it against a source.
10. **H+b scale-weight (Yukawa) fix:** an agent cross-checks it. The result goes to the existing `full-rerun` deck, built by the keeper.
11. **GEN re-production request for the central H+c/H+b weights:** deferred.
12. **Fixes for Saranya** (see [[Projects/HToWW/framework/2026-11-05-saranya-hczz-branch-comparison]]): recorded only, not sent.
13. **Vault commit `9ea0bf0`:** stays as is (Co-Authored-By trailer, not amended).
14. **Threads "Opus review HToWW organization" and "Htoww_local ⑂":** no action.

## Progress, 2026-11-05 (worker)

### ttH lepton-MVA port (decision 2)
- **Code:** `analysis/leptonmva/tth.py` builds vectorised features and scores them with ONNX Runtime 1.23.2, using the BRANCH_LT graphs plus `meta.yaml` (sha256 of the ONNX and XML files).
  - Enabled by the `tthMVA` object correction. The scores are computed on NanoAOD-level inputs before muon/electron scale and smearing, and reused by every shift pass.
  - The working points are in `working_points.py`; the HWW/latinos SFs are in `muon.py` and `electron.py`; the SF files are in `analysis/data/{muon_HWW,electron_HWW}`, copied from `tvl/MVA`.
- **Validation:** ONNX vs TMVA-exact gives max |Δ| = 3.05e-7 (μ, 24,484 leptons) and 3.27e-7 (e, 25,713), including all tie-sensitive leptons. Unit test: `TestTthMVA`, against `tests/data/tthmva_ref_fixture.npz`.
- **Fixes vs Thomas's code:**
  - muon HWW SFs now use signed η; the tables are binned in −2.4…2.4, and Thomas passed |η|;
  - no φ argument for the 2023 electron SFs; these JSONs have none, so his 2023 call would raise;
  - supercluster η for the electron SF.
- **Open questions:**
  - SF provenance and factorisation, to check with Thomas. Is `cut_MediumID_tthMVA_Run3` measured on top of the POG Medium ID SF, which is applied as well (as in his config)?
  - The v11 event MVA was trained with the old tight/wp80iso leptons, so it needs retraining before the limit.

### Other changes and tests
- **NNLO H+c:** the 4FS H+c xsec is 0.0016626 pb in all 4 eras (0.0022141 × 0.1664/0.2216). Backups are `*.pre_nnlo_hc`.
- **Tests:** `tests/test_allfix.py` has 34 tests; all pass, with 1 skipped (b-hive reference, needs EOS).
- **Smoke tests:** single-file, 2022, `hww_allfix_4fs`, all EXIT=0.

  | sample | wall time | RSS | nominal rows |
  |---|---|---|---|
  | H+c | 51 s | 0.91 GB | 423 (563 on 11-04 with the old leptons, −25%) |
  | TTbar | 1:57 | 1.13 GB | 5491 |
  | SingleMuon 2022C | 1:20 | 0.98 GB | 4 (was 7) |

  New SF variations (Up/nom) on H+c: `CMS_eff_m_promptMVA` 1.0036 and `CMS_eff_e_promptMVA` 1.0097.

### Baseline commit
- `hww-analysis` commit **`0850e51`**, 74 files, not pushed. The message is in `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/commitmsg_baseline_20261105.txt`.
- Left out: compiled `lhe_yukawa/{as2,tab}`, CSVs, root scratch scripts, `outputs/`, `CLAUDE.md` and backups.

### Run B source paper (decision 7)
- The source is LHCHWG-2026-007, arXiv:2608.26863, §4.4. Verbatim: "phase-space splitting based on the number of charm jets with pT>10 GeV"; "Nc-jet=0 from the 4FS-FxFx sample and … Nc-jet>=1 from the 3FS sample".
- §4.4 cites no earlier paper for the split itself. It only cites arXiv:2510.18815 (the bbH NNLO/NLO K-factor) and arXiv:2107.01226 (the theory motivation).
- The jet radius and |η| are not given. R = 0.4 and |η| < 2.5 is Chirayu's choice (decision 6).
- The PDF is already in `References/HToWW/2026-LHCHWG-2026-007_Hc_flavour_schemes_arXiv2608.26863.pdf`.

### BLOCKER for the Run A submission: EOS quota
`eos quota /eos/user/c/cgupta`: 919 GB used of a 1.00 TB logical quota (91.9%), about 81 GB free. The last full production plus its ttsyst run used 266 GB. Space by directory:

| path | size |
|---|---|
| `higgscharm/outputs/hww_combine_full` | 198 GB |
| `higgscharm/outputs/hww_combine_2dcat` | 179 GB |
| `higgscharm/outputs/hww_combine_full_ttsyst` | 68 GB |
| `HToWW/CMSSW_13_0_13` | 78 GB |
| `flashjet` | 163 GB |
| `EPR_task` | 126 GB |

Nothing is deleted. The submission is held until Chirayu frees or redirects the space.

### Agent results folded in (2026-11-05, worker)
- **BR check** ([[Projects/HToWW/samples-and-production/2026-11-05-br-hww-xsec-check]]): BR(H→WW) = 0.2152 is the mH = 125.09 value (YR4 Table 177). H+c NNLO by ratio = 0.0016626 pb is confirmed. The remaining WH entries were aligned to the 125.09 set: `WplusH_WtoLNu` 0.006601 and `WminusH_Wto2Q` 0.008722.
- **H+b Yukawa cross-check** ([[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-hb-yukawa-fix-crosscheck]]): the scale fix is VALIDATED (agent check).
  - **Side finding:** PDF/αS for H+c and H+b are biased by lhe_norm + replica centring.
    - H+b PDF Up: 1.0145 vs 1.0217 clean.
    - H+b αS Up: 1.000 vs 1.030 clean.
  - **Needs Chirayu**, one of three options:
    1. per-event r normalisation for the PDF/αS members;
    2. keep the current behaviour;
    3. flat lnN instead.
- **Speed-ups** ([[Projects/HToWW/framework/optimization/2026-11-05-speedup-patches]]): patches 01–04 applied. The output is byte-identical in the agent's seeded test. Job time is −33% (46.5 s → 31.1 s).
  - Re-tested after applying: 34 unit tests pass, and the 3 smoke tests give EXIT=0. Rows: H+c 423, TT 5489 (5491 before; the muon-smearing RNG is unseeded), SingleMuon 4.
  - Open decisions: `request_cpus = 2`, seeding the muon RNG, TRAIN/RUN mode, and gen columns only for negrw.
- **Commit:** `hww-analysis` commit **`40d0e3e`** (speed-ups + WH alignment) on top of `0850e51`. Not pushed.
