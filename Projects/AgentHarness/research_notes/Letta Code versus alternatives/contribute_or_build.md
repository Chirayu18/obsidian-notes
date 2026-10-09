---
tags: [reference]
status: active
date: 2026-10-08
source: laptop
---
# Contribute or Build: a vendor-neutral, learned per-turn context selector

Scope: does existing OSS already do this, how open the closest projects are to contributions, what the smallest publishable artifact would be, and how it fits the user's profile. Current as of 2026-10-08.

Method: about 16 tool calls. GitHub stats come from the public REST API (`api.github.com/repos/...`), fetched 2026-10-08 before the API rate-limited this session. Later repos were checked through their GitHub pages with WebFetch. The technical content of LRE, DyCP, CWL, ACON and ContextCite is covered in the sibling note `history_selection.md` and is not repeated here.

---

## Q1. Does any existing OSS project already combine vendor neutrality, learned per-turn history selection, pinned constraints, verbatim keep, and training from the user's own logs?

### Takeaway
No. Every piece exists somewhere, but no project combines them, and the projects with real users are all rule-based, LLM-prompted, or trained by a vendor. **No found project trains a keep/drop policy from the user's own logs with counterfactual labels.** Several popular projects now sit on the "context proxy" ground, though, so plain proxy-level pruning is not a differentiator. The open slot is the *learned, self-supervised selector*.

### Cited Findings

**Research code for learned selection (closest in method, but 0–3 stars and dormant)**
- **LRE** (github.com/NusRAT-LiA/LRE): **0 stars, 0 forks, last push 2026-06-23, no license file** (the API returns `license: null`). — [GitHub API](https://api.github.com/repos/NusRAT-LiA/LRE)
  - The repo has a README, `lre/` (features.py, labels.py, scorer.py, select.py), `experiments/` and `data/`. It has no CONTRIBUTING file and no tests dir. — [repo root](https://github.com/NusRAT-LiA/LRE)
  - It is "code only". All model calls route through OpenRouter with `openai/gpt-4.1-mini`, and the agent study patches into the ACON agent on AppWorld. — [LRE README](https://github.com/NusRAT-LiA/LRE)
- **pi-cwl** (Kiz8-Team): **3 stars, last push 2026-06-17, MIT**. It is a fork of the pi monorepo; its CONTRIBUTING.md is pi's, with pi's approval gate. It ships CWLPaper.pdf and CITATION.cff. — [GitHub API](https://api.github.com/repos/Kiz8-Team/pi-cwl); [CONTRIBUTING](https://github.com/Kiz8-Team/pi-cwl/blob/HEAD/CONTRIBUTING.md)
- **microsoft/acon**: **123 stars, last push 2025-10-14** (about a year with no commits), MIT, 8 open issues. — [GitHub API](https://api.github.com/repos/microsoft/acon)
- **MadryLab/context-cite**: **341 stars, last push 2024-10-08**, MIT. — [GitHub API](https://api.github.com/repos/MadryLab/context-cite)
- **DyCP** has no code release; the paper's link is a placeholder. — see `history_selection.md` / [arXiv 2601.07994v3](https://arxiv.org/html/2601.07994v3)
- **SWE-Pruner Pro** (arXiv 2607.18213, July 2026) is learned, but at a different granularity:
  - A small trained head on the coder LLM's own hidden states labels each line of a *tool output* keep/prune.
  - It saves up to 39% of tokens and gives +3.8% on SWE-Bench Verified on one model.
  - Code is at github.com/Ayanami1314/swe-pruner-pro.
  - It needs access to the agent model's internals (open weights), so it is not vendor-neutral, and it does not select *messages*. — [arXiv abs](https://arxiv.org/abs/2607.18213)
- **Self-GC** (Xiaohongshu, arXiv 2607.00692) is not learned:
  - A side *planner LLM* (default Qwen3.6-Plus) proposes fold/mask/prune per user turn or tool call once input exceeds 30% of the window.
  - Edits are committed only when the expected savings beat the cost of breaking the cache.
  - Results: about 44% of prefix tokens pruned, with 84.85% of future continuations unaffected, vs 54.55–69.70% for heuristics.
  - No GitHub repo was found. — [alphaxiv](https://www.alphaxiv.org/abs/2607.00692.md); [DeepLearning.AI The Batch](https://www.deeplearning.ai/the-batch/llms-take-out-the-agents-trash)

**Popular "context proxy / pruning" OSS, which is the crowded part**
- **headroomlabs-ai/headroom**: **about 74.7k stars, 5.8k forks, Apache-2.0** (per the GitHub page).
  - It runs as a library (`compress(messages)`), a proxy (`headroom proxy --port 8787`), an agent wrapper, and an MCP server.
  - It supports Claude Code, Codex, OpenCode, Cline, Aider, Goose, OpenHands, "Oh My Pi", and any OpenAI-compatible client.
  - **"History is never dropped"**: the frozen prefix stays byte-identical, and only the "live zone" (new tool output, latest turn) is compressed.
  - It has a learned text compressor, *Kompress-v2-base* on Hugging Face, "trained on agentic traces". — [GitHub](https://github.com/headroomlabs-ai/headroom)
  - Kompress's architecture is described inconsistently across secondary sources (ModernBERT token classifier vs text-to-text), which are likely partly AI-generated. **Unverified.** — [instagit deep-dive](https://instagit.com/chopratejas/headroom/what-is-kompress-base-and-how-is-it-trained); [mer.vin](https://mer.vin/2026/06/headroom-explained-open-source-context-compression-for-ai-agents-60-95-fewer-tokens/)
  - The 74.7k star count was read from the page by a fetch summarizer and was not cross-checked against the API, which was rate-limited. Treat the order of magnitude as plausible but **unverified**.
- **Opencode-DCP / opencode-dynamic-context-pruning**: **about 4.3k stars, 251 forks, AGPL-3.0**, about 1,426 commits.
  - Pruning comes from an LLM tool call (the model calls `compress`) plus rules (dedupe repeated tool calls, purge errors after N turns).
  - It keeps session history unmodified and substitutes placeholders at send time. `protectUserMessages` keeps user messages verbatim.
  - **No learned model. "Development has slowed, and new features are landing in Sleev first"** (Sleev is a separate proxy product covering Claude Code, Codex, Pi and Hermes). — [GitHub](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning)
- **fkiene/llmtrim**: **about 244 stars, MPL-2.0**. It is a local MITM proxy plus library and MCP server. All of it is deterministic (BM25+, TextRank, etc.), with a token gate and a "quality gate" that reverts lossy cuts. There is no learned model and no training from logs. — [GitHub](https://github.com/fkiene/llmtrim)
- Many tiny 2026 repos appear in GitHub search (0–4 stars each): `enslaver/litellm-acp-kernel` (a LiteLLM proxy callback for model-driven context compression, pushed 2026-10-08), `Ayush-o1/contextforge`, `saminkhan1/context-compression`, `pomagrenate/ice_age`, `naranor/wamp-proxy`, and a Pi port `@zenobius/pi-dcp` (rule-based: hash dedupe, superseded writes, keep last 10). — [GitHub search API](https://api.github.com/search/repositories?q=litellm+context+compression); [pi-dcp README](https://cdn.jsdelivr.net/npm/@zenobius/pi-dcp@0.1.0/README.md)

**Memory layers. These are adjacent: they store and retrieve facts and do not select verbatim turns.** All figures are from the GitHub API on 2026-10-08.
- mem0ai/mem0: 66.8k stars, Apache-2.0, pushed 2026-10-08. — [API](https://api.github.com/repos/mem0ai/mem0)
- getzep/graphiti: 31.6k stars, Apache-2.0, pushed 2026-10-07. — [API](https://api.github.com/repos/getzep/graphiti)
- plastic-labs/honcho: 7.5k stars, **AGPL-3.0**, pushed 2026-10-08. — [API](https://api.github.com/repos/plastic-labs/honcho)
- letta-ai/letta: 25.1k stars, Apache-2.0, last push 2026-09-10. — [API](https://api.github.com/repos/letta-ai/letta)

**Harnesses and gateway (integration targets).** All figures are from the GitHub API on 2026-10-08.
- letta-ai/letta-code: 3.55k stars, Apache-2.0, pushed 2026-10-08, 500 open issues or PRs. — [API](https://api.github.com/repos/letta-ai/letta-code)
- anomalyco/opencode (redirected from sst/opencode): 212k stars, MIT. — [API](https://api.github.com/repos/sst/opencode)
- earendil-works/pi (redirected from badlogic/pi-mono): 113.5k stars, MIT. — [API](https://api.github.com/repos/badlogic/pi-mono)
- NousResearch/hermes-agent: 252k stars, MIT, about 47.8k open issues or PRs. — [API](https://api.github.com/repos/NousResearch/hermes-agent)
- BerriAI/litellm: 60.4k stars, license NOASSERTION (the repo has an `enterprise/` dir alongside the MIT core), 5.3k open issues or PRs, CONTRIBUTING.md present. — [API](https://api.github.com/repos/BerriAI/litellm)

**Labeled datasets**
- No public Hugging Face dataset was found with per-turn keep/drop or eviction labels for agent sessions. The nearest are raw agent-trace sets such as DCAgent/taskmaster2-*, which have no labels. — [HF taskmaster2-8ep](https://huggingface.co/datasets/DCAgent/taskmaster2-8ep/blob/main/README.md)

### Inferences
- The space splits into two groups:
  - **Popular, unlearned proxies or plugins**: headroom, DCP, llmtrim. They are rule-, statistic- or LLM-driven.
  - **Learned but academic, dormant and unpackaged code**: LRE, pi-cwl, ACON, SWE-Pruner Pro.
- Nobody sits in the middle: a *packaged, vendor-neutral, learned message selector trained on the user's own logs*. That middle is the user's niche.
- Headroom's design ("history is never dropped", only the live zone is compressed) is the *opposite* bet to per-turn re-selection. It optimizes prefix-cache stability. This is a real tension, documented in `history_selection.md` (DyCP and CWL both concede cache costs), and any new project must answer it.
- "Proxy that trims context" is now a commodity. A new project that only does that would be invisible next to a 75k-star incumbent. **The defensible novelty is the learning signal (later-reference plus counterfactual ablation labels) and the benchmark/dataset, not the proxy.**

### Gaps
- Headroom's star count and Kompress model details were not cross-verified (API rate-limited; secondary sources conflict).
- The Supermemory router was not re-checked this session; that it is closed-source is prior knowledge, *unverified*.
- Reddit and HN discussions were not found directly; the r/LocalLLaMA search returned no specific thread.
- Self-GC's code availability is unknown.

---

## Q2. Are the closest projects open to contributions, and which contribution would have high leverage?

### Takeaway
The *method* repos (LRE, pi-cwl, ACON, ContextCite) are effectively dead ends for contribution: no license (LRE), forks of someone else's harness (pi-cwl), or about 1–2 years without commits (ACON, ContextCite).

The *platforms* (Letta Code, Pi, LiteLLM, opencode) are active and do merge external PRs. However, they gate contributors heavily against AI-generated slop and would only take small, verifiable patches, not a research subsystem.

Contributing is therefore good for *credibility and integration*, not as the vehicle for the core idea.

### Cited Findings
- **Letta Code** has CONTRIBUTING.md plus an **AI_POLICY.md** adapted from Ghostty's:
  - Every PR must disclose all AI tools used, select an authorship option, and include an exact "human-verification phrase".
  - "Noncompliant pull requests are automatically closed"; trusted contributors and org members are exempt.
  - "AI-generated media is not accepted." — [AI_POLICY.md](https://github.com/letta-ai/letta-code/blob/HEAD/AI_POLICY.md); [CONTRIBUTING.md](https://github.com/letta-ai/letta-code/blob/HEAD/CONTRIBUTING.md)
- Letta Code has 91 merged PRs matching "compaction".
  - Most are by collaborators (cpacker).
  - External "Contributor"-badged authors have had compaction or local-model fixes merged, e.g. #3977 "keep custom prompt in automatic full-summarization fallback" (feiiiiii5, 2026-08-24) and #3838 "use Ollama's served context window, not the GGUF maximum" (just-cameron, 2026-08-15).
  - Affiliation is inferred from badges only. — [letta-code merged PRs](https://github.com/letta-ai/letta-code/pulls?q=is%3Apr+is%3Amerged+compaction)
- **Pi** (and pi-cwl, which inherits its rules) has a first-contributor **approval gate**:
  - First open an issue that fits on one screen and is "written in your own voice"; a maintainer replies `lgtm`, and only then can you submit PRs.
  - "You must understand your code… your PR will be closed." — [pi-cwl CONTRIBUTING.md](https://github.com/Kiz8-Team/pi-cwl/blob/HEAD/CONTRIBUTING.md)
- **LiteLLM** has CONTRIBUTING.md and ARCHITECTURE.md and is extremely active (pushed 2026-10-08; 12k forks, 5.3k open issues or PRs).
  - A context-compression proxy callback already exists as a third-party repo (`enslaver/litellm-acp-kernel`), so the hook route is proven. — [GitHub API](https://api.github.com/repos/BerriAI/litellm); [search](https://api.github.com/search/repositories?q=litellm+context+compression)
  - The `async_pre_call_hook` mechanism is documented in `history_selection.md`.
- **DCP** (opencode) is AGPL and slowing down, with features moving to a commercial-looking sibling (Sleev). Contributing a learned scorer there would tie the work to AGPL and to a waning plugin. — [GitHub](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning)
- **LRE has no license.** Without one, default copyright applies and its code cannot legally be reused or redistributed. Even a fork or PR is ambiguous until the authors add a license. — [GitHub API](https://api.github.com/repos/NusRAT-LiA/LRE)

### Inferences (ranked by leverage, highest first)
1. **Open a polite issue on LRE asking for a license (and offering a pip-packaging PR).** It costs little and directly unblocks reuse of the closest baseline. If they add MIT or Apache, depend on `lre` as a baseline rather than reimplementing it.
2. **Release a clean, tested DyCP reimplementation.** It is about 50 lines of core logic (see `history_selection.md`) and the paper has no code. Ship it either as a module in your own library or as a standalone tiny repo, and tell the DyCP authors so they can link it. This is the single most *citable* small contribution.
3. **Small upstream PRs to Letta Code or Pi to earn trusted-contributor status**: compaction hooks, bugs that surface with local models via Ollama or vLLM. These are evidently mergeable (#3838, #3977). Their value is visibility and getting the *extension point* you need, not landing the selector itself.
4. **A Pi extension or Letta Code plugin** that calls your library is better than a patch to core: no approval friction for the logic, and the core repos stay a thin integration.
5. Contributing to ACON or ContextCite: low value (stale), except as citations and baselines.

### Gaps
- Exact external-PR merge rates and median time-to-review for Letta Code, Pi and LiteLLM could not be computed (API rate limit).
- Whether Letta Code exposes a public, pluggable compaction or message-selection hook (vs internal code) was not verified in source this session.
- No good-first-issue counts were gathered.

---

## Q3. If building new, what is the minimal novel, publishable, reusable artifact, and where could it be published?

### Takeaway
Build a **small pip library** with three parts:
- **(a)** a pluggable selector interface, with LRE-style, DyCP and learned scorers;
- **(b)** a labeling pipeline that turns any logged session into keep/drop labels via later-reference plus ContextCite-style random-subset ablation on an open-weights model;
- **(c)** a benchmark that reports quality vs tokens vs *cache cost* on LoCoMo/LongMemEval *and* on real coding-agent traces.

Ship a LiteLLM callback as the vendor-neutral adapter. Present the **labeled-trace dataset plus the benchmark** as the paper contribution, since no such dataset was found. The nearest open venue is the **ICLR 2027 workshops** (submissions around February 2027); the NeurIPS 2026 memory and agent workshops are closed.

### Cited Findings
- No Hugging Face dataset with per-turn keep/drop eviction labels was found. — [search result summary; HF DCAgent traces](https://huggingface.co/datasets/DCAgent/taskmaster2-8ep/blob/main/README.md)
- No published work uses per-message counterfactual ablation to *train* a history keep/drop classifier. ContextCite is used for attribution only. — `history_selection.md` (sibling note; [ContextCite arXiv 2409.00729](https://arxiv.org/pdf/2409.00729))
- Self-GC measures "future continuations unaffected" (84.85%), which is essentially a counterfactual-replay metric, but it uses it only for *evaluation* of an LLM planner, not for training labels. — [The Batch](https://www.deeplearning.ai/the-batch/llms-take-out-the-agents-trash)
- **Venues:**
  - **NeurIPS 2026 PALM** (long-term, personalized, safe memory for agents): deadline August 24–30, 2026, **closed**. — [memories.ai CFP](https://memories.ai/blogs/call-for-papers-palm-at-neurips-2026); [AI Workshop Tracker](https://aiworkshoptracker.com/conference/neurips/)
  - **Other NeurIPS 2026 agent workshops**, all closed in late August or early September: Resource-Aware Agentic AI, Evaluation of Interactive Agents, Agents in the Wild (deadline September 5), SLM-Agents (September 6), AgenticOS, and "Who Verifies the Agents?". — [resource-aware](https://resource-aware-workshop.github.io/); [eval-interactive-agents](https://eval-interactive-agents-workshop.github.io/); [agentwild](https://agentwild-workshop.github.io/neurips2026/); [SLM-Agents](https://slmw2026.github.io/); [AgenticOS](https://www.sigarch.org/call-contributions/agenticos-neurips-2026/); [verify-agents](https://verify-agents-workshop.github.io/)
  - **ICLR 2026 had a MemAgents workshop**, a precedent for a 2027 successor. — [MemAgents ICLR26](https://sites.google.com/view/memagent-iclr26/)
  - **ICLR 2027** (April 26–30, 2027): main-track paper deadline September 25, 2026 (passed). Workshop proposals were due 2026-10-09, with acceptance notifications on 2026-11-29, and the **suggested workshop paper deadline is 2027-02-01**. — [ICLR 2027 workshops CFP](https://iclr.cc/Conferences/2027/CallForWorkshops); [ICLR 2027 CFP](https://iclr.cc/Conferences/2027/CallForPapers)
- Related precedents for the paper's framing:
  - "Demand Paging for LLM Context Windows" (arXiv 2603.09023) reports that simple observation masking halves agent cost while matching LLM-summarization solve rates. **This is a strong cheap baseline the paper must beat.** — [arXiv 2603.09023](https://arxiv.org/pdf/2603.09023)
  - "Context as an Environment" (arXiv 2608.21690). — [arXiv](https://arxiv.org/pdf/2608.21690)

### Inferences
- **Minimal novel and publishable core.** The *labels* are the contribution: a self-supervised keep/drop signal combining later-reference with sparse counterfactual ablation, validated against gold evidence (LoCoMo, LongMemEval) and against Self-GC-style "continuation unaffected" replays.
  - A selector trained on these labels and compared to recency, observation masking, LRE, DyCP and LLM summarization at equal token *and* cache-adjusted cost is a complete workshop paper.
  - The PIN/KEEP/COMPRESS/DROP 4-way head is a secondary novelty.
- **Dataset value.** A released set of a few thousand labeled turns from real coding and analysis sessions would fill an apparent gap and be reusable by LRE, Self-GC and SWE-Pruner-style work.
  - Privacy is the catch: the user's CERN and analysis logs are sensitive, which matches the user's own principle 1.
  - Release labels on *public* traces instead: SWE-bench or AppWorld trajectories, opencode or Pi sessions on OSS repos, LoCoMo and LongMemEval. Keep personal logs for local fine-tuning only.
- **Packaging order.**
  1. Library with a stable `select(messages, query, budget) -> messages` API.
  2. LiteLLM `async_pre_call_hook` adapter (vendor-neutral; works for every harness that can point at an OpenAI-compatible base URL).
  3. Optional Pi or Letta Code extension that additionally passes structure (tool-pair boundaries, pins) the proxy cannot see.
- **Sequencing against deadlines.** About four months to 2027-02-01 is realistic for library plus labels plus a LoCoMo, LongMemEval and SWE-trace benchmark if scoped tightly. An arXiv preprint can go out earlier, independent of venue.

### Gaps
- The ICLR 2027 accepted workshop list is not out until about 2026-11-29, so a memory or agents workshop there is likely but **unconfirmed**.
- Other 2027 venues were not checked: ACL/EMNLP 2027 workshops, COLM 2027, and the NeurIPS 2027 Datasets & Benchmarks track (a natural fit for a labeled dataset).

---

## Q4. Profile angle: what makes such a project visible and credible, and how does it fit a physicist moving toward ML/AI engineering?

### Takeaway
In a space where the popular projects advertise "up to 95% fewer tokens", the credibility currency is **honest, reproducible measurement**: error bars, pre-registered comparisons, and stated cache costs. That is exactly a particle physicist's comparative advantage. Visibility comes from integrating with where users already are (LiteLLM, Pi, Letta Code, opencode, which have tens to hundreds of thousands of stars) plus an arXiv preprint and a short blog post with one clear plot.

### Cited Findings
- Headroom's visibility is driven by marketing-style claims ("cuts token spent 95%") amplified on Substack and Medium. — [The Applied Report](https://theapplied.substack.com/p/this-open-source-project-cuts-token-spent-95); [Medium](https://medium.com/design-bootcamp/headroom-the-netflix-tool-that-makes-ai-agents-10x-cheaper-fdd94b5252cf)
- Published results in this area are fragile and model-dependent. CWL authors call their SWE-bench differences "within run-to-run variance", and DyCP softened "consistently improves" to "competitive" between versions. — `history_selection.md` ([CWL](https://arxiv.org/html/2606.11213), [DyCP](https://arxiv.org/abs/2601.07994))
- The user's own vault already shows this discipline: pre-registered go/no-go designs (kappa-HCE A/B, "no-go") and a "control must falsify your setup" rule. — vault commits `cfd5045`, `555a78c`; memory note `control-must-be-able-to-falsify-setup.md`
- Harness reach (GitHub API, 2026-10-08): hermes-agent 252k stars, opencode 212k, pi 113.5k, litellm 60.4k, letta-code 3.55k. — [API](https://api.github.com/repos/NousResearch/hermes-agent)

### Inferences
- **Credibility signals:**
  - a pip package with CI and tests;
  - a benchmark table with seeds and CIs;
  - a cache-adjusted cost column (most competitors omit it);
  - a released labeled dataset on Hugging Face;
  - an arXiv preprint;
  - one integration that a real harness user can try in five minutes (a LiteLLM config snippet).
- Upstream PRs merged into Letta Code, Pi or LiteLLM give external validation that a personal repo cannot.
- **Career fit.** The project shows the full ML-engineering arc: data/labeling pipeline, classifier training, evaluation methodology, inference-latency constraints, and production integration. It is cleaner evidence than one more physics-ML paper. HEP habits (blinded and pre-registered analyses, systematic uncertainties, falsifying controls) are a visible differentiator in an area full of unreplicated "X% savings" claims.
- Avoid presenting it as "yet another agent harness". Hermes, opencode and Pi have 100k–250k stars, and a new harness will not be noticed. Present it as **"a measured, learned context-selection layer for any harness."**

### Gaps
- No data on how hiring managers weigh OSS contributions vs preprints for physics-to-ML transitions; this is opinion, not sourced.

---

## Q5. Risks: crowded space, fast-moving harness APIs, maintenance burden

### Takeaway
The real risks are three:
- being out-marketed by heavily-starred proxies;
- harness API churn breaking integrations;
- finding that learned selection gives no gain over cheap baselines (observation masking, recency plus pins) with strong models.

Mitigations: keep the core harness-agnostic (one LiteLLM adapter), make the benchmark and labels the durable contribution, and pre-register a go/no-go before investing in packaging.

### Cited Findings
- **Crowding.** Headroom (about 74.7k stars) already offers library, proxy, MCP and a learned compressor across about 18 harnesses. DCP (4.3k), llmtrim (244) and many small 2026 repos crowd the same niche. — [headroom](https://github.com/headroomlabs-ai/headroom); [DCP](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning); [llmtrim](https://github.com/fkiene/llmtrim)
- **Churn and abandonment.**
  - Projects in this niche fade fast: DCP's development "has slowed" with features moving to Sleev, ACON has had no commits since October 2025, and LRE and pi-cwl have had none since June 2026.
  - Repos also move: sst/opencode is now anomalyco/opencode, and badlogic/pi-mono is now earendil-works/pi.
  - — [DCP](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning); [GitHub API](https://api.github.com/repos/microsoft/acon)
- **Null-result risk.**
  - Observation masking matches LLM summarization at half the cost. — [arXiv 2603.09023](https://arxiv.org/pdf/2603.09023)
  - Strong models gain little from pruning (GPT-4.1 full context about 92 on LoCoMo; DyCP slightly below).
  - Every history-dropping method loses a few points on agent tasks (LRE −2.9 on AppWorld). — `history_selection.md`
- **Cache tension.** Headroom deliberately never drops history so that the prefix cache survives, and Self-GC only commits edits when the savings beat the cache cost. Per-turn re-selection is at odds with prefix caching. — [headroom](https://github.com/headroomlabs-ai/headroom); [The Batch on Self-GC](https://www.deeplearning.ai/the-batch/llms-take-out-the-agents-trash)
  - Caveat: with *local* models (the user's principle 1), there is no provider cache billing, though vLLM prefix caching still matters for latency.
- **Contribution-friction risk.** Letta Code auto-closes noncompliant AI-assisted PRs, and Pi requires issue approval first. — [AI_POLICY](https://github.com/letta-ai/letta-code/blob/HEAD/AI_POLICY.md); [Pi CONTRIBUTING](https://github.com/Kiz8-Team/pi-cwl/blob/HEAD/CONTRIBUTING.md)

### Inferences
- **Recommendation: a hybrid that is "build-first, contribute at the edges".**
  1. **Build** a small, focused library: selector interface, labeling pipeline, benchmark, LiteLLM hook. **Do not build a harness.**
  2. **Contribute:**
     - a license-request issue (and packaging) to LRE;
     - a public DyCP reimplementation;
     - one or two small, human-verified PRs to Letta Code and Pi to get extension points and trusted status;
     - a thin Pi or Letta Code extension that calls the library.
  3. **Gate it like a physics analysis.** Pre-register that the learned selector must beat recency+pins+observation-masking and LRE at equal *cache-adjusted* cost on held-out coding traces. If it does not, publish the labels, dataset and benchmark plus the negative result. That is still a credible artifact, and it is cheaper to maintain than a product.
- **Maintenance.** Keep integrations to two (LiteLLM callback, one harness extension) and pin harness versions in CI. Make the dataset and benchmark the long-lived asset, since those do not rot with harness APIs.
- Use permissive licensing (Apache-2.0 or MIT) for maximum adoption. Avoid building on DCP (AGPL) or Honcho (AGPL).

### Gaps
- No usage or telemetry data shows how many harness users actually run context proxies, so the size of the audience for a learned selector is unknown.
- How Headroom and Kompress perform on verbatim-identifier recall is unknown, so it is unclear whether a learned *selector* would beat Headroom's learned *compressor* on the user's coding traces. This should be the first experiment.
