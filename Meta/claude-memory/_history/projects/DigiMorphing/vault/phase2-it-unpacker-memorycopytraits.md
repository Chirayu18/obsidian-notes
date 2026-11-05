---
name: phase2-it-unpacker-memorycopytraits
description: "CORRECTED: the branch does NOT delete MemoryCopyTraits -- its 16_0_X merge-base predates them; the conflict is base-vs-pre1 drift, not a branch defect"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f1af237-184c-46ae-b080-bdbda78b16b2
  modified: 2026-09-21T22:23:31.059Z
---

Second independent blocker in Si Hyun Jeon's Phase-2 IT Alpaka unpacker branch
(`feature/it_alpaka_tests` @ `3354683874a`), found building on
**CMSSW_16_1_0_pre1** 2026-09-22. Distinct from the
`PortableHostCollection2` issue in [[Meta/claude-memory/_history/projects/DigiMorphing/vault/phase2-it-unpacker-base-release|phase2-it-unpacker-base-release]].

> **CORRECTION (2026-09-22, same session).** The claim below that "the branch
> deletes" the traits is **WRONG**. Diffing against the branch's own merge-base
> `dd7156a9fb9` (16_0_X, 2025-10-03) shows Si Hyun touched neither header:
> `git diff --stat <merge-base> sihyun/feature/it_alpaka_tests -- <those headers>`
> is **empty**, that base's `SiPixelDigisHost.h` contains **zero** occurrences of
> `MemoryCopyTraits`, and it has **no** `DataFormats/SiPixelDigiSoA/plugins/`
> directory at all. pre1 ADDED both the traits requirement and the
> `TrivialSerialisation` plugin after his base was cut. The "deletion" was an
> artifact of diffing his branch against pre1 rather than against its own base.
> It is still a real build conflict, but it is base-drift, **not** a branch defect,
> and it must not be reported as something he removed.

**What the branch's tree looks like relative to pre1 (the misleading view):**

| File | Lines removed |
|---|---|
| `DataFormats/SiPixelDigiSoA/interface/SiPixelDigisHost.h` | 35 |
| `DataFormats/SiPixelDigiSoA/interface/SiPixelDigiErrorsHost.h` | 33 |

Both lose the `#include "DataFormats/TrivialSerialisation/interface/MemoryCopyTraits.h"`
and the whole `namespace ngt { template <> struct MemoryCopyTraits<...> }` block
(`properties` / `initialize` / `regions`). After checkout, `grep -rn MemoryCopyTraits
DataFormats/SiPixelDigiSoA/` returns **nothing**.

pre1 ships a stock plugin `DataFormats/SiPixelDigiSoA/plugins/TrivialSerialisation.cc`
that instantiates `ngt::Writer<SiPixelDigisHost>` / `ngt::Reader<SiPixelDigiErrorsHost>`,
so the build dies on:

```
HeterogeneousCore/TrivialSerialisation/interface/Writer.h:17:24: error: static assertion failed:
  No specialization of MemoryCopyTraits found for type T
```

4 errors, all in **one** object file
(`.../DataFormatsSiPixelDigiSoATrivialSerialisation/TrivialSerialisation.cc.o`).

**Not forced by a layout change.** The branch's `SiPixelDigisSoA` layout is
byte-identical to stock — the same 7 columns (`clus`, `pdigi`, `rawIdArr`, `adc`,
`xx`, `yy`, `moduleId`). So the deletion looks like a rebase artifact: the branch
was developed against a 16_0_X tree whose headers had no traits block, and the
deletion got carried forward as if it were an intentional change.

**`TrivialSerialisation` exists in BOTH 16_0_9 and 16_1_0_pre1**, so this is not a
"newer release added a requirement" story.

**Why:** the base-release problem is not one issue but at least two, in opposite
directions. `PortableHostCollection2` needs a release *newer* than 16_0_9; the
`MemoryCopyTraits` deletion breaks against a stock plugin present in both. Fixing
the first does not fix the second.

**How to apply:** when a feature branch deletes code rather than adding it, diff
against the base (`git diff HEAD -- <pkg>`) before assuming the failure is yours.
Here `git status --short` showed `M` on two headers, and the diff showed pure
deletion — that distinguished a branch defect from a packaging mistake (the
earlier `memcpy`/FEDRawData error WAS a packaging mistake: it only appeared
because FEDRawData was needlessly `git cms-addpkg`'d).
