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
