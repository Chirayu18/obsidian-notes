---
tags: [reference]
status: active
date: 2026-08-13
source: lxplus
---

# RAG system — evaluation and deck

Evaluation of `scripts/rag/vault-search` against the alternatives, plus a deck
explaining how the system works.

- **`rag-system-deck.md`** — Marp deck (19 slides). Render:
  `npx @marp-team/marp-cli rag-system-deck.md --pdf --allow-local-files`
- **`rag-system-deck.pdf`** — rendered output
- **`img/`** — plots (regenerable via `eval/make_plots.py`)
- **`eval/`** — the harness, so the numbers can be re-derived or argued with

## What was measured

16 queries with labelled ground truth, phrased the way you'd actually ask —
deliberately avoiding the notes' own vocabulary. Split into `paraphrase` (8, no
shared distinctive term), `partial` (4), `literal` (4).

| Arm | Solved | Tool calls | Context read |
|---|---|---|---|
| B. vault + grep | 9/16 | 64 | 322k tok |
| C. vault + RAG | 12/16 | 46 | **91k tok** |

Retrieval quality: hit@5 **62% → 88%**, MRR **0.35 → 0.73**.

The headline is the context reduction (**3.5×**), not the accuracy: without an
index the agent runs a *search loop* — grep, read a wrong file, guess again —
and every wrong file is burned context.

## What was modelled

The third arm (**A. vanilla** — no vault, no notes) is *not* measured. The notes
exist; I can't un-know them. It's a model with stated inputs (`eval/vanilla_model.py`):

- repo source 7.5 MB / 168 files, 856 commits — **measured**
- orientation reads 15% of source — assumed
- re-deriving one finding: 180k tokens / 60 calls — anchored on the real record
  (the autoMCStats thread ran 2026-06-17 → 2026-07-12, ~4 weeks, 5 notes), and
  deliberately **deflated** so the vanilla figure is understated
- 35% of questions aren't derivable from code at all — assumed

Result: ~3,162k tokens for the same 16 questions (**35× the RAG arm**), answering
*fewer* of them (10 vs 12).

## The finding that matters most

A third of these questions have **no answer in the source code at any budget**.
"Which knobs did we decide to treat as one nuisance?" is a judgement call; the
code records what was done, never what was considered and rejected.

That's the argument for the vault — not retrieval speed. The RAG makes the record
cheap to reach; it doesn't create it.

## Caveats

- n=16, one vault, ground truth labelled by me. Directional, not publication-grade.
- Not an end-to-end agent study — no paired Claude Code sessions on real tasks.
  The token figures model a search loop; they are not session transcripts.
- Two real bugs were found *during* this evaluation (dead keyword arm; raw match
  counts burying exact-title matches). Both fixed; hit@5 went 62% → 88% as a result.
  Numbers here are post-fix.
