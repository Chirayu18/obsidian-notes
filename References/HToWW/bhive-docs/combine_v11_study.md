---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# v11 Combine Study (2022postEE, H+c → WW) — full record

**Model:** v11, 6-class CE (`hwwcom_multiclass_v11`), discriminant = `argmax_winner_score` = P(argmax class).
**Lumi:** 26.7 fb⁻¹ (2022postEE). **Fit:** 1POI (r_hplusc floats; higgsbkg fixed to SM via lnN).
**Pipeline:** higgscharm `scripts/combine/make_combine_inputs.py` (yaml-driven) → `drive_combine` (CMSSW combine v10.6.0).
**Comparison baseline:** AN-23-102 (full Run 2, 138 fb⁻¹): 1POI expected limit **431**, 2POI **969**.

---

## 1. Headline numbers

| version | full r₉₅ | stat-only | syst inflation | notes |
|---|---|---|---|---|
| **v3** (baseline) | **1693** | 756 | ×2.24 | argmax winner-score, 20 uniform bins, tt fixed |
| v4 — all-4 rateParams | 1800 | 807 | ×2.23 | floating st/diboson/vjets via impure CRs → **worse** |
| v4 — tt-only rateParam + variable binning | 1722 | 771 | ×2.23 | |
| v4 — + diboson scalevar (theo_vv) + ggH flavour | 1739 | 771 | ×2.26 | more complete → slightly higher |
| v4 — + LOWESS template smoothing | 1742 | 771 | ×2.26 | **no effect** (systs aren't noise) |
| **AN-23-102 1POI** (138 fb⁻¹) | **431** | ~330 | ×1.31 | |

**One-line conclusion:** v11 is **statistics-limited** (stat-only floor 756–771) and **signal-theory–inflated** (×2.26). The gap to the AN is **luminosity (×2.27) × systematic robustness (×1.7)** — *not* MVA separation, binning, or background modelling.

---

## 2. Why the limit is what it is

### 2.1 Catastrophic S/B in the SR (v3 yields)
SR_hplusc: hplusc **0.168**, higgsbkg 71.2, tt **6768**, st 655, diboson 338, vjets 775 → total bkg **8607**. **S/B = 2×10⁻⁵.**

Per-bin (discriminant = P(hplusc) winner score): signal **saturates at P=0.55** (bins 12–19 empty), peaks in bins 8–10 (P=0.40–0.50) sitting **on the background peak**. Best single bin S/B = 1.2×10⁻⁴. Combined shape S/√B = **0.003**.

The winner-score discriminant doesn't separate signal from the tt that lands in SR_hplusc (that tt is there *because* P(hplusc) was its argmax) → no high-purity tail.

### 2.2 Impacts (v3) — signal theory dominates
| nuisance | \|Δr\| | type |
|---|---|---|
| **xsec_hplusc_4FS_5FS** (30%) | **527** | signal theory (irreducible) |
| scalevar_muR | 256 | scale (mostly on **signal**) |
| scalevar_muR_muF | 245 | scale |
| ps_fsr | 198 | parton shower |
| xsec_hplusc_PDF | 104 | signal PDF |
| scalevar_muF | 94 | scale |
| xsec_vjets | 27 | bkg rate |
| (lumi, xsec_st/diboson/higgsbkg, all SF systs) | ≤17 | |

**Background rate systematics are negligible** (≤27). The inflation is **signal theory** (4FS/5FS, scale, PDF, ps) — all on the signal, all irreducible. This refuted the earlier "background-systematics-limited" framing.

---

## 3. Stat-only decomposition — why it's not better than the AN

Counting limit ≈ 1.64/(S/√B); shape limit = counting / shape-gain.

| | counting @138fb⁻¹ | shape gain | **stat-only @138fb⁻¹** |
|---|---|---|---|
| **v11** | **400** (S/√B ~2× better — more signal/fb) | ×1.18 (winner-score) | **339** |
| **AN** | 863 | ×2.6 (BDT tail) | 330 |

**Your raw sensitivity is ~2× better than the AN's** (you keep ~2× more signal per fb⁻¹). But your winner-score shape barely beats counting (×1.18) while the AN's BDT localizes signal into a high-purity tail (×2.6). **Their shape advantage exactly cancels your efficiency advantage → equal stat floors** (339 vs 330) at equal lumi.

**To actually beat the AN:** replace winner-score with a **signal-vs-bkg likelihood ratio** (e.g. P(hplusc)/(P(hplusc)+P(tt))) that has a real tail — then the 2× efficiency edge converts to a 2× better stat limit.

---

## 4. Systematics vs AN-23-102

**Match:** QCD scale, ps_isr/fsr, signal PDF (6%), αs, BR(H→WW), pileup, lepton ID/iso/reco SFs, JER, lepton scale/res, luminosity, MC-stat (autoMCStats), **tt normalization (after v4 rateParam)**.

**Mine bigger/explicit:** `xsec_hplusc_4FS_5FS` 30% (confirmed correct — AN §7.1.1: "discrepancy order of 30%, 3FS undershooting 4FS").

**AN values confirmed (§7.1/7.2):** single-top +1.67/−1.27%, V+jets 2.7%, diboson 3.7%, signal PDF 6%, signal scale up to 10%, pileup 4.6%, **ggH heavy-flavour composition 50% on the ggH yield**.

**Gaps (theirs-only):**
| missing | status | fix |
|---|---|---|
| **charm tagging** (ctag DeepFlav Stat + XSec/BRUnc) | **no weight column exists** (only cvsl/cvsb scores as MVA inputs) | **upstream production** (correctionlib PNet c-tag SF → `weight_ctag*`) |
| ggH flavour composition (their #1 impact) | **added v4** as `flavor_composition_ggH: higgsbkg 1.40` (50%×~80% ggH fraction; placeholder until ggH split out) | split ggH from higgsbkg, apply 1.50 to ggH only |
| diboson theory (theo_vv) | **added v4** (un-excluded diboson scalevar; weights already existed) | done |
| top-pT reweighting | not present (tt now data-driven → less critical) | weight on tt |
| lepton trigger eff, MET unclustered | not present | upstream production |
| JES sub-source splitting (~10) | single `CMS_scale_j` | correctionlib RegroupedV2 (minor) |

---

## 5. Fixes attempted and their effect

1. **Data-driven tt** (rateParam shared CR_tt→SR, drop tt theory shapes): **neutral** (1693→1722). The floating tt norm adds back ~as much SR freedom as dropping its theory removed. tt was never the dominant systematic (signal theory is).
2. **All-background rateParams:** **worse** (→1800). The argmax CRs for st/diboson/vjets are **tt-dominated** (CR_st: tt=13592 vs st=1455), so floating those bkgs leaves them weakly constrained → SR freedom. Only CR_tt is pure → only tt should be data-driven (matches AN).
3. **Variable binning** concentrated in [0.40,0.60]: **neutral** — signal saturates at 0.55, nothing to resolve.
4. **diboson theo_vv + ggH flavour composition:** correctly **raises** limit (1722→1739) — these were missing uncertainties.
5. **LOWESS template smoothing** (AN §7.2.1): **no effect** (1739→1742). Your systematics are *genuine signal theory*, not MC-stat bin noise, so smoothing can't touch them.

---

## 6. Bottlenecks (ranked)

1. **Luminosity** (26.7 vs 138 fb⁻¹). Stat-only floor 771 → 771/√(138/26.7)=**~340 ≈ AN's 330**. The dominant, buildable lever (add preEE + 2023 full backgrounds). ×2.27.
2. **Systematic inflation ×2.26 vs AN ×1.31.** Dominated by **irreducible signal theory** (4FS/5FS 30%, scale, PDF). The reducible portion (un-smoothed templates) turned out negligible here. The AN is less inflated mainly via higher lumi + data-driven backgrounds.
3. **Intrinsic S/B = 2×10⁻⁵** (0.17-event signal). Fundamental to H+c→WW; only lumi grows the signal; a 2nd SR (N_cjet>1) helps marginally.

**NOT bottlenecks (measured):** the MVA/separation (stat-only matches AN at equal lumi), the binning (signal saturates), background rate systematics (impacts ≤27).

**Actionable priority:** (1) add eras; (2) switch winner-score → signal-vs-bkg likelihood-ratio discriminant (unlocks the ~2× efficiency edge); (3) produce c-tag systematic (correctness, raises limit); (4) 4FS/5FS 30% is irreducible.

---

## 7. Files / config

- **`higgscharm/scripts/combine/make_combine_inputs.py`** — added: variable `binning.edges` support; per-process theory-shape skip (`no_theory`); `rateParam` emission (`rate_params`); `smooth_shape_variations()` (LOWESS, gated on `smooth_shapes`).
- **`higgscharm/analysis/workflows/hww_combine_fixed.yaml`** `combine:` block — `binning.edges`, `rate_params: [tt]`, `no_theory: [tt]`, lnN with `flavor_composition_ggH: {higgsbkg: 1.40}`, `smooth_shapes: true`, outputs → `v11_hplusc_v4.{txt,root}`.
- Outputs: `outputs/combine/v11_hplusc_v3.*` (baseline), `v11_hplusc_v4.*` (current).
- Run: `text2workspace.py …v4.txt`; `combine -M AsymptoticLimits …v4.workspace.root --run blind -t -1` (full) and `… --freezeParameters allConstrainedNuisances` (stat-only).

*(See also memory: combine v1/v2/v3 experiment log in `docs/combine.md`.)*
