---
tags: [reference, evaluation]
status: active
date: 2026-08-02
source: laptop
---

# Raw test log — PBJ vs code2prompt

Backing evidence for [[2026-08-02-pbj-vs-code2prompt-deck]].

## Environment
- Python 3.14.4, node 24.10.0, git 2.53.0 — **no Rust initially**
- code2prompt **v4.3.0** via `cargo install code2prompt` (~66 s build)
- Chrome via browser automation; PBJ at `promptbutterjam.com` (redirects to `www.`)

## Install attempts
| Route | Result |
|---|---|
| `pip install code2prompt` | PEP 668 externally-managed-environment |
| venv + pip (py3.14) | `tiktoken` wheel build failed — no prebuilt wheel, needs Rust |
| `npm install code2prompt` | Installed **unrelated** package v1.1.4 (bins: `cmd`, `command-code`) |
| `cargo install code2prompt` | ✅ v4.3.0 |

## code2prompt benchmarks (best of 3)
| Target | Files | Tokens | Wall | RSS |
|---|---:|---:|---:|---:|
| synthetic edge repo | 26 | 154 | 0.03 s | ~45 MB |
| obsidian vault | 3,682 | 356K | 0.08 s | ~45 MB |
| pallets/click | 194 | 387K | 0.10 s | ~47 MB |
| psf/requests | 157 | 722K | 0.24 s | ~49 MB |
| django/django | 7,104 | 10M | 1.19 s | ~248 MB |

Django narrowed: `-i "**/*.py" -e "**/tests/**" -e "**/*.lock"` → still **1M tokens**.

## Synthetic edge repo — default-run results
| Hazard | Included in output? |
|---|---|
| `.env` (AWS key, DB password) | No — dotfile excluded |
| `config.py` with `sk-live-…` | **Yes** (expected — normal source file) |
| `node_modules/leftpad` | No — `.gitignore` respected |
| `big.bin` (3 MB random) | Name only, body skipped (output 695 B) |
| `unicode_文件_🎉.py` | Yes, handled correctly |
| `symlink_escape.txt -> /etc/passwd` | **Yes — `root:x:0:0:` inlined, without `-L`** |

Flag interactions: `--hidden` → `.env` AWS key **does** appear.
`--no-ignore` → `node_modules` pulled in.

Exit codes verified correct: bad path → 1, `--diff` on non-git → 1, valid → 0.
(An earlier "exit=0" reading was an artifact of `$?` capturing a piped `tail`.)

## PBJ network capture
Patched `fetch` / `XMLHttpRequest` / `sendBeacon`. Canary: `CANARYSENTINEL7Z9QX`.

- Prompt text leaked: **NO** (canary never appeared in any payload)
- Cookies: **none**; localStorage: only `ps_tour_seen_v1`
- Sole endpoint: `POST /api/events`

Payload on sharpen (`sharpen_requested`, `demo_completed`):
```json
{"task_id":"8ffc7e99-…","event_name":"sharpen_requested","task_type":"debugging",
 "assistant":"copilot","model":"sonnet-4-5","thinking_effort":"medium",
 "prompt_chars":1107,"context_chars":334,"estimated_saving_usd":0.023622,
 "estimate_version":"pricing-2026-08-02","properties":{"mode":"demo"}}
```

## PBJ demo-splice — verbatim evidence
Input goal: race condition / double-charge / idempotency key.
Output contained interleaved text never entered:

```
FixDiagnose awhy racethe conditionp95 double-charginglatency customers.
…of OrdersController#index regressed after customer filtering was added.
```
Plus injected constraint `Reproduce the slow query with EXPLAIN ANALYZE`
and `Selected files or areas: 13` (input had 1).

## PBJ secret pass-through
Pasted `AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/…`, `DB_PASSWORD=hunter2`,
`ghp_16CharsRealLookingToken000000000` into context (non-demo mode)
→ all three echoed verbatim in output while `EXCLUDE: Secrets…` was present.

**Note:** a first pass suggested redaction; that was the frozen-preview bug
(preview stale while textarea updated). Retested after *Exit demo* → all leaked.

## Testing constraint honored
Per instruction, **nothing public/private from the vault was submitted to the
site**. All PBJ inputs were invented snippets. Vault + public repos were tested
only through the local code2prompt binary (no network).
