---
tags: [dashboard]
---

# 📊 Dashboard

> Live overview of open work. Pin this note (right-click tab → Pin). Nothing here needs editing — queries auto-discover projects.

`BUTTON[new-daily]` `BUTTON[new-meeting]`

## 📌 Pinned
Notes with `pinned: true` — always shown here, even when `done`. Toggle with the
**📌 Pin / Unpin** and **✅ Done / 🔄 Active** buttons inside any note (Meta Bind).

```dataview
TABLE WITHOUT ID file.link AS Note, status AS Status, file.mday AS Modified
FROM -"Archive"
WHERE pinned = true
SORT status ASC, file.mday DESC
```

---

## 🔥 Today
Open tasks tagged `#today` anywhere, plus open tasks in today's daily note.

```dataview
TASK
FROM -"Archive"
WHERE !completed
  AND (contains(text, "#today") OR file.name = dateformat(date(today), "yyyy-MM-dd"))
GROUP BY file.link
```

---

## 🗣️ Meeting action items
Open tasks from any meeting note across all projects.

```dataview
TASK
FROM "Projects" AND #meeting AND -"Archive"
WHERE !completed AND file.frontmatter.status = "active"
GROUP BY file.link
```

---

## 📌 Project tasks
All open tasks in active project notes (excluding meetings — those are above).

```dataview
TASK
FROM "Projects" AND -#meeting AND -"Archive"
WHERE !completed AND file.frontmatter.status = "active"
GROUP BY file.link
```

---

## 📂 Active notes by project
Quick index of every active note, grouped by project folder.

```dataview
TABLE WITHOUT ID file.link AS Note, file.frontmatter.status AS Status, file.mday AS Modified
FROM "Projects" AND -"Archive"
WHERE file.frontmatter.status = "active" OR pinned = true
SORT file.mday DESC
```

---

## 🖼️ Recent plots
Every plot entry — including multiple plots listed inside a single note.
Plot entries are `###` headings under a `#plot` note (see [[Plots]] for how to add them).

```dataviewjs
// Surface individual plot entries even when many live in one note.
// An entry = a "### Heading" inside a #plot note, optionally followed by a
// "- **Description:**" / "- **Date:**" / "- **Link:**" line.
const rows = [];
for (const p of dv.pages('#plot').where(p => !p.file.path.startsWith("Archive/"))) {
  const text = await dv.io.load(p.file.path);
  const lines = text.split("\n");
  let cur = null;
  const push = () => { if (cur && cur.title) rows.push(cur); };
  for (const line of lines) {
    const h = line.match(/^#{2,4}\s+(.*)/);
    if (h) { push(); cur = { title: h[1].trim(), note: p.file.link, date: p.Date ?? "", desc: "", link: "" }; continue; }
    if (!cur) continue;
    const d = line.match(/\*\*Description:\*\*\s*(.*)/i); if (d) cur.desc = d[1].trim();
    const dt = line.match(/\*\*Date:\*\*\s*(.*)/i);        if (dt) cur.date = dt[1].trim();
    const lk = line.match(/\*\*Link:\*\*\s*(\S+)/i);       if (lk) cur.link = lk[1].trim();
  }
  push();
  // Fallback: a single-plot note with no sub-headings → use the file itself.
  if (!lines.some(l => /^#{2,4}\s+/.test(l))) {
    rows.push({ title: p.file.name, note: p.file.link, date: p.Date ?? "", desc: p.Description ?? "", link: p.Link ?? "" });
  }
}
rows.sort((a, b) => String(b.date).localeCompare(String(a.date)));
dv.table(["Plot", "Date", "Description", "Open"],
  rows.slice(0, 20).map(r => [
    r.title,
    r.date,
    r.desc,
    r.link ? `[CERNBox](${r.link})` : r.note
  ]));
```

%% --- Dashboard buttons (Meta Bind) --- %%
```meta-bind-button
label: ＋ Daily note
id: new-daily
hidden: true
style: default
actions:
  - type: command
    command: daily-notes
```

```meta-bind-button
label: ＋ Meeting
id: new-meeting
hidden: true
style: default
actions:
  - type: command
    command: templater-obsidian:create-new-note-from-template
```
