---
tags: [reference, talk, review]
status: active
date: 2026-10-16
source: laptop
---

# Slide review 2: Higgs 2026 "Constraints on Higgs-charm couplings at CMS"

Deck reviewed: `higgs2026_higgs_charm.tex` at commit 179a490 (27 pages: 15 main, 12 backup). Config: `slide-review.json` (public mode, 15+5 min, now with the abstract, the day's programme, and two speaker notes: text density is fine, and add a Feynman diagram on the title slide). Previous review: [[2026-10-15-slide-review]].

**Status: COMPLETE** (all five layers; claims and statistics finished on 16 Oct after a rate-limit pause). Every number on the slides matches its paper (arXiv full text, INSPIRE, CMS public pages), all κc intervals are at 95% CL, all links resolve, and HIG-25-001/-017 and HIG-26-003 are still not public (re-checked 16 Oct 09:19 UTC). No blocker.

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
2. [major] Slide 13, "Toward Run 3": the "measured tt̄+cc̄ background" (TOP-26-003) comes from Run 2 data. The figure label reads 138 fb⁻¹ (13 TeV), yet the slide frames it as Run 3 progress and tags it NEW. The same framing recurs in the S15 bullet. Raised by all five layers, and confirmed by the claims check (PAS TOP-26-003 abstract: 13 TeV, 138 fb⁻¹). The same framing is on slide 3 ("Run 3 delivered the tools"). Only the HLT taggers are a Run 3 deliverable. Evidence: p-13; tex:113, tex:346, tex:352, tex:386. Fix: caption "Run 2 data (138 fb⁻¹), the main background for Run 3 tt̄H(cc̄)"; take-away "Run 3 searches start with higher trigger efficiency and a tt̄+cc̄ background already measured in Run 2"; same wording on slides 3 and 15. While editing, put stat before syst: 680 ± 40 (stat) +130/−100 (syst) fb.
3. [major] Slide 3, "How CMS probes κc" (and Summary, slide 15): the "best" labels are wrong on observed. The H+c box says "best: |κc| < 47 (51)", but γγ alone gives |κc| < 38 (73) on slide 9: WW fluctuated up (μ̂_cH = 390 vs −230 in γγ), the same pattern as ttH alone (3.0) vs the ttH+VH combination (3.5). Evidence: tex:95, tex:100; 2503.08797 (38.1 (72.5)), 2508.14988 Sec. 7. Fix: "comb.: |κc| < 47 (51 exp.)" and "ttH+VH comb.: |κc| < 3.5 (2.7 exp.)"; optionally one line on slide 10: "combined obs. weaker than γγ alone (38) because WW fluctuated up".
4. [declined by Chirayu: CMS talk, ATLAS stays in backup] Slide 12, "Where we stand": there is no ATLAS line on the day's reference table. Both afternoon plenaries (Cabrera Urban, D'Eramo) will compare ATLAS and CMS, and the ATLAS number appears only on backup p26. Evidence: tex:312-326, tex:546. Fix: a footnote, "ATLAS VBF+VH(cc̄): |κc| < 4.7 (3.9), arXiv:2511.21911", after checking that the κ assumptions match (unverified, see below).
5. [major] Slide 21 (backup), "cH(H→WW) post-fit": the last caption line, "heavy-flavour modelling.", overprints the footer. Evidence: p-21 and the 150 dpi crop; tex:472. Fix: shorten the sentence, or drop the figure height below 5.8 cm.
6. [declined by Chirayu: keep the slide] Slide 5, "Direct H→cc̄: boosted H": the slide feeds no κc number. Its result is not in the S3 "best" list, the S12 table or the summary, and its take-away concerns ggH dominance. It is the cheapest minute to cut from a talk the audience reviewer estimates at 16 to 17 min. Fix: fold the Z→cc̄-in-Z+jets point into S4 and move S5 to backup, or add the boosted μ limit to the S12 table. Either way, fix the "first time" clash with S4 (see your S5 line).
7. [minor] Slide 13: "parking and scouting → backup" points at p25, which covers only HLT tagging. Drop the pointer, or drop "scouting" (the word also trips the forbidden-pattern list, though only as a false positive).
8. [minor] Slide 11, "Indirect": the blue "On-shell" curve is the on-shell-only fit from HIG-25-003, while the bullet labels on-shell as "(γH paper) [−3.7, 3.2]". Fix: a caption with the colour key, "blue on-shell, red on+off-shell (|κV| ≤ 1), black κZ, κW free; arXiv:2607.23352". The asymmetric 4ℓ intervals (S11, S12) also come with no word on where the sign sensitivity comes from. A theorist will ask (tex:289-293).
9. [minor] Slide 7: neither figure has a caption, and the |κc| scan legend is unreadable. Fix: one line each: "μ limits: ttH, VH, comb." and "|κc| scans, κb = 1".
10. [minor] Slide 9: the figure prints μ_cH = −230 +170/−251, but the slide never mentions it. Prepare a Q&A line.
11. [minor] Slide 13: the trigger gain in the BTV figure compares 10 Hz (2018) with 60 to 170 Hz (Run 3). Have an answer ready for how much of the gain comes from the tagger and how much from the rate budget.
12. [minor] Jargon a non-CMS audience may not know: ParticleNet (S4: add "graph-NN jet tagger"), DeepDoubleX (S5), "γH paper" (S3, S11), "1 POI" (S10), "light κq prof." (S12). Also, the "F. Errico's talk" and "J. Daniel's talk" pointers give no day.
13. [minor] Slide 2: the κc point in the HIG-21-018 figure is the separate ttH+VH constraint ("not part of combined fit"), and the caption does not say so.
14. [minor] Backup p23 and p25: the plots are unreadable even at 150 dpi. Show one enlarged panel each. On p25, say "light (solid) and b (dashed) misID vs. c-jet efficiency". Backups p17, p18 and p22 have no take-away line, and p24 gives no CL for the J/ψγ κc interval.
15. [minor] Slide 7 title "most stringent direct constraint": HIG-24-018 itself says "most stringent constraint to date", so the wording follows the paper, and the claims and statistics reviewers both accept it. On observed limits, though, ttH alone (3.0) beats the combination (3.5), and the take-away "below the BSM-motivated |κc| ∼ 3" holds only for the expected limit. Clearer: title "...best expected direct sensitivity", take-away "|κc| < 2.7 (obs. 3.5)". (Was major in the first draft of this report; downgraded after the claims check.)
16. [minor] Slide 26 (likely questions): "VH excess about 2σ above SM" is our own estimate, (7.7−1)/3.5 ≈ 1.9. The paper calls it "a small upward statistical fluctuation". Fix: "about 1.9σ above μ = 1 (estimated from the quoted uncertainty)".
17. [minor] Slide 5: μ_Z is quoted with the syst part only, which reads as the full uncertainty. The full result is 1.00 +0.17 −0.14 (syst) ± 0.08 (theo) ± 0.06 (stat), total +0.19 −0.17. The boosted block also lacks the "95% CL obs. (exp.)" label the other blocks carry. Evidence: tex:152, tex:155.
18. [minor] Slide 12, J/ψγ row: the header promises "obs. (exp.)" but gives only the observed value. Expected is (−128, 169). J/ψγ uses 123 fb⁻¹, so slide 3's "All κc results: Run 2 data (13 TeV, 138 fb⁻¹)" should say "up to 138 fb⁻¹".
19. [minor] Slides 11 and 12, |κV| ≤ 1 labels: slide 11 says |κV| ≤ 1 (tex:292) but slide 12 says |κZ = κW| ≤ 1 (tex:319) for the same on+off-shell row. Use HIG-25-003 Table 3's "|κV| ≤ 1" in both, and keep |κZ = κW| ≤ 1 for the on-shell PRD 112 row. The indirect rows also allow Γ_BSM ≥ 0, which the direct rows do not; worth stating, since the indirect rows are the more general ones.
20. [minor] Slide 14: the assumptions behind |κc| < 1.5 are partly missing: 14 TeV, VH(cc̄) only, S2 systematics with improved c tagging (2504.00672). The "30% better" is relative to the YR2019 projection, not the HIG-21-008 figure on the slide. The history bullet "~37 (2016) → 5.6" compares VH alone with VH+ttH; like-for-like it is 37 → 7.6, or label it "VH → VH+ttH".
21. [minor] Notation: results use \obsexp on slides 4, 6, 7, 9, 10 and 12, but "(2.7 exp.)" on slides 3 and 15. Slide 4 writes "(<3.4)" without κc. Slide 3's footnote calls κc intervals "limits"; better: "μ limits and κc intervals at 95% CL: obs. (exp.)". Slide 10's combination block should say "(1 POI)".
22. [minor] Slide 13: the BTV trigger-efficiency figure is simulation; add "simulation" to the caption.
23. [minor] Slide 27 (references): the bookkeeping notes "(backup)", "(motivation figure)" and "(motivation)" are visible in four entries (verified in the PDF text). Drop them.
24. [minor, optional] Slide 2: "couplings to t, b, τ, μ measured": μ is evidence at about 3σ, so "evidence for μ" is safer.
25. [minor] Slides 4, 6 and 7: the band colours swap meaning between papers (VH: green 68%, yellow 95%; ttH: yellow 68%, blue 95%). This comes from the sources, so just say "inner band 68%" once.

## Unverified

- Backup p23: the pT-spectrum fit channels (γγ, ZZ, resolved ττ) were not re-checked in this pass; they were verified against 2504.13081 on 15 Oct.

Cleared since the first draft: all numbers (claims table in the claims verifier's scratch, `tmp/cv/`), confidentiality, links and journal references, the CL of every interval, and the S8 flat-direction wording (correct: both papers rescale all other couplings by a common κH(κc) so the other Higgs rates stay SM). The 4ℓ asymmetry is NOT a sign measurement; the deck does not claim one, so do not add one. If asked: "the small asymmetry comes from charm-loop interference in ggH and H→gg; the constraint is essentially on κc²".

## Q&A prep from the checks

- **ATLAS arXiv:2511.21911** uses the same assumptions as CMS (other couplings SM, SM decays only, SM VBF/ggF/VH production), so 4.7 (3.9) vs CMS 3.5 (2.7) is like-for-like. But its VBF part includes Run 3 data (51.5 fb⁻¹ at 13.6 TeV), so ATLAS has a partly-Run-3 κc result and CMS does not. ATLAS also fluctuated up (μ = 3.3 +5.2 −5.0); ATLAS VH alone gives |κc| < 4.2 (4.1).
- **The theorist recasts** in 2410.05236 Table 3 (the SFV paper on slide 2) list "CMS |κc| < 2.92" and an ATLAS ±2.27 from the pT shape. These are not CMS results, but someone may quote them.
- **The slide 13 trigger gain** compares 10 Hz (2018) with 60/115/170 Hz (2022/23/24), so part of the gain is rate budget.
- **The slide 9 observed limit** (38) is much better than expected (73) because μ̂ = −230.

## Three unanswered questions

1. ATLAS (a hardest question): "Your 3.5 (2.7) vs our 4.7 (3.9): same assumptions? Combination plans?" Only the number is in backup. Nothing on fairness or plans.
2. Theorist: "How model-dependent are κc values from 2.8 to 208? At κc ≈ 47 in the cH flat direction, what keeps Γ_H SM? Where does the 4ℓ sign sensitivity come from?" Partly answered by the S12 assumptions column. The flat-direction and sign questions are not.
3. Chair: "Answering 'does the Higgs give charm its mass' needs κc = 0 excluded. When?" Not answered, and slightly overclaimed (finding 1).

PPTEval's deck-level questions add three more: how compatible are VH (μ̂ = 7.7) and ttH (μ̂ = −1.6), and what is the combination's p-value? Why is boosted H→cc̄ not converted to κc or combined (overlap with the VH merged-jet category)? What κc reach is expected from Run 3 before the HL-LHC (there is no intermediate point between 2.7 and 1.5)?

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

## PPTEval (Claude, all 27 pages)

Mean content 3.04, mean readability 2.67. **Coherence 4/5**: clear order (motivation, roadmap, direct, H+c, indirect, table, Run 3, HL-LHC, summary), terms defined before use, and backups that answer the main slides. It falls short of 5 because of the S13 scouting pointer, the unexplained "γH paper", and the boosted slide disappearing without a κc value. Lowest pages: p7 (2/2), p14 (2/3), p23 (2/1, unreadable panels), p25 (3/2, unreadable panels). Readability 2 on p2, p5, p6, p9, p11, p17, p19 and p21, mostly small figures. The p6 candidate "VH comparison not shown" is minor, since S4 sits right before it.

## Chirayu's reactions (16 Oct)

He agreed with every main-deck line under "Your review", with finding 1, and with the S7 retitle (now finding 15). He cares little about backup polish. He disagreed with finding 4 (no ATLAS line on the CMS table) and finding 6 (keep the boosted slide in the main deck). Findings 3 and 16 to 24 were added after his reactions and are not yet reacted to. He wants a Feynman diagram on the title slide, and text density is fine by him. Saved for the personal reviewer in `~/slide-review/skills/cern-slides/personal/feedback/higgs2026-hcharm-2026-10-16/reactions.jsonl`.

## Applied (16 Oct)

All main-deck lines and findings 1 to 3, 5 and 7 to 25 applied, including the optional ones; findings 4 (ATLAS line on S12) and 6 (boosted slide to backup) skipped as Chirayu declined them. Choices worth knowing:

- S1: two TikZ diagrams (gc → cH left, H → cc̄ right, κc at orange vertices).
- S4: the per-channel μ-limit plot could not be made readable in a column (row labels stay about 3 pt even cropped to three rows), so it moved to backup p17 with a pointer; the merged-jet mass plot is larger and the block quotes the merged-jet limit.
- S14: the old HIG-21-008 projection plot is replaced by a TikZ bar chart of allowed |κc| (Run 2 obs. 3.5, exp. 2.7, HL-LHC exp. 1.5, SM line, BSM band). The history bullet is dropped (and HIG-18-031 from the references). The 1.5 assumptions are as stated in 2504.00672: 14 TeV, VH(cc̄) with improved c tagging from an ATLAS study, 30% better than the 2019 Yellow Report; the paper does not name S2 for charm, so the slide does not either.
- S11 caption uses the review's |κV| ≤ 1 for the red curve, though the HIG-25-003 figure legend itself writes |κZ = κW| ≤ 1.
- Talk days added: F. Errico Tue 27, J. Daniel Mon 26, J. Bierkens Thu 29 (Indico 1668640).
- Build: 27 pages, no errors; residual overfull 2.3 pt (S3 boxes) and 2.2 pt (likely-questions slide), not visible.
