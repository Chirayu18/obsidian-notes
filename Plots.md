---
tags: [index]
---

# 🖼️ Plot Archive

All plot entries across every project, newest first. Each entry links to its plot on CERNBox.

```dataview
TABLE WITHOUT ID file.link AS Plot, Date, Description, Link
FROM #plot
SORT Date DESC
```

---

## Adding a new plot

1. Create a note inside the relevant `Projects/<name>/Plots/` folder.
2. Run **Templater → Plot Entry** (`Ctrl+P` → "Templater: Create new note from template", or the Templater hotkey).
3. Paste the **EOS path** and a short **description** when prompted.

The CERNBox link is generated automatically — including the
`/eos/home-c/cgupta` → `/eos/user/c/cgupta` conversion — so you never hand-write the URL.
