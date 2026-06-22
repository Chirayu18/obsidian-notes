---
tags:
  - plot
Date: <% tp.date.now("YYYY-MM-DD") %>
Description:
Link: https://cernbox.cern.ch/files/spaces/
Path:
---
### Path → Link Conversion

CERNBox URL format: `https://cernbox.cern.ch/files/spaces/eos/[path]`

**Important:** Always convert `/home-c/cgupta` to `/user/c/cgupta` in the URL.

### Name Extraction Convention

- `ztomumu` → "Z TO MuMu"
- `hww` → "H To WW"
- Parse date from path if present (e.g., `10Feb_2026` → `2026-02-10`)