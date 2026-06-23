---
tags: [dashboard]
---

# 📊 Dashboard

> Live overview of open work. Pin this note (right-click tab → Pin). Nothing here needs editing — queries auto-discover projects.

`BUTTON[new-daily]` `BUTTON[new-meeting]`

## 📌 Pinned
Notes with `pinned: true` — always shown here, even when `done`.
Each row has its own **status** and **unpin** buttons (act on that note directly).

```dataviewjs
const pages = dv.pages('-"Archive"').where(p => p.pinned === true)
  .sort(p => [p.status, -p.file.mtime], 'asc');

const btn = (label, file, fn) => {
  const b = this.container.createEl("button", { text: label, cls: "mod-cta" });
  b.style.cssText = "padding:2px 8px;margin:0 4px 0 0;font-size:12px;cursor:pointer;";
  b.onclick = async () => { await fn(file); };
  return b;
};
const tf = (p) => app.vault.getAbstractFileByPath(p.file.path);
const setStatus = async (p) => app.fileManager.processFrontMatter(tf(p), fm => {
  fm.status = (fm.status === "active") ? "done" : "active"; });
const unpin = async (p) => app.fileManager.processFrontMatter(tf(p), fm => { fm.pinned = false; });

const rows = pages.map(p => {
  const span = document.createElement("span");
  span.appendChild(btn(p.status === "active" ? "✅ done" : "🔄 active", p, setStatus));
  span.appendChild(btn("📌 unpin", p, unpin));
  return [p.file.link, p.status ?? "—", span];
});
dv.table(["Note", "Status", "Actions"], rows.array());
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
Every active (or pinned) note. Each row toggles its own **status** and **pin** directly.

```dataviewjs
const pages = dv.pages('"Projects" and -"Archive"')
  .where(p => p.status === "active" || p.pinned === true)
  .sort(p => -p.file.mtime, 'asc');

const btn = (label, file, fn) => {
  const b = this.container.createEl("button", { text: label });
  b.style.cssText = "padding:2px 8px;margin:0 4px 0 0;font-size:12px;cursor:pointer;";
  b.onclick = async () => { await fn(file); };
  return b;
};
const tf = (p) => app.vault.getAbstractFileByPath(p.file.path);
const setStatus = async (p) => app.fileManager.processFrontMatter(tf(p), fm => {
  fm.status = (fm.status === "active") ? "done" : "active"; });
const togglePin = async (p) => app.fileManager.processFrontMatter(tf(p), fm => {
  fm.pinned = !(fm.pinned === true); });

const rows = pages.map(p => {
  const span = document.createElement("span");
  span.appendChild(btn(p.status === "active" ? "✅ done" : "🔄 active", p, setStatus));
  span.appendChild(btn(p.pinned === true ? "📌 unpin" : "📍 pin", p, togglePin));
  return [p.file.link, p.status ?? "—", p.pinned === true ? "📌" : "", span];
});
dv.table(["Note", "Status", "Pin", "Actions"], rows.array());
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
  - type: templaterCreateNote
    templateFile: Templates/Meeting.md
    openNote: true
```
