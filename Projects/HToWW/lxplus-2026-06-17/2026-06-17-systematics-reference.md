---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# H+c → WW combine — systematics reference (v11 & v32)

> ⚠️ **SUPERSEDED IN PART (checked 2026-07-31).** The AN impact percentages quoted in this
> note (charm-tag "5.9%", MC-stat "6.2%", JES "6.0%") **do not match AN-23-102**. The AN has
> **no Table 18**; the inventory is **Table 16** and the impacts are **Table 17**. In Table 17's
> **1POI $r_{H+c}$** column the real values are charm-tag **1.1%**, MC-stat **5.4%**,
> JES/JER **1.1%**, trigger **0.0%**. The numbers here look like they came from a different
> column or source. Use [[2026-07-24-systematics-master-list]] for the current inventory and
> the verified AN comparison.

Every systematic **implemented** and **missing** vs AN-23-102. Datacards:
`higgscharm/outputs/combine/v11_hplusc_v4.txt`, `b-hive/combine_inputs/v11_hplusc_v32_v9.txt`.
Weight shapes read `weight_<name>Up/Down` from the parquets; object shifts are separate parquet dirs.

## 1. Implemented — v11 (v4)

### Rate-only (lnN)
| nuisance | magnitude | processes | AN | match |
|---|---|---|---|---|
| `lumi_13p6TeV` | 1.4% | all | LumiPOG Table 15 | ✓ (single) |
| `xsec_st` | +1.67/−1.27% | st | §7.1 | ✓ exact |
| `xsec_diboson` | 3.7% | diboson | §7.1 | ✓ exact |
| `xsec_vjets` | 2.7% | vjets | §7.1 | ✓ exact |
| `xsec_higgsbkg` | 5.0% | higgsbkg | Higgs XS WG | ✓ |
| `flavor_composition_ggH` | **40%** (=50%×80% ggH) | higgsbkg | §7.1: **50% on ggH** | ⚠ placeholder |
| `BR_HtoWW` | 1.0% | hplusc, higgsbkg | §7.1 | ✓ |
| `xsec_hplusc_PDF` | 6.0% | hplusc | §7.1.1 | ✓ exact |
| `xsec_hplusc_4FS_5FS` | **30%** | hplusc | §7.1.1 ~30% | ✓ exact |
| `alphaS_PDF` | 3.0% | all | §7.1 | ✓ |

### Shape — weight-based (12)
`pileup` (`weight_CMS_pileup_2022`), `ps_isr`, `ps_fsr`, `scalevar_muR/muF/muR_muF`,
`muon_id` (`CMS_eff_m_id`), `muon_iso` (`CMS_eff_m_iso`), `electron_id` (`CMS_eff_e_id`),
`electron_reco_RecoBelow20/Reco20to75/RecoAbove75` (`CMS_eff_e_reco_*`). All processes.
Diboson `scalevar` **enabled** (`no_scalevar: []`) = proxy for AN `theo_vv`.

### Shape — object shifts (6, v11 only; separate re-scored parquet dirs)
`CMS_scale_j_2022`, `CMS_res_j_2022`, `CMS_scale_e_2022`, `CMS_res_e_2022`,
`CMS_scale_m_2022`, `CMS_res_m_2022`. All processes.

### Other
- `autoMCStats 10` — Barlow-Beeston per-bin (6 channels). **Dominant systematic** (41% of inflation).
- `rate_tt` (rateParam) — data-driven tt; **tested → worse**; postfit 1.000 ± 1.2%.

## 2. v32 — differences from v11
Same lnN + weight-shapes **except MISSING**: `flavor_composition_ggH`, all 6 object shifts, `rate_tt`.
→ v32's systematic model is **less complete** than v11's. Keeps `autoMCStats` (dominant there too, 42%).

## 3. Missing (AN has, we don't)

| AN nuisance | AN value | type | why missing | how to add |
|---|---|---|---|---|
| **Charm-jet tagging** (`CMS_ctag_DeepFlav_Stat`, `_XSec_BRUnc_WJets_c/_DYJets_c/_b`, `Interp`, `Extrap`) | **5.9%** | shape | **no weight column** (only cvsl/cvsb scores as MVA inputs) | PNet c-tag SF (BTV-20-001) in the processor → `weight_ctag*`. **Most important omission.** |
| **ggH flavour composition** | **50% on ggH** (AN #1–2 impact) | lnN | only a placeholder (40% on merged higgsbkg) | split ggH out of higgsbkg, apply 1.50 |
| **top-pT reweighting** | small | shape | no column | `weight_toppt*` on tt |
| **Lepton trigger eff** | part of 4.6% | shape | no trigger SF weight | `weight_trig*` upstream |
| **MET unclustered energy** | small | obj shift | no shifted parquet | produce met-uncl shift dir |
| **JES sub-source split** (RegroupedV2 ×11) | 6.0% | obj shift | single `CMS_scale_j` | per-source JEC (minor) |
| **PDF as shape** | 1–3% | shape | flat lnN used; `weight_lhe_pdf` exists | swap lnN → shape (cheap) |
| L1 prefiring | — | — | **N/A for 2022** (2016/2017 only) | — |

## 4. Notes
- `xsec_hplusc_4FS_5FS` 30% is **correct** (AN §7.1.1), irreducible, shared with the AN.
- `flavor_composition_ggH` placeholder is low-priority (higgsbkg = 0.7% of SR).
- `autoMCStats` dominates both (41%/42%) vs AN 6.2% → fix = **cross-era MC averaging**, not binning.
- Charm-tag is the key missing piece; adding it **raises** the limit (more honest), required for correctness.

## 5. Summary
| | v11 | v32 | AN |
|---|---|---|---|
| lnN | 10 | 9 | ~10 |
| weight shapes | 12 | 12 | ~12 |
| object shifts | 6 | 0 | many |
| ggH flavour | ⚠ placeholder | ❌ | ✓ 50% |
| charm-tag | ❌ | ❌ | ✓ 5.9% |
| top-pT/trigger/MET-uncl | ❌ | ❌ | ✓ |
| autoMCStats | ✓ dominant | ✓ dominant | ✓ 6.2% |
