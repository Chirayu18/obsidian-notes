---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# Higgscharm framework changes

Recommended changes to the upstream higgscharm framework so that the
parquet → MVA-inference → combine pipeline runs automatically, without
needing the b-hive-side scripts to look up xsec / lumi / sumw in
multiple YAMLs.

Source locations referenced:
- `analysis/processors/base.py`
- `analysis/postprocess/postprocessor.py`
- `analysis/postprocess/utils.py`
- `analysis/postprocess/plotter.py`

## Pain points today

1. **Raw sumw is destroyed before disk.** `save_histograms_by_sample`
   computes `weight = lumi × xsec / sumw` and applies it to the
   histograms but the per-sample `<sample>.coffea` it saves
   (postprocessor.py:144) is just `{variable: hist.Hist}` — no
   metadata block. The base-category cutflow file written by
   `save_cutflows` (utils.py:227-229) multiplies every cutflow value
   by the same weight, so `initial = sumw × (lumi×xsec/sumw) = lumi×xsec`
   — the raw sumw has been cancelled out. Verified for
   `HplusCharm_HtoWW`: `cutflow_base_HplusCharm_HtoWW.coffea` has
   `initial = 59.054 = 26671.7 × 0.0022141`.

2. **Lumi / xsec / sumw live in three different YAMLs.** Anything
   downstream that wants a yield in events at the data luminosity
   has to load `luminosity.yaml`, the fileset YAML, and (if it's
   working from parquet) re-derive sumw from NanoAOD.

3. **MVA inference is external.** Per-event score columns have to be
   computed in a separate script that re-loads parquets and models.
   The systematic-variation loop already in
   `fill_histograms_from_parquets` (postprocessor.py:99-107) is
   exactly the right machinery — but it can't see the score.

4. **Combine export is external.** The TH1D-writing script lives in
   b-hive (`scripts/make_combine_histograms_v11.py`) and re-implements
   the per-sample lumi scaling that postprocess already does once.

5. **Parquets cannot be normalised on their own.** Per-event weights
   in the parquet are pre-lumi-scaling. Without an external sumw
   lookup, no consumer of the parquet alone can produce a yield in
   events.

## Recommended changes

In order of value-for-effort.

### 1. Persist sumw and the scale factor in `<sample>.coffea` (1 PR, ~5 lines)

`save_histograms_by_sample` already has `metadata` and `weight` in
scope (postprocessor.py:137-138). Wrap the histograms in a dict
with a metadata block:

```python
save({
    "histograms": scaled_histograms,
    "metadata": {
        "sumw":        metadata["sumw"],
        "lumi":        luminosities[year],
        "xsec":        dataset_config[sample].get("xsec"),
        "lumi_weight": weight,        # lumi × xsec / sumw
        "era":         dataset_config[sample]["era"],
    },
}, Path(output_dir) / f"{sample}.coffea")
```

Consumers that today do `load(...)["kinematics"]` move to
`load(...)["histograms"]["kinematics"]`. A short transition shim
inside `load_processed_histograms` (utils.py:315-323) handles both
shapes for one release.

For `save_cutflows` (utils.py:215-233): also keep the unscaled
`metadata[category]["cutflow"]` alongside the scaled version so the
multiplication stops being destructive. Currently a one-way
operation.

**Impact:** every downstream script can read sumw, xsec, lumi, and
the scale factor from a single file — the one it already loads.

### 2. Write sumw into the parquet schema metadata (~5 lines)

In the processor's parquet branch (base.py:190-219), `sumw` is in
scope when `dump_pa_table` writes a chunk. Stamp it into pyarrow's
schema-level metadata:

```python
table = table.replace_schema_metadata({
    **(table.schema.metadata or {}),
    b"sumw": str(sumw).encode(),
    b"xsec": str(dataset_config[dataset]["xsec"]).encode(),
    b"era":  dataset_config[dataset]["era"].encode(),
})
```

When `fill_histograms_from_parquets` (postprocessor.py:40-54) merges
chunks into the per-sample parquet, sum the per-chunk `sumw` values
and stamp the total onto the merged parquet's schema.

**Impact:** the parquet alone is self-normalising. Critical for the
b-hive use case where the natural input is parquet and the coffea
file is only loaded as a sumw sidecar.

### 3. Built-in MVA-inference plugin in postprocess

Today `fill_histograms_from_parquets` (postprocessor.py:27-109)
builds `variables_map` from columns and fills histograms with the
existing nominal + Up/Down loop. Extend with a workflow-config-driven
inference step:

```yaml
# workflow yaml
mva_inference:
  - name:        D_hplusc
    model_path:  /eos/.../v11/best_model.pt
    features:    [dilepton_pt, lepton1_pt, ..., nSV]
    score_expr:  "softmax(out)[:, 0] / (softmax(out) * kappa).sum(axis=1)"
    kappa:       [1, 1, 1, 1, 1, 1]
    axis:        {bins: 20, start: 0, stop: 1}
```

The postprocessor reads this once, loads each model in `eval()`
mode, runs it on the sample DataFrame, and injects `D_hplusc` into
`variables_map` before `fill_histogram` is called. The existing
nominal / syst-Up / Down loops handle the rest — including lumi
scaling via change #1. One model → ~25 lumi-scaled TH1Ds per
sample, with no user-side script.

Cheap wins to bundle:
- batch-size config for GPU inference.
- skip inference when `era == "data"` unless explicitly requested.
- cache the loaded model across samples within one postprocess run.

**Impact:** MVA score becomes a first-class histogram axis. Removes
the b-hive-side inference script entirely.

### 4. Built-in combine exporter

After `save_histograms_by_process` (postprocessor.py:151-189) writes
the per-process coffea, add a new step driven by:

```yaml
combine_export:
  axis:     D_hplusc
  filename: v11_hplusc.root
  process_map:
    hplusc:   [H+c]
    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]
    tt:       [tt]
    st:       [Single Top]
    diboson:  [WW, WZ, ZZ]
    vjets:    [DY+Jets, V+Jets]
```

It reads each `<process>.coffea`, slices on the `variation` axis,
and writes `<combine_process>` / `<combine_process>_<syst>Up/Down`
TH1Ds via `uproot.writing.identify.to_TH1x` (sumw2 preserved).

**Impact:** replaces `b-hive/scripts/make_combine_histograms_v11.py`
with one workflow-config block.

### 5. Drop the dual `output_format` in the processor

`BaseProcessor.process` currently branches at base.py:179 on
`output_format ∈ {coffea, parquet}`:

- `coffea`: immediately bins events into `hist.Hist` via
  `fill_histograms`, returns histograms only.
- `parquet`: dumps per-event arrays + weight columns to a
  chunk-level parquet, no histograms.

With changes #1 and #2, the parquet path is strictly more capable
than the coffea path:

- it carries `sumw` (parquet schema metadata, change #2);
- it carries the lumi-scaled histograms in the post-step coffea
  (change #1);
- it preserves the per-event arrays needed for MVA inference (change #3).

Recommend deprecating `output_format=coffea` in a release: keep the
flag but emit a `DeprecationWarning` that points at the parquet
path. The coffea-only branch is the cause of the "parquet weights
aren't lumi-normalised, coffea histograms are" footgun that the v11
combine first-pass hit.

**Note on plotting:** dropping `output_format=coffea` does **not**
break plotting. `Plotter` (plotter.py:30, 126) consumes a
`processed_histograms[process][variable] -> hist.Hist` dict that is
built by `load_processed_histograms` (utils.py:315-323) from per-process
`.coffea` files. Those per-process files are emitted by
`save_histograms_by_process` regardless of `output_format`, and in
the parquet branch they are built from `fill_histograms_from_parquets`
output. The `.coffea` extension is just a coffea-flavored pickle of
`hist.Hist` — keep emitting them, but always built from parquet.
Nothing in `plotter.py` changes.

## Priority

| change | effort | unblocks | recommended order |
|---|---|---|---|
| 1. sumw in `<sample>.coffea` | 5 lines | b-hive consumers stop multi-YAML lookups | first |
| 2. sumw in parquet schema | 5 lines | parquet is self-normalising | first |
| 3. MVA-inference plugin | medium | drops external inference scripts | after 1+2 |
| 4. combine exporter | small | drops external TH1D writer | after 3 |
| 5. drop `output_format=coffea` | deprecation cycle | removes the parquet/coffea normalisation footgun | last |

If only **#1 and #2** ship, the combine pipeline collapses from
"lookup three YAMLs + re-derive sumw" to "open parquet, read schema,
run model, write ROOT." That's the minimum useful change. **#3** and
**#4** then convert it from b-hive scripts into reproducible
workflow-config lines, which is what "automatic" really means.
