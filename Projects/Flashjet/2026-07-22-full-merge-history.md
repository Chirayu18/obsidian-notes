---
tags: [reference]
status: active
date: 2026-07-22
source: lxplus
---

# Seeing the full merge history of one jet (and where grooming sits)

Companion to [[2026-07-18-tagger-inputs]] / [[2026-07-18-history-tagger-design]].
Answers the question *"can we see the full merge history, and are the trees we read
the groomed ones?"* — **no, they are the full ungroomed trees**; grooming is a walk
*over* the C/A tree that keeps a subset.

## What flashjet stores

Every clustering pass records the **complete binary merge tree** as four arrays
(`ClusterOutput.hist_p1, hist_p2, hist_child, hist_d`):

- `hist_p1, hist_p2` — the two pseudojet ids merged at each step
- `hist_child` — the resulting pseudojet id
- `hist_d` — the $d_{min}$ at which they merged

Initial particles are ids `0..n-1` (mask order); `-1` = beam (a jet finalises),
`-2` = padding. So for an $n$-constituent jet there are $n-1$ real merge rows taking
$n$ leaves down to one jet. **Nothing is removed** — this is the raw history.

## The figure (`full_history_tree.png`)

One real boosted $t\bar t\to 4q$ jet (Run 3 2024 JMENanoV15): 25 PF constituents,
raw $p_T=789$ GeV, mass 135 GeV, $n_{drop}=5$. Both panels are drawn as dendrograms:
- **leaves (red)** = constituents, marker size $\propto p_T$;
- **nodes (blue)** at $y=\ln(\sqrt{d}\,R)\approx\ln k_t$-scale of the merge;
- **left = C/A tree** (angular-ordered), **right = kT tree** (value-sorted) — same
  constituents, different clustering.

### Grooming overlaid on the C/A tree (left panel)
Soft drop ($z_{cut}=0.1$, $\beta=0$) is replayed on the full C/A tree:
- **green spine** = the path grooming keeps (root → down the harder branch);
- **grey dashed** = the 5 soft prongs grooming **drops** ($=n_{drop}$);
- **green star** = the first split that passes $z>z_{cut}(\Delta R/R)^\beta$ — its
  mass is $m_{SD}$, its momentum share is $z_g$, its angle is $R_g$.

So the **groomed jet is a pruned path through the full tree**, not a different tree.
The Lund coordinates ($z,\Delta R,\ln k_t$ per emission) are read off this same
primary branch.

### kT tree (right panel)
The hardest merges sit at the top because the kT ordering is **value-sorted**; their
$\sqrt{d}\,R$ are exactly the exclusive scales $\sqrt{d_{12}}\ge\sqrt{d_{23}}\ge\dots$
(the `splitting_scales()` outputs). Contrast the C/A tree, ordered by **angle**, whose
primary branch *is* the soft-drop / Lund sequence.

## Provenance recap (which tree feeds which variable)
- **kT** (value-sorted): $\sqrt{d_{12}},\sqrt{d_{23}},\sqrt{d_{34}}$ + ratios.
- **C/A** (angular): $m_{SD}, z_g, R_g, n_{drop}$, all Lund counts / $\ln k_t$ / $z,\Delta R$.
- **anti-kT**: the jet itself ($m_{ung}$, $n_{const}$).
See the deck's "Which tree does each variable come from?" slide and [[2026-07-18-tagger-inputs]].

## A second example — grooming that *works* (`full_history_good.png`)

The first jet is a **cautionary case**: soft-drop follows the highest-$p_T$ branch,
which marches down the leading quark's own collinear fragmentation and never crosses
the wide balanced decay split, so it "passes" on a tiny near-collinear split and
$m_{SD}$ collapses to $\sim3$ GeV (even though $n_{drop}=5$ and the kT scales still
show the 3-prong top). Known $\beta=0$ soft-drop pathology.

The companion figure shows grooming **doing its job** on a boosted $W\to q\bar q$
(30 constituents, $p_T$ 507 GeV):
- ungroomed mass **119.6 GeV**, inflated by soft wide-angle radiation;
- soft-drop drops 4 soft prongs ($z\approx0.005$) then lands the passing split on a
  genuinely **balanced, wide** decay: $z_g=0.49$, $R_g=0.34$, $k_t$ jumps to 80 GeV;
- groomed mass **$m_{SD}=83$ GeV $\approx m_W$**.

Side by side the two figures make the point: *the same algorithm can strip junk and
recover the resonance, or misfire into collinear noise*, depending on whether the
hard decay split sits on the highest-$p_T$ branch. This is the concrete motivation for
feeding the tagger the **kT splitting scales and $n_{drop}$ alongside $m_{SD}$** — the
kT scales don't care about branch-$p_T$ ordering and recover the structure either way.

## Reproduce
`full_history3.py` (the top/misfire example, first jet with $n_{drop}\ge3$) and
`full_history_good.py` (the clean $W$ example: requires a wide balanced passing split,
$m_{SD}$ on a resonance, and $m_{ung}-m_{SD}>15$) in
`/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`. Both cluster the
constituents with C/A and kT, replay soft drop, and draw both dendrograms.
`history_readout.py` prints the per-step soft-drop walk (mass, z, ΔR, kt) for the
misfire jet. Earlier drafts: `full_history.py`, `full_history2.py`. Links in [[plots]].
