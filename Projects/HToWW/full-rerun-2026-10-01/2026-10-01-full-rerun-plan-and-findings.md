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
