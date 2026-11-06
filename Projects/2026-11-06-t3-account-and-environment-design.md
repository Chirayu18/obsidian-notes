---
tags: [reference]
status: active
date: 2026-11-06
source: laptop
---

# Reconsidered T3 account and environment design

**CERN service follow-up:** [ML sessions and AI Gateway](2026-11-06-cern-ml-and-ai-gateway.md) records the subsequent public-document checks and separately prepared gateway provider. ML sessions have persistent file storage but documented idle culling; an uninterrupted SSH socket is not an architectural requirement for retaining T3 history.

**Implementation follow-up:** [Native account preparation](2026-11-06-native-t3-account-preparation.md) records the second laptop entry now configured. Its sign-in is pending; cswap remains unchanged and installed. The discussion of the earlier applied configuration below describes the state at design-review time.

**Recommendation: move account selection to native T3 on the laptop first; keep the established laptop-to-lxplus workflow for production; treat remote T3 execution as a separate pilot.** Keep cswap installed during verification. Retire it only after account behavior and the role briefs' quota dependency have replacements. Do not build automatic cross-machine credential synchronization.

**Agent-reported design review**, with documentation/source checks against installed T3 **v0.1.6**. No further live settings, logins, services or credential stores were changed during this review. The preceding [applied setup](2026-11-06-cswap-t3-account-setup.md) remains the actual configuration; the design below is not claimed implemented.

Chirayu clarified the intended outcome, verbatim:

> Wait so after this I won't need cswap on my laptop too right? Both accounts on laptop as well will be accessible via t3?

Then requested:

> Can you think more on the setup. I'll be back in 10 mins

The previous implementation kept T3's default Claude entry on the cswap-managed login. That does not establish two independently authenticated laptop T3 account entries. It was a mismatch with the clarified end state. The earlier explanations also needed a clearer distinction between native quota display, automatic account rotation, and continuity of an existing conversation.

## What the installed version actually supports

**Native account entries:** Claude supports separate provider entries with separate config-directory logins. Existing Claude threads can switch only between entries with the same config home. Source `ClaudeHome.ts` builds the continuation key from that resolved home path; a shared user identity alone does not make two homes compatible. Separate native Claude logins are suitable for choosing an account for new work, but do not establish seamless continuation across accounts. [Claude account guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-claude.md), [continuation-key implementation](https://github.com/pingdotgg/t3code/blob/v0.1.6/apps/server/src/provider/Drivers/ClaudeHome.ts)

**Codex/ChatGPT differs:** T3 supports multiple ChatGPT account entries; compatible accounts can continue a thread. Its documented CLI alternative uses shared Codex state and a separate shadow login. The managed ChatGPT flow is preferable here to manually assembling that layout. Claude's isolated-home arrangement should not be described as equivalent. [T3 Codex account guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-codex.md)

**Native quota visibility exists:** T3's **Usage → Limits** supports Claude and Codex subscription accounts, individual account details and pooled views across connected environments. Duplicate reports of the same account are deduplicated. Thread details can show the current account's windows. A pooled number is not sufficient to enforce a limit on the selected account. These capabilities were verified in version-matched docs and shipped UI code, not tested with the missing second login. [Usage/limits guide](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/usage.md)

**Native fallback is narrower than a quota manager:** the inspected `resolveNewThreadModelSelection` implementation supports an explicit configured fallback for a new thread when the remembered/default account reports an exhausted window. It skips that substitution when a model/account was explicitly selected and checks fallback availability. Its exhaustion test is at **100%**, not the conductor's approximately **80%** preflight rule. This does not establish proactive best-headroom rotation or moving a running Claude session between different homes. [Fallback implementation](https://github.com/pingdotgg/t3code/blob/v0.1.6/packages/shared/src/usageLimits.ts)

**cswap's remaining distinct behavior:** it can change the default login while retaining the same Claude home, or maintain account session profiles. The current laptop T3 entry therefore follows its default-login changes. That feature can still be useful for continuing a pinned Claude conversation, but it is a dependency rather than native T3 account selection. Its source warns against independently maintaining copies of the same refresh-token lineage. No credential export/replication was introduced. [cswap documentation](https://github.com/realiti4/claude-swap)

## Recommended target

1. **Laptop is the stable control and record host.** Keep Obsidian, the canonical vault checkout, conductor and keeper there. Keep one worker globally. Keep current pinned threads and account 1 working through migration.
2. **Use explicit native T3 accounts.** For Claude, reuse the already authenticated default home as account 1 and authenticate account 2 in one separate home. This avoids a redundant login/copy for account 1. Add distinct T3 names and verify actual identities. Use T3-managed ChatGPT account connections for the OpenAI accounts, preserving the currently working Codex entry until its replacement is tested. Do not switch model accounts silently.
3. **Accept explicit Claude handoffs.** When another Claude home/account is needed, record the task state and continue in a fresh visible thread with a bounded brief. The vault is the durable record. For a pinned conductor, changing account may require recreating/pinning it from its role brief. If Chirayu requires seamless same-thread Claude account rotation, retain cswap for that requirement rather than claiming native independent profiles already provide it.
4. **Keep account grants per host.** Use independent supported authentication on laptop and any approved remote host. Do not put tokens, auth files, callback URLs or keytabs in the vault, Git or shell configuration. Provider account setup is separate from T3 Connect identity and separate from CERN login. More environments do not create more allowance for an account. [Official OpenAI account/session guidance](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions)
5. **Keep production CERN work on the proven SSH path initially.** Native laptop accounts can run commands through the existing connection. This account migration does not require a remote T3 server or a cloud tunnel. Run the synthetic remote pilot only to decide whether direct remote file/tool operations justify the additional operational work.

## The two dependencies that block immediate cswap removal

**Quota preflight is written into the current roles.** `Meta/roles/conductor.md` requires `cswap list --json` and `omp usage` before a worker; `Meta/roles/keeper.md` also references them. Removing a binary or abandoning its saved account inventory while leaving those instructions active would break the workflow. The keeper must revise these keeper-owned files after a replacement is agreed and checked.

Native T3's Limits UI can replace human quota inspection. A supported agent-readable replacement for the conductor's per-account percentage check was **not verified**: the current exposed MCP catalog has no quota-reading tool, and the inspected capability/environment tool definitions do not return usage windows. This is a tool-access gap, not absence of T3 quota data. Do not invent a credential-polling service or scrape secret stores to bridge it. During transition retain the existing helper for supported routes; an independently configured account with unavailable verified quota data needs an explicit human check before an automatic launch. A fully cswap-free automated conductor is not yet validated.

**Thread continuity needs a deliberate choice.** New-thread account selection is straightforward. Same-thread Claude failover is not equivalent across the documented separate-home setup. The migration should test the behavior Chirayu actually values before deleting the old convenience path.

## Why the current lxplus pilot is not a permanent environment

Observed connections reached **lxplus938** on 2026-11-05 and **lxplus977** on 2026-11-06. Yesterday's temporary root was not present on today's node. Each restored pilot acquired its own environment ID. A shared AFS home does not move a process, port, credential cache or node-local database.

The temporary `/tmp` setup is appropriate for an authorized short test; it is not a durable deployment. T3 keeps projects, threads, state and providers on the environment's server. Live SQLite state requires suitable storage/locking; simply moving it into AFS/EOS is not a verified solution. No same-state-directory concurrent servers should be started on different login nodes. [Remote architecture](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/internals/remote.md), [SQLite storage guidance](https://sqlite.org/wal.html)

Before a permanent remote setup, confirm an approved runtime lifetime, stable host/service ownership, durable suitable storage, account/model egress, and credential lifecycle. A CERN-approved managed development host could be a better service host than a load-balanced login alias; its actual AFS/EOS/CMSSW/Condor integration is unverified. Do not provision one or assume it replaces lxplus without a separate task. The support confirmation in this conversation covered a **short SSH-only pilot**, not this permanent deployment.

The current master is inside `lxplus-eos.service`'s cgroup. Separating ownership may be worthwhile later, but no new master service is necessary merely to test T3. Do not use an EOS restart as a casual network test. T3 placement still does not renew Kerberos, AFS authorization or VOMS proxies automatically.

## Vault and project routing

Keep the existing logical project folders. Do not split the research record into laptop and lxplus project copies. Let the keeper maintain a small workspace mapping in the relevant project/leaf README: logical environment, actual code checkout, validated T3 identifiers where durable, fallback route and manual failover policy. Projects with several code repositories may need several workspace entries; one path per top-level research project is not always enough.

The mapping is an instruction convention, not a T3 runtime configuration file. It must distinguish **agent host** from **where shell/analysis commands execute**: a laptop worker using SSH still executes CERN commands on lxplus. Never silently fall back by running CMSSW/Condor work locally. Verify that a prior remote worker has stopped before starting another route; one-worker discipline applies across environments.

For production remote workers, keep a separate vault Git checkout for their notes and an explicit keeper-reviewed SSH fetch/patch handoff of unpushed commits to the laptop. A pull from GitHub does not transfer unpushed remote commits. The hook lock only coordinates one shared Git directory. A code-root T3 worker also needs the vault role/recording instructions in its explicit brief; it will not discover a separate vault's AGENTS.md automatically. Do not copy laptop mount/login hooks onto lxplus account profiles.

## Concrete migration sequence

1. Confirm the account/continuity choice on Chirayu's return. No additional live configuration was changed while considering it.
2. Keep current default Claude account 1. Prepare **one native laptop account-2 entry**, authenticate it separately, verify both identities and test one bounded thread on each. For a cswap-free target, use that independent account-2 login rather than running the recovery helper whose purpose is to repair the cswap pool.
3. Add/verify the intended ChatGPT accounts through T3. Check native per-account Limits; do not infer account 2's headroom from account 1 or pooled totals.
4. Have keeper update account selection and quota preflight instructions with the validated method. Until then retain cswap installed and preserve its state. No cswap uninstall/purge is authorized or necessary now.
5. Complete the already prepared synthetic lxplus test with **one** authenticated remote account. Verify supervision, identity/path, real edit and unchanged passing check, reconnection, and notes handoff. Avoid bulk authorizing remote ChatGPT accounts into temporary state before choosing a durable remote design.
6. Retain laptop workers as production default until a remote environment has stable state, credentials and handoff. Only then choose project-by-project remote defaults. Keep conductor and keeper on the laptop.

The desired endpoint can be **both accounts visible in T3 without using cswap for account selection**. A completely removed cswap dependency additionally needs the quota-role migration and an accepted Claude continuity policy. Those are the missing pieces, not more credential-copying scripts.
