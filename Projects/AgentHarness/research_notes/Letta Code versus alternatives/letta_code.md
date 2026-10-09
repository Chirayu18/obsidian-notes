---
tags: [reference, research]
status: active
date: 2026-10-08
source: laptop
---

# Letta Code as the harness for a memory-centric, vendor-independent multi-agent system

Scope: letta-ai/letta-code. The brief said v0.34.4. Main is now **v0.34.7**: v0.34.5, v0.34.6 and v0.34.7 were all tagged on 2026-10-08. Source was read at commit `3a958a4` (2026-10-08, package.json `"version": "0.34.7"`). The original `/tmp/lc` clone was missing, so I re-cloned shallowly into `/tmp/lc_src/lc`. I only read it and ran nothing from the repo.

Tags: **[verified in source]** means I read the code. **[docs]** means docs.letta.com or the README. **[reported/third-party]** means GitHub issues and similar.

Source links below are pinned to `https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/` (abbreviated `SRC/`).

## Q1. How mature is the local backend (no Letta Cloud)? Is LETTA_LOCAL_BACKEND_EXPERIMENTAL still required? What is cloud-only? What do issues report?

### Takeaway
You no longer need the env var for local mode. `letta backend local` (saved default) or `--backend local` (one-off) selects it, and the docs present it as a normal mode. Internally the code still calls it "experimental", and the open issues show real production bugs: compaction death-spirals, Ollama turns stalling, oversized transcripts and context-window misdetection. Treat it as beta.

### Cited Findings
- [verified in source] The env var `LETTA_LOCAL_BACKEND_EXPERIMENTAL` still exists (`=1`/`true`). However, `resolveBackendMode()` gives a runtime override priority: `configuredBackendMode ?? (isLocalBackendEnvEnabled() ? "local" : "api")`. The `--backend` flag and the saved `letta backend local` setting both set that override. — [SRC/src/backend/backend-mode.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/backend-mode.ts), [SRC/src/backend/local/paths.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/paths.ts), [SRC/src/cli/subcommands/backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/subcommands/backend.ts)
- [docs] The README says: "Letta Cloud is the default. On first launch, choose to sign in with Letta or proceed locally… `letta backend cloud` / `letta backend local` to change the default. Use `--backend cloud` or `--backend local` for a one-off override". — [README](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/README.md)
- [docs] The local-mode page does not label the mode experimental. It says "all agent state, including messages, memory, and provider connections, stays on-device" and "no Letta account is required". Its limitations: no chat.letta.com access, no automatic backup, and remote providers still receive the prompts. — [Local setup](https://docs.letta.com/letta-code/local-mode)
- [verified in source] Capability flags show what differs. The `LocalBackend` sets `promptRecompile:true, localMemfs:true, localModelCatalog:true`. It has `remoteMemfs:false, serverSideToolManagement:false, serverSecrets:false, byokProviderRefresh:false, environmentRouting:false`. `environmentRouting` (sending subagent turns to other computers or Cloud sandboxes) is documented in code as "Cloud-only". — [SRC/src/backend/backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/backend.ts), [SRC/src/backend/dev/fake-headless-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/fake-headless-backend.ts), [SRC/src/backend/local/local-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-backend.ts)
- [verified in source] Local compaction accepts only the modes `"all"` and `"sliding_window"`. Anything else throws `Local backend compaction currently supports only modes "all" and "sliding_window"`. — [SRC/src/backend/local/local-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-backend.ts)
- [docs] Deploying an existing stateful agent as a subagent requires "the same Letta API org/project". — [Subagents](https://docs.letta.com/letta-code/subagents)
- [reported/third-party] Issue #4962 (v0.34.2, `letta server --backend local`, vLLM Qwen3.8-27B behind a **LiteLLM proxy**) reports three failures. First, an off-by-one context check: 114,689 prompt + 16,384 max_tokens = 131,073, against a 131,072 limit, gave silent 400s. Second, a "no-op compaction death spiral": 16 compaction entries with `msgs 101 -> 101`, each adding about 4KB. Third, compaction never fired again after a failed turn. A bot closed the issue on 2026-10-05 for not meeting the template requirements, not because it was fixed. — [#4962](https://github.com/letta-ai/letta-code/issues/4962)
- [reported/third-party] Issue #4650 (open, v0.32.18) reports that every turn on local backend + Ollama stalled. Root cause per the reporter: the local agent's system prompt is about 15k tokens (persona + memory + about 20 bundled skills + tool schemas). Prompt processing on an M4 Pro with qwen3:8b took 60–150 s, and the stream-stall reconciler aborts after 60 s of silence. The workaround is `LETTA_STREAM_STALL_RECONCILE_MS=600000`. — [#4650](https://github.com/letta-ai/letta-code/issues/4650)
- [verified in source] That default is still 60 s: `DEFAULT_STREAM_STALL_RECONCILE_MS = 60_000`, overridable with `LETTA_STREAM_STALL_RECONCILE_MS`. — [SRC/src/cli/helpers/stream-stall-reconciler.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/helpers/stream-stall-reconciler.ts)
- [reported/third-party] #4938 (open): an oversized local transcript hits the JS string limit (`Cannot create a string longer than 0x1fffffe8 characters at readJsonlFile`), and projection fails 419 times. #4893 (open): preflight compaction ignores the mid-conversation `<memory_update>`. #3956 (open): tool-heavy turns quickly refill context after `sliding_window` compaction. #4936 (closed): Desktop favorites do not show local agents. — [#4938](https://github.com/letta-ai/letta-code/issues/4938), [#4893](https://github.com/letta-ai/letta-code/issues/4893), [#3956](https://github.com/letta-ai/letta-code/issues/3956), [#4936](https://github.com/letta-ai/letta-code/issues/4936)
- [reported/third-party] A GitHub issue search for "local backend" in the repo returns 157 issues (all states) as of 2026-10-08. — [GitHub search](https://github.com/letta-ai/letta-code/issues?q=is%3Aissue+local+backend)

### Inferences
- Local mode works and is officially supported, but the code underneath is young. Pi-ai was adopted as the provider layer around July 2026 (#3482 mentions a "pi-ai 0.81 migration"). Expect to patch it or pin versions.
- #4962 has the same topology as the user's plan (local backend + LiteLLM + self-hosted Qwen), so its failure modes are directly relevant.

### Gaps
- I did not run the binary, so the maturity assessment rests on the code and issues, not on measurement.
- I could not confirm whether #4962's three bugs were fixed after the bot closed it. I found no "no-op compaction" guard in `compaction.ts` or `local-backend.ts`, but I only searched for keywords.

## Q2. Where is state stored locally? What exactly goes into each LLM request? Can each turn start fresh?

### Takeaway
State lives in `~/.letta/lc-local-backend/` as JSON and JSONL files plus one git repo of markdown memory per agent. Every turn sends the compiled system prompt, the full post-compaction conversation history and the tool schemas, so persistent memory is the core design. There are three ways to get a fresh start: headless `--ephemeral`, the agent-free ephemeral conversations used by the Workflow tool, or a new conversation each time. None of them lets you inject your own selected history into a persistent agent's turn.

### Cited Findings
- [verified in source] Storage root is `LETTA_LOCAL_BACKEND_DIR` or `~/.letta/lc-local-backend`. Agents are `agents/<id>.json`. Conversations are `conversations/<id>/{conversation.json, system-prompt.json, manifest.json, messages.jsonl}`. Memory is `memfs/<agentId>/memory`, a git repo (the prompt compiler runs `git ls-tree -r --name-only HEAD`). — [SRC/src/utils/local-backend-paths.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/utils/local-backend-paths.ts), [SRC/src/backend/local/local-store.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-store.ts), [SRC/src/backend/local/local-transcript.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-transcript.ts), [SRC/src/backend/local/system-prompt-compilation.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/system-prompt-compilation.ts)
- [verified in source] Turn assembly in `HeadlessBackend` works as follows. It settles interrupted tool calls, then `appendTurnInput`. It loads `history = store.listConversationMessages(...)` and `uiMessages = store.listLocalMessages(...)`, resolves the system prompt, and passes `{systemPrompt, midConversationSystemPrompt, history, uiMessages}` to the executor. The request therefore carries the whole stored, post-compaction message window every turn. — [SRC/src/backend/dev/fake-headless-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/fake-headless-backend.ts)
- [verified in source] The system prompt is compiled from MemFS. `system/*.md` files are inlined in a `<memory>` section. Other memory files appear only as a tree of `<projection>$MEMORY_DIR/...` paths, which the agent reads with tools. When memory changes mid-conversation, a `<memory_update>` block is injected and declared "authoritative from now on". — [SRC/src/backend/local/system-prompt-compilation.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/system-prompt-compilation.ts), [SRC/src/backend/local/local-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-backend.ts)
- [verified in source] Compaction does not destroy the on-disk transcript. `messages.jsonl` keeps "historical JSONL rows (especially after compaction, which appends …)", and the in-context window is rebuilt as `[summary, ...keptMessages]`. — [SRC/src/backend/local/local-transcript.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-transcript.ts), [SRC/src/backend/local/local-context-estimate.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-context-estimate.ts)
- [verified in source] Fresh-context options:
  - Headless `--ephemeral`: "Run in a temporary conversation with no agent or memory".
  - `--stateless`: "Run an existing agent without MemFS enablement or sync".
  - `--system-custom <string>` and `--new`.
  - `LocalBackend.createEphemeralConversation({model, system, ...})`.
  - The Workflow tool runs "each agent() call in the script … in an agent-free ephemeral conversation".

  Sources: [SRC/src/cli/args.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/args.ts), [SRC/src/tools/impl/workflow.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/tools/impl/workflow.ts)
- [reported/third-party] The baseline local-agent system prompt is about 15k tokens (persona + memory + about 20 skills + tool schemas). — [#4650](https://github.com/letta-ai/letta-code/issues/4650)
- [verified in source] Flags exist to slim it: `--no-skills`, `--no-bundled-skills`, `--no-system-info-reminder`, `--toolset <mode>`, `--tools`, `--no-mods`. — [SRC/src/cli/args.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/args.ts)

### Inferences
- The user's "rebuild context per turn" design conflicts with Letta's core model of an append-only conversation, a compiled memory system prompt and compaction. You can get a fresh turn by having an external controller run `letta -p --ephemeral` (or `--new`) each turn with a custom system prompt carrying the state card and selected messages. That reduces Letta to a tool-running executor, and you lose its memory and agent identity.
- Because Letta keeps the full transcript in `messages.jsonl`, a sidecar classifier/RAG can read it as the source corpus.

### Gaps
- I did not check whether `--system-custom` combines with `--ephemeral` in headless mode, or how big the ephemeral system prompt is.

## Q3. Can message selection be replaced: hooks, harness mods, provider mods, compaction config, or only a fork?

### Takeaway
No supported extension point lets you see and rewrite the full message list before the LLM call. Hooks and mods can only append context or rewrite the new user input. Provider mods only register endpoints and models. Compaction can be tuned but not replaced. You have two practical routes: (a) an OpenAI-compatible proxy in front of the model, which Letta sees as just a provider, or (b) a fork patching `HeadlessBackend` turn assembly or `resolveSystemPromptForTurn`.

### Cited Findings
- [verified in source] `UserPromptSubmit` command hooks: exit 0 with stdout means the stdout is collected as feedback. The TUI wraps it in `<system-reminder>…</system-reminder>` and injects it into the turn. A block exit stops the prompt. Only `PreToolUse` supports an `updatedInput` rewrite. — [SRC/src/hooks/executor.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/hooks/executor.ts), [SRC/src/cli/app/use-submit-handler.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/app/use-submit-handler.ts)
- [verified in source] `runUserPromptSubmitHooks` is called only from the TUI submit handler (`src/cli/app/use-submit-handler.ts`); a search of `src/` finds no headless call site. — [SRC/src/hooks/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/hooks/index.ts)
- [docs] Hook feedback "is injected as a `<system-reminder>` for that turn", "is turn context, not a memory block write", and "is not an in-place replacement mechanism for previous messages". — [Hooks](https://docs.letta.com/letta-code/hooks)
- [verified in source] Mod events are `conversation_open/close, tool_start/end, turn_start/end, compact_start/end, llm_start/end`.
  - `turn_start` may return `{input?: MessageCreate[], cancel?}`, which rewrites or cancels only the **new turn input**.
  - `llm_start` is observe-only: it receives `{model, messageCount, contextWindow}` and returns `undefined`.
  - `compact_*` events are observe-only.
  - `turn_end` can return `{continue}`.
  - The conversation handle exposes `fork`, `getHistory` (read), `sendMessageStream` and `updateLlmConfig({model, contextWindow, scope})`.

  Source: [SRC/src/mods/types.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/mods/types.ts)
- [verified in source] Provider mods (`PiProviderRegistration`) declare `baseUrl, apiKey, api, headers, models, listModels, connect, oauth{login, refreshToken, getApiKey, modifyModels}`. There is no stream or request-transform hook, so they cannot see or rewrite messages. — [SRC/src/backend/dev/pi-provider-mod-types.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/pi-provider-mod-types.ts)
- [verified in source] Compaction settings stored per agent are `mode` (`all` | `sliding_window`), `prompt`, `clip_chars`, `sliding_window_percentage` and `model`. The trigger threshold is hard-coded: `contextWindow − min(16384, 20% of contextWindow)`. The only indirect knob is `context_window_limit`. — [SRC/src/backend/local/local-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-backend.ts), [SRC/src/backend/dev/provider-turn-executor.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/provider-turn-executor.ts)
- [verified in source] Sliding-window detail, which corrects the brief's "evicts oldest 30%". The default percentage is 0.3, but the loop adds 0.1 *before* its first cut, so the first attempt evicts about 40% of messages by count. It keeps adding 10% until the kept messages fit within `(1−p)·contextWindow` by char/4 estimate. The summary uses `SLIDING_WORD_LIMIT = 300` words, and tool returns are clipped to 2,000 chars inside the summarizer input. — [SRC/src/backend/local/compaction.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/compaction.ts)
- [verified in source] The `PreCompact` hook "cannot block". — [SRC/src/hooks/types.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/hooks/types.ts)

### Inferences
- A trainable PIN/KEEP/COMPRESS/DROP selector cannot be plugged in through hooks or mods. The only in-process interception points are `resolveSystemPromptForTurn` (overridden in `LocalBackend`) and the `history`/`uiMessages` arrays in `HeadlessBackend.sendMessage`. Both require a fork.
- The low-friction route is a local proxy configured as an `openai-compatible` provider, or as a provider mod with `baseUrl` pointing to it. This keeps Letta unforked, but see Q4 for the accounting side effects.
- A UserPromptSubmit hook (TUI only) can inject RAG or vault snippets as a system-reminder. That only adds context and never removes old turns.

### Gaps
- I did not find a public plugin API for overriding `resolveSystemPromptForTurn`. It is a protected method on an internal class.

## Q4. If an upstream proxy (e.g. LiteLLM with async_pre_call_hook) rewrites or truncates messages, how do Letta's token accounting and compaction react?

### Takeaway
Letta anchors its context estimate on **provider-reported usage** from the last assistant message, plus a char/4 estimate for messages after it. If a proxy truncates, usage comes back small. Letta then believes the context is small, never compacts, and its own store keeps growing while the proxy keeps cutting it down. Nothing errors, but Letta ends up shipping ever-larger requests to the proxy, and very large transcripts hit known JS string limits (#4938).

### Cited Findings
- [verified in source] `estimateProviderContextTokens` uses `estimateLocalContextTokens(uiMessages)`. If any assistant message carries usage, the result is anchored on it: `totalTokens`, or `input+output+cacheRead+cacheWrite`, plus the trailing messages at chars/4. Only when no usage exists does it fall back to serialized system prompt + messages + tools at chars/4. The logic is ported from Pi's `calculateContextTokens`. — [SRC/src/backend/local/local-context-estimate.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-context-estimate.ts), [SRC/src/backend/dev/provider-turn-executor.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/provider-turn-executor.ts)
- [verified in source] Usage anchors at or before the latest compaction timestamp are ignored. Assistant messages with all-zero usage are skipped as anchors. — same file
- [verified in source] Compaction triggers pre-request when `contextTokens > contextWindow − reserve` (`shouldCompactForContextPressure`). There is also a post-overflow path, `compactAfterContextOverflow`, triggered by a provider overflow error. — [SRC/src/backend/dev/provider-turn-executor.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/provider-turn-executor.ts), [SRC/src/backend/local/local-backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/local-backend.ts)
- [verified in source] There is also a fail-loud guard, `estimateProviderPromptFloorTokens`, for when system prompt + tools alone exceed the window. — same file
- [reported/third-party] #4962's deployment ran exactly this topology (LiteLLM proxy in front of vLLM) and saw silent 400s from one-token overflows. Proxy errors were visible only in the proxy logs. — [#4962](https://github.com/letta-ai/letta-code/issues/4962)
- [reported/third-party] Custom OpenAI-compatible endpoints were clamped to 128k regardless of the `context_length` in `/v1/models`, and `LOCAL_ENDPOINT_DEFAULT_MAX_TOKENS = 32000` (#4246, open). The 32000 constant is still in source. — [#4246](https://github.com/letta-ai/letta-code/issues/4246), [SRC/src/backend/dev/pi-local-endpoint-provider.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/pi-local-endpoint-provider.ts)

### Inferences
- With a truncating proxy, either set `context_window_limit` to what the proxy actually forwards, or have the proxy report usage as if untruncated. Otherwise Letta's compaction is effectively turned off.
- A safer split: the proxy only *adds* context (state card, RAG) and leaves history trimming to Letta's compaction, set via `context_window_limit` plus a custom summary `prompt`. A proxy that drops messages must keep tool_call/tool_result pairs intact, or providers will reject the request.

### Gaps
- I did not test the interaction empirically. The reasoning above follows from the code paths.

## Q5. Telemetry: what is collected, is there an opt-out, and does the local backend phone home?

### Takeaway
**Yes, it phones home by default, even in local mode.** Telemetry is on unless `LETTA_CODE_TELEM=0` (or `false`) or `DO_NOT_TRACK=1` is set. Events go to `api.letta.com/v1/metadata/telemetry`. The payload includes the **full startup argv** (so `letta -p "<prompt>"` sends the prompt text), raw **tool stderr**, and, on errors, a **debug-log tail** and recent stream chunks. For an unpublished CMS-results vault, set `LETTA_CODE_TELEM=0` and `DO_NOT_TRACK=1` before first launch, and also `DISABLE_AUTOUPDATE`.

### Cited Findings
- [verified in source] `isTelemetryEnabled()` returns false only for `LETTA_CODE_TELEM` = `"0"` or `"false"`, or `DO_NOT_TRACK === "1"`. The comment says "Enabled by default unless explicitly disabled." — [SRC/src/telemetry/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/telemetry/index.ts)
- [verified in source] The flush does a `POST /v1/metadata/telemetry` with header `X-Letta-Code-Device-ID`. For non-desktop runs, `getMetadataRequestConfig` always uses `LETTA_CLOUD_API_URL`, whatever the backend. Events are tagged `backend: "local"`, but local backend is not a reason to skip sending. — [SRC/src/backend/api/metadata.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/api/metadata.ts), [SRC/src/telemetry/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/telemetry/index.ts)
- [verified in source] Event contents:
  - `session_start.startup_command = process.argv.slice(2).join(" ")`.
  - `user_input`: `input_length`, `is_command`, `command_name`, `model_id`, `channel`. This is length only, not the text.
  - `tool_usage`: `tool_name`, `success`, `duration`, `response_length`, `error_type`, and **`stderr`** (the raw joined stderr, from `tools/manager.ts`).
  - `session_end`: token and step counts.
  - Every event carries `session_id`, `agent_id`, `surface` and `backend`. Flushes run every 2 min.

  Sources: [SRC/src/telemetry/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/telemetry/index.ts), [SRC/src/tools/manager.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/tools/manager.ts)
- [verified in source] `trackError` sends only if `isCloudUser()`, which checks `getServerUrl().includes("api.letta.com")`. `getServerUrl()` falls back to `LETTA_CLOUD_API_URL` when `LETTA_BASE_URL` is unset, so a plain local-backend install counts as a "cloud user". Error events include `error_message`, `recent_chunks` and `debug_log_tail: debugLogFile.getTail()`, unless the caller passes `omitDebugLogTail`. — [SRC/src/telemetry/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/telemetry/index.ts), [SRC/src/backend/api/server-url.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/api/server-url.ts)
- [verified in source] The debug log file "Respects LETTA_CODE_TELEM=0 — skips file logging when telemetry is disabled." — [SRC/src/utils/debug.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/utils/debug.ts)
- [verified in source] The opt-in experiment `reflection_arena` (`LETTA_REFLECTION_ARENA`, off by default) is the most sensitive path. When used, it sends `transcript_payload` (up to 1,000,000 chars) in telemetry. If `HF_TOKEN` is set in env or agent secrets, it also git-pushes a vote row to the public Hugging Face dataset `letta-ai/reflection-arena`. — [SRC/src/cli/helpers/reflection-arena.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/helpers/reflection-arena.ts), [SRC/src/cli/helpers/reflection-arena-hf-upload.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/helpers/reflection-arena-hf-upload.ts), [SRC/src/experiments/manager.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/experiments/manager.ts)
- [verified in source] Other outbound calls:
  - The auto-updater queries `https://registry.npmjs.org`. It can be disabled with `DISABLE_AUTOUPDATE`, and the registry overridden with `LETTA_UPDATE_REGISTRY_BASE_URL`.
  - The remote model catalog is fetched from `LETTA_CLOUD_API_URL`.

  Sources: [SRC/src/updater/auto-update.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/updater/auto-update.ts), [SRC/src/agent/remote-model-catalog.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/remote-model-catalog.ts)
- [docs] The README and local-mode docs do not mention telemetry or `LETTA_CODE_TELEM`. Web searches turned up no Letta page documenting the opt-out. The local-mode page's "stays on-device" statement covers agent state only. — [README](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/README.md), [Local setup](https://docs.letta.com/letta-code/local-mode)
- [reported/third-party] A May 2026 static audit (v0.25.1) flagged "HIGH-3 Unfiltered Error Messages Sent to Cloud Telemetry". The issue is closed. — [#2212](https://github.com/letta-ai/letta-code/issues/2212)

### Inferences
- Error messages, stderr and debug-log tails can contain file paths, dataset names, yields or snippets of tool output. This is incompatible with the CMS confidentiality requirement unless telemetry is disabled. Verify with an egress firewall or a mitmproxy run. Auto-update is a second reason to pin versions.

### Gaps
- I did not inventory exactly what `debugLog` writes, so I can't say how much conversation content reaches the debug-log tail.
- I did not check whether `LETTA_CODE_TELEM=0` also suppresses the remote model-catalog fetch. It probably does not, since the fetch is separate code.

## Q6. How well does it work with small, open or free models (Ollama, Nemotron, Qwen)?

### Takeaway
Ollama, LM Studio, llama.cpp, generic OpenAI-compatible endpoints, OpenRouter (API key or OAuth) and Ollama Cloud are first-class providers. All requests go through pi-ai's `openai-completions` with native function calling. I found no text or XML tool-call fallback. The roughly 15k-token base prompt and the 60 s stall timeout are both hostile to a 6 GB-VRAM laptop running 7–8B models. Users report stalls, capability misdetection and context clamps.

### Cited Findings
- [verified in source] The BYOK provider list includes `openai-compatible`, `openrouter`, `openrouter-oauth`, `ollama`, `ollama-cloud`, `lmstudio`, `gemini`, `zai`, `moonshot`, `minimax` and `bedrock`. — [SRC/src/providers/byok-providers.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/providers/byok-providers.ts)
- [verified in source] The OpenAI-compatible provider discovers models via `GET {base}/models`. "capabilities remain conservative because the OpenAI model-list schema does not report them". It returns a `Provider<"openai-completions">`. — [SRC/src/backend/dev/pi-openai-compatible-provider.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/pi-openai-compatible-provider.ts)
- [verified in source] The Ollama provider reads the served context window from `/api/ps` (needs Ollama ≥ 0.10.0) and errors if it can't verify it. It reads capabilities (`completion`, `vision`, `tools`, `thinking`) from Ollama metadata. — [SRC/src/backend/dev/pi-ollama-provider.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/dev/pi-ollama-provider.ts)
- [docs] For slow local servers there is a per-provider `--timeout` (e.g. `--timeout 600s`) and `--no-timeout`. — [Local setup / docs search summary](https://docs.letta.com/letta-code/local-mode)
- [reported/third-party] Reported issues:
  - #4650 (open): Ollama turns stall with qwen3:8b, qwen2.5-coder:7b and llama3.2.
  - #4081 (open): Ollama Qwen3.8 reasoning control is hidden and the configured effort is ignored.
  - #2541 (closed): local OpenAI-compatible providers misdetect capabilities by model-ID substring. Vision was silently dropped, the context fell back to 128K, and the reasoning flag was wrong.
  - #2791 (closed): local helper subagents resolved to llama2.
  - #3409 (open): an OpenAI-compatible endpoint passed the connection test but was rejected at runtime.

  Sources: [#4650](https://github.com/letta-ai/letta-code/issues/4650), [#4081](https://github.com/letta-ai/letta-code/issues/4081), [#2541](https://github.com/letta-ai/letta-code/issues/2541), [#2791](https://github.com/letta-ai/letta-code/issues/2791), [#3409](https://github.com/letta-ai/letta-code/issues/3409)
- [reported/third-party] #4962 ran production on self-hosted Qwen3.8-27B-AWQ via vLLM + LiteLLM with a 131k context. So mid-size open models work, with the bugs noted in Q1. — [#4962](https://github.com/letta-ai/letta-code/issues/4962)

### Inferences
- NVIDIA NIM (build.nvidia.com) and OpenRouter `:free` should connect through the `openai-compatible` or `openrouter` providers, provided the model supports OpenAI-style `tools`. Free tiers with rate limits or missing tool support will break the agent loop.
- On 6 GB VRAM you would need `--no-skills`, `--no-bundled-skills`, a reduced `--toolset`, a raised `LETTA_STREAM_STALL_RECONCILE_MS` and a small `context_window_limit` to be usable at all.
- Compaction summaries also run on the agent's model (configurable via `compaction_settings.model`), which adds load.

### Gaps
- I found no Nemotron-specific or OpenRouter `:free`-specific reports in the issue tracker.
- I did not confirm whether pi-ai has any parsing fallback for models that emit tool calls as text.

## Q7. Subagent and multi-agent mechanics

### Takeaway
Custom subagents are Markdown files with YAML frontmatter in `.letta/agents/` (project) or `~/.letta/agents/` (global). The frontmatter sets `name`, `description`, `tools`, `model`, `skills`, `fork` and `launchProfile`, and the body is the system prompt. Non-fork subagents start fresh, with the system prompt plus the task prompt. `fork: true` copies the parent conversation. Nesting is capped at depth 2. A deterministic Workflow tool runs scripted `agent()` calls in ephemeral contexts. Worktrees are per-conversation, through EnterWorktree and ExitWorktree. An orchestrator/worker/reviewer split maps onto this reasonably well.

### Cited Findings
- [verified in source] The `SubagentConfig` fields are `name, description, systemPrompt, allowedTools ("all" | list), recommendedModel ("inherit" default), skills, fork, launchProfile`. The frontmatter parser reads `description`, `tools`, `model`, `skills`, `fork` and `launchProfile`. I did not find `memoryBlocks` parsed. — [SRC/src/agent/subagents/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/subagents/index.ts)
- [verified in source] The built-ins in source are `fork, general-purpose, init, memory, recall, reflection`, plus v2 variants of init, memory and reflection. — [SRC/src/agent/subagents/builtin/](https://github.com/letta-ai/letta-code/tree/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/subagents/builtin)
- [docs] The docs list "seven built-in subagent types", including `history-analyzer`, which is absent from the source. The docs also list a `memoryBlocks` frontmatter field. Both are drift between docs and code. The docs say built-ins are "created fresh on each invocation", except `fork`, which "forks the parent conversation with its full context and tools". Background mode is supported, and a completion notification is injected. — [Subagents](https://docs.letta.com/letta-code/subagents)
- [verified in source] `MAX_SUBAGENT_DEPTH = 2`. The Task tool schema takes `description, prompt, subagent_type, model, agent_id, conversation_id, computer, mcp`. Deploying an existing agent requires `subagent_type` `general-purpose`. Subagents run as separate processes (`subagent-process.ts`, with `LETTA_CODE_AGENT_ROLE=subagent` making them stateless). Reflection subagents get a capped parent-memory snapshot (16k-token startup budget). — [SRC/src/agent/subagents/subagent-depth.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/subagents/subagent-depth.ts), [SRC/src/tools/schemas/Task.json](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/tools/schemas/Task.json), [SRC/src/agent/subagents/context-budget.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/subagents/context-budget.ts), [SRC/src/cli/args.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/args.ts)
- [verified in source] The Workflow tool "launches a workflow script that orchestrates multiple subagents deterministically". Each `agent()` runs in an agent-free ephemeral conversation via `@letta-ai/letta-agent-sdk`, in the background, with completion notifications. — [SRC/src/tools/impl/workflow.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/tools/impl/workflow.ts)
- [verified in source] `EnterWorktree` creates or enters worktrees under `.letta/worktrees/` for the current conversation. The Task schema has no per-subagent `isolation` parameter. There are also `external-coding-agent` descriptors that run the Claude Code or Codex CLIs as workers. — [SRC/src/tools/schemas/EnterWorktree.json](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/tools/schemas/EnterWorktree.json), [SRC/src/agent/subagents/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/agent/subagents/index.ts)
- [verified in source] `environmentRouting` (routing subagent turns to other computers) is Cloud-only. — [SRC/src/backend/backend.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/backend.ts)

### Inferences
- Fresh-context workers and reviewers fit the user's design well: each worker gets only the prompt the orchestrator writes. The orchestrator itself, though, still has Letta's append-and-compact history (Q2/Q3).
- Per-subagent `model` allows cheap free models for workers and a stronger model for the reviewer.

### Gaps
- I did not verify how `fork` interacts with local compaction, or how per-subagent model resolution behaves on local-only provider catalogs (#2791 suggests it was buggy).

## Q8. Release cadence and breaking changes

### Takeaway
Releases come out extremely fast: 100 GitHub releases between 2026-07-23 (v0.28.17) and 2026-10-08 (v0.34.7), about 9 a week and often several a day. Minor bumps come roughly every 1–2 weeks, and auto-update is on by default. Pin versions and set `DISABLE_AUTOUPDATE`.

### Cited Findings
- [verified via GitHub API] There were 100 releases from v0.28.17 (2026-07-23) to v0.34.7 (2026-10-08). v0.34.5, v0.34.6 and v0.34.7 all shipped on 2026-10-08. Minor versions: v0.31.0 on 08-26, v0.32.0 on 09-09, v0.33.0 on 09-23, v0.34.0 on 09-30. — [Releases](https://github.com/letta-ai/letta-code/releases)
- [verified in source] Examples of breaking or migration churn:
  - MemFS became mandatory ("All user-facing agents are memfs-enabled unconditionally"). `--no-memfs` is now a hidden no-op, because auto-update version skew between a parent and its child "broke reflection subagents (LET-9436)".
  - A `letta local-backend migrate-transcripts` subcommand exists for storage-format migration.
  - MemFS v2 budgets were enforced in v0.32.0.

  Sources: [SRC/src/backend/local/paths.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/backend/local/paths.ts), [SRC/src/cli/args.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/cli/args.ts), [SRC/src/index.ts](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/src/index.ts), [v0.32.0 release](https://github.com/letta-ai/letta-code/releases/tag/v0.32.0)
- [reported/third-party] #3482: the standalone bundle could not load OAuth flows after the pi-ai 0.81 migration. #4995: `letta model get` added an extra `provider/` prefix for mod-registered providers (fixed 10-08). — [#3482](https://github.com/letta-ai/letta-code/issues/3482), [#4995](https://github.com/letta-ai/letta-code/issues/4995)
- [verified in source] The license is Apache-2.0, so a fork is legally straightforward. — [SRC/LICENSE](https://github.com/letta-ai/letta-code/blob/3a958a40c3484f69c4812049a14a09368cc13ee5/LICENSE)

### Inferences
- A fork carrying a custom turn-assembly patch will face constant rebase pressure, since the core backend files change weekly.

### Gaps
- There is no formal changelog section for breaking changes. Release notes are auto-generated PR lists, so I could not compile a complete list of breaking changes.

## Overall fit for the user's plan (inference, combining Q1–Q8)

**Strong fit:**
- Apache-2.0 licence.
- Fully local state with git-backed markdown memory, which is conceptually close to an Obsidian vault.
- Any OpenAI-compatible, Ollama or OpenRouter model can be used.
- Fresh-context subagents, custom subagents and a deterministic Workflow tool.
- Append-only transcripts on disk that external RAG can index.

**Poor fit:**
- Its central design is the opposite of "rebuild fresh context per turn".
- No supported hook can replace history selection; you need a fork or a proxy.
- Proxy truncation confuses its usage-anchored compaction.
- Telemetry is on by default, ships argv, stderr and debug tails to api.letta.com even in local mode, and is undocumented.
- The roughly 15k-token base prompt plus the 60 s stall timeout fight small local models.
- Very fast churn.

**If adopted:** set `LETTA_CODE_TELEM=0`, `DO_NOT_TRACK=1` and `DISABLE_AUTOUPDATE=1`; pin the version; do context building in a local proxy or a small fork of `HeadlessBackend` turn assembly; and use subagents and workflows for fresh-context workers and the reviewer.
