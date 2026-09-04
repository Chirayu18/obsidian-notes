---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# ML4Jets 2026 deck — flashjet

LaTeX/beamer deck for **ML4Jets 2026** (Vienna, 14–18 Sep 2026).
Source: `flashjet-ml4jets.tex` → `flashjet-ml4jets.pdf` (**27 slides**, 16:9, Madrid theme).

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
| title + summary | 1–2 | validation ladder: unit tests → analytic closures → vs FastJet → vs the experiment → speed |
| **What flashjet is** | 3–7 | the CPU-in-a-GPU-pipeline problem; returns the tree not just jets; the API; what's implemented; **prototype status** |
| **Correctness** | 8–12 | analytic closures; clustering geometry; 150/150 vs FastJet; closure vs the experiment's own jets |
| **Speed** | 13–19 | benchmark method; time/jet; speedup vs multiplicity; R-independence; the numbers; caveats |
| **Conclusions** | 20–23 | summary, what's next, thank-you |
| **Backup** | 24–27 | per-sample scans, datasets |

27 slides, zero overfull boxes.

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
