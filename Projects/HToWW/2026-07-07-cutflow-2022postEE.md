---
tags: [reference]
status: active
date: 2026-07-07
source: lxplus
---

# Cutflow — H+c (H→WW), 2022postEE (`base` workflow)

Weighted event counts after each selection step (MC: Σ `weight_nominal`; Data: raw
events), for the single `base` category.

**Source:** `/eos/user/c/cgupta/higgscharm/outputs/hww/2022postEE/base/cutflow_base.csv`
(+ per-sample `cutflow_base_<sample>.csv`).

Cut order: `atleast_one_goodvertex → lumimask → met_filters → trigger → met_45 →
one_ll_pair → one_muon_one_electron`.

| sample | goodvertex | lumimask | met_filters | trigger | met_45 | one_ll_pair | one_mu_one_e |
|---|---:|---:|---:|---:|---:|---:|---:|
| Data | 1.404e+09 | 1.351e+09 | 1.346e+09 | 6.137e+08 | 1.632e+08 | 1.156e+06 | 2.187e+05 |
| Total Background | 2.537e+09 | 2.537e+09 | 2.537e+09 | 4.576e+08 | 1.592e+08 | 1.357e+06 | 2.359e+05 |
| H+c | 54.88 | 54.88 | 54.88 | 20.60 | 10.47 | 2.85 | 1.49 |
| tt | 2.407e+07 | 2.407e+07 | 2.406e+07 | 5.465e+06 | 3.759e+06 | 3.555e+05 | 1.781e+05 |
| DY+Jets | 7.246e+08 | 7.246e+08 | 7.246e+08 | 6.453e+07 | 8.628e+06 | 9.010e+05 | 1.207e+04 |
| Single Top | 8.507e+06 | 8.507e+06 | 8.503e+06 | 1.229e+06 | 7.383e+05 | 3.774e+04 | 1.887e+04 |
| WW | 3.199e+06 | 3.199e+06 | 3.198e+06 | 5.906e+05 | 2.973e+05 | 2.490e+04 | 1.254e+04 |
| WZ | 1.425e+06 | 1.425e+06 | 1.425e+06 | 1.983e+05 | 9.259e+04 | 8692.72 | 1040.50 |
| ZZ | 4.397e+05 | 4.397e+05 | 4.395e+05 | 4.227e+04 | 1.278e+04 | 4673.86 | 104.74 |
| WG | 1.742e+07 | 1.742e+07 | 1.741e+07 | 1.649e+06 | 6.291e+05 | 2103.30 | 1212.86 |
| V+Jets | 1.758e+09 | 1.758e+09 | 1.757e+09 | 3.839e+08 | 1.450e+08 | 2.060e+04 | 1.087e+04 |
| ggH | 1.061e+05 | 1.061e+05 | 1.061e+05 | 2.018e+04 | 9049.52 | 1665.94 | 856.64 |
| VBF | 8974.29 | 8974.29 | 8964.68 | 2071.55 | 1280.59 | 236.90 | 118.18 |
| ggZH | 76.66 | 76.66 | 76.59 | 40.84 | 31.87 | 10.36 | 4.21 |
| ZH | 538.78 | 538.78 | 538.50 | 231.81 | 154.15 | 44.83 | 18.98 |
| WH | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ttHnonBB | 487.80 | 487.80 | 487.18 | 114.32 | 85.79 | 7.66 | 3.72 |
| ttHtoBB | 8683.51 | 8683.51 | 8674.47 | 2002.51 | 1522.78 | 132.26 | 66.18 |

## Notes

- **WH = 0** at every step — that sample had no events pass even `goodvertex` (empty /
  not produced in this fileset).
- The **trigger** step is where the [[2026-07-07-trigger-efficiency|trigger efficiency]]
  is derived (`N(trigger)/N(met_filters)`).
- 2022postEE only — 2022preEE was not run with a cutflow.

Related: [[2026-07-07-trigger-efficiency]] · [[Analysis QUICKSTART]]
