---
theme: black
transition: slide
enableMenu: true
enableSearch: true
height: "1080"
width: "2100"
---
## H$\rightarrow$WW MVA
### Chirayu Gupta
#### 20th March 2026

---

### Overview

**Goal**: Maximize H+c signal extraction in H$\rightarrow$WW* using a multiclass DNN

**Challenge**: Extreme class imbalance — H+c has 2,257 events vs 3.18M $t\bar{t}$ events (ratio 1:1400)

**Three key training versions**:

| Version | Classes | Loss | hplusc\_vs\_all AUC |
|---|---|---|---|
| v10 | 13 (fine-grained) | Standard CE | 0.51 (FAILED) |
| v11 | 6 (H+c vs higgsbkg) | Standard CE | 0.966 |
| **v32** | **13 (fine-grained)** | **Kappa HCE** | **0.975** |

v32 achieves the best of both worlds: fine-grained class information AND best H+c discrimination

---

### Event Selection

**Object Selection**
- **Muons**: $p_T > 10$ GeV, $|\eta| < 2.4$, tight ISO, tight ID
- **Electrons**: $p_T > 10$ GeV, $|\eta| < 2.5$, wp80iso ID, $\Delta R(e, \mu) > 0.4$
- **Dilepton pair**: Leading $p_T > 20$ GeV, subleading $p_T > 10$ GeV, $p_T(ll) > 30$ GeV, opposite sign, $m(ll) > 12$ GeV
- **Jets**: $p_T > 30$ GeV, $|\eta| < 2.4$, tightLepVeto ID, $\Delta R(\text{jet}, \ell) > 0.4$
- **c-jets**: $p_T > 20$ GeV, $|\eta| < 2.4$, PNet c-tag medium WP

**Event-level**: good vertex, lumi mask, MET filters, trigger (MuEle/SingleMu/SingleEle), MET $> 45$ GeV, exactly one e-$\mu$ pair

---

### Training Dataset

| Process | Events | Category |
|---|---|---|
| H+c (signal) | 2,257 | higgs |
| H+b | 1,093 | higgs |
| ggH | 28,413 | higgs |
| VBF | 4,067 | higgs |
| ZH, ggZH, WH | 105k + 1.6k + 1.4k | higgs |
| ttH(nonBB), ttH(BB) | 181k + 24k | higgs |
| $t\bar{t}$ | 3,180,107 | top |
| Single top | 499,001 | top |
| Diboson (WW, WZ, ZZ) | 41,540 | diboson |
| V+Jets | 7,319 | vjets |

**Total**: ~4.08M events (3.26M train, 815K test)

**Features**: 17 event-level variables (kinematic, transverse mass, angular, charm tagging, nSV)

**Central Production**:  Ongoing. Samples already on mcm [[HIG] HWW+C Run3 (#1235) ](https://gitlab.cern.ch/cms-gen/mccm/-/issues/1235)

---

### Model Architecture

- **Model**: SimpleMLP_MultiClass — feedforward MLP
- Layers: $17 \rightarrow 128 \rightarrow 64 \rightarrow 32 \rightarrow 13$ outputs
- BatchNorm + ReLU + Dropout(0.2) per layer
- **Optimizer**: Adam (lr=$10^{-3}$), batch size 1024
- **Reweighting**: Inverse-frequency class weights
- v10/v32: 13 output nodes, v11: 6 output nodes

---

## v10: Fine-grained 13-class (Standard CE)

- **13 one-hot classes** — every Higgs production mode gets its own label
- **Loss**: Standard cross-entropy with inverse-frequency weights
- **Result**: **FAILED** — hplusc\_vs\_all AUC $\approx$ 0.51
- Too many classes with extreme imbalance; model cannot learn H+c separation

---

### v10: ROC Curves
<split even>

![[Images/all_trainings/v10_finegrained/roc/roc_default_hplusc_vs_all.png|1000]]

![[Images/all_trainings/v10_finegrained/roc/roc_default_hplusc_vs_tt.png|1000]]

</split>

> AUC $\approx$ 0.51 — no better than random. Standard CE with 13 classes completely fails for H+c.

---

### v10: H+c Score Distribution
<split even>

![[Images/all_trainings/v10_finegrained/inference_v3/mva_score_hplusc.png|1000]]

![[Images/all_trainings/v10_finegrained/inference_v3/mva_score_hplusc_breakdown.png|1000]]

</split>

---

## v11: H+c vs Higgs Background (6-class Standard CE)

**Solution to v10**: Merge all non-H+c Higgs into single "higgsbkg" class $\rightarrow$ 6 classes
- `is_hplusc`, `is_higgsbkg`, `is_tt`, `is_st`, `is_diboson`, `is_vjets`
- Standard CE with inverse-frequency weights, 30 epochs

**Results**:
- hplusc\_vs\_all AUC = **0.966**
- hplusc\_vs\_tt = 0.976
- hplusc\_vs\_higgsbkg = 0.882

**Limitation**: No fine-grained Higgs sub-class information available

---

### v11: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/training/loss.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/inference_v4/confusion_matrix.png|1000]]

</split>

---

### v11: H+c Score and Breakdown
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/inference_v4/mva_score_hplusc.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/inference_v4/mva_score_hplusc_breakdown.png|1000]]

</split>

---

### v11: ROC — H+c vs All and vs $t\bar{t}$
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_all.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_tt.png|1000]]

</split>

---

### v11: ROC — H+c vs Higgs Background
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_higgsbkg.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_diboson.png|1000]]

</split>

> v11 achieves excellent H+c discrimination but loses fine-grained Higgs sub-class info. Can we have both?

---

## Motivation for Kappa HCE Loss

**The problem**: Standard CE with 13 classes fails (v10), but grouping to 6 classes loses information (v11)

**Key insight**: We need a loss that simultaneously:
1. Learns **global** group separation (higgs vs top vs diboson vs vjets)
2. Learns **fine-grained** separation within groups (H+c vs other higgs)
3. Optimizes the **discriminant** $D_\kappa = \frac{P_\text{sig}}{P_\text{sig} + \sum_j \kappa_j P_j}$ directly

**The kappa** $\kappa_j$ controls how much each background class $j$ contributes to the discriminant denominator — classes similar to signal get high $\kappa$ (less suppression), dissimilar classes get low $\kappa$ (more suppression)

---

### Kappa HCE Loss: Three Components

$$\mathcal{L} = \mathcal{L}_\text{group} + K_\text{fine} \cdot \mathcal{L}_\text{fine} + \lambda \cdot \mathcal{L}_\text{sig}$$

**$\mathcal{L}_\text{group}$**: Cross-entropy over dynamic groups
- Groups determined by cosine similarity of output layer weight vectors
- Classes with $\cos(\mathbf{w}_\text{H+c}, \mathbf{w}_j) > 0$ form the "positive" (signal-like) group
- Remaining classes form individual groups
- Maintains global background separation

**$\mathcal{L}_\text{fine}$**: Cross-entropy within the positive group
- Conditional probability $P(i|\text{group}) = P(i) / \sum_{j \in \text{group}} P(j)$
- Teaches fine-grained H+c vs similar-higgs separation

**$\mathcal{L}_\text{sig}$**: Discriminant-aware significance loss
- $\mathcal{L}_\text{sig} = \sum_\text{sig} -\log(D_i) + \sum_\text{bkg} \log(1 + D_i)$
- $D_i = P_\text{sig} / (P_\text{sig} + \sum_j \kappa_j P_j)$, with $\kappa_j = \sigma(\cos_\text{sim} / \tau)$
- Directly optimizes the analysis discriminant during training

---

### How $\kappa$ Values are Learned

The $\kappa_j$ for each class $j$ are derived from the **cosine similarity** between the output layer weight vectors:

$$\alpha_j = \sigma\left(\frac{\cos(\mathbf{w}_\text{H+c},\, \mathbf{w}_j)}{\tau}\right), \quad \tau = 0.3$$

- Signal-like classes (high $\cos_\text{sim}$) $\rightarrow$ high $\alpha$ $\rightarrow$ less suppression in $D_\kappa$ denominator
- Background-like classes (low $\cos_\text{sim}$) $\rightarrow$ low $\alpha$ $\rightarrow$ more suppression

This creates a **natural curriculum**: early in training, most classes have positive cosine similarity (broad multiclass learning). As training progresses, the model pushes dissimilar classes to negative cosine similarity, focusing the discriminant on the hardest backgrounds.

---

## v32: Kappa HCE (50 epochs)

**Configuration**:
- 13 output classes, 50 epochs, batch size 1024, lr=$10^{-3}$
- Loss: $\mathcal{L}_\text{group} + K_\text{fine} \cdot \mathcal{L}_\text{fine} + 1.0 \cdot \mathcal{L}_\text{sig}$, $\tau = 0.3$

**Results**:

| Metric | v10 (CE) | v11 (6-class CE) | **v32 (Kappa HCE)** |
|---|---|---|---|
| hplusc\_vs\_all AUC | 0.51 | 0.966 | **0.975** |
| hplusc\|higgs AUC | — | 0.882 | **0.887** |
| Fine-grained info | yes (unusable) | no | **yes** |

---

### v32: Training Loss and Accuracy
<split even>

![[Images/all_trainings/v32_kappa_hce/training/loss.png|1000]]

![[Images/all_trainings/v32_kappa_hce/training/acc.png|1000]]

</split>

---

### v32: Cosine Similarity Evolution

![[Images/all_trainings/v32_kappa_hce/cosine_similarity_evolution.png|1400]]

Model learns to separate signal-like (H+b, ggH, VBF) from background-like classes over training. By epoch 49, only H+b, ggH, VBF retain positive cosine similarity with H+c.

---


### v32: Learned Alpha Values (from best model)

| Class | $\cos_\text{sim}$ | $\alpha$ ($\tau=0.3$) | Interpretation |
|---|---|---|---|
| H+c | +1.000 | 0.966 | signal |
| H+b | +0.355 | 0.765 | most signal-like bkg |
| VBF | +0.277 | 0.716 | signal-like |
| ggH | +0.097 | 0.580 | signal-like |
| V+Jets | -0.244 | 0.307 | background |
| ttHtoBB | -0.434 | 0.191 | background |
| ZH | -0.478 | 0.169 | background |
| ttHnonBB | -0.498 | 0.160 | background |
| ggZH | -0.522 | 0.149 | background |
| $t\bar{t}$ | -0.621 | 0.112 | strong background |
| Diboson | -0.670 | 0.097 | strong background |
| WH | -0.708 | 0.086 | strong background |
| ST | -0.733 | 0.080 | strong background |

The model discovers that H+b, VBF, ggH are kinematically most similar to H+c signal.

---

### v32: Alpha-weighted Feature Importance

![[Images/all_trainings/v32_kappa_hce/feature_importance_alpha_heatmap.png|1400]]

Per-class gradient importance weighted by $\alpha$: charm tagging variables (CvsB, CvsL) dominate across all classes. $\Delta R(ll, c)$ and c-jet $p_T$ are the key kinematic discriminants.

---

### v32: Alpha-weighted Feature Importance (Grouped)

![[Images/all_trainings/v32_kappa_hce/feature_importance_alpha_weighted.png|1400]]

---
### v32: Alpha-weighted Feature Importance (Grouped)

| Group         | #1         | #2         | #3       | #4        | #5        |
| ------------- | ---------- | ---------- | -------- | --------- | --------- |
| Higgs bkg     | cvsb\_pnet | cvsl\_pnet | cjet\_pt | dR\_ll\_c | met\_pt   |
| Non-higgs bkg | cvsb\_pnet | cvsl\_pnet | cjet\_pt | met\_pt   | dR\_ll\_c |
| All bkg       | cvsb\_pnet | cvsl\_pnet | cjet\_pt | dR\_ll\_c | met\_pt   |

---

### v32: ROC — H+c vs All and vs $t\bar{t}$
<split even>

![[Images/all_trainings/v32_kappa_hce/roc/roc_default_hplusc_vs_all.png|1000]]

![[Images/all_trainings/v32_kappa_hce/roc/roc_default_hplusc_vs_tt.png|1000]]

</split>

---

### v32: ROC — H+c vs Key Backgrounds
<split even>

![[Images/all_trainings/v32_kappa_hce/roc/roc_default_hplusc_vs_hplusb.png|1000]]

![[Images/all_trainings/v32_kappa_hce/roc/roc_default_hplusc_vs_vjets.png|1000]]

</split>

---

### v32: $D_\kappa$ Score Distribution (H+c vs grouped backgrounds)

![[Images/all_trainings/v32_kappa_hce/score_distribution_D_kappa.png|1400]]

$D_\kappa = P_\text{sig} / (P_\text{sig} + \sum_j \kappa_j P_j)$ — optimized kappas from differential evolution at 50% efficiency

---

### v32: $D_\kappa$ Signal vs Background (log scale)
<split even>

![[Images/all_trainings/v32_kappa_hce/score_distribution_D_kappa_sig_vs_bkg.png|1000]]

![[Images/all_trainings/v32_kappa_hce/score_distribution_D_kappa.png|1000]]

</split>

---

### v32: Confusion Matrix (4-class, unweighted, median-normalized $D_\kappa$)
<split even>

![[Images/all_trainings/v32_kappa_hce/inference/confusion_matrix_4class_Dkappa_true.png|1000]]

![[Images/all_trainings/v32_kappa_hce/inference/confusion_matrix_4class_Dkappa_pred.png|1000]]

</split>

Classification via per-group $D_\kappa$ normalized by median, then argmax. H+c recall = 46.4%.

---

### v32: S/$\sqrt{B}$ vs Signal Efficiency

![[Images/all_trainings/v32_kappa_hce/inference/sqrtb_vs_efficiency_Dkappa.png|1400]]

| Metric | Yield-weighted | Unweighted |
|---|---|---|
| Peak S/$\sqrt{B}$ | 0.0150 $\pm$ 0.0180 | 5.41 |
| At efficiency | 96% | 45% |

Yield-weighted uses cutflow yields: H+c=1.49, $t\bar{t}$=197K, Higgs bkg=1080, EW bkg=24.6K

---

### AUC Comparison: Development History

| Metric | v10 | v11 | v20 | v25 | v28 | v31 | **v32** |
|---|---|---|---|---|---|---|---|
| hplusc\_vs\_all | 0.51 | 0.966 | 0.973 | 0.968 | 0.972 | 0.975 | **0.975** |
| higgs\_vs\_all | — | — | 0.903 | 0.772 | 0.801 | 0.792 | **0.796** |
| hplusc\|higgs | — | — | 0.857 | 0.863 | 0.873 | 0.887 | **0.887** |

- v10$\rightarrow$v11: Fixing class imbalance by merging higgs sub-classes (AUC 0.51$\rightarrow$0.966)
- v11$\rightarrow$v20: Adding discriminant-aware significance loss (AUC 0.966$\rightarrow$0.973)
- v20$\rightarrow$v32: Kappa HCE with dynamic groups and curriculum learning (AUC 0.973$\rightarrow$0.975)

---

### S/$\sqrt{B}$ Comparison (unweighted, optimized $\kappa$)

| Efficiency | v11 | v20 | **v32** |
|---|---|---|---|
| 10% | 3.29 | 3.70 | — |
| 20% | 4.12 | 4.51 | — |
| 30% | 4.57 | 4.93 | — |
| 50% | 4.82 | **5.21** | **5.41** |
| 70% | 4.66 | 4.88 | — |
| 90% | 3.68 | 3.77 | — |

v32 peak S/$\sqrt{B}$ = **5.41** at 45% efficiency — **+12.2%** over v11 (4.82) and **+3.8%** over v20 (5.21)

---

### Loss Function Evolution Summary

| Version | Loss | Key change | Outcome |
|---|---|---|---|
| v10 | CE (13-class) | Fine-grained classes | FAILED (AUC 0.51) |
| v11 | CE (6-class) | Merge higgs bkg | AUC 0.966, no fine-grained info |
| v12-v13 | Hierarchical CE | $\mathcal{L}_\text{global} + \lambda \mathcal{L}_\text{fine}$ | AUC 0.951-0.961 |
| v17-v19 | HCE + significance | Add $-S/\sqrt{B}$ or $\log(B)$ | Kappa collapse issues |
| v20 | HCE + discriminant | $-\log(D) + \log(1+D)$ | AUC 0.973 (breakthrough) |
| v25-v28 | Kappa HCE | Dynamic groups from $\cos_\text{sim}$ | AUC 0.968-0.972 |
| **v32** | **Kappa HCE (tuned)** | **50 epochs, $\tau=0.3$** | **AUC 0.975 (best)** |

---

### Key Takeaways

1. **Standard CE fails** with extreme class imbalance (13 classes, H+c = 0.06% of data)
2. **Hierarchical structure** enables fine-grained classes without collapsing (v12-v13)
3. **Discriminant-aware loss** ($-\log D + \log(1+D)$) directly optimizes the analysis observable
4. **Learned $\kappa$** from cosine similarity provides physically meaningful class grouping
5. **Dynamic curriculum**: model starts broad, narrows focus to signal-like classes
6. **v32 achieves best AUC (0.975)** while retaining all 13 fine-grained classes
7. Charm tagging variables (CvsB, CvsL) are the dominant discriminating features

---

### Next Steps

- Train a version with 2D tagging (running into lxplus issues with the new config with the included features)
- 2D fit using $D_\kappa$ score distribution
- Extend to 2024 data (Run 3, NanoAODv15) once H+c signal MC is available

---
