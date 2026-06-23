---
tags: [reference]
status: active
date: 2026-06-23
source: lxplus
---

# H+c → WW — autoMCStats root cause + xsec/sumw audit

Follow-up to [[2026-06-17-LIMIT-ISSUE]]. Answers two questions: **(1) why does autoMCStats
blow up?** and **(2) are any xsec/sumw values physically wrong?** No code changed yet (nothing to revert).

## Q1 — autoMCStats blow-up = DY (vjets) undersampling in the SR

Freeze tests on `v11_hplusc_v4` (blind Asimov, median expected r₉₅):

| config | r₉₅ |
|---|---|
| baseline full | **1742** |
| freeze **SR** autoMCStats only (`prop_binSR_hplusc.*`) | **1069** |
| freeze ALL autoMCStats (`prop_bin.*`) | 1032 |
| stat-only (all constrained) | 771 |

→ The **SR channel's** autoMCStats alone is ~the entire systematic inflation (1742→1069). The other
5 channels' MC-stat barely matter (1069→1032).

Per-bin breakdown of the SR total-MC error (`(Σw)²/Σw² = N_eff`):

| SR bin | total | tot_err | N_eff(tot) | **vjets content** | **vjets err** | **vjets N_eff** | vjets share of bin err |
|---|---|---|---|---|---|---|---|
| 4 | 1597.6 | 70.9 | 507 | 221.3 | 70.6 | **9.8** | **99.5%** |
| 5 | 1477.7 | 63.1 | 548 | 205.6 | 62.8 | **10.7** | **99.5%** |
| 6 | 752.3 | 41.3 | 332 | 0.0 | 41.0 | **0.0** | **99.2%** |

Every other process is well-sampled in the SR tail: tt N_eff ≈ 33k–43k (rel 0.5%), st ≈ 6k, diboson ≈ 1k.
**Only DY (vjets) is starved** — ~10 effective MC events carry ~150–220 expected events per bin. Bin 6 is
the pathological case: 0 ± 41 (huge + and − weights cancel in yield but not in variance). So
`prop_binSR_hplusc_bin{4,5,6}` are literally "DY yield here is ±30%," floating ±50–70 events under a
0.06-event signal.

### Why DY is starved (NOT a normalization bug)
- Only 2 inclusive amc@NLO DY samples: `DYto2L_2Jets_50` (xsec 6688 pb) and `_10to50` (20950 pb).
- amc@NLO gen weights are huge and broad: `_50` median |w|≈18.6k, max 225k, min −49.6k; `_10to50`
  85 events total, |w| up to ±79.7k, **N_eff = 2.6**.
- Builder applies `w_final = weight_nominal × (lumi·xsec/sumw)`; scale `_50`=4.7e-5 → max event ≈ 10.6
  expected events. Internally consistent.
- The H+c SR is c-tagged + high-MET → DY selection efficiency ~10⁻⁴. Despite a large *generated*
  sample, only ~85/10k DY events survive, landing in the high-weight tail → N_eff≈10 in the SR.

Outliers are NOT clippable: for `_50` the single largest |w| event is only 0.8% of Σw² — the weights are
*uniformly* large, not a few spikes. Capping won't help.

## Q2 — xsec/sumw physical audit (2022postEE, lumi = 26671.7 pb⁻¹)

scale = lumi·xsec/sumw = expected events per generator event.

### ❌ Physically WRONG
- **`TbarBQ` and `TBbarQ`: xsec = 0** (t-channel single-top, 5FS b-associated). Parquets exist (177K/266K)
  → processed but **scale=0 → contribute nothing**. t-channel single-top is ~130–230 pb, not 0. Real bug;
  undercounts `st`. Not the SR-tail driver, so it won't move the limit, but it's wrong. **Fix: set the two
  xsecs in the dataset config.**

### ⚠ Dropped (sumw = None in `sumw_2022postEE.json`, no parquet → silently absent from build)
- All tt/tW **`-ext` extension samples** (`TTto2L2Nu-ext`, `TTto4Q-ext`, `TTtoLNu2Q-ext`,
  `TWminus*-ext`, `TbarWplus*-ext`) → lost extra tt/tW MC stats (tt is well-sampled anyway).
- **`WZto3LNu`, `ZZto4L`, 6× `GluGluToContin…2Z` (gg→ZZ)** → genuine diboson samples missing; diboson uses
  only inclusive WW/WZ/ZZ.
- All `H→ZZ→4L` samples (`GluGluHtoZZto4L`, `VBFHto2Zto4L`, …) → minor higgsbkg components missing.

### ✅ Physically fine (checked, not the bug)
- DY xsecs 6688 / 20950 pb and sumw 3.8e12 / 7.6e12 are correct (equiv. lumi ≫ data). The DY problem is
  **selection efficiency**, not the numbers.
- tt/st/diboson scales all O(1e-4), consistent within each process.

## Tested 2026-06-23: shape-from-CR and rateParam — both fail (for instructive reasons)

| config | full r₉₅ | stat | freeze SR autoMCStats |
|---|---|---|---|
| v4 baseline | 1742 | 771 | 1069 |
| v4 + vjets rateParam (shared CR↔SR) | **1791** ⬆ | 783 | 1105 |
| v5 shape-from-CR_vjets *(wrong axis)* | 1221 | 825 | 1135 |
| v5 shape + rateParam | 1228 | 860 | 1141 |

**rateParam is the wrong tool (proven).** vjets rateParam alone makes the limit *worse* (1742→1791);
on top of the shape fix it does nothing (1221→1228). A rateParam floats the overall normalization but
cannot change a bin's Σw² → it leaves every `prop_binSR_hplusc_bin*` (autoMCStats) untouched, which is
the dominant term. Same failure mode as the earlier tt rateParam. **Do not pursue rateParams for this.**

**Shape-from-CR_vjets does NOT work — the regions aren't compatible.** All argmax channels share the bin
edges [0,0.2,…,1.0], but the *axis variable differs*: SR `D = P(hplusc)`, CR_vjets `D = P(vjets)`. A
bin-by-bin transfer pastes the P(vjets) shape onto the P(hplusc) axis → physically meaningless. The
1221 is only a **sensitivity bound**: "if the SR DY shape had CR-like per-bin precision, r₉₅ ≈ 1221"
(prize ≈ −520). It is NOT claimable.

**The orthogonality dilemma (why no cheap fix exists).** argmax channelization makes CR_vjets ⊥ SR_hplusc
(an event wins exactly one class) — but orthogonality is *bought* by the winning class differing, i.e. a
different discriminant. Conversely, any region on the right axis (P(hplusc) for all DY) reuses the SR's
own events → not orthogonal/circular. So **"orthogonal" and "same discriminant" are mutually exclusive**
within this construction; you cannot build a clean CR→SR shape transfer from the existing templates.

**Decisive test (2026-06-23): histogram P(hplusc) for the orthogonal CR_vjets events** (user's idea — the
sharpest attempt: orthogonal CR *and* same axis). Result: CR_vjets P(hplusc) has N_eff 668 but **entirely
at P(hplusc)<0.3, with ZERO events in the signal bins (0.40–0.52)**. Reason: argmax==vjets ⟹ P(vjets) is
max ⟹ P(hplusc) forced low ⟹ the orthogonal region is empty exactly where the SR signal lives. General
law: **any region orthogonal to the SR is, by construction, absent from the SR's discriminant range** —
you cannot estimate the high-P(hplusc) vjets shape from an MVA-orthogonal CR; the info isn't there. This
is why the AN orthogonalizes on a **physics** variable (same-flavor+Z-peak), which doesn't cut on
P(hplusc) and so IS populated across the SR discriminant while staying orthogonal to the eμ SR.

## ✅ FIX THAT WORKS (2026-06-23): smooth the DY SR template

| config | full r₉₅ | stat | freeze SR autoMCStats |
|---|---|---|---|
| v4 baseline | 1742 | 771 | 1069 |
| **v6 DY-smooth** | **1399** (−20%) | 781 | 1173 |

Regularize *only* the `SR_hplusc/vjets` template (nominal + every variation) with a 5-tap binomial
smoothing kernel, on its **own axis** using its **own SR events**, with **proper linear error
propagation** `Σw²ᵢ' = Σⱼ kᵢⱼ² Σw²ⱼ`, rescaled to preserve each template's yield (shape-only). This:
- removes the unphysical zero-spikes (bin6 0±41 from ±79k NLO weight cancellation),
- pools the DY's ~36 effective SR events across the smooth shape → per-bin rel error 32%→~20%,
- drops the limit **1742 → 1399** and collapses the full−freezeSR gap 673→226 (most autoMCStats gone).

**Why this is legitimate (unlike v5=1221):** no axis mismatch, no orthogonality problem, no CR — it's
the DY's own SR distribution, just de-noised. The only assumption (stated): true DY shape ≈ its smoothed
version, i.e. smoothing bias ≪ the MC-stat removed. Standard low-stat template regularization.
**Caveat:** the kernel bandwidth is a knob; widening it lowers the limit further but increases shape
bias. 1399 uses a conservative 5-tap. Could tune, or do the principled version (kernel-density / spline
fit with a validated bandwidth).

Implementation: `b-hive/scripts/dy_template_smooth.py` → `v11_hplusc_v6_dysmooth.{root,txt}`.
Plots: `b-hive/docs/plots/combine_final/automcstats_issue.png` (the issue: SR band explosion, N_eff≈10,
±10⁵ DY weights) and `automcstats_fix.png` (raw vs smoothed DY template + limit bars).

## v32 overhaul — selection, LOWESS, JES/JER, smoothing (2026-06-23)

Found v32 was on a DIFFERENT (looser) selection than v11: `hww_MVA` (25.7k DY events, no ≥1-cjet) vs v11's
`hww_combine_fixed` (10.3k, tight). Fixed v32 to match v11 + enable object shifts. Changes (all in the
b-hive builder/datacard, permanent):
- `make_combine_histograms_v11_v32.py`: SAMPLE_DIR → **hww_combine_fixed** (model kept v9, per user);
  **LOWESS variation-smoothing now OFF by default** (`--smooth` to enable — it sculpts variations, can bias);
  **folded 6 object shifts** (JES/JER + lepton scale/res) by re-scoring the shifted parquets with frozen
  prior/edges (STAGE 3.5).
- `make_datacard_v11_v32.py`: emits the 6 `CMS_*_2022 shape` rows when present.
- `dy_template_smooth.py`: now takes CLI args `[SRC.root] [DST.root]` (was v11-hardcoded).

v32 progression (blind Asimov median r95):
| variant | full | stat | freeze autoMCStats |
|---|---|---|---|
| old (hww_MVA, LOWESS on) | 1934 | 584 | 1130 |
| fixed baseline (hww_combine_fixed, no LOWESS) | 1889 | 600 | 990 |
| + JES/JER object shifts | 1935 | 600 | 1068 |
| **+ vjets smoothing** | **1487** | 580 | 988 |

JES/JER = ~22% syst for v32 (vs 4.8% v11; shifts migrate events across log-L channels). Smoothing
1935→1487 (−23%, same as v11). Smoothed inputs: `combine_inputs/v11_hplusc_v32_v9_smooth.{root,txt}`.
NB the LOWESS-off + hww_combine_fixed switch means the EARLIER v32 numbers (1934, Table 18 below) are the
OLD hww_MVA+LOWESS config — superseded by the above.

## Table 18 — uncertainty breakdown + c-tag placeholder (2026-06-23)

Added a **c-tag lnN placeholder** (5.9% = AN total, on all MC) → `v11_hplusc_v4_ctag.txt`,
`v11_hplusc_v32_v9_ctag.txt`. |Δr|/r % = sqrt(1−(r_frozen/r_nom)²)×100 (quadrature share of total unc.,
r95 scale); statistical = r_stat/r_nom. Freeze-each-source via AsymptoticLimits.

| source | v11 \|Δr\|/r % (r_nom 1743) | v32 \|Δr\|/r % (r_nom 1934) |
|---|---|---|
| **MC-stat (autoMCStats)** | **80.6** | **81.2** |
| Signal theory (4FS5FS,PDF,αS,BR) | 46.2 | 46.6 |
| Scale+PS | 30.7 | 40.9 |
| Lepton | ~0 | 31.0 |
| Bkg-Higgs (ggH-flav,xsec) | 13.9 | ~0 |
| Other-bkg xsec | 9.0 | 13.6 |
| **c-tag (placeholder)** | **3.4** | **12.4** |
| JES/JER (v11 only) | 4.8 | — |
| Pileup / Lumi | ~0 | 3.2 / ~0 |
| **Statistical** | **44.2** | **30.2** |
| Total systematic | 89.7 | 95.3 |

MC-stat dominates both (~81%); v32 more syst-limited (stat 30%). **c-tag placeholder is small (3.4%/12.4%)
because autoMCStats swamps it** — the urgent missing systematic barely moves the limit until MC-stat is
fixed. NB |Δr|/r are quadrature shares, not linearly additive. Also: **v6 smoothing extended to ALL 6
channels** (222 hists) → r95 1399 (SR-only) → **1361** (all channels); CR smoothing adds a small extra gain.

## Completeness check — no missing samples / events (2026-06-23)

Verified DY processing→postprocessing (user asked "does sumw make sense / samples missing?"):

| sample | .coffea (processing) | parquet (postprocess) | match |
|---|---|---|---|
| DYto2L_2Jets_50 | yield 4446, N_eff **1333.4** | 10,325 rows, N_eff **1333.4** | ✅ exact |
| DYto2L_2Jets_10to50 | yield 50.3, N_eff **2.6** | 85 rows, N_eff **2.6** | ✅ exact |

**No events lost in the merge** (N_eff identical proc vs postproc). sumw is correct: parquet stores raw
gen weights (94.8M for `_50`); `scale=lumi·xsec/sumw=4.7e-5` → 4456 yield = .coffea's 4446 (0.2%). So DY
starvation is **real selection physics**, not a processing/normalization bug. Config has exactly 2 DY
samples (both present) + WtoLNu_2Jets; no DY `-ext` missing. `_50` is the only useful DY (N_eff 1333,
collapses to ~10 in the SR tail at ~10⁻⁴ c-tag+MET efficiency); `_10to50` is intrinsically pathological
(85 evts, N_eff 2.6, 20950 pb → weight ~36k each; ~1% of DY yield, pure noise). Also confirmed merging
the vjets *process* into st gives r₉₅ 1742→1756 (≈unchanged) — autoMCStats is process-grouping-invariant.

## vjets is DY + W+jets — W+jets is a 2nd undersampling disaster (2026-06-23)

The `vjets` process = DYto2L_2Jets_50 + DYto2L_2Jets_10to50 + **WtoLNu_2Jets (W+jets)**:

| sample | rows | sum(w) | N_eff | \|w\|max |
|---|---|---|---|---|
| DYto2L_2Jets_50 | 10,325 | 94.8M | 1333 | 225k |
| DYto2L_2Jets_10to50 | 85 | 0.68M | **2.6** | 80k |
| WtoLNu_2Jets (W+jets) | **518** | **49.3M** | **68** | **470k** |

**W+jets is ~34% of the vjets yield from only 518 events** (N_eff 68), with a single event of weight 470k
→ ×scale 3.66e-5 = **17 expected events from one MC event**.

### AN-23-102 §6.1 confirms this EXACTLY and gives the fix (user quoted it 2026-06-23)
The AN states W+jets is "not negligible in the signal region, especially signal-enriched bins"; that
"selected events come mainly from the low W-pT and low HT region where statistics are not sufficient and
events are generated with **large weights → large fluctuations of the W+jets template**" — *precisely* our
WtoLNu_2Jets (518 evts, N_eff 68, w=470k). Their mitigation = THREE parts:
1. **Stitch** jet-binned + W-pT-binned + HT-binned samples (NLO+LO) to maximize stats (§2.3).
2. **Average** the W+jets shape across periods (2016/17/18) then **smooth** it.
3. **Bin-by-bin errors from the averaged/smoothed template**; scale to each period's lumi.

**We have implemented NONE of step 1-2 and only step 3's smoothing (my 1399 fix, now AN-validated).**
Crucially we have **only the inclusive `WtoLNu_2Jets`** in the config — the pT/HT/jet-binned W+jets
samples the AN stitches are **MISSING** (the `WGtoLNuG_PTG*` are W+γ, a different process). So the proper
AN-aligned fix:
1. add the W-pT/HT/jet-binned W+jets samples (LO+NLO) → stitch → fixes low-pT/HT SR starvation;
2. average the W+jets template across eras (2022preEE+postEE+2023) + smooth + bin errors from average;
3. keep my smoothing as the interim stopgap.
**NB:** the cross-era averaging the user ruled out earlier is literally the AN's method *for the W+jets
template* — for this template it's the documented solution, not a shortcut.

## Floor-the-error "histogram hack" — gives 1158 but is NOT honest (2026-06-23)

Setting content&error → 1e-4 for every bin with content ≤ 1e-4 (the popular combine "hack"): r₉₅
1742 → **1158** (below the smoothing's 1399!). **But it cheats.** The gain comes mostly from zeroing the
error in **bin 6** — the *highest-S/√B* bin AND a *weight-cancellation* bin (0±41 from +79k/−79k events,
not genuinely empty). Setting it to 0±0 asserts "background = exactly 0, perfectly known" in the most
signal-sensitive bin → optimistic bias. The quoted claim "the 1e-4 error is ignored, zero impact" is
**wrong**: a tiny error means *perfectly known*, which removes a real uncertainty. Legitimate only for
*genuinely empty* bins (no MC entries); illegitimate for cancellation bins. **Use smoothing (1399), not
this.** Hybrid (floor only zero-raw-entry bins + smooth cancellation bins) would be honest. Script:
`b-hive/scripts/floor_empty_errors.py` → `v11_hplusc_v8_floorerr.{root,txt}`.

## Binning optimization — confirmed dead end (2026-06-23)

Total MC in the SR signal bins is NOT low — only DY is. Per-bin: totB = 750–1600 events (N_eff
330–550), but **tt alone has N_eff ≈ 30,000**; DY (N_eff ≈ 10) drags the *total* bin N_eff down by
~60× and supplies **97–99% of every signal bin's MC-stat error**. autoMCStats blows up not from low
total stat but because DY's ±40–70-event error sits under a **0.05-event** signal (bin6: err 41 = 5.5%
of 752, but ≫ 0.05 sig). Binning range is correct: signal peaks at D=P(hplusc)=0.44–0.52, nothing >0.6.

Rebinning the SR (merge adjacent bins, counts+Σw² add), median expected r₉₅:

| binning | full | freeze SR autoMCStats |
|---|---|---|
| v4 baseline (10 bins) | **1742** | 1069 |
| merge tail only (8) | 1743 | 1070 |
| merge sig5-6+tail (7) | 1864 | 1167 |
| low+sig+tail (6) | 1864 | 1167 |
| coarse sig (4) | 1866 | 1169 |

**Every rebinning ≥ baseline.** Merging the DY-starved bins *adds* their huge errors in quadrature (the
high-weight DY events don't vanish) while *diluting* signal across wider bins → loses both ways. Binning
trades signal resolution for DY stats and cannot win. Only smoothing (1399) helped, because it borrows
info *across* bins via a smoothness prior — which binning cannot do. Script: `b-hive/scripts/rebin_sr_optimize.py`.

**Channel-combination ideas also don't work:** merging the vjets *process* with another bkg process →
no effect (autoMCStats already pools all processes per bin into one total-Σw² nuisance). Tying SR↔CR_vjets
→ rateParam (norm only, useless) or shared shape (axis mismatch). Only merging low-stat *bins* touches
autoMCStats, and that's the binning scan above (dead).

## FINAL COUNT: only 198 vjets MC events exist anywhere in the signal bins (2026-06-23)

Counting *every* vjets event in the full sample by its P(hplusc), **regardless of channel** (no argmax cut):

| D = P(hplusc) | raw vjets events (anywhere) | N_eff | in SR? |
|---|---|---|---|
| 0.40–0.44 | 90 | 9.8 | all 90 |
| 0.44–0.48 | 70 | 10.7 | all 70 |
| 0.48–0.52 | 38 | **0.1** (yield −14, cancellation) | all 38 |
| **signal bins total** | **198** | ~10 | **198 / 198** |

**All 198 are argmax==hplusc (already in the SR); every other channel has exactly zero.** The all-events
P(hplusc) distribution in the signal bins is identical to the SR-only one. Reason: a vjets event with
P(hplusc)≥0.40 essentially always wins hplusc (two of six softmax scores both >0.40 is rare). So there is
**no reservoir of high-P(hplusc) vjets events in any other channel** — the SR vjets shape rests on ~198 raw
MC events total (N_eff≈10/bin); bin6 (highest S/√B) is 38 events cancelling to −14±41, N_eff 0.1. That is
*everything* 2022postEE MC has. Every reshuffling of existing events is ruled out by direct count; only
more MC (binned W+jets, other eras) or data-driven (AN method) adds real information.

## Implication for the fix
DY smoothing (above) is the cheap, legitimate win (−20%, no new data). Beyond it, the limit is gated by
**DY MC-stat in the SR** — a *sample/efficiency* problem, not fixable further by reshuffling templates
(shape-from-CR and rateParam both fail above). Larger gains (toward the ~1221 sensitivity bound or the
AN's 1148) need real DY events. Ways to go further:
1. **Data-driven DY** from a CR orthogonalized on a *physics* variable (same-flavor + Z-peak), NOT the
   MVA argmax — the AN-23-102 method. This is the only construction that is both orthogonal to the SR and
   on the SR discriminant. Needs upstream selection/parquets.
2. **More DY MC** (cross-era added stats — ruled out by user; would directly add SR DY events).
3. **Accept autoMCStats** as a genuine uncertainty (it is being honest: we really don't know the SR DY shape).
4. Correctness (small effect): fix `TbarBQ/TBbarQ` xsec=0; pull in the dropped `-ext`/diboson samples.

### Artifacts (reversible — originals untouched; delete to revert)
- **KEPT (the working fix):** `higgscharm/outputs/combine/v11_hplusc_v6_dysmooth.{root,txt}`;
  `b-hive/scripts/dy_template_smooth.py`; `b-hive/scripts/plot_automcstats_issue.py` + the 2 PNGs
  (`docs/plots/combine_final/automcstats_{issue,fix}.png`, also embedded in vault `combine-plots`).
- **DELETED** (all failed/dishonest tests, 2026-06-23): v5 shape-from-CR (`v11_hplusc_v5_vjetsCR.*`,
  `vjets_shape_from_cr.py`), rateParam (`*_vjrp.txt`, `card_rp*.txt`), binning (`v11_hplusc_rb_m*.*`,
  `rebin_sr_optimize.py`), process-merge (`v11_hplusc_v7_dymerge.*`, `merge_dy_into_st.py`), floor-hack
  (`v11_hplusc_v8_floorerr.*`, `floor_empty_errors.py`), and all their `*.ws.root` + `higgsCombine*` outputs.
- baseline `v11_hplusc_v4.{txt,root}` and the parquets were NOT modified.
4. Fix `TbarBQ/TBbarQ` xsec=0 and pull in the `-ext`/missing diboson samples (correctness; small effect).

## Files
- Datacard/ROOT: `higgscharm/outputs/combine/v11_hplusc_v4.{txt,root}`.
- Builder: `higgscharm/scripts/combine/make_combine_inputs.py` (`read_scale` = lumi·xsec/sumw).
- xsec: dataset config via `analysis/filesets/utils.get_dataset_config`; sumw: `analysis/filesets/sumw_2022postEE.json`.
- Freeze-test script: scratchpad `freeze_test.sh`.
