---
tags: [reference]
status: active
date: 2026-10-08
source: laptop
---

# Free / locally-runnable LLMs for agentic tool calling, and the privacy terms of free endpoints (as of 2026-10-08)

## Nemotron 3 family: release status, availability, agentic benchmarks, tool-call format

### Takeaway
All three Nemotron 3 tiers are out. The real sizes are Nano 30B-A3.5B (Dec 2025), Super 120B-A12B (Mar 2026) and Ultra 550B-A55B (Jun 4 2026), not the ~100B/~500B figures in the brief. NVIDIA's model cards report solid but not frontier agentic scores: Super gets about 60 on SWE-bench with OpenHands, 61 on tau2 and 26 on Terminal-Bench hard. Ultra is free on OpenRouter, but the free route's provider and data policy are not shown on the page. In vLLM, every tier uses the `qwen3_coder` tool-call parser plus a Nemotron-specific reasoning parser.

### Cited Findings
- **Nemotron 3 Nano**: released 2025-12-15 on HF. 30B total / 3.5B active hybrid Mamba-Transformer MoE (128 routed experts + 1 shared, 6 active), context up to 1M (HF default config 256k), NVIDIA Nemotron Open Model License (commercial use OK). — [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
- Nano self-reported benchmarks (Nano / Qwen3-30B-A3B-Thinking-2507 / GPT-OSS-20B): SWE-Bench (OpenHands) 38.8 / 22.0 / 34.0; Terminal Bench hard subset 8.5 / 5.0 / 6.0; tau2 avg 49.0 / 47.7 / 48.7; BFCL v4 53.8 / 46.4 / n.a. — [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
- Nano vLLM serving: `--enable-auto-tool-choice --tool-call-parser qwen3_coder` plus a custom reasoning parser plugin (`--reasoning-parser-plugin nano_v3_reasoning_parser.py --reasoning-parser nano_v3`). — [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
- **Nemotron 3 Super**: released 2026-03-11. 120B total / 12B active, context up to 1M (vLLM/SGLang default 256k, an env var is needed for 1M), Nemotron Open Model License. — [HF model card (FP8)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
- Super benchmarks (FP8 / BF16 / NVFP4): Terminal Bench hard 26.04 / 25.78 / 24.48; tau2 avg 61.07 / 61.15 / 60.46 (FP8 airline 56.25, retail 63.05, telecom 63.93). BFCL is not reported. — [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
- Super SWE-Bench (OpenHands) 60.47 vs Qwen3.5-122B-A10B 66.40 vs GPT-OSS-120B 41.9; SWE-Bench (OpenCode) 59.20; SWE-Bench (Codex) 53.73; SWE-Bench Multilingual (OpenHands) 45.78. NVIDIA notes some SWE runs used the official implementation or an internal scaffold. — [NVIDIA model card mirrored on Docker Hub](https://hub.docker.com/r/ai/nemotron-3-super) (seen via search snippet only; not fetched in full)
- Super serving: vLLM `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser nemotron_v3`. SGLang and TRT-LLM also use the `qwen3_coder` tool parser. — [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
- **Nemotron 3 Ultra**: released 2026-06-04. About 550B total / ~55B active hybrid Mamba-Attention MoE, native NVFP4, 1M context (one source says 262K). — [dev.to article (third party)](https://dev.to/creeta/nemotron-3-ultra-went-live-june-4-heres-the-call-that-works-55g7); [Ollama blog](https://registry.ollama.ai/blog/nemotron-3-ultra); [NVIDIA Ultra Base cookbook](https://docs.nvidia.com/nemotron/nightly/usage-cookbook/Nemotron-3-Ultra-Base/README.html)
- Ultra's Artificial Analysis Intelligence Index is about 48 (47.7 in another report), vs Kimi K2.6 at 54. Vendor claims are a 91% PinchBench score and 60% fewer reasoning tokens. NVIDIA says it is post-trained for the Hermes Agent, LangChain Deep Agents, OpenHands and OpenCode harnesses. I did not find SWE-bench Verified, Terminal-Bench, tau2 or BFCL numbers for Ultra. — [dev.to article (third party, cites Artificial Analysis)](https://dev.to/creeta/nemotron-3-ultra-went-live-june-4-heres-the-call-that-works-55g7)
- The Ultra *Base* checkpoint is not instruction-tuned. NVIDIA says not to use it as an assistant and to use the post-trained release instead. Calling the wrong slug gives incoherent output. — [NVIDIA docs](https://docs.nvidia.com/nemotron/nightly/usage-cookbook/Nemotron-3-Ultra-Base/README.html); [dev.to](https://dev.to/creeta/nemotron-3-ultra-went-live-june-4-heres-the-call-that-works-55g7)
- Ultra on NIM: base URL `https://integrate.api.nvidia.com/v1`, with reasoning toggled by `chat_template_kwargs: {enable_thinking: true/false}`. Reasoning arrives in `reasoning_content`. Suggested sampling is temperature 1.0 and top_p 0.95 (borrowed from the Super card). The article's model ID `nvidia/nemotron-3-ultra` is labelled "illustrative". — [dev.to](https://dev.to/creeta/nemotron-3-ultra-went-live-june-4-heres-the-call-that-works-55g7)
- OpenRouter lists **"NVIDIA: Nemotron 3 Ultra (free)"** as `nvidia/nemotron-3-ultra-550b-a55b:free`, with `tools`/`tool_choice` accepted. The page does not name the provider, give a context length, show a data policy or give a promo end date. — [OpenRouter model page](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free)
- Ultra NVFP4 checkpoint is about 352 GB, so it cannot be self-hosted on the user's hardware. — [search summary of a third-party review](https://www.forgenex.com/en/blog/nemotron-3-ultra-ya-est-disponible-el-modelo-de-nvidia-que-transforma-la-ia-empresarial) (aggregator)
- build.nvidia.com also lists an `nvidia/nemotron-3.5-lightning-30b-a3b` model. It is a newer Nano-class model; no details were gathered. — [build.nvidia.com](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/playground)

### Inferences
- The `qwen3_coder` parser is an XML-style tool-call format. Harnesses that call a *self-hosted* Nemotron 3 need the server-side parser set correctly, or tool calls come back as raw text in `content`. On NIM/OpenRouter the provider does the parsing, so this should not come up.
- Interleaved reasoning (`reasoning_content`) can be a problem with harnesses that resend history: if they drop or mangle reasoning fields, multi-turn quality may drop. This is not documented for Letta specifically; test it.
- Ranking for agentic use from model-card numbers: Ultra > Super >> Nano. Super's ~60 on SWE-bench (OpenHands) is below Qwen3.5-122B-A10B (66.4) on NVIDIA's own table.

### Gaps
- No primary Ultra benchmark table (SWE-bench Verified, Terminal-Bench 2.0, tau2, BFCL) was found. I did not reach the HF Ultra card or an NVIDIA blog post.
- **Nemotron Nano 9B v2**: not researched in this pass (out of tool budget). It predates Nemotron 3 (Aug 2025) and is likely superseded by Nemotron 3 Nano / 3.5 Lightning.
- I did not confirm whether Nemotron 3 Super/Ultra are in the build.nvidia.com free trial catalog under exact IDs. Check `GET https://integrate.api.nvidia.com/v1/models`.
- I found no reported harness-specific Nemotron 3 tool-call bugs, and the absence of reports is not proof of reliability.

## Other strong free/open models for agentic coding in late 2026

### Takeaway
Among open-weight models, the September 2026 leaders on Terminal-Bench 2.0 are DeepSeek V4 Pro and Qwen3.6 (27B dense and 35B-A3B). Kimi K2.6 scores above Nemotron 3 Ultra on Artificial Analysis. I could not check which of these are currently free on NIM or OpenRouter. The user should list live free models from the API.

### Cited Findings
- Terminal-Bench 2.0 open-weight entries (BenchLM aggregator, updated 2026-09-15): DeepSeek V4 Pro (High) 63.3%, Qwen3.6-27B 59.3%, DeepSeek V4 Pro 59.1%, Qwen3.6-35B-A3B 51.5%. The overall leader is GPT-5.6 Sol at 91.9%. **Third-party aggregator**: it mixes harnesses and snapshots, and another aggregator dated 2026-09-09 lists a different leader. — [BenchLM Terminal-Bench 2](https://www.benchlm.ai/benchmarks/terminal-bench-2)
- Harness engineering alone can move Terminal-Bench scores by 20+ points for the same model. — [search summary of an aggregator analysis](https://www.codesota.com/benchmark/terminal-bench) (third party)
- Kimi K2.6 scores 54 on the Artificial Analysis Intelligence Index vs Nemotron 3 Ultra at 48. — [dev.to citing Artificial Analysis](https://dev.to/creeta/nemotron-3-ultra-went-live-june-4-heres-the-call-that-works-55g7)
- Qwen3.5-122B-A10B scores 66.40 on SWE-Bench (OpenHands), per NVIDIA's own comparison. GPT-OSS-120B scores 41.9 on the same table. — [Nemotron 3 Super card on Docker Hub](https://hub.docker.com/r/ai/nemotron-3-super)
- There is a known open Qwen3.5 tool-call parser issue affecting qwen3.5:9b in local runtimes (Sept 2026 guide). — [insiderllm guide (third party)](https://insiderllm.com/guides/best-local-coding-models-2026/)

### Inferences
- For an agent harness, the safest free candidates are models with first-party-documented tool parsers (Qwen3.x/Qwen3-coder, Nemotron 3, DeepSeek V4, Kimi K2.x, GLM). Check which are live with `curl -H "Authorization: Bearer $NVIDIA_API_KEY" https://integrate.api.nvidia.com/v1/models` and with the OpenRouter `/models` page filtered to free models with tools.

### Gaps
- I did not establish which of DeepSeek V4, Qwen3.6, GLM-5.x, Kimi K2.6, MiniMax M-series or gpt-oss are free on NIM or OpenRouter today. A WebFetch of the OpenRouter filtered list returned no `:free` entries, and the page was likely rendered client-side.
- I did not fetch BFCL v4 or the official tbench.ai leaderboard directly. SWE-bench Verified numbers for these models are not gathered.

## What runs on 6 GB VRAM + 15 GB RAM laptop, and on a V100S 32 GB

### Takeaway
On a 6 GB RTX 4050, only ~3–4B models run fully on the GPU, for example qwen3.5:4b (3.4 GB) or granite4.1:3b. They can call tools but are weak agents. Usable context is the real constraint. A V100S 32 GB can host a mid-size coding model (Qwen3.6-27B or Nemotron 3 Nano at 4-bit). It is Volta (SM 7.0): no FP8/NVFP4, no FlashAttention, and CUDA 13 dropped Volta, so pin a CUDA-12.x vLLM build or use llama.cpp/Ollama GGUF.

### Cited Findings
- qwen3.5:4b (3.4 GB in the Ollama library) is called the best Ollama model for 6 GB VRAM in 2026. It supports tool calling and thinking, and leaves about 2 GB for context. It was tested on RTX 4050 laptop and similar cards. Alternatives: phi4-mini (2.5 GB), granite4.1:3b (2.1 GB, Apache-2.0, tool calling, 128K listed), llama3.2:3b, qwen2.5-coder:3b, gemma4:e2b-it-qat (4.3 GB). **Third-party guide.** — [localaimaster 6GB guide](https://localaimaster.com/vram/best-ollama-models-6gb-vram)
- "The trap on a 6GB card is not the weights, it is the context window." Agent tools need Ollama `num_ctx` ≥ 64k, which will not fit alongside the weights on 6 GB. — [localaimaster](https://localaimaster.com/vram/best-ollama-models-6gb-vram); [Tembo guide](https://www.tembo.io/blog/best-local-llm-for-coding) (third party)
- qwen3.5:9b is 6.6 GB, aimed at an 8 GB tier, and has an open tool-call parser issue. — [insiderllm](https://insiderllm.com/guides/best-local-coding-models-2026/) (third party)
- Anecdote: someone ran Qwen3.6-35B-A3B mostly from system RAM on a 6 GB card with 48 GB RAM and called the speed usable. — [Reddit snapshot](https://reddit.sentinel-team.org/posts/1w0vui9/snapshots/2026-09-04T21%3A20%3A12.3645Z) (anecdotal)
- vLLM requires compute capability ≥ 7.0 (V100 included), per the v0.8.3 docs. Upstream AWQ kernels need SM75+. The community fork 1Cat-vLLM claims AWQ Qwen3.5/3.6 MoE on 4×V100 32GB. CUDA 13.0 removed Volta, and 12.9.1 is the last version that supports it. FlashAttention does not support Volta. — [vLLM docs v0.8.3](https://docs.vllm.ai/en/v0.8.3/getting_started/installation/gpu.html); [1Cat-vLLM](https://www.sourcepulse.org/projects/29732850); [groundy blog](https://groundy.com/articles/putting-a-datacenter-v100-in-a-gaming-pc-the-local-llm-math) (third party)

### Inferences
- With 15 GB RAM + 6 GB VRAM (~21 GB total, minus the OS), a 30–35B-A3B MoE at Q4 (~18–20 GB of weights) would barely load and leave almost no room for KV cache. This applies to Nemotron 3 Nano and Qwen3.6-35B-A3B. Treat it as not viable. The user's 23 GB qwen3.6 likewise will not fit.
- The laptop is best used for embeddings (bge-m3, already in use) and maybe a small 3–4B model for trivial, private sub-tasks. It should not be the main agent driver.
- On a V100S 32 GB, inferred options are Qwen3.6-27B at 4-bit (~16–17 GB) or Nemotron 3 Nano / Qwen3.6-35B-A3B at Q4 GGUF (~18–20 GB). Either leaves ~10 GB for KV cache, enough for roughly 32–64k context. Use llama.cpp/Ollama (GGUF works on SM70) or a CUDA-12.x vLLM with GPTQ, not AWQ/FP8. Memory notes say lxplus-gpu interactive sessions die at logout and condor GPU slots are contended, so a persistent server needs a held ssh session.
- I have no measured tok/s for either setup. Expect roughly 20–40 tok/s for a 3B-active MoE on V100S, but this is an estimate, not a sourced number.

### Gaps
- No primary benchmark of tok/s or agentic success for these quantized models on RTX 4050 or V100S.
- I did not verify current upstream vLLM (late 2026) support for SM70 or for Nemotron-H Mamba kernels on Volta.

## Exact rate limits and data terms: NVIDIA API catalog trial and OpenRouter free

### Takeaway
**NVIDIA's trial terms rule out the user's use case.** They limit use to trial/evaluation ("not in production") and forbid submitting "any confidential information". Section 3.3 lets NVIDIA collect User Content and Generated Content "to improve NVIDIA products and services, including AI models". **OpenRouter's** free tier is 20 RPM and 50/day (1,000/day after a $10 lifetime top-up). Free endpoints commonly log prompts or train on them, depending on the provider. Neither is acceptable for unpublished CMS results.

### Cited Findings
- **NVIDIA API Trial ToS** (PDF metadata date 2025-10-07):
  - §1.2: "access to the API Service for limited trial purposes only and without use of the API Service or Generated Content in production."
  - §1.4: without a paid Subscription "you may only use the API Service for internal testing and evaluation purposes, not in production."
  - §2.3: NVIDIA "will not store or use User Content or Generated Content at the end of each API Service session" except per §2.4/§3.3.
  - **§2.6(a)**: you agree not to "include any confidential information, controlled or sensitive data …".
  - §2.7: NVIDIA "may … block, monitor, scan or review communications or User Content".
  - **§3.3**: NVIDIA will collect, "without identifying specific users … (iv) User Content and Generated Content to improve NVIDIA products and services, including AI models. Your use of the API Services will be logged for security, fraud or abuse monitoring and shared with third party service providers for this purpose."
  - Source: [NVIDIA API Trial Terms of Service PDF](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) (linked by NVIDIA staff in [forum thread](https://forums.developer.nvidia.com/t/clarification-on-trial-api-use/334275))
- Note that §2.3 ("will not store … at end of session") and §3.3(iv) ("collect … User Content … to improve … AI models") are in tension. Forum users asked NVIDIA staff to clarify in May–June 2025 and got no answer in the thread. — [NVIDIA forum](https://forums.developer.nvidia.com/t/clarification-on-trial-api-use/334275)
- **NIM free rate limit: 40 RPM.** This figure comes only from many user forum threads asking to go from 40 to 200 RPM. Moderator replies, reposted by users, say the limit varies by model and traffic and that there is no official way to raise it on the free tier. I found no official NVIDIA page stating 40 RPM. — e.g. [forum thread](https://forums.developer.nvidia.com/t/request-for-nvidia-nim-api-rate-limit-increase-40-200-rpm-agentic-development-workflow/378941), [forum thread](https://forums.developer.nvidia.com/t/rpm-increase-request-40-rpm-200-rpm/376235)
- **OpenRouter free limits** (official): model IDs ending `:free` get 20 RPM. Per day: 50 if fewer than 10 credits purchased all-time, 1,000 if at least 10. The higher ceiling is "currently" granted from 9 credits. The daily counter resets on the UTC day. BYOK requests are not gated by the daily counter. — [OpenRouter limits docs](https://openrouter.ai/docs/api-reference/limits)
- Third-party claim: limits are per account across all keys. — [fast.io](https://fast.io/resources/openrouter-rate-limit/) (third party)
- **OpenRouter data policy**:
  - Each provider has its own retention and training policy.
  - "If you opt out of training in your account settings, OpenRouter will not route to providers that train"; "There are separate settings for paid and free models"; the setting "has no bearing on OpenRouter's own policies".
  - Requests can be restricted to providers with a given data policy (provider routing `data_collection: "deny"`, ZDR endpoints).
  - Source: [OpenRouter provider logging docs](https://openrouter.ai/docs/guides/privacy/provider-logging)
- OpenRouter itself stores prompts only if the user opts into prompt logging, and otherwise keeps metadata (tokens, latency). — [OpenRouter logging docs](https://openrouter.ai/docs/guides/privacy/logging) (via search summary)
- Third-party tutorials say free models typically log prompts and outputs at the provider to improve models, and advise against confidential data. — [lilting.ch](https://lilting.ch/en/articles/openrouter-free-models); [rajeevpentyala blog](https://rajeevpentyala.com/2026/05/21/openrouter-pick-a-free-ai-model-and-build-a-react-chat-app/) (third party)

### Inferences
- **Request budget:** at 5–15 calls per user message, OpenRouter's 50/day allows only about 3–10 user turns per day. 1,000/day after $10 allows about 65–200 turns. 20 RPM allows 1–4 turns per minute. NIM at ~40 RPM is roughly 2× more headroom per minute with no stated daily cap, but the terms say evaluation-only.
- If the training opt-out (free-model setting) is set, OpenRouter may refuse to route some `:free` models whose only provider trains on data, and the request fails. This means many promo free models are likely unusable with a strict privacy posture. This is inferred, not verified for Nemotron 3 Ultra :free.
- Practical rule: free cloud endpoints are fine for public code, public papers and generic tooling. Prompts that contain unpublished yields, limits, card contents or AN text should go only to self-hosted models (V100S/laptop) or a CERN-approved service.

### Gaps
- I did not see the specific data policy (provider, retention, training) for `nvidia/nemotron-3-ultra-550b-a55b:free`; the page did not show it. The user should check the model's "Providers" tab or call `/api/v1/models/.../endpoints`.
- No official NVIDIA document states the 40 RPM figure or any daily or credit cap for current free API keys.

## CERN-approved LLM service and CMS policy on external AI

### Takeaway
I found no production, CERN-approved general LLM API as of October 2026. CERN IT presented a *planned* central LLM/agentic platform in April 2026: an OpenAI-compatible LLM proxy, a catalog of on-prem and cloud models, and agent hosting. The ml.cern.ch Kubeflow platform (default quota of 1 GPU per personal profile) is a current way to self-host. I found no public CMS policy text on external AI with internal results.

### Cited Findings
- April 2026 talk "A Centralized LLM and Agentic AI Infrastructure for CERN" (J. M. Guijarro): a new ML service with an LLM Proxy compatible with OpenAI APIs, a Model Catalog of on-premises and cloud models, and an Agent Hosting and Orchestration platform, framed as planned. — [Indico abstract](https://indico.cern.ch/event/1598655/contributions/7005586)
- A 2026 CERN job posting for an ML engineer to build "CERN's next-generation LLM and AI agent platform" suggests the platform is still being built. — [CERN careers](https://careers.cern/?p=34016)
- ml.cern.ch is Kubeflow-based. The July 2026 MLOps slides list NVIDIA/AMD GPU flavors and personal profiles with a default quota of 1 GPU. — [MLOps@CERN slides](https://indico.cern.ch/event/1678348/contributions/7063051/attachments/3313827/5932014/MLOps%20Service@CERN.pdf)
- AccGPT is a pilot chatbot over CERN internal knowledge (BE + IT), with the goal of wider availability. — [Indico](https://indico.cern.ch/event/1543967/contributions/6534764)
- A CERN-wide AI statement was being discussed, and its rollout was "next step". Its contents are not visible. — [Indico meeting note](https://indico.cern.ch/event/1426918/note/)

### Inferences
- Until the CERN LLM proxy is GA, the compliant route for sensitive content is self-hosting on CERN resources (lxplus-gpu V100S, ml.cern.ch GPU, condor GPU). If the proxy launches with on-prem models, it would likely become the preferred backend, since it is OpenAI-compatible and works with any harness.
- **Routing recommendation (synthesis):**
  1. Sensitive/analysis-context calls go to a self-hosted model on CERN GPU, e.g. Qwen3.6-27B or Nemotron 3 Nano at Q4 via Ollama/llama.cpp on lxplus-gpu, exposed only over an ssh tunnel.
  2. Public, non-sensitive heavy reasoning (generic coding, public docs) goes to OpenRouter free (Nemotron 3 Ultra :free or similar) with training opt-out set, or to NIM, accepting the evaluation-only terms.
  3. Embeddings stay local (bge-m3).
  4. Keep calls per message low; free tiers cannot sustain 15-call loops at volume.

### Gaps
- I found no CMS-collaboration policy document on external AI and internal results. It is likely internal (CMS TWiki/CADI/Publication Committee guidelines) and not web-searchable. The user should ask CMS Publication/Comp coordination or check internal pages.
- CERN Computer Security guidance on gen-AI (whether one exists, and its text) was not found in this pass.
- Launch status, model list and access policy of the CERN LLM proxy are unknown, because the talk slides were not posted.
