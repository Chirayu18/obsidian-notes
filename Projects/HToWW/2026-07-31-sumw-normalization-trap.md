---
tags: [reference]
status: active
date: 2026-07-31
source: lxplus
---

# ⚠️ combine builder: the sumw normalization trap

**TL;DR — the parquets ARE self-normalizing, but `make_combine_inputs.py` doesn't read the
self-normalizing part. It hand-rolls its own `sumw` sum, and one of its two variants reads the
*legacy* per-shard metadata, which undercounts low-efficiency samples. Rebuild with that one and
V+jets comes out ~2.4× too large and every limit you quote is wrong.**

Found 2026-07-31 while building a with/without c-tag-SF closure. Both of my first rebuilds
disagreed with the reference datacard by a factor ~2.4 in total V+jets — the reference was
right and the rebuilds were wrong.

## There are THREE sumw sources, not two

`read_scale(sample, year, base_dir, lumi)` returns `lumi * xsec / sumw`. Only `sumw` is at
issue — it must be the **pre-selection generator weight sum of the whole dataset**.

| # | source | correct? |
|---|---|---|
| 1 | **`sumw_records/`** — written by `dump_chunk_sumw` **pre-selection, for every read-chunk** | ✅ the real self-normalizing scheme |
| 2 | per-shard schema metadata in `parquets_<sample>/base/` | ❌ **legacy**, undercounts |
| 3 | sidecar `analysis/filesets/sumw_<year>.json` | ✅ correct, but an external file |

The repo's own `read_parquet_sumw()` (`analysis/postprocess/utils.py`) reads **#1** and falls
back to **#2**, and says why:

> Primary: sum the per-chunk `sumw_records` written by `dump_chunk_sumw`. These are emitted on
> the PRE-selection events for EVERY read-chunk (**including chunks that select zero events and
> therefore write no data shard**), so their sum is the true generator sumw.
>
> Fallback … **WARNING: undercounts low-efficiency samples because zero-selection chunks wrote
> no shard and thus no metadata sumw.**

**That is the mechanism.** A read-chunk where no event survives selection writes no data shard,
so its generator weight vanishes from #2 entirely. `make_combine_inputs.py` never calls
`read_parquet_sumw()` — it reimplements the sum, and its two variants correspond to #3
(`.bak_pre_readscale_revert`) and #2 (the version reverted to at 03:04 on 2026-07-31).

## Measured, all three sources (2022postEE)

| sample | `sumw_records` (#1) | shard-meta (#2) | sidecar (#3) | rec/meta | rec/side |
|---|---|---|---|---|---|
| **WtoLNu_2Jets** | 4.574e+13 | 8.520e+12 | 4.940e+13 | **5.37×** | 0.926 |
| **DYto2L_2Jets_10to50** | 6.998e+12 | 2.943e+11 | 7.557e+12 | **23.8×** | 0.926 |
| DYto2L_2Jets_50 | 3.605e+12 | 3.774e+12 | 3.794e+12 | 0.96 | 0.950 |
| TbarQto2Q | 1.021e+09 | 1.406e+07 | 1.021e+09 | **72.6×** | 1.000 |
| TbarWplusto4Q | 2.231e+08 | 6.980e+06 | 2.231e+08 | **32.0×** | 1.000 |
| TTto2L2Nu / WW | — | — | — | 1.00 | 1.000 |
| WWZ / WZZ / ZZZ | **none** | **0.0** | ~1e6 | — | — |

Two things to read off this:

1. **#1 and #3 agree to 1.000** for every sample *except* the three vjets ones (0.926–0.950).
   That gap is the **~7% of vjets events lost to the transient xrootd errors** in the Jul-15
   re-run: those input files were never read, so `sumw_records` legitimately has no record for
   them, while the sidecar was built from the older, complete `.coffea` cutflow.
2. **#2 is catastrophically wrong** exactly where selection efficiency is low — and `WtoLNu_2Jets`
   is a **V+jets** sample, so the damage lands squarely on the template the whole
   negative-weight-reweighting effort was about.

## Full coverage audit (2026-07-31): 44 of 50 samples have records

Scanning every sample in the sidecar:

- **44 have `sumw_records`**, 6 do not (`TTWW`, `TTZ`, `TTZZ`, `WWZ`, `WZZ`, `ZZZ`).
  **None of those 6 is in a v11 process group** (`diboson` is `[WW, WZ, ZZ]`), so the v11
  build logged **zero** sidecar fallbacks — source #1 is fully self-sufficient for this analysis.
- Of the 44, **37 agree with the sidecar to 1.0000**. Seven differ:

| sample | records/sidecar | interpretation |
|---|---|---|
| **HplusBottom_HtoWW** | **0.324** | ⚠️ see below |
| **HplusCharm_HtoWW** (the signal) | **0.844** | ⚠️ see below |
| WtoLNu_2Jets | 0.926 | the ~7% xrootd loss in the Jul-15 vjets re-run |
| DYto2L_2Jets_10to50 | 0.926 | same |
| DYto2L_2Jets_50 | 0.950 | same |
| TQbarto2Q | 0.995 | ~0.5%, negligible |

### ⚠️ The sidecar is STALE for the signal

For `HplusCharm_HtoWW`, the two *independent parquet-derived* sources agree **exactly**:

```
sumw_records   : 7.822690e+04   (80 record files)
shard metadata : 7.822690e+04   (6 shards)      records/meta = 1.0000
sidecar json   : 9.265575e+04                   records/sidecar = 0.8443
```

The fileset lists **80 files**, and there are **80 shards and 80 records** — every input file
was processed, so nothing is missing. Two independent parquet sources agreeing against the
external json means **the sidecar is the outlier**: it was built from an older, larger signal
production.

**Consequence:** switching to source #1 makes the signal template **~18% larger**
($1/0.8443$), which moves the limit directly and is *not* a bug fix — it is a real
normalization change. It should be adopted deliberately, and any limit quoted after the
switch is **not** comparable to the pre-switch numbers without saying so.

### Proof that the records are complete (2026-07-31)

The direct check — summing `genEventSumw` from each NanoAOD `Runs` tree — **cannot be run
without a grid proxy** (the signal is a private production at
`root://maite.iihe.ac.be//store/user/cgupta/…`; all 80 reads fail with
`Auth failed: No protocols left to try`).

Instead, the record **coverage** was verified directly. Each record filename encodes
`<file-uuid>_<tree>_<lo>-<hi>`, so the chunks can be checked for completeness:

```
80 record files
distinct file UUIDs : 80        <- matches the 80 files in the fileset
chunks per file     : min 1, max 1
gaps                : 0         <- every chunk starts at event 0
overlaps            : 0         <- nothing double-counted
events covered      : 277,345
TOTAL sumw          : 7.822690e+04
```

**The records tile the entire dataset exactly once.** Combined with shard metadata agreeing
to 1.0000 and the fileset/shard/record counts all being 80, this is conclusive:
`sumw_records` = 7.823e+04 is the true generator sumw, and the sidecar's 9.266e+04 is stale
(built from an older, larger signal production).

## So do you need the sidecar?

**No — and as of 2026-07-31 `make_combine_inputs.py` no longer does.** `read_scale` was
rewritten to read `sumw_records` (source #1) with the sidecar kept only as a logged fallback
for samples that have no records. The v11 build uses **zero** fallbacks.

The sidecar is not merely redundant, it is **wrong for the signal** (see above), so keeping it
as primary was actively harmful.

**But the switch is a normalization change, not a pure bug fix.** Measured on the rebuilt
templates (summed over all six channels), sidecar → records:

| process | sidecar | records | ratio |
|---|---|---|---|
| **hplusc** (signal) | 0.25 | 0.29 | **1.1844** |
| higgsbkg | 284.19 | 285.20 | 1.0036 |
| tt | 93624.16 | 93624.16 | 1.0000 |
| st | 7457.20 | 7457.20 | 1.0000 |
| diboson | 2137.61 | 2137.61 | 1.0000 |
| **vjets** | 6163.14 | 6534.86 | **1.0603** |

Only signal and vjets move; tt/st/diboson are identical to 4 decimals.

⚠️ **Note the sign.** `sumw` is the *denominator* of `lumi*xsec/sumw`, so a records-sumw that is
*smaller* than the sidecar (vjets 0.926–0.950) makes the yield **larger**, not smaller. SR vjets
goes 745.9 → 802.6 (**+7.6%**) and the SR signal 0.1711 → 0.2026 (**+18.4%**).

Limits computed after the switch are therefore **not directly comparable** to the
1343 / 1371 / 1422 series computed before it. Both are internally consistent; they normalize to
different sumw conventions. The pre-switch datacards are preserved as
`v11_hplusc_v4.{root,txt}.bak_sidecar_20260731`, and the old builder as
`make_combine_inputs.py.bak_sidecar_20260731`.

**Still open:** the vjets 7% is a genuine missing-statistics effect. Re-running vjets with
`ruhex-osgce.rutgers.edu` blacklisted would close it and remove the last records-vs-sidecar
discrepancy that is not simply staleness.

## The limits, both normalizations (2022postEE, blind Asimov)

| variant | full | stat-only | freeze-autoMCStats |
|---|---|---|---|
| **sidecar** — no SF | 1343 | 788 | 1100 |
| **sidecar** — + `CMS_ctag2d_2022` | 1371 | 797 | 1144 |
| **records** — no SF | **1172** | 668 | 941 |
| **records** — + `CMS_ctag2d_2022` | **1192** | 676 | 976 |

Ratio records/sidecar: full **0.869** (SF) and **0.873** (no SF), stat-only 0.848,
freeze 0.853 — all clustered around the naive signal-scaling expectation
$1/1.1844 = 0.844$, slightly above it because the +6% vjets background partly offsets the
signal gain. <span>**This is a normalization shift, not a sensitivity gain.**</span> Nothing
about the discriminant, the reweighting or the systematics changed.

Physics conclusions are unchanged on the new normalization:

- the c-tag SF still costs **+1.7%** (was +2.1%) — same sign, same size;
- the stat-only → full gap is still autoMCStats-dominated (freeze 976 vs full 1192).

⚠️ **No `2dcat` number.** That build failed — `outputs/hww_combine_2dcat/2022postEE/mva/`
does not exist (the tree was rebuilt in a new layout on 2026-07-30 22:08–23:09 and
`run_inference.py` has not been re-run on it). A limit of 2140 appeared in the batch output,
but it came from `v11_hplusc_2dcat.txt` **rewritten at 09:39 by a concurrent
`drive_combine.py`**, i.e. a mixed-normalization artifact. It is **not** comparable to the
1422 in [[2026-07-19-ctag2d-full-documentation]] and must not be quoted.

Reproduce either series: the pre-switch datacards are
`v11_hplusc_v4.{root,txt}.bak_sidecar_20260731` and the pre-switch builder is
`make_combine_inputs.py.bak_sidecar_20260731`.

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

The reverted version reads source **#2**, which is never right for this tree. Do not use it.

The *forward* fix — pointing `read_scale` at `read_parquet_sumw()` (source #1) — becomes safe
once **(a)** the legacy diboson-triplet samples (`WWZ`/`WZZ`/`ZZZ`) are re-produced with
`dump_chunk_sumw` so they have `sumw_records`, and **(b)** the vjets re-run is redone with
`ruhex-osgce.rutgers.edu` blacklisted, closing the ~7% gap. At that point the sidecar can be
retired and the parquets really are fully self-normalizing.

Related: [[2026-07-19-ctag2d-full-documentation]], [[RESUME-condor-retrain]],
[[2026-07-18-v32-optimization-negative-results]]
