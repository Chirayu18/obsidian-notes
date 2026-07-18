---
tags: [reference]
status: active
date: 2026-07-17
source: lxplus
---

# Speaker notes — flashjet-substructure deck (35 pages)

One entry per slide: what it shows, how it was made, the line to say. Deep-dive
companions: [[2026-07-17-plots-explained]] (theory + method per plot),
[[2026-07-17-msd-outlier-anatomy]] (slide 19 in full), [[2026-07-13-cms-validation]].

1. **Title** — kt/C-A substructure on the merge history; branch `benchmarking`, commit `2e912ef`; every claim closed against an independent reference; all plots regenerable.
2. **Summary / validation ladder** — three features = pure-torch post-reads of the merge history (no kernel changes, CPU/CUDA identical). Ladder: unit tests (85 vs NumPy tree-walks) → paper closures → real CMS QCD (pt 1.000000, m_SD −0.004, R_g 99.2%<0.01) → 2× ttbar → full-event → physics regimes. Line: *flashjet reproduces CMS's FastJet reconstruction to NanoAOD storage precision; the ~4% m_SD tail is fully attributed.*
3. **Where this sits** — flashjet = generalized-kt on padded (B,N,4) torch tensors; the key object is the merge history (hist_p1, hist_p2, hist_child, hist_d) = the full binary clustering tree. Our contribution = read that tree.
4. **Pre-existing vs added** — credit boundary with Alex: kernels/history/decoders his; F1/F2/F3 + helpers + API + tests ours; the `_ref_*` NumPy walkers are ours, used only to pin the fast paths.
5. **The three features** — feature ↔ function ↔ defining paper table; one-liners: F1 undo last merges; F2 walk harder branch until z > z_cut(ΔR/R)^β; F3 emit (z, ΔR, kt, ln1/ΔR, ln kt, d) per primary split.
6. **Divider** — honesty flag: flashjet has no generator; all toys are in the plot scripts, outside the repo.
7. **Toy generators (A)** — 1500 QCD-like (hard core 92% pt + soft spray, massive pions) + 1500 W-like (pair mass forced to 80.4, z∈[0.30,0.45]) at pt≈500, R=0.8. Known truth ⇒ failures would be real bugs.
8. **Toy shower (B)** — emissions sampled *uniformly in the Lund triangle*, ᾱ=0.25/unit area, 1 TeV spine — the exact LL approximation the papers derive their formulas in ⇒ closures are quantitative. Also the ghost construction.
9. **Divider: Correctness** — input legend (A) toys, (B) shower, (C) real CMS; seed 20260713.
10. **Jet areas (B)** — anti-kt Fig. 1: hard particles + 3200 ghosts; anti-kt circles vs kt/C-A ragged. Clustering orderings right before substructure.
11. **F1 (A)** — √d12 ≈ min(pt1,pt2)ΔR: W ~65 GeV, QCD low; exclusive-2 z recovers the *generated* [0.30,0.45] plateau.
12. **F2 z_g (B)** — p(z_g) = (1/z_g)/ln(1/2z_cut), no fit; lying on the exact answer is unambiguous. 72% tagged.
13. **F2 β-ordering (B)** — z_cut(ΔR/R)^β: β=0 angle-blind (mMDT, hardest), larger β spares collinear ⇒ strict curve ordering (SD Figs. 3–4).
14. **F3 Lund (A)** — QCD triangle + W island at the analytic ★: ΔR = m/(pt√(z(1−z))) ≈ 0.33, kt = z·pt·ΔR ≈ 62 ⇒ (1.1, 4.1). Pure kinematics.
15. **Divider: real CMS (C).**
16. **Pipeline** — JMENano (only format with PFCand+FatJetPFCand); three proven facts: constituents already PUPPI-weighted (titles); stored values JEC-corrected (raw = pt×(1−rawFactor); msoftdrop ≡ m(corr sub1+sub2) at +0.0002 GeV); SD declusters the big-R C/A reclustering, not the anti-kt tree. O(N³) ⇒ exact chunking.
17. **CMS (1)** — our pt vs raw: 1.000000, σ 2.5e-4 (= storage). The ~6% vs stored pt is the JEC, nothing else.
18. **CMS (2)** — m_SD diagonal −0.004 GeV, 95.6%<0.5, z_g 7e-5; wrong-tree contrast −1.37 GeV. Two stacked artefacts removed: JEC (reference side) + wrong tree (ours).
19. **CMS (2b)** — outlier anatomy: core = storage rounding (half-ulp jitter reproduces it); one-sided tail = soft candidates missing from the table (~0.1 GeV floor; δm² ≈ pt·pt_lost·ΔR²); rate rises with mass only because 0.5 GeV is absolute — relative ~0.1% everywhere; shares 50/23/20/7%. NanoAOD property, not algorithm error.
20. **CMS (3)** — Lund plane of 60k real jets; full 1807.04758 morphology, no reference needed.
21. **CMS (4)** — full-event clustering: all PFCands → anti-kt → ΔR-match to stored AK8: 100% pt within 2%, ΔR med 0.0019. Finds FastJet's jets a priori.
22. **Divider: ttbar** — stored-branch comparison (never a FastJet re-run); TTTo2L2Nu is dileptonic ⇒ b-jets + ISR, no hadronic tops.
23. **ttbar exact** — 12 561 leading jets: pt 1.000002, m_SD −0.041 (94.2%<0.5). Not QCD-specific.
24. **ttbar Lund** — enhancement from composition (b-jets), explicitly not decays.
25. **ttbar substructure** — √d12 w/ m_W/m_t marks; our z_g vs raw subjet z |Δ|=1.6e-4 (F2 vs FastJet's own output); stored τ ratios as context only.
26. **Divider: three samples** — adds Run 3 2024 TTto4Q (13.6 TeV, JMENanoV15) — first sample with real boosted W/top; shared selection, condor 9099026.
27. **Lund comparison + ratio** — emissions/jet/area; top island at ln kt≈3.5–4.5 wide-angle (= slide-14 formulas with m_W/m_t), >2× QCD in ratio; bulk of plane universal.
28. **Spectra** — our m_SD: 4q peaks at m_W + m_t shoulder; 2ℓ2ν broad b-hump; QCD falls. z_g flatter for ttbar; √d12 bump at decay scale. Line: *our grooming reconstructs masses.*
29. **R_g exact match** — our split angle vs stored ΔR(sub1,sub2) (the subjets ARE the passing split's prongs): Δ ≤ 2e-4; 99.2/95.9/87.0% <0.01. Run 3 = slide-19 mechanism at 2024-pileup dose (90% pt<1, 99% Δm<0, rel. 0.14%).
30. **β-family on data** — slide 13 redone on 164k real jets by re-reading the same histories (no re-clustering — the design point).
31. **Backup divider.**
32. **Outlook: tagger inputs** — 18 history-derived variables (kT scales + C/A groom + Lund
    summaries), TTto4Q vs pt-reweighted QCD, weighted logistic. Mass-scale vars saturate at
    0.794 (0.8–0.97 correlated); adding the declustering *sequence* → 0.827, ~2× rejection at
    30% eff. Sleeper: n_drop 0.764 alone; ln kt^(2) sees the 2nd decay splitting. Exploratory
    (no gen-match, linear, cross-era) — the point: this input vector is free once the history
    exists. Line: *the history isn't just for validation — it's the tagger input.*
    See [[2026-07-18-tagger-inputs]]. Condor 9128460.
33. **Reproducibility table** — every headline number + condor ID + jet count.
34. **Function reference** — added API surface.
35. **Reproducing everything** — commands, condor pattern (AFS submit dir), seed, papers catalogue.
