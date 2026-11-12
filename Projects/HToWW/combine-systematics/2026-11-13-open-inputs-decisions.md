---
tags: [reference, decision]
status: active
date: 2026-11-13
source: laptop
---

# Open inputs before the Arm A result: Chirayu's decisions (13 Nov 2026)

Chirayu's answers (verbatim, 13 Nov) to the list of items that remain after the conveners agree on the prescriptions. They update the open items in [[2026-11-12-current-ab-systematics-status]] and [[2026-11-12-final-cards-todo]].

| Item | Chirayu (verbatim) | What it means |
|---|---|---|
| c-tag calibration | "waiting for Livio (okay)" | External input expected from Livio; c-tag stays provisional until then. |
| Sourced H+c αS rate | "we can ask that" | Question to the theory/sample contacts; see [[2026-11-12-hplusc-alphas-rate-sources]]. |
| H+b PDF⊕αS and overlap with the 5% Higgs rate | "we can ask that" | Same: ask, then install without double counting. |
| BR terms on the merged Higgs background | "huh" | Explained by the keeper: the 1% BR(H→WW) and 1% BR(H→ττ) lnN currently act on the whole merged `higgsbkg`, which mixes WW and ττ decays. They should be scaled to each decay component's share per channel (or the process split). Small (1%), our own card-builder fix. Not yet decided or implemented. |
| ttH→ττ coverage | "yes , this was the issue Thomas had no?" | Yes: the forwarded Tahys/Thomas discussion with Ming-Yan's reply (an inclusive ttH→non-bb sample already contains ττ). Our open point is the converse: `ttHnonBB` is the exclusive cc/γγ/Zγ samples, so ττ may be uncovered. Check without double counting ([[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-direct-continuation-training-launch]]). |
| negrw closure in the final fit bins | "ignore" | Dropped from the to-do list for the result. |
| hDamp | "we will implement it" | To be implemented (was deferred on 12 Nov). |
| Empty shifted-template policy | "okay" | Acknowledged as listed; current default is fallback to nominal with a log unless `object_shift_empty_fallback: error` is set. |

The November talk's closing slide ([deck](../talks/2026-11-13-november-update/deck/index.html#/open)) now splits these into "Inputs we will ask for", "Expected" and "We implement".
