---
tags: [reference]
status: active
date: 2026-10-01
source: lxplus
---

# Learned recursive jet clusterer: v1 status (2026-10-01)

Context: [[2026-09-24-lmkt-gnn-ceiling]], [[2026-09-25-lmkt-algorithm]], [[2026-09-25-part-pairbias-anatomy-and-tree-substitution]].
Code and data: `/eos/user/c/cgupta/flashjet/learned_clusterer/`.

## Bottom line

- The pipeline works end to end. That covers truth labels, the model, the batched merge engine, teacher-forced training, DAgger training and the evaluation against C/A, kt and LM-kT. All tests pass.
- **On T4-scale training (20k jets, 2 epochs) the learned tree does not yet beat LM-kT.**
  - Top W pairing: learned 0.354 (DAgger), C/A 0.341, LM-kT 0.654.
  - The learned tree is 30x slower per jet than the clustering baselines.
- **Diagnosis (measured):** the judge orders *consistent* merges as well as the teacher does. When its argmax is restricted to truth-consistent pairs it reaches top W pairing 0.81, against 0.78 for the teacher. The loss comes entirely from **free-running cross-prong errors that compound**:
  - 0.1% of free-running top trees have no prong-level violation;
  - the first violation comes at a median of 45% of the merge sequence.
- DAgger roll-in helps: top W pairing goes from 0.278 (pure teacher forcing) to 0.354. A full-data H100 run with DAgger is queued (condor **9478441**).

## Model (whiteboard design, as implemented in `clusterer.py`)

Each step works on the current pseudojets D_0..D_{n-1}:
1. An MLP embeds node features computed from the current 4-vector: ln pT, ln E, ln z, ln E/E_jet, Δy, Δφ, ΔR to the axis, ln m, ln n_constituents, and the pT fractions per PID token.
2. This is concatenated with the carried encoder state c, then passed through a Linear layer.
3. Then 3 ParT blocks: d = 64, 8 heads, with a pair bias from (ln kT, ln z, ln ΔR, ln m²) of the current pseudojet pairs.
4. A symmetric judge scores each pair from (h_a + h_b, h_a ⊙ h_b, pair embedding).

Exactly one pair merges per step, with an E-scheme sum. The merged object carries c = h_a + h_b, and every other object carries its own h. There are n−1 steps per jet. The output is the merge history in the flashjet schema, so `lmkt` metrics apply unchanged. The model has 195k parameters.

It is not IRC safe, because ln pT and ln E are inputs. That was not required here.

## Truth labels

Labels come from `gen_pythia_v3.py`. It regenerates `lmkt/data2` event by event (same seeds; 4-vectors checked identical), with corrected ancestry.

**The v2 bug:**
- `isAncestor()` stops at partons with two mothers (status-73 merges).
- So whole string pieces became "unassigned": 8.7% of W-jet pT.
- v3 walks all mothers instead. That reduces unassigned pT to:

| jet | unassigned pT (v2) | unassigned pT (v3) |
|---|---|---|
| W | 0.087 | 0.017 |
| top | 0.107 | 0.028 |
| QCD | 0.136 | 0.050 |

- v3 only fills labels where v2 said −1; no v2 label changed (`check_v3.py`).

**Per-constituent label** `anc`:
- decay quark k of the resonance: top b = 0, W quarks = 1 and 2; W/Z quarks = 0 and 1;
- 3 = radiated by the top line before its decay;
- −1 = unassigned: ISR, MPI, remnant, or the other resonance.
- For QCD, the label is which of the two hard 2→2 partons the particle descends from.

**Hierarchy:**
- top: root → {R → {b, W → {q, q′}, top-radiation…}, unassigned…}
- W/Z: R → {q, q′}
- QCD: R → {P0[, P1]}

A merge is **truth-consistent** iff the union of its leaves is a union of complete children of their lowest common truth node. The vectorised counting implementation equals the set definition on 88k subsets (`test_truth.py`).

**What the labels can specify:**
- the prong partition;
- that the two W quarks join before the b;
- that UE/ISR joins only after the whole resonance system.

**What they cannot specify:**
- **The order inside a prong.** A prong is a flat set. The tie-break is the teacher, a truth-constrained C/A that executes the consistent pair with the smallest ΔR². This is a convention, trained with a weight of 0.25.
- **The hadron → parton step.** A hadron is attached to the nearest parton of its string in (y, φ). String fragmentation has no unique parent, so this is a convention.
- **Ambiguous two-mother merges.** The more energetic mother wins. Flagged pT share: top 1.8%, W 2.7%, QCD 7.5%.
- **QCD second-parton labels.** They carry 3.0% of QCD-jet pT, mostly soft string pieces. The QCD hierarchy is weak.

## Training

The loss is computed per step:
- L_set = −log Σ_{consistent} softmax(s): multi-positive, because truth does not order the consistent pairs.
- plus 0.25 × L_tie, which targets the teacher pair.
- Jet weights are class-balanced.
- Truncated BPTT through the carried state runs over 16 steps, with per-step activation checkpointing. Without it, the first batch went out of memory on a T4.

**DAgger (`--dagger p`):**
- With probability p per jet-step, the model's own argmax is executed even if it is inconsistent.
- The impure pseudojet is then relabelled wholly to its pT-majority truth channel, and the jet totals are recomputed (`Engine.relabel`). This is a convention, not truth.
- `test_relabel.py` uses a random policy and confirms that a consistent pair always still exists (0 of 16k steps without one) and that particle totals are conserved.

## Tests (re-run 2026-10-01 on v3 jets)

- `test_data.py`: all 8 splits are identical to `lmkt/data` in p4, tok, label, cls, jet and nq.
- `test_truth.py`:
  - counting equals the set definition (88,218 subsets);
  - the teacher makes 0 inconsistent merges over 95,969 merges, and 0 truth nodes are missing;
  - with a single prong, the teacher reproduces C/A exactly.
- `test_engine.py`:
  - the engine's C/A equals flashjet C/A on 400 jets, and a brute-force C/A on 40;
  - node p4 equals the sum of leaves;
  - the model policy gives valid trees and is batch-invariant.
- `test_relabel.py`: PASS.

**Finding:** the previous agent's `data/jets_*.npz` had been built from v2 labels, before the v3 generation finished. They were rebuilt from `data3/`; the v2 jets were kept in `data_v2anc/`.

## Results

**Setup:**
- 8000 test jets (2000 per class, rng(1), the same draw as `diag_lmkt.py`).
- The `lmkt` groomed metrics (zcut 0.1) use geometric labels, so they are comparable with the 09-24 numbers.
- Statistical error is about ±0.011 on a W-pairing fraction near 0.35 (2000 top jets).
- Source: `results/eval_t4dag.json`, `results/eval_t4med.json`.

| tree | top W pair | top 3 prongs | top W-cand 65–95 | top m3 ±15% | W m2 ±15% | Z m2 ±15% | QCD fake | ms/jet (T4) |
|---|---|---|---|---|---|---|---|---|
| C/A | 0.341 | 0.732 | 0.421 | 0.714 | 0.820 | 0.797 | 0.107 | 0.8–1.3 |
| kt | 0.393 | 0.834 | 0.529 | 0.782 | 0.450 | 0.532 | 0.278 | 0.8–1.1 |
| LM-kT c=4 | **0.654** | 0.837 | 0.619 | 0.751 | 0.780 | 0.750 | 0.101 | 2.1–2.3 (GNN 1.1) |
| truth oracle (geo) c=8 | 0.868 | 0.868 | 0.699 | 0.776 | 0.440 | 0.523 | 0.107 | 1.0–1.2 |
| teacher TC-C/A (anc truth) | 0.794 | 0.803 | 0.782 | 0.814 | 0.866 | 0.844 | 0.126 | 2.6–2.7 |
| learned, teacher forcing (t4med) | 0.278 | 0.722 | 0.386 | 0.802 | 0.837 | 0.811 | 0.213 | 34.6 |
| learned, DAgger 0.3 (t4dag) | 0.354 | 0.826 | 0.497 | 0.784 | 0.838 | 0.801 | 0.139 | 34.3 |

- Both learned rows used 20k training jets and 2 epochs on a T4.
- With ancestry labels, top W pairing for the learned tree is 0.354 (LM-kT 0.655, C/A 0.352).
- The re-measured C/A (0.341) and LM-kT (0.654) agree with the 09-24 values (0.33 and 0.66).

**Timing:**
- Measured on a shared T4.
- C/A and kt use the flashjet torch reference, not the Triton kernel, so they are not the fast path.
- The learned tree runs n−1 full transformer passes per jet, at batch 256.

**Where the loss is** (`diag_lc.py`, 1000 jets per class):

| policy | top W pair (t4med) | top W pair (t4dag) |
|---|---|---|
| model, free running | 0.273 | 0.348 |
| model, restricted to consistent pairs | 0.786 | 0.810 |
| model, restricted only against prong-level violations | 0.846 | 0.854 |
| teacher | 0.783 | 0.783 |

- In free running, 0.1–0.2% of top trees are free of prong violations; the median first violation comes at 45–47% of the steps.
- The judge is good at ordering. It is not robust off its training distribution.
- Teacher-forced step accuracy plateaus near 0.85 by about epoch 1 of 20k jets (val ≈ train).
- `--w_risk 5 --rollin 0.5` gave free-running top W pairing 0.287 against 0.273. That is no real gain; not pursued.

## Running

- Condor **9478441**: H100 NVL, one job, `~/flashjet_condor/lc_train.sub` and `run_lc_train.sh`.
  - Arguments: full training set (163k jets), 12 epochs, batch size 256, tag `h100_v1`, mid-epoch checkpoints every 100 batches.
  - **It runs with `--dagger 0.3`.** That became the train.py default (0.0 → 0.3) after the T4 A/B, while the job was still idle. The job log prints `md5sum train.py`; the DAgger version is `3ac5f154…`. The checkpoint's `args` records the value actually used.
  - Status at writing: idle (queue).
- Evaluate with `python eval_lc.py models/lc_h100_v1_best.pt 2000 results/eval_h100_v1.json`, then `diag_lc.py`.

## Open problems / next steps

1. **Compounding free-running errors are the bottleneck.** Next: raise the DAgger fraction (on a schedule up to about 0.7), and validate on the free-running metric rather than step accuracy.
2. **The step-level label noise floor is unknown.** Is 0.85 step accuracy the floor set by soft-particle labels (the hadron→parton convention)? Measure step accuracy versus z of the pair. A z-gated "don't care" for soft particles would be a definition change, so it must be documented.
3. **Cost.** 34 ms/jet against about 1 ms for C/A. The O(n) steps × O(n²) pair work per step is inherent to the design. Merging several non-conflicting pairs per step would break "exactly one merge per step", which needs the user's call.
4. If the H100 run does not clear LM-kT, the honest conclusion is that a pair-GNN plus constrained clustering (LM-kT) is a stronger and cheaper way to use the same truth.
