---
name: hww-postprocess-plot-mechanics
description: run_postprocess plotting -- --plot reads a CACHE, postprocess re-merges from shards and OOMs; use --skipmerging
metadata:
  type: project
---

Three behaviours of `run_postprocess.py` that each cost a ~40 min wasted run
(2026-09-09/10, chasing empty 2022postEE data/MC plots):

1. **`--plot` alone never reads the parquets.** It loads a cached
   `<year>_processed_histograms.coffea` (`run_postprocess.py:439-441`) and raises if
   absent. The cache was 3 weeks stale. To pick up ANY input change you must pass
   `--postprocess --plot` together.

2. **Postprocess discovers samples from DISK, not the config.** Commenting a sample
   out of the fileset yaml while its parquet still exists gives
   `KeyError: '<sample>'` in `get_process_sample_map`. To exclude a sample you must
   move its files, not edit the config.

3. **It re-merges from per-job shards**, so moving only `<sample>.parquet` is undone
   mid-run -- the merged file gets recreated from `parquets_<sample>/<category>/`.
   Quarantine ALL of: `<sample>.parquet`, `parquets_<sample>/`, `<sample>/`,
   `<sample>.coffea`.

**`--skipmerging` is the flag that matters.** Without it, `--postprocess`
unconditionally re-merges every object-shift dir; `WtoLNu_2Jets_2J` (2169 partitions)
loads into one dataframe and gets OOM-killed on a shared login node -- silent death,
no traceback, partial output left behind. The shift merge feeds the inference/combine
path only (per its own docstring), NOT plotting. If the nominal merged parquets already
exist, always pass `--skipmerging`.

Run it in **tmux with the log on EOS** -- a plain nohup dies with the login node and
`/tmp` is wiped on reconnect (see [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]]).

Note `outputs/` in the thomas_new repo is ALREADY a symlink to
`/eos/user/c/cgupta/higgscharm/outputs`. `ls` inside it shows EOS files; do not mistake
those for AFS usage. AFS sits at 92% but is unrelated to these failures.

Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-sumw-trap|hww-combine-sumw-trap]]
