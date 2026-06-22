---
theme: black
transition: slide
enableMenu: true
enableSearch: true
height: "1080"
width: "2100"
---
## H$\rightarrow$WW status update
### Chirayu Gupta
#### 19th February 2026

---
### Ran HWW with newly added variables by Thomas
- dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt
- mtl1, mtl2, dilepton_mass
- delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c
- delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET
- cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet, nSV
---

### Event Selection

**Object Selection**
- **Muons**: $p_T > 10$ GeV, $|\eta| < 2.4$, tight ISO, tight ID
- **Electrons**: $p_T > 10$ GeV, $|\eta| < 2.5$, wp80iso ID, $\Delta R(e, \mu) > 0.4$
- **Leptons**: HWW lepton selection (e-$\mu$ pair)
- **Dilepton pair**: Leading $p_T > 20$ GeV, subleading $p_T > 10$ GeV, $p_T(ll) > 30$ GeV, opposite sign, $m(ll) > 12$ GeV
- **Jets**: $p_T > 30$ GeV, $|\eta| < 2.4$, tightLepVeto ID, $\Delta R(\text{jet}, \ell) > 0.4$
- **c-jets**: $p_T > 20$ GeV, $|\eta| < 2.4$, PNet c-tag medium WP, $\Delta R(\text{jet}, \ell) > 0.4$
- **b-jets**: $p_T > 20$ GeV, $|\eta| < 2.4$, PNet b-tag medium WP, $\Delta R(\text{jet}, \ell) > 0.4$

**Event-level (base category)**: good vertex, lumi mask, MET filters, trigger (MuEle/SingleMu/SingleEle), MET $> 45$ GeV, exactly one dilepton pair, e-$\mu$ channel

No $m_ll$ or $m_T$ cuts applied at preselection; 

---

### Training Configuration

**Multi-class Classification**: H+c $\rightarrow$ HWW (signal) vs tt, single top, diboson, V+jets

**Input Features (17 variables)**

| Category           | Variables                                                 |
| ------------------ | --------------------------------------------------------- |
| Kinematic          | dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt |
| Transverse mass    | mtl1, mtl2, dilepton_mass                                 |
| $\Delta R$         | delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c                |
| $\Delta\phi$       | delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET |
| Charm tagging      | cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet                  |
| Secondary vertices | nSV                                                       |

Reweighting: 2D histogram in $(p_T(ll),\, m(ll))$ bins, reference class: higgs

---

### Model Architecture

- **Model**: SimpleMLP_MultiClass
- 3-layer MLP: $128 \rightarrow 64 \rightarrow 32 \rightarrow 5$ outputs
- BatchNorm + ReLU + Dropout(0.2) per layer
- Input: global features only (no particle-flow candidates)

**Hyperparameters**: 50 epochs, batch size 1024, LR $10^{-3}$, CrossEntropyLoss, mixed precision training

---

### Datasets

| Process                                                                                              | Category |
| ---------------------------------------------------------------------------------------------------- | -------- |
| ggH$\rightarrow$WW, VBF H$\rightarrow$WW, WH$\rightarrow$WW, ZH, ggZH, ttH(nonbb), ttH(bb), H+c, H+b | higgs    |
| tt                                                                                                   | tt       |
| Single top                                                                                           | st       |
| WW, WZ, ZZ                                                                                           | diboson  |
| DY(NLO), W+jets, V+jets, Electroweak                                                                 | vjets    |

---

### Lepton $p_T$
<split even>

![[hww_MVA_base_lepton1_pt_2022postEE.png]]

![[hww_MVA_base_lepton2_pt_2022postEE.png]]

</split>

---

### Dilepton Variables
<split even>

![[hww_MVA_base_dilepton_mass_2022postEE.png]]

![[hww_MVA_base_dilepton_pt_2022postEE.png]]

</split>

---

### MET and $\Delta\phi(l_1, MET)$
<split even>

![[hww_MVA_base_met_pt_2022postEE.png]]

![[hww_MVA_base_delta_phi_l1_MET_2022postEE.png]]

</split>

---

### $\Delta\phi(l_2, MET)$ and $\Delta\phi(l_1 + MET)$
<split even>

![[hww_MVA_base_delta_phi_l2_MET_2022postEE.png]]

![[hww_MVA_base_delta_phi_l1PlusMET_c_2022postEE.png]]

</split>

---

### Transverse Mass
<split even>

![[hww_MVA_base_mtl1_2022postEE.png]]

![[hww_MVA_base_mtl2_2022postEE.png]]

</split>

---

### $\Delta R_{ll}$
<split even>

![[hww_MVA_base_delta_R_ll_c_2022postEE.png]]

![[hww_MVA_base_delta_R_ll_l1_2022postEE.png]]

</split>

---

### $\Delta R_{ll,l_2}$ and $n_{SV}$
<split even>

![[hww_MVA_base_delta_R_ll_l2_2022postEE.png]]

![[hww_MVA_base_nSV_2022postEE.png]]

</split>

---

### c-jet Candidate $p_T$ and CvsL
<split even>

![[hww_MVA_base_cjet_cand_pt_2022postEE.png]]

![[hww_MVA_base_cjet_cand_cvsl_pnet_2022postEE.png]]

</split>

---

### c-jet Candidate CvsB
<split even>

![[hww_MVA_base_cjet_cand_cvsb_pnet_2022postEE.png]]

</split>

---

## MVA Training Results Overview

| Version | Key Change                                       | Reweighting                       | Region            |
| ------- | ------------------------------------------------ | --------------------------------- | ----------------- |
| v5      | Baseline 5-class multiclass                      | Histogram (2D $p_T(ll)$, $m(ll)$) | Base              |
| v6      | Class reweighting                                | Class weights                     | Base              |
| v7      | Loss reweighting + signal enriched cuts          | Loss weights                      | Base + $m_T$ cuts |
| v8      | Reduced epochs (50→30), train on enriched region | Loss weights                      | $m_T$ cuts        |
| v9      | Binary: Higgs vs background                      | Loss weights                      | Base              |
| v10     | Fine-grained 13-class (all Higgs separated)      | Loss weights                      | Base              |
| v11<br> | 6-class: H+c vs higgsbkg explicitly              | Loss weights                      | Base              |
Link to all plots: 

---

### v5: Multiclass with Histogram Reweighting

- **5 classes**: Higgs (all processes grouped) vs tt, single top, diboson, V+jets
- **Reweighting**: 2D histogram in $(p_T(ll),\, m(ll))$ bins, reference class: higgs
- **Epochs**: 50, batch size 1024, LR $10^{-3}$

---

### v5: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v5_multiclass_5class_histReweight/training/loss.png|1000]]

![[Images/all_trainings/v5_multiclass_5class_histReweight/inference/confusion_matrix.png|1000]]

</split>

---

### v5: Higgs Score and Breakdown
<split even>

![[Images/all_trainings/v5_multiclass_5class_histReweight/inference/mva_score_higgs.png|1000]]

![[Images/all_trainings/v5_multiclass_5class_histReweight/inference/mva_score_higgs_breakdown.png|1000]]

</split>

---

### v5: ROC
<split even>

![[Images/all_trainings/v5_multiclass_5class_histReweight/roc/roc_default_higgs_vs_all.png|1000]]

![[Images/all_trainings/v5_multiclass_5class_histReweight/roc/roc_default_higgs_vs_tt.png|1000]]

</split>


---

### v6: Class Reweighting

**Change from v5**: Replaced 2D histogram reweighting with **class reweighting**
- Class weights computed from inverse class frequencies — simpler and more stable
- Same 5-class setup, 50 epochs, identical architecture

---

### v6: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v6_multiclass_5class/training/loss.png|1000]]

![[Images/all_trainings/v6_multiclass_5class/inference/confusion_matrix.png|1000]]

</split>

---

### v6: Higgs Score and Breakdown
<split even>

![[Images/all_trainings/v6_multiclass_5class/inference/mva_score_higgs.png|1000]]

![[Images/all_trainings/v6_multiclass_5class/inference/mva_score_higgs_breakdown.png|1000]]

</split>

---

### v6: ROC
<split even>

![[Images/all_trainings/v6_multiclass_5class/roc/roc_default_higgs_vs_all.png|1000]]

![[Images/all_trainings/v6_multiclass_5class/roc/roc_default_higgs_vs_tt.png|1000]]

</split>

> **Conclusion (v6)**: Class reweighting produces better results to histogram reweighting. Serves as stepping stone toward loss reweighting in v7

---

### v7: Loss Reweighting + Signal Enriched Region

**Changes from v6**:
- **Loss reweighting**: per-sample weights folded into the cross-entropy loss during training
- **Signal enriched region cuts** applied at inference: $m_T^{l_2} > 30$ GeV, $m_T^{ll} > 60$ GeV, $m_{ll} \leq 72$ GeV

| Process       | Before cuts | After cuts | Pass rate |
| ------------- | ----------- | ---------- | --------- |
| H+c           | 2257        | 1899       | 84.1%     |
| ggH/VBF/WH/ZH | ~280k       | ~160k      | ~58–65%   |
| tt            | 3 180 107   | 910 569    | 28.6%     |
| Single top    | 499 001     | 134 738    | 27.0%     |

---

### v7: Loss and Confusion Matrix — Base Region
<split even>

![[Images/all_trainings/v7_multiclass_5class/training/loss.png|1000]]

![[Images/all_trainings/v7_multiclass_5class/inferenc/confusion_matrix.png|1000]]

</split>

---

### v7: Higgs Score and Breakdown — Base Region
<split even>

![[Images/all_trainings/v7_multiclass_5class/inferenc/mva_score_higgs.png|1000]]

![[Images/all_trainings/v7_multiclass_5class/inferenc/mva_score_higgs_breakdown.png|1000]]

</split>

---

### v7: ROC — Base Region
<split even>

![[Images/all_trainings/v7_multiclass_5class/roc/roc_default_higgs_vs_all.png|1000]]

![[Images/all_trainings/v7_multiclass_5class/roc/roc_default_higgs_vs_tt.png|1000]]

</split>

---

### v7: Confusion Matrix and Higgs Score — Signal Enriched Region ($m_T^{l_2} > 30$, $m_T^{ll} > 60$, $m_{ll} \leq 72$ GeV)
<split even>

![[Images/all_trainings/v7_multiclass_5class/inference_v1_mtll/confusion_matrix.png|1000]]

![[Images/all_trainings/v7_multiclass_5class/inference_v1_mtll/mva_score_higgs.png|1000]]

</split>

---

### v7: Higgs Score Breakdown — Signal Enriched Region
<split even>

![[Images/all_trainings/v7_multiclass_5class/inference_v1_mtll/mva_score_higgs_breakdown.png|1000]]

![[Images/all_trainings/v7_multiclass_5class/inference_v1_mtll/mva_score_higgs.png|1000]]

</split>

> **Conclusion (v7)**: Loss reweighting performs best among v5–v8. Applying signal enriched region cuts at inference retains 84% of H+c while rejecting ~72% of tt. The breakdown shows significantly cleaner H+c peak in the enriched region. **Best performing multiclass model so far.**

---

### v8: Reduced Epochs + Training on Signal Enriched Region

**Changes from v7**:
- Reduced epochs: 50 → **30** (training loss plateaued — no gain beyond this)
- **Training** itself restricted to signal enriched region (vs. v7 where cuts applied only at inference)
- Same loss reweighting as v7

---

### v8: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v8_multiclass_5class/training/loss.png|1000]]

![[Images/all_trainings/v8_multiclass_5class/inference_v1_mtll/confusion_matrix.png|1000]]

</split>

---

### v8: Higgs Score and Breakdown
<split even>

![[Images/all_trainings/v8_multiclass_5class/inference_v1_mtll/mva_score_higgs.png|1000]]

![[Images/all_trainings/v8_multiclass_5class/inference_v1_mtll/mva_score_higgs_breakdown.png|1000]]

</split>

---

### v8: ROC
<split even>

![[Images/all_trainings/v8_multiclass_5class/roc/roc_default_higgs_vs_all.png|1000]]

![[Images/all_trainings/v8_multiclass_5class/roc/roc_default_higgs_vs_tt.png|1000]]

</split>

> **Conclusion (v8)**: Training on the signal enriched region degrades performance compared to applying cuts only at inference (v7). The model overfits to the restricted phase space. v7 with inference-time cuts remains preferred.

---

### v9: Binary Classification

**Changes from v7**:
- **Binary classification**: Higgs (all) vs background (tt + st + diboson + V+jets lumped together)
- Labels: `is_higgs` / `is_background` — simpler objective
- Based on v7 architecture and loss reweighting
- Tests whether a binary discriminant is competitive with 5-class multiclass

---

### v9: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v9_binary/training/loss.png|1000]]

![[Images/all_trainings/v9_binary/inference/confusion_matrix.png|1000]]

</split>

---

### v9: Higgs Score and Breakdown
<split even>

![[Images/all_trainings/v9_binary/inference/mva_score_higgs.png|1000]]

![[Images/all_trainings/v9_binary/inference/mva_score_higgs_breakdown.png|1000]]

</split>

---

### v9: ROC
<split even>

![[Images/all_trainings/v9_binary/roc/roc_default_higgs_vs_all.png|1000]]

![[Images/all_trainings/v9_binary/roc/roc_default_higgs_vs_background.png|1000]]

</split>

> **Conclusion (v9)**: Binary classifier provides a simpler discriminant but loses per-class separation power. Particularly v+jets is identified as higgs

---

### v10: Fine-grained 13-class Classification

**Changes from v7**:
- **13 one-hot classes** — every Higgs production mode gets its own label:
  - Signal: `is_hplusc`, `is_hplusb`
  - Higgs bkg: `is_ggH`, `is_vbf`, `is_zh`, `is_ggzh`, `is_wh`, `is_tthnonbb`, `is_tthtobb`
  - Bkg: `is_tt`, `is_st`, `is_diboson`, `is_vjets`
- Goal: directly discriminate H+c from all other Higgs production modes

---

### v10: Loss and Confusion Matrix
<split even>

![[Images/all_trainings/v10_finegrained/training/loss.png|1000]]

![[Images/all_trainings/v10_finegrained/inference_v3/confusion_matrix.png|1000]]

</split>

---

### v10: H+c Score and Breakdown
<split even>

![[Images/all_trainings/v10_finegrained/inference_v3/mva_score_hplusc.png|1000]]

![[Images/all_trainings/v10_finegrained/inference_v3/mva_score_hplusc_breakdown.png|1000]]

</split>


> **Conclusion (v10)**: Fine-grained classification enables separation of H+c from individual Higgs backgrounds. More classes means more confusion per class due to limited statistics.

---

### v11: H+c vs Higgs Background — 6-class

**Changes from v10**:
- **6 classes**: `is_hplusc`, **`is_higgsbkg`** (all other Higgs grouped), `is_tt`, `is_st`, `is_diboson`, `is_vjets`
- Merges all non-H+c Higgs into a single "higgsbkg" class — targeted at the specific analysis need
- Uses dedicated `v4_hplusc_higgsbkg` parquet files with updated labels
- Key new discriminant: H+c vs Higgs background ROC

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

### v11: Higgs Background Score and ROC vs All
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/inference_v4/mva_score_higgsbkg.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_all.png|1000]]

</split>

---

### v11: ROC — H+c vs Higgs Background and vs tt
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_higgsbkg.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_tt.png|1000]]

</split>

---

### v11: ROC — H+c vs Other Processes
<split even>

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_diboson.png|1000]]

![[Images/all_trainings/v11_hplusc_higgsbkg/roc/roc_default_hplusc_vs_st.png|1000]]

</split>

> **Conclusion (v11)**: Explicit H+c vs higgsbkg separation provides a targeted discriminant for the key irreducible Higgs background. The breakdown shows H+c is well-separated from individual Higgs processes.

---
### Training versions with 2D tagging
- Had to rerun the processing to add missing variables
- Continuously ran into xrootd issues for few backgrounds
- The code is implemented, need to fix/wait for all the backgrounds to process before giving a result for these trainings
---

## 2024 MC Samples (Run 3, NanoAODv15)

**Campaign**: `RunIII2024Summer24NanoAODv15` — GT `150X_mcRun3_2024_realistic_v2`

<split even>

**Available ✓**
- tt (TTto2L2Nu, TTtoLNu2Q, TTto4Q)
- Single top: tW, s-channel, t-channel (new 4FS naming)
- Diboson: WW, WZ, ZZ (inclusive + exclusive)
- WGamma (inclusive + PTG-binned)
- ggH→WW, VBF H→WW, ggH→ττ
- ttH (bb, nonbb, Hto2C, Hto2G, HtoZG, HtoNon2B — new)
- gg→ZZ continuum, triboson (ZZZ, WZZ, WWZ)
- V+jets: **PTLL/PTLNu-binned only** (inclusive DY and W+jets **not available**)

**Missing ✗**
- ZH→WW, ggZH→WW, WH→WW *(not in 2024 NanoAODv15)*
- VBF H→ττ, WH→ττ *(not available)*
- ZH→ZZ→4L, bbH→ZZ→4L *(not available)*
- **H+c, H+b signal** *(private production needed — not centrally available)*
- **2024 data** NanoAODv15 *(not yet processed)*
- DY inclusive MLL-50, W+jets inclusive *(only binned versions exist)*

</split>

---

### 2024 MC: Key Naming & Structural Changes

| Item | 2022 | 2024 |
|------|------|------|
| Mass point | `M-125` | `Par-M-125` |
| t-channel single top | 5FS `TQbar`/`TbarQ` | 4FS `TBbarQ`/`TbarBQ` |
| DY+jets | Inclusive MLL-binned | Only PTLL-binned (Bin-MLL-50-PTLL-100/200/400/600) |
| W+jets | Inclusive | Only PTLNu-binned (Bin-PTLNu-100/200/400/600) |
| Muon data stream | Single `Muon` | Split `Muon0` + `Muon1` |
| Data eras | D–G | B–I |
| WZtoL3Nu generator | amcatnlo | powheg |
| TTWW generator | madgraph-madspin | madgraph |
| Triboson naming | `ZZZ`, `WZZ`, `WWZ_4F` | `ZZZ-5F`, `WZZ-5F`, `WWZ-4F` |

> Cross sections marked **VERIFY** (t-channel single top, WGamma inclusive, PTLL/PTLNu-binned DY/W+jets) need checking against latest XSDB/twiki.

Full spreadsheet: [2024 MC samples documentation](https://cernbox.cern.ch/s/a485yHglnoLrHtQ)

---

### higgscharm Framework: MVA Integration Changes

**Branch**: [`theumesvl/higgscharm` — `mva`](https://github.com/theumesvl/higgscharm/tree/mva)


**`run_postprocess.py`**
- Added `--mva` flag: merges parquets per process, attaches one-hot truth labels (`is_higgs`, `is_tt`, `is_st`, `is_diboson`, `is_vjets`) and training weight, generates `filelists/base.txt` for b-hive
- Added `--infer` flag + `--model-path`: loads `best_model.pt`, scores all process parquets, writes copies with `mva_score_*` columns to `mva/` subdirectory (originals untouched)
- Both steps can be run together in a single command

**`analysis/postprocess/utils.py`**
- Added `PROCESS_GROUPS`: ordered list of class names (defines label order)
- Added `PROCESS_TO_GROUP`: maps physics process names → class names
- `PROCESS_GROUP_IDS` computed automatically; must stay in sync with b-hive config `truths:` field
- Changing classes = update both `PROCESS_GROUPS` here **and** `truths:` in `HPlusCHToWW_multiclass.yml`

---

