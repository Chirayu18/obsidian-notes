---
tags: [reference]
status: active
date: 2026-07-24
source: lxplus
---

# HToWW H+c — master systematics list + remaining work

Authoritative inventory of every nuisance in the live `hww_combine_2dcat` datacard,
what's **missing**, where each is **picked up from**, and the **references**. The
machine-readable version is [[HToWW-systematics-inventory.xlsx]] (also `.csv`).

Companion to [[2026-07-19-ctag2d-full-documentation]] and the run steps in
[[2026-07-24-run-analysis-steps]].

## 1. Systematics IN the card (live)

### 1a. Weight-based shape nuisances (`shape_systematics:` in workflow)
Emitted by the processor `Weights` container as `weight_<name>Up/Down`; combine morphs
nominal↔Up/Down.

| Nuisance | Processes | Picked up from | Reference |
|---|---|---|---|
| `pileup` | all MC | `pileup.py` (PileupWeights), LUM POG PU json | LUM POG; AN-23-102 §7 |
| `ps_isr`, `ps_fsr` | all MC exc. tt | `partonshower.py`, LHE PS weights | AN-23-102 §7.1 |
| `scalevar_muR`, `_muF`, `_muR_muF` | all MC exc. tt | `lhescale.py`, LHEScaleWeight | AN-23-102 §7.1 (QCD scale) |
| `muon_id`, `muon_iso` | all MC | `muon.py`, MUO POG SF json | MUO POG; AN-23-102 §6 |
| `electron_id` | all MC | `electron.py`, EGM POG SF | EGM POG |
| `electron_reco_{RecoBelow20,Reco20to75,RecoAbove75}` | all MC | `electron.py`, EGM reco SF (pt-binned) | EGM POG |
| **`CMS_ctag2d_2022`** | all MC | **`ctag2d.py` (CTag2DCorrector) — NATIVE as of 2026-07-24**; `ParticleNetAK4_pseudocontinuous` in `flavTaggingSF_2022postEE.json.gz` (cmshgg ingredients), `up_Total`/`down_Total` | cmshgg 2D_HF_Tagging; PNet AK4 pseudo-continuous |
| **`CMS_negrw_vjets`** | vjets | `base.py::_score_negrw` + `make_combine_inputs.py`; `negrw_models.joblib` (20× HistGradientBoostingClassifier), std-band | **arXiv:2510.16217** |

### 1b. Object-shift shape nuisances (separate shifted parquet trees, `object_shifts: true`)
| Nuisance | Picked up from | Reference |
|---|---|---|
| `CMS_scale_j_2022` (JES **Total**) | `jerc.py`, JME POG JEC | JME POG; AN-23-102 §7.2 |
| `CMS_res_j_2022` (JER) | `jerc.py`, JME POG JER | JME POG |
| `CMS_scale_e_2022`, `CMS_res_e_2022` | `electron_ss.py`, EGM SS | EGM POG |
| `CMS_scale_m_2022`, `CMS_res_m_2022` | `muon_ss.py`, MUO scale/res | MUO POG |

### 1c. Rate (lnN) + rateParam + MC-stat
| Nuisance | Value | Processes | Reference |
|---|---|---|---|
| `lumi_13p6TeV` | 1.014 | all exc. tt | CMS LUM POG (Run3 2022) |
| `xsec_st` | 0.9873/1.0167 | st | AN-23-102 Table 16 |
| `xsec_diboson` | 1.037 | diboson | AN-23-102 Table 16 |
| `xsec_vjets` | 1.027 | vjets | AN-23-102 Table 16 |
| `xsec_higgsbkg` | 1.05 | higgsbkg | AN-23-102 §7.1 |
| `flavor_composition_ggH` | 1.40 ⚠ | higgsbkg | AN-23-102 §7.1 — **PLACEHOLDER** (0.5·0.8; apply full 1.50 to ggH once split out) |
| `BR_HtoWW` | 1.01 | hplusc,higgsbkg | LHCHWG YR4 |
| `xsec_hplusc_PDF` | 1.06 | hplusc | AN-23-102 §7.1 |
| `xsec_hplusc_4FS_5FS` | 1.30 | hplusc | AN-23-102 §7.1 |
| `alphaS_PDF` | 1.03 | all exc. tt | PDF4LHC / AN-23-102 |
| `tt` **rateParam** | free | tt | data-driven, CR_tt→SR shared (AN-23-102) |
| `autoMCStats 10` | per-bin BB | all | combine Barlow-Beeston |

## 2. MISSING / TODO — what's remaining

| Item | Status | What to do |
|---|---|---|
| **Trigger SFs (muon + electron)** | 🔴 MISSING | `trigger: false` in workflow → **enable**, add SF + nuisance. Currently no trigger SF at all. |
| **PDF *shape* nuisance** | 🔴 MISSING | `LHEPdfWeight` IS computed (`lhepdf.py` wired) but only the `xsec_hplusc_PDF` lnN is used. Add the PDF Hessian/envelope **shape** rows. |
| **Decorrelate all systematics** | 🟠 TODO (deferred) | Whole-card pass: JES Total→Regrouped(~11); `CMS_ctag2d_2022` Total→Stat + per-source (map SF's JES/PU/lepton/theory onto the analysis' OWN shared nuisances — HiggsDNA `bTagShapeSF` style, **not** double-count). Decision 2026-07-24: kept as single Total for now. |
| **`flavor_composition_ggH` placeholder** | 🟠 TODO | Split ggH out of `higgsbkg`, then apply full 1.50 to the ggH component only (currently 1.40 effective on merged higgsbkg). |
| **L1 prefiring** | 🟡 likely-negligible | No prefiring code in framework. Run3 2022 ECAL prefiring ~0; add L1-muon prefiring only if AN requires. |
| Year combination (2022pre + 2023) | 🟡 scope | Card is 2022postEE only; correlate/decorrelate nuisances across campaigns when combining years. |

## 3. What's DONE / not-applicable
- **Signal theory shapes** (`ps_*`, `scalevar_*` on hplusc): ✅ present — `hplusc` is not in `no_theory`.
- **1D fixed-WP c-tag SF** (`CTagCorrector`, BTV `particleNet_wc/tnp`): N/A — superseded by the 2D pseudo-continuous SF for this analysis.
- **JER**: single `CMS_res_j` Total — no split needed at current precision.

## 4. Current limit (all three latest changes)
negrw (Jul-15 model) + 2D-cat MVA + 2D SF (Total): **r95 = 1422 full / 749 stat-only / 1168 freeze-autoMCStats**.
The 2D SF is now applied **natively in the processor** (CTag2DCorrector); the post-hoc
`apply_ctag2d_sf.py` is retired. Full native re-run in progress (2026-07-24).
