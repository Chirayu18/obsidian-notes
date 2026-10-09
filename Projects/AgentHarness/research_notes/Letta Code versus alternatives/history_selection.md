---
tags: [reference]
status: active
date: 2026-10-08
source: laptop
---

# Per-turn learned selection of past messages for LLM context: prior art, evidence, architecture

Scope: what already exists for classifier- or model-based PIN/KEEP/COMPRESS/DROP selection of conversation history, what the benchmarks say, the known pitfalls, labeling methods, and whether this belongs in a proxy or in the harness. Current as of 2026-10-08. 16 search/fetch calls. Items marked *(prior knowledge, not re-verified)* come from training data, not from this session's searches.

## Q1. Does open-source code already do per-turn learned selection or eviction?

### Takeaway
Yes, two recent pieces of work cover most of the planned design. **LRE (arXiv 2606.20954, code released)** is a write-time learned eviction scorer: CPU-only logistic regression, budgeted keep, verbatim emit, with a self-supervised "later reference" label. **DyCP (arXiv 2601.07994, code NOT released)** is query-time relevance selection over turns, with contiguous-span extraction. Nobody has published the full combination of write-time static importance, query-time relevance, a knapsack, and a pinned state card. The user's design would be the first to combine them, but each part has a working precedent.

### Cited Findings
**LRE: Learned Relevance Eviction** (Lia & Mazumder, arXiv 2606.20954, v2 Sep 2026). Code: https://github.com/NusRAT-LiA/LRE
- Scorer: L2-regularized logistic regression, p_i = σ(θᵀφ(u_i, u_≤i)). It is CPU-only and uses no language model. Its features are causal: they see only the prefix up to the unit, never future units or the test query. — [arXiv HTML](https://arxiv.org/html/2606.20954)
- Agent features (AppWorld): relative position, log length, digit count, capitalized-word count, error indicator, code-token presence, rare-word density, Jaccard similarity with the previous step, and URL/ID presence. Conversation features: TF-IDF capped at 104, plus six trajectory features. — [arXiv HTML](https://arxiv.org/html/2606.20954)
- Retention: units are ranked by score per token cost, kept greedily under a budget (a knapsack approximation), and emitted verbatim in chronological order. Agent runs use a 2048-token budget and always keep the last 5 steps. — [arXiv HTML](https://arxiv.org/html/2606.20954)
- Unit granularity: an (action, observation) step for agents, a turn for LoCoMo, a session for LongMemEval-S. — [arXiv HTML](https://arxiv.org/html/2606.20954)
- Results on AppWorld: 41.1% task success vs 44.0% with full history (93% recovered), zero compressor calls, 52% lower worst-case peak prompt. On LoCoMo it gives the best budgeted answer quality while reading 68% fewer tokens. It outranks dense (BGE) and token-pruning (LLMLingua-2) scorers while being 295–1569x smaller. — [arXiv abs](https://arxiv.org/abs/2606.20954)
- Baselines: recency/FIFO, MemoryBank decay, TF-IDF salience, LLMLingua-2, frozen-BGE dense salience, ACON (LLM summarizer), and no compression. — [arXiv HTML](https://arxiv.org/html/2606.20954)
- Stated limitation: a write-time scorer "can evict information that later becomes important, even with perfect training data". — [arXiv HTML](https://arxiv.org/html/2606.20954)

**DyCP: Dynamic Context Pruning** (Choi, Zhang, Choi; Emory; arXiv 2601.07994, v5 Jun 2026)
- Runs outside the LLM. A bi-encoder scores every past turn against the current query, z-normalizes the scores, and then KadaneDial (a modified Kadane maximum-subarray search, τ=0.6, θ=1.0) picks contiguous high-relevance spans. Spans are concatenated in chronological order. It needs no pre-segmentation and no extra LLM calls. — [arXiv v3 HTML](https://arxiv.org/html/2601.07994v3)
- Retrievers tested: Contriever, Contriever-msmarco (used for generation), BGE-base-en, and BGE-base-en-v1.5. — [arXiv v3](https://arxiv.org/html/2601.07994v3)
- **Code: the paper gives a placeholder link (github.com/to/be/updated). No released repo.** — [arXiv v3](https://arxiv.org/html/2601.07994v3)
- The abstract was softened between versions. v1 said DyCP "consistently improves answer quality"; v5 says "competitive answer quality". — [arXiv abs](https://arxiv.org/abs/2601.07994)

**CWL: Context Window Lifecycle** ("Beyond Compaction", arXiv 2606.11213). Code: https://github.com/Kiz8-Team/pi-cwl (a fork of the pi.dev harness)
- The agent labels its own trajectory into typed episodes (`expl` and `act`) with a `delimiter` tool and declares dependencies, which form a DAG. A deterministic, LLM-free policy then evicts the oldest eligible `act` episode first. An `expl` episode can be evicted only after the episodes that depend on it are gone. Stripping is tiered: reasoning first, then bulk outputs (grep/glob), then file reads and bash, then whole episodes. **User turns are never evicted, and the prologue is protected.** — [arXiv HTML](https://arxiv.org/html/2606.11213)
- This is model-labelled but not learned. Its authors contrast it with Context-Folding, which uses RL (FoldGRPO) to learn branch/return. — [arXiv HTML](https://arxiv.org/html/2606.11213)

**ACON** (Kang et al., arXiv 2510.00615, ICML 2026). Code: https://github.com/microsoft/acon
- Optimizes a *natural-language compression guideline* rather than a classifier. An optimizer LLM compares cases where the full-context agent succeeds and the compressed agent fails, then revises the guideline. This is a counterfactual signal, applied at the level of the guideline. It reports 26–54% lower peak tokens on AppWorld, OfficeBench, and multi-objective QA while largely preserving performance. The compressor can be distilled into a smaller model. — [arXiv](https://arxiv.org/pdf/2510.00615); [search summary](https://proceedings.mlr.press/v306/kang26b.html)

**RL-learned memory managers.** These are model-based, not classifiers, and they write memories rather than select turns.
- Memory-R1 (arXiv 2508.19828): an RL-trained memory manager (ADD/UPDATE/DELETE/NOOP) plus an answer agent. Base models are LLaMA-3.1-8B and Qwen-2.5 3B–14B. It trains on LoCoMo and transfers to MSC and LongMemEval. — [arXiv](https://arxiv.org/pdf/2508.19828)
- Mem-α (arXiv 2509.25911): RL-learned memory construction into core, episodic, and semantic memory. On Qwen3-4B, RL lifts the average score from 0.389 to 0.642, per a third-party review. Trained on ≤30k-token instances, it generalizes beyond 400k tokens. — [HF paper page](https://huggingface.co/papers/2509.25911); [review](https://liner.com/review/memα-learning-memory-construction-via-reinforcement-learning)
- Memory-R2 (arXiv 2605.21768): a follow-up focused on fair credit assignment. — [arXiv](https://arxiv.org/pdf/2605.21768)
- MemBuilder (arXiv 2601.05488): RL memory construction with "attributed dense rewards". — [arXiv](https://arxiv.org/pdf/2601.05488)

**Commercial and proxy products**
- Supermemory "Infinite Chat" / Memory Router is a drop-in OpenAI-compatible proxy: `https://api.supermemory.ai/v3/<provider-url>` with user and conversation headers. It "removes unnecessary context from long conversations", segments history, and above roughly 20k tokens retrieves relevant earlier messages. Memories are written asynchronously. Its selection logic is proprietary and undocumented, and the "save up to 70%" figure is marketing. — [Supermemory docs](https://supermemory.ai/docs/model-enhancement/context-extender); [Memory Router](https://supermemory.ai/docs/memory-router/overview)
- Maximem Synap (the ACM paper, arXiv 2607.21503) is a lifecycle framework with five primitives: architecting, ingesting, scoping, anticipating, and compacting/consolidation. It reports 92% on LongMemEval and 93.2% on LoCoMo. These numbers are self-reported by a commercial reference system, and no open code was found. — [arXiv](https://arxiv.org/pdf/2607.21503); [HF](https://huggingface.co/papers/2607.21503)

**Framework reducers (heuristic, not learned)**
- LangChain `trim_messages`: token- or count-based trimming. `start_on="human"` and `ends_on=("human","tool")` keep valid ordering. This is a cut at turn boundaries, not a guarantee that every tool call stays paired. — [LangChain how-to](https://python.langchain.com/docs/how_to/trim_messages)
- Semantic Kernel / Agent Framework `ChatHistoryTruncationReducer(target_count, threshold_count)` and the summarization reducer cut at a "safe boundary index" so that function calls and their results are never orphaned. — [MS devblog](https://devblogs.microsoft.com/semantic-kernel/semantic-kernel-python-context-management/)

### Inferences
- **LRE is the closest thing to the planned classifier. Clone it and use it as a baseline before building anything.** Its findings argue against starting with bge-m3: a logistic regression on cheap lexical and structural features *beat* frozen-BGE dense salience as a write-time scorer. Embeddings may be more useful on the query-time relevance side (DyCP-style) than for static importance.
- DyCP's algorithm is simple enough to reimplement in about 50 lines from the paper (bi-encoder, z-normalization, Kadane spans). The missing code is not a blocker.
- The planned design amounts to "LRE (static, write-time) × DyCP (query-time) + CWL-style protection rules + Governance-Decay-style pinning". That decomposition is well supported. Two parts look genuinely new: the *combination* and the 4-way PIN/KEEP/COMPRESS/DROP label set.

### Gaps
- I did not verify code or method for MemOS, A-MEM, LangMem, Letta, Mem0, Zep/Graphiti internals, kiwi-mem, tinyMem, Mem-T, or Context-Folding repos in this session. From prior knowledge (not re-verified), A-MEM (arXiv 2502.12110), SeCom (arXiv 2502.05589, segment-level memory with LLMLingua-2 denoising), Provence (arXiv 2501.16214, a sentence-level context pruner for RAG), and LLMLingua-2 (arXiv 2403.12968, a token classifier) exist. None of them is a per-turn keep/drop classifier over chat history. Provence and LLMLingua-2 are within-passage pruners that could implement COMPRESS.
- I could not find kiwi-mem or tinyMem in this session, so I cannot say whether they exist or what they do.
- I did not confirm whether the Mem-α and Memory-R1 code is public.

## Q2. Benchmarks: selection vs summarization vs retrieval

### Takeaway
On conversational QA (LoCoMo, MT-Bench+), query-time *selection* of verbatim turns matches or beats full context at about 1/5 of the tokens. On agent and coding tasks, every method that drops history loses a few points versus full history (LRE −2.9 pts on AppWorld; CWL within noise on SWE-bench Lite and Terminal Bench), but cuts cost substantially. Vendor memory-layer leaderboards are mutually contradictory and should not drive the design.

### Cited Findings
- DyCP on LoCoMo (GPT4Score; first-token latency):
  - GPT-4o: 75.13 → 83.27 (2.32 s → 1.10 s)
  - Claude 3.7: 74.21 → 83.05 (5.54 s → 1.52 s)
  - GPT-4.1: 92.06 → 91.46, roughly flat, at 0.97 s

  Mistral-Nemo scores 66.75 → 79.04. — [DyCP v3](https://arxiv.org/html/2601.07994v3)
- DyCP average input tokens: LoCoMo 25,750 → 4,982; MT-Bench+ 20,364 → 2,698; SCM4LLMs 24,006 → 4,042. It beats SeCom and SCM4LLMs on retrieval hit, recall, and precision. — [DyCP v3](https://arxiv.org/html/2601.07994v3)
- **Stronger models gain less from pruning.** GPT-4.1 full context is already at 92, and DyCP slightly underperforms it. — [DyCP v3](https://arxiv.org/html/2601.07994v3)
- LRE: AppWorld 41.1% vs 44.0% full history. Macro-AUC for predicting evidence turns is 0.829 on LoCoMo and 0.708 on LongMemEval-S. — [LRE HTML](https://arxiv.org/html/2606.20954)
- CWL with GPT-5.4 at an 80k budget, vs baseline:
  - Terminal Bench 2.0: 68.25 vs 68.40
  - SWE-bench Lite (50 tasks): 43.0 vs 40.0
  - Recovery Bench: 66.8 vs 69.75
  - LongCLI: 20 vs 20

  The authors describe all differences as within run-to-run variance. Capping cut cost 20–70%. CWL cost 23% less than a compaction baseline on real repos (Excalidraw, Redis, Linux). Budgets above 120k added cost but no accuracy. A budget near 50k cut cost up to 3× but raised wall-clock time up to 2× because of re-exploration. — [CWL HTML](https://arxiv.org/html/2606.11213)
- ACON: 26–54% lower peak tokens with task performance largely preserved on AppWorld, OfficeBench, and multi-objective QA. — [ACON](https://arxiv.org/pdf/2510.00615)
- Memory-layer leaderboards conflict:
  - LongMemEval: Mem0 is cited at both 93.4% and 94.4% on Mem0's own pages, while another source has Zep at 63.8 vs Mem0 at 49.0.
  - LoCoMo: full context scored about 73% vs about 68% for Mem0's best variant in Mem0's own earlier comparison.
  - Letta's "files + 4 tools, no memory product" scored 74.0% on LoCoMo.

  — [Mem0 blog](https://mem0.ai/blog/ai-memory-benchmarks); [Mem0 vs Zep](https://mem0.ai/blog/zep-vs-mem0-which-ai-memory-layer-should-you-choose); [TowardsAI](https://pub.towardsai.net/mem0-vs-zep-vs-letta-a-folder-of-text-files-shouldnt-beat-the-61k-star-memory-layer-9d7e65c5799c)
- LoCoMo does not score knowledge updates (a user changing job, city, or preference), so it cannot test whether a selector honours *corrections*. — [TowardsAI](https://pub.towardsai.net/mem0-vs-zep-vs-letta-a-folder-of-text-files-shouldnt-beat-the-61k-star-memory-layer-9d7e65c5799c)
- ACM/Synap argues that naive accumulation makes cost quadratic in conversation length. Crude summarization makes cost linear but causes an "accuracy cliff". Only *validated* compaction keeps cost linear while preserving fidelity. — [arXiv 2607.21503](https://arxiv.org/pdf/2607.21503)

### Inferences
- For the user's use case (coding and analysis agent sessions), the relevant evidence is CWL and LRE-on-AppWorld, not LoCoMo. Expect parity or a small loss in quality. The win is cost and latency, not accuracy.
- **Verbatim selection beats summarization on fidelity** in every head-to-head found (CWL vs compaction, LRE vs ACON at zero compressor calls). Treat COMPRESS as the riskiest label.
- Building a personal eval set from one's own sessions matters more than public leaderboards. LoCoMo lacks updates, and vendor numbers disagree with each other.

### Gaps
- I found no benchmark that directly compares learned selection vs summarization vs RAG on *tool-heavy coding sessions* with the same model and budget. CWL is the closest, and it uses one model and small n.
- I did not fetch the official LongMemEval leaderboard. The numbers above come from vendor or secondary pages.

## Q3. Known pitfalls

### Takeaway
There are four main pitfalls:
1. Dropping standing constraints or corrections, which is measured and large.
2. Orphaning tool calls from their results, which is a hard API error.
3. Destroying the prompt cache, which is a real cost.
4. Re-exploration when the budget is too tight.

Pinning fixes the first cheaply, and an append-mostly layout mitigates the third.

### Cited Findings
- **Constraint loss (Governance Decay, arXiv 2606.22528).**
  - Across 7 models and 1,323 episodes, compaction raised policy-violation rates from 0% to 30% pooled, and up to 59% for DeepSeek-V4 and Kimi-K2.5. Claude-Sonnet-4.6 reached 19%, Gemini-3.5-flash 4%, GLM-5.1 0%.
  - When the constraint survived summarization, violation was 0% (n=90). When it was dropped, violation was 38% (n=315).
  - Soft organizational policies decay about 8.3× more than hard safety norms.

  — [arXiv HTML](https://arxiv.org/html/2606.22528v2)
- **Constraint Pinning** (about 47 tokens) restored 0% violation, with 99% of allowed actions completed and 1% over-refusal. An operator-impersonation injection in recent context still produced 17% residual violation, or 10% with provenance wording. — [arXiv HTML](https://arxiv.org/html/2606.22528v2)
- A "Compaction-Eviction Attack" through ingested content forced constraint loss: 65% violation on Claude, 100% on DeepSeek-V4. — [arXiv HTML](https://arxiv.org/html/2606.22528v2)
- **Tool pairing.** A ToolMessage is valid only after an AIMessage that made the tool call. LangChain's `start_on`/`ends_on` handles turn boundaries only. — [LangChain](https://python.langchain.com/docs/how_to/trim_messages). Semantic Kernel's reducers explicitly avoid orphaning function-call/result pairs. — [MS devblog](https://devblogs.microsoft.com/semantic-kernel/semantic-kernel-python-context-management/). The CWL paper does not address pairing at the tool-call level, because its dependencies are per episode. — [CWL](https://arxiv.org/html/2606.11213)
- **Prompt caching.**
  - Anthropic charges cache reads at 0.1× base input, 5-minute writes at 1.25×, and 1-hour writes at 2×. A request can have at most 4 breakpoints. — [Anthropic docs](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
  - OpenAI caches automatically above 1,024 tokens at about a 50% discount, with no write surcharge (the launch figure). — [OpenAI](https://openai.com/index/api-prompt-caching)
  - The DyCP authors concede that with KV or provider prefix caching, full context "may be as fast or faster" and that pruning lowers cache hit rates. — [DyCP v3](https://arxiv.org/html/2601.07994v3)
  - CWL: in-place eviction invalidates the cache, and under sustained pressure cache-write costs can exceed the savings. Holding the active size near a stable ceiling keeps the prefix mostly stable. — [CWL](https://arxiv.org/html/2606.11213)
- **Re-exploration.** Aggressive budgets (about 50k) cut cost 3× but doubled wall-clock time. — [CWL](https://arxiv.org/html/2606.11213)
- **Write-time blindness.** A static scorer cannot know future relevance. — [LRE](https://arxiv.org/html/2606.20954). This is why the query-time term is needed.
- **Recency.** LRE always keeps the last 5 steps and CWL never evicts user turns, so both hard-code recency or user-turn protection. — [LRE](https://arxiv.org/html/2606.20954); [CWL](https://arxiv.org/html/2606.11213)
- **Summary drift and hallucination.** CWL argues that LLM compaction has unpredictable lossiness, destroys causal structure, and can introduce hallucinations. Context-Folding's model-generated return messages carry the same risk. — [CWL](https://arxiv.org/html/2606.11213)

### Inferences
- **Fully fresh context on every message is the worst case for caching.** Rough arithmetic on Anthropic pricing: a 30k-token context that is re-written every turn costs 1.25× instead of about 0.1× on the stable portion, so input cost is roughly 10× higher on the reused part. Recommended layout:
  1. Stable prefix: system prompt + state card + PIN set, which changes rarely. Put a cache breakpoint here.
  2. Append-mostly selected history, re-selected only when the budget is crossed (hysteresis, as in CWL's ceiling) rather than on every turn.
  3. Volatile tail: query-time RAG + recent turns.

  This keeps most of the cache benefit.
- Make tool-pair atomicity a hard constraint: treat (assistant tool_call, tool_result) as one knapsack item. Make user corrections and constraints PIN by rule (regex or a small classifier for "don't / always / never / actually / instead"), not by a learned probability.

### Gaps
- I found no published measurement of end-to-end cache-hit loss for per-turn reselection in a real coding harness. The cost estimate above is an inference from list prices.
- OpenAI's cache TTL is reported inconsistently: 5–10 minutes in some sources, up to 1 hour off-peak in others.

## Q4. Labeling: counterfactual ablation, later-reference, cheaper proxies

### Takeaway
Both planned label sources have precedent. Later-reference labels are used by LRE: an identifier reused ≥3 times for agents, or ≥40% token overlap with the answer for dialogue. They recover 82–95% of supervised quality, but transfer poorly across domains. Counterfactual ablation is the basis of ContextCite (random-subset ablation + sparse linear surrogate) and, at the guideline level, ACON's success/failure contrast. ContextCite's sampling trick makes ablation affordable.

### Cited Findings
- LRE annotation-free labels:
  - Agent: a step is positive if an identifier it introduces is reused in ≥3 later steps.
  - Dialogue: a turn is positive if ≥40% of its content tokens overlap the eventual answer.

  The self-supervised variant recovers about 95% of the supervised signal on LongMemEval-S and 82% on LoCoMo. **The identifier-reuse label falls near chance on dialogue**, so labels are domain-specific. — [LRE HTML](https://arxiv.org/html/2606.20954)
- LRE supervised labels come from gold evidence annotations: LoCoMo evidence turns and LongMemEval `answer_session_ids`. — [LRE HTML](https://arxiv.org/html/2606.20954)
- ContextCite (arXiv 2409.00729): sample random ablation masks over sources, measure the logit of the original response's probability, and fit a LASSO sparse linear surrogate. Its weights are the attributions. Sparsity means only a few dozen ablations are needed rather than 2^n. Code is reportedly at github.com/MadryLab/context-cite *(not verified this session)*. — [arXiv](https://arxiv.org/pdf/2409.00729)
- AttriBoT (arXiv 2411.15102): a bag of tricks for cheaply approximating leave-one-out context attribution, such as proxy models and hierarchical attribution. — [arXiv](https://arxiv.org/pdf/2411.15102)
- SelfCite (arXiv 2502.09604): self-supervised context attribution using ablation-based rewards. — [arXiv](https://arxiv.org/pdf/2502.09604)
- ACON uses a counterfactual signal at the guideline level: (full succeeds, compressed fails) pairs feed an LLM that rewrites the compression guideline. — [ACON](https://arxiv.org/pdf/2510.00615)
- Semantic-aware prefix-cache eviction (arXiv 2605.18825) trains a lightweight classifier to predict whether the user will continue after a prompt/response pair. It is a nearby precedent for cheap learned eviction, but it targets KV caches. — [arXiv](https://arxiv.org/pdf/2605.18825)

### Inferences
- Replaying the full turn with and without message i, one message at a time, costs O(n) LLM calls per turn and is wasteful. Use **ContextCite-style random-mask ablation**: about 32–64 masked replays per target turn, with LASSO giving per-message attributions for all messages at once. Score with the log-prob of the actual next response, which requires an open-weights model on the GPU node (e.g. Qwen) rather than an API without logprobs.
- Use cheap proxies first, then ablate only a subset:
  - lexical or identifier later-reference (LRE)
  - explicit back-references ("as I said", quoted file paths or IDs)
  - attention or retrieval hits from the query-time scorer

  Use the ablation labels as a gold calibration set.
- Labels from one model's behaviour may not transfer to another model. LRE reports a "2× self-report inflation correction via replay" and only one host family plus two transfer models.

### Gaps
- I found no published work that uses per-message counterfactual ablation specifically to train a *chat-history keep/drop classifier*. ContextCite-style methods are used for attribution, not for training eviction policies. This appears to be a genuine gap.

## Q5. Architecture: proxy vs inside the harness

### Takeaway
There is precedent for both. Supermemory is a commercial OpenAI-compatible proxy. LiteLLM's `async_pre_call_hook` is the documented place to rewrite `data["messages"]`. CWL, LangChain, and Semantic Kernel live inside the harness. A proxy gives vendor independence, but it only sees opaque message arrays. The harness has the structure it needs: tool pairs, episode boundaries, file edits, and cache breakpoints.

### Cited Findings
- LiteLLM `async_pre_call_hook(user_api_key_dict, cache, data, call_type)` runs just before the completion call, can modify `data` including messages, and returns it. The docs include a guardrail example that loops over and rewrites messages. The `call_type` literal differs across versions. LiteLLM has no built-in context trimming. — [LiteLLM call hooks](https://docs.litellm.ai/docs/proxy/call_hooks); [custom guardrail](https://docs.litellm.ai/docs/proxy/guardrails/custom_guardrail)
- Supermemory Memory Router: a proxy URL prefix plus headers works with any OpenAI-compatible endpoint (OpenAI, Anthropic, Gemini, Groq, OpenRouter, custom), and writes memories asynchronously. — [Supermemory](https://supermemory.ai/docs/memory-router/overview)
- CWL needs the *agent itself* to emit episode delimiters and dependencies, which only works inside the harness. It is implemented as a fork of the pi.dev harness. — [CWL](https://arxiv.org/html/2606.11213)
- DyCP describes itself as "a lightweight context manager that runs outside the LLM", so it is architecture-agnostic. — [DyCP](https://arxiv.org/html/2601.07994v3)

### Inferences
- Recommended split:
  - Put the **selector library** (scoring, knapsack, pairing rules) in a pure Python package with no network calls.
  - Call it from a **thin LiteLLM proxy hook**. This works for any client that speaks OpenAI or Anthropic format, including Claude Code via `ANTHROPIC_BASE_URL`, and keeps the design vendor-independent.
  - Optionally call it from **inside the harness** where structure is available.
- The proxy has to reconstruct the conversation identity (a header or a hash of the prefix), keep its own archive store, and preserve tool-pair integrity on raw JSON. It also strips the harness's own cache_control markers, so it must re-insert breakpoints itself.
- A risk specific to proxying Claude Code or another harness that does its own compaction: two context managers fight each other. Disable the harness's auto-compaction or detect it.
- Latency budget on a 6 GB laptop:
  - bge-m3 embedding of one new message plus a dot product against cached embeddings, plus LightGBM: well under 100 ms.
  - Re-embedding history every turn is not necessary. Embed once at write time and store.

### Gaps
- I found no public precedent of a *learned* selector deployed as a LiteLLM hook. Supermemory's router is closed source.
- I did not verify how Claude Code reacts when a proxy rewrites its history, for example its expectations about tool_use IDs and thinking blocks. For Anthropic extended thinking, dropped or reordered thinking blocks can cause API errors. This needs testing.

## Design recommendations (synthesis, all inference)
1. **Baseline first.** Run (a) recency plus pins, (b) LRE as released, and (c) a DyCP reimplementation against your own logged sessions before training anything.
2. **Score.** Use score = static_prior(write-time, LRE-like LR/LightGBM on cheap features + bge-m3 cosine to the state card) combined with query_relevance(bge-m3 vs current query, Kadane span smoothing). Hard rules sit on top:
   - PIN for system and user constraints and corrections
   - always keep the last k turns
   - tool-call and result treated as atomic
   - never cut an `act` before its `expl` dependencies
3. **COMPRESS** should be extractive (LLMLingua-2 or Provence-style token or sentence pruning, or truncating tool outputs to head and tail), not abstractive summaries. This follows from the summary-drift and Governance Decay evidence.
4. **Cache-aware selection.** Use a stable prefix, re-select with hysteresis rather than on every turn, and keep the active size near a ceiling.
5. **Labels.** Bootstrap from later-reference (identifier reuse, quoted paths, IDs). Calibrate on a few hundred ContextCite-style random-mask ablations run on the CERN GPU with an open-weights model.
6. **Eval on your own data.** Measure the constraint-survival rate (ConstraintRot-style), the rate of user corrections being re-violated, tokens per turn, cache hit rate, and task success on replayed sessions.
