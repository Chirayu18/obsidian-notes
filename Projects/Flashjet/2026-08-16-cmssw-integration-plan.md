---
tags: [reference]
status: active
date: 2026-08-16
source: lxplus
---

# flashjet → CMSSW: minimal integration plan

Goal: the smallest change that lets flashjet cluster inside CMSSW and be timed
against production **FastJet 3.4.1 C++** — which is the missing baseline behind
every speedup number we currently quote (see [[2026-08-16-validation-inventory]] §C1).

**Work area (created 2026-08-16):**
`~/flashjet_cmssw/CMSSW_20_1_X_2026-08-16-0000`, `SCRAM_ARCH=el9_amd64_gcc14`
(latest IB; `/cvmfs/cms-ib.cern.ch/sw/x86_64/week1/`).

Tools confirmed present in the IB: **alpaka 2.1.1** (cuda/rocm/serial/tbb),
**CUDA 13.3.1**, **fastjet 3.4.1** + contrib 1.101.

---

## The insertion point (found, not guessed)

`RecoJets/JetProducers/plugins/`:

- **`VirtualJetProducer`** — does everything generic: reads the input collection,
  fills `std::vector<fastjet::PseudoJet> fjInputs_` (`VirtualJetProducer.h:198`),
  then calls a **pure virtual** `runAlgorithm(iEvent, iSetup)` (`.h:113`), and
  afterwards converts `fjJets_` → `reco::Jet` products.
- **`FastjetJetProducer::runAlgorithm`** (`.cc:334`) is the concrete FastJet
  implementation; the actual clustering is one line (`.cc:356`):
  ```cpp
  fjClusterSeq_ = std::make_shared<fastjet::ClusterSequence>(fjInputs_, *fjJetDefinition_);
  ```

**⇒ The minimal integration is a sibling class that overrides `runAlgorithm` only.**
Everything upstream (input handling, PU subtraction config, JEC) and downstream
(product writing) is inherited unchanged, so the comparison is genuinely
like-for-like: same inputs, same outputs, only the clustering swapped.

### The hard part is not the hook, it is `fjClusterSeq_`

Downstream code does not just read `fjJets_`; it calls
`fjClusterSeq_->constituents(...)` (`.cc:299`) and, for grooming/substructure,
walks the sequence. flashjet returns its **own** merge history, not a
`fastjet::ClusterSequence`. Options, cheapest first:

1. **Jets only** (recommended first step). Produce `fjJets_` from flashjet and
   support only the paths that need jet four-vectors + constituent indices.
   Constituents can be rebuilt from flashjet's particle→jet assignment without a
   `ClusterSequence` at all. Grooming/area paths are left on FastJet initially.
2. Populate a real `fastjet::ClusterSequence` from flashjet's history
   (`ClusterSequence::transfer_from_sequence` or a synthetic history). More
   faithful, considerably more work, and easy to get subtly wrong.
3. Full substructure port. Out of scope for "minimal".

---

## Plan

### Step 0 — baseline, no new code (do this first)
Run standard AK4 PF jet reco on a few hundred Open Data events in the IB and time
`FastjetJetProducer` with the framework's own timing service:
```
process.Timing = cms.Service("Timing", summaryOnly=cms.untracked.bool(False))
# or FastTimerService for per-module numbers
```
**This alone answers C1**: it gives the per-event cost of production C++ FastJet on
the exact inputs we benchmark, and it needs no flashjet at all. Even if the rest of
the integration stalls, this number is the one that makes the abstract defensible.

### Step 1 — `FlashjetJetProducer` skeleton
New package `RecoJets/FlashjetProducers` (keeps the IB's `RecoJets/JetProducers`
untouched):
- `plugins/FlashjetJetProducer.{h,cc}` deriving from `VirtualJetProducer`,
  overriding `runAlgorithm` and nothing else.
- Initially: convert `fjInputs_` → a padded `(1, N, 4)` buffer, call flashjet,
  convert back to `fjJets_`. One event per call, batch size 1.
- `python/flashjetJetProducer_cfi.py` mirroring the FastJet cfi parameters.
- Gate substructure/area options off with a clear exception rather than silently
  producing wrong output.

### Step 2 — how flashjet is actually called from C++
flashjet is **Triton/PyTorch Python**. Three routes, and this is the main design
decision to settle with Alex:

| route | what it means | cost / risk |
|---|---|---|
| **(a) Port the kernel to Alpaka/CUDA C++** | reimplement the clustering kernel natively in CMSSW | cleanest production answer, matches CMS's Alpaka direction (alpaka 2.1.1 is in the IB), but a real port — not "minimal" |
| **(b) Call Python from C++** | embed the interpreter / pybind11 | fastest to a number, but the GIL and interpreter startup make in-job timing unrepresentative; unacceptable in production |
| **(c) Offline comparison harness** | dump `fjInputs_` from CMSSW, cluster externally, compare | trivial, and enough to prove **agreement**, but proves nothing about **in-framework timing** |

**Recommendation: (c) for correctness now, (a) as the real target.** (b) flatters
nobody — it would measure Python overhead, which is exactly the criticism we are
trying to answer.

### Step 3 — what to measure once it runs
- Per-event module time, flashjet vs `FastjetJetProducer`, same events, FastTimerService.
- **Batching reality check**: CMSSW is one event at a time; flashjet's advantage
  comes from large batches. Measure how much of the speedup survives at batch 1.
  This is the number that decides whether GPU clustering makes sense in reco at all,
  and it should be measured rather than assumed.
- H↔D transfer per event as a fraction of total (nsys shows it is negligible in the
  batched standalone case; per-event it may dominate).
- Output equality: `reco::Jet` collections compared jet-by-jet against the FastJet path.

---

## Honest assessment

The "minimal" integration that produces a **timing** number is not small, because
flashjet is a Python/Triton library and CMSSW is C++. Steps 0 and 1 are genuinely
minimal and worth doing immediately — Step 0 in particular delivers the most
valuable missing number (C++ FastJet baseline) with no flashjet code at all.

Step 2 route (a) is a real porting project and should be scoped separately, not
smuggled in under "minimal". Worth asking Alex whether CMSSW integration is meant
to be a **conference deliverable** or a **post-conference direction** — the C++
FastJet baseline (Step 0) may be all the conference actually needs.
