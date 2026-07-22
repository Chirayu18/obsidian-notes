---
tags: [reference]
status: active
date: 2026-07-17
source: lxplus
---

# Speaker notes — flashjet-substructure deck (49 pages)

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
33. **Outlook II: functions + full history** — 13 dimensionless physics functions of the 18
    vars (grooming survival, √(z/(1−z)), closure χ<1 for massive prongs, ψ₁/ψ₂
    emission-vs-decay scale): functions-only 0.813; **mass-decorrelated set 0.797 with no
    explicit mass input** (sculpting-safe). Full history → b-hive: a history is a padded
    token sequence = the cpf/npf/vtx contract; C/A Lund list (LundNet input) + kT scales as
    new groups, tree via ParT's pairwise channel. Design only ([[2026-07-18-history-tagger-design]]).
    Line: *compress to physics functions today; feed the raw sequence tomorrow.*
34. **Which tree does each variable come from?** — provenance overview. Each jet is clustered
    3× in `extract_tagger_vars.py`: **anti-kT** R=0.8 → the jet (m_ung, n_const); **kT** →
    `splitting_scales()` value-sorted (√d12/√d23/√d34 + ratios); **C/A** big-R recluster →
    `groomed_jets`+`lund_coordinates` (m_SD/z_g/R_g/n_drop + all Lund counts/ln kt/z/dR). Two
    functions are *mixed*: fgroom=m_SD/m_ung (C/A÷anti-kT), fz=√d12/m_SD (kT÷C/A). Say: kT is
    value-sorted (prong hierarchy), C/A is angular-ordered (= the Lund/soft-drop sequence). The
    colored tags on the next 5 slides (kT red / C/A blue / anti-kT gray / mixed purple) mark the source.
35. **The full merge history of one jet** — dendrograms of ONE boosted top jet (25 const,
    pt 789, mass 135, n_drop=5). flashjet stores the complete tree (hist_p1/p2/child/d) — this
    is the FULL ungroomed history. Left C/A: green spine = groomed jet, grey = the 5 dropped soft
    prongs, star = passing split (m_SD/z_g/R_g). Right kT: value-sorted, top merges = √d12≥√d23≥….
    Say: **grooming is a pruned path through the C/A tree, not a separate tree**; answers the
    "are these groomed?" question. Made by full_history3.py. [[2026-07-22-full-merge-history]].
    NB this jet is the *misfire* case: soft-drop follows the hardest branch into collinear junk,
    m_SD collapses to ~3 GeV even though kT scales still show the 3-prong top (β=0 pathology).
36. **…and here grooming WORKS: recovering m_W** — companion jet, a boosted W→qq̄ (30 const,
    pt 507). m_ung 120 (inflated by soft radiation) → after dropping 4 soft prongs, soft-drop
    lands on a balanced wide split (z_g 0.49, R_g 0.34, kt 80) → m_SD 83 ≈ m_W. Contrast prev
    slide: same algorithm, two outcomes → why the tagger uses n_drop + kT scales, not m_SD alone.
    Made by full_history_good.py. [[2026-07-22-full-merge-history]].
37. **All inputs (1/5) mass-scale** — per-variable sig-vs-bkg distributions, 6 panels, AUC
    on each. msd/ktg/ln msd/lnρ [C/A], √d12 [kT], m_ung [anti-kT] — all 0.78–0.79, 0.8–0.97
    correlated (same 2-prong mass). Point to m_W≈80 + m_t≈160 in ln m_SD. Made by `tagger_allvars.py`.
38. **All inputs (2/5) prong/kT** — d23/d34/d23r/f21/f32 [all kT], fz [kT÷C/A mixed]. Splitting
    scales beyond the first + ratios; d23 0.684 carries 3-prong top; fz=√(z/(1-z)) mass-decorrelated.
39. **All inputs (3/5) Lund/counting** — n_lund/n_kt1/n_kt5/lnkt2/lnkt3/ndrop, **all C/A**
    (primary declustering). n_drop 0.765 (best non-mass), lnkt2 sees the 2nd decay splitting,
    signal has *fewer* emissions despite higher pileup (physical, not pileup artifact).
40. **All inputs (4/5) groom geom** — zg/rg/z_kt1/dr_kt1 [C/A], n_const [anti-kT], fgroom
    [C/A÷anti-kT mixed]. R_g 0.779 (fixed wide decay angle vs QCD collinear); fgroom 0.747 survival.
41. **All inputs (5/5) functions** — chi/psi1/psi2/fmatch/lndrop/nkt5, **all C/A** (no kT tree
    in this set). Closure χ<1 flags massive prongs (top); ψ2 0.670 sees the W sub-decay. Every
    AUC weighted-logistic single-variable. All in [[2026-07-18-tagger-inputs]]. Condor 9128460.
37. **Tree gallery — QCD vs clean top** — QCD (23 const, pt 331): m_ung 33 → m_SD 1.2, n_drop
    **13**, green spine is a long staircase, no balanced hard split. Clean top (32 const, pt 529):
    m_ung 156 → m_SD 155, n_drop **1**, star at the very top. Spine length 13 vs 1 IS the discriminant.
38. **Tree gallery — boosted & b-jet** — boosted (pt 629, R_g 0.26): decay angle shrinks ~m/pt, tree
    compresses, grooming gets harder. b-jet (pt 403): single hard core, no balanced split — looks
    QCD-like, foreshadowing the AK4 flavour result.
39. **AK4 from MINIAOD** — JMENano has AK4 Jet_* + hadronFlavour but NO PF→AK4 linker (only
    FatJetPFCand for AK8), so AK4 trees are impossible there. Went to MINIAOD via DAS (slimmedJets
    carry packedPFCandidates as daughters): 12k AK4 jets, 3552 b / 6593 udsg. Two-stage pipeline
    because CMSSW python 3.9 and b_hive 3.11 are ABI-incompatible: FWLite dumps constituents,
    b_hive runs flashjet. Figure: b jet and light jet at same pt have near-identical trees.
40. **AK4 result: no flavour tagging** — every variable 0.50–0.59 (best: z of hardest emission
    0.591, √d12 0.588). Expected and important: b vs light is a LIFETIME question (IP, SVs), absent
    from a kinematic tree. ⇒ history tokens belong in boosted 2-/3-prong tagging, not b-tagging.
    Quantitatively confirms the UParT argument.
41. **Correction: AUC tie handling** — the AUC integrated the ROC without handling ties; for
    discrete counts (>80% share one value) that manufactures separation. Caught via AK4 n(kt>5)
    scoring 0.773 while b/light had identical means per pt slice. Fixed with unique-value ROC
    (Mann-Whitney). Corrected AK8: n_kt1 0.587, n_kt5 0.663, n_drop 0.769, f_match 0.648 (was badly
    understated at 0.516). All mass/geometry vars unchanged → AK8 conclusions stand.
    [[2026-07-22-ak4-and-tree-gallery]].
47. **Reproducibility table** — every headline number + condor ID + jet count.
48. **Function reference** — added API surface.
49. **Reproducing everything** — commands, condor pattern (AFS submit dir), seed, papers catalogue.
