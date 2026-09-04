---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# ML4Jets 2026 deck — flashjet

LaTeX/beamer deck for **ML4Jets 2026** (Vienna, 14–18 Sep 2026).
Source: `flashjet-ml4jets.tex` → `flashjet-ml4jets.pdf` (**32 slides**, 16:9, Madrid theme).

```bash
cd Projects/Flashjet/ml4jets
latexmk -pdf flashjet-ml4jets.tex      # pdflatex + beamer, all local
latexmk -c                             # clean aux files
```

Related: [[2026-09-03-atlas-opendata-full-survey]] (all benchmark numbers),
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
- `grep` for CMS terms over the `.tex` returns **nothing**;
- the figures actually referenced are ATLAS benchmark plots or toy/analytic
  closures.

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
| `kt_observables.png`, `lund_plane.png` | toy (Input A) — **spares**, not used |

Profiling figures (`nsys_*`, `ncu_*`) were **removed** — see the disclosure
policy below.

---

## Structure

Modelled on the substructure deck: a **summary/validation-ladder slide up front**,
then **lead section dividers**, one claim per slide. Theme is **Madrid**
(classic HEP header/footer bars), recoloured to the flashjet red.

| § | slides | content |
|---|---|---|
| title + **outline** | 1–2 | `\tableofcontents` |
| **Jet clustering, and flashjet** | 3–15 | **jet clustering: the workhorse and its cost** (IRC safety, sequential dependency, and a table of how often clustering is re-run — ML is one row, not the headline); **flashjet** (what it is, how it is implemented, backends, prototype status); **how sequential recombination works** (3-panel figure); **one exponent → three algorithms**; returns the tree; the API; what's implemented + prototype status; **F1**, **F2**, **F3** one slide each, plus a **real-jet C/A tree gallery** |
| **Correctness** | 13–17 | analytic closures; clustering geometry; 150/150 vs FastJet; closure vs the experiment's own jets |
| **Speed** | 19–23 | benchmark method; time/jet; speedup vs multiplicity; R-independence — **headline numbers now sit in the plot captions**, not a separate table |
| **Conclusions** | 24–26 | summary, thank-you |
| **Backup** | 27–32 | per-sample scans, **the numbers table**, datasets |

32 slides. **Removed** on request: the *opportunity: data is already on the GPU*
slide (folded into the two opening slides), and earlier the old *Summary*, *Caveats* and *What is next*
slides. The caveats they carried (Python FastJet baseline, large-$R$ jets, batch
regime) now live only in this README — **decide whether to reinstate any verbally**.

### Feature slides (F1/F2/F3)

Each follows the same shape: **What it does / How / Why this tree** on the left,
an illustrative plot on the right.

| slide | figure | shows |
|---|---|---|
| F1 exclusive subjets | `kt_observables.png` | $\sqrt{d_{12}}$ and subjet $z$ separating toy W-like from QCD-like |
| F2 soft drop | `softdrop_walk.png` | **generated for this deck** — ungroomed vs groomed mass, plus the declustering walk on the C/A tree |
| F3 Lund coordinates | `lund_plane.png` | QCD soft-collinear fill vs the localised W hard splitting (star = prediction) |
| tree gallery | `tree_gallery.png` | **real ATLAS jets** — QCD staircase (n_drop 8, mass 80→1 GeV) vs two boosted tops that stop immediately (n_drop 0, at 80 and 170 GeV) |

### The tree gallery

Drawn in the style of the C/A-tree artifact: **root at top, constituents at the
bottom**, thin uniform grey edges, small filled leaf dots, and hollow rings
marking the soft-drop spine / dropped prongs / stopping node.

Built by `make_tree_gallery.py`, which runs **on lxplus** (it reads the ATLAS
Top Tagging HDF5 at `/tmp/cgupta_toptag_test.h5`), clusters real jets with C/A
and runs the soft-drop walk on the resulting tree.

The old deck's tree gallery could **not** be reused: those jets are CMS
`GenPart`-verified. A toy version was tried first and rejected — the toy did not
reproduce the staircase-vs-short-spine contrast (it gave n_drop 0 for both the W
and top cases), so the captions would have overclaimed. The real jets show it
cleanly.

Two figures were **generated for this deck** by `make_illustrations.py` (pure
toy/analytic, no experiment data):

- `clustering_steps.png` — constituents → smallest $d_{ij}$ → merge/record/repeat
- `softdrop_walk.png` — the F2 mass effect and the tree walk

Rerun with `python3 make_illustrations.py`.

### Two policies enforced in the source

**1. No CMS data.** Every CMS-derived figure was deleted from `fig/`, including
ones with neutral filenames that were actually CMS MINIAOD/NanoAOD (`ak4_*`,
`ttbar_*`, `compare_*`, `tree_*` traced to `GenPart`, `fullevent_match`,
`outlier_anatomy`, `tvars_*`, `tagger_*`). **If you add a figure, check its
provenance first** — several files in the old decks' `img/` are CMS-derived
despite generic names.

**2. No profiler internals.** The deck must not expose GPU-tuning detail. Cut
entirely: both Nsight slides, all four `ncu_*`/`nsys_*` figures, and every
occupancy / register-count / SM-count / waves-per-SM number, plus the
~1.7–1.8× headroom estimate. Hardware is stated **only** as "NVIDIA V100-class",
once, on the numbers slide; the caveats slide says "a single GPU generation was
benchmarked" without naming a better one.

Verify both with:

```bash
grep -in "cms\|nanoaod\|miniaod\|jmenano" flashjet-ml4jets.tex
grep -in "H100\|A100\|Tesla\|occupancy\|register\|DRAM\|Nsight\|waves" flashjet-ml4jets.tex
```

Both should return only the policy comments at the top of the file.

### The "prototype" framing

Stated on the summary slide, again as a `Status` block on "What is implemented",
and once more in the conclusions. It lists what is validated against what is not
yet done (not inside experiment software, Python-binding CPU baseline).

## Where the numbers come from

Every benchmark figure traces to the sweep in
[[2026-09-03-atlas-opendata-full-survey]]:

- **Correctness 150/150** — 3 algorithms × 5 radii × 5 multiplicity bins ×
  2 samples, 20 000 jets/bin, 100.000 % $n_{jets}$ agreement at every point.
- **The two non-1.0000 rows** are the *same single jet* (a constituent assigned
  across an $R$ boundary). Slide 10 states this rather than rounding to 100 %.
- **39–99× (median 64×)** — the deck says only "NVIDIA V100-class", once. The
  underlying card and all profiling detail are deliberately withheld.
- **ATLAS `RecoJets_R4` closure** — 100 % jet-count match, 10.96 vs 10.96
  jets/event, at 599.3 clusters/event.

Raw results on lxplus: `/eos/home-c/cgupta/flashjet/bench_atlas/results_v100/`
(150 + 150 JSON), tables `atlas_table_atlastop-{top,qcd}.md`.

### Known caveats carried into the deck

1. **CPU baseline is the Python FastJet binding**, not C++ FastJet. Flagged on
   the caveats slide in red as the single most valuable missing test.
2. **Large-$R$ jets** (~50–120 constituents), not small-$R$.
3. **Batch regime** — a per-event framework may not exploit it.
4. **Hardware** — the deck says only that one GPU generation was benchmarked.
   The numbers are a lower bound; that is stated without naming a better card.

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

---

## Review pass (2026-09-04)

Changes made after a read-through:

- **Opening rewritten for an expert audience.** The old "a quark hadronises into a
  spray" framing was too general; it now leads with IRC safety and the sequential
  dependency that keeps clustering on the CPU. The vague "essentially every LHC
  measurement runs this step" claim is replaced by a **table of how often
  clustering is re-run** (reconstruction, JES/JER systematics, substructure,
  scans, ML training).
  - *A CMS-approved plot was requested here. Not usable — the deck is
    ATLAS-only, and an approved plot cannot be fabricated. The table is the
    stated alternative.*
- **"The opportunity" slide removed**, replaced by a **flashjet** slide (what it
  is, how it is implemented, the three backends, prototype status).
- **API slide reworked into documentation style**: the call, an argument table
  (type + meaning), then the returns.
- **Differentiability note moved** out of the API slide to after *What is
  implemented*, where it now has its own block.
- **Plots enlarged** on the F3 slide; text moved to a three-column strip below.
- **`The numbers` table moved to backup.** The headline figures (0.35–2.7 µs/jet,
  39–99×, median 64×) now appear as **captions under the plots** instead.
- **Hardware name removed from two plot titles** — `atlas_abs_timing.png` and
  `atlas_speedup_algs.png` had "Tesla V100S" baked into the image. Regenerated
  via `make_speed_plots.py`. The deck says "V100-class" once, in a caption.
