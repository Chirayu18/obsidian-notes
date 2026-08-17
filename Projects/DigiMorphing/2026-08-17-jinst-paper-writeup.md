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
- "forward physics" → "recovered physics performance at high $|\eta|$"

**Not applied** (poster-only comments, rejected for the paper):
- the $d_{xy}$ drop — that comment was scoped to the poster, where the figure
  wasn't shown. The paper *does* show it, and Chirayu's tracking section keeps it.
- softening the J/$\psi$ result — rejected; the direct claim stands.

## Overleaf is the live copy — `6a5a2a3da030d5296033a920/` in the vault

Cloned 2026-08-17. **The Overleaf version had drifted well ahead of the Jul 17
local file**, so `jinst_paper/main_v2_writeup.tex` (built on the stale base) is
**superseded — do not paste it over Overleaf.** It would have destroyed work.

Already written by Chirayu on Overleaf, left untouched:
- **HLT tracking performance** — full section, keeps the $d_{xy}$ result
- **Physics performance (HLT scouting)** — cites the scouting stream `\cite{HLTscout}`
- cluster-size *definition* paragraph
- figure restructuring: `fig07/fig08` merged into one (a)/(b) float `fig:csize_xy`;
  `fig:csizex`, `fig:csizey`, `fig:csizeyL1eta/L2eta`, `fig:jpsiyield` now commented out
- `\usepackage{float}` + `[H]` floats; bib keys `AlpakaDP`, `HLTscout`, `timing`

Filled in only the genuinely empty sections: **Introduction**, **the algorithm**
(incl. implementation/deployment), **Impact on clusters**, **HLT local
reconstruction**, plus the **cluster-size trends** discussion appended after the
existing definition paragraph. Removed 6 stale `% TODO` markers (two sat above
prose that was already written).

Diff verified: **only deletions are the 6 TODO markers**; everything else is
pure addition. Compiles clean — 14 pp, no undefined refs, 0 overfull boxes.

### Lesson
`% TODO: writeup` markers on Overleaf are **stale** — two had finished prose
directly beneath them. Always read the following lines before filling a section.

## Open items

- **DP note number** unassigned (`AlpakaDP` bibitem).
- **Figures are still PNG**. Vector PDFs exist in `twiki/Alpaka-poster/newfigs/`.
  Four have no vector source (sensor cross-sections, config grid, detector regions).
- Typos in the pre-existing text: "iimproves" (fig:efficiency caption),
  "the cluster size in x" (lowercase sentence start, cluster-size section).
- Commented-out block at ~line 475 describing the $\eta$-split cluster-size
  trends refers to `fig:csize_y`, which no longer exists. Restore or delete.
- Push to Overleaf: `git -C 6a5a2a3da030d5296033a920 commit -am "..." && git push`

## 8-page restructure (2026-08-17, later)

Target was 8 pp. Landed at **12 total = 9 body + 3 appendix**.

**The page count was a layout problem, not a content problem.** `\usepackage{float}`
+ `[H]` pinned every figure in place, leaving 4 near-empty pages (one had 11 text
lines). Fixes that recovered ~4 pp:
- freed body floats `[H]` → `[htbp]`
- suppressed the auto TOC (`jinstpub` emits it from `\maketitle`)
- relaxed float params (`topfraction` .92, `textfraction` .08, `totalnumber` 5)
- shrank body figures (~0.32-0.6\textwidth)

**Measured, don't assume:** splitting the 3-panel resolution figure (§7) and the
x+y cluster-size figure (§8) into body+appendix **saved zero body pages** — 9 pp
either way, body pages 1-7 byte-identical — and *cost* one extra appendix page for
the extra floats/captions. Both were restored intact.

Appendix A now holds only genuinely repetitive figures:
extreme cluster comparison, η-split cluster size L1, η-split cluster size L2.

Body text now fills 9 pp on its own, so the last page would have to come out of
prose — conflicts with keeping DP wording verbatim. Left as a decision for Chirayu.

### Concurrent-edit collision
Chirayu was editing Overleaf while this ran. His new cluster-size paragraph
duplicated one written here (both explained the fill-to-fill spread, both cited
`pixelplots`). **Kept his, deleted the duplicate**, and fixed its stale "x and y
directions" phrasing. Check for this whenever both sides edit at once.

The commented-out η-split block in his file has a copy-paste bug (pulls
`fig10_..._outer` into the L1 pair) — appendix figures were rebuilt from the DP
originals instead.

