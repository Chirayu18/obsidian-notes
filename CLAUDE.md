# Obsidian notes vault — Claude instructions

This is Chirayu's Obsidian vault, synced between the laptop (where Obsidian runs)
and lxplus (where analysis work happens) **via git** (GitHub remote `origin`).

## When running on lxplus — dump work into the vault

When you generate notes, docs, or plots during a session on lxplus, **save them into
this vault under `References/<ProjectName>/`** instead of scattering them in scratch
dirs. Then commit and push so they reach the laptop's Obsidian.

`<ProjectName>` is the analysis you're working on (e.g. `HToWW`, `Alpaka`). Match the
folder names already under `Projects/`. Create `References/<ProjectName>/` if absent.

### What to write where
- **Notes / docs / explanations** → `References/<ProjectName>/YYYY-MM-DD-<topic>.md`
  with frontmatter:
  ```yaml
  ---
  tags: [reference]
  status: active
  date: YYYY-MM-DD
  source: lxplus
  ---
  ```
- **Plot links** → append to `References/<ProjectName>/plots.md` as entries with
  `tags: [plot]`, a `Date`, a `Description`, the `Path`, and a `Link`.
  - Build the CERNBox `Link` from the EOS `Path` like this:
    `https://cernbox.cern.ch/files/spaces` + path, converting
    `/eos/home-c/cgupta` → `/eos/user/c/cgupta`.
    Example: `/eos/user/c/cgupta/public/hww_x/` →
    `https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/public/hww_x/`
  - These `#plot` entries auto-appear in the laptop's `Dashboard.md` and `Plots.md`.

### Sync discipline
- **Start of session:** `git pull --rebase` (a SessionStart hook does this automatically;
  if it didn't run, do it manually) so you build on the latest from the laptop.
- **After writing:** `git add -A && git commit -m "lxplus: <what>" && git push`.
- Keep large binaries (plots, parquet, ROOT files) **out of git** — they stay on EOS.
  Only the *link entries* go in the vault. The `.gitignore` already covers caches.

## General
- Don't edit files under `Archive/` — that's a frozen snapshot.
- Active project notes live under `Projects/`; lxplus dumps land under `References/`.
- The laptop pulls these in and reviews/promotes them into `Projects/` as needed.
