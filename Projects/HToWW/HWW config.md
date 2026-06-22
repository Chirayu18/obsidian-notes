---
tags:
  - hww
status: "[[Projects/HToWW/MVA]]"
related: "[[Archive/HToWW/HToWW]]"
date: 2026-02-23
---

# HWW config

---

## Commands

```bash
python3 jobs_status.py --workflow hww_MVA_noMtll --y 2022postEE --eos --hours_ago 11
```

---

## Tasks

- [x] Reduce MET cut and try training with that : Don't do this as discussed by gerrit
- [ ] Add MT cut back

---

## Log

#### HWW_MVA

cutflow: /eos/home-c/cgupta/higgscharm/outputs/hww_MVA/2022postEE/base/cutflow_base.csv

Created 2 new configs:
#### HWW_MVA_FEB
- Includes all cuts and add the jet array
#### HWW_MVA_noMtll
- Same as previous but no mt cut


Take drell yann samples for 2024 from daniel
