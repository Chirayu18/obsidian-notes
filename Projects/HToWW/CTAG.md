---
tags:
  - hww
status: active
pinned: false
related:
date: 2026-07-11
---

# Untitled

> `BUTTON[toggle-status, toggle-pin]`  `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

---

## Commands

```bash

```

---

## Tasks

- [ ] Implement WP 

---

## Log
- [gitlab file with working points](https://gitlab.cern.ch/cms-analysis/general/HiggsDNA/-/blob/master/higgs_dna/metaconditions/Era2022_v1.json?ref_type=heads#L567-645)
- [Here](https://etsai.web.cern.ch/2DCalibration/SFbc-2D/docs.html) is the documentation for 2024, which is in terms of code and method identical.
- this is the order of argument for the evaluation:

`evaluator.evaluate( "central", nth_jet_hFlav, wp_evaluate, nth_jet_abs_eta, nth_jet_pt, )`

- Idea of this 2d phase tagging method here: /home/cgupta/mnt/lxplus-eos/HToWW/ctag.py
- Plan is to replace the current ctag variables with these ones. To be added in the processing step later. A quick script for now that appends these columns in the parquets should do. Then retrain both versions of MVA and hopefully not much difference in the results. Refer to this for running framework: https://github.com/Chirayu18/higgscharm/blob/migration-v2/QUICKSTART.md 
- 
