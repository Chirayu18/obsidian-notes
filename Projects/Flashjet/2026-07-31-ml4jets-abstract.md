---
tags: [reference, abstract]
status: active
date: 2026-07-31
source: lxplus
---

# ML4Jets abstract — flashjet (library-level)

**Venue:** ML4Jets 2026, 14–18 Sep 2026, Vienna. https://indico.global/event/15240/
Broad ML-in-physics audience — LHC experimentalists *and* theorists, phenomenologists,
method scientists, astro/nuclear, and computer scientists. **Not a CMS meeting.**

Framing: flashjet as a GPU-native jet-clustering library and an in-training-loop
substitute for CPU clustering. Deliberately free of experiment-specific jargon,
hardware model numbers, file-format internals, and substructure minutiae.

---

## Title (options)

1. **flashjet: GPU-Native Jet Clustering for Machine-Learning Pipelines**
2. flashjet: A GPU Substitute for FastJet Inside the Training Loop
3. Differentiable-Pipeline Jet Clustering on GPUs with flashjet

---

## Abstract (main version, ~210 words)

Jet clustering sits on the critical path of nearly every jet-level machine-learning
pipeline, yet it is almost always performed on the CPU, off the accelerator. Particle
four-momenta are copied to the host, clustered, and copied back. In training loops that
revisit the same events for many epochs, and in studies that recluster jets under many
systematic or hyperparameter variations, this round trip — rather than the network
itself — increasingly limits throughput.

We present **flashjet**, a GPU-native implementation of the generalised-$k_t$ family of
sequential recombination algorithms (anti-$k_t$, $k_t$, Cambridge–Aachen). flashjet
clusters batches of jets or events directly in GPU memory, never moving the data to the
host, and returns both the particle-to-jet assignment and the complete merge history.
Because the full clustering tree is retained, standard substructure observables —
exclusive subjets, groomed jets, and Lund-plane coordinates — are recovered as
inexpensive array operations rather than by clustering a second time. The library
presents a single entry point and runs unchanged on CPU and GPU, so it can be dropped
directly into an existing pipeline.

The tagging-scale workload sustains hundreds of thousands to millions of jets per
second, with sub-microsecond latency per jet across the relevant range of constituent
multiplicity. Correctness is established by reclustering jets from a large experimental
dataset and comparing jet by jet against the quantities produced by the standard CPU
implementation: the two agree to the precision at which the reference values are stored.
flashjet is thus a practical, accelerator-resident substitute for conventional
CPU clustering wherever jets must be built or rebuilt inside a learning workflow.

---

## Short version (~120 words, if a tight limit applies)

Jet clustering remains a CPU-side step in otherwise GPU-resident pipelines, forcing a
host round trip on every pass over the data — a cost that dominates when events are
revisited across many training epochs or reclustered under many variations. We present
**flashjet**, a GPU-native implementation of the generalised-$k_t$ algorithms (anti-$k_t$,
$k_t$, Cambridge–Aachen) that clusters batches directly in device memory and returns the
full merge history, so that substructure observables — exclusive subjets, grooming, and
Lund-plane coordinates — follow as cheap array operations instead of a second clustering
pass. It runs unchanged on CPU and GPU behind one entry point, sustains sub-microsecond
latency per jet at tagging scale, and reproduces the standard CPU implementation jet by
jet on real experimental data, to the precision at which the reference is stored.

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

**Deliberately NOT claimed:** exact equality with the CPU reference (we say "to the
precision at which the reference is stored"); no claim the residual is fully understood;
no per-constituent / tagger-input results (that work is jet-level only so far).

### Kept OUT of the abstract on purpose (venue is not CMS, not a hardware talk)

| omitted | why | where it lives if asked |
|---|---|---|
| "NVIDIA A100", CUDA/Triton version | hardware specifics belong in the talk, not the abstract | report.pdf header |
| "130–145 Mpart/s", "0.08–0.76 µs/jet" | precise numbers are device-specific; replaced by "hundreds of thousands to millions of jets/s, sub-µs per jet" | report.pdf §4, Tables 2–3 |
| "CMS", "NanoAOD", "FatJet", "PUPPI" | experiment/format jargon; replaced by "a large experimental dataset" / "the standard CPU implementation" | deck, [[2026-07-13-cms-validation]] |
| "FastJet" by name | kept generic as "the standard CPU implementation" — reads as a comparison, not a pitch against one package. **Put FastJet back if you want the substitute claim to be unmistakable.** | — |
| $p_T$ 1.000000, $\Delta m_{SD}$ −0.004 GeV, $R_g$ 99.2% | number-dense for a general audience; the qualitative statement carries it | deck Summary table |
| padded `(B,N,4)`, `hist_p1/p2/child/d`, mMDT, soft-drop $z_{cut}/\beta$ | API/algorithm internals | deck, [[2026-07-22-full-merge-history]] |
| 85 tests / validation ladder | implementation detail | [[Status]] |

**Judgement call to review:** I dropped the *name* FastJet from the abstract body since
this is a mixed audience, but the note's title framing is "substitute for FastJet". If
you'd rather name it explicitly (most ML4Jets attendees will know it), swap "the
standard CPU implementation" → "FastJet" in both versions — it costs nothing and
sharpens the claim.

**Before submission:** the throughput characterisation traces to the 19 Jun 2026 report,
which predates the substructure features landing — re-confirm on current `benchmarking`
HEAD.
