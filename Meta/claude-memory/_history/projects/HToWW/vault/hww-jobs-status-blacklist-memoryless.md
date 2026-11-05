---
name: hww-jobs-status-blacklist-memoryless
description: "jobs_status.py's auto-blacklist is memoryless and re-admits previously-failed sites; the preEE filesets list only ONE replica per file"
metadata: 
  node_type: memory
  type: project
  originSessionId: af76ec6a-a549-46b2-be18-cf006051e43e
  modified: 2026-08-11T14:16:27.639Z
---

`jobs_status.py --workflow ... --eos` auto-blacklists xrootd sites **per dataset**, derived
from *recent* `.err` files (`analyze_xrootd_errors_by_dataset`). Two traps:

**1. It is memoryless — it cycles instead of converging.** `update_input_filesets_for_group`
(around lines 349–353) **resets every site to "white" first**, then applies only the latest
offenders. Sites blacklisted in an earlier round are silently re-admitted. Observed
2026-08-11 on `hww_ctag_compare` 2022preEE: `T3_US_Rutgers` blacklisted at 04:36, absent from
the list by 15:43, and it killed a job again at 16:06. Each round removes one slow site and
the next job lands on another.

Corollary: **hand-editing `analysis/filesets/<year>_sites.yaml` is pointless** — the next
regeneration wipes it.

**2. The fileset lists ONE replica per logical file — a blacklist DELETES files.** In
`fileset_2022preEE_nanov12_lxplus.json`, `TTto2L2Nu` had 67 LFNs and exactly 67 entries. A
cumulative "union" blacklist of everything that had ever failed it (SPRACE, NotreDame,
Rutgers, CIEMAT, Purdue, Florida, RAL-echo) would have removed **16 of 67 files (24%)** with
no alternative replica, silently biasing the tt yield downward. Check before blacklisting:
group the file list by the `/store/...` LFN and count how many LFNs have *all* replicas on
the blacklist.

**Practical rule:** for a dataset whose files are scattered over many sites (TTto2L2Nu: 13
sites, ~5 files each, only 5 at `eoscms.cern.ch`), blacklisting will not converge. Resubmit
once or twice, then accept a partial dataset and say so, rather than shrinking the fileset.

Do **not** fix this by repartitioning with `--nfiles 3` on a partially-complete dataset —
changing partition boundaries makes new partitions overlap the existing `*_N.coffea` outputs
and the merge would double-count.

Related: [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]]
