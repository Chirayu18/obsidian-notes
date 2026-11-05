---
name: hww-combine-pipeline
description: HToWW combine pipeline — the exact scripts/paths from parquet shards to the limit (QUICKSTART-confirmed)
metadata: 
  node_type: memory
  type: project
  originSessionId: af76ec6a-a549-46b2-be18-cf006051e43e
---

The HToWW (H+c→WW) end-to-end pipeline, from the analysis repo's `QUICKSTART.md`
(repo: `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`,
run from repo root; env `micromamba activate b_hive`; outputs on EOS at
`/eos/user/c/cgupta/higgscharm/outputs/<workflow>/<year>/`):

1. **`runner.py`** (Condor) → shards `<year>/<sample>_<N>/base/*.parquet`
   (+ object-shift subdirs `base/<shift>{Up,Down}/`, + `sumw_records/`).
   `python runner.py -w <wf> -y 2022postEE --output_format parquet --eos --submit --memory 6000`
2. **`jobs_status.py`** → parquet-aware completion/resubmit. **Counts JOBS not EVENTS** —
   reports 0 missing even when xrootd read-timeouts silently drop events inside successful jobs.
   `python jobs_status.py -w <wf> -y 2022postEE --eos --output_format parquet`
3. **`run_postprocess.py --postprocess --output_format parquet`** → merges shards.
   Core merger = `analysis.postprocess.utils.merge_parquet_files(input_files, output_file)`
   (flat pyarrow concat + sumw/xsec/era metadata aggregation) via
   `merge_parquets_by_sample` + `merge_shifted_parquets_by_sample`. Produces
   `<year>/<sample>.parquet` (nominal) + `<year>/<shift>/<sample>.parquet` (12 obj shifts).
   To merge a SUBSET only, call `merge_parquet_files` directly on that sample's shards
   (don't run the full merge). **It OVERWRITES; back up first.**
4. **`scripts/mva/run_inference.py`** → the SCORED per-sample parquets combine reads:
   `<year>/[<shift>/]mva/<sample>.parquet`. Adds `mva_score_<class>` cols to the FULL df and
   writes it (`analysis/postprocess/inference.py:171-176`) → **keeps all columns** (weight_*,
   gen features, weight_negrw all pass through). `python scripts/mva/run_inference.py -w <wf> -y 2022postEE`
5. **`scripts/combine/make_combine_inputs.py`** (THE canonical combine builder; reads
   `mva/<sample>.parquet` at line 444) → ROOT templates + datacard. Fills
   `process_sample()` with `weight_nominal*scale`, argmax-routes to 6 channels
   (SR_hplusc + 5 CRs). `python scripts/combine/make_combine_inputs.py -w <wf> -y 2022postEE`
6. **`scripts/combine/drive_combine.py`** / `run_combine.sh` → text2workspace + fits.
   Limit script (b-hive): `bash /eos/user/c/cgupta/HToWW/b-hive/scripts/run_limit.sh <datacard.txt>`
   prints full / stat-only / freeze-autoMCStats r95.

**TWO combine builders exist** (don't confuse):
- `scripts/combine/make_combine_inputs.py` = **canonical/current (v11)**, QUICKSTART flow →
  `outputs/combine/v11_hplusc_v4.txt`. **USE THIS.**
- `/eos/user/c/cgupta/HToWW/b-hive/scripts/make_combine_histograms_v11_v32.py` = the parallel
  **v32** builder (13-class kappa-HCE MVA) → `b-hive/combine_inputs/v11_hplusc_v32_v9.txt`.
  `combine_full_results.sh` runs BOTH.

**Neg-weight reweighting (2026-07-17):** wired into `make_combine_inputs.py process_sample`
(`is_vjets` arg) — vjets fill becomes `|w|*weight_negrw*renorm` (yield-preserving), REPLACES
`dy_template_smooth.py` (don't smooth AND reweight). See [[Meta/claude-memory/_history/projects/HToWW/vault/hww-negweight-reweight-fix|hww-negweight-reweight-fix]] and
`Projects/HToWW/negrw-training/`.

Docs: repo `QUICKSTART.md`, `GUIDE.md`, `README.md`, `CLAUDE.md`. See [[Meta/claude-memory/_history/workflow/vault/lxplus-coffea-env|lxplus-coffea-env]].
