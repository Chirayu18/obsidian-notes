---
tags: [reference]
status: active
date: 2026-09-24
source: lxplus
---

# LM-kT (learned-metric kT): the GNN-guided ceiling

Follows [[2026-09-24-nopair-arms-final]]. Those arms concluded that the pairwise bias's value lies in pair *selection*, not pair *description*. LM-kT attacks that directly: a clustering that learns which pairs belong together.
Scope, as the user decided: **GNN only (the ceiling)**. The distilled student and the Phase-2 physics-loss fine-tuning are deferred. The IRC-unsafe comparison GNN was dropped.

## Method

- **Clusterer.** `flashjet.lmkt.cluster_lmkt` (branch `lmkt`, commit `0bddc57`, local, not pushed).
  - It is generalised kT with a bounded learned factor on the pair distance:
    d_ab = min(kt^2p)·ΔR²/R² · exp(clip_c(g_ab)).
  - g_ab is the **pT-weighted average** of a particle pair matrix G over the constituents of a and b. It is kept exactly through the recombination by adding rows and columns on each merge.
  - Substructure mode: C/A, p=0, reclustering each AK8 jet into one tree.
- **G.** From an energy-weighted message-passing GNN (`lmkt/ewmp.py`, 119k parameters). The GNN is IRC safe:
  - pT enters only as the attention weight z_j;
  - node inputs are PID and direction;
  - the graph is radius-based (no kNN).
- **Targets are hierarchical:** "same prong", plus "same W" (the two W quarks inside a top). G = −(ℓ₀+ℓ₁)/2.
  - A flat same-prong target cannot order b | (q q′). With it, the truth oracle paired the W quarks correctly only 29% of the time.
- **Tests** (`tests/test_lmkt.py`, 22 pass):
  - c=0 is bit-for-bit the torch backend (anti-kt, C/A, kt);
  - the batched code matches a brute-force implementation of the definition;
  - IRC harness;
  - a count-weighted control, which the harness must flag and does.
- **Data.** JetClass stores only the resonance, not its decay quarks, so it can't give prong labels.
  - Own Pythia 8, truth level, 13.6 TeV: W′→WZ (hadronic), tt̄ all-hadronic, QCD.
  - AK8 jets with pT 500–1000 and |y|<2, top 128 constituents.
  - Labels: nearest decay quark, or unassigned if ambiguous (3–4% of pT).
  - Samples: 163k train, 27k val, 27k test.
  - Check: labelled-particle masses are W 81.6, Z 91.9, top 170.6 GeV.
- **Training.** 12 epochs on lxplus905 (T4), 400 s/epoch. Final val same-prong accuracy is 96.5%, with pairs weighted by z_i·z_j and classes balanced; "always same" scores 0.64.

## Results (test set, 27k jets)

**Pair level** (z-weighted same-prong AUC, signal jets):
- The GNN logit scores **0.999**, against 0.983 for ΔR alone (which ParT already has).
- Scored by lowest-common-ancestor merge order, the LM-kT c=4 tree scores 0.882, against C/A's 0.869.
- So the tree keeps the prong-level structure but not the fine ordering inside prongs.

**Versus the kt family** (val, epoch-7 checkpoint, the training accuracy metric):
- kt told the true k scores 0.979, but that uses a hint: QCD is free with k=1. With k fixed it drops to 0.86 (k=2) or 0.80 (k=3).
- The GNN scores 0.968 without being told k. On signal jets it matches or beats kt even with kt's hint: W 0.982 vs 0.969, Z 0.981 vs 0.974, top 0.970 vs 0.971.
- C/A and anti-kt, ungroomed, are near trivial (0.69 and 0.64).

**Tree quality** (groomed declustering, zcut=0.1):

| metric | C/A | kt | LM-kT c=2 | LM-kT c=4 | truth oracle |
|---|---|---|---|---|---|
| top: W quarks paired correctly | 0.33 | 0.40 | 0.59 | **0.66** | 0.86 |
| top: 3 prongs correct | 0.72 | 0.83 | 0.81 | 0.83 | 0.87 |
| top: W candidate 65–95 GeV | 0.41 | 0.53 | 0.57 | **0.60** | 0.69 |
| W: 2 prongs correct | 0.91 | 0.91 | 0.91 | 0.91 | 0.93 |
| W: groomed m within ±15% | **0.82** | 0.44 | 0.81 | 0.78 | 0.43 |
| QCD: fake W (m 65–105) | 0.108 | 0.274 | 0.105 | **0.096** | 0.108 |

- LM-kT closes about 60% of the C/A-to-oracle gap on top W pairing.
- It adds nothing for 2-prong jets.
- It does not sculpt QCD.
- The oracle's poor W mass window comes from unlabelled UE particles: they are "compatible with everything", so the oracle doesn't groom them. It is not a clustering failure.

**Tagger proxies** (gradient-boosted trees on tree features):

| | acc | top AUC | Hbb AUC | Z vs W |
|---|---|---|---|---|
| Pythia truth, C/A tree | 0.826 | 0.9706 | — | 0.900 |
| Pythia truth, LM-kT c=2 tree | **0.834** | **0.9760** | — | 0.901 |
| JetClass, stored mSD+τ (base) | 0.687 | 0.9691 | 0.9337 | 0.734 |
| JetClass, base + C/A tree | 0.704 | 0.9718 | 0.9416 | 0.740 |
| JetClass, base + LM-kT c=4 tree | **0.708** | **0.9743** | **0.9456** | **0.742** |

- On JetClass, the GNN was trained on truth-level Pythia and applied to Delphes without retraining.
- The gain over C/A is about +0.5 points of accuracy. The statistical error on 50k test jets is about ±0.2 points, so the gain is real but modest.
- It sits in the hierarchy classes, top and Hbb.
- The oracle's tagging number (0.877) is meaningless: every QCD jet is labelled as one prong, so the tree leaks the class.

**IRC on real jets** (1000 signal jets, GNN in float64, 3-prong four-momenta compared to 1e-6):

| perturbation | C/A | LM-kT |
|---|---|---|
| ghosts at 1e-8 | 0.001 | 0.001 |
| ghosts at 1e-10 | 0.001 | 0.000 |
| collinear split at 1e-7 | 0.003 | 0.003 |

- LM-kT's rate equals C/A's at every scale.
- Larger scales (1e-4 ghosts, 1e-3 splits) "fail" for both, because the 1e-6 tolerance is tighter than the perturbation itself.

**Timing** (T4, 512 jets × 128 particles):

| step | time |
|---|---|
| GNN forward | 534 ms |
| LM-kT torch reference, c=0 | 437 ms |
| LM-kT torch reference, c=4 | 639 ms |
| flashjet torch backend C/A | 643 ms |
| flashjet Triton C/A | **4.0 ms** |

- The GNN costs about 130× the fused clustering. At inference that is the student's job.
- The modulation must go into the Triton kernel to keep flashjet speed.

## Verdict

- **A learned, IRC-safe clustering finds genuinely better trees where hierarchy matters**: top W pairing goes from 0.33 to 0.66.
- It gives nothing on 2-prong jets, and it doesn't sculpt QCD.
- **The tagging benefit is small** (+0.5 points over C/A tree features on JetClass). That is consistent with the arm-D lesson that tree summaries add little on top of what a tagger can already infer.
- The real test is **G2**: ParT with no pair bias, plus rank-K groomed-prong membership channels in q/k. That is flash-attention compatible, with no N×N tensor.
  - Compare it with C (84.6) and A (86.2).
  - Membership bits must be **precomputed** (about 10–20 GPU-hours), not computed on the fly, which would make training 3–5× slower.
  - The user approved G2 *after* this evaluation. Not launched yet.

## Where things live

- Code:
  - flashjet `lmkt` branch: `src/flashjet/lmkt.py`, `tests/test_lmkt.py`.
  - Study dir `/eos/user/c/cgupta/flashjet/lmkt/`:
    - `gen_pythia.py` (LCG_107), `make_jets.py`, `ewmp.py`, `train_gnn.py`;
    - `eval_lmkt.py`, `irc_timing.py`, `jetclass_eval.py`, `compare_kt.py`, `plot_lmkt.py`.
- Model: `lmkt/models/ewmp_safe.pt`. Results: `lmkt/results/{summary,irc_timing,jetclass_tagger}.json`. Logs: `lmkt/logs/`.
- Running on lxplus-gpu:
  - Each login goes to a different node, and a node kills a user's processes at logout, so tmux does not survive.
  - Run jobs inside a held ssh session to a named node (lxplus905).
