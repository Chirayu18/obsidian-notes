---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# HToWW review protocol adopted from the JFC survey

**Adopted review instructions; effectiveness on a new analysis review is unvalidated.** Chirayu authorised adoption on 2026-11-05: “Adopt what you can adopt then”. This brief makes the useful parts of [[Projects/HToWW/framework/2026-11-05-jfc-code-survey|the JFC code survey]] reusable within the existing worker/reviewer workflow. It adds review requirements, not a replacement analysis framework.

Use `$htoww-review` for an HToWW correctness review. Its source is [[Projects/HToWW/framework/review/htoww-review/SKILL|the review skill]] and its repository discovery entry is `.agents/skills/htoww-review`. A worker using another provider can read this brief directly. The skill does not change that provider's global instructions or the conductor/keeper roles.

## Establish the review boundary

Read the task and applicable vault/repository instructions. Identify the repository, branch, HEAD, uncommitted diff and files in scope. Use `scripts/rag/vault-search` for vault context, then read the current decision records and their latest updates. Use the actual environment and setup already established for the analysis.

Record a short review manifest: source revision and diff, workflow/configuration, sample/era, input identities, relevant model/calibration versions, and commands/check outputs. Record seeds and execution layout when comparing numerical output. Keep checks proportional to the change; a focused defect does not require a new full production.

The review leaves analysis files unchanged unless fixes are authorised by the task. Use bounded scratch checks where appropriate and record their paths. Inherit existing permissions for jobs, pushes, merges, unblinding, external services and data access. This brief supplies no additional authority and does not require spawning agents.

## Trace prescriptions into evidence

For each material concern, connect the authoritative prescription to the implementation and an observable output. Use this table, omitting columns only when genuinely inapplicable:

| Item / applicability | Approved prescription and source/date | Implementation location and revision | Independent check / exact command | Observed result and saved output | Status / remaining uncertainty |
|---|---|---|---|---|---|

Keep recorded user decisions in force. Distinguish the source paper's statement from a user-selected convention. If provenance is missing or conflicting, preserve that uncertainty and continue independent work; do not silently substitute a textbook default or invent a correction.

**Existing test logs (standing rule, Chirayu, 2026-11-05; [[Projects/HToWW/2026-11-05-decision-review-trust-test-logs|standing decision]]):** do not rerun unit tests that were already run on the same code; cite the existing log instead. Rerun only if the code under test changed after the logged run (compare file mtimes or SHA256SUMS against the log time) or no log exists. Mark such results "author-run test log, not re-executed by the reviewer"; never call them independently verified. Chirayu, verbatim: "Trust the log... Keep it a standing decision during reviews, dont run same unit tests on the same code again".

Use clear evidence states: **checked** (state precisely what a command or source establishes), **defect reproduced**, **source/physics input needed**, **author-run log (not re-executed)**, **not run**, or **outside this review's scope**. Passing a software check establishes only its exercised boundary. The overall research record remains agent-reported until independently validated under the vault's rules.

## Check the relevant parts of the implementation

Select checks needed for the task; do not turn this list into a mandatory full-analysis rerun.

- **Object and event semantics:** follow branches, units, masks, correction order, signs, and sorting through consumers and stored columns. Check that a locally corrected/sorted collection is also the collection used by downstream code. Use a small independently specified example where it can distinguish the intended behaviour from the defect.
- **Weights and normalisation:** trace the source cross section/branching factors, generated sum of weights and per-event correction into the saved result. Keep inclusive normalisation and acceptance/shape effects distinct. Compare against a separately calculated reference rather than reproducing the implementation's formula without checking its meaning.
- **Systematic completeness:** derive the expected sample/process-by-nuisance set from the active configuration and applicability rules. Compare it with input metadata, correction dispatch and produced columns/templates. Record exceptions explicitly. Check for missing-column fallback, nonfinite replacement and variations silently equal to nominal.
- **Systematic effects:** inspect nominal and varied inputs, evaluation level (generator/reconstruction), normalisation convention, migration, direction where predictable and resulting outputs. An absent input or zero effect prompts investigation; it is not automatically a software defect. PDF-only inputs cannot supply absent alphaS members. A legitimate normalisation-only nuisance can be flat across bins.
- **Calibrations and models:** verify object definitions, era coverage, input features, working points and what each SF measures. Separate conditional and inclusive factors. Missing SF provenance is a request for authoritative input, not permission to infer factorisation from a filename. Trace selection changes into training/model compatibility.
- **Numerical comparisons:** compare event identities, columns/schema, weights and relevant distributions with controlled seeds/layout when equivalence is claimed. An unseeded baseline cannot support a strict event-for-event equivalence claim. Record both raw event counts and signed-weight summaries when useful.
- **Statistical model:** when inference is in scope, check nuisance applicability/correlation, templates and datacard/workspace against the active prescription. Use independent signal-injection, null, closure or coverage checks when required by the task. Identify when pseudo-data and fitting share assumptions that could conceal a defect. Running those studies requires the established environment and task authority.
- **Documentation:** compare reported numbers and plots with actual saved artifacts from the reviewed revision. A test described in prose needs an execution record; a proposed test remains not run.

## Avoid inherited false alarms

Unweighted nested-cut event counts should not increase. Signed-weight cutflows can: weights `+2, -1` sum to `1`, and selecting only the positive event leaves `2`. Apply positivity requirements at the appropriate final statistical-model boundary, not indiscriminately to signed-weight intermediates.

A signal strength at a physical boundary, a large nuisance pull, a flat shift or a data/MC discrepancy needs interpretation using the actual model and test construction. Do not automatically widen physical parameter bounds, impose a universal percentage threshold or call these observations bugs without evidence. Deterministic self-consistency checks and independent physics validation serve different purposes; label each correctly.

Keep the existing CMS analysis/blinding procedure, lxplus/container/Condor/Combine setup and reviewer arrangement. JFC's Pixi/SLURM/pyhf defaults, fixed partial-unblinding fraction and multi-agent panels are not adopted.

## Make findings reproducible and verify fixes

Each finding should identify the trigger, observed behaviour, expected behaviour and its authority, file/line and revision, affected outputs, and the smallest practical reproduction or diagnostic. Classify missing physics input separately from an implementation defect. If execution is unavailable, state that the finding is based on source inspection and identify the decisive check still needed.

After reproducing a defect, inspect related uses in the relevant code path: a sorting fix may affect both leading objects and saved arrays; a broken nuisance branch may have a parallel PDF-only path. Keep that inspection within the review's scope and report what was checked.

For an authorised fix, make the minimum effective change, run the relevant regression/equivalence checks, and recheck the original finding against the changed revision. Trace downstream consumers and record which need rerunning and why. For example, a lepton-selection change can affect event-MVA training, templates, datacards and limits. Do not claim those artifacts are updated merely because the code changed. Never rerun a production or alter a settled physics prescription solely to close a review finding.

Finish with the findings, evidence table, checks actually run, limitations, downstream work and any concrete decision needed. Preserve existing failures as failures; do not accept a narrative explanation as a substitute for contradictory output.

## Adoption record and sources

Implemented as an instruction-only skill plus this provider-neutral brief. No analysis code, model, scoring method, production configuration, role file or keeper-owned index was changed by this adoption. No claim is made that these instructions detect more bugs than the existing independent review. CombineAgent's nugget method receives no change.

Validation on 2026-11-05: the bundled skill creator's `scripts/quick_validate.py` accepted the skill. The repository discovery symlink and its target, the relative protocol link and all vault links were checked. Manual review of the instructions covered signed-weight cutflows, a physical signal-strength boundary, absent alphaS members and an unseeded comparison; these are design checks, not an independent agent benchmark. No new analysis review or model-based effectiveness trial was run during adoption.

The adopted ideas are evidence-backed review, systematic implementation tracing, bounded related-code checks, explicit downstream impact and verification of fixes. These instructions are newly written for HToWW, informed by the inspected JFC revision `9eecb0e0b4c95c362053ad6b121760b47379bc54`: [critical reviewer](https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/agents/critical_reviewer.md), [systematic implementation checklist](https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/templates/phase4_claude.md#L194), and [fix protocol](https://github.com/jfc-mit/jfc/blob/9eecb0e0b4c95c362053ad6b121760b47379bc54/src/agents/fixer.md#L61). HToWW-specific qualifications follow the survey and [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|the existing independent review]].

Discovery uses the repository skill location and symlink support documented in the [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills). Filesystem registration and structural validation do not prove automatic selection in every client or improved scientific review quality.
