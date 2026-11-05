---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---

# Proposed lxplus T3 checks and project routing

**Agent-reported proposal.** The read-only checks were subsequently executed at Chirayu's request; see [the live results and separately approved AFS cleanup](2026-11-05-lxplus-t3-readiness-checks.md). Setup/pilot actions below remain unexecuted. This extends [the recommendation](2026-11-05-t3-connect-vs-lxplus-setup.md), without replacing it. No environment, service, credential, role brief or project configuration was changed. These instructions separate observations from setup actions; passing an observation does not authorize a setup action.

Chirayu, verbatim, 2026-11-05:

> Can you tell me step by step how to do thoese checks? Also a different folder for each project makes sense? In my vault... It would basically have frontmatter for  the path and environment for each project and a fallback... Conductor and keeper stays on laptop?

**Recommended layout:** keep the existing `Projects/HToWW/`, `Projects/Flashjet/`, `Projects/DigiMorphing/` and `Projects/Agenthon/` folders. All four folders and their READMEs were checked locally. Let the keeper add routing frontmatter to those existing READMEs after the paths/IDs are verified. A remote code checkout remains separate from the project's vault folder. One lxplus environment can contain multiple T3 projects.

Conductor and keeper stay on the laptop. The conductor selects a route and enforces one worker globally; the worker runs on the selected environment; keeper reviews the resulting note/commit on the laptop. Frontmatter is a proposed convention for agents to read, not built-in T3 configuration or an enforcement mechanism. Existing role briefs still need a keeper-managed update before automatic remote routing.

## 1. Check the existing transport on the laptop

Run these yourself in a laptop terminal. They inspect configuration and the already-running master; they do not establish a new master or renew authentication.

```bash
ssh -G lxplus | awk '$1 ~ /^(hostname|user|batchmode|controlmaster|controlpath|controlpersist)$/ {print}'
ssh -O check lxplus
systemctl --user show lxplus-eos.service -p ActiveState -p SubState -p Restart
```

Expected from the prior configuration inspection: host `lxplus.cern.ch`, user `cgupta`, BatchMode enabled and a reusable control socket. `Master running` means that master is alive at that instant. The EOS service should report active/running if it is healthy. These checks alone do not prove that either mount is readable.

If the master check fails, stop here and use the established human-approved login procedure. Do not call the reconnect wrapper as part of a credential-preserving diagnostic: it can authenticate automatically. A new master service has not been implemented; the existing unit found was only `lxplus-eos.service`.

For the proposed master service, acceptance means one foreground SSH process/socket owner, bounded retries, usable session keyring/DBus, and coordination with the EOS script and wrapper. Its design must avoid concurrent authentication attempts. Starting it is a separate configuration task.

## 2. Inspect the remote host and tool paths

While the master is healthy, run this from the laptop. It uses BatchMode and does not request interactive credentials. Stop on authentication failure rather than renewing anything.

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 lxplus 'sh -lc "
hostname -f
id -un
uname -m
command -v curl wget tar sha256sum shasum
command -v claude codex t3
"'
```

Record which command produced each path. The first group needs `curl` OR `wget`, `tar`, and `sha256sum` OR `shasum`; the second needs only your chosen provider. Missing `t3` means it has not been found on that shell's PATH, not that a runtime download is authorized. A missing alternative can make the command return nonzero even when the required alternative exists.

T3's SSH launcher uses a non-interactive shell, so do not accept “works in my interactive terminal” as sufficient. Its remote runtime downloads and provider setup are documented in the [version-matched SSH guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md#desktop-managed-ssh). Current packaged runtimes differ from older Node-only setup instructions; inspect the exact version rather than installing Node speculatively.

## 3. Inspect credentials and storage on lxplus

In an existing authenticated remote shell, run:

```bash
if klist -s; then
  printf 'Kerberos ticket valid\n'
else
  printf 'Kerberos ticket missing or expired\n'
fi
command -v voms-proxy-info
voms-proxy-info -timeleft
findmnt -T "$HOME"
df -h "$HOME"
ulimit -a
```

`voms-proxy-info -timeleft` reports seconds remaining; an error, missing command or nonpositive time needs investigation. This does not prove every custom proxy location is absent, or that VOMS attributes and every CMS service authorization are valid. Do not run `kinit`, `aklog`, proxy initialization or keytab creation for this check. Keep credential contents and identifying diagnostic dumps out of shared chat. [Packaged VOMS manual](https://manpages.debian.org/unstable/voms-clients/voms-proxy-info.1.en.html)

Repeat filesystem inspection for the proposed T3 state directory, once an administrator identifies an allowed location. **Do not assume AFS home or EOS is appropriate for T3's live database.** SQLite documents network-filesystem/WAL restrictions; locking and durability require deliberate evaluation. Node-local scratch may solve locality while losing state on cleanup or node replacement. Shell `ulimit` does not reveal every cgroup/service limit. [SQLite WAL documentation](https://sqlite.org/wal.html)

## 4. Resolve policy and service lifetime before setup

Ask lxplus support/Computer Security, through the normal CERN support channel, for an answer to this concrete question; no message has been sent by this agent:

> May my personal lxplus account run a short interactive T3 Code server and coding-agent process, reached only through an existing SSH port forward? Which resource limits, session/logout cleanup rules, state-storage location, model-service egress destinations and credential-handling rules apply? Is a persistent user service permitted later? I am not requesting a public listener or Cloudflare tunnel for the initial test.

Separately confirm which material may be sent to the chosen model provider under the actual account/contract. Use synthetic inputs until that is settled. A connection succeeding is not a policy approval. Current lifetime, cgroup, storage and egress permissions remain unverified. See [CERN AI/privacy guidance](https://privacy.web.cern.ch/artificial-intelligence-ai).

## 5. Perform an explicitly authorized toy setup

Only after the preceding gates, choose one approved provider/account and a synthetic repository. Do not import the real vault or analysis repository for the first run.

- Where its default runtime/state locations have been approved, use **Settings → Environments → Add environment → SSH**, target `lxplus`. This downloads/starts software and authorizes access; it is a setup action. If the default locations are unsuitable, stop and arrange a manual foreground server with its approved state directory and version-checked CLI flags instead.
- Inspect the actual launcher/process settings to establish whether it reuses the configured socket; do not assume it invokes `lxplus-ssh`. Keep the master alive beforehand and retain fail-fast BatchMode behavior.
- Configure the selected provider on lxplus through its approved login flow. Do not copy laptop credential files. Provider configuration belongs to the environment's machine. [T3 installation/provider guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/install.md#providers)
- Keep Connect cloud exposure, peer links, load balancing, background installation and lingering off for this test. Choose **Supervised** explicitly before the first worker; T3 documentation says the initial default is Full access. [Permission modes](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/permission-modes.md)

The desktop-managed launch owns its remote process lifecycle; if a strictly foreground-only test is the approved scope, use the manual-server alternative rather than assuming the desktop launch implements that restriction.

## 6. Verify from inside the remote T3 session

In its terminal check `hostname -f`, `pwd -P`, `id -un` and the credential checks from step 3. They must agree with the intended node, directory and user. The credential check must succeed in this actual runtime context, not merely an unrelated SSH shell. Check the selected T3 environment ID and project ID; record them alongside their readable names. Never write an endpoint token or pairing code to frontmatter.

Have one supervised worker edit a synthetic text file and run a tiny local assertion. Verify the change directly from the existing SSH shell. Inspect the expected approval prompt, actual path and diff. While idle, disconnect/reconnect the T3 client once and verify the same environment, node, state and file. Compare with the current laptop-agent workflow before claiming improvement.

Initially check only that `condor_q`, `crab` and `scram` can be found after the appropriate approved shell setup. Defer live scheduler/CRAB queries and submissions: some CLI commands contact services or manage credentials. Normal CMSSW setup and job authorization remain necessary.

For rollback, stop only the test-owned process/forward, revoke its client session, retain the toy files and use the current laptop workflow. Do not stop a pre-existing remote server or alter the current mounts/helpers.

## Proposed per-project frontmatter

Example for the keeper to merge into the existing HToWW README; `null` means **unknown and unusable for launch**, not a value the conductor should guess. The source/date below describe the metadata record's provenance.

```yaml
---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
vault_path: Projects/HToWW
execution:
  preferred:
    environment: lxplus
    environment_id: null
    t3_project_id: null
    code_path: null
    transport: ssh
    status: unverified
  fallback:
    environment: laptop
    mode: agent_over_ssh
    ssh_host: lxplus
    remote_code_path: null
  fallback_policy: ask_before_switching
vault_authority: laptop
---
```

The fallback still executes CERN commands remotely; it does not turn the laptop into an analysis compute host. Fill both code paths from the actual checkout, and add the mount path only if browsing it locally is useful. IDs are exact T3 IDs, independent of directory names. Subprojects inherit this mapping unless they use another repository, environment or software setup. Keep the one-global-worker rule in the role brief rather than inventing separate per-project concurrency allowances.

Conductor should check verified route/paths, availability and quota before launch. If the route fails or identity/path differs, pause and offer the fallback; do not silently switch environments, model accounts or software. Selecting a remote environment in Chirayu's client does not grant a laptop conductor cross-environment launch rights. That later automation needs an explicitly authorized peer link and revised role brief; do not introduce it for the manual pilot. [Environment architecture](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/internals/remote.md)

For real remote workers, establish the vault handoff first: a separate lxplus Git clone, notes committed there, and a keeper-reviewed SSH fetch/patch transfer to the authoritative laptop copy, with no worker push. GitHub pull alone cannot transfer unpushed commits. The toy pilot can use a Chirayu-mediated report with an explicitly agreed exception to the usual worker-note rule. No remote clone or handoff implementation is claimed here.
