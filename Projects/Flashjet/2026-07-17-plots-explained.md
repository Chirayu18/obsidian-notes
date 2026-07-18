---
tags: [reference]
status: active
date: 2026-07-17
source: lxplus
---

# Every flashjet plot, explained — inputs, method, and the theory behind each

Companion to the deck (`presentation/flashjet-substructure.md`, 34 pages) and
[[plots.md]]. All scripts live in `/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`.

## 0. The framework everything rests on

flashjet clusters padded `(B,N,4)` torch tensors with generalized-kt
($d_{ij}=\min(k_{t,i}^{2p},k_{t,j}^{2p})\,\Delta R_{ij}^2/R^2$; $p=-1$ anti-kt, $0$ C/A, $+1$ kt).
The kernels record the **merge history** — four arrays `(hist_p1, hist_p2, hist_child, hist_d)`,
one row per recombination. That history *is* the full binary clustering tree, so jet substructure
never needs new kernels: F1 (exclusive jets), F2 (soft-drop grooming) and F3 (Lund coordinates)
are pure-torch *reads* of the tree.

The validation philosophy: each feature is pinned to (a) an independent NumPy tree-walk,
(b) an analytic QCD prediction it must land on, and (c) CMS's own stored FastJet output on
real events. Three input classes appear below: **(A)** ad-hoc toys, **(B)** a leading-log toy
shower, **(C)** real CMS PF candidates.

## 1. The Lund plane, from scratch

Take one jet. **Recluster its constituents with Cambridge/Aachen** — C/A merges the two
closest-in-angle objects first, so the resulting tree is *angular-ordered*: reading it from the
root downward, you meet the widest-angle structure first, exactly mirroring how QCD radiation
is ordered. Now **decluster**: at the root the jet splits into a harder branch and a softer
branch; call the softer one an *emission*, step into the harder branch, repeat. The sequence of
emissions off the hard core is the **primary declustering sequence**. For each emission record

- $\Delta R$ — the angle between the two branches,
- $k_t = p_T^{\rm soft}\,\Delta R$ — the emission's transverse momentum w.r.t. the core,
- $z = p_T^{\rm soft}/(p_T^{\rm soft}+p_T^{\rm hard})$ — the momentum fraction.

Plot every emission of every jet at $(\ln 1/\Delta R,\ \ln k_t)$: that 2-D histogram is the
**primary Lund plane** (Dreyer–Salam–Soyez, arXiv:1807.04758).

**Why these axes:** to leading order, the probability of one soft-collinear gluon emission is

$$dP \;=\; \frac{2\,\alpha_s(k_t)\,C_i}{\pi}\;\frac{d\theta}{\theta}\,\frac{dk_t}{k_t}
\;=\; \bar\alpha \; d\ln(1/\theta)\; d\ln k_t .$$

The two logarithms are *flat* directions: QCD radiation fills the plane with **uniform density**
$\bar\alpha = 2\alpha_s C_i/\pi$ (exactly uniform for fixed coupling; with running coupling the
density rises slowly toward small $k_t$). The plane is bounded by a triangle:

- **right/diagonal edge** — kinematics: $z\le 1/2$ means $k_t \le (p_T/2)\,\theta$, i.e.
  $\ln k_t \le \ln(p_T/2) - \ln(1/\theta)$ — the hypotenuse;
- **left edge** — $\theta \le R$: wider-angle emissions aren't in the jet;
- **bottom** — $k_t \sim \Lambda_{\rm QCD}$ (~1 GeV): below this, hadronization, not
  perturbative radiation.

**Where a heavy 2-body decay sits.** A W/top decay is *not* soft-collinear — it's one hard
splitting at a fixed mass. Small-angle 2-body kinematics give

$$m^2 = z(1-z)\,p_T^2\,\Delta R^2 \quad\Rightarrow\quad
\Delta R = \frac{m}{p_T\sqrt{z(1-z)}},\qquad
k_t = z\,p_T\,\Delta R = m\sqrt{\tfrac{z}{1-z}} .$$

So a resonance deposits an **isolated island** at a predictable spot: for the W-like toys
($m=80.4$, $p_T\!\approx\!500$, generated $z\in[0.30,0.45]$, $\bar z\!\approx\!0.375$):
$\Delta R = 80.4/(500\times0.484) \approx 0.33 \Rightarrow \ln(1/\Delta R)\approx 1.1$, and
$k_t \approx 0.375\times500\times0.33 \approx 62$ GeV $\Rightarrow \ln k_t \approx 4.1$. That is
the red ★ on `lund_plane.png` — pure kinematics, no tuning. For hadronic tops the same formulas
with $m_W$ (variable $z$) and $m_t$ put the enhancement at $\ln k_t \approx 3.5{-}4.5$,
$\ln(1/\Delta R)\lesssim 1$ — exactly where the blob appears in `compare_lund.png`.

## 2. Toy justification plots — input (A), `make_plots.py`

The toys: 1500 "QCD-like" jets (one hard collinear core carrying 92% of $p_T$,
$\sigma_{y,\phi}=0.06$, plus wide-angle soft spray) and 1500 "W-like" jets (two prongs with
pair mass forced to 80.4 GeV, $z\in[0.30,0.45]$, 6% soft contamination), each a bag of massive
pions, $p_T\approx500$, $R=0.8$, seed 20260713. The point of toys with a *known* truth: any
observable that fails to separate them, or misses the analytic position, is a real bug.

- **`kt_observables.png` (F1):** left, $\sqrt{d_{12}}$ — the kt-algorithm splitting scale of the
  last merge, $\sqrt{d_{12}}\simeq \min(p_{T1},p_{T2})\Delta R = k_t$ of the hardest split. For
  a mass-$m$ decay this is $m\sqrt{z/(1-z)}$ ~ tens of GeV (W-like peaks ~65 GeV), while QCD,
  having no intrinsic scale, Sudakov-piles at small values (~25 GeV). Right: exclusive
  $n=2$ kt-subjet momentum fraction $z$ — W-like reproduces the *generated* $z$ plateau
  [0.30,0.45] (a closure on the generator input); QCD is soft-lopsided.
- **`softdrop_mass.png` (F2):** leading-jet mass before/after soft drop
  ($z_{\rm cut}=0.1,\beta=0$). QCD mass (all from soft wide-angle spray) collapses 70→38 GeV;
  W mass survives at 80.4 (the prongs are hard: SD keeps them). Grooming = "remove soft
  wide-angle, keep hard structure" demonstrated in one figure.
- **`lund_plane.png` (F3):** QCD toy fills the triangle smoothly; W toy = same background
  **plus** the island at the ★ computed above.
- **`parity_timing.png`:** groomed mass vs an independent single-event NumPy declustering:
  max |diff| = 1.7×10⁻¹³ GeV (f64 roundoff ⇒ implementations are *identical*, not merely
  similar); decoders cost 10–100× less CPU than clustering.

## 3. Paper-figure closures — input (B), `make_paper_plots.py`

The generator here is a **primary, fixed-coupling, leading-log toy shower**: emissions are
sampled *uniformly* in the Lund triangle with density $\bar\alpha=0.25$ per unit area
($u=\ln 1/\theta$, $v=\ln k_t$, keep $z\le 1/2$, $k_t>k_t^{\min}$), each mapped to a physical
4-vector at angle $\theta$ around a 1 TeV spine. This is *the same approximation the papers'
analytic predictions are derived in* — which is what makes these closures quantitative.

- **`jet_areas.png`** (anti-kt paper 0802.1189 Fig. 1): one event with 10 hard particles +
  ~3200 uniform **ghosts** ($p_T=10^{-8}$); cluster at $R=1$ with $p=+1/0/-1$ and colour each
  ghost by the jet that absorbed it. Anti-kt distance to a hard particle is
  $\sim k_{t,\rm hard}^{-2}\Delta R^2$ (small), while soft–soft distances are huge — so hard jets
  accrete ghosts radially outward and give **perfect circles**; kt does the opposite (soft pairs
  merge first) giving ragged areas. This is the figure that made anti-kt the LHC default, and it
  comes out of flashjet's own clustering.
- **`lund_triangle.png`** (Lund paper Fig. 2): the shower's input density is flat at 0.25 *by
  construction*, so F3 must return a flat interior — measured 0.17±0.02, flat to ~12%, edges in
  the right places; the offset below 0.25 is genuine wide-angle reclustering migration (present
  in the paper too), not a decoding error.
- **`zg_distribution.png`** (Soft Drop 1402.2657): at leading log, the first C/A declustering
  that passes $z>z_{\rm cut}$ is distributed like the soft-enhanced splitting kernel $1/z$,
  truncated and normalized on $[z_{\rm cut}, 1/2]$:
  $$p(z_g) = \frac{1/z_g}{\ln\!\frac{1}{2 z_{\rm cut}}}\qquad(=1/(z_g\ln 5)\ \text{for }z_{\rm cut}=0.1).$$
  The black curve is that formula with **no fit**; our $z_g$ lies on it across the whole range.
  This is the decisive grooming test because the target is *the* correct answer.
- **`softdrop_rho.png`**: groomed $\rho=m^2/(p_T^2R^2)$ for $\beta=0,1,2$. The SD condition is
  $z>z_{\rm cut}(\Delta R/R)^\beta$: at $\beta=0$ the cut ignores angle (mMDT — grooms hardest);
  larger $\beta$ relaxes the cut at small angles (grooms less). Hence the strict ordering of the
  curves, matching the paper's Figs. 3–4.

## 4. Real CMS data — input (C): the methodology first

Samples are **JMENano** (the only NanoAOD flavour storing `PFCand` + the `FatJetPFCand`
jet↔constituent map). Three facts, all *proven from the files*, define the comparison:

1. **`PFCand_pt/mass` are already PUPPI-weighted** (the branch titles say so) — you cluster them
   as-is; there is no separate weight to apply.
2. **Stored jet quantities are JEC-corrected.** Raw jet $p_T$ = `FatJet_pt×(1−rawFactor)`;
   `FatJet_msoftdrop` ≡ m(JEC-corrected SubJet1+SubJet2) — shown directly from data
   (Δ = +0.0002 GeV, while the raw-subjet sum is −2.23 GeV away). So the honest comparison is
   **raw-to-raw**: our clustering vs `pt×(1−rawFactor)` and vs m(raw sub₁+sub₂).
3. **Soft drop declusters a C/A tree.** FastJet's SoftDrop *reclusters* the jet with C/A at
   large R and declusters that. Grooming our anti-kt merge tree instead biases m_SD by
   −1.37 GeV (the anti-kt tree accretes soft particles one at a time onto the core — its
   declustering sequence has no angular meaning). We therefore cluster twice: anti-kt R=0.8 for
   the jet, and one big-R (`RBIG=10`) **cambridge** pass of the same constituents for
   grooming/Lund.

Per-plot:

- **`cms_recluster.png`:** our anti-kt $p_T$ vs CMS, jet-by-jet, 60 257 QCD jets. Vs the JEC-corrected
  value there's a ~6% shift (that *is* the JEC); vs raw the ratio is **1.000000, σ=2.5×10⁻⁴** —
  pure float-storage noise. Proves constituent indexing + clustering end-to-end.
- **`cms_exact_match.png`:** (i) the $p_T$-ratio histogram (corrected vs raw reference) making the
  JEC point visually; (ii) our C/A-tree m_SD vs m(raw subjets) — diagonal, median −0.004 GeV;
  (iii) the Δm distribution on the C/A tree vs on the anti-kt tree (the wrong-tree contrast).
- **`cms_lund.png`:** F3 on 60k real QCD jets. Needs no reference curve — the point is that the
  full 1807.04758 morphology (perturbative ridge, soft plateau, three edges) emerges from
  detector-level data through our code alone.
- **`fullevent_match.png`:** the realistic path — cluster **all** PF candidates per event (no
  per-jet pre-grouping), then ΔR-match our inclusive jets to CMS's stored AK8 jets: 7 701
  matches, pt ratio 1.0000 (100% within 2%), median ΔR 0.0019. Full-event flashjet finds the
  same jets FastJet found, without knowing them a priori.

## 5. ttbar (UL18 TTTo2L2Nu — dileptonic, so b-jets + ISR, no hadronic tops)

- **`ttbar_exact.png`:** same raw-to-raw exact match on a different final state — pt 1.000002,
  m_SD −0.041 GeV. Rules out "it only works on QCD".
- **`ttbar_lund.png`:** Lund plane of 12.6k ttbar jets — the enhancement vs QCD here comes from
  jet *composition* (b-jets), since there are no hadronic decays in a 2ℓ2ν sample.
- **`ttbar_substr.png`:** our $\sqrt{d_{12}}$ (with $m_W$/$m_t$ scale marks), our $z_g$ vs CMS's
  raw-subjet $z=\min(p_{T1},p_{T2})/(p_{T1}{+}p_{T2})$ jet-by-jet (|Δ| median 1.6×10⁻⁴ — this is
  F2 closed directly against FastJet's SoftDrop *output*), and the sample's stored
  N-subjettiness ratios for context.

## 6. Three-sample comparison (`make_compare_plots.py`, + Run3 2024 TTto4Q)

- **`compare_lund.png`:** normalized Lund planes (emissions/jet/area) for QCD, dileptonic and
  fully-hadronic ttbar + the 4q/QCD **ratio**. The top-decay island appears at the position the
  Section-1 formulas predict ($\ln k_t\!\approx\!3.5{-}4.5$, wide angle), >2× QCD in the ratio.
  QCD → b-jets → boosted tops on one line, same code.
- **`compare_spectra.png`:** our m_SD (W peak + top shoulder in 4q; broad b-enriched hump in
  2ℓ2ν; falling QCD), $z_g$ (ttbar flatter than QCD's ~1/z, as hard 2-body splits must be),
  $\sqrt{d_{12}}$ (4q bump at the decay scale).
- **`compare_rg.png`:** the second jet-by-jet exact match: our groomed split angle $R_g$
  (F2's `dR`) vs stored ΔR(SubJet1,SubJet2) — the two stored subjets *are* the two prongs of the
  passing split, so this must be diagonal if the declustering is right. Median Δ ≤ 2×10⁻⁴.
- **`qcd_beta_family.png`:** the §3 β-ordering repeated on 164k **real** jets by re-grooming the
  *same* merge histories three times — possible precisely because grooming is a post-read.

## 7. `outlier_anatomy.png` — why 4.4% of jets miss by >0.5 GeV

Every input branch is mantissa-truncated (measured by counting trailing zero mantissa bits:
`PFCand_pt` ~10 bits ≈ 10⁻³ relative; `SubJet_rawFactor` ~5 bits ≈ 2%), while CMS ran FastJet at
full precision. Panel by panel: (1) signed Δm — the core is symmetric storage noise (a half-ulp
input jitter reproduces it), but there's a one-sided negative tail; (2) the fixed 0.5 GeV window
mostly selects **heavy** jets — relative agreement is ~0.1% in *every* mass bin; (3) the decisive
scatter: for the one-sided tail, our groomed $p_T$ sits below the subjet-pair $p_T$ and tracks
Δm — soft candidates are **missing from the stored table** (~0.1 GeV floor), and mass is
quadratically sensitive to a soft wide-angle loss ($\delta m^2 \approx p_T^{\rm jet}
p_T^{\rm lost}\Delta R^2$: a 0.5 GeV candidate at ΔR=0.6 in a 500 GeV jet moves m by ~0.5 GeV at
m=95 while moving $p_T$ by only 4×10⁻⁴); (4) the attribution bar: 50% missing-soft, 23% storage
rounding, 20% rounding-sensitive C/A trees, 7% genuine $z\approx z_{\rm cut}$ prong flips.
Details: [[2026-07-17-msd-outlier-anatomy]].
