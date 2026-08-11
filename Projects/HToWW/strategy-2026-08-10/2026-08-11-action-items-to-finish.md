---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# Action items to finish the analysis — systematics audit

State: **r < 1185** (2022postEE, `hww_combine_2dcat`), stat-only 637, baseline 1164.
Card holds **30 named nuisances** (10 lnN + 20 shape) + autoMCStats on 6 channels + 1 rateParam.

Companion notes: [[2026-08-11-route-to-a-better-limit]] (sensitivity),
[[2026-08-11-lessons-from-AN-24-091]] (Run 3 precedent), [[2026-08-10-analysis-strategy-from-AN]].

---

## A. Systematics that are NOT VERIFIED

### A1. ⚠️ 13 of 20 shape systematics have never had their impact measured

The `freeze_per_nuisance` impacts loop ran all 46 fits and **combine exited 0**, but only
**9 of 23** produced a usable result. The other 14 — **every shape systematic** — wrote a
degenerate file with a single entry at quantile 0.025 (value 3984.4) instead of the normal
5-quantile band. The driver did not flag it.

**Unmeasured:** `pileup`, `ps_isr`, `ps_fsr`, `scalevar_muR/muF/muR_muF`, `muon_id`,
`muon_iso`, `electron_id`, `electron_reco_×3`, **`CMS_ctag2d_2022`**, and the 6 object shifts
(**`CMS_scale_j`, `CMS_res_j`** = JES/JER, plus e/m).

This matters because the JES/JER migration exposure is the *specific* weakness of
argmax-defined regions (§2 of the strategy note) and we cannot currently put a number on it.

**Fix:** the fit options are likely under-determined — `-t -1 --run blind --noFitAsimov` with
`--freezeParameters` on a *shape* nuisance. `drive_combine.py` should also assert the output
has 5 quantiles rather than trusting the exit code.

### A2. ⚠️ Only ONE object-shift systematic was ever validated end-to-end

Today's fix verified `CMS_scale_j` and `CMS_res_j` are physical (opposite-sign, few-percent,
per-process totals conserved). The **lepton** shifts — `CMS_scale_e`, `CMS_res_e`,
`CMS_scale_m`, `CMS_res_m` — were rebuilt from the same repaired inference but were **not
individually checked** for the same pathology.

**Fix:** run `/afs/cern.ch/user/c/cgupta/check_shifts.py` and inspect the lepton blocks. Cheap
(~1 min) — the script already prints all six.

### A3. ⚠️ 92 residual checker flags are *argued* benign, not *proven* benign

After the fix the checker still flags 92 templates: 18 "frozen" (empty signal templates in
background CRs, nominal = 0.00) and 74 "same-sign". The argument that these are channel
**migration** rests on per-process totals over all channels being conserved and physical
(vjets +1.50/−1.70%, etc.), which is solid — but no per-event migration matrix was built.

**Fix (optional):** count events changing argmax class between nominal and shifted trees. This
also directly quantifies the exposure in A1.

### A4. The `flavor_composition_ggH` value was wrong for months — FIXED IN CONFIG 2026-08-11

The yaml comment claimed "ggH is ~80% of the merged higgsbkg" and set 1.40. **Measured: ggH is
13.1%** of the higgsbkg SR yield (VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%, rest 4.6%). The
1.40 was penalising ~87% of the group with a ggH-specific uncertainty.

**Done:** `hww_combine_2dcat.yaml` now has **1.066** (backup `.bak_ggh_scoping_*`), config
loads clean. **NOT yet in the card** — needs a rebuild. Measured effect: **1185 → 1164**.

**Lesson:** other lnN values should be spot-checked against the actual merged composition. Any
uncertainty scoped to a *component* of a merged group carries this bug class.

### A5. `no_theory` / `no_scalevar` scoping is asserted, not tested

`rate_params: [tt]` with tt's theory shapes dropped. AN-24-091 **confirms** this is right
(they apply no µR/µF or PDF rate uncertainty to tt and DY *because* those float). But we drop
`ps_isr`/`ps_fsr`/`scalevar_*` **shapes** too, which is a stronger statement than the AN makes.
Never tested by refitting with them restored.

---

## B. Systematics that are MISSING

Against AN-23-102 Table 16, verified present/absent in `hww_combine_2dcat.yaml`:

| missing item | severity | note |
|---|---|---|
| **HLT / trigger efficiency SFs** | 🔴 **correctness** | `trigger: false` for muons, no electron trigger line. The SFs are *structurally disabled*, not merely missing a nuisance — events are mis-weighted, so this is a **bug**, not a bookkeeping gap. |
| **MET unclustered energy** | 🟠 | zero mentions in the yaml. AN-23-102 §7.2.1 names it as a leading migration source alongside JES. |
| **PU Jet ID** | 🟠 | zero mentions. |
| L1 prefire | 🟢 | AN applies it to 2016/17 only, so plausibly a non-issue for 2022 — but should be a *documented* decision, not an omission. |
| top-pT reweighting | 🟢 | not itemised; AN applies it to tt only (line 566). AN-24-091 applies the **full** correction as its own uncertainty. |
| ctag2d decomposition | 🟢 | single `up_Total/down_Total`; AN decomposes into Stat/PU/PS/scale/XSec/JES/JER/Interp/Extrap. **Deliberate deferral** — see [[hww-ctag2d-sf-total-decision]]. |
| JES regrouping | ⚪ **not a gap** | we use single `Total`; AN-23-102 uses 11-source RegroupedV2 — but **AN-24-091 (Run 3) deliberately chose "total"**, justified by impacts. We are aligned with the newer note. Needs our own impacts plot to defend (blocked by A1). |

---

## C. Prioritised action list

### Tier 1 — correctness (do first; these are *wrong*, not merely suboptimal)

1. **Enable trigger SFs.** `trigger: false` means every event is mis-weighted. Requires
   reprocessing, so it is the long pole — start it before the cosmetic work.
2. **Rebuild the card** to pick up `flavor_composition_ggH: 1.066` (already in config).
   Expected **1185 → 1164**. ~30 min.
3. **Fix the impacts loop** (A1) so the 13 shape systematics converge, then re-rank. Without
   this we are flying blind on JES/JER and ctag2d.
4. **Run the shift checker on the lepton blocks** (A2). ~1 min.

### Tier 2 — sensitivity (measured or precedented, no retraining/reprocessing)

5. **Collapse the 5 CRs to yield-only (1 bin).** Two independent AN precedents (AN-23-102 line
   662; AN-24-091 Table 10 — literally 1 bin per CR). Removes the argmax migration artifact
   class from 5 of 6 channels.
6. **Add MET-unclustered and PU-Jet-ID nuisances.** Closes the two real AN gaps. Expect the
   limit to get slightly *worse* — that is honest, not a regression.
7. **Split V+jets normalisation into HF/LF floating rates** (AN-24-091 does exactly this for
   DY). Targets our worst process.
8. **Adaptive binning**: logit-transform the score, then choose bins so signal is flat and
   `σ_bkg < N_bkg/3`, with per-category bin counts. **Test finer as well as coarser** —
   AN-24-091 Table 15 has 20×4 beating 10×4 (30 → 28).

### Tier 3 — the big lever (needs processing)

9. **Multi-era V+jets MC.** Measured: **2× → 1077, 3× → 1037**. MC stats is the dominant
   systematic (252 units, 223 of it in the SR). A real multi-era fit also adds **data**,
   lowering the 637 stat-only floor, so 1037 is a conservative bound.
10. **Split `higgsbkg` by jet flavour.** Retires the A4 placeholder properly, enables the 2POI
    fit, removes shape-averaging across a group spanning 15–31% charm.
11. **Nc-j=1 / Nc-j>1 SR split** (AN +8%) — **blocked by 9**: Nc-j>1 has only 147 raw V+jets
    MC events (14.7/bin), which would fall below the autoMCStats threshold.

### Tier 4 — validation

12. **Partial unblinding test** (AN-24-091 §9.1): blind bins above an S/√B threshold, fit the
    rest, check the background model against data. We have no equivalent.
13. **Sideband / validation region** distinct from the CRs (both Run 3 references have one).

---

## D. The one-line summary

**Nothing in Tier 1 is optional** — the trigger SFs are an outright weighting bug, the card is
stale relative to the config, and 13 of 20 shape systematics have literally never been
measured. Tier 2 is where the cheap wins are. Tier 3 is where the limit actually moves, and it
all routes through **more V+jets MC**.
