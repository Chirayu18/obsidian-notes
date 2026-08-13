---
tags: [reference]
status: active
date: 2026-08-13
source: lxplus
---

# W+jets: inclusive -> jet-binned (0J/1J/2J), 2022postEE

Task A1.1. Replaces the inclusive `WtoLNu_2Jets` with the three jet-binned NLO
aMCatNLO samples, to fix the V+jets MC-statistics problem that dominates the limit
(autoMCStats = **-255** of the -523 total systematic budget; V+jets `n_eff`=280 in
the SR vs <=1.1% relative stat error for every other background).

## Cross sections -- XSDB, retrieved 2026-08-13

| sample | xsec (pb) | events | files | neg-w XSDB | neg-w measured |
|---|---|---|---|---|---|
| `WtoLNu-2Jets_0J` | 55,760 | 678.4M | 3,432 | 10.31% | **10.17%** |
| `WtoLNu-2Jets_1J` | 9,529 | 522.6M | 2,669 | 25.85% | **25.67%** |
| `WtoLNu-2Jets_2J` | 3,532 | 344.6M | 2,135 | 34.70% | **34.71%** |
| **sum** | **68,821** | **1,545.5M** | **8,236** | | |
| *old inclusive* | *67,710* | *281.5M* | *381* | | *16.08%* |

Sum is **+1.6%** vs the inclusive -- normal NLO merging spread, not a double-count.
The measured negative-weight fractions match XSDB to ~1%, confirming both the
sample identity and the records.

### XSDB metadata is WRONG on two fields

XSDB reports `accuracy: "LO"` and `matrix_generator: "Pythia8"` for all three.
**Both are wrong** (the entries are auto-populated, `comments: "Automatically
computed"`). `amcatnloFXFX` is NLO, and the 10-35% negative-weight fractions are
impossible at LO -- LO matrix elements have strictly positive weights; negative
weights only arise from NLO subtraction. `cross_section` is the reliable field.

## The payoff: 15.6x effective statistics

Raw events go up 5.5x, but **effective** statistics go up **15.6x**, because the
inclusive sample spends most of its cross section on 0-jet events:

| sample | n_eff/N | equivalent lumi |
|---|---|---|
| 0J | 0.6347 | 7.72 /fb |
| 1J | 0.2367 | 12.98 /fb |
| 2J | 0.0935 | 9.12 /fb |
| **jet-binned total** | | **29.82 /fb** |
| inclusive | 0.4602 | **1.91 /fb** |

Projected SR effect: `n_eff` 280 -> **~4,400**, i.e. V+jets relative stat error
5.98% -> **~1.5%**, comparable to the other backgrounds.

## Scope: jet-binned ONLY (option 1), not the full AN stitch

AN-23-102 sec 2.3's full prescription is *"jet-binned samples with LHE Vpt smaller
100 GeV and pT-binned samples with pT larger than 100 GeV"* -- i.e. 7+ samples.
**We deliberately did only the jet-binned part for now.**

This is self-consistent: **measured, every 0J event has `LHE_Vpt < 100`**
(min 0.0, max 62.4, 100.00% below 100). So no `LHE_Vpt` cut is needed and there is
no overlap with the `PTLNu-*` samples -- those simply are not included, so W-pT >
100 GeV is under-covered relative to the AN. Adding them is the natural follow-up.

## negrw: NO retrain needed -- verified, not assumed

The negrw ensemble was trained with the inclusive sample in its dataset list. It
**still applies** to the jet-binned samples:

- `P+(x)` is a **generator property** of amc@NLO FxFx. These are the same
  generator/tune/merging, sliced by jet multiplicity.
- `lhe_njets` is already an input feature, so the jet-bin distinction is *inside*
  the model's domain, not outside it.
- **The risk would be extrapolation, so it was measured.** The jet-binned gen phase
  space sits INSIDE the inclusive sample's support:

  | check | result |
  |---|---|
  | 2J events beyond inclusive p99.9 Vpt (240.4) | 0.74% |
  | 2J events beyond inclusive **max** Vpt (884) | **0.002%** |
  | 2J events beyond inclusive **max** HT (2239) | **0.000%** |

  Interpolation, not extrapolation -- exactly the condition
  [[2026-07-11-negweight-reweight-training-region]] requires.

`negrw.datasets` was updated to the three new names. Note `_dataset_matches`
strips only `_\d+$`, so `WtoLNu_2Jets_0J` does NOT collapse to `WtoLNu_2Jets` --
checked, no false match.

## Blocker hit and fixed: coffea crashes on a malformed SITECONF entry

`make_filesets` died with `Exception: 'rse'` -> `dataset_discovery_*.json` written
as literal `null` -> `TypeError: 'NoneType' object is not iterable`.

**Root cause:** `coffea/dataset_tools/rucio_utils.py::get_xrootd_sites_map()` reads
`site["rse"]` for **every** site in `/cvmfs/cms.cern.ch/SITECONF/`. Exactly **one**
of 143 entries -- **`T3_CN_Nanjing`** -- publishes a DISK volume with **no `rse`
key**, raising `KeyError` and killing the whole replica lookup.

```json
{"site": "T3_CN_Nanjing", "volume": "NNU_testing",
 "protocols": [{"protocol": "direct", "access": "site-rw", ...}], "type": "DISK"}
```

**The site whitelist does NOT protect you** (`T3_CN_Nanjing` is already absent from
the 39-site whitelist) because the sites map is built over ALL of SITECONF *before*
the allowlist is applied. **`jobs_status.py` blacklisting does not help either** --
it filters an *existing* fileset; here discovery itself fails, one stage earlier.
This is a distinct failure mode from [[hww-jobs-status-blacklist-memoryless]].

Also note `.sites_map.json` is cached for only **10 minutes**, so the bad entry is
re-read on essentially every run.

**Fix applied:** `site["rse"]` -> `site.get("rse")`, 3 occurrences, in
`~/.local/lib/python3.9/site-packages/coffea/dataset_tools/rucio_utils.py`
(backup `.bak_pre_rse_*`). This is the upstream-correct behaviour: skip the
malformed entry instead of aborting. Worth reporting upstream.

Rucio also needs `source /cvmfs/cms.cern.ch/rucio/setup-py3.sh` -- without it,
`ConfigNotFound`. And `make_filesets` needs the **`base`** env (coffea 2025.9.0);
`b_hive` has coffea 0.7.22 with no `dataset_tools`.

## Disk cost: negligible

The selection keeps **1 in 542,473** W+jets events (519 rows survived from 281.5M).
Merged parquet was **1.7 MB**. At 5.5x the input that is ~9 MB merged / ~10 GB
including all 12 shift dirs, against 97 GB already used and 2.1 PB free.
**CPU is the cost here, not disk.**

## State

- Fileset rebuilt: 8,236 files, counts match DAS **exactly** (3432/2669/2135).
- **550 condor jobs submitted** 2026-08-13 18:02, `--nfiles 15` (default),
  clusters **9189871** (0J, 229), **9189872** (1J, 178), **9189873** (2J, 143).
- Backups: `2022postEE_nanov12.yaml.bak_pre_wjets_*`,
  `hww_combine_2dcat.yaml.bak_pre_wjets_*`, fileset `.bak_20260813_174549`.

### Remaining pipeline after jobs land
1. `run_postprocess.py --postprocess --mva`
2. inference over nominal + 12 shift dirs
3. `make_combine_inputs.py` -> datacard
4. `combine -M AsymptoticLimits` -> compare against **1160**

Watch for: `read_scale` needs `sumw_records` per sample (see
[[hww-combine-sumw-trap]]); the three new samples must each produce them.
