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

| id | what it tests |
|---|---|
| `mcstat-threshold-1` | autoMCStats threshold is tested on the bin TOTAL n_eff, not per process |
| `freeze-mcstat-1` | `--freezeNuisanceGroups autoMCStats` / `rgx{prop_bin<ch>_bin.*}` |
| `channel-mask-sr-1` | CR-only fit with `--channel-masks` + `mask_SR=1` |
| `shape-only-syst-1` | `shape` normalises templates; norm via asym lnN → equalise integrals |
| `shape-missing-down-1` | Down template is mandatory; t2w RuntimeError (verified) |
| `combinecards-era-correlation-1` | correlation by name; autoMCStats becomes per-era |
| `agent-freeze-mcstat-1` | agent run on the tutorial card: 1.8438 / 1.3320 / 0.9883 (v10.6.0) |

**How the gold answers were checked:**
- Every gold answer is written against the Combine docs on `main` (fetched 2026-10-12).
- Behaviour claims were run on the public tutorial card `simple-shapes-TH1` (v10.6.0).
- Re-check the agent item's numbers on v11.1.0, the remote server's version.

**Removed as too analysis-specific (2026-10-12):**
- `mcstat-rateparam-1` (rateParam vs autoMCStats on a starved NLO background)
- `mcstat-zero-yield-1` (0 ± 40 bin from weight cancellation)

Both came from [[2026-06-23-automcstats-rootcause]].
