---
tags: [reference, decision, framework]
status: superseded
superseded_by: "[[2026-11-12-train-card-scorer-implemented]]"
date: 2026-11-12
source: laptop
evidence: in-progress
---

# TRAIN-mode stat-only limit (design, 2026-11-12)

## Chirayu's request
- "wire things in the framework PROPERLY to make a stat only limit with autoMCstats if the framework is run in TRAIN mode, this makes things considerably faster and I can also debug and stuff"
- On the SR split (`SR_hplusc_1cj` / `SR_hplusc_2cj` by `cjet_multiplicity`, `combine.channel_splits`): "For today, yes, do that". Today's TRAIN parquets lack the split variable. So: future TRAIN writes it, and the builder fails by default but can build a single merged SR with an explicit flag.

## What TRAIN outputs contain (read 2026-11-12, `analysis/processors/base.py::_mode_sink`, one real A shard)
- Per job `.coffea`: per-sample `sumw`/`sumw2`/`events_read`/`chunks` over the full pre-selection chunk (zero-selection chunks included), `selected_events`, Route B `routeb_stitch`, `execution_checks` (files, expected = processed entries), provenance (mode/year/features/selection hashes).
- Per chunk parquet (eμ + ≥1 c-jet preselection, nominal only, MC and data): the 26 model `FEATURES`, `event/run/luminosityBlock/fold`, `weight_nominal`, `process/sample/label/is_*`, and for negrw datasets `lhe_*`, `genparton*`, `weight_negrw(_std)`. **No `cjet_multiplicity`.**
- Parquet sumw (`sumw_records/`, per-shard metadata) is written only in legacy parquet mode (`base.py:98`). TRAIN and RUN normalise from the coffea sums, as `scripts/mva/split_folds.py` already does for training.

## Design
Reuse, do not copy: TRAIN coffea + parquet → RUN-shaped accumulator → the existing `build_cards_from_templates.py` (`make_process_hists`, `finalize_templates`, `write_root`, `write_data_obs`, `write_datacard`).
- Score each event with `FoldModels.score` (its held-out fold model; same class RUN uses) and fill with `analysis/sinks/hww.py::make_templates` (same function RUN uses), nominal weight only.
- Normalisation: `lumi*xsec/sumw` from the TRAIN coffea sums (Route B: the existing stitch scale factors).
- `--stat_only`: no shape systematics, no lnN, no negrw shape; keeps `autoMCStats` and the unconstrained `rate_tt` rateParam (recorded as `rate_params_kept` in `template_policy.json`).
- `--merge_channel_splits`: drops `combine.channel_splits` (single SR). Without it, a missing split variable is an error.
- Guards ported from the production prep (`~/bhive_prod_20261112_sol/prepare.py`): coffea mode/year/hash match, entry-count checks, no duplicate chunks, parquet hash/year/fold metadata, `source_file` in the coffea file record, per-(era, sample) parquet rows = summed `selected_events`, no orphan parquet. Accepts the validated `inputs.json` lists.
- TRAIN (and slim RUN) parquets will also carry the `combine.channel_splits` variables from now on. These are extra columns, so the feature and selection hashes are unchanged.

## Decisions to state with every result
- **negrw:** TRAIN parquets carry `weight_negrw` from whatever model the job loaded by path (TRAIN records no model identity). The A/B TRAIN jobs predate the v2 adoption (`71eef55`), so they most likely hold the July model (`05567a8c…`). The builder re-scores g from the stored generator columns with the workflow's current `negrw.model`, so the stat-only card uses the same negrw model as RUN, and the RUN negrw identity check applies unchanged.
- **Stat-only** here means MC statistics (autoMCStats) + Asimov data statistics, with `rate_tt` floating.
- **Merged SR** cards from today's TRAIN outputs are not directly comparable with split-SR RUN cards.

## Status
Design only at time of writing; implementation and tests follow in this note's successor/update. No result yet. Production fold models do not exist yet (training prep running).
