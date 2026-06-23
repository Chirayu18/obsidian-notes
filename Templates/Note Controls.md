---
tags: [meta]
---

# Note Controls

These two **global** Meta Bind buttons are registered here once and can be used in any
note with `` `BUTTON[toggle-status]` `` and `` `BUTTON[toggle-pin]` `` (or combined:
`` `BUTTON[toggle-status, toggle-pin]` ``). Templates already reference them.

> Don't delete this note — it's where the buttons live. (Keep it open once after a restart
> so Meta Bind registers the global buttons.)

```meta-bind-button
label: ✅ Done / 🔄 Active
id: toggle-status
hidden: true
class: ""
tooltip: Toggle this note's status between active and done
style: primary
actions:
  - type: inlineJS
    code: |
      const file = app.workspace.getActiveFile();
      await app.fileManager.processFrontMatter(file, fm => {
        fm.status = (fm.status === "active") ? "done" : "active";
      });
```

```meta-bind-button
label: 📌 Pin / Unpin
id: toggle-pin
hidden: true
tooltip: Pin/unpin this note to the Dashboard (stays even when done)
style: default
actions:
  - type: inlineJS
    code: |
      const file = app.workspace.getActiveFile();
      await app.fileManager.processFrontMatter(file, fm => {
        fm.pinned = !(fm.pinned === true);
      });
```

## Live preview here
status: `VIEW[{status}]` · pinned: `VIEW[{pinned}]`
`BUTTON[toggle-status, toggle-pin]`
