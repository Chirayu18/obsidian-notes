---
name: cswap-service-pr
description: User's PR realiti4/claude-swap#527 adds `cswap auto --install-service` (Linux systemd user unit); the running cswap-auto service on the laptop points at the BRANCH venv, reinstall after merge
metadata:
  type: project
---

PR https://github.com/realiti4/claude-swap/pull/527 (opened 2026-10-29; #526 was closed by the user's request for more testing). Branch `feat/linux-auto-service` on fork Chirayu18/claude-swap, clone at ~/src/claude-swap, one squashed commit, Codex reviewed three times (READY), real-machine install + SIGKILL restart tested.

2026-10-29 state: the branch is installed as the uv tool (`uv tool install --force ~/src/claude-swap`, reports 0.30.0b1), and `cswap-auto.service` runs `~/.local/bin/cswap auto`. A plain `cswap upgrade` before the merge would drop `--install-service` but the running unit keeps working. Both accounts were re-added with `cswap add` (the dead-token status had blocked auto-switching: usage unreadable). Set `autoswitch.weeklyThreshold 97` because the default hysteresis refused a target at 7d 89% vs line 90; first proactive switch gmail -> vub.be verified 18:08. Upstream PR texts: plain prose, no Claude attribution ([[Meta/claude-memory/_history/general/vault/no-claude-attribution-plain-prose|no-claude-attribution-plain-prose]]).
