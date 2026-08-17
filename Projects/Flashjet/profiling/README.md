---
tags: [reference]
status: active
date: 2026-08-17
source: lxplus
---

# Profiling reports — open these locally for screenshots

Nsight reports from the flashjet benchmarking runs, copied into the vault so they
can be opened on the laptop. Viewing needs the **free** NVIDIA GUIs (no GPU
required just to read a report):

- **Nsight Systems** → `.nsys-rep` (timeline, kernel share)
- **Nsight Compute** → `.ncu-rep` (hardware counters, occupancy)

Numbers extracted from these are on the profiling slide of
[[flashjet-benchmark-status]]; see also [[2026-08-16-validation-inventory]].

---

## Which file is which

| file | GPU | workload | use it for |
|---|---|---|---|
| `nsys_NVIDIA_H100_NVL_B16384_N64.nsys-rep` | H100 NVL | **jet regime** — 16 384 jets × 64 particles | **the timeline screenshot** (matches the deck's headline) |
| `nsys_NVIDIA_A100-PCIE-40GB_B16384_N64.nsys-rep` | A100 | same workload | same view on the older GPU, if a comparison is wanted |
| `nsys_NVIDIA_H100_NVL_B256_N2048.nsys-rep` | H100 NVL | large-N — 256 × 2048 | only if the large-N case is discussed |
| `ncu_NVIDIA_H100_NVL_B128_N512.ncu-rep` | H100 NVL | one kernel launch | **the occupancy screenshot** |

---

## Screenshots to take

### 1. Timeline — *the one worth having*
**File:** `nsys_NVIDIA_H100_NVL_B16384_N64.nsys-rep` (Nsight Systems)

Expand the **CUDA HW** row so the kernel track shows, then zoom to **2–3
iterations** — not the whole capture, not a single kernel.

**Should show:** one long kernel bar repeating back to back, with **no memcpy bars
between them**. Keep any memory-transfer row visible-but-empty — that emptiness is
the point.

**Why:** this is the claim a table cannot make. It *shows* that there is no
CPU↔GPU traffic and no gaps: the GPU just clusters.

### 2. Occupancy
**File:** `ncu_NVIDIA_H100_NVL_B128_N512.ncu-rep` (Nsight Compute)

Details page → **Occupancy** section. Capture Theoretical **18.75 %** vs Achieved
**6.25 %**, ideally including the block-limit chart that flags **registers** as the
limiting factor.

**Why:** the tool itself identifies the bottleneck, which is more convincing than
us asserting it.

### 3. Kernel summary — *optional, probably skip*
Same nsys file → Stats → **CUDA GPU Kernel Summary**
(`_cluster_large_kernel` ~97 %, `_decode_kernel` ~1.5 %).
This duplicates a table already in the deck.

---

## Two practical notes

- **Switch to a light theme** before capturing (Nsight Systems:
  *Preferences → Appearance*). Dark screenshots look muddy on a projector and
  clash with the white slides.
- **Crop tightly** (⌘⇧4) to just the panel — no menus, no sidebars. Window
  furniture is what makes these unreadable once scaled into a slide.

Save the PNGs into `Projects/Flashjet/presentation/img/` and they can be added to
the deck.

---

## Regenerating (if ever needed)

These come from `run_bench.sh` on an lxplus GPU node; originals live in
`/eos/home-c/cgupta/flashjet/bench_opendata/`.

```bash
nsys profile --trace=cuda,nvtx --capture-range=cudaProfilerApi \
  --capture-range-end=stop -o OUT python benchmarks/scripts/prof_flashjet_clean.py 16384 64 10

ncu --kernel-name "regex:_cluster_large_kernel" --launch-count 1 --set basic \
  --clock-control none -o OUT python benchmarks/scripts/prof_ncu.py 128 512
```

<span>Note: `ncu` cannot lock clocks on a MIG slice, so profiling must target a full
card (hence `--clock-control none` above, and why absolute timings in the ncu
report are indicative while occupancy/register figures are structural).</span>
