---
tags: [reference, agenthon, preprint]
status: active
date: 2026-11-03
source: laptop
author: paper-codex (Codex), saved by the conductor
---

# Agenthon preprint: recommendation and publication readiness

## Bottom line

**Pursue a focused simulator paper, not a new ConvBench project and not an equally weighted account of every track.** The strongest contribution is a native implementation of the patched ABIDES simulator that preserves reference behavior across retained comparisons. Coding and forecasting supply useful supporting cases, but weaker publication evidence.

The manuscript is a working research draft, not yet ready for arXiv submission.

## What exists

`paper/preprint/` contains the manuscript, generated tables, bibliography, evidence-recomputation script, and release checklist:

- `main.tex`
- `tables.tex`
- `refs.bib`
- `scripts/recompute_tables.py`
- `TODO.md`

The conductor verified that the manuscript compiles to **nine pages** and that its tables regenerate exactly from retained records. Sources: conductor build verification of `paper/preprint/main.tex` and execution of `paper/preprint/scripts/recompute_tables.py`. The checklist’s older statements that compilation and script execution were unavailable are superseded by that verification.

**History:** No ICAIF paper ever existed. ConvBench was an unfinished experiment idea and has been set aside.  
A cross-track manuscript was subsequently proposed; Codex now recommends narrowing its main contribution to simulator compatibility and acceleration.

## Why the simulator should lead

The technical content is more substantial than “C++ is faster than Python.” It addresses random-stream consumption, mixed Python numeric clocks, deterministic event ordering, order storage, and trace production without intentionally changing the simulated execution.

The paper should ask:

> How can a stochastic market simulator be accelerated while preserving a specified reference implementation’s observable behavior?

That is a clearer research question than a general claim about financial agents.

| Retained evidence | Supported interpretation | Unsupported interpretation |
|---|---|---|
| **95 matching scenario/subscenario comparisons**, `track3/runs/cand_all.log` | Equality under the retained decoded-data comparator | Universal equivalence or identical Parquet bytes |
| **71 successful container records with no fallback markers**, `track3/runs/docker_all_v2.log` | Native completion across the logged public roster | Official Final acceptance or exhaustive native coverage |
| **188 matching rechecks**, `track3/runs/fuzz_recheck_v2.log` | Regression evidence using available stored references | Independent random coverage, or coverage added to the original fuzz campaign |
| Mega-throughput timing **504 to 367 ms**, `track3/runs/roster_t3sim:v1.log:33` and `track3/runs/roster_t3sim:v2.log:33` | A favorable historical native-version comparison | Controlled ABIDES speedup or attribution to one optimization |
| Coding and reader outcomes, `paper/preprint/tables.tex`, underlying sources cited there | Development case studies and validation warnings | Established general accuracy improvement |

The missing controlled baseline and optimization ablation are the largest scientific gaps. Comparator null handling and source-to-binary provenance also require attention.

## Referee findings and revisions

The recorded referee-response checklist, `paper/preprint/TODO.md`, documents these corrections:

- Selected timing improvements were replaced by a consecutive workload block that also exposes regressions.
- Earlier own coding runs were restored, preventing a favorable extra-pool result from obscuring weaker public-pool performance.
- Inspected holdout material is explicitly development data.
- Different extra-task rosters are distinguished rather than compared as identical evaluations.
- Rival runs are identified and excluded from our result tables.
- Fuzz rechecks are described as conditional regression evidence, not fresh coverage.
- Unsupported causal and official-result claims were removed or qualified.

These revisions improve honesty and interpretability. They do not substitute for missing experiments.

**Where Claude and Codex differ:** the clearest remaining difference is scope. The revised draft retains the cross-track framing; Codex favors a tighter simulator paper. The recorded referee revisions emphasize repairing evidence presentation within the existing structure. A separate Claude referee transcript was not available in the inspected files, so this report does not attribute stronger publication recommendations to Claude.

## Ownership, data, and licensing

The conductor verified the following official provisions:

- Agenthon terms §3: **“You keep ownership of your submission.”**
- Licensing §10: cite Agenthon and underlying datasets/software. Organizers need author permission to publish a participant-authored paper.
- Licensing §4: never retain, publish, or reconstruct private-test content.

Sources: [Terms](https://www.agenthon.net/terms/) and [Licensing policy](https://www.agenthon.net/licensing/).

| Material | Applicable rights and release approach |
|---|---|
| Participant-authored implementation | Retained participant rights, subject to collaborators, employment obligations, and upstream components |
| Public simulator materials | Repository default MIT; inspected manifests specify CC BY licenses and redistribution permission. Check every released file |
| ABIDES | BSD license with required notices and attribution |
| Coding benchmark | Default noncommercial Creative Commons license, with per-file overrides |
| Forecasting corpus and panels | Mixed rights, including unresolved third-party permissions. **Exclude raw corpus and panels from the release** |
| Rival repositories and private tests | **Exclude** from our artifact and claims of authorship |

Local sources: each track’s `DATA-LICENSE.md`, `track3/abides/LICENSE`, `track3/kit/THIRD-PARTY-NOTICES.md`, and inspected unit manifests.

A lawful reproduction package need not redistribute every dependency. Acquisition instructions and pinned manifests are preferable where rights are uncertain.

## AI-use disclosure

Use a factual disclosure, not a warning banner. Suggested final wording, only after the described review is completed:

> Generative-AI tools assisted software development, experimental scripting, evidence inspection, and manuscript preparation. The authors reviewed the implementation, checked reported results against experimental records, and verified the references. The authors take responsibility for the final manuscript.

Identify actual tools and relevant versions where recorded. Explain material methodological assistance in Methods. AI tools are not authors. Source: [arXiv moderation and AI-use policy](https://info.arxiv.org/help/moderation/index.html).

## Related work

**Already in the bibliography:** ABIDES and JAX-LOB, with verified records in `paper/preprint/refs.bib`.

**Still needed:** differential testing, numerical reproducibility, compatible simulator implementations, and a clear comparison of compatibility obligations versus throughput-oriented redesigns.

Treat minABIDES as **not yet verified for inclusion in the manuscript bibliography**. Any suggested arXiv identifier recalled from memory must be independently checked. The draft explicitly leaves “Right Numbers, Wrong Questions” unverified and uncited in `main.tex`; do not promote it into a reference without reconciliation.

Faster simulation and differential testing are established ideas. The defensible novelty claim concerns their compatibility-oriented integration, not invention of either.

## Remaining work and author decisions

Remaining work comprises a substantive scope edit, controlled local CPU measurements, optimization ablation, provenance/comparator audit, verified literature review, and release preparation. **Reliable effort estimates are not established by the retained records.** Experimental duration depends on the selected workload and repetition plan; that plan should precede scheduling.

Chirayu must decide:

- Whether to narrow the paper.
- Whether to authorize the local CPU benchmark and ablation.
- Which affiliation to use, and whether VUB, PhD, employment, or funding obligations require permission for outside publication.
- Whether to email organizers about any specific unresolved publication or artifact restriction.

The public terms support publication in principle. They do not settle institutional obligations or every third-party file.

## Recommended next steps

- **Choose the focused simulator framing** and confirm authorship, affiliation, and institutional obligations.
- **Authorize a controlled local benchmark and bounded ablation**, with raw repetitions and frozen provenance. No model endpoint is required.
- **Finalize related work, rights, and disclosure**, then review the rendered manuscript and release artifact before approving arXiv submission.

**Checked:** current manuscript, tables, bibliography, and referee-response checklist; earlier simulator and forecasting evidence; published competition terms and licensing documents. Compilation and exact table regeneration are conductor-verified. No new experiments, submissions, or file changes were performed for this report.

## Conductor's note

One correction to the report's "Where Claude and Codex differ" section: the Claude referee (paper-verify) answered the same questions separately and **also recommended narrowing to the simulator paper**, with Tracks 1 and 2 folded into a short lessons section, about 1 to 2 weeks of focused work, and no posting before the controlled benchmark exists. So the two agents agree on scope; only the current draft still carries the three-track framing. The Agenthon terms and licensing quotes were checked by the conductor on agenthon.net on 2026-11-03.
