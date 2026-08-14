# Working scripts from the 2026-08-13 W+jets session

Copies of the diagnostics/fix scripts used during the jet-binned W+jets
reprocessing. See [[2026-08-13-wjets-session-handoff]].

Run on lxplus with:
```bash
export MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
$MAMBA_EXE run -n b_hive python3 <script>
```

| script | what it does |
|---|---|
| `repoint.py` | **The key fix.** Queries Rucio for all replicas of files on dead endpoints and swaps in a healthy one. Asserts file counts unchanged, so it can never drop a file (unlike `jobs_status.py` blacklisting). |
| `fix81.py` | Same, for a single additional bad endpoint (NCG Lisbon). |
| `site_audit.py` | Replica host distribution per sample — how many files sit on which endpoint. |
| `probe.py` | Reads random files from the fileset to verify replicas actually work before submitting. |
| `find_missing.py` | Which partition ids lack `sumw_records`. NOTE: partitions are numbered from 1; a reported `missing=[0]` is an artifact, not a gap. |
| `audit.py` | Per-sample coverage: partitions total / jobs finished / XRootD failures / partitions with output. |
| `integrity.py` | Readability + row counts of every live jet-binned parquet; confirms quarantine holds only inclusive. |
| `quar_verify.py` | Deeper quarantine check. **Its duplicate-sumw count is buggy** (overwrites a dict key) — use `dupcheck` logic instead. |
| `fix_quarantine.py` | Merges accidentally-quarantined jet-binned dirs back, file by file, tolerating jobs that recreate paths concurrently. |
| `neff.py` | Measures negative-weight fraction and effective statistics (n_eff/N, equivalent lumi) per sample. |

Needs Rucio for `repoint.py` / `fix81.py`:
```bash
source /cvmfs/cms.cern.ch/rucio/setup-py3.sh
```
