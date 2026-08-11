---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# What actually limits the H+c sensitivity, and the route to ~1000

Starting point: **r < 1185** (2022postEE, `hww_combine_2dcat`, after the JES/JER fix in
[[2026-08-11-jes-jer-bug-fixed]]). Stat-only floor is **637**.

Everything below is measured on the real card, not estimated.

## The dominant systematic is MC statistics, not theory

Freezing nuisance groups one at a time, with everything else left floating:

| what is frozen | limit | cost of that group |
|---|---:|---:|
| nothing (nominal) | **1185** | — |
| **all autoMCStats** (`rgx{prop_bin.*}`) | **933** | **252** |
| all constrained nuisances (stat-only) | 637 | 548 |

**MC statistics alone is worth 252 units — roughly half the total systematics penalty.**
For comparison, the largest single lnN nuisance (`xsec_hplusc_4FS_5FS`, the 30% H+c
flavour-scheme theory term) swings the limit by 370 between its ±1σ endpoints, but that is
a *theory argument to be won*, whereas MC stats is an engineering problem.

## It is concentrated almost entirely in the signal region

| freeze MC-stat in | limit |
|---|---:|
| **`SR_hplusc`** | **962** |
| `CR_vjets` | 1174 |
| `CR_diboson` | 1170 |
| `CR_tt`, `CR_st`, `CR_higgsbkg` | 1185 (no effect) |
| all channels | 933 |

The SR alone accounts for **223 of the 252**. The control regions are essentially free.

## And within the SR, it is V+jets

Per-bin relative statistical error in `SR_hplusc`:

| process | SR total | per-bin rel. error | n_eff (min / median) |
|---|---:|---|---|
| tt | 16938.8 | **0.3%** | 414 / 96500 |
| higgsbkg | 131.1 | 1.5–7% | 1.4 / 1890 |
| diboson | 599.5 | 2.3–4% | 4.4 / 797 |
| **V+jets** | **1507.7** | **14–23%** | **1.0 / 30** |

V+jets is only ~8% of the SR background but carries nearly all of the MC-stat penalty.

### Two things this is NOT

1. **Not a negative-weight problem.** `weight_negrw` is already applied and is well behaved:
   max |w| = 1.0, median 0.56, and the ten largest-|w| events carry only 0.2% of the total
   for DY-50. negrw fixes weight *sign* cancellation; `n_eff = (Σw)²/Σw²` is destroyed by
   weight *dispersion*, and there is none here. A weight cap would achieve nothing.

2. **Not a binning artifact — rebinning will not fix it.** Only **bin 1** falls below the
   autoMCStats threshold of 10, and bin 1 holds almost nothing (vjets 0.45 events,
   higgsbkg 0.016, diboson 0.248). Merging it removes ~3 nuisances, not the 223-unit
   penalty. The cost is spread across *all ten* vjets bins, every one of which sits above
   threshold but carries a 14–23% error.

**It is a genuine MC statistics shortfall.** Post-selection, 2022postEE has only 10,328
DY-50, 519 W+jets and 84 DY-10to50 events, spread over 6 channels × 10 bins.

## Measured: what more V+jets MC buys

Scaling **only** the V+jets bin errors by 1/√N (yields untouched, so this isolates the
MC-stat effect from any change in normalisation) and re-running the limit:

| V+jets MC | limit | gain |
|---|---:|---:|
| current (postEE only) | **1185** | — |
| **2× (add preEE)** | **1077** | −108 |
| **3× (add preEE + 2023)** | **1037** | −148 |
| ∞ (MC stat frozen) | 933 | −252 |

Diminishing returns are visible: 3× captures 148 of the 252, because once V+jets errors
fall the other processes begin to dominate.

## Route to ~1000 — the ordering matters

| # | action | expected limit | effort |
|---|---|---:|---|
| **1** | **3× V+jets MC (preEE + 2023)** | **1037** | processing already exists |
| 2 | `flavor_composition_ggH` correctly scoped | ~1012 | config only, independent |
| 3 | AN's Nc-j=1 / Nc-j>1 SR split | ~930 | **blocked by 1 — see below** |

**~1000 is comfortably reachable**, and none of it requires winning the argument about the
30% 4FS/5FS theory uncertainty.

### The Nc-j split is currently blocked by the same MC shortfall

`cjet_multiplicity` is already in the parquets, so the AN's Nc-j=1 / Nc-j>1 split (lines
337–338, quoted at +8%) needs no reprocessing. The SR populations are favourable —
**signal is 91% Nc-j=1 against tt's 79%**, so the split does concentrate signal.

But it collides with the MC-stat problem above. Raw V+jets MC events in the SR:

| category | raw V+jets MC events | per bin (10 bins) |
|---|---:|---:|
| combined SR (current) | 1043 | 104 — already n_eff ≈ 30 |
| Nc-j = 1 | 896 | 90 |
| **Nc-j > 1** | **147** | **14.7** |

The Nc-j>1 category would sit at `n_eff` of order 5–15 per bin, i.e. **below the
autoMCStats threshold of 10**, spawning per-bin nuisances precisely in the region that
already costs 223 units. The AN's +8% is quoted for **full Run 2**, with several times the
MC available.

**On 2022postEE alone the split would probably cost more in MC-stat nuisances than it
gains in separation.** After action 1, Nc-j>1 would hold ~440 V+jets events and the split
becomes affordable — so this is a good idea whose prerequisite is more MC, not a bad idea.

**This is a conservative lower bound on the multi-era gain.** The test above adds only MC
statistics. A real multi-era fit also adds **data**, which lowers the 637 stat-only floor
itself — so the true multi-era limit should be better than 1037.

## Caveat on the impacts ranking

The per-nuisance impacts loop is **partial**: 9 of 23 converged, and all 13 *shape*
systematics returned a degenerate single-quantile result while combine exited 0. So JES/JER
and ctag2d costs are currently unmeasured and could re-rank items below the top two. See
the follow-up list in [[2026-08-11-jes-jer-bug-fixed]].
