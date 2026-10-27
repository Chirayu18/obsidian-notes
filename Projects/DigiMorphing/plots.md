---
tags: [reference]
status: active
date: 2026-10-23
source: lxplus
---

# DigiMorphing — plots

Plot links for the Phase-2 Alpaka digi morphing validation. PNGs stay on EOS. Numbers in
`/eos/user/c/cgupta/phase2morph/plots/summary.json`. See [[2026-09-30-phase2-alpaka-morphing-plan]].

---

### Recovered digis per module: GPU vs CPU, and GPU vs exact reference

tags: [plot]
Date: 2026-10-23
Description: Phase-2 digi morphing, TBPX layer 1, TTbar PU200 (100 events, 21,600 module-events). Left: GPU (Alpaka strip morphing) vs CPU SiPixelDigiMorphing, 12.1% of modules identical. Right: GPU vs an exact whole-module reference, 100% identical (0 differences in 1,696,444 recovered digis).
Path: /eos/user/c/cgupta/phase2morph/plots/recovered_digis_gpu_vs_cpu.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/recovered_digis_gpu_vs_cpu.png

---

### Digis per module before and after morphing

tags: [plot]
Date: 2026-10-23
Description: Real digis per TBPX L1 module (5.29M total) and after morphing, GPU (6.99M) and CPU (6.92M).
Path: /eos/user/c/cgupta/phase2morph/plots/digis_per_module.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/digis_per_module.png

---

### Difference in recovered digis per module

tags: [plot]
Date: 2026-10-23
Description: Per-module GPU minus CPU recovered digis (mostly 0 to +10, GPU recovers more), and GPU minus exact reference (all exactly 0).
Path: /eos/user/c/cgupta/phase2morph/plots/recovered_digis_difference.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/recovered_digis_difference.png

---

### Where GPU and CPU recovered digis differ

tags: [plot]
Date: 2026-10-23
Description: Positions of the 69,844 recovered digis found by only one of GPU and CPU: 55,407 at the 27-column chunk edges of the CPU module (its 1-column halo is not dilated), 10,551 on the first/last row (deliberate Phase-1 GPU edge rule), 3,886 CPU-only on the last module column (CPU artifact), 0 elsewhere. In all 69,844 the GPU agrees with the exact reference.
Path: /eos/user/c/cgupta/phase2morph/plots/difference_location.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/difference_location.png

---

### Clusters per module before and after morphing

tags: [plot]
Date: 2026-10-23
Description: TBPX L1 clusters: 927,589 before, 897,298 after GPU morphing (-3.3%), 897,990 after CPU morphing.
Path: /eos/user/c/cgupta/phase2morph/plots/clusters_per_module.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/clusters_per_module.png

---

### Cluster size in TBPX layer 1 with and without morphing

tags: [plot]
Date: 2026-10-23
Description: GPU clusters, pixels per cluster (mean 5.70 -> 5.89) and size along columns (3.96 -> 4.07).
Path: /eos/user/c/cgupta/phase2morph/plots/cluster_size_L1.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/cluster_size_L1.png

---

### Event display 1: merged clusters in a TBPX L1 module

tags: [plot]
Date: 2026-10-23
Description: Real digis colored by cluster before morphing (left) and the merged cluster after (right), true 25x100 um pixel aspect; GPU recovered digis as outlines, CPU recovered as crosses.
Path: /eos/user/c/cgupta/phase2morph/plots/display_1.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/display_1.png

---

### Event display 2: merged clusters in a TBPX L1 module

tags: [plot]
Date: 2026-10-23
Description: Real digis colored by cluster before morphing (left) and the merged cluster after (right), true 25x100 um pixel aspect; GPU recovered digis as outlines, CPU recovered as crosses.
Path: /eos/user/c/cgupta/phase2morph/plots/display_2.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/display_2.png

---

### Event display 3: merged clusters in a TBPX L1 module

tags: [plot]
Date: 2026-10-23
Description: Real digis colored by cluster before morphing (left) and the merged cluster after (right), true 25x100 um pixel aspect; GPU recovered digis as outlines, CPU recovered as crosses. Display 3 shows a crossing cluster merged into a long track.
Path: /eos/user/c/cgupta/phase2morph/plots/display_3.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/display_3.png

---

### Event display 4: merged clusters in a TBPX L1 module

tags: [plot]
Date: 2026-10-23
Description: Real digis colored by cluster before morphing (left) and the merged cluster after (right), true 25x100 um pixel aspect; GPU recovered digis as outlines, CPU recovered as crosses.
Path: /eos/user/c/cgupta/phase2morph/plots/display_4.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/display_4.png

---

### Count difference vs master, morphing off (Phase-1-style)

tags: [plot]
Date: 2026-10-27
Description: Pixels and clusters per module, this branch minus master, stock config, 100 PU200 events: 0 of 400,000 module-events differ. Same plot as the Phase-1 PR #49991 validation.
Path: /eos/user/c/cgupta/phase2morph/plots/phase1style/count_difference.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/phase1style/count_difference.png

---

### Cluster size without, with, overlapped, per-module difference (Phase-1-style)

tags: [plot]
Date: 2026-10-27
Description: TBPX L1 GPU clusters, 4 panels as in #49991. Mean 5.70 -> 5.89; per-module mean size +0.25 pixels, never negative.
Path: /eos/user/c/cgupta/phase2morph/plots/phase1style/cluster_size_phase1style.png
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/plots/phase1style/cluster_size_phase1style.png

---

### IIHE Tracker DPG talk folder (slides + plots)

tags: [plot]
Date: 2026-10-27
Description: Beamer and HTML PDFs of the 27 Oct talk, HTML sources, and all validation plots. Internal: contains CERN-restricted workshop figures.
Path: /eos/user/c/cgupta/phase2morph/talk-2026-10-27
Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/phase2morph/talk-2026-10-27
