---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---

# Short SSH-only lxplus T3 pilot

**Agent-reported status: backend and SSH transport tested; account sign-in, client pairing and the model-driven edit remain pending.** This is the latest readiness snapshot, extending [the checklist](2026-11-05-lxplus-t3-checks-and-project-routing.md) and superseding [the earlier readiness snapshot](2026-11-05-lxplus-t3-readiness-checks.md). Prior deletion/storage details remain there. No job submission, credential copying/renewal, account switch, cloud tunnel, persistent service, analysis change or Git push was performed in this pilot setup.

## Authorization and account preference

Chirayu requested, verbatim:

> step by step instructions for the test for only the things u cant do , otherwise do  what u can

In response to the question whether CERN/lxplus support had confirmed the short runtime/model-service pilot, Chirayu selected:

> Confirmed for a short SSH-only pilot

This is Chirayu's confirmation; this agent did not inspect a CERN ticket or contact support. It authorizes the short SSH-only pilot, not an unattended deployment.

Chirayu subsequently asked about reusing the laptop Claude login and keeping it synchronized with cswap, then clarified:

> Basically if t3 can take care of multiple claude accounts and all then its fine

T3 v0.1.6 supports separate Claude provider entries backed by separate `CLAUDE_CONFIG_DIR` logins. Account selection is supported; automatic quota rotation equivalent to cswap was not established. Provider credentials remain host-specific. No laptop credentials or cswap accounts were exported, imported, copied or switched. [T3 multi-account documentation](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-claude.md#separate-accounts-or-configurations)

## Implemented and checked

- Created an owner-only temporary root, `/tmp/cgupta-t3-pilot-20261105-hgv57rp7`, on **lxplus938.cern.ch**. Its mode was checked as `0700`. The earlier `findmnt` check identified node-local ext4 under `/tmp`; this directory is temporary and node-specific. It is not a durable production state location.
- Copied the laptop's matching **T3 0.1.6** public runtime into its `runtime/` subdirectory, without running an installer or downloading a runtime from CERN. Local and remote executable SHA-256 matched: `45edbf73a2d2a0417f0c75a5dac9d54156b150ecf5b70c38e957fe3197ffebbf`. Remote `t3 --version` returned `t3 v0.1.6`; `serve --help` and `pair --help` succeeded. The packaged runtime works for these operations despite the older system Node version observed earlier.
- Put runtime state under `state/userdata/` using the verified `--base-dir` option and `T3CODE_HOME`. The database exists there; `~/.t3` remained absent in the latest check at **13:43:30 UTC**. No home-directory T3 install was made.
- Started a foreground SSH-owned server with `serve --host 127.0.0.1 --port 3783 --base-dir .../state`. Remote `ss -ltnp` confirmed only `127.0.0.1:3783` listening. SSH forwards laptop `127.0.0.1:3783` to the same remote loopback port. There is no LAN/public listener, Connect tunnel, systemd unit or lingering change.
- The server's initial process metadata records start **2026-11-05 13:38:48 UTC**, server PID `2395167`, supervisor PID `2395054`. The supervisor stops only this test-owned server after **1800 seconds from readiness**, approximately **14:09 UTC**, or when its supervising SSH process is interrupted. No automatic restart was configured. Temporary files are retained.
- From the laptop, both the public environment descriptor and UI root returned **HTTP 200** through the SSH forward. Descriptor identity matched remote **environment ID `4f48bd00-e812-40bc-83d6-4b4e6360bf53`**, version `0.1.6`. Secrets in the server's startup output are confined to owner-only `server.log`; they were not printed into tool/chat output or copied into the vault.
- Registered synthetic project **`lxplus-toy-pilot`**, ID **`c25f1a87-cf09-45f3-a0b1-baa0578c6a78`**, at `/tmp/cgupta-t3-pilot-20261105-hgv57rp7/workspace`. Registration was independently checked in the temporary database. `serve` did not auto-register the workspace despite the supplied auto-bootstrap flag, so the version-matched `project add` command was used explicitly.
- The synthetic fixture source is under [t3-lxplus-pilot](t3-lxplus-pilot/labels.py): invented labels, one deliberate normalization bug, and checks for blanks, whitespace, case and Unicode case folding. `python3 -B check_labels.py` fails at the expected assertion both locally and remotely. This is the intended baseline, not a failed infrastructure check. No model has fixed it yet.
- Remote `claude auth status` returned code **1**, `loggedIn=false`, `authMethod=none`, `apiProvider=firstParty`. Only those fields were emitted; no credential or identifying account data was printed. No login or model request was made.

## What requires Chirayu

1. **Authenticate one approved Claude account on lxplus.** In a laptop terminal, run:

   ```bash
   ssh -t lxplus '~/.local/bin/claude auth login'
   ```

   Complete the browser/terminal flow yourself. Do not paste codes, tokens or credential files into chat. Later accounts can use separate remote config directories and separate T3 provider entries; this first pilot needs only one.

2. **Pair your T3 client to this SSH-forwarded server.** While the temporary server/forward is still running, run the prepared helper in your laptop terminal:

   ```bash
   bash /home/cgupta/obsidian-notes/Projects/t3-lxplus-pilot/pair-pilot.sh
   ```

   It runs the verified `t3 pair` command on lxplus and prints a fresh pairing URL/code only in that terminal. Its TTL is ten minutes. In T3's **Settings → Environments → Add environment**, use that pairing URL/code. Its endpoint is laptop loopback `127.0.0.1:3783`, reached through the existing SSH forward. Do not select the SSH auto-installer for this already-staged server. The helper requests the listed orchestration/provider/terminal/file/diagnostic scopes; it does not request cloud relay management. Terminal/agent access still has the authority of the remote user, not OS confinement to the toy directory. Set the worker's mode separately.

   This session's `t3_environment_links` and `t3_environment_link` tools were each attempted and are not callable (`TypeError: ... is not a function`). Native desktop control is unavailable here. The helper was syntax-checked with `bash -n`; it has not been executed, so no fresh pairing secret was minted by it during this setup.

3. **Start the visible toy worker from the paired environment.** Choose project `lxplus-toy-pilot`, the approved Claude account and **Supervised** explicitly. Send:

   > Follow AGENTS.md. Fix labels.py so python3 -B check_labels.py passes. Keep the checks unchanged. Work only in this synthetic directory; no network, credentials, jobs, installs or commits. Report hostname, working directory, diff and check result.

   A completed pilot requires the expected supervision prompts, the edit on lxplus, a passing unchanged check, and identity/path confirmation. This is pending; backend success is not a completed agent-workflow test. Afterward the parent discussion can independently inspect the diff and rerun the check over SSH. Keep one worker globally; conductor and keeper remain on the laptop.

If the server has expired, report that rather than rerunning a general installer; the existing runtime and toy workspace can be restarted explicitly on the same node. Do not treat `/tmp` identity/state as permanent or reconnect a second node to a shared live database. Removing this temporary setup or configuring persistent runtime ownership is outside this short pilot.

## Still unverified

Actual model-account access, account quota/selection behavior in T3, supervision behavior, agent editing, client reconnection after pairing, and durable deployment/storage. No cswap synchronization was implemented. The existing AFS cleanup left approximately **2.33 GiB free**, per the earlier quota snapshot, but this pilot keeps T3 state off AFS. The transport and runtime observations above do not validate permission for a persistent deployment.
