---
tags:
  - hww
  - mva
status: active
---

# MVA

## TODO

- [x] Fix the MVA pipeline [completion:: 2026-02-25]
- [x] Class reweighting [completion:: 2026-02-25]
- [x] Talk to Alex about improving MVA [completion:: 2026-02-25]

---

## Commands

```
cd ~/higgscharm_thomas/higgscharm_thomas_new/higgscharm/
```

```bash
python3 jobs_status.py --workflow hww_MVA --y 2022postEE --eos --hours_ago 11
```

```bash
python3 run_postprocess.py -w hww_MVA -y 2022postEE --postprocess --plot --mva --output_format parquet
```

```bash
#Postproc with no extra
python3 run_postprocess.py -w hww_MVA -y 2022postEE --postprocess --plot --mva --output_format parquet --nocutflow --skipmerging
```

```bash
python3 run_postprocess.py -w hww_MVA -y 2022postEE --output_format parquet --infer --model-path /eos/home-c/cgupta/EPR_task/b-hive/output/TrainingTask/HPlusCHToWW_multiclass/hww_multiclass_v5/hww_multiclass_v5/SimpleMLP_MultiClass/epochs_50/nominal/best_model.pt
```

```bash
python3 scripts/plot_mva.py --input-dir /eos/user/c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/mva_hww_multiclass_v6
```
---

## Log

- Resubmitted jobs for `hww_MVA`
- Resubmitted again: 3 datasets missing, should be done soon
- 1 dataset with missing jobs is expected (HplusBottom)
- Didn't check yet but jobs should be done
- Postprocessing done
- MVA filelist generated at /eos/user/c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/filelists/base.txt

#### hww_multiclass_v2
- Use the filelists from hww_MVA config
- Issue with inputfiles:
  ```
   File "/eos/user/c/cgupta/HToWW/b-hive/utils/coffea_processors/lz4_ttcc_processor.py", line 22, in callColumnAccumulator
    global_arr, cpf_arr, npf_arr, vtx_arr, lt_arr, truth_arr, process = super().callColumnAccumulator(output, events, flag, **kwargs)
                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/eos/user/c/cgupta/HToWW/b-hive/utils/coffea_processors/pf_candidate_and_vertex.py", line 67, in callColumnAccumulator
    global_arr = structured_custom_array_from_tree(
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/eos/user/c/cgupta/HToWW/b-hive/utils/dataset/structured_arrays.py", line 130, in structured_custom_array_from_tree
    arr[key] = np.array(events[key], dtype=[(dtype_name, precision)])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/lib/python3.11/site-packages/awkward/highlevel.py", line 1351, in __array__
    return ak._connect._numpy.convert_to_array(self.layout, args, kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/lib/python3.11/site-packages/awkward/_connect/_numpy.py", line 13, in convert_to_array
    out = ak.operations.convert.to_numpy(layout, allow_missing=False)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/lib/python3.11/site-packages/awkward/operations/convert.py", line 302, in to_numpy
    raise ValueError(
ValueError: ak.to_numpy cannot convert 'None' values to np.ma.MaskedArray unless the 'allow_missing' parameter is set to True
  ```
  - Issue is because nulls present in input files:
  ```md
   ┌─────────────────────┬─────────────┬─────────────┬─────────────┐
  │       Feature       │ tt.parquet  │ H+c.parquet │ WW.parquet  │
  ├─────────────────────┼─────────────┼─────────────┼─────────────┤
  │ cjet_cand_cvsl_pnet │ 52.3% nulls │ 77.5% nulls │ 86.4% nulls │
  ├─────────────────────┼─────────────┼─────────────┼─────────────┤
  │ cjet_cand_cvsb_pnet │ 52.3% nulls │ 77.5% nulls │ 86.4% nulls │
  └─────────────────────┴─────────────┴─────────────┴─────────────┘
  ```
  
- In the next config need to make sure to have atleast 1 cjetcand per event so this error is avoided

- Temporary fix: Filtered parquet files: Files overwritten in place
- Removed Data.parquet, EW.parquet and WG.parquet from the inputfilelist
- Error with merging: changed chunck size to 5M
#### hww_multiclass_v4
- New config for cleanup purposes. Nothing in v3 as well
#### hww_multiclass_v5
- Including new variables from thomas 
- Training done, need to make plots
- Used histogram reweighting
#### hww_multiclass_v6
- Used class reweighting
- Training done, plots need to be added to slides
- Plots: /user/c/cgupta/public/hww_multiclass_v6_slides/slides.md


Plan for next steps:
- [x] Use loss reweighting
- [ ] Add the 2D truth information and proceed as 1 hot
- [x] Add the 2D truth information as my method and proceed [completion:: 2026-04-15]
- [x] Add the other cuts and train
- [x] Train with binary classifier to test
- [ ] Train with ParT
- [x] Process h+b dataset and train with that as well
- [x] Train a MVA with categories: h+c vs other higgs and h+c vs other bkg
     

##### Create new versions of parquet files and corresponding filelists.txts with the following:
- Add the mTll cut in one version ( dont repeat for others )
- Labels for binary classifier ( see the binary classifer code)   my signal would still be all higgs processes background would be all others
- labels like, is_hplusc for H+c processes and similarly for all other higgs processes for other processes labels remain unchanged
  
  Script used:
  `` cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm && python3 scripts/prepare_parquet_versions.py --input-dir /eos/user/c/cgupta/h...
    
  Done: 
  All three versions are done and look correct:

  - v1_mtll_cut/ — 15 files, multiclass labels (is_higgs, is_tt, ...), H+c cut from 2257 → 1899 events
  - v2_binary/ — 15 files, binary labels (is_higgs, is_background), no cuts applied
  - v3_finegrained/ — 15 files, 13 one-hot labels (is_hplusc, is_ggH, is_vbf, ..., is_tt, is_st, is_diboson, is_vjets)
    
#### hww_multiclass_v7 
- Used loss reweighting
- Training done need to make plots
-
Adding cuts mtl2 > 30 and mtll > 60 and mll <=72:
 ┌────────────┬─────────┬────────┬───────────┐
  │  Process   │ Before  │ After  │ Pass rate │
  ├────────────┼─────────┼────────┼───────────┤
  │ H+c        │ 2257    │ 1899   │ 84.1%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ ggH        │ 28476   │ 18388  │ 64.6%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ VBF        │ 69848   │ 40851  │ 58.5%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ ZH         │ 54721   │ 33657  │ 61.5%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ ggZH       │ 104802  │ 52977  │ 50.5%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ WH         │ 25437   │ 14403  │ 56.6%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ tt         │ 3180107 │ 910569 │ 28.6%     │
  ├────────────┼─────────┼────────┼───────────┤
  │ Single Top │ 499001  │ 134738 │ 27.0%     │
  └────────────┴─────────┴────────┴───────────┘
  
  >[!important]
  >Till here loss reweighting performs the best
  >

#### hww_multiclass_v8
- Reduced epochs to 30 as no improvement seen in higher epochs
- Training done with loss reweighting with the signal enriched region as mentioned above
- Performance is worse

##### Inference on signal enriched region with v7
- Performance seems better

>[!todo]
>TODO: change postprocess script to include the relavant input directory\

#### hww_multiclass_v9
- binary classification from v7
#### hww_muticlass_v10
- Finegrained classes like from v7:
  - "is_hplusc"
  - "is_hplusb"
  - "is_ggH"
  - "is_vbf"
  - "is_zh"
  - "is_ggzh"
  - "is_wh"
  - "is_tthnonbb"
  - "is_tthtobb"
  - "is_tt"
  - "is_st"
  - "is_diboson"
  - "is_vjets
Recreated postprocessing parquet files after adding H+c and removed events with no cjet

#### hww_multiclass_v11
- Created v4_hplusc_higgsbkg after adding relavant labels
- Updated bhive config ( need to revert later if needed )
- Instead of :
  truths:
- "is_higgs"
- "is_tt"
- "is_st"
- "is_diboson"
- "is_vjets"
We have:
truths:
  - "is_hplusc"
  - "is_higgsbkg"
  - "is_tt"
  - "is_st"
  - "is_diboson"
  - "is_vjets"

  Filelist: /eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/v4_hplusc_higgsbkg/filelists/base.txt

#### hww_multiclass_v12
- v5_finegrained_higgs created with higgs + finegrained classes
- Implemented the new Hierchical loss function
- Implementation details:
    Files Created

  1. utils/loss/HierarchicalCrossEntropyLoss.py — New loss module with:
    - forward(pred, truth) computing L = L_global + λ × L_fine
    - L_global: sums sub-class probs into group probs, CE over 5 global groups (inverse-freq weighted)
    - L_fine: conditional CE over higgs sub-classes (P(sub)/P(higgs)), only applied to higgs events (background contributes 0)
    - Weights registered as buffers so they follow .to(device)
  2. config/HPlusCHToWW_hierarchical.yml — 12-class config with hierarchical_loss block defining global_groups, fine_group: higgs, and lambda: 1.0

  Files Modified

  3. utils/loss/LossFunctionLoader.py (line 30) — Added "HierarchicalCrossEntropyLoss" case that passes **kwargs to the constructor
  4. utils/weighting/batches.py — Added compute_hierarchical_weights() returning (global_weights, fine_weights, group_indices, fine_group_idx) with
  inverse-frequency weighting for both levels
  5. tasks/training.py — Gated on "hierarchical_loss" in config:
    - Calls compute_hierarchical_weights() instead of compute_class_weights()
    - Constructs HierarchicalCrossEntropyLoss with both weight sets + lambda
    - Existing configs without the key are completely unaffected
  6. utils/models/base_model.py (line 221) — Removed hardcoded loss_fn = nn.CrossEntropyLoss(reduction="none") in predict_model() so the passed-in loss
  function is used
  7. utils/models/simple_mlp_multiclass.py — Stores self.hierarchical_config and updated calculate_roc_list() to produce:
    - higgs_vs_all, higgs_vs_tt, higgs_vs_st, etc. ROCs (using summed P(higgs))
    - hplusc_vs_other_higgs ROC (using conditional P(hplusc|higgs))
    - hplusc_vs_all ROC


#### hww_multiclass_v13
- 5 global groups: charm_higgs (H+c, H+b), top (tt, st, ttHtoBB, ttHnonBB), diboson_like (diboson, WH, ZH, ggZH), gluon_vbf_higgs (ggH, VBF), vjets
- Conclusion: ggH looks similar to charm higgs, 
-   - 5 groups: charm_higgs=[hplusc, hplusb], top=[tt, st, tthtobb, tthnonbb], diboson_like=[diboson, wh, zh, ggzh], gluon_vbf_higgs=[ggH, vbf], vjets
  - Single fine group (charm_higgs only), single lambda
  - hplusc_vs_all AUC: 0.9605
  - hplusc_vs_other_charm_higgs: 0.7872
  - charm_higgs_vs_all: 0.9542

#### hww_multiclass_v13
- New global and fine groups and new scaling factors
 - 5 groups: charm_higgs=[hplusc, hplusb, ggH], top=[tt, st, tthtobb, tthnonbb], h_plus_v=[wh, zh, ggzh, vbf], diboson, vjets
  - Per-group lambdas: charm_higgs=2.0, top=0.1, h_plus_v=0.1
  - Weight boosts: global charm_higgs 2x, fine is_hplusc 2x
  - hplusc_vs_all AUC: 0.9653 (+0.48%)
  - hplusc_vs_other_charm_higgs: 0.7831 (-0.41%)
  - charm_higgs_vs_all: 0.9256 (-2.85%)

  Key findings from v15 diagnostics:

  ┌─────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │        Issue        │                                                           Detail                                                            │
  ├─────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ h_plus_v →          │ 47% of h_plus_v misclassified as charm_higgs. VBF worst (60%). All Higgs production modes share H→WW* decay — features      │
  │ charm_higgs         │ can't distinguish production mechanism                                                                                      │
  ├─────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ charm_higgs → vjets │ 12% leakage, almost entirely ggH (13.6%). The leaking ggH events have hard jets (pT~86), high MET, high nSV — misidentified │
  │                     │  light jets mimicking V+Jets                                                                                                │
  ├─────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ ttH in top          │ Fine — 81-87% correct. Top kinematics dominate over Higgs decay                                                             │
  └─────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


#### hww_multiclass_v18
##### hiarchical config
- Significance term added with kappa but set to 0
##### sig config
- Significance term added
  
   Config differences

  ┌─────────────────────┬──────────────────────────┬──────────────────┐
  │                     │ hierarchical (train_MVA) │ sig (train_MVA2) │
  ├─────────────────────┼──────────────────────────┼──────────────────┤
  │ fine_groups higgs λ │ 2.0                      │ 2.0              │
  ├─────────────────────┼──────────────────────────┼──────────────────┤
  │ significance λ      │ 0.0 (disabled)           │ 100.0            │
  └─────────────────────┴──────────────────────────┴──────────────────┘

  So the hierarchical config has significance turned off (lam: 0.0) — it's the control run. The sig config cranks significance to lam=100.

  Results

  ┌───────────────────────┬───────────────────────┬───────────────┐
  │        Metric         │ hierarchical (no sig) │ sig (lam=100) │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ hplusc_vs_all         │ 0.954                 │ 0.928         │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ higgs_vs_all          │ 0.909                 │ 0.892         │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ hplusc_vs_other_higgs │ 0.855                 │ 0.809         │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ top_vs_all            │ 0.924                 │ 0.900         │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ vjets_vs_all          │ 0.969                 │ 0.951         │
  ├───────────────────────┼───────────────────────┼───────────────┤
  │ diboson_vs_all        │ 0.837                 │ 0.770         │
  └───────────────────────┴───────────────────────┴───────────────┘

  Conclusion

  The significance loss is hurting across the board. With lam=100, the -S/√B term completely dominates — the loss goes deeply negative (-6.5) meaning the
  CE terms (~1.0) are negligible. The model optimizes purely for the discriminant ratio, destroying class separation. Accuracy is ~2% (random).

  Even the lam=1.0 version (v17, which we checked earlier) showed accuracy collapse to ~12%. The fundamental problem: the -S/√B gradient conflicts with
  the CE gradients. The CE wants calibrated probabilities; the significance loss wants to push P(hplusc) up for signal and down for background, regardless
   of the actual class structure.

  The control run without significance loss (hierarchical, lam=0) with the merged 4-group higgs config is actually the best result. The higgs_vs_all gain
  to 0.91 comes entirely from the grouping change, not the significance loss.

  I'd recommend dropping the significance loss and keeping the merged 4-group hierarchical CE as the baseline going forward.
  
  
Bottom line: If your only goal is H+c discrimination, v11's 6-class flat CE is still the best at 0.966. The 13-class hierarchical setup gives you more
  granular information (higgs sub-class separation, top/diboson/vjets ROCs) at the cost of ~1% on hplusc_vs_all
  
  
  ![[Pasted image 20260311191848.png|688]]
![[Pasted image 20260311193922.png]]

![[Pasted image 20260311193939.png]]
---
