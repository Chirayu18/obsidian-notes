---
tags: [reference]
status: active
date: 2026-07-01
source: lxplus
---

# Kappa HCE Loss — Complete Mathematics & b-hive Integration

The **kappa hierarchical cross-entropy (kappa HCE)** loss is the current best
loss for the H→WW H+c MVA (v32: hplusc_vs_all AUC **0.975**). It replaces
manually-defined hierarchical groups with *dynamic* groups derived from the
geometry of the classifier's own output layer, and couples them to a
differentiable significance term. This note derives all of the mathematics and
describes how to integrate it into b-hive for jet-flavour tagging.

Implementation: `utils/loss/HierarchicalCrossEntropyLoss.py`
(`_kappa_hce_forward`, mode `"kappa_hce"`). Config:
`config/HPlusCHToWW_kappa_hce.yml`. See also [[MVA]] for the full version history.

---

## 1. Setup and notation

| Symbol | Meaning |
|---|---|
| $C$ | number of classes (13 for H→WW: hplusc, hplusb, ggH, vbf, zh, ggzh, wh, tthnonbb, tthtobb, tt, st, diboson, vjets) |
| $s$ | signal class index (hplusc) |
| $z \in \mathbb{R}^{C}$ | logits from the network for one event |
| $p_i = \mathrm{softmax}(z)_i$ | predicted posterior $P(\text{class } i \mid x)$, $\sum_i p_i = 1$ |
| $W \in \mathbb{R}^{C \times h}$ | weight matrix of the **final linear layer** ($h=32$ hidden units) |
| $W_j \in \mathbb{R}^{h}$ | row $j$ of $W$ — the learned *template vector* for class $j$ |
| $y$ | integer truth label of the event |
| $N_j$ | number of training events in class $j$ |
| $\tau$ | temperature for soft group membership |
| $\lambda$ | weight of the significance term (`lam`) |
| $k_\text{fine}$ | weight of the fine-separation term |

The logit for class $j$ is $z_j = W_j \cdot \phi(x) + b_j$, where $\phi(x)$ is the
penultimate activation. So **each row $W_j$ is the direction in feature space that
the network associates with class $j$.** Two classes whose templates point in
similar directions are "confusable" — this is the geometric intuition the loss
exploits.

---

## 2. Dynamic groups from cosine similarity

Define the cosine similarity between the signal template and every class template:

$$
c_j \;=\; \cos\!\big(W_s, W_j\big) \;=\; \frac{W_s \cdot W_j}{\lVert W_s\rVert \, \lVert W_j\rVert}, \qquad c_s = 1 .
$$

This is recomputed **every forward pass** from the live weights, so the grouping
evolves as the model trains (`_get_cosine_similarities`).

### 2.1 Hard split (used by the group term)

$$
\mathcal{P} = \{\, j : c_j \ge 0 \,\} \quad(\text{"positive" / signal-like, includes } s), \qquad
\mathcal{N} = \{\, j : c_j < 0 \,\}.
$$

Let $n_\mathcal{N} = |\mathcal{N}|$.

### 2.2 Soft membership (used by the fine and significance terms)

$$
\alpha_j \;=\; \sigma\!\left(\frac{c_j}{\tau}\right) \;=\; \frac{1}{1 + e^{-c_j/\tau}} \;\in (0,1).
$$

$\alpha_j$ is the **soft "kappa"** — the degree to which class $j$ is treated as
belonging to the signal-like fine group. $\tau$ controls sharpness:

- $\tau = 0.3$: $\alpha > 0.5$ once $c_j > 0$, $\alpha < 0.05$ by $c_j < -0.6$.
- Smaller $\tau$ → harder (step-like) membership; larger $\tau$ → softer.

> **Stop-gradient.** In code $\alpha$ is computed from `cos_sim.detach()`, so
> $\alpha$ acts as a *read-out gate*, not a free parameter driven by the loss.
> The template geometry ($c_j$) is shaped **only** by the CE terms below; the
> significance term cannot push $\alpha$ around. This is precisely why the kappa
> HCE loss does **not** suffer the kappa-collapse (→0) or kappa-convergence (→1)
> pathologies of the earlier learned-kappa losses (v18s / v18logB — see [[MVA]] §3).

---

## 3. The three loss terms

$$
\boxed{\; \mathcal{L} \;=\; \mathcal{L}_\text{group} \;+\; k_\text{fine}\,\mathcal{L}_\text{fine} \;+\; \lambda\,\mathcal{L}_\text{sig} \;}
$$

### 3.1 Group term — hard-split coarse CE

Collapse the $\mathcal{P}$ classes into a single merged column and keep each
$\mathcal{N}$ class separate. Grouped probabilities $q \in \mathbb{R}^{n_\mathcal{N}+1}$:

$$
q_k = p_{\mathcal{N}_k}\ (k < n_\mathcal{N}), \qquad
q_{n_\mathcal{N}} = \sum_{j \in \mathcal{P}} p_j .
$$

Map each event's truth to a group index $g(y)$: its own column if $y \in \mathcal{N}$,
else the merged column $n_\mathcal{N}$. Then

$$
\mathcal{L}_\text{group} \;=\; -\,\frac{\sum_x w_{g(y)} \, \log q_{g(y)}(x)}{\sum_x w_{g(y)}} ,
$$

(a weighted NLL). The group weights are inverse-frequency:

$$
w_k = \widehat{\mathrm{invfreq}}(\mathcal{N}_k)\ (k<n_\mathcal{N}),
\qquad
w_{n_\mathcal{N}} = \frac{1}{\sum_{j\in\mathcal{P}} N_j},
$$

where $\widehat{\mathrm{invfreq}}(j) = \dfrac{\sum_i N_i}{N_j}$ normalised so
$\max_j = 1$ (built in `training.py` for `kappa_hce`).

**Why merge the positives instead of giving them individual columns?** A merged
column contributes no term that pushes the $\mathcal{P}$ templates *apart*. If each
positive class had its own softmax column, the CE gradient would repel their
weight vectors, destabilising the very cosine structure that defines the groups.
Merging keeps the signal-like cluster cohesive.

### 3.2 Fine term — soft-membership conditional CE

Build an $\alpha$-gated conditional distribution over classes:

$$
\tilde p_i(x) \;=\; \frac{\alpha_i \, p_i(x)}{\sum_j \alpha_j \, p_j(x)} .
$$

Per-event fine loss (inverse-frequency weighted NLL), then **each event weighted
by $\alpha$ of its own true class**:

$$
\ell_\text{fine}(x) = -\,\widehat{\mathrm{invfreq}}(y)\,\log \tilde p_y(x),
\qquad
\mathcal{L}_\text{fine} \;=\; \frac{\sum_x \alpha_{y(x)}\,\ell_\text{fine}(x)}{\sum_x \alpha_{y(x)}} .
$$

The double appearance of $\alpha$ — inside $\tilde p$ (softens the denominator to
the signal-like region) and as the per-event weight $\alpha_{y(x)}$ (down-weights
background events) — is what makes this term focus purely on separating the
signal from its near neighbours. Its final contribution is scaled by $k_\text{fine}$.

### 3.3 Significance term — kappa discriminant

Define the **kappa discriminant** with $\alpha$ playing the role of $\kappa$:

$$
D(x) \;=\; \frac{p_s(x)}{\,p_s(x) + \displaystyle\sum_{j \ne s} \alpha_j \, p_j(x)\,} \;\in (0,1].
$$

Signal-like classes ($\alpha_j \to 1$) stay in the denominator and **dilute** $D$
— so $D$ only grows when $p_s$ genuinely dominates its near neighbours.
Background-like classes ($\alpha_j \to 0$) drop out and cannot inflate the
denominator. The term is a **batch-mean** on each half (composition-invariant,
spike-free):

$$
\mathcal{L}_\text{sig} \;=\; \underbrace{\frac{1}{n_\text{sig}} \sum_{x:\,y=s} -\log D(x)}_{\text{push } D \uparrow \text{ for signal}}
\;+\; \underbrace{\frac{1}{n_\text{bkg}} \sum_{x:\,y\ne s} \log\!\big(1 + D(x)\big)}_{\text{push } D \downarrow \text{ for background}} .
$$

- $-\log D$ diverges as $D\to 0$: strong pull to raise $p_s$ on true signal.
- $\log(1+D)$ is bounded and floored at $0$ (unlike the old $\log B$ which ran to
  $-\infty$): it gently suppresses $p_s$ on backgrounds without dominating.
- Both gradients act on $p$ (via $z$), **aligned with the CE terms** — no
  probability-suppression artefact.

The $\tfrac{1}{n_\text{sig}}$, $\tfrac{1}{n_\text{bkg}}$ normalisation (with a guard
for signal-empty batches) removes the batch-composition dependence that made the
older summed significance losses spike on signal-heavy batches.

---

## 4. Why it works: the natural curriculum

The grouping is emergent, so training passes through phases automatically:

1. **Early (random $W$):** cosines are scattered around $0$; many classes land in
   $\mathcal{P}$. $\mathcal{L}_\text{fine}$ is effectively a *broad multiclass CE*
   over most of the 13 classes → the model first learns coarse structure.
2. **Middle:** $\mathcal{L}_\text{group}$ drives dissimilar backgrounds' templates
   to anti-align ($c_j < 0$), so they leave $\mathcal{P}$. The fine term's support
   shrinks toward the signal-like cluster.
3. **Late:** only the genuinely signal-like classes remain positive. In v32 by
   epoch 49 that is just **hplusb, ggH, VBF** (see
   `plots/all_trainings/v32_kappa_hce/group_evolution.png`). $\mathcal{L}_\text{fine}$
   has converged to a near-binary hplusc-vs-near-neighbour problem.

So a *single* objective interpolates from coarse multiclass to fine binary
discrimination without any manual schedule — this is the qualitative advantage
over the fixed-group hierarchical losses (v12–v18).

### v32 learned membership (from `best_model.pt`, $\tau=0.3$)

| Class | $c_j$ | $\alpha_j$ | Group |
|---|---|---|---|
| H+c | +1.000 | 0.966 | signal |
| H+b | +0.355 | 0.765 | $\mathcal{P}$ |
| VBF | +0.277 | 0.716 | $\mathcal{P}$ |
| ggH | +0.097 | 0.580 | $\mathcal{P}$ |
| V+Jets | −0.244 | 0.307 | $\mathcal{N}$ |
| ttHtoBB | −0.434 | 0.191 | $\mathcal{N}$ |
| ZH | −0.478 | 0.169 | $\mathcal{N}$ |
| ttHnonBB | −0.498 | 0.160 | $\mathcal{N}$ |
| ggZH | −0.522 | 0.149 | $\mathcal{N}$ |
| tt | −0.621 | 0.112 | $\mathcal{N}$ |
| Diboson | −0.670 | 0.097 | $\mathcal{N}$ |
| WH | −0.708 | 0.086 | $\mathcal{N}$ |
| ST | −0.733 | 0.080 | $\mathcal{N}$ |

The model discovers, without being told, that H+b / VBF / ggH are the charm-like
Higgs backgrounds that matter, and rejects everything else.

---

## 5. Inference / post-training discriminant

At inference the trained templates give fixed $\kappa_j$ (via $\alpha_j$ or a
separately-optimised vector). The event score is the same discriminant:

$$
D_\text{sig}(x) = \frac{p_s(x)}{p_s(x) + \sum_{j\ne s}\kappa_j\, p_j(x)} .
$$

Two ways to set $\kappa$:

- **From the model:** $\kappa_j = \alpha_j = \sigma(c_j/\tau)$ (or the `smooth`
  mapping $(1+c_j)/2$, or `clamp` $\max(0,c_j)$) — `scripts/kappa_from_model.py`.
- **Optimised per working point:** maximise $S/\sqrt{B}$ at a target signal
  efficiency via differential evolution, $\kappa_j \in [0,5]$ —
  `scripts/compare_significance.py`. For v32/v20 this gives only ~+1.2% over
  uniform $\kappa$, because the trained posteriors already encode the structure.

$S/\sqrt{B}$ at a working point uses **raw event counts** (no inverse-frequency):
$S = \sum_{x\in\text{sig}} \mathbb{1}[D(x)>t]$, $B = \sum_{x\in\text{bkg}} \mathbb{1}[D(x)>t]$,
threshold $t$ set to the target signal efficiency.

---

## 6. Integration into b-hive

### 6.1 How it is wired today

```
config YAML (hierarchical_loss.significance, mode: kappa_hce)
        │
        ▼
tasks/training.py
  ├─ builds class_inv_freq from the class histogram
  ├─ builds significance_config = {signal_idx, lam, mode}
  └─ LossFunctionLoader("HierarchicalCrossEntropyLoss",
                         group_indices, class_inv_freq,
                         significance_config, model=model)
        │
        ▼
utils/loss/HierarchicalCrossEntropyLoss.py
  └─ forward() → mode=="kappa_hce" → _kappa_hce_forward()
```

The loss holds a **reference to the model** (stored in a 1-element list so
`nn.Module` doesn't register it as a submodule) purely to read the final
`nn.Linear` layer's weights for the cosine similarities. The final layer is
cached on first use (`_final_layer_cache`).

Config block (`config/HPlusCHToWW_kappa_hce.yml`):

```yaml
hierarchical_loss:
  significance:
    signal_class: "is_hplusc"
    mode: "kappa_hce"
    lam: 25       # λ on the significance term
    tau: 0.3      # temperature for α = sigmoid(cos/τ)
    k_fine: 7.0   # weight on the fine-separation term
```

### 6.2 ⚠️ Bug to fix as part of the PR: `tau` / `k_fine` are dropped

`tasks/training.py` (≈ lines 389–393) constructs

```python
significance_config = {
    "signal_idx": signal_idx,
    "lam": sig_cfg.get("lam", 1.0),
    "mode": sig_mode,
}
```

It does **not** copy `tau` or `k_fine`. But `_kappa_hce_forward` reads
`self.significance_config.get("tau", 1.0)` and `forward` reads
`.get("k_fine", 7.0)`. **Consequence:** `tau: 0.3` in the YAML is ignored (the
loss actually runs at $\tau=1.0$), and `k_fine` only happens to match its default.
Fix — forward the keys:

```python
significance_config = {
    "signal_idx": signal_idx,
    "lam": sig_cfg.get("lam", 1.0),
    "mode": sig_mode,
    "tau": sig_cfg.get("tau", 1.0),
    "k_fine": sig_cfg.get("k_fine", 7.0),
}
```

(Re-run v32 after this fix; the documented $\tau=0.3$ number is really a
$\tau=1.0$ result until then.)

### 6.3 Using it for jet-flavour tagging

The loss is generic — it only needs (a) softmax posteriors over $C$ classes and
(b) a final linear layer whose rows are per-class templates. To repurpose it from
event-level MVA to **per-jet flavour tagging** (DeepJet/ParticleTransformer heads
in b-hive):

1. **Truths = jet flavours.** Set `truths:` to the flavour one-hots
   (e.g. `is_b, is_c, is_uds, is_g`, or a finer `is_bb, is_lepb, is_c, …`).
   `signal_class` = the flavour you want to tag (e.g. `is_c` for a c-tagger).
2. **Model head.** Any model ending in an `nn.Linear(h, C)` works
   (`simple_mlp_multiclass`, or the transformer taggers
   `particletransformer_ttcc`). The loss auto-discovers the last `nn.Linear`.
3. **Class histogram.** `loss_weighting: true` so `training.py` builds
   `class_inv_freq` from the flavour histogram — essential given jet-flavour
   imbalance (light/gluon ≫ c).
4. **Dynamic groups become flavour neighbourhoods.** Cosine similarity now groups
   *confusable flavours* automatically — e.g. `b`/`lepb` cluster, `c` sits between
   `b` and `light`. The fine term then sharpens exactly the hard c-vs-b / c-vs-light
   boundary, which is the physically limiting one for charm tagging.
5. **Discriminant = tagger score.** The inference score
   $D_c = p_c / (p_c + \sum_{j\ne c}\kappa_j p_j)$ generalises the standard
   CvsB / CvsL discriminants: choosing $\kappa$ to keep only $b$ in the
   denominator recovers CvsB; keeping only light recovers CvsL. The learned/optimised
   $\kappa$ gives a single c-tag score tuned for $S/\sqrt B$ instead.

Practical notes:
- Keep `mode: kappa_hce`, start from `lam` small (1–5) and $\tau \sim 0.3$–$1.0$;
  the significance term matters less for a pure tagger than for the H+c MVA where
  extreme imbalance (2k signal vs 4M bkg) is the whole problem.
- For a tagger you may set $k_\text{fine}$ high to prioritise the c-vs-b edge,
  which is tagger-ceiling-limited (~0.715 from CvsB alone for this dataset).
- Validate with per-flavour ROC (`utils/plotting/roc.py`) and the confusion-matrix
  scripts, exactly as for the MVA.

---

## 7. Relation to earlier losses (summary)

| Loss | Groups | $\kappa$ source | Failure mode | AUC |
|---|---|---|---|---|
| Flat CE (v10) | none | — | 13-class imbalance collapse | 0.51 |
| Hierarchical CE (v12–v15) | **manual** | — | needs hand-tuned groups | ≤0.965 |
| $-S/\sqrt B$ (v18s) | manual | learned, clamp | $\kappa$ collapse → 0 | 0.928 |
| $\log B$ (v18/19logB) | manual | learned, smooth | $\kappa$ converge → 1 | 0.961 |
| Discriminant-aware (v20) | manual | learned, smooth | — (best fixed-group) | 0.973 |
| **Kappa HCE (v32)** | **dynamic** | $\alpha=\sigma(c/\tau)$, **detached** | — | **0.975** |

The kappa HCE loss keeps v20's discriminant-aware significance term but (i)
replaces manual groups with emergent cosine groups and (ii) detaches $\kappa$ so
the significance objective can never destabilise the grouping — giving the best
AUC and a hyperparameter-light, self-scheduling training. See [[MVA]] for the
full numeric comparison and $S/\sqrt B$ tables.
