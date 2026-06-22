# Vault sync: laptop ↔ GitHub ↔ lxplus

The vault is a git repo (`origin` = github.com/Chirayu18/obsidian-notes).
GitHub is the bridge: both the laptop and lxplus push/pull from it.

```
  Laptop (Obsidian)  ⇄  GitHub (origin)  ⇄  lxplus (Claude + analysis)
```

## One-time setup on lxplus

```bash
ssh lxplus-gpu.cern.ch          # or your usual lxplus host
cd ~                            # or wherever you keep working dirs
git clone https://github.com/Chirayu18/obsidian-notes.git
cd obsidian-notes
git config user.name  "Chirayu Gupta"
git config user.email "chirayu.gupta@vub.be"
```

That's it. The clone already contains `CLAUDE.md` (tells Claude to dump into
`References/<Project>/`) and `.claude/settings.json` (a SessionStart hook that
auto-`git pull`s when a Claude session starts here).

## Daily use

- **On lxplus**, start Claude Code from inside `~/obsidian-notes`. It will:
  1. auto-pull on session start (hook),
  2. write notes/plot-links into `References/<ProjectName>/` per `CLAUDE.md`,
  3. commit + push when done.
- **On the laptop**, pull to see it in Obsidian:
  ```bash
  cd ~/obsidian-notes && git pull --rebase
  ```
  (Or install the **Obsidian Git** community plugin to auto pull/push — recommended,
  so you never run git by hand on the laptop.)

## Notes
- Large binaries (plots, ROOT/parquet) stay on EOS — only *link entries* go in the vault.
- If a pull/push conflicts, it's almost always `.obsidian/workspace.json` — already
  gitignored, so conflicts should be rare. Resolve by keeping your local copy.
- lxplus dumps land in `References/`; promote anything important into `Projects/` from
  the laptop.
```
