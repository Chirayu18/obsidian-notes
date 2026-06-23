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

## Implication for the fix
The limit is gated by **DY MC-stat in the SR** — a *sample/efficiency* problem, not xsec/sumw, and not
fixable by reshuffling the existing MC templates (shape-from-CR and rateParam both fail above). The
achievable prize is bounded at ~520 in r₉₅ (1742→1221). Legitimate ways to claim it:
1. **Data-driven DY** from a CR orthogonalized on a *physics* variable (same-flavor + Z-peak), NOT the
   MVA argmax — the AN-23-102 method. This is the only construction that is both orthogonal to the SR and
   on the SR discriminant. Needs upstream selection/parquets.
2. **More DY MC** (cross-era added stats — ruled out by user; would directly add SR DY events).
3. **Accept autoMCStats** as a genuine uncertainty (it is being honest: we really don't know the SR DY shape).
4. Correctness (small effect): fix `TbarBQ/TBbarQ` xsec=0; pull in the dropped `-ext`/diboson samples.

### Artifacts (reversible — originals untouched; delete to revert)
- `higgscharm/outputs/combine/v11_hplusc_v5_vjetsCR.root` + `v11_hplusc_v5_vjetsCR.txt` (sensitivity test)
- `…/v11_hplusc_v4_vjrp.txt`, `v11_hplusc_v5_vjrp.txt` (rateParam tests) + `*.ws.root` workspaces
- `b-hive/scripts/vjets_shape_from_cr.py` (the transfer script)
- baseline `v11_hplusc_v4.{txt,root}` and the parquets were NOT modified.
4. Fix `TbarBQ/TBbarQ` xsec=0 and pull in the `-ext`/missing diboson samples (correctness; small effect).

## Files
- Datacard/ROOT: `higgscharm/outputs/combine/v11_hplusc_v4.{txt,root}`.
- Builder: `higgscharm/scripts/combine/make_combine_inputs.py` (`read_scale` = lumi·xsec/sumw).
- xsec: dataset config via `analysis/filesets/utils.get_dataset_config`; sumw: `analysis/filesets/sumw_2022postEE.json`.
- Freeze-test script: scratchpad `freeze_test.sh`.
