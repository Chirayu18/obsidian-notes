---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# ML4Jets 2026 deck — flashjet

LaTeX/beamer deck for **ML4Jets 2026** (Vienna, 14–18 Sep 2026).
Source: `flashjet-ml4jets.tex` → `flashjet-ml4jets.pdf` (**29 slides**, 16:9).

```bash
cd Projects/Flashjet/ml4jets
latexmk -pdf flashjet-ml4jets.tex      # pdflatex + beamer, all local
latexmk -c                             # clean aux files
```

Related: [[2026-09-03-atlas-opendata-full-survey]] (all benchmark numbers),
[[2026-09-04-ca-1M-verdict-and-pairwise]] (the ParT placeholders),
[[2026-07-31-ml4jets-abstract]] (framing).

---

## DATA POLICY — ATLAS Open Data only

**No CMS data appears anywhere in this deck.** This was an explicit requirement
and it is enforced, not assumed:

- every CMS-derived figure was **deleted** from `fig/`, including ones with
  neutral-looking names that were actually CMS MINIAOD/NanoAOD
  (`ak4_*`, `ttbar_*`, `compare_*`, `tree_*`, `fullevent_match`,
  `outlier_anatomy`, `tvars_*`, `tagger_*` — the tree gallery was traced to
  CMS `GenPart`);
- `grep -in "cms\|nanoaod\|miniaod\|jmenano\|msoftdrop\|FatJet"` over the `.tex`
  returns **nothing**;
- the 11 figures actually referenced are ATLAS benchmark plots or
  toy/analytic closures.

**If you add a figure, check its provenance first.** Several files in the old
decks' `img/` are CMS-derived despite generic filenames.

### What survived the purge

| figure | source |
|---|---|
| `atlas_abs_timing.png` | ATLAS Top Tagging Open Data (new) |
| `atlas_speedup_algs.png` | ATLAS, all 3 algorithms (new) |
| `atlas_R_independence.png` | ATLAS, R-scan (new) |
| `atlas_{radius_scan,multiplicity}_atlastop-{top,qcd}.png` | ATLAS sweep |
| `zg_distribution.png`, `softdrop_rho.png` | toy shower (Input B) vs analytic |
| `jet_areas.png`, `lund_triangle.png`, `qcd_beta_family.png` | toy / analytic |
| `nsys_*`, `ncu_*` | Nsight profiling — hardware counters, no physics data |
| `kt_observables.png`, `lund_plane.png` | toy (Input A) — **spares**, not used |

---

## Structure

| § | slides | content |
|---|---|---|
| title | 1 | states the ATLAS-only data policy up front |
| **What flashjet is** | 2–6 | the CPU-in-a-GPU-pipeline problem; what it returns (assignment **+ full merge history**); the API; **what is implemented**; **prototype status** |
| **Physics validation** | 7–8 | analytic closures: soft-drop $z_g$ on the $1/z$ curve, $\beta$-ordering, jet areas, Lund triangle |
| **Benchmark** | 9–16 | dataset + method; **correctness (150/150)**; ATLAS `RecoJets_R4` closure; time/jet; speedup vs multiplicity; R-independence; the numbers table; **caveats** |
| **ParT + C/A** | 17–18 | **`[PLACEHOLDER]`** — left deliberately unfinished |
| **Profiling** | 19–20 | nsys kernel share, ncu counters, the named bottleneck |
| **Conclusions** | 21–23 | summary, what's next, thank-you |
| **Backup** | 24–29 | repro commands, per-sample scans, GPU timeline, occupancy, **why not PHYSLITE** |

### The "prototype" framing (requested)

Slide 6 is explicit: flashjet is a **prototype**, not production software. It
lists what is solid (129 unit tests, FastJet agreement, analytic closures,
reproduces an experiment's own jets) against what it is not yet (not inside
experiment software, Python-binding CPU baseline, GPU largely idle, no pile-up
study). The caveats slide (16) and "what's next" (22) repeat this.

---

## The placeholder slides — LEFT INTENTIONALLY UNFINISHED

Slides 17–18, both titled `[PLACEHOLDER]`, cover **ParT + C/A features on
JetClass**. Per instruction these are **not to be treated as final**. The numbers
on them are the real measured state as of **2026-09-04**, taken from
[[2026-09-04-ca-1M-verdict-and-pairwise]]:

- matched 480k checkpoint, 20.05 M-jet test set: accuracy **85.625 %** (baseline)
  vs **85.524 %** (+C/A), Δ = **−0.102**; mean 1-vs-QCD AUC 0.98981 → 0.98970;
- all nine classes marginally worse, but **inside the ~1.3-point seed spread** —
  the deck says *"indistinguishable from baseline, with a consistent negative
  sign"*, **not** "C/A hurts";
- the earlier **+1.3 at 20k iterations was a training transient**, and the deck
  says so;
- root cause on slide 18: **measured group size is exactly 1.00**, so the
  features carry zero prong-grouping information; the pairwise redesign was built
  and **cancelled unrun** because `share_bp` is identically zero;
- current attempt: **subjet-level features at $k_t$ cut 20 GeV**
  (`part_sj_lnm`, `part_sj_lnptfrac`, `part_sj_nconst`) — passes the set-model
  probe, **training result pending**.

**Before the talk:** replace with the subjet-feature result once it trains, or
cut both slides if it has not.

---

## Where the numbers come from

Every benchmark figure traces to the sweep in
[[2026-09-03-atlas-opendata-full-survey]]:

- **Correctness 150/150** — 3 algorithms × 5 radii × 5 multiplicity bins ×
  2 samples, 20 000 jets/bin, 100.000 % $n_{jets}$ agreement at every point.
- **The two non-1.0000 rows** are the *same single jet* (a constituent assigned
  across an $R$ boundary). Slide 10 states this rather than rounding to 100 %.
- **39–99× (median 64×)** on a **Tesla V100S** — the deck says V100S in the
  table caption, on the caveats slide, and in the summary, precisely so nobody
  reads it as an H100 number.
- **ATLAS `RecoJets_R4` closure** — 100 % jet-count match, 10.96 vs 10.96
  jets/event, at 599.3 clusters/event.

Raw results on lxplus: `/eos/home-c/cgupta/flashjet/bench_atlas/results_v100/`
(150 + 150 JSON), tables `atlas_table_atlastop-{top,qcd}.md`.

### Known caveats carried into the deck

1. **V100S, not H100** — a lower bound; H100 should be ~2× above.
2. **CPU baseline is the Python FastJet binding**, not C++ FastJet. Flagged on
   the caveats slide in red as the single most valuable missing test.
3. **Large-$R$ jets** (~50–120 constituents), not small-$R$.
4. **Batch regime** — a per-event framework may not exploit it.

---

## Rebuilding the ATLAS plots

The three new plots are generated on lxplus from the sweep JSONs:

```bash
# on lxplus, b_hive python
python /tmp/mk_extra_plots.py     # -> atlas_abs_timing / _R_independence / _speedup_algs
python make_atlas_plots.py        # -> atlas_radius_scan_* / atlas_multiplicity_*
```

Source scripts live in `/eos/home-c/cgupta/flashjet/bench_atlas/`.
Copy the PNGs into `fig/` and rebuild.
