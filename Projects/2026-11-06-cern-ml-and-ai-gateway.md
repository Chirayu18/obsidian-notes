---
tags: [reference]
status: active
date: 2026-11-06
source: laptop
---

# CERN ML sessions and AI Gateway in T3

**Agent-reported recommendation: use CERN AI Gateway from laptop T3 first. Treat CERN ML as a candidate for restartable remote development sessions, not as a verified permanent T3 service.** No ML session, GPU allocation, Kubernetes configuration, service installation or cloud tunnel was created.

Chirayu supplied <https://ml.docs.cern.ch/getting-started/#web-ui> and requested the gateway models in T3. The web fetch returned 403; a direct unauthenticated laptop HTTPS fetch returned 200. The findings below come from those public pages, read on 2026-11-06.

## What the ML docs establish

- Sessions have a user-selected name and can be reached with `ssh SESSION@ml.cern.ch`. The curated `registry.cern.ch/mlops/lxplus-like:9` image provides an lxplus-like environment.
- Idle sessions are stopped after **8 hours**. Installed packages in a disposable session are not preserved after deletion; images provide a reproducible installation route.
- `/shared` persists across sessions and has **10 GB per user**. `/scratch` is cleared at session termination. AFS, EOS and CVMFS mounts are supported; AFS still requires Kerberos. A grid-access option installs relevant access configuration, but is not proof that Chirayu's Condor/CRAB workflow works there.
- Outside CERN, non-web access needs a CERN network route, such as eduVPN, lxtunnel or SSH proxying. CLI setup uses CERN SSO; its token is documented as lasting **10 hours**. This is not a blanket lifetime for every credential in a session.
- The resource overview currently marks **CPU-only resources as coming soon**. Do not allocate a GPU merely to host a coding-agent controller whose inference runs elsewhere.

Sources: [session/access/storage guide](https://ml.docs.cern.ch/getting-started/), [resource availability](https://ml.docs.cern.ch/#available-flavors), [environment images and package persistence](https://ml.docs.cern.ch/environments/).

**Unverified:** how idle activity is measured for a non-Jupyter T3 workload; whether T3 is an approved use of this service; CPU-only availability beyond the published page; SQLite/WAL locking and backup suitability on `/shared`; pod restart/recreation behavior for this specific deployment; full Condor/CRAB/CMSSW integration; T3 Connect egress approval. Do not defeat idle culling with artificial keepalives. Do not assume persistent files imply an uninterrupted process.

The previous discussion overstated the need for an uninterrupted SSH connection. A server managed independently of SSH can keep working while the UI disconnects; a client can reconnect later. Durable server identity/database and supported process supervision matter more than retaining one SSH socket forever. The existing pilot deliberately ties lifetime to an SSH-owned bounded supervisor and stores state in node-local `/tmp`. Changing that timer alone does not solve persistence. [T3 remote-access architecture](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md)

## Gateway is independent of the agent host

CERN documents API-key access at `https://aigw.cern.ch`, including chat completions and a model-list endpoint at `/v1/models`. A laptop agent can call that endpoint; it does not need a CERN ML session or a locally allocated GPU. Access from Chirayu's current network still needs a live authenticated test.

The public model page distinguishes **on-premises** models from preview routes hosted on **Google Cloud/Vertex**. A CERN gateway URL is not proof of CERN-local inference for every model. The initial client profile contains only these documented on-premises general models:

- `qwen3.8-27b-fp16` — initial default.
- `hf-qwen3-32b-awq`.
- `gpt-oss-20b`.
- `gemma-4-12b-it-qat-w4a16-ct`.
- `glm-5.3-flash-int4`.

These are configured choices, not yet a verified inventory of Chirayu's key access. Embedding, transcription and cloud preview models were not added. Context/output budgets are conservative local settings, not experimentally measured server capacities. Default sandbox accounts have limited quotas; extra access or quota requires the relevant team. No pricing or departmental billing terms were verified. [Gateway authentication/endpoints/quotas](https://ml.docs.cern.ch/aigw/gettingstarted/), [model IDs and deployment locations](https://ml.docs.cern.ch/aigw/models/)

## Applied laptop configuration

Found an existing `aigw` provider in `~/.omp/agent/models.yml`, using a keyring command and a Qwen model. Its read-only key lookup returned exit 1 with no key, including a retry with environment expansion. No raw keyring output or credential was printed. No authenticated HTTP request was made by those failed preflights. The existing OMP configuration was preserved.

Prepared a separate T3 instance in `~/.t3/userdata/settings.json`:

- Instance ID `cern_gateway`, driver `pi`, display name **CERN AI Gateway**.
- **Disabled pending a valid key and end-to-end checks.** Existing Claude, Codex and Pi entries are unchanged.
- Binary `/home/cgupta/.local/bin/omp`, installed version **18.13.3**.
- Instance environment sets `PI_CODING_AGENT_DIR=/home/cgupta/.omp/profiles/cern-gateway/agent`.
- Launch arguments `--no-extensions --no-title --no-lsp`. T3's explicitly injected extension is separate from extension auto-discovery; no custom extension was installed by this task.

Created owner-only profile/config directories and `models.yml` / `config.yml` with mode 0600. The custom `cern-aigw` provider uses the documented root URL and OpenAI-compatible chat transport. Its key reference reads the private file `~/.config/t3-cern-gateway/api-key`; that file has not yet been populated. No secret is in T3 settings or this vault. Default/smol/slow/plan model roles target CERN Qwen, and interactive model choices are scoped to `cern-aigw/*`. These settings are not an OS/network sandbox.

Private settings backup: `~/.t3/userdata/account-setup-backups/settings-before-cern-gateway-20261106-151530.json` (UTC filename). Restore only the added provider entry when rolling back; preserve unrelated subsequent settings and existing providers.

## Checks and next action

**Passed:** installed OMP parses the new model configuration without stderr; its RPC `get_state` and `get_available_models` commands succeed from an empty `/tmp` directory with context-file/skill/extension discovery disabled for the probe. RPC returns five available configured models. No prompt was sent. T3's native capability listing recognizes **CERN AI Gateway** and reports it disabled, validating settings reload without a restart.

**Network check:** the laptop resolves `aigw.cern.ch` but unauthenticated HTTPS to `/v1/models` times out. The same unauthenticated request from lxplus through the existing SSH master returns **HTTP 401**, establishing reachability from CERN and the authentication requirement. An approved working CERN network route (for example VPN or appropriate proxying) is needed before the prepared laptop provider can be tested; the exact cause of the laptop timeout is not proven. No VPN, proxy or SSH configuration was changed.

**Pending:** gateway reachability from the agent host, a working API key, authenticated model-list access, invented-text response, streaming/tool-call checks, actual T3 inference and a supervised synthetic coding test. Model metadata/credential-source presence is not proof that inference works. No production project or default model was moved to this provider.

Requested the key using T3's private secret card, file delivery, request ID `cern-aigw-key-20261106-1`. Chirayu can create it in the [gateway key UI](https://aigw.cern.ch/ui/?page=api-keys), selecting the intended team and **All Team Models**, with an optional token cap. Do not paste it into chat. After private delivery, store it only in the owner-only key file, check the actual key's model inventory, retain only the approved on-premises choices, and enable the provider only after tests pass.

Implementation sources checked against installed versions: [T3 Pi provider](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/providers-pi.md), [T3 Pi settings schema](https://github.com/pingdotgg/t3code/blob/v0.1.6/packages/provider-pi/src/settings.ts), [OMP 18.13.3 provider configuration](https://github.com/can1357/oh-my-pi/blob/v18.13.3/docs/models.md).

The earlier bounded lxplus T3 wrapper has now completed successfully and reported `pilot_server_stopped=true`, server child return code 130. It was not restarted for gateway setup.
