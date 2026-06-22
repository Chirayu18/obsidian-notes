---
theme: black
transition: slide
enableMenu: true
enableSearch: true
height: "1080"
width: "1920"
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

| Category | Variables |
|----------|-----------|
| Kinematic | dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt |
| Transverse mass | mtl1, mtl2, dilepton_mass |
| $\Delta R$ | delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c |
| $\Delta\phi$ | delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET |
| Charm tagging | cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet |
| Secondary vertices | nSV |

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

| Process | Category |
|---------|----------|
| ggH$\rightarrow$WW, VBF H$\rightarrow$WW, WH$\rightarrow$WW, ZH, ggZH, ttH(nonbb), ttH(bb), H+c, H+b | higgs |
| tt | tt |
| Single top | st |
| WW, WZ, ZZ | diboson |
| DY(NLO), W+jets, V+jets, Electroweak | vjets |

---

### Corrections Applied

- **Object**: JEC, muon scale/smearing, electron scale/smearing
- **Event weights**: genWeight, pileupWeight, partonshowerWeight, lhepdfWeight, lhescaleWeight, nnlopsWeight
- **Lepton SFs**: muon ID(tight) + ISO(tight), electron ID(wp80iso) + reco

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

