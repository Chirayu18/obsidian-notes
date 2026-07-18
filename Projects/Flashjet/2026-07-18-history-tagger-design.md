---
tags: [reference]
status: active
date: 2026-07-18
source: lxplus
---

# Design: feeding merge histories (C/A + kT + anti-kT) into a b-hive tagger

**Question**: can the *entire* merge history be fed to a tagger, and how would it fit
into the b-hive framework at `/eos/user/c/cgupta/EPR_task/b-hive`? **Design only — not
implemented.** Companion: [[2026-07-18-tagger-inputs]] (scalar-variable study).

## How b-hive taggers take inputs today

From `config/ParT_cls.yml` + `utils/dataset/structured_arrays.py` + `utils/models/particletransformer.py`:

- The YAML config declares **input groups**: `global_features` (flat per-jet vector) and
  per-object **sequences** — `cpf_candidates` (26×20), `npf_candidates` (25×10),
  `vtx_features` (5×15) — each padded to a fixed `n_*_candidates` length, plus `truths`
  (one-hot classes) and pt/eta bins for resampling.
- The dataset task reads those branches from the ntuple into structured arrays →
  padded `(B, N, F)` tensors per group.
- Model side (`InputEmbed`): each group gets its own BatchNorm + conv embedding to a
  common `embed_dim`, then the groups are **concatenated along the token axis** and fed
  to the transformer (ParT variants also take pairwise features `v`/`uu` built from the
  candidate 4-vectors). Class token → MLP → `truths`.

**Key observation**: a merge history is structurally *identical* to what b-hive already
consumes — a variable-length sequence of objects with fixed feature dimension. Each
clustering tree becomes one more input group next to cpf/npf/vtx. No framework surgery
needed; this is config + one ntuple-production change + a small InputEmbed extension.

## What a "history token" is

flashjet's `lund_coordinates` / `splitting_scales` already emit one row per
de-clustering split, ordered (slot 0 = widest), zero-padded — exactly the padded-sequence
format. Per split, the natural token features (all post-reads, GPU-batched):

`(z, ΔR, ln kt, ln 1/ΔR, ln m_split, ln m_heavy/m_split, depth, d_ij)`

- **C/A tree (big-R reclustering)**: the primary declustering sequence = the **Lund
  plane list** — this is precisely LundNet's input (2012.08526), which beat
  image/particle-cloud taggers with fewer parameters. Highest priority group.
- **kT tree**: the exclusive-scale sequence (√d12 ≥ √d23 ≥ …) = prong hierarchy;
  value-sorted, so the first ~10 tokens carry it. Second group.
- **anti-kT tree**: merge order is pt-ordered accretion — less physical splitting
  structure, but its d-sequence encodes the soft/pileup accretion pattern. Cheapest to
  include, lowest priority (or summarize into `global_features` only).

Full-tree (not just primary-branch) option: all N−1 merges as tokens + **tree structure
in the pairwise channel** — ParT's `uu` interaction input can carry (LCA depth, same-branch
flag, ΔR between splits), which turns ParT into a GNN-over-the-tree ≈ LundNet without new
architecture. This is the elegant b-hive-native way to encode the tree.

## Concrete integration sketch (3 touchpoints)

1. **Ntuple production**: run flashjet on the stored constituents at ntuple-writing time
   (validated exact vs CMS FastJet — see [[2026-07-13-cms-validation]]); write per-jet
   `ca_split_*` (pad ~40), `kt_split_*` (pad ~15) branches + the 13 physics functions
   ([[2026-07-18-tagger-inputs]]) as scalars. O(N³) clustering happens once here,
   batched on GPU — same place the current tagvars are computed.
2. **Config** (`config/history_ParT.yml`): add groups
   `ca_splits:` / `kt_splits:` with `n_ca_splits: 40`, `n_kt_splits: 15`; put the 13
   functions into `global_features`; keep cpf/npf/vtx groups as-is (histories *augment*
   candidates, they don't replace them — the tree is derived information the model
   otherwise has to learn to compute from the candidates).
3. **Model** (`utils/models/`): extend `InputEmbed` with two more BatchNorm+InputConv
   branches (pattern-copy of cpf/npf/vtx, ~10 lines each), concatenate their tokens;
   optionally add tree-distance to the pairwise `uu` builder.

## Why this is worth trying

- The scalar study showed the declustering *sequence* carries information beyond mass
  (AUC 0.794 → 0.827 with just 7 counting/sequence scalars, linear model); the full
  token list is the un-compressed version of exactly that.
- The histories are **already computed and exact** — flashjet reproduces CMS's FastJet
  trees to storage precision, so the input is well-defined and re-derivable offline.
- Everything is invariant under longitudinal boosts / azimuthal rotations by
  construction (z, ΔR, kt), which makes it a natural *invariant baseline* for the
  Lorentz-equivariance model comparisons already in this repo (LorentzNet / L-GATr /
  LLOCA) — same training pipeline, same truths, only the input group differs.

## Open questions (for when it's implemented)

- Which sample already has per-candidate + truth info to build history branches from?
  (The b-hive DeepNtuples have candidates; flashjet needs their raw p4.)
- Pad lengths: measured n_lund ≤ ~40 for AK8; AK4 (b-hive's DeepJet samples) will be
  shorter (~15/8).
- IRC safety: token list with a kt > ~0.5–1 GeV floor avoids the NanoAOD table-floor
  noise measured in [[2026-07-17-msd-outlier-anatomy]].
