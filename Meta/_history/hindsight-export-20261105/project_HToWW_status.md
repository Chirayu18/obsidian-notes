---
source: Hindsight research bank document `project:HToWW:status`
exported: 2026-11-05
status: superseded
note: verbatim export before Hindsight was retired; dated snapshot, not live state
---

# HToWW coordination status
Revision: hindsight-decks-3. Updated: 2026-11-04T23:12Z. Previous: hindsight-decks-2 (22:55Z).
Designated writer and single continuation owner: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:534e608eec40b30d1c22f71c819e6b774031bef8b3a95577b35571bfc4b85d39>. See workflow:current for rules. Live jobs and latest results are NOT verified by this record.

## STATE: ALL WORK STOPPED on Chirayu's order (2026-11-04 ~23:08Z)
Nothing committed, pushed, submitted to condor/CRAB, or deleted by any HToWW agent. No agent is to resume until Chirayu says so.
- S1 HTOWW-TTHMVA-MERGE <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:9dd1af08139499d2ae198e0f7c90b8ba63b375b29911414305bd1711692a4eea>: interrupt requested 23:08Z while running (132 items); NO report delivered; any partial files under /eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/proposals/HTOWW-TTHMVA-MERGE/ are unreviewed.
- S2 HTOWW-FRAMEWORK-SPEEDUP <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:f017c4581a84acca472d1a72cc3c62c678d275a92132becec5443ffead80d5c3>: interrupt requested 23:08Z while running (81 items); NO report delivered; partial proposals/HTOWW-FRAMEWORK-SPEEDUP/ unreviewed. Interrupt completion not re-verified by the lead.
- S3 HTOWW-RUNB-INPUTS <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:526f75a45954a1ce6db05f30898aa82463a5664c2798ababadc800e836adf493>: completed 22:57Z, report delivered to the FULLFIX worker.
- FULLFIX worker <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:0a085f5f6123e902dae945a412fbaac27624ff7a2dd345a25861a529c4e14fb5> (Opus 5.5, auto): idle, last turn completed 22:57Z.
- 3FS/4FS continuation <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3A28e42937-c585-4e38-9735-d9d3e7b1c43c%3Adelegate-task%3A93370e6b-1d08-4a22-a029-483a691de3ef>: completed 22:57Z (deck split resumed after the quota failure; outputs not inspected by the lead).
- Audit HTOWW-RECOVER-OPEN-WORK-20261104 <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:f0298b4953a87de847ff692d6322ccc14c493760c8c87045b644a43abcb4ccee>: failed 14:30Z (quota), not resumed, no result.

## Task HTOWW-FULLFIX-RERUN-20261104 (higgscharm, branch hww-analysis)
Repo: /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm (laptop mount /home/cgupta/mnt/lxplus/...). Single edit owner: the FULLFIX worker. Backup: /eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/.
Run A prep (checkpoint 13:15Z): 31/31 unit tests (tests/test_allfix.py), 3 local smoke runs OK, new workflow analysis/workflows/hww_allfix_4fs.yaml on hww_combine_full.
CORRECTION: the 2026-10-06 Type-1 MET sign fix in jerc.py had the wrong sign (corr -0.48 vs NanoAOD JESUp; corrected +0.48; full pipeline +0.68). Fixed; nothing reprocessed with the wrong version.
Chirayu's answers 14:32Z (applied by the worker after 22:48Z, per its report): DoubleMuon 2022C as before (zero mask); JER propagates to MET; WH xsec from LHCHWG; Run B stitching = official split; build on latest workflow; do not commit yet; also asked for text rundown (given in worker thread) and decision-5 explanation (given in worker thread).
APPLIED 22:57Z (uncommitted): the eight zero WH xsec entries in the four era fileset YAMLs now hold LHCHWG-2024-001 (arXiv:2402.09955 Table 3) values: WminusH_WtoLNu 0.004215 pb, WplusH_Wto2Q 0.013659 pb (mH 125.09, BR(H->WW)=0.2152 NOT verified against source). Backups <file>.pre_whxsec in the backup dir.
S3 finding (arXiv:2608.26863 / LHCHWG-2026-007, Sec. 4.4/5.3, Table 3): split on number of charm jets with pT>10 GeV; Ncjet=0 from 4FS FxFx, Ncjet>=1 from 3FS; each part normalised to its own sample, whole rescaled to NNLO ccH (MiNNLOPS 4FS). R and |eta| for the split not stated. Our H+c xsec 0.0022141 pb matches NLO 4FS (~97.6 fb) not NNLO (~73.3 fb, implying ~0.00167 pb, about 24% less signal); the dropped 30% xsec_hplusc_4FS_5FS lnN assumed NNLO. Worker's own conversion; BR(H->gg) unchecked.
Unvalidated: H+b scalevar (P0-16); ctag2d one-hots through torch inference; Run-3 jetveto PF-muon term. Run B not started. Thomas lepton-MVA/ONNX merge and framework speed-ups NOT assessed (S1/S2 stopped).

## Open decisions (Chirayu)
1 Move H+c xsec to NNLO (~0.00167 pb) in the four 4FS H+c entries, or stay at NLO and restore a normalisation uncertainty.
2 Run B split: assume R=0.4 and |eta|<2.5, or ask the note authors.
3 Decision 5: gen_chad1_pt vs gen_cjet1_pt and Down=2-R vs one-sided (explained in worker thread).
4 Whether to restart S1/S2 (lepton-MVA merge, speed-ups) before Run A.
5 Approval of any baseline commit and of the Run A submit commands (not yet presented).

## Provider quota
2026-11-04 22:59Z Claude 5h 54%, 7d 39%; earlier 5h limit hit ~14:24-14:32Z (Claude) and 14:30Z (Codex) caused the 14:35Z failures of the FULLFIX, audit and 3FS threads. No provider/account change by the lead.

## Next action
None until Chirayu restarts work. On restart: confirm S1/S2 interrupts landed, review partial proposals, get decisions above, then FULLFIX worker presents Run A submit commands for explicit OK.

