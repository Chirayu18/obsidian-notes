---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# Arm status + probe results, 2026-09-04 16:00

## Jobs
- CA5    9259275, `jet_class_ca` / `b_hive_paper_compile_4_ca`     — 800k/1M, ends ~22:30 today
- SUBJET 9265170, `jet_class_subjet` / `b_hive_paper_subjet_1`     — 100k/1M, 63 min/checkpoint, ends ~Sun 16:00
- BASELINE done, `jet_class` / `b_hive_paper_compile_4`            — 1M, best val 86.23 @ 980k

Metrics path: `output/TrainingTask/<config>/JetClass_train_100_mod/<version>/ParticleTransformer_Paper_JetClass/epochs_0/nominal`

## CA5 vs baseline — the paired test (do NOT use last-5 means, they mislead)

Paired Δ val ACC (CA5 − baseline), matched iterations:

| block | mean | sem | t |
|---|---|---|---|
| 20–200k | −0.330 | 0.136 | — |
| 220–400k | −0.076 | 0.050 | — |
| 420–600k | −0.119 | 0.053 | — |
| 620–800k | +0.003 | 0.028 | — |

Last 20 matched: **mean −0.058, 95% CI [−0.122, +0.006], t = −1.77, NOT significant.**
CA5 ahead at only **4 of 20**. Verdict: **parity, with a small negative point estimate.**

Same on val LOSS: last-20 mean +0.00107, t = +1.56, also not significant. Loss and
accuracy agree (4/20 both) — no calibration difference between arms.

### Noise levels (converged region, mean |step-to-step|)
| arm | val | train |
|---|---|---|
| BASELINE | **0.089** | 0.206 |
| CA5 | **0.074** | 0.229 |

**Val is ~2.5x LESS noisy than train.** Train is measured with dropout active over a
moving-weights window; val is a clean frozen snapshot. Rank arms on val.

### The derivative finding (the one that complicates the null)
5-checkpoint smoothed dL/d(20k), val loss:
- CA5 descends **faster than baseline at 7 of 9 sampled points** (720k: −1.46e−3 vs −0.62e−3)
- Baseline **flattens after 860k**: −0.22e−3, −0.16e−3, then **+1.26e−3** (positive)
- Baseline's 1M checkpoint (0.3935) is WORSE than 980k (0.3863) — bad final draw

So baseline hit its floor ~880k while CA5 still had slope at 800k. **The arms may not
be at the same stage.** Caveat: the derivative is a smoothed average of a quantity whose
per-step noise (0.0026) exceeds the signal (0.0015). Suggestive, not established.
CA5's final 200k tests it.

Generalization gap (val − train) over 600–800k: baseline +0.0001, CA5 −0.0013.
**Neither arm overfits.** Both are underfit if anything.

Plot: https://claude.ai/code/artifact/29906dd9-f5c4-49ef-aac4-2dede2fad936

## SUBJET arm so far

| iter | Δ val acc | Δ val loss | Δ train loss |
|---|---|---|---|
| 20k | +0.23 | −0.0046 | −0.0065 |
| 40k | +0.06 | −0.0010 | +0.0079 |
| 60k | +0.14 | −0.0042 | +0.0055 |
| 80k | **−0.47** | +0.0096 | +0.0031 |
| 100k | pending | pending | **−0.0064** (train acc +0.223) |

Train-loss deficit shrank monotonically then **crossed ahead at 100k**. Val record
mixed (3 good, 1 bad). Train loss can improve from extra fitting capacity without
generalizing — the 80k checkpoint was exactly that pattern. Val at 100k is the test.

## Probe results (why C/A doesn't help)

**The arity argument.** Lund coords ln(z)/ln(kT)/ln(1/dR) at a splitting are **2-body**
— ParT's `PairEmbed` already computes these for every pair. A subjet mass is **n-body**.

- `share_bp` (do particles i,j merge at the same branch point) recoverable from the
  paper's 4 pairwise features by a small MLP at **AUC 0.87** → C/A tree structure is
  reconstructible from pairwise kinematics.
- rule-C group separation was **92% multiplicity**.
- DeepSets probe: subjet mass R² **0.232** (control 0.95) → subjet features ARE new
  information, not recoverable by pooling.

**BUT — prong test (`prong.py`, val only, 16k jets):**
- `corr(nsub, prong_count) = +0.175`; `corr(nsub, n_const) = **+0.695**`
  → the kT=20 GeV walk does NOT resolve prongs. Tbqq (3-prong) finds median **5.0**
  subjets; Wqq (2-prong) finds **7.0** — backwards, it's tracking multiplicity.
- Tbqq vs Wqq+Zqq AUC: multiplicity floor 0.804 | **2-body control 0.9617** |
  subjet only 0.9553 | both 0.9694 → **gain over control only +0.0077**.
  Subjets carry prong info, but the 2-body channel already has it.

**Per-class at matched 480k (`perclass.py`, 20,046,720 test jets):**
overall 85.625 (BL) vs 85.523 (CA5). |dAUC| ≤ 0.0023 everywhere — **ranking power
identical class by class**. Tbqq (the one place the arity argument left room):
dacc +0.397, **rejection ratio 0.636**, dAUC −0.0005. No top-specific gain.
Rejection ratios <1 for 8/9 classes with flat AUC — mostly the −0.102 accuracy offset
amplified in the tail, but since loss shows no calibration difference, the 480k CA5
checkpoint was probably just genuinely in its −0.119 block. **Redo at 1M.**

## Lim connection (arXiv:1807.03312, 1904.02092; AEI/KIAS talk Nov 2019)
Functional Taylor expansion → leading term is the **two-point energy correlation
spectrum S2**, strictly 2-body. MLP+S2 **matches CNN-on-images** for Higgs vs QCD;
so does the interpretable two-level model. **2-body is sufficient for two-prong.**
Slide 21 (tops): "Two-point correlations are enough [for bq/qq] … Need more information
to fully encode the substructures → higher order correlation? → **utilize subjet
information?**"

Our result is his sufficiency claim confirmed in the transformer regime.
His other open branch — **S3, three-point correlations** — is untried, permutation-invariant
by construction, needs no clustering, and is genuinely 3-body. Cheapest next arm.

## Encoding ideas not yet tried
1. **Subjets as TOKENS** (not per-particle columns): append ~8 subjet tokens carrying
   (m, pT frac, n_const, eta, phi). Then PairEmbed computes subjet–subjet features for
   free — a subjet-pair mass is 2-body on subjet tokens but 6–10-body on particles.
   This is the one construction that is NOT a re-encoding of 2-body info.
   NB: `capair` (`flashjet_ca_pair_features.py`, N_CA_PAIR_FEATURES=2, MIN_GROUP=3) put
   *particle-pair* C/A features into the attention bias — different thing, and it only
   ever ran as `smoke_capair_v1` (20 iters, val acc 0.101 = random). No verdict from it.
2. Segment IDs / attention masking on subjet membership — weaker.
3. **Fix the walk first** — fixed kT=20 GeV is why nsub tracks multiplicity.
   pT-scaled threshold, or exclusive-kT with fixed N (2 or 3). Option 1 built on the
   current walk inherits its defect. Cheap to test with `prong.py`.

## Housekeeping
- `utils/flashjet_subjet_features.py` is **UNTRACKED in b-hive git** (flagged 3x)
- Root-termination bug fixed 2026-09-04 (was giving 18.5% of constituents the WHOLE
  JET as their subjet); backup at `.bak_rootbug`
- Vault commits f99e29a, 8f8fc7d are local-only; I cannot push
