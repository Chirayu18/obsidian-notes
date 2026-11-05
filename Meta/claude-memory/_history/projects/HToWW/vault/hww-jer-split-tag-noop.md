---
name: hww-jer-split-tag-noop
description: cvmfs JME "latest" JSON split JER SF into ScaleFactor + SFUncertainty (2026-06-05); old systematic=up/down code silently returns nominal
metadata:
  type: project
---
Since 2026-06-05 the cvmfs JME `latest/jet_jerc.json.gz` files have `*_ScaleFactor_AK4PFPuppi` with inputs (JetEta, JetPt) only
and a separate ABSOLUTE `*_SFUncertainty_AK4PFPuppi`. higgscharm `jerc.py` passed systematic up/down through
get_corr_inputs, which skips missing inputs silently → JER Up == Down == nominal. Fixed 2026-10-06 (SF ± SFUncertainty).
Same day (audit): toppt.py dropped the nominal top-pT SF in shift trees; jerc.py Type-1 MET re-correction used
(PuppiMET, new, RAW) — undid Type-1 with the wrong sign, MET moved WITH jets under JES; electron_ss smear_up/down used
the nominal key (CMS_res_e dead); MiNNLO WH->tautau per-event PDF delta O(1000) (capped at 0.5). All fixed 2026-10-06.

**Why:** a silently-ignored input makes a dead nuisance with no error; found only because a data/MC study showed
JER Up and Down giving bit-identical results.
**How to apply:** any hww production before 2026-10-06 has no JER uncertainty; when a nuisance's Up equals its Down
exactly, suspect the producer, not physics. Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-other-era-config-bugs|hww-other-era-config-bugs]].
