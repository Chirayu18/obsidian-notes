---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---
# higgscharm speed-up patches that leave the output unchanged (HTOWW-FRAMEWORK-SPEEDUP-2, 2026-11-05)

**Status: agent-reported.** The patches are written and tested locally on one file. When this note was written none was applied. **Update (keeper, 2026-11-05):** patches 01–04 were later applied by the FULLFIX worker in `hww-analysis` commit `40d0e3e`; the [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|independent review, 9aa71d5]] checked that the combined patch reverses cleanly and reran the 19-type writer check. Patch 05 (`request_cpus`) is untested and undecided.

**Inputs**
- Plan: [[2026-10-08-framework-optimization-plan]], §1.2 and §5 P1-perf.
- Repo: `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, current working tree.
- Nothing in the repo was edited, stashed or committed. No submission was made.
- All work was done in `/tmp/cgupta_speedup2` on lxplus921.

**Deliverables:** `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/proposals/HTOWW-FRAMEWORK-SPEEDUP-2/`
- the patches;
- `README.md`, with the full detail;
- `tests/`: scripts, comparison JSONs, profiles and `time -v` logs.

## Items

| patch | what | status |
|---|---|---|
| `00-all-ready-01-04.patch` | 01–04 combined | READY |
| `01-dump-parquet-numpy.patch` | (a) `dump_pa_table`: awkward → numpy before `pa.Table.from_pydict`, reproducing pyarrow's Python-scalar type inference (float→double, int/uint→int64, None→null, all-None→`null`); otherwise falls back to the old path | READY |
| `02-dataset-config-cache.patch` | `dump_parquet` parses the era YAML once per process (it was 15× per chunk) | READY |
| `03-correctionlib-cache.patch` | `cset_cache.load_correction_set` (`lru_cache`) in `ctag2d.py`, c-tag WP `utils.py`, `pileup.py` | READY |
| `04-trigger-yaml-cache.patch` | `trigger_flags.yaml` parsed once per process (it was 45× per chunk) | READY |
| `05-condor-request-cpus-NEEDS-DECISION.patch` | `request_cpus = 2`, to match `workers=2` | NEEDS DECISION; untested |

`git apply` succeeds on a copy of the live tree taken at 07:02Z, which already includes the FULLFIX lepton-MVA edits. The patched files are identical to the ones I tested.

## Evidence

**Setup**
- Job image: `coffea-base-almalinux9:0.7.30-py3.10`.
- Workflow: `hww_allfix_4fs`, 2022postEE.
- Input: central H+c file `…/2520000/27982ec7-6713-495c-b35c-4058f99feadc.root`, 85,732 events.
- Harness: a copy of `smoke_allfix.sh` that points at the `/tmp` repo copy.

**The baseline alone is not reproducible.** Two unpatched runs differ in the lepton-pT columns, because the muon scale/smearing RNG is unseeded (P0-8/B1). The `weight_*` column order also follows the Python hash seed. The equivalence runs therefore seed both RNGs (test-only instrumentation, applied to both sides) and use `PYTHONHASHSEED=0`.

**Equivalence results**
- **Baseline vs (a) and vs (a)–(d):** 16/16 parquets (nominal 563×127, 14 shifts ×75, sumw record) are exactly equal: same columns, order, dtypes and schema metadata. They are **byte-identical** (md5 over all 16 files: 41664e43fff5 for all three trees). The `.coffea` output is identical.
- **Multi-chunk run** (4 chunks, so the caches are reused): 64/64 files exactly equal.
- **Live-tree snapshot with the lepton-MVA port** (nominal 423×133): 16/16 exactly equal.
- **Unit test, 19 column types, old path vs new path:** same schema and byte-identical parquet for every type.

**Timings** (whole job, 1 chunk, `/usr/bin/time -v`, 3 alternating runs each; medians)

| | wall | CPU | max RSS |
|---|---|---|---|
| baseline | 46.5 s | 45.4 s | ~850 MB |
| (a) only | 33.5 s (−28%) | 33.2 s (−27%) | ~855 MB |
| (a)–(d) | 31.1 s (−33%) | 31.2 s (−31%) | ~850 MB |

- In-process cProfile: `dump_parquet` drops from 16.8 s to 1.8 s.
- The biggest remaining cost is `select_objects`, re-run on all 15 passes: 17.8 s of 39.7 s.
- The job times include fixed start-up, so the saving per chunk in multi-chunk condor jobs should be larger. That is an estimate, not measured.

## Needs a decision

1. TRAIN/RUN-mode restructuring (plan §2.3–2.5). Not implemented.
2. `request_cpus = 2` (patch 05), or `workers=1` instead.
3. Partitioning TT into ≤30 chunks per job (P1-perf (d)): changes the job layout.
4. Writing gen/LHE columns only for negrw datasets (P1-perf (e)): changes the output columns.
5. Adding the correctionlib cache in `muon.py`/`electron.py` (FULLFIX is editing them; about 0.12 s per chunk) and in the once-per-chunk loaders (`jerc.py` about 0.23 s per chunk, among others).
6. Optional: sort the weight variations so the column order is deterministic.
7. Physics: seed the muon smearing RNG (P0-8/B1).
