---
tags: [reference]
status: active
date: 2026-11-06
source: laptop
---

# lxplus Claude 2 pilot — authenticated backend ready

**Agent-reported checks:** remote Claude profile 2 is authenticated and the bounded SSH-only T3 backend is running. Pairing and an end-to-end agent edit are still pending. Chirayu reports that the laptop account test passed; that inference result was not independently observed here.

This continues the [native account preparation](2026-11-06-native-t3-account-preparation.md) and [account/environment design](2026-11-06-t3-account-and-environment-design.md). Production routing remains laptop agents using SSH, with conductor and keeper on the laptop. cswap remains unchanged.

## Verified before starting

- Sanitized `claude auth status` checks: both laptop profiles authenticated and their emails differ; remote private profile 1 unauthenticated, remote private profile 2 authenticated. No credentials were emitted, copied or renewed by the worker.
- Existing ControlMaster reaches `lxplus977.cern.ch`. The staged runtime is present at `/tmp/cgupta-t3-pilot-20261106-qucyawnc/runtime/t3`. Remote provider `claude_account2` uses `/afs/cern.ch/user/c/cgupta/private/claude-t3-2`.
- SHA-256 checks confirmed remote synthetic `AGENTS.md`, `labels.py`, and `check_labels.py` match the laptop fixture under `Projects/t3-lxplus-pilot/`. `python3 -B check_labels.py` fails at the intentional baseline assertion. No fixture file was changed.
- Removed only the stale local forwarding using SSH multiplex `-O cancel -L 127.0.0.1:3783:127.0.0.1:3783`; did not terminate the shared master or restart EOS.

## Started and checked

Launched `python3 scripts/t3/run-lxplus-pilot.py`. Start metadata: **2026-11-06T14:49:28.415773+00:00**, host **lxplus977.cern.ch**, supervisor PID **21271**, server PID **21402**. Maximum lifetime is **1800 seconds after readiness**. The loopback-only server and laptop SSH forwarding use port **3783**. No persistent service, cloud tunnel, CERN job or Git push was created.

Both `python3 scripts/t3/pair-lxplus-pilot.py --check` and an HTTP request through laptop loopback confirmed environment **bfb0877b-5e88-4c11-a8c2-7da8f98266a7**, T3 **0.1.6**. The check mode minted no pairing credential. Native environment-link listing was attempted but is not callable in this session.

## Human actions still needed

1. If this environment is already listed in T3, select it and confirm it connects. Otherwise run `python3 scripts/t3/pair-lxplus-pilot.py` in a laptop terminal and use its pairing details in T3 Settings → Environments → Add environment. Keep pairing codes in that terminal and T3, never chat or Git.
2. Open the remote **lxplus-toy-pilot** project, choose **Claude 2 (lxplus)** and **Supervised**, and start one visible worker. Do not select the unsigned remote Claude 1 entry.
3. Task: read the synthetic workspace's AGENTS.md, fix only `labels.py`, keep `check_labels.py` unchanged, run `python3 -B check_labels.py`, and report hostname, working directory, change and result. The workspace is `/tmp/cgupta-t3-pilot-20261106-qucyawnc/workspace`.
4. Return the result to this discussion for independent file/hash/check validation. Do not call the remote workflow validated until that passes. Reconnection and vault commit handoff remain separate untested acceptance checks.

No analysis repository, CERN data, proxy, keytab or remote vault was supplied to the toy worker. Project instructions restrict the task, but do not establish an OS-level sandbox. Production analysis access is outside this pilot. The temporary server will stop automatically; private profile files and the staged directory are not deleted by that stop.
