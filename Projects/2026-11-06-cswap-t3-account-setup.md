---
tags: [reference]
status: active
date: 2026-11-06
source: laptop
---

# cswap inspection and T3 account setup

**Design follow-up:** Chirayu clarified that both laptop accounts should be directly accessible in T3 without needing cswap. See [the reconsidered design](2026-11-06-t3-account-and-environment-design.md) before following the recovery steps below. This file records the applied cswap-backed configuration; no migration to independent native laptop accounts is claimed.

**Agent-reported status: laptop integration configured and checked; remote entries/server prepared; human sign-ins remain pending.** This supersedes the prior [pilot snapshot](2026-11-05-lxplus-t3-pilot.md) and [generic sign-in guide](2026-11-05-t3-multi-account-sign-in.md) as instructions for the setup actually chosen here. Earlier storage/deletion records remain historical evidence. No credentials were printed, exported, copied between machines or committed. No real account switch, interactive sign-in, model request, CERN credential renewal, job submission, persistent service or Git push was performed.

Chirayu requested, verbatim:

> Umm check my cswap setup and can you do the setup for me?

## cswap observations

- Installed `cswap` is **0.30.0b1**, located at `~/.local/bin/cswap`, backed by the uv tool environment under `~/.local/share/uv/tools/claude-swap/`.
- Account metadata is in `~/.local/share/claude-swap/sequence.json`, with two slots. The legacy `~/.claude-swap-backup` directory is absent. An initial sandboxed status call failed on cswap's routine migration-marker cleanup; the supported CLI worked outside the sandbox. This was not treated as a broken account store.
- Supported `cswap list --json`, captured and filtered without emitting emails/organization identifiers, reports **slot 1 active and `usageStatus=ok`**; its five-hour usage was **0%**, seven-day usage **65%** at inspection. **Slot 2 reports `usageStatus=relogin_required`**, with no usable usage reading. No retry or forced activation of slot 2 was attempted.
- Existing settings include `autoswitch.weeklyThreshold=97.0`; this and all switching preferences were left unchanged. A process inventory found no `cswap auto` process at that instant; this is not a guarantee about future runs or other launch mechanisms.
- Direct `claude auth status`, with identifying fields compared only inside the process, confirmed an authenticated default login matching cswap slot 1. No model inference was invoked to establish that observation.

Installed source and [the upstream cswap documentation](https://github.com/realiti4/claude-swap) were inspected. Its session mode deliberately avoids duplicating the active default credential; copying a refresh-token lineage to independent stores can drift after rotation. The chosen laptop integration therefore keeps the default profile as the source of truth rather than cloning slot 1 into another login directory.

## Laptop changes

Updated only the existing `claudeAgent` entry in `~/.t3/userdata/settings.json`:

- Display name: **Claude (cswap active account)**.
- Binary path: `/home/cgupta/.local/bin/claude`.
- Config home remains the existing default: no custom `homePath` was set. Thus the ordinary cswap-managed login remains the one used by this T3 entry.

All other provider entries and settings were preserved. A private pre-change backup is at `~/.t3/userdata/account-setup-backups/settings-before-cswap-20261106-142203.json` (the filename uses laptop local time). The update used an atomic replacement and refused a concurrent modification. T3's native `orchestrator_capabilities` subsequently reported the new display name for `claudeAgent`, validating live settings reload without a restart.

This is a cswap-managed pool exposed through one default T3 Claude entry. It does not create two independently authenticated laptop T3 instances or claim T3 implements cswap's automatic rotation. Existing Codex/ChatGPT and Pi entries were not changed.

## Resumed remote setup

The current ControlMaster reaches **lxplus977.cern.ch**. Yesterday's root `/tmp/cgupta-t3-pilot-20261105-hgv57rp7` was absent on this node and port 3783 was not listening. That does not imply the directory is absent from every lxplus node; it demonstrates why node-local state cannot be treated as a shared durable environment.

Created two owner-only directories under the existing private AFS tree:

- `/afs/cern.ch/user/c/cgupta/private/claude-t3-1`
- `/afs/cern.ch/user/c/cgupta/private/claude-t3-2`

No credentials were seeded into either. The account/path manifest `~/private/t3-account-setup.json` holds non-secret provider configuration and the current pilot node/root.

Prepared a new node-local root, **`/tmp/cgupta-t3-pilot-20261106-qucyawnc`**, and restored the matching T3 0.1.6 public runtime plus the synthetic fixture. No home-directory runtime installation was made. Its `state/userdata/settings.json` has enabled entries **Claude 1 (lxplus)** and **Claude 2 (lxplus)**, with `homePath` set to the corresponding private AFS profile and binary `~/.local/bin/claude`.

Started [run-lxplus-pilot.py](../scripts/t3/run-lxplus-pilot.py) as an SSH-owned foreground test, bounded to **1800 seconds after readiness**. Server start metadata: **2026-11-06 13:25:35 UTC**, remote supervisor PID **3941130**, server PID **3941241**. It binds remote loopback **127.0.0.1:3783**, forwarded to the same laptop loopback port. No LAN listener, cloud tunnel, systemd install or lingering change was requested.

Validated current environment **`bfb0877b-5e88-4c11-a8c2-7da8f98266a7`**, T3 version **0.1.6**, using the public loopback descriptor. Registered **lxplus-toy-pilot**, project ID **`bd210363-72fe-4374-b6d0-92caac033b45`**, at the root's `workspace/`. Both configured profile directories exist. `claude auth status` in each profile returns **loggedIn=false**; that is the remaining remote authentication step. The synthetic check still fails at its intentional baseline assertion. No agent has edited it yet, and default `~/.t3` remained absent.

## Prepared helpers and the remaining user actions

All commands below run in a **laptop terminal**, starting in `/home/cgupta/obsidian-notes`.

1. Recover cswap account 2:

   ```bash
   python3 scripts/t3/recover-cswap-account2.py
   ```

   Complete the browser flow as account 2 while Claude turns are idle. The helper verifies the selected account/workspace against slot 2 before calling supported `cswap add --slot 2`; it then uses supported `cswap switch` to restore the previously active slot. It never copies token files. On cancelled/wrong-account/wrong-workspace/add failures it does not report success and attempts restoration; restoration failure is an explicit error. It was **not run in real login mode**. Its `--check` mode passed against the current default account.

2. Sign into the two prepared lxplus profiles, one at a time:

   ```bash
   bash scripts/t3/login-lxplus-claude.sh 1
   bash scripts/t3/login-lxplus-claude.sh 2
   ```

   Complete each browser/terminal flow with the intended account. These obtain independent remote logins; they do not clone laptop refresh tokens or make cswap switch both machines in lockstep.

3. Pair the resumed environment, while the temporary server is running:

   ```bash
   python3 scripts/t3/pair-lxplus-pilot.py
   ```

   Use its URL/code in T3 **Settings → Environments → Add environment**. Codes print only in that terminal. The helper reads the current private manifest and refuses if SSH reaches another node. Its `--check` mode passed without minting a pairing code. The old `Projects/t3-lxplus-pilot/pair-pilot.sh` now delegates to this helper, so it no longer hardcodes yesterday's missing path.

Native `t3_environment_links` and `t3_environment_link` were each attempted and remain unavailable in this session. Browser authentication and client pairing are therefore the remaining user-controlled operations. Account approvals for any additional ChatGPT accounts also remain user-controlled in T3; no existing ChatGPT connection was replaced by this task.

After sign-ins/pairing, account identity and cswap slot 2 must be rechecked before calling either usable. The toy worker should use **Supervised**, one worker globally, and only the synthetic directory. Conductor/keeper stay on the laptop. The resumed runtime expires approximately thirty minutes after readiness; private account profiles/manifest persist on AFS, but live T3 state is still temporary.

## Validation

- T3 live provider name and direct default Claude identity checks passed.
- Remote provider/path/status checks and environment descriptor check passed; both remote logins remain pending.
- Six mocked recovery-flow scenarios passed: success, wrong account, wrong workspace, cancellation, cswap-add failure and restoration failure. Tests used invented metadata and did not invoke real OAuth or account mutation.
- Python parsing, shell syntax and authored-diff whitespace checks passed. Helpers that start login or mint pairing codes were not executed in those modes. No end-to-end model test is claimed.
