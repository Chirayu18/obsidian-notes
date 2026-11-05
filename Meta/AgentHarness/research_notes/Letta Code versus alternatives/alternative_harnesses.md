---
tags: [reference]
status: active
date: 2026-10-08
source: laptop
---

# Open-source alternatives to Letta Code as the harness for a memory-centric multi-agent system (as of 2026-10-08)

Scope: Pi, Hermes Agent, opencode, Goose, OpenHands, Crush, plus a brief look at Aider, LocalHarness, Omnigent, and a "thin loop" built in Python. The requirements come from the user's plan: per-turn fresh context built from a state card, a Python classifier and RAG; free or local models; orchestrator, workers and reviewer; CERN data stays local.

Verification legend: **[V-src]** = read in official repo docs or source, or taken from the GitHub API on 2026-10-08. **[V-docs]** = official docs site, read through a fetch summarizer. **[3P]** = third-party mirror, blog or guide, not independently confirmed.

## Q0: Comparison table (summary)

### Takeaway
Two harnesses expose a documented hook that runs before every LLM call and can replace the message list without changing persisted history: **Hermes Agent** (`ContextEngine.select_context`, in Python) and **Pi** (`context` / `context_with_system` extension events, in TypeScript). opencode has an equivalent hook, but it is undocumented, mutation-only and regression-prone. Goose, Crush and Aider expose no such hook. For a Python classifier, the strongest candidates are **Hermes** (in-process Python) and a **thin PydanticAI/LiteLLM loop**, which gives full control. Pi is the strongest TS option and can be driven from Python over its RPC mode.

### Cited Findings

| Harness | Lang / License | Stars (2026-10-08) | Latest release | Per-request message rewrite hook | Subagents | Custom OpenAI-compat / Ollama |
|---|---|---|---|---|---|---|
| Hermes Agent (NousResearch) | Python / MIT | 252,016 | v0.21.6, 2026-10-08 | **Yes**: `ContextEngine.select_context()`, request-only, Python | Yes: `delegate_task`, 3 concurrent by default | Yes: "Custom endpoint", Ollama `/v1` |
| Pi (earendil-works/pi) | TypeScript / MIT | 113,504 | v1.1.0, 2026-10-07 | **Yes**: `context` and `context_with_system` events | **Not built in** (by design; add via packages) | Yes: `models.json` `baseUrl` + `api: openai-completions` |
| opencode (anomalyco) | TypeScript / MIT | 212,187 | v1.18.35, 2026-10-06 | Partial: `experimental.chat.messages.transform` (undocumented, in-place mutation only, regressions) | Yes: markdown agents, `mode: subagent`, Task tool | Yes (per third-party guides) |
| Goose (aaif-goose) | Rust / Apache-2.0 | 55,083 | v1.54.0, 2026-10-08 | Not found | Yes: subagents + YAML recipes | Ollama, OpenRouter + 15 providers |
| OpenHands | Python SDK (repo language reported as TS) / MIT | 90,294 | v1.26.0, 2026-10-08 | Via SDK condenser (Python); no per-call transform verified | SDK-level | Provider-agnostic LLM layer (LiteLLM-based, not verified this session) |
| Crush (charmbracelet) | Go / FSL-1.1-MIT | 28,546 | v0.98.0, 2026-10-08 | No ("preliminary" hooks) | Not mentioned | Yes: `openai-compat`, Ollama, LM Studio, llama.cpp |
| Aider | Python / Apache-2.0 | 49,427 | v0.86.0, 2025-08-09 (stale) | No | No | Yes (LiteLLM-based, from prior knowledge, not re-verified) |
| Omnigent (Databricks) | Python+Node / Apache-2.0, alpha | unverified | unverified | N/A (meta-harness above Pi, Claude Code, Codex) | Composition across harnesses | Inherits from wrapped harness |
| Thin loop (PydanticAI) | Python / MIT | n/a | n/a | **Yes**: `ProcessHistory` wraps `before_model_request` | You build it | Yes (any OpenAI-compatible) |

- Star counts, licenses, primary language and latest release tags come from the GitHub REST API (`api.github.com/repos/<repo>` and `/releases`), queried 2026-10-08 — [V-src] e.g. [opencode](https://github.com/anomalyco/opencode), [hermes-agent](https://github.com/NousResearch/hermes-agent), [pi](https://github.com/earendil-works/pi), [goose](https://github.com/aaif-goose/goose), [OpenHands](https://github.com/OpenHands/OpenHands), [crush](https://github.com/charmbracelet/crush), [aider](https://github.com/Aider-AI/aider)
- Hermes also publishes date-style tags (latest `v2026.9.24`, 2026-09-24) alongside semver `v0.21.6` — [GitHub API releases](https://github.com/NousResearch/hermes-agent/releases)
- Aider's last release was v0.86.0 on 2025-08-09, and the repo was last pushed 2026-05-22 — [V-src GitHub API](https://github.com/Aider-AI/aider)
- The `block/goose` API path resolves to `aaif-goose/goose`, and the README says goose is "part of the Agentic AI Foundation (AAIF) at the Linux Foundation" — [goose README](https://github.com/aaif-goose/goose)
- arXiv 2609.00006 ("Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents — A Source-Code Study of Eleven Systems") covers Claude Code, Codex CLI, Gemini CLI, Mistral Vibe, OpenHands, Aider, Mini-SWE-Agent, Hermes, Pi, OpenCode and OpenClaw, with Omnigent as a meta-harness contrast, pinned to July 2026 releases — [arXiv](https://arxiv.org/pdf/2609.00006); [search summary/EmergentMind](https://www.emergentmind.com/papers/2609.00006)
- According to secondary write-ups, that paper's first observation is that "loop sophistication does not predict benchmark performance", and it catalogues 29 design patterns across 7 subsystems — [3P Daniel Vaughan blog](https://codex.danielvaughan.com/2026/09/03/harness-engineering-anatomy-eleven-coding-agents-codex-cli-architecture/)
- arXiv 2609.20804 ("An Empirical Study of Harness Design for Coding Agents", 17 Sep 2026) fixes one lightweight loop and varies planning, action space and context management across 176 settings and 4 models (SWE-Bench Verified, Terminal-Bench 2.1). Its findings:
  - Context management matters more as the context budget shrinks, and its benefit comes mostly from preventing overflow failures.
  - Rule-based elision staged before LLM summarization is the most efficient strategy.
  - Making elided content recoverable gave no accuracy gain.
  - Planning acts as an accuracy scaffold for weaker models.
  - Bash-only action spaces suit bash-capable models.

  — [arXiv abs](https://arxiv.org/abs/2609.20804)

### Inferences
- The 2609.20804 result matters for the user's design. Small free or local models (6 GB VRAM → roughly 7–9B quantized) are exactly the "tight budget / weaker model" regime, where context management and planning help most. Rule-based selection followed by summarization is the empirically efficient order, which supports a classifier-first and summarize-second pipeline.
- Star counts are popularity, not quality. Hermes at 252k and opencode at 212k exceed many established projects. All six active projects released within the last week, so expect API churn everywhere.

### Gaps
- I did not verify Omnigent's GitHub repo, stars or release.
- I did not re-verify OpenHands' and Aider's provider internals (LiteLLM) this session.
- I did not read the 2609.00006 full text. Its per-harness findings come from secondary coverage only.

## Q1: Provider independence (custom baseURL, Ollama, free endpoints, tool-calling needs)

### Takeaway
Every active candidate accepts a custom OpenAI-compatible base URL, which covers NVIDIA NIM (`integrate.api.nvidia.com/v1`), OpenRouter `:free` and Ollama `/v1`. In practice the binding constraint is the model's tool-calling reliability, not the harness. Third-party guides say small local models drift on tool schemas and that Hermes wants roughly 64K or more of context.

### Cited Findings
- **Pi**:
  - Ollama, LM Studio, vLLM and SGLang are configured in `models.json` with `"baseUrl": "http://localhost:11434/v1", "api": "openai-completions", "apiKey": "ollama"`.
  - The `apiKey` can use `$ENV`, a literal, or a `!command`.
  - The docs warn: "Do not enable [compat settings] based only on an endpoint advertising OpenAI or Anthropic compatibility."

  — [V-src pi docs/models.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)
- **Pi**: `@earendil-works/pi-ai` is the unified multi-provider LLM API (OpenAI, Anthropic, Google, …). It is the library Letta Code uses, per the task brief — [V-src pi README](https://github.com/earendil-works/pi)
- **Hermes**: Run `hermes model`, choose "Custom endpoint" and enter `http://localhost:11434/v1`. Hermes appends `/chat/completions` itself and requires a non-empty API key — [Ollama docs: Hermes integration](https://docs.ollama.com/integrations/hermes); [3P haimaker guide](https://haimaker.ai/blog/hermes-custom-provider-setup/)
- **Hermes**: The README says "Use any model you want": Nous Portal, OpenRouter, OpenAI, or "your own endpoint", with "no code changes, no lock-in" — [V-src README](https://github.com/NousResearch/hermes-agent)
- **Hermes**: Delegation and auxiliary tasks have separate nested provider config blocks. A third-party guide recommends at least 64K of context and says "small models drift on tool schemas" — [3P haimaker](https://haimaker.ai/blog/hermes-custom-provider-setup/)
- **Crush**: Supports custom `openai-compat` and `anthropic` provider types, and auto-discovers Ollama, LM Studio and llama.cpp. The Ollama example URL is `http://localhost:11434/v1/` — [V-src crush README](https://github.com/charmbracelet/crush)
- **Goose**: Supports "15+ providers" including Ollama, OpenRouter, Azure and Bedrock, plus ACP to existing Claude, ChatGPT or Gemini subscriptions — [V-src goose README](https://github.com/aaif-goose/goose)
- **opencode**: There is an open issue, "feat(core): discover context limits for custom OpenAI-compatible providers" (#53236). Another open issue, #53477, says config-defined models get a placeholder `limit.context` of 200,000 when seen by plugins. In other words, opencode does not know a custom provider's context window unless you set it — [opencode #53236](https://github.com/anomalyco/opencode/issues/53236); [#53477](https://github.com/anomalyco/opencode/issues/53477)
- **opencode**: Open PR #42801, "coalesce system messages for OpenAI-compatible providers", points to friction with strict OpenAI-compat servers — [opencode #42801](https://github.com/anomalyco/opencode/issues/42801)
- **OpenHands**: OpenHands needs at least a 22K context window, and Ollama defaults to 4K, so `num_ctx` must be raised — [3P guide via search](https://theaiarchitects.com/blog/local-llm-coding-agent)

### Inferences
- With 6 GB VRAM, the local Ollama model is at most about a 7–9B Q4 model with a modest context window. That is below Hermes' third-party "64K+" recommendation, and its tool-call reliability will be weak. The realistic split is: the free NIM or OpenRouter models (e.g. Nemotron) do the agentic tool-calling; local Ollama handles the *sensitive-data* steps and small tasks such as classification, summarization and embeddings (bge-m3 is already in use in this vault).
- The free endpoints (NIM, OpenRouter `:free`) are *cloud* endpoints. Any harness routing CMS data to them breaks the "stays local" rule. Routing per task (sensitive → local) requires per-agent/per-subagent model config. opencode (per-agent `model`), Hermes (separate delegation provider block) and Pi (`models.json` + per-session model) all support this.

### Gaps
- I did not verify NIM-specific quirks, such as tool-call format for Nemotron on `build.nvidia.com`, against any harness.
- I did not verify opencode's Ollama setup from official docs this session. The well-known path is the `@ai-sdk/openai-compatible` provider, but I have not checked it.

## Q2: Per-request context control (rewrite the full message list before every LLM call) and native compaction

### Takeaway
- **Hermes `select_context`** is the best match for "fresh context per turn from a Python classifier": it is Python, request-only, runs before every provider request and on retries, and is documented.
- **Pi `context` / `context_with_system`** is the TS equivalent and is documented.
- **opencode `experimental.chat.messages.transform`** works only by in-place mutation. It is undocumented in the official plugin docs, has a live regression (#43764), and maintainers closed fix and docs efforts as not planned.
- **PydanticAI `ProcessHistory`** gives the same capability in a self-built loop.

### Cited Findings
**Hermes Agent [V-docs]**
- Context engines subclass `ContextEngine` in `agent/context_engine.py`. One engine is active at a time, selected by `context.engine` in `config.yaml`, and plugin engines are never auto-activated.
- Required members: `name`, `update_from_response(usage)`, `should_compress(prompt_tokens)`, and `compress(messages, current_tokens, focus_topic)`, which returns a valid OpenAI-format list.
- Optional members include `select_context`, `on_turn_complete`, `get_tool_schemas`/`handle_tool_call`, `clone_for_agent`, `should_compress_preflight` and `update_model`.

— [Hermes context-engine plugin docs](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)
- `select_context(request_messages, ...)` "can return a replacement list for a single provider request". It is request-only, so persisted history is unchanged, and returning `None` leaves the request unchanged. It runs **before prompt cache-control and request sanitizers** and re-runs on retries. The `pre_llm_call` plugin hook is *inject-only* and cannot replace the list. The docs advise stable selections to preserve prompt-cache reuse — [same](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)
- Messages carry a stable `message_uid`, which an engine can use to key per-message classifier state. Compression may run on a pooled daemon thread, so an engine instance must be thread-safe. Each `AIAgent` (parent, subagents, gateway sessions) gets its own copy via `clone_for_agent()`, a deep copy by default. If cloning fails, the agent falls back to the built-in compressor — [same](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)
- An engine can expose its own tools via `get_tool_schemas()`/`handle_tool_call()`, for example a `recall_turns` RAG tool — [same](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)

**Pi [V-src]**
- "`context` transforms conversation messages without prompt and tool system messages; Pi restores that state afterward. Use `context_with_system` only when a request-local transformation must own the complete transcript, and keep a system message at index zero." — [pi docs/extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
- `before_agent_start` can change prompt sections or tools, or return `systemPrompt`/`forceSystemPrompt` to replace the whole system prompt for a run. `turn_end` and `agent_before_settle` can chain `custom`, `custom_message`, `context_edit` or `compaction` entries and return `continue: true` for one more model request. The docs warn that unconditional continuation can loop — [same](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
- Exact types live in `packages/coding-agent/src/core/extensions/types.ts`. Extensions live in `~/.pi/agent/extensions/` or `.pi/extensions/` and hot-reload with `/reload` — [pi docs](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md); [3P mirror](https://www.mintlify.com/pt-act/pi-mono/concepts/extensions)
- A third-party guide says `event.messages` in `context` is a deep copy that is safe to modify — [3P runoob](https://www.runoob.com/pi-agent/pi-agent-events.html)
- Pi compaction has two mechanisms: auto-compaction and branch summarization. The source is in `core/compaction/compaction.ts` and `branch-summarization.ts`, with `CompactionEntry` and `BranchSummaryEntry` entry types and extension hooks — [pi docs/compaction.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/compaction.md)
- **Language bridge**: "RPC mode runs Pi as a long-lived subprocess controlled through JSON records on stdin and stdout. Use it for language-independent integrations" — [pi docs/rpc.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md)
- `ctx.modelRegistry.streamSimple()` is available for provider-neutral nested model calls inside extensions, for example a summarizer call — [pi extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)

**opencode [V-src issues, V-docs]**
- The official plugin docs list no `experimental.chat.messages.transform` and no `chat.params`. They document only `experimental.session.compacting`, which can push to `output.context` or replace `output.prompt` for the continuation summary — [opencode.ai/docs/plugins](https://opencode.ai/docs/plugins/)
- #25754: reassigning `output.messages = newArray` is a silent no-op, and only in-place mutation (`splice`) works. It was closed **not_planned** on 2026-05-04 — [#25754](https://github.com/anomalyco/opencode/issues/25754)
- PR #32758, the fix that would accept reassignment in prompt.ts and compaction.ts, was closed **unmerged** on 2026-06-18 — [#32758](https://github.com/anomalyco/opencode/pull/32758)
- Docs PR #33025, which would have documented `experimental.chat.{system,messages}.transform`, was closed not_planned on 2026-06-19. #19960 (system.transform fires after messages.transform) was closed not_planned on 2026-07-03 — [#33025](https://github.com/anomalyco/opencode/issues/33025); [#19960](https://github.com/anomalyco/opencode/issues/19960)
- #43764 is **open** (filed 2026-08-21). On opencode ≥1.18.15, the DCP plugin's context removal via `messages.transform` became "cosmetic": the model-visible context never shrinks (130K→80K on 1.18.13 vs. stuck at about 135K on 1.18.18), because commit `db581e47a` changed message ordering. The reporter also found native compaction "inert" — [#43764](https://github.com/anomalyco/opencode/issues/43764)
- #46331 is open (2026-08-31) and refers to dev `10765ff`. It says compaction calls `structuredClone(selected.head)` "even when no `experimental.chat.messages.transform` hook exists" and that "the existing clone must remain when a transform hook is registered". This implies the compaction path does invoke the transform hook on current dev — [#46331](https://github.com/anomalyco/opencode/issues/46331)
- #53109 is open: "Per-request context tail truncation splits tool-call groups, causing HTTP 400". #51818 is open: compaction can make the context larger. #50338 is open: AI SDK V2 providers silently lose usage and disable auto-compaction — [#53109](https://github.com/anomalyco/opencode/issues/53109); [#51818](https://github.com/anomalyco/opencode/issues/51818); [#50338](https://github.com/anomalyco/opencode/issues/50338)
- A separate report says opencode 1.16.2 silently ignored some `experimental.*` hook names (`system.transform`, `session.compacting`) — [3P hindsight #2656](https://github.com/vectorize-io/hindsight/issues/2656)

**OpenHands [V-docs]**
- The SDK default is `LLMSummarizingCondenser`, which triggers past `max_size` events and keeps the `keep_first` events. The condenser can use a separate LLM (`llm.model_copy(update={"usage_id": "condenser"})`) — [OpenHands condenser guide](https://docs.openhands.dev/sdk/guides/context-condenser)

**Goose [3P]**
- Auto-compaction triggers at 75% of the context window, per a third-party source mirror. No pre-call message-rewrite hook was found — [3P mintlify mirror](https://mintlify.com/block/goose/concepts/architecture)

**Crush [V-src]**
- Hooks have "preliminary support". Context comes from `CRUSH.md`/`AGENTS.md`, and `.crushignore` excludes files. The README does not describe compaction — [crush README](https://github.com/charmbracelet/crush)

**PydanticAI thin loop [V-docs]**
- `ProcessHistory` wraps the `before_model_request` hook and runs "before each model request". It takes and returns `list[ModelMessage]`, optionally with a `RunContext`, and the processed list **replaces** history in state.
- Caveat: slicing that separates a tool call from its return is silently "repaired". The orphaned return is dropped, or a synthetic "interrupted" return is added. Slice on call/return boundaries.

— [PydanticAI message history](https://pydantic.dev/docs/ai/core-concepts/message-history/)

### Inferences
- **On the brief's opencode claim**: I found no issue matching "broke in v1.17.1". The verified record is:
  - The reassignment contract bug was closed not_planned (#25754) and its fix was never merged (#32758).
  - A live ordering regression from 1.18.15 makes transform-based pruning ineffective (#43764, open).
  - On current dev the hook *does* appear to be called on the compaction path (#46331).

  The "not fired during compaction" claim may therefore be **stale**, but the hook remains undocumented and fragile. Any design built on it must splice in place and pin a version.
- For a design where the "fresh context every turn" is the system's *core* invariant, the hook must be a first-class, documented API. Only Hermes (`select_context`), Pi (`context`/`context_with_system`) and a self-built loop meet that bar.
- Hermes' `select_context` + `compress` + `message_uid` + `get_tool_schemas` maps almost 1:1 onto the plan:
  - state card → system or first message
  - classifier picks UIDs
  - RAG tool over older turns and the Obsidian vault
  - all of it in Python, in-process
- A request-only selection that changes every turn defeats prompt caching. That cost is near zero on free or local endpoints but matters with paid APIs, and Hermes' docs call it out explicitly.

### Gaps
- I could not locate the specific opencode v1.17.1 breakage issue the brief refers to.
- I did not read Pi's `types.ts` for the exact `context` handler return shape. A third-party source says it returns `{ messages }`.
- I did not confirm whether OpenHands exposes a per-call (rather than condensation-time) message transform.

## Q3: Multi-agent / subagent support (custom agents, parallel workers, worktrees, reviewer loops)

### Takeaway
opencode and Hermes have the most usable built-in subagents. opencode has declarative markdown agents with per-agent model and permissions plus a `steps` cap; Hermes has `delegate_task` with parallel batches. Goose has subagents plus YAML recipes. Pi deliberately ships none. None of the docs I read provide git-worktree orchestration natively, so worktree-per-worker plus reviewer loops would be user-built in any harness, or provided by a meta-harness like Omnigent.

### Cited Findings
- **opencode**:
  - Agents are markdown files in `~/.config/opencode/agents/` or `.opencode/agents/` (or JSON under `agent`).
  - Frontmatter fields: `description` (required), `mode: primary|subagent|all`, `model: provider/model-id`, and `permission` (read/edit/bash/task/webfetch → ask/allow/deny, with bash globs).
  - The `task` permission controls which subagents can be invoked.
  - `steps` caps agentic iterations, which gives bounded loops.
  - Built-in subagents: General (can run multiple units in parallel), Explore, Scout.
  - Worktrees are mentioned only as the "project worktree" boundary.

  — [opencode.ai/docs/agents](https://opencode.ai/docs/agents/)
- **Hermes**:
  - `delegate_task` "spawns child AIAgent instances with isolated context, restricted toolsets, and their own terminal sessions".
  - Batch runs default to 3 concurrent subagents, configurable.
  - Children start with zero parent history: everything goes in `goal`/`context`.
  - Execution is synchronous within the parent turn.

  — [Hermes delegation docs (via search summary)](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)
- **Hermes**: the README advertises "Spawn isolated subagents for parallel workstreams" and Python scripts calling tools over RPC — [README](https://github.com/NousResearch/hermes-agent)
- **Pi**: Pi "skips features like sub-agents and plan mode", and the docs suggest installing a package or having Pi build them — [pi README](https://github.com/earendil-works/pi)
- **Pi**: a tool can call other tools via `ctx.executeTool(name, args, …)`. Nested calls are bounded: at most 256 recorded, and their arguments are dropped from the record above 8 KiB per call or 32 KiB per tool result — [pi extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
- **Goose**:
  - Subagents run as separate instances and are used autonomously only in the default autonomous permission mode.
  - A subagent gets a 5-minute default timeout, and you get no output if it fails or times out.
  - Recipes are declarative YAML (extensions, model, instructions, tasks) and are one of two ways to configure subagents.

  — [goose-docs.ai subagents](https://goose-docs.ai/docs/guides/subagents); [context-engineering/subagents](https://goose-docs.ai/docs/guides/context-engineering/subagents)
- **Omnigent**:
  - A "meta-harness" from Databricks that wraps Claude Code, Codex and Pi, plus the OpenAI Agents and Claude Agents SDKs.
  - A runner sandboxes each session, and a server provides policies and sharing.
  - It mixes harnesses and models in multi-agent teams, with cost caps.
  - Alpha, Apache-2.0. Requires Python 3.12+, Node 22 and tmux.

  — [Databricks blog](https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents); [3P runtimewire](https://runtimewire.com/article/databricks-open-sources-omnigent-to-put-a-meta-harness-above-ai-agents)
- **Crush**: the README does not mention subagents — [crush README](https://github.com/charmbracelet/crush)

### Inferences
- The orchestrator → workers-in-worktrees → reviewer topology with bounded loops is application logic. It is easiest to own in Python, for example a LangGraph graph or a plain asyncio loop that calls `git worktree add` per worker. Each worker can then be any harness run headless (Hermes, Pi via RPC, or opencode `run`), or a thin PydanticAI agent.
- Hermes' children start with no parent history, which fits a "fresh context" philosophy: the orchestrator writes a state card into `goal`/`context`. Synchronous delegation means no true background workers unless you run several Hermes processes.

### Gaps
- I found no harness with documented first-class git-worktree management in this session.
- I did not verify Hermes' per-subagent model and endpoint config keys.

## Q4: Built-in memory features

### Takeaway
Hermes is the only candidate with substantial built-in memory: curated MEMORY.md and USER.md, FTS5 session search, autonomous skills, and pluggable external providers (Mem0, Supermemory, Honcho, LanceDB). The others rely on static context files (AGENTS.md, CRUSH.md) plus MCP.

### Cited Findings
- **Hermes memory**:
  - Built-in file memory: `MEMORY.md` capped at about 2,200 chars and `USER.md` at about 1,375 chars.
  - The agent edits it with add/replace/remove, and it is injected into the system prompt at session start, so there is no read action.

  — [Hermes memory docs (via search summary)](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- **Hermes**: "FTS5 session search with LLM summarization for cross-session recall"; skills are created autonomously and "self-improve during use" (agentskills.io standard); Honcho provides user modeling — [README](https://github.com/NousResearch/hermes-agent)
- **Hermes**: one external memory provider can run alongside the built-in one. The LanceDB provider runs in-process and stores to local disk — [LanceDB docs](https://docs.lancedb.com/integrations/ai/hermes-agent); [Mem0 docs](https://docs.mem0.ai/integrations/hermes); [3P wiki](https://wiki.enola.dev/computer/ai/software/memory/hermes-memory-providers.html)
- **Pi**: `pi.appendEntry()` persists "durable data excluded from model context" in the session. This is a primitive for building memory, not a memory system — [pi extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
- **opencode**: there is a community plugin, "opencode-mempalace-persistence" (#49559), but no core memory — [#49559](https://github.com/anomalyco/opencode/issues/49559)

### Inferences
- Hermes' built-in memory partly overlaps with the user's own design (pinned state card ≈ MEMORY.md; RAG over old turns ≈ FTS5 session search). The user could either reuse it or disable it and own memory in a custom ContextEngine. The roughly 2.2K-char cap on MEMORY.md is much smaller than a full state card would likely need.

### Gaps
- I did not verify memory features for Goose (beyond MCP), OpenHands or Crush.

## Q5: Local / privacy (telemetry, cloud dependence)

### Takeaway
All candidates can run fully against local endpoints. Crush has documented pseudonymous metrics, with an opt-out. I found no authoritative telemetry statements for Hermes, Goose or opencode this session, so check the source before using any of them with CMS data. Pi ships a `pi-telemetry` package that defines vendor-neutral telemetry contracts.

### Cited Findings
- **Crush**: collects pseudonymous usage metrics with a device hash; "prompts and responses are NEVER collected". Opt out with `CRUSH_DISABLE_METRICS=1` or `DO_NOT_TRACK=1` — [crush README](https://github.com/charmbracelet/crush)
- **Pi**: the monorepo includes `pi-telemetry` ("vendor-neutral telemetry contracts, a reference adapter, conformance tests") — [pi README](https://github.com/earendil-works/pi). Separately, PostHog documents an opt-in LLM-analytics integration for Pi — [PostHog docs](https://posthog.com/docs/llm-analytics/installation/pi.md)
- **Goose**: a review site claims goose "does not phone home or collect telemetry beyond what you explicitly configure". This is unverified [3P] — [aicoolies review](https://aicoolies.com/reviews/goose-review)
- **Hermes**: the README does not discuss telemetry. Its security docs cover command approval and container isolation — [README](https://github.com/NousResearch/hermes-agent)
- **Hermes context engines**: no dedicated telemetry API; observability is local (token counters, `get_status()`) — [context-engine docs](https://hermes-agent.nousresearch.com/docs/developer-guide/context-engine-plugin)
- **Omnigent**: one write-up says the design keeps inference and credentials local — [3P via search](https://www.opensourceforu.com/?p=99837)

### Inferences
- The real privacy risk is model routing, not harness telemetry. Free NIM and OpenRouter endpoints are cloud services, so CMS-sensitive turns must be routed to local Ollama by policy. A Python orchestrator, or a Hermes ContextEngine that redacts in `select_context`, is a natural enforcement point.
- opencode has a share feature (from prior knowledge, not verified this session), which should be disabled.

### Gaps
- I found no official telemetry or privacy statements for opencode, Hermes or Goose this session, and their source needs auditing.

## Q6: Maturity, cadence, breaking changes, and extensibility language

### Takeaway
All six active projects ship weekly or faster (releases dated 2026-10-06 to 2026-10-08), so breaking changes are a constant. opencode's issue tracker shows repeated silent plugin-contract breaks. Aider is effectively stalled (last release Aug 2025). Hermes is the only top candidate whose extension language is Python, matching the classifier. Pi and opencode are TS, Crush is Go and Goose is Rust.

### Cited Findings
- Releases:
  - opencode v1.18.34 (09-30) → v1.18.35 (10-06)
  - pi v1.0.4 (10-05) → v1.1.0 (10-07)
  - goose v1.53.0 (10-02) → v1.54.0 (10-08)
  - OpenHands v1.25.0 (10-06) → v1.26.0 (10-08)
  - crush v0.98.0 (10-08) plus nightlies
  - Hermes v0.21.6 (10-08)

  — [V-src GitHub API releases](https://github.com/anomalyco/opencode/releases)
- **opencode plugin fragility record**:
  - #25754 (reassign no-op, not_planned)
  - #32758 (fix unmerged)
  - #43764 (regression ≥1.18.15, open)
  - #25293/#30631 (plugin `@latest` pinned to a stale npm version)
  - #50488 (title generation runs `system.transform`)

  — [#25293](https://github.com/anomalyco/opencode/issues/25293); [#50488](https://github.com/anomalyco/opencode/issues/50488)
- **opencode**: plugins are JS/TS modules (types from `@opencode-ai/plugin`), and dependencies are installed with Bun at startup — [opencode docs/plugins](https://opencode.ai/docs/plugins/)
- **Pi**: extensions, skills, prompt templates and themes are bundled as "Pi packages" via npm or git. The repo has 6,827 commits on main — [pi README](https://github.com/earendil-works/pi)
- **Pi**: the npm scope is `@earendil-works/*`. Third-party mirrors still refer to it as `pi-mono`, and the README references `badlogic/pi-share-hf`. The move from badlogic/pi-mono is likely but not stated on the page — [pi README](https://github.com/earendil-works/pi); [3P mirror](https://www.mintlify.com/pt-act/pi-mono/concepts/architecture)
- **Hermes**: Python; gateways for Telegram, Discord, Slack, WhatsApp, Signal and Email; MCP support; Termux APT repo — [README](https://github.com/NousResearch/hermes-agent)
- **Crush** is licensed FSL-1.1-MIT (Functional Source License, converting to MIT later), not OSI open source at release time — [crush README](https://github.com/charmbracelet/crush)
- **Omnigent** is alpha. A Medium post claims about 8,000 stars and 3,000+ Databricks engineers, but this is unverified — [3P Medium](https://medium.com/@adnanmasood/omnigent-a-meta-harness-for-ai-agents-6ed55361a01b)

### Inferences
- **Ranking for this user's plan:**
  1. **Hermes Agent**: Python, documented request-only `select_context`, `message_uid`, engine-owned tools, built-in subagents and memory. The main risks are that it is a large, fast-moving codebase and that its subagents run synchronously.
  2. **Thin Python loop** (PydanticAI `ProcessHistory`, or LiteLLM + LangGraph): total control over fresh-context invariants, worktrees and reviewer loops, with no harness churn. The cost is building the tools, TUI and permission layer, and the 2609.00006 "loop sophistication ≠ performance" finding suggests a thin loop is not inherently weaker.
  3. **Pi**: the cleanest documented TS hook (`context_with_system`), minimal by design, and it shares pi-ai with Letta Code. The Python classifier would run as a sidecar (HTTP or stdio) called from a TS extension, or Pi would be driven from Python over RPC. Subagents would have to be added.
  4. **opencode**: rich agents and permissions, but its message transform is undocumented and has regressed. Usable only with pinned versions and in-place splicing.
  5. **Goose / Crush / OpenHands**: no per-call rewrite hook was found, so they are poor fits for a fresh-context design. OpenHands' Python SDK condenser is the nearest analogue.
- **LocalHarness**: I found no project by that name. The search surfaced Ollama-Code, local-agent (Go, alpha) and ollama-agent-harness, all small and early.

### Gaps
- I did not verify LocalHarness at all, so the brief may refer to a project I could not find.
- I did not verify LiteLLM or LangGraph specifics this session. Only the PydanticAI `ProcessHistory` docs were read.
- Hermes' breaking-change history was not examined.
