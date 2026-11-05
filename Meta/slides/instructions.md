---
tags: [meta, slides]
status: active
review: pending-chirayu
date: 2026-11-05
source: laptop
---

# Slide instructions: consolidated

Rules for making and reviewing Chirayu's slides, collected from the vault sources listed in [[Meta/slides/source-handoff]].
Scope was narrowed on 2026-11-05 to the vault files below. No `~/.claude` memories, personal-feedback JSONL files, chat logs or web sources were read.

**How to read this file**
- **Chirayu (verbatim)** marks his own words, quoted exactly, with date and source. They outrank everything else.
- **Recorded** marks a decision of his that an agent wrote down in its own words. It is not a quote.
- **Agent recommendation** or **agent design** marks advice from agents that he has not confirmed.
- **Newer and more specific wins.** A dated, talk-specific decision beats an older or general rule, but only for that kind of talk. One talk's config never becomes a universal rule (§5).
- The keeper owns this file and [[Meta/roles/update-slide-style]]. Workers who get new slide feedback write it into a normal note, and the keeper adds it to the log in §7.

**Which sections apply**

| Deck | Read |
|---|---|
| Personal work-update deck (`<subproject>/deck/`, keeper) | §1, §2; §4 only before anything is shared outside |
| Group / analysis talk to CMS experts (internal) | §1, §3, §6 |
| CMS public or conference talk | §1, §4, §5 (write a per-talk config), §6 |
| Any review of slides | §6, plus the section for the deck type |

Status: agent-consolidated from vault sources on 2026-11-05; the rules are only as strong as the label on each one. Chirayu has not yet reviewed this file (open points in §8).

---

## 1. Rules for every deck (internal or public)

Each rule cites the comments it comes from. The full quotes are in §7.

1. **Define every symbol, acronym and piece of jargon on or before the slide that uses it.** If a definition is needed, move the defining slide earlier rather than adding a forward reference.
   - Flashjet S4/S5 ("what is dij , diB etc", "dij diB defination can come here"), 2026-09-12 [F1].
   - Higgs talk: "wdym by μ and S/(S+B) weighted, nowhere defined", ParT, Γ_H, "flat direction", "γH paper" [H1, H2].
   - Exception for public review talks: define only the terms the story needs (§4.3).
2. **Order slides so prerequisites come first.** Datasets and inputs go before the results that use them. Definitions go before mechanisms.
   - "the datasets used should come before this slide" [F1].
   - "Add a slide on input C, all the cms datasets used" [F2].
3. **Make formulas readable.** Give the key formula a large displayed equation; never bury it in a footnote or caption.
   - "Formula not visible clearly" (S4), "Make the stop when formula bigger" (S11) [F1].
   - "κc definition is buried tiny under the plot, make it bigger and put it in the bullets" [H1].
4. **Make plots big and fill the space.** Most of the comments are about this. Readability fixes are a bigger plot, a crop to the relevant panel, or moving the extra panels to backup.
   - "plot needs to be a bit bigger", "Bigger plots needed" [F1].
   - "only middle plot relavant rest move to backup" [F2].
   - "Plots too small", "axis unreadable", "half the slide empty, make figure bigger" [H1, H2, H3].
5. **Explain mechanisms in steps or bullets, not prose captions.**
   - "mechanism not explained clearly in steps or bullets", "maybe a better caption in point form?" [F1].
6. **Explanations go in notes, not on the slide.** If a slide needs paragraphs of explanation, the explanation goes in speaker notes or a companion note.
   - "Dont put in slides put add a comment here explaining the results of the slide?" (S10) [F1].
   - The format to copy is one entry per slide: what it shows, how it was made, the line to say. See [[Projects/Flashjet/talks/_history/substructure/speaker-notes]].
7. **Cut implementation detail that doesn't serve the argument.** Implementation sits below the goal.
   - "three backends part not needed, ragged input via a mask and all not needed, wdym by jet regime and event regime" [F1].
   - "Why triton not required, execution not required" [F1].
8. **One topic per slide.** Every main slide ends with a take-away line.
   - "two topics on one slide", "No final statement", "Run 3 analyses are under way is not a take-away" [H1].
   - Positive examples he gave: "I like the final statement here" [F1, H1].
9. **Say on every slide which inputs or datasets it uses.** Label them consistently (A, B, C1, C2, …), and don't repeat a definition that an earlier slide already gave.
   - "Clearly define the inputs in each slide subtitle … make each dataset like c1,c2 etc" [F2].
   - "If we have already defined input B before why do we need all this information down here now" [F2].
10. **Put source links on slides without changing the figures.**
    - "add paper links, everywhere I mean, don't change figures, just add in slides" [F2].
    - For public talks, see the conflict in §8.2.
11. **Wire main slides to backup and backup to main slides.** Every backup slide is reached by a "→ backup" pointer from a main slide, and every pointer lands on the right slide.
    - Higgs review fix list, agreed by Chirayu on 2026-10-15 and 2026-10-16 [H1, H2].
12. **Restructure by looking at real CMS talks.** When a slide is "not structured well", find comparable CMS presentations first and rebuild from them.
    - "need to look at other CMS presentations, etc, and remake this slide" [F1].
    - "go online, get me some reference slides first, then do that based on those" [F1b].
13. **Never make content up.** Every number on a slide has a source (note, file, command, commit, EOS path or paper) that can be checked. A caption must describe what the figure actually shows.
    - This is the rule throughout [[Meta/roles/keeper]].
    - Example: the `B3_shapes_SR_hplusc` figure was captioned as a template but shows shape variations [[Projects/HToWW/talks/_history/analysis-overview/REVIEW-HANDOFF]].

---

## 2. Internal personal work-update decks (keeper)

These are Chirayu's own progress decks, one per subproject. They are not CMS talks.
The authority for them is [[Meta/roles/keeper]] (Decks section) and [[Meta/roles/update-slide-style]]. The points below summarise those files; they are not new rules.

- **Location:** `<subproject>/deck/`, containing:
  - `<subproject>` means the actual leaf workstream, including nested subprojects; parent indexes link to that deck. Support folders such as assets, scripts and history are not separate deck owners (Chirayu's 2026-11-05 clarification in [[Meta/roles/keeper]]).
  - `index.html`: Reveal.js loaded from `_shared/reveal/`, no CDN;
  - `assets/`: plot previews of 300 KB or less, each with a small JSON giving the original path, script and commit;
  - `<name>_rN.pdf`;
  - `CHANGELOG.md`.
- **First build:** built from scratch from the subproject's notes. Older decks move to `_history/` unconverted.
- **Later updates:** change only the affected slides, found by their stable `<section id>`:
  - `status` first: where it stands and what needs Chirayu;
  - `result-<name>`, `decisions`, `open`, `changes`, `backup-<name>`.
- **Default style** ([[Meta/roles/update-slide-style]]):
  - status slide first;
  - one result per slide, with its plot;
  - few words;
  - backup holds the exact tables and sources.
  - Slide text is written as Markdown inside the sections.
- **Every revision:**
  - render-check the changed slides with headless Chrome;
  - export a new PDF revision;
  - update `CHANGELOG.md`;
  - the subproject README gets 3 status lines and embeds the latest PDF.
- **Feedback:**
  - Chirayu's slide comments go verbatim, with the date, into the comment log of [[Meta/roles/update-slide-style]], and each is distilled into a rule.
  - Newer rules win.
  - That log is empty as of 2026-11-05. The comments in §7 here come from talks, not update decks; see conflict §8.5.
- **Results are agent-reported** until Chirayu or a check validates them. Slides must say which ones are recorded, implemented, tested or validated.
- **Internal only.** Apply §4 before anything leaves the vault.

---

## 3. Group and analysis talks to expert audiences (internal CMS)

These come from the H+c status-deck review brief [[Projects/HToWW/talks/_history/analysis-overview/REVIEW-HANDOFF]], dated 2026-08-19 and written for that deck.

- **Audience:** physicists who know the analysis better than the presenter. Don't include tutorials (combine, datacards).
- **The deck must survive hostile questions.**
- **Every claim is measured, not asserted.** Weak points are labelled honestly.
  - Example: on that deck, the 1034 limit was labelled "under investigation". The brief says this was "deliberate, per the user's instruction". That is a recorded decision for that deck, not a quote.
- **Results that are private or not yet public never reach slides.**
  - The guard has to be deterministic (a string/filename list), not a model's judgement. *Agent design*, [[Meta/AgentHarness/2026-10-15-slide-review-agent-research]].
  - Example list: `forbidden_patterns` in the Higgs config (§5).
- **Example of a complete, checked deck record:** [[Projects/HToWW/talks/_history/ctag-and-negrw/README]]. It has:
  - the structure table;
  - the plots and the generator for each;
  - a "Deck claims independently verified" table that re-measures every number from the stored outputs;
  - the dropped figures, with the reason each was dropped.

---

## 4. CMS public and conference talks

### 4.1 CMS rules (apply to every external talk)
- **Public CMS results only:** papers, PAS, DP. Re-check that cited internal analysis IDs are still non-public before the talk.
  - Source: the 2026-10-16 review re-checked the status of HIG-25-001/-017 and HIG-26-003 [H2].
- **Label plots correctly:** CMS / CMS Preliminary / Simulation. Lumi and energy labels must match the figures. Simulation is captioned as simulation.
  - Source: [H2] finding 22; the agent design's deterministic checks.
- **Data-era framing must match the figure label.** A Run 2 result cannot be presented as Run 3 progress.
  - Source: [H2] finding 2, agreed with the reviewer's findings on 2026-10-16.
- **State the claim scope precisely,** e.g. "most stringent **direct** constraint; best expected sensitivity", not "tightest to date", when another result beats it on observed. An upper bound cannot answer a "does X exist" question.
  - Source: [H1] item 2; [H2] findings 1 and 15, agreed.
- **Results blocks say "95% CL, obs. (exp.)" and the method.** Notation is the same on every slide.
  - Source: [H1] minor 14; [H2] finding 21.
- **Every figure carries a link to its publication,** and the link points to the paper the figure actually comes from.
  - Source: [H1] minor 17.
- **Internal decks are not approved public talks.** Sensitive material never goes to an unapproved service.
  - Source: vault `CLAUDE.md` (Safety).

### 4.2 Legibility (public talks)
- The checks to run are:
  - can figure text be read from the back of the room;
  - is the text big enough to read;
  - is there empty space a figure could grow into;
  - does anything overflow the frame or footer.
- [H3] measured body text from the PDF (21 px on a 1280×720 slide ≈ 16 pt) against a "usual floor … about 18 pt (24 px)".
  - **Agent recommendation, from one talk.** It is not a confirmed universal rule (§8.3).

### 4.3 Recorded exceptions for review talks (Higgs 2026, 2026-10-15/16)
These are recorded, not verbatim. They were decided for a 15-minute public review talk of other people's work.
- "this is a review talk of others' work, so dense slides are acceptable, and only the terms the story needs get defined" [H1].
- Text density is fine; do not flag word counts. Source: `speaker_notes` in the config, dated 2026-10-16.
- Content and storyline are already approved. After 2026-10-18, review only text size and legibility, correctness and minor polish [H3, config].
- Chirayu declined two suggestions [H2]:
  - an ATLAS line on the CMS summary table (he keeps ATLAS in backup: "CMS talk");
  - moving the boosted slide to backup (he keeps it).
- He "cares little about backup polish" [H2].
- The S4 μ-limit plot stays on the slide (Chirayu: "it's okay"). This is a short quote inside the agent's note [H2].

---

## 5. The talk-specific config is not a standard

`Projects/HiggsCharmTalk-Higgs2026/slide-review.json` configures **one** talk:
- mode `public`;
- a 15+5 min slot;
- the Higgs 2026 audience;
- `max_words_per_slide: 200`;
- a forbidden-pattern list;
- dated speaker notes.

Copy its **structure** for new talks: deck, mode, audience, minutes, focus, forbidden patterns, speaker notes, context. Do **not** copy its values (word limit, focus, patterns) to other talks. Write a new config for each talk.

---

## 6. Reviewing slides

### 6.1 Review brief (copy for any deck review)
Source: [[Projects/HToWW/talks/_history/analysis-overview/REVIEW-HANDOFF]].

- Go slide by slide and ask four questions of each:
  1. Is the claim true and supported?
  2. Would this audience need it?
  3. What is missing that they would ask about right away?
  4. Does the plot show what the caption says?
- Report a numbered list keyed to slide number, most serious first.
- **Do not edit the deck while reviewing** if someone else is editing it.
- Name the known weak points and attack them first.

### 6.2 Check every claim against the source
- Check every number and claim against the real code, datacards, configs, papers or rendered page, never against the slide's own prose. A finding of "contradicted" needs a file or paper reference; without one it becomes "unverified". (Agent design in [[Meta/AgentHarness/2026-10-15-slide-review-agent-research]]; also how [H1–H3] were run.)
- Check page numbering before editing. The 2026-09-12 Flashjet mapping found that unnumbered title frames shift the S-numbers [F1].
- **Agent design, not confirmed rules** ([[Meta/AgentHarness/2026-10-15-slide-review-agent-research]]):
  - deterministic checks first (private-result guard, CMS labels, lumi/energy, undefined symbols, plot area, text density);
  - then reviewer agents for claims, plot vs caption, statistics, narrative and audience, and hostile audience;
  - then an editor that drops any finding without evidence;
  - PPTEval rubric (Content, Design, Coherence 1–5);
  - model routing by sensitivity;
  - a learning loop that scores the reviewer against Chirayu's manual reviews.

### 6.3 What the reviewer outputs
- Keep three things separate:
  1. Chirayu's own review lines;
  2. agent findings;
  3. Chirayu's reactions (agreed / declined).
- After the fixes are applied, record what changed and what was skipped and why. Follow the pattern in [H1–H3]: "Fix list agreed with Chirayu", "Chirayu's reactions", "Applied".
- When an agent does not follow an instruction, it says so on the record and gives the reason. Example: the Flashjet S7 tree-gallery order [F1], kept pending Chirayu's answer (§8.4).

### 6.4 Build and provenance (examples, not mandates)
- Two good build/provenance records:
  - [[Projects/DigiMorphing/phase2-morphing/talk/2026-10-26-iihe-talk-README]];
  - [[Projects/HToWW/talks/_history/ctag-and-negrw/README]].
- What they do:
  - give the build commands;
  - keep figures and PDFs out of git, with a fetch script to rebuild them;
  - list restricted crops by origin;
  - record a generator script for every figure;
  - name a script that reports overflowing slides;
  - state "not done yet" plainly;
  - keep a table of re-verified deck numbers.
- Treat overfull boxes and spilling content as build failures to fix or report.

---

## 7. Feedback log (verbatim, dated)

All quotes are reproduced exactly, including typos.

### [F1] Flashjet ML4Jets deck, 2026-09-12
Source: [[Projects/Flashjet/talks/SLides review]], `## Log`.
Slide numbers follow the agent's mapping in the same note: Outline = S1.

> - S2: Like the content , but its not structured well, need to look at other CMS presentations, etc, and remake this slide
> - S3: Why triton not required, execution not required, overall, the slide is not well explained, tractable part also, needs a full remake
> - S4: Firstly, the datasets used should come before this slide. Formula not visible clearly, and mechanism not explained clearly in steps or bullets, plot needs to be a bit bigger. Caption , what is dij , diB etc
> - S5: This needs to move up along with S6(dij diB defination can come here). Also maybe take this table from a paper or something. I like the final statement here
> - S6: Bigger plots needed. And maybe a better caption in point form?
> - S7: Nice I like the final sentence content, maybe better framing? And after this we need to right away jump to showing those binary trees
> - S8: Looks fine for now. But I feel this should go more towards the end of the ppt, just before ParT training
> - S9: This should be written in better statements, like three backends part not needed, ragged input via a mask and all not needed, wdym by jet regime and event regime.
> - S10: Dont put in slides put add a comment here explaining the results of the slide?
> - S11: Make the stop when formula bigger.
> - I'll come to next slides in another iteration

**[F1b]** Second pass, same note, quoted by the agent as "You said":

> "S2 and S3, go online, get me some reference slides first, then do that based on those. S5 do it without citing so reproduce. S7 and S6 same as S2 and S3. S8 also just do it."

### [F2] Flashjet substructure deck, inline comments
Source: [[Projects/Flashjet/talks/_history/substructure/flashjet-substructure_comments]].
The comments are undated. The deck footer is dated 2026-07-17, and git has no history for this path on the current branch.

> [Add github link] (title)
> [update this slide with a better table] (summary)
> [Add a slide on input C, all the cms datasets used]
> [add paper links, everywhere I mean, don't change figures , just add in slides ]
> [Clearly define the inputs in each slide subtitle if input C is used make each dataset like c1,c2 etc and clearly indicate which datasets were used]
> [Skip previous line as already in title,also,If we have already defined input B before why do we need all this information down here now]
> [same comments as previous slide]
> [only middle plot relavant rest move to backup also cleanup extra information and move to backup] (CMS (2))
> [move to backup] (CMS (2b))

### [H1] Higgs 2026 κc talk, review 1, 2026-10-15 (beamer)
Source: [[Projects/HiggsCharmTalk-Higgs2026/2026-10-15-slide-review]] (now `status: superseded`).
- `## Your review`, S1–S24: these lines are in Chirayu's style. Who wrote them is unclear (§8.1).
- Recorded decisions under "Fix list agreed with Chirayu":
  - he agreed to all correctness and content items;
  - the dense-slides / define-only-needed-terms exception for review talks;
  - about 3 extra slides allowed.

### [H2] Higgs 2026 κc talk, review 2, 2026-10-16 (beamer)
Source: [[Projects/HiggsCharmTalk-Higgs2026/2026-10-16-slide-review]].
- `## Your review`: same provenance caveat as [H1].
- `## Chirayu's reactions (16 Oct)` (recorded):
  - he agreed with every main-deck line and with findings 1 and 15;
  - he declined finding 4 (ATLAS line) and finding 6 (boosted slide to backup);
  - he "cares little about backup polish";
  - he wants a Feynman diagram on the title slide;
  - text density is fine.
- Short verbatim fragment: S4 plot "it's okay".

### [H3] Higgs 2026 κc talk, review 3, 2026-10-18 (HTML deck)
Source: [[Projects/HiggsCharmTalk-Higgs2026/2026-10-18-slide-review]].
- Scope was narrowed on Chirayu's request to legibility, correctness and minor polish.
- "Reactions saved: all six top findings agreed" (recorded).

---

## 8. Unresolved conflicts and open questions

1. **Who wrote the "Your review" lines in [H1]/[H2]?**
   - They read like Chirayu ("wdym"), but [H2] says he "agreed with every main-deck line under 'Your review'". That suggests the personal-reviewer agent drafted them and he endorsed them.
   - This file treats them as endorsed, not verbatim.
   - Chirayu to confirm.
2. **Citations on slides.** Three comments pull in different directions:
   - [F2]: "add paper links, everywhere";
   - [F1b]: "S5 do it without citing so reproduce";
   - [H1] S2: "arXiv ref not needed on slide".
   - Possible reading (agent inference): link the source of figures and results; reproduced teaching tables need no citation; in public talks put full references on a references slide, not in the bullets.
   - Not confirmed.
3. **Text density and font floors.**
   - "Few words" is the default for internal decks, and Flashjet wants explanations moved to notes.
   - The Higgs config allows up to 200 words and its speaker note says density is fine.
   - [H3] used about 18 pt as the conference floor.
   - None of these is a universal rule. Each talk config decides.
4. **Flashjet S7 order.**
   - Chirayu asked to "right away jump to showing those binary trees".
   - The agent kept the gallery three slides later, because soft drop is defined in between, and asked him to decide.
   - There is no answer in the vault.
5. **Where feedback is logged.**
   - [[Meta/roles/keeper]] says slide comments go into the comment log in [[Meta/roles/update-slide-style]], which is still empty.
   - This file holds the talk feedback.
   - The keeper should decide whether update-deck comments go only there (with talk comments here), or whether everything comes here.
6. **Model routing for internal material.**
   - The agent design sends internal decks to CERN-hosted models and public decks to Claude.
   - The Higgs reviews used Claude (public deck).
   - Whether Claude or other external models are approved for internal CMS slides is not recorded. Until it is, follow vault `CLAUDE.md` Safety.
7. **[F2] comments have no date.** The year 2026 and the deck date are inferred.
8. **Wrong frontmatter on the source note.** [[Projects/Flashjet/talks/SLides review]] has `tags: [hww]` and the title "Untitled", which hurts search ranking. This is noted, not changed.

9. **This file is unreviewed.** It was consolidated by an agent and nothing in it is approved by Chirayu as a whole. His verbatim quotes in §7 stand on their own; the grouping into rules in §1 is an agent reading of them.

> History, 2026-11-05: deferred during drafting (Chirayu: “Okay forget the slide instruction for now... Do that later... For now, just continue”), then resumed the same day (Chirayu: “Lauch a opus 5.5 agent yourself for the slides work”). Draft re-checked against the sources in [[Meta/slides/source-handoff]] and finished; quotes in §7 were re-verified against the source notes on 2026-11-05.
