---
tags: [reference, production]
status: active
date: 2026-11-10
source: laptop
---

# EOS cleanup for Run A: `hww_combine_2dcat` removed (2026-11-10)

**Chirayu's OK (2026-11-10, verbatim):** "Remove: hww_combine_2dcat"

He chose this from an EOS inventory on 10 Nov, where it was listed as superseded. Nothing else was approved for deletion.

## Before
- `eos quota -m /eos/user/c/cgupta/`: usedlogicalbytes = 919,394,509,962 of 1,000,000,000,000 (about 81 GB free).
- Target: `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat`, 179,009,597,945 B, more than 100,022 files and 22,052 directories (`eos find --count` was truncated at the query limit). Contents: `2022postEE` (1268 entries, 10 Sep), `2022postEE_disabled_tbbarq`, `2022postEE_old_inclusive_wjets`.
- Why it was superseded: it is the pre-full-fix 2022postEE-only production. `hww_combine_full` (4 eras, 6–8 Oct) replaced it. The Run A workflow `hww_allfix_4fs.yaml` mentions it only in comments (lines 17 and 23). Legacy workflows that name it in their config (`hww_2dcat_nocjet`, `hww_2dcat_looseWP`, `hww_2dcat_nocjet_kin`) are not in use for Run A.

## How it was deleted
- One `eos rm -r` refused: "the directory tree exceeds the configured query limit".
- The delete was then split into per-child deletions by `lxplus977:~/rm_hww_combine_2dcat_20261110.sh`. The script used the list `~/rm_hww_combine_2dcat_20261110.list` (1284 paths, all under the target) and logged to `~/rm_hww_combine_2dcat_20261110.log`. The empty parents were then removed with `rmdir`.
- EOS recycle bin: every deletion printed a `recycle restore pxid:…` line in the log. The bin's object lifetime is 3,628,800 s (42 days). Restoring is possible until then.

## After
- **The folder is gone.** `eos ls` of the target gives "No such file or directory".
- The log has 1284 `rc=` lines, which is every listed path. 1283 have rc=0.
- `2022postEE/MuonRun2022G` failed once with rc=21. It is gone after the second pass.
- The first background run stopped after 350 paths, probably when lxplus ended the session. It was restarted with a rebuilt list (`~/rm_hww_combine_2dcat_20261110.list2`, 934 paths). This time it ran inside an SSH session held open from the laptop. Afterwards the four `rmdir` calls returned rc=0 (the three subfolders and the top folder).
- **Quota after** (`eos quota -m`): usedlogicalbytes = 739,094,006,749 of 1,000,000,000,000. **Free space is now about 261 GB, up from about 81 GB, so about 180 GB was freed.** The recycle-bin contents do not count against this quota.
- The Run A space need is not yet measured. The last full production plus ttsyst used 266 GB, and TRAIN mode also writes parquet files. Measure the size per dataset in the TRAIN smoke test before the full launch.

## Kept, per the same discussion
`hww_combine_full` and `hww_combine_full_ttsyst` (baseline until Run A is validated), `hww_genrw_train` (needed for the negrw overlap check) and `EPR_task/b-hive` (holds the v11 model at `hww_allfix_4fs.yaml:1048`).
