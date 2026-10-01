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
