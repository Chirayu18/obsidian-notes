---
tags:
  - hww
status: active
pinned: false
related:
date: 2026-06-30
---

# Untitled

> `BUTTON[toggle-status, toggle-pin]`  `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

---

## Commands

```bash

```

---

## Tasks

- [x]  [completion:: 2026-06-30]

---

## Log
- Thomas
I have some results for getting the electron WP from the main HWW analysis with some tables in attachment (cutflows for data, signal and total bkg + S/B and S/sqrt(B) going from old wps to the one where new muon wp is taken, to the one where new electron and muon wp are taken) . It does give a drastic cut in events, as said before, but the S/B is better, although the S/sqrt(B) is worse (76% of the previous value, with the original WPs). I do not have plots for it yet, as there is an issue regarding the ggH and V+Jets samples. There the [#events](https://mattermost.web.cern.ch/cms-exp/channels/hc-with-h-ww-2l-2#) after the selection completely drops to zero and the framework does not save any variations in that case. So plotting can be something that can be fixed rather soon, but more fundamentally I feel like we should also include uncertainties/systematics on the zero events, right? I am not sure though how that would need to be implemented yet.![[Screenshot 2026-06-29 at 12.16.26.png]]
![[Screenshot 2026-06-29 at 12.16.32.png]]
![[Screenshot 2026-06-29 at 12.16.40.png]]![[Screenshot 2026-06-29 at 12.16.29.png]]- I am also a bit confused by how at the last cut for the signal (H+c) events, the [#events](https://mattermost.web.cern.ch/cms-exp/channels/hc-with-h-ww-2l-2#) with only the new muon wp is higher than for the old wps, as the cut before leaves less events for the new wp. Could that be that new dilepton pairs are made, due to new muon wp and that we therefore have different dilepton masses, leaving now more events/dilepton lpairs surviving the dilepton mass cut?