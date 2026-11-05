---
name: hww-ctag2d-sf-total-decision
description: HToWW 2D ctag SF uses up_Total/down_Total as ONE nuisance now; full decorrelation deferred to a whole-card pass
metadata: 
  node_type: memory
  type: project
  originSessionId: f8da6695-10e4-4546-93f9-e2fae00a093e
  modified: 2026-07-23T02:46:15.869Z
---

For the HToWW PNet 2D c-tag scale factor (`flavTaggingSF_2022postEE.json.gz`,
correction `ParticleNetAK4_pseudocontinuous`), the tagger uncertainty **is** the SF
uncertainty (correction `central` folded into weight_nominal + up/down band as a shape
nuisance) — there is no separate tagger uncertainty.

**Decision (2026-07-23):** keep the SF uncertainty as a SINGLE nuisance
`CMS_ctag2d_2022` built from `up_Total`/`down_Total`. Do NOT decorrelate yet.

**Why:** decorrelation is a whole-card exercise the user wants done in one coherent
sweep later (JES→Regrouped, ctag→sources, lepton→components), not piecemeal on ctag.

**How to apply (when we do decorrelate):** the SF file has 525 systematic keys.
The correct model = HiggsDNA `bTagShapeSF` (event_weight_systematics.py): decorrelate
into independent sources, and map the SF's own JES/PU/lepton/theory components onto the
analysis's EXISTING nuisance names (CMS_scale_j, pileup, muon_id...) via SHARED names so
they CORRELATE (not double-count). The SF's `Stat`/per-bin-Stat keys become their own
new nuisances. Precedents differ by systematic type: JES & EGM scale/smear use a single
Total (one physical effect each); tagging SFs decorrelate (independent measurements).

Current limit (Jul-15 negrw + 2D-cat MVA + 2D SF Total): 1422 full / 749 stat / 1168 freeze.
See [[Meta/claude-memory/_history/projects/Flashjet/vault/flashjet-workflow|flashjet-workflow]] sibling HToWW notes; combine pipeline [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]].
