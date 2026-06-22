---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# H→WW MVA Training — Full Results

Multi-class MVA discriminant for H+c signal extraction in H→WW* analysis using the b-hive framework.

---

## Dataset

- **Data path**: `/eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/v5_finegrained_higgs/`
- **13 process classes**: hplusc, hplusb, ggH, vbf, zh, ggzh, wh, tthnonbb, tthtobb, tt, st, diboson, vjets
- **Train/test split**: 80:20 random split per process (seed=42)
- **Total events**: ~4.08M (3.26M train, 815K test)
- **Dominant classes**: tt (3.18M), Single Top (499K), ggZH (105K). Signal hplusc has only 2,257 events.

### Features (17 event-level variables)
- Kinematic: dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt
- Transverse mass: mtl1, mtl2, dilepton_mass
- Angular: delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c, delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET
- Charm tagging: cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet
- Vertex: nSV

---

## Model

- **Architecture**: SimpleMLP_MultiClass — feedforward MLP [17→128→64→32→N_classes] with BatchNorm, ReLU, Dropout
- **Optimizer**: Adam (lr=1e-3)
- **Batch size**: 1024
- **Epochs**: 30
- **Loss weighting**: Inverse-frequency class weights

---

## Training Version Summary

| Version | Classes | Loss | Key Change |
|---|---|---|---|
| v10 | 13 | Standard CE | FAILED (AUC~0.51) |
| v11 | 6 | Standard CE | Merged higgs → higgsbkg |
| v12 | 13 | Hierarchical CE | 5 groups: charm_higgs, top, h_plus_v, diboson, vjets |
| v13 | 13 | Hierarchical CE | Updated group structure |
| v15 | 13 | Hierarchical CE | Per-group λ + manual weight boosts |
| v17 | 13 | Hier CE + S/√B sig | Merged higgs group (h_plus_v → higgs) |
| v18h | 13 | Hier CE (control) | Same groups as v17, no significance loss |
| v18s | 13 | Hier CE + S/√B λ=100 | High significance loss weight |
| v18logB | 13 | Hier CE + logB λ=10 | Log-background loss |
| v19logB | 13 | Hier CE + logB λ=1 | Reduced logB weight |

---

## AUC Comparison

| Metric | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|---|---|---|---|
| hplusc_vs_all | **0.966** | 0.951 | 0.961 | 0.965 | 0.964 | 0.954 | 0.928 | 0.960 | 0.961 |
| higgs_vs_all | — | 0.847 | 0.847 | 0.842 | **0.910** | 0.909 | 0.892 | 0.905 | 0.906 |
| hplusc\|higgs | — | — | 0.858 | 0.855 | 0.853 | 0.855 | 0.809 | 0.867 | **0.870** |
| top_vs_all | — | — | 0.952 | 0.951 | 0.921 | 0.924 | 0.900 | 0.922 | — |
| Accuracy | — | — | — | — | ~15% | ~40% | ~2% | ~3% | ~4% |

---

## ROC Comparison (all versions)

![ROC hplusc vs all — all versions](plots/comparison_roc_hplusc.png)

---

## S/√B Comparison (raw P(hplusc), all versions)

![S/sqrt(B) vs efficiency](plots/comparison_sb.png)

### Quick Summary (raw P(hplusc))

| Eff | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|---|---|---|---|
| 5% | 2.79 | 2.07 | 2.79 | 2.85 | 2.08 | 2.00 | 2.06 | **2.96** | 2.81 |
| 50% | 4.39 | 3.98 | 4.09 | 4.43 | 4.61 | 4.20 | **4.69** | 4.22 | 4.46 |
| 90% | **3.41** | 2.60 | 3.09 | 3.32 | 2.97 | 2.80 | 2.33 | 3.03 | 3.08 |

---

## Per-Version Detailed Results

---

### v11 — 6-class Standard CE (best hplusc discrimination)

- **Classes**: hplusc, higgsbkg (all other higgs merged), tt, st, diboson, vjets
- **Loss**: Standard CE with inverse-frequency weights
- **Results**: hplusc_vs_all AUC = **0.966**, hplusc_vs_tt = 0.976, hplusc_vs_higgsbkg = 0.882, hplusc_vs_diboson = 0.931
- **Conclusion**: Best raw hplusc discrimination. No fine-grained higgs sub-class info. No two-step possible.

| | |
|---|---|
| ![1D P(hplusc)](plots/v11_1d_phplus.png) | ![ROC](plots/v11_roc.png) |
| ![Confusion (recall)](plots/v11_confmat_recall.png) | ![Confusion (precision)](plots/v11_confmat_precision.png) |

---

### v12 — 13-class Hierarchical CE

- **Groups**: charm_higgs=[hplusc, hplusb, ggH], top=[tt, st, tthtobb, tthnonbb], h_plus_v=[wh, zh, ggzh, vbf], diboson, vjets
- **Loss**: L_global (CE over 5 groups) + λ · L_fine (CE within fine groups)
- **Results**: hplusc_vs_all AUC = 0.951, higgs_vs_all AUC = 0.847
- **Conclusion**: Fixed v10's failure. Trade-off: -1.5% hplusc_vs_all vs v11, but gained fine-grained info.

| | |
|---|---|
| ![1D P(hplusc)](plots/v12_1d_phplus.png) | ![1D P(higgs)](plots/v12_1d_phiggs.png) |
| ![ROC hplusc](plots/v12_roc.png) | ![ROC higgs](plots/v12_roc_higgs.png) |
| ![Confusion (recall)](plots/v12_confmat_recall.png) | ![Confusion (precision)](plots/v12_confmat_precision.png) |

---

### v13 — 13-class Hierarchical CE (updated groups)

- **Groups**: Same as v12 with better group structure
- **Results**: hplusc_vs_all AUC = 0.961, higgs_vs_all AUC = 0.847

| | |
|---|---|
| ![1D P(hplusc)](plots/v13_1d_phplus.png) | ![1D P(higgs)](plots/v13_1d_phiggs.png) |
| ![ROC hplusc](plots/v13_roc.png) | ![ROC higgs](plots/v13_roc_higgs.png) |
| ![Confusion (recall)](plots/v13_confmat_recall.png) | ![Confusion (precision)](plots/v13_confmat_precision.png) |

---

### v15 — Hierarchical CE + per-group λ + boosts

- **Config changes**: charm_higgs fine λ=2.0, is_hplusc boost=2.0, charm_higgs global boost=2.0
- **Results**: hplusc_vs_all AUC = 0.965, higgs_vs_all AUC = 0.842
- **Diagnostic findings**: h_plus_v → charm_higgs leakage: 47%, ggH → vjets leakage: 14%
- **Decision**: Merge h_plus_v into higgs group for future versions

| | |
|---|---|
| ![1D P(hplusc)](plots/v15_1d_phplus.png) | ![1D P(higgs)](plots/v15_1d_phiggs.png) |
| ![ROC hplusc](plots/v15_roc.png) | ![ROC higgs](plots/v15_roc_higgs.png) |
| ![Confusion (recall)](plots/v15_confmat_recall.png) | ![Confusion (precision)](plots/v15_confmat_precision.png) |

---

### v17 — Hierarchical CE + significance loss

- **Groups (merged)**: higgs=[hplusc, hplusb, ggH, vbf, zh, ggzh, wh], top=[tt, st, tthtobb, tthnonbb], diboson, vjets
- **Loss**: L_global + 1.0 · L_fine_higgs + 1.0 · L_significance
- **Results**: hplusc_vs_all AUC = 0.964, higgs_vs_all AUC = **0.910** (big improvement from merged groups), top_vs_all AUC = 0.921 (degraded), accuracy ~12-20%
- **Conclusion**: higgs_vs_all gain came from the grouping change, not the significance loss

| | |
|---|---|
| ![1D P(hplusc)](plots/v17_1d_phplus.png) | ![1D P(higgs)](plots/v17_1d_phiggs.png) |
| ![ROC hplusc](plots/v17_roc.png) | ![ROC higgs](plots/v17_roc_higgs.png) |
| ![Confusion (recall)](plots/v17_confmat_recall.png) | ![Confusion (precision)](plots/v17_confmat_precision.png) |

---

### v18h — Hierarchical CE (control, no significance loss)

- **Loss**: L_global + 2.0 · L_fine_higgs (no significance term)
- **Results**: hplusc_vs_all AUC = 0.954, higgs_vs_all AUC = 0.909, hplusc_vs_other_higgs AUC = 0.855, top_vs_all AUC = 0.924, vjets_vs_all AUC = 0.969, diboson_vs_all AUC = 0.837, accuracy ~40%
- **Healthiest outputs** — good calibration, fine-grained sub-class info

| | |
|---|---|
| ![1D P(hplusc)](plots/v18h_1d_phplus.png) | ![1D P(higgs)](plots/v18h_1d_phiggs.png) |
| ![ROC hplusc](plots/v18h_roc.png) | ![ROC higgs](plots/v18h_roc_higgs.png) |
| ![Confusion (recall)](plots/v18h_confmat_recall.png) | ![Confusion (precision)](plots/v18h_confmat_precision.png) |

---

### v18s — S/√B significance loss λ=100

- **Loss**: L_global + 2.0 · L_fine_higgs + 100.0 · (-S/√B)
- **Kappa mode**: clamp (κ = max(0, cos_sim))
- **Results**: hplusc_vs_all AUC = 0.928 (lowest), higgs_vs_all AUC = 0.892, accuracy ~2%
- **Kappa collapse**: 7/12 kappas went negative → clamped to 0. Only zh, ggzh, tthtobb, tt, wh retained positive kappas.
- **Conclusion**: Significance loss at high λ destroys CE-based class separation. High S/√B at 30-50% is an artifact of ROC reshaping.

| | |
|---|---|
| ![1D P(hplusc)](plots/v18s_1d_phplus.png) | ![1D P(higgs)](plots/v18s_1d_phiggs.png) |
| ![ROC hplusc](plots/v18s_roc.png) | ![ROC higgs](plots/v18s_roc_higgs.png) |
| ![Confusion (recall)](plots/v18s_confmat_recall.png) | ![Confusion (precision)](plots/v18s_confmat_precision.png) |

---

### v18logB — log(B) loss λ=10

- **Loss**: L_global + 2.0 · L_fine_higgs + 10.0 · log(B)
- **Kappa mode**: smooth (κ = (1+cos_sim)/2)
- **Results**: hplusc_vs_all AUC = 0.960, higgs_vs_all AUC = 0.905, hplusc_vs_other_higgs AUC = 0.867, accuracy ~3%
- **Kappa behavior**: All 12 kappas positive (0.20–0.95). No collapse, but all pushed high.
- **Known issue**: log(B) → -∞ as B → 0. Fix: use log(1+B).

| | |
|---|---|
| ![1D P(hplusc)](plots/v18logB_1d_phplus.png) | ![1D P(higgs)](plots/v18logB_1d_phiggs.png) |
| ![ROC hplusc](plots/v18logB_roc.png) | ![ROC higgs](plots/v18logB_roc_higgs.png) |
| ![Confusion (recall)](plots/v18logB_confmat_recall.png) | ![Confusion (precision)](plots/v18logB_confmat_precision.png) |

---

### v19logB — log(B) loss λ=1

- **Loss**: L_global + 2.0 · L_fine_higgs + 1.0 · log(B)
- **Kappa mode**: smooth (κ = (1+cos_sim)/2)
- **Results**: hplusc_vs_all AUC = **0.961** (best 13-class), higgs_vs_all AUC = 0.906, hplusc_vs_other_higgs AUC = **0.870** (best), accuracy ~4%
- **Kappa behavior**: More spread than v18logB (0.15–0.90), but still all positive.

| | |
|---|---|
| ![1D P(hplusc)](plots/v19logB_1d_phplus.png) | ![1D P(higgs)](plots/v19logB_1d_phiggs.png) |
| ![ROC hplusc](plots/v19logB_roc.png) | ![ROC higgs](plots/v19logB_roc_higgs.png) |
| ![Confusion (recall)](plots/v19logB_confmat_recall.png) | ![Confusion (precision)](plots/v19logB_confmat_precision.png) |

---

## Kappa Values from Model Weights

Kappas derived from cosine similarity of final linear layer weight vectors: cos_sim(W_hplusc, W_j).
Two mappings: **clamp** = max(0, cos_sim), **smooth** = (1+cos_sim)/2.

### Raw cosine similarity

| Class | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|
| hplusb | 0.714 | -0.000 | 0.931 | 0.879 |
| ggH | 0.793 | -0.001 | 0.952 | 0.896 |
| vbf | 0.767 | -0.000 | 0.949 | 0.894 |
| zh | 0.476 | 0.496 | 0.912 | 0.872 |
| ggzh | 0.087 | 0.526 | 0.802 | 0.685 |
| wh | 0.096 | -0.269 | 0.853 | 0.837 |
| tthnonbb | -0.029 | -0.251 | 0.403 | 0.155 |
| tthtobb | -0.113 | 0.558 | 0.690 | 0.263 |
| tt | -0.048 | 0.229 | 0.309 | 0.548 |
| st | -0.247 | -0.354 | 0.202 | 0.560 |
| diboson | -0.226 | -0.297 | 0.848 | 0.898 |
| vjets | 0.050 | -0.042 | 0.813 | 0.715 |

**Key observations**:
- **v18s**: 7/12 negative → clamp zeroes them → acts as feature selector
- **v18h**: 5/12 negative → mixed behavior. Smooth works better.
- **logB versions**: All positive → clamp = cos_sim. All pushed high → κD ≈ P(hplusc)

### Clamp vs smooth kappas
- **v18s: clamp wins** — collapsed negative kappas act as feature selectors
- **v18h: smooth wins** — negative kappas still carry ordering info, (1+cos)/2 preserves it
- **logB versions: identical** — all cos_sim > 0

---

## S/√B Detailed Comparison

All S/√B values use **raw event counts** (no inverse-frequency weighting).
Signal = hplusc (2,257 events), Background = all other classes (4,074,257 events).

### Single-step P(hplusc) — All versions

| Eff | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|---|---|---|---|
| 5% | 2.79 | 2.07 | 2.79 | 2.85 | 2.08 | 2.00 | 2.06 | **2.96** | 2.81 |
| 10% | 3.41 | 2.41 | 3.36 | 3.53 | 2.71 | 2.68 | 2.78 | **3.69** | 3.53 |
| 20% | 4.05 | 3.20 | 3.46 | 3.95 | 3.60 | 3.36 | 3.77 | 4.05 | **4.14** |
| 30% | 4.26 | 3.64 | 3.46 | 4.04 | 4.14 | 3.82 | **4.37** | 4.17 | 4.23 |
| 50% | 4.39 | 3.98 | 4.09 | 4.43 | 4.61 | 4.20 | **4.69** | 4.22 | 4.46 |
| 70% | 4.29 | 3.60 | 4.13 | 4.31 | **4.46** | 3.87 | 4.02 | 4.09 | 4.16 |
| 90% | **3.41** | 2.60 | 3.09 | 3.32 | 2.97 | 2.80 | 2.33 | 3.03 | 3.08 |

### Single-step κD smooth (κ = (1+cos)/2)

| Eff | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|
| 5% | 2.03 | 2.06 | 2.92 | 2.84 |
| 10% | 2.74 | 2.78 | 3.68 | 3.51 |
| 20% | 3.47 | 3.78 | 4.02 | 4.11 |
| 30% | 3.91 | **4.37** | 4.10 | 4.16 |
| 50% | 4.31 | **4.70** | 4.15 | 4.33 |
| 70% | 3.92 | 4.05 | 4.06 | 4.08 |
| 90% | 2.84 | 2.34 | 3.00 | 3.06 |

### Single-step κD clamp (κ = max(0, cos))

| Eff | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|
| 5% | 1.71 | **3.51** | 2.85 | 2.80 |
| 10% | 2.42 | **3.51** | 3.65 | 3.44 |
| 20% | 3.25 | 3.85 | 3.97 | **4.07** |
| 30% | 3.79 | 4.34 | 4.01 | 4.09 |
| 50% | 4.17 | **4.74** | 4.08 | 4.17 |
| 70% | 3.89 | 4.11 | 4.00 | 3.98 |
| 90% | 2.57 | 2.43 | 2.95 | 3.00 |

Note: For logB versions, clamp = cos_sim (all kappas positive).

### Two-step: P(higgs) → P(hplusc|higgs)

v11 excluded (6-class, no meaningful P(higgs) grouping).

| h_eff | Eff | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|
| 70% | 5% | 2.44 | 2.39 | 3.18 | 3.07 |
| 70% | 10% | 3.11 | 3.02 | 3.38 | 3.39 |
| 70% | 20% | 3.71 | 3.88 | 3.69 | 3.83 |
| 70% | 30% | 4.04 | **4.47** | 3.80 | 3.95 |
| 70% | 50% | 4.15 | **4.57** | 3.60 | 3.68 |
| 80% | 5% | 2.28 | 2.33 | 3.11 | 2.88 |
| 80% | 10% | 2.92 | 2.96 | 3.49 | 3.30 |
| 80% | 20% | 3.58 | 3.88 | 3.77 | 3.81 |
| 80% | 30% | 3.98 | **4.49** | 3.84 | 3.96 |
| 80% | 50% | 4.21 | **4.65** | 4.03 | 4.16 |
| 90% | 5% | 1.96 | 2.45 | 2.70 | 2.32 |
| 90% | 10% | 2.71 | 2.99 | 3.15 | 2.86 |
| 90% | 20% | 3.43 | **3.90** | 3.36 | 3.25 |
| 90% | 30% | 3.83 | **4.46** | 3.53 | 3.49 |
| 90% | 50% | 4.16 | **4.73** | 3.74 | 3.84 |
| 90% | 70% | 3.88 | 4.07 | 3.66 | 3.75 |
| 90% | 90% | 2.76 | 2.29 | 2.71 | 2.66 |
| 95% | 50% | 4.14 | **4.73** | 3.60 | 3.64 |
| 95% | 70% | 3.88 | 4.13 | 3.55 | 3.63 |
| 95% | 90% | 2.84 | 2.52 | 2.76 | 2.77 |

### Two-step: P(higgs) → κD smooth (κ = (1+cos)/2)

| h_eff | Eff | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|
| 70% | 5% | 2.33 | 2.43 | 3.25 | 3.08 |
| 70% | 10% | 2.94 | 3.04 | 3.59 | 3.48 |
| 70% | 20% | 3.51 | 3.93 | 3.66 | 3.82 |
| 70% | 30% | 3.99 | **4.45** | 3.80 | 3.92 |
| 70% | 50% | **4.33** | 4.55 | 3.77 | 3.84 |
| 80% | 5% | 2.33 | 2.41 | 3.25 | 3.19 |
| 80% | 10% | 2.93 | 3.00 | 3.80 | 3.66 |
| 80% | 20% | 3.50 | 3.93 | 4.06 | 4.11 |
| 80% | 30% | 3.98 | **4.47** | 4.08 | 4.17 |
| 80% | 50% | **4.33** | **4.65** | 4.22 | 4.36 |
| 90% | 5% | 2.32 | 2.50 | 3.22 | 3.16 |
| 90% | 10% | 2.96 | 3.01 | 3.80 | 3.67 |
| 90% | 20% | 3.50 | 3.93 | **4.13** | **4.15** |
| 90% | 30% | 3.98 | **4.43** | 4.13 | 4.20 |
| 90% | 50% | **4.33** | **4.69** | 4.20 | 4.36 |
| 90% | 70% | 3.99 | 4.04 | 4.06 | 4.08 |
| 90% | 90% | 2.96 | 2.24 | 3.03 | 3.01 |
| 95% | 20% | 3.50 | 3.93 | 4.11 | **4.16** |
| 95% | 30% | 3.98 | **4.46** | 4.12 | 4.20 |
| 95% | 50% | **4.34** | **4.69** | 4.19 | 4.36 |
| 95% | 70% | 3.99 | 4.09 | 4.06 | 4.10 |
| 95% | 90% | 3.05 | 2.52 | 3.09 | 3.18 |

### Two-step: P(higgs) → κD clamp (κ = max(0, cos))

| h_eff | Eff | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|
| 80% | 20% | 3.50 | 3.97 | 4.02 | 4.08 |
| 80% | 30% | 3.97 | **4.46** | 3.99 | 4.08 |
| 80% | 50% | **4.26** | **4.66** | 4.15 | 4.21 |
| 90% | 20% | 3.39 | 3.97 | 4.07 | 4.06 |
| 90% | 30% | 3.90 | **4.45** | 4.04 | 4.08 |
| 90% | 50% | 4.23 | **4.72** | 4.10 | 4.18 |
| 90% | 70% | 3.93 | 4.07 | 3.99 | 3.97 |
| 90% | 90% | 2.73 | 2.31 | 3.00 | 2.95 |
| 95% | 50% | 4.23 | **4.73** | 4.10 | 4.18 |
| 95% | 70% | 3.95 | 4.17 | 3.99 | 4.02 |
| 95% | 90% | 2.77 | 2.57 | 3.05 | 3.15 |

Note: For logB versions clamp = cos_sim (identical results).

### Best S/√B per version (best method at each efficiency)

Note: v12, v13, v15, v17 use raw P(hplusc) only (no kappa discriminant or two-step). v11, v18h/s, v18/v19logB use best method (raw, κD, or two-step).

| Eff | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB | **Winner** |
|---|---|---|---|---|---|---|---|---|---|---|
| 5% | 2.79 | 2.07 | 2.79 | 2.85 | 2.08 | 2.44 | 2.50 | **3.26** | 3.19 | v18logB |
| 10% | 3.41 | 2.41 | 3.36 | 3.53 | 2.71 | 3.11 | 3.04 | **3.81** | 3.67 | v18logB |
| 20% | 4.05 | 3.20 | 3.46 | 3.95 | 3.60 | 3.71 | 3.93 | 4.13 | **4.16** | v19logB |
| 30% | 4.26 | 3.64 | 3.46 | 4.04 | 4.14 | 4.04 | **4.49** | 4.17 | 4.23 | v18s |
| 50% | 4.39 | 3.98 | 4.09 | 4.43 | 4.61 | 4.34 | **4.73** | 4.22 | 4.46 | v18s |
| 70% | 4.29 | 3.60 | 4.13 | 4.31 | **4.46** | 4.01 | 4.13 | 4.09 | 4.16 | v17 |
| 90% | **3.41** | 2.60 | 3.09 | 3.32 | 2.97 | 3.05 | 2.52 | 3.09 | 3.18 | v11 |

### Winning method at each efficiency

| Eff | v11 | v18h | v18s | v18logB | v19logB |
|---|---|---|---|---|---|
| 5% | P(hplusc) | 2s h70%→P(c\|h) | 2s h90%→κD smooth | 2s h95%→κD smooth | 2s h80%→κD smooth |
| 10% | P(hplusc) | 2s h70%→P(c\|h) | 2s h70%→κD smooth | 2s h95%→κD smooth | 2s h90%→κD smooth |
| 20% | P(hplusc) | 2s h70%→P(c\|h) | 2s h70%→κD smooth | 2s h90%→κD smooth | 2s h95%→κD smooth |
| 30% | P(hplusc) | 2s h70%→P(c\|h) | 2s h80%→P(c\|h) | P(hplusc) | P(hplusc) |
| 50% | P(hplusc) | 2s h95%→κD smooth | 2s h95%→P(c\|h) | 2s h80%→κD smooth | P(hplusc) |
| 70% | P(hplusc) | 2s h80%→κD smooth | 2s h95%→P(c\|h) | P(hplusc) | P(hplusc) |
| 90% | P(hplusc) | 2s h95%→κD smooth | 2s h95%→P(c\|h) | 2s h95%→κD smooth | 2s h95%→κD smooth |

---

## Post-Training Kappa Optimization

### Method
Optimize kappas post-training via **differential evolution** to maximize S/√B at each target efficiency WP. Each WP gets its own optimal κ vector — no gradient conflicts.

- Background subsampled to 100k events (with scale factor) for speed
- Bounds: κ ∈ [0, 5] per class
- maxiter=20, popsize=15

### Results: Versions with optimized kappas vs raw P(hplusc)

Post-training kappa optimization was run for v11, v18h, v18s, v18logB, v19logB. Versions v12–v17 show raw P(hplusc) for comparison.

| Eff | v11 raw | v11+opt κ | v12 | v13 | v15 | v17 | v18h+opt κ | v18s+opt κ | v18logB+opt κ | v19logB+opt κ |
|---|---|---|---|---|---|---|---|---|---|---|
| 5% | 2.79 | 2.41 | 2.07 | 2.79 | 2.85 | 2.08 | 2.46 | 2.18 | 3.01 | **3.03** |
| 10% | 3.41 | 3.29 | 2.41 | 3.36 | 3.53 | 2.71 | 2.99 | 2.94 | **3.77** | 3.70 |
| 20% | 4.05 | 4.12 | 3.20 | 3.46 | 3.95 | 3.60 | 3.74 | 3.81 | 4.42 | **4.52** |
| 30% | 4.26 | 4.57 | 3.64 | 3.46 | 4.04 | 4.14 | 4.24 | 4.38 | 4.80 | **4.80** |
| 50% | 4.39 | 4.82 | 3.98 | 4.09 | 4.43 | 4.61 | 4.67 | 4.73 | 4.91 | **5.12** |
| 70% | 4.29 | 4.66 | 3.60 | 4.13 | 4.31 | 4.46 | 4.39 | 4.14 | 4.65 | **4.68** |
| 90% | 3.41 | 3.68 | 2.60 | 3.09 | 3.32 | 2.97 | 3.33 | 2.65 | 3.41 | **3.47** |

**v19logB + post-training kappa optimization wins at nearly every WP**, peak S/√B = 5.12 at 50% eff (+17% over v11 raw).

**v11 + opt κ** also improves significantly (+7-14% over raw v11), reaching 4.82 at 50% eff. This shows kappa optimization helps even for the 6-class model.

v11 optimal kappas (50% eff): tt=4.94, st=4.92 (high — suppress dominant bkg), higgsbkg=0.55, diboson=0.38, vjets=0.12 (low — less dangerous).

### Optimized Kappa Values (representative, 50% eff)

**v19logB**: High κ: tt (~3.5), st (~2.8). Medium: vjets (~1.5), diboson (~1.2). Low: higgs sub-classes (~0.1–0.5).

**v18h**: Similar pattern — tt and st get highest kappas.

### Abundance–Kappa Correlation

| Version | corr(log_count, avg_κ_opt) | corr(cos_sim, avg_κ_opt) |
|---|---|---|
| v19logB | **+0.716** (strong) | -0.71 (anti-correlated) |
| v18h | **+0.431** (moderate) | -0.02 (none) |

Optimal κ ∝ class abundance. Abundant backgrounds (tt: 3.18M, st: 499k) need higher κ to suppress them in S/√B.

### Why In-Training Kappas Fail

The logB loss uses **inverse-frequency weighting** in B: `w_i = 1/count(class_i)`. This equalizes all classes. But S/√B with raw counts wants κ ∝ count(class_i) — the opposite. Post-training optimization directly optimizes S/√B with raw counts, finding the correct abundance scaling.

---

## Key Findings

### 1. Hierarchical loss rescues 13-class training
Flat CE on 13 classes (v10) fails completely (AUC~0.51). Hierarchical CE (L_global + L_fine) enables 13-class training with competitive AUCs.

### 2. Group structure matters more than loss engineering
Merging h_plus_v into higgs (v17/v18) boosted higgs_vs_all from 0.84 → 0.91. This came entirely from the grouping change, not from the significance loss.

### 3. In-training significance losses have fundamental kappa problems

**S/√B loss (v18s)**: Kappas collapse to 0 via "Path B" — gradient pushes weight vectors apart → cos_sim goes negative → clamp zeros κ → denominator shrinks → D becomes binary. 7/12 kappas collapsed. AUC dropped to 0.928, accuracy to 2%.

**log(B) loss (v18logB, v19logB)**: Kappas converge to ~1. log(B) gradient pushes κ UP but nothing pushes any κ DOWN, so all race toward 1. When all κ ≈ 1: D = P(hplusc) / (P(hplusc) + Σ P_j) ≈ P(hplusc). Kappas become useless.

**Additional**: log(B) → -∞ as B → 0. Loss unbounded below. Fix: log(1+B).

### 4. v18s's high S/√B is misleading
Despite lowest AUC (0.928) and 2% accuracy, v18s peaks at S/√B=4.73 (50% eff). The significance loss concentrated all power at 30-50%, destroying tight WPs (2.06 at 5%) and loose WPs (2.33 at 90%). This is ROC reshaping, not genuine improvement.

### 5. v19logB is the best 13-class model overall
Best 13-class AUC (0.961), best hplusc|higgs AUC (0.870), consistent S/√B. logB with λ=1 provides gentle refinement without destroying CE separation.

### 6. Two-step helps at tight WPs, not loose WPs
At 5-10% eff, 2-step P(higgs)→κD(smooth) gives 3.19-3.81 for logB — better than single-step. At 30-50%, single-step P(hplusc) is already optimal.

### 7. v11 remains most robust for pure hplusc discrimination
v11 (AUC=0.966) has highest AUC, best accuracy, wins at 70-90% eff. 13-class setup costs ~0.5-1.2% on hplusc_vs_all AUC.

---

## Loss Function Implementations

### Hierarchical Cross-Entropy
```
L = L_CE_global(group probs, group truth) + Σ_g λ_g · L_CE_fine(sub-class probs within group g)
```
- Global CE: softmax over summed group logits, weighted by inverse-frequency
- Fine CE: per-group softmax over sub-class logits, only for events in that group

### Significance Loss (-S/√B) — NOT RECOMMENDED
```
L_sig = -S/√(B+ε)
```
- D = P(hplusc) / (P(hplusc) + Σ κ_j · P_j), κ_j = max(0, cos_sim(W_hplusc, W_j))
- Problem: kappas collapse to 0, discriminant becomes binary

### log(B) Loss — NOT RECOMMENDED
```
L = L_hier_CE + λ · log(Σ_bkg w_i · D_i + ε)
```
- κ_j = (1 + cos_sim) / 2, w_i = 1/count(class_i)
- Problem 1: All kappas → 1, making κD ≈ P(hplusc)
- Problem 2: log(B) → -∞ (loss unbounded below)

### Kappa Discriminant (post-training)
```
D = P_signal / (P_signal + Σ κ_j · P_j)
```
Kappas optimized via differential evolution per WP.

---

## Recommended Approach

**v19logB + post-training kappa optimization via differential evolution.**

1. Train with hierarchical CE + logB(λ=1) for best 13-class probabilities
2. Optimize kappas post-training per working point (no gradient conflicts)
3. Use two-step P(higgs)→κD at tight WPs (5-10% eff)
4. Fall back to v11 if fine-grained higgs info not needed

---

## File Locations

| File | Path |
|---|---|
| b-hive repo | `/eos/home-c/cgupta/HToWW/b-hive/` |
| Training data | `/eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/v5_finegrained_higgs/` |
| Training output | `/eos/user/c/cgupta/EPR_task/b-hive/output/` |
| Hierarchical loss | `utils/loss/HierarchicalCrossEntropyLoss.py` |
| Loss loader | `utils/loss/LossFunctionLoader.py` |
| Weight computation | `utils/weighting/batches.py` |
| Training task | `tasks/training.py` |
| Config (hierarchical) | `config/HPlusCHToWW_hierarchical.yml` |
| Config (sig loss) | `config/HPlusCHToWW_sig.yml` |
| Config (logB loss) | `config/HPlusCHToWW_logB.yml` |
| Config (6-class) | `config/HPlusCHToWW_multiclass.yml` |

## Analysis Scripts

| Script | Location | Purpose |
|---|---|---|
| `plot_all_mva_versions.py` | higgscharm/scripts/ | Generate all plots for all versions |
| `run_all_mva_inference.py` | higgscharm/scripts/ | Batch inference runner |
| `compare_significance.py` | b-hive/scripts/ | S/√B with kappa optimization |
| `hierarchical_significance.py` | b-hive/scripts/ | Two-step hierarchical analysis |
| `kappa_from_model.py` | b-hive/scripts/ | Extract kappas from checkpoints |
| `plot_mva.py` | higgscharm/scripts/ | Flat-class MVA score plots |
| `plot_mva_hierarchical.py` | higgscharm/scripts/ | Hierarchical MVA score plots |
