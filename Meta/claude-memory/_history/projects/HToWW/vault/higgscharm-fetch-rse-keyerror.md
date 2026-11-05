---
name: higgscharm-fetch-rse-keyerror
description: higgscharm fetch.py "Exception: 'rse'" + every dataset "selected: N" + empty fileset = stock coffea rucio_utils crashing on T3_CN_Nanjing storage.json; repo overlay guard fixes it (verified 2026-10-22)
metadata:
  type: project
---

Since 2026-05-01, `/cvmfs/cms.cern.ch/SITECONF/T3_CN_Nanjing/storage.json` has a DISK entry with no `rse` key.
Stock coffea `get_xrootd_sites_map` does `site["rse"]` -> KeyError, DataDiscoveryCLI only prints "Exception: 'rse'",
no replicas get selected, the fileset JSON is empty, and make_filesets.py dies with `TypeError: 'NoneType' object is not iterable`.
The repo's `analysis/filesets/rucio_utils.py` (bind-mounted over coffea's copy by fetch.py, target path hardcoded to python3.10)
has `if "rse" not in site.keys(): continue`.

VERIFIED 2026-10-22 on a `git archive` scratch copy of hww-analysis b7f67ef, 2024 GluGlu2Zto2Mu2Tau, image coffea-dask-almalinux9:2025.10.1-py3.10:
- Stock coffea: reproduces the colleague's failure exactly.
- With the overlay: 31 files, which equals the DAS count.

Colleague's branch AlexDeMoor/higgscharm@Htautau-analysis (78699d0) ALREADY has the guard + overlay, and running her pushed branch exactly as she did works for me (31 files, 2026-10-22). So her failure is her local checkout/environment, not the code; no PR made. Ask for hostname, `git log -1`, the guard grep, and whether a stale 2024_sites.yaml exists.
Gotcha: hww-analysis make_filesets.py hardcodes `{year}_nanov12.yaml` while 2024 is `2024_nanov15.yaml`.

ROOT CAUSE FOUND 2026-10-22: the colleague (Claire Dooms, cdooms) runs `$PY fetch.py`, with $PY = apptainer coffea-base-almalinux9:0.7.30-py3.10
as in her branch README. She had replaced fetch.py's nested `singularity exec` (which carries the rucio_utils bind) with plain
`python3 -m analysis.filesets.make_filesets`, so stock coffea was loaded.
FIX PUSHED: branch Chirayu18/higgscharm:fix-rucio-utils-override (0d773b2, based on AlexDeMoor Htautau-analysis 78699d0).
- make_filesets registers the repo module in sys.modules before importing DataDiscoveryCLI.
- fetch.py runs make_filesets directly when APPTAINER_CONTAINER/SINGULARITY_CONTAINER is set.
- Accepts the coffea 0.7 list format for "files" (0.7.30 saves a list; the old code's .keys() crashed).
Tested: control reproduced 'rse'; then 31 files via her $PY, via host python3, and inside coffea-dask 2025.10.1.
