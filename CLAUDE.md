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
your query) with a keyword pass, via reciprocal rank fusion. Use it when you know
*what you mean* but not what the note calls it. Plain `rg` is still the right tool
when you know the exact term (a function name, a dataset tag).

- `--limit N` — number of results (default 8)
- `--paths-only` — bare paths, for piping into Read
- `--no-archive` — hide `Archive/` hits (they're tagged `[ARCHIVED]` otherwise)
- `--build` — refresh the index; **run this after writing notes**, it's incremental
  (~0.4s when nothing changed, ~75s for a full rebuild)

Requires Ollama running with `bge-m3` pulled. If Ollama is down it degrades to
keyword-only and says so on stderr — it never hard-fails. On lxplus (no Ollama)
it runs keyword-only; that's expected.

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
