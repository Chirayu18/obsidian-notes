---
tags: [reference]
status: active
date: 2026-09-18
source: lxplus
---

# FlashJet GPU kernel: what we measured, and why every intra-event optimisation failed

One-line answer: **the CUDA kernel runs at `grid_size = 1.5` and 17.4 % occupancy
on a 40-SM T4, so it is latency-bound on an almost-empty GPU.** Three separate
optimisations that each removed real work changed nothing measurable, because
work was never the constraint. The only lever left is batching events into one
kernel call, and that is blocked by the CMSSW alpaka module API, not by the
kernel or the data format.

Everything below was measured today on a Tesla T4 via `lxplus-gpu.cern.ch`,
against `CMSSW_20_1_X_2026-09-15-2300` on EOS.

## The ncu profile — the number that explains the rest

`ncu --kernel-name gpuKernel` on the recluster + soft-drop workload:

| launch | grid × block | time | `sm__warps_active` | barrier stall | thread efficiency |
|---|---|---|---|---|---|
| A | **1** × 256 | 14.34 ms | 25.0 % | 12.5 % | 30.98 / 32 |
| B | **2** × 128 | 1.31 ms | 12.5 % | 33.6 % | 26.81 / 32 |
| C | **1** × 256 | 60.07 ms | 25.0 % | 6.8 % | 31.36 / 32 |

* `launch__grid_size` is **1–2**. `launch__occupancy_limit_blocks` is 16, and the
  T4 has 40 SMs, so ~640 blocks could be resident. We use one or two.
* `smsp__thread_inst_executed_per_inst_executed` ≈ **31 of 32 lanes** — warp
  divergence is already essentially absent.
* Barrier stalls are **6.8–33.6 %**, not the >50 % a static model predicted.

## Three optimisations, all correct, none faster

Each was validated to 0 mismatches before being timed, and each is reverted.

| attempt | what it removed | measured |
|---|---|---|
| block-parallel stale rescan | the divergent `for (k = tid; ...) if (stale[k]) rescan(k)` — only ~2 of n slots are stale, so 2 threads did O(n) while 254 idled | **+4.6 % slower** |
| skip provable rescans | a stale slot with `d <= nnd_old` provably keeps the merged `i` as its NN (verified: 4122 stale slots, 0 violations) — fires ~8 % | bundled, no separate number |
| live-list compaction | every loop ran `k < n` regardless of how many slots were alive; at step 700/800 that is 87.5 % wasted. Live list cut **38 % of loop trips** and preserved slot indices so tie-breaks were untouched (400 trials, 0 history mismatches) | **0.26 %, i.e. nothing** |

Compaction, all 37 launches summed, same job:
`compaction 8516.97 ms` vs `baseline 8494.53 ms`.

### A methodology trap worth remembering

The first A/B runs used `ncu --launch-count 12`, which samples only the first 12
launches. Entry sizes in the recluster workload range 1.31–60.07 ms, so the mean
over an arbitrary 12 is noise:

| run | compaction | baseline | apparent verdict |
|---|---|---|---|
| 1 | 107.26 ms | 246.22 ms | 2.30× faster |
| 2 | 127.14 ms | 108.88 ms | 1.17× slower |

**The same unmodified baseline measured 246.22 and 108.88 ms.** Always sum all
launches over a fixed input; never compare across ncu rounds. (Upstream's README
makes the same point about MIG slices varying ~35 % between rounds.)

## Why parallel merging does not work — and the one place I over-generalised

Tested the Cacciari–Salam / NN-chain idea: merge all mutual-nearest-neighbour
pairs at once.

| variant | wrong jets | merges per round |
|---|---|---|
| naive mutual-NN | 6 / 300 | ~5 |
| strict (`d_ij ≤ all competitors`) | 7 / 300 | **1.03** |

Compared by replaying histories into particle sets, not by comparing pseudojet
ids. Concrete failure: sequential gives `[2,3,6]`, parallel gives `[2,3,5]`.

**[Sitian's "Reducible jet measures" proposal](https://sqian.web.cern.ch/jet-math/)
(Sept 2026 draft) independently measures 1.1 merges/round for anti-kt.** Our 1.03
and their 1.1 agree, which is good corroboration — but the proposal is sharper
about the cause and shows I generalised too far:

> Reducibility: "merging two pseudojets must never bring the result closer to a
> third than both parents were." It fails two ways — **weight**: "the merged
> object's weight falls when p < 0, so distances can shrink"; **geometry**: "the
> merged axis moves under E-scheme recombination".

I found the geometric channel empirically and attributed it loosely to the beam
term. The weight channel is the real discriminator: **p < 0 is what breaks
anti-kt specifically.** And it is fixable —

> "Winner-take-all recombination closes the geometric channel; p ≥ 0 closes the
> weight channel."

| algorithm | rounds | merges/round | exact? |
|---|---|---|---|
| kt + WTA | 9.8 | 31 | 20/20 events |
| C/A + WTA | 6.7 | 45 | 20/20 events |
| kt + E-scheme | 9.4 | 32 | — |
| **anti-kt** | — | **1.1** | intrinsically serial |

**So "generalised-kt cannot be parallelised" is wrong; anti-kt cannot.** kt and
C/A can. That matters here: `FlashJetReclusterProducer` defaults to **C/A** with
R = 1000, and that is the one workload where the GPU already wins (455 vs 331
ev/s, upstream README). See [[2026-09-14-cpu-backend-pr-merge-test]] for the
package layout.

External check, [ParChain (VLDB 2022)](https://arxiv.org/abs/2106.04727):
supports "complete linkage, average linkage, and Ward's" — exactly the reducible
Lance–Williams linkages. Not a coincidence; it is the theorem's precondition.

## Other avenues closed today

| idea | verdict | basis |
|---|---|---|
| precompute the full distance matrix, CPU does only merges | **impossible** | the merged pseudojet sits at a position that did not exist when the cache was built. 3-particle counterexample: cache holds d(0,2)=0.3844, d(1,2)=0.1024; after merging 0+1 the true d=0.2209 is neither, and cannot be derived without the four-momenta |
| CPU merges, GPU distances | 30–200× slower | needs n round trips/entry; ~25 µs each × 800 = ~20 ms vs 0.1–0.6 ms total |
| speculative depth-d | **28.6 GB at n=800, d=2**; branching factor measured at **1.00** | top-k candidate merges overlap — essentially always exactly one is independent |
| tiling on GPU | already done, deliberately CPU-only | `FlashJetTiled.h` (heap + linked cells + reverse-NN index) is GPU-hostile; it trades parallel scans for sparse pointer chasing |
| full N² matrix | ~40 % fewer `dr2()` | same order as compaction's 38 %, which measured 0.26 %. Also converts cheap ALU into global-memory traffic |

[Fülöp & Nagy 2017](https://acta.sapientia.ro/content/docs/parallel-iksubtsubi-jet-clustering-algor.pdf),
the only paper directly on parallel kt, parallelises exactly what we already do —
*"the distance update of the newly created jets after each recombination step"*,
with the merge *"sequential on the assignment of the new closest neighbor"* —
and gets **1.67×** on 8 CPU threads, still losing to tile-based clustering.
Nothing there to adopt.

## Batching: the mechanism exists, the alpaka wrapper blocks it

The kernel and SoA are **already batch-capable**: `FlashJetDeviceCollection`
holds N independent entries and `grid_size == nEntries`. `FlashJetReclusterProducer`
already exploits this within an event (~80 jets → 80 blocks). Nothing there needs
to change.

The blocker is purely the producer. Surveyed all 104 packages:

* `edm::StreamCache` — all 15 users treat it as per-stream scratch, not batching
* Run/Lumi/ProcessBlock producers — wrong product scope (they put into the lumi)
* SONIC — `SonicEDProducer` is `edm::stream::EDProducer<edm::ExternalWork>`, one
  event per call. **The batching lives in the Triton server**, not CMSSW:
  `data/models/flashjet/config.pbtxt` has `max_batch_size: 64` and
  `dynamic_batching { max_queue_delay_microseconds: 500 }`
* **No in-framework cross-event batching exists anywhere in the release.**

The mechanism that would work: `edm::stream::EDProducer<edm::ExternalWork,
edm::GlobalCache<...>>`. `acquire()` has no deadline (`stream/implementors.h:295`)
and `GlobalCache` is shared across streams (`stream/EDProducer.h:41`), so a module
can hold N events and release them all after one launch.

**But the alpaka wrapper forbids it.** `ALPAKA_ACCELERATOR_NAMESPACE::stream::EDProducer`
has a `static_assert` against `ExternalWork`, and `SynchronizingEDProducer`
swallows the holder — `EDMetadataAcquireSentry` takes ownership and calls
`doneWaiting` itself when the queue drains (`EDMetadataAcquireSentry.cc:37`). The
module never sees it. Options: bypass the alpaka base class, or propose an API
change upstream.

## Shipped

Two commits, validated then pushed to `Chirayu18/cmssw@flashjet-alpaka-idioms`:

* `b58036e4b` — `independent_groups` for the one-entry-per-block loop,
  `once_per_block` ×5, 6 × `ALPAKA_ASSERT_ACC`, `//#define GPU_DEBUG` (+20/−8)
* `72fdd1e0a` — `kMinWarpSize`/`kMaxWarps` hoisted to file scope, `better()` as a
  free `ALPAKA_FN_ACC ALPAKA_FN_INLINE` function, `divide_up_by` (+9/−7)

Both behaviour-neutral. Validation each time: `testFlashJetCore` **97 269
assertions**, CPU serial_sync **475 jets 0 mismatches**, CUDA **475 jets 0
mismatches + 165 groomed values 0 mismatches**.

A `flashJetClustering` namespace rename was tried and dropped — it de-indented
the whole kernel for a 373/359-line diff with no functional gain.

## Not finished

**The stream scan never produced a number.** It measures how many events are
concurrently in `acquire()`, which caps any batch size — if concurrency is ~2–4,
the batching design yields `grid_size = 4`, not 32, and is probably not worth the
alpaka deviation.

Three bugs, all mine: results written to `/tmp` while `lxplus-gpu.cern.ch`
round-robins across nodes (901/902/908/909); the job run in an ssh foreground
that timed out; and `-n`/`maxEvents=` instead of `--threads`/`--maxEvents`, which
made it unbounded (27 000+ events). Leftover processes from the superseded script
then contended for the same T4. Script is at
`/eos/home-c/cgupta/flashjet/cmssw/bench/scan5.sh`, output to `bench/scan.txt`.

To restart cleanly from a login shell:

```
ssh lxplus901.cern.ch "pkill -9 -u \$USER cmsRun; sleep 2; \
  setsid nohup bash /eos/home-c/cgupta/flashjet/cmssw/bench/scan5.sh \
  >/tmp/scan5.log 2>&1 </dev/null & disown"
```

## What I would do next

1. Finish the stream scan — it is the cheap measurement that gates everything.
2. If concurrency is useful, batch via `ExternalWork` + `GlobalCache`, bypassing
   the alpaka base class. Needs flush-on-lumi, a timeout, a mutex, and
   `doneWaiting(exception_ptr)` on every held holder or the job hangs.
3. Feed the anti-kt 1.03 vs 1.1 agreement and the ncu occupancy data to WP1/WP2
   of [the reducible-measures proposal](https://sqian.web.cern.ch/jet-math/) —
   WP3 is this repo.
