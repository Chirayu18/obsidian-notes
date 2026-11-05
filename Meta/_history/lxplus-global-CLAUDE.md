# Global Claude instructions (lxplus)

I am Chirayu, a CMS physicist working on HToWW and Alpaka analyses on lxplus.

## Always: dump notes, docs, and plots into my Obsidian vault

I keep an Obsidian vault (a git repo) at `~/obsidian-notes`, synced to my laptop
via GitHub. **Whenever you generate notes, documentation, explanations, or plots
in any session — regardless of which directory we're working in — also record them
in that vault** so they reach my laptop's Obsidian. Don't leave notes scattered in
scratch dirs.

### Where to write
- Save under `~/obsidian-notes/References/<ProjectName>/`, where `<ProjectName>`
  matches a folder under `~/obsidian-notes/Projects/` (e.g. `HToWW`, `Alpaka`).
  Create `References/<ProjectName>/` if it doesn't exist.
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
- **Plot links** → append entries to `References/<ProjectName>/plots.md`, each with
  `tags: [plot]`, `Date`, `Description`, `Path` (the EOS path), and `Link`.
  Build `Link` from the EOS path as:
  `https://cernbox.cern.ch/files/spaces` + path,
  converting `/eos/home-c/cgupta` → `/eos/user/c/cgupta`.
  (Large plot binaries stay on EOS — only the link entry goes in the vault.)

### Sync discipline
- Before writing into the vault, pull: `git -C ~/obsidian-notes pull --rebase --autostash`.
- After writing, push it:
  `~/obsidian-notes/scripts/vault-dump.sh "short description of what you added"`
  (this pulls, commits, and pushes in one step).
- Never touch `~/obsidian-notes/Archive/` — it's a local-only snapshot on the laptop
  and won't exist in the lxplus clone anyway.

If `~/obsidian-notes` doesn't exist yet, tell me to clone it (see its `SYNC.md`)
rather than inventing another location.
