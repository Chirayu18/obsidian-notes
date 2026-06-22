# Obsidian notes vault — Claude instructions

This is Chirayu's Obsidian vault, synced between the laptop (where Obsidian runs)
and lxplus (where analysis work happens) **via git** (GitHub remote `origin`).

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
