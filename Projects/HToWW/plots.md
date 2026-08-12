---
tags: [reference]
status: active
date: 2026-07-12
source: lxplus
---

# HToWW — plots

Plot links for the H+c (H→WW) analysis. Large PNGs stay on EOS; only link entries live here.

---

### 2D-CTAG plane with frozen bins + flavour composition

tags: [plot]
Date: 2026-07-19
Description: The 2D-CTAG plane (HFvLF vs BvC) with the 11 official SFbc-2D frozen bins overlaid on
2022postEE MC density (tt+H+c+DY+ST+WW, candidate c-jet, 845k jets), plus zoom insets for the
thin C4/C3/C2 and B1–B4 bands and a per-bin flavour-composition table. Shows that B1–B4 are
empty for the charm-selected candidate. See [[2026-07-19-ctag2d-full-documentation]].
Path: /eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.png

---

### 2D-cat MVA retrain — ROC curves (hplusc vs backgrounds)

tags: [plot]
Date: 2026-07-12
Description: ROC curves for the v11 MVA retrained with the 11 one-hot 2D-CTAG categories
(`cjet_cand_ctag2d_*`) replacing the raw PNet cvsl/cvsb scores. 6 plots: hplusc vs
all / higgsbkg / tt / st / diboson / vjets. AUC(hplusc_vs_all)=0.932 vs baseline 0.928.
Compare with the baseline `hwwcom_multiclass_v11` ROCs in the sibling directory.
Path: /eos/user/c/cgupta/EPR_task/b-hive/output/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/EPR_task/b-hive/output/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/

## Lepton MVA (mvaTTH) 2022EE — ONNX conversion #plot

tags: [plot]
Date: 2026-08-12
Description: ONNX vs TMVA::Reader validation (corr = 1.0000000000); prompt-vs-nonprompt
separation on the eµ selection; and the prompt/nonprompt ROC with working-point markers.
Path: /eos/home-c/cgupta/HToWW/leptonmva
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/leptonmva

- `plot_validation.png` — ONNX vs TMVA::Reader, both flavours, max |Δ| = 2e-07
- `plot_separation.png` — score distributions, prompt vs nonprompt (log y)
- `plot_roc.png` — prompt eff vs nonprompt eff, markers at score > 0.0 / 0.4 / 0.8
