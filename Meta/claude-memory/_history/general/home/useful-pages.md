---
name: useful-pages
description: "URLs the user asks to be opened in Chrome — HA dashboard, STIB stop, football, weather"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7ca21f69-71ba-4de4-a60c-ac4ca2aeca80
  modified: 2026-07-26T22:38:57.962Z
---

Pages the user has asked to see. Open these directly in Chrome rather than
searching for them again (see [[Meta/claude-memory/_history/preferences/home/browser-automation-preferences|browser-automation-preferences]]).

| What | URL |
|---|---|
| HA Bedroom dashboard | `http://192.168.0.214:8123/bedroom-panel/bedroom` |
| STIB stop Léopold III (live departures) | `https://www.stib-mivb.be/home/travel/realtime/stops?stop=90540` |
| Man Utd fixtures (official) | `https://www.manutd.com/en/matches/mens-team/fixtures` |
| Brussels 10-day weather (Met Office) | `https://weather.metoffice.gov.uk/forecast/u15170` |

Context: the user is in Brussels (HA timezone Europe/Brussels). Léopold III is served
by trams 7 and 62, buses 63 and N04. Supports Manchester United.

HA needs a browser login the first time in a given Chrome profile — the user does
that themselves; "Keep me logged in" is ticked so it should persist.

**Open suggestion, not yet done:** add HA's built-in Met.no weather integration for a
live forecast card on the dashboard — cleaner than scraping a weather site, and it
would put the 10-day forecast in the same place as the light controls.
