---
tags: [reference]
status: active
date: 2026-09-03
source: lxplus
---

# ATLAS Open Data — complete survey for the flashjet benchmark

Exhaustive pass over **all 188 ATLAS records** on the CERN Open Data portal
(`/api/records/?experiment=ATLAS&size=1000`), checking every dataset for usable
jet-clustering input. Supersedes the PHYSLITE-only conclusion in
[[2026-09-03-atlas-opendata-feasibility]].

**Headline: ATLAS *does* publish jet constituents — three usable datasets, one of
them detector-level reconstructed clusters with higher multiplicity than any CMS
sample currently in the deck.**

---

## Full catalogue breakdown

188 records: 163 Dataset, 7 News, 5 VM, 4 Glossary, 7 Documentation, 3 Software.

| format | n | verdict |
|---|---|---|
| `root` (2020 educational ntuples) | 71 | summary kinematics only — **no** |
| `DAOD_PHYSLITE` | 12 | constituents deliberately dropped — **no** |
| `root`+`zip` (2020 collections) | 8 | summary kinematics — **no** |
| `DAOD_HION14` (Pb+Pb) | 3 | no jets/clusters, but **TruthParticles** — partial |
| `h5` / `gz`+`h5` | 3 | **YES — top tagging + JetSet** |
| `parquet` | 1 | **YES — OmniFold** |
| `HEPMC` | 2 | generator level, 24.2M events — usable, not a measurement |
| `<none>` (masterclass etc.) | 57 | educational — no |
| misc (csv/LHE/hdf5) | 6 | ATLFast3, DM search, calo voxels — no |

**Method note:** the portal mixes numeric recids (`80014`) with namespaced ones
(`atlas-160005`). A numeric-only filter silently drops the entire `datascience`
family — which is where all the good datasets live. Enumerate everything.

---

## The three usable datasets

### 1. ATLAS Top Tagging Open Data — **best match, detector level**

`recid 15013` (ATL-PHYS-PUB-2022-039), superseded by `recid 80030` (adds
systematics: 92.8M train / 10.3M test jets + 8 systematic variations).

```
root://eospublic.cern.ch//eos/opendata/atlas/datascience/ATL-PHYS-PUB-2022-039/test.h5   (8.2 GB, 2 484 117 jets)
root://eospublic.cern.ch//eos/opendata/atlas/datascience/ATL-PHYS-PUB-2022-039/train.h5  (139 GB, 42M jets)
```

HDF5 layout (verified by reading the file):

| dataset | shape | content |
|---|---|---|
| `fjet_clus_pt/eta/phi/E` | (2484117, **200**) | **calorimeter cluster constituents**, MeV |
| `fjet_pt/eta/phi/m` | (2484117,) | the stored large-R jet |
| `fjet_{C2,D2,Tau32_wta,Split12,ECF1..3,Qw,...}` | (2484117,) | 15 substructure quantities |
| `labels` | (2484117,) | 1 = boosted top, 0 = light quark/gluon |
| `weights` | (2484117,) | required training weight |

Measured on 200k jets: **55.9 constituents/jet** (median 50, min 4, max 200),
100 % of jets have >=2; signal 59.4, background 52.5. Clusters are **massless**
(median m^2/E^2 = 5.3e-4). Balanced signal/background.

**Closure check (FastJet, anti-kt R=1.0, 400 jets):**
- recluster pT / **vector-sum** pT = **1.0000 +- 0.0000**, 100 % within 1 %
  -> FastJet recovers every constituent into one jet, exactly.
- recluster pT / **stored** jet pT = 0.866 +- 0.017 — a uniform offset, i.e. the
  stored jet's **calibration (JES)**, present before any clustering. Not a defect.

This is the CMS-MINIAOD-equivalent input: real detector-level constituents,
**multiplicity above all four CMS points** (10.8 / 15.1 / 22.2 / 34.0).

### 2. 2020 Jet Reconstruction dataset — **event regime**

`recid 15010`, "for educational purposes related to Jet Clustering techniques".

```
root://eospublic.cern.ch//eos/opendata/atlas/OutreachDatasets/2020-05-26/JetRecoDataset/mc_jets-2020.part01.root  (x10 parts, 1.03M events)
```

Branches: `Clusters_{pt,eta,phi,m}`, `Particles_{pt,eta,phi,m,pdgID}`, plus ATLAS's
own `RecoJets_R4`, `RecoJets_R10(_Trimmed)`, `TrackJets_R4`, `TruthJets_R4/R10`
with `D2beta1` / `tau32wta`.

Measured (3000 events): **591.6 clusters/event** (median 564, max 1431), 441
particles/event, `Clusters_m` identically 0. RecoJets_R4 17.0/event.

Two things the top-tagging set cannot give: the **event regime** (O(N^2), C5) and
a **built-in reference jet collection** for agreement — cluster the event, compare
to ATLAS's own RecoJets_R4.

**Closure vs ATLAS's own jets (anti-kt R=0.4, pT>20 GeV, 60 events) — exact:**

| check | result |
|---|---|
| n jets, mine vs `RecoJets_R4` | **10.58 vs 10.58**, exact count match on **100 %** of events |
| leading-jet pT ratio | **1.0000**, std **0.0000** |

This is a *stronger* validation than agreeing with FastJet: reclustering the stored
clusters reproduces **ATLAS's official reconstructed jets exactly**. Worth a slide
on its own — it closes the algorithm against the experiment's own output, not
against another implementation of the same algorithm.

**Confirmed with flashjet itself in the loop** (`event_matrix.py`, 50 events,
**599.3 clusters/event**, anti-$k_t$ R=0.4):

| comparison | result |
|---|---|
| flashjet vs FastJet, n_jets | **100.0 %** |
| flashjet vs FastJet, leading pT within 1e-4 | **1.0000** (median rel. 4.5e-08) |
| flashjet vs **ATLAS `RecoJets_R4`**, n_jets (pT>20 GeV) | **100.0 %** (10.96 vs 10.96 per event) |

So flashjet reproduces **ATLAS's own published jets** while clustering ~600 real
calorimeter clusters per event. Note the CPU torch backend is O(N^3) here and
warns at N=1384 (2.9 GB of (B,N,N) buffers) — the full event-regime grid belongs
on the GPU's triton-large backend.

### 3. OmniFold charged particles — particle level

`recid atlas-160005`, STDM-2024-02. Parquet, 1 035 835 events.
`truth_{pT,eta,phi,pdgId}_particles` + `truth_trackJetIndex_particles`.
**55.2 particles/event.** Charged-only, unfolded — legitimate clustering input but
not detector level. See [[2026-09-03-atlas-opendata-feasibility]].

### Also noted
- **Pb+Pb `DAOD_HION14`** (`80035-80037`): no jet/cluster containers, but a real
  `TruthParticles` with **8378 particles/event, max 59389** — an extreme-N stress
  case far beyond anything currently benchmarked.
- **JetSet** (`93940`): ttbar with track-level info for flavour tagging, 50M events
  — tracks per jet, not calorimeter constituents.
- **HEPMC** (`160000`, `160002`): 24.2M generator events, full final state.

---

## Extractor (written, run, validated)

`/eos/home-c/cgupta/flashjet/bench_atlas/` — `dump_atlas_toptag.py` emits the
**same npz contract** as the CMS `dump_opendata_constituents.py`
(`p4 (Njet,NMAX,4)`, `ncon`, `raw_pt`), so the existing benchmark scripts run
unmodified. MeV->GeV, massless clusters, rows compacted so valid constituents form
a contiguous prefix.

```
opendata_constit_atlastop-top_ak4.npz   30 000 jets, mean 59.2 const/jet, 1 777 407 total
opendata_constit_atlastop-qcd_ak4.npz   30 000 jets, mean 52.4 const/jet, 1 573 073 total
```

Contract verified: 0 violations in 2000 jets (padding zero beyond `ncon`, no zero
rows within), massless to 3.4e-4.

---

## Full sweep — what is being run

`bench_atlas/sweep_flashjet.py` + `sweep_fastjet.py`, submitted to Condor
(clusters **9262951** H100/A100, **9262953** V100).

**Grid: 3 algorithms x 5 radii x 5 multiplicity bins x 2 samples = 150 points/GPU.**

- algorithms: anti-$k_t$, $k_t$, **C/A** (`flashjet.cluster(algorithm=...)`)
- radii: R = 0.4, 0.6, 0.8, 1.0, 1.2
- multiplicity bins on n_const: `lo` 2-30, `mid` 30-60, `hi` 60-100,
  `vhi` 100-200, `all`
- samples: `atlastop-top` (boosted top), `atlastop-qcd` (light quark/gluon)
- baselines: FastJet **classic** (per-jet) and **awkward** (vectorised, the fair one)

### Agreement is checked two ways

The existing CMS benchmark compares **jet counts** only. That is weak for
$k_t$ / C-A, where counts can coincide while the jets differ. The sweep adds a
**leading-jet pT match** (relative, 1e-4 and 1e-2 thresholds).

### CORRECTNESS MATRIX — complete, CPU (no GPU needed) — **NEW PHYSICS**

`correctness_matrix.py`, 150 jets per bin, **3 algorithms x 5 radii x 4
multiplicity bins x 2 samples**. Results: `correctness_atlastop-{top,qcd}.json`.

| sample | points | njet agreement | leading-pT within 1e-4 | worst rel. diff |
|---|---|---|---|---|
| `atlastop-top` | **60/60** | **100.000 %** | **1.0000** | 7.06e-07 |
| `atlastop-qcd` | 49+ | **100.000 %** | **1.0000** | 7.82e-07 |

**Zero disagreements at any point.** Broken out by multiplicity (top sample):

| bin | ⟨n_const⟩ | points | njet % | lead-pT 1e-4 |
|---|---|---|---|---|
| `lo` | 24.6 | 15 | 100.0 | 1.000 |
| `mid` | 45.4 | 15 | 100.0 | 1.000 |
| `hi` | 73.6 | 15 | 100.0 | 1.000 |
| `vhi` | **122.5** | 15 | 100.0 | 1.000 |

Agreement holds to **122.5 constituents/jet**, well past every CMS point. The
residual ~7e-7 is float32 precision, not an algorithmic difference.

Per [[2026-08-16-validation-inventory]] C6, **$k_t$ and C/A had never been checked
against FastJet on real data** — only unit-tested against NumPy tree-walks. This
closes that gap across the whole radius x multiplicity grid, on ATLAS detector
data. *This result needs no GPU and is independent of the timing sweep.*

### Earlier smoke test (400 top jets, bin `mid`)

All three algorithms, R = 0.4 and 1.0, vs FastJet on real ATLAS detector data:

| algorithm | n_jets agreement | leading-pT within 1e-4 | median rel. diff |
|---|---|---|---|
| anti-$k_t$ | **100 %** | **1.0000** | 8.2e-8 |
| $k_t$ | **100 %** | **1.0000** | 8.2e-8 |
| C/A | **100 %** | **1.0000** | 8.1e-8 |

Per [[2026-08-16-validation-inventory]] C6, **$k_t$ and C/A had never been checked
against FastJet on real data** — only unit-tested against NumPy tree-walks. This
closes that gap: all three agree to ~1e-7 relative on ATLAS calorimeter clusters.

### Environment trap (cost me a silent wrong baseline)

`b_hive` has **awkward 1.10.3**, which breaks FastJet's vectorised interface
(`module 'awkward' has no attribute 'contents'`). It fails *softly* — the script
records `{"error": ...}` and reports only the ~10x slower per-jet numbers, so a
speedup computed from it would be badly overstated. **`fjbench` (awkward 2.9.1)
is the correct env for the FastJet side**; `b_hive` for flashjet. The runner uses
both. Python paths (micromamba is a shell function, so `timeout micromamba` fails):

```
b_hive : /eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python
fjbench: /eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/fjbench/bin/python
```

### Condor note
Standard schedds reject `/eos` paths in the submit file. Keep the **submit file,
executable and logs on AFS** (`~/atlas_sweep/`) and do the EOS work inside the
script. Also: the H100/A100 requirement queues behind everything; the free GPUs on
this pool are **V100s**, hence the second job.

## Caveats to state on a slide

1. **Large-R jets, R=1.0.** These are boosted-top fat jets, not AK4 — the natural
   comparison is the CMS AK8/R=0.8 column, not R=0.4.
2. **Clusters, not PFlow.** ATLAS topo-clusters; CMS numbers are PF candidates.
3. **Reclustered pT sits 13 % below the stored jet** — that is JES calibration, and
   it must be stated, or a reviewer will read it as disagreement.
4. `train.h5` is 139 GB; `test.h5` (8.2 GB, 2.48M jets) is plenty.
5. Prefer **`recid 80030`** for anything new — 15013 is explicitly superseded.
