---
tags: [meta, slides]
status: active
date: 2026-11-05
source: laptop
---
# Shared Reveal.js assets

Local runtime for keeper progress decks. Reveal.js 5.2.0 core, reset and CSS were copied byte-for-byte from the existing HToWW gridpack deck; the Markdown plugin was copied byte-for-byte from the installed Obsidian Slides Extended plugin. No network download or CDN is used. Original copies are unchanged.

`sources.json` records source paths and SHA-256 hashes. The core retains its embedded upstream copyright notice. The Markdown bundle includes its upstream parser and plugin; upstream source: https://github.com/hakimel/reveal.js (MIT) and https://github.com/markedjs/marked (MIT).

The keeper deck references this directory with relative paths. This runtime is shared; scientific content and source notes stay in each subproject.
