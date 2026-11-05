---
name: hww-signal-private-fetch-iihe
description: "HToWW private H+c/H+b signal NanoAOD must be fetched via fetch.py --onlysignal (IIHE redirector maite), NOT cms-xrd-global"
metadata: 
  node_type: memory
  type: project
  originSessionId: f8da6695-10e4-4546-93f9-e2fae00a093e
  modified: 2026-07-28T14:49:16.807Z
---

The HToWW signal (`HplusCharm_HtoWW`, `HplusBottom_HtoWW`) are **private /USER NanoAODv13
datasets** (DBS `instance=prod/phys03`) with files under `/store/user/...`.

**The correct redirector is PER-ERA — do not assume one works for all (verified 2026-07-28):**

| era | readable via | notes |
|---|---|---|
| **2022postEE** | **IIHE only** (`root://maite.iihe.ac.be:1094`) | `cms-xrd-global` → `[3010] Permission denied` / `[3011] no read access` |
| **2022preEE** | **cms-xrd-global** | IIHE → `[3011] No such file` |
| **2023preBPix** | **cms-xrd-global** | IIHE → `[3011] No such file` |

Always `xrdfs <redirector> stat <lfn>` one file per era before submitting — a wrong
redirector fails every job of that dataset.

**Symptom:** every signal condor job fails `FileNotFoundError: No remaining servers have read
access`; `jobs_status.py`/`runner.py` fileset regeneration does NOT fix it (leaves cms-xrd-global URLs).

**Fix:** rebuild the signal fileset with `fetch.py`, which routes through IIHE:
```
python3 fetch.py --year 2022postEE --onlysignal     # (or --signal)
```
It calls `analysis/filesets/make_signal_filesets.py`: dasgoclient query on prod/phys03, then
**prepends `--site` (default root://maite.iihe.ac.be:1094)** to each LFN. Verified: the postEE
file reads fine via `xrdfs maite.iihe.ac.be:1094 stat` (IsReadable) but fails via cms-xrd-global.

**Signal inventory (DAS-verified 2026-07-28; vault table
Projects/HToWW/2026-07-08-hplusc-hplusb-crab-status.md):**
| era | hplusc | hplusb |
|---|---|---|
| 2022postEE | `cgupta-Run3Summer22EE...postEE_ForNanov13_v1-v1-0a036fde...` 277,345 evt (80 files) | same tag, 298,177 evt (1 file) |
| 2022preEE | `cgupta-Run3Summer22...ForNanov13_v1-v4-8653679c...` 328,838 evt (95 files) | **tvanlaer**-published `...v1-v1-8653679c...` 809,802 evt (276 files) |
| 2023preBPix | `cgupta-Run3Summer23...ForNanov13_v1-v1-666a5f9b...` 280,356 evt (81 files) | **DOES NOT EXIST** |
| 2023postBPix | **DOES NOT EXIST** | **DOES NOT EXIST** |

hplusc preEE v1 is a 3,436-event stub — use **v4** (v2/v3/v4 all 328,838).
The 2022preEE yaml originally had **no** HplusBottom entry; added 2026-07-28 (tvanlaer tag).
The old hww_combine_fixed run used the preEE(v4) signal in a postEE config (wrong era);
the 2dcat config correctly uses postEE(v1).

Proxy note: dasgoclient/xrootd need X509_USER_PROXY set explicitly to
`/afs/cern.ch/user/c/cgupta/private/x509up_u151861` in over-ssh sessions. See [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]].
