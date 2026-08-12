# Obsidian notes vault — Claude instructions

This is Chirayu's Obsidian vault, synced between the laptop (where Obsidian runs)
and lxplus (where analysis work happens) **via git** (GitHub remote `origin`).

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

**Three tiers are searched together**, ranked so notes come first:

| Tier | What | Weight |
|---|---|---|
| `notes` | vault markdown, recency-weighted | 1.0 |
| `papers` | `References/**.pdf`, text-extracted | 0.7 |
| `code` | lxplus analysis repos via the sshfs mount | 0.5 |

Flags:
- `--tier code` / `--tier papers` — restrict to a tier (repeatable)
- `--limit N` — number of results (default 8)
- `--paths-only` — bare paths, for piping into Read
- `--no-archive` — hide `Archive/` hits (tagged `[ARCHIVED]` otherwise)
- `--notes-only` — skip the multi-source index

Results are tagged `[PDF]` / `[CODE]` so you know what you're looking at. A `code`
hit reads `lxplus:higgscharm/runner.py` → that's `~/mnt/lxplus/higgscharm/runner.py`
locally, `~/higgscharm/runner.py` on lxplus.

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

**Keeping it fresh.** `scripts/rag/build_index.py` rebuilds incrementally: it
re-embeds changed files and **prunes entries whose file is gone**. SessionEnd and
PreCompact hooks fire `scripts/rag/refresh-index.sh`, which detaches the rebuild
(~8ms to return, so it never blocks). Run it by hand after writing a batch of notes
if you want them searchable immediately:

```bash
scripts/rag/refresh-index.sh --wait     # foreground, shows result
```

Requires Ollama with `bge-m3`. If Ollama or the index is missing it degrades to
keyword-only and says so on stderr — it never hard-fails. **On lxplus there is no
Ollama and the index is gitignored, so it runs keyword-only there; that's expected.**
Code indexing happens laptop-side over the sshfs mount, since that's where Ollama is.

## When running on lxplus — dump work into the vault

When you generate notes, docs, or plots during a session on lxplus, **save them into
`Projects/<ProjectName>/`** instead of scattering them in scratch dirs. Then commit and
push so they reach the laptop's Obsidian.

`<ProjectName>` is the analysis you're working on (e.g. `HToWW`, `Alpaka`). Match the
folder names already under `Projects/`. Put a session's dump in a clearly-labelled
subfolder (e.g. `Projects/HToWW/lxplus-YYYY-MM-DD/`) so it doesn't clobber the curated notes.

### What goes where
- **Your generated notes / docs / explanations** → `Projects/<ProjectName>/...` as
  `YYYY-MM-DD-<topic>.md` with frontmatter:
  ```yaml
  ---
  tags: [reference]
  status: active
  date: YYYY-MM-DD
  source: lxplus
  ---
  ```
- **Reference materials** (papers, the big analysis-note / paper **PDFs**, external
  inputs) → `References/<ProjectName>/`. These reference PDFs **are committed** (they're
  stable inputs you want to read offline in Obsidian). Add a `References/<ProjectName>/papers.md`
  cataloguing them.
- **Plot links** → append to `Projects/<ProjectName>/plots.md` (or a `*-plots.md`) as
  entries with `tags: [plot]`, a `Date`, a `Description`, the `Path`, and a `Link`.
  - Build the CERNBox `Link` from the EOS `Path`:
    `https://cernbox.cern.ch/files/spaces` + path, converting
    `/eos/home-c/cgupta` → `/eos/user/c/cgupta`.
  - These `#plot` entries auto-appear in the laptop's `Dashboard.md` and `Plots.md`.

### Sync discipline
- **Start of session:** `git pull --rebase` (a SessionStart hook does this automatically;
  if it didn't run, do it manually).
- **After writing:** `git add -A && git commit -m "lxplus: <what>" && git push`.
- Keep **regenerable** large binaries (plot PNGs, parquet, ROOT files) **out of git** —
  they stay on EOS; only the *link entries* go in the vault. Reference **PDFs/papers** are
  the exception and may be committed under `References/`. The `.gitignore` already covers caches.

## General
- Don't edit files under `Archive/` — that's a frozen snapshot.
- `Projects/<ProjectName>/` = your generated notes + curated work.
- `References/<ProjectName>/` = external reference materials (papers, PDFs).
