---
source: Hindsight research bank document `workflow:current`
exported: 2026-11-05
status: superseded
note: verbatim export before Hindsight was retired; dated snapshot, not live state
---

# Current workflow
Revision: streamlined-2. Updated: 2026-11-04T12:21:09.952492+00:00.

## How Chirayu uses it
Start any new project work by messaging that project's one pinned Claude Sonnet/low lead. The lead searches Hindsight for its own project, answers simple stored-status questions, records/tracks tasks, and reuses or launches a visible top-level worker when substantive work is needed. The worker knows its lead and reports meaningful checkpoints, completion and blockers to it. Chirayu may then speak directly with that worker. The main Sonnet/low conductor handles cross-project tracking and communication, not substantive science. Exactly one coordinator drives each task; no standing reviewer or acknowledgment loops.

## Records and identity
Hindsight research at http://127.0.0.1:8888 is authoritative for task state, open decisions and Night logs. Exact documents: workspace:catalog, project:<Project>:status, night-log:YYYY-MM-DD. One designated writer; read before replacing a current document and read back before claiming success. Check a timed-out write before retrying; there is no verified compare-and-swap lock. Recall and knowledge pages are discovery/summaries, not exact task state or proof of live jobs. Do not create Markdown research notes or status boards or require Obsidian. Existing notes remain historical evidence; CLAUDE.md role instructions intentionally remain files.

Bind role/project to the stable native thread ID and workspace:catalog, never a display title. Explicit role briefs win. Each worker brief names its lead/coordinator link, task ID, project status ID, allowed paths, evidence and acceptance check. Default cwd /home/cgupta/obsidian-notes; main conductor cwd /home/cgupta/ai-orchestrator. HToWW's restored label remained ◆ Lead · HToWW through the corrective run. A permanent native title-lock option was not exposed by installed T3 tools/CLI; do not claim a hard lock or add a rename watcher.

## Research record
New decks default to editable Reveal.js HTML exportable to PDF. Preserve local assets for private material, stable slide IDs, source revision, rendered/inspected PDF and evidence appendix (exact tables, commands, configurations, assumptions, provenance). Hindsight links to deck revisions/slides/PDFs. No Beamer/PowerPoint default or implicit conversion of old decks. Original PDFs/code/data stay in established storage. No new exporter or empty decks.

## Scheduled check-ins
The user removed monthly project/task check-ins. The native monthly schedule was deleted and both conductor/workspace schedule inventories returned empty. Do not recreate periodic inactivity reviews without a new explicit request. Track tasks through user requests and meaningful worker events.

## Native integrations and verified limits
Both Claude workspace projects now locally register the maintained bank-scoped HTTP MCP server under hindsight: http://127.0.0.1:8888/mcp/research/. Coding-agent recall/retention hooks are preserved. The installed official MCP SDK listed 36 tools and get_document returned the exact workflow text with matching SHA256. Existing Claude sessions retain the old eight-tool coding-agent MCP surface: the main conductor's subsequent live check could not find get_document. Those sessions need native MCP reconnection/session refresh before exact-record coordination is operational; no API/service restart was performed and no private-token workaround was used.

After explicit bootstrap, the HToWW lead actually read its role, used native discovery and launched one pi/openai-codex read-only HToWW worker at compatible approval-required/default modes, with the exact lead link in its brief. The worker has a native approval pending; its audit result is not claimed complete. The main full-access conductor and approval-required leads still have asymmetric callback ceilings; native permissions must be respected. Pi can leave completed output marked running: require current-request checkpoint identity and prior native turn closure before continuation, and do not poll forever or double-drive.

## Boundaries
Use native T3/Hindsight and maintained slide tools only. No custom orchestrator code, registry, watcher, sync engine or API client. Codex through pi/openai-codex, not codex exec or a Claude bridge. Check quota before substantial dispatch and after quota errors; no exhausted-provider retries or silent substitutions. Sonnet/low reliability is not benchmarked. No push, merge, job submission, data deletion or service restart without explicit user OK. Night logs remain private/local in Hindsight, without automatic Git commits/pushes. Notify only when the user must act. Never retain secrets, expand permissions/spending autonomously or treat internal research decks as public-approved CMS talks.

