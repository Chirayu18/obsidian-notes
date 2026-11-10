---
tags: [reference]
status: active
date: 2026-11-10
source: laptop
evidence: agent-reported
---

# HToWW κ-HCE: the saved event-yield-weighted comparison favours v32-v9

**Agent-reported.** Chirayu clarified that HToWW should be assessed with the event-weighted S/sqrt(B) ratio, then delegated the choice of saved comparison with “do ur best”. The most directly relevant saved artifact found is `plots/new_v9_v11/sb_vs_eff_overlay.png`, from `/eos/user/c/cgupta/HToWW/b-hive/scripts/make_new_plots.py`. Its central curves favour κ-HCE v32-v9 over six-class CE v11. At the historical 50% count-based signal-efficiency point the ratio is **1.14420 (+14.42%)**. This corrects any implication that the Flashjet replica established κ-HCE was worse on HToWW's intended weighted metric.

The result is descriptive evidence for the **complete HToWW configurations**, not an isolated or independently validated benefit of the loss. No training, resubmission, model change, weight change, push or PR was performed in this recovery.

## Which versions and artifacts to use

Use the later, 30-epoch pair, not the original March v20/v32 raw-count table:

- κ-HCE: `HPlusCHToWW_kappa_hce/hwwcom_v32_train/hwwcom_kappahce_v32_v9/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt`.
- CE: `HPlusCHToWW_multiclass/hwwcom_v11_train/hwwcom_multiclass_v11/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt`.
- Both model paths are under `/eos/user/c/cgupta/EPR_task/b-hive/output/TrainingTask/`. The former has 13 output classes, the latter six; both use the 17-feature MLP. Current `train_v32.sh` and `train_v11.sh` enable loss weighting. Thus v11 is not the unweighted 13-class CE baseline from the Flashjet replica.
- Paired scored cache: `/eos/user/c/cgupta/HToWW/b-hive/combine_inputs/new_v9v11_scored_2022postEE.parquet` (4,076,514 rows). Both models' scores, truth labels and one shared `w_lumi` column live in the same rows. Era/luminosity label on the saved plot: 2022postEE, 26.7 fb^-1.
- Producer: `scripts/build_v9v11_cache.py`. For each sample, saved event weight is `weight_nominal * coffea_nominal_integral / sum(weight_nominal)`, before dropping invalid feature rows. This recovery preserves those historical weights; it does not certify their cross-section, branching-fraction or luminosity inputs against November conventions.
- Saved plot: [CERNBox: weighted overlay](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/plots/new_v9_v11/sb_vs_eff_overlay.png). A local copy is in `weighted-significance/saved_sb_vs_eff_overlay.png`, ignored by git.

## Recovered numbers

Thresholds reproduce `make_new_plots.py:sb_curve`: percentile of the **unweighted signal scores**, using `>=`. Then S and B are sums of the **signed saved event-yield weights** passing the threshold. The ratio below is Z(v32-v9)/Z(v11), where Z=S/sqrt(B), with the same cache/weights. This is the explicit ratio chosen for the current question; no claim is made that it is an independently recovered original ratio-panel definition.

| Nominal count-based signal efficiency | CE v11 Z | κ-HCE v32-v9 Z | κ-HCE / CE |
|---|---|---|---|
| 5% | 0.00070801 | 0.00123760 | 1.74800 |
| 10% | 0.00120697 | 0.00155162 | 1.28554 |
| 20% | 0.00193482 | 0.00229014 | 1.18364 |
| 30% | 0.00235587 | 0.00273941 | 1.16280 |
| 50% | 0.00267739 | 0.00306346 | 1.14420 |
| 70% | 0.00254041 | 0.00290122 | 1.14203 |
| 90% | 0.00173681 | 0.00218157 | 1.25608 |

At the 50% point, CE has S=0.1375482744 and B=2639.2840685; κ-HCE has S=0.1268837515 and B=1715.4832077. Weighted signal efficiency is therefore **50.28% for CE and 46.38% for κ-HCE**, despite the shared 50% count-based efficiency label. The ratio is not an equal-weighted-efficiency comparison. The finite grid peaks are κ-HCE 0.00318041 at 45.41% nominal efficiency and CE 0.00272256 at 61.94%; these are descriptive grid maxima, not validation-selected operating points.

All numbers come from [[Projects/HToWW/selection-and-mva/weighted-significance/recovered_comparison.json|recovered JSON]], computed read-only from the cache by [[Projects/HToWW/selection-and-mva/weighted-significance/recover_weighted_comparison.py|recovery script]]. Run on lxplus: `python3 recover_weighted_comparison.py > recovered_comparison.json` in the existing numpy/pandas/pyarrow environment (pandas 2.3.3 observed). [[Projects/HToWW/selection-and-mva/weighted-significance/plot_recovered_comparison.py|Plot script]] generates the local ignored `recovered_weighted_ratio.png` from that JSON. No full inference, training, or expensive κ optimization was rerun.

## Evidence and limitations

| Item | Prescription / implementation | Check and observed result | Status |
|---|---|---|---|
| Relevant weighted comparison | Chirayu's 10 November metric clarification; `make_new_plots.py` uses `w_lumi` | Recovered central values from shared cache; visual inspection of original plot agrees in scale and ordering | Agent-reported, computed from existing artifact |
| Event alignment | Both scores, labels and weights must refer to the same rows | Cache has both columns; signal-mask equality asserted; finite scores/weights asserted | Checked at cache level; no persistent event IDs |
| Signs | Preserve signed nominal MC weights | 589/2257 signal rows and 18,574 background rows negative; none clipped | Checked; cancellation affects interpretation |
| Efficiencies | Preserve saved plot convention | Count-percentile thresholds, weighted sums; report actual weighted efficiencies alongside | Checked; weighted-efficiency comparison not substituted |
| Uncertainty | Weighted MC requires sum(w²), not Poisson variance equal to sum(w) | Recovery stores sumw² and fixed-threshold delta-method errors | Diagnostic only; threshold/ratio correlations and systematic uncertainty not evaluated |
| Generalisation | Do not present a full-sample plot as held-out | Cache producer reads all original `hww_MVA/2022postEE` sample rows; no test mask/IDs. Separate held-out inference has 2,203,524 rows for each model | Cache is not established as held-out; cannot claim out-of-sample loss superiority |
| Physics normalisation | Use approved cross sections/BR/SFs, retain process coverage | Cache WH class has 25,437 rows with all weights zero. Original `hww_MVA/2022postEE` and current filelist `hww_combine_fixed` source paths no longer exist at inspected locations | Historical normalization not revalidated; missing/zero contributions preclude production endorsement |
| Loss-only comparison | Match class structure, training inputs, selection and budget | v32-v9 is 13-class κ-HCE, v11 six-class weighted CE; one configuration each | Confounded by class decomposition; missing matched 13-class CE baseline |

The saved plot's uncertainty bands use `sqrt(S/B + S²/(4B²))`, a count-style approximation inappropriate for these general event weights. At the 50% point, fixed-threshold sumw² propagation gives MC-only errors 0.00024594 (κ-HCE) and 0.00018568 (CE). These are individual curve diagnostics, not a significance test of their paired ratio; threshold uncertainty is also omitted. This recovery changes no existing plot or analysis code.

Total saved signed yields are S=0.2735873289, B=101550.4921083. Signal sum|w|=0.5846482828, sumw²=0.0001892916. Negative signal weights mean a naïve cumulative signed-weight quantile need not define a monotonic efficiency curve; the script deliberately does not invent a weighted-quantile prescription or clip weights. Background cancellation is visible too: at 50%, background N_eff=(sumw)²/sumw² is about 259 for κ-HCE and 1120 for CE.

Separate held-out outputs under `output/InferenceTask/{config}/{train_dataset}/{test_dataset}/{version}/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/` contain `prediction.npy`, `truth.npy`, `kinematics.npy`, `process.npy`; no saved per-event physics-weight column was found. Kinematics has only two columns, and the paired cache has neither sample nor event IDs. Matching by row position across the full cache and those test outputs would be unjustified. Rebuilding aligned held-out weights needs recoverable event identity/source inputs; this recovery does not declare that impossible in all archives, only unavailable in the inspected artifacts.

## Use-case statement supported now

**κ-HCE is a promising training-side option for a rare-signal, fine-grained HToWW classifier. The saved HToWW v32-v9 configuration improves the historical event-yield-weighted S/sqrt(B) curve relative to the six-class CE v11 configuration, including a +14.4% ratio at 50% count-based efficiency. This motivates a matched held-out ablation; it does not demonstrate that κ-HCE universally outperforms CE or that its loss alone causes the gain.**

For CMSSW the loss belongs in b-hive training, with the exported network used for inference. A public b-hive PR should document the optional loss, configuration and software checks without publishing internal CMS numbers/plots or asserting a validated performance gain. The remaining decisive evidence is a 13-class CE versus κ-HCE comparison with the same inputs, split, budget and validation selection, evaluated with aligned approved event weights. No new jobs are authorized by this note. The Flashjet result remains separate and unchanged.

Repository inspected read-only: `/eos/user/c/cgupta/HToWW/b-hive`, branch `mva_loss`, HEAD `ce3bdd5e083b547450eee6a7513043be9e993b5b`, dirty checkout left untouched. The JSON records SHA256 of the inspected producer, plotting script and training entry points. Sources also include [[Projects/HToWW/talks/athens/TRANSCRIPT|Athens transcript]], slides 9–10, which describe the yield-weighted optimization and roughly 0.0032 baseline; that narrative's validation-set claim was not verified by this cache inspection. The original March v20/v32 findings in [[Projects/Flashjet/kappa-hce/2026-10-07-kappa-hce-assessment]] concern another model lineage and do not decide this weighted comparison.
