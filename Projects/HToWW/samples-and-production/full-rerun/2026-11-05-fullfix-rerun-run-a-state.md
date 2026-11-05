---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---
# Full-fix rerun (Run A / Run B): state as of 2026-11-05

Task HTOWW-FULLFIX-RERUN-20261104.

All of the edits below are uncommitted and unvalidated by Chirayu. Nothing has been submitted, committed, pushed or deleted. Every number is agent-reported.

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

## Read-only helper runs (2026-11-04)
- **HTOWW-RUNB-INPUTS:** completed. It produced the WH and stitching numbers above.
- **HTOWW-TTHMVA-MERGE and HTOWW-FRAMEWORK-SPEEDUP:** both were interrupted at about 23:07Z on 11-04 before they reported.
  - No patches reached `proposals/` on EOS.
  - TTHMVA-MERGE had a port assembled in a scratch clone and 6 unit tests passing.
  - SPEEDUP had the `dump_parquet` patch applied to a copy.
  - Both scratch locations were node-local and are not recoverable from here.

## Run B (private 3FS + central 4FS)
- **Production:** 9,936,966 / 10M events in DAS. 2022postEE needs both the main dataset and `_ext1`.
- **Filesets:** none of the 3FS samples are in the higgscharm filesets yet.
- **Status:** on hold until the open issues above are settled.
