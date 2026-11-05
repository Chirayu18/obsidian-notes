---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
---
# Saranya's HcZZ branch vs our hww-analysis: comparison and ports

This note consolidates three sessions: the 2026-10-23 history check (session `fa3f94a0`) and the 2026-10-29 survey and port (sessions `da82409c` and `a5acb22c`). The 11-05 column was checked read-only in the live tree. The other findings are agent-reported from those sessions and were not re-run here.

- **Her branch:** https://github.com/Saranya-Nandakumar/higgscharm/tree/HcZZ-zx-estimation (H→ZZ→4ℓ + c).
- **Our branch:** lxplus `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`.
- **Survey clone:** `~/.cache/hczz-port-survey/sn` (lxplus).

## Shared history
- **Common base:** both branches fork from upstream `ua-cms` main at `7d6838e` (2026-02-13). On 10-29 hers was 78 commits ahead, and ours had 77 commits of its own plus many uncommitted fixes. Bringing things over is therefore a cherry-pick job, not a merge.
- **Where her commits come from:** most are upstream `ua-cms` commits (936 of 991 on 10-23) that she pulled from upstream directly, not from our fork.
- **Code of ours on her branch:**
  - our `ctag2d.py` and `higgs_hf.py`;
  - the 2D c-tag SF paths in `utils.py`;
  - the impact-ranking method (`make_impact_plot.py`).

  Her README credits the hww-analysis branch for these, including an 08-14 list titled "next techniques to port from hww-analysis".
- **Her systematics:** 2 of her 19 systematics are our code (`CMS_ctag2d`, `higgs_plus_c`). She wrote her own object shifts and `autoMCStats` on upstream machinery.

## From her branch to ours

| item | decision | status |
|---|---|---|
| **Invalid DY datasets:** all 10 central DY NanoAODv12 datasets in our era YAMLs are INVALID in DBS. Jobs would die with `[3011] No servers are available`. This was the most useful find. | must fix before rerun | replaced 11-03, see [[Projects/HToWW/samples-and-production/2026-11-03-dy-replacements\|2026-11-03-dy-replacements]] |
| `lhescale.py`: Up/Down label swap. Up was r(1), i.e. μR = 0.5; now Up is the ×2 entry. | ported 10-29 (labels only; our per-event Yukawa and w4 logic kept) | in tree (uncommitted) |
| `lhepdf.py`: signed αS instead of `0.5*abs(w_high − w_low)` | ported 10-29 (our 0.5 cap kept) | in tree (uncommitted) |
| her PDF `/99` | **not ported**: it is for MC-replica sets, and our central samples use Hessian 306000 | n/a |
| `parquet_writer.py`: xrdcp retry on "[3018] Unable to mkdir: File exists" | ported 10-29 | in tree, `analysis/utils/parquet_writer.py` |
| correctionlib `latest` paths pinned to dated snapshots, so they can't drift silently like the JER tag split did | ported 10-29 (all 10 paths, md5-identical to `latest` that day) | in tree, `correctionlib_files.py` |
| `eos_io.py`: list `/eos` from the EOS server, not FUSE. Stale FUSE listings made her builder read subsets and moved one of her limits from 342 to 412. | ported 10-29 as `analysis/utils/eos_io.py` (merge, shift shards, sample discovery, sumw, `make_combine_inputs.py`) | in tree. 10-29 test: same 55 samples and bit-identical sumw on 2022postEE; listing 31 s vs 5 s |
| job completeness check in `bookkeeping.py`, comparing events written with parquet rows (our plan item P0-14) | not ported | open |
| per-era c-tag 2D category edges (`BOUNDARIES_BY_ERA`, from HiggsDNA), incl. 2024/25 UParT | **skipped**: Chirayu said "no ctag" on 10-29 | open; matches our known "ctag2d edges wrong" bug |
| c-tag SF placeholder cells: about 41% of the grid returns 1.0 / 3.0 / 0.3. This likely explains our +43% `CMS_ctag2d_2022` Up on SR signal. Her `_decorr` builder splits the c-tag uncertainty into 33 stat sources per era. | **skipped** (c-tag set aside) | open |
| GEN c-jet / c-hadron columns plus split sumw sidecars (`count_gen_cjets`, `gen_chadron_info`, `sumw_by_genc`) | was optional on 10-29 (shape-only FS decision then) | may be relevant again for Run B stitching |
| her `condor/submit.sh` exit-0-on-xrdcp-failure trap | does not apply to us: our script ends on `python3 submit.py` with `-e` | n/a |

**Traps to remember**
- The EOS 5M file-count quota fills before the byte quota.
- Nuisance names longer than 25 characters break `write_datacard`.

## From our branch to her (probably not sent yet)

The 10-29 assessment was that we have more to tell her than she has to tell us.

1. **Unit LHE scale nominal.** Her `lhescale.py` passes `LHEScaleWeight[4]` as the nominal for all three nuisances. That multiplies weights by w4³, the bug we fixed on 10-01. It matters for powheg MiNNLO WH/ZH, where w4 reached about 2×10⁴.
2. **JER on 2022preEE.** Her JERC pin there is still `latest`, so JER is probably a no-op after the tag split. Her other eras are pinned before the split. This was not run to confirm.
3. **Type-1 MET re-correction sign.** It is wrong in her `jerc.py`, which re-corrects stored PuppiMET using `pt_raw`. It is minor for ZZ→4ℓ unless MET is used. Our fix was itself corrected again on 11-04; see [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|2026-11-05-fullfix-rerun-run-a-state]].
4. **Electron scale and smearing uncertainties.** They are not implemented in her `electron_ss.py` (marked TO DO), and she has 4e and 2e2μ channels.
5. **Our PDF/αS outlier cap**, and the top-pT and electron-smearing fixes.

## Open follow-ups
- **Message to Saranya:** Chirayu decides whether and when to send items 1–5 above. Nothing in the vault shows it was sent.
- **c-tag items:** port the per-era edges and decorrelate the placeholder cells, if c-tag is revisited.
- **Bookkeeping:** port her `bookkeeping.py` completeness check.
- **Commits:** the 10-29 ports are uncommitted and are part of the pending Run A baseline commit. Backups are `*.bak_pre_hczzport_20261029`.
- **Vault commit trailer:** vault commit `9ea0bf0` (10-29) was pushed with a Co-Authored-By trailer against the no-attribution rule. It was left rather than force-pushed, pending Chirayu.
