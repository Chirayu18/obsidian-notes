---
tags: [reference, plot, production]
status: active
date: 2026-11-13
source: laptop
evidence: executed-and-output-checked
---

# A four-era TRAIN-based expected limits

**First new A blind expected limits are computed:** median **493.1641 stat-only**, **505.3711 with configured rate nuisances**. Both use the new held-out fivefold models, current negrw v2, one merged SR plus five argmax CRs per era, finite-MC autoMCStats and a shared freely fitted tt rate. They are **not full-systematics results**, not the planned two-Nc-jet-SR result, and not a definitive A/B flavour-scheme comparison. No observed-data result was calculated.

Follows [[2026-11-12-train-card-scorer-implemented]], [[2026-11-13-a-performance-plots]] and the interpretation in [[Projects/HToWW/talks/2026-11-13-ab-physics-comparison-slide-decision]]. Earlier statements that A is waiting for export or has no limit are historical snapshots, superseded by this result boundary.

## Expected95%CL upper limits on r

r scales the current workflow's reference H+c prediction. Quantiles below are the expected-limit distribution, not parameter-fit errors.

| Card |2.5%|16%|Median|84%|97.5%|
|---|---:|---:|---:|---:|---:|
|Stat-only|265.8463|354.6423|**493.1641**|687.7756|919.2838|
|Stat + configured lnN rates|270.4525|362.2176|**505.3711**|710.8430|965.7158|

Source: `/afs/cern.ch/user/c/cgupta/bhive_prod_20261112_sol/A/limits_20261113/{stat_only,rate_systematics}/limit.log` and respective `higgsCombine_A_<mode>.AsymptoticLimits.mH125.09.root`. Read every ROOT limit-tree quantile back with uproot: exactly five positive, finite, ordered expected quantiles; no observed entry. Full precision saved in `limits_20261113/summary.json` and local `framework/figures/2026-11-13-A-limits/summary.json`. Combine v10.6.0; no warnings/errors appeared in the saved completed limit logs.

## Evidence chain

| Gate | Saved evidence / result |
|---|---|
|A training completed|DAG9706925 all5nodes successful02:39:27CET; each completed training record's best checkpoint checksum matched the real checkpoint |
|Full held-out export comparison|`A/export_20261113/export_validation.json`; per-fold counts1390662/1392167/1393887/1390880/1391712. Maximum absolute ONNX−PyTorch differences1.5199184e−6/7.3015690e−7/1.3411045e−6/1.6093254e−6/2.1159649e−6; all below1e−5 |
|Strict production registration|`A/registered_20261113/meta.yaml`, diagnostic_only=false; registration log records success. Model manifest SHA256852cf79ce79cba7f9d5efecf8ab427267b1e97115c1cbf0fd27d514853dbe5f7; four eras, exact feature/class order, seeds/config/LZ4-fix provenance and split identity retained |
|Scoring|`A/cards_20261113/commands.json`, four logs and exit_codes.json: all0. Total2437MCmarkers/22613originalparquets/6959308selectedrows; complete file coverage/current frozen hashes checked by the new scorer |
|Nominal negrw|Actual model bytes hashed and rescored from retained generator inputs, SHA256af53567ccfeddeef94c1fa62b3a6ed3c1285937919ced3f7705c565b819155cb; selected sample/era yield preserved after accumulated reweighting |
|Card contents|All four stat-only cards: no explicit lnN/shape nuisance rows, six autoMCStats lines and free rate_tt. Configured-rate variants: eight lnN rows per era, no modelling shape rows; identical nominal ROOT templates from one scoring pass |
|Fit|Established CMSSW14_1_0_pre4 environment; combineCards.py → text2workspace.py → `combine -M AsymptoticLimits workspace.root -t -1 --run blind --mass125.09 --rMin0 --rMax100000 -n _A_<mode>` (actual arguments separated normally). Both commands exited0; limits far inside upper r bound |

Analysis local commit5b25295. No workflow/correction/training input or recipe modified during export, registration, scoring or fitting. No push. Full-result physics review is not claimed by software/checksum/card validation alone.

## Final-template floor audit

Saved `A/cards_20261113/floor_audit.json` compares each ROOT histogram to normalized **pre-floor** moments in its `nominal_accumulator.coffea`. Verified stored counts equal max(raw,1e−6) and sumw2 is unchanged. All140floored bins across the four eras include zero/tiny-positive bins; **11bins were genuinely negative**.

|Era|Negative bins|Sum of negative contents|Total yield added by flooring all processes/channels|
|---|---:|---:|---:|
|2022preEE|3|−0.3581731|0.3582111|
|2022postEE|5|−0.0002782|0.0003082|
|2023preBPix|0|0|0.0000340|
|2023postBPix|3|−1.0787797|1.0788167|

Largest negative contributions are V+jets in preEE CR_st (−0.3580781) and postBPix CR_tt (−1.0787103); the other negative entries are tiny H+c/Higgs-background CR bins. This records the existing approved final-template policy; no alternative floor or claimed fit-impact study was introduced.

## Slide-ready plot

- **Date:**2026-11-13.
- **Description:**A combined expected95%CL upper-limit medians and68%/95%expected bands for stat-only and stat+configured-rate variants. Explicitly labels blind Asimov, merged SR, free tt/autoMCStats and exclusion of modelling shape uncertainties.
- **Path:**`/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_limits_20261113/A_expected_limits.png`.
- **Link:**[CERNBox limit plot](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_limits_20261113/A_expected_limits.png).

Local PNG retained/gitignored under `framework/figures/2026-11-13-A-limits/`; numerical summary/render source recorded there and on EOS. No PNG/PDF committed. Keeper owns the actual deck. Additional cheap per-era/per-year blind fits from these same checked templates were started under `limits_20261113/<mode>/components/`; their results are not claimed in this snapshot.

## Interpretation boundary for the talk

Use **“First corrected A statistical-sensitivity check:493”**, not “full-systematics limit493”. The rate-only505variant still omits A's3FS/4FS shape, scale/PDF shape/acceptance, detector shifts and negrw method shape. Configured rate terms retain the existing provisional merged-process assumptions; no new official theory treatment is established. The old October691 and its old-card scale diagnostics remain separate historical results. This output does not quantify the benefit of B stitching; B needs its own completed/checked models and ultimately a consistent systematic comparison. G3 fit-bin closure remains scientifically open without undoing Chirayu's explicit v2 adoption decision.
