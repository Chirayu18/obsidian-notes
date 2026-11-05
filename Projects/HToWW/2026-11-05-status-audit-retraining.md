---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# HToWW status audit: slides vs reality, open items, event-MVA and negrw retraining (2026-11-05)

**Status: agent-reported, read-only audit. Chirayu has not reviewed it.** Brief 1 in [[Meta/keeper/2026-11-05-pending-worker-briefs]]. It was run as a sub-agent fallback because the top-level thread launches failed. No analysis-repo edit, commit, job, EOS deletion, credential change or push was made. No unit tests were run. A separate agent reviews the uncommitted code at the same time, so this note covers status and dependencies, not a line-by-line code review.

## Review manifest

| item | value |
|---|---|
| Audit time | 2026-11-05 13:53–14:00 CET |
| Vault | branch `keeper/vault-organised-20261105`, HEAD `771b517` |
| Analysis repo | lxplus938, `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `40d0e3e9e5f1` (on `0850e51`), unpushed |
| Uncommitted | 11 modified files (+248/−20). Untracked: `analysis/{features,models,sinks}/`, `processing_{modes,checks}.py`, `scripts/mva/{split,register}_folds.py`, `scripts/check_train_outputs.py`, `build_cards_from_templates.py` and 2 test files. The newest mtime is `features/hww.py` at 09:03:38 CET, so the inspected mtimes show no changes after about 09:03; mtimes alone do not establish an immutable snapshot. `analysis/processors/.base.py.swp` is 0 bytes and dated 2026-08-17: stale, not a live editor |
| Workflow | `analysis/workflows/hww_allfix_4fs.yaml` (1234 lines) |
| Event model | `hwwcom_multiclass_v11_2dcats`, `best_model.pt` (mtime 2026-07-12 05:59, sha256 prefix `9b28bcfe5adf3e47`) |
| negrw model | `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models.joblib` (8,042,889 B, 2026-07-15 15:36) |
| Inputs read | Deck r5 `index.html`, the full-fix state note, the Sol review, the framework how-to, the Route B note, the re-NANO note, the negrw training-region and closure notes, the 10-01 full-rerun findings, CTAG.md, the Saranya comparison and the lepton-MVA nonprompt diagnostic |
| Live checks run | `git status/diff/log`; greps and reads of the workflow, `base.py`, `lhepdf.py`, `muon.py`, `electron.py`, `muon_ss.py`, `jerc.py`, `make_combine_inputs.py`, `features/hww.py`, `models/registry.py`, `register_folds.py`, `submit.py`, `condor/submit.sub` and the era YAMLs; b-hive `train_v11_2dcats.sh`, `HPlusCHToWW_2dcats.yml` and `filelists/v11_train_allEras.txt`; `eos quota`; `dasgoclient` (prod/phys03) on the re-NANO outputs |

## 1. Event MVA (v11): retrain? **Yes. Confirmed, and more inputs changed than the slides say.**

Chirayu's question: does the event MVA need retraining because of the new signal as well as the new lepton WPs? Both reasons hold, and there are more.

What v11 was trained on (b-hive `train_v11_2dcats.sh`, config `HPlusCHToWW_2dcats`, file list `v11_train_allEras.txt` dated 2026-06-16):
- **19 files from `hww_combine_fixed`:**
  - 2022postEE: all 16 classes;
  - 2022preEE: only H+c and H+b;
  - 2023preBPix: only H+c.
- **Backgrounds come from 2022postEE only.**
- **Signal: the private H+c sample** (10-01 findings note: "MVA = July v11_2dcats (trained on PRIVATE signal + old 2022postEE bkg) — caveats: central-signal transfer unchecked").
- **Features (26):** dilepton/lepton pTs, `cjet_cand_pt`, `met_pt`, `mtl1`, `mtl2`, `dilepton_mass`, ΔR/Δφ variables, 11 c-tag 2D one-hots and `nSV`.
- **Class re-weighting** (`reweighting_mode: class`) in bins of `dilepton_pt` × `dilepton_mass`.
- **Training inputs no longer at the recorded path:** `/eos/home-c/cgupta/higgscharm/outputs/hww_combine_fixed/` does not exist now (checked). I did not search for where it went. v11 therefore cannot be rebuilt from its recorded input path.

What has changed since then, with evidence:

| change | how it reaches the MVA | source |
|---|---|---|
| **Signal sample: private H+c → central 4FS FxFx `HplusCharm_4FS_HToWWTo2L2Nu`** (and the central 5FS H+b in higgsbkg) | The training class `hplusc` now has different signal kinematics. The nominal weight of the central sample carries the running-Yukawa factor F per event (`lhe_yukawa_fix.py` docstring: "The nominal event weight carries F"). Never checked for v11 | 10-01 note; workflow `datasets: hc_central, hb_central` |
| NNLO normalisation and the Yukawa scale-weight fix | **These do not by themselves justify retraining.** NNLO is a flat factor, and class re-weighting removes the overall scale. The Yukawa fix (`lhe_yukawa_fix.py`) changes only the scale/PDF *variations*, not the nominal weight. They matter for the templates, not the training | `lhe_yukawa_fix.py` docstring and the dispatch in `correction_manager.py:118–144` |
| **Lepton WPs:** muon `tight_HWW` + ttH-MVA > 0.67; electron cut-based Medium + ttH-MVA > 0.9 + IP/convVeto (was tight/wp80iso) | Changes the lepton features, the event composition per class and the ΔR jet cleaning, so `cjet_cand` changes too. H+c smoke: 423 rows vs 563 before (−25%) | workflow lines 89–105; state note |
| JEC-recorrected `events.MET`, Type-1 MET sign/selection fix, JER→MET | `met_pt`, `mtl1`, `mtl2` and the Δφ(MET) features shift. Selected W+jets rose by +35/+26/+15% (0J/1J/2J) after the MET change | 10-01 note; state note |
| Jet re-sort after JEC, shared jet ordering (Sol fix, uncommitted), jet-veto map | The candidate-jet population and `nSV` change | state note; `object_selections.py:590–591` |
| WH added to higgsbkg; WG decision | WG is processed (`datasets: wg`, process `WG`) but is **not** in `combine.process_map` or `mva.labels`. Chirayu 10-02: "ADD IT (to diboson, in training and in process_map) WHEN RETRAINING" | workflow; 10-01 note |
| Eras | Run A covers 4 eras; v11 saw no 2023 backgrounds | file list |
| Train/fit overlap | 2022postEE background events used in training are also in the fit. The TRAIN/RUN k-fold scheme fixes this by design | 10-01 note; framework note |

**Verdict:** retrain before any Run A limit is trusted. The two strongest reasons are the new signal sample and the new leptons, followed by the MET fixes. NNLO and the Yukawa fix alone would not force a retrain. Because the c-tag CRs (`CR_tt` etc.) are MVA-argmax regions, retraining also redefines the `rate_tt` control region and every other CR (section 5).

## 2. negrw: retrain? **The classifier itself: probably not. Its "disjoint by construction" guarantee: not established for Run A. A coverage and overlap check is needed; if it fails, retrain.**

What negrw is (training-region note 2026-07-11, `hww_genrw_train.yaml`, `base.py:170–181, 276–313`):
- It learns g(x) = 2P₊(x) − 1 from **generator-level features only** (`lhe_*`, `genparton_*`).
- The training sample is DY 10to50, DY 50 and the inclusive `WtoLNu_2Jets`, **2022postEE only, 35 files each**, about 9.65M rows.
- Training region: base cuts + trigger + `veto_emu_sr`.
- It is applied to the DY and **jet-binned** W+jets samples in all four eras. Dataset names match in all four era YAMLs (checked).
- Per-dataset yield renormalisation (`make_combine_inputs.py:290–297`) is recomputed at card-building time.

Against the full-fix changes:

| change | effect on negrw | verdict |
|---|---|---|
| Leptons, JEC/MET, jet veto, jet re-sort, trigger | The model inputs remain generator-level, but that alone does not prove that a changed reco selection preserves sign probabilities conditional on the finite feature set | No automatic retraining verdict from feature type alone; recheck support and signed-weight closure in the new selection |
| **Lepton WPs vs `veto_emu_sr`** | `hww_genrw_train.yaml` still defines the veto with the **old** leptons: muon tight/tight-iso, electron wp80iso (checked). In Run A an event can now have exactly one eμ pair under the new WPs while it did not under the old ones (e.g. an electron that fails wp80iso but passes Medium + ttH-MVA > 0.9). An event with this pattern could occur in both sets; this audit has not identified a shared event ID. `base.py:174–176` still states "disjoint-by-construction … no hold-out is needed". **The old veto no longer proves disjointness; actual event overlap has not been measured.** The identified overlap risk concerns **DY in 2022postEE**, in the 35 training files only. W+jets is not affected because the jet-binned samples were never trained on | **Needs an event-ID overlap check** (training parquet `outputs/hww_genrw_train/2022postEE/` vs the new SR). If the overlap is not negligible, retrain with the new-lepton veto or with an `event mod k` hold-out |
| SR coverage | The 2026-07-11 coverage gate (SR x inside the training support) was done on the old SR. The new SR is a different subset (tighter leptons, new MET) | Recheck coverage on `lhe_vpt`, `lhe_ht`, `lhe_nc` and `genparton1_pt`. Likely to pass, but unverified |
| Closure | 07-17: closure 0.994 on the training region and 1.058 in the old SR, handled by per-dataset renormalisation | The renormalisation adapts automatically. The size of the residual in the new SR is unknown until cards are built |
| Eras | Trained on 2022postEE, applied to all 4 eras | Holds if the generator setup is the same across campaigns. The DY replacements are the "same generator, same campaign" (2026-11-03 note). Not checked for 2023 |
| TRAIN/RUN | Scoring happens before the mode branch (`base.py:177–181`), so it runs in all modes | Correct use in the RUN templates is the code reviewer's scope |

## 3. Open items, one by one

| # | item | current real state (evidence) | needed to close | owner | blocks Run A? | hidden dependencies |
|---|---|---|---|---|---|---|
| 1 | **Signal PDF/αS prescription** | `lhe_pdf`, `lhe_alphaS` are shapes (`hww_allfix_4fs.yaml:1151–1152`, matches the slide). H+c LHA 325500 has 101 members, so `lhepdf.py` emits unit αS. The PDF⊕αS combined fix is uncommitted (`git diff lhepdf.py`). The old `xsec_hplusc_PDF`/`alphaS_PDF` lnNs are commented out. The H+b PDF/αS are suppressed by lhe_norm + centring (H+b note) | Chirayu picks (a) per-event repair + separately justified αS, (b) xsec lnNs + shape-only residuals, or (c) keep as is. Then an agent implements it | Chirayu → agent | **Yes** (card content) | Implementing (a) or (b) changes `analysis/corrections/lhepdf.py`. That changes `selection_signature`, which hashes all `corrections/*.py`, so **decide before TRAIN** or the trained models are refused by RUN (`registry.py:19`) |
| 2 | **Lepton-SF factorisation** | Electron: POG Medium ID SF (`CMS_eff_e_id`) **and** `cut_MediumID_tthMVA_Run3` are both applied (`electron.py:86, 92–108`). **Muons have the same question, which nobody has asked:** ID `NUM_TightID_HWW_DEN_TrackerMuons` × iso `NUM_TightPFIso_DEN_TightID_HWW` × MVA `NUM_TightID_HWW_TightIso_tthMVA_DEN_TightPFIso` (`muon.py:115, 189, 221`). The MVA numerator repeats TightID_HWW, and its denominator names only TightPFIso. If that denominator does not include ID, the ID efficiency is counted twice. The docstring asserts "measured on top of TightID_HWW + TightPFIso", but no source is cited | Ask Thomas about **both** flavours: what is the denominator of each `*_tthMVA` SF, and what are the provenance and era validity of the files? Then possibly drop or adjust one factor | Chirayu asks Thomas | **Yes** for the limit (normalisation of every MC process). Production could start, but an SF change edits `corrections/*.py` (same hash dependency as #1) | Affects every MC yield, `rate_tt` and the MVA training weights if they are SF-weighted |
| 3 | **Event-MVA retraining** | v11 still configured (`inference:` block). TRAIN/RUN exists but is uncommitted, unreviewed and has no real models | Section 1. TRAIN on the final selection → split_folds → b-hive training → register_folds → RUN. Add WG to diboson (10-02 decision) | Chirayu authorises; agent runs (job submission needs his OK) | **Yes** for any limit. A legacy Run A with v11 gives templates with a stale model | Needs #1, #2, #4, #8, #13 and the c-tag edges (#N2) settled first. Each of these changes the selection hash or the features, which would force another TRAIN. Needs #5 (EOS) and #7 (commit) |
| 4 | **Muon RNG seeding** | Still unseeded: `muon_ss.py:6,125` (`random()`), `:530` (`np.random.rand`). TT smoke rows 5489/5491/5492/5496 across runs | Chirayu: require deterministic event-based seeding, or accept it. If required, an agent implements and tests chunk/worker independence | Chirayu → agent | Not strictly. But TRAIN/RUN equivalence and fold reproducibility rely on it, and a later change edits `corrections/` (hash) | #3 |
| 4b | **CPUs per job** | `submit.py:125` `workers: 2`; `condor/submit.sub` has no `request_cpus`, so the default is 1. Old logs show CPU usage of 3.29 against 1 requested (`condor/logs/hww/2022postEE/MuonE/hww_MuonE.6781198.2.log:79`) | Chirayu: `request_cpus = 2` (proposal 05, untested) or `workers: 1` | Chirayu → agent | No (efficiency and fair-share) | None |
| 5 | **EOS space** | Re-measured now: `eos quota` gives 919.02 GB of 1.00 TB (91.90%), about 81 GB free. The file count is 2.40M of 5.00M. The estimate is 266 GB for a legacy production + ttsyst. Nothing may be removed | A new output location (another quota/project space) that Chirayu names. Or decide that Run A goes TRAIN→RUN: slim nominal ntuples + coffea templates are much smaller than legacy per-shift parquets (size not measured) | Chirayu | **Yes** for legacy | The TRAIN/RUN choice (#3) changes the space needed |
| 6 | **One mH for Higgs cross sections** | H+c 0.0016626 inherits BR(WW) = 0.2137 (125.00); WH uses 0.2152 (125.09); 0.2152/0.2137 = 1.0070 (slide correct). **Not considered:** the other Higgs entries have unverified conventions. Back-computing with BR(WW)·0.3258² (agent arithmetic, 2022postEE YAML) gives σ(ggH) = 47.72 / 47.39 pb, VBF 4.102 / 4.074, ZH 0.950 / 0.944 (125.00 / 125.09 BRs). These were not matched to any source in this audit | Chirayu picks the mass. An agent then re-derives **all** Higgs entries (ggH, VBF, ZH, ggZH, WH, ttH, H→ττ, H+b, H+c) from one LHCHWG table | Chirayu → agent | Small for the limit (0.7%), but it should be fixed before production. YAML-only, no hash effect | `xsec_higgsbkg` 5% lnN. Route B uses the same X |
| 7 | **Commit the uncommitted code** | Confirmed as above: 11 modified files and the new modules. Unpushed. `register_folds.py:55` records `git rev-parse HEAD` only, so a TRAIN run from a dirty tree gets misleading provenance | Code review (other agent) → Chirayu OK → the edit owner commits, with explicit paths and no `*.pre_sol_review` | Reviewer agent, then Chirayu, then the edit owner | **Yes.** The jet-ordering fix is part of Run A physics. The slide's "Run A is committed" is only partly true | #3 provenance |
| 8 | **Silent nominal fallbacks, `make_combine_inputs.py`** | Still present: a missing column falls back to `nominal_w`, and non-finite weights are replaced with nominal (`make_combine_inputs.py:304–305` missing column, `:311–313` non-finite; unchanged from the Sol review) | Process × nuisance completeness audit before accepting legacy cards. `build_cards_from_templates.py` (RUN) needs explicit "not applicable" entries instead (framework note) | Agent | Yes for **legacy** cards; less for RUN cards | Removed in practice if the RUN route is used |
| 9 | **JEC `pt_raw` / diagnostics** | Still present: `jerc.py:310` `Path(...).exists` without the call, so it is always true. `warnings` is used at `:314, 401, 485` but never imported (imports at `:4–16`); this fails only on the fallback branch. The L1L2L3 input at `:385–387` uses `j` before `j["pt"]` is set to `pt_raw` (the 10-06 finding). `fitdiag_plots.py:21` not rechecked | Focused fix + test. Estimate the size of the raw-pT effect on JEC | Agent (edit owner) | Unknown size. The `pt_raw` issue moves every jet pT and MET a little | A fix edits `corrections/jerc.py` (hash, #3) |
| 10 | **Route B (parked) / 3FS re-NANO** | Route B is proposal-only (live tree has no `analysis/stitching/`; per the Route B note). **Re-NANO is no longer just "pending":** DAS prod/phys03 at 12:57Z shows 4 of 5 outputs complete (2022preEE 1,261,997; 2022postEE 4,119,986; postEE ext1 166,999; 2023preBPix 2,869,993 = inputs). 2023postBPix has 1,502,991 / 1,517,991 (15,000 short, last publish 12:57Z). `nLHEPdfWeight` = 101 in the outputs is **not checked** | Finish 2023postBPix; check 101 members in a few files; switch the Route B filesets. Comparing A and B needs Route B integrated (card builder, config, sinks, training weights) | Agent (check) / Chirayu (re-enable B) | **No** | The A/B comparison would also need a retrained MVA for B. The `stitching` hook touches `base.py` |
| 11 | **Scale-variation normalisation (if Route B returns)** | Open (Route B review addendum) | Decision when B is re-enabled | Chirayu | No | #10 |

Additional items found in the notes, not on the slide's "Needs you" list:

| # | item | state | needed | owner | blocks Run A? | dependencies |
|---|---|---|---|---|---|---|
| N1 | **negrw disjointness / coverage** | Section 2 | Overlap + coverage check; retrain if it fails | Agent | Probably not (V+jets is a small SR background), but an unchecked bias | New SR from Run A |
| N2 | **c-tag 2D SF and edges** | `CMS_ctag2d_2022` Up raises SR signal by +43% ("verify before the final limit", 10-01, still open on 10-21). Saranya comparison: about 41% of the SF grid are placeholder cells (1.0/3.0/0.3), and the per-era category edges are not ported. Live `ctag2d_categories.py:12–13` uses one global set of edges for all eras | Decide on edges and SF placeholders **before TRAIN**: the one-hots are MVA features, so the edges are inside the feature hash | Chirayu (c-tag was set aside on 10-29) | Yes for a trustworthy limit. c-tag is the largest nuisance group (23.5 in the 10-21 breakdown) | #3 |
| N3 | **WG in the card** | Processed but dropped from the card and from training (no `WG` in `process_map`/labels) | Add at retraining (10-02 decision) | Agent at #3 | No | #3 |
| N4 | **Output completeness check in legacy** | The HZZ port (`processing_checks`) is active only in TRAIN/RUN (framework note). Legacy has no events-in vs rows-out check (plan item P0-14) | Use TRAIN/RUN, or port the check to legacy | Agent | Yes for legacy integrity | #3 |
| N5 | **Test evidence for TRAIN/RUN** | "49 tests" is from the thread only. The evidence dir `sol_trainrun_20261105/` holds only `initial_changes.json` and `phase2_files.json`, with no test log. `base.py`, `sinks/hww.py` and the tests were modified at 09:01, after that dir's last write (08:59) | Under the standing rule a rerun is allowed (no log exists). That is the code reviewer's call | Code-review agent | Not by itself | #7 |

**What really blocks Run A now:** #1, #2, #3 (plus N2 if the limit should be trusted), #5, #7. #6 is cheap and should be done first.

**Suggested order**, a proposal, not a decision:
1. Decide #1, #2 (both flavours), #4, #6, N2 and the CPU question.
2. Implement them, review and commit (#7).
3. TRAIN.
4. Do the negrw overlap/coverage check (N1) on the TRAIN output.
5. Retrain the MVA with WG added (#3).
6. RUN.
7. Build cards from templates.

Every code change in `corrections/`, `selections/`, `working_points/`, `leptonmva/` or in the workflow selection/corrections blocks **after** TRAIN invalidates the trained models: RUN refuses them by `selection_hash` (`features/hww.py::selection_signature`, `models/registry.py:19`).

## 4. Are the slide claims still accurate? (deck r5)

| slide | claim | verdict |
|---|---|---|
| status | "Run A is committed" | **Partly wrong.** `0850e51`+`40d0e3e` are committed (unpushed), but the two Run A review fixes are uncommitted |
| status | "49 with TRAIN/RUN and the ports (worker-reported)" | Worker-reported only. No saved log found (N5) |
| status / result-routeb | "3FS re-NANO: submitted 5 Nov, pending" | **Outdated.** 4/5 datasets complete in DAS; 2023postBPix at 99.0% (#10) |
| status, "Needs you" | Lists PDF/αS, lepton SF + MVA, RNG/CPUs, EOS, mH | **Incomplete:** c-tag SF/edges (N2), the muon-SF factorisation (#2), negrw (N1) and the commit gate are missing |
| result-code | Normalisation, WH, ONNX |Δ| ≤ 3.3e-7 | Consistent with the state note and the Sol review (not re-derived) |
| result-review | Line refs `object_selections.py:591`, `lhepdf.py:97–100` | Still correct in the live tree |
| result-pdf-alphas | `hww_allfix_4fs.yaml:1151–1152`; H+c PDF-only, 101 members | Correct (lines checked) |
| open | Lepton SF row asks only about electron `cut_MediumID_tthMVA_Run3` | **Incomplete:** muons need the same question (#2) |
| open | "Event MVA: v11 was trained on the old leptons" | True but **incomplete:** private signal, pre-fix MET, 2022postEE-only backgrounds, WG excluded, train/fit overlap (section 1) |
| open | Higgs mass 0.2137 vs 0.2152, 0.7% | Correct, but **incomplete** (other Higgs entries, #6) |
| open | EOS ~81 GB free vs ~266 GB | Still correct (91.90% at 13:56 CET) |
| backup-sources | "silent nominal fallbacks", "JEC pt_raw" | Still open (#8, #9). The `jerc.py` JEC line numbers have moved slightly |

## 5. Missing or underemphasised dependencies (ranked by impact on Run A)

1. **Order versus the model hash.** Every open physics or code fix (PDF prescription, SF factorisation, muon RNG, JEC `pt_raw`, c-tag edges) edits files that `selection_signature` hashes. Doing any of them after TRAIN wastes the TRAIN production and the training. No note plans this order.
2. **The CRs and `rate_tt` move with the MVA.** All 5 CRs, including the only `rateParam` region `CR_tt`, are argmax-of-MVA channels (`combine.channels`, `rate_params: [tt]`). Retraining redefines the tt control region. Earlier tt purity figures (CR_tt 99.1%, 87.9%) and the per-channel binning studies do not carry over.
3. **c-tag SF/edges as MVA features** (N2): the +43% Up is unexplained, and the per-era edges are missing. This is the largest nuisance group, and it feeds the MVA inputs.
4. **The muon prompt-MVA SF chain** may double-count the ID efficiency (#2). It affects every MC process, and the tt normalisation is fitted against it.
5. **negrw disjointness** needs rechecking after the lepton change, for DY in 2022postEE; overlap is a source-inspection risk, not a measured result (section 2).
6. **Nonprompt/fake leptons are taken from MC only.** There is no data-driven estimate. The 08-12 diagnostic found 0.3–0.5% nonprompt in tt with the old leptons, and the ttH-MVA cut lowers it further. W+jets in the eμ SR is still fake-driven and relies on MC (with negrw). Low priority, but a reviewer will ask.
7. **The other Higgs cross sections use unknown mH and sources** (#6).
8. **Trigger SFs are still disabled** (accepted gap, 2026-08-11). Leptons are tighter now, so the efficiency for the new WPs is unmeasured. This is a known gap; it is only flagged here because the selection changed.
9. **Legacy has no input-completeness check** (N4), so partial jobs give silent yield loss.
10. **v11 training inputs are missing** from their recorded EOS path, so v11 cannot be reproduced for an A/B comparison of models.
11. **Era coverage:** H+b and H+c are in all 4 eras. negrw and v11 are trained on 2022postEE (backgrounds) only. The c-tag one-hots use one set of edges for 2022 and 2023.

Checked and **not** a problem: the negrw dataset names match all 4 era YAMLs; the ctag2d SF maps 2023preBPix/postBPix to "2023"; the EOS file count is 48%; DY replacements are the same generator.

Keeper review (2026-11-05): checked this record and its evidence boundaries, not the remote implementation. Changed the negrw overlap wording to a risk pending event-ID checks; selection changes alone do not demonstrate overlap. SF concerns remain provenance questions, not demonstrated double-counting. DAS completion counts do not validate the new PDF-weight contents.

## Limits of this audit

- **Not run:**
  - unit tests (standing rule; the code is unchanged since the logged runs, or no log exists — that is the reviewer's call);
  - `crab status`;
  - `nLHEPdfWeight` in the re-NANO outputs;
  - the negrw overlap/coverage check;
  - re-derivation of the ggH/VBF/ZH cross sections against a source;
  - a numerical effect of the JEC `pt_raw` issue.
- **Not reviewed:** the correctness of the TRAIN/RUN code (other agent).
- **Not found:** where `hww_combine_fixed` went.
- The muon/electron SF factorisation concern is based on the correction **names** and docstrings, not on the SF provenance.
- Everything here is agent-reported.
