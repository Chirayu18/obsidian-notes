---
tags: [reference]
status: active
date: 2026-09-25
source: lxplus
---

# LM-kT: the current algorithm, the oracle, and how it is evaluated

Companion to [[2026-09-24-lmkt-gnn-ceiling]] (results). This note describes the configuration evaluated there: substructure mode, c = 4, zmin = 0.
Code: flashjet branch `lmkt`, `src/flashjet/lmkt.py` (`cluster_lmkt`, `groomed_prong_membership`, `decluster_prongs`). Study scripts are in `/eos/user/c/cgupta/flashjet/lmkt/`.

## 1. LM-kT as it runs now

**Input.** One AK8 jet. Anti-kT R=0.8 defines the jet and is left unchanged. Its constituents are i = 1..n, each with a four-momentum and a PID/charge token.

### Step 0: GNN, once per jet (IRC-safe energy-weighted message passing, `ewmp.py`)

- **Node input:** h_i = embed(PID, charge) + MLP(Δy_i, Δφ_i relative to the jet axis). There are no pT inputs.
- **Three attention rounds** over neighbours with ΔR_ij < 0.8:

      h_i ← h_i + Σ_j α_ij · V h_j,   α_ij ∝ z_j · exp(q_i·k_j + f(ΔR_ij)),   z_j = pT_j / pT_jet

  pT enters only as the attention weight z_j, which is what makes it IRC safe.
- **Pair head:** two logits per pair.
  - ℓ0_ij = "same prong?"
  - ℓ1_ij = "same decay parent?": the two W quarks in a top; every pair in W/Z.
- **Pair score:** G_ij = −(ℓ0_ij + ℓ1_ij)/2.

  | pair | ℓ0 | ℓ1 | G |
  |---|---|---|---|
  | same prong | ≫0 | ≫0 | strongly negative → pull together |
  | W siblings (q, q′ in a top) | <0 | >0 | ≈ 0 → neutral |
  | unrelated (b vs q) | <0 | <0 | strongly positive → push apart |

### Step 1: initialise

Every particle is a pseudojet a, with S_a = pT_a and L_ab = pT_a · pT_b · G_ab.

### Step 2: C/A-style merging, n−1 times

- For every live pair: g_ab = L_ab / (S_a · S_b). This is the pT-weighted average of G over all particles in a × b.
- **Distance:** d_ab = ΔR²_ab · exp(clip(g_ab, −c, +c)). With c = 4 the factor lies between 1/55 and 55.
  - Option `zmin`: apply the factor only if z_ab = min(pT_a, pT_b)/(pT_a + pT_b) > zmin. It is 0 (off) in the evaluated version.
- Merge the pair with the smallest d; ties go to the lowest index. The merged pseudojet has:
  - p = p_a + p_b;
  - S = S_a + S_b;
  - row L_m,· = L_a,· + L_b,· (exact, O(n) per merge).
- Record the merge: parents, child, and (ΔR, z, kT, m², g).
- With c = 0 or G = 0 this is exactly C/A. That is pinned bit for bit to flashjet's torch backend in `tests/test_lmkt.py`.

**Why it is IRC safe.**
- Collinear: ΔR = 0 gives d = 0 whatever g is (g is bounded), so collinear pieces merge first. Their pT-weighted rows add up to the unsplit particle's row.
- Infrared: a soft particle enters every average with weight pT → 0, and the factor is bounded.
- The tests check both, on toy events and on real jets. A count-weighted control, which is not collinear safe, is caught by the same harness.

### Step 3: read out prongs (groomed declustering)

1. Start from the root.
2. Repeatedly open the frontier node that was merged last.
3. If z = min(pT)/sum > 0.1, keep both children. Otherwise drop the softer child (Soft Drop / mMDT, β = 0).
4. Stop at k prongs: k = 2 for W/Z, k = 3 for top.
5. For top, the second accepted split is the W candidate.

## 2. The oracle

The same Steps 1–3, but with G_ij taken from truth labels instead of the GNN:

| pair | oracle G |
|---|---|
| same truth prong | −8 |
| W siblings in top (q, q′) | 0 |
| different prongs (b vs q, or q vs q̄ in W/Z) | +8 |
| either particle unlabelled | 0 |

- It is run with c = 8. It shows what a perfect GNN could achieve within this algorithm, and it can't be used on data.
- **The QCD oracle is exactly C/A.** Every QCD particle has label 0, so every pair gets −8, and a uniform factor doesn't change the merge order. The QCD fake rate is therefore identical: 0.108.
- **Unlabelled soft particles are neutral (G = 0),** while labelled same-prong pairs are pulled by e⁻⁸. So the soft particles end up attached to prongs in an odd order. That is why the oracle's groomed W mass window is poor (0.43): UE particles stay in the prongs.

## 3. Truth labels (own Pythia, truth level)

- Each particle gets the index of its nearest decay quark. For top: b = 0, the W quarks 1 and 2. For W/Z: the two quarks.
- The quark must be clearly nearest: ΔR_min < 0.75·ΔR_2nd and ΔR_min < 0.5. Otherwise the particle is unassigned (−1), about 3–4% of the pT.
- Every QCD particle is labelled 0: one prong.
- Sanity check: summing the labelled particles gives W 81.6, Z 91.9, top 170.6 GeV.

## 4. GNN training

- Binary cross-entropy on both heads, over pairs where both particles are labelled.
- Each pair is weighted by z_i·z_j, normalised per jet, with the classes balanced.
- 12 epochs; validation same-prong accuracy 96.5%, where "always same" scores 0.64.
- **Limitation:** the loss is on particle pairs, not on the merge decisions the clustering makes. That is a candidate reason the GNN's 0.999 pair AUC becomes 0.88 in the tree.

## 5. Baselines

The same code with G = 0: C/A (p = 0), kt (p = 1) and anti-kt (p = −1). Each reclusters the same constituents into one tree and uses the same groomed readout.

## 6. Metrics

| metric | definition |
|---|---|
| prongs correct | each prong's pT-weighted majority label is different, and every quark is covered |
| top W pairing correct | the two prongs from the second split are the two W quarks |
| mass window | groomed k-prong mass within ±15% of M_W / M_Z; top W candidate in 65–95 GeV |
| QCD fake | QCD jets with a groomed 2-prong mass in 65–105 GeV (mass sculpting) |
| pair AUC | z_i·z_j-weighted same-prong AUC. Trees are scored by the merge step at which a pair first shares a pseudojet (lowest common ancestor) |

## 7. Suspected losses and what is being tried (2026-09-25)

1. **The bound c may be too tight.** Top W pairing rose 0.45 → 0.59 → 0.66 for c = 1 → 2 → 4; the oracle used c = 8. Being swept.
2. **Soft particles get learned nudges.** They are pulled into prongs instead of being left for grooming, which gives the W mass tail. Fix under test: `zmin` gating, applying the factor only to hard merges. This is IRC safe like a Soft Drop z cut.
3. **The GNN is trained on pairs, not on merge decisions.** Candidate fix: train through the clustering (DAgger-style imitation of the oracle's merges).
4. **The GNN was still improving at epoch 12.** A v2 run is training: width 96, 4 layers, 30 epochs.
