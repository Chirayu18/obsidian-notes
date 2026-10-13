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

**Usage (gold stated by the docs):**

| id | what it tests | source |
|---|---|---|
| `mcstat-threshold-1` | autoMCStats threshold is tested on the bin TOTAL n_eff, not per process | `part2/bin-wise-stats.md` |
| `freeze-mcstat-1` | `--freezeNuisanceGroups autoMCStats` / `rgx{prop_bin<ch>_bin.*}` | `part2/settinguptheanalysis.md`, `part3/runningthetool.md` |
| `channel-mask-sr-1` | CR-only fit with `--channel-masks` + `mask_SR=1` | `part3/nonstandard.md` |
| `combinecards-era-correlation-1` | correlation by name; autoMCStats becomes per-era | `part2/settinguptheanalysis.md` |
| `shape-only-syst-1` | shape/norm split → equalise integrals (restored: Qwen passed it; recipe is derived) | `part2/settinguptheanalysis.md` |
| `asymptotic-blind-1` | AsymptoticLimits expected is post-fit by default; `--noFitAsimov`, `--run blind` | `part3/commonstatsmethods.md` |
| `lnn-asymmetric-1` | κ^θ: `1.2` gives ×0.833 at −1σ; asymmetric `κdown/κup` | `part2/settinguptheanalysis.md` |
| `gmn-control-region-1` | `gmN N` + α, rate = Nα | `part2/settinguptheanalysis.md` |
| `shape-question-mark-1` | one `shape?` line for mixed shape/rate effects | `part2/settinguptheanalysis.md` |
| `gof-saturated-1` | saturated GoF on data + toys, frequentist toys, p-value | `part3/commonstatsmethods.md` |

**Agent-debug (Galli's `agent-setparam-range-1` style):**
- Each one is a failing command on public tutorial cards.
- The gold answer is the real error plus the documented fix.
- The errors were captured on the remote combine-run server (v11.1.0) on 2026-10-13.
- Attachments are in `combine-agent-evals/attachments/<id>/`.

| id | failure | fix (source) |
|---|---|---|
| `agent-missing-down-1` | `RuntimeError: Failed to find background_alphaDown` | both Up+Down required (settinguptheanalysis) |
| `agent-undefined-group-1` | `Unknown nuisance group: theory` | declare `theory group = …` in the card (settinguptheanalysis, runningthetool) |
| `agent-shape-counting-1` | `KeyError: Shape map has no entry for channel 'counting'` | `combineCards.py -S` / `shapes * * FAKE` (settinguptheanalysis) |
| `agent-mask-ignored-1` | silent: `Warning: Did not find a parameter with name mask_counting` | `text2workspace.py --channel-masks` first (nonstandard) |
| `agent-expected-significance-1` | silent: 0.153 instead of 1.284 | `-t -1 --expectSignal=1` (commonstatsmethods; `--expectSignal` defaults to 0) |

**Docs discrepancy found:** the docs say `combineCards.py` fails when mixing shape and counting cards. In v11.1.0 the combination succeeds, and the failure only appears at the workspace step. Worth telling Galli and the Combine maintainers.

**Rule (matches Galli's examples):**
- The question is a conceptual or usage question, phrased as a user would ask it.
- The gold answer is stated by a cited source: a docs page, a solved forum thread, the paper or the code.
- Agent questions are "run my failing command and diagnose it".
- No numbers in the question prose (numbers only inside quoted commands, as in Galli's example).

**How the gold answers were checked:** every gold answer is written against the Combine docs on `main` (fetched 2026-10-12).

**Removed 2026-10-13 for not matching the examples' philosophy:**
- `shape-only-syst-1`: the "rescale Up/Down to the nominal integral" recipe is an inference, not stated by any source.
- `shape-missing-down-1`: the docs only say both templates are needed. The failure behaviour came from our own test run, and the forum thread (cms-talk 2199) is unsolved and contested.
- `agent-freeze-mcstat-1`: a "compute this for me" task, not a "debug my failing command" question.

`shape-only-syst-1` was restored on 2026-10-13 because Qwen passed it.

**Removed 2026-10-12 as too analysis-specific:**
- `mcstat-rateparam-1` (rateParam vs autoMCStats on a starved NLO background)
- `mcstat-zero-yield-1` (0 ± 40 bin from weight cancellation)

Both came from [[2026-06-23-automcstats-rootcause]].
