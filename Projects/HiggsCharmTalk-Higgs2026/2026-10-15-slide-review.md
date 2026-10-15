---
tags: [reference, talk, review]
status: active
date: 2026-10-15
source: laptop
---

# Slide review: Higgs 2026 H-charm talk (deck as of 5611113)

Config: `slide-review.json` (public, Higgs 2026 audience, 15+5 min, focus all, backend Claude).
Layers run: cern_checks, PPTEval (Claude), claim verifier, figures, statistics, expert audience, personal.
Slide numbers are PDF pages. Every correctness item below was checked against the paper or the rendered page.

## Your review

- S1: Fine.
- S2: Like the motivation, but too much text for slide 2, κc definition is buried tiny under the plot, make it bigger and put it in the bullets, plot caption 2 lines of tiny, arXiv ref not needed on slide.
- S3: Nice roadmap, I like this. But boxes are half empty and text is scriptsize, make the refs smaller and the "best" line bigger, maybe add which slide each box goes to? Γ_H not defined.
- S4: Firstly, two topics on one slide, boosted has no plot at all, either give it a figure or move it to backup. Plots too small, μ-limits plot axis unreadable. wdym by μ and S/(S+B) weighted, nowhere defined.
- S5: Plot is good size. But wdym by ParT, HF, standard candle, 2D categories need one line of explanation. By-product ttH(bb) bullet not needed here. No final statement.
- S6: Plots need to be bigger, lots of empty space bottom left. κb floating not explained. Bullets below the block are weak, maybe one take-away line instead?
- S7: I like the final statement here. But left plot is tiny, right block too narrow (μ wraps), maybe drop the left plot and make the scan bigger.
- S8: Content fine, but diagrams small and half the slide empty, make figure bigger. wdym by "flat direction". Challenges block maybe in point form shorter.
- S9: Looks fine for now. But no take-away, why the limit is 38 not 3 should be said in one line.
- S10: Too dense, firstly split WW and the combination or move 2-POI and the −87% correlation to backup. SRs/CRs, 1-POI/2-POI jargon for theorists. Plots too small, labels unreadable.
- S11: Too much text, three probes crammed. J/ψγ already on S3 and in another talk, one line enough. Plot legend unreadable, caption wraps in tiny. Make the figure bigger.
- S12: Like this table, good slide. But ttH alone beats the combination obs, will confuse people, maybe a summary plot instead of a table? First bullet repeats S3.
- S13: Two topics with no story between them. HLT plot labels unreadable, captions tiny. wdym by UParT, GloParT. "Run 3 analyses are under way" is not a take-away, needs a better final line.
- S14: Too many bullets, history bullet maybe not needed. Plot does not show the 1.5 number the slide quotes. Final box question is confusing, rephrase.
- S15: Fine, but bullets 4 and 5 both say |κc|~3, merge them. S2 asks the Higgs-mechanism question, answer it here.
- S16-S24: Backups fine, but the main slides never point to them, add "→ backup" on S4, S6, S10, S11, S13. pT-spectrum backup (S21) is never mentioned in the main talk.

Top points: (1) plots too small and too much text on the results slides; (2) jargon not introduced for a mixed audience (μ, ParT, S/(S+B), POI, flat direction, UParT/GloParT, κb, κV); (3) take-away lines missing on S5, S6, S9, S10, S11, S13, and no pointers to backup.

## Correctness and CMS

1. [blocker] Deck-wide, `\Hcc` (tex:19) and `\ttbar` (tex:22): c̄ renders as "e", so titles read "H → ee" (S4 to S7, S12 to S15, S17 to S19, S24). The text layer is correct; this is a glyph problem, visible at 300 dpi and at projection. Evidence: page 4 title crop at 300 dpi, S14 caption, S19 title. Fix: `\mathrm{c}\overline{\mathrm{c}}` (same for t̄), recompile, zoom-check one title.
2. [major] S7 title (tex:185), S12 (tex:327) and S15 (tex:383): "tightest / most stringent constraint to date" is contradicted by the deck's own S11. Off-shell+on-shell H→4ℓ with |κV|≤1 gives κc ∈ [−3.3, 2.8] (arXiv:2607.23352 Table 3), and ttH alone gives 3.0 obs. Fix: "most stringent **direct** constraint; best expected sensitivity (2.7)", as tex:204 already says. Add one line: ttH alone beats the combination on observed because of the VH upward fluctuation.
3. [major] S7 tex:200: "Expected limit improves by ~20% over the best single channel". arXiv:2509.22535 says "5.6, representing a 36% (26%) improvement over the ttH (VH) channel alone". Fix: "26% better than VH alone".
4. [major] S2 tex:64: "vector-like quarks (arXiv:2410.05236)". That paper is an SFV two-Higgs-doublet study and never mentions vector-like quarks (grep: 0 hits). Fix: drop VLQ or cite a VLQ paper.
5. [major] S12 tex:316: "κb = 1, SM-like width" is wrong for the direct rows. Production is SM and Γ_H varies via Γ_cc (2509.22535 eq. 3; 2205.05550). Fix: "κb = 1, SM production, no BSM decays".
6. [major] S12 tex:321: the cH row has an empty assumptions cell. It uses the flat direction (other H rates fixed to SM), and the κc comes from a translated μ limit. The rows are not directly comparable. Fix: fill the cell and add a footnote that the rows use different coupling models.
7. [major] S12: the tightest indirect result (off-shell, |κV|≤1: [−3.3, 2.8] ([−3.5, 2.9])) is missing from the table, and the indirect assumptions are incomplete (κb = κt = 1, other light Yukawas profiled; 2502.05665 imposes κZZ = κWW, 2607.23352 does not). Also on S3 tex:97: start the indirect range at [−3.3, 2.8].
8. [major] S14 tex:360-374: the figure is the old CMS-only HIG-21-008 extrapolation. Its 2σ contour reaches |κc| ≈ 2, next to the bullet's |κc| < 1.5 from the ATLAS+CMS 2504.00672 projection. Also, 1.5 is an expected sensitivity. Verified on the 300 dpi crop. Fix: use the HIG-25-002 figure, or caption this one as "previous CMS-only projection (YR18 systematics, 1σ/2σ)".
9. [major] S15 tex:385: J/ψγ is grouped with indirect probes that "reach |κc| ~ 3", but it gives [−166, 208]. Fix: name only on/off-shell 4ℓ with |κV| ≤ 1 (about 8 without).
10. [major] S5 tex:152-153: the caption says "ParticleNet (b vs. light, c vs. light) plane", but the axes are p_B+C and p_BvsC. Verified on the crop. Fix: "(b+c vs. light, b vs. c) plane".
11. [major] S13 tex:338-344: both figures are unreadable (about 3 pt text). The BTV figure includes a ttH(bb) panel the caption does not mention. Fix: crop to the ttH(cc) panel and enlarge.
12. [minor] S21 tex:467: the pT-spectrum (κb, κc) fit is listed as "(γγ, ZZ, WW, ττ)". arXiv:2504.13081 says the H→WW analysis "is excluded from this interpretation", and so is boosted ττ. Fix: "γγ, ZZ, resolved ττ". "Shape sensitive to the sign of κc" is not stated in the paper (unverified).
13. [minor] S4 tex:118: the observed 1.1 < |κc| excludes the SM at 95% CL, and nothing on the slide explains why. Fix: "(VH upward fluctuation, μ = 7.7; see backup)".
14. [minor] S4, S6, S7, S10: blocks do not say "95% CL, obs. (exp.)", and the method is never stated (μ: CLs; κc: profile-likelihood scans; cH: translated μ limit). S7 also needs "(SM production)". S10 needs "1-POI" on the combination block.
15. [minor] S11 tex:289: "γH + on-shell H→4ℓ". The γH categories do not drive the κc limit; the inclusive 4ℓ rate does (2502.05665 Sec. 8). S11 tex:292: "breaks the width degeneracy" should be "κV–Γ_H degeneracy". The caption should say solid = observed, dashed = expected.
16. [minor] S14 tex:364: "~37 (2016)" needs the citation HIG-18-031, JHEP 03 (2020) 131.
17. [minor] Provenance: the S4 pubref links only to HIG-21-008 though it cites HIG-21-012 too. The S8 pubref links to HIG-24-009, but its figure is HIG-23-010.
18. [minor] Backup captions: S18 needs "orange obs, blue exp". S19's HIG-21-012 panel shows both passing and failing regions (the peak is Z(cc)). S22 has no caption. S19's ttH(cc) panel shows μ_fit = −1.6: this is the published value, but have an answer ready.

Unverified: "first search for H→cc in ttH" (S5; the paper says "a new approach"); the S13 claims "Run 3 dataset already larger" and UParT/GloParT have no public reference on the slide; HL-LHC systematics scenario (S2 vs S3); speaker names and talk order (README only).

## Three unanswered questions (PPTEval coherence and the expert reviewer agree)

1. VH observes 1.1 < |κc|, excluding the SM, and μ obs (14) is about twice exp (7.6). How big is the excess, and why is the combination (3.5) weaker than ttH alone (3.0)? Not answered (only the backup S17 shows μ = 7.7).
2. How does this compare with ATLAS (VBF+VH, arXiv:2511.21911: |κc| < 4.7 (3.9)), and is an ATLAS+CMS κc combination planned? Not answered.
3. What exactly is fixed in each κc number, and why do production (cH) and decay (VH/ttH) differ by an order of magnitude? Partly answered (S8, S12), with the assumption errors above. PPTEval also raises the dominant systematics (c-tag calibration, tt+cc and V+HF modelling), which the deck names on S14 but never quantifies.

## Timing

14 content slides in 15 min is about 64 s each; S3, S7, S11 and S12 need 1.5 to 2 min. As written, the talk runs about 18 min. Suggested merges: S9+S10 into one cH slide (saves about 1.5 min; Bevilacqua follows), S5+S6 into one ttH slide with the tagging plane moved to backup (about 1 min), and optionally S13 folded into S14 as "Outlook".

## Layer 1 (cern_checks)

| severity | finding |
|---|---|
| (false positive) | forbidden `scouting` (tex:348) is the generic stream name; `14.3` on p4 is the public HIG-21-008 Fig. 4 2L expected limit. Confidentiality clean: no HIG-25-001/017, HIG-26-003, Athens or Novak material |
| major | 2 overfull hbox (tex:105, 330; max 12 pt) |
| major | 24 pages for 15 min (incl. 8 backup + divider) |
| minor | dense pages 13, 19, 20, 21 (138 to 170 words); `\tiny` used 27× |
| info | lumi 138, 3000 fb⁻¹; energies 13, 13.6, 14 TeV, all consistent with the figures; Type 3 fonts present |

All 7 `\pubref` URLs return HTTP 200. All arXiv/journal/CMS-ID mappings on the references slide were verified on INSPIRE.

## PPTEval (Claude)

Mean content 3.08, mean readability 2.67, coherence 4/5. Lowest scores: S7 (2/2, the "tightest" claim), S19 and S21 (2/2). Readability 2 on S4, S5, S6, S7, S10, S13, S17, S19 to S23 is driven by small plots and the c̄ glyph. The S21 "blocker" (γH not shown) is downgraded to minor: HIG-23-011 is the γH paper, but its caption should say so.

Full per-page output: `higgs2026_higgs_charm.ppteval.json` (next to the deck).

## Content vs. abstract (Indico 1668640)

Abstract: discovery + 3rd-gen couplings; 2nd-gen is harder; "With the Run3 data collected by the CMS experiment, a lot of progress has been made to constrain this coupling"; latest direct and indirect results; prospects.

- **Gap:** the abstract promises Run 3 progress, but every κc number is Run 2 (no Run 3 Hcc result is public; the Athens numbers stay out). Fix: say it on S3 ("all κc results are Run 2; Run 3 has delivered the tools and background measurements"), and give S13 that story (HLT ttH(cc) trigger gain + first tt+cc̄ cross section, the main ttH(cc) background), with a take-away line in place of "Run 3 analyses are under way". Add one Run 3 bullet to S15.
- **Place in the day (28 Oct):** this talk is first (09:20), before Tarek (off-shell, 14:00), Cabrera Urban (H+c, 16:30), D'Eramo (H→cc, 17:00) and Davighi (Higgs and flavour, 18:00). S12 is the reference table for the day, so it is the slide most worth getting right.
- **Title vs. content:** S2's question is never answered (answer it on S15: reach ~3×SM now, ~1.5× at HL-LHC). S4 has two topics and no boosted figure. S7 overclaims (see finding 2). S11 has no message about what off-shell adds, and its γH label is misleading. S13 has two figures with no link to κc. S14's figure does not show its number. Backup S19 "more figures" is not a message, and S21 promises γH without labelling it.
- The abstract says the discovery was "ten years ago" (it was 14); the slide already says 2012, fine.

## Fix list agreed with Chirayu (for whoever applies it)

He agreed to all items under "Correctness and CMS" and to the content section above. Presentation exception: this is a review talk of others' work, so dense slides are acceptable, and only the terms the story needs get defined (μ on S3, κc on S2 as a bullet, "flat direction" on S8), not every term.

1. Macros (tex:19, 22): `\mathrm{c}\overline{\mathrm{c}}`, `\mathrm{t}\overline{\mathrm{t}}` (also `\ttH`, `\ttZ`, `\Hbb` and the inline `c$\bar{\mathrm{c}}$` at tex:114, 146, 218, 342, 344, 500); zoom-check one title.
2. "Most stringent **direct**; best expected sensitivity" on S7 title (185), S12 (327), S15 (383); one line on why ttH alone beats the combination on observed (VH upward fluctuation, μ = 7.7).
3. S7 tex:200: ~20% → "26% better than VH alone (36% than ttH)".
4. S2 tex:64: drop "vector-like quarks".
5. S12 table: direct rows "κb = 1, SM production, no BSM decays"; cH "flat direction, from μ limit"; add the off-shell |κV|≤1 row [−3.3, 2.8] ([−3.5, 2.9]); fuller indirect assumptions; footnote that the rows are not directly comparable. S3 tex:97 range starts at [−3.3, 2.8].
6. S15 tex:385: J/ψγ out of "|κc| ~ 3"; merge bullets 4 and 5; answer S2's question; add a Run 3 bullet.
7. S5 tex:153 caption: "(b+c vs. light, b vs. c) plane". S21 tex:467: "γγ, ZZ, resolved ττ"; label γH.
8. S14: swap in the HIG-25-002 figure, or caption the current one as the old CMS-only projection; "expected |κc| < 1.5"; cite HIG-18-031 for "~37"; rephrase the closing box.
9. Take-away lines on S5, S6, S9, S10, S11, S13; "→ backup" pointers on S4, S6, S10, S11, S13 (S21 from S11/S12).
10. Merges: S9+S10 into one cH slide, S5+S6 into one ttH slide (tagging plane to backup).
11. Minor items 13 to 18 above (95% CL labels, S4 excess note, S11 wording/caption, pubref links, backup captions); S13 crop the BTV figure to the ttH(cc) panel.
