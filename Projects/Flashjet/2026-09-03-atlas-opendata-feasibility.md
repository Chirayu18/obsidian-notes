---
tags: [reference]
status: active
date: 2026-09-03
source: lxplus
---

# Can the flashjet benchmark be repeated on ATLAS Open Data? — Yes, via the OmniFold release

Question: reproduce [[flashjet-benchmark-status]] (4-process CMS Open Data sweep,
flashjet vs FastJet) using **ATLAS** Open Data instead.

**Answer: yes — but NOT from PHYSLITE.** PHYSLITE ships no constituents (verified
below). The usable dataset is the **ATLAS OmniFold release** (`atlas-160005`),
which publishes per-event charged-particle four-vectors. Verified by reading it.

**Correction:** an earlier version of this note concluded "not possible". That was
based on PHYSLITE alone and was wrong — it missed the datascience records, whose
recids are namespaced (`atlas-160005`) and so were skipped by a numeric-recid scan.

Related: [[2026-08-16-validation-inventory]], [[presentation/flashjet-benchmark-status]].

---

## Why the benchmark needs constituents

The pipeline's only experiment-specific stage is stage 1,
`dump_opendata_constituents.py` (FWLite), which emits

```
opendata_constit_<tag>_ak4.npz :  p4 (Njet, NMAX, 4) float32, ncon int32, raw_pt float32
```

Everything downstream is experiment-agnostic and consumes only that npz:
`bench_opendata_flashjet.py` -> `bench_<tag>_R<R>.npy` (ragged, for FastJet) ->
`bench_opendata_fastjet.py` -> plots. **Reclustering per-jet four-vectors is the
whole measurement**; per-jet summary kinematics are useless for it.

## What ATLAS actually publishes

### 1. DAOD_PHYSLITE (2024 "Open Data for Research", 2015-16, 36 fb-1)

Checked file (60 000 events, read fine over the open `eospublic` redirector,
no proxy — same access model as the CMS files):

```
root://eospublic.cern.ch//eos/opendata/atlas/rucio/mc20_13TeV/DAOD_PHYSLITE.38191664._000001.pool.root.1
```

Branch scan of `CollectionTree`:

| looked for | found |
|---|---|
| `CaloCalTopoClusters` | **0 branches** |
| `FlowElement` / PFO containers | **0 branches** |
| `TruthParticles` (general stable-particle container) | **absent** |
| UFO / large-R jet containers | present (`AntiKt10UFOCSSKJets`, `AnalysisLargeRJets`) |
| `constituentLinks` on those jets | **present but dangling** |
| `InDetTrackParticles` | present but **thinned to ~4.1 tracks/event** |

The constituent links are *structurally intact but unresolvable*:

- `AntiKt10UFOCSSKJetsAux.constituentLinks` -> `m_persKey` = **1036585512**
  (a single non-zero key, i.e. a real container), `m_persIndex` 0-235,
  **22.5 constituents/jet** mean, max 76.
- No container in the file matches that key — the top-level container list has no
  PFO/UFO/topocluster collection at all.
- Truth jets (`AntiKt4TruthDressedWZJets`) link to key 662974859, also absent.

So the file *describes* jets of ~22 constituents each and then does not ship the
four-vectors. ATLAS confirms this is deliberate, not corruption:

> "we don't store jet constituents in PHYSLITE, so any time you see a link to a
> jet constituent it is almost certainly going to be invalid."
> — ATLAS reply, [opendata-forum thread 351](https://opendata-forum.cern.ch/t/empty-elementlinks-in-atlas-physlite-open-data/351)

PHYSLITE by design keeps calibrated **objects** and high-level discriminants, not
jet-finding **inputs**.

`InDetTrackParticles` at 4.1/event is thinned to lepton/b-tagging use — it is not a
usable charged-constituent proxy (a real jet has O(10-30) constituents).

### 2. The 2020 educational 13 TeV release

Flat ntuple, ~80 branches: `jet_n, jet_pt, jet_eta, jet_phi, jet_e` only.
Per-jet summary kinematics, no constituent level. Also unusable.

---

## 3. ATLAS OmniFold release (`atlas-160005`) — **THIS ONE WORKS**

"ATLAS OmniFold Full Charged Particle Phase Space Open Data" — the unbinned
Z(mumu)+jets full-phase-space measurement, STDM-2024-02. Parquet, 1 035 835 events,
54 GiB, CC0, on the same open `eospublic` redirector.

```
root://eospublic.cern.ch:1094//eos/opendata/atlas/datascience/STDM-2024-02/measurement/data.parquet
root://eospublic.cern.ch:1094//eos/opendata/atlas/datascience/STDM-2024-02/mc_predictions/truth_sherpa.parquet
root://eospublic.cern.ch:1094//eos/opendata/atlas/datascience/STDM-2024-02/mc_predictions/truth_madgraph.parquet
```

Readable with `fsspec.open(url).open()` + `pyarrow.parquet.ParquetFile` (streams the
footer + one row group; no need to pull the whole 1.7 GB). Works in `b_hive`.

**The columns that matter** (variable-length, one entry per particle):

| column | content |
|---|---|
| `truth_pT_particles` | per-particle pT |
| `truth_eta_particles` | per-particle eta |
| `truth_phi_particles` | per-particle phi |
| `truth_pdgId_particles` | PDG id (-> mass for the 4-vector) |
| `truth_trackJetIndex_particles` | **which R=0.4 track jet each particle belongs to**, -1 = unassociated |

Measured on row group 0 (3000 events):

- **55.2 particles/event** mean, max 181 — fully populated, real values.
- 71 261 track jets; **2.2 constituents/jet** mean, median 1, max 46; 39 % have >=2.

The *track jets* are thin because they are charged-only R=0.4 jets — but that is
irrelevant for the benchmark: you cluster **the event's ~55 particles**, which is
the event-regime path (C5 in [[2026-08-16-validation-inventory]]), and
`trackJetIndex` then serves as an independent cross-check of the clustering.

### Caveats to state honestly on a slide

1. **Particle level, not detector level.** These are unfolded/truth charged
   particles, not calorimeter constituents. It is a legitimate *clustering input*
   and legitimately ATLAS-published, but it is not "ATLAS reconstructed jets".
2. **Charged only.** No neutrals, so multiplicity is roughly half a full jet's and
   sits below the CMS points (10.8-34 const/jet) rather than extending them.
3. **Event regime, O(N^2).** ~55 particles/event is the regime where flashjet is
   weakest (per [[2026-08-16-validation-inventory]] B5, throughput falls to
   ~1.1 Mpart/s). Expect a much smaller speedup than the 65-97x jet-regime headline
   — this is a *coverage* point, not a second headline.
4. `data.parquet` carries ~164 OmniFold weight columns; ignore them for timing.

## Consequence for the deck

The CMS Open Data sweep cannot be mirrored on ATLAS **reconstructed** jets — no
public ATLAS dataset ships calorimeter/PFO constituents. But an ATLAS point is
available at **particle level** via OmniFold, on public CC0 data with no approval.

Ranked options:

1. **OmniFold event-regime point** (recommended if an ATLAS slide is wanted).
   Real ATLAS-published data, no approval, and it closes C5 (event regime) at the
   same time. Frame it as *"ATLAS-published charged-particle events, clustered as
   full events"* — never as "ATLAS jets". Expect a modest speedup, not 80x.
2. **Do nothing on ATLAS; close C1 instead** (the C++ FastJet baseline). Per
   [[2026-08-16-validation-inventory]] that is still the single highest-value
   missing test, and it removes the "could be Python overhead" caveat that
   currently qualifies *every* number in the deck.
3. Truth/generator particles from other public MC — clusters fine but is Pythia or
   Sherpa output, not an ATLAS measurement.

My recommendation is **2 before 1**: the C++ baseline strengthens numbers already
in the deck, whereas the ATLAS point adds breadth in the regime where flashjet
looks weakest. Do 1 only if cross-experiment coverage is specifically asked for.

## Verification log

Everything above was checked against the actual files on lxplus (`b_hive`, uproot
4.3.7 / pyarrow+fsspec), not from documentation:

- PHYSLITE branch scan -> 0 topocluster/PFO branches; `constituentLinks` persKey
  1036585512 with no matching container; `InDetTrackParticles` 4.1/event.
- OmniFold schema + row group 0 -> 55.2 particles/event, jet indices populated.
- **Method note:** the first pass missed OmniFold because the CERN Open Data API
  returns namespaced recids (`atlas-160005`) alongside numeric ones, and a
  numeric-only filter silently dropped the entire `datascience` family. When
  surveying a portal for "does X exist", enumerate *all* records and inspect the
  ones that fail the expected id format rather than discarding them.
