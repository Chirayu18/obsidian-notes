---
tags: [reference]
status: active
date: 2026-10-08
source: laptop
---

# Build the selector and borrow the harness

**Letta Code is the wrong foundation for this system.** Its core design is a persistent agent with an append-only conversation, a compiled memory prompt and usage-anchored compaction. That is the opposite of rebuilding fresh context every turn. Its hooks and mods cannot replace the message list. It also sends telemetry to api.letta.com by default, even in local mode, and the payload includes the full startup argv and raw tool stderr (verified in source at v0.34.7).

The recommended route has four parts:

- **Own the core in Python.** Write a network-free selector library (state card + PIN/KEEP/COMPRESS/DROP + RAG) and a thin orchestrator that holds the fresh-context invariant, the worktrees, the reviewer loop and the routing policy.
- **Borrow the harness.** Use **Hermes Agent** as the first off-the-shelf worker harness. Its documented Python `select_context` hook replaces each provider request without touching persisted history.
- **Add a LiteLLM adapter** so the same selector also serves Pi, opencode or Letta Code.
- **Route by data sensitivity.** Anything touching unpublished CMS content goes only to a self-hosted model on the lxplus-gpu V100S. The 6 GB laptop does embeddings and trivial tasks. Free cloud endpoints and paid models handle public work only.

You do not need a paid plan to start. A one-time $10 OpenRouter top-up is the best-value first purchase. Defer ChatGPT Plus ($20/month) until a measured bake-off shows free models are the bottleneck.

On the public-profile question: build a small, measured context-selection library with a labeled dataset and benchmark, not another harness, and contribute at the edges. The open niche is a *learned, self-supervised* selector trained from your own logs. Plain "context-trimming proxies" are already crowded. Your training in pre-registered, falsifiable measurement is exactly the credibility currency this space lacks.

## Update: using the existing Claude subscriptions

*Added after the synthesis, in response to "Claude is the strongest model and I have two subscriptions."*

**Claude Pro/Max subscriptions are reportedly barred only from *third-party* harnesses** (enforcement reported from 2026-01-09; terms updated around 2026-02-20; this comes from the paid-options note and was not re-checked against Anthropic's current terms). They remain usable through Claude Code itself. That fits the core design, because the fresh-context invariant lives in your own Python layer, not in the harness:

- **Backend A, the main brain:** each turn, your orchestrator builds the prompt (state card + selected messages + RAG) and calls Claude Code headless (`claude -p`, a new session per call), logged in with your subscription. Within that turn Claude Code keeps its own tools, subagents and hooks.
- **Backend B, everything else:** Hermes or LiteLLM, routed to the self-hosted CERN model, free endpoints, or a ChatGPT sign-in.
- **What you give up:** your selector chooses what enters each turn, but cannot trim context *during* a long multi-step Claude turn. Hermes's `select_context` would allow that; Claude Code manages its own context within a turn.
- **Do not** put a subscription-authenticated Claude Code behind a message-rewriting proxy (`ANTHROPIC_BASE_URL` → LiteLLM), and do not use the subscription inside Hermes, opencode or Letta. Claude in those harnesses requires a paid API key.
- **The sensitivity rule applies to Claude too.** Sending unpublished CMS results to Anthropic is the same policy question as sending them to OpenAI or NVIDIA. Get the CMS answer once and apply it to every provider; at minimum, turn off model training in Claude's privacy settings.

This changes the "Harness" and "Paid vs free" rows below. Claude Code (subscription) becomes the primary backend for non-sensitive work, Hermes becomes the harness for non-Claude models, and no new purchase is needed.

## Five decisions, stated plainly

| Decision | Verdict | One-line reason |
|---|---|---|
| Harness | Thin Python core + **Hermes Agent** as first worker harness; Pi as the TypeScript alternative; Letta Code only as an optional client behind the proxy | Hermes is the only Python harness with a documented, request-only per-call rewrite hook |
| Classifier location | Pure-Python library with no network calls, called in-process (orchestrator, Hermes `select_context`) and through one LiteLLM `async_pre_call_hook` adapter | The harness sees tool pairs and episode boundaries; a proxy gives vendor neutrality. Use both, sharing one library |
| Model routing | Sensitive → self-hosted Qwen3.6-27B or Nemotron 3 Nano (Q4 GGUF) on the V100S over an ssh tunnel. Laptop → bge-m3 + a 3–4B model. Public → OpenRouter free/ZDR, optionally ChatGPT Plus | NVIDIA's trial terms forbid confidential data; free endpoints commonly log |
| Paid vs free | Free to start; **$10 OpenRouter top-up now**; ChatGPT Plus only after the Phase 2 gate; no consumer plan ever sees CMS data | The top-up raises the free cap from 50 to 1,000 requests/day and unlocks ZDR routing |
| Contribute vs build | **Build** a selector + labels + benchmark library; **contribute** a license request to LRE, a DyCP reimplementation, and small PRs to Pi/Letta | Learned selection is the open niche; harnesses with 100k+ stars cannot be out-competed |

## Letta Code inverts the fresh-context invariant

Letta Code's local mode is real and officially supported. You no longer need the `LETTA_LOCAL_BACKEND_EXPERIMENTAL` variable: `letta backend local` sets the default. The local docs promise that "all agent state … stays on-device" ([Letta local mode](https://docs.letta.com/letta-code/local-mode)). The harness is still built around the opposite of your design.

Each turn, `HeadlessBackend` loads the stored, post-compaction conversation and sends it with the compiled MemFS system prompt and the tool schemas ([fake-headless-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/fake-headless-backend.ts)). No supported extension point can rewrite that list:

- `UserPromptSubmit` hooks only append a `<system-reminder>`, and only in the TUI ([hooks executor](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/hooks/executor.ts)).
- The mod `turn_start` event can rewrite only the *new* input, and `llm_start` is observe-only ([mods/types.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/mods/types.ts)).
- Provider mods register endpoints but have no request-transform hook ([pi-provider-mod-types.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/pi-provider-mod-types.ts)).

Inserting your classifier therefore means either a fork of the turn assembly or an upstream proxy, and the proxy route has a trap verified in source. Letta's context estimate anchors on **provider-reported usage** from the last assistant message ([local-context-estimate.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-context-estimate.ts)). If a proxy truncates the request, the reported usage comes back small, so Letta never compacts. Its own store keeps growing while the proxy keeps cutting, and nothing errors. A user running exactly your planned topology hit this class of failure: local backend → LiteLLM → vLLM Qwen. They reported silent one-token-overflow 400s and a "no-op compaction death spiral" ([#4962](https://github.com/letta-ai/letta-code/issues/4962)). The issue was bot-closed for template reasons, not fixed.

Three further facts weigh against it as a base.

**Privacy.** Telemetry is on unless `LETTA_CODE_TELEM=0` or `DO_NOT_TRACK=1`. It posts to `api.letta.com/v1/metadata/telemetry` with the **full startup argv** (so `letta -p "<prompt>"` ships the prompt text), **raw tool stderr**, and on errors a **debug-log tail**. A plain local install counts as a "cloud user" for error reporting ([telemetry/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/telemetry/index.ts)). Neither the README nor the local-mode docs mention it.

**Small models.** The local system prompt is about 15k tokens, and the stream-stall reconciler aborts after 60 s. On qwen3:8b every Ollama turn stalled ([#4650](https://github.com/letta-ai/letta-code/issues/4650)). That is fatal on a 6 GB card.

**Churn.** There were **100 releases in eleven weeks** (v0.28.17 on 2026-07-23 to v0.34.7 on 2026-10-08), with auto-update on by default ([releases](https://github.com/letta-ai/letta-code/releases)). A fork carrying a turn-assembly patch would need rebasing weekly.

Letta does have real strengths: Apache-2.0, git-backed markdown memory close in spirit to an Obsidian vault, fresh-context subagents defined as markdown files, and a deterministic Workflow tool. Its strongest residual use is as a *client* behind your proxy, or as a stateless executor through `--ephemeral`.

## Only three options give a documented per-request rewrite

The deciding question is narrow: can the harness replace the full message list before *every* model call without corrupting its persisted history? Only three options meet that bar with a documented API.

**Hermes Agent.** `ContextEngine.select_context()` "can return a replacement list for a single provider request". It is request-only, so persisted history is unchanged. It runs before cache-control and sanitizers, re-runs on retries, and keys messages with a stable `message_uid` that is ideal for per-message classifier state. The engine can also expose its own tools, such as a `recall_turns` RAG tool ([Hermes context-engine docs](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)).

**Pi.** The `context` and `context_with_system` extension events do the same in TypeScript ([Pi extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)).

**A thin PydanticAI loop.** `ProcessHistory` runs "before each model request" and replaces history ([PydanticAI](https://pydantic.dev/docs/ai/core-concepts/message-history/)).

opencode's equivalent, `experimental.chat.messages.transform`, is undocumented and works only by in-place splicing. The fix that would have made it work otherwise was closed unmerged ([#32758](https://github.com/anomalyco/opencode/pull/32758)). An open regression since v1.18.15 makes pruning through it "cosmetic": the model-visible context never shrinks ([#43764](https://github.com/anomalyco/opencode/issues/43764)).

| Harness | Language / license | Per-call rewrite hook | Subagents | Built-in memory | Telemetry status | Fit |
|---|---|---|---|---|---|---|
| **Hermes Agent** v0.21.6 | Python / MIT | **Yes, documented** (`select_context`, request-only) | `delegate_task`, isolated, 3 concurrent, synchronous | MEMORY.md (~2.2k chars), FTS5 session search | **Not audited** | **Best off-the-shelf** |
| **Thin loop** (PydanticAI + LiteLLM) | Python / MIT | **Yes** (`ProcessHistory`) | You build it | You build it | You control it | **Best control**; you own the core here anyway |
| **Pi** v1.1.0 | TS / MIT | **Yes, documented** (`context_with_system`) | None by design | Primitives only | `pi-telemetry` contracts; not audited | Best TS option; drive over RPC from Python |
| **Letta Code** v0.34.7 | TS / Apache-2.0 | **No** (fork or proxy needed) | Markdown subagents, depth 2, Workflow tool | MemFS git repo | **On by default, verified sends argv/stderr** | Client behind the proxy only |
| **opencode** v1.18.35 | TS / MIT | Partial, undocumented, regressed | Markdown agents, per-agent model, `steps` cap | None in core | Not audited | Pinned-version experiments only |
| Goose / Crush / OpenHands | Rust / Go (FSL) / Python | Not found | Varies | Minimal | Crush: opt-out documented | Poor fit |

Sources for versions, licenses and stars: GitHub API, 2026-10-08 ([hermes-agent](https://github.com/NousResearch/hermes-agent), [pi](https://github.com/earendil-works/pi), [opencode](https://github.com/anomalyco/opencode), [crush](https://github.com/charmbracelet/crush)).

Hermes ranks first for a concrete reason: `select_context` + `message_uid` + engine-owned tools + `clone_for_agent()` map almost one-to-one onto your design. The state card goes at the head. The classifier picks UIDs. A RAG tool searches old turns and the vault. All of it runs in-process Python, the same language as the classifier.

Hermes is not a safe bet in every respect. Its subagents run synchronously within the parent turn. Its repo shows about 47.8k open issues and PRs ([GitHub API](https://api.github.com/repos/NousResearch/hermes-agent)). Third-party guides say it wants 64K+ of context and that small models "drift on tool schemas" ([haimaker](https://haimaker.ai/blog/hermes-custom-provider-setup/)). **Its telemetry has not been audited.**

That is why the core belongs in your own thin Python layer, with Hermes as a pluggable worker harness rather than the foundation. Recent evidence also says you lose little by keeping the loop simple. A source-code study of eleven harnesses reportedly finds that "loop sophistication does not predict benchmark performance" ([secondary summary of arXiv 2609.00006](https://codex.danielvaughan.com/2026/09/03/harness-engineering-anatomy-eleven-coding-agents-codex-cli-architecture/)). A 176-setting ablation finds that context management matters most at tight budgets with weaker models, and that rule-based elision before summarization is the most efficient strategy ([arXiv 2609.20804](https://arxiv.org/abs/2609.20804)). Your free/local regime is exactly that case.

## The classifier belongs in a network-free library, with two thin adapters

The design question "proxy or harness?" has a both/and answer. The selector needs structure that only a harness sees: tool-call/result pairs, episode boundaries, and user corrections. Vendor neutrality needs a proxy that any OpenAI-compatible client can point at.

So put the scoring, knapsack and pairing rules in one pure-Python package with a stable `select(messages, query, budget) -> messages` API, and call it from two places:

1. **In-process**, from your orchestrator and Hermes' `select_context`, where structure is available.
2. **A LiteLLM `async_pre_call_hook`**, which is documented as able to rewrite `data["messages"]` just before the completion call ([LiteLLM call hooks](https://docs.litellm.ai/docs/proxy/call_hooks)).

Run inference on the laptop: a CPU logistic regression or LightGBM plus cached bge-m3 embeddings costs well under 100 ms per turn (estimated, not measured). Run label generation and training on the V100S.

Prior art tells you what to build first:

- **LRE** (Learned Relevance Eviction) is the closest precedent. It is a CPU-only logistic regression over cheap lexical and structural features, with greedy knapsack keeping and verbatim emit. It recovers **41.1% vs 44.0%** task success on AppWorld with zero compressor calls, and it **beats frozen-BGE dense salience** while being 295–1569× smaller ([arXiv 2606.20954](https://arxiv.org/abs/2606.20954)). Do not assume bge-m3 is the right static-importance feature. Use embeddings for query-time relevance instead.
- **DyCP** does query-time selection: bi-encoder scores, z-normalization, then Kadane contiguous spans. On LoCoMo it cut input from about 25.8k to 5.0k tokens while lifting GPT-4o from 75.1 to 83.3. It gave nothing for GPT-4.1, which was already at 92 ([arXiv 2601.07994v3](https://arxiv.org/html/2601.07994v3)). Stronger models gain less.
- **Governance Decay** sets the hard rule. Compaction pushed policy-violation rates from 0% to 30% pooled. A roughly 47-token constraint pin restored 0% ([arXiv 2606.22528](https://arxiv.org/html/2606.22528v2)). So PIN for user constraints and corrections must be rule-based, not a learned probability.
- **Atomic tool pairs.** Treat each (tool_call, tool_result) pair as one knapsack item. Orphans are hard API errors, and opencode has an open bug for exactly this ([#53109](https://github.com/anomalyco/opencode/issues/53109)).
- **Extractive COMPRESS only**, not abstractive summaries. Every head-to-head found favours verbatim selection on fidelity ([CWL, arXiv 2606.11213](https://arxiv.org/html/2606.11213)).

The fresh-context design has one well-documented cost: **prompt caching**. DyCP's authors concede that with prefix caching, full context "may be as fast or faster". CWL shows cache-write costs can exceed the savings under sustained eviction ([CWL](https://arxiv.org/html/2606.11213)). The mitigation is a layout:

1. A byte-stable prefix: system prompt, state card and PIN set.
2. Append-mostly selected history, re-selected with hysteresis when a budget ceiling is crossed.
3. A volatile tail: RAG hits and recent turns.

This tension also resolves your model-routing question in your favour. On self-hosted models there is no per-token cache billing, only latency. **The fresh-context design is cheapest exactly where your privacy policy already sends the sensitive work.**

## Sensitivity, not price, should route every call

The free cloud endpoints are not a privacy tier.

**NVIDIA.** The API trial terms restrict use to "internal testing and evaluation purposes, not in production" (§1.4). They forbid including "any confidential information, controlled or sensitive data" (§2.6a). They let NVIDIA collect user and generated content "to improve NVIDIA products and services, including AI models" (§3.3) ([NVIDIA API Trial ToS](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf)).

**OpenRouter.** `:free` models get **20 RPM and 50 requests/day**, rising to **1,000/day after a $10 lifetime top-up** ([OpenRouter limits](https://openrouter.ai/docs/api-reference/limits)). Data policy is per provider. A training opt-out makes OpenRouter refuse to route to providers that train ([OpenRouter provider logging](https://openrouter.ai/docs/guides/privacy/provider-logging)), and ZDR can be enforced account-wide ([OpenRouter ZDR](https://openrouter.ai/docs/features/zdr)). The Nemotron 3 Ultra `:free` page shows no provider or data policy ([OpenRouter](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free)).

At 5–15 calls per user message, 50/day is only 3–10 user turns. That alone makes the $10 top-up the obvious first purchase.

**CERN.** No production CERN LLM service exists yet. CERN IT presented a *planned* OpenAI-compatible LLM proxy with on-prem and cloud models in April 2026 ([Indico HEPiX](https://indico.cern.ch/event/1598655/contributions/7005586)). Self-hosting on CERN GPUs is therefore the only compliant sensitive route today. CMS collaboration rules can forbid sending unblessed results to *any* external service regardless of vendor terms, and that policy was not found publicly, so ask CMS computing/publication coordination.

The hardware dictates the rest.

**Laptop (RTX 4050, 6 GB).** Only 3–4B models fit fully on the GPU, e.g. qwen3.5:4b at 3.4 GB. On a 6 GB card "the trap is … the context window", because agent work needs about 64k `num_ctx` ([localaimaster](https://localaimaster.com/vram/best-ollama-models-6gb-vram), third-party). The laptop is your embedding and classifier box, not an agent driver.

**V100S (32 GB).** It can host Qwen3.6-27B or Nemotron 3 Nano (30B-A3.5B) at Q4. Volta has no FP8 or FlashAttention, and CUDA 13 dropped it, so use llama.cpp/Ollama GGUF or a CUDA-12.x vLLM build ([vLLM docs](https://docs.vllm.ai/en/v0.8.3/getting_started/installation/gpu.html)). Self-hosted Nemotron 3 needs vLLM's `qwen3_coder` tool parser plus its reasoning parser, or tool calls arrive as raw text ([Nemotron 3 Super card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)).

| Data class | Example | Route | Never |
|---|---|---|---|
| **Sensitive** | Unpublished yields, limits, datacards, AN drafts, EOS paths with blinded content | Self-hosted Qwen3.6-27B or Nemotron 3 Nano Q4 on lxplus-gpu V100S via ssh tunnel; laptop 3–4B for trivia | Any cloud endpoint, free or paid, until CMS and CERN policy is confirmed |
| **Internal-but-public-adjacent** | Your own framework code, public CMSSW, configs without results | V100S model, or OpenRouter with ZDR enforced | NIM trial; un-opted-out consumer plans |
| **Public** | Papers, generic coding, docs, OSS repos | OpenRouter free (Nemotron 3 Ultra `:free`, training opt-out on), NIM for evaluation, optionally ChatGPT Plus | — |
| **Embeddings / classifier** | Vault and turn embeddings, selector inference | Laptop: bge-m3 + CPU model | — |

Enforce this in the orchestrator, not in per-harness config. Tag each message with its data class at write time. Any outbound request to a non-local base URL that contains a sensitive-tagged message fails closed.

**On paid options:**

- **ChatGPT Plus ($20/month)** is the only major-lab subscription that OpenAI publicly tolerates in third-party harnesses. Pi and OpenCode are about 10% of Codex traffic, though the arrangement is "tolerated rather than committed" ([Manifest](https://manifest.build/blog/chatgpt-plus-tokens-third-party-harnesses/), third-party). Personal plans **train by default**, and Codex has a separate "full environments" toggle the ChatGPT setting does not cover ([OpenAI Help](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance)).
- **Claude Pro/Max** subscriptions are barred from third-party harnesses ([AlternativeTo](https://alternativeto.net/news/2026/2/anthropic-officially-bans-using-subscription-authentication-for-third-party-claude-use), third-party).
- **Gemini CLI** stopped serving AI Pro users in June 2026 ([dev.to](https://dev.to/owen_fox/gemini-cli-free-tier-shut-down-6-fixes-that-work-2026-26hc), third-party).
- **Pay-as-you-go APIs.** gpt-6-luna and Haiku 5.5 at $0.10/$0.50 per M tokens cost about **$8–130/month** at your volume. A flagship at $2/$10 costs **$165–2,640/month** uncached ([OpenAI pricing](https://developers.openai.com/api/docs/pricing); [Claude pricing](https://claude.com/pricing)).

There is a practical catch that the earlier "Plus is best value" framing misses. A subscription is reachable only through harnesses that implement "Sign in with ChatGPT" (Letta Code, opencode, Pi). Your thin Python core would need the pay-per-token API instead. Whether Hermes supports ChatGPT sign-in was not verified.

The verdict follows: **free plus a $10 OpenRouter top-up now**. Add ChatGPT Plus only if Phase 2 shows the V100S/free models fail public coding tasks that a frontier model passes, and use it then through Pi or opencode with both training toggles off. No consumer plan ever touches sensitive data.

## Build a measured selector, not another harness

Every component of your design exists somewhere, but no project combines them, and **none trains a keep/drop policy from the user's own logs with counterfactual labels**. The field splits into two groups:

**Popular but unlearned proxies.**

- Headroom: about 74.7k stars (page-read, unverified via API). It runs as library, proxy and MCP server, and deliberately never drops history so the prefix cache survives ([headroom](https://github.com/headroomlabs-ai/headroom)).
- opencode-DCP: 4.3k stars, AGPL, development "has slowed" ([DCP](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning)).
- llmtrim: deterministic ([llmtrim](https://github.com/fkiene/llmtrim)).

**Learned but dormant research code.**

- LRE: 0 stars and **no license file**, so it cannot legally be reused yet ([GitHub API](https://api.github.com/repos/NusRAT-LiA/LRE)).
- pi-cwl: 3 stars.
- ACON: no commits since October 2025.
- DyCP: no code at all.

No public Hugging Face dataset with per-turn keep/drop labels for agent sessions was found.

A context-trimming proxy is now a commodity. The defensible contribution is the **learning signal and the benchmark**: later-reference labels (LRE recovers 82–95% of supervised quality with them) plus sparse ContextCite-style random-mask ablation run on an open-weights model on the V100S ([ContextCite, arXiv 2409.00729](https://arxiv.org/pdf/2409.00729)). Report the results against cheap baselines at equal *cache-adjusted* cost. Observation masking already matches LLM summarization at half the cost ([arXiv 2603.09023](https://arxiv.org/pdf/2603.09023)), and that is the baseline to beat.

Contribution remains valuable at the edges. Two edge contributions cost little:

- **A license request plus a pip-packaging offer on LRE**, which unblocks the closest baseline.
- **A clean DyCP reimplementation.** It is about 50 lines of core logic, the paper has none, and it is the most citable small artifact.

Upstream PRs need care. Letta Code auto-closes PRs that do not follow its AI_POLICY.md disclosure and human-verification rules ([AI_POLICY](https://github.com/letta-ai/letta-code/blob/HEAD/AI_POLICY.md)). Pi requires an approved issue "in your own voice" before any PR ([CONTRIBUTING](https://github.com/Kiz8-Team/pi-cwl/blob/HEAD/CONTRIBUTING.md)). Small fixes do land: external contributors merged local-model and compaction fixes such as Letta #3838 and #3977 ([merged PRs](https://github.com/letta-ai/letta-code/pulls?q=is%3Apr+is%3Amerged+compaction)).

For publication, the nearest open venue is the ICLR 2027 workshops, with a suggested paper deadline of **2027-02-01** ([ICLR 2027 workshops](https://iclr.cc/Conferences/2027/CallForWorkshops)). An arXiv preprint can go out whenever the gate passes.

Release labels on *public* traces (SWE-bench/AppWorld trajectories, OSS-repo sessions, LoCoMo, LongMemEval). Keep CMS logs for local training only.

The framing matters for your profile. "Yet another agent harness" disappears next to 100k–250k-star projects. "A measured, learned context-selection layer for any harness, with error bars and cache-adjusted cost" stands out in a space whose most visible project markets "95% fewer tokens".

## Four phases, each with a pre-registered gate

The thresholds below are proposed pre-registrations derived from the cited baselines, not externally sourced numbers. Fix them in a dated vault note before running anything, in the same way as the kappa-HCE go/no-go design.

| Phase | Weeks | Concrete steps | Gate (go / no-go) |
|---|---|---|---|
| **0. Lock down and log** | 1 | Set `LETTA_CODE_TELEM=0`, `DO_NOT_TRACK=1`, `DISABLE_AUTOUPDATE=1` globally for any Letta trial. Never set `LETTA_REFLECTION_ARENA`, and keep `HF_TOKEN` out of agent env. Set `CRUSH_DISABLE_METRICS=1`. Pin every harness version. Run each candidate once behind mitmproxy or an egress firewall in local-only mode and record every outbound host. On OpenRouter, top up $10, enable the training opt-out and account-wide ZDR, and turn prompt logging off. Ask CMS computing/publication coordination and CERN IT (LLM proxy status) for a written policy. Start logging your own sessions (Claude Code transcripts, vault-adjacent work) in a common JSONL schema. | **Go** if a local-only run shows zero unexplained egress. **No-go** for that harness otherwise, with no exceptions for CMS work. |
| **1. Baselines before learning** | 2–4 | Write the selector library skeleton. Implement recency + rule PINs + atomic tool pairs, observation masking, DyCP (reimplemented), and LRE (if licensed; otherwise reimplement from the paper). Bring up Qwen3.6-27B Q4 on the V100S under llama.cpp with a held ssh session. Measure tok/s and usable context. | **Go** if the V100S sustains a usable context (target ≥32k) and the best baseline holds task success within 3 points of full history on replayed sessions. Otherwise the sensitive path is not viable on current hardware: pause until the CERN proxy or ml.cern.ch GPU is available. |
| **2. Harness bake-off** | 5–6 | Wire the library into a thin PydanticAI loop and a Hermes `ContextEngine.select_context` plugin. Optionally add the LiteLLM hook in front of Pi or opencode. Run the same 20–30 replayed tasks through each. | **Go with Hermes** if mitm logs confirm the request carries only the selected messages, zero tool-pair 400s over the suite, and no unaudited egress. Otherwise keep the thin loop as the worker. Add ChatGPT Plus only if frontier models pass public tasks the free/V100S models fail. |
| **3. Learned selector** | 7–14 | Generate later-reference labels on all logs. Run 32–64 random-mask ablations per target turn on the V100S open-weights model for a few hundred calibration turns. Train the LR/LightGBM selector with a 4-way head. Run the held-out evaluation with seeds and CIs. | **Go (publish selector)** if it beats the best Phase-1 baseline at equal cache-adjusted cost on held-out coding traces, with pinned-constraint violation no worse than the rule-PIN baseline. **No-go:** publish the labels, dataset and benchmark plus the negative result. That is still a citable artifact. |

Run the orchestrator/worker/reviewer topology from Phase 2 onward as plain Python. The orchestrator writes the state card. Each worker gets `git worktree add` plus a fresh-context harness run. A reviewer with a bounded loop count returns pass/fail. None of the harnesses examined offered first-class worktree orchestration, so you would own this logic anyway.

## Risks worth naming before you start

The largest technical risk is a **null result**. Strong models gain little from pruning, and every history-dropping method loses a few points on agent tasks: LRE is −2.9 on AppWorld, and CWL's differences are "within run-to-run variance" ([CWL](https://arxiv.org/html/2606.11213)). The pre-registered Phase 3 gate turns that risk into a publishable outcome rather than a sunk cost.

The largest operational risk is the **sensitive path's availability**. Your own notes record that lxplus-gpu interactive sessions die at logout and that condor GPU slots are contended. The one route compliant for CMS data is therefore also the least reliable. The CERN LLM proxy, when it launches, is the structural fix.

The **harness churn** risk is universal. Every candidate shipped a release in the week of 2026-10-06. Hermes' breaking-change history and telemetry were not examined. Pin versions in CI and keep integrations to two (LiteLLM, plus one harness plugin).

The **subscription** risks are policy risks. OpenAI's third-party tolerance is not contractual, and Anthropic has already banned the equivalent. Keep paid models optional in the routing table, never load-bearing.

## What was verified, and how

| Claim | Evidence level |
|---|---|
| Letta telemetry on by default; payload includes argv, tool stderr, debug-log tail; posts to api.letta.com in local mode | **Source** (commit `3a958a4`, v0.34.7) |
| Letta hooks/mods cannot rewrite history; usage-anchored compaction misbehaves behind a truncating proxy | **Source** (code paths read, not executed) |
| Letta stalls with small Ollama models; LiteLLM topology death spiral | **Third-party** (GitHub issues #4650, #4962) |
| Hermes `select_context` semantics, `message_uid`, request-only | **Docs** (not source-read, not executed) |
| Pi `context`/`context_with_system` | **Docs in repo** |
| opencode transform hook fragility | **Issue tracker** (maintainer actions verified) |
| Hermes, opencode, Goose telemetry | **Not verified**: audit before CMS use |
| NVIDIA trial terms; OpenRouter limits and ZDR | **Primary legal/docs text** |
| NIM 40 RPM | **Forum reports only** |
| 6 GB / V100S model fit | **Third-party guides plus inference**: no tok/s measured |
| ChatGPT third-party tolerance; Claude subscription ban | **Third-party reporting** |
| API prices (OpenAI, Anthropic) | **Official pricing pages**; DeepSeek/GLM/Kimi via aggregators |
| No existing learned, log-trained selector; no labeled keep/drop dataset | **Search-based absence**: strong but not exhaustive |
| Headroom ~74.7k stars | **Page summary, not API-verified** |

## Conclusion

The question "which harness?" turned out to be the wrong unit of decision. The asset that compounds is the selection layer and its evaluation, and harnesses are interchangeable shells around it. The fact that tips the choice is that only Hermes, Pi and a thin loop expose the one hook your design depends on. Letta Code's memory-first design, superficially the closest match to a "memory-centric" system, is in practice the hardest to bend toward per-turn reconstruction.

Two less obvious alignments emerged. First, the privacy constraint and the fresh-context design reinforce each other: self-hosted models carry no cache billing, so the design's main cost penalty disappears on the path where sensitive work must go anyway. Second, the field's weakest point is unreplicated savings claims. That makes a CMS physicist's habit of pre-registered gates and falsifying controls the project's differentiator, not a side skill. A clean negative result with a released dataset would still be more credible than most of what the 75k-star incumbents publish.
