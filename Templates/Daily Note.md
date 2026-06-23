---
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [daily]
---

# <% tp.date.now("dddd, MMMM Do") %> · <% tp.date.now("YYYY") %>

`BUTTON[open-dashboard]` &nbsp; ← [[<% tp.date.now("YYYY-MM-DD", -1) %>|Yesterday]] · [[<% tp.date.now("YYYY-MM-DD", 1) %>|Tomorrow]] →

## 🎯 Focus
> What matters most today.
- 

## ✅ Tasks
> Open tasks here appear under **Today** on the [[Dashboard]]. Tag `#today` to pin a task from any note.
- [ ] 

## 🗓️ Carried over
> Yesterday's unfinished tasks (tick or copy up).

```dataview
TASK
FROM "Daily"
WHERE !completed AND file.name = dateformat(date(this.file.name) - dur(1 day), "yyyy-MM-dd")
```

## 📝 Log
> What happened / decisions / where I left off.
- 

---
```meta-bind-button
label: 📊 Dashboard
id: open-dashboard
hidden: true
style: default
actions:
  - type: open
    link: "[[Dashboard]]"
```
