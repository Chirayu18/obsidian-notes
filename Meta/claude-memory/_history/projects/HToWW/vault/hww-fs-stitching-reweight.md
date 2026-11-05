---
name: hww-fs-stitching-reweight
description: H+c flavour-scheme treatment = stitching via reweighting (LHCHWG-2026-007); where results/scripts live, acceptance criteria, what not to touch
metadata:
  type: project
---

**Current approach (user decision 2026-09-29):** follow LHCHWG-2026-007 (arXiv:2608.26863) — stitched
signal instead of a flat 3FS/4FS nuisance, implemented by **reweighting** the existing 4FS FxFx H→WW
signal: events with ≥1 GEN c-jet (pT>10, |η|<2.4, decay-cleaned) get w = σ(3FS)/σ(4FS FxFx) binned in
GEN c-jet pT; 0c events weight 1. No new samples.

**Everything is standalone, OUTSIDE the framework, until the user says go** — never touch higgscharm
`outputs/` or production parquets for this. Work dir `/eos/user/c/cgupta/HToWW/fs_unc/`.
Results: `fs_unc/SUMMARY_STITCH.md` (self-written by `gen/run_stitch.sh`), plots `plots/stitch_fxfx/`.
Full write-up: vault `Projects/HToWW/fs-unc-2026-09-29/2026-09-29-fs-3FS-4FS-status.md` §3b–3c.

**Key facts learned:** official 3FS/4FS/4FS-FxFx H→γγ NanoAOD exists for all Run-3 eras (no 3FS H→WW
in Run 3); raw GenJets contain the Higgs decay products, so the c-jet-pT shape does NOT transfer γγ→WW
unless decay-cleaned (81/7 → 7.9/7); the WW 4FS non-FxFx central sample has a 3.4% low σ (XSDB-confirmed),
so compare GG vs WW on shapes/fractions only; the paper never specifies decay cleaning (all γγ).
The derivation definition must be identical when applying the weights to the signal. QUEUED NEXT: exact decay treatment on MiniAOD — subtract Higgs-descendant constituents (slimmedGenJets → packedGenParticles) from official GenJets, keep official hadronFlavour. User rejected BOTH reclustering and the approximate NanoAOD subtraction.

Related: [[Meta/claude-memory/_history/slides/vault/hww-fs-private-results-not-for-ppt|hww-fs-private-results-not-for-ppt]], [[Meta/claude-memory/_history/general/vault/check-das-before-generating|check-das-before-generating]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]]

**State at 2026-09-29 18:25 (before compaction):** (1) `run_stitch.sh` absolute R is WRONG for FxFx —
Σw/N gives pre-merging σ (262.6 vs XSDB 90.67 fb); fractions/shapes fine, fix with XSDB σ; need Run-3 FxFx
XSDB values from the user. (2) MiniAOD job (`gen/mini_fs.py`, `gen/mini_job.sh`) segfaults in FWLite on a
UL18 file — NOT queued yet; debug first (try CMSSW_10_6 for Run-2). Details in the vault note §3c.


**UPDATE 2026-09-30 — MiniAOD exact subtraction DONE (current result, vault note §3d):** R(≥1c) = 3FS/4FS-FxFx ≈ 0.66
in every sample (Run-3 22postEE/2023/2023BPix, Run-2 γγ and WW agree within 0.5%). Results `fs_unc/mini_results/`,
plots `fs_unc/plots/stitch_mini/`, condor submit dir `~/fs_mini_condor/`. FWLite gotcha: never call
`pr.first.key()` on slimmedGenJetsFlavourInfos (segfault) — use `finfo.value(j)` by index. FxFx norm: XSDB =
(Σw/N) × accepted_n/tried_n from GenLumiInfoProduct (validated 3 samples); Run-3 4FS FxFx HTo2G XSDB = 97.62 fb.
2022preEE MiniAOD is tape-only (needs Rucio request, user decision). Open: 0c lead-jet γγ vs WW χ² 486/8.
