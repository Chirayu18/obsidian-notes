---
tags: [reference]
status: active
date: 2026-08-21
source: lxplus
---

# Page count + where the vector figures live

## Page count (current Overleaf clone build, 2026-08-17 18:30)

**12 pp total = 10 body + 2 appendix.**

- Body: pp. 1-10 (title page through Summary + bibliography)
- Appendix A "Supplementary figures": pp. 11-12

Note the earlier [[2026-08-17-jinst-paper-writeup]] said "9 body + 3 appendix" —
that was a mid-restructure count. The final committed state is **10 + 2**.

## Where the current paper is

- **Source + PDF:** `~/obsidian-notes/6a5a2a3da030d5296033a920/` (the Overleaf clone,
  in the vault). Clean tree, nothing unpushed — Overleaf and local agree.
- **PDF copy on EOS:** `/eos/home-c/cgupta/digimorphing/jinst_paper/main_current_2026-08-21.pdf`
- `jinst_paper/main_v2_writeup.pdf` on EOS is the **superseded** stale-base build. Ignore it.

## Vector figure sources — `twiki/Alpaka-poster/newfigs/`

23 of the 27 figures used in `main.tex` have a vector PDF. The names differ from the
paper's `figNN_*` names; mapping:

| main.tex (PNG) | vector PDF in `newfigs/` |
|---|---|
| `fig01_dilation_erosion` | `cand_E_final_T.pdf` |
| `fig02_cluster_comparison` | `fig3_303042568.pdf` |
| `fig04_res_localx` | `recHitXResLayer1.pdf` |
| `fig04_res_localy` | `recHitYResLayer1.pdf` |
| `fig05_efficiency` | `effic.pdf` |
| `fig05_fake_duplicates` | `fakeduprate_vs_eta.pdf` |
| `fig06_res_dxy` | `dxyres_vs_eta_Sigma.pdf` |
| `fig06_res_dz` | `dzres_vs_eta_Sigma.pdf` |
| `fig06_res_pt` | `ptres_vs_eta_Sigma.pdf` |
| `fig07_csizex_inner` / `_outer` | `hlt_sizex_inner_0.pdf` / `hlt_sizex_outer_0.pdf` |
| `fig08_csizey_inner` / `_outer` | `hlt_sizey_inner_0.pdf` / `hlt_sizey_outer_0.pdf` |
| `fig09_csizey_L1eta_inner` / `_outer` | `hlt_sizey_vs_eta_inner_0.pdf` / `hlt_sizey_vs_eta_outer_0.pdf` |
| `fig10_csizey_L2eta_inner` / `_outer` | `hlt_sizey_vs_eta_inner_1.pdf` / `hlt_sizey_vs_eta_outer_1.pdf` |

Identified by `pdftotext` on each vector PDF and matching the axis/legend text to the
paper captions — the `_0`/`_1` suffix is the **layer** (L1/L2), not inner/outer.

Same files also exist in `twiki/DigiMorphing2025/attachments/` and `posterfigs/`
(identical set). `newfigs/` is the post-review one — use it.

## Still raster — no vector source anywhere on EOS

- `config_grid.png`, `detector_regions.png`, `sensor_broken_shorter.png` — diagrams,
  not plot output. Would need redrawing.
- `fig03_cluster_comparison_extreme.png` — no PDF counterpart.
- `fig11_jpsi_yield.png`, `fig12_jpsi_mass_pos.png` — J/psi plots exist **only as PNG**
  everywhere (`posterfigs/`, `newfigs/jpsi_n_sig_vs_eta.png`). Needs regeneration from
  the fitting code if vector is wanted.
- `piechart_morph/nomorph.png`, `timing_table_*.png` — currently **commented out** in
  `main.tex` (the timing section uses Table 1 instead), so they don't matter.

So the real swap list is the 13 rows above; the J/psi pair is the only *plot* that
would need re-making.
