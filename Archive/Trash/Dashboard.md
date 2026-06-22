---
tags:
  - dashboard
---

# Dashboard

---

## TODO

- [ ] Fix the MVA pipeline [[Projects/HToWW/MVA]]
- [ ] Class reweighting [[Projects/HToWW/MVA]]
- [ ] Talk to Alex about improving MVA [[Projects/HToWW/MVA]]
- [x] Monitor the new hww_MVA workflow
- [ ] Proceed with 2024 integration
- [ ] Proceed with sample generation for other ERAs
- [ ] Produce HPlusB gridpack [[Central Production]]
- [ ] Postprocess with log [[Projects/HToWW/Z TO MuMu]]
- [ ] 

---

## Open Tasks

```dataview
TASK
FROM "Research"
WHERE !completed
GROUP BY file.link
```

---

## Recently Modified

> Manually log changes here as you work.

| Date | Note | Change |
|------|------|--------|
| 2026-02-10 | [[Projects/HToWW/Z TO MuMu]] | Postprocessing complete, plots added |
| 2026-02-10 | [[Projects/HToWW/MVA]] | Resubmitted jobs, 1 dataset expected missing |
| 2026-02-10 | [[Plots]] | Added Z TO MuMu plots |

---

## Latest Plots

```dataview
TABLE Date, Description, "[Link](" + Link + ")" as "CERNBox"
FROM "Research/HToWW/Plots"
SORT Date DESC
LIMIT 10
```

