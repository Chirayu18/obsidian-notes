---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
task: HTOWW-ROUTEB-SOL-20261105
---
# Route B (private 3FS + central 4FS FxFx) stitching: proposal implemented and tested

**Status: agent-reported.** This was written by the Claude implementation child, working in parallel with Sol's TRAIN/RUN work. Chirayu has not reviewed it.

What it is:
- a **proposal**, with a standalone module, workflow, filesets and a reference hook;
- tested with synthetic unit tests and local single-file smokes.

What it is not:
- **not integrated** into the live processor;
- not run as a production;
- no limit.

No analysis-repo file was edited, committed or pushed. No checkout was made, no jobs were submitted, nothing was deleted, and no credentials were renewed.

- **Proposal directory:** `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/proposals/HTOWW-ROUTEB-SOL-20261105/`. The full detail is in its `README.md`; `FILELIST.txt` and `SHA256SUMS.txt` list the files; `*.v1` are backups of overwritten proposal files.
- **Live repo**, read-only: lxplus921, branch `hww-analysis`, HEAD `40d0e3e`, plus Sol's uncommitted edits. Snapshots with sha256 are in `src_snapshots/live/SNAPSHOT_INFO.txt` (08:13:54Z).
- **Background:** [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state]] (decision 6, R = 0.4 and |η| < 2.5) and [[Projects/HToWW/2026-11-05-sol-review-unpushed-work]].

## The physics, as implemented (no decision reopened)

- **Source:** LHCHWG-2026-007 (arXiv:2608.26863) §4.4, read from `References/HToWW/2026-LHCHWG-2026-007_Hc_flavour_schemes_arXiv2608.26863.pdf`.
  - The split is on N(c-jets, pT > 10 GeV). Footnote 4 explains the 10 GeV: it is set below the usual 25 GeV to resolve the soft-charm region.
  - Events with N = 0 come from 4FS-FxFx; events with N ≥ 1 come from 3FS.
  - Each region gets its sample's fiducial σ × a flat bb̄H NNLO/NLO K-factor. The total is then rescaled to MiNNLOPS.
- **Table 3** (13.6 TeV, H→γγ, "No cuts", fb):

  | | value |
  |---|---|
  | MiNNLOPS 4FS | 0.1664 |
  | NLO 4FS | 0.2216 |
  | NLO 3FS | 0.1248 |
  | NLO+bbHfact 4FS | 0.1690 |
  | NLO+bbHfact 3FS | 0.1630 |

  - So K₄FS = 0.7626 and K₃FS = 1.3061. They are the same within rounding in all three columns.
  - The paper gives **only per-scheme flat factors**, no separate per-region factors.
- **c-jet:** NanoAOD GenJet (anti-kT 0.4) with hadronFlavour == 4, pT > 10 (strict), |η| < 2.5 (strict).
- **Event weight (kept events only):**

  ```
  L · X · c_s · genWeight / F_s
  ```

  - F_s: the signed, pre-selection, pre-jet-veto sum of genWeight over all datasets of scheme s in the era. 2022postEE main and `_ext1` are summed together.
  - f_s: the kept fraction of F_s.
  - D = 0.1690·f₄FS + 0.1630·f₃FS, and c_s = A_s / D (A₄FS = 0.1690, A₃FS = 0.1630).
  - X = 0.0016626 pb is the existing NNLO fileset xsec. It is shared by both schemes, and the code enforces that.
  - Closure: the kept events sum to exactly L·X.
- **Not the same as Run A:** Run A's `xsec_hplusc_3FS_4FS` is a reweighting of the 4FS sample by c-hadron pT. Route B is not that. The Route B workflow disables that nuisance (`hpluscFSShape: []` and removed from the shape list). The paper's reason: stitching makes the flavour-scheme uncertainty unnecessary, and the stitched sample's scale uncertainty covers what is left.

## What was produced (proposal paths)

| what | path under the proposal dir |
|---|---|
| Stitching module: masks, additive full/kept sums with sumw2, \|w\| and negative counts, normalisation, workflow config | `new_files/analysis/stitching/hplusc_routeb.py` |
| Record I/O and card-builder scales: per-chunk records keyed by partition key, de-duplication, cross-check against `sumw_records`, TRAIN/RUN reader | `new_files/analysis/stitching/routeb_io.py` |
| 20 synthetic tests | `new_files/tests/test_routeb_stitching.py` |
| Route B workflow, derived from `hww_allfix_4fs` (sha256 `365cd60d…`) | `new_files/analysis/workflows/hww_routeb_3fs4fs.yaml`; diff in `patches/hww_routeb_3fs4fs.yaml.vs_allfix.diff` |
| Era YAML additions: key `hc_3fs`, process `H+c`, xsec 0.0016626 (this is σ_NNLO × BR, **not** a 3FS σ) | `filesets/proposed_<era>_nanov12.yaml`, `patches/<era>_nanov12.yaml.patch` |
| Derived file lists | `filesets/fileset_<era>_routeb_3fs_only.json`, `filesets/proposed_fileset_<era>_nanov12_lxplus.json`, `filesets/MANIFEST.json` |
| Reference BaseProcessor hook, against a snapshot of Sol's in-progress `base.py`. Sol ports it; do not apply blindly | `patches/base.py.routeb_hook.REFERENCE.patch` |

The file lists come from `dasgoclient` on prod/phys03 (2026-11-05) and use the redirector `root://maite.iihe.ac.be:1094/` (T2_BE_IIHE). The event counts:

| era | events |
|---|---|
| 2022preEE | 1,261,997 |
| 2022postEE | 4,119,986 |
| 2022postEE `_ext1` | 166,999 |
| 2023preBPix | 2,869,993 |
| 2023postBPix | 1,517,991 |
| **total** | **9,936,966** (matches) |

The `cgupta-TEST-*` datasets are excluded.

## Tests (agent-run, coffea 0.7.30 container on lxplus921)

- **Unit tests: 20/20 pass** (`diagnostics/unittest_routeb.log`). They check:
  - the masks are complementary and exclusive;
  - the boundaries at pT = 10 and |η| = 2.5 are strict, and only flavour 4 counts;
  - the count equals Saranya's when there is no η cut;
  - the sums do not depend on how the input is partitioned or ordered;
  - closure holds and the normalisation equals the paper's two-step formula;
  - pooled and per-era fractions behave as expected;
  - a retried or duplicated chunk is not double counted, and a conflicting one raises;
  - a missing chunk is caught;
  - main and `_ext1` share one F_s.

  The suite also fails under each of four deliberate mutations: pT `>` → `>=`, η `<` → `<=`, 3FS keeping `n >= 2`, and dropping the 4FS K-factor.
- **Single-file smokes** (local, EXIT 0):
  - 3FS 2022postEE `nanoaod_100.root` (1000 events) and 4FS central `27982ec7…` (85,732 events).
  - Σw matches the Runs-tree `genEventSumw` to 5e-8 and 2e-8.
  - Splitting into 4 partitions changes nothing.
  - NanoAOD keeps GenJets only above 10 GeV (smallest seen: 10.0007 and 10.00005 GeV) and applies no η cut.
  - The Higgs decays only to W in both files.
  - The workflow parses with the live `WorkflowConfigBuilder`, and every H+c dataset in each era maps to a scheme.
- **Subset estimate** (local GEN-branch reads only; illustrative, **not** the production normalisation):

  | | files | kept fraction |
  |---|---|---|
  | 3FS 2022postEE | 206 | f₃ = 0.4647 ± 0.0052 |
  | 3FS 2023postBPix | 102 | f₃ = 0.4684 ± 0.0075 |
  | 4FS 2022postEE | 6 | f₄ = 0.6060 ± 0.0015 |

  This gives c₄FS ≈ 0.948 and c₃FS ≈ 0.914. In the stitched σ_NNLO, about 57% comes from 4FS events with 0 c-jets and 43% from 3FS events with ≥1 c-jet. In Run A, 4FS events with ≥1 c-jet carry 39.4%. Negative-weight fraction: 3FS 39.5%, 4FS 19.7–19.8%. For 3FS, Neff/N ≈ 0.044.
- **Not tested:**
  - the hook inside the live processor;
  - the production record writer (`write_record`);
  - the card-builder integration;
  - any production, card or limit.

## Saranya's HcZZ code (Chirayu: take anything useful)

- **Source:** commit `c508ecc58a165bd1a7d1e47f8db5a0ede1320872` on `origin/HcZZ-zx-estimation`. It was read from Sol's clone `/tmp/cgupta_sol_hczz_20261105` on lxplus921; the old `~/.cache/hczz-port-survey/sn` clone is gone. A snapshot is in `src_snapshots/saranya_c508ecc/`.
- **Reused:** the logic of `count_gen_cjets`, with |η| < 2.5 **added** (hers has no η cut).
- **Not reused as-is:** her `sumw_by_genc`. Two problems:
  - Its sums are taken after the jet veto; she flagged this herself.
  - It applies raw `LHEScaleWeight/[4]` ratios, which are broken on our central 4FS sample unless the `lhe_norm`/Yukawa fix is applied.

  Route B instead records signed, pre-veto full and kept sums, with optional *corrected* multipliers.
- **Not needed:** her c-hadron columns, which are Run A's definition.

## Blockers and open points (flagged, values not invented)

1. **The private 3FS NanoAOD has an empty `LHEPdfWeight`** (0 members, and an empty branch title). The live `lhepdf.py` then silently sets PDF/αS Up = Down = 1 on every 3FS event with ≥1 c-jet, which is most of the c-tagged signal region. **Needs Chirayu:** produce a custom NanoAOD that stores that PDF set, or use a flat PDF lnN for that region.
2. **Scale variations are normalised inconsistently across the stitch.** The central 4FS variations are inclusive-renormalised by `lhe_norm` plus the Yukawa fix. The 3FS variations are clean and keep their normalisation effect. The paper does not say whether the stitched variations should be renormalised to NNLO. **Needs a decision.** The 3FS sample must *not* go into `lhe_renorm_datasets`.
3. **GenJets include the H→WW leptons**, which can push a c-jet across 10 GeV. The paper studies only H→γγ, so it does not cover this. Flagged, not corrected.
4. **Pending live integration (Sol):**
   - BaseProcessor: full-chunk sums, then the mask. F_s stays on the existing sumw path.
   - TRAIN/RUN sinks: one JSON string per chunk.
   - Card builder: use L·X·c_s/F_s.
   - `selection_signature`: hash the `stitching` block and `analysis/stitching/`.
   - MVA training weights.
   - A hook smoke test on one file per scheme.

**Needs Chirayu:** items 1 and 2, and the `per_era` vs `pooled_fractions` estimator for the kept fractions (default `per_era`).
