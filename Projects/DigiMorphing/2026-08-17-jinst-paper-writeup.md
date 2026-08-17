---
tags: [reference]
status: active
date: 2026-08-17
source: lxplus
---

# JINST paper writeup — filled from the reviewed poster

Filled the seven `% TODO: writeup` sections of the digi morphing JINST paper using
the **reviewed** conference poster as the prose source, and propagated the poster's
two rounds of review comments into the paper.

## Where everything lives (EOS, not `EPR_task`)

The Todo said "find the alpaka DP note in EPR_task" — it is **not** there.
`~/eos/EPR_task/` is unrelated b-hive/ML code. Everything is under `~/eos/digimorphing/`:

| Path | What |
|---|---|
| `DP_note_digi-morphing.pdf` | the DP note |
| `jinst_paper/main.tex` | JINST skeleton (Jul 17) — figures + captions only, body blank |
| `jinst_paper/main_v2_writeup.tex` | **new** — body written up, compiles clean |
| `poster_digimorphing.tex` | first poster |
| `twiki/Alpaka-poster/poster_updated.tex` | **poster after 2 review rounds** ← prose source |
| `twiki/Alpaka-poster/comments.md` | review comments + how each was resolved |
| `twiki/Alpaka-poster/CHANGES.md` | exact before/after LaTeX for each change |
| `twiki/Alpaka-poster/newfigs/` | **vector PDF** versions of the plots |
| `twiki/DigiMorphing2025/` | TWiki source + attachments |

**Use `poster_updated.tex`, not `poster_digimorphing.tex`** — the latter is pre-review.

## Sections written

Introduction, the algorithm (+ new "Implementation and deployment" subsection),
impact on clusters, HLT local reconstruction, HLT tracking, cluster size trends,
physics performance. Summary + abstract also revised.

## Review comments propagated into the paper

- "alpaka portability **library**", not "framework"
- no hyphen in "digi morphing" or "charge collection efficiency"
- "pixel local reconstruction at HLT", not "HLT local reconstruction"
- morphing recovers **broken** clusters but **cannot** recover shortened ones (was missing)
- over-merging (different tracks) / under-merging (gap too large) are the limitations —
  merging same-angle fragments is *wanted*, not a flaw
- central region "lies outside the morphed rings and is unchanged by construction"
- $p_T \approx 10$ GeV, not $> 10$ GeV
- dropped the $d_{xy}$ claim (reviewer: not shown) — **but the paper still has
  `fig06_res_dxy.png`**; either cite it or drop the figure
- "forward physics" → "recovered physics performance at high $|\eta|$"
- softened the J/$\psi$ result: 2025G vs 2025G-digi differ in *detector conditions*
  too, so it is not a controlled A/B test

## Open items

- **Author list** — poster has 4 (Gupta, Nandakumar, Delcourt, Petersen/UCLouvain);
  skeleton had 2. Applied the poster's list, flagged in a comment. Confirm.
- **DP note number** unassigned: `CMS-DP-2026-XXX` in `\bibitem{dpnote}`.
- **Figures are still PNG** in `jinst_paper/figs/`. Vector PDFs exist in
  `twiki/Alpaka-poster/newfigs/` — swap them in for print quality.
  Four have no vector source (sensor cross-sections, config grid, detector regions).
- **Overleaf not reconciled** — `main_v2_writeup.tex` is based on the *local* Jul 17
  file, which may have drifted from Overleaf. Diff before pasting.

Overleaf git clone needs a token (Account Settings → Git integration), username `git`:
`git clone https://git.overleaf.com/6a5a2a3da030d5296033a920`
