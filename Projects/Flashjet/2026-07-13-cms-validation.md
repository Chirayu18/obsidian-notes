---
tags: [reference]
status: active
date: 2026-07-13
source: lxplus
---

# flashjet validated on REAL CMS simulated data

The toy plots ([[2026-07-13-substructure-plots]]) prove the substructure code is
self-consistent. This note is the stronger claim: **our GPU clustering + F1/F2/F3
run on real CMS PF candidates and reproduce CMS's own reconstruction.**

## The data

- Dataset: `/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/RunIISummer20UL18NanoAODv15-20UL18JMENano_150X_mc2018_realistic_v1-v3/NANOAODSIM`
- Found via DAS (`dasgoclient`), copied with `xrdcp` → `/eos/home-c/cgupta/flashjet/data/qcd_jmenano_150x.root` (1.7 GB).
- **Why JMENano specifically:** ordinary NanoAOD only has jet-level branches. The 150X
  JMENano reprocessing carries the `PFCand` table (per-event particle-flow candidates)
  and `FatJetPFCand` (the index map linking each AK8 jet to its constituents). Without
  those two, there is nothing to re-cluster — the first file I pulled (106X UL18 v1)
  had no PF candidates and was useless for this.

## The pipeline (`make_cms_plots.py`)

1. For each AK8 FatJet with pt>300, |η|<2.4, read its constituents via
   `FatJetPFCand_jetIdx == j → pfCandIdx → PFCand_{pt,eta,phi,mass}`.
2. Build each constituent 4-vector: `px=pt·cosφ, py=pt·sinφ, pz=pt·sinhη,
   E=√(px²+py²+pz²+m²)`.
3. Pad into a `(Njets, Nmax, 4)` torch tensor + mask and call
   `cluster(p4, mask, R=0.8, algorithm="antikt")` — **CMS AK8 is exactly anti-kt R=0.8** — for the
   jet pt; **plus a big-R `cambridge` reclustering** of the same constituents for grooming/Lund
   (FastJet SoftDrop declusters a C/A tree; the primary Lund plane is defined on C/A too).
4. Take the leading jet, groom with `groomed_jets(z_cut=0.1, β=0)` — **exactly CMS's
   `FatJet_msoftdrop` definition** — and read its Lund coordinates.
5. Chunked at 3000 jets with per-chunk padding trim (the O(N³) torch backend OOMs on
   60k×128 otherwise).

## Results

| plot | what it shows | verdict |
|------|---------------|---------|
| `cms_recluster.png` | our reclustered pt vs raw `FatJet_pt` | **exact**, median ratio 0.999999 |
| `cms_softdrop.png` | our C/A-tree soft-drop mass vs raw subjet mass | **exact**, median Δ=−0.004 GeV |
| `cms_exact_match.png` | pt + m_SD + tree, raw-to-raw, side by side | the decisive figure |
| `cms_lund.png` | primary Lund plane of 60285 real jets | full arXiv:1807.04758 structure |

The clustering closes exactly: raw-to-raw, our anti-kt pt equals CMS's AK8 pt to float precision,
and (declustering the C/A tree) our soft-drop mass equals the raw subjet-pair mass to a few MeV.

## CORRECTION (2026-07-15): the offset was **JEC + wrong tree, NOT PUPPI**

The earlier "PUPPI" explanation on this page was **wrong**, overturned by the file's own
branch titles and a raw-to-raw test (`exact_match.py` / `exact_match2.py`):

- **`PFCand_pt` / `PFCand_mass` titles literally read "Puppi-weighted pt / mass"** — the
  constituents we cluster are **already PUPPI-weighted**. There is no missing weight; the
  weighted 4-vectors are stored directly (which is *why* there's no per-candidate weight branch).
- **`FatJet_pt` / `FatJet_msoftdrop` are JEC-corrected.** Raw jet = `FatJet_pt·(1−rawFactor)`;
  `FatJet_msoftdrop` = m(sub₁+sub₂) with **subjet JECs** applied. Proven from the data:
  `m(corr sub1+sub2) − stored msoftdrop = +0.0002 GeV` (MAD 0.02); the raw subjet sum is −2.2 GeV off.

So the apparent ~6% pt / ~4 GeV mass offsets were **jet energy corrections**, plus one bug on
our side: we groomed the **anti-kt** merge tree, whereas FastJet SoftDrop declusters a **C/A**
reclustering. Fixing both closes it:

```
pt   (our / raw FatJet_pt)          : median 0.999999 , std 2.1e-4
m_SD (our C/A-tree / m(raw subjets)): median -0.004 GeV , 95.6% within 0.5 GeV , 93% within 1%
z_g  (our / raw subjet z)           : median |Δ| = 6.9e-5
   [contrast — grooming the anti-kt tree (the old bug): median -1.37 GeV]
```

The residual is **NanoAOD float storage precision**, nothing physical. `make_cms_plots.py`
now clusters anti-kt R=0.8 for the jet and a big-R **C/A** reclustering of the same
constituents for soft-drop / Lund.

## Bottom line

Our clustering and substructure, written against a toy validation ladder, drop onto real CMS
detector-level data and reproduce CMS's own AK8 reconstruction **exactly** — pt to 10⁻⁶, soft-drop
mass to a few MeV, z_g to 10⁻⁵ — once the comparison is made raw-to-raw on the matching (C/A)
tree. The Lund plane needs no comparison at all — a clean, publication-quality primary Lund plane
of 60k real QCD jets produced entirely by our F3.
