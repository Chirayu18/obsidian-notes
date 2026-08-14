---
tags: [reference]
status: active
date: 2026-08-13
source: lxplus
---

# HANDOFF — W+jets jet-binned replacement, session state at 2026-08-13 22:15

**Resume here.** Companion to [[2026-08-13-wjets-jetbinned-replacement]] (the
physics/config detail) and [[2026-08-12-master-task-list]].

---

## 0. WHERE WE ARE — one paragraph

Reprocessing of the three jet-binned W+jets samples is **COMPLETE (550/550
partitions, 4,851 surviving SR rows vs 519 for the old inclusive = 9.3×)**. A
blocker in `run_postprocess.py` (stale `TBbarQ` outputs from samples disabled on
2026-08-12) has been **resolved by quarantining them on AFS** (§4).
**Next action: run `run_postprocess.py` — see §5.** Nothing downstream
(postprocess, inference, datacard, limit) has been run yet, so the **1160
baseline card is still untouched and the whole change is still fully
reversible** (§7).

---

## 1. What this task is

Task A1.1: replace the inclusive `WtoLNu_2Jets` W+jets sample with the
jet-binned NLO 0J/1J/2J samples, to attack the dominant systematic.

**Why:** autoMCStats is **−255** of the −523 total systematic budget (limit
1160 → 905 when frozen), and **−225 of that −255 is the signal region alone**.
V+jets has `n_eff = 280` in the SR vs ≤1.1% relative stat error for every other
background. V+jets MC statistics is the single biggest lever on the limit.

> **Correction to earlier framing:** I previously told the user `scalevar_muF`
> (−69) was "the largest lever, roughly twice ctag2d". That was wrong —
> autoMCStats is ~4× larger. Task #35 (`scalevar_muF`) is NOT the priority;
> this task is.

---

## 2. DONE and verified

### Cross sections (XSDB, retrieved via the user — XSDB needs CERN SSO, `auth-get-sso-cookie` could NOT authenticate headlessly)

| sample | xsec (pb) | events | files | neg-w XSDB | neg-w measured |
|---|---|---|---|---|---|
| `WtoLNu-2Jets_0J` | 55,760 | 678.4M | 3,432 | 10.31% | **10.17%** |
| `WtoLNu-2Jets_1J` | 9,529 | 522.6M | 2,669 | 25.85% | **25.67%** |
| `WtoLNu-2Jets_2J` | 3,532 | 344.6M | 2,135 | 34.70% | **34.71%** |
| **sum** | **68,821** | **1,545.5M** | **8,236** | | |
| *old inclusive* | *67,710* | *281.5M* | *381* | | *16.08%* |

Sum is +1.6% vs inclusive — normal NLO merging spread, not a double-count.

> **XSDB metadata is WRONG on two fields**: it reports `accuracy: "LO"` and
> `matrix_generator: "Pythia8"` for all three. Both are auto-populated and wrong.
> `amcatnloFXFX` is NLO — proven by the 10–35% negative-weight fractions, which
> are impossible at LO. Only `cross_section` is trustworthy.

### Config edits (all verified by YAML round-trip, all backed up)

- `analysis/filesets/2022postEE_nanov12.yaml`: 83 → 85 entries, 3 added,
  inclusive removed, **no existing entry modified**.
  Backup `*.bak_pre_wjets_20260813_171913`
- `analysis/workflows/hww_combine_2dcat.yaml`: `negrw.datasets` repointed to the
  three new names; only that block changed.
  Backup `*.bak_pre_wjets_20260813_172253`
- Fileset JSON rebuilt: 8,236 files, counts match DAS **exactly**.
  Backups `*.bak_20260813_174549`, `*.bak_pre_repoint_20260813_183414`

### negrw: NO retrain needed — measured, not assumed

The user said "if that is a problem then retrain… duh", but it was checked first
and a retrain is **not** required:

- `P₊(x)` is a **generator property** of amc@NLO FxFx; these are the same
  generator/tune/merging sliced by jet multiplicity, and `lhe_njets` is already
  an input feature.
- The risk would be extrapolation, so it was measured: 2J events beyond the
  inclusive sample's **max** Vpt = **0.002%**, beyond max HT = **0.000%**.
  Interpolation, not extrapolation — the condition
  [[2026-07-11-negweight-reweight-training-region]] requires.

`_dataset_matches` strips only `_\d+$` (digits), so `WtoLNu_2Jets_0J` does NOT
collapse to `WtoLNu_2Jets`. Checked — no false match.

### Reprocessing: COMPLETE

**550/550 partitions** (0J 229/229, 1J 178/178, 2J 143/143).
**4,851 surviving SR rows** vs **519** for the old inclusive = **9.3×**.

| sample | rows | share |
|---|---|---|
| 0J | 195 | 4% |
| 1J | 1,324 | 27% |
| 2J | **3,332** | **69%** |

2J dominates despite being the smallest sample — the jet-binned samples are
enriched in exactly what the ≥1 c-jet selection needs. The inclusive sample spent
most of its cross section on 0-jet events that essentially never survive
(survival rate 1 in 542,473).

---

## 3. The big blocker that was solved: XRootD dead replicas

**First submission (clusters 9189871/2/3) was a near-total loss** — 1J and 2J
failed ~100%. Root cause: round-robin replica selection assigned **1,601 of 8,236
files (19.4%)** to three dead/slow endpoints:

| endpoint | site | failures |
|---|---|---|
| `ruhex-osgce.rutgers.edu` | T3_US_Rutgers | 855 |
| `cms-t2-se01.sdfarm.kr` | T2_KR_KISTI | 255 |
| `cms-se0.kipt.kharkov.ua` | T2_UA_KIPT | 201 |

11% of 0J files but **24%/27%** of 1J/2J — which is exactly why those two died.

### The fix: repoint, do NOT blacklist

**`jobs_status.py` blacklisting was deliberately NOT used.** Per
[[hww-jobs-status-blacklist-memoryless]], filesets list ONE replica per file, so
blacklisting a site **deletes those files** rather than repointing them.

Instead `/tmp/repoint.py` queries Rucio for **all** replicas of each affected LFN
and swaps in a healthy one. It asserts file counts are unchanged before writing,
so it cannot silently drop anything:

```
repointed: 1601   kept original (no good replica): 0
file counts unchanged: 0J 3432, 1J 2669, 2J 2135
remaining URLs on bad hosts: 0
```

Verified by probing 15 random repointed files: **15/15 read OK**, 0.9–9.7 s.

**Result: resubmission (clusters 9189885/6/7) had 1 failure in 542 (0.18%).**

### The last straggler — and the trap it revealed

1J partition 81 still failed, on a 4th endpoint `xroot01.ncg.ingrid.pt`
(T2_PT_NCG_Lisbon). An interactive probe read that file fine in 7 s, so it was
called transient and resubmitted — **it failed identically**. A slow replica can
pass an interactive read and still time out under job conditions.

> **TRAP: the condor job reads `partitions.json`, NOT the fileset JSON.**
> Repointing the fileset alone is not enough — you must re-run `submit_condor.py`
> (without `--submit`) to regenerate `partitions.json`, or the job keeps using the
> old URL. This is why the second retry failed on the same file.

Also: to resubmit ONE partition, `jobnum.txt` is temporarily narrowed to that id
and then **must be restored** (178 lines for 1J) or later resubmissions break.

---

## 4. TBbarQ blocker — RESOLVED (quarantined), postprocess NOT yet run

`run_postprocess.py` failed immediately with:

```
KeyError: 'TBbarQ'
  analysis/filesets/utils.py:254 in get_process_sample_map
```

**Cause:** `TBbarQ`/`TbarBQ` were deliberately disabled in
`2022postEE_nanov12.yaml` on 2026-08-12 (commented out, lines ~140/199/215), but
their **output parquets still existed**. Postprocess globs output directories and
looks each up in the config, so it dies on orphans. **Pre-existing, unrelated to
the W+jets work.**

**ACTION TAKEN 2026-08-13 ~22:20 — quarantined, nothing deleted:**

```
/afs/.../higgscharm/outputs/hww_combine_2dcat/2022postEE_disabled_tbbarq/
   39 items moved (merged parquets kept under their <shiftdir>/ subdir,
                   raw partition dirs under partitions/)
   remaining in the live AFS tree: 0
```

EOS reported 0 moved — **postprocess reads from AFS**
(`<repo>/outputs/hww_combine_2dcat/2022postEE`), not EOS, so the AFS copy was the
one blocking. The 13 stale EOS parquets are still in place and are harmless for
postprocess, but **will need the same treatment before `make_combine_inputs`**
if that builder globs EOS — CHECK THIS.

Used anchored regex `(TBbarQ|TbarBQ)(?:_\d+)?` and exact basename matching, not a
glob — see mistake #1 in §8.

> To undo: `mv` the contents of `2022postEE_disabled_tbbarq/` back. Nothing was
> deleted.

### ⛔ WHERE IT STOPPED

**`run_postprocess.py` has NOT been successfully run yet.** The rerun attempt
failed only because the helper `/tmp/postproc.sh` had been cleared from the
node's `/tmp` (`bash: /tmp/postproc.sh: No such file or directory`) — a lost
scratch file, **not** an analysis problem. Recreate it and run (§5).

---

## 5. Remaining pipeline — START HERE

Step 1 is the immediate next action. Run it inside tmux (it takes a while):

```bash
cat > /tmp/postproc.sh <<'EOF'
#!/bin/bash
export X509_USER_PROXY=/tmp/x509up_u$(id -u)
export MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
$MAMBA_EXE run -n b_hive python3 run_postprocess.py \
   --workflow hww_combine_2dcat --year 2022postEE \
   --postprocess --output_format parquet 2>&1 | tail -30
echo "POSTPROCESS_EXIT=${PIPESTATUS[0]}"
EOF
chmod +x /tmp/postproc.sh
tmux new-session -d -s pp "bash /tmp/postproc.sh > /tmp/postproc.log 2>&1"
tail -f /tmp/postproc.log
```

> **NOTE: there is NO `--mva` flag.** Merging is the default; `--skipmerging`
> disables it. `README_HToWW.md` wrongly documents `--mva` — fix that too.
> Expect more orphan `KeyError`s if other samples were disabled without their
> outputs being cleared; same quarantine treatment applies (§4).

# 2. inference — MUST cover nominal + all 12 shift dirs
python3 scripts/mva/run_inference.py --workflow hww_combine_2dcat --year 2022postEE \
    --model-path /eos/user/c/cgupta/EPR_task/b-hive/output/TrainingTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt \
    --bhive-config HPlusCHToWW_2dcats

# VERIFY (this is the bug that once cost 500 units — 1676 instead of 1185):
find outputs/hww_combine_2dcat/2022postEE -name 'mva' -type d | wc -l
# baseline BEFORE this change was 14. Must grow, and cover every dataset × shift dir.

# 3. datacard
python3 scripts/combine/make_combine_inputs_v2.py --workflow hww_combine_2dcat --year 2022postEE

# 4. limit — compare against baseline 1160
combine -M AsymptoticLimits v11_hplusc_2dcat.txt -t -1 --run blind --noFitAsimov --mass 120
```

**Report `n_eff` for V+jets in SR_hplusc alongside the limit** — that is the
number this whole exercise exists to move. Baseline `n_eff = 280`,
rel. stat err 5.98%. Projection was ~4,400 / ~1.5%, but that used a 15.6×
effective-statistics estimate across all three samples; the SR gain is driven by
1J/2J, so **re-measure rather than trusting the projection**.

Projected effective-statistics gain (measured pre-run):

| sample | n_eff/N | equiv. lumi |
|---|---|---|
| 0J | 0.6347 | 7.72 /fb |
| 1J | 0.2367 | 12.98 /fb |
| 2J | 0.0935 | 9.12 /fb |
| **jet-binned total** | | **29.82 /fb** |
| inclusive | 0.4602 | **1.91 /fb** |
| | | **→ 15.6×** |

---

## 6. Environment / gotchas needed to resume

```bash
export MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
export X509_USER_PROXY=/tmp/x509up_u$(id -u)   # copy of the AFS proxy
cp /afs/cern.ch/user/c/cgupta/private/x509up_u151861 /tmp/x509up_u$(id -u)
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
```

- **Two envs matter**: `b_hive` (coffea 0.7.22) for the analysis; **`base`
  (coffea 2025.9.0)** for `make_filesets` — `b_hive` has no `coffea.dataset_tools`.
- **Rucio needs** `source /cvmfs/cms.cern.ch/rucio/setup-py3.sh`, else
  `ConfigNotFound`.
- **coffea SITECONF bug — PATCHED.** `get_xrootd_sites_map()` read `site["rse"]`
  for all 143 SITECONF entries; `T3_CN_Nanjing` publishes a DISK volume with no
  `rse` key → `KeyError` → the whole replica lookup dies and
  `dataset_discovery_*.json` is written as literal `null`. Fixed to
  `site.get("rse")` (3 occurrences) in
  `~/.local/lib/python3.9/site-packages/coffea/dataset_tools/rucio_utils.py`
  (backup `.bak_pre_rse_*`). **Worth reporting upstream.** Note the site
  whitelist does NOT protect against this (the map is built over ALL of SITECONF
  before the allowlist applies) and `.sites_map.json` caches for only 10 min.
- **XSDB needs interactive CERN SSO** — `auth-get-sso-cookie` gets a cookie but
  the app still bounces to the login page. Ask the user to paste rows.

---

## 7. Everything is recoverable — verified 2026-08-13

**Quarantine** `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_old_inclusive_wjets/`:

- `merged/<shiftdir>/WtoLNu_2Jets.parquet` × **13** — all READABLE, 6,736 rows
  total (519 nominal, matching the pre-change measurement). Each shift dir kept
  as its own subdir, so **no name collisions, nothing overwritten**.
- `partitions/` × **27** inclusive dirs, 2,830 sumw files, total sumw 4.97e13.
- 100% match the anchored inclusive pattern; **0** jet-binned dirs left inside.

**The 1160 datacard is untouched**: `v11_hplusc_2dcat.txt` (19,847 B) and
`.root` (1,133,932 B) in `/eos/user/c/cgupta/higgscharm/outputs/combine/`.
`make_combine_inputs` has NOT been re-run.

**To roll back completely:** restore the two `.bak_pre_wjets_*` configs, `mv` the
quarantine contents back, and regenerate the fileset for the inclusive sample
(a DAS query over 381 files). Nothing has been deleted at any point.

---

## 8. Mistakes made this session — recorded so they are not repeated

1. **Glob matched more than intended.** `WtoLNu_2Jets_[0-9]*` also matches
   `WtoLNu_2Jets_0J_1` (starts with `0`), so 127 NEW partition dirs were
   accidentally quarantined. Recovered fully (moved, not deleted; 745 files
   merged back with an anchored `WtoLNu_2Jets(_\d+)?` regex). **Use anchored
   regex, not globs, for sample names** — the same discipline `_dataset_matches`
   already encodes.
2. **"Finishing too fast" was misdiagnosed as the selection working.** It was
   jobs dying on XRootD and exiting early. Verification was run only on
   partitions that *did* write — a biased sample. **Count partitions against the
   expected total**, which catches this immediately.
3. **Blamed `--nfiles 15` concurrency** by analogy with the IIHE `nocjet`
   failures. Wrong — it was three dead replica sites. `--nfiles 3` would have
   helped only by accident.
4. **Reported a false "411 duplicate sumw chunks"** — a bug in my own
   verification script (dict key overwritten). Real answer: 2,864 unique names,
   **0 duplicates**.
5. **README_HToWW.md documents a `--mva` flag for `run_postprocess.py` that does
   not exist.** Needs fixing.
