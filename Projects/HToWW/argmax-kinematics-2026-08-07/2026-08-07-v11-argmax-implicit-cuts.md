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

The location is suggestive. The SR selection is `mTl2 > 30 && mTll > 60`. The learned
wall sits at **52.8, i.e. just below the 60 cut** — consistent with the network having
learned the SR boundary from the training-label correlation and reproducing it with
finite resolution rather than exactly.

## Relation to the SR cuts

The model has effectively *internalised* the SR selection:

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

Scripts: [`plot_argmax_kin.py`](plot_argmax_kin.py), [`edge_diag.py`](edge_diag.py)
(both also on lxplus in the repo root).
Plots: `argmax_mll.png`, `argmax_mTll.png`, `argmax_mTl2.png`.
Support table: `argmax_support.txt`. Edge/SR numbers: `argmax_edge_diagnostics.txt`.

Left panel of each is raw counts on a log y-axis (a hard cut shows as a cliff to zero);
right panel is each class normalised to unit area for shape comparison.

## Related

- [[2026-07-19-ctag2d-full-documentation]] — the 2D ctag scheme
- [[2026-07-24-systematics-master-list]] — systematics inventory
- `decks-2026-07-31/` — the negrw and ctag decks
