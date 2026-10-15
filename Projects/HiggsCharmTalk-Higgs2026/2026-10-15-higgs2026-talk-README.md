---
tags: [reference, talk]
status: active
date: 2026-10-15
source: laptop
---

# Higgs 2026 talk: "Constraints on Higgs-charm couplings at CMS"

Higgs 2026, Louvain-la-Neuve, **Wed 28 Oct 2026, 09:20, 15+5 min** (Indico event 1668640).
CINCO: a reminder on 15 Oct asks for the **Final Draft within three days, i.e. by Sun 18 Oct**, at
https://cms-mgt-conferences.web.cern.ch/conferences/pres_upload.aspx?cid=4235&pid=33256 ;
also enter the bibliography on the presentation page.
Rehearsal: Indico event 1738114, **Thu 22 Oct 2026, 14:30** (30 min slot; chairs M. Schroeder, M. Donega). Errico (mass/width) and Daniel (exp. methods) rehearse on 21 Oct.

## Files
- `higgs2026_higgs_charm.tex` with theme `beamerthemecmstalk.sty`; build with `latexmk -pdf higgs2026_higgs_charm.tex`
- `figures/` is gitignored; `./fetch_figures.sh` re-downloads all 39 public figures and crops them to their bounding box
- 13 main slides including the title (12 content slides after the 2026-10-15 review fixes: ttH and cH each merged into one results slide), plus 10 backup slides. Review and fix list: [[2026-10-15-slide-review]]. Earlier layout: H+c has 3 slides (production, γγ, WW + combination): Jas Bierkens confirmed H+c is covered here, not in his rare processes talk. Condensed on 15 Oct to follow Zucchetta LP2025 plus post-LP2025 results; dropped the tagging slide, HIG-17-028, HIG-21-009, TOP-26-002 and DP-2025-081; HIG-23-013 is backup only

## Scope decisions
- Only public CMS results (papers, PAS, DP notes). No Run 3 Higgs-charm physics result was public on 2026-10-15:
  HIG-25-001, HIG-25-017 and HIG-26-003 all returned 404 on the public-results pages. The Athens workshop numbers for
  these (boosted VH 6.9, resolved VH 9.0, VBF ~40/16, ggH 14.3, scouting 27) are internal and must not appear.
- Run 3 slide uses only public material: BTV-25-002 (arXiv:2608.18331) and PAS TOP-26-003 (tt+b/c, released 2026-10-06).
- H→J/ψγ is one line on the indirect slide plus the summary table and a backup slide: J. Bierkens' rare Higgs
  processes talk (29 Oct) covers it.
- Novak's Athens projections and waterfall are "CMS+ATLAS private work": not used. Monti's ICHEP HL-LHC significance
  curve has no public reference, so it was not used either; HL-LHC slide uses arXiv:2504.00672 (|κc| < 1.5) and
  HIG-21-008 supplementary Fig. 50.
- (Superseded: H+c now has two slides, production + cH results.) Originally H+c got one slide: T. Bevilacqua's flavour-scheme talk is right after this one (09:40), and the rare-Higgs talks
  (Cabrera Urban, D'Eramo, Bierkens) cover H+c and J/ψγ in more detail.

## Number checks (against the papers, 2026-10-15)
- arXiv:2502.05665 is HIG-23-011, PRD 112 (2025) 112001: κc ∈ [−3.7, 3.2] (exp [−3.8, 3.3]), others floating.
  The "−3.4 < κc < 4.0" quoted in Davis's Athens deck is not in the paper.
- HIG-23-013 (JHEP 04 (2026) 093) gives only 2D (κb, κc) contours, no 1D κc interval.
- HIG-24-009 (H→WW + c) is published: JHEP 08 (2026) 051.
- Off-shell + on-shell H→4ℓ is HIG-25-003, arXiv:2607.23352: κc ∈ [−8.6, 7.5] (exp [−9.6, 8.3]) with κZ, κW profiled;
  [−3.3, 2.8] with |κV| ≤ 1.
- VH(cc) Run 2 limit is μ < 14 (7.6); the "≲ 12" in one Athens deck is wrong.
- arXiv:2511.21911 is the ATLAS VBF+VH(cc) paper, not CMS ttH.

## Sources
- Athens 2nd CMS Higgs-charm workshop, Indico 1645713 (June 2026), all decks
- Prior talks: Monti ICHEP 2026 (event 1522800, the closest template), Wuchterl Higgs 2024 and EPFL 2025,
  Cosby Higgs 2025, Giannini SUSY 2025, Generoso ICNFP 2026
- Indico token at `~/.indico_token` (Bearer header with the export and search APIs)
