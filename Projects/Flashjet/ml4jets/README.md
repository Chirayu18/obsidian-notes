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

---

## Second review pass (2026-09-04)

Reframed around the ML4Jets abstract.

- **Opening replaced.** The "what jet clustering is" framing is gone. It now
  opens on **heterogeneous reconstruction**, anchored in a citable public fact:
  CMS has run GPUs in the Run 3 HLT since the start, offloading **~30 % of HLT
  reconstruction** for a **~25 % timing reduction** — tracking, vertexing and
  calorimetry are all ported, and **jet clustering is not**. That is the gap the
  talk addresses.
  - *This cites CMS as published context, not CMS data. No CMS event or plot
    appears anywhere — the data policy is intact.*
- **flashjet slide rewritten.** The three-backend list was dropped (only
  `triton_large` is used in practice, so it was misleading). It now says what is
  actually interesting about the code: the **Cacciari–Salam nearest-neighbour
  lemma** giving O(N²) per event instead of O(N³), the bandwidth-bound fused
  sweep, branchless pair-vs-beam via masked stores, and autotuning cached **once
  per GPU model** so runs stay reproducible.
- **Formulas added.** The generalised-\(k_t\) distance measure (\(d_{ij}\),
  \(d_{iB}\), \(\Delta R_{ij}\)) is now displayed on the algorithms slide with
  the \(p\)-table under it; splitting scales on F1; Lund coordinates on F3.
- **"It is differentiable" removed.**
- **Layout:** the clustering-steps figure enlarged; the algorithms slide rebuilt
  (table + formulas left, plot right) instead of the cramped stacked version.
- **Zero overfull boxes** for the first time.

---

## Third review pass (2026-09-04)

- **Slides 2 and 3 converted to bullets.** Both were paragraph-heavy; they now
  read as scannable points, with "not jet clustering" called out in red as the
  punchline of the opening.
- **Algorithms slide split in two**: the distance measure + the \(p\)-table on
  one, and the jet-areas figure alone on the next at ~3× the size.
  - This left `jet_areas.png` appearing **twice**, so it was dropped from
    *Clustering geometry*; the remaining two figures there are now larger.
- **Removed** the "kt and C/A had never been checked against FastJet on real
  data" claim and the single-outlier-jet footnote from the correctness slide.
- **Conclusions section divider removed** (the Summary slide remains).
- **Profiling restored to backup** — four slides: nsys kernel share + ncu
  counters, the GPU timeline, the "small grid" bottleneck with NVIDIA's
  ~1.7–1.8× estimate, and occupancy detail.

### Disclosure status changed

This **reverses** the earlier removal. The main slides are still clean —
hardware appears once as "V100-class", no counters. But the **backup section now
carries the full profiler detail** (occupancy 6.25 %, 168 registers/thread, 0.32
waves/SM, the 132-SM grid finding, the headroom estimate) and its figures are
labelled **H100**.

**If the audience should not see that, delete the four `Backup ---` profiling
slides.** The policy comment at the top of the `.tex` says the same.

36 slides, zero overfull boxes.

---

## Fourth pass — aligned with the substructure deck (2026-09-04)

Read the substructure deck's results section and adopted its conventions.

**What that deck does that this one did not:**

1. **Every correctness slide is labelled with its input.** That deck uses an
   A/B/C taxonomy (toy fat jets / toy shower / real data) and tags each slide.
   This deck now carries the same tags in the frame titles — `[toy A]`,
   `[toy B]`, `[ATLAS Open Data]` — so an audience always knows whether a plot
   is generated or measured.
2. **Toys come first, real data second.** That ordering is deliberate: on toys
   the answer is known analytically, so a miss is unambiguously a bug; on real
   data the reference is FastJet. Added a **"Two kinds of validation"** slide
   that states this explicitly before the closures.
3. **The toys are documented.** That deck devotes slides to how each input was
   generated. Added two backups with the actual specs:
   - **Input A** — QCD-like (92 % collinear core, σ=0.06 + 8 % soft at σ=0.30)
     and W-like (two prongs, m = √(z(1−z))·p_T·ΔR = 80.4 GeV, z ∈ [0.30,0.45]),
     with the spray code
   - **Input B** — primary fixed-coupling leading-log shower, uniform in the
     Lund triangle, with the sampling relations and the ghost construction used
     for jet areas (ᾱ = 0.25, p_T0 = 1 TeV, 20 000 showers)
4. **A validation ladder backup**, matching that deck's summary table: each rung
   with its input and its independent reference, making explicit that **no rung
   is validated against another part of flashjet**.

Also filled the whitespace left on the FastJet-agreement slide (after the two
claims were removed) with why the *grid* matters and the two independent
references.

40 slides, zero overfull boxes.

---

## Fifth pass — the jet-by-jet closure, on ATLAS (2026-09-04)

**Yes, the CMS-style jet-by-jet closure is reproducible on ATLAS data.** The
earlier note that it was not has been superseded.

Two closures, `make_jetbyjet.py` (4000 jets):

| closure | reference | result |
|---|---|---|
| reclustered \(p_T\) | stored `fjet_pt` | median **0.8711**, IQR **0.0133** |
| \(k_t\) splitting scale \(\sqrt{d_{12}}\) | stored `fjet_Split12` | median **1.0000**, IQR **0.0000**, **99.9 %** within 1 % |

The second is the strong one and the direct analogue of the CMS `msoftdrop`
closure: **ATLAS computed `Split12` with FastJet and stored it**, and we recover
it by reading the merge history — no reclustering, no second pass. The perfect
delta at 1.0000 is what a closure should look like.

The \(p_T\) ratio is deliberately **not** claimed as agreement: 0.87 is the
stored jet's calibration, applied after clustering. The tight 0.013 spread is the
real content — the *shape* closes even though the scale is offset.

**On the groomed mass.** The top-tagging file has no groomed mass, so a direct
`m_SD` analogue is not available there. The 2020 Jet Reconstruction dataset does
ship `RecoJets_R10_Trimmed_m` (ATLAS trimming, not soft drop), which would give a
groomed-mass closure against a *different* grooming algorithm — worth doing if a
groomed-mass slide is wanted, but it is not the same observable.

### Slide moved to backup

**Clustering geometry** (Lund triangle + β-family) → `Backup --- more toy
closures`. With the jet-by-jet ATLAS closure now in the main line, two toy-only
slides in a row was one too many.

### Placeholders

Two blank **ParT training** placeholders added before the Summary, under their
own section divider — `[ to be filled in ]`, nothing else.

44 slides, zero overfull boxes.

---

## Provenance audit (2026-09-04)

Prompted by a check on the F2 slide. It is **not** CMS data — `softdrop_walk.png`
is generated by `make_illustrations.py` from an `rng`-seeded toy two-prong sample
plus a hand-drawn schematic tree, with no file reads at all.

But the check exposed a real inconsistency: **F2 was the only F-slide without an
input tag**, while F1 and F3 both carried `[toy A]`. Audited every figure-bearing
slide and closed the gaps:

| slide | figure | tag |
|---|---|---|
| How sequential recombination works | `clustering_steps` | `[toy A]` ← added |
| anti-kt gives rigid, circular jets | `jet_areas` | `[toy B]` ← added |
| F2 soft drop | `softdrop_walk` | `[toy A]` ← added |
| Backup — speedup vs R | `atlas_radius_scan_*` | `[ATLAS Open Data]` ← added |
| Backup — speedup vs multiplicity | `atlas_multiplicity_*` | `[ATLAS Open Data]` ← added |
| The benchmark / Time per jet / speedup / R-independence | ATLAS speed plots | `[ATLAS Open Data]` ← added |

**Every slide carrying a figure now states its provenance.** No CMS data appears
anywhere in the deck; the only CMS mention is the published HLT-GPU fact cited on
the opening slide.
