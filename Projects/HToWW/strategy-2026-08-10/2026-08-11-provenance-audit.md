---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# Provenance audit — every number in the card, and where it actually comes from

A different question from "which nuisances are missing" ([[2026-08-11-action-items-to-finish]]
§B). This asks: **for each value in `hww_combine_2dcat.yaml`, do we have a verifiable source,
and is it valid for OUR analysis?**

Three failure modes, and most of the card is in category 2 or 3:

- ✅ **Sourced and valid** — traceable to a POG/AN/paper, and applicable to Run 3 / our selection
- ⚠️ **Inherited** — copied from AN-23-102, which is **full Run 2 at 13 TeV**; we are
  **2022–2023 at 13.6 TeV** with a different c-tagger, so validity is assumed, not shown
- 🔴 **Unsourced or unreproduced** — no verifiable origin, or a number the AN *derives* from
  samples we have never run

---

## A. The two you flagged

### A1. 🔴 `xsec_hplusc_4FS_5FS: 1.30` — misnamed, unreproduced, and the AN's own numbers give 38%

**AN-23-102 §7.1 line 580–583:**

> "**Flavor scheme (FS) uncertainty:** Obtain the flavor scheme uncertainties **(4FS vs. 3FS)**
> or (5FS vs. 4FS) using the samples **without FXFX merging matching**. The differences between
> the two predictions are used as uncertainty and added to the nominal FXFX merging sample.
> **The discrepancy is in order of 30% with 3FS undershooting 4FS.**"

Four separate problems:

1. **The name is wrong.** For **H+c** (our signal) the comparison is **4FS vs 3FS**. "5FS vs
   4FS" is the **H+b** prescription. Our nuisance `xsec_hplusc_4FS_5FS` applies to `hplusc`
   but is named for the H+b scheme. Cosmetic, but it will confuse a reviewer.
2. **It is a derived measurement, not a constant.** The AN obtains it by comparing two
   *specific non-FXFX samples*. We have never run those samples, so we cannot reproduce it.
3. **The AN's own Table 1 gives ~38%, not 30%:**

   | sample (σ×Br, fb) | value |
   |---|---:|
   | HPlusCharm **4FS** …amcatnloFXFX (nominal) | 2.04 |
   | HPlusCharm **4FS** …amcatnlo (non-FXFX) | **1.83** |
   | HPlusCharm **3FS** …amcatnlo (non-FXFX) | **1.13** |

   Per the prescription (non-FXFX pair): (1.83 − 1.13)/1.83 = **38.3%**. "In order of 30%" is
   the AN rounding its own number down. **We use 1.30 with no derivation of our own.**
4. **It is Run 2 at 13 TeV.** The 3FS/4FS difference is a function of the charm PDF and the
   generator setup **at that energy**. Ours is 13.6 TeV.

**This is our single largest lever** (impacts: 815 ↔ 1376, a 370-unit swing). It is worth
knowing whether the true value is 30%, 38%, or something else at 13.6 TeV.

**Action:** either (a) obtain 3FS and 4FS non-FXFX H+c samples at 13.6 TeV and derive it, or
(b) state explicitly in the AN that we adopt AN-23-102's Run 2 value, flag that the same table
implies 38%, and treat the difference as an additional uncertainty on the uncertainty.

### A2. 🔴 `flavor_composition_ggH` — the AN's 50% is on ggH ALONE, and our grouping cannot express it

**AN-23-102 §7.1 line 547–551:**

> "**Higgs(bkg-H) heavy flavor composition uncertainty:** A conservative uncertainty of heavy
> flavor modeling of **ggH** is assigned, **50% uncertainty on the normalisation of the yield**,
> larger than the current uncertainty on ggH inclusive production, and in agreement with the
> theoretical uncertainty on ggH+bb."

Confirmed in **Table 16**: "ggH+heavy flavor jets uncertainty — normalization — 100% — **50%**".

The 50% is **sourced and valid**. What is broken is our **grouping**:

- The AN applies it to **ggH alone**.
- We merge **7 samples** into `higgsbkg`: H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB.
- **Measured 2026-08-11:** ggH is **13.1%** of the merged SR yield (VBF 29.0%, ggZH 23.3%,
  ZH 21.0%, WH 9.1%, ttH/H+b/H→ττ 4.6%).
- The yaml comment claimed **~80%** and set 1.40. **Fixed today → 1.066** (= 0.50 × 0.131).

**But 1.066 is still an approximation, not the AN's uncertainty.** A single scaled lnN on the
merged group is *not* the same as 50% on ggH: it moves all seven components together, whereas
the real uncertainty moves only ggH and therefore also changes the group's **shape**. This is
only correct once `higgsbkg` is **split**.

**This is the grouping change you named**, and it is a prerequisite for:
- correctly-scoped ggH+HF (§4 of [[2026-08-10-analysis-strategy-from-AN]])
- the **2POI fit** (AN v10 splits `bkg-H` into `bkg-H+c` / `bkg-H+notc` "due to shape differences")
- removing shape-averaging across a group spanning **15–31% charm** (ggH 14.6%, VBF 31.1%)

---

## B. Every other lnN — provenance

| nuisance | our value | AN-23-102 Table 16 | status |
|---|---|---|---|
| `lumi_13p6TeV` | 1.014 | 1.2 / 2.3 / 2.5% (2016/17/18) | 🔴 **ours is a Run 3 number not from this AN.** 1.4% matches the **2022 LumiPOG** recommendation — but that is unstated in the yaml, and 2023 differs. **No source comment anywhere.** |
| `xsec_hplusc_PDF` | 1.06 | 6% ✓ | ⚠️ matches, but NNPDF31 **nf4** at 13 TeV; we should confirm the same set/energy |
| `xsec_st` | 0.9873/1.0167 | +1.67/−1.27% ✓ | ⚠️ exact match, Run 2 value at 13 TeV |
| `xsec_diboson` | 1.037 | 3.7% ✓ | ⚠️ exact match, Run 2 |
| `xsec_vjets` | 1.027 | Z+jets 2.7% ✓ | 🔴 **AN says Z+jets; ours covers Z+jets AND W+jets.** No W+jets value is given in Table 16, so applying 2.7% to the merged `vjets` is an assumption. W+jets is our **statistically weakest** process. |
| `xsec_higgsbkg` | 1.05 | "Higgs production 1–5%" | ⚠️ we take the **top** of the range for the whole merged group; the AN's range is per-process |
| `BR_HtoWW` | 1.01 | 1% ✓ | ✅ Higgs XS WG, energy-independent |
| `alphaS_PDF` | 1.03 | 1–3% | ⚠️ top of range, applied flat to all processes |
| `flavor_composition_ggH` | 1.066 | 50% on ggH | 🔴 see A2 |
| `xsec_hplusc_4FS_5FS` | 1.30 | 30% | 🔴 see A1 |

**Pattern:** where the AN gives a *range* (1–5%, 1–3%) we take the maximum and apply it flat.
Conservative, defensible, but should be *stated* rather than silently assumed.

**Missing from our lnN entirely** (in AN Table 16): **BR(H→ττ) 1%**. We have `BR_HtoWW` but no
`BR_Htautau`, despite `GluGluHto2Tau` and `VBFHToTauTau` being in our sample list.

## C. Shape systematics — provenance

| ours | AN Table 16 | status |
|---|---|---|
| `pileup` | Pileup weight ✓ | ⚠️ AN varies the **4.6%** minbias xsec; our variation size is not documented in the yaml |
| `ps_isr`, `ps_fsr` | UE & PS ✓ | ⚠️ AN says "UE **and** PS"; we have PS only — **no underlying-event variation** |
| `scalevar_muR/muF/muR_muF` | Renorm & fact ✓ | ✅ standard |
| `muon_id`, `muon_iso` | Muon ID/ISO/Reco ✓ | 🔴 **no muon RECO** — AN lists ID/ISO/**Reco**, we have ID/ISO only |
| `electron_id`, `electron_reco_×3` | Electron ID/Reco ✓ | ✅ |
| `CMS_ctag2d_2022` | charm tagging ✓ | ⚠️ single Total; AN decomposes into 9 sources — deliberate ([[hww-ctag2d-sf-total-decision]]) |
| `CMS_scale_j/res_j` | JES/JER ✓ | ⚠️ single Total vs AN's RegroupedV2 11 sources — **but AN-24-091 (Run 3) also chose Total**, so defensible |
| `CMS_scale_e/res_e/scale_m/res_m` | (part of lepton scale) | ⚠️ not itemised in AN Table 16 |
| `CMS_negrw_vjets` | — | 🔴 **not in the AN at all** — our own addition (arXiv:2510.16217). Needs its own justification written down. |
| — | **top-pT reweight** | 🔴 **MISSING** (shape, AN applies to tt only) |
| — | **UE (underlying event)** | 🔴 **MISSING** (we have PS only) |
| — | **L1 prefire** | 🟢 2016/17 only; likely N/A for Run 3 — but undocumented |
| — | **HLT efficiencies** | 🔴 **MISSING + SFs structurally disabled** (`trigger: false`) |
| — | **MET unclustered** | 🔴 **MISSING** |
| — | **PU Jet ID** | 🔴 **MISSING** |

## D. Structural / grouping issues

| # | issue | consequence |
|---|---|---|
| D1 | **`higgsbkg` merges 7 samples** spanning 15–31% charm | ggH+HF cannot be scoped correctly; blocks 2POI; averages away shapes the AN calls distinguishable |
| D2 | **`vjets` merges Z+jets and W+jets** | one xsec lnN sourced only for Z+jets; no HF/LF split (AN-24-091 floats DY+HF and DY+LF **separately**) |
| D3 | **`st` merges ~17 single-top samples** | one lnN across tW / t-ch / s-ch, which have different theory uncertainties |
| D4 | **Only `tt` floats** | AN-24-091 floats **four** rates; our `vjets` is the weakest process and is fixed to MC |
| D5 | **Merged-group lnN bug class** | any uncertainty scoped to a *component* hits the A2 problem. **D1–D3 are all exposed.** |

## E. Ranked action list

### Provenance (write these down before the AN is reviewed)

1. 🔴 **Derive or explicitly adopt the flavour-scheme uncertainty** (A1). Largest single lever
   (370-unit swing). Note the AN's own Table 1 implies **38%**, not 30%. Also **rename** the
   nuisance to `xsec_hplusc_3FS_4FS`.
2. 🔴 **Document the lumi source.** 1.4% is the 2022 LumiPOG value but the yaml says nothing,
   and 2023 differs — we will need a per-era treatment for multi-era.
3. 🔴 **Justify `xsec_vjets` for W+jets**, or split it (D2). The 2.7% is the AN's **Z+jets**
   number.
4. 🔴 **Write down the `CMS_negrw_vjets` justification** — it is ours, not the AN's.
5. ⚠️ **State the range-maximum convention** for `xsec_higgsbkg` and `alphaS_PDF`.

### Grouping (the change you named)

6. 🔴 **Split `higgsbkg`** → at minimum `ggH` / `other-H`; ideally by jet flavour
   (`bkg-H+c` / `bkg-H+notc`) per AN v10. Retires the 1.066 approximation, applies the real
   50% to ggH alone, enables 2POI. **`cjet_cand_flavour` is already in the parquets** — config
   change, no reprocessing.
7. 🟠 **Split `vjets` into HF/LF** with separate floating normalisations (AN-24-091 precedent).
8. 🟢 Consider splitting `st` by production mode.

### Genuinely missing nuisances

9. 🔴 **HLT/trigger** — and the SFs are *disabled*, so this is a weighting bug first.
10. 🔴 **MET unclustered**, **PU Jet ID**, **top-pT reweight**, **UE**, **muon Reco**,
    **BR(H→ττ)**.
11. 🟢 Document the L1-prefire non-application.

### Verification

12. 🔴 **Fix the impacts loop** — 13 of 20 shape systematics have never been measured.
13. ⚠️ **Check the 4 lepton object-shift blocks** with `check_shifts.py`.

---

## F. The honest summary

**Only two values in the entire card are ✅ sourced-and-valid without qualification:**
`BR_HtoWW` (1%, energy-independent Higgs XS WG) and the `scalevar_*` shapes (standard method).

Everything else is either **inherited from a 13 TeV Run 2 note** without a Run 3 validity
argument, **taken as the maximum of a quoted range**, **applied to a merged group the source
never intended**, or — for the flavour scheme — **a derived measurement we have never
reproduced**.

That is not unusual for an analysis at this stage, but it means the systematics section of the
AN is largely **unwritten**, not merely incomplete. The grouping fix (E6) is the highest-value
item because it unblocks correct scoping, the 2POI fit, *and* removes a whole bug class.
