---
name: check-cms-public-status
description: "How to verify whether a CMS result is public (for public talks) — listing pages, INSPIRE, and Indico anonymous-vs-token comparison"
metadata:
  node_type: memory
  type: reference
  originSessionId: 44979bb5-dbf6-44f6-80e6-8765822550fa
  modified: 2026-10-17T06:33:47.768Z
---

To decide whether a CMS result may go in a public talk, check in this order (verified working 2026-10-17):

1. CMS group listings (papers and PAS, with dates and journal refs): `https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG/index.html` and `.../preliminary-results/HIG/index.html` (swap HIG for BTV, TOP, SMP...). A single result page is `.../publications/HIG-XX-YYY/index.html`; 404 on both trees = not public under that ID (but it may exist under another ID, so also scan the listing).
2. INSPIRE API (indexes arXiv, PAS, proceedings): `https://inspirehep.net/api/literature?q=collaboration:CMS and t charm and t higgs and de > 2025-01-01&sort=mostrecent`. Prefer it to the arXiv API, which rate-limits (HTTP 429) and then returns 0 entries silently.
3. Indico: compare the export API anonymously vs with `~/.indico_token`. Contributions/attachments that appear only with the token are CMS-internal. For the 2nd CMS Higgs-charm workshop (event 1645713): 22 contributions / 20 attachments anonymous vs 46 / 41 with token; the "Boosted ggH/VBF/VH(cc)" talk is token-only.

Recent CMS proceedings are a cross-check: F. Heyen, PoS EPS-HEP2025 392 (Jan 2026) states all CMS Higgs-charm analyses use Run 2 only. Related: [[Meta/claude-memory/_history/slides/vault/higgs2026-hcharm-talk|higgs2026-hcharm-talk]], [[Meta/claude-memory/_history/slides/vault/hww-fs-private-results-not-for-ppt|hww-fs-private-results-not-for-ppt]].
