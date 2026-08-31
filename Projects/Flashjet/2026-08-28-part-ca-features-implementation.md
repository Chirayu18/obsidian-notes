---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# Per-particle C/A features in b-hive (+ a note on the JetClass ParT 4-vector ordering)

Implements the per-particle Cambridge/Aachen branch-point features as extra ParT
inputs, computed **live at train time** from flashjet. Two small-scale trainings are
staged on lxplus.

Along the way I flagged the column ordering in `ParticleTransformer2_JetClass` as a
bug and patched it. **That patch has been reverted** — the model is untouched
upstream code. The observation is kept below as a question to settle with the
authors, not as a defect to act on. **Nothing in the CA work depends on it.**

## Open question: which 4 columns ParT uses as its Lorentz vector

`ParticleTransformer2_JetClass.forward` splits its input as

```python
cpf    = cpf_features[:, :, :-4]   # token features
cpf_4v = cpf_features[:, :, -4:]   # fed to PairEmbed
```

`PairEmbed` → `pairwise_lv_fts` → `to_ptrapphim`, which **requires
`(px, py, pz, energy)`**: it computes ΔR, ln kt, ln z and ln m² between every pair.

But the class declared **no `cpf_candidates` attribute**, so `_subselect_features`
took its `else` branch and passed all 23 on-disk columns through **in file order**:

| idx | columns |
|---|---|
| 0–11 | deta, dphi, d0val, d0err, dzval, dzerr, charge, isCH, isNH, isPh, isEl, isMu |
| **12–15** | **part_px, part_py, part_pz, part_energy** ← momenta sit *here* |
| 16–22 | logpt, loge, logpt_rel, loge_rel, deltaR, tanhd0val, tanhdzval |

So `[-4:]` was `[part_loge_rel, part_deltaR, part_tanhd0val, part_tanhdzval]`.

### Verified on real data against pristine upstream code

Extracted `git archive HEAD` to a clean tree (no local patches on `sys.path`) and ran
one real `JetClass_val_mod` file through `get_inpt`:

```
model's cpf_4v columns: ['part_loge_rel','part_deltaR','part_tanhd0val','part_tanhdzval']
for kept real particles:  true pt mean 18.47 / max 577.74
                         wrong pt mean  4.40 / max   7.42
```

The pair features `PairEmbed` actually consumes, averaged over 64 jets:

| | model (wrong) | correct |
|---|---|---|
| ln kt | 2.2283 | 0.7701 |
| ln z | 0.3297 | 0.2195 |
| ln dR | 1.5984 | 0.1836 |
| **ln m2** | **0.0000** | 1.7865 |

`ln kt` correlates only **0.10** with the correct value, and **`ln m2` is identically
zero** — the clamp floors it, because those four columns do not form a timelike
four-vector. That channel of the attention bias carries no information at all.

### Scope — narrower than it first looks

Two things that are **NOT** broken, checked explicitly:

- **The padding mask is correct.** It is `cpf_4v[:, :, 0] == 0`, i.e. `part_loge_rel`,
  which is zero on exactly the padded slots. On a real file: 48150 padded by the
  model vs 48150 correct, **0 real particles wrongly masked, 0 padding wrongly kept**.
  (An earlier synthetic test suggested otherwise; it used non-zero filler in those
  columns and could not resolve this. Real data settles it.)
- **Token features are intact** — `cpf_features[:, :, :-4]` still contains the real
  momenta at indices 12–15, so per-particle inputs are unaffected.

The defect is confined to the **pair-attention bias**.

**Does it matter?** A judgment call. `PairEmbed` is a learned MLP over 4 numbers and
`part_deltaR` is a genuine geometric quantity, so the model trains and gives a
plausible ROC. But the entire point of ParT is the physics-motivated pair bias — three
of its four channels are computed from the wrong inputs and the fourth is dead. If the
target is the ParT paper number, this is not that architecture.

Worth checking: whether the `_orig` variant named in the reference command
(`ParticleTransformer2_JetClass_orig`, absent from this repo) declares the list — that
would suggest this class is a stripped copy.

**Every other model in the repo declares an explicit `cpf_candidates` list with the
kinematic 4-vector last** (e.g. `deepjettransformer.py:393` ends
`..., Cpfcan_pt, Cpfcan_eta, Cpfcan_phi, Cpfcan_e`). The JetClass class was simply
missing one.

**Status: not changed.** A one-line fix exists (declare an explicit
`cpf_candidates` on the class with the momenta last — the pattern every other model
in the repo follows, e.g. `deepjettransformer.py:393`), but it was reverted on the
grounds that the upstream code is likely intentional. Reasons that may be so:

- `PairEmbed` is a *learned* MLP over 4 numbers, not a fixed physics formula; it can
  extract structure from `part_deltaR` and the impact-parameter columns.
- The model is constructed with `build_4v=False`, so it is not asserting these are
  raw momenta the way `ParticleTransformer2` (`build_4v=True`) does.
- Anyone reproducing published numbers with this class would presumably have noticed.

**Worth confirming with Alex/Sitian** before quoting a baseline against the ParT
paper — but it does not block the CA comparison, since both runs share whatever
convention the model uses.

## The features (ascending scan only)

Walk from each leaf up the C/A tree to the **first node where its branch is the
softer child**. The two children there are **pseudojets**; Lund convention, soft-side pT:

    z = pT_soft / (pT_soft + pT_hard)   (<= 0.5)
    dR = dR(soft, hard);   kt = pT_soft * dR

| feature | note |
|---|---|
| `part_ca_lnkt` | ln kt |
| `part_ca_lnz` | ln z |
| `part_ca_lndR` | ln(1/dR) |
| `part_ca_depth` | merges from leaf to root |
| `part_ca_has_bp` | 1 if a branch point exists, else 0 |

**Missing values are a flag, not a sentinel.** A particle always on the harder side
has no such node → all five values 0 with `has_bp = 0`. `ln z` is legitimately
negative (~[-7, -0.69]), so any single "missing" number either collides with real
soft emissions (-1, -6.9) or reads as an extreme measurement (-99). The physical
limits also blow up under logs: z→1 gives ln z = 0, but kt→0 and dR→0 give ∓inf.
Deferred: `survives_SD`, `z_at_SD`.

## Why train time, not a rebuilt dataset

- **No 239 GB rebuild** — only ~265 GB free on EOS; `JetClass_train_100_mod` exists.
- **Feature definitions stay cheap to change.**
- It is the demo Alex asked for: clustering live, overhead measurable as ms/batch.

Verified in the code, not assumed:
- `base_model.py:377` moves the batch to GPU **before** `get_inpt` → `cpf` is already
  CUDA, no extra host↔device copy.
- `get_inpt` reshapes `cpf` to `(B, 128, 23)` — already flashjet's `(B, N, F)` layout.
- Clustering batch size **is** the training batch size; there is no second batching knob.
- `jet_class.yml` declares no npf/vtx/lt → those are zero-width. All 128 particles
  are in `cpf`, so C/A features attach to cpf only.

## Files changed

Repo `/eos/user/c/cgupta/flashjet/b-hive` (backups `*.bak_ca`):

1. **NEW `utils/flashjet_ca_features.py`** — `ca_features_from_cpf(cpf, R)` →
   `(B, N, 5)`. Slices momenta at 12:16, clusters with
   `flashjet.cluster(..., algorithm="cambridge")` (float32 — the triton path has no
   float64), then a pure-torch ascending walk. `_direct_parents` deliberately does
   **not** pointer-jump: the walk needs one hop at a time, unlike flashjet's
   `_resolve_parents` which resolves straight to the root.
2. **`utils/models/particletransformer2.py`** — **unmodified** (patch reverted).
3. **`utils/models/base_model.py`** — compute C/A from the raw cpf, then concatenate
   **after** `_subselect_features` and **before the trailing four columns**, whatever
   those are: ParT-style models split `cpf_features` into `[:-4]` (tokens) and
   `[-4:]` (PairEmbed), so appending at the very end would silently displace the
   model's second input. Width accounting via `ca_feature_length`, which returns 0
   unless a config sets `ca_features` — so every other model and config is inert.
   `calculate_feature_length` is deliberately **left alone** — it drives `input_dims`,
   which reshapes the on-disk array; +5 there would corrupt the read.
4. **NEW `config/jet_class_ca.yml`** — `jet_class.yml` + `ca_features: true`,
   `ca_R: 0.8`. The names are **not** added to `cpf_custom_features` (same trap).
5. **NEW `~/cawork/run_smallscale.sh`** — runs both trainings back to back.

## Verification (all passed)

- **Walk correctness** vs an independent NumPy tree walk:
  `checked 477 particles, 28 with no branch point, MISMATCHES = 0`,
  `ln z max = -0.7011` (≤ ln 0.5 = -0.6931).
- **Plumbing**, both configs: baseline cpf width 23, CA 28, forward pass finite,
  `has_bp frac ≈ 0.97`. Crucially the **trailing four columns are bit-identical
  between baseline and CA**, and the momenta are untouched at 12:16 — so the CA run
  differs from the baseline *only* by the 5 added token features.
- **On-disk layout identical** for both configs —
  `input_dims = [(1,15),(128,23),(0,0),(0,0),(0,0)]` — so both read the same
  prebuilt dataset.
- **law resolves `DatasetConstructorTask` as `existent`** for both configs (symlinks
  into the group area under `output/DatasetConstructorTask/jet_class{,_ca}/`), so
  neither run rebuilds anything.

## Measured overhead (first data point)

Tesla T4, batch 128, `jet_class_ca`:

```
C/A clustering+walk   :  21.24 ms/batch  (166.0 us/jet)
full train step (+CA) : 276.85 ms/batch
clustering overhead   :    7.7 % of the training step
```

**Treat 7.7% as an upper bound.** Three biases all push the same way:
- T4 is flashjet's worst card (6.25% achieved occupancy, 0.32 waves/SM, ~40 SMs).
- Batch 128 is far below the 16k-jet regime the kernel is efficient in.
- The ParT step it is compared against is *also* T4-slowed, which if anything
  flatters the ratio.

**The 166 us/jet needs pre-empting when shown.** The benchmark deck quotes
~0.08 us/jet; that is 16384 jets in one launch. At 128 jets the kernel puts ~128
blocks on the device and per-jet cost is launch-dominated, not work-dominated —
same code, different regime. Anyone comparing the two numbers cold will think
something is broken. Re-measure on A100/H100 at batch 512 before the talk.

## First training result (superseded — pair bias was broken in both arms)

H100 NVL, batch 512, 20k iters each (~2.4 epochs), cluster 9246381:

| | baseline | + C/A |
|---|---|---|
| val accuracy (best) | **80.23%** | 77.86% |
| val loss (best) | **0.5527** | 0.6218 |

C/A **lost by ~2.4 points**, and was behind at every checkpoint. Overhead 7.4%.

Both arms ran with the 4-vector ordering defect (see above), so neither is a real
ParT baseline. Rerun with the fix applied: cluster 9251422
(`train_v4fix_baseline` / `train_v4fix_ca`).

## Why C/A lost — two hypotheses tested, both REJECTED

**1. Feature scale / normalisation — rejected by measurement.** The idea was that
unnormalised C/A columns (ln kt, ln z tails reach ~[-18,+5]) would swamp the O(1)
inputs through `InputConv`'s `RMSNorm` (which normalises across the feature
dimension *jointly*, so it cannot rescale columns individually). Measured RMS on a
real batch:

| column | RMS | | column | RMS |
|---|---|---|---|---|
| `part_d0val` | **10.66** | | `ca_lnz` | 3.88 |
| `part_dzval` | 4.62 | | `ca_lnkt` | 3.63 |
| `part_logpt_rel` | 4.58 | | `ca_lndR` | 3.39 |

The C/A columns are **smaller** than features the baseline already carries, and
adding them attenuates the original 19 by only **×0.889**. Nowhere near enough to
cost 2.4 points. The "[-18,+5]" framing was tail extremes, not typical scale.

**2. The features are uninformative — rejected by a standalone BDT.** Per-jet
aggregation (mean/max/min/std) of the 5 per-particle columns, 6000 jets sampled
across all 50 files, `HistGradientBoostingClassifier`:

Script: `~/cawork/bdt_check.py` (lxplus). 120 jets read from **each of the 50
files** — each `.lz4` holds ONE class, so taking the first N files samples only N
classes; sampling every file is what gets all 10. Runs on the login node in ~12 min.

| features | accuracy | macro-AUC (ovr) |
|---|---|---|
| **C/A only** (5 cols → 20 aggregated) | **40.89%** | **0.7950** |
| a 4-column kinematic subset (→16) | 40.06% | 0.7779 |
| **that subset + C/A** | **49.83%** | **0.8394** |

Per-class AUC from C/A alone follows the predicted decay-structure pattern exactly:

`Tbqq 0.905 > H4q 0.859 > Hcc 0.817 > Zqq 0.811 ≈ Wqq 0.810 > Hgg 0.801 >
Hqql 0.754 > QCD 0.727 > Hbb 0.669`

Strongest on multi-prong decays, weakest on Hbb/QCD — exactly the AK4 expectation,
and the strongest single piece of evidence that the walk is computing real physics.

**Read these two rows with care.** The reference row is **not** the ParT baseline: it
is a 4-column subset chosen for the test — per-particle `pT`, `part_deta`,
`part_dphi`, `part_deltaR` — each aggregated 4 ways. ParT's actual token block is
**19** columns, additionally carrying `d0val/d0err/dzval/dzerr`, `charge`, five
particle-ID flags, the four log-kinematics and two tanh'd impact parameters. In
particular the subset has **no impact-parameter or particle-ID information**, which
is exactly what separates Hbb/Hcc. So "C/A beats kinematics" is true of *that
subset*, NOT of what ParT sees, and must not be quoted as the latter.

The **complementarity** result (+9.8 points) is the robust one: it only requires that
C/A adds information to a kinematic description, which does not depend on the
reference being complete.

Other caveats: 6000 jets; class `Tbl` absent from the sample (the per-class print
loop must index the classifier's own column order, not 0-9, or it raises IndexError);
per-jet aggregation is a cruder use than ParT makes of per-particle inputs.

**Not yet done:** rerunning the reference against the full 19-column token block,
which would make the first two rows directly comparable.

**What remains.** The features carry signal and are not mis-scaled, so the
regression is architecture-level: either ParT's pair bias already supplies this
information *once fed correctly* (which run 9251422 tests, since the old run had it
broken), or an optimisation effect from 24 vs 19 input columns at identical LR.

## Running it

```bash
ssh lxplus-gpu.cern.ch
bash ~/cawork/run_smallscale.sh
```

20k iterations each at batch 512, identical seed; the only difference is the config.
The script first prints the clustering overhead (ms/batch and % of a full training
step), then runs baseline, then C/A.

**Caveat when quoting results:** these train on `JetClass_val_mod`, the *validation*
set. It is a fast signal on whether the features move anything — there is no held-out
set unless we split it, so this is **not** a publishable ROC.

## Expectation, stated up front

From the AK4 study these are **decay-structure** observables: essentially no flavour
separation (AUC ~0.5–0.55, b vs light) but strong separation of boosted decays.
Expect gains on **top/W/Z/H** and little on **q/g, b/c**. Saying this before the run
makes the result credible either way.

Related: [[2026-08-28-bhive-jetclass-part-setup]], [[flashjet-workflow]]
