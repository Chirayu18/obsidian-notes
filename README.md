---
tags: [index]
---

# 📓 How to use this vault

Physics-analysis notes (HToWW, Alpaka), synced **laptop ⇄ GitHub ⇄ lxplus** via git.
Start from [[Dashboard]] (pin it) for a live view of open work.

## Layout

| Folder | What lives here |
|---|---|
| `Projects/<Name>/` | Your curated notes + generated work per analysis. lxplus session dumps land in dated subfolders `Projects/<Name>/lxplus-YYYY-MM-DD/`. |
| `References/<Name>/` | Stable external inputs — papers, analysis-note **PDFs** (committed so they open offline). Catalogue them in `papers.md`. |
| `Daily/` | One note per day (journal + today's tasks). |
| `Templates/` | Templater templates (Daily Note, Meeting, Plot Entry, …). |
| `Archive/` | Frozen snapshot. **Local-only** (gitignored) and hidden from Obsidian. Don't edit. |
| `Dashboard.md`, `Plots.md` | Live index notes (Dataview). |

## Daily workflow

1. **Open today's daily note** (Calendar plugin, or the daily-note hotkey). It's created from `Templates/Daily Note`.
2. Write **Focus**, jot tasks as `- [ ]`, keep a **Log**. Open tasks here appear under **Today** on [[Dashboard]] — no tags needed.
3. Check [[Dashboard]] for meeting action items and open project tasks across everything.

## Recording a meeting

`Ctrl+P` → **Templater: Create new note from template** → **Meeting**.
It prompts for project, date, time → creates `YYYY-MM-DD-HHMM.md` in
`Projects/<Project>/Meetings/` with Agenda / Notes / Action Items.
Open `- [ ]` items tagged `#meeting` show on the Dashboard under *Meeting action items*.

## Adding a plot

Plots themselves stay on **EOS** — the vault stores *links*, not binaries.

- **One plot:** make a note in `Projects/<Project>/Plots/`, run **Templater → Plot Entry**,
  paste the EOS path + description. The CERNBox link is built automatically
  (`/eos/home-c/cgupta` → `/eos/user/c/cgupta`).
- **Many plots from one session:** put them as `###` entries in a single `*-plots.md`
  note with `tags: [plot]` frontmatter; each entry has `**Date:**`, `**Description:**`,
  `**Link:**`. Both styles surface on [[Dashboard]] and [[Plots]].

## Tasks & the Dashboard

- Task = a Markdown checkbox `- [ ]` anywhere. `- [x]` marks it done.
- A note is "active" if its frontmatter has `status: active` — that's what the Dashboard's
  project-task and active-note queries filter on. Set `status: done`/remove it to retire a note.
- The Dashboard needs Dataview's **JavaScript Queries** enabled (already on) for the plots table.

## Sync (laptop ⇄ lxplus)

- See [[SYNC]] for the full setup. Short version:
  - **Laptop:** `git pull` / `git push` (or the **Obsidian Git** plugin to automate).
  - **lxplus:** clone the repo; Claude there follows [[CLAUDE]] — writes into
    `Projects/<Name>/` (notes) and `References/<Name>/` (PDFs), then runs
    `scripts/vault-dump.sh "msg"` to pull/commit/push.
- Regenerable binaries (plot PNGs, parquet, ROOT) **never** go in git — only links.
  Reference PDFs are the one committed-binary exception.
