---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# Per-particle C/A features in b-hive — and a 4-vector ordering bug in the JetClass ParT

Implements the per-particle Cambridge/Aachen branch-point features as extra ParT
inputs, computed **live at train time** from flashjet. Two small-scale trainings are
staged on lxplus. Along the way this uncovered a **pre-existing bug** in
`ParticleTransformer2_JetClass` that would have made the baseline meaningless — see
below, it matters more than the feature work.

## The bug: ParT was reading the wrong 4 columns as its Lorentz vector

`ParticleTransformer2_JetClass.forward` splits its input as

```python
cpf    = cpf_features[:, :, :-4]   # token features
cpf_4v = cpf_features[:, :, -4:]   # fed to PairEmbed
```

`PairEmbed` → `pairwise_lv_fts` → `to_ptrapphim`, which **requires
`(px, py, pz, energy)`**: it computes ΔR, ln kt, ln z and ln m² between every pair.
The padding mask is likewise `cpf_4v[:, :, 0] == 0`.

But the class declared **no `cpf_candidates` attribute**, so `_subselect_features`
took its `else` branch and passed all 23 on-disk columns through **in file order**:

| idx | columns |
|---|---|
| 0–11 | deta, dphi, d0val, d0err, dzval, dzerr, charge, isCH, isNH, isPh, isEl, isMu |
| **12–15** | **part_px, part_py, part_pz, part_energy** ← momenta sit *here* |
| 16–22 | logpt, loge, logpt_rel, loge_rel, deltaR, tanhd0val, tanhdzval |

So `[-4:]` was `[part_loge_rel, part_deltaR, part_tanhd0val, part_tanhdzval]`.
The pair-attention bias was computed from tanh'd impact parameters, and the padding
mask from `loge_rel == 0`. Verified directly, not inferred:

```
has cpf_candidates attr: False
last 4 (model treats as cpf_4v): ['part_loge_rel','part_deltaR','part_tanhd0val','part_tanhdzval']
```

**Every other model in the repo declares an explicit `cpf_candidates` list with the
kinematic 4-vector last** (e.g. `deepjettransformer.py:393` ends
`..., Cpfcan_pt, Cpfcan_eta, Cpfcan_phi, Cpfcan_e`). The JetClass class was simply
missing one.

**Fix**: added an explicit `cpf_candidates` to `ParticleTransformer2_JetClass`,
reordered so `part_px/py/pz/energy` are last. After the fix:

```
baseline  on-disk=23  model cpf width=23  InputProcess dim=19
          last4 == (px,py,pz,E)? True     forward OK, finite
```

> Anyone who ran the JetClass ParT training on this repo trained with a scrambled
> pair-attention bias. Worth telling Alex/Sitian before comparing any numbers.

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
2. **`utils/models/particletransformer2.py`** — explicit `cpf_candidates` (the bug fix).
3. **`utils/models/base_model.py`** — compute C/A from the raw cpf, then concatenate
   **after** `_subselect_features` and **before** the trailing 4-vector, so
   `[-4:]` stays the four-momentum. Width accounting via `ca_feature_length`, added
   to *both* branches of `model_feature_length`.
   `calculate_feature_length` is deliberately **left alone** — it drives `input_dims`,
   which reshapes the on-disk array; +5 there would corrupt the read.
4. **NEW `config/jet_class_ca.yml`** — `jet_class.yml` + `ca_features: true`,
   `ca_R: 0.8`. The names are **not** added to `cpf_custom_features` (same trap).
5. **NEW `~/cawork/run_smallscale.sh`** — runs both trainings back to back.

## Verification (all passed)

- **Walk correctness** vs an independent NumPy tree walk:
  `checked 477 particles, 28 with no branch point, MISMATCHES = 0`,
  `ln z max = -0.7011` (≤ ln 0.5 = -0.6931).
- **Plumbing**, both configs: baseline cpf width 23, CA 28, `last4 == (px,py,pz,E)`
  True in both, forward pass finite, `has_bp frac ≈ 0.97`.
- **On-disk layout identical** for both configs —
  `input_dims = [(1,15),(128,23),(0,0),(0,0),(0,0)]` — so both read the same
  prebuilt dataset.
- **law resolves `DatasetConstructorTask` as `existent`** for both configs (symlinks
  into the group area under `output/DatasetConstructorTask/jet_class{,_ca}/`), so
  neither run rebuilds anything.

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
