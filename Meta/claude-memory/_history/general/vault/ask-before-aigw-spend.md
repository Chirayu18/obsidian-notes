---
name: ask-before-aigw-spend
description: "Ask the user before ANY aigw (CERN AI Gateway) usage for agent runs or judging, including self-hosted Qwen; give a cost/token estimate"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4802996e-67e1-456e-b436-0c4812daa983
  modified: 2026-10-21T15:33:26.253Z
---

Before spending any budget on CERN's models (aigw: GPT-5.6 luna/terra/sol AND self-hosted Qwen), ask the user first with a concrete scope and estimate (runs, tokens, $ from the opencode.json cost table).

**Why:** user said (2026-10-21) "before you spend any budget for cern's models, ask me". The OpenAI models share a $1000/month CERN-wide budget with throttling (ML Mattermost channel), so heavy eval runs affect other users.

**How to apply:** plan the matrix, estimate, ask via AskUserQuestion, then run. Prior approval for one batch does not carry to the next. Agent runs go through lxplus, so eduVPN is not needed for them. Related: [[Meta/claude-memory/_history/slides/vault/acat2027-combine-agent-talk|acat2027-combine-agent-talk]].
