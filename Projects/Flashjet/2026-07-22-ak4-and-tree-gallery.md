---
tags: [reference]
status: active
date: 2026-07-22
source: lxplus
---

# AK4 from MINIAOD + a gallery of merge trees (and an AUC tie-bug fix)

Three things: (1) more merge-tree examples on AK8, (2) the same machinery on **AK4**
jets built from **MINIAOD** constituents with real flavour truth, (3) a **correction**
to some published AUCs. Companions: [[2026-07-22-full-merge-history]],
[[2026-07-18-tagger-inputs]].

## Why MINIAOD was needed for AK4

The JMENano files have AK4 `Jet_*` kinematics **and** `Jet_hadronFlavour`, but **no
PF-candidate→AK4 linker** — the only linker is `FatJetPFCand_*` (AK8). So AK4
constituents (and therefore AK4 merge trees) are impossible from those files.

Solution: go to **MINIAOD**, where `slimmedJets` carry their `packedPFCandidates` as
daughters. Datasets (found via DAS with a VOMS proxy):
- signal: `/TTto4Q-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-.../MINIAODSIM`
- background: `/QCD_PT-470to600_TuneCP5_13p6TeV_pythia8/Run3Summer22MiniAODv4-.../MINIAODSIM`

**Two-stage pipeline** (the two pythons are ABI-incompatible — CMSSW is 3.9, `b_hive`
is 3.11, so they cannot share a process):
1. `dump_ak4_constituents.py` — FWLite in `CMSSW_14_1_0_pre4`: read `slimmedJets`,
   their PF daughters, and `hadronFlavour` → `ak4_constit_{tag}.npz` (no torch).
2. `ak4_substructure.py` — `b_hive` env: flashjet C/A + kT + soft-drop + Lund on those
   constituents → `ak4_vars_{tag}.npz` (18 vars + flavour).

Yield: **12 000 AK4 jets each** for ttbar (3552 b, 1855 c, 6593 udsg) and QCD.

## AUC tie bug — CORRECTION to earlier numbers

The AUC routine sorted values and integrated the ROC **without handling ties**. For
discrete count variables (where >80% of jets share one value) this splits tied jets
arbitrarily and **manufactures separation**. Caught because AK4 `n(k_t>5)` scored 0.773
while b and light had *identical means* in every pt slice — impossible.

Fixed by building the ROC on **unique values** (proper Mann–Whitney tie handling) in
both `tagger_allvars.py` and `ak4_allvars.py`. Continuous variables are unaffected;
the corrected AK8 numbers are:

| variable | was | **corrected** |
|---|---|---|
| $n(k_t>1)$ | 0.593 | **0.587** |
| $n(k_t>5)$ | 0.691 | **0.663** |
| $n_{drop}$ | 0.765 | **0.769** |
| $f_{match}$ | 0.516 | **0.648** |
| $n_{Lund}$, $n_{const}$ | 0.602 | 0.602 (unchanged) |

All mass/geometry variables (msd 0.782, √d12 0.792, R_g 0.779, f_groom 0.747 …) are
unchanged, so the AK8 story stands: $n_{drop}$ is still the best non-mass variable.
$f_{match}$ was substantially **understated** before.

## AK4 result: the history does NOT do flavour tagging

b vs light (udsg), pt-reweighted, MINIAOD AK4 jets — **every variable lands at 0.50–0.59**:

| best AK4 variables | AUC |
|---|---|
| $z$ of hardest emission | 0.591 |
| $\sqrt{d_{12}}$ | 0.588 |
| $k_{t,g}$ | 0.585 |
| $\ln k_t^{(2)}$, $n_{Lund}$, $n_{const}$ | ~0.578 |
| $m_{SD}$ | 0.573 |
| $n(k_t>5)$, $f_{32}$ | ~0.51 (nothing) |

This is the expected — and important — answer. **b vs light is a lifetime question**
(displaced tracks, secondary vertices); none of that is in a purely kinematic merge
tree. The residual ~0.55–0.59 is just the mild mass/multiplicity difference of a b hadron.

**Direct consequence for the b-hive/UParT discussion** ([[2026-07-18-history-tagger-design]]):
history inputs are worth real information for **boosted 2-/3-prong tagging**
(AK8: 0.78–0.79 mass-scale, 0.827 combined) and **essentially nothing for AK4 flavour
tagging** (~0.55). So history tokens should be pitched at fat-jet/boosted taggers, not
as a DeepJet/UParT b-tagging input — quantitatively confirming the earlier argument
that UParT's IP/SV lifetime inputs carry information no clustering tree contains.

The AK4 tree figure (`ak4_tree.png`) shows this visually: a b jet and a light jet at the
same $p_T$ have near-identical trees (both $m_{SD}\approx13.5$, similar depth/shape).

## Tree gallery (AK8)

| figure | jet | numbers | what it shows |
|---|---|---|---|
| `tree_qcd.png` | QCD | 23 const, $p_T$ 331, m_ung 33 → **m_SD 1.2**, $n_{drop}$ **13** | The QCD signature: green spine is a long **staircase** dropping soft prong after soft prong, mass collapses. Why $n_{drop}$ discriminates. |
| `tree_top.png` | clean top | 32 const, $p_T$ 529, m_ung 156 → **m_SD 155**, $n_{drop}$ **1** | Grooming barely has to work; ★ sits at the top on a wide balanced split. The counterpart to the misfiring top. |
| `tree_boosted.png` | boosted | 35 const, $p_T$ 629, m_SD 74, $R_g$ 0.26 | Collimated regime — decay angle shrinks, tree compresses. |
| `tree_bjet.png` | b jet | 26 const, $p_T$ 403, m_ung 40 → m_SD 13, $n_{drop}$ 8 | Single hard core; no balanced hard split (cf. the AK4 flavour result). |

## Reproduce
In `/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`:
`tree_gallery.py <qcd|top|boosted|bjet>`, `ak4_tree.py`, `ak4_allvars.py`,
`ak4_substructure.py`; and in `~/CMSSW_14_1_0_pre4/src/`: `dump_ak4_constituents.py`
(needs `cmsenv` + `voms-proxy-init -voms cms`). Plot links in [[plots]].
