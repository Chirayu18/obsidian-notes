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

## Implication for the fix
The limit is gated by **DY MC-stat in the SR**, which is a *sample/efficiency* problem, not xsec/sumw.
Cross-era averaging (ruled out by user) would have helped because it adds DY events. Remaining honest
levers, in order:
1. **Data-driven DY** in the SR (CR→SR transfer, as AN-23-102 does) — removes the MC-stat entirely.
2. **Take DY *shape* from the high-stats `CR_vjets`**, normalize to SR yield → kills the per-bin noise.
3. **Drop `DYto2L_2Jets_10to50` from the SR** (N_eff=2.6, pure noise; only 0.7% of DY yield).
4. Fix `TbarBQ/TBbarQ` xsec=0 and pull in the `-ext`/missing diboson samples (correctness; small effect).

## Files
- Datacard/ROOT: `higgscharm/outputs/combine/v11_hplusc_v4.{txt,root}`.
- Builder: `higgscharm/scripts/combine/make_combine_inputs.py` (`read_scale` = lumi·xsec/sumw).
- xsec: dataset config via `analysis/filesets/utils.get_dataset_config`; sumw: `analysis/filesets/sumw_2022postEE.json`.
- Freeze-test script: scratchpad `freeze_test.sh`.
