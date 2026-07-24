---
tags: [reference]
status: active
date: 2026-07-24
source: lxplus
---

# HToWW H+c — run the whole analysis (with negrw + native 2D c-tag SF)

End-to-end steps to reproduce the limit with **both new changes**:
1. **Negative-weight reweighting** of V+jets (arXiv:2510.16217) — lives in the processor
   (`base.py::_score_negrw`), driven by the `negrw:` block in the workflow.
2. **Native 2D c-tag SF** (`CTag2DCorrector`) — 2D pseudo-continuous PNet SF applied in
   the processor as `CMS_ctag2d_2022`, replacing the old post-hoc `apply_ctag2d_sf.py`.

Repo: `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
Workflow: `hww_combine_2dcat`  ·  Year: `2022postEE`  ·  Env: micromamba `b_hive`.

See also [[2026-07-24-systematics-master-list]], [[2026-07-19-ctag2d-full-documentation]],
combine pipeline [[hww-combine-pipeline]].

---

## What changed vs the old pipeline (so you know why steps differ)

| piece | old | new (this doc) |
|---|---|---|
| 2D c-tag SF | post-hoc `apply_ctag2d_sf.py` patched onto mva/ parquets | **native** `analysis/corrections/ctag2d.py` (CTag2DCorrector), activated by `ctagging_2d: true` in `event_weights` |
| SF file | — | registered as `ctagging_2d` in `correctionlib_files.py` |
| negrw | processor `_score_negrw`, config-only | unchanged (Jul-15 `negrw_models.joblib`, verified latest) |
| MVA | baseline model | 2D-cat model `hwwcom_multiclass_v11_2dcats` |

**Key consequence:** because the SF is now native, `CMS_ctag2d_2022Up/Down` and the
central correction are already in the parquets after step 3 — no separate SF-patching
step. The `append_onehot.py` / `rescore_2dcat.py` / `apply_ctag2d_sf.py` scripts are
**retired** for production.

---

## Steps

### 0. Grid proxy (interactive — you)
```bash
voms-proxy-init --voms cms --valid 192:00
```

### 1. (Optional) refresh fileset
`runner.py` auto-calls `fetch.py` per submission, so an explicit fetch is usually not
needed. To force it:
```bash
python3 fetch.py --workflow hww_combine_2dcat --year 2022postEE
```

### 2. Submit MC+signal to Condor
```bash
python3 runner.py --workflow hww_combine_2dcat --year 2022postEE \
        --submit --eos --output_format parquet
```
Runs the processor over all ~21 MC+signal datasets, emitting nominal + all object-shift
(JES/JER/lepton) parquet trees, with negrw and native 2D-cat SF columns baked in.

### 3. Monitor
```bash
watch condor_q
python3 jobs_status.py --workflow hww_combine_2dcat --year 2022postEE --eos
```
Resubmit any failed/held jobs (memory: step2 DRPremix OOMs → bump `-m` if needed).

### 4. Postprocess → merged parquets (with MVA labels)
```bash
python3 run_postprocess.py --workflow hww_combine_2dcat --year 2022postEE \
        --postprocess --output_format parquet --mva
```

### 5. MVA inference (2D-cat model)
```bash
B_HIVE_DIR=<bhive> python3 scripts/mva/run_inference.py \
  --workflow hww_combine_2dcat --year 2022postEE \
  --model-path <...>/HPlusCHToWW_2dcats/.../best_model.pt \
  --bhive-config HPlusCHToWW_2dcats
```
Writes `mva_score_*` into `<var>/mva/` for nominal + every shift dir.

### 6. Build combine inputs
```bash
python3 scripts/combine/make_combine_inputs.py --workflow hww_combine_2dcat --year 2022postEE
```
Fills templates per channel/process, applies the vjets negrw reweight (`|w|·g`, per-dataset
renorm) + `CMS_negrw_vjets` band, and emits every `shape_systematic` row (incl. the native
`CMS_ctag2d_2022`). Output: `outputs/combine/v11_hplusc_2dcat.{root,txt}`.

### 7. Run the limit
```bash
bash scripts/combine/run_limit.sh outputs/combine/v11_hplusc_2dcat.txt
# or run_combine.sh for the full fit/impacts
```
Expected: **r95 ≈ 1422 full / 749 stat-only / 1168 freeze-autoMCStats**.

---

## Sanity checks
- After step 3: a vjets parquet should carry `weight_negrw`, `weight_negrw_std`, and
  `weight_CMS_ctag2d_2022Up/Down`; `weight_nominal` includes the central SF.
- After step 6: the datacard should list `CMS_ctag2d_2022` and `CMS_negrw_vjets` as
  `shape` rows, and `tt` as a rateParam.
- 2D-cat routing: ~91% of signal lands in SR; SR yield larger than baseline (argmax pulls
  more tt in) — expected, documented in [[2026-07-19-ctag2d-full-documentation]].
