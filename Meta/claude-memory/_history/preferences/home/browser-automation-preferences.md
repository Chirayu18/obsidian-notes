---
name: browser-automation-preferences
description: "Show lookups in Chrome, not in chat; don't take confirmation screenshots"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7ca21f69-71ba-4de4-a60c-ac4ca2aeca80
  modified: 2026-07-26T22:38:51.490Z
---

**Show results in the browser, not as chat text.** When the user asks to see
something (fixtures, weather, a timetable, any lookup), open the real page in Chrome
and leave it there. Do not summarise it into a markdown table in the reply — a short
sentence saying what was opened is enough.

**Why:** the user has Chrome automation set up specifically so results land somewhere
they can look at and interact with. Restating everything in chat defeats the point.
Said explicitly on 2026-07-27 after receiving fixtures + weather as chat tables when
they had asked for Chrome.

**Don't take confirmation screenshots.** If the URL is known, navigate straight there
and stop. A successful `navigate` result is proof enough the page loaded. Screenshot
only when the image is the deliverable, or when page content is genuinely needed to
decide the next action and no text tool would do.

**Never enter credentials.** The user logs into Home Assistant (and anything else)
themselves. Navigate to the page and hand off.

Related: [[Meta/claude-memory/_history/workflow/home/home-assistant-setup|home-assistant-setup]], [[Meta/claude-memory/_history/general/home/useful-pages|useful-pages]].
