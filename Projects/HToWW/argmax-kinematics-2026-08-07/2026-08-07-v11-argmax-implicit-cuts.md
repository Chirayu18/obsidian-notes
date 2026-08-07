---
tags: [reference]
status: active
date: 2026-08-07
source: lxplus
---

# Does the v11 model impose implicit kinematic cuts?

**Question.** Split events by the v11 network's *predicted* class (argmax over the six
`mva_score_*`) and look at `mll`, `mTll`, `mTl2` — does the model implicitly carve out
kinematic regions per class?

**Answer. Yes, and sharply — most of all in `mTll`, which is not even an input feature.**

## Setup

- Model: `hwwcom_multiclass_v11`, workflow `hww_combine_fixed`, year **2022postEE**
- Scored parquets: `outputs/hww_combine_fixed/2022postEE/mva/`
- **Split is by argmax only** — the sample an event came from is never used.
- 35 per-sample parquets pooled, **4,046,127 events**, **raw and unweighted**
  (no `lumi*xsec/sumw`, no negrw: a physics weight would smear out a hard edge).
- Classes collapsed: `signal` = hplusc; `higgs` = higgsbkg;
  `other` = tt + st + diboson + vjets.

Note the `mva/` dir also holds group-level merges (`H+c.parquet`, `tt.parquet`, …)
whose events duplicate the per-sample files. The script takes exactly the per-sample
list via `gather_samples()`, so nothing is double counted.

| argmax class | events | share |
|---|---:|---:|
| signal (hplusc) | 372,722 | 9.21% |
| higgs bkg | 783,292 | 19.36% |
| other | 2,890,113 | 71.43% |

## Kinematic support (raw, unweighted)

| var | class | N | min | p0.1 | p1 | p50 | p99 | max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| mll | signal | 372722 | 12.00 | 12.14 | 13.27 | 41.19 | 82.74 | **100.20** |
| mll | higgs | 783292 | 12.00 | 12.26 | 14.10 | 47.02 | 94.33 | 656.64 |
| mll | other | 2890113 | 12.00 | 14.30 | 22.78 | 108.86 | 421.71 | 2860.96 |
| mTll | signal | 372722 | **52.76** | 63.74 | 72.61 | 113.80 | 164.53 | **201.72** |
| mTll | higgs | 783292 | 0.00 | 0.26 | 2.58 | 90.17 | 236.12 | 871.78 |
| mTll | other | 2890113 | 0.00 | 0.33 | 3.18 | 124.92 | 317.05 | 2077.33 |
| mTl2 | signal | 372722 | 0.16 | 14.38 | 22.67 | 66.98 | 107.58 | **133.05** |
| mTl2 | higgs | 783292 | 0.00 | 0.19 | 1.85 | 57.80 | 143.78 | 1200.53 |
| mTl2 | other | 2890113 | 0.00 | 0.18 | 1.78 | 75.13 | 202.72 | 986.19 |

The shared wall at `mll = 12` is just the `mll > 12` preselection — it applies to all
three classes and is expected. Everything **bolded** is the model's own doing.

## The findings

**1. `mTll` — a hard two-sided box on the signal class.**
`argmax = signal` never occurs below **mTll ≈ 52.8** or above **≈ 202**, while higgs and
other both run smoothly from 0 out to 800–2000. On a log axis the low edge is nearly
vertical. The signal class is confined to a *window*, not merely peaked in one.

**2. `mll` — a hard upper edge at ≈ 100 GeV** on the signal class, against 657 (higgs)
and 2861 (other). `dilepton_mass` *is* an input feature, so this is the network keying
on a variable it can see directly.

**3. `mTl2` — an upper edge at ≈ 133, but no lower wall** (signal reaches 0.16).
So the sharp lower cut is specific to `mTll`.

## How sharp is the wall?

Sharp enough that it is effectively a cut. `P(argmax = signal)` as a function of `mTll`,
over the whole 4.05M pool:

| mTll bin | N events | N argmax=sig | P(sig) | max P(hplusc) |
|---|---:|---:|---:|---:|
| [0,10) | 121,389 | 0 | 0.000% | 0.191 |
| [30,40) | 126,127 | 0 | 0.000% | 0.246 |
| [45,50) | 67,263 | 0 | 0.000% | 0.296 |
| [50,52) | 27,245 | 0 | 0.000% | 0.296 |
| **[52,53)** | 13,684 | **1** | 0.007% | 0.321 |
| [56,58) | 28,921 | 28 | 0.097% | 0.348 |
| [58,60) | 29,536 | 41 | 0.139% | 0.358 |
| [60,62) | 30,319 | 116 | 0.383% | 0.384 |
| [65,70) | 81,205 | 1,544 | 1.901% | 0.435 |
| [70,80) | 184,640 | 11,413 | 6.181% | 0.519 |
| [80,100) | 475,632 | 82,771 | 17.402% | 0.553 |
| [100,150) | 1,405,363 | 257,139 | 18.297% | 0.589 |
| [150,200) | 747,267 | 19,289 | 2.581% | 0.521 |
| [200,250) | 205,975 | **1** | 0.000% | 0.329 |
| [250,400) | 94,042 | 0 | 0.000% | 0.186 |

The decisive number: **662,103 events (16.4% of the pool) sit below mTll = 52.76, and
exactly one of them is assigned argmax = signal.** Their maximum `P(hplusc)` is 0.307
— never enough to win the argmax — and their mean is 0.033.

The mechanism is a smooth *probability ceiling* producing a hard *argmax* edge:
`max P(hplusc)` rises monotonically 0.19 → 0.30 → 0.59 across the wall and decays back
to 0.19 above 250. The network never assigns high signal probability outside the
window, so the argmax boundary is crisp even though the underlying score is continuous.

## Why `mTll` is the interesting one

**`mTll` is NOT one of the 17 v11 input features.** From
`b-hive/config/HPlusCHToWW_multiclass.yml`, `global_features` contains
`dilepton_pt, lepton1_pt, lepton2_pt, cjet_cand_pt, met_pt, mtl1, mtl2,
dilepton_mass, delta_R_ll_l1, delta_R_ll_l2, delta_R_ll_c,
delta_phi_l1PlusMET_c, delta_phi_l1_MET, delta_phi_l2_MET,
cjet_cand_cvsl_pnet, cjet_cand_cvsb_pnet, nSV` — no `mtll`.

But `mTll = transverse_mass(l1+l2, MET)` (`object_selections.py:547`) is a
deterministic function of the dilepton system and MET, and the network *does* see
`dilepton_pt`, `dilepton_mass`, `met_pt`, `mtl1`, `mtl2` and the
`delta_phi_l*_MET` angles. It has everything needed to reconstruct `mTll` internally.

So the wall is **emergent**: the model rebuilt an unseen variable out of its inputs
and then drew a hard boundary on it. It is not reading `mTll` off a column.

The location is suggestive. The SR selection is `mTl2 > 30 && mTll > 60`, and the
learned wall sits at **52.8, just below the 60 cut**.

**But the network did not copy the cut.** Two facts rule that out:

1. The v11 training workflow `hww_MVA.yaml` has **no mT or mll cut in its `base`
   category** (`grep -c` over the categories block returns 0 — the `transverse_mass_*`
   selections are *defined* but never applied). Training therefore spanned the full
   mTll range, including the region below 60.
2. The training labels are **process truth** (`is_hplusc`, `is_tt`, …), not SR
   membership. Nothing in the loss ever told the model where the SR boundary was.

So what the network learned is the **signal's true kinematic support**: H→WW→eμνν with
`mTl2 > 30` physically lives in that mTll window, and the SR cuts were themselves
designed around the same physics. Both the wall and the cut descend from the signal
distribution; neither descends from the other. That is precisely why the wall sits at
~53 rather than exactly 60 — it tracks where signal density actually dies, not where
someone drew a line.

The correct statement is therefore *not* "the MVA internalised the SR cuts" but
**"the MVA independently recovers the same kinematic region the SR cuts select,
because both follow the signal distribution."**

## Relation to the SR cuts

The model's own signal region and the hand-written SR cuts land on nearly the same
events — arrived at independently:

| | events | argmax=signal | rate |
|---|---:|---:|---:|
| passing SR kinematics (`mTl2>30 && mTll>60`) | 2,836,034 (70.1%) | 360,924 | 12.73% |
| failing SR kinematics | 1,210,093 (29.9%) | 11,798 | 0.975% |

**96.8% of all signal-argmax events already lie inside the SR kinematic cuts** — the
network reproduces the cut it was never given. Of the 3.2% that leak out, essentially
all leak through the **`mTl2 > 30`** boundary (11,732 of 11,798), not the `mTll > 60`
one (only 75). That asymmetry matches finding 3: the model built a hard wall in `mTll`
but only a soft one in `mTl2`.

So of the two SR cuts, `mTll > 60` is nearly redundant with what the MVA does on its
own, while `mTl2 > 30` is still doing independent work.

### The plots that show it

`internalised_2d_plane.png` — the (mTll, mTl2) plane coloured by the fraction of events
the model assigns argmax=signal, with both SR cut lines drawn on top. The signal-argmax
island's **left edge lands essentially on the mTll = 60 line**, while the mTl2 = 30 line
**cuts straight through the middle of the island** — the model is happy to call events
signal below it. The island is also bounded on the right (~170) and top (~120), edges
that no cut in the workflow imposes.

`internalised_profile_mTll.png` / `internalised_profile_mTl2.png` — the argmax=signal
rate vs each variable (red, left axis) with the mean `P(hplusc)` score overlaid (grey,
right axis).

| | rate below cut | rate above cut | ratio | signal-argmax events below cut |
|---|---:|---:|---:|---:|
| `mTll > 60` | **0.0098%** | 11.363% | **1160×** | 75 |
| `mTl2 > 30` | 1.8197% | 10.613% | 5.8× | 11,732 |

In the mTll profile the red curve is pinned at exactly zero across the whole region
below the cut and lifts off the axis at the line. In the mTl2 profile it is already at
~6% *at* the line and rises smoothly through it — no wall at all.

Both grey score curves are smooth and rise well before their cut, with no discontinuity
anywhere. That is the mechanism: **a continuous score meeting a hard argmax threshold**.
The score does not jump at 60; it simply crosses the level where `hplusc` starts winning
the six-way argmax.

## Why this matters

- The signal class is effectively a **kinematic box in a variable nobody put in the
  feature list**. Any statement of the form "the MVA selection is independent of the
  SR kinematic cuts" is false for this model — 96.8% of the SR cut is reproduced by
  the network on its own.
- The window is **two-sided**. Signal-like events with mTll > 202 or mll > 100 cannot
  be assigned to the signal class at all, regardless of their charm content. The upper
  edges are not imposed by any cut in the workflow — they are purely the model's.
- The edges are an **argmax** effect, not a score effect. `P(hplusc)` is continuous
  everywhere; it simply never rises above ~0.30 outside the window, so it never wins
  the six-way argmax. A discriminant built on `P(hplusc)` directly (rather than on
  the argmax-winner channel) would not have hard walls — worth remembering, since
  `discriminant: argmax_winner_score` is exactly what the combine block uses.
- **`mTll > 60` is nearly redundant** with what the MVA already does; `mTl2 > 30`
  still does independent work. If the SR definition is ever revisited, that is the
  asymmetry to exploit.
- If the fit is ever extended below mTll = 60, the network will not populate the SR
  there — the extension would be empty by construction, not by physics.

## The same study in the two control regions

Definitions taken from `hww_combine_fixed.yaml` (both are *defined* there; neither is
applied in the `base` category):

- **Top CR** = `mTl2 > 30 && mTll <= 60` — inverts the SR mTll cut. N = 565,368 (14.0%).
- **High-mll CR** = `mll > 72` — inverts the SR `mll <= 72` cut. N = 2,375,781 (58.7%).

Both are overwhelmingly tt by truth (78.1% and 83.0%), as a top CR should be.

### Which classes have the stats?

Measured first (`cr_populations.txt`), rather than assumed — and the answer differs
by region:

| argmax class | Top CR | High-mll CR |
|---|---:|---:|
| hplusc (signal) | **66 (0.01%)** | 21,607 (0.91%) |
| higgsbkg | 123,373 | 101,167 |
| tt | 240,095 | 1,186,251 |
| st | 32,594 | 585,580 |
| diboson | 71,071 | 418,425 |
| vjets | 98,169 | 62,751 |

**The Top CR has essentially no signal class — 66 events — and that is not a stats
accident.** The Top CR is *defined* as `mTll <= 60`, which is exactly the region where
the model refuses to assign signal. The CR sits wholly inside the model's signal-dead
zone. Max `P(hplusc)` anywhere in the Top CR is **0.358**, never enough to win the
six-way argmax.

So the class split is region-dependent:

- **Top CR** → the five populated background classes (tt, single-t, higgs bkg,
  diboson, V+jets). No signal curve — there is nothing to draw.
- **High-mll CR** → signal / higgs bkg / top (tt+st) / diboson / V+jets.

### What the CR plots show

`cr_topcr_2d_plane.png` — the whole plane is black (zero signal density) **except** a
sliver of cells pressed against the mTll = 60 line, peaking at just 0.48%. This is the
cleanest single view of the wall: an entire 565k-event region lies inside the dead zone,
with the handful of signal-argmax events clinging to the boundary.

`cr_himll_2d_plane.png` — a real signal island survives (max 12.0%), still walled at
mTll ≈ 60 on the left but **leaking below the mTl2 = 30 line**. The same asymmetry as
the SR, in a disjoint event sample — so it is a property of the model, not of the region.

`cr_topcr_mll.png` — inside the Top CR the background classes separate cleanly in mll
and **each has its own implicit edges**: diboson switches on at ~62, single-t at ~72,
while higgs-bkg and V+jets die off above ~110. The bounded-box behaviour is not special
to the signal class — every class occupies one.

`cr_himll_mll.png` — the signal class dies at mll ≈ 100 while the CR runs to 200+,
reproducing the inclusive upper wall against a background that continues smoothly.

| region | N | argmax=signal | rate | max P(hplusc) |
|---|---:|---:|---:|---:|
| Top CR | 565,368 | 66 | 0.0117% | 0.358 |
| High-mll CR | 2,375,781 | 21,607 | 0.9095% | 0.444 |

### Consequence for the fit

The Top CR cannot constrain anything about the signal class — by construction it holds
no signal-argmax events. That is fine if its job is to constrain the **tt normalisation**
(it is 78% tt by truth, and `CR_tt` is a real channel in the datacard). But it means the
Top CR gives **no handle on signal-region migration**, and any systematic whose effect is
to move events across the mTll ≈ 60 boundary will be unconstrained by it.

## Should we retrain without these cuts?

**No — and there is nothing to remove. v11 IS already the uncut training.**

`hww_MVA.yaml`'s `base` category contains no mT or mll selection, so the model was
trained on the full kinematic range. A "version without the SR cuts" is what we have.

Beyond that, the boundary is not a defect to be trained away. A correctly trained
classifier **must** assign low `P(signal)` where the signal density is ~zero — that is
what a good classifier *is*. Forcing it to spread probability into a region containing
no signal would make it worse, not better. The wall is evidence the training worked.

Retraining is therefore not the lever here. What *would* change the picture:

- **Use `P(hplusc)` directly instead of `argmax_winner_score`.** The hard walls are an
  argmax artifact, not a score artifact — the score is continuous everywhere. A
  discriminant built on `P(hplusc)` has no cliff and would keep the events currently
  discarded at the class boundary. This is a `combine:` block change, not a retrain.
- **Drop or loosen `mTll > 60`.** It removes almost nothing the MVA would have kept
  (75 events), so it costs acceptance without buying rejection. `mTl2 > 30` should
  stay — it is doing real work.

Neither requires touching the network.

### Caveats

- This is an argmax **class-assignment** study on 2022postEE MC only. It says where
  each class lives in kinematic space; it does not by itself say the model is
  mis-trained. A network that learns the SR boundary from label correlation is doing
  something reasonable — the point is that the boundary is *there* and undocumented.
- Raw and unweighted by design. Applying `lumi*xsec/sumw` would not move the edges
  (a weight cannot create or destroy an event's argmax) but would change the relative
  heights, so these plots must not be read as yields.
- Edge positions are quoted from the pooled MC min/max, so they are single-event
  extremes. The 1st-percentile values in the support table are the robust version.

## Reproduce

```bash
cd ~/higgscharm_thomas/higgscharm_thomas_new/higgscharm
micromamba run -n b_hive python -u plot_argmax_kin.py <outdir>
```

and for the sharpness / SR-overlap numbers:

```bash
micromamba run -n b_hive python -u edge_diag.py
```

and for the SR-overlap plots:

```bash
micromamba run -n b_hive python -u plot_internalised.py <outdir>
```

Scripts: [`plot_argmax_kin.py`](plot_argmax_kin.py), [`edge_diag.py`](edge_diag.py),
[`plot_internalised.py`](plot_internalised.py) (all also on lxplus in the repo root).

| output | content |
|---|---|
| `argmax_mll.png`, `argmax_mTll.png`, `argmax_mTl2.png` | per-class kinematic shapes |
| `internalised_2d_plane.png` | (mTll, mTl2) plane vs both SR cut lines |
| `internalised_profile_mTll.png`, `internalised_profile_mTl2.png` | argmax rate + mean score vs each cut |
| `cr_topcr_*.png`, `cr_himll_*.png` | the same split inside each CR (3 kinematics + 2D plane each) |
| `argmax_support.txt` | per-class support table |
| `argmax_edge_diagnostics.txt` | wall sharpness, SR overlap |
| `internalised_numbers.txt` | above/below-cut rates |
| `cr_populations.txt` | per-CR class populations (argmax **and** truth) |
| `cr_numbers.txt` | per-CR signal rates and max score |

CR plots and populations:

```bash
micromamba run -n b_hive python -u cr_pop.py          # populations, decides the split
micromamba run -n b_hive python -u plot_cr.py <outdir>
```

Left panel of each is raw counts on a log y-axis (a hard cut shows as a cliff to zero);
right panel is each class normalised to unit area for shape comparison.

## Related

- [[2026-07-19-ctag2d-full-documentation]] — the 2D ctag scheme
- [[2026-07-24-systematics-master-list]] — systematics inventory
- `decks-2026-07-31/` — the negrw and ctag decks
