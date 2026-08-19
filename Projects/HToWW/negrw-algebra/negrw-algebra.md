---
marp: true
theme: default
paginate: true
size: 16:9
title: Negative-Weight Reweighting — the algebra
math: katex
style: |
  section {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 24px; padding: 40px 62px;
    background: #fcfcfb; color: #1a1c1f;
  }
  h1 { font-size: 36px; color: #1f4e79; border-bottom: 3px solid #b8862b;
       padding-bottom: 8px; margin-bottom: 14px; }
  h2 { font-size: 27px; color: #1f4e79; }
  table { font-size: 21px; border-collapse: collapse; margin: 8px 0; width: 100%; }
  th { background: #1f4e79; color: #fff; padding: 7px 13px; text-align: left; }
  td { padding: 6px 13px; border-bottom: 1px solid #dde1e5; }
  code { background: #ebeef1; padding: 1px 5px; border-radius: 3px;
         font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .85em; }
  strong { color: #a01c1c; }
  section.lead { justify-content: center; text-align: center; }
  section.lead h1 { border-bottom: none; font-size: 44px; }
  .key { background: #edf4ed; border-left: 5px solid #2f6b3c; padding: 10px 16px; margin-top: 10px; }
  .warn { background: #fbf2e8; border-left: 5px solid #b5651d; padding: 10px 16px; margin-top: 10px; }
  .box { background: #f2f4f6; border: 1px solid #dde1e5; padding: 10px 16px; margin: 8px 0; }
  img { display: block; margin: 0 auto; max-height: 430px; width: auto; }
---

<!-- _class: lead -->

# Negative-Weight Reweighting

### The algebra, and why it is an identity

H→WW + charm · V+jets · arXiv:2510.16217

---

# 1 · Where negative weights come from

An NLO cross section splits into real and virtual contributions:

$$\sigma_{\rm NLO} = \int d\Phi_{n+1}\, R + \int d\Phi_n\, V + \int d\Phi_n\, B$$

$R$ and $V$ are **each divergent**; the divergences cancel only in the sum. To
integrate numerically you introduce subtraction terms $S$:

$$\sigma_{\rm NLO} = \int d\Phi_{n+1}(R - S) + \int d\Phi_n\Big(V + \int_1 S\Big) + \int d\Phi_n B$$

Each bracket is now finite — but $R-S$ and $V+\int_1 S$ are **not positive
definite**. Events sampled from them carry weights of either sign.

<div class="key">

Negative weights are not a bug or a generator pathology. They are the price of a
finite, matched NLO calculation.

</div>

---

# 2 · Why that hurts

The yield estimator in a bin $B$:

$$\hat N_B = \sum_{i \in B} w_i, \qquad w_i = \pm|w_i|$$

| quantity | behaviour |
|---|---|
| expectation $\langle \hat N_B\rangle$ | **correct** — the estimator is unbiased |
| variance $V[\hat N_B]$ | $\propto \sum_i w_i^2 = \sum_i \lvert w_i\rvert^2$ |

The **mean** is the signed sum (small), the **variance** follows the unsigned sum
(large). Define the effective sample size

$$n_{\rm eff} = \frac{\big(\sum_i w_i\big)^2}{\sum_i w_i^2} \;\ll\; N$$

<div class="warn">

In our V+jets, **16.4%** of events had $w<0$. One DY bin came out
$0 \pm 41$ from $\pm 79{,}000$ weights cancelling — zero content, large error.
`autoMCStats` then assigns that bin a huge nuisance.

</div>

---

# 3 · The decomposition

Any signed density can be written as a **difference of two positive, normalised**
densities:

$$p(\vec x) \;=\; a\,p_+(\vec x) \;-\; b\,p_-(\vec x)$$

with $a,b \ge 0$ and, since $p$ is itself normalised,

$$\int p = a - b = 1$$

<div class="box">

$p_+$ — the normalised density of **positive-weight** events
$p_-$ — the normalised density of **negative-weight** events
$a, b$ — their total weights, with $a - b = 1$

</div>

A Monte Carlo generator samples $p_+$ with probability $\propto a$ and $p_-$ with
probability $\propto b$, assigning $\pm$ accordingly.

---

# 4 · The positive-weight probability

At a point $\vec x$, the probability that an event drawn there carries $w>0$:

$$P_+(\vec x) \;=\; \frac{a\,p_+(\vec x)}{a\,p_+(\vec x) + b\,p_-(\vec x)}$$

Write $u(\vec x) \equiv a\,p_+(\vec x) + b\,p_-(\vec x)$ — the **unsigned** density.
Then

$$a\,p_+ = P_+\,u, \qquad b\,p_- = (1-P_+)\,u$$

Substituting into $p = a p_+ - b p_-$:

$$p(\vec x) = P_+ u - (1-P_+)u = \big(2P_+(\vec x)-1\big)\,u(\vec x)$$

<div class="key">

$$\boxed{\;p(\vec x) \;=\; g(\vec x)\;u(\vec x), \qquad g(\vec x) \equiv 2P_+(\vec x)-1\;}$$

</div>

---

# 5 · Why this solves the problem

$u(\vec x)$ is the density that $\sum_i |w_i|$ samples — **all events, unsigned**.

So for any observable $f$:

$$\int f(\vec x)\,p(\vec x)\,d\vec x \;=\; \int f(\vec x)\,g(\vec x)\,u(\vec x)\,d\vec x$$

$$\Longrightarrow\quad \sum_i w_i\,f(\vec x_i) \;\;\widehat{=}\;\; \sum_i |w_i|\,g(\vec x_i)\,f(\vec x_i)$$

**Both estimate the same distribution.** The reweighting is therefore

$$w_i \;\longrightarrow\; |w_i|\cdot g(\vec x_i)$$

<div class="key">

**Same yield. Same shape. Smaller variance** — because every event now contributes
with the same sign, scaled by $g \in [-1,1]$, instead of cancelling.

</div>

---

# 6 · The variance gain, explicitly

| | signed | reweighted |
|---|---|---|
| estimator | $\sum w_i$ | $\sum \lvert w_i\rvert\, g_i$ |
| per-event magnitude | $\lvert w_i\rvert$ | $\lvert w_i\rvert\cdot\lvert g_i\rvert \le \lvert w_i\rvert$ |
| cancellation | yes | **no** |

Since $|g| \le 1$, every term shrinks *and* nothing cancels. The variance

$$V\Big[\sum |w_i| g_i\Big] \;=\; \sum |w_i|^2 g_i^2 \;\le\; \sum w_i^2$$

with equality only where $|g| = 1$, i.e. where the sign is deterministic.

<div class="box">

Measured in our sample: $\langle g\rangle = 0.672 = 2(0.836)-1$, matching the
global positive fraction. Range $[-0.991, 0.993]$ — inside $[-1,1]$, no
pathological events.

</div>

---

# 7 · The one approximation

Everything above is **exact for the true $P_+$**. In practice $P_+$ is unknown, so
we estimate it with a classifier:

$$\hat P_+(\vec x) \approx P_+(\vec x) \quad\Longrightarrow\quad \hat g = 2\hat P_+ - 1$$

<div class="warn">

**This is the only approximation in the method.** Closure stops being an algebraic
guarantee and becomes an **empirical property that must be measured**.

</div>

| | |
|---|---|
| model | `HistGradientBoostingClassifier`, 20-model ensemble |
| target | $\mathrm{sign}(w)$ |
| features | **20, all generator-level** (`lhe_*`, `genparton_*`) |
| training | 9.8M events |
| ensemble AUC | **0.829** |

---

# 8 · Why generator-level features only

$P_+(\vec x)$ is a property of **the generator**, not of the detector.

The identity $p = g\,u$ holds in the variables the generator actually sampled. If
$\vec x$ contained reconstruction-level quantities, $u$ would no longer be the
density $\sum|w|$ samples, and closure would not follow.

<div class="key">

The paper (§V.2) rejects reco-level inputs for exactly this reason: *"using
reconstruction-level variables will not guarantee closure on generator-level
variables."*

</div>

Our 20 features: `lhe_njets`, `lhe_nb/nc/nuds/nglu`, `lhe_ht`, `lhe_vpt`,
`lhe_alphas`, `genparton_multiplicity`, `genparton_n_pt20/100/200`,
incoming parton PDG IDs, and the two leading partons' $p_T$ and $\eta$.

---

# 9 · Train loose, infer tight

The signal region has far too few V+jets events to train on — that starvation is
the problem being solved.

| | region |
|---|---|
| **train** | all base cuts **+ veto of the eμ SR topology** |
| **infer** | the tight eμ signal region |

<div class="key">

**Disjoint by construction.** An event that is not "exactly one eμ pair" can never
be an SR event, so training and inference sets cannot overlap — no event-ID
bookkeeping needed, and no overfitting bias.

</div>

<div class="warn">

Disjoint **events**, but *not* an orthogonal **phase space**. $g$ must be
interpolated over the SR's support, never extrapolated — so an anti-SR training
region (e.g. c-depleted) would be actively harmful.

</div>

---

# 10 · Validation

| check | result |
|---|---|
| training-region closure | **0.994** on 9.8M events |
| calibration of $\hat P_+$ in the SR | on the diagonal, $P_+ \approx 0.15\to0.93$ |
| ensemble spread $\delta g$ | mean **0.006**, max 0.467 |
| SR closure | **carries an offset** |

<div class="warn">

**The SR closure offset is real.** The SR is a small, kinematically-biased corner
of the training space, so a finite $\hat P_+$ does not close perfectly there.
*This caveat is our extension — the paper's evaluation region was not this starved.*

</div>

Why it is acceptable: reweighting fixes **variance, not yield**; the $n_{\rm eff}$
benefit comes from reduced per-bin variance and survives the offset; and the
residual is covered by `CMS_negrw_vjets`, which **profiles to 0.0%** in the fit.

---

# 11 · What enters the analysis

```python
# per event, dumped alongside the nominal weight
weight_negrw     = 2 * P_plus_ensemble_mean(x) - 1      #  = g
weight_negrw_std = 2 * P_plus_ensemble_std(x)           #  = delta g
```

| column | role |
|---|---|
| `weight_negrw` | the reweight factor $g$ applied to $\lvert w\rvert$ |
| `weight_negrw_std` | the 20-model spread → shape nuisance **`CMS_negrw_vjets`** |

Applied only to the V+jets samples the ensemble was trained for, via an
**anchored** dataset match — a substring gate would also catch
`WplusH_WtoLNu_...` and silently reweight a Higgs template with a V+jets model.

<div class="key">

`CMS_negrw_vjets` profiles to **0.0%** — the method's own uncertainty is negligible.

</div>

---

<!-- _class: lead -->

# Summary

$$p(\vec x) = \big(2P_+(\vec x)-1\big)\,u(\vec x)$$

**An algebraic identity, not an approximation.**

Same yield, same shape, no cancellation.

The only approximation is $\hat P_+$ from a finite classifier —
and its residual is a nuisance that profiles to zero.
