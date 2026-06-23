<%*
const folders = app.vault.getAllLoadedFiles()
  .filter(f => f.children)
  .map(f => f.path)
  .filter(f => f.startsWith("Projects/"));
const folder = await tp.system.suggester(folders, folders);
const meetingDate = await tp.system.prompt("Meeting date (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD"));
const time = await tp.system.prompt("Meeting time (e.g. 1400)");
const filename = meetingDate + "-" + time;
await tp.file.rename(filename);
await tp.file.move(folder + "/Meetings/" + filename);
-%>
---
date: <% tp.date.now("YYYY-MM-DD") %>
scheduled: <%* tR += meetingDate %>
status: active
pinned: false
tags: [meeting]
---

# <% tp.file.title %>

> `BUTTON[toggle-status, toggle-pin]` &nbsp;·&nbsp; status: `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

## Agenda
- 

## Notes
- 

## Action Items
- [ ] 