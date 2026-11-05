---
name: lxplus-afs-token-aklog
description: "AFS 'Permission denied' on lxplus while ssh still works = missing AFS token; fix with aklog, not kinit or reconnect"
metadata:
  type: feedback
---

On lxplus, when `~` (AFS) gives `Permission denied` / `Could not chdir to home
directory` but `ssh lxplus` itself works and EOS is still readable, the Kerberos
ticket is usually FINE — what is missing is the **AFS token**.

**Diagnose:** `klist` shows a valid TGT, but `tokens` prints
`Tokens held by the Cache Manager:` followed by `--End of list--`.

**Fix:** `ssh lxplus 'aklog'` — converts the existing TGT into an AFS token.
Verify with `tokens` (should list `rxkad tokens for cern.ch`).

**Why:** it is easy to misread this as a dropped connection and reach for
`~/bin/lxplus-connect.py` (which just prints `MASTER_ALREADY_UP`) or to assume
the ticket expired and want `kinit`. Neither helps — the TGT was never the
problem. Do NOT ask the user to run `kinit` by hand before checking `tokens`.

Note `fs listquota ~` can still succeed without a token, so it is not a good
test; `ls ~` and `tokens` are.

See [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]] for the genuine connection-drop recovery path (that one
needs the connect script plus remounting), and [[Meta/claude-memory/_history/workflow/vault/vault-push-not-allowlisted|vault-push-not-allowlisted]].
