---
tags: [reference]
status: active
date: 2026-09-24
source: lxplus
---

# No-pair arms C / E / F: final 1M results. Nothing we tried replaces the pairwise bias.

Follows [[2026-09-11-plum-final-verdict]] (arm P) and [[2026-09-04-ca-1M-verdict-and-pairwise]] (arm D).
All arms use identical settings: JetClass_train_100_mod, 1M iterations, batch 512, Ranger lr 1e-3, torch.compile, H100 NVL.
Test set: JetClass_test_mod, 20,049,152 jets.

## Arms

| arm | model | pairwise bias U_ij | extra info |
|---|---|---|---|
| A | ParT (baseline) | ON | — |
| P | PLuM | ON | 48 kT Lund tokens |
| D | ParT + C/A node features | ON | 5 C/A columns per particle |
| C | ParT without pair bias | **OFF** | 5 C/A columns (ln kT, ln z, ln 1/ΔR, depth, has_bp) |
| E | PLuM without pair bias | **OFF** | 48 kT Lund tokens |
| F | ParT without pair bias | **OFF** | 6 C/A columns (C + ln m² of the branch-point pair) |

## Final numbers (checkpoint 1M)

| arm | val acc | Δ vs A | test acc | Δ vs A | train wall | throughput |
|---|---|---|---|---|---|---|
| A | 85.952 | — | 86.212 | — | 37.3 h | 7.44 it/s |
| P | 86.064 | +0.11 | 86.206 | −0.01 | — | — |
| D | 85.847 | −0.11 | 86.156 | −0.06 | — | — |
| C | 84.625 | −1.33 | 84.862 | −1.35 | 24.6 h | 11.30 it/s |
| E | 84.582 | −1.37 | 85.161 | −1.05 | ~44 h | 6.17 it/s |
| F | 84.604 | −1.35 | 84.791 | −1.42 | ~24.5 h | 10.87 it/s |

Wall times are wall-clock hours on the Condor node for training plus inference (E: 09/20 22:18 → 09/22 18:29; F: 09/22 00:30 → 09/23 01:03).
Host RAM peaked at 136–141 GB for E and F with a 100 GB request. The request is not hard-enforced at that overshoot.

## Per-class test AUC vs QCD, deltas vs A in units of 10⁻⁴

Noise floor: the within-run late-checkpoint standard deviation is 10.2×10⁻⁴.

| class | D | C | P | E | F |
|---|---|---|---|---|---|
| Hbb | −0.1 | −1.8 | −0.1 | −1.0 | −2.4 |
| Hcc | −0.5 | −18.7 | −0.0 | −15.6 | −14.7 |
| Hgg | −0.6 | −16.3 | −0.1 | −13.1 | −17.1 |
| H4q | −0.3 | −12.4 | +0.3 | −10.1 | −12.4 |
| Hqql | −0.0 | −0.2 | 0.0 | −0.1 | −0.2 |
| Zqq | −0.9 | −31.4 | −0.1 | −27.2 | −26.0 |
| Wqq | −1.3 | −30.7 | −0.0 | −26.5 | −26.1 |
| Tbqq | −0.2 | −3.7 | 0.0 | −2.6 | −4.6 |
| Tbl | 0.0 | −0.0 | −0.0 | −0.0 | −0.0 |

Baseline A absolute AUCs: Hbb 0.99898, Hcc 0.99465, Hgg 0.97194, H4q 0.99393, Hqql 0.99990, Zqq 0.97567, Wqq 0.97899, Tbqq 0.99862, Tbl 0.99998.

## Verdict

- **F − C ≈ 0.** Val −0.02, test −0.07. The per-class AUCs split both ways, all within about 5×10⁻⁴. Adding ln m² recovers nothing, and it does not hurt either. This answers Alex's "why is F worse than C": it isn't, once both are fully trained. The −0.15 gap at 420k was curve wobble.
- **E recovers about 22% of the gap on test** (−1.05 vs −1.35), but not on validation (−1.37). It is the slowest arm at 6.17 it/s, which is slower even than A. It is not a cheap substitute.
- **The loss sits in the classes defined by two-prong mass**: Zqq and Wqq around −26 to −31, then Hcc and Hgg. Classes identified by leptons (Hqql, Tbl) and Hbb are untouched. JetClass has no b-tag score, only raw impact parameters (d0/dz and their errors).
- **Why ln m² couldn't help:** (1) m² ≈ pT_s·pT_h·ΔR², so it is nearly a linear combination of ln kT, ln z and ln ΔR, which were already present. (2) It is the mass of the wrong pair. For most constituents, the C/A branch point is a soft emission inside a prong, not the prong–prong splitting that carries the W/Z mass.
- **Conclusion: the pairwise bias's value lies in pair *selection*, not pair *description*.** All-pairs attention can find the pair whose m² is 80 GeV. Per-particle or per-splitting summaries fix the pair in advance and can't.

## Open follow-ups (not launched)

- Arm B: no pair bias and no extra features. This is the anchor that says how much the bias alone is worth.
- ln Δ-only pair bias (`pairwise_lv_fts_paper`, `num_outputs=1`). If the score stays near 86, the all-pairs structure is what matters; if it drops to about 84.6, the features matter.
- The learned carried-state approach ([[2026-09-24-learned-clustering-teacher-student]]) is the direct attack on "selection": a tree walk that learns which merges are prong–prong.

## Where things live

- Test AUC script: `~/flashjet_condor/final_auc.py` (lxplus AFS). Val curve summary: `~/flashjet_condor/summary.py`
- Runners: `/eos/user/c/cgupta/flashjet/run_paper_{nopair_ca,plum_nopair,nopair_ca_mass}.sh`; submit files in `/eos/user/c/cgupta/flashjet/condor/`
- b-hive branch `cawork`: commits f2c3293 (C), ef5bebe (E), 6b6df43 (F)
- Outputs: `/eos/user/c/cgupta/flashjet/b-hive/output/{TrainingTask,InferenceTask}/<config>/JetClass_train_100_mod/.../<version>/`
