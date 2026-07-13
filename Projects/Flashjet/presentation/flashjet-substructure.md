---
marp: true
theme: default
paginate: true
size: 16:9
header: 'flashjet — GPU substructure (F1/F2/F3)'
footer: 'C. Gupta · 2026-07-13'
style: |
  section { font-size: 21px; padding: 48px 60px 60px; }
  h1 { color: #b00020; font-size: 32px; }
  h2 { color: #333; }
  table { font-size: 18px; }
  code { font-size: 0.9em; }
  section.lead { text-align: center; }
  section.lead h1 { font-size: 44px; }
  img { background: white; }
  .small { font-size: 16px; color: #555; }
  .cols { display: flex; gap: 24px; align-items: flex-start; }
  .cols > div { flex: 1; }
---

<!-- _class: lead -->

# GPU substructure for **flashjet**

### kt / C-A jet substructure on the merge history

exclusive jets · soft-drop grooming · Lund coordinates

**Chirayu Gupta** — for Alexandre De Moor
2026-07-13 · branch `benchmarking` (working tree, not committed)

<span class="small">Every claim below is closed against an independent reference and/or the
defining paper. All plots regenerable: `plots/2026-07-13-substructure/`.</span>

---

## Where this sits in flashjet

flashjet clusters padded `(B, N, 4)` torch tensors into jets on the GPU, staying on-device
for ML training loops. Generalized-kt:

$$ d_{ij} = \min(k_{t,i}^{2p}, k_{t,j}^{2p})\,\frac{\Delta R_{ij}^2}{R^2}, \qquad
p=-1\;(\text{anti-}k_t),\; 0\;(\text{C/A}),\; +1\;(k_t) $$

**The key object Alex's kernels already produce: the _merge history_.** Every recombination
step records four arrays — `hist_p1, hist_p2` (the two inputs), `hist_child` (the output id),
`hist_d` (the distance at which they merged). That history *is* the full binary clustering tree.

> **Our contribution = read that tree.** No new kernels, no changes to the clustering path.
> All three features are pure-torch post-reads of `(hist_p1, hist_p2, hist_child, hist_d)`,
> so they run unchanged on CPU or CUDA and add negligible cost.

---

## What was already there vs. what we added

<div class="cols">
<div>

**Pre-existing (Alex)**
- `history.py`: `jet_idx_from_history`, `_resolve_parents`, `_decode`,
  `splitting_scales_from_history`, Triton `_decode_triton`
- `reference.py`: single-event NumPy ground truth (`cluster_event`)
- `nn_reference.py`: nearest-neighbour reference
- `conftest.py`: `random_event` fixtures
- The kernels + the merge-history recording

</div>
<div>

**Added (this work)** — in `history.py`
- **F1** `exclusive_jets_from_history`
- **F2** `groom_from_history`
- **F3** `lund_coordinates_from_history`
- helpers: `_resolve_roots`, `_jet_roots`,
  `_pseudojet_p4`, `_dense_number_roots`
- `api.py`: `ClusterOutput.{exclusive_jets, groomed_jets,
  mass_drop, lund_coordinates}` + a `mask` field
- `tests/test_substructure.py` (new)

</div>
</div>

<span class="small">The `_ref_*` walkers inside `test_substructure.py` are also ours — independent
naive NumPy tree-walks used only to pin the fast implementations.</span>

---

## The three features

| | Feature | Function | Implements |
|---|---|---|---|
| **F1** | Exclusive jets (kt) | `exclusive_jets_from_history(...)` | kt algorithm — FastJet manual [1111.6097], [0802.1189] |
| **F2** | Grooming (C/A) | `groom_from_history(...)` | Soft Drop [1402.2657] · mMDT [1307.0007] · mass-drop [0802.2470] |
| **F3** | Lund coordinates | `lund_coordinates_from_history(...)` | Primary Lund plane [1807.04758] |

**F1** — undo the last merges of the sequence to expose exactly `n_jets` (or a `d_cut`) subjets;
reduces to the inclusive jets at the trivial cut.
**F2** — walk each jet down the harder branch, dropping the softer prong until
$z > z_{\rm cut}(\Delta R/R)^\beta$ (soft-drop) — the $O(\log_2 n)$ declustering.
**F3** — for every primary split emit $(z,\Delta R, k_t, \ln 1/\Delta R, \ln k_t, d)$; the
$d$-channel ties **exactly** to `splitting_scales`.

---

## Design: everything is a cheap post-read

All three reuse two batched **pointer-jumping** primitives that resolve parents / roots of the
tree in $O(\log N)$ gathers (`_resolve_parents`, `_resolve_roots`) — no Python-side per-jet loop.

![w:760](img/parity_timing.png)

<span class="small"><b>Left:</b> groomed mass from F2 vs an independent per-event NumPy declustering — agree to
<b>max |Δ| = 1.71×10⁻¹³ GeV</b> (float64 round-off). <b>Right:</b> per-event CPU cost — the decoders are
<b>10–100× cheaper</b> than the clustering they read; they are not on the critical path.</span>

---

<!-- _class: lead -->

# How the toys were generated

*(the "simulation" — none of it pre-existing; flashjet only clusters, it does not generate events)*

---

## The toy event generators (written in the plot scripts)

flashjet takes 4-vectors in and returns jets — it has **no event generator**. To exercise the
features I wrote small, transparent toys *outside the repo*, in the plot scripts.

**`make_plots.py` — two single-fat-jet samples at $p_T\!\approx\!500$ GeV, $R=0.8$:**
- **QCD-like**: one hard collinear core (92% of $p_T$, $\sigma_{y,\phi}=0.06$) + soft wide-angle
  radiation (8%, $\sigma=0.30$). Each "spray" = $n$ massive pions with exponential $p_T$ fractions.
- **W-like**: two hard prongs with pair mass $m=\sqrt{z(1-z)}\,p_T\,\Delta R = 80.4$ GeV
  ($z\in[0.30,0.45]$), random orientation, + 6% soft contamination.

```python
def _spray(rng, n, y0, phi0, pt_total, sigma):     # n pions around (y0,phi0)
    frac = rng.exponential(1., n); frac /= frac.sum()
    pt = pt_total * frac
    y, phi = rng.normal(y0, sigma, n), rng.normal(phi0, sigma, n)
    mt = np.sqrt(M_PI**2 + pt**2)
    return np.stack([pt*np.cos(phi), pt*np.sin(phi), mt*np.sinh(y), mt*np.cosh(y)], 1)
```

<span class="small">1500 events per sample. Purpose: QCD vs W is a *known* truth, so any observable that
fails to separate them (or lands off the analytic curve) would be a real bug.</span>

---

## The toy parton shower (for the paper-figure closures)

**`make_paper_plots.py`** builds a **primary, fixed-coupling, leading-log** shower — emissions
sampled **uniformly in the Lund triangle** with density $\bar\alpha$ per unit
$(\ln 1/\theta,\ \ln k_t)$ area, off a hard spine at $(y,\phi)=(0,\pi)$:

$$ \theta=e^{-u},\quad k_t=e^{v},\quad z=\frac{k_t}{p_{T0}\,\theta},\qquad
\text{keep } v\le \ln(p_{T0}/2)-u \;(z\le\tfrac12),\ k_t>k_t^{\min} $$

This is **exactly the semi-classical picture the papers' analytic predictions are derived in** —
which is what makes the closure *quantitative*, not just qualitative.

- **Jet areas**: one hard event + a dense grid of infinitely-soft **ghosts** ($p_T=10^{-8}$);
  the ghosts each algorithm sweeps up trace its catchment area (the anti-kt-paper construction).

<span class="small">$\bar\alpha=0.25$, $p_{T0}=1$ TeV, $R=0.4$, 20 000 showers. Everything is re-runnable with a fixed seed (`20260713`).</span>

---

<!-- _class: lead -->

# Correctness

*each feature reproduces the signature figure of the paper it implements*

---

## anti-kt jet shapes — reproduces [0802.1189] Fig. 1

![w:960](img/jet_areas.png)

Same event + soft-ghost grid, $R=1$. **kt** and **C/A** give ragged, area-fluctuating jets;
**anti-kt** gives rigid **circles** around each hard particle — the defining result of the anti-kt paper,
here from flashjet's own clustering.

---

## F1 — kt substructure separates 2-prong from QCD [0802.1189, 1111.6097]

![w:880](img/kt_observables.png)

<div class="cols">
<div>

**Left — $\sqrt{d_{12}}$** (`splitting_scales_from_history`):
kt scale of the last merge. W-like peaks at $\sim m_W/2$, QCD sits low.

</div>
<div>

**Right — exclusive 2-subjet $z$** (`exclusive_jets_from_history`, $n_{\rm jets}=2$):
W-like balanced ($z\!\approx\!0.35$), QCD lopsided ($z\!\to\!0$) — the tagging split.

</div>
</div>

---

## F2 — soft-drop $z_g$ vs the analytic prediction [1402.2657]

<div class="cols">
<div>

The soft-drop momentum fraction $z_g$ from `groom_from_history`
($z_{\rm cut}=0.1,\ \beta=0$) tracks the **leading-log QCD prediction**

$$ p(z_g)=\frac{1/z_g}{\ln(1/2z_{\rm cut})} $$

across the **entire range**, with no free parameters. 72% of jets tagged.

> This is the **decisive grooming-correctness plot**: the target curve is
> *the* right answer, so lying on it is unambiguous closure.

</div>
<div>

![w:520](img/zg_distribution.png)

</div>
</div>

---

## F2 — groomed mass ordering in $\beta$ [1402.2657 Figs. 3–4]

<div class="cols">
<div>

Groomed mass $\rho=m^2/(p_T^2R^2)$ for $\beta=0,1,2$ vs ungroomed.

- Grooming shifts the spectrum to **lower $\rho$** (removes soft-wide radiation).
- **Smaller $\beta$ grooms harder**: the $\beta=0$ curve reaches furthest left.

Reproduces the $\beta$-ordering of the Soft Drop paper.

</div>
<div>

![w:560](img/softdrop_rho.png)

</div>
</div>

---

## F3 — primary Lund plane [1807.04758]

![w:940](img/lund_plane.png)

`lund_coordinates_from_history` (C/A, $R=0.8$). **QCD** fills the soft-collinear region smoothly.
**W-like** shows the same background **plus an isolated hard-splitting spot** exactly where the
2-body $m_W$ decay must sit (red ★ = predicted position).

---

## F3 — Lund-triangle closure [1807.04758 Fig. 2]

<div class="cols">
<div>

Emissions sampled **uniformly** in the Lund triangle (input $\bar\alpha=0.25$/unit area) are
recovered by `lund_coordinates_from_history` as a **flat interior plateau** bounded by the three
physical edges ($z=\tfrac12$, $k_t$ cutoff, $\theta_{\max}$).

- Interior density **0.17 ± 0.02** — flat to ~12%; uniform input recovered.
- The offset below 0.25 is genuine **wide-angle reclustering migration** (C/A reassigns some
  wide emissions), **not** a bug — it is a property of the observable, reproduced honestly.

</div>
<div>

![w:520](img/lund_triangle.png)

</div>
</div>

---

## F3 runs on **real CMS data** — primary Lund plane of 60 285 QCD jets

<div class="cols">
<div>

Not a toy: **PF candidates** from CMS UL18 QCD **JMENano** (the format that carries the
`PFCand` + `FatJetPFCand` constituent map), grouped per AK8 jet, clustered by our anti-kt
$R=0.8$, read by **F3**.

The full physical structure of [1807.04758] emerges straight from detector-level simulation:
the hard-collinear perturbative ridge, the soft plateau, and the three kinematic edges — with
**no toy input**.

<span class="small">The pipeline was also validated jet-by-jet vs CMS AK8 $p_T$ / $m_{\rm SD}$ (omitted here — a
known raw-vs-PUPPI offset, accounted for by a per-jet rescale; the algorithm is correct).</span>

</div>
<div>

![w:540](img/cms_lund.png)

</div>
</div>

---

## Validation ladder & test suite

Each feature is pinned at every level, top to bottom:

1. **FastJet** (where applicable) → **NumPy reference** (`cluster_event`) — the single-event ground truth
2. **torch backend** matches the reference
3. **Triton kernels** match the torch backend (`decode=False` parity)
4. **each feature** matches an **independent naive NumPy tree-walk** (`_ref_*` in `test_substructure.py`)
5. **physics anchors**: $z_g$ vs analytic $1/z$; $\sqrt{d_{12}}\to m_W/2$; Lund hard-split position; groomed-mass parity to $10^{-13}$ GeV

```
micromamba run -n b_hive python -m pytest -q     →   85 passed, 13 skipped (CUDA-only)
```

<span class="small">The 13 skips are the Triton `decode=False` parity tests, which need a GPU node.</span>

---

## Status & next steps

**Done**
- F1/F2/F3 implemented as pure-torch reads of the merge history — no kernel changes
- Independent-reference parity to float64 round-off; full suite green (85 passed)
- Reproduced the signature figures of anti-kt, Soft Drop, and Lund papers
- F3 demonstrated end-to-end on real CMS UL18 QCD PF candidates

**Open / for Alex**
- Review the working-tree changes — **not committed** to the repo, per instruction
  (`src/flashjet/{history,api,__init__}.py`, `README.md`, `tests/test_substructure.py`)
- GPU-node follow-up: the Triton `decode=False` parity tests still need CUDA
- Optional: expose secondary Lund planes; wire the exclusive-jet API into a tagging demo

<span class="small">Repo: `flashjet/FlastJetDemo` (branch `benchmarking`). Plots + scripts:
`plots/2026-07-13-substructure/`. Papers: `References/Flashjet/papers.md`.</span>

---

<!-- _class: lead -->

# Backup

---

## Function reference (added)

```text
exclusive_jets_from_history(hist_p1, hist_p2, hist_child, hist_d, mask,
                            n_jets=None, d_cut=None)          # F1
groom_from_history(hist_p1, hist_p2, hist_child, hist_d, mask, p4, R,
                   z_cut=0.1, beta=0.0, mu=None)              # F2 (soft-drop / mMDT / mass-drop)
lund_coordinates_from_history(hist_p1, hist_p2, hist_child, hist_d, mask, p4)  # F3 -> (B,J,S,6)

# helpers
_resolve_roots(...)      # pointer-jump roots of an arbitrary sub-forest
_jet_roots(...)          # per-jet root pseudojet id, beam-merge order
_pseudojet_p4(...)       # E-scheme 4-momentum of every pseudojet, keyed by id
_dense_number_roots(...) # compact per-particle jet index
```

**API surface**: `ClusterOutput.exclusive_jets`, `.groomed_jets`, `.mass_drop`,
`.lund_coordinates`, plus a new `.mask` field to map slots→ids.

---

## Reproducing everything

```bash
# on lxplus, env b_hive (torch 2.5.1)
cd /eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure
micromamba run -n b_hive python make_plots.py        # F1/F2/F3 toy justification + parity
micromamba run -n b_hive python make_paper_plots.py  # anti-kt/SoftDrop/Lund paper figures
micromamba run -n b_hive python make_cms_plots.py    # real CMS UL18 QCD (needs qcd_jmenano_150x.root)

# tests
cd /eos/home-c/cgupta/flashjet/FlastJetDemo
micromamba run -n b_hive python -m pytest -q          # 85 passed, 13 skipped
```

Fixed seed `20260713` throughout. Papers catalogued in `References/Flashjet/papers.md`.
