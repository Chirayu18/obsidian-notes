---
tags: [reference, talk, review]
status: active
date: 2026-10-18
source: laptop
---

# Slide review 3: Higgs 2026 HTML deck (text size, correctness, minor)

Deck: `html/higgs2026_higgs_charm_main.pdf` (19 main slides, built from `html/deck.html` at fc43d92). Config: `slide-review.json` (public, 15+5 min). On Chirayu's request the scope is narrow: content and storyline are already reviewed and liked, so this covers only text size and legibility, correctness and minor polish. Previous reviews: [[2026-10-16-slide-review]], [[2026-10-15-slide-review]].

**Status:** no blockers. Layer 1 is clean: no forbidden patterns and no internal markings. Of roughly 90 claims checked against the papers, 4 are contradicted (one major, three minor). Everything else matches.

## Correctness

1. [major] S6 "VH(H→cc̄): results": the subtitle "The most sensitive single channel of Run 2" holds for expected μ (VH 7.6 vs ttH 8.7) but not for κc. Expected |κc| is 3.3 for ttH alone (κb = 1, arXiv:2509.22535 p.7) and 3.4 for VH (2205.05550). Both values sit on S16, so a reader comparing the two slides will see the clash. Fix: subtitle "Best expected μ of any single Run 2 channel". The take-away already says "Expected μ < 7.6", which is fine.
2. [minor] S4 "Rare exclusive decays" tag reads "slide 15", but J/ψγ is on slide 16 (the table row). Fix: `deck.html:171`, change the tag to "slide 16".
3. [minor] S5: the "p_T^H = 300 GeV" pill. The split is on the pT of the reconstructed large-R (R = 1.5) H-candidate jet, not on true pT(H). 2205.05550 p.3: "a given H_cand, identified through a large-R jet, has pT above or below a threshold of 300 GeV". Fix: "p_T(H_cand) = 300 GeV". The ">95% of the signal" bullet does use true pT(H), so it can stay.
4. [minor] S3, DeepJet "on all jet constituents": DeepJet uses at most 25 charged and 25 neutral candidates plus 4 SVs (arXiv:2008.10519). Fix: "on up to 50 jet constituents and 4 SVs", or just "on jet constituents".
5. [nit] S9: the paper calls the validation region "signal-depleted", while the slide says "no signal". S7: DeepDoubleX inputs are PF candidates and SVs ("tracks" is close enough).
6. [carried over, already accepted] S19 Direct card, "most stringent direct constraint": this is the paper's wording, but S16 shows ttH alone at 3.0 below the combined 3.5. Have a Q&A line ready.

Unverified: S3 "UParT … adversarial training". The DP-2025-081 text is behind the CDS bot wall. The "UParT v2 lowest mis-ID" annotation is verified from the figure.

## Text size and legibility

Measured from the PDF (mutool stext; the slide is 1280×720 px). Body text is 21 px, about 16 pt in a 13.3-inch PowerPoint frame. The usual floor for a conference room is about 18 pt (24 px) for content. The following text is noticeably below that:

| Slide | Text | Size | Room to grow? |
|---|---|---|---|
| S3 | Tagger descriptions in the three algorithm boxes ("likelihood of track impact parameters", "dense DNN (4×100)", …) | **13.5 px**, the smallest content text in the deck | Little room. Drop the descriptions to one line each and set them at 16 px |
| S5 | Resolved and merged bullets | 15.5 px | Some: the boxes could go down to y ≈ 560 |
| S19 | Card sub-notes ("most stringent direct constraint…", "with \|κV\| ≤ 1 (about ±8 without)", "tt̄cc̄ background already measured") | 15 px | Yes: about 90 px free below the orange box. Go to 17 to 18 px |
| S4 | Card text 21 px with refs at 14 px | ok | Yes: about 130 px empty between the cards and the footnote. Make the cards taller and the text bigger (κc numbers already big) |
| S7, S12, S13, S14 | Step-card bullets | 16.5 px | S12 has space under the challenges and next to the diagrams. S13 and S14 are full |
| S6 | Uncertainty-bar labels and caption | 15 px | Ok as secondary |
| S18 | Bar-chart labels 16 to 17 px, axis 14 px | ok | About 130 px empty at the bottom. The chart could be 20% taller |

Figures whose text cannot be read from the back (these come from the papers, so the fix is size or a crop):
- **S6 left** (μ limits per category): the per-category "Expected / Observed" labels are about 7 px. The image is about 360 px wide. Widen it to about 480 px, since the stat box below can shrink. Same point as the 16 Oct review, still open.
- **S10** (post-fit discriminants): the region labels are about 6 px. It is an overview, so fine as a picture, but 130 to 180 px of vertical space is free above it and 70 px below. Making it about 20% bigger costs nothing.
- **S9** (classifier flowchart): node text is about 11 px. Acceptable, since the strip on the left carries the message.
- **S15** (κc scans): the legend is about 9 px. The caption gives the colour key, so fine.
- **S11 right**: the legend is tiny, and the red/blue key is not in the caption. Add "red ttH, blue VH, black comb." to the caption.

## Minor polish

- S10 table header: the hat in "best fit μ̂" renders after the μ, not on it (combining U+0302 in Inter). Use `μ&#x0302;` inside a span with a math-capable font, or write "μ (best fit)". The same μ̂ appears in backup slides (`deck.html:708, 722, 836, 861`).
- S8: "tt̄ +b" breaks across lines in the Main background sentence. Use `&nbsp;` or wrap the entries in `white-space: nowrap`. The left column also has about 60 px empty above the 0ℓ card, so the cards could move up and get bigger.
- S9: "→ backup" wraps onto its own line in the Validation bullet. Shorten the bullet or keep the arrow with the word ("→&nbsp;backup").
- S5: the caption above the figure wraps with an orphan "(red)" on the third line. Shorten it to "Merged-jet mass; bottom: VZ (grey, ≈ 90 GeV) and VH (red) after background subtraction". The two pT arrows land on the box titles and touch the "M" of "Merged". Stop them about 10 px higher.
- S17 left caption: "Run 2 (2018) vs Run 3 (2022–24), 13.6 TeV" reads as if 2018 were at 13.6 TeV. Better: "Run 2 (2018, 13 TeV) vs Run 3 (2022–24, 13.6 TeV)".
- S6 "85% of the uncertainty is statistical": the shares add in quadrature (0.85² ≈ 72% of the variance). The caption already says so, but a statistician may ask. Keep as is or write "stat. ≈ 85% of total (in quadrature)".
- S4 footnote "μ limits and κc intervals at 95% CL, observed (expected)": the Indirect and J/ψγ cards show observed only. This is fine because the footnote is generic.

## Layer 1

| severity | check | finding |
|---|---|---|
| info | energy-values | 13 TeV, 13.6 TeV |
| info | fonts | Type 3 fonts present (from the embedded paper figures) |

No forbidden patterns. All "→ backup" pointers land on matching backup slides in `deck.html` (21 to 34). Every "slide N" pointer is correct except S4 (item 2).

Reactions saved: all six top findings agreed (`~/.claude/skills/cern-slides/personal/feedback/higgs2026-html-2026-10-18/reactions.jsonl`).
