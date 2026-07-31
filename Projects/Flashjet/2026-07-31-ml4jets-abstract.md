---
tags: [reference, abstract]
status: active
date: 2026-07-31
source: lxplus
---

# ML4Jets abstract — flashjet (library-level)

Target: ML4Jets conference. Framing: flashjet as a GPU-native jet-clustering library
and an in-training-loop substitute for FastJet. Deliberately light on substructure
internals.

---

## Title (options)

1. **flashjet: GPU-Native Jet Clustering for Machine-Learning Pipelines**
2. flashjet: A GPU Substitute for FastJet Inside the Training Loop
3. Differentiable-Pipeline Jet Clustering on GPUs with flashjet

---

## Abstract (main version, ~230 words)

Jet clustering sits on the critical path of nearly every jet-tagging pipeline, yet it
remains a CPU-bound, host-side step: constituents are copied off the accelerator,
clustered with FastJet, and copied back. In training loops that reprocess the same
events for many epochs, or in analyses that recluster jets under systematic variations,
this round trip — not the network — increasingly sets the throughput.

We present **flashjet**, a GPU-native implementation of the generalised-$k_t$ family
(anti-$k_t$, $k_t$, Cambridge–Aachen) written in Triton and PyTorch. flashjet operates
directly on padded `(B, N, 4)` momentum tensors that never leave the device, returning
the particle-to-jet assignment and the **complete merge history**, from which
substructure observables — exclusive subjets, soft-drop/mMDT grooming, and Lund-plane
coordinates — are obtained as inexpensive tensor reads requiring no additional
clustering. The library exposes a single entry point and runs unchanged on CPU and CUDA.

On an NVIDIA A100 the jet-reclustering regime typical of tagging sustains
130–145 Mparticle/s at 0.08–0.76 µs per jet, remaining sub-microsecond across the full
constituent-multiplicity range, while full-event clustering scales as expected with
the per-event $O(N^2)$ cost.

Correctness is established against FastJet itself: applied to CMS NanoAOD constituents,
flashjet reproduces the stored FastJet-derived quantities jet by jet, with a
reclustered-to-stored $p_T$ ratio of 1.000000 and a median soft-drop-mass difference of
−0.004 GeV, residuals consistent with NanoAOD floating-point storage. flashjet is
therefore a drop-in, accelerator-resident replacement for FastJet wherever clustering is
required inside a machine-learning workflow.

---

## Short version (~120 words, if a tight limit applies)

Jet clustering remains a CPU-bound, host-side step in otherwise GPU-resident tagging
pipelines, forcing a device round trip on every pass over the data. We present
**flashjet**, a GPU-native implementation of the generalised-$k_t$ algorithms
(anti-$k_t$, $k_t$, Cambridge–Aachen) in Triton/PyTorch that clusters padded momentum
tensors in place and returns the full merge history, from which substructure
observables follow as cheap tensor reads. On an A100 the tagging regime sustains
130–145 Mparticle/s at sub-microsecond latency per jet. Validated against CMS NanoAOD,
flashjet reproduces the stored FastJet quantities jet by jet — $p_T$ ratio 1.000000,
median $\Delta m_{SD}$ = −0.004 GeV — at the level of NanoAOD storage precision, making
it a drop-in accelerator-resident substitute for FastJet inside the training loop.

---

## Fact-check / provenance of every number

| claim | source |
|---|---|
| Triton + PyTorch, generalised-$k_t$ (anti-$k_t$/$k_t$/C-A) | [[Status]]; report.pdf abstract |
| padded `(B,N,4)` stay-on-GPU | report.pdf §1 |
| returns particle→jet assignment + full merge history | report.pdf §1 |
| substructure = cheap reads, no re-clustering | deck "Summary" (pure-torch post-reads, negligible cost) |
| CPU/CUDA identical | deck Summary |
| 130–145 Mpart/s, 0.08–0.76 µs/jet | report.pdf §4 + Table 2 |
| event regime $O(N^2)$, falls 47→1.1 Mpart/s | report.pdf §4 + Table 3 |
| $p_T$ ratio 1.000000, median $\Delta m_{SD}$ −0.004 GeV, $R_g$ 99.2% <0.01 | deck Summary validation table |
| residuals at NanoAOD storage level | deck (hedged wording, matches msd-outlier-anatomy) |
| 85 passed / 13 CUDA-skipped | [[Status]] 2026-07-08 (repo suite; report's "105" is Alex's A100 count) |

**Deliberately NOT claimed:** exact equality with FastJet (we say "consistent with
NanoAOD float storage"); no claim the residual split is fully understood; no
per-constituent / tagger-input results (that work is jet-level only so far).

**Numbers to double-check before submission:** the A100 throughput figures are from
Alex's 19 Jun 2026 report — confirm they still hold on the current `benchmarking` HEAD,
since the substructure features landed after that measurement.
