---
tags: [reference]
status: active
date: 2026-10-12
source: laptop
---

# Combine-agent eval questions from HToWW

The questions with gold answers are in
[`combine-agent-evals/questions_hww.yaml`](combine-agent-evals/questions_hww.yaml).
They use the schema of Galli's eval set (`maxgalli/combine-bot` → `evals/questions.yaml`, 8 entries
as of 2026-10-12): `id`, `category`, `source_file`, `question`, `gold_answer`, `notes`, `attach`.
Graded there with RAGAS (Faithfulness / ResponseRelevancy / FactualCorrectness vs gold).
Setup context: [[2026-10-12-combine-ai-agent-setup]].

| id | what it tests | origin in our analysis |
|---|---|---|
| `mcstat-rateparam-1` | rateParam cannot shrink autoMCStats (e_i scales with normalisation) | [[2026-06-23-automcstats-rootcause]] (1742 → 1791) |
| `mcstat-threshold-1` | threshold is tested on the bin TOTAL n_eff, not per process | corrects our own `prop_binCR_vjets_bin7_higgsbkg` explanation |
| `mcstat-zero-yield-1` | 0 ± 40 process: inflates e_tot (BB-lite) or is silently skipped (per-process) | SR bin 6, V+jets 0.0 ± 41 |
| `freeze-mcstat-1` | `--freezeNuisanceGroups autoMCStats` / `rgx{prop_bin<ch>_bin.*}` | [[2026-08-11-route-to-a-better-limit]] |
| `channel-mask-sr-1` | CR-only fit with `--channel-masks` + `mask_SR=1` | pre-unblinding plan |
| `shape-only-syst-1` | `shape` normalises templates; norm via asym lnN → equalise integrals | 3FS/4FS shape-only decision |
| `shape-missing-down-1` | Down template is mandatory; t2w RuntimeError (verified) | c-tag 2D SF `up_Total` |
| `combinecards-era-correlation-1` | correlation by name; autoMCStats becomes per-era | 4-era combination, MC pooling |
| `agent-freeze-mcstat-1` | agent run: 1.8438 / 1.3320 / 0.9883 (v10.6.0) | execution path |

**How the gold answers were checked:**
- Every gold answer is written against the Combine docs on `main` (fetched 2026-10-12).
- Behaviour claims were run on lxplus (v10.6.0) with the public tutorial card `simple-shapes-TH1`, so the set contains no CMS-internal inputs.
- The scratch files are in `/eos/user/c/cgupta/combine-agent-tutorial/evalgold/`.
- Re-check the agent item's numbers on v11.1.0, the remote server's version.

**Dropped (gold not verifiable from the docs):**
- AsymptoticLimits at r ≈ 1000
- GoodnessOfFit on Asimov
- negative template bins (beyond "truncated at 0")
- pooled-MC autoMCStats across eras (kept only as a probe in the notes)
