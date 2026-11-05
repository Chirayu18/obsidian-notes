---
tags: [reference]
status: active
date: 2026-10-13
source: laptop
---

# Combine agent: Claude vs Qwen on the 13 new eval questions

**Submitted 2026-10-13:** [combine-assistant-evals!2](https://gitlab.cern.ch/cms-analysis/general/combine-assistant-evals/-/merge_requests/2) (13 questions + results PDF; Galli notified). Harness improvements MR to follow.

**Submitted 2026-10-14:** [combine-assistant-evals!3](https://gitlab.cern.ch/cms-analysis/general/combine-assistant-evals/-/merge_requests/3) (only `gmn-control-region-1` and `agent-shape-counting-1`, split out of !2 at Galli's request so the Qwen failures can be debugged one question at a time; !2 stays open).

Questions: [questions_hww.yaml](questions_hww.yaml), submitted to Galli's `combine-assistant-evals` (fork branch `add-usage-and-agent-debug-questions`).

## Setup

Both agents ran through Galli's own harness (`run_agent.py`, then `score_trajectory.py`), with the same MCP servers and the same combine skill.

| | Claude | Qwen |
|---|---|---|
| engine | Claude Code (`--engine claude`), default model | combagent (`--engine opencode`), `aigw/qwen3.8-27b-fp16` |
| where | laptop over eduVPN, no local Combine | lxplus, Combine on PATH |
| repetitions | 1 | 3 |

No LLM judge. Correctness was graded by hand against the gold answers.

## Results

| question | Claude | Qwen (3 reps) |
|---|---|---|
| `mcstat-threshold-1` | correct | 1 correct, 2 wrong (said the sparse process gets its own parameter) |
| `freeze-mcstat-1` | correct | 3 partial: group right, per-channel regex wrong (`prop_bincat_SR_…`, copied from the docs example) |
| `combinecards-era-correlation-1` | correct | 1 correct, 2 no answer |
| `asymptotic-blind-1` | correct | 2 correct, 1 no answer |
| `lnn-asymmetric-1` | correct | 1 partial (1/κ right, syntax wrong), 1 wrong (`0.93 1.10` instead of `0.93/1.10`), 1 no answer |
| `gmn-control-region-1` | correct | 3 no answer |
| `shape-question-mark-1` | correct | 1 correct, 1 wrong (plain `shape` line), 1 timeout |
| `gof-saturated-1` | correct | 3 correct |
| `agent-missing-down-1` | correct diagnosis, did not run | 3 stopped before answering (2 ran `text2workspace.py` and reproduced the crash first) |
| `agent-undefined-group-1` | correct, reproduced on combine-run | 1 correct, 1 stopped before answering, 1 no answer |
| `agent-shape-counting-1` | correct, reproduced on combine-run | 3 no answer |
| `agent-mask-ignored-1` | correct | 2 stopped before answering, 1 no answer |
| `agent-expected-significance-1` | correct, ran both commands on combine-run | 2 partial (fix right, explanation wrong), 1 stopped before answering |

Claude: 13/13 correct. Trajectory: tools used and no tool errors on all 13; `doc_hit` on all 8 usage questions; `exec_hit` false on `agent-missing-down-1`.

Qwen, 36 runs on the 12 questions that ran (`agent-missing-down-1` excluded): 9 correct, 6 partial, 4 wrong, 17 with no final answer (empty, a timeout, or stopped after announcing the next step). Retrieval itself is fine: `source_hit` and `doc_hit` are 24/24 on the usage runs. The weakness is finishing an answer, and on the conceptual questions applying the docs correctly (threshold, lnN syntax, `shape?`).

Every Qwen run that attaches a `.root` file logs `Cannot read binary file` from combagent's `--file`. It is not necessarily fatal: on Galli's `agent-run-asymptotic-1` Qwen still found the file in the repo, ran Combine and reported the right limits. On our three questions with a ROOT attachment, none of the 9 runs gave a final answer, but this test does not separate the attachment error from Qwen stopping early.

## Harness notes

Galli's Claude setup denies Bash, so on a machine without Combine Claude cannot base64 a ROOT file for combine-run. It diagnosed `agent-missing-down-1` by reading the histogram names from the file instead, which `exec_hit` scores as not run.

`run_agent.py` does not detach stdin; `claude -p` appends piped stdin to the prompt. Run it with `< /dev/null`.

`agent-missing-down-1` was rerun for both agents after its ROOT file was rebuilt (the old one's internal name gave the answer away); the table shows the reruns.
