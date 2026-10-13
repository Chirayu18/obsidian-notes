---
tags: [reference]
status: active
date: 2026-10-01
source: lxplus
---
# Full rerun with all systematics — workflow `hww_combine_full` (2026-10-01)

Repo: `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` (uncommitted edits, all with backups).
Outputs: `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_full[_ttsyst]/<era>/`. Logs/scripts: `/eos/user/c/cgupta/higgscharm/{logs_runall,runall}/`.
`hww_combine_2dcat` (the 1034 result, 2022postEE) is left untouched.

## User decisions (2026-10-01)
- New workflow, rerun everything incl. 2022postEE. **2022preEE + 2022postEE first; 2023 only after 2022 looks good.**
- Trigger SFs: **stay OFF** (reconfirmed). Flavour scheme: unchanged (30% lnN `xsec_hplusc_4FS_5FS`).
- tt modelling from dedicated samples: **hdamp (158/418), mtop (171.5/173.5), UE tune (TuneCP5 Up/Down)**. Colour reconnection NOT included.
- Signal: **central** `HPlusCharm-4FS-MuRFScaleDynX0p50-HToWWTo2L2Nu` (all 4 eras on DAS, ~1M evt/era; 22EE and 23 still PRODUCTION status) and central `HPlusBottom_5FS-...-HToWWTo2L2Nu` replace the private samples. **xsec = placeholder (private values) until the user provides XSDB.**
- EOS cleanup approved and done: hww_combine_fixed, hww_ctag_compare, stale July preEE/2023 2dcat, 2dcat/2023postBPix, quarantine_20260730 → quota 597 GB / 1 TB.

## What the new workflow adds
| item | how |
|---|---|
| top-pT (tt) | `toppTWeight` → shape `top_pt` |
| Higgs+HF composition (ggH/VBF) | `higgsHFWeight` → shape `higgs_plus_c`; interim `flavor_composition_ggH` lnN removed |
| MET unclustered | new object-shift trees (jerc.py PuppiMET fix from Aug 11) |
| tt hdamp / mtop / UE | workflow `hww_combine_full_ttsyst` (nominal only, keys tt_hdamp/tt_mtop/tt_tune); alt-sample shapes at card build |
| binned W+jets + WH→WW in 2022preEE | as already in 2022postEE |

## Bugs found and fixed
1. **7 dead nuisances in the current card.** `pileup, muon_id, muon_iso, electron_id, electron_reco_{RecoBelow20,Reco20to75,RecoAbove75}`
   are Up/nominal = 1.00000 exactly in `v11_hplusc_2dcat` — the card asks for `weight_pileupUp` etc. while the processor writes
   `weight_CMS_pileup_2022Up`, `weight_CMS_eff_m_id_2022Up`, …; the builder silently falls back to nominal for missing columns.
   New workflow uses the real names (`_2022` → `_2023` substituted per era at card build).
2. **`lhescale.py` multiplied every event weight by w4³** (w4 = LHEScaleWeight[4], used as the nominal factor of all three
   scale nuisances). Invisible when w4≈1; produced the 1e13 weights in WminusHTo2Tau/WplusHTo2Tau (w4 up to 2.4e4).
   Fixed: nominal 1, up/down = w_var/w4. Backup `lhescale.py.bak_pre_nomfix_20261001`. Also added a missing `import warnings`.
3. **WH dropped from the card**: process `WH` (WH→WW, WH→ττ) was in no `process_map` group → added to higgsbkg.

## Open (need user)
- XSDB cross sections of the central H+c and H+b HToWWTo2L2Nu samples.
- **Wγ** (`WGtoLNuG_PTG*`, process `WG`) is processed but in no card group — add to diboson?
- `CMS_ctag2d_2022` Up raises SR signal yield by +43% (higgsbkg +33%, tt +15%) in the current card — verify before the final limit.
- 2023postBPix can now be included (central signal exists).

## Update 17:00 — local tests + two more fixes, 2022 submitted
Local 1-file tests (2022postEE, TT / ggH / WH→ττ / central H+c) in the condor image:
- lhescale fix works: scalevar nominal factor = 1 everywhere; WH→ττ nominal/genweight ≤ 2.2 (was up to 1e13).
- `weight_top_pt` on tt (0.92–1.06), `weight_higgs_plus_c` on ggH: present.
4. **MET-unclustered shift never fired for Run 3**: the Aug-11 fix only patched `get_corrected_jets_coffea`; Run 3 uses
   `get_corrected_jets_correctionlib`. Added there as a vector shift (NanoAOD unclustered-varied PuppiMET − PuppiMET) on
   top of the re-corrected nominal. Backup `jerc.py.bak_pre_metunc_correctionlib_20261001`.
5. **MET never followed ANY object shift (pre-existing, all past results).** Workflow `met: events.PuppiMET` = raw
   NanoAOD branch; jerc.py writes the corrected/shifted MET into `events.MET`. So JES/JER never moved met_pt, mTll, mTl2,
   the MET>45 cut or MET-based MVA inputs. New workflows use `met: events.MET`. Verified: JES Up moves met_pt in 100% of
   events (median 1.9 GeV), MET-unclustered median 0.9 GeV; mTll/mTl2 follow. (`hww_combine_2dcat` left as is.)
Test-harness gotchas: inside the coffea image, EOS FUSE needs `-B /eos -B /run/user` + `KRB5CCNAME`; without `--eos`
submit.py writes parquets to `~/public/higgscharm/outputs/`.

**Submitted 2022-10-01 17:00:** `hww_combine_full` + `hww_combine_full_ttsyst`, 2022preEE + 2022postEE
(logs `/eos/user/c/cgupta/higgscharm/logs_runall/submit_hww_combine_full*_2022*.log`). 2023 waits for user OK.

## TODO logged 2026-10-02 (user): RETRAIN the v11 MVA on the new production
The current model (`hwwcom_multiclass_v11_2dcats`, trained July on the old 2dcat inputs; config `HPlusCHToWW_2dcats`,
script `Projects/HToWW/lxplus-2026-07-12/train_v11_2dcats.sh`) predates this rerun. Retrain "at some point" on
`hww_combine_full` once all eras are in, because the inputs changed:
- **central** H+c signal (~1M evt/era, ~3.5× the private stats) instead of the private sample;
- MET is now the **JEC-recorrected** `events.MET` (MET, mTll, mTl2 and MET-based features shift slightly);
- scale-weight fix changes per-event weights slightly (w4³ removed); WH now in higgsbkg;
- jet-binned W+jets + WH in 2022preEE; 2023 eras once processed.
**Wγ decision (user, 2026-10-02): do NOT add `WG` to the card now; ADD IT (to diboson, in training and in `process_map`)
WHEN RETRAINING.** It was excluded from the July training and therefore never got a card group. Also decide then whether to use the
`--split test` held-out events for the final fit (2022postEE backgrounds overlap the training events).
Until then, the July model is used for inference on the new parquets.

## TODO logged 2026-10-02 (user): integrate alternative-sample systematics properly into the framework
**Now (stopgap):** the tt modelling variations (hdamp 158/418, mtop 171.5/173.5, TuneCP5 Up/Down) run in a SEPARATE
workflow `hww_combine_full_ttsyst`, a copy of `hww_combine_full.yaml` with `object_shifts: false` and only the
tt_hdamp/tt_mtop/tt_tune datasets. Reason: `object_shifts` is a per-WORKFLOW switch; the framework cannot run some
datasets nominal-only. Verified 2026-10-02 that these cannot be weights: TTto2L2Nu NanoAOD has only LHEScaleWeight(9),
LHEPdfWeight, PSWeight(4); `LHEReweightingWeight` is empty.
**Drawback:** two yamls must be kept in sync by hand (any edit to the main workflow must be repeated or the copy regenerated).

**Wanted (like hh2bbww / columnflow):** mark such datasets as *shift datasets* in the config, e.g.
```yaml
TTto2L2Nu_Hdamp158:
  key: tt
  shift_of: TTto2L2Nu        # the nominal it replaces
  shift: tt_hdampDown       # nuisance name + direction
  # => processed nominal-only (no object shifts), never added to the nominal tt
```
hh2bbww (`hbw/config/config_run2.py`) does exactly this: `tune_up/down`, `hdamp_up/down`, `mtop_up/down` are shifts flagged
`disjoint_from_nominal` and served by dedicated datasets. Needed pieces in our framework:
1. per-dataset object-shift switch in `base.py`/`correction_manager` (skip the shift loop for shift datasets);
2. combine builder: build `<proc>_<shift>{Up,Down}` templates from the shift datasets (ratio to their nominal sample,
   applied to the full process), so no wrapper script is needed;
3. remove `hww_combine_full_ttsyst` afterwards.
Same mechanism would also serve future alt-sample systematics (colour reconnection CR1/CR2/ERDOn, V+jets/DY alternatives).

## 2026-10-02 — Central signal LHE weights are broken → fixed in the framework, signal reprocessed
First 2022preEE card: full fit HUNG; stat-only 888. Template scan showed the **central H+c** theory variations were
nonsense: `lhe_pdf` Up ×11–14 / Down ×0.00, `scalevar_*` Up AND Down both ×1.8–3 (same side).
Cause (Runs-tree sums, full generated sample): in the central `MuRFScaleDynX0p50` FxFx samples **every LHE variation is
offset ~2× from the nominal** — LHEScaleSumw 1.49–2.47 (μ=1 entry = 1), LHEPdfSumw replicas mean 2.20 (H+c) / 1.88 (H+b).
Private H+c (0.87–1.07, 1.00) and TTto2L2Nu (0.88–1.13, 1.00) are fine. Likely the variations were computed around the
default dynamic scale while the nominal uses 0.5× it. In addition, PDF **member 0 is inconsistent with the replicas
per event** (replicas agree to 0.5%, member 0 offset by an event-dependent factor) → Hessian sum vs member 0 gives +116%.
**Fix (opt-in, only `lhe_renorm_datasets: [HplusCharm_4FS_HToWWTo2L2Nu, HplusBottom_5FS_HToWWTo2L2Nu]`):**
- new `analysis/corrections/lhe_norm.py`: per-file generator means from the Runs tree (genEventSumw-weighted, cached);
- `lhescale.py`: each scale variation divided by its generator mean (keeps acceptance/shape, removes offset);
- `lhepdf.py`: each member divided by its generator mean, and the per-event **mean of the 100 replicas** used as centre;
- `correction_manager.py` passes the norms for listed datasets (prefix match: jobs run as `<sample>_<partition>`);
- `workflow_config_builder.py`: plain string lists allowed under `event_weights`.
Backups `*.bak_pre_lhenorm_20261002`. Verified on a central H+c file: lhe_pdf **±5.0%**, scale −14…+2% (Up/Down opposite).
Old signal outputs MOVED (not deleted) to `/eos/user/c/cgupta/higgscharm/_quarantine_lhebug_20261002/`; the two samples
resubmitted (10 jobs). Unattended pipeline `runall/pipeline_2022.sh` (tmux pipe2022): wait → re-merge → inference →
cards → combineCards (2022preEE+postEE) → limits; summary in `logs_runall/pipeline_2022.done`.
Other fixes today: coffea `xrootdtimeout` 60 s → 600 s in submit.py (most first-pass failures were "Operation expired",
395/~520 at Rutgers); tt alt-sample ratio uses the integrated ratio where a bin's MC-stat error > 10%.

## 🎯 2022 BASELINE (2026-10-05) — `hww_combine_full`, expected 95% CL (blind Asimov)
| card | full | stat-only | freeze autoMCStats |
|---|---|---|---|
| 2022preEE (8.0 fb⁻¹) | 1549 | 888 | 1451 |
| 2022postEE (26.7 fb⁻¹) | 1076 | 546 | 985 |
| **2022 combined** | **905** | **463.5** | **831** |
Cards: `outputs/combine/full/v12_hplusc_full_{2022preEE,2022postEE,2022}.txt` (combineCards, era-prefixed channels;
lumi_13p6TeV_2022 correlated across 2022 eras; rate_tt decorrelated per era). Built by `runall/make_combine_inputs_full.py`.
Compare old 2022postEE-only `hww_combine_2dcat`: 1034 (stat-only 641). postEE now: stat-only better (central signal,
SR signal 0.26→0.32), full slightly worse (dead nuisances revived, MET follows JES/JER, MET-unclustered, top-pT, hdamp/mtop/UE).
MVA = July v11_2dcats (trained on PRIVATE signal + old 2022postEE bkg) — caveats: central-signal transfer unchecked,
corrected-MET inputs, 2022postEE bkg overlaps training events. Retraining logged.
**postEE yield changes vs 1034 card (SR):** signal +24%, higgsbkg +19% (WH added), tt −5%, **V+jets +36%**. Not from w4³
(w4 = 1 for all these samples). Selected-event counts rose: W 0J/1J/2J +35/+26/+15%, DY +13%, ggH +15% → attributed to
the JEC-re-corrected MET (MET>45 and mT cuts); to be validated with data/MC (plots: condor 9491705).
Pipeline ran as condor job 9491687 after the interactive run was killed by the lxplus logout reaper (2 Oct 17:02).

## 2026-10-05 — data/MC check, plotting hang, band decomposition, postEE slope (IN PROGRESS)
- 2023 SUBMITTED (user OK, EOS 759 GB/1 TB): 1079 jobs (main 619 preBPix + 386 postBPix; ttsyst 44 + 30).
  Era yamls `.bak_pre_full_*`; central H+c/H+b + tt variations (+ binned W, WH for postBPix). Script `runall/submit_full2023.sh`.
- Plot hang: `analysis/postprocess/build_color_map.py` infinite loop once all 20 tab20 colours were used (triggered by
  the 6 new tt_* process names). Fixed (reuse after one pass; backup `.bak_pre_infloop_20261005`). run_postprocess logs
  go to `outputs/<wf>/<era>/output.txt`, not stdout. Plots: `outputs/hww_combine_full/<era>/base/*.png` (53/era).
- Data/MC: 2022preEE flat ≈1.0 (MET 1.05→0.95). 2022postEE overall 0.923 with a SLOPE: MET 1.0→0.83, mTll 0.98→0.77,
  Njets 0.93→0.80, jet η 0.93 barrel → 1.05–1.1 at |η|>2, φ flat. SAME slope in old hww_combine_2dcat (raw PuppiMET)
  → pre-existing, not from the MET fix. top-pT IS applied in nominal (toppt.py: nom=SF, Up=2SF−1, Down=1; yaml comment wrong).
  No jet veto maps applied in the workflow (files exist in correctionlib_files.py, unused).
- Band decomposition (`runall/band_breakdown.py <era>` → `outputs/hww_combine_full/<era>/band_breakdown/`, plots + summary.json):
  band = MC stat + all weight variations (no object shifts, no lnN). ~90% of the variance from 3 tt sources:
  CMS_ctag2d_2022 (integrated 16.5% postEE / 12.2% preEE, 75–80% on tt), scalevar_muR_muF 11.7%, scalevar_muR 10.1%.
  The tt scale normalisation is NOT in the fit (rate_tt floats, no_theory:[tt]) → plot band overstates fit uncertainty.
- Shape diagnostic (Δχ², norm floated) postEE: MET χ² 309/19 — best fixes scalevar_muR_muF Down −97, top_pt Up −54,
  ps_fsr Down −49; Njets 124/14 — muR_muF Down −89, ISR Up −69; mT: pileup Down −20…−23. preEE MET only 47/19.
  Same tt sample both eras → points to an ERA-SPECIFIC jet effect (JEC/JER/pileup), not tt modelling.
- NEXT: (a) ctag2d SF size — code read (ctag2d.py: up_Total/central ratios, candidate c-jet, flav=hadronFlavour, pt
  clipped 20–9999) — need numeric check of up_Total vs central per category; (b) test JES/JER Down shift trees vs the
  postEE slope; (c) pileup; (d) jet veto maps; (e) make plot band mirror the fit (drop tt normalisation theory).

## 2026-10-06 — TWO FRAMEWORK BUGS found via the slope study (fixed in code, rerun pending)
- (a) ctag2d SF size check DROPPED — user: an expert is already checking the c-tag SF.
- 2023 first pass: 826/1079 done; 253 failed, ~all `XRootD [FATAL] Connection error` at two dead sites
  (cms-se0.kipt.kharkov.ua, se01.grid.nchc.org.tw) + 3 wall-time. Resubmitted all 253 via global redirector
  (`runall/resubmit_all.py <eras>`, `completion.py <eras>` — both now take eras as args; log `logs_runall/resubmit_2023_r1.log`).
- Slope study `runall/slope_study.py <era>` (condor `~/pipeline_condor/slope_job.{sh,sub}`, out
  `outputs/hww_combine_full/<era>/slope_study/`): rebuilds data/MC from parquets and re-fits shapes under JES/JER/
  MET-uncl shift trees, pileup Up/Down, top-pT off, jet veto map (leading jet), and per-run data.
  preEE control showed JER Up == JER Down == "top-pT off" EXACTLY → two bugs:
  1. **toppt.py returned early when `shift is not None`** → every object-shift tree (JES/JER/e/μ/MET-uncl) of tt lacked
     the nominal top-pT SF (verified: w_shift = w_nom / SF_top exactly, +1.5% tt sumw). Every tt shape template from an
     object shift therefore carried a spurious +1.5% + top-pT shape in BOTH Up and Down. Fix: under a shift add the
     nominal weight only (as pileup.py does). Backup `toppt.py.bak_pre_shiftnom_20261006`.
  2. **JER variations were a no-op**: JME JSONs on cvmfs changed 2026-06-05 ("Split JER SF nom and up/down tags"):
     `*_ScaleFactor_AK4PFPuppi` now has inputs (JetEta, JetPt) only, with a separate absolute `*_SFUncertainty_AK4PFPuppi`.
     jerc.py passed systematic="up"/"down" via get_corr_inputs, which silently found no `systematic` input → JER Up = Down
     = nominal for 100% of jets (verified on 3000 tt events). Affects EVERY production since early June incl. the July
     2dcat runs and the 2022 baseline (905). Fix: if the SF has no systematic input, JERSF = SF ± SFUncertainty.
     Verified after fix: JER up/nom 0.95/1.001/1.03 (5/50/95%), MET moves. Backup `jerc.py.bak_pre_jersplit_20261006`.
  No other correction module has the toppt-style early return (pileup/ctag/e/μ/LHE/PS checked; higgs_hf nominal = 1).
- Consequence: all MC needs reprocessing for correct CMS_res_j shapes (data unaffected): 2184 MC jobs
  (preEE 407, postEE 909, preBPix 528, postBPix 340; TT* 22/65/100/72). Awaiting user go-ahead.
- JER fix convention verified: new `SFUncertainty` is ABSOLUTE — old explicit up SF == SF + unc to 4 digits
  (e.g. 1.128+0.018 = 1.146). The 2026-07-15 changelog text "SF×(1±unc)" is misleading. 2023 old "down" was bounded at
  1.0; new SF−unc can go below 1 (follows the published JSON).
- User decision (2026-10-06, BEFORE bugs 3–6 below were found): "Finish 2023 first, rerun after".

### More bugs from the systematic audit (`runall/audit_syst.py <era>`, condor `audit_job.*`, log `logs_runall/audit_<era>.log`)
3. **Type-1 MET re-correction wrong (MAJOR, nominal AND shifts, data AND MC)** — jerc.py correctionlib path called
   coffea `corrected_polar_met(PuppiMET, new_pt, raw_pt)`, i.e. MET_stored_type1 + Σ(new − raw). NanoAOD PuppiMET is
   already Type-1, and coffea's formula is met + Σ(jet_pt − jet_pt_orig), so this undid Type-1 with the wrong sign
   (validated: raw − Σ(corr − raw) rebuilds stored PuppiMET to ±1 GeV; raw + Σ gives ±35 GeV). Effects measured on 4k
   events: tt MET median 65.9 vs Type-1 74.8, spread −28…+7 GeV; data −23…+15 GeV; and under JES Up the MET moved
   WITH the jets (wrong direction) → "JES Down fixes the slope" in the slope study is an artifact of this.
   Introduced effectively on 2026-10-01 when the workflow switched met field PuppiMET → events.MET (the re-corrected
   one); July runs used stored PuppiMET (correct Type-1, no shifts) → the postEE slope there is NOT explained by this.
   Fix: metinfo = (PuppiMET, jets.orig_pt [NanoAOD-corrected], new pt) for nominal + JES/JER shifts.
   Verified: data re-corrected = reference (30.4 vs 30.4 GeV median), corr(ΔMET_x, Δjet_x) under JES Up = −1.000.
   Backup `jerc.py.bak_pre_type1fix_20261006`. (Run 2 coffea path line ~199 has the same call pattern; not used.)
4. **CMS_res_e dead** — electron_ss.py evaluated the nominal "smear" key for smear_up/smear_down (comment even
   describes the intended max(smear−unc,0)). Fixed to "smear_up"/max("smear_down",0). Backup `.bak_pre_smearfix_20261006`.
5. **lhe_pdf blow-up from powheg-MiNNLO WH→ττ** — per-event Hessian δ of O(100–1000) in a few events: WminusHTo2Tau
   summed pdf Up/nom 22.8 (postEE), WplusHTo2Tau 4.5 → card higgsbkg lhe_pdf Up 6.2× (CR_diboson), 2.5× (CR_st),
   2.0× (CR_higgsbkg). Fix: cap per-event δ_pdf, δ_αs at 0.5 (columnflow-style outlier threshold); <1% change for all
   other samples (table in session). Backup `lhepdf.py.bak_pre_deltacap_20261006`.
6. Minor / noted, not changed: lepton scale/res shifts do not propagate to MET (update_met imported, unused);
   H+c central sample has no αS members (lhe_alphaS = 1); `raise (f"...")` JEC-tag sanity check in jerc.py can never
   fire (np.all(...) == -1 precedence).
- Card-level design points (recommendations, not bugs): scalevar_muR, _muF AND _muR_muF are three independent
  nuisances (over-counts; usual = muR+muF or one envelope); theory nuisances share one name across all processes
  (signal and backgrounds correlated; usually decorrelated per process); CMS_scale_j/res_j shared between preEE and
  postEE (different JEC campaigns; usually decorrelated); plot band sums all three scale variations too.
- Checked OK: MET filters (standard Run 3 list, data+MC), golden JSON, jet ID (Run 3 NanoV12 jetId fix), muon_ss
  (distinct keys, res_m/scale_m move muon pT), pileup / e/μ ID / ctag shift-tree handling, higgs_hf nominal = 1.
- Slope study (pre-fix numbers, postEE / preEE): jet veto map (leading jet) removes 1.7% / 1.3% of events in BOTH data
  and MC → negligible for the slope; pileup Up/Down small; top-pT on is better than off (χ² 419 vs 497); per-run
  E/F/G show the SAME MET slope → not a run-period (EE leak) effect. To be redone after the MET fix.
- **Smoke test PASSED (2026-10-06, full processor, 1 file each, 2022postEE, `runall/localtest_fix.sh` +
  `runall/validate_smoke.py`)**: TT shift trees w_shift/w_nom = 1.0000 (top-pT now in); JER moves jet pT in 97% of
  events and MET follows; CMS_res_e moves electron pT (51% = events with the electron leading), Up≠Down; JES moves MET
  in 100%; WminusHTo2Tau lhe_pdf Up/nom 1.112 (was 22.8), αS 1.077. 2023: 993/1079 done (old/mixed code).
  Rerun of ALL data+MC, 4 eras, awaiting user go-ahead.

## 2026-10-07 — 2023 pipeline AS IS + Run 3 combined limit (PAUSED by user, resume here)
- User decision: run the 2023 pipeline as is (old/mixed code; 6 missing jobs accepted: preBPix EGamma1Cv2 1/2,
  GluGluHto2Tau 1/1, Muon1Cv4 1/8; postBPix DY50 1/15, W0J 1/42, W2J 1/31), get a combined limit, THEN fix things.
  Numbers are a pre-fix reference: they carry all 2026-10-06 bugs + review findings.
- Condor 9498399 (`~/pipeline_condor/pipeline_2023_job.{sh,sub}`): merge/inference (main + ttsyst), cards, combineCards
  → `outputs/combine/full/v12_hplusc_full_{2023,run3}.txt`, limits. Log `logs_runall/pipeline_2023.log`.
- **2023preBPix: full 1348, stat-only 604, freeze autoMCStats 1172.**
- 2023postBPix limit FAILED: one corrupted histogram (`SR_hplusc_hplusc_higgs_plus_cDown`, "unrecognized compression
  algorithm", 1 of 1878) in `v12_hplusc_full_2023postBPix.root` — EOS write glitch. Resume job condor 9499885
  (`pipeline_2023_resume.{sh,sub}`) rebuilds that card, checks every histogram is readable, recombines 2023 + run3, runs
  limits 2023postBPix / 2023 / run3 → results in `logs_runall/pipeline_2023.done` (and limit_<n>.log). It was left
  running unattended when the session paused (2026-10-07 ~16:45).
- NEXT on resume: read pipeline_2023.done; if run3 limit is there, report the table (2022: preEE 1549, postEE 1076,
  2022 905). Then the fix pass: review items (preEE SingleMuon/DoubleMuon duplicates, MVA ctag one-hot inputs,
  WH xsec 0.0, MET re-correction jet selection, muon SS JSON, NNLOPS scope, jet re-sort, jet veto map, strict
  missing-column fallback; ZH/ggH xsec need user call) → full data+MC rerun of all 4 eras.

## 🎯 Run 3 combined (pre-fix reference, 2026-10-07) — expected 95% CL on μ, blind Asimov
| card | full | stat-only | freeze autoMCStats |
|---|---|---|---|
| 2022preEE | 1549 | 888 | 1451 |
| 2022postEE | 1076 | 546 | 985 |
| 2023preBPix | 1348 | 604 | 1172 |
| 2023postBPix | 1689 | 894 | 1503 |
| 2022 | 905 | 463.5 | 831 |
| 2023 | 1077 | 498.5 | 943 |
| **Run 3 (all 4 eras)** | **691** | **338.5** | **616** |
Cards `outputs/combine/full/v12_hplusc_full_{2023,run3}.txt` (combineCards, era-prefixed; lumi per year; rate_tt per era;
CMS_*_2022/_2023 per year; theory nuisances correlated across all eras). Resume job 9499885 rebuilt the corrupted
2023postBPix card (all 1878 histograms readable). These numbers carry every bug in the 2026-10-06 audit + independent
review; they are the "before fixes" reference only.

### Run 3 (pre-fix) vs Run 2 (AN-23-102), 2026-10-08
AN-23-102 expected 1POI UL (line 669, Fig. 49): Run 2 **431** @ 138 fb⁻¹ (2POI 969); per period 2018 619 (59.8 fb⁻¹),
2017 773 (41.5), 2016postVFP 1256 (16.8), 2016preVFP 1197 (19.5). NB the "505" in June notes/papers.md was a misread PDF
line number — corrected in papers.md.
√L check inside Run 2 itself: 2018 619 → √(59.8/138) → 407 vs actual 431 (combination ~6% worse than pure √L).
Ours: Run 3 **691** @ 61.9 fb⁻¹ (7.98+26.67+17.79+9.45). Scaled to 138 fb⁻¹: 691·√(61.9/138) = **463** vs 431 → ~7% worse.
Same-lumi view: Run 2 scaled to 61.9 fb⁻¹ = 644 vs our 691; 2018 alone (59.8 fb⁻¹) = 619.
Caveats: pre-fix numbers (JER no-op and WH xsec 0 make ours optimistic; missing MVA ctag inputs slightly pessimistic);
our syst inflation ×2.0 vs stat-only, so √L scaling of our number is optimistic; μ is relative to SM at each √s.

**CORRECTION (2026-10-08, user):** the reference is the PUBLISHED paper CMS-HIG-24-009 (arXiv:2508.14988): expected UL
**506**, observed 1065 @ 138 fb⁻¹. The 431 above is from the older AN-23-102 v14 PDF in References (superseded). With 506:
ours scaled to 138 fb⁻¹ = 463 vs 506 → **~9% better**; Run 2 scaled to 61.9 fb⁻¹ = 755 vs our 691. Same caveats apply.

## 2026-10-13 — Cross-check of the central H+c LHE-weight fix (scale fix only partial)
Script `runall/lhe_xcheck.py`, one 2022postEE central H+c file (60k events) vs a DYto2L-2Jets amcatnloFXFX control file.
- **Control is clean:** DY scale means 0.94–1.03, PDF replicas 1.000, member0/replicas 1.000 per event. So our reading of
  NanoAOD is right and the **H+c sample's variation weights are broken**.
- **H+c:** originalXWGTUP/genWeight = 1 (nominal consistent). Scale [4] (1,1) and PDF member 0 are exactly 1 (copies of
  the nominal); **every computed variation is ~2× high**: scale 1.83–2.52 (both directions up), the 100 nf_4 replicas
  (LHA 325500–325600) 2.10–2.23 with only 0.6% spread per event. A real scale variation cannot go the same way by 2×, and
  replicas must scatter around member 0. The cause is unknown; the earlier "0.5× dynamic scale" explanation is a guess,
  and its direction is doubtful (a higher scale lowers this cross section).
- **The offset is not one global factor; it depends on the event category** (FxFx multiplicity):
  replicas 2.26 (NpNLO=0) vs 1.80 (NpNLO=1); scale (2,2) 2.67 vs 1.93; LHE_Njets=2 replicas 1.61.
- **PDF fix: correct.** It uses the per-event mean of the replicas as centre, which removes any per-event offset.
- **Scale fix: partial.** Dividing by the global mean leaves a fake shape across multiplicities:
  H+c (0.5,0.5) 1.02 / 0.91 and (2,2) 1.06 / 0.77 for NpNLO=0 / 1, i.e. **both directions down** for 1-parton events.
  DY control (genuine): 0.98 / 1.06 and 1.02 / 0.96, opposite directions. The "−14…+2%" signal scale effect quoted on
  10-02 is therefore probably mostly this artefact (the c-jet selection favours real-emission events).
- **To do:** (1) don't trust the signal scalevar shapes. Use acceptance ratios from the private H+c sample (sane weights),
  or normalisation from the xsec table with no signal scale shape. (2) Report to GEN / the sample requestor with the
  McM gridpack run_card (scalefact, systematics settings). H+b shows the same pattern (replicas 1.88).
- **Run 2 comparison (same check, one file each, 60k events): all Run 2 signal samples are clean.**

  | sample (RunIISummer20UL…NanoAODv9) | scale means | PDF replicas / member 0 |
  |---|---|---|
  | UL18 H+c 4FS amcatnloFXFX | 0.88–1.05 | 0.999 / 1.000 per event |
  | UL18 H+c 4FS amcatnlo | 0.84–1.02 | 0.999 / 1.000 |
  | UL17 H+c 3FS amcatnlo | 0.77–1.24 (opposite directions) | no PDF weights stored |
  | UL18 H+b 5FS amcatnloFXFX | 0.84–1.07 | 1.000 / 1.000 |
  | UL18 H+b 5FS amcatnlo | 0.73–1.06 | 1.000 / 1.000 |
  | **Run3Summer23 H+c 4FS amcatnloFXFX** | **1.82–2.52** | **2.17 / 0.44–0.71 per event** (same as 22EE) |

  Same generator configuration, clean in Run 2, broken in Run 3 → a Run 3 production problem (gridpack / MG version /
  systematics settings), not the physics setup. Strong evidence for the GEN report.
- **Root cause found (2026-10-13, gridpack on CVMFS).**
  - **The setup.** The Run 3 gridpack (MG 2.9.9) applies a custom `_mg5amc.patch`. It sets `runfac=1` and `cpower=2`, and adds a running charm Yukawa to `rwgt_muR_dep_fac`. The param card has `ymc = 0.986 # ymc(3 GeV), only to be used with proper MG5 patch`. The same patch exists in the Run 2 gridpack (MG 2.6.5).
  - **Nominal is OK.** Nominal σ from the weights: Run 2 UL18 FxFx 0.2636 pb, Run 3 22EE 0.2979 pb, Run 3 23 0.2982 pb. The ratio of 1.13 is roughly the energy scaling.
  - **The variations are what's broken.** They carry y_c(3 GeV) instead of y_c(μ), i.e. they miss the factor (m_c(μ)/m_c(3 GeV))² ≈ 0.44 per event. The patch evidently doesn't reach the 2.9.9 variation-weight code.
  - **Per-event correction validated** (`runall/percorr_test.py`). r = mean(replicas)/member0 measures the missing factor per event.
    - μF-only weights divided by r: **0.942 / 1.026 vs Run 2 0.946 / 1.021**. Exact, with no running model needed.
    - μR-varied weights also need ×(m_c(kμ0)/m_c(μ0))², which takes a running model (1-loop, nf=4). They come out at 0.97–1.05 vs Run 2 0.88–1.05. Approximate.
    - The multiplicity dependence now has opposite-direction variations, like DY.
    - PDF (replica-centred) was already exact. The global-mean `lhe_norm.py` scale fix must be replaced.
- **Current fix (global Runs-mean renorm) vs exact per-event correction** (`runall/fix_compare.py`): acceptance effect in an analysis-like gen region (2 dressed leptons pT>10 + ≥1 gen c/b-jet pT>20, |η|<2.5).
  - **H+c, 22EE (6 files, 112k events):**
    - μF 0.5 / 2: ours −8.0% / −5.9% vs exact −0.1% / +1.6%.
    - μR 0.5 / 2: ours +0.5% / −14.3% vs exact +9.3% / −7.8%.
    - (0.5,0.5) / (2,2): ours −1.6% / −13.9% vs exact +7.9% / −7.6%.
  - **H+b, 22EE:** same pattern. μF ours −8.8% / −2.4% vs exact −0.5% / +5.0%.
  - **Result.** The current fix biases every scale variation by **−6 to −10%** in the selected region, so both directions go down: a fake one-sided effect. It plausibly explains the one-sided `scalevar_muR` impact in the Run 3 fit. The μF columns are model-independent; the μR columns use 1-loop running.
  - **Verdict.** Replace with the per-event correction. PDF handling and the nominal are fine. Other samples are untouched (`lhe_renorm_datasets` lists only these two).
- **Per-event fix implemented (2026-10-13; repo uncommitted; backups `*.bak_pre_yukawafix_20261013`).**
  - **New module `analysis/corrections/lhe_yukawa_fix.py`.**
    - Measures F(μ0) = 1/r per event, with r = mean(PDF members 1–100)/member 0.
    - Inverts F to μ0 using the gridpack's own running, then multiplies each scale weight by F(k·μ0; μ0).
    - Has a dataset→table map. It raises if a `lhe_renorm_datasets` entry has no table, and refuses samples without the offset (median r < 1.2).
  - **Tables in `analysis/data/lhe_yukawa/`.**
    - Produced by `tab.f`, the patched `rwgt_muR_dep_fac` compiled with the `runalpha`/`runmass` routines from MG5_aMC v2.9.10 `reweight_xsec.f`. The patch applies with the identical offset as in the gridpack build log.
    - Inputs are the param-card values and α_s(M_Z) from LHAPDF: 0.11266 for 325500 (nf4, H+c), 0.11800 for 325300 (H+b).
    - H+c: y_c = 0.986 at 3 GeV, nf = 4. H+b: y_b = 4.18 at m_b, nf = 5.
  - **`lhescale.py`** uses the module via `yukawa_table`. `correction_manager.py` passes `table_for_dataset(dataset)`. PDF handling is unchanged.
  - **Results (corrected means vs Run 2 UL18):**
    - H+c 22EE: [1.007 1.008 0.970 0.947 1 1.021 0.888 0.971 1.023] vs [1.045 1.051 1.018 0.946 1 1.021 0.879 0.961 1.013].
    - H+c 23: same to 0.5%.
    - H+b: [0.971 0.952 0.841 0.912 1 1.016 0.853 0.999 1.088] vs [1.018 1.019 0.930 0.909 1 1.023 0.835 0.979 1.067].
    - μF-only and μR=2 entries agree to ≤1%; μR=0.5 entries are ~4% (H+c) to 7–9% (H+b) lower than Run 2. Run 2 differs in √s and MG version, so it is not an exact reference.
  - **Off-table events:** ~0.16%, all NpNLO=1, implied μ0 < 1.5 GeV. They get the measured factor only. ~1e-5 of events (r ≤ 0) keep ratio 1.
  - **Exactness:**
    - Exact: F(μ) itself (same code and inputs).
    - Approximate: μ0 from the replica mean, ±0.1% per event (clean Run 2 sample: replicas/member0 = 1.000 ± 0.001, 1–99% within 0.999–1.005).
    - Assumed, not proven in code: the stored variations carry F = 1, i.e. they miss the factor entirely. The 2.9.10 source does call `rwgt_muR_dep_fac` for the variations, so why it is ineffective there is unexplained.
    - Definitive closure would need running the gridpack with a debug print of F per event.

## 2026-10-13 (later) — TRUE root cause: the WW gridpack runs the Python systematics module (γγ gridpack skips it)
- **Provenance** (edmProvDump on MiniAOD):
  - **WW** used `/cvmfs/cms-griddata.cern.ch/phys_generator/gridpacks_tarball/pp/13p6TeV/madgraph/HPlusHF/HPlusCharm/HPlusCharm_4FS_MuRFScaleDynX0p50_M125_..._el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`. It is MG **2.9.18**, built Feb 2026 from `/eos/home-c/cgupta/HToWW/mcm_grid/genproductions_scripts/...` (our own build).
  - **γγ FxFx** used the slc7 MG 2.9.9 HToGG gridpack: the one dissected earlier, built by `bevila_t`.
- **Difference:**
  - The γγ gridpack's `runcmsgrid.sh` has a SAMPLE-SPECIFIC CHANGE ("Skipping execution of ./bin/aMCatNLO systematics") and keeps `reweight_scale/PDF = True`. The weights therefore come from the Fortran, which includes the patched running Yukawa.
  - Our gridpack has the standard genproductions additions (`reweight_scale/PDF = False`, `store_rwgt_info = True`) and runs the Python `systematics` module. That module recomputes every variation per contribution WITHOUT F(μR); the nominal still comes from the Fortran, so it is correct.
  - **This is the "missing patch".** The custom Fortran patch is present in both gridpacks.
- **The γγ 4FS FxFx sample is CLEAN** (22EE NanoAODv13): replicas/member0 = 0.999; stored scale means [1.048 1.052 1.014 0.947 1 1.019 0.879 0.960 1.011].
- **Our per-event fix vs γγ:**
  - μF-only: exact to 0.2% (0.948 / 1.021 vs 0.947 / 1.019).
  - μR entries: 1–4% off; NpNLO=1 (0.5,0.5): 1.185 vs 1.304.
  - Reason: the missing F is per contribution (each with its own μR) and cannot be undone with one per-event factor.
  - Caveat: the WW and γγ gridpacks differ (2.9.18 vs 2.9.9, NpNLO=1 share 32% vs 41%), so γγ is the right physics reference but not an identical sample.
- **MiniAOD LHEEventProduct** keeps 566 weights but no comment lines (rwgt info stripped), so an exact per-contribution recomputation from existing files is impossible.
- **Exact options:** (1) fix the gridpack (copy the γγ runcmsgrid change, in-code reweighting) and request a new production or extension; (2) private LHE-level generation with the fixed gridpack to derive the scale weights; (3) use the clean γγ FxFx sample's scale response at generator level as the reference.
- **Shape test vs the clean γγ 4FS FxFx sample** (`runall/shape_compare.py`, 22EE, 118k WW / 126k γγ events). Each variation's shape is normalised to its own integral, so any common factor cancels; max |deviation| from γγ is shown.

  | variable | variation | common factor | per-event fix |
  |---|---|---|---|
  | NpNLO | (0.5,0.5) | 0.33 (wrong direction: 1.02 / 0.92 vs 0.91 / 1.25) | 0.075 |
  | NpNLO | μR0.5 | 0.35 | 0.11 |
  | NpNLO | μR2, (2,2), μF | 0.11–0.17 | 0.010–0.022 |
  | Higgs pT | (0.5,0.5) | 0.27 | 0.064 |
  | Higgs pT | μR0.5 | 0.30 | 0.11 (top bins) |
  | Higgs pT | (2,2) | 0.09 | 0.023 |
  | Higgs pT | μF | 0.13–0.16 | 0.023–0.029 |
  | gen c-jet pT | all | 0.12–0.21 | 0.035–0.087 |

  - **Common factor:** fails (residual shape 10–35%).
  - **Per-event fix:** μF and μR-up are good to ≲2–4%; the μR-down family is off up to 7–11%, mostly in NpNLO=1 and high-pT tails. This is the per-contribution limitation.
  - The gen-jet multiplicity axis is not comparable: GenJets cluster the H→γγ photons.
- **Exactness test for single-scale events.** Events with weights identical to 6 digits (clusters, all NpNLO=0, i.e. one common central scale) have 1/r = 0.442196–0.442201 (spread 1e-6). The gridpack-code table gives F(62.5 GeV) = 0.441895, i.e. μ0 = 62.26 GeV (0.07%: the replica-mean offset or the exact scale). So the per-event fix reproduces the patch to <0.1% for single-scale events; the residual is entirely the multi-contribution NpNLO=1 events.
- **No central GEN-SIM / LHE / AOD exists** for the WW sample (DAS, incl. invalid): only MiniAOD and NanoAOD; the chain was wmLHEGS → DRPremixNoOutput.
- **`LHE_AlphaS` (AQCDUP) is NOT the weights' μR**: it varies inside identical-weight clusters.
- **Plots:** `outputs/hww_lhe_fix/scale_shape_vs_gg_{higgs_pt,npnlo,cjet_pt,summary}.png` (`runall/plot_shapes.py`).
- **Where the residual lives (S/H × NpNLO split, `runall/sh_classes.py`).**
  - **The sample's Born is c c̄ → H** (FxFx 0j + 1j). S-events have NpNLO outgoing partons; H-events have NpNLO+1.
  - **Raw per-class means, WW-fixed vs γγ-clean:**
    - NpNLO=0 S (61% of events): agree to ≤0.3%.
    - NpNLO=0 H (19%): ≤1%.
    - NpNLO=1 S (16%): 1–3%.
    - **NpNLO=1 H (5%): off.** (0.5,0.5) 1.75 vs 2.24, μR0.5 1.83 vs 2.35, μR2 0.62 vs 0.57, (2,2) 0.63 vs 0.57; μF fine.
  - **Why:** the real emission and its counterterms have different FxFx clustering scales, so a single per-event factor cannot correct them.
  - **In the ≥1 gen c-jet region** the class shares become 16 / 20 / 47 / **17%**, so the bad class is 17% of the signal-like region.
- **Composition differs between the samples (flag).** The WW sample has fewer NpNLO=1 events than γγ (20% vs 27% inclusive). Different gridpacks (MG 2.9.18 vs 2.9.9): check whether the nominal merging differs too.

### 2026-10-13 (late): the NpNLO=1 H "residual" is mostly the γγ reference, not the fix
Scripts: `runall/scale_pred.py`, `runall/unmix.py` (22EE, 3 WW files vs 3 γγ files).

- **MG5_aMC source (v2.9.10 `fks_singular.f`, `setscales.f`, `reweight_xsec.f`):**
  - The running factor is applied **per contribution**: `rwgt_muR_dep_fac(sqrt(mu2_r(kr)), sqrt(scales2(2,i)))`.
  - In an H-event, the real emission takes its FxFx scales from the n+1 momenta (`setclscales(p)`, "mohdr"). The FKS/MC counterterms in the same event take them from the n-body counter-event momenta (`setclscales(p1_cnt(0,1,0))`, "izero").
  - The FxFx μR (ickkw=3) is mT(colourless)/2 for the 0-jet Born and the **jet kT clustering scale**/2 for the 1-jet Born.
  - S-events: every piece is n-body, so there is one scale.
- **The scale can be rebuilt from the LHE partons.** Comparing μ0 from r with the prediction:
  - NpNLO=0 S: median 0.9962 vs 0.5·mT(H).
  - NpNLO=1 S: median 0.9957 vs 0.5·pT(parton).
  - The 0.4% offset is the known 0.07% F offset seen in μ. So S-events behave exactly as the code says.
  - NpNLO=1 H vs the real-emission scale: correlation 0.6 only. These are two-scale events: μ(real)/μ(counterterm) median 1.55, 16–84% between 0.9 and 4.9.
- **Two-piece un-mixing (exact model for H-events).** Per event:
  - r = bR + bC; 1 = bR·F(μR) + bC·F(μC); stored broken S_k = bR·aR(k) + bC·aC(k), with a = α_s ratio².
  - μR comes from the partons; μC from the FKS-mapping candidates or a scan.
  - Closure against the stored muR-only weights: |Δ| median 0.07–0.1%, 92–96% of events < 0.5%.
  - **Result: the class mean moves only 1.831 → 1.849 (μR0.5) and 0.622 → 0.618 (μR2).** F runs slowly, so the two-scale effect on the weights is ~1%.
  - Caveat: the closure is weakly sensitive to μC, but so is the result.
- **Same-scale comparison with γγ (bins of the real-emission μR):** medians agree to ≤0.3% in every bin; μR0.5 [20,30) gives 1.614 vs 1.615.
- **The class-mean gap comes from the γγ sample:**
  - (a) 1.7% of γγ NpNLO=1 H-events (**7% of the class weight**, all genW>0) have **constant** ratios μR0.5 = 6.198 and μR2 = 0.308, independent of kinematics. That means one piece sits at a fixed, very low scale (around a GeV). There are **zero** such events in WW, before or after the fix (the broken ratio would be ~12).
  - (b) The scale spectrum differs: WW has no events with μ(real) < 15 GeV, γγ has 6%; NpNLO=1 is 20% vs 27%. This is a different merging setup between the MG 2.9.18 and 2.9.9 gridpacks.
  - Removing (a) and matching (b): μR0.5 is 1.831 (WW fix) vs 1.953 (γγ), μR2 0.622 vs 0.609. That is down from 1.83 vs 2.33.
- **Verdict:** the per-event fix is good to ~1% even for NpNLO=1 H-events. The remaining ≤6% gap in that 5% class (~0.3% inclusive) cannot be attributed to the fix, since the reference sample differs in generator setup. A private sample with both weight sets (option 3) is now only the final proof, not a necessity.

### 2026-10-13 (later still): CORRECTION — γγ is not odd; our WW sample is. Independent check vs Run 2 UL18 WW
- **Run 2 UL18 H+c→WW 4FS FxFx** (clean Fortran weights; 3 NanoAODv9 files, 29k NpNLO=1 H-events) vs our Run 3 WW, using `runall/unmix.py` with TAG=run2:
  - **It has the same constant-ratio "spike":** 1.7% of NpNLO=1 H-events, 7.2% of the class weight, 6.199 / 0.308.
  - The same low-scale population: 6.5% of these events have μ(real) < 15 GeV (γγ 6%, our WW 0.2%).
  - The same class means: μR0.5 2.339, μR2 0.572 (γγ 2.332 / 0.573; our WW fix 1.831 / 0.622).
  - Per scale bin, its medians again match our fixed WW to ≤0.3%.
- **So two independent clean central samples (MG 2.6.5 WW, MG 2.9.9 γγ) agree, and our MG 2.9.18 WW sample is the outlier.** The per-event fix is right for the events we have. But our sample (a) has no spike-type weights and (b) has almost no one-jet events with a jet clustering scale below 30 GeV (= qCut), which is a NOMINAL kinematics difference. NpNLO=1 is 20% vs 27%.
- **Identical between the three gridpacks:**
  - proc_card (`p p > h [QCD] @0; p p > h j [QCD] @1`, model loop_sm_MSbar_yb_yc-yc4FS);
  - param_card (same md5);
  - run_card (apart from beam energy and our systematics flags);
  - Pythia FxFx settings from the MiniAOD provenance: qCut 30, qCutME 10, nJetMax 1 in all three.
- **Remaining differences:** the MG version (2.9.18 vs 2.9.9 / 2.6.5) and the Python systematics module. (b) is nominal-level, so it must be the MG version or the generation itself. (a) could be either.
- **Impact if the older samples are right:**
  - μR-down for one-jet H-events is ~20% low in our sample. That class is 5% inclusive (~1–2% on the inclusive μR-down) and 17% of the c-jet region (~3–4%).
  - The nominal one-jet composition also differs, which is a signal-modelling question beyond the weights.
- **Higgs-pT shape plot without the γγ spike events** (`outputs/hww_lhe_fix/scale_shape_vs_gg_nospike_*.png`, `runall/plot_shapes_nospike.py`): the spike is only 233/105k events (0.4% of the weight) inclusively, so removing it barely moves the normalised shapes. The per-event fix agrees with γγ within ≲5%, i.e. within the statistical errors.
- **Next:**
  1. Compare the NOMINAL distributions (Higgs pT, c-jet pT, NpNLO) of our WW vs γγ vs Run 2.
  2. Run a quick private LHE-only test, with identical cards under MG 2.9.9 vs 2.9.18, to pin the version effect.

### 2026-10-13 (evening): spike events = MG's 1 GeV scale floor; fix extended; edge-case audit
- **What the spike events are:** one-jet H-events whose renormalisation scale is clamped at **exactly 1 GeV** in MadGraph.
  - The patch's own running at μ = 1.000 GeV gives F = 2.085, F(μ/2) = 6.406, F(2μ) = 1.288.
  - Measured: 1/r = 2.085, and clean/raw = 6.404 / 1.289.
  - Clean samples therefore show the constant ratios 6.199 / 0.308.
- **Our sample has them too.** The raw weights show a constant cluster 0.968 / 0.239 (133 events, 0.8% of one-jet H-events). These sat below the table edge (1.5 GeV), so the fallback multiplied them by a flat 2.08, giving 2.02 / 0.50.
- **Fix updated** in `lhe_yukawa_fix.py` and `analysis/data/lhe_yukawa/`:
  - The tables start at 1 GeV (`tab.f`).
  - A 0.5% tolerance at the edge absorbs replica-mean noise. Floor events now give **6.1986 / 0.3078**.
  - Events with F(μ0) above F(1 GeV) (only near-total cancellations; 7 events, one had 1/r = 62 and a ×(−103) variation) now get no variation, like r ≤ 0.
  - `build.sh` path bug fixed: it ran in the CMSSW src dir. Its stray files there were removed.
  - Old tables backed up at `/tmp/cgupta_gp/low/*.bak_1p5` (node-local).
- **Edge-case audit** (`runall/edge_audit.py`, 142k ours / 133k γγ / 300k Run 2; `outputs/hww_lhe_fix/edge_audit*.txt`):

  | category | events | weight share |
  |---|---|---|
  | normal | 142,153 | 99.89% |
  | 1 GeV floor | 133 | 0.09% |
  | r ≤ 0 | 5 | 0.004% |
  | off-table high | 7 | 0.005% |
  | off-table low | 6 | 0.004% |

  - No member0 = 0 or non-finite weights. No other constant-value clusters in any class or sample, apart from the common S-event scale clusters, which agree across all three samples.
  - Per-class quantiles: 0j S ≤0.6%, 0j H ≤2%, 1j S ≤2%; 1j H medians fine, tails differ (floor-event deficit).
- **Remaining difference vs the two clean samples** (γγ and Run 2 agree with each other):
  - One-jet H: muR0.5 2.01 vs 2.35, muR2 0.613 vs 0.570.
  - Inclusive: muR0.5 1.017 vs 1.048–1.052; (0.5,0.5) 1.009 vs 1.044; muR2 0.970 vs 0.961; (2,2) 1.025 vs 1.013; μF within 0.3–0.5%.
  - Cause: our sample has fewer one-jet events (20% vs 27%), half as many floor events (0.8% vs 1.7% of 1j H) and fewer low-kT one-jet events. This is a nominal-generation difference that the weight fix cannot add back. Per-scale-bin medians agree to 0.3%.
- **Plots:** `scale_shape_v2_{higgs_pt,class,cjet_pt}.png`, `scale_norm_v2_inclusive.png` (`runall/plot_shapes3.py`). Higgs-pT shapes agree with both references within ~0.04, about as well as the two references agree with each other.
