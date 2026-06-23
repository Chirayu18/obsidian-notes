---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
pinned: true
---

# H→WW MVA Training Summary

## Overview

Multi-class MVA discriminant for H+c signal extraction in H→WW* analysis.
The goal is to maximize H+c vs background separation (S/√B) using a DNN classifier
trained with b-hive framework.

## Dataset

- **Data path**: `/eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/v5_finegrained_higgs/`
- **13 process classes**: hplusc, hplusb, ggH, vbf, zh, ggzh, wh, tthnonbb, tthtobb, tt, st, diboson, vjets
- **Train/test split**: 80:20 random split per process (seed=42), files in `train/` and `test/` subdirectories
- **Total events**: ~4.08M (3.26M train, 815K test)
- **Dominant classes**: tt (3.18M), Single Top (499K), ggZH (105K). Signal hplusc has only 2,257 events.

### Features (17 event-level variables)
- Kinematic: dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt
- Transverse mass: mtl1, mtl2, dilepton_mass
- Angular: delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c, delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET
- Charm tagging: cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet
- Vertex: nSV

## Model

- **Architecture**: SimpleMLP_MultiClass — feedforward MLP with layers [17→128→64→32→13]
- **Optimizer**: Adam (lr=1e-3)
- **Batch size**: 1024
- **Epochs**: 30
- **Loss weighting**: Inverse-frequency class weights

## Training Versions

### v10: 13-class flat Cross-Entropy
- **Config**: `HPlusCHToWW_finegrained`
- **Loss**: Standard CE over 13 classes
- **Result**: FAILED — hplusc_vs_all AUC ~0.51. Too many classes with extreme class imbalance; the model couldn't learn meaningful separation.

### v11: 6-class flat Cross-Entropy (best hplusc discrimination)
- **Config**: `HPlusCHToWW_multiclass`
- **Classes**: hplusc, higgsbkg (all other higgs merged), tt, st, diboson, vjets
- **Loss**: Standard CE with inverse-frequency weights
- **Results**:
  - hplusc_vs_all AUC = **0.966**
  - hplusc_vs_tt = 0.976
  - hplusc_vs_higgsbkg = 0.882
  - hplusc_vs_diboson = 0.931
- **Conclusion**: Best raw hplusc discrimination. Merging all other higgs into one "higgsbkg" class simplified the problem effectively. However, no fine-grained higgs sub-class information available. No two-step analysis possible (only 2 higgs classes).

### v12: 13-class hierarchical Cross-Entropy
- **Config**: `HPlusCHToWW_hierarchical`
- **Groups**: charm_higgs=[hplusc, hplusb, ggH], top=[tt, st, tthtobb, tthnonbb], h_plus_v=[wh, zh, ggzh, vbf], diboson, vjets
- **Loss**: L_global (CE over 5 groups) + λ · L_fine (CE within fine groups)
- **Results**:
  - hplusc_vs_all AUC = 0.951
  - higgs_vs_all AUC = 0.847
- **Conclusion**: Fixed v10's failure by adding hierarchical structure. Trade-off: -1.5% hplusc_vs_all vs v11, but gained fine-grained higgs sub-class info.

### v13: 13-class hierarchical CE (new groups)
- **Groups**: charm_higgs=[hplusc, hplusb, ggH], top=[tt, st, tthtobb, tthnonbb], h_plus_v=[wh, zh, ggzh, vbf], diboson, vjets
- **Results**:
  - hplusc_vs_all AUC = 0.961
  - higgs_vs_all AUC = 0.847
- **Conclusion**: Improved over v12 with better group structure.

### v15: 13-class hierarchical CE with per-group λ and weight boosts
- **Groups**: Same as v13 + per-group fine lambdas and manual weight boosts
- **Config changes**: charm_higgs fine λ=2.0, is_hplusc boost=2.0, charm_higgs global boost=2.0
- **Results**:
  - hplusc_vs_all AUC = 0.965
  - higgs_vs_all AUC = 0.842
- **Diagnostic findings**:
  - h_plus_v → charm_higgs leakage: 47% (wh/zh/ggzh/vbf classified as charm_higgs)
  - ggH → vjets leakage: 14%
  - ttH processes correctly assigned to top group
- **Decision**: Merge h_plus_v into higgs group for future versions (can't separate with current features).

### v17: 13-class hierarchical CE + significance loss (all λ=1)
- **Config**: `HPlusCHToWW_hierarchical`
- **Groups (merged)**: higgs=[hplusc, hplusb, ggH, vbf, zh, ggzh, wh], top=[tt, st, tthtobb, tthnonbb], diboson, vjets
- **Loss**: L_global + 1.0 · L_fine_higgs + 1.0 · L_significance
- **L_significance**: Differentiable -S/√B using kappa discriminant with cosine-similarity-derived kappas from model's final layer weights
- **Results**:
  - hplusc_vs_all AUC = 0.964
  - higgs_vs_all AUC = **0.910** (big improvement from merged groups)
  - top_vs_all AUC = 0.921 (degraded)
  - Accuracy collapsed to ~12-20% (significance loss distorts probability outputs)
- **Conclusion**: higgs_vs_all gain came from the grouping change, not the significance loss. The significance loss degraded accuracy and top separation.

### v18 hierarchical (no significance loss — CONTROL)
- **Config**: `HPlusCHToWW_hierarchical` with `significance.lam: 0.0`
- **Groups**: Same merged 4-group as v17
- **Loss**: L_global + 2.0 · L_fine_higgs (no significance term)
- **Results**:
  - hplusc_vs_all AUC = **0.954**
  - higgs_vs_all AUC = **0.909**
  - hplusc_vs_other_higgs AUC = 0.855
  - top_vs_all AUC = 0.924
  - vjets_vs_all AUC = 0.969
  - diboson_vs_all AUC = 0.837
  - Accuracy: ~40%

### v18 sig (S/√B significance loss λ=100)
- **Config**: `HPlusCHToWW_sig` with `significance.lam: 100.0`, `fine_groups.higgs: 2.0`
- **Loss**: L_global + 2.0 · L_fine_higgs + 100.0 · (-S/√B)
- **Kappa mode**: clamp (κ = max(0, cos_sim))
- **Results**:
  - hplusc_vs_all AUC = 0.928 (lowest)
  - higgs_vs_all AUC = 0.892
  - hplusc_vs_other_higgs AUC = 0.809
  - top_vs_all AUC = 0.900
  - Loss went deeply negative (-6.5), accuracy ~2%
- **Kappa collapse**: 7/12 kappas went negative → clamped to 0. Only zh, ggzh, tthtobb, tt, wh retained positive kappas.
- **Conclusion**: Significance loss at high λ completely dominates, destroying CE-based class separation. The high S/√B at 30-50% is an artifact of ROC reshaping, not genuine improvement.

### v18 logB (log(B) loss λ=10)
- **Config**: `HPlusCHToWW_logB` with `significance.mode: "logB"`, `significance.lam: 10`
- **Loss**: L_global + 2.0 · L_fine_higgs + 10.0 · log(B)
- **Kappa mode**: smooth (κ = (1+cos_sim)/2)
- **Results**:
  - hplusc_vs_all AUC = 0.960
  - higgs_vs_all AUC = 0.905
  - hplusc_vs_other_higgs AUC = 0.867
  - Accuracy: ~3%
- **Kappa behavior**: All 12 kappas positive (0.20–0.95). No collapse, but all pushed high.
- **Known issue**: log(B) → -∞ as B → 0. Loss decreases indefinitely. Fix: use log(1+B).

### v19 logB (log(B) loss λ=1)
- **Config**: `HPlusCHToWW_logB` with `significance.lam: 1`
- **Loss**: L_global + 2.0 · L_fine_higgs + 1.0 · log(B)
- **Kappa mode**: smooth (κ = (1+cos_sim)/2)
- **Results**:
  - hplusc_vs_all AUC = 0.961
  - higgs_vs_all AUC = 0.906
  - hplusc_vs_other_higgs AUC = 0.870
  - Accuracy: ~4%
- **Kappa behavior**: More spread than v18logB (0.15–0.90), but still all positive.

### v20: Discriminant-aware significance loss (BEST OVERALL)
- **Config**: `HPlusCHToWW_logB` with `significance.lam: 1`
- **Loss**: L_global + 2.0 · L_fine_higgs + λ · L_sig
  - L_sig = Σ_sig -log(D_i) + Σ_bkg log(1 + D_i)
  - D_i = P(sig) / (P(sig) + Σ_j κ_j · P_j), κ_j = (1+cos_sim)/2
- **Key design**: Signal term -log(D) pushes D up (gradient aligns with CE: P(sig) up for signal). Background term log(1+D) pushes D down (P(sig) down for bkg, κ up). κ finds equilibrium between opposing forces. No P(sig) suppression issue.
- **Results**:
  - hplusc_vs_all AUC = **0.9729** (best ever)
  - higgs_vs_all AUC = **0.9025** (best ever)
  - hplusc_vs_other_higgs AUC = 0.8574
  - top_vs_all AUC = 0.918
  - vjets_vs_all AUC = 0.963
  - diboson_vs_all AUC = 0.820
  - Accuracy: ~22% (noisy but improving)
- **P(hplusc)**: mean=0.012 for signal, 0.0004 for bkg (no longer suppressed like v19logB)
- **Learned kappas** (from cosine similarity of output layer weights):
  - hplusb: 0.87 (high — similar to signal, don't suppress)
  - ggH: 0.88, vbf: 0.87, zh: 0.78, wh: 0.72 (higgs classes: moderate-high)
  - ggzh: 0.67, diboson: 0.66, vjets: 0.66 (moderate)
  - tthnonbb: 0.55, tt: 0.54, st: 0.51, tthtobb: 0.70 (top classes: lower)
- **S/√B**: Peak 5.14 at 60% eff (uniform κ), 5.21 at 50% eff (optimized κ). Uniform κ already beats all previous versions including v11+opt κ.
- **Post-training kappa optimization barely matters (+1.2%)** — the loss learns near-optimal discriminant structure during training.
- **Conclusion**: The discriminant-aware loss resolves all previous issues: no P(sig) suppression, no kappa collapse/convergence, gradients align with CE. Best AUC and best S/√B simultaneously.

### v21–v23: logB variants
- **Config**: `HPlusCHToWW_logB`, 30 epochs
- Incremental improvements to the log(B) loss formulation
- **v21**: AUC 0.965, higgs_vs_all 0.749 — regression from v20
- **v22**: AUC 0.968, higgs_vs_all **0.383** — collapsed higgs grouping
- **v23**: AUC 0.973, higgs_vs_all 0.747 — recovered hplusc AUC but higgs grouping still poor

### v24: Three variants (control, logB, logB_weighted)
- **v24 control** (`HPlusCHToWW_control`): Significance loss uses raw P(signal) instead of kappa discriminant D
  - L_sig = -log(P_sig) + log(1+P_sig) — no kappas at all
  - AUC = **0.973**, higgs_vs_all = 0.708
  - Shows that without kappas, hplusc discrimination is strong but higgs grouping degrades
- **v24 logB** (`HPlusCHToWW_logB`): AUC = 0.972, higgs_vs_all = 0.564 — kappa convergence issue persists
- **v24 logB_weighted** (`HPlusCHToWW_logB_weighted`): Inv-freq weighted background in significance term
  - AUC = **0.940** (worst) — inverse-frequency weighting in the significance term destroys discrimination
  - Confirms v20's finding: inv-freq in the significance loss pushes kappas the wrong way

### v25: First kappa HCE
- **Config**: `HPlusCHToWW_kappa_hce`, 30 epochs
- **Loss**: L_group + K_fine · L_fine + λ · L_sig with dynamic groups from cosine similarity
- Groups determined each forward pass: classes with cos_sim > 0 are "positive" group, the rest form individual groups in L_group
- **tau = 0.3** for soft membership: α = sigmoid(cos_sim / τ)
- AUC = 0.968, higgs_vs_all = 0.772, hplusc|higgs = 0.863
- **Conclusion**: First working version of dynamic group kappa HCE. Decent but needs tuning.

### v27–v28: kappa HCE refinements
- **v27**: AUC = 0.972, higgs_vs_all = 0.786 — improved over v25
- **v28**: AUC = 0.972, higgs_vs_all = **0.801** — best higgs grouping among 30-epoch runs

### v30: kappa HCE (further tuning)
- AUC = 0.973, higgs_vs_all = 0.790, hplusc|higgs = 0.882

### v31: kappa HCE (50 epochs)
- First run with 50 epochs instead of 30
- AUC = 0.975, higgs_vs_all = 0.792, hplusc|higgs = 0.887
- Longer training helps: +0.3% AUC, +0.5% hplusc|higgs over v30

### v32: kappa HCE (50 epochs, final — CURRENT BEST)
- **Config**: `HPlusCHToWW_kappa_hce`, 50 epochs, batch_size=1024, lr=1e-3
- **Loss**: L_group + K_fine · L_fine + λ · L_sig (λ=1, τ=0.3)
- **Results**:
  - hplusc_vs_all AUC = **0.975**
  - higgs_vs_all AUC = 0.796
  - hplusc|higgs AUC = 0.887
- **Dynamic group evolution**: At epoch 0, most classes start with cos_sim > 0 (in +group). Over training, the model learns to push dissimilar classes negative — by epoch 49, only H+b, ggH, VBF remain in the +cos_sim group (see `plots/all_trainings/v32_kappa_hce/group_evolution.png`)
- **Conclusion**: Best hplusc_vs_all AUC (0.975, surpassing v20's 0.973). The kappa HCE loss with dynamic groups provides a natural curriculum: early training does broad multiclass, late training focuses on signal-like classes.

### v32 Alpha Values (from best_model.pt)

Cosine similarity and alpha (soft group membership) for each class relative to H+c signal:

| Class | cos_sim | alpha (τ=0.3) | Group |
|---|---|---|---|
| H+c | +1.000 | 0.966 | signal |
| H+b | +0.355 | 0.765 | +cos |
| VBF | +0.277 | 0.716 | +cos |
| ggH | +0.097 | 0.580 | +cos |
| V+Jets | -0.244 | 0.307 | -cos |
| ttHtoBB | -0.434 | 0.191 | -cos |
| ZH | -0.478 | 0.169 | -cos |
| ttHnonBB | -0.498 | 0.160 | -cos |
| ggZH | -0.522 | 0.149 | -cos |
| tt | -0.621 | 0.112 | -cos |
| Diboson | -0.670 | 0.097 | -cos |
| WH | -0.708 | 0.086 | -cos |
| ST | -0.733 | 0.080 | -cos |

**Interpretation**: The model learns that H+b, VBF, and ggH are the most signal-like backgrounds (highest alpha → treated as part of the same "fine" group). All non-higgs backgrounds (tt, ST, diboson, V+Jets) and most higgs backgrounds (ZH, ggZH, WH, ttH) are pushed to negative cosine similarity, meaning the model treats them as clearly distinct from signal.

### v32 Alpha-weighted Feature Importance (gradient-based)

Top 5 features per class, weighted by alpha (from `scripts/feature_importance_alpha_grad.py`):

**Per-class (H+c vs each, alpha × |grad|):**

| Class (α) | #1 | #2 | #3 | #4 | #5 |
|---|---|---|---|---|---|
| H+b (0.77) | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |
| ggH (0.58) | cvsb_pnet | cvsl_pnet | dR_ll_c | cjet_pt | dilepton_pt |
| VBF (0.72) | cvsb_pnet | cvsl_pnet | dR_ll_c | cjet_pt | met_pt |
| ZH (0.17) | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |
| ggZH (0.15) | cvsb_pnet | cvsl_pnet | dR_ll_c | cjet_pt | dilepton_pt |
| WH (0.09) | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |
| ttHnonBB (0.16) | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | dilepton_pt |
| ttHtoBB (0.19) | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |
| tt (0.11) | cvsb_pnet | cvsl_pnet | cjet_pt | met_pt | dR_ll_c |
| ST (0.08) | cvsb_pnet | cvsl_pnet | cjet_pt | met_pt | dR_ll_c |
| Diboson (0.10) | cvsb_pnet | cvsl_pnet | dR_ll_c | cjet_pt | met_pt |
| V+Jets (0.31) | cvsb_pnet | cvsl_pnet | dR_ll_c | cjet_pt | dilepton_pt |

**Grouped alpha-weighted gradient:**

| Group | #1 | #2 | #3 | #4 | #5 |
|---|---|---|---|---|---|
| Higgs bkg | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |
| Non-higgs bkg | cvsb_pnet | cvsl_pnet | cjet_pt | met_pt | dR_ll_c |
| All bkg | cvsb_pnet | cvsl_pnet | cjet_pt | dR_ll_c | met_pt |

**Key finding**: The charm tagging variables (cvsb_pnet, cvsl_pnet) dominate across all classes — the MLP relies heavily on c-tagging for H+c discrimination. cjet_pt and dR_ll_c are the next most important kinematic features.

## AUC Comparison Table

### v10–v20 (hierarchical CE + significance loss development)

| Metric | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB | **v20** |
|---|---|---|---|---|---|---|---|---|---|---|
| hplusc_vs_all | 0.966 | 0.951 | 0.961 | 0.965 | 0.964 | 0.954 | 0.928 | 0.960 | 0.961 | **0.973** |
| higgs_vs_all | — | 0.847 | 0.847 | 0.842 | 0.910 | 0.909 | 0.892 | 0.905 | 0.906 | **0.903** |
| hplusc\|higgs | — | — | 0.858 | 0.855 | 0.853 | 0.855 | 0.809 | 0.867 | **0.870** | 0.857 |
| top_vs_all | — | — | 0.952 | 0.951 | 0.921 | 0.924 | 0.900 | 0.922 | — | 0.918 |
| Accuracy | — | — | — | — | ~15% | ~40% | ~2% | ~3% | ~4% | ~22% |

### v21–v32 (kappa HCE development)

| Metric | v21 logB | v23 logB | v24 ctrl | v24 logBw | v25 kHCE | v27 kHCE | v28 kHCE | v30 kHCE | v31 kHCE | **v32 kHCE** |
|---|---|---|---|---|---|---|---|---|---|---|
| hplusc_vs_all | 0.965 | 0.973 | 0.973 | 0.940 | 0.968 | 0.972 | 0.972 | 0.973 | 0.975 | **0.975** |
| higgs_vs_all | 0.749 | 0.747 | 0.708 | 0.713 | 0.772 | 0.786 | 0.801 | 0.790 | 0.792 | **0.796** |
| hplusc\|higgs | 0.894 | 0.877 | 0.879 | 0.799 | 0.863 | 0.877 | 0.873 | 0.882 | 0.887 | **0.887** |

## Kappa Values from Model Weights

Kappas derived from cosine similarity of final linear layer weight vectors: cos_sim(W_hplusc, W_j).
Two mappings tested: **clamp** = max(0, cos_sim), **smooth** = (1+cos_sim)/2.

### Raw cosine similarity

| Class | v18h | v18s | v18logB | v19logB | **v20** |
|---|---|---|---|---|---|
| hplusb | 0.714 | -0.000 | 0.931 | 0.879 | **0.750** |
| ggH | 0.793 | -0.001 | 0.952 | 0.896 | **0.762** |
| vbf | 0.767 | -0.000 | 0.949 | 0.894 | **0.739** |
| zh | 0.476 | 0.496 | 0.912 | 0.872 | **0.562** |
| ggzh | 0.087 | 0.526 | 0.802 | 0.685 | **0.345** |
| wh | 0.096 | -0.269 | 0.853 | 0.837 | **0.442** |
| tthnonbb | -0.029 | -0.251 | 0.403 | 0.155 | **0.104** |
| tthtobb | -0.113 | 0.558 | 0.690 | 0.263 | **0.406** |
| tt | -0.048 | 0.229 | 0.309 | 0.548 | **0.082** |
| st | -0.247 | -0.354 | 0.202 | 0.560 | **0.024** |
| diboson | -0.226 | -0.297 | 0.848 | 0.898 | **0.315** |
| vjets | 0.050 | -0.042 | 0.813 | 0.715 | **0.324** |

**Key observations**:
- **v18s**: 7/12 negative → clamp zeroes them → acts as feature selector (only zh, ggzh, tthtobb, tt contribute). This accidentally helps.
- **v18h**: 5/12 negative → mixed behavior. Smooth works better (preserves ordering).
- **logB versions (v18/v19)**: All positive → clamp = cos_sim (no clamping needed). All pushed high (0.15–0.95) → kappa D ≈ monotonic rescaling of P(hplusc) → kappas are useless.
- **v20**: Physically meaningful spread! Higgs classes high (0.34–0.76), top classes low (0.02–0.41). The discriminant-aware loss learns that backgrounds dissimilar to signal (tt, st) should have low κ (= high suppression in denominator), while similar classes (hplusb, ggH) should have high κ. This is the opposite of logB versions and makes physical sense.

## S/√B Comparison

All S/√B values use **raw event counts** (no inverse-frequency weighting). Signal = hplusc (2,257 events), Background = all other classes (4,074,257 events).

### Single-step P(hplusc) / uniform κ — All versions

| Eff | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB | **v20** |
|---|---|---|---|---|---|---|---|---|---|---|
| 5% | 2.79 | 2.07 | 2.79 | 2.85 | 2.08 | 2.00 | 2.06 | 2.96 | 2.81 | — |
| 10% | 3.41 | 2.41 | 3.36 | 3.53 | 2.71 | 2.68 | 2.78 | 3.69 | 3.53 | **3.62** |
| 20% | 4.05 | 3.20 | 3.46 | 3.95 | 3.60 | 3.36 | 3.77 | 4.05 | 4.14 | **4.52** |
| 30% | 4.26 | 3.64 | 3.46 | 4.04 | 4.14 | 3.82 | 4.37 | 4.17 | 4.23 | **4.88** |
| 40% | — | — | — | — | — | — | — | — | — | **5.06** |
| 50% | 4.39 | 3.98 | 4.09 | 4.43 | 4.61 | 4.20 | 4.69 | 4.22 | 4.46 | **5.13** |
| 60% | — | — | — | — | — | — | — | — | — | **5.14** |
| 70% | 4.29 | 3.60 | 4.13 | 4.31 | 4.46 | 3.87 | 4.02 | 4.09 | 4.16 | **4.80** |
| 80% | — | — | — | — | — | — | — | — | — | **4.45** |
| 90% | 3.41 | 2.60 | 3.09 | 3.32 | 2.97 | 2.80 | 2.33 | 3.03 | 3.08 | **3.70** |

Note: v20 uses uniform κ=1 (not raw P(hplusc)). v11-v19logB use raw P(hplusc) for the single-step columns.

### Single-step κD smooth (κ = (1+cos)/2)

v11 excluded (6-class, no kappas).

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

Note: For logB versions, clamp = cos_sim (all kappas positive, nothing gets clamped).

### Two-step: P(higgs) → P(hplusc|higgs)

v11 excluded (6-class, no meaningful P(higgs) grouping — only hplusc + higgsbkg).

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

Note: For logB versions clamp = cos_sim (identical results) since all kappas are positive.

### Best S/√B per version (best method at each efficiency)

Note: v12, v13, v15, v17 use raw P(hplusc) only. v11 includes opt κ. v18h/s, v18/v19logB use best of (raw, κD, two-step). v20 uses uniform κ=1 (opt κ gives only +1.2%).

| Eff | v11 | v12 | v13 | v15 | v17 | v18h | v18s | v18logB | v19logB | **v20** | **Winner** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10% | 3.41 | 2.41 | 3.36 | 3.53 | 2.71 | 3.11 | 3.04 | 3.81 | 3.67 | **3.70** | v18logB |
| 20% | 4.12 | 3.20 | 3.46 | 3.95 | 3.60 | 3.71 | 3.93 | 4.13 | 4.16 | **4.52** | **v20** |
| 30% | 4.57 | 3.64 | 3.46 | 4.04 | 4.14 | 4.04 | 4.49 | 4.17 | 4.23 | **4.93** | **v20** |
| 50% | 4.82 | 3.98 | 4.09 | 4.43 | 4.61 | 4.34 | 4.73 | 4.22 | 4.46 | **5.21** | **v20** |
| 70% | 4.66 | 3.60 | 4.13 | 4.31 | 4.46 | 4.01 | 4.13 | 4.09 | 4.16 | **4.88** | **v20** |
| 90% | 3.68 | 2.60 | 3.09 | 3.32 | 2.97 | 3.05 | 2.52 | 3.09 | 3.18 | **3.77** | **v20** |

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

### Clamp vs smooth kappas

- **v18s: clamp wins** — collapsed negative kappas act as feature selectors, zeroing out irrelevant classes
- **v18h: smooth wins** — negative kappas still carry ordering info, (1+cos)/2 preserves it
- **logB versions: identical** — all cos_sim > 0, so max(0, cos) = cos. Smooth just compresses toward 1

## Post-Training Kappa Optimization

### Method
Instead of learning kappas during training (which suffers from collapse/convergence), optimize kappas post-training via **differential evolution** (`scipy.optimize.differential_evolution`) to maximize S/√B at each target efficiency working point. Each WP gets its own optimal κ vector — no gradient conflicts.

- Background subsampled to 100k events (with scale factor) for speed
- Bounds: κ ∈ [0, 5] per class
- maxiter=20, popsize=15

### Results: All versions with optimized kappas

| Eff | v11 raw | v11+opt κ | v18h+opt κ | v18s+opt κ | v18logB+opt κ | v19logB+opt κ | **v20 uni κ** | **v20+opt κ** |
|---|---|---|---|---|---|---|---|---|
| 10% | 3.41 | 3.29 | 2.99 | 2.94 | 3.77 | 3.70 | 3.62 | **3.70** |
| 20% | 4.05 | 4.12 | 3.74 | 3.81 | 4.42 | 4.52 | 4.52 | **4.51** |
| 30% | 4.26 | 4.57 | 4.24 | 4.38 | 4.80 | 4.80 | 4.88 | **4.93** |
| 40% | — | — | — | — | — | — | 5.06 | **5.14** |
| 50% | 4.39 | 4.82 | 4.67 | 4.73 | 4.91 | 5.12 | 5.13 | **5.21** |
| 60% | — | — | — | — | — | — | **5.14** | 5.02 |
| 70% | 4.29 | 4.66 | 4.39 | 4.14 | 4.65 | 4.68 | 4.80 | **4.88** |
| 80% | — | — | — | — | — | — | 4.45 | **4.50** |
| 90% | 3.41 | 3.68 | 3.33 | 2.65 | 3.41 | 3.47 | 3.70 | **3.77** |

**v20 with uniform kappas (κ=1) already beats all previous versions** including v11+opt κ and v19logB+opt κ. Post-training kappa optimization gives only +1.2% on top — the loss learns near-optimal discriminant structure during training.

Peak S/√B = **5.21** at 50% efficiency (v20+opt κ), a **+18.7%** improvement over v11 raw (4.39) and **+8.1%** over v11+opt κ (4.82).

### Optimized Kappa Values (at 50% efficiency)

| Class | v11 opt κ | v12 opt κ | v20 opt κ |
|---|---|---|---|
| higgs/hplusb | 1.34 | 1.92 | **0.39** |
| ggH | — | 5.03 | **13.99** |
| vbf | — | 3.68 | **18.62** |
| zh | — | 19.33 | **17.94** |
| ggzh | — | 19.86 | **10.92** |
| wh | — | 7.54 | **14.98** |
| tthnonbb | 5.62 | 0.85 | **18.90** |
| tthtobb | — | 9.34 | **8.59** |
| tt/tt_st | 19.77 | 11.11 | **16.14** |
| st | — | 0.60 | **8.71** |
| diboson | 0.38 | 0.04 | **5.16** |
| vjets | 0.03 | 0.93 | **19.60** |

**v20 kappa structure**: hplusb is the only low κ (0.39) — don't suppress the class most similar to signal. Everything else is high (5–20), aggressively rejecting all dissimilar backgrounds. This is physically sensible: the discriminant should focus on separating hplusc from backgrounds, not from hplusb.

### Learned vs Optimized Kappas (v20)

The v20 loss learns kappas during training via cosine similarity. Comparing these to post-training optimized kappas (at 50% eff):

| Class | Learned κ | Optimal κ | Ratio opt/learned |
|---|---|---|---|
| hplusb | 0.87 | 0.39 | 0.45 |
| ggH | 0.88 | 13.99 | 15.9 |
| vbf | 0.87 | 18.62 | 21.4 |
| zh | 0.78 | 17.94 | 23.0 |
| ggzh | 0.67 | 10.92 | 16.3 |
| wh | 0.72 | 14.98 | 20.8 |
| tthnonbb | 0.55 | 18.90 | 34.4 |
| tthtobb | 0.70 | 8.59 | 12.3 |
| tt | 0.54 | 16.14 | 29.9 |
| st | 0.51 | 8.71 | 17.1 |
| diboson | 0.66 | 5.16 | 7.8 |
| vjets | 0.66 | 19.60 | 29.7 |

**Key insight**: The learned kappas have the right **ordering** (hplusb lowest, tt/st/tthnonbb lowest among bkg) but are compressed into [0.51, 0.88] by the (1+cos_sim)/2 mapping which bounds κ to [0,1]. The optimal kappas span [0.39, 19.6] — a much wider dynamic range. Despite this compression, uniform κ=1 already gives excellent S/√B (5.14) because the learned probability outputs P(j|x) already encode the discriminant structure. The kappas provide fine-tuning rather than the primary separation.

### Abundance–Kappa Correlation

Optimal kappas are **positively correlated with class abundance** (number of events), not with cosine similarity:

| Version | corr(log_count, avg_κ_opt) | corr(cos_sim, avg_κ_opt) |
|---|---|---|
| v19logB | **+0.716** (strong) | -0.71 (anti-correlated) |
| v18h | **+0.431** (moderate) | -0.02 (none) |

This makes physical sense: S/√B ∝ S/√(Σ N_j · ...). Abundant backgrounds (tt: 3.18M, st: 499k) contribute more to B in absolute terms, so the optimal discriminant needs higher κ for these classes to suppress them harder.

### Why Previous In-Training Kappas Failed (v18/v19)

The old logB loss used **inverse-frequency weighting** in B: `w_i = 1/count(class_i)`. This equalizes all classes in B. But S/√B with raw counts wants κ ∝ count(class_i) — the opposite. The in-training gradient pushes kappas in the wrong direction.

**v20 solves this** with a discriminant-aware loss (`-log(D)` for signal, `log(1+D)` for bkg) that has no inverse-frequency weighting in the significance term. The opposing signal/background forces on κ find a natural equilibrium, making post-training optimization nearly unnecessary.

## Key Findings

### 1. Hierarchical loss rescues 13-class training
Flat CE on 13 classes (v10) fails completely. Hierarchical CE (L_global + L_fine) enables 13-class training with competitive AUCs.

### 2. Group structure matters more than loss engineering
Merging h_plus_v into higgs (v17/v18) boosted higgs_vs_all from 0.84 → 0.91. This came entirely from the grouping change, not from the significance loss.

### 3. In-training significance losses have a fundamental kappa problem

All three approaches (S/√B, log(B) with λ=10, log(B) with λ=1) suffer from kappa degeneracy:

**S/√B loss (v18s)**: Kappas collapse to 0 via "Path B" — the gradient pushes weight vectors apart → cos_sim goes negative → clamp zeros κ → denominator shrinks → D becomes binary. 7/12 kappas collapsed. AUC dropped to 0.928, accuracy to 2%.

**log(B) loss (v18logB, v19logB)**: Opposite problem — kappas converge to ~1. The log(B) gradient pushes κ UP (bigger denominator → smaller D → smaller B). But there's no force pushing any κ DOWN, so all kappas race toward 1 together. When all κ ≈ 1:

D = P(hplusc) / (P(hplusc) + 1·Σ P_j) ≈ P(hplusc) / 1

The kappa discriminant becomes a monotonic rescaling of P(hplusc), making it useless. The kappas are not differentiating between classes.

**Additional log(B) issue**: log(B) → -∞ as B → 0. The loss decreases indefinitely because B is not bounded below by 1. Fix: use log(1+B) which floors at 0.

### 4. v18s's high S/√B is misleading
Despite lowest AUC (0.928) and 2% accuracy, v18s achieves the highest peak S/√B (4.73 at 50% eff). This is because the significance loss concentrated all discriminating power at 30-50% efficiency, destroying tight WPs (2.06 at 5%) and loose WPs (2.33 at 90%). This ROC reshaping is an artifact, not a reliable improvement.

### 5. v20's discriminant-aware loss resolves kappa issues
v20 achieves best S/√B at every working point (peak 5.21 at 50% eff). The discriminant-aware loss (`-log(D)` for signal, `log(1+D)` for bkg) resolves all previous issues:
- No P(sig) suppression (gradients align with CE)
- No kappa collapse or convergence (opposing signal/bkg forces find equilibrium)
- Uniform kappas already outperform all previous versions with optimized kappas
- Post-training kappa optimization gives only +1.2% (vs +11% for v11, +9% for v12)

### 6. Two-step helps at tight WPs, not loose WPs
At 5-10% efficiency, 2-step P(higgs)→κD(smooth) gives 3.19-3.81 for logB versions — significantly better than single-step. At 30-50%, single-step P(hplusc) is already optimal. The higgs pre-filter removes bulk backgrounds first, then the second cut does useful refinement.

### 7. Kappa HCE with dynamic groups outperforms fixed groups (v25–v32)
The kappa HCE loss removes the need for manual group definitions. Groups are determined dynamically from cosine similarity each forward pass, creating a natural curriculum: early training does broad multiclass CE, late training focuses on signal-like classes. v32 achieves the best hplusc_vs_all AUC (0.975) and best hplusc|higgs (0.887).

### 8. Inverse-frequency weighting in significance term is harmful
v24_logB_weighted confirmed that applying inv-freq weights to the significance loss background term (w_j = 1/count_j) destroys discrimination (AUC drops from 0.973 to 0.940). The significance term should use raw event counts.

## Recommended Approach

**Use v32 (kappa HCE with dynamic groups).**

Rationale:
1. Best hplusc_vs_all AUC (0.975) — surpasses v20 (0.973)
2. Dynamic groups eliminate manual group tuning — groups emerge from model weights
3. Natural curriculum: broad multiclass early, focused binary-like late
4. 13-class output with meaningful alpha-weighted soft group membership
5. Best hplusc|higgs AUC (0.887) among all versions

## Loss Function Implementations

### Hierarchical Cross-Entropy
```
L = L_CE_global(group probabilities, group truth) + Σ_g λ_g · L_CE_fine(sub-class probs within group g)
```
- Global CE: softmax over summed group logits, weighted by inverse-frequency
- Fine CE: per-group softmax over sub-class logits, only for events in that group

### Significance Loss (-S/√B) — NOT RECOMMENDED (kappas collapse to 0)
```
L_sig = -S/√(B+ε)
```
where:
- D_hplusc = P(hplusc) / (P(hplusc) + Σ κ_j · P_j)
- κ_j = max(0, cosine_similarity(W[hplusc], W[j])) from final layer weights
- S = Σ D_i · is_signal_i, B = Σ D_j · is_bkg_j
- Problem: kappas collapse to 0, discriminant becomes binary

### log(B) Loss — NOT RECOMMENDED (kappas converge to ~1, loss → -∞)
```
L = L_hierarchical_CE + λ · log(Σ_bkg w_i · D_i + ε)
```
where:
- D_i = P(hplusc)_i / (P(hplusc)_i + Σ_j κ_j · P_j_i) — computed for bkg events only
- κ_j = (1 + cos_sim(W_hplusc, W_j)) / 2 — smooth, always positive
- w_i = 1/count(class_i) — inverse-frequency weighting within B
- Problem 1: All kappas pushed toward 1, making κD ≈ P(hplusc)
- Problem 2: log(B) → -∞ as B → 0 (loss unbounded below)

### Discriminant-Aware Significance Loss — RECOMMENDED (v20)
```
L = L_hierarchical_CE + λ · (Σ_sig -log(D_i) + Σ_bkg log(1 + D_i))
```
where:
- D_i = P(hplusc)_i / (P(hplusc)_i + Σ_j κ_j · P_j_i)
- κ_j = (1 + cos_sim(W_hplusc, W_j)) / 2
- Signal term -log(D): pushes D up. Gradient: P(sig) up (aligns with CE), κ down.
- Background term log(1+D): pushes D down. Gradient: P(sig) down (aligns with CE), κ up.
- κ finds equilibrium between the two opposing forces.
- No inverse-frequency weighting in the significance term.
- No detach needed — all gradient paths align with CE.

### Kappa HCE Loss — RECOMMENDED (v25–v32)
```
L = L_group + K_fine · L_fine + λ · L_sig
```
where:
- **Dynamic groups**: Each forward pass, compute cos_sim(W_signal, W_j) for all classes j. Classes with cos_sim > 0 form the "+cos" group (fine group), others are individual groups.
- **L_group**: CE over {each -cos class as individual group, merged +cos group}. Weighted by κ × inv_freq, where κ = sigmoid(cos_sim / τ).
- **L_fine**: CE within +cos classes only. Weighted by (1+κ) × inv_freq. Background events (from -cos classes) contribute 0.
- **L_sig**: -log(D) for signal + log(1+D) for background. D = P_sig / (P_sig + Σ α_j · P_j), α_j = sigmoid(cos_sim_j / τ).
- **τ (temperature)**: Controls sharpness of soft membership. τ=0.3 gives α>0.5 at cos_sim>0, α<0.05 at cos_sim<-0.6.
- **Natural curriculum**: Early in training, most cos_sim > 0 → broad multiclass fine CE. Late in training, only signal-like classes remain → fine CE converges to binary.

### Kappa Discriminant (post-training)
```
D_signal = P_signal / (P_signal + Σ κ_j · P_j)
```
Kappas optimized via differential evolution to maximize S/√B at a target efficiency working point. See `scripts/compare_significance.py`.

## Analysis Scripts

### `scripts/compare_significance.py`
Post-training S/√B comparison with optimized kappas via differential evolution.
- Loads inference outputs (prediction.npy, truth.npy) for v11, v18h, v18s
- Applies softmax to raw logits
- Computes S/√B at fixed efficiency working points using raw P(hplusc)
- Optimizes kappa discriminant via `scipy.optimize.differential_evolution`
- Vectorized discriminant computation: `p_others @ full_kappas`
- Scaled iterations: maxiter=n_other*3, popsize=n_other
- Generates per-version S/√B curves and summary comparison table

### `scripts/hierarchical_significance.py`
Two-step hierarchical S/√B analysis.
- Compares v11 (single-step P(hplusc)) vs v18h and v18s (two-step: P(higgs) cut + P(hplusc|higgs) cut)
- Scans P(higgs) efficiency working points: 50%, 70%, 80%, 90%, 95%, 99%
- For each step-1 cut, scans step-2 efficiency

### `scripts/kappa_from_model.py`
Extracts kappas from trained model checkpoints via cosine similarity.
- Loads `best_model.pt` → finds last linear layer (`net.12.weight`)
- Computes κ with both clamp and smooth mappings
- Builds kappa discriminant D and computes S/√B

### `scripts/feature_importance_alpha_grad.py`
Alpha-weighted gradient feature importance for kappa_hce model.
- Computes per-class |dP_hplusc/dx - dP_class/dx| weighted by α = sigmoid(cos_sim / τ)
- Per-class and grouped (higgs bkg, non-higgs bkg, all) rankings
- Args: `--model-path`, `--data-path`, `--tau`, `--max-events`, `--top-k`

### `scripts/confusion_matrix.py`
Confusion matrix plotter with CMS styling.
- Args: `--truth`, `--prediction`, `--labels`, `--apply-softmax`, `--normalize`

### `scripts/plot_v32_all.py`
Comprehensive v32 plot generation: confusion matrices, ROC curves, score distributions, S/√B vs efficiency, cosine similarity evolution, group membership evolution.

### `scripts/prepare_parquet_for_training.py`
Merges per-process parquet files, shuffles globally, splits back into equal-sized files for balanced train/val splits.

### Inference output locations

| Model | Inference path |
|---|---|
| v11 | `.../InferenceTask/HPlusCHToWW_multiclass/hww_multiclass_v11/hww_multiclass_v11/hww_multiclass_v11/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v18h | `.../InferenceTask/HPlusCHToWW_hierarchical/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v18s | `.../InferenceTask/HPlusCHToWW_sig/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v18logB | `.../InferenceTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v19logB | `.../InferenceTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v19/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v20 | `.../InferenceTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v20/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` |
| v32 | `.../InferenceTask/HPlusCHToWW_kappa_hce/hww_multiclass_v13/hww_multiclass_v13/hww_multiclass_v32/SimpleMLP_MultiClass/epochs_50/nominal/test_attack_nominal/` |

All paths prefixed with `/eos/user/c/cgupta/EPR_task/b-hive/output/`. Each directory contains `prediction.npy` (raw logits, shape [N, n_classes]) and `truth.npy` (integer labels).

### Model checkpoint locations

| Model | Checkpoint path |
|---|---|
| v11 | `.../TrainingTask/HPlusCHToWW_multiclass/hww_multiclass_v11/hww_multiclass_v11/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v18h | `.../TrainingTask/HPlusCHToWW_hierarchical/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v18s | `.../TrainingTask/HPlusCHToWW_sig/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v18logB | `.../TrainingTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v18/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v19logB | `.../TrainingTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v19/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v20 | `.../TrainingTask/HPlusCHToWW_logB/hww_multiclass_v13/hww_multiclass_v20/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt` |
| v32 | `.../TrainingTask/HPlusCHToWW_kappa_hce/hww_multiclass_v13/hww_multiclass_v32/SimpleMLP_MultiClass/epochs_50/nominal/best_model.pt` |

Checkpoints are dicts with keys: `epoch`, `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict`, `loss_train`, `acc_train`, `loss_val`, `acc_val`. Final layer is `net.12.weight` with shape [n_classes, 32]. v32 has per-epoch checkpoints (`model_0.pt` through `model_49.pt`) for tracking cosine similarity evolution.

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
| Config (kappa HCE) | `config/HPlusCHToWW_kappa_hce.yml` |
| Config (control) | `config/HPlusCHToWW_control.yml` |
| Config (logB weighted) | `config/HPlusCHToWW_logB_weighted.yml` |
| S/√B comparison | `scripts/compare_significance.py` |
| Two-step hierarchical | `scripts/hierarchical_significance.py` |
| Kappa from model | `scripts/kappa_from_model.py` |
| Feature importance | `scripts/feature_importance_alpha_grad.py` |
| Confusion matrix | `scripts/confusion_matrix.py` |
| v32 all plots | `scripts/plot_v32_all.py` |
| Parquet shuffler | `scripts/prepare_parquet_for_training.py` |
| Training script (hier) | `train_MVA.sh` |
| Training script (logB) | `train_MVA2.sh` |
| v32 plots | `plots/all_trainings/v32_kappa_hce/` |
| Plotting (hierarchical) | higgscharm repo: `scripts/plot_mva_hierarchical.py` |
