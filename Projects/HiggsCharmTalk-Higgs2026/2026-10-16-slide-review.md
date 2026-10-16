---
tags: [reference, talk, review]
status: active
date: 2026-10-16
source: laptop
---

# Slide review 2: Higgs 2026 "Constraints on Higgs-charm couplings at CMS"

Deck reviewed: `higgs2026_higgs_charm.tex` at commit 179a490 (27 pages: 15 main, 12 backup). Config: `slide-review.json` (public mode, 15+5 min, now with the abstract, the day's programme, and two speaker notes: text density is fine, and add a Feynman diagram on the title slide). Previous review: [[2026-10-15-slide-review]].

**Status: PARTIAL.** Both the claims verifier and the statistics reviewer hit the Claude session limit before they finished, so the numbers on the slides have not been re-verified against INSPIRE in this pass. They resume after 16:00 on 16 Oct. PPTEval scores are missing for pages 25 to 27, and there is no deck coherence score yet, for the same reason. Every finding below comes from the personal, figures and audience reviewers, plus my own check of slide 7.

## Your review

- S1: Looks clean. But add a Higgs-charm Feynman diagram for aesthetics (an H→cc̄ vertex, or cc̄→H / gc→Hc, maybe reuse the S8 style), the slide is empty above the logos.
- S3: Like the roadmap now, slide numbers are in. Maybe say what "γH paper" means, or drop the label, it shows up on S3, S11 and backup p23 and is never explained.
- S4: Right μ-limits plot is unreadable (per-channel labels about 3 pt), make it bigger or crop it to the combined/merged/resolved rows.
- S5: Fine. But S4 already says "Z→cc̄ observed at 5.7σ", so "first time" here reads as a contradiction. Say "first in Z+jets". Also, no κc number in the block, people will ask why.
- S6: Good. But "κb fitted" has no pointer, and the (κb, κc) backup p20 exists, so add →backup there.
- S12: Like the table, but this is the reference slide of the day and it sits at scriptsize in the top half with the bottom empty. Make the table bigger. The footnote is tiny. The second bullet should be the blue take-away line.
- S13: Story is better now. But the right plot is 138 fb⁻¹ at 13 TeV (Run 2 data) on a "Toward Run 3" slide, so the framing needs care. Its labels are unreadable. "→ backup" wraps onto its own line, and backup p25 has nothing on parking or scouting.
- S14: The figure still doesn't show the 1.5 that the slide quotes. The "Previous" caption helps, but maybe drop the plot or show the HL-LHC number some other way. The history bullet is maybe not needed. No blue take-away line (the box does the job, fine).
- S15: Nice, it answers the S2 question now.
- Backup: p21 caption runs into the footer. p23 plots are tiny, and the pT spectrum is still never named from the main talk. p18 and p21 have no pointer. p25 repeats the S13 panel.

Top points:
1. S12 is the slide everyone photographs. Bigger table, and a take-away line.
2. Backup wiring. The S13 pointer has the wrong target (parking/scouting is not in p25). p18, p20, p21 and the pT-spectrum part of p23 are never pointed to. The p21 caption overflows.
3. S1 Feynman diagram, and the two unreadable figures that remain (S4 right, S13 right).

Also noticed: κb (S6), κV/κZ/κW (S11) and POI (S10) are used without definition. That is acceptable under the "only what the story needs" rule, except κV, which the S11 story leans on.

## Correctness and CMS

1. [major] Slides 14 and 15, "Prospects at the HL-LHC" and "Summary": the S2 question ("does the Higgs give 2nd-generation quarks their mass?") is answered with an upper bound, and an upper bound cannot answer it. |κc| < 1.5 says nothing about κc = 0, and slide 14 itself gives VH(cc̄) at the HL-LHC as about 1.6σ expected. Raised independently by the audience reviewer and PPTEval. Evidence: tex:363, tex:370, tex:387; p-14 and p-15. Fix: on S15, "HL-LHC expected |κc| < 1.5: approaching, not yet reaching, sensitivity to κc = 0". In the S14 box, "κc at O(1): first sensitivity to whether the Higgs gives charm its mass".
2. [major] Slide 13, "Toward Run 3": the "measured tt̄+cc̄ background" (TOP-26-003) comes from Run 2 data. The figure label reads 138 fb⁻¹ (13 TeV), yet the slide frames it as Run 3 progress and tags it NEW. The same framing recurs in the S15 bullet. Raised by all three reviewers. Evidence: p-13; tex:346, tex:352. Fix: caption "Run 2 data (138 fb⁻¹), the main background for Run 3 tt̄H(cc̄)", and add "(Run 2 data)" to the take-away and the summary. While editing, put stat before syst: 680 ± 40 (stat) +130/−100 (syst) fb.
3. [major] Slide 7, "Combination of ttH and VH: most stringent direct constraint on κc": on observed limits the title is false, because ttH alone gives 3.0 and the combination gives 3.5. The slide's own bullet explains this, but the title and the take-away line ("below the BSM-motivated |κc| ∼ 3") hold only for the expected limit. Verified on the rendered page. Fix: title "...best expected direct sensitivity to κc". Take-away: "Best expected sensitivity to date, |κc| < 2.7 (obs. 3.5), probing the BSM-motivated |κc| ∼ 3".
4. [major] Slide 12, "Where we stand": there is no ATLAS line on the day's reference table. Both afternoon plenaries (Cabrera Urban, D'Eramo) will compare ATLAS and CMS, and the ATLAS number appears only on backup p26. Evidence: tex:312-326, tex:546. Fix: a footnote, "ATLAS VBF+VH(cc̄): |κc| < 4.7 (3.9), arXiv:2511.21911", after checking that the κ assumptions match (unverified, see below).
5. [major] Slide 21 (backup), "cH(H→WW) post-fit": the last caption line, "heavy-flavour modelling.", overprints the footer. Evidence: p-21 and the 150 dpi crop; tex:472. Fix: shorten the sentence, or drop the figure height below 5.8 cm.
6. [major] Slide 5, "Direct H→cc̄: boosted H": the slide feeds no κc number. Its result is not in the S3 "best" list, the S12 table or the summary, and its take-away concerns ggH dominance. It is the cheapest minute to cut from a talk the audience reviewer estimates at 16 to 17 min. Fix: fold the Z→cc̄-in-Z+jets point into S4 and move S5 to backup, or add the boosted μ limit to the S12 table. Either way, fix the "first time" clash with S4 (see your S5 line).
7. [minor] Slide 13: "parking and scouting → backup" points at p25, which covers only HLT tagging. Drop the pointer, or drop "scouting" (the word also trips the forbidden-pattern list, though only as a false positive).
8. [minor] Slide 11, "Indirect": the blue "On-shell" curve is the on-shell-only fit from HIG-25-003, while the bullet labels on-shell as "(γH paper) [−3.7, 3.2]". Fix: a caption with the colour key, "blue on-shell, red on+off-shell (|κV| ≤ 1), black κZ, κW free; arXiv:2607.23352". The asymmetric 4ℓ intervals (S11, S12) also come with no word on where the sign sensitivity comes from. A theorist will ask (tex:289-293).
9. [minor] Slide 7: neither figure has a caption, and the |κc| scan legend is unreadable. Fix: one line each: "μ limits: ttH, VH, comb." and "|κc| scans, κb = 1".
10. [minor] Slide 9: the figure prints μ_cH = −230 +170/−251, but the slide never mentions it. Prepare a Q&A line.
11. [minor] Slide 13: the trigger gain in the BTV figure compares 10 Hz (2018) with 60 to 170 Hz (Run 3). Have an answer ready for how much of the gain comes from the tagger and how much from the rate budget.
12. [minor] Jargon a non-CMS audience may not know: ParticleNet (S4: add "graph-NN jet tagger"), DeepDoubleX (S5), "γH paper" (S3, S11), "1 POI" (S10), "light κq prof." (S12). Also, the "F. Errico's talk" and "J. Daniel's talk" pointers give no day.
13. [minor] Slide 2: the κc point in the HIG-21-018 figure is the separate ttH+VH constraint ("not part of combined fit"), and the caption does not say so.
14. [minor] Backup p23 and p25: the plots are unreadable even at 150 dpi. Show one enlarged panel each. On p25, say "light (solid) and b (dashed) misID vs. c-jet efficiency". Backups p17, p18 and p22 have no take-away line, and p24 gives no CL for the J/ψγ κc interval.
15. [minor] Slides 4, 6 and 7: the band colours swap meaning between papers (VH: green 68%, yellow 95%; ttH: yellow 68%, blue 95%). This comes from the sources, so just say "inner band 68%" once.

## Unverified

- The numbers themselves: the claims verifier did not finish, so nothing on the slides was re-checked against INSPIRE in this pass. The README number checks from 15 Oct still stand.
- Whether the ATLAS arXiv:2511.21911 κc interval uses the same assumptions as CMS (κb = 1, SM production).
- The CL and assumptions of every κc interval in the S12 table: the statistics reviewer did not finish.
- Whether the HIG-23-010/HIG-24-009 "flat direction" rescales the other couplings to keep the Higgs rates SM (S8 wording).
- HIG-25-001, -017 and HIG-26-003 still being non-public today: not re-checked in this pass.

## Three unanswered questions

1. ATLAS (a hardest question): "Your 3.5 (2.7) vs our 4.7 (3.9): same assumptions? Combination plans?" Only the number is in backup. Nothing on fairness or plans.
2. Theorist: "How model-dependent are κc values from 2.8 to 208? At κc ≈ 47 in the cH flat direction, what keeps Γ_H SM? Where does the 4ℓ sign sensitivity come from?" Partly answered by the S12 assumptions column. The flat-direction and sign questions are not.
3. Chair: "Answering 'does the Higgs give charm its mass' needs κc = 0 excluded. When?" Not answered, and slightly overclaimed (finding 1).

## Fixed since the previous review

Fixed: the c̄ glyph, the HL-LHC "Previous" caption, take-aways on every main slide, the S2 question answered on S15 (in form), the Run 3 gap stated on S3 and S15, table assumptions and the not-comparable footnote, the S4 split with a boosted figure, the ttH merge, J/ψγ reduced to one line plus a handoff to Bierkens, the Bevilacqua handoff, and the backup captions. Still open: S4 right plot readability, S14 figure vs. 1.5, the pT spectrum never named, and the overall timing (partly improved).

## Layer 1 (cern_checks, public mode)

| | |
|---|---|
| blockers | 3, all false positives: "14.3" on p4 is the public 2L expected limit inside the HIG-21-008 figure; "scouting" (tex:350, p13) is a generic word with no number. Tighten the `\b14\.3\b` pattern. |
| dead-reference | 15 rows, a checker bug: the `\pubHIG` macro is not expanded |
| figure provenance | the title-slide logos (tex:45), fine |
| overflow | 1 overfull hbox, 6.5 pt (tex:114, slide 4) |
| timing | 27 pages / 15 min (12 are backup) |
| density | 9 slides over 110 words: ignored per the speaker, and the config limit is now 200 |
| `\tiny` | 10 uses (provenance and captions) |

## PPTEval (Claude, pages 1 to 24)

Mean content is about 3.2 and mean readability about 2.7 (pages 1 to 9: 3.22 / 2.67; pages 10 to 24: 3.13 / 2.73). Pages 25 to 27 and the coherence score are missing because of the rate limit. Lowest scores: p7 (2/2, title overclaim, finding 3), p14 (2/3, overclaim, finding 1), p23 (2/1, unreadable panels), and p2, p5, p6, p9, p11, p17, p19, p21 (readability 2, mostly small figures). The p6 candidate "VH comparison not shown" is minor, since S4 sits right before it.
