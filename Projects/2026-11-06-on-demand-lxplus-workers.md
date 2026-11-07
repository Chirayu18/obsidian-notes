---
tags: [reference]
status: superseded
superseded_by: "[[2026-11-07-t3-connect-vs-lxplus-verdict]]"
date: 2026-11-06
source: laptop
---

# Decision: laptop default with on-demand lxplus workers

**2026-11-07 update:** Chirayu cancelled lxplus workers. See [[2026-11-07-t3-connect-vs-lxplus-verdict]] for the current stay recommendation and the outstanding rollback status. This historical design is not an instruction to restart the pilot.

**Agent-reported architecture recommendation, following Chirayu's requested direction: keep the existing laptop T3/auto-SSH workflow as the default, and retain lxplus as an optional task execution environment.** Conductor and keeper remain on the laptop. No backend was restarted, environment linked, agent launched or configuration changed by recording this decision.

Chirayu requested that a laptop worker be able to spawn a task on lxplus, have that task work directly there, and receive its result back when finished. This replaces pursuing a continuously available lxplus T3 server as the immediate goal. It does not remove the separate requirement for an appropriate dedicated identity if work continues unattended while Chirayu is away.

## Intended task lifecycle

1. A laptop parent chooses direct lxplus execution for a task that benefits from it. Start or reuse the approved SSH-only backend, confirm the actual node, provider, project root and run budget, then establish the necessary T3 agent link.
2. Use T3 linked-environment delegation so the remote task has a tracked parent and its completion wakes that parent with the result. The remote task is a visible ordinary thread on lxplus. It works in the selected code/synthetic workspace, not the AFS home root.
3. Keep one substantive worker globally: the laptop parent waits while its remote worker executes. Conductor and keeper are not replicated remotely.
4. Return the change summary, verification, relevant paths/commits and remaining issues to the parent. The parent records results in the laptop vault; the keeper reviews, consolidates and pushes. If a remote vault commit is produced, transfer it explicitly over SSH for keeper review; GitHub pull does not retrieve an unpushed commit.
5. After all tasks using the test-owned backend have finished and results are acknowledged, it can stop. Preserve code, account profiles and any deliberately retained history; do not delete the environment's state or unrelated threads. A deadline or dropped connection must be reported as interruption/failure, not a completed task.

This makes remote server uptime task-scoped. Durable research results live in code/Git and the laptop vault, so the first implementation need not promise permanent availability or indefinitely retained remote chat history. If the saved environment and remote history must remain reusable across node changes, server identity, consistent state restoration and relinking still need a tested design. A disposable backend is not automatically the same saved environment on its next start.

## Verified capability versus remaining implementation

[T3 0.1.6 remote access](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md#link-another-environment) documents linked-machine delegation and automatic result delivery to the parent. Desktop-managed SSH can start/reuse a remote server and forward its port. These are product capabilities, not evidence that the current lxplus pilot already implements the full lifecycle.

The current saved pilot is a manual connection to a stopped temporary server. Agent linking was disabled in Labs at the last native tool check; the link-list/link tools were not callable here. Therefore **automatic start → delegate → report → stop has not been configured or tested**. Re-pairing a manual address is separate from enabling an agent-to-agent environment link. Native SSH's default installation/state paths must be checked before using them on AFS-backed lxplus home.

The implementation should first pass one supervised synthetic round trip, including result delivery and a reconnect/restart check. Use the existing short-pilot approval and an explicit task deadline; a longer run needs the appropriate authorization rather than silently dropping the time limit. A permanent systemd service, cloud reverse tunnel or new account is not necessary merely to describe this architecture and none was installed now.

The [prior persistence survey](2026-11-06-persistent-lxplus-t3-design.md) remains the evidence for storage, node selection, credential and policy constraints. In particular, task-scoped delegation does not make a personal-account worker supervised when its owner is away. [CERN AI identity requirements](https://security.web.cern.ch/rules/en/ai-tools.shtml)
