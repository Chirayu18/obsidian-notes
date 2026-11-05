---
name: hww-combine-sumw-trap
description: HToWW combine builder has two read_scale variants; only the sidecar sumw one is correct — parquet-metadata undercounts WtoLNu 5.8x and inflates V+jets ~2.4x
metadata: 
  node_type: memory
  type: project
  originSessionId: af76ec6a-a549-46b2-be18-cf006051e43e
  modified: 2026-07-31T07:51:45.149Z
---

There are **THREE** sumw sources. The parquets ARE self-normalizing, but
`scripts/combine/make_combine_inputs.py` never reads the self-normalizing part — it
hand-rolls its own sum, in two variants:

1. ✅ `sumw_records/` — `dump_chunk_sumw`, **pre-selection, every read-chunk**. The real
   self-normalizing scheme. Read by the repo's own `read_parquet_sumw()`
   (`analysis/postprocess/utils.py`) — which `make_combine_inputs.py` does NOT call.
2. ❌ per-shard schema metadata in `parquets_<sample>/base/` — **legacy**, undercounts.
3. ✅ sidecar `analysis/filesets/sumw_<year>.json` (`.bak_pre_readscale_revert`).

**Mechanism:** a read-chunk where no event survives selection writes no data shard, so its
generator weight vanishes from #2. Measured undercount: WtoLNu_2Jets 5.4×,
DYto2L_10to50 23.8×, TbarQto2Q 72.6×, TbarWplusto4Q 32×; WWZ/WZZ/ZZZ have neither
records nor metadata. `sumw` is the denominator, so undercounting **inflates** the yield.

**Do you need the sidecar? NO — as of 2026-07-31 `read_scale` was rewritten to use #1**,
sidecar only as a logged fallback. The v11 build uses ZERO fallbacks (the 6 samples lacking
records — TTWW/TTZ/TTZZ/WWZ/WZZ/ZZZ — are in no v11 process group).

**The sidecar is STALE for the signal.** HplusCharm: records = shard-meta = 7.823e+04
exactly (ratio 1.0000) vs sidecar 9.266e+04. Proven complete by record coverage: the 80
records tile all 80 files, 1 chunk each, **0 gaps / 0 overlaps**, 277,345 events. (The
direct `Runs`-tree genEventSumw check is impossible without a grid proxy — private
production at maite.iihe.ac.be.)

**Switching is a NORMALIZATION CHANGE, not just a bug fix.** sumw is the DENOMINATOR, so
smaller records-sumw => LARGER yield: signal +18.4%, vjets +6.0%, tt/st/diboson exactly
1.0000. Limits move accordingly:

| variant | sidecar | records |
|---|---|---|
| no SF | 1343 / 788 / 1100 | **1172 / 668 / 941** |
| + CMS_ctag2d_2022 | 1371 / 797 / 1144 | **1192 / 676 / 976** |

(full / stat-only / freeze-autoMCStats). Ratios ~0.85-0.87 ~ 1/1.1844 — normalization, NOT
sensitivity. c-tag SF still costs ~+1.7%; still autoMCStats-dominated.

Backups: `v11_hplusc_v4.{root,txt}.bak_sidecar_20260731`,
`make_combine_inputs.py.bak_sidecar_20260731`.

**Symptom:** rebuilt combine inputs give SR vjets ~3780 / all-channel vjets ~14.5k instead
of the correct **~750 / ~6.2k** (2022postEE). Dangerous because it is a *common-mode* scale —
two variants rebuilt the same way still agree with each other to ~1%, so an A/B comparison
looks internally consistent while both numbers are wrong.

**Check after any rebuild:** `grep -n sidecar scripts/combine/make_combine_inputs.py` must
match, and SR vjets must be ~750, not ~3780.

Safe to revert only once parquets are re-produced with `dump_chunk_sumw`.

See [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-negweight-reweight-fix|hww-negweight-reweight-fix]].
Vault note: `Projects/HToWW/2026-07-31-sumw-normalization-trap.md`
