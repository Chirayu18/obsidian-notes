---
name: phase2-it-unpacker-base-release
description: "sihyunjeon feature/it_alpaka_tests does not build on ANY CMSSW_16_0_X -- it needs PortableHostCollection2, which exists only in 16_1_0_pre1"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T22:12:38.900Z
---

Si Hyun Jeon's Phase-2 IT Alpaka unpacker branch (`sihyunjeon/cmssw`,
`feature/it_alpaka_tests`, pinned `3354683874adc1f804d0bd18885bfd4cf8398347`)
**cannot be built on CMSSW_16_0_9**, or on any 16_0_X. Measured 2026-09-21.

`DataFormats/Phase2ITBitStreamSoA/interface/Phase2ITModuleMapHost.h:8` declares

```cpp
using Phase2ITModuleMapHost = PortableHostCollection2<Phase2ITModuleMapSoA, Phase2ITFedMapSoA>;
```

and the device header `:10` uses `PortableCollection2`. Neither template exists
in `CMSSW_16_0_9/src/DataFormats/Portable/interface/` — grep returns nothing in
16_0_0, 16_0_5 or 16_0_9. Failure cascades: the type is undeclared, so the
generated `T_EventSetup_*.cc` typelookup registrations fail too.

**Where it does exist:** only `CMSSW_16_1_0_pre1`, as an alias —
`PortableHostCollection.h:422: using PortableHostCollection2 = ::PortableHostMultiCollection<T0, T1>;`

**It was WITHDRAWN, not renamed.** Occurrence counts in
`DataFormats/Portable/interface/PortableHostCollection.h` (verified on cvmfs,
gcc13, 2026-09-21) — `PortableHostCollection2` / `PortableHostMultiCollection`:
16_0_9 = 0/0; **16_1_0_pre1 = 1/30**; 16_1_0_pre2 = 0/0; 16_1_3 = 0/0.
So in pre1 it is a thin alias over `PortableHostMultiCollection`, and *that*
template is gone from pre2 onward too — grepping the whole interface dir,
16_1_3 has only single-layout `PortableCollection` / `PortableObject`, with no
variadic multi-layout template at all. Porting to `PortableHostMultiCollection`
therefore does **not** work on a current release; the multi-layout concept has
no successor there. 16_1_0_pre1 is the only release this commit can compile on.

**Consequence beyond the build:** the port cannot be upstreamed as written,
regardless of correctness — that outranks any physics bug in the branch.

Second, independent error in the same branch:
`DataFormats/FEDRawData/src/RawDataBuffer.cc:34` calls `memcpy` without
`#include <cstring>` (gcc13 rejects it; the file is upstream-derived,
last touched by "Srecko code-format"). **Not his bug and it self-resolves:**
16_1_0_pre1 already has that include at line 11. His branch carries a stale
copy of a file upstream had fixed — do not patch it, rebase instead.

**Decision (2026-09-21):** Chirayu chose to build on `CMSSW_16_1_0_pre1`,
`el9_amd64_gcc13` (the only arch it is built for), asserts ON
(`USER_CXXFLAGS="-UNDEBUG -DALPAKA_DEBUG=1"`), to get the `moduleId` range
measurement. Numbers from it must be labelled with the release: the API is a
dead end, so a timing number quoted without that caveat will be read as current.
The moduleId answer transfers anyway — it depends on the geometry and cabling
map, not the Portable API.

**Why:** the study's whole build leg was scoped against 16_0_9 because that is
what the base-release note said. The branch was never buildable there, so no
amount of addpkg/checkout fiddling would have worked — the first real compiler
error is the answer, not an obstacle to route around.

**How to apply:** before scoping a CMSSW build for someone else's feature branch,
grep the base release for the templates its new headers name. See
[[Meta/claude-memory/_history/workflow/vault/lxplus-cmssw-build-location|lxplus-cmssw-build-location]] for where to put the build area.
