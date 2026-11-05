---
tags: [meta, reorganisation]
status: implemented
date: 2026-11-05
source: laptop
---

# Vault reorganisation — 2026-11-05

## Chirayu’s instructions (verbatim)

- “Reorgaize my whole vault now please”
- “You can parallelize this work, spliiting into multiple opus 5.5 subabgests”
- “After you have reorganised the vault. Push it on a new branch ( keep gitignore and all , dont push png files )”
- “Also take things from older claude's memory and put in meta, reorgaized”
- “Okay forget the slide instruction for now... Do that later... For now, just continue”
- PDF policy: “Keep every PDF local-only”
- Later resumption: “Lauch a opus 5.5 agent yourself for the slides work”

## Organization

- HToWW: analysis-strategy, combine-systematics, selection-and-mva, negative-weights, samples-and-production, framework, analysis-note, talks.
- Flashjet: clustering-validation, performance, jet-tagging, learned-clustering, kappa-hce, talks.
- DigiMorphing: publication, unpacker-review, phase2-morphing.
- CombineAgent: separate project with setup, question set, evaluations and supporting assets.
- AgentHarness and PromptTooling: moved to Meta. Authored Athens/autoMCStats slide material moved from References to its research stream; external Tracker DPG PDF moved into References.
- Personal chat export is kept unopened under Personal/Chavi. Empty placeholders and the unattributed TeX failure log are retained in Inbox/_history.
- Topic indexes were added throughout; original decks and their asset bundles are preserved. No new scientific decks were generated during this structural pass.

Exact per-file moves, reasons and initial hashes: `Meta/reorg/vault-20261105.tsv`. HToWW detail: [[Meta/reorg/HToWW-plan]].

## Preservation and publication policy

- Original inventory: 1,446 tracked regular files + 157 local-only supporting files = **1,603 original files**, plus one pre-existing gitlink. All 1,603 files remain on disk at their unique mapped destination.
- Moves: **933 tracked files + 64 local-only supporting files = 997**. No file content was deleted. Only empty old directories were removed.
- Binary SHA256 values are unchanged. Original text changes are logged navigation/path rewrites, plus the keeper-owned root guide, attachment default and .gitignore updates. Recorded evaluation JSON outputs were kept byte-identical.
- Original Archive, private notes and independent Overleaf/analysis checkouts were not moved or edited. Pre-existing Meta/setup.md edits and the thread-archive TSV were preserved outside this commit.
- Existing .gitignore content is retained. All PNG and PDF files are kept locally and ignored; 336 PNG paths and 129 PDF paths were removed from the tracked publication tree. A separate publication commit is based directly on current ssh/master, so earlier unpushed setup commits do not introduce PNG blobs through their history. Previously published remote history is not rewritten.
- Decks and reference PDFs remain usable locally; a fresh remote clone needs PNG/PDF assets separately from EOS or their source links. Text deck sources, SVGs, metadata and reference catalogs remain in the branch.

## Older Claude memory

[[Meta/claude-memory/README]] indexes **83 imported source Markdown notes** by topic. `Meta/claude-memory/sources.json` records source and imported hashes, dates and navigation rewrites. Source memories remain unchanged; zero credential matches were found by the local import screening. These are historical agent records; current roles/setup take precedence and scientific claims remain agent-reported.

The attempted external Opus memory-import delegation was rejected by automatic approval review. The actual import, categorization and credential screening ran locally without transmitting raw memory contents to a reviewer.

## Slide instructions

The collected source handoff is [[Meta/slides/source-handoff]]. The resumed Opus task writes [[Meta/slides/instructions]] using the listed current-vault slide sources only. Original home-directory memory access was excluded after automatic approval review; no credentials or original memory corpus were passed to that agent.

## Ambiguous — needs Chirayu

1. KappaHCE in jet tagging: the original user task remains in HToWW selection-and-mva, with a cross-link from Flashjet/kappa-hce; confirm its current owner/status if still live.
2. Inbox: four empty placeholders, grade_report.py and texput.log are retained; their intended purpose is not clear.
3. Existing personal chat ZIP remains tracked as before, now under Personal/Chavi. Decide separately whether it should become local-only; no history removal was performed.
4. Existing .omp/config.yml still selects Hindsight although the setup says it is retired. This separate branch does not validate that configuration or merge it into master.
5. Missing historical link targets/plots cannot be recreated honestly from filenames; see the issue inventory. Four blank notes are deliberately preserved in Inbox/_history.

## Possible missing info from worker threads

No earlier keeper/last-run tag existed, so this is a baseline run rather than a complete since-tag audit. The latest completed records were sampled. Gridpack recovery produced vault decks; the following completed workers may have information still recorded chiefly in chat:

- Run-B inputs: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:526f75a45954a1ce6db05f30898aa82463a5664c2798ababadc800e836adf493>. Its final explicitly reports no repo edits.
- Full-fix runs A/B: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:0a085f5f6123e902dae945a412fbaac27624ff7a2dd345a25861a529c4e14fb5>. Its final reports uncommitted analysis changes and unresolved scientific decisions. No analysis code or jobs were touched by this keeper run.

## Validation

Validation commands: `/tmp/keeper_validate.py` (inventory/hash/edge assertions), `python3 Meta/tools/vault_links.py`, and `git diff --check`. The link checker validates local target files, including ignored local PNG assets and declared TeX graphic paths; it does not claim to validate all heading/block anchors, external URLs, scientific values or executable source-repository examples.


- Preservation: **1,603 original files before = 1,603 after**; unique destinations and all original binary hashes match. The pre-existing gitlink remains in place.
- **910 original resolved link expectations preserved; zero lost or retargeted edges; zero newly broken links.**
- Before: 111 unresolved/case-ambiguous references. After move/repair/memory import: **79 remaining legacy unresolved references** (some old memory links now resolve to the imported historical records). These are reported in `link-issues-20261105.tsv`; this is not a claim of zero legacy broken links.
- Four original blank placeholders remain unchanged in Inbox/_history.
- `path-rewrites-20261105.tsv` logs the navigation edits; `Meta/claude-memory/sources.json` separately logs memory-source links and the two explicitly annotated absent source memories.
- Local search rebuilt successfully (notes + papers); 346 cached code-tier entries from the old index were pruned because the code tier is disabled.
- Publication is a new branch, `keeper/vault-organised-20261105`; master is not merged or force-pushed. PNG/PDF files remain local-only.

- Python syntax checked for 15 changed/new helper and path-updated scripts; copied plot/analysis scripts were not executed. Authored/reorganized files pass whitespace checks. Historical memory-source whitespace is preserved verbatim (32 inherited warnings), with hashes retained.
- Slide instructions completed by the requested Opus 5.5 agent; [[Meta/slides/instructions]] is marked pending Chirayu review and keeps user quotes distinct from recorded/inferred guidance.
