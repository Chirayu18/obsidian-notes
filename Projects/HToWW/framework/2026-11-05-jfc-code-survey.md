---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# JFC code survey: usefulness for the existing HToWW analysis

**Verdict: adapt a few review instructions; do not migrate the analysis to JFC on the strength of this survey.** JFC explicitly asks reviewers to investigate implementation bugs, including wrong systematic propagation and stale numerical outputs. Its public repository supplies useful review procedures, but no demonstrated improvement over Chirayu's current code-based review and no ready-made HToWW bug detector. The hidden-truth HEPEXBENCH demonstration from the workshop is not implemented in this checkout.

**Adoption follow-up, 2026-11-05:** Chirayu authorised adoption of the useful parts. They are now implemented as [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|the HToWW review protocol]] and the `$htoww-review` skill. This survey remains the code-inspection evidence; the follow-up records what was adopted and its validation limits.

This is an **agent-reported code inspection with small local software checks**, not a test of JFC's agents on HToWW. No agent was run through JFC, no model endpoint was called, and no CERN data or internal analysis material was sent to an external service. The survey supplements [[Projects/CombineAgent/evaluations/2026-11-05-indico-1716863-survey|the event survey]] with implementation evidence; the event inventory remains applicable.

## Source and scope

Inspected public [jfc-mit/jfc](https://github.com/jfc-mit/jfc) `main` at **`9eecb0e0b4c95c362053ad6b121760b47379bc54`**, fetched on 2026-11-05. `git log -1` reports 2026-03-31, subject `docs: add full name Just Furnish Context (JFC) and paper-aligned description`. The code-specific conclusions below refer to this revision, not unpublished workshop code or every version of the authors' system.

Read the scaffolder, reviewer/fixer/investigator definitions, orchestration and review methodology, processing/inference templates, search conventions, plotting linter, tool/environment configuration, and the document helper's structure and entrypoint. Exact executable inventory: **four Python files**, with **two byte-identical plot linters**; the others are the scaffolder and a TeX postprocessor. The tracked repository contains **55 files, including 46 Markdown files** (`git ls-files` and local extension counts). No committed automated test suite, CI workflow, HToWW adapter, or CMS Combine/datacard execution integration was found in this revision. The preferred fit tools are pyhf/cabinetry; the columnar stack has useful conceptual overlap with HToWW. [Tool choices][tools], [environment template][environment].

## What it actually provides

| Component | What is present | Consequence for Chirayu |
|---|---|---|
| Scaffolder | Python creates a new five-phase analysis tree, instructions, links to conventions/roles, configuration stub and a git repository. | Useful for starting a new analysis; there is no supplied command to import and audit the existing `higgscharm` tree. [Implementation][scaffold] |
| Review system | Markdown prompts for physics, critical and constructive reviewers, plot/bibliography/rendering reviewers, an arbiter, a fixer and an investigator. | Can structure a serious review if the agent follows the instructions and has the real code and evidence. These are not deterministic proof or bug-detection algorithms. [Critical reviewer][critical], [review protocol][review] |
| Orchestration | The Claude orchestrator is instructed to execute, review, fix, commit and advance through phases. The automation appendix explicitly calls its shell block non-runnable pseudocode. | The repository does not provide a separate controller that mechanically verifies all physics gates before advancement. [Automation appendix][automation] |
| Physics validation | Requirements for signal injection, closure, nuisance impacts, source completeness, independent checks and fit diagnostics. | The agent must write and run analysis-specific implementations. The repository has no generic executable HToWW injection/coverage test. [Search conventions][search], [inference template][inference] |
| Mechanical helper | Regex-based plotting-style linter and TeX postprocessor. | Real executable checks, with a narrow scope. They do not verify selections, event weights, scale-factor semantics or datacards. [Plot linter][linter] |
| Experiment knowledge | Documentation assumes an external SciTreeRAG/LEP corpus and gives example MCP configuration. | The MCP server/index and a CMS Run-3 HToWW knowledge base are not bundled. It cannot know Chirayu's approved prescriptions without being given them. [Integration appendix][integration] |
| Access/gates | An `.analysis_config` stub mentions an isolation hook; no implementation of that hook or Claude settings registering it is shipped/generated here. Human unblinding approval is an instruction. | Retain the actual runtime's permissions and Chirayu's existing protocol; the stub is not evidence of enforced filesystem or data-access isolation. [Scaffolder lines 127–137][scaffold] |

## Can it find the minor bugs Chirayu means?

**Yes, its review prompts are intended to investigate code-level errors as well as physics methodology.** This is more concrete than merely asking a model to read a finished note. In particular:

- The critical reviewer must check that validation was actually run, follow each systematic through the analysis, compare saved numerical results with prose, and support verification claims with a number, file location or computation. It explicitly requests focused investigations when correctness requires tracing several files. These are instructions to the reviewing model, not prewritten analyses of the target code. [Critical reviewer lines 60–92, 155–206][critical].
- The inference checklist asks whether a varied input really changes, whether its effect is present, whether its direction is expected and whether generator/reconstruction levels are mixed. [Inference template lines 194–203][inference].
- The investigator records the origin of an issue and its downstream effects; the fixer makes a targeted change, rechecks it, checks related code and updates affected results. [Investigator][investigator], [fixer][fixer].

For HToWW, the following are **proposed applications**, not demonstrated JFC findings:

| Existing concern | Useful JFC-style question | What still has to be implemented or supplied |
|---|---|---|
| Shared jet ordering differs from derived leading-jet variables | Do the direct saved jet arrays and derived jet variables use the same corrected ordering? Trace the producer through the writer. | A synthetic ordering case and a comparison of stored columns. No JFC array-ordering checker is shipped. |
| PDF/alphaS repair changes inclusive shifts or returns unit weights | Does each configured nuisance have a real input, the right PDF-set interpretation and the intended effect in saved templates? | Branch metadata, LHAPDF-set information, nominal/varied weight calculations and process-by-nuisance output checks. Missing alphaS members require a physics prescription; an agent cannot repair their absence by inventing weights. |
| Lepton SF factorisation | Does the implemented product match what each SF actually measures? | Thomas's authoritative provenance/conditional-efficiency definitions. A generic reviewer cannot establish this from plausible names alone. |
| Selection changed while the event MVA remains from the old selection | Which downstream training, templates and results consume the changed selection? | Model/training provenance and a bounded downstream-validation plan. JFC does not supply retrained weights. |
| Missing systematic column silently falls back to nominal | Is every expected sample/process/nuisance represented by a real varied output, with documented exceptions? | A completeness table derived from the workflow and produced artifacts; equality to nominal must be explained, not automatically treated as proof of correctness. |

These cases are drawn from [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|the independent review]] and [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|the current full-fix handoff]]. The former already records code tracing and regression tests that caught the shared-jet ordering and PDF-only combined-variation defects. **The current workflow already performs the kind of investigation JFC requests.** This survey did not re-run or independently validate those HToWW checks. There is no measured JFC-versus-current-review comparison here.

## What needs adaptation before using its rules

1. **NLO weights:** the critical reviewer requests non-negative yields and a monotonically decreasing cutflow without stating a weighted/unweighted distinction. That must not be applied mechanically to signed-weight intermediate quantities. Simple counterexample: event weights `+2, -1` sum to `1`; a cut removing the negative-weight event leaves `2`. The weighted cutflow increased although the event selection removed an event. This is an algebraic counterexample to an unconditional rule, not evidence that negative final likelihood expectations are acceptable. [Critical reviewer lines 111–125][critical].
2. **Fit boundaries:** the general phase specification treats any fitted parameter near a boundary as needing wider bounds or a qualified uncertainty, while the search conventions intentionally require a non-negative signal strength. A background-only fit can legitimately reach that physical boundary. A reviewer must apply the actual test-statistic and interval construction rather than automatically widen the signal-strength range. [Phase specification lines 681–692][phases], [search conventions lines 30–34][search].
3. **Heuristics versus diagnoses:** fixed rules about data/MC disagreement, pulls and zero variation are useful investigation triggers, not universal demonstrations of a bug. A legitimate absent source, normalization-only nuisance, statistical fluctuation or deterministic self-consistency test needs the right interpretation. The reviewer should distinguish evidence of a software defect from a request for physics judgement.
4. **Infrastructure and authority:** JFC defaults to Pixi, pyhf/cabinetry and SLURM, expects new per-phase artifacts, and prescribes a 10% partial-unblinding stage. HToWW uses the established lxplus/container/Condor/Combine setup and existing approval rules. Adopt review questions without changing the production stack or exposing data under a new default. [Tools][tools], [blinding protocol][blinding], [root template][root].
5. **Review volume:** full adoption requires repeated multi-reviewer panels and compiled notes before some gates. It may add cost and review noise. Different role prompts do not establish independent model error, and the template explicitly favours Opus for all spawned agents. No incremental bug-detection precision/recall benchmark for an existing CMS analysis is supplied in this checkout. [Root template lines 125–135][root].

## Checks actually run

All checks used public source and synthetic scratch inputs under `/tmp`; no dependencies were installed and no analysis environment was changed. Results: `/tmp/jfc-survey-checks-r8eklxif/results.json`. The public checkout is `/tmp/jfc-survey-20261105/`.

- Parsed all four Python files with `ast.parse`: passed. This is syntax checking, not runtime/physics validation.
- Ran `python src/scaffold_analysis.py <scratch-dir> --type measurement` and `--type search`: both exited 0 and generated the root plus five phase instruction files and resolving role links. No analysis was executed.
- Parsed each generated `pixi.toml`: the only initial tasks are `py`, `build-pdf` and `lint-plots`; `all` is an example to be implemented by the analysis author/agent, not a ready-to-run analysis pipeline. The document task invokes `tectonic` although the template does not declare it as a dependency; a clean environment needs that supplied. A full environment/PDF build was not attempted.
- Examined generated hook-related paths: only the normal git hook directory was present, not a Claude isolation/gate implementation. The `.analysis_config` comment does not create one.
- Scope check: the shipped plot linter returned 0 on a deliberately wrong synthetic normalization function (`xsec * lumi * generated_sumw`, multiplying instead of dividing by the generated sum). Adding the banned style call `ax.set_title(...)` made it return 1. This confirms that the executable linter checks plotting rules, not weight algebra; it is **not** a failure to meet its advertised plotting scope and says nothing about whether an LLM reviewer would catch that bug.
- Searched all tracked Python/Markdown/TOML source for HEPEXBENCH: no matches. Also inspected the executable and tracked-file inventory; no sealed-world generator/evaluator or automatic CMS Combine integration was found. The workshop's benchmark should not be confused with the public framework available here.

## Recommendation

**For HToWW:** use a compact, analysis-specific version of the critical-review and systematic-implementation checklist in the current worker/reviewer arrangement. The useful output is a table connecting **approved prescription → implementation location → independently computed check → saved output → status**, with unknowns retained as unknowns. Require each code-bug finding to include a reproducible failing case and distinguish it from a missing physics input. One finding must not authorize a wholesale rewrite or reopen settled decisions.

**For CombineAgent:** no demonstrated addition to the nugget scoring method. JFC evaluates/builds complete analyses through prompted reviews; it supplies neither a new nugget scorer nor a ready-made Combine execution oracle. [[Projects/CombineAgent/evaluations/2026-10-14-nugget-evaluation-research|The nugget design]] already includes repeated attempts, negative criteria, paired comparisons, failure accounting and judge calibration, with cross-family judge results recorded in [[Projects/CombineAgent/evaluations/2026-10-21-omp-qwen-baseline|the baseline]].

**Before investing in JFC integration:** a bounded retrospective comparison would be informative: give a reviewer an earlier snapshot containing known defects, withhold the defect list, and compare the current review brief against an adapted JFC brief under the same model/tools/budget. Score correct findings, false positives, evidence quality and human review time. Do not count a checklist item as a detected bug. This survey did not run that model-based experiment.

The defensible conclusion is that **JFC offers reusable review discipline, while improved bug detection for Chirayu remains unproven**. The most relevant parts can be adopted without installing its full workflow.

[scaffold]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/scaffold_analysis.py#L77
[critical]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/agents/critical_reviewer.md#L60
[review]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/06-review.md#L89
[automation]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/appendix-automation.md#L7
[search]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/conventions/search.md#L98
[inference]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/templates/phase4_claude.md#L194
[linter]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/conventions/lint_plots.py#L34
[tools]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/07-tools.md#L3
[environment]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/templates/pixi.toml#L44
[integration]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/appendix-integration.md#L7
[investigator]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/agents/investigator.md#L42
[fixer]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/agents/fixer.md#L61
[phases]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/03-phases.md#L681
[blinding]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/methodology/04-blinding.md#L8
[root]: https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/templates/root_claude.md#L60
