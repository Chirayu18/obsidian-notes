---
tags: [reference]
status: active
date: 2026-11-06
source: laptop
---

# Native T3 account preparation — migration not completed

**Agent-reported implementation record. Recommendation: move explicit account selection into T3, retain cswap during transition, and keep it if same-thread Claude account switching is required.** Separate Claude config homes cannot continue the same thread. Native T3 usage displays also do not yet replace the agent-readable quota checks in the current role briefs. See the [design review](2026-11-06-t3-account-and-environment-design.md).

Chirayu requested “continue”, then asked whether to use or move away from cswap. No further account changes or pilot restart were made after that question. This record supersedes the [preceding applied configuration](2026-11-06-cswap-t3-account-setup.md); its remote preparation details remain historical evidence.

## Applied and checked

- In `~/.t3/userdata/settings.json`, preserved existing `claudeAgent` ID and default home; renamed its display label to **Claude 1 (laptop default; cswap follows)**. This provider still follows any cswap change to the default login.
- Added enabled provider `claude_account2`, driver `claudeAgent`, display label **Claude 2 (laptop)**, binary `/home/cgupta/.local/bin/claude`, `homePath: /home/cgupta/.claude-t3-2`.
- Created that separate profile directory with owner-only permissions. Copied no credentials, settings, hooks or conversation state into it. Its global configuration therefore does not inherit the default Claude profile's laptop connection hook; project-local instructions/settings remain separate.
- Preserved every other provider and top-level setting. A private backup is `~/.t3/userdata/account-setup-backups/settings-before-native-claude2-20261106-143457.json` (UTC filename). Read-back assertions confirmed the intended changes. T3 UI reload and successful inference through this new entry remain unverified.
- Added [login-laptop-claude2.sh](../scripts/t3/login-laptop-claude2.sh), a human-terminal helper using the same config home and subscription login. Shell syntax check passed. It has not been run in login mode.

Sanitized direct `claude auth status` checks found the **laptop default signed in**, **laptop account 2 not signed in**, and **both remote prepared profiles not signed in**. Checks used the existing SSH master and reached `lxplus977.cern.ch`; no CERN authentication renewal occurred. No model request or credential copying was performed.

The remote pilot server is stopped: remote port 3783 was closed. Laptop port 3783 remains held by the existing SSH master PID 5991, and its environment descriptor request reset. A listening local port is therefore not evidence that this pilot is ready. Nothing was killed or restarted. Before a later pilot start, inspect/cancel only the stale pilot forwarding through supported SSH multiplex control, or choose an unused forwarding port consistently; do not restart the EOS service or terminate the shared master.

## Remaining decisions and human steps

1. Decide whether fresh-thread Claude account handoffs are acceptable. If not, keep cswap as the active switching mechanism.
2. For native account 2, run `bash scripts/t3/login-laptop-claude2.sh` from the vault in a laptop terminal, selecting the intended second account. Keep OAuth codes in the terminal/browser. Then verify the reported identities differ and check per-account T3 Usage → Limits before a bounded test.
3. Additional ChatGPT connections require the user-controlled **Settings → Providers → Add ChatGPT account** flow. Existing Codex configuration was preserved. Do not bulk-authorize accounts on temporary lxplus state.
4. Keeper must replace the role briefs' cswap quota dependency before removing cswap. No keeper-owned files were edited and no uninstall is proposed now.
5. Resume the short SSH-only synthetic lxplus pilot with one approved remote login only when ready. The current setup has not passed an end-to-end agent test.

Rollback needs only restoring the two changed provider entries from the private backup while retaining unrelated subsequent settings. Do not overwrite the whole current file blindly or delete account profiles. No push was performed.

Version-matched primary sources: [T3 Claude account guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-claude.md), [T3 ChatGPT account guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-codex.md), and [T3 usage display](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/usage.md). Native environment-link listing was attempted again but remains unavailable as a callable tool here.
