---
tags: [dashboard]
---

# 📊 Dashboard

> Live overview of open work. Pin this note (right-click tab → Pin). Nothing here needs editing — queries auto-discover projects.

## 🔥 Today
Tasks tagged `#today` anywhere in the vault, plus tasks in today's daily note.

```dataview
TASK
WHERE !completed AND (contains(text, "#today") OR contains(file.name, dateformat(date(today), "yyyy-MM-dd")))
GROUP BY file.link
```

---

## 🗣️ Meeting action items
Open tasks from any meeting note across all projects.

```dataview
TASK
FROM "Projects" AND #meeting
WHERE !completed AND file.frontmatter.status = "active"
GROUP BY file.link
```

---

## 📌 Project tasks
All open tasks in active project notes (excluding meetings — those are above).

```dataview
TASK
FROM "Projects" AND -#meeting
WHERE !completed AND file.frontmatter.status = "active"
GROUP BY file.link
```

---

## 📂 Active notes by project
Quick index of every active note, grouped by project folder.

```dataview
TABLE WITHOUT ID file.link AS Note, file.frontmatter.status AS Status, file.mday AS Modified
FROM "Projects"
WHERE file.frontmatter.status = "active"
SORT file.mday DESC
```

---

## 🖼️ Recent plots
Latest plot entries (see [[Plots]] for the full archive and how to add new ones).

```dataview
TABLE WITHOUT ID file.link AS Plot, Date, Description
FROM #plot
SORT Date DESC
LIMIT 10
```
