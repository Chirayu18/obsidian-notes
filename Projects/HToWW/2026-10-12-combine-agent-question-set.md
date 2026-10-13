---
tags: [reference]
status: active
date: 2026-10-12
source: laptop
---

# Combine-agent eval questions

The questions with gold answers are in
[`combine-agent-evals/questions_hww.yaml`](combine-agent-evals/questions_hww.yaml).
They use the schema of Galli's eval set (`maxgalli/combine-bot` → `evals/questions.yaml`, 8 entries
as of 2026-10-12): `id`, `category`, `source_file`, `question`, `gold_answer`, `notes`, `attach`.
They are general-usage questions only, with no analysis-specific inputs, so they can go upstream as-is.
Setup context: [[2026-10-12-combine-ai-agent-setup]].

| id | what it tests | source |
|---|---|---|
| `mcstat-threshold-1` | autoMCStats threshold is tested on the bin TOTAL n_eff, not per process | `docs/part2/bin-wise-stats.md` |
| `freeze-mcstat-1` | `--freezeNuisanceGroups autoMCStats` / `rgx{prop_bin<ch>_bin.*}` | `docs/part2/settinguptheanalysis.md`, `part3/runningthetool.md` |
| `channel-mask-sr-1` | CR-only fit with `--channel-masks` + `mask_SR=1` | `docs/part3/nonstandard.md` |
| `combinecards-era-correlation-1` | correlation by name; autoMCStats becomes per-era | `docs/part2/settinguptheanalysis.md` |

**Rule (matches Galli's examples):**
- The question is a conceptual or usage question, phrased as a user would ask it.
- The gold answer is stated by a cited source: a docs page, a solved forum thread, the paper or the code.
- Agent questions are "run my failing command and diagnose it".

**How the gold answers were checked:** every gold answer is written against the Combine docs on `main` (fetched 2026-10-12).

**Removed 2026-10-13 for not matching the examples' philosophy:**
- `shape-only-syst-1`: the "rescale Up/Down to the nominal integral" recipe is an inference, not stated by any source.
- `shape-missing-down-1`: the docs only say both templates are needed. The failure behaviour came from our own test run, and the forum thread (cms-talk 2199) is unsolved and contested.
- `agent-freeze-mcstat-1`: a "compute this for me" task, not a "debug my failing command" question.

**Removed 2026-10-12 as too analysis-specific:**
- `mcstat-rateparam-1` (rateParam vs autoMCStats on a starved NLO background)
- `mcstat-zero-yield-1` (0 ± 40 bin from weight cancellation)

Both came from [[2026-06-23-automcstats-rootcause]].
