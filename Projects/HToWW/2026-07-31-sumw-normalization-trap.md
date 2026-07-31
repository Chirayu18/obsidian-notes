---
tags: [reference]
status: active
date: 2026-07-31
source: lxplus
---

# ⚠️ combine builder: the sumw normalization trap

**TL;DR — `scripts/combine/make_combine_inputs.py` has two `read_scale` implementations.
Only the *sidecar* one is correct. If you rebuild the combine inputs with the
parquet-metadata one, V+jets comes out ~2.4× too large and every limit you quote is wrong.**

Found 2026-07-31 while building a with/without c-tag-SF closure. Both of my first rebuilds
disagreed with the reference datacard by a factor ~2.4 in total V+jets — the reference was
right and the rebuilds were wrong.

## The two implementations

`read_scale(sample, year, base_dir, lumi)` returns `lumi * xsec / sumw`. The `sumw` comes from
one of two places:

| variant | source of `sumw` | correct? |
|---|---|---|
| **sidecar** (`.bak_pre_readscale_revert`) | `analysis/filesets/sumw_<year>.json` | ✅ **yes** |
| parquet metadata | sums `sumw` key from `parquets_<sample>/base/*.parquet` schema metadata | ❌ **undercounts** |

The docstring of the sidecar version says it plainly:

> LOCAL/UNCOMMITTED: reads the true generator sumw from the sidecar
> `analysis/filesets/sumw_<year>.json` … because **the existing parquet metadata sumw
> undercounts low-efficiency samples**. The committed fix (`dump_chunk_sumw`) makes future
> runs' parquet sumw correct on their own, at which point this can revert.

The revert was made prematurely — the parquets in `hww_combine_fixed/2022postEE` were produced
*before* `dump_chunk_sumw`, so their metadata is still the undercounting kind.

## How badly it undercounts (2022postEE, measured)

| sample | sidecar sumw | parquet-md sumw | ratio |
|---|---|---|---|
| **WtoLNu_2Jets** | 4.9395e+13 | 8.5197e+12 | **5.80×** |
| TbarQto2Q | 1.0206e+09 | 1.4057e+07 | **72.6×** |
| TbarWplusto4Q | 2.2307e+08 | 6.9797e+06 | **32.0×** |
| WGtoLNuG_PTG10to100 | 2.1944e+11 | 1.8459e+11 | 1.19× |
| WWZ / WZZ / ZZZ | ~1e5–1e6 | **0.0** | ∞ (no metadata at all) |
| most samples (DY, tt, Higgs, ST) | — | — | **1.000** ✅ |

The affected samples are exactly the "low-efficiency" ones — few events survive the selection
per input file, so the per-chunk metadata misses most of the generator sum. `WtoLNu_2Jets` is a
**V+jets** sample, which is why the damage lands squarely on the template that the whole
negative-weight-reweighting effort was about.

## The symptom

Rebuild with the parquet-metadata version and you get:

| build | SR vjets | all-channel vjets |
|---|---|---|
| reference `v11_hplusc_v4.root` (sidecar) | 745.9 | 6163.1 |
| rebuild, parquet-md | 3779.7 | 14491.5 |

`sumw` is in the **denominator**, so undercounting it **inflates** the yield. Note both of my
rebuilds (with and without the c-tag SF) agreed *with each other* to ~1% — the bug is a common-mode
scale, so an A/B comparison still looks internally consistent. **That is what makes it dangerous:
it does not announce itself.**

## Fix / how to check

```bash
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/scripts/combine
grep -n "sidecar" make_combine_inputs.py     # must match -> sidecar version is active
```

If it does not match, restore it:

```bash
cp make_combine_inputs.py make_combine_inputs.py.bak_parquetmd_<date>
cp make_combine_inputs.py.bak_pre_readscale_revert make_combine_inputs.py
```

**Sanity check after any rebuild:** SR V+jets should be **~735** and total V+jets across all six
channels **~5.8k** (2022postEE, no c-tag SF; the reference `v4` card, which *has* the SF, gives
745.9 / 6163). If V+jets is ~3780 / ~14.5k, you are on the parquet-metadata path.

## When the revert becomes safe

Only once the parquets are **re-produced** by a processor that includes `dump_chunk_sumw`.
Until then the sidecar `sumw_<year>.json` is the only correct source. The sidecar was built by
`scripts/combine/compute_sumw.py` from the `.coffea` cutflow.

Related: [[2026-07-19-ctag2d-full-documentation]], [[RESUME-condor-retrain]],
[[2026-07-18-v32-optimization-negative-results]]
