# Obsidian notes vault — Claude instructions

This is Chirayu's Obsidian vault, synced between the laptop (where Obsidian runs)
and lxplus (where analysis work happens) **via git** (GitHub remote `origin`).
The vault is the research record. (Hindsight was retired on 2026-11-05; its last
state is exported under `Meta/_history/hindsight-export-20261105/`.)

## How work flows: conductor, one worker, keeper

- **Conductor** (pinned T3 thread, brief at `Meta/roles/conductor.md`): routes Chirayu's requests, starts
  **one worker at a time**, says what is running, what is blocked and what needs him.
  Never writes to the vault.
- **Worker** (you, by default, unless your brief names another role): does one task. Writes its results into the vault as
  normal notes (below), with sources and status. Commits locally, **never pushes**.
- **Keeper** (pinned T3 thread, brief at `Meta/roles/keeper.md`): the only one who
  organises the vault, maintains project/subproject READMEs and decks, rebuilds the
  search index, lints, and **pushes after reviewing the changes**.
- Workers do not edit keeper-owned files: subproject `deck/` folders, project
  `README.md` files, `Meta/`. Write a note instead; the keeper consolidates it.
- A result you produced is **agent-reported** until Chirayu or a check validates it.
  Say what was recorded, implemented, tested or validated; never call untested work fixed.
- T3: workers are visible top-level threads, never sub-agents of other agents; no
  relaying messages between agents; explanations ("why/how") go to a Codex thread.

## Searching the vault — use `vault-search` before grepping

**When you need prior context from these notes (past decisions, why something was
done, where a pipeline is documented), run this first:**

```bash
scripts/rag/vault-search "why did the limit come out wrong"
```

It fuses semantic search (meaning-based, finds notes that share no keywords with
your query) with a keyword pass. Use it when you know *what you mean* but not what
the note calls it. Plain `rg` is still the right tool when you know the exact term
(a function name, a dataset tag).

**Two tiers are searched together**, ranked so notes come first:

| Tier | What | Weight |
|---|---|---|
| `notes` | vault markdown, recency-weighted | 1.0 |
| `papers` | `References/**.pdf`, text-extracted | 0.7 |

The `code` tier is **off** (2026-11-05): search analysis code in its own repo with
`rg` (`~/mnt/lxplus/<repo>` locally, `~/<repo>` on lxplus). `VAULT_INDEX_CODE=1`
re-enables it.

Flags:
- `--tier papers` — restrict to a tier (repeatable)
- `--limit N` — number of results (default 8)
- `--paths-only` — bare paths, for piping into Read
- `--no-archive` — hide `Archive/` hits (tagged `[ARCHIVED]` otherwise)
- `--notes-only` — skip the multi-source index

**Newest wins.** Ranking is recency-weighted with a 120-day half-life, so a fresh
note outranks a year-old one by ~2.3× at equal relevance. Recency uses the note's
`date:` frontmatter when present (mtime lies after a git checkout or a typo fix).

**When a note replaces an older one, mark the old one superseded:**

```yaml
---
status: superseded
superseded_by: "[[2026-08-11-card-rebuild-1160]]"
---
```

It is then demoted (×0.55) and tagged `[SUPERSEDED → …]` in results — still
reachable for "what did we think in June", but never mistakable for current.
**Do this whenever you write a note that updates a previous result** (a new limit,
a corrected yield, a revised decision); age alone can't distinguish a stale number
from an old-but-still-valid method note.

**Keeping it fresh.** The keeper rebuilds the index (`scripts/rag/refresh-index.sh`)
when it consolidates. If you need your new notes searchable immediately, run
`scripts/rag/refresh-index.sh --wait`.

Requires Ollama with `bge-m3`. If Ollama or the index is missing it degrades to
keyword-only and says so on stderr — it never hard-fails. **On lxplus there is no
Ollama and the index is gitignored, so it runs keyword-only there; that's expected.**

## Where to write — dump work into the vault

When you generate notes, docs, or plots during a session (laptop or lxplus), **save
them into the right project/subproject folder under `Projects/<ProjectName>/`**
instead of scattering them in scratch dirs. Match the folders that already exist;
if unsure, put it at the project top level and the keeper will file it.

### What goes where
- **Your generated notes / docs / explanations** → `Projects/<ProjectName>/...` as
  `YYYY-MM-DD-<topic>.md` with frontmatter:
  ```yaml
  ---
  tags: [reference]
  status: active
  date: YYYY-MM-DD
  source: lxplus        # or laptop
  ---
  ```
  Put every number next to where it came from (file, command, commit, EOS path).
- **Reference materials** (papers, the big analysis-note / paper **PDFs**, external
  inputs) → `References/<ProjectName>/`. Keep reference PDFs locally for offline
  Obsidian reading; **all PNG and PDF files are gitignored** (Chirayu, 2026-11-05).
  Preserve source/download links in `References/<ProjectName>/papers.md`
  cataloguing them.
- **Plot links** → append to `Projects/<ProjectName>/plots.md` (or a `*-plots.md`) as
  entries with `tags: [plot]`, a `Date`, a `Description`, the `Path`, and a `Link`.
  - Build the CERNBox `Link` from the EOS `Path`:
    `https://cernbox.cern.ch/files/spaces` + path, converting
    `/eos/home-c/cgupta` → `/eos/user/c/cgupta`.

### Sync discipline
- **Start of session:** a SessionStart hook (`scripts/sync-on-start.sh`) fetches and,
  on normal branches, runs `git pull --rebase --autostash`. If it reports a failure,
  resolve it before writing.
- **After writing:** `git add <your files> && git commit -m "<lxplus|laptop>: <what>"`.
  **Do not push** — the keeper reviews and pushes.
- Keep **regenerable** large binaries (plot PNGs, parquet, ROOT files) **out of git** —
  they stay on EOS; only the *link entries* go in the vault. Local deck previews
  and reference PDFs may remain in their project/reference folders, but **no PNG
  or PDF is committed or pushed**, including reference papers (Chirayu, 2026-11-05).
  Preserve existing `.gitignore` rules and source/CERNBox links.

## Safety
- No push (except the keeper, as above), merge, job submission, data deletion or service
  restart without Chirayu's explicit OK. Shell access is not that OK.
- CERN analysis uses the established lxplus setup unless told otherwise; don't submit
  jobs just to verify a record. Preserve original reference files.
- Sensitive CERN/analysis material must not go to an unapproved service or be published.
  Internal decks are not approved public talks; apply CMS public-safety rules before sharing.
- Away work: write it in `Daily/YYYY-MM-DD.md` (what, evidence, next action, "Needs you").

## General
- Don't edit files under `Archive/` — that's a frozen snapshot.
- `Projects/<ProjectName>/` = your generated notes + curated work.
- `References/<ProjectName>/` = external reference materials (papers, PDFs).
- `Meta/` = agent-setup notes and history, kept out of research work.
