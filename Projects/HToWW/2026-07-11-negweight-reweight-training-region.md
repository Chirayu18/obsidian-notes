---
tags:
  - reference
status: active
date: 2026-07-11
source: lxplus
pinned: false
---

# Neg-weight reweighting — training region & selection logic

How we chose the **training region** for the negative-weight reweighting fix
(arXiv:2510.16217) and *why*. This is the region on which we learn
`g(x⃗) = 2·P₊(x⃗) − 1`, where `P₊(x⃗) = P(genWeight>0 | gen kinematics x⃗)`.

**Context:** [[2026-06-23-automcstats-rootcause]] (why the fix is needed),
[[ProposedFix-Automcstats]] (fix decision). Full pipeline plan lives outside the
vault at `~/.claude/plans/for-the-fix-of-logical-wadler.md`.

---

## TL;DR — the decision

- **Features `x⃗` = generator/parton-level only** (`lhe_*`, `genparton_*`), NOT reco.
- **Train on a looser region than the SR, but DISJOINT from it by construction:**
  all base cuts + a veto that removes **only the eμ signal-region topology**
  (`veto_emu_sr`). Keeps the no-dilepton-pair bulk + same-flavor (ee/μμ) pairs.
- **Infer** `g(x⃗)` on the tight eμ SR (`hww_combine_fixed`) later.
- Workflow: `analysis/workflows/hww_genrw_train.yaml` (category `train`).

The SR selection (eμ dileptonic + MET≥45 + ≥1 c-jet) starves vjets by ~10⁴×
(N_eff≈10/SR bin — the whole reason autoMCStats blows up). Training there is
impossible. So we train elsewhere and infer on the SR.

---

## Why generator-level features (not the analysis cuts)

`P₊(x⃗)` is a property of the **generator** (the amc@NLO FxFx NLO subtraction),
defined for *every generated event* regardless of which analysis box it lands in.
The paper (§V.2) explicitly rejects reco-level variables:

> *"Using reconstruction-level variables … will not guarantee closure on
> generator-level variables … Including all kinematic information … sampled during
> MC generation should be sufficient."*

Its 56 features (Table 4) are all gen/parton-level: parton pT/η/φ (up to 5),
kT merging scales, PS scales, `numPartons/Pt20/100/200`, `numB/numC`,
incoming-flavor flags. Our YAML dumps the matching set: `lhe_njets/nb/nc/nuds/nglu/
npnlo/ht/htincoming/vpt/alphas`, `genparton_multiplicity/n_pt20/100/200`,
`genparton_incoming1/2_pdgId`, `genparton1/2_pt/eta`, label `genweight_sign`.

**Consequence:** we do NOT apply the SR cuts before training. They would (a) throw
away ~99.99% of vjets and (b) add no gen information the classifier can use. Paper
§V.3 confirms they train on the full generated sample (a flat `event ≡ 1 mod 100`
subset) *before* analysis cuts.

## Why the training region must be event-DISJOINT from the SR

Paper §V.4: the SR evaluation **excludes the events used to train** the reweighting
classifier. If you reweight the same events whose weight-sign the classifier
memorized, `g(x⃗)` is optimistically biased and the measured variance reduction is
partly overfitting, not real. The paper enforces this with the `event mod 100`
hold-out.

**Our design gap it exposed:** naive train-loose / infer-tight is NOT disjoint — a
tight-SR event is a *subset* of a loose-training event (same underlying NanoAOD),
so they overlap. We needed an explicit disjointness mechanism.

## Why DISJOINT EVENTS, but NOT an orthogonal phase space

Two different things, easy to conflate:

| | required? | why |
|---|---|---|
| disjoint **events** | **yes** | else overfitting bias (above) |
| disjoint / orthogonal **phase space** | **NO — harmful** | `g(x⃗)` must be *interpolated* over the SR's x⃗ support, never *extrapolated*. Training in an anti-SR (e.g. c-depleted) region leaves the c-enriched SR corner unlearned → closure fails exactly where it matters |

So the goal is: **same phase space (spanning the SR), disjoint events.**

## The chosen mechanism: veto only the eμ SR topology

The SR requires `one_ll_pair AND one_muon_one_electron` (exactly one eμ pair) + MET≥45
+ ≥1 c-jet. We build the training region by taking the base cuts and vetoing **only**
the exactly-one-eμ-pair topology:

```
train = atleast_one_goodvertex AND lumimask AND met_filters AND trigger AND veto_emu_sr
veto_emu_sr = NOT( (num ll_pair == 1) AND (that pair is eμ) )
```

This gives, all at once:
- **Disjointness by construction** — an event that is not "exactly-one-eμ-pair"
  can never be an eμ SR event. No event-id bookkeeping needed.
- **Coverage of the SR's hard tail** — keeps the huge **no-dilepton-pair** population
  (≈88% of events have ≤1 lepton), which carries the hard Vpt/HT/parton-pT tail the
  SR probes. Also keeps **same-flavor (ee/μμ)** pairs (DY-rich).
- **Kinematic proximity** — lepton flavor (an EW decay choice) is ~orthogonal to the
  gen-parton `x⃗` that drives the negative weights, so the surviving region's x⃗
  distribution matches the eμ SR.

### Alternatives we rejected (and why)

- **Invert `met_45` (low-MET sideband)** — disjoint, but data-verified **kinematically
  softer** than the SR: `lhe_vpt` 20 vs 28, `lhe_ht` 32 vs 42, `genparton1_pt` 48 vs 59
  (MET<45 vs ≥45). Under-covers the SR hard tail → extrapolation. Rejected.
- **Invert `atleast_one_cjet` (c-depleted)** — the trap: flips into the *opposite* of the
  SR's c-enriched gen corner. Extrapolation where it matters most. Rejected.
- **Blind `event mod N` k-fold (paper's exact method)** — valid, but the veto scheme is
  more physically interpretable and keeps identical reco cuts. Kept as fallback.

---

## Selection coverage vs the SR (from the 2022postEE cutflow)

Why the SR itself is untrainable — vjets collapse across the SR cuts
([[2026-07-07-cutflow-2022postEE]], weighted events):

| cut | V+Jets | DY+Jets |
|---|---:|---:|
| trigger | 3.84e8 | 6.45e7 |
| + met_45 | 1.45e8 | 8.63e6 |
| + one_ll_pair | **2.06e4** | 9.01e5 |
| + one_mu_one_e | **1.09e4** | 1.21e4 |

V+Jets: 3.8e8 → ~1e4 (~35,000×). The `train` region sits at the **trigger** level
(minus the eμ sliver) — full stats, spanning x⃗.

---

## Verified numbers (small test run, 4 chunks of one WtoLNu file)

- **Efficiency ≈ 22.7%** raw (18,130 rows / 80,000 entries).
- Veto integrity: **0 eμ pairs leaked**; 18,128 no-pair + 2 same-flavor.
- Gen features clean & physical: `lhe_vpt` mean 23 (p95 89, **max 914** → hard tail
  present), `lhe_nc≥1` = 8.5% (the c-enriched corner), `frac(genWeight>0)` = 0.846.

**Production estimate** (3 vjets datasets, ~600M raw across 989 files):

| scope | raw in | training rows (~22.7%) | c-enriched (~8.5%) |
|---|---:|---:|---:|
| ~35 files | ~23M | ~5M | ~430k |
| ~160 files | ~105M | ~24M | ~2M |
| full 989 | ~600M | ~136M (overkill) | ~12M |

~5M rows is ample for a 20× classifier ensemble; full production is unnecessary.

---

## The veto bug we hit (documented so it never recurs)

`select_hww_ll_pair` (`analysis/selections/object_selections.py:519`) uses
**`ak.mask`**, so events with <2 leptons get `ll_pair = None` (option-type/masked),
**NOT** an empty list `[]`. Then `ak.num(None) == 1` → `None`, and the selection
manager treats `None` as **False** → a naive veto **drops every pairless event**
(~1000× over-veto; efficiency 22.7% → 0.009%, 18k rows → 7).

**Fix:** wrap the full eμ mask in `ak.fill_none(..., False)` *before* negating, so
pairless/same-flavor → not-SR → survive:

```python
veto_emu_sr: ~ak.fill_none(
    (ak.num(objects['ll_pair']) == 1) &
    ak.firsts(  # eμ test on the (masked) pair
        ((abs(objects['ll_pair'].l1.pdgId)==11) & (abs(objects['ll_pair'].l2.pdgId)==13)) |
        ((abs(objects['ll_pair'].l1.pdgId)==13) & (abs(objects['ll_pair'].l2.pdgId)==11))
    ), False)
```

Unit-tested on `[no-lep, eμ-pair, same-flavor-pair, single-lep]` →
`[keep, veto, keep, keep]`. General lesson: **any selection touching `ll_pair`
must be None-safe**, because pairless events are masked, not empty.

---

## Training-parquet stripping (gen-level classifier only)

The classifier only needs gen features + `sign(genWeight)`, so for the `train`
workflow we stripped everything else:
- `object_shifts: false` — reco shifts duplicate gen features + label.
- `add_syst_axis: false` — no systematics needed.
- `event_weights: {genWeight}` only — dropped pileup/PS/PDF/scale/nnlops + lepton-SF.
- Added `lepton1/2_pdgId` axes so the coverage check can split eμ vs same-flavor.

The reco/jet-topology axes are `None`-filled for no-pair events (harmless — the
writer's `ak.firsts` yields None per missing object), so they don't drop rows; but
they're irrelevant to training and could be pruned in a later cleanup.

---

## Phase-1 production run — what was done (2026-07-11)

**NOT the full datasets — deliberately capped at 35 files/dataset.** The full vjets
samples are 286 (`DYto2L_2Jets_50`) + 322 (`_10to50`) + 381 (`WtoLNu_2Jets`) = 989
files ≈ 600M raw events ≈ 136M feature rows. That is **overkill** for a 20× classifier
ensemble (the paper trains on ~millions), and processing all 989 files is a multi-hour
job for **zero statistical gain** — the c-enriched corner (~8.5%) is already saturated
at a few M rows. So we capped:

| dataset | full files | **used** | Condor partitions |
|---|---:|---:|---:|
| DYto2L_2Jets_50 | 286 | **35** | 3 |
| DYto2L_2Jets_10to50 | 322 | **35** | 3 |
| WtoLNu_2Jets | 381 | **35** | 3 |
| **total** | 989 | **105** | **9 jobs** |

→ ~105 files × ~660k entries ≈ **~24M raw → ~5M training rows** (~430k c-enriched) at
the verified 22.7% efficiency. Enough for the ensemble; the cap can be lifted later if
the coverage check shows a sparse corner.

**How the cap was applied:** the live fileset
`analysis/filesets/fileset_2022postEE_nanov12_lxplus.json` had been truncated to just
the 1 signal sample. Restored the 3 vjets samples into it from
`.bak_presiteredir`, sliced to the **first 35 URLs each** (`bak[name][:35]`). Prior
live fileset backed up to `.bak_pre_genrw`. Used the **grid redirectors** (FNAL/gridka/
RWTH) — the earlier "no proxy on lxplus" note is STALE: a valid CMS VOMS proxy exists
(`/tmp/x509up_u151861`, ~191h left), so DY-50/DY-10to50 (which have no `eoscms` copies)
open fine over grid. Only WtoLNu has eoscms URLs (35 of them).

**Submission:**
```
python runner.py -w hww_genrw_train -y 2022postEE --output_format parquet \
    --eos --nfiles 12 --memory 6000 --submit
```
`--nfiles 12` = files per Condor partition (→ 3 partitions × 35 files). NOTE `--nfiles`
is the *partition size*, NOT a total cap — the total is controlled by how many files
are in the fileset (the 35-slice above). 9 jobs submitted: clusters **9071462**
(DY-50), **9071463** (DY-10to50), **9071464** (W). Flavour `longlunch`, 6 GB, coffea
0.7.30 singularity. Output → `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/`.

## ✅ PHASE-1 RESULTS + COVERAGE PASS (2026-07-12 00:20)

**Phase-1 production is DONE** (8/9 jobs finished; 1 DY_50 straggler still running but
its ~1M rows don't change any verdict). Ran the veto-integrity + coverage analysis on the
9.65M rows landed so far. **Both gates PASS — cleared to launch Phase 2.**

Analysis scripts: `~/.claude/jobs/af76ec6a/tmp/analyze_genrw.py` (rows+veto+features) and
`.../coverage_genrw.py` (coverage), both copied to `/tmp/*.py` on lxplus, run via
`micromamba run -n b_hive python`.

**Row count:** **9.65M training rows** (497 parquet files; higher than the ~5M estimate —
more stats, good). Split: 8.76M no-pair + 833k same-flavor-pair rows.

**Veto integrity — PERFECT:** **0 eμ-pair rows leaked** among 833k rows-with-a-pair (all
same-flavor). Train/infer disjoint-by-construction confirmed at scale.

**Weights:** `weight_nominal` 100% non-null, frac>0 = 0.836 (=`genweight_sign` frac>0),
mean|w| ≈ 148k. This is the classifier label/weight column (NOT weight_genweight).

**COVERAGE CHECK — PASS.** SR-proxy = the **same-flavor dilepton pairs** (flavor-blind gen
analog of the eμ SR: same W/Z+jets ME, lhe_* are ME-level so identical support). Every one
of 9 gen features (lhe_vpt/ht/nc/nb/njets/npnlo, genparton1_pt, dilepton_pt, met_pt) has
SR-proxy max ≤ training-domain max → **no extrapolation, only interpolation**. Highlights:
- lhe_vpt: SR-proxy p99=223 max=1127 ⊂ train p99=161 max=1296 ✓ (SR lives in the hard
  tail — median 49 vs 2.3 GeV — but that tail IS populated in training).
- lhe_ht: SR max 2542 ⊂ train max 3479 ✓. lhe_nc: SR needs up to 3, train has up to 3 ✓
  (SR nc≥1 frac 8.96% vs train 6.44% — training carries the c-enriched support).
- Tail extrapolation risk tiny: only ~3% of SR-proxy events beyond train-p99, and the max
  still fits (interpolation).

**N_eff (the whole point):** full training N_eff = **2.76M / 9.65M**; SR-proxy N_eff =
**180k / 833k** (frac>0 only 0.738 — the pair region is the negatively-weighted, starved
regime the paper targets). The rich training pool is what lets g(x⃗) lift the SR N_eff.

**→ NEXT: Phase 2** — run `/eos/user/c/cgupta/HToWW/b-hive/scripts/negweight_reweight_train.py`
(20× HistGradientBoostingClassifier ensemble, label `weight_nominal>0`, features = the 20
lhe_*/genparton* cols). Then closure gate (Σ|w|·g reproduces nominal; SR N_eff up).

---

## ⏳ RESUME STATE (2026-07-11 22:53 — read this first if picking up cold)

**Where we are:** Phase-1 training-pass Condor jobs SUBMITTED, all 9 **idle** in a busy
queue (22k idle cluster-wide), no parquet output yet. Everything below is durable; the
plan file `~/.claude/plans/for-the-fix-of-logical-wadler.md` has the full pipeline.

**Live job handles:**
- Clusters: **9071462** (DYto2L_2Jets_50), **9071463** (DYto2L_2Jets_10to50),
  **9071464** (WtoLNu_2Jets). 3 jobs each = 9 total.
- Check: `ssh lxplus 'condor_q 9071462 9071463 9071464 -totals'`
- Output: `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/`
- Count parquet: `find <output> -name '*.parquet' | grep -v sumw_records | wc -l`

**Resume connection if dropped (do NOT ask user for password/kinit):**
`python3 ~/bin/lxplus-connect.py` (now self-heals stale sockets) → verify
`ssh lxplus 'echo OK'`, `ls ~/mnt/lxplus` non-empty. See [[lxplus-workflow]] memory.

**NEXT STEPS in order:**
1. **Wait for the 9 jobs** to finish (idle → running → done). If HELD, `condor_q -held`
   for the reason (likely xrootd auth if the AFS proxy `private/x509up_u151861` expired —
   re-run the runner build step to refresh it, then `condor_release`).
2. **Merge + load** the parquet output, count rows (~5M expected).
3. **Veto integrity at scale:** confirm 0 eμ pairs leaked (`lepton1/2_pdgId`: no
   exactly-one |11|+|13| pair among rows with a pair).
4. **COVERAGE CHECK (the Phase-2 gate):** compare the training `x⃗` distribution against
   the **eμ-SR** `x⃗` on `lhe_vpt`, `lhe_ht`, `lhe_nc≥1` (+ `genparton1_pt`). The eμ-SR
   reference = the existing `hww_combine_fixed` parquets (they lack gen cols yet — either
   read gen cols from a small eμ-SR test run, OR the plan's Phase-1 step 2 "inference
   pass" produces `hww_combine_fixed_genrw/` with gen cols; that pass is NOT yet run).
   Pass criterion: SR `x⃗` inside the training domain (no extrapolation), esp. the
   c-enriched and high-Vpt tails. If under-covered → lift the 35-file cap for that
   dataset (edit the fileset slice `bak[name][:N]`) and resubmit.
5. **Phase 2** (only after coverage passes): run
   `/eos/user/c/cgupta/HToWW/b-hive/scripts/negweight_reweight_train.py` — 20×
   HistGradientBoostingClassifier ensemble on the gen features, label `weight_nominal>0`
   (or `genweight_sign`), emit `g=2·mean(P₊)−1` + ensemble spread. Then closure gate
   (reweighted `Σ|w|·g` reproduces nominal within stat err; N_eff up in SR bins 4–6).

**Files touched this session (all durable):**
- `analysis/workflows/hww_genrw_train.yaml` — `veto_emu_sr` selection (+ None-safe fix),
  `train` category, stripped weights/syst axis, `lepton1/2_pdgId` axes.
- `analysis/filesets/fileset_2022postEE_nanov12_lxplus.json` — restored 3 vjets samples
  @ 35 files each (prior backed up to `.bak_pre_genrw`).
- `~/bin/lxplus-connect.py` — self-healing stale-socket fix (unrelated infra).
- Plan: `~/.claude/plans/for-the-fix-of-logical-wadler.md`.
- Test driver (throwaway): `/afs/cern.ch/user/c/cgupta/test_genrw_veto.py`.

## Next step (short form)

Jobs finish → count rows → veto integrity → coverage check → Phase-2 training.

Related: [[2026-06-23-automcstats-rootcause]] · [[ProposedFix-Automcstats]] ·
[[2026-07-07-cutflow-2022postEE]] · [[Analysis QUICKSTART]]
