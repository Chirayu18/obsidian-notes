---
tags: [reference]
status: active
date: 2026-10-08
---

# Paid AI subscriptions vs pay-as-you-go APIs for a vendor-independent agent harness (as of 2026-10-08)

Scope: whether a paid plan or API is needed (vs free NIM / OpenRouter :free / local Ollama), which paid option is best value for a Letta Code / opencode / Pi + LiteLLM multi-agent loop (5–15 LLM calls per user message, ~50–100 user messages/day), with data retention and training on unpublished CMS results as a hard constraint.

Note on model names: by October 2026 OpenAI's current API line is GPT-6.x ("Sol", "Luna", "Astra") and Anthropic's is Claude 5.5 / Fable 5.1. Several third-party aggregators still quote GPT-5.5 / Sonnet 4.6 figures. The official pricing pages fetched on 2026-10-08 are used below wherever they were available.

## 1. Consumer and coding subscriptions usable inside third-party / open-source harnesses

### Takeaway
ChatGPT (Plus $20 / Pro $100–500) is the only big-lab subscription that OpenAI publicly endorses for third-party harnesses: OpenCode and Pi are about 10% of Codex traffic, and there is a "Sign in with ChatGPT" flow. Letta Code supports it natively. Claude Pro/Max is **banned** outside Claude Code and claude.ai, and Gemini subscriptions no longer serve Gemini CLI. The Chinese coding plans (Z.ai GLM, Kimi, MiniMax) are cheap and harness-friendly, but their data terms were not verified and they are a poor fit for unpublished physics.

### Cited Findings
**ChatGPT / Codex (OpenAI)**
- Codex is included in ChatGPT Free, Go ($8), Plus ($20), Pro (from $100; $100 / $200 / $500 tiers) and Business ($20/user/mo billed annually for 2+ users, $25 billed monthly). Edu and Enterprise are also included. — [ChatGPT/Codex pricing (learn.chatgpt.com, fetched 2026-10-08)](https://learn.chatgpt.com/docs/pricing)
- Plus usage, as local messages per 5 hours by model: GPT-6 Astra 5–45; GPT-6.1 Sol 15–160; GPT-6 Sol 15–150; GPT-6 Luna 350–3,000. "Weekly limits may also apply." Pro: "no five-hour limit currently." Plus and Pro users can buy extra credits (e.g. GPT-6.1 Sol = 50 credits/M input, 250/M output). — [ChatGPT/Codex pricing](https://learn.chatgpt.com/docs/pricing)
- OpenAI exec Tibo Sottiaux said "you can use your ChatGPT account in a flourishing set of other tools," and that Pi and OpenCode are about 10% of Codex traffic. OpenAI shipped "Sign in with ChatGPT" for subscription users (docs at developers.openai.com/codex/auth). The OpenAI ToS neither explicitly permits nor prohibits this, and OpenAI reserves the right to terminate for "economic harm". The author calls it "tolerated rather than committed". — [Manifest blog, 2026-07-01 (third-party)](https://manifest.build/blog/chatgpt-plus-tokens-third-party-harnesses/)
- OpenAI estimates that the $20 Plus plan is worth roughly $100–200 in tokens. — [Manifest (third-party, quoting OpenAI)](https://manifest.build/blog/chatgpt-plus-tokens-third-party-harnesses/)
- A Sept 2026 report says OpenAI formalised "Sign in with ChatGPT" for third-party tools with 16 launch partners (Amp, Devin, Lovable, OpenClaw named). Whether OpenCode is one of them was not confirmed. — [search summary of third-party coverage; e.g. Zed blog](https://zed.dev/blog/chatgpt-subscription-in-zed)
- Zed also supports using a ChatGPT subscription. — [Zed blog](https://zed.dev/blog/chatgpt-subscription-in-zed)
- Letta Code docs: "use your existing API keys and coding plans (like the ChatGPT/Codex and zAI coding plans)" via `/connect`. Local mode needs no Letta login. With BYOK or a plan connected, usage goes directly through the provider and does not consume Letta credits. — [Letta Code quickstart](https://docs.letta.com/letta-code/quickstart/index.md); [Letta Code pricing](https://docs.letta.com/letta-code/pricing); [Letta providers](https://docs.letta.com/letta-code/providers)
- **Data:** on personal plans (incl. Plus/Pro) ChatGPT and Codex content *may be used for training by default*. You can opt out via Settings → Data Controls → "Improve the model for everyone", or via the privacy portal. **Codex has a separate "full environments" training setting that the ChatGPT toggle does not cover.** Thumbs-up/down feedback can put the whole conversation into training even after opt-out. Business, Enterprise and the API are *not* trained on by default. — [OpenAI Help: how your data is used](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance)

**Claude Pro/Max (Anthropic)**
- Pro is $20/mo ($17/mo annual) and Max starts at $100/mo (5x and 20x tiers). — [claude.com/pricing (fetched 2026-10-08)](https://claude.com/pricing)
- From 2026-01-09 Anthropic blocked subscription OAuth tokens server-side outside Claude Code and claude.ai. On ~2026-02-19/20 the terms/docs were updated to ban Free/Pro/Max OAuth tokens in any other product, including the Agent SDK, and to bar third parties from offering Claude.ai login. Account bans were reported. — [AlternativeTo news, Feb 2026 (third-party)](https://alternativeto.net/news/2026/2/anthropic-officially-bans-using-subscription-authentication-for-third-party-claude-use); [falcao.org ecosystem write-up (third-party)](https://falcao.org/posts/anthropic-claude-access-crackdown-ecosystem-fallout/)
- An OpenCode maintainer commit reportedly removed Claude OAuth after a legal request from Anthropic (screenshot-sourced, least verified). — [falcao.org (third-party)](https://falcao.org/posts/anthropic-claude-access-crackdown-ecosystem-fallout/)

**GitHub Copilot**
- Pro is $10/mo and Pro+ $39/mo. Since June 2026, premium requests have been replaced by usage-based "AI Credits". Legacy annual subscribers keep 300 (Pro) / 1,500 (Pro+) premium requests at $0.04 per overage request. One report says Pro+ includes about $70 of credits (unverified against GitHub). One source says new individual sign-ups were *paused* during the billing rollout. — [GitHub docs: premium requests](https://docs.github.com/en/billing/concepts/product-billing/github-copilot-premium-requests); [morphllm comparison (third-party)](https://www.morphllm.com/comparisons/github-copilot-vs-claude-code); [tech-insider (third-party)](https://tech-insider.org/au/github-copilot-usage-based-billing-2026/)

**Google Gemini**
- At I/O (2026-05-19) Google announced that from 2026-06-18 Gemini CLI stops serving free, Google AI Pro and Ultra users, who are redirected to the closed-source Antigravity CLI. Code Assist Standard/Enterprise keep CLI access. AI Pro moved to compute-based limits on 2026-05-20, refreshing every 5 h up to a weekly cap. — [search summary citing Google announcement; dev.to (third-party)](https://dev.to/owen_fox/gemini-cli-free-tier-shut-down-6-fixes-that-work-2026-26hc); [Android Authority](https://www.androidauthority.com/google-ai-pro-limits-tested-3674942/)
- Gemini API free tier: content "used to improve our products: Yes". Paid tier: "No". — [Google AI pricing](https://ai.google.dev/pricing?hl=fi); [Gemini billing docs](https://ai.google.dev/gemini-api/docs/billing?authuser=1)

**Z.ai GLM Coding Plan**
- Lite / Pro / Max are about $18 / $72 / $160 per month (30% promo through Sept 2026), with roughly 80 / 400 / 1,600 prompts per 5 h and about 400 / 2,000 / 8,000 per week. One "prompt" is one user query that may invoke the model 15–20 times. GLM-5.2 consumes 3x quota at peak (14:00–18:00 UTC+8) and 2x off-peak. There is no overage billing. Sources conflict: one lists Pro at $80 and Max at $168. — [layer3labs (third-party, Jul 2026)](https://www.layer3labs.io/guides/z-ai-pricing); [hyscaler review (third-party)](https://hyscaler.com/insights/glm-coding-plan-review); [aipricing.guru (third-party)](https://www.aipricing.guru/z-ai-subscription-pricing/)

**Kimi (Moonshot) and MiniMax**
- Kimi: Moderato $19, Allegretto $39 (~5x), Allegro $99 (~15x), Vivace $199 (~30x), drawn from a shared credit pool. Sources disagree on whether there is a 5-hour window. — [codeagentswarm guide, Jul 2026 (third-party)](https://www.codeagentswarm.com/en/guides/kimi-code-plans-and-pricing); [codepick comparison (third-party)](https://codepick.dev/en/compare/coding-plan-comparison-2026/)
- MiniMax: Starter $10, Plus $20, Max $50 per month, with request caps per 5 h. Prices conflict with RMB listings. — [codepick MiniMax vs GLM (third-party)](https://codepick.dev/en/compare/minimax-coding-plan-vs-glm-coding-plan/)

### Inferences
- **For the user's design, ChatGPT Plus ($20) has the best $/token among plans that can be used legitimately in a third-party harness.** OpenAI values it at 5–10x its price in tokens, and it is supported natively in Letta Code and opencode. The risk is that the arrangement is not contractual and could be throttled.
- A multi-agent loop burns quota fast. On Plus, the GPT-6.1 Sol limit of 15–160 messages per 5 h may be hit within a few user turns if every subagent call counts. That makes it sensible to route cheap calls (classifier, summariser, memory ops) to an API model like gpt-6-luna and keep the subscription for the main reasoning calls.
- **For unpublished CMS results, a consumer Plus/Pro account is acceptable only with training switched off in both places (ChatGPT Data Controls and the Codex full-environment setting) and feedback buttons avoided.** Even then, consumer terms give no ZDR. ChatGPT Business ($25/mo monthly) is no-training by default and is the safer subscription.
- Claude via a third-party harness is only legitimate through the **API** (pay-per-token), not Pro/Max.
- The Chinese coding plans are the cheapest raw quota, but they should be limited to non-sensitive or public-code work until their data terms are checked (see Gaps).

### Gaps
- Whether "Sign in with ChatGPT" in third-party harnesses works for **Business/Edu** workspaces (which have no-training defaults), or only Plus/Pro. Not found.
- How a harness's 5–15 sub-calls map onto Codex's "local messages" quota (per model call vs per user turn). Not documented on the pricing page.
- Mistral (Le Chat Pro / Mistral Vibe) price, harness usage and data terms: not researched in this pass.
- Z.ai / Kimi / MiniMax privacy policies (training on prompts, data location) were not fetched, so their training defaults are **unknown**.
- Exact Copilot Pro+ AI-credit amount, and whether opencode's Copilot login is ToS-sanctioned: unverified.

## 2. Pay-as-you-go API prices and estimated monthly cost

### Takeaway
At the user's volume, a flagship-class API model ($2/$10 per M tokens: gpt-6.1-sol, Sonnet 5.5) costs roughly **$165–2,600/month uncached**. A mini model (gpt-6-luna, Haiku 5.5, DeepSeek V4 Flash) costs **$8–160/month**. A tiered LiteLLM routing (cheap model for most sub-calls, flagship for the main turn) plus prefix caching should land around **$50–300/month**.

### Cited Findings
- **OpenAI API (official, 2026-10-08), per 1M tokens, ≤272K context:** gpt-6-astra $10 in / $1.00 cached / $50 out; gpt-6.1-sol $2 / $0.10 / $10; gpt-6-sol $2 / $0.20 / $10; gpt-6-luna (mini) $0.10 / $0.01 / $0.50; gpt-5.6-sol $4 / $0.40 / $20; gpt-5.6-luna $0.20 / $0.02 / $1.20; gpt-5.5 $5 / $0.50 / $30; gpt-5.4-mini $0.75 / $0.075 / $4.50. Regional-processing (data-residency) endpoints carry a +10% uplift for models released on or after 2026-03-05. — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- **Anthropic API (official, 2026-10-08), per 1M tokens:** Fable 5.1 $10 in / $50 out (cache write $12.50, read $0.25); Opus 5.5 $4 / $20 ($5 / $0.20); Sonnet 5.5 $2 / $10 ($2.50 / $0.10); Haiku 5.5 $0.10 / $0.50 for prompts ≤100K ($0.50 / $2.50 above 100K). Cache prices are for the 5-minute TTL. — [claude.com/pricing](https://claude.com/pricing)
- **Google:** Gemini 3.1 Pro $2 / $12 (≤200K), $4 / $18 (>200K). Gemini 3.5 Flash is listed at $1.50 / $9 by one aggregator, and "Flash-Lite" at $0.30 / $2.50 by another (conflicting). — [benchlm (third-party, Oct 2026)](https://benchlm.ai/llm-pricing); [morphllm (third-party)](https://www.morphllm.com/llm-api)
- **DeepSeek:** V4-Flash $0.14 / $0.28, cache hit $0.0028/M; V4-Pro $0.435 / $0.87 (promo made permanent, per one source). — [spheron (third-party)](https://www.spheron.network/blog/llm-api-pricing-comparison-gpt-claude-gemini-deepseek-2026/); [finout (third-party)](https://www.finout.io/blog/llm-token-cost-by-model-2026-pricing-data-and-optimization-tips)
- **Open-weight models via hosts:** GLM-5.2 $1.40 / $4.40 (Zhipu / SiliconFlow), or $0.90 / $2.86 via OpenRouter. Kimi K2.6 $0.95 / $4; Kimi K3 $3 / $15. — [benchlm](https://benchlm.ai/llm-pricing); [morphllm](https://www.morphllm.com/llm-api) (both third-party)
- Aggregators conflict on several model names and prices (e.g. Sonnet 5 at $3/$15 vs $2/$10). — [search summary of finout / morphllm / benchlm](https://benchlm.ai/llm-pricing)

**Cost model (my assumptions, 22 working days/month, no caching):**

| Scenario | Calls/day | Input tok/call | Output tok/call | Input/month | Output/month |
|---|---|---|---|---|---|
| Low | 50 msgs × 5 = 250 | 10k | 1k | 55M | 5.5M |
| Mid | 75 msgs × 10 = 750 | 20k | 1.5k | 330M | 24.75M |
| High | 100 msgs × 15 = 1,500 | 30k | 2k | 990M | 66M |

Monthly cost in USD, uncached, computed from the prices above:

| Model ($in / $out per M) | Low | Mid | High |
|---|---|---|---|
| gpt-5.5 ($5 / $30) | 440 | 2,390 | 6,930 |
| Opus 5.5 ($4 / $20) | 330 | 1,815 | 5,280 |
| Gemini 3.1 Pro ($2 / $12) | 176 | 957 | 2,772 |
| gpt-6.1-sol or Sonnet 5.5 ($2 / $10) | 165 | 908 | 2,640 |
| GLM-5.2 direct ($1.40 / $4.40) | 101 | 571 | 1,676 |
| Kimi K2.6 ($0.95 / $4) | 74 | 413 | 1,205 |
| DeepSeek V4-Pro ($0.435 / $0.87) | 29 | 165 | 488 |
| DeepSeek V4-Flash ($0.14 / $0.28) | 9 | 53 | 157 |
| gpt-6-luna or Haiku 5.5 ($0.10 / $0.50) | 8 | 45 | 132 |

### Inferences
- Input tokens dominate cost (about 70% at these ratios). **The "fresh rewritten context per turn" design is therefore the biggest cost lever, and it fights prompt caching.**
  - Caching works only on an identical *prefix*. OpenAI caches automatically with no write fee (cached input is 1/10–1/20 of the price). Anthropic charges 1.25x to write and 0.1x to read, with a 5-minute TTL.
  - Keep a byte-stable prefix (system prompt → tool schemas → slow-changing memory blocks) and put the classifier-rewritten material **last**. Then 30–60% of input could be cache hits, cutting the input bill by roughly 25–55%.
  - If the LiteLLM classifier reorders or rewrites the head of the prompt every turn, caching is close to zero.
- A sensible tiered mix: flagship ($2/$10) for the 1–2 "planner/answer" calls per user message, and a $0.10/$0.50 model for the rest. At the Mid scenario this gives roughly 0.2 × $908 + 0.8 × $45 ≈ **$220/month** before caching, about $130–170 with prefix caching (estimate).
- On ChatGPT Plus, $20 versus $165–900 of equivalent API usage makes the subscription far cheaper *if* the quota holds and the data terms are acceptable. Pro $100–200 removes the 5-hour cap.

### Gaps
- Groq / Cerebras / Together / Fireworks current prices and their data terms were not fetched in this pass.
- No official Google pricing page was fetched for Gemini 3.x; the Gemini figures above are aggregator-only.
- DeepSeek and Kimi prices come from aggregators, not the official pages.
- Real per-call token counts for Letta Code (memory blocks + tool schemas) were not measured. The scenario numbers are assumptions.

## 3. Data policy: no-training / ZDR / EU residency / CERN institutional route

### Takeaway
All big-lab **APIs** (OpenAI, Anthropic, Google paid tier) default to *no training*. Consumer plans (ChatGPT Plus/Pro, Gemini free) default to *training on*. OpenRouter can enforce ZDR-only routing. CERN is building an internal LLM proxy (OpenAI-compatible, on-prem + cloud catalog), but no live production service or CERN–Azure OpenAI agreement was found.

### Cited Findings
- **OpenAI:** no training by default for Business, Enterprise and the API. Personal plans are trained on unless opted out, and Codex has its own full-environment toggle. — [OpenAI Help](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance)
- **OpenAI** offers regional-processing (data-residency) endpoints at a +10% price. The pricing page does not mention ZDR (ZDR is typically an approved-account arrangement; not verified here). — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- **Google Gemini API:** free tier is "used to improve our products"; paid tier is not. A third-party blog says the free tier cannot serve EU/EEA/UK/CH users (secondary). — [Google AI pricing](https://ai.google.dev/pricing?hl=fi); [wetheflywheel (third-party)](https://wetheflywheel.com/en/ai-model-access/free-gemini-api/)
- **OpenRouter ZDR:**
  - ZDR routing can be enforced per account, per model group, per guardrail, or per request (`provider.zdr: true`).
  - Under ZDR, providers neither retain nor train. Endpoints with an unclear policy are assumed to retain and train.
  - In-memory prompt caching is *not* counted as retention, so caching still works under ZDR.
  - OpenRouter itself doesn't retain prompts unless you opt in to logging.
  - ZDR does **not** cover plugins/tools such as web search.
  - The list of ZDR endpoints is available via API.
  
  — [OpenRouter ZDR docs](https://openrouter.ai/docs/features/zdr); [OpenRouter ZDR blog](https://openrouter.ai/blog/insights/zero-data-retention/)
- **CERN:** a HEPiX Spring 2026 talk (J. M. Guijarro, R. Rocha, 24 Apr 2026) describes a new CERN IT ML service for LLMs and agentic AI with an **LLM Proxy compatible with OpenAI APIs**, a Model Catalog of on-prem and cloud models, and agent hosting/orchestration. It is "in development". The abstract does not name the models or give a data policy. — [Indico HEPiX 2026 contribution](https://indico.cern.ch/event/1598655/contributions/7005586)
- **CERN AccGPT:** an internal-knowledge RAG chatbot pilot (BE + IT), with a prototype deployed and community-wide testing being prepared. — [Indico AccGPT](https://indico.cern.ch/event/1543967/contributions/6534764); [EPJ Conf. CHEP 2024 paper](https://www.epj-conferences.org/10.1051/epjconf/202533701279)

### Inferences
- **Free routes that are not safe for unpublished CMS results:** NIM free tier, OpenRouter `:free` models and the Gemini free tier. These typically log or train; Gemini free is confirmed to train, and the others are unverified here. Local Ollama is the only free route that is safe for such data.
- **Compliant-ish paid routes:**
  - (a) A big-lab API (no training by default).
  - (b) OpenRouter with account-level ZDR enforced and prompt logging off. This is also the most vendor-independent option, since one key spans every model and the ZDR filter is applied centrally.
  - (c) When available, CERN's internal LLM proxy. Because it is OpenAI-compatible, it would slot straight into LiteLLM. **Ask CERN IT (ServiceNow / Mattermost ML channel) about its status before paying for anything for sensitive work.**
- Collaboration rules are separate from vendor terms: CMS publication policy may forbid sending unblessed results to *any* external service regardless of ZDR. Check with CMS before sending anything (not researched).

### Gaps
- No evidence was found of a CERN-wide Microsoft / Azure OpenAI or other vendor agreement covering LLM use. I could not confirm whether one exists, nor whether CERN has published guidance on using external LLMs with unpublished data.
- The status and launch date of the CERN LLM proxy, its models, and who is eligible are unknown. The HEPiX slides (LLMnAgenticAI_Hepix2026_2.pdf) were not read.
- Anthropic's API retention default (number of days) and ZDR availability were not fetched in this pass.
- EU data residency for Anthropic and Google was not researched.

## 4. Is OpenAI specifically the best choice?

### Takeaway
For *subscriptions*, yes: ChatGPT is currently the only major-lab plan that is officially usable in open-source harnesses, and Letta Code supports it natively. For *pay-as-you-go*, OpenAI is competitive but not uniquely best. gpt-6.1-sol ($2/$10, $0.10 cached) ties Sonnet 5.5 on list price with cheaper caching, and gpt-6-luna and Haiku 5.5 tie at $0.10/$0.50. DeepSeek, GLM and Kimi are 3–20x cheaper but come with data-jurisdiction concerns.

### Cited Findings
- gpt-6.1-sol $2 / $0.10 cached / $10 vs Sonnet 5.5 $2 / $10 with $0.10 cache read but a $2.50 cache write. gpt-6-luna $0.10 / $0.50 = Haiku 5.5 (≤100K). — [OpenAI pricing](https://developers.openai.com/api/docs/pricing); [claude.com/pricing](https://claude.com/pricing)
- OpenAI publicly backs third-party harness use of subscriptions, while Anthropic bans it. — [Manifest](https://manifest.build/blog/chatgpt-plus-tokens-third-party-harnesses/); [AlternativeTo](https://alternativeto.net/news/2026/2/anthropic-officially-bans-using-subscription-authentication-for-third-party-claude-use)
- Letta Code `/connect` supports ChatGPT/Codex plans and zAI coding plans directly. — [Letta Code quickstart](https://docs.letta.com/letta-code/quickstart/index.md)

### Inferences
- **Recommendation (decision-ready):**
  1. **You do not need a paid plan if** all of the following hold: you work only with public or non-sensitive code; you accept free-tier rate limits and data logging; and local Ollama on 6 GB handles the sensitive bits (it will be weak at agentic tool use). Otherwise you do.
  2. **Best value: ChatGPT Plus at $20/mo** as the primary "big brain" via Sign in with ChatGPT in Letta Code / opencode. Turn off training in *both* the ChatGPT and Codex settings. Upgrade to Pro $100 only if the 5-hour caps bite.
  3. **Add an OpenRouter account (~$10–50/mo prepaid) with ZDR enforced account-wide**, behind LiteLLM, for cheap sub-agent and classifier calls (gpt-6-luna, Haiku 5.5, or ZDR-hosted DeepSeek/GLM) and for model swapping. This keeps the vendor-independent property.
  4. **Strictly unpublished results:** use the OpenAI/Anthropic API (no training by default) or OpenRouter-ZDR rather than a consumer plan, and switch to CERN's internal proxy once it is live.
  5. Avoid: Claude Pro/Max in third-party harnesses (ToS violation and ban risk); Gemini AI Pro for CLI agents (CLI access withdrawn); and Chinese coding plans for sensitive data until their terms are verified.
- Expected spend: about $20 (Plus) plus $20–150 (API/OpenRouter), i.e. **$40–170/month**, versus $900+ for a flagship-only API at the Mid scenario.

### Gaps
- No independent benchmark comparison of agentic tool-calling quality across gpt-6.1-sol, Sonnet 5.5, GLM-5.2, Kimi K3 and DeepSeek V4 was gathered in this pass.
- The durability of OpenAI's subscription tolerance is uncertain: it is not contractual and is subject to change.
