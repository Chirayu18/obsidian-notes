---
tags: [reference]
status: superseded
superseded_by: "[[2026-11-06-on-demand-lxplus-workers]]"
date: 2026-11-06
source: laptop
---

# Persistent lxplus T3 workers, laptop conductor and keeper

**Agent-reported recommendation: pursue an SSH-only lxplus backend as a recoverable development service, subject to a supported storage/lifetime arrangement and a dedicated identity for unattended workers. Keep conductor and keeper on the laptop. Do not turn the personal-account pilot into an unattended deployment by removing its timer.** A persistent session is technically possible; permission and durability for this exact service are not yet established.

This updates the [earlier account/environment design](2026-11-06-t3-account-and-environment-design.md). The [CERN ML/Gateway note](2026-11-06-cern-ml-and-ai-gateway.md) remains the implementation record for the disabled gateway provider. No permanent server, service account, keytab, job, tunnel, config change or push was made during this documentation survey.

## Clarified target

Chirayu wants a persistent T3 server **on lxplus**, with conductor and keeper **only on the laptop**, and explicitly selected **workers also keep acting while away**. He then proposed keeping work alive only while the laptop conductor keeps running.

The role split is sensible. One worker globally remains the rule. The conductor routes and reports; the worker acts in an explicitly selected code workspace; the keeper owns the canonical laptop vault and reviews/pushes notes. Laptop sleep means no new conductor decisions. An already running remote worker is a separate process and may continue unless an actual guard stops it.

## What the CERN sources establish

| Question | Verified evidence | Implication for this setup |
|---|---|---|
| Can sessions survive SSH logout? | LHCb StarterKit slides dated 2025-12-01, PDF pages 23–24, discuss linger and systemd-managed tmux/screen sessions on lxplus. They link IT article KB0008111. | Technical persistence is possible. This is training guidance, not a blanket approval for a permanent T3/AI service. |
| Will reconnecting find the same process? | ATLAS's remote-SSH guide explains lxplus load balancing and recommends ControlMaster to keep repeated connections on one node. CERN Linux guidance warns that an individual node can become unavailable or disappear. | Record and reconnect to the backend's actual node. The generic alias alone is not durable service discovery, and ControlMaster does not survive a host failure. |
| Is network-backed home suitable for tool state? | ATLAS recommends avoiding remote-development installation on network storage, especially AFS, and keeping locks local. SQLite explicitly excludes network filesystems for ordinary WAL use. | Separate code/vault storage from the live T3 database. Do not claim AFS/EOS makes the database durable and safe. |
| Is an uninterrupted SSH socket required? | T3 documents a Linux user service that can survive logout with linger. SSH is a client access route, not inherently the process supervisor. | A properly managed backend can persist while its client disconnects. Our pilot's connection-bound lifetime is a deliberate test design, not an inherent T3 limit. |
| Can a personal-account agent keep acting while its owner is away? | CERN AI principles SPAI7–8 require human supervision for personal identities and dedicated independent identities for unattended workflows. SPAI9–10 add controls and audit logging. | A running AI conductor is not the supervising human. A second personal/secondary account or another Claude profile does not settle the execution-identity issue. |
| Can T3 Connect expose the server through an outbound tunnel? | CERN NET10 prohibits reverse-tunnel services that expose internal services through outbound Internet endpoints. | T3 Connect appears to fall within this category; that classification is an inference, not a T3-specific CERN ruling. Keep this design on approved SSH/VPN access unless CERN grants an applicable exception. |

Primary sources:

- [LHCb StarterKit 2025 Bash slides, PDF pages 23–24](https://indico.cern.ch/event/1598797/contributions/6808829/attachments/3183490/5663835/StarterKit_Bash.pdf). A second CERN-hosted [Pepper presentation](https://indico.cern.ch/event/1463748/contributions/6163162/attachments/2941168/5167391/Pepper-1.pdf) also points to KB0008111; its old Condor workaround was not adopted.
- [ATLAS remote SSH: network storage and multiplexing](https://atlas-software.docs.cern.ch/athena/ide/ssh/).
- [CERN Linux Kerberos/SSH guidance](https://linux.web.cern.ch/docs/kerberos-access/). Some examples are historical; no old encryption or authentication recipe was applied.
- [SQLite WAL storage requirements](https://sqlite.org/wal.html).
- [T3 0.1.6 background service](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/background-service.md).
- [CERN AI security principles](https://security.web.cern.ch/rules/en/ai-tools.shtml), [network rules](https://security.web.cern.ch/rules/en/net.shtml).

## Identity is the main change for away work

Under [IAA3](https://security.web.cern.ch/rules/en/iaa.shtml), CERN service accounts are intended for programmatic/background access, not routine human work, and must not log in from the Internet. The account type and its eligibility for lxplus, CMS resources, Condor/CRAB and AFS/EOS access still need confirmation. A separate secondary account remains a personal identity under the AI rule.

The intended arrangement is human access from the laptop over approved SSH, with the worker running under a dedicated internal service identity and only the required project permissions. Do not infer that logging in as a service user automatically changes the identity of a personal Kerberos ticket, CMS proxy or model API key. Those grants need an appropriate, independently revocable ownership and scope too. No personal credential copying or automatic renewal was configured.

CERN Gateway remains the preferred inference route for this design, initially with an explicitly selected on-premises model. Gateway routes can also target cloud providers; a CERN endpoint alone does not establish data residency. Its actual dedicated-worker key/team arrangement is unverified. The prepared laptop gateway entry remains disabled, with no key delivered and laptop reachability still unresolved; lxplus unauthenticated reachability was already verified.

The standing vault restriction on job submission/deletion/push remains. Away work does not by itself authorize those operations. Any future autonomous workload needs an explicit bounded task and the required human approvals or pre-authorized scope, as well as CERN's identity requirements.

## Current-machine evidence

Read-only checks on **lxplus977.cern.ch**, 2026-11-06:

- `loginctl show-user <uid> --property=Linger --property=State`: **State=active**, **Linger=no**. No setting was changed. A user manager running during a login is not proof it will run after logout or reboot.
- The stopped pilot's `state/userdata/statev2.sqlite` has SQLite header read/write format **2/2**, confirming WAL format without opening or modifying its contents.
- `findmnt` reports **ext4** for `/tmp` and `/var/tmp`, and **afs** for the home directory. Local filesystem type does not establish retention, backups or an allocated durable directory.
- Restarting the Nov6 pilot with the same node-local state preserved its T3 environment ID. Previous connections on Nov5 and Nov6 reached different lxplus nodes, demonstrating the node-selection problem.

No logout-survival, reboot, migration, backup/restore or service-account test has been executed. The old pilot is stopped. There is no permanent T3 service now.

## Proposed backend and worker lease

Keep the persistent backend and its history separate from permission to execute work:

1. **Backend:** one server and one state directory, on a recorded node, with a CERN-supported user/service supervision method. Loopback binding, approved SSH access, explicit recovery on node loss. No concurrent servers sharing one database.
2. **State:** live database on suitable approved local/block storage; supported consistent backups to protected persistent storage, and tested restore to a replacement node. Live rsync/copying one SQLite file while it changes is not a backup plan. AFS/EOS can hold code and notes without being the live database location. Retention and an acceptable recovery-loss window must be agreed.
3. **Worker:** one globally, exact project root, dedicated identity for unattended operation, bounded resource/cost/run limits, approved model endpoint and retained audit evidence. Keep compute-heavy analysis in its established batch workflow with explicit submission authorization.
4. **Lease:** a small deterministic guard could renew short-lived worker authority while the conductor is healthy. The guard should gate each new side-effecting tool action, not merely the creation of another chat turn. On expiry: stop admitting actions, request cancellation and retain state. An already executing shell process, external request or submitted job may need separate cancellation; a heartbeat cannot promise instantaneous rollback.
5. **Human supervision:** if personal credentials are used, a conductor heartbeat is insufficient. An actively supervising human must remain present under the published policy. A dedicated-identity workflow can additionally use the heartbeat as an operational limit.

The lease is a proposed design, **not a verified native T3 option** and not implemented. A prompt telling an agent to stop is not a dependable enforcement layer. T3's ordinary linked-environment connection loss was not shown to cancel an active worker. The current laptop has linked-environment tool access disabled in Labs; no setting was changed.

If Chirayu instead wants the server itself to exist only while the laptop conductor is alive, that can be a session-bounded service design. It still needs durable state to restore history and does not make an away personal-account worker supervised.

## What remains unverified, and a concrete support request

The authoritative lxplus documentation root returned **401**. The public KB0008111 URL returned only the ServiceNow shell, without the article content; KB0008901 is linked by ATLAS for remote-development recommendations but was not read. The coding-tools considerations page also returned **401**. No authentication was attempted. Therefore exact current lxplus service limits, allowed persistent-service procedure, storage retention and service-account eligibility are not established. HTCondor runtime-limit pages describe batch jobs, not login-session lifetimes; they were not used as evidence of an lxplus time limit. Historical cron/keytab documentation was not treated as current unattended-AI authorization.

Draft for Chirayu to send to CERN support — **not sent by the worker**:

> I want a long-lived T3 coding-agent backend on lxplus, with one worker at a time and inference through an approved CERN AI Gateway model. Conductor and keeper stay on my laptop. The backend would listen only on loopback and be accessed through approved SSH, with no T3 Connect/reverse tunnel or public listener. Workers may continue while I am away, using an appropriate dedicated service identity and narrowly scoped credentials. Can you confirm whether lxplus supports this use, the supported supervision/logout/reboot procedure (including linger if applicable), a suitable durable local/block-storage location for SQLite WAL state and backups, and the permitted service-account access to AFS/EOS/CMS/Condor? If lxplus cannot support those requirements, which managed CERN CPU host is appropriate?

Chirayu needs to decide the accepted interruption/recovery window and allowed unattended task scope. CERN must confirm the hosting/identity/storage arrangement; personal approval alone does not grant an exception to its published rules. If lxplus has no suitable durable storage/service arrangement, [CERN OpenStack](https://clouddocs.web.cern.ch/) is the documented service-hosting fallback, with eligibility/quota and CMS integration still to be checked. No VM was requested or created.
