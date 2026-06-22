---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# Systematics reference — H+c → WW combine (v11 & v32, 2022postEE)

Complete list of every systematic **implemented** and every one **missing** relative to AN-23-102,
with magnitudes, sources, and how to add the missing ones.

- v11 datacard: `higgscharm/outputs/combine/v11_hplusc_v4.txt`
- v32 datacard: `b-hive/combine_inputs/v11_hplusc_v32_v9.txt`
- Weight columns live in the parquets (`weight_<name>Up/Down`); object shifts are separate parquet dirs.

---

## 1. Implemented systematics — v11 (v4)

### 1a. Rate-only (lnN)

| nuisance | magnitude | processes | AN-23-102 reference | match? |
|---|---|---|---|---|
| `lumi_13p6TeV` | 1.4% | all | LumiPOG (Table 15, per-year 1–2%) | ✓ (single, not per-year) |
| `xsec_st` | +1.67 / −1.27% | st | §7.1 TopPAG / LHC top WG | ✓ exact |
| `xsec_diboson` | 3.7% | diboson | §7.1 | ✓ exact |
| `xsec_vjets` | 2.7% | vjets | §7.1 | ✓ exact |
| `xsec_higgsbkg` | 5.0% | higgsbkg | §7.1 Higgs XS WG | ✓ |
| `flavor_composition_ggH` | **40%** (=50%×~80% ggH frac) | higgsbkg | §7.1: **50% on ggH yield** | ⚠ placeholder (merged template) |
| `BR_HtoWW` | 1.0% | hplusc, higgsbkg | §7.1 Higgs XS WG | ✓ |
| `xsec_hplusc_PDF` | 6.0% | hplusc | §7.1.1: 6% on signal | ✓ exact |
| `xsec_hplusc_4FS_5FS` | **30%** | hplusc | §7.1.1: "~30%, 3FS undershoots 4FS" | ✓ exact |
| `alphaS_PDF` | 3.0% | all | §7.1 NNPDF αs | ✓ |

### 1b. Shape — weight-based (read `weight_<name>Up/Down` from the nominal parquet)

| nuisance | parquet column | processes | AN reference |
|---|---|---|---|
| `pileup` | `weight_CMS_pileup_2022` | all | §7.2 (4.6% on minbias xsec) |
| `ps_isr` | `weight_ps_isr` | all | §7.1 UE/PS |
| `ps_fsr` | `weight_ps_fsr` | all | §7.1 UE/PS |
| `scalevar_muR` | `weight_scalevar_muR` | all (incl. diboson) | §7.1 μR scale |
| `scalevar_muF` | `weight_scalevar_muF` | all | §7.1 μF scale |
| `scalevar_muR_muF` | `weight_scalevar_muR_muF` | all | §7.1 combined scale |
| `muon_id` | `weight_CMS_eff_m_id_2022` | all | §7.2 MuonPOG |
| `muon_iso` | `weight_CMS_eff_m_iso_2022` | all | §7.2 MuonPOG |
| `electron_id` | `weight_CMS_eff_e_id_2022` | all | §7.2 EGammaPOG |
| `electron_reco_RecoBelow20` | `weight_CMS_eff_e_reco_below20_2022` | all | §7.2 |
| `electron_reco_Reco20to75` | `weight_CMS_eff_e_reco_20to75_2022` | all | §7.2 |
| `electron_reco_RecoAbove75` | `weight_CMS_eff_e_reco_above75_2022` | all | §7.2 |

> Note: diboson `scalevar` is **enabled** (`no_scalevar: []`) — this is the proxy for the AN's `theo_vv`
> diboson-theory shape. Earlier it was excluded; now included since the weights exist.

### 1c. Shape — object shifts (separate parquet dirs, re-scored & re-channelized) — **v11 only**

| nuisance | shift | processes | AN reference |
|---|---|---|---|
| `CMS_scale_j_2022` | jet energy scale | all | §7.2 JES (AN: split into 11 RegroupedV2 sources) |
| `CMS_res_j_2022` | jet energy resolution | all | §7.2 JER |
| `CMS_scale_e_2022` | electron energy scale | all | §7.2 lepton scale |
| `CMS_res_e_2022` | electron energy resolution | all | §7.2 |
| `CMS_scale_m_2022` | muon momentum scale | all | §7.2 |
| `CMS_res_m_2022` | muon momentum resolution | all | §7.2 |

### 1d. Other

| nuisance | description |
|---|---|
| `autoMCStats 10` | Barlow-Beeston bin-by-bin MC-stat, per channel (6 channels). **Dominant systematic** (41% of inflation). |
| `rate_tt` (rateParam) | data-driven tt normalization from CR_tt. **Tested → made limit worse** (Asimov adds freedom); kept for reference. Postfit 1.000 ± 1.2%. |

---

## 2. Missing systematics (AN-23-102 has them, we do NOT)

| AN nuisance | AN value | type | why missing | how to add |
|---|---|---|---|---|
| **Charm-jet tagging** (`CMS_ctag_DeepFlav_Stat`, `_XSec_BRUnc_WJets_c`, `_DYJets_c/_b`, `Interp`, `Extrap`) | **5.9%** | shape | **No weight column exists** — only the `cjet_cand_cvsl/cvsb_pnet` *scores* (MVA inputs) | apply PNet c-tag SF (BTV-20-001) via correctionlib in the higgscharm processor → write `weight_ctag*Up/Down`. **Upstream production.** |
| **top-pT reweighting** | small | shape | no weight column | vary by disabling tt top-pT reweight → `weight_toppt*` on tt |
| **Lepton trigger efficiency** | ~part of lepton (4.6%) | shape | no trigger SF weight | trigger SF via correctionlib → `weight_trig*`. Upstream. |
| **MET unclustered energy** (`CMS_scale_met_unclustered_energy`) | small | object shift | no shifted parquet | produce a met-unclustered object-shift dir (like the jet/lepton shifts) |
| **JES sub-source splitting** (RegroupedV2: `Absolute`, `BBEC1`, `EC2`, `FlavorQCD`, `HF`, `RelativeBal`, `RelativeSample` ± year) | 6.0% total | object shift | I have a **single** `CMS_scale_j` | split via correctionlib per-source JEC uncertainties (minor for the limit) |
| **Per-year luminosity correlation** (Table 15: uncorrelated + correlated components) | ~1–2% | lnN | single `lumi_13p6TeV` 1.4% | split into correlated/uncorrelated parts (negligible) |
| **PDF as shape** | 1–3% | shape | I use a **flat lnN** (`xsec_hplusc_PDF`); `weight_lhe_pdf` exists in parquet | swap the lnN for the `lhe_pdf` shape template (cheap; weights present) |

### Not applicable
- **L1 prefiring** — AN applies it for 2016/2017 only; **N/A for 2022**.

---

## 4. Treatment notes

2. **`flavor_composition_ggH` is a placeholder.** AN applies 50% to the ggH yield; since `higgsbkg` here
   merges ggH (~78% of it) with VBF/VH/ttH, the effective 40% is approximate. Proper fix: split ggH.
   Low priority because `higgsbkg` is only ~0.7% of the SR background.
3. **`rate_tt` made the limit worse** in the blind Asimov fit (data≡MC → the rateParam only adds SR
   freedom). It is informative but not used in the best config. Our postfit tt constraint (±1.2%) is
   **tighter** than the AN's (±5%) precisely because we lack c-tag + dropped tt theory.
4. **`autoMCStats` is the dominant systematic for both v11 (41%) and v32 (42%)** — far above the AN's 6.2%.
   Reducible via **cross-era MC template averaging**, not binning.
5. **Charm-jet tagging is the most important missing systematic** — it's a c-tagging analysis with *zero*
   c-tag uncertainty. Adding it will *raise* the limit (more honest) and is required for correctness.

---

## 5. Summary

| | v11 | v32 | AN-23-102 |
|---|---|---|---|
| lnN (rate) | 10 | 9 | ~10 |
| weight shapes | 12 | 12 | ~12 |
| object shifts | 6 | 0 | many (JES split + MET) |
| ggH flavour comp | ⚠ placeholder | ❌ | ✓ 50% |
| charm-tag | ❌ | ❌ | ✓ 5.9% |
| top-pT, trigger, MET-uncl | ❌ | ❌ | ✓ |
| autoMCStats | ✓ (dominant) | ✓ (dominant) | ✓ (6.2%) |
| tt rateParam | tested (worse) | ❌ | ✓ (±5%) |

**Headline:** the experimental model is broadly AN-aligned **except charm-tagging** (the most important
omission) and JES sub-splitting; the theory model is AN-aligned (st/vjets/diboson/PDF/4FS5FS exact) with
ggH-flavour as a placeholder.
