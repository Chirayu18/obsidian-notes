---
tags: [reference]
status: active
date: 2026-11-07
source: laptop
---

# Verdict: keep laptop T3 agents and the established lxplus SSH route

**Recommendation: stay.** Keep conductor, keeper and the coding agent on the laptop; use the established SSH connection for CERN commands and the existing mounts when useful. Do not adopt T3 Connect or resume the lxplus-worker pilot now. This is **agent-reported advice**, revised after the pilot history and Chirayu's cancellation. It supersedes the earlier [pilot recommendation](2026-11-05-t3-connect-vs-lxplus-setup.md) and [on-demand-worker decision](2026-11-06-on-demand-lxplus-workers.md).

Chirayu's latest direct instruction before this read-only review, verbatim:

> Don't need lxplus workers... Forget it... I accept the limitations of ssh and all.. Remove all that part for the lxplus workers and revert

The conductor's 2026-11-07 message requested completion of this advice under the original read-only operating boundary. This pass inspected local files, Git history, existing environment links and public documentation. It did not start/stop a backend, link/pair/unlink, execute SSH, renew credentials, change configuration, submit jobs or push. Only the advice notes and their local commit are changed. The earlier rollback request is **not claimed complete**.

**Reasons, ranked**

1. **The additional operational burden now exceeds the demonstrated gain.** The committed trial record includes backend/forwarding failures, a noninteractive-shell failure, an approval that never reached execution, and a stop refusal caused by apparently stale active-run state. I found no validated complete start → useful task → returned result → clean stop acceptance run. Direct remote execution could help, but that benefit has not earned a permanent extra system to maintain.
2. **The current route already runs CERN commands on lxplus.** A laptop agent can invoke a properly initialized remote shell for CMSSW, Condor and CRAB. It need not read a large tree through SSHFS: searches and bulk file operations can run in one SSH command and return a small result. A warm ControlMaster avoids a fresh login for each command. Remote T3 mainly removes shell/transport friction and laptop mount dependency; it does not provide new CERN permissions, extra quota or valid credentials.
3. **Persistent hosting and unattended authority remain separate unresolved requirements.** A background laptop SSH master cannot make a remote server durable, preserve node-local state or renew its credentials. A running conductor is not human supervision. The short SSH-only clearance Chirayu reported does not establish approval for an unattended service or a Connect tunnel.
4. **Keeping one laptop record writer fits the vault.** There is no need to maintain a second active vault clone, transfer unpushed remote note commits, or recover research decisions from an interrupted remote chat. Conductor routes one worker globally; that laptop worker records evidence and commits; keeper reviews and pushes.

**What was verified in this review**

- The original recommendation exists at `Projects/2026-11-05-t3-connect-vs-lxplus-setup.md`, committed as `fc8392a`. The persistence survey is committed as `5bb7773`; the on-demand proposal as `2182a0a`. They were advice/design records, not proof of successful deployment.
- At inspection, HEAD was `227b103` on `keeper/vault-organised-20261105`; the cached upstream comparison showed 17 local commits ahead and zero behind. No fetch was run, so that is not a fresh remote comparison. Later pilot evidence is committed in `Projects/DigiMorphing/phase2-morphing/2026-11-06-pr-amend.md`, notably `d1ae161`, `0febe48` and correction `8c6da3c`. Those observations are **prior agent reports**, not tests rerun here.
- The working tree still contains uncommitted remote-worker instructions in `CLAUDE.md` and `Meta/roles/conductor.md`, and untracked `scripts/t3/lxplus-worker.py` / `lxplus_worker_remote.py`. It also contains separate account/quota migration edits and the deletion of the cswap recovery script. These changes must not be indiscriminately reset together.
- Native `t3_environment_links` is now callable. It lists one lxplus peer, `bfb0877b-5e88-4c11-a8c2-7da8f98266a7`, label `lxplus977.cern.ch`, **unreachable**, access **approval-required**, expiring `2026-12-06T16:22:53.601Z`. This corrects older notes saying link-list tools were unavailable. I did not connect or pair it. Unreachable does not prove remote processes are absent.
- Local `~/.local/state/t3-lxplus-on-demand/status.json` says **stopped**, with a maximum of **1800 seconds**; local T3 settings still have linked environments enabled. The status file is bookkeeping, not a fresh remote process inspection. It is not evidence that authorization was revoked or cleanup completed.
- Re-read setup, conductor/keeper briefs, the global/vault Claude hooks, `scripts/sync-on-start.sh`, the lxplus SSH configuration, `lxplus-eos.service` and `~/bin/lxplus-eos-mount.sh`. Configured behavior: a reusable SSH master with `ControlPersist 8h`; session-start mount/connect handling; systemd-owned EOS SSHFS with restart/reconnect; locked Git sync within this checkout. Hooks/services were read, not run, and current mount health was not tested. Hook execution for every provider is not established.
- Vault search was attempted first and returned relevant records using its keyword fallback; Ollama was inaccessible from the sandbox. `Projects/Conductor/` does not exist, hence this project-top-level note.

**What T3 would change, if reconsidered**

An SSH master supplies transport, not a T3 environment. Remote T3 needs a server and provider runtime on lxplus. Its files, terminals, agent tools, provider login and history are remote; model requests go to the configured inference service. A project selects a workspace on that host, not a separate security identity. Existing threads do not migrate just because a project is grouped across environments. [T3 remote architecture](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/internals/remote.md)

Desktop-managed SSH starts/reuses a remote server and forwards access. Direct pairing grants a client session; agent peer linking is a separate beta requiring enablement on both ends. Peer links last 30 days; forgetting a link locally does not revoke its receiving-server grant. T3 documents delegated result delivery, but product capability does not validate this lxplus implementation. [T3 v0.1.6 remote access](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md)

T3 Connect adds cloud identity and managed tunnels; it is not required for SSH access or multiple projects. The published architecture uses Clerk and Cloudflare. Host Internet access is needed for its tunnel, identity/download endpoints and the selected model service. Exact current machine allowances, prices, CERN egress availability and permitted endpoints were not reverified; they do not affect this stay decision. [Connect architecture](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/internals/t3-connect.md)

The **30-minute cutoff belongs to our bounded pilot**, not a native T3 session limit or a verified CERN login-node limit. Linux T3 can use a systemd user service with linger; that requires an appropriate host arrangement. Reconnection, backend survival and durable history are three different properties. [Background service documentation](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/background-service.md)

**Practical effects and remaining risks**

- **Latency and mounts:** local remote-agent tools avoid SSHFS metadata round trips and laptop FUSE failures. Running searches inside SSH already avoids much of that cost. AFS/EOS and model latency remain. No comparative timing, prompt-count or token-cost benchmark was completed.
- **Permissions and approvals:** a remote agent has the remote account's rights plus its provider/T3 restrictions. Placement does not remove approval prompts; the recorded review was blocked at an approval. Selecting broader access to suppress prompts would change the risk, not validate compatibility.
- **Kerberos, VOMS and shell setup:** both routes need valid credentials in the actual execution context and the right CMSSW/CVMFS environment. A live socket does not prove tickets or proxies are valid. A daemon may not inherit renewed interactive credentials; another lxplus node may not have the same `/tmp` proxy. No renewal or copying is recommended. CRAB can contact services or manage credentials; no live CRAB/Condor command or submission was used to test this advice.
- **Node/storage/process lifetime:** an lxplus alias can select another host; a shared home does not move a process or its listening port. Node-local state can disappear, while a live SQLite database needs suitable locking/storage. The [persistence survey](2026-11-06-persistent-lxplus-t3-design.md) identifies these requirements but does not establish a supported permanent service, current logout/process-killing rules, numeric session/resource limits, or tested backup/restore.
- **Current SSH limitations remain accepted:** laptop suspend/network loss can interrupt commands and mounts; a successful reconnect does not prove an interrupted operation completed. Check outputs/diffs and job state before retrying. Do not blindly repeat a side-effecting command. Existing authentication automation was inspected, not certified as CERN-approved.

**CERN policy and model-service boundary**

Public CERN AI rules were freshly fetched without authentication: SPAI7 requires human presence/supervision for personal identities; SPAI8 requires dedicated independently revocable identities for unattended workflows, with controls and audit evidence under SPAI9–10. This applies to laptop agents acting through SSH too. A second Claude account or an AI conductor does not supply that authority. [CERN AI security rules](https://security.web.cern.ch/rules/en/ai-tools.shtml)

NET10 prohibits reverse-tunnel exposure of internal services. Applying that to Connect is an **inference**, not a T3-specific CERN ruling. Service-account restrictions also need checking before an unattended design. [Network rules](https://security.web.cern.ch/rules/en/net.shtml), [identity rules](https://security.web.cern.ch/rules/en/iaa.shtml)

CERN 2FA, account permissions and approved credential practice still apply. Do not create keytabs, copy personal tokens or automate renewal to compensate for disconnects. Hosting an agent at CERN does not authorize sending unpublished CMS material to its model provider. Approve the actual material, endpoint/model and account contract independently; a CERN Gateway can route to different hosting locations. No new private analysis content or credentials were submitted to an external service in this review.

The public [CERN ML getting-started page](https://ml.docs.cern.ch/getting-started/) was reachable by unauthenticated HTTPS despite the web tool's 403. It describes managed sessions and optional AFS/EOS/CVMFS access, not permission to host a permanent T3 server on lxplus. Full Condor/CRAB parity, service lifetime, suitable database storage and this exact use case remain unverified. It does not change the recommendation. The [Gateway preparation record](2026-11-06-cern-ml-and-ai-gateway.md) remains separate; this review did not enable or test inference.

**Projects, accounts and vault workflow**

Keep the existing HToWW, Flashjet, DigiMorphing and Agenthon vault folders. Each can record its actual code path, `execution: laptop_agent_over_ssh`, SSH alias, software context and credential prerequisites; any fallback must be explicit. Metadata documents routing, it does not configure T3 or enforce permissions. One shared lxplus connection can serve several project directories. Separate folders/projects help context; separate environments per analysis are unnecessary.

Conductor and keeper stay on the laptop; one substantive worker globally. Prefer remote shell commands against the intended code checkout, with evidence written in the laptop vault. An existing lxplus vault copy may remain, but do not make it a simultaneous record writer. Git sync does not transfer unpushed commits between copies; its lock covers one Git directory, not both machines.

Model usage follows the selected account across laptop/remote sessions; remote placement grants no additional allowance. Use native T3 per-account Usage → Limits, and treat unknown headroom as unknown. Additional retries/context can consume quota; changing to API authentication can change billing. Current balances, concurrent-use entitlement, Gateway allocations and prices were not checked. The earlier cswap-removal/account work is separate from abandoning remote workers; do not restore cswap as collateral rollback.

**Next action and decisions needed**

No new pilot, subscription or migration decision is needed to stay. Chirayu has already selected this direction. The outstanding implementation task is the previously requested **scoped rollback**: remove the added remote-worker route/instructions and helper deployment, revoke only its grants, preserve historical notes/account profiles and the established SSH/EOS setup, and retain separate native-account/quota migration work. First establish actual backend ownership/state; an unreachable peer is not sufficient evidence to delete live state. This read-only review performs none of those operations and does not request the same authorization again. Keeper-owned instruction edits need coordination with the keeper.

Reopen a pilot only if Chirayu later requests it for a concrete task where SSH friction is measurable, with an approved supervised runtime/model boundary and a tested state/stop path. Until then, neither the current `CLAUDE.md` route nor the persistence design changes this **stay** verdict; they are leftover implementation/design context, not a reason to resume cancelled work.
