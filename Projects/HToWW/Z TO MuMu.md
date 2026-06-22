---
tags:
  - hww
status: active
---


**Working directory:** `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`

---

## Tasks

- [x] Fix paths
- [x] Submit jobs
- [x] Postprocess
- [x] Give plots to Thomas
- [x] Postprocess with log [[Projects/HToWW/Z TO MuMu]] [completion:: 2026-03-02]
---

## Commands

```bash
python3 jobs_status.py --workflow ztomumu --y 2022postEE --eos --hours_ago 11
```

```bash
python3 run_postprocess.py -w ztomumu -y 2022postEE --postprocess --plot
```

---

## Log

### Issue: 15 jobs held

Attempted fix in `jobs_status.py` — changing `base_dir = Path.cwd()` to include `../higgscharm_new/`. Did not work, reverted.

Second attempt — copied directory:

```bash
cp -r higgscharm higgscharm_new
```

Resubmitted after killing held jobs.

### Status

- Jobs running: 3 datasets remaining → **All jobs done**
- Postprocessing complete
- Plots added to [[Plots]]
