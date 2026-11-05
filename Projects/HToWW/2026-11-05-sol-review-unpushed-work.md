---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# Independent review of recent unpushed HToWW work

**Status: agent-reported.** Sol inspected the live lxplus tree and primary sources and ran the local checks below. Passing software checks does not validate the final physics model, a production, or a limit. Chirayu has not reviewed this report. No analysis-repository commit, push, merge, job submission, deletion, credential renewal or service restart was performed by this review.

## Recent work, in plain language

- The analysis now has a reproducible git baseline for the previously loose fixes: `0850e51`, followed by the speed-up/WH alignment commit `40d0e3e`, both on `hww-analysis`, unpushed. The starting brief's “~25 modified files” is historical: the tracked working tree was clean when inspected; the two commits together change **77 files** relative to `b7f67ef` (`git diff --stat b7f67ef..HEAD`). This review leaves two implementation files and the test file modified, without committing them there.
- Run A (`hww_allfix_4fs`) includes the central H+c/H+b samples, running-Yukawa scale-weight correction, trigger-PD correction, Type-1 MET/JER/electron-smearing changes, top-pT under object shifts, c-tag one-hots, jet veto, and the c-hadron-based 3FS/4FS variation. The old 30% flavour-scheme lnN is removed. The four main era files now use the same H+c NNLO normalization and WH values.
- Thomas's lepton working points have been ported, evaluated with ONNX, with HWW scale factors. The recorded lepton-selection change and v11 training mismatch matter: the event classifier needs retraining before a new limit is trusted. The scale-factor factorization is still unresolved.
- Invalid DY inputs were replaced and their derived file lists rebuilt. This review independently checked all ten replacement lists against their YAML processing, their unique LFNs, and their old backups.
- The H+b worker recorded a substantial scale-weight cross-check, including an exact rebuilt table. This review checked the saved table comparison and result artifacts, but did not independently rerun the full gridpack reconstruction/clean-sample study. Its PDF/αS warning remains consequential.
- Four output/caching speed-ups are applied. Their reported performance gain and seeded full-output equivalence remain worker-reported; this review independently reran the 19-type writer equivalence check and verified that the combined proposal patch reverses cleanly from the live tree. Run A remains unsubmitted in the worker record, blocked on physics choices and EOS capacity. Run B stitching has not been implemented in the reviewed baseline.

## Scope and provenance

Canonical repo: `ssh lxplus`, `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`; host reached through the existing connection: `lxplus921.cern.ch`. Branch `hww-analysis`; reviewed HEAD `40d0e3e`, with baseline `0850e51`. Reviewed tracked changes with `git diff b7f67ef..HEAD`, including the now-tracked `lhe_norm.py`, `lhe_yukawa_fix.py`, Yukawa tables, `eos_io.py`, and `hww_2dcat_fsbase.yaml`.

Read the initial brief and recent messages of the [full-fix thread](t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:0a085f5f6123e902dae945a412fbaac27624ff7a2dd345a25861a529c4e14fb5), including the 11-05 decisions and latest commit/test handoff. These decisions already approve NNLO, the lepton working points, and R=0.4 / |η|<2.5 for Run B; this review did not reopen or change them. No subagents were started.

Vault: ran `git log origin/master..HEAD`, `git status`, and HToWW commit diffs. There were no uncommitted HToWW notes at entry. The HToWW-related commits inspected were `338975c`, `f26a601`, `b687a74`, `fa49200`, `e3a0e4b`, `89ae385`, `05ad599`, `63fb5ab`, `f027bdc`, `4d26800`, `b0fb5a4`, `f4475c7`. Setup/index commits in the unpushed log are outside analysis physics; `6cc4ffd` appeared concurrently and concerns CombineAgent, not HToWW. This is a comparison with the existing `origin/master` ref, not a fresh remote fetch. No sync failure was reported in this session.

`338975c` is a large organization commit: HToWW history has hundreds of path changes and removal of tracked PNG/PDF entries under the new ignore policy. Rename-aware diffs show Combine-agent notes moved to `Projects/CombineAgent/`, not lost. Reviewed its HToWW markdown/path changes and the later deck/status diffs; historical research results were not independently rederived. Keeper-owned READMEs, decks and Meta were left untouched. Semantic search was attempted first; Ollama was unavailable in the sandbox. Exact file/context reads were used thereafter.

The recent research notes read are the full-rerun state, BR/xsec check, H+b cross-check, Saranya comparison, DY replacements, and speed-up proposals, with their linked earlier reviews.

## Findings

Severity is relative to producing reliable analysis output. “Fixed” below means changed and regression-tested here, not physics-validated.

| severity | item | evidence | fixed? | action |
|---|---|---|---|---|
| High | Signal PDF normalization is changed by the repair itself | `lhepdf.py:47–58`: each PDF member divided by its Runs mean, then member 0 replaced by the eigen-member mean; this removes inclusive member shifts. `correction_manager.py` passes this only for the opted-in central signals. `hww_allfix_4fs.yaml:1151–1152` uses PDF/αS shapes while the old lnNs are commented. Independent first-2000-event H+c check gives PDF Up 1.07153 with this normalization; the H+b note records 1.0145 vs 1.0217 clean, and αS 1.000 vs 1.030. | No: physics prescription | Choose a signal prescription before Run A: per-event offset correction with a separately justified αS treatment, or explicit cross-section lnNs with shape-only residuals, or knowingly retain current behavior. Merely dividing by `/99` does not address this. |
| High | H+c αS weights are absent, not just normalized away | Actual H+c `LHEPdfWeight` title identifies LHA IDs **325500–325600**, 101 members; `lhepdf.py:85–100` emits unit αS. Its LHAPDF info is `symmhessian`, with no αS pair. The active card asks for `lhe_alphaS`; there is no active replacement αS lnN for H+c. | No: missing physics input | Decide how H+c αS uncertainty is supplied. A per-event repair cannot create absent αS members. Treat this separately from H+b, which has 103 weights. |
| High | Lepton SF factorization and event-model mismatch | `electron.py` applies POG Medium ID as well as `cut_MediumID_tthMVA_Run3`; provenance does not establish whether the latter already includes ID. `hww_allfix_4fs` uses new working points with the old v11 event model. Existing worker records the selection change. | No: explicitly deferred judgment | Ask Thomas whether the combined electron SF is incremental or inclusive; confirm all-era SF provenance. Authorize/schedule event-MVA retraining on the adopted selection before interpreting limits. |
| Medium | Jet re-sort fix was incomplete | `select_leading_jets` sorted a local copy for `jet1/2/3`, but direct `objects['jets']` remained in NanoAOD order. The workflow saves direct jet arrays and jet-flavour columns; the writer takes firsts for 2D arrays. Synthetic input `[20,80,40]` still saved first=20 while jet1=80. | **Yes**, `object_selections.py:591` | Shared unpadded jet array now receives the sorted collection. Review the two-line diff before the edit owner commits it; downstream stored jet columns now follow corrected pT order. |
| Medium | Combined PDF⊕αS variation became unity for a PDF-only sample | `lhepdf.py` 101-member branch had nonzero PDF but total Up/Down = 1. Synthetic symmetric Hessian δ=0.1 reproduced this exactly. | **Yes**, `lhepdf.py:97–100` | Combined total now equals PDF when αS is absent. The current Run-A card uses separate PDF and αS nuisances, so this does **not** repair the missing H+c αS uncertainty. |
| Medium | Production is not reproducible event for event | `muon_ss.py:125,530` uses Python and numpy random draws without event-deterministic seeding. The speed-up equivalence tests seeded both in test-only instrumentation. Different TT row counts alone do not prove the cause of each changed event. | No: user-designated judgment | Decide whether to require deterministic event-based muon RNG before production; the edit owner must test chunk/worker independence if implemented. |
| Medium | Existing silent shape fallbacks survive the fixes | `make_combine_inputs.py:304–305` falls back to nominal for a missing column, and also replaces nonfinite weights. Inclusive diboson samples have no LHE theory weights in the prior review. `postprocess/utils.py:447` still gates shift listing with a FUSE `exists()` despite server-side globs. | No: wider framework change | Require a sample/process-by-nuisance completeness audit before accepting datacards; retain this as a follow-up for the edit owner. Server-side listing alone does not eliminate all silent omissions. |
| Medium | Older JEC/diagnostic defects remain outside these patches | `jerc.py:310` uses `.exists` without calling it; warning fallback lacks `warnings` import; JEC compound input at `382–386` still comes from corrected NanoAOD pT instead of `pt_raw` (already recorded by the 10-06 review). `fitdiag_plots.py:21` treats every floating fit parameter as a unit Gaussian nuisance; rate parameters need separate treatment, and `norm_prefit` is assumed directory-like. | No: pre-existing or outside Run-A fix path | Edit owner should take these separately with focused tests; do not treat the diagnostic pull plot or all JEC edge cases as validated by this review. No numerical re-estimate of the raw-pT issue was made here. |
| Low | Active notes contain conflicting historical status | Full-rerun state opens with “uncommitted”, old HEAD/NLO and 31 tests, then appends `40d0e3e`/NNLO/34 tests. Speed-up note says “None is applied”; latest state says applied. Earlier “within 0.3%” WH agreement should be 0.36% for W+H leptonic. | Recorded here; keeper-owned consolidation pending | Keeper should give the latest state prominence and label old snapshots/history, preserving Chirayu's decisions and supersession links. This audit is additional evidence, not a replacement for the operational full-fix note. |
| Pass | Main four-era xsecs and YAML consistency | Strict duplicate-key loader: all 22 changed YAML files parse. All 14 changed workflow YAMLs build. Main eras have identical H+c/H+b/WH values; no selected Run-A MC has nonpositive xsec. Every selected dataset is present in its JSON fileset. | Existing edits checked | Keep the main era files as authoritative. The `_withWH`/`_withoutWH` variants were syntax-checked but are historical and were not brought to identical normalization. |
| Pass | Hessian variance divisor | H+c branch is 325500; TT branch is 325300–325402. Official info for 325500, 325300 and 306000 is symmetric Hessian. Their eigenvector quadratic sum has **no `/99`**. A replica RMS formula requires different set metadata and centering. | No edit needed | Preserve the divisor; fix neither the divisor nor eigenvector centering by guesswork. Member count alone is not enough to dispatch arbitrary future sets. |
| Pass | DoubleMuon 2022C does not add duplicates under current HWW logic | `trigger.py:140–157`: SingleMuon maps to the Muon mask; DoubleMuon returns all false. Ordered MuonEG/Muon/EGamma masks are exclusive. Existing synthetic tests passed, including unknown-PD rejection; real SingleMuon smoke passed. | Existing edit checked | Keep current decision. This proves mask behavior, not a full production event-ID deduplication. |
| Pass | Down definition / gen observable / dropped lnN | Copied FS JSON is byte-identical to EOS artifact; unit tests check c-hadron definition and `Up+Down=2`. Run-A declares `xsec_hplusc_3FS_4FS` and no active `xsec_hplusc_4FS_5FS`. | Existing edits checked, definitions unchanged | No switch to gen-cjet pT, reciprocal Down, alternate R/η, or restored 30% lnN was made. Inclusive shape normalization is the source construction; selected yields may change. |
| Pass with limits | Yukawa scale, Type-1, one-hots, top-pT, electron smearing | Static diffs and local suite cover Yukawa inversion/guard/fallbacks, nominal scale=1, scale labels, Type-1 sign/threshold/EM fraction, one-hots vs b-hive, and jet order. H+b tracked table equals saved rebuilt table byte for byte. Top-pT is now applied in shift trees; electron smear variations use distinct keys. | Existing implementation checked | Full data/MC closure and all-era physics validation are still needed; the worker's full H+b causal diagnosis was not rederived. |
| Pass with limits | Speed-up proposal provenance | `git apply --reverse --check .../00-all-ready-01-04.patch` succeeds against live code. Independent 19-type writer check passes; saved seeded comparisons report matching schema/metadata/output. | Applied by owner, checked here | CPU request decision remains open: `submit.py` uses two workers, proposal 05 requests two CPUs and is untested. Do not apply interrupted proposals again. |

## Independent arithmetic and sources

Public primary sources were read independently; the arithmetic below was recomputed, rather than copied from the worker conclusion.

- [LHCHWG-2026-007 Table 3](https://arxiv.org/html/2608.26863v1#S5.T3): inclusive H→γγ values 0.2216 fb (NLO 4FS) and 0.1664 fb (MiNNLOPS 4FS), including the decay BR. Their ratio is 0.7509025. The old `0.0022141 pb` implies **97.609 fb** with BR(WW)=0.2137 and BR(W→ℓν)=0.3258. This numerically matches NLO if BR(γγ)=0.002270 is assumed; it does not independently prove the old number's provenance. Multiplying by the table ratio gives **0.001662573285 pb**, rounded in all four files to **0.0016626 pb**. The unknown common γγ BR cancels in this ratio. NLO-vs-NNLO is already decided by Chirayu; no normalization choice was made here.
- [LHCHWG BR table](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR): BR(H→WW)=0.2137 at 125.00 GeV and **0.2152 at 125.09 GeV**; BR(γγ)=0.002270 at both. Thus the formerly unverified 0.2152 is mass-consistent with the WH row used.
- [LHCHWG-2024-001 Table 3](https://arxiv.org/html/2402.09955v1#S0.T3): at 125.09 GeV, W+H=0.8870 pb and W−H=0.5664 pb.
- [PDG W listing](https://pdgweb.lbl.gov/2025/listings/rpp2025-list-w-boson.pdf): per-flavour leptonic BR=0.1086, hadronic BR=0.6741. Summing three charged-lepton species gives 0.3258; the WW two-lepton factor is **0.3258²=0.10614564**. The inclusive lepton convention includes τ, consistent with the stated sample normalization; generator decay-filter efficiency was not rederived.

For each WH sample the formula is `σ(W±H) × 0.2152 × 0.3258² × BR(W_assoc)`:

| sample | recomputed pb | live pb, all four main eras |
|---|---:|---:|
| W+H, associated W→ℓν | 0.006601142784 | 0.006601 |
| W−H, associated W→ℓν | 0.004215205494 | 0.004215 |
| W+H, associated W→qq | 0.013658165595 | 0.013659 |
| W−H, associated W→qq | 0.008721516339 | 0.008722 |

The W+H hadronic entry differs by about 0.006% from rounding the inputs above; it is negligible rounding/convention precision, not a meaningful wrong-number finding. No xsecs or BRs were changed by this review.

PDF metadata: [325500 info](https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_as_0118_nf_4_mc_hessian/NNPDF31_nnlo_as_0118_nf_4_mc_hessian.info), [325300 info](https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_as_0118_mc_hessian_pdfas/NNPDF31_nnlo_as_0118_mc_hessian_pdfas.info), [306000 info](https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_hessian_pdfas/NNPDF31_nnlo_hessian_pdfas.info). The first is PDF-only; the latter two include αS members at 101–102.

## Exact review change log

All paths below are relative to the canonical analysis repo. **Every file was copied first to `<file>.pre_sol_review`, adjacent to its original, using `shutil.copy2`; no earlier backup was overwritten.** Backups still exist. No higgscharm commit was made.

| file / final line | before | after | reason and evidence |
|---|---|---|---|
| `analysis/selections/object_selections.py:590–591` | Sorted local `jets`; `self.objects['jets']` unchanged | Added comment and `self.objects['jets'] = jets` before padding | Completes the declared re-sort; a pre-fix assertion on `[20,80,40]` failed, while jet1 was already 80. Keeps jagged multiplicity and avoids inserting padded nulls into the shared collection. |
| `analysis/corrections/lhepdf.py:97–100` | 101-member `w_up_total` / `w_down_total` = ones | `w_up_total = w_up_pdf`, `w_down_total = w_down_pdf`, explanatory comment | PDF⊕0 = PDF. Synthetic δPDF=0.1 produced total 1 before, 1.1/0.9 afterward. This changes combined-weight columns, not the missing separate αS pair. |
| `tests/test_allfix.py:368` | Only jet1/2/3 order tested | Added assertion on the complete shared jet collection | Regression covers direct writer inputs as well as candidate vectors. |
| `tests/test_allfix.py:510–524` | No PDF-only combined regression | Added `TestPdfOnlyCombined` | Tests known Hessian quadratic sum, combined ±0.1 and unit separate αS. |

Backup SHA256 before edits:

```text
5f91e275690a1cfd77cd852bb0e994e62357ee55ca211560e1a87872672ac5bf  analysis/selections/object_selections.py.pre_sol_review
9bf26acf8ea9e93094453ce745d00cb5ed7b207b60db906eb17dd008806eccf5  analysis/corrections/lhepdf.py.pre_sol_review
120b731fd2100d506a618bc8108f0a0de98c9faf3e2b411d2267e9ad7196e4d1  tests/test_allfix.py.pre_sol_review
```

Owner-visible change log and patch: `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/sol_review_20261105/{changes.json,changes.patch}`. The log names this vault note. Audit scripts, unit/regression/writer logs, the final smoke summary and the six smoke logs are also retained in this directory. Adjacent backups deliberately remain untracked; the owner should stage explicit implementation paths and omit backups.

## Checks and evidence

Established image: `/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-base-almalinux9:0.7.30-py3.10`. Used `singularity exec -B /afs -B /cvmfs -B /eos -B /tmp -B /run/user`, existing `KRB5CCNAME` and proxy, and `PYTHONDONTWRITEBYTECODE=1` for unit/audit runs. No credentials were renewed. The first test invocation without `/run/user` produced a permission error reading the external b-hive reference; after using the established bind, all 34 original tests passed, with **no skip**.

- Original suite: **34/34 pass** (6.298 s), including the externally mounted b-hive comparison; the brief's 31 is an older count.
- Added regressions before implementation edit: **35 tests, exactly 2 failures** (shared jet order and combined PDF-only variation).
- After edits: **35/35 pass** (6.734 s), no skips. `git diff --check` is clean.
- Static Python AST parsing for the changed Python files passes. Strict YAML loader found no duplicate keys in all 22 changed YAMLs; all 14 changed workflow configurations build. The 8 HWW muon/electron correction sets load; representative signed-η prompt-MVA SF evaluation succeeds for all four eras. Both ONNX SHA256 values match `meta.yaml`.
- Run-A selected datasets per era: **51 / 52 / 62 / 52**, all present in JSON, all selected MC xsecs positive. Full JSON counts remain **92 / 93 / 95 / 84**. Only DY keys differ from `.bak-20261103`; all other lists are identical.
- DY lists in the note's order contain **525, 448, 1682, 1573, 457, 506, 657, 301, 312, 342** entries, each with exactly that many unique LFNs, all matching the replacement campaign/primary/tier/processing. This checks local file lists, not fresh DBS validity or all remote file access.
- FS correction JSON equals the EOS source byte for byte. H+b table equals the worker's saved 6001-row rebuilt table byte for byte. The table rebuild itself was not repeated.
- Writer type equivalence: **19/19 pass** using the saved `test_writer_types.py`, comparing schema and parquet bytes. The prior full-job performance benchmark was not repeated.

### Backups and interrupted proposals

Checked `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/`:

- All four `.pre_whxsec` YAMLs preserve the original two zero WH entries and NLO-like H+c value.
- `.pre_nnlo_hc` preserves the filled WH entries and H+c=0.0022141; `.pre_wh_align` has H+c=0.0016626 and the older two WH values. The sequence is consistent, not conflicting live inputs.
- The `.pre_drop4fs5fs` workflow backup exists. The four `.bak-20261103` JSONs are old inputs and must not be restored for production. `.onlywjets_180057` is also an untracked alternative, not the authoritative fileset. No backup was removed.
- The original `proposals/HTOWW-TTHMVA-MERGE` and `proposals/HTOWW-FRAMEWORK-SPEEDUP` directories are **absent**. Only `HTOWW-FRAMEWORK-SPEEDUP-2` and its tests are saved there. Thus there are no EOS partial patches from the interrupted pair to approve or apply; the later ONNX implementation and applied speed-up patch are what was reviewed. Node-local old TTH scratch exists but was not treated as an active proposal.

### Single-file smoke tests

Used the existing read-only harness `/eos/user/c/cgupta/HToWW/backups/smoke_allfix.sh`, which runs `python3 submit.py` locally, with unique `sol_*` and `solfix_*` output tags under `/tmp/cgupta_allfix_smoke/`. It does **not** invoke `runner.py --submit`, Condor or CRAB. Pre-edit and post-edit H+c, TT and SingleMuon tests all returned `EXIT=0`. Parquet inspection found no nonfinite values in any `weight_*` column. Nominal selected rows were H+c 423 / TT 5492 / SingleMuon 4 before, and H+c 423 / TT 5496 / SingleMuon 4 after. These are smoke counts, not a controlled yield-difference measurement: the muon RNG is unseeded. Post-edit H+c combined PDF weights equal separate PDF weights, as required. The FS Up/Down yield ratios were 1.13689 / 0.86311 in this file; selected-yield variation is allowed for the inclusive-normalized shape definition. Logs: `sol-smoke-summary.log`, and `log_{sol,solfix}_{hc,tt,sm}.txt` in the evidence directory below. Outputs are local to lxplus921 and not a production.

Input files:

- H+c, 2022postEE: central `Run3Summer22EENanoAODv12` file `27982ec7-6713-495c-b35c-4058f99feadc.root`.
- TTto2L2Nu, 2022postEE: `07a6b4e8-a99d-4cd4-8ab0-9a51635f6a6f.root`.
- SingleMuon Run2022C, 2022preEE: `55e413fa-1dd6-4143-9c24-846e397f45d9.root`.

## Remaining limits and exact handoff

Not checked here: full-production data/MC closure, an event-ID duplicate scan across all primary datasets, remote completeness of every input file, new DBS/CRAB status, full H+b gridpack recompilation/causal study, all-era end-to-end smoke processing, a rebuilt datacard/limit, or old historical numerical results moved by the keeper. No claims about a finished production or limit follow from passing these tests. No Run-B stitching implementation was validated. R/η, gen-chad vs gen-cjet, Down convention and lepton WPs were left as existing decisions.

**Needs Chirayu's attention (decisions):**

1. Select the signal PDF/αS model, explicitly including the absent H+c αS pair. Options are per-event PDF repair plus separately justified αS, or cross-section lnNs plus residual shapes, or explicit acceptance of the present suppression/absence.
2. Require deterministic event-based muon RNG before production, or explicitly accept nondeterministic output; choose two requested CPUs for two workers, or one worker within the present CPU request.
3. Keep already recorded NNLO/WP/stitch-radius decisions in force; the open implementation/physics checks above are not requests to decide those again.

**Needs an action from Chirayu:**

1. Give the edit owner a concrete output path with adequate quota, or explicitly authorize removal of named obsolete outputs after inspection. The worker's recorded capacity is about 81 GB free versus an estimated 266 GB requirement; this review did not delete anything or remeasure quota. Deleting only its suggested 179 GB directory would leave roughly 260 GB, still short of that estimate and without headroom.
2. Ask Thomas: “Does `cut_MediumID_tthMVA_Run3` already include the Medium-ID efficiency SF, or is it conditional on passing Medium ID? What are the provenance and era validity of these files?” No message was sent on Chirayu's behalf.
3. Authorize/schedule retraining and validation of the event MVA on the adopted lepton selection before interpreting the new limit.
4. Review the uncommitted Sol patch with `cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm && git diff -- analysis/selections/object_selections.py analysis/corrections/lhepdf.py tests/test_allfix.py`; let the single edit owner incorporate it. Do not stage `.pre_sol_review` files.

Chirayu also requested slides summarizing the recent work and this review. The commit for this note uses `make slides`; after finishing, Sol asks the existing keeper to update the appropriate internal leaf decks, preserve agent-reported status, consolidate stale active wording, and commit locally without pushing as part of this handoff.

## Addendum: why the private 3FS NanoAOD has an empty `LHEPdfWeight` (2026-11-05, agent-reported)

Route B reported that the private 3FS H→WW NanoAOD has `nLHEPdfWeight = 0` and an empty branch title (`proposals/HTOWW-ROUTEB-SOL-20261105/diagnostics/smoke_3fs.json`, file `…/261023_145954/0000/nanoaod_100.root`, 1000 events). Cause, checked on lxplus:

- The 3FS run card uses `lhaid 321900` ([[2026-10-13-GEN-ticket-draft-HplusC-HplusB-WW]]: "3FS: 321900, maxjetflavor 3", as in the official γγ cards). LHAPDF `pdfsets.index` (`/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current`): `321900 NNPDF31_nnlo_pch_as_0118_nf_3`.
- NanoAOD fills `LHEPdfWeight` only for a set on its `preferredPDFs` list (`CMSSW_13_3_3/src/PhysicsTools/NanoAOD/python/genWeightsTable_cfi.py`, 13 entries). 321900 is not on it, and no `nf_3` set is. 325500 (the 4FS set) is, which is why the 4FS file has 101 members.
- So the sample's generator-level weights are not shown to be wrong. The LHE weights exist: the 2026-10-21 CRAB test saw a 1.6% replica spread, and `LHEScaleWeight` (9) and `PSWeight` are filled. The PDF weights are simply not copied into NanoAOD. The private chain kept MiniAOD ([[2026-10-28-4fs-el8-gridpack-and-3fs-production]]), and MiniAODSIM carries the `LHEEventProduct`. A NanoAOD re-run from MiniAOD with 321900 added to `preferredPDFs` should recover the branch **without regenerating GEN/SIM**. Not tested.
- **Checked with Chirayu's renewed proxy (2026-11-05):**
  - The official γγ 3FS NanoAOD has the same empty branch: `Run3Summer22EENanoAODv13/HPlusCharm_3FS_MuRFScaleDynX0p50_HTo2G…/a4e83ef8-….root` and `RunIISummer20UL18NanoAODv9/HPlusCharm_3FS_…HToGG…/AA5E17E4-….root` both have title `''` and `nLHEPdfWeight = 0` (first 200 events). So this is standard NanoAOD behaviour for this PDF set, not a defect of the private production.
  - Private `nanoaod_100.root` (copied with xrdcp): title `''`, n = 0, which confirms the Route B result.
  - Private MiniAOD exists next to it (`…/261023_145954/0000/miniaod_*.root` on maite). `miniaod_1.root` contains `LHEEventProduct_externalLHEProducer__SIM` (Events) and `LHERunInfoProduct_externalLHEProducer__SIM` (Runs). So a NanoAOD re-run from MiniAOD can read the weights. That the 321900 weight group itself is in the header was not inspected here; it is inferred from the 10-21 CRAB test.
- Effect now: `lhepdf.py` gives PDF/αS Up = Down = 1 for these events, so the ≥1c region of a Route B stitch has no PDF shape uncertainty.

### TODO (Chirayu, 2026-11-05): 3FS PDF weights. Not a blocker.

- [ ] Only if Route B is adopted: put a flat PDF lnN on the 3FS (≥1c) component, e.g. about 2%, from the 4FS PDF acceptance effect or the 1.6% LHE replica spread, and record the justification. Run A (4FS only, 101 PDF members) is not affected.
- [ ] Optional, only if a reviewer asks for a per-event PDF shape: re-run NanoAOD from the private 3FS MiniAOD with `lhaid 321900` added to `genWeightsTable.preferredPDFs`. This needs CRAB jobs and Chirayu's OK.

## Addendum: review of the Route B proposal (HTOWW-ROUTEB-SOL-20261105), read-only, agent-reported

Source: `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/proposals/HTOWW-ROUTEB-SOL-20261105/` (`hplusc_routeb.py`, `routeb_io.py`, `patches/base.py.routeb_hook.REFERENCE.patch`, `patches/*_nanov12.yaml.patch`, `patches/hww_routeb_3fs4fs.yaml.vs_allfix.diff`). Nothing in higgscharm was edited.

| Severity | Item | Evidence | Fixed? | Action |
|---|---|---|---|---|
| Pass | Normalisation | Per-event weight L·X·c_s·w/F_s with c_s = A_s/Σ A_s f_s reproduces the paper's two steps (region → A_s f_s, then rescale to σ_NNLO); closure Σ c_s f_s = 1. A₄/A₃ enters only as a ratio; sample NLO ratio 97.62/54.97 = 1.776 matches Table 3 (0.2216/0.1248). | – | – |
| Pass | f_s statistical uncertainty | var f = [(1−f)² Σ_kept w² + f² Σ_notkept w²]/F² is the correct correlated-subset formula. | – | – |
| Pass | F_s / double counting | Hook takes sumw from the full chunk before the veto in all three paths (`dump_chunk_sumw(events_full)`, TRAIN/RUN stats, stitch record). Records are keyed by partition (retry overwrites). A conflicting duplicate raises. A chunk accumulated twice makes invalid JSON and raises. Stitch `full` is cross-checked against `sumw_records` at 1e-6. Legacy coffea output is refused. | – | – |
| Pass | Filesets | All four eras get `HplusCharm_3FS_HToWW` (non-TEST CRAB outputs), and 2022postEE also gets `_ext1`. All use xsec = 0.0016626 = 0.0022141 × 0.1664/0.2216, the same as the 4FS entry. | – | – |
| Pass (log) | Unit tests | `diagnostics/unittest_routeb.log`: 20/20 OK. Author-run log, not re-executed (standing review rule, Chirayu 2026-11-05). | – | – |
| Low | BR convention between H+c and WH | The H+c X carries BR(H→WW) = 0.2137 (mH 125.00, via 0.0022141); the WH entries use 0.2152 (mH 125.09). That is a 0.7% relative normalisation offset between signal and the WH background. | No (convention) | Chirayu: pick one mH for all Higgs entries. |
| Medium | Not yet integrated | Card builder (`read_scale` × c_s), `WorkflowConfigBuilder` (the `stitching:` block), sinks and training weights are not wired in. The fileset header warns that using the 3FS entries without the hook double-counts H+c. An empty chunk after masking is untested (the patch says so). | No (open implementation) | Edit owner: implement, then smoke one file per scheme. |
| Medium | Open physics choices (already flagged by Route B) | Scale-variation normalisation differs between regions; GenJets include H→WW leptons; 3FS Neff/N ≈ 0.04; 3FS PDF weights (see TODO above). | No (decisions) | Chirayu. |
| Info | Run A shape nuisance dropped in Route B | `hpluscFSShape: []` and `xsec_hplusc_3FS_4FS` removed, following the paper ("stitching mitigates the need for the flavour-scheme uncertainty"). | – | Confirm when choosing A vs B. |

Interrupted step: a temporary copy for rerunning the tests was being made under `/tmp/cgupta/tmp.*` on an lxplus node, and Chirayu stopped it. It may have left a scratch directory there. It touches no repo or EOS data.
