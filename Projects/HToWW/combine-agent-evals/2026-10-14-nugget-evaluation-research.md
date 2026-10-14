---
tags: [reference, combine-agent, evals]
status: active
date: 2026-10-14
source: laptop
---

# Nugget / key-point evaluation for the Combine agent: literature, RAGAS comparison, Agenthon lessons

Research done on 2026-10-14 for the combine-assistant-evals harness (MR !2, !3, see [[2026-10-13-claude-vs-qwen-results]]). Citations were checked against arXiv, ACL Anthology or the publisher's page. Anything marked [unverified] could not be confirmed.

## Short answer

Nugget evaluation means human-written key points per question, each labelled vital or okay. An LLM judge then only decides whether the answer supports each point. As of 2025-2026 this is the consensus method for long-form and RAG answers. TREC RAG 2024 and 2025, TREC RAGTIME 2025, HealthBench, ResearchRubrics, ResearchQA and PaperBench all use a variant of it.

It differs from RAGAS in two ways: who writes the units, and whether they are fixed. In RAGAS an LLM re-splits the gold answer into claims on every run, and every claim weighs the same. With nuggets the units are written once by a human, carry importance weights and are reused. The current frontier adds negative items: HealthBench's negative points, the Pitfall items in Rubrics-as-Rewards, and RAGTIME's sentence support. Those items catch confident wrong statements, which recall-only scores miss.

The caveat is that this works for ranking systems over a whole set, not for grading a single question. In "The Great Nugget Recall" agreement with humans at run level is Kendall τ 0.73 to 0.90, but per topic it is only 0.3 to 0.66.

## What RAGAS actually computes in our score.py (checked in source)

We have ragas 0.2.15, file `ragas/metrics/_factual_correctness.py`, lines 252-285. `score.py` calls `FactualCorrectness(mode="recall")` with the defaults `atomicity="low"` and `coverage="low"`. The computation goes as follows:

1. The judge splits the **answer** into claims, then checks each against the gold answer. Answer claims supported by the gold count as `tp`.
2. The judge splits the **gold answer** into claims, then checks each against the answer. Gold claims missing from the answer count as `fn`.
3. recall = tp / (tp + fn).

So "recall" here is not "fraction of the gold points covered". The numerator counts claims from one decomposition and the denominator adds claims from a different decomposition. Several things move the score even when the content is the same:

* An answer that repeats a gold fact in three sentences gets three `tp`.
* A concise correct answer gets few `tp`.
* Incidental gold remarks, such as the "~50%" docs comment in gmn, always add to `fn`.

Both splits are redone on every call, so the score also moves from run to run (Wanner et al. 2024 show decomposition alone changes these scores). That is the most likely reason the GPT answers got rubric 5/5 but FC 0.41 to 0.66 on gmn-control-region-1.

## How nugget evaluation differs from RAGAS FC

| | Nuggets (AutoNuggetizer, TREC) | RAGAS FC recall |
|---|---|---|
| Units | written once by a human, or LLM draft plus human edit | re-split by the LLM on every run |
| Importance | vital / okay (or graded weights) | all equal, incidental claims included |
| Judge task | per nugget: support / partial_support / not_support | NLI entailment, binary |
| Stability | fixed denominator; only the assignment step is noisy | both the split and the assignment are noisy |
| Diagnosis | "missed vital point 3" | "4 of 9 claims", and the 9 are unknown |
| Wrong extra statements | not seen by recall; needs must_not items | precision mode only flags claims absent from the gold, which is not the same as wrong |

Lineage:

* TREC QA 2003 introduced vital/okay nuggets with recall over vital nuggets only. Its precision was a length allowance, because assessors could not list everything in an answer.
* The Pyramid method (Nenkova and Passonneau 2004) added importance weighting.
* Lin and Demner-Fushman 2006 showed that a single vital/okay vote is unstable, with zero-median scores when a question has one or two vital nuggets.
* The AutoNuggetizer (Pradeep et al. 2024) and "The Great Nugget Recall" (SIGIR 2025) are the modern versions. Their key result: **automating only the assignment step, on human-curated nuggets, agrees best with human assessors.** Per-topic τ rises from 0.49 to 0.66. The LLM was also stricter than the NIST assessors.

Close relatives:

* CheckEval: binary checklists beat Likert scales on agreement.
* HealthBench: about 48k physician criteria weighted from -10 to +10, scored as points earned over possible points.
* Rubrics as Rewards: Essential, Important, Optional and Pitfall weights. Rubrics help small judges most, which matters for our Qwen-27B judge.
* FActScore, VeriScore and SAFE are precision on atomic facts of the answer, the complementary direction.
* RAGChecker does claim-level precision and recall, close to RAGAS.

## Judge reliability

Judging the Judges (Thakur et al. 2024) found:

* use a chance-corrected agreement statistic; they used Scott's π, not Cohen's κ;
* small judges rank systems correctly but give wrong absolute scores;
* small judges are lenient: they say "correct" when unsure.

Two biases matter for us. Self-preference (Panickssery et al. 2024) is a real concern while the Qwen judge grades Qwen answers. Position bias means the order of the key points should be shuffled across judge repetitions.

No paper validates a ~27B Qwen as a nugget assigner against humans, so we have to calibrate it ourselves.

## Lessons from Agenthon Track 1 that apply here

Track 1 grading is the deterministic version of nuggets. Each unit had 5 to 85 hidden pytest checks: schema checks, reference values with per-value justified tolerances, and invariants. The pass rule was all-or-nothing, and failure labels came only from the grader, never from the participant's own report (`track1-coding-public/docs/TRUSTED-CHECKER-LABELS.md`).

What we learned there:

1. **The harness itself produced false passes.** 4 of the first 19/86 passes were false, because the checks were not mounted at `/tests`. Run collisions and a 400-character preview cut produced fake agent failures. For us the analogues are: the ask-permission kills, the `.root` attachment error, the combine-mcp `#`-in-code-fence bug, `score.py` skipping timed-out runs, and run_id collisions. Audit and tag these as harness failures before blaming the model.
2. **A reviewer that reads the output rubber-stamps.** s2 got "VERDICT: PASS" in 7 tokens; one unit got "28 OK / 0 WRONG" and still failed. The checklist gate (PASS needs `[OK] req — evidence` lines) forced evidence but did not make it true. For us: the judge must quote the answer span for every nugget it marks supported, and the harness checks the quote really appears in the answer.
3. **Measure each judge or check on known-right and known-wrong outputs before adopting it.** In Track 1:
   * the constraint scanner had 0/33 false positives on verified solutions and was kept;
   * a schema check flagged 14% of passing and 13% of failing outputs (no signal) and was dropped;
   * an output-only LLM judge flagged 5/21 passing vs 6/19 failing outputs and was not adopted.

   For us: the hand grades from 2026-10-13 (13 questions, Claude ×1 and Qwen ×3) are a ready-made calibration set.
4. **Noise is as large as a real difference.** s11 vs s12 flipped 11 units, and s16 vs s14b was +4 on 117 units against roughly ±10 noise. Ship a change only when the gains match a diagnosed failure mode. Report passed-in-any vs passed-in-every across reps.
5. **Freeze a hold-out set.** In Track 1 we froze 25 units on day 1, logged every inspection, and checked for near-duplicates. The dev leaderboard (0.98) was answer replay and did not carry over to the Final. For us: keep some questions out of all prompt, skill and retrieval tuning.
6. **The model fabricated evidence.** 46% of notebook replies in Track 1 contained an invented "Output:" block. Qwen's invented `<skill_content>` block is the same failure. Gate on real tool calls, never on the model's claims.
7. **Repeat loops at temperature 0.** These are a failure mode of their own; record them as a trajectory metric (the 45-call loop).
8. **"Almost right" usually meant one wrong convention.** 89% of failing values were computed differently, not missing. Keep vital nuggets as hard gates, so a fluent answer with a wrong lnN or shape convention cannot score 4/5.

## Recommended design for combine-assistant-evals

**questions.yaml.** Add `key_points` with 2 to 5 vital and 0 to 5 okay items, plus `must_not`:

```yaml
key_points:
  - id: kp1
    text: "With N MC events the relative stat uncertainty on the CR yield is 1/sqrt(N+1)."
    importance: vital
    accept: ["1/sqrt(N)", "Poisson relative error"]
  - id: kp2
    text: "gmN takes the observed CR count N and the extrapolation factor alpha."
    importance: vital
must_not:
  - id: mn1
    text: "Uses lnN for a control-region-driven normalisation."
    severity: major
```

Writing rules for the key points:

* one checkable fact per key point, stated in full;
* leave incidental gold content out;
* record observed wrong answers as `must_not`, e.g. Qwen copying the `prop_bincat` regex.

An LLM may draft the nuggets from the gold answer, but a human edits them. The answering model must not draft them, to avoid circularity.

**Judge.** One call per answer with the question, the answer and the numbered key points. Do not include the gold prose. For each key point the judge returns `support | partial_support | not_support` and a quoted span; a separate call returns `present | absent` per `must_not` item. Use temperature 0 where the endpoint allows it, shuffle the key-point order, run 3 judge repetitions with a majority vote, and report the label flip rate as judge noise.

**Scores per question, then averaged over questions:**

* `V_strict` = vital points supported / vital points. This is the headline, as at TREC.
* `W` = (Σ vital s + 0.5 Σ okay s) / (N_v + 0.5 N_o), with s = 1, 0.5 or 0.
* `contradiction` = any major must_not present.
* `pass` = all vital points supported and no major must_not. This is the Track 1 analogue.

Keep the 1-5 rubric as a secondary signal. Keep FC precision if wanted; drop FC recall as a headline.

**Agent-level reporting**:

* pass@1, pass@3 and pass^3 (τ-bench) from the 3 reps;
* standard errors clustered by question (Miller 2024), not over the 45 runs as if independent;
* paired per-question differences when comparing configs;
* a statement that at 15 questions only differences of about 20 to 30 points are resolvable;
* two denominators: every run counted, killed runs as 0; and valid runs only, with infra kills rerun and the kill rate shown next to it.

**Trajectory tags per run:**

* `INFRA_PERMISSION_KILL`, `TIMEOUT`, `LOOP` (N identical calls; threshold is our choice, no published standard);
* `UNGROUNDED_TOOL_CLAIM` (claimed output with no matching tool call);
* `CORPUS_BYPASS` (webfetch);
* `CITATION_UNPROVENANCED` (cited URL not returned by any tool in the run);
* `RETRIEVAL_MISS` vs `RETRIEVED_BUT_MISREAD`.

**Calibration.** Hand-label 30 to 50 answer/question pairs (about 200 to 300 nugget decisions) from both Claude and Qwen. Report:

* Scott's π or Cohen's κ;
* the confusion matrix and judge leniency (support where the human said not);
* agreement on Qwen answers vs Claude answers, as a self-preference check.

Target π or κ ≥ 0.6 to 0.7. Version the nugget bank and the calibration set together. Galli's "don't grade by hand" still holds for scoring; the hand labels are only to validate the judge once.

## References

Nugget lineage:

* Voorhees, Overview of the TREC 2003 QA Track (TREC 2003): vital/okay nuggets, F_β, length allowance.
* Nenkova & Passonneau, Pyramid method, HLT-NAACL 2004 (N04-1019).
* Lin & Demner-Fushman, POURPRE, HLT/EMNLP 2005 (H05-1117); Will Pyramids Built of Nuggets Topple Over?, HLT-NAACL 2006 (N06-1049).
* Pradeep, Thakur, Upadhyay, Campos, Craswell, Lin, Initial Nugget Evaluation Results for TREC 2024 RAG (arXiv 2411.09607).
* Same authors, The Great Nugget Recall, SIGIR 2025 (arXiv 2504.15068).
* Thakur et al., Support Evaluation for the TREC 2024 RAG Track (arXiv 2504.15205).
* Upadhyay et al., Overview of TREC 2025 RAG (arXiv 2603.09891).
* Lawrie et al., Overview of TREC 2025 RAGTIME (arXiv 2602.10024).
* Gupta et al., TREC 2024 BioGen (arXiv 2411.18069).
* Sharifymoghaddam et al., Chatbot Arena Meets Nuggets (arXiv 2504.20006).
* Dietz, Human-in-the-Loop Nugget Annotation (arXiv 2606.29033).

Key points, checklists and rubrics:

* Lee et al., KPQA, NAACL 2021 (arXiv 2005.00192).
* Qi et al., Long²RAG / Key Point Recall, EMNLP 2024 Findings (arXiv 2410.23000).
* Lee et al., CheckEval, EMNLP 2025 (arXiv 2403.18771).
* Arora et al., HealthBench (arXiv 2505.08775).
* Gunjal et al., Rubrics as Rewards (arXiv 2507.17746).
* Kim et al., Prometheus, ICLR 2024 (arXiv 2310.08491).
* Kim et al., BiGGen Bench, NAACL 2025 (arXiv 2406.05761).
* Starace et al., PaperBench (arXiv 2504.01848).
* Du et al., DeepResearch Bench (arXiv 2506.11763).
* Li et al., ResearchQA (arXiv 2509.00496).
* Sharma et al., ResearchRubrics, ICLR 2026 (arXiv 2511.07685).

Claim-level factuality and RAG metrics:

* Min et al., FActScore, EMNLP 2023 (arXiv 2305.14251).
* Wanner et al., A Closer Look at Claim Decomposition (arXiv 2403.11903).
* Song, Kim, Iyyer, VeriScore (arXiv 2406.19276).
* Wei et al., Long-form factuality / SAFE, NeurIPS 2024 (arXiv 2403.18802).
* Ru et al., RAGChecker (arXiv 2408.08067).
* Gao et al., ALCE, EMNLP 2023 (arXiv 2305.14627).
* Es et al., Ragas (arXiv 2309.15217).

Judges and their biases:

* Thakur et al., Judging the Judges (arXiv 2406.12624).
* Panickssery, Bowman, Feng, LLM Evaluators Recognize and Favor Their Own Generations (arXiv 2404.13076).
* Wang et al., LLMs are not Fair Evaluators (arXiv 2305.17926).
* Zheng et al., MT-Bench (arXiv 2306.05685).
* Haldar & Hockenmaier, Rating Roulette, EMNLP 2025 Findings (arXiv 2510.27106).

Agent reliability, trajectories and benchmark validity:

* Yao et al., τ-bench (arXiv 2406.12045): pass^k.
* Kapoor et al., AI Agents That Matter (arXiv 2407.01502).
* Kapoor et al., HAL (arXiv 2510.11977).
* Rabanser et al., Towards a Science of AI Agent Reliability (arXiv 2602.16666).
* Miller, Adding Error Bars to Evals (arXiv 2411.00640).
* Anthropic, Demystifying evals for AI agents (blog, 2026).
* Ma et al., AgentBoard (arXiv 2401.13178).
* He et al., TRAJECT-Bench (arXiv 2510.04550).
* Zhuge et al., Agent-as-a-Judge (arXiv 2410.10934).
* MCP benchmarks: MCP-Bench (arXiv 2508.20453), MCP-Universe (arXiv 2508.14704), MCPEval (arXiv 2507.12806), LiveMCPBench (arXiv 2508.01780).
* Cemri et al., MAST (arXiv 2503.13657).
* Zhu et al., Agentic Benchmark Checklist (arXiv 2507.02825).

Unverified: the venues for Ragas, RAGChecker, Panickssery and Wanner; the MAST step-repetition definition; RAGAS answer_correctness default weights. No "KPEval" paper matching the description was found.

Agenthon evidence paths:

* `~/agenthon_hacathon/STATUS.md`
* `testlib_build/{spot_check_v2.log,eval_testgen.log,NEAR_MISS_2026-10-06.md}`
* `submission/FINAL_DECISION_s16.md`
* `track1-coding-public/docs/{AUTHORING-GUIDE.md,TRUSTED-CHECKER-LABELS.md}`
* `ext_Fpengz_Agenthon-track-1-coding/experiments/README.md`
