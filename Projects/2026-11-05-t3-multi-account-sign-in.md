---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---

# Signing two Claude accounts and ChatGPT accounts into T3

**Agent-reported instructions, checked against installed CLI help and T3 v0.1.6 documentation.** No account was signed in, switched or copied by the agent. This guide uses fresh Claude config directories so the existing default Claude/cswap configuration is not overwritten. T3-managed ChatGPT sign-in avoids requiring a separate Codex CLI install.

Chirayu requested:

> Gimme instructions to 1 . Sign into both my claude accounts here, and 2. On lxplus (along with my chatgpt accounts)

## Laptop: two Claude accounts

In a laptop terminal, create the separate directories:

```bash
mkdir -m 700 -p "$HOME/.claude-t3-1" "$HOME/.claude-t3-2"
```

Run the first login and complete it as account 1:

```bash
CLAUDE_CONFIG_DIR="$HOME/.claude-t3-1" claude auth login
```

Then run the second login and complete it as account 2:

```bash
CLAUDE_CONFIG_DIR="$HOME/.claude-t3-2" claude auth login
```

Check which web account the browser selects each time; use the intended browser profile or change the selected account before approving. Keep returned codes in the terminal/browser, not chat.

In T3 **Settings → Providers**, select the **laptop/cgupta environment**. Add two Claude entries:

| Entry | Binary path | CLAUDE_CONFIG_DIR path |
| --- | --- | --- |
| Claude 1 | `/home/cgupta/.local/bin/claude` | `/home/cgupta/.claude-t3-1` |
| Claude 2 | `/home/cgupta/.local/bin/claude` | `/home/cgupta/.claude-t3-2` |

Use T3's dedicated config-directory field, not launch arguments or a changed HOME. Refresh provider status and verify that the two entries report different intended accounts. T3 documents account isolation through config directories. Existing Claude threads can switch only between entries using the same config directory; select the desired separate account when creating a new thread. [T3 Claude accounts](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-claude.md#separate-accounts-or-configurations)

## lxplus: two Claude accounts

From the laptop, enter the existing SSH connection:

```bash
ssh -t lxplus
```

Run these inside that remote terminal, completing each login separately:

```bash
mkdir -m 700 -p "$HOME/private/claude-t3-1" "$HOME/private/claude-t3-2"
CLAUDE_CONFIG_DIR="$HOME/private/claude-t3-1" "$HOME/.local/bin/claude" auth login
CLAUDE_CONFIG_DIR="$HOME/private/claude-t3-2" "$HOME/.local/bin/claude" auth login
```

Open any printed login URL on the laptop and finish the flow in the remote terminal. Then `exit` returns to the laptop shell.

The agent checked `fs listacl /afs/cern.ch/user/c/cgupta/private`: rights are granted only to `cgupta` and `system:administrators`. These paths use that existing private directory. The mkdir commands above were not run by the agent; no ACLs were changed.

Once the [pilot environment is paired](2026-11-05-lxplus-t3-pilot.md), choose that **lxplus environment** in T3's provider settings. Add:

| Entry | Binary path | CLAUDE_CONFIG_DIR path |
| --- | --- | --- |
| Claude 1 | `/afs/cern.ch/user/c/cgupta/.local/bin/claude` | `/afs/cern.ch/user/c/cgupta/private/claude-t3-1` |
| Claude 2 | `/afs/cern.ch/user/c/cgupta/.local/bin/claude` | `/afs/cern.ch/user/c/cgupta/private/claude-t3-2` |

Check account identity in both entries. A login in one environment is not an automatic login in the other. Separate new config directories also have separate user settings/hooks; do not copy laptop connection hooks onto lxplus. Project instructions/settings still need to be appropriate for each workspace.

## ChatGPT accounts: T3-managed sign-in on each environment

Use **Settings → Providers → Connect with ChatGPT**. T3 handles its Codex runtime installation. Select laptop first, sign into the first ChatGPT account, grant the displayed plan-sharing permission, then use **Add another ChatGPT account** and authenticate the second. Verify the reported account and use distinct labels.

Repeat with **lxplus selected**, once the remote environment is paired. Sign into the same intended ChatGPT accounts for that host. If the remote browser return cannot load localhost, T3 documents pasting the full final callback URL into its sign-in panel. Keep that URL out of chat; it belongs only in the T3 sign-in panel. [T3 Codex/ChatGPT sign-in and multiple accounts](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-codex.md)

This is ChatGPT-plan authentication through T3, not an API-key setup. Do not paste an API key into the flow or copy `auth.json`. Separate account registrations must retain separate credentials; the application's active account should be checked before use. [Official OpenAI account/session guidance](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions)

**Temporary pilot caveat:** lxplus T3 state/provider registrations are currently under `/tmp/cgupta-t3-pilot-20261105-hgv57rp7/state`. The server/SSH forward is time-limited, and node-local files may be cleaned. Claude credentials in the separate private AFS directories are distinct from that temporary T3 state. T3-managed ChatGPT registrations/provider entries may need to be repeated when a durable environment/state location is chosen. Prefer finishing the single-account pilot before repeating every remote account registration if avoiding reauthorization work matters.

## Verification and cswap behavior

Before using an entry, confirm the selected environment, provider account and workspace. For the synthetic pilot choose Supervised and only one worker globally. No account-specific model request or quota entitlement was tested by this sign-in guide.

The new named T3 Claude configurations do not automatically follow switches in the laptop's default cswap configuration. cswap remains available for the existing default login. This guide does not implement account replication or automatic quota rotation. T3's support for multiple entries should not be read as a claim of cswap-equivalent rotation.
