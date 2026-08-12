---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# HToWW master task list — reprocessing + combine

Consolidates everything outstanding as of 2026-08-12. Two independent tracks:

- **Track A (reprocessing)** — needs the framework re-run over MC. Nothing here
  changes the limit until the campaign completes.
- **Track B (combine)** — card/config only, can run against existing parquets
  today.

Current limit: **1160** (Asimov, blind, 1POI). Stat-only: 637.

---

## Track A — REPROCESSING campaign

All of these ride on ONE re-run. Batch them; do not run the campaign twice.

### A1. Sample changes (fileset edits, then reprocess)

| # | change | status | blocker |
|---|---|---|---|
| A1.1 | **W+jets replacement** — `WtoLNu-2Jets` inclusive -> `0J/1J/2J` binned | not started | needs xsecs (user) |
| A1.2 | **DY -> Z→ττ** — inclusive DY -> `DYto2Tau-2Jets_M-50_{0,1,2}J_Filtered` | not started | needs xsecs (user) |
| A1.3 | **WH completion (postEE)** — 2 samples ADDED with `xsec: 0.0` | fileset done | needs xsecs (user) |
| A1.4 | **WH for other 3 eras** — `whtoww` absent from preEE/2023preBPix/2023postBPix | not started | decide scope first |

Rationale and measurements: `2026-08-12-postEE-background-audit-vs-AN.md`.

- A1.1: AN-23-102 §2.3 explicitly rejects the inclusive NLO aMCatNLO sample we
  use ("5 times smaller size than LO and with large fraction of negative
  weights"). Replacements: 1545.5M events vs our 281.5M (5.5x).
- A1.2: our eμ cut discards **98.4%** of DY events that had a lepton pair —
  those are Z→ee/μμ, physically incapable of giving eμ. Filtered ττ samples
  total 219.2M events.
- A1.3: all four W-decay/charge combos exist; config had an arbitrary pairing.
  `WminusH_WtoLNu` (696,034 events) is the one that matters — leptonic W⁻H is
  the 3-lepton final state most likely to enter an eμ selection.

**Open decision — stitch or replace?** For both A1.1 and A1.2, decide whether to
drop the inclusive sample entirely or stitch inclusive + binned with per-slice
weights. AN-23-102 stitches (jet-binned NLO for LHE VpT < 100, pT-binned above;
LO HT-binned + inclusive for HT < 70). Stitching is more work and needs the
overlap handled carefully; replacing is simpler and is what the sample counts
alone would suggest.

**TRAP — do not repeat the `-ext` mistake.** When adding samples that overlap an
existing one's phase space, the cross sections must be **re-split**, not
appended. Verified: tt parent-only = 923.41 pb = NNLO 13.6 TeV (923.6); adding
the `-ext` xsecs on top gives 1393 pb, a 1.5x inflation. Any A1 change must be
checked the same way — sum the group and compare to the known total.

### A2. Systematics awaiting reprocessing

Modules are WRITTEN and WIRED; they emit nothing until the campaign runs.
Currently commented out in `hww_combine_2dcat.yaml` so the card stays honest.

| # | systematic | module | card state |
|---|---|---|---|
| A2.1 | `top_pt` | `analysis/corrections/toppt.py` | commented out (line ~1094) |
| A2.2 | `higgs_plus_c` | `analysis/corrections/higgs_hf.py` | commented out (line ~1098) |
| A2.3 | MET unclustered energy | `analysis/corrections/jerc.py` (patched) | needs 2 new shift dirs |

- A2.1/A2.2 verified against hh2bbww and HiggsDNA respectively — see
  `2026-08-11-verified-against-HiggsDNA-and-hh2bbww.md`.
- A2.3 also requires `run_inference.py` to be re-run over the two new
  object-shift directories, not just the base pass.
- On completion: uncomment the two `shape_systematics` lines AND remove the
  `flavor_composition_ggH` lnN (line ~1140), which `higgs_plus_c` supersedes.

### A3. `-ext` samples (optional stats gain, NOT a bug)

`tt-ext` (3) + `singletop-ext` (6) are in the fileset but not in the workflow's
`mc:` list, so they never run. **This is currently correct** — parent-only
reproduces NNLO exactly. Wiring them in is a **two-part** change:
add the keys AND re-split the parent xsecs. Gain: ~34% more tt/ST events.
Only worth doing inside a reprocessing campaign that is happening anyway.

### A4. Pre-flight before submitting the campaign

- [ ] EOS space check — was ~95% full; campaign needs headroom.
      **Do not delete anything on EOS without confirming first.**
- [ ] Grid proxy live (node-local; use the AFS copy at
      `private/x509up_u151861`, not `cms.proxy`).
- [ ] Submit from **tmux**, not nohup.
- [ ] `jobs_status.py` blacklist is memoryless — it re-admits failed sites and
      filesets list ONE replica per file, so blacklisting DELETES files. Watch it.

---

## Track B — COMBINE (no reprocessing needed)

Can be done today against existing parquets.

### B1. Decompose `CMS_ctag2d_2022` (task #26)

Second-largest shape nuisance: freezing it moves 1160 -> 1125 (**35 units**).
Currently ONE nuisance (`up_Total`). Decision recorded in memory: keep as one
for now, full decorrelation deferred to a whole-card pass. HiggsDNA's
`bTagShapeSF` is the decorrelation model to follow.

### B2. QCD scale variations — the actual largest nuisance

**Revised ranking from the 2026-08-12 impacts scan** (limit with nuisance
frozen; nominal 1160):

| nuisance | frozen | delta |
|---|---|---|
| `scalevar_muF` | 1091 | **-69** |
| `CMS_ctag2d_2022` | 1125 | **-35** |
| `ps_fsr` | 1135 | -25 |
| `scalevar_muR_muF` | 1144 | -16 |
| `scalevar_muR` | 1151 | -9 |
| `lhe_alphaS` | 1156 | -4 |
| `lhe_pdf`, `CMS_scale_j_2022` | 1159 | -1 |
| all others | 1160 | 0 |
| `xsec_vjets` | 1173 | **+13** (fit uses it to absorb something) |

`scalevar_muF` at -69 is nearly 2x ctag2d. **This, not ctag2d, is the biggest
single lever.** Investigate: is the muF variation being applied per-process
correctly, and should it be decorrelated by process? The `xsec_vjets` +13 is
also worth understanding — a nuisance that *helps* when frozen usually means
it is mis-scoped.

Caveat: these are frozen-limit deltas, not full `combine -M Impacts` pulls.
Ranking is indicative.

### B3. Update systematics notes with verified sources (task #24)

Outstanding provenance gaps:
- lumi source
- `xsec_vjets` — currently Z+jets-only provenance
- `CMS_negrw_vjets` justification
- range-maximum convention

### B4. Closed / not real

- ~~task #23 "fix the impacts loop"~~ — **NOT A REAL TASK.** The loop was never
  broken; all 23 shape systematics converged with 5 quantiles. The "degenerate
  3984.4" was a bug in my own parsing script (`rsplit('_',1)` mangled names
  containing underscores: `ps_fsr`, `muon_id`, `electron_reco_RecoBelow20`).
- **TTZ and `WZto3LNu`** — parked by decision 2026-08-12. Both sit in the
  fileset with valid cross sections but are absent from `combine.process_map`.
  AN-23-102 does not model ttV, so there is no Run 2 precedent forcing them.
  Revisit only if a Run 3 reference (e.g. AN-24-091) makes it necessary.
- **Diboson exclusive split** — AN uses 12 decay-exclusive samples, we use 3
  inclusive. Not wrong, but the exclusive set concentrates stats in the
  leptonic corners that reach an eμ SR. Noted, not scheduled; would be another
  A1-class change with the same xsec re-split trap.

---

## Suggested order

1. **B2** — understand `scalevar_muF` (-69). Biggest lever, no reprocessing.
2. **User supplies cross sections** for A1.1 / A1.2 / A1.3.
3. **A1 + A2 + A3 batched into ONE reprocessing campaign**, after A4 pre-flight.
4. **B1 / B3** — during or after the campaign.

Do not start the campaign until the cross sections are settled — a second
re-run to fix a normalisation would cost days.
