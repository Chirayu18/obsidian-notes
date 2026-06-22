---

---
Made config minimalish: [https://github.com/Chirayu18/nvim](https://github.com/Chirayu18/nvim)

---

# Neovim Configuration — Comprehensive Reference

> **Leader Key:** `Space` · **Local Leader Key:** `\`

> Plugin Manager: **lazy.nvim** · Colorscheme: **onedark / onelight**

---

## Directory Structure

```javascript
~/.config/nvim/
├── init.lua                    # Entry point → loads config.lazy
├── lazy-lock.json              # Plugin version lockfile
├── static/
│   └── neovim.cat              # ASCII art
└── lua/
    ├── config/
    │   ├── lazy.lua            # Bootstrap lazy.nvim, plugin loading, load order
    │   ├── options.lua         # Vim options (leader, UI, indentation, search, etc.)
    │   ├── util.lua            # Global `om` namespace + helper functions
    │   ├── keymaps.lua         # All keymaps (loaded on VeryLazy event)
    │   ├── commands.lua        # User commands (loaded on VeryLazy event)
    │   ├── functions.lua       # Utility functions (ChangeFiletype, ToggleLineNumbers, etc.)
    │   └── autocmds.lua        # Autocommands (yank highlight, etc.)
    └── plugins/
        ├── lsp.lua             # LSP, completion (blink.cmp), formatting (conform.nvim)
        ├── treesitter.lua      # Treesitter + autopairs
        ├── ui.lua              # Lualine, gitsigns, devicons
        ├── colorscheme.lua     # Onedarkpro theme config
        ├── coding.lua          # nvim-surround
        ├── editor.lua          # nvim-surround (duplicate)
        └── remote.lua          # Empty (placeholder)
```

---

## Plugin List

### Plugin Manager

| Plugin | Purpose |
| --- | --- |
| **folke/lazy.nvim** | Plugin manager with lazy-loading, lockfile, and auto-checking |

### LSP & Completion

| Plugin | Purpose |
| --- | --- |
| **neovim/nvim-lspconfig** | LSP server configuration |
| **mason-org/mason.nvim** | LSP/tool installer (UI with `:Mason`) |
| **mason-org/mason-lspconfig.nvim** | Bridge between Mason and lspconfig |
| **saghen/blink.cmp** | Completion engine (sources: lsp, path, snippets, buffer) |
| **onsails/lspkind.nvim** | VS Code-like icons in completion menu |
| **stevearc/conform.nvim** | Code formatting (format-on-save) |

### Treesitter & Editing

| Plugin | Purpose |
| --- | --- |
| **nvim-treesitter/nvim-treesitter** | Syntax highlighting, code parsing |
| **windwp/nvim-autopairs** | Auto-close brackets, quotes (treesitter-aware) |
| **kylechui/nvim-surround** | Surround text with delimiters (`cs`, `ds`, `ys`) |

### UI & Appearance

| Plugin | Purpose |
| --- | --- |
| **olimorris/onedarkpro.nvim** | Colorscheme (onedark dark / onelight light) |
| **nvim-lualine/lualine.nvim** | Statusline (mode, branch, diff, diagnostics, file info) |
| **lewis6991/gitsigns.nvim** | Git change signs in the sign column |
| **nvim-tree/nvim-web-devicons** | File type icons |

---

## Installed LSP Servers (via Mason)

| Server | Language |
| --- | --- |
| **clangd** | C / C++ |

> Additional servers can be added in `lua/plugins/lsp.lua` under `ensure_installed`.

## Formatter Configuration (conform.nvim)

| Language | Formatters |
| --- | --- |
| Python | `black`, `isort` |
| C++ | `clang_format` |

Format-on-save is enabled with a 500ms timeout and LSP fallback.

---

## Treesitter Parsers

Automatically installed if missing: `python`, `cpp`, `c`, `lua`, `vim`, `vimdoc`, `markdown`, `markdown_inline`, `bash`, `json`, `yaml`

---

## Options Summary

### Leader Keys

- **Leader:** `Space`
- **Local Leader:** `\`

### Line Numbers

- Absolute + relative numbers enabled

### Indentation

- Tab width: **4 spaces**, expand tabs, smart indent, shift round

### Search

- Case insensitive (smart case when uppercase used), highlight + incremental search

### UI

- True color, cursor line, sign column always visible
- Color columns at **80** and **120**
- Command height: 0, global statusline, mode hidden (shown in lualine)
- Mouse enabled, no line wrap

### Splits

- Horizontal splits open below, vertical splits open right

### Scrolling

- Scroll offset: 5 lines, side scroll offset: 8 columns

### Files

- Persistent undo (stored in `stdpath('data')/undos`)
- No backup, no swap files

### Completion

- `menuone,noselect`, update time 250ms, timeout 300ms

### Whitespace Display

- Visible tabs (`» `), trailing spaces (`·`), non-breaking spaces (`␣`)

### Wildmenu

- Mode: `list:longest`
- Ignored: `.git/`, `node_modules/`, `__pycache__/`, `*.pyc`

### Disabled Built-in Plugins

- `gzip`, `matchit`, `matchparen`, `tarPlugin`, `tohtml`, `tutor`, `zipPlugin`

---

## All Keymaps

### Basic Operations

| Key | Mode | Description |
| --- | --- | --- |
| `<C-q>` | Normal | Quit Neovim |
| `<C-s>` | Normal, Insert | Save buffer (silent) |
| `<C-y>` | Normal | Copy entire buffer to system clipboard |
| `<C-c>` | Normal | Delete buffer |
| `<Tab>` | Normal | Next buffer |
| `<S-Tab>` | Normal | Previous buffer |
| `<Esc>` | Normal | Clear search highlights (`:noh`) |
| `<S-w>` | Normal | Hide WinBar |

### Window / Split Management

| Key | Mode | Description |
| --- | --- | --- |
| `\sv` | Normal | Create vertical split |
| `\sh` | Normal | Create horizontal split |
| `\sc` | Normal | Close current split |
| `\so` | Normal | Close all splits except current |
| `<C-k>` | Normal | Move to split above |
| `<C-j>` | Normal | Move to split below |
| `<C-h>` | Normal | Move to split left |
| `<C-l>` | Normal | Move to split right |

### Line Navigation

| Key | Mode | Description |
| --- | --- | --- |
| `B` | Normal, Visual | Jump to beginning of line (`^`) |
| `E` | Normal, Visual | Jump to end of line (`$`) |
| `<CR>` | Normal | Insert blank line below cursor |
| `<S-CR>` | Normal | Insert blank line above cursor |
| `<A-j>` | Normal | Move current line down |
| `<A-j>` | Visual | Move selection down |
| `<A-k>` | Normal | Move current line up |
| `<A-k>` | Visual | Move selection up |

### Text Wrapping (Local Leader)

| Key | Mode | Description |
| --- | --- | --- |
| `\(` | Normal | Wrap word under cursor in `()` |
| `\(` | Visual | Wrap selection in `()` |
| `\[` | Normal | Wrap word under cursor in `[]` |
| `\[` | Visual | Wrap selection in `[]` |
| `\{` | Normal | Wrap word under cursor in `{}` |
| `\{` | Visual | Wrap selection in `{}` |
| `\"` | Normal | Wrap word under cursor in `""` |
| `\"` | Visual | Wrap selection in `""` |

### Surround (nvim-surround, Visual mode)

| Key | Mode | Description |
| --- | --- | --- |
| `(` or `)` | Visual | Surround selection with `()` |
| `{` or `}` | Visual | Surround selection with `{}` |
| `[` or `]` | Visual | Surround selection with `[]` |

### Appending Characters

| Key | Mode | Description |
| --- | --- | --- |
| `\,` | Normal | Append comma at end of line |
| `\;` | Normal | Append semicolon at end of line |

### Indentation

| Key | Mode | Description |
| --- | --- | --- |
| `>` | Visual | Indent and keep selection |
| `<` | Visual | Outdent and keep selection |

### Find and Replace

| Key | Mode | Description |
| --- | --- | --- |
| `\fw` | Normal | Replace word under cursor in entire buffer |
| `\fl` | Normal | Replace word under cursor in current line |

### Miscellaneous

| Key | Mode | Description |
| --- | --- | --- |
| `\U` | Normal | Capitalize (uppercase) current word |

---

## Multiple Cursors

Custom implementation using search + `cgn` (no plugin needed).

### Simple Multi-Cursor (`cn` / `cN`)

1. Position cursor on a word (or make a visual selection)
2. Press `cn` (forward) or `cN` (backward)
3. Type the replacement text
4. Press `Esc` to return to Normal mode
5. Press `.` to repeat on the next occurrence

| Key | Mode | Description |
| --- | --- | --- |
| `cn` | Normal | `*``cgn` — search forward, change next match |
| `cn` | Visual | Search selection forward, change next match |
| `cN` | Normal | `*``cgN` — search forward, change previous match |
| `cN` | Visual | Search selection forward, change previous match |

### Macro-based Multi-Cursor (`cq` / `cQ`)

6. Position cursor on a word (or make a visual selection)
7. Press `cq` (forward) or `cQ` (backward) to start recording a macro
8. Perform your edits
9. Press `Esc` to return to Normal mode
10. Press `Enter` to replay the macro across all remaining matches

| Key | Mode | Description |
| --- | --- | --- |
| `cq` | Normal | Start macro recording on forward search matches |
| `cq` | Visual | Start macro recording on forward selection matches |
| `cQ` | Normal | Start macro recording on backward search matches |
| `cQ` | Visual | Start macro recording on backward selection matches |

---

## LSP Keymaps

> Only active when an LSP server is attached to the buffer.

| Key | Mode | Description |
| --- | --- | --- |
| `gd` | Normal | Go to definition |
| `gr` | Normal | Find references |
| `gI` | Normal | Go to implementation |
| `gy` | Normal | Go to type definition |
| `K` | Normal | Hover documentation |
| `ga` | Normal | Code action |
| `grn` | Normal | Rename symbol |
| `gf` | Normal | Show diagnostics (floating window) |
| `[d` | Normal | Previous diagnostic |
| `]d` | Normal | Next diagnostic |
| `gq` | Normal | Format buffer (via conform.nvim with LSP fallback) |

### Diagnostic Signs

| Severity | Icon |
| --- | --- |
| Error |   |
| Warning |   |
| Info |   |
| Hint |   |

Virtual text is enabled with `●` prefix and 4-space spacing.

---

## Completion (blink.cmp)

Sources: **LSP**, **Path**, **Snippets**, **Buffer**

| Key | Mode | Description |
| --- | --- | --- |
| `<C-Space>` | Insert | Toggle completion menu + documentation |
| `<C-e>` | Insert | Hide completion menu |
| `<CR>` | Insert | Accept selected completion |
| `<Tab>` | Insert | Next item / snippet jump forward |
| `<S-Tab>` | Insert | Previous item / snippet jump backward |

Features: auto brackets on accept, auto-show documentation (250ms delay), rounded borders, signature help enabled.

---

## User Commands

| Command | Description |
| --- | --- |
| `:LineNumbers` | Toggle relative line numbers on/off |
| `:ChangeFiletype` | Interactively change buffer filetype |
| `:CopyMessage` | Copy `:messages` output to clipboard |
| `:New` | Create a new empty buffer |
| `:Theme` | Toggle between onedark (dark) and onelight (light) |

---

## Autocommands

| Trigger | Behavior |
| --- | --- |
| `TextYankPost` | Briefly highlight yanked text |
| `FileType` (treesitter) | Auto-start treesitter highlighting per filetype |
| `User VeryLazy` | Load keymaps and commands after all plugins |

---

## Global Utility Namespace (`om`)

The config defines a global `_`[`G.om`](http://g.om/) table with helper functions used throughout:

| Function | Purpose |
| --- | --- |
| `om.has(feature)` | Check if Neovim has a feature/version |
| `om.on_big_screen()` | Returns true if terminal is >150 cols and ≥40 lines |
| `om.set_keymaps(lhs, rhs, mode, opts)` | Wrapper around `vim.keymap.set` |
| `om.create_user_command(name, desc, cmd, opts)` | Wrapper around `nvim_create_user_command` |
| `om.create_autocmd(autocmd, opts)` | Wrapper around `nvim_create_autocmd` |
| `om.ChangeFiletype()` | Interactive filetype changer |
| `om.MoveToBuffer()` | Interactive buffer number jump |
| `om.ToggleLineNumbers()` | Toggle relative line numbers |
| `om.ToggleTheme()` | Switch dark/light colorscheme |

---

## Lualine Statusline Layout

| Section | Content |
| --- | --- |
| A (left) | Mode |
| B | Git branch, diff stats |
| C | Filename (relative path) |
| X (right) | Diagnostics, encoding, file format, filetype |
| Y | Progress (%) |
| Z | Line:Column location |

Separators: `|` (components),  /  (sections). Global statusline enabled.

---

## Git Signs (gitsigns.nvim)

| Sign | Meaning |
| --- | --- |
| `│` | Added line |
| `│` | Changed line |
| `_` | Deleted line |
| `‾` | Top-deleted line |
| `~` | Changed + deleted line |

---

## Colorscheme (onedarkpro.nvim)

- **Default:** `onedark` (dark background)
- **Light variant:** `onelight` (toggle with `:Theme`)
- **Style overrides:** comments → *italic*, keywords → *italic*, functions → **bold**, methods → **bold**
- Cursorline highlighting enabled

---

## Tips & Workflows

11. **Quick multi-replace:** Position on word → `cn` → type replacement → `Esc` → `.` `.` `.` to repeat
12. **Complex multi-edit:** Position on word → `cq` → do edits → `Esc` → `Enter` to replay everywhere
13. **Fast wrapping:** `\(` wraps a word in parens, works in visual mode for selections too
14. **Buffer workflow:** `<Tab>` / `<S-Tab>` to cycle, `<C-c>` to close
15. **Format on save** is automatic for Python and C++; manual format with `gq`
16. **Persistent undo** means you can undo changes even after closing and reopening a file
17. **Theme toggle:** `:Theme` switches between dark and light instantly
18. **Add new LSP servers:** Edit `ensure_installed` in `lua/plugins/lsp.lua` and restart