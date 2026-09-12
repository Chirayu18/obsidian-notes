---
tags:
  - hww
status: active
pinned: false
related:
date: 2026-09-12
---

# Untitled

> `BUTTON[toggle-status, toggle-pin]`  `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

---

## Commands

```bash

```

---

## Tasks

- [ ] 

---

## Log
- S2: Like the content , but its not structured well, need to look at other CMS presentations, etc, and remake this slide
- S3: Why triton not required, execution not required, overall, the slide is not well explained, tractable part also, needs a full remake
- S4: Firstly, the datasets used should come before this slide. Formula not visible clearly, and mechanism not explained clearly in steps or bullets, plot needs to be a bit bigger. Caption , what is dij , diB etc
- S5: This needs to move up along with S6(dij diB defination can come here). Also maybe take this table from a paper or something. I like the final statement here
- S6: Bigger plots needed. And maybe a better caption in point form?
- S7: Nice I like the final sentence content, maybe better framing? And after this we need to right away jump to showing those binary trees
- S8: Looks fine for now. But I feel this should go more towards the end of the ppt, just before ParT training
- S9: This should be written in better statements, like three backends part not needed, ragged input via a mask and all not needed, wdym by jet regime and event regime. 
- S10: Dont put in slides put add a comment here explaining the results of the slide?
- S11: Make the stop when formula bigger. 
- I'll come to next slides in another iteration

---

## Response (Claude, 2026-09-12)

Slide numbering used: frames 1-2 are `[plain,noframenumbering]` (title + cover), so
**Outline = S1** and S2-S11 are frames 4-13. Cross-checked against the content —
S4 mentions $d_{ij}/d_{iB}$ and that frame is the recombination slide; S11 mentions a
"stop when" formula and that frame is soft drop. Mapping confirmed before editing.

### DONE

- **S5 + S6 moved up** — "One exponent, three algorithms" now precedes "How sequential
  recombination works", so $d_{ij}$ and $d_{iB}$ are *defined before they are used*.
  (S6 "akt gives rigid jets" already sat directly after, so it moved with it.)
- **S4** — rewritten. Plot to full width; added an explicit two-column block defining
  $d_{ij}$ = pair distance and $d_{iB}$ = beam distance, then the algorithm as a
  numbered 3-step loop instead of one dense prose caption.
- **S9** — dropped the implementation-detail bullets ("three backends,
  auto-dispatched", "ragged input via a mask") and replaced the jargon: "jet regime
  *and* event regime" → "scales from single jets to whole events".
- **S11** — the soft-drop stopping condition is now a large displayed equation
  ($\min(p_{T1},p_{T2})/(p_{T1}+p_{T2}) > z_{cut}(\Delta R_{12}/R)^{\beta}$) instead of
  being buried in a footnote; plot slightly reduced to make room.
- Deck **rebuilt and compiles clean**. Backup of the previous version at
  `flashjet-ml4jets.tex.bak_review`.

### S10 — the explanation you asked for here instead of on the slide

S10 is **F1, exclusive $k_t$ subjets**. What the slide shows and what it means:

Exclusive clustering stops when exactly $N$ objects remain rather than when the beam
distance wins, so a jet is forced to resolve into exactly $N$ subjets. Reading them off
the *stored* $k_t$ history costs nothing extra — the tree is already there, so this is a
post-read, not a re-clustering. The physics content: the $k_t$ tree is ordered by
relative $p_T$, so the last few merges are the hardest ones, which is exactly the
splitting scale a boosted-object tagger wants ($\sqrt{d_{12}}$, $\sqrt{d_{23}}$, ...).
That is why F1 uses $k_t$ and F2/F3 use C/A: different orderings expose different physics
from the same clustering.

### Second pass (all of S2/S3/S5/S6/S7/S8 now done)

You said: *"S2 and S3, go online, get me some reference slides first, then do that based
on those. S5 do it without citing so reproduce. S7 and S6 same as S2 and S3. S8 also just
do it."* All six are done. Deck compiles clean — **0 errors, 0 overfull boxes, 45 pages**.

**Reference deck used:** the **CMS Patatrack** talk (Kortelainen et al., HOW2019, indico).
It is the closest published analogue — a CMS GPU-offload project presented to a software
audience. Its structure, which I copied:
group/goal → *scope* ("focus on a ~10% slice of HLT time") → workflow → timing → lessons.
The key move is that **implementation detail sits below the physics goal**, never above it.

- **S2 remade** — now a numbered 1–4 argument instead of a flat bullet list:
  *1. Where the field is* (GPUs in the HLT since Run 3; ~30% of reco offloaded → ~25% less
  HLT time) → *2. What is missing*, as a centred standalone block: **"Jet clustering is
  still on the CPU"** → *3. Why it stayed there* (sequential, IRC-safe, serial data
  dependence) → *4. Why that costs us now* (reclustering in a training loop, R scans,
  substructure on demand). Patatrack's shape: state of the field, then the gap, then the
  cost of the gap.
- **S3 remade** — retitled **"flashjet — a GPU jet clusterer"** and reordered to answer
  *what it does* before *how it works*:
  **What it does** → **Why it can be done at all** (the Cacciari–Salam nearest-neighbour
  lemma as 4 steps, ending in $O(N^2)$ instead of $O(N^3)$) → **In the ML ecosystem**.
  **Triton is demoted to a side note** — that is the answer to "why Triton not required":
  it is an implementation choice (autotunes for whatever GPU it finds, no separate CUDA
  build), not part of the argument, so it no longer sits at the top of the slide.
- **S5 reproduced, not cited** — as you asked. The table is my own LaTeX (nothing lifted)
  and now has a **5th column, "used for"**, so each exponent is tied to what it buys:
  \akt → finding jets; C/A → grooming, Lund plane; $k_t$ → exclusive subjets. Row spacing
  loosened (`\arraystretch 1.25`). The citation sits **commented out** in the source
  (`%% \cite{Cacciari:2008gp}`) in case you later want it. Your closing statement kept.
- **S6** — plot up from 0.72 to **0.93** linewidth, and the prose caption is now **two
  columns of bullets** (left: what the panels are; right: what they show, ending on
  "the algorithm's defining result, **reproduced without FastJet**").
- **S7 reframed** — the closing block is now **"The tree is the product, not a
  by-product"**, and a grey lead-in line at the foot points forward to F1/F2/F3 and the
  real-jet tree slide.
- **S8 moved** — "Using it" is now the **last slide of the Speed section, immediately
  before the Downstream / ParT section** (slide 26 of 45), exactly as you asked.

**Two bugs fixed while compiling** (both mine, from the edits above):
- the S5 table preamble still declared 4 columns after I added the 5th → fatal
  *"Extra alignment tab"*, no PDF produced.
- S4 overflowed its frame by 27.6 pt once the plot went full width → removed the closing
  block there (it said "both distances are defined on the previous slide", which is now
  redundant since S5 precedes it) and trimmed the plot to 0.95 linewidth.
- also cleared a pre-existing 43.6 pt overfull line on F1: the $d_{ij}$ definition was one
  displayed equation in a narrow column; split over two lines.

### One thing I did *not* do the way you said, and why

S7: *"after this we need to right away jump to showing those binary trees."* The real-jet
binary-tree gallery is slide **13**, three slides after S7 — not immediately after. I left
the order alone because **that slide uses soft drop**, which is only defined on F2 (slide
12). Moving the trees up to slide 10 would show drops before the reader knows what a drop
is. Instead I changed S7's lead-in to promise the right thing: *"Three things are read off
that tree — F1, F2, F3 — and then we look at it on a real jet."* If you would rather have
the trees immediately and take the hit on soft drop being undefined, say so and I will
move it.

### Note on this file's frontmatter

`tags: [hww]` and the title `# Untitled` look like a template leftover — this is a
Flashjet/ML4Jets note, not HToWW. Worth fixing so vault-search ranks it correctly, but I
have not changed it since it is your note.
