---
tags: [results, combine-agent, evals]
status: active
date: 2026-10-21
source: lxplus
---

# omp + Qwen 3.8 baseline on the 10 public questions (3 tries)

**Setup**
* Harness `harness-omp` (eval dir `/eos/user/c/cgupta/cae-eval-2026-10`).
* omp 18.12.5 with the combine-assistant omp config: persona and skill from CVMFS 0.5.5, web on, timeout 400 s, Combine v10.6.0 on PATH via cmsenv.
* Model: `aigw/qwen3.8-27b-fp16`.

**Scoring**
* trajectory (`score_trajectory.py`);
* RAGAS FC recall and the rubric (`score.py`, Qwen judge);
* nuggets (`nugget_score.py` on branch `nugget-score`): Qwen as the headline judge, GLM-5.3-flash as the second judge, 3 judge repeats.

Results are copied to `/eos/user/c/cgupta/combine-agent-evals-results/2026-10-21/`. Related: [[2026-10-14-nugget-evaluation-research]], [[2026-10-21-kb-agents-workshop-takeaways]].

## Headline

| metric | value |
|---|---|
| runs finished / timed out | 22 / 8 |
| nugget pass (failed runs = 0) | 0.60 [0.37, 0.83] |
| V_strict | 0.67 [0.43, 0.88] |
| wrong-answer rate | 0.00 |
| pass^3 (all three tries pass) | 4 of 10 questions |
| Qwen vs GLM judge agreement | 96% exact, 98% support vs not, over 135 items |
| RAGAS FC (finished only) | 0.70 ± 0.08 |
| rubric overall (finished only) | 5.0 for all 22 |

## Per question

| question | runs (S scored, X failed) | nugget pass | FC |
|---|---|---|---|
| debug-fastscan-1 | SSS | 3/3 | 0.73-0.82 |
| gmn-control-region-1 | SSS | 3/3 | 0.75-0.92 |
| paper-statmodel-1 | SSS | 3/3 | 0.91-1.0 |
| forum-142937 | SSS | 3/3 | 0.5-0.86 |
| code-adaptive-hybridnew-1 | SSS | 2/3 | 0.44-0.62 |
| freeze-snapshot-1 | XSS | 2/3 | 0.7-0.76 |
| forum-130063 | SSS | 1/3 | 0.0-0.6 |
| forum-144631 | XXS | 1/3 | 0.87 |
| agent-setparam-range-1 | XXS | 0/3 | 0.6 |
| agent-run-asymptotic-1 | XXX | 0/3 | - |

**Spot checks of failed but scored answers (the judge was right in each case):**
* forum-130063 run 1 writes `r_bkg1 rateParam bkg1 <N> <f>`, missing the channel field. FC gave it 0.0 and the rubric 5.
* forum-130063 run 2 gives no syntax.
* agent-setparam-range-1 run 3 explains the cause but gives no fix.

## Scorer bug found and fixed

The first pass rejected 47 judge quotes: pass rate 0.47, judge agreement 90%. 35 of them were valid. Judges join spans out of document order and write formulas in Unicode where the answer uses LaTeX (`\vec{y}` vs `y`, `\prod_k` vs `∏_k`). The quote check now compares letters, digits and symbols only, in any order, and ignores spans under 6 characters.

The other 12 rejections were correct: the judge pasted the key point text or paraphrased. Fixed in nugget-score commit "robust quote check". The first-pass results are kept in `results/nuggets-v1-strictquotes/`.

## Why runs time out (all 8)

* **Compound shell commands are refused by omp.**
  * `command -v combine ...; which root | head` and `base64 ... | cut` are denied: omp's `bash.patterns` allow only simple commands, while opencode's glob matches the whole string.
  * So Qwen never finds the local `combine`. On `agent-run-asymptotic-1` it tries to ship the `.root` file to combine-run-remote as base64 (eval and task are also denied) and runs out of time in all 3 tries.
  * **This is a client-config difference to fix before more runs.** Options: `bash.allowCompoundCommands: true` (covers `&&` chains only), or allow-patterns that cover common forms, or the agent instructions.
* **omp's `read` tool fetches URLs.** On forum-144631 Qwen read GitHub raw files instead of using combine-mcp, the same URL 22 times in one run (60-76 calls, a loop). It is a corpus bypass even with web fetch in mind, and a loop.
* **agent-setparam-range-1 run 2 stalled:** 2 tool calls (the second a denied compound command) and then nothing until the timeout. Probably a hung model call.
* **freeze-snapshot-1 run 1:** 9 remote run_combine calls, 7 of them the same command.
