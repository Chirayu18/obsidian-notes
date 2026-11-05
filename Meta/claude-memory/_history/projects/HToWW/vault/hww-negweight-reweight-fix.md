---
name: hww-negweight-reweight-fix
description: "HToWW autoMCStats fix via negative-weight reweighting (arXiv:2510.16217) — repo paths, gen-parton conventions, method"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ca41308-54ac-45ea-b7d8-0e5143b2f542
---

Implementing the **negative-weight reweighting** fix for the HToWW autoMCStats blow-up
(user's chosen fix = arXiv:2510.16217, Palmer & Kronheim). Root cause + hierarchy of fixes:
`Projects/HToWW/2026-06-23-automcstats-rootcause.md` and `ProposedFix-Automcstats.md`.
Plan file: `~/.claude/plans/for-the-fix-of-logical-wadler.md`.

**Method:** train a binary classifier for P₊(x⃗)=P(genWeight>0 | kinematics); reweight each event
by g(x⃗)=2·P₊−1; the reweighted estimator Σ|w|·g has lower variance than differencing ±w → raises
N_eff in the SR, shrinks autoMCStats at the source. Ensemble of 20 classifiers → PCA over the
per-bin covariance = the (favored) observable-level shape systematic.

**Design (user-confirmed):** g(x⃗) is a generator property, independent of the analysis selection.
So **train on a looser / mutually-exclusive workflow** (many more vjets events, must span the SR
x⃗ support) then **infer** on the tight `hww_combine_fixed` selection. Guardrail = coverage check
(SR x⃗ inside training domain) before wiring into combine.

**LIVE repos (verified by mtime — the plain ~/higgscharm and EPR_task/b-hive are STALE):**
- analysis: `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
- b-hive (combine scripts, dy_template_smooth.py, make_combine_histograms_v11_v32.py):
  `/eos/user/c/cgupta/HToWW/b-hive`
- env: `micromamba activate b_hive` → **coffea 0.7.22 / uproot 4.3.7** (OLD API:
  `NanoEventsFactory.from_root(url, treepath="Events", schemaclass=NanoAODSchema, entry_stop=N)`
  — NOT the `{path:tree}` dict form).

**Feature extraction (verified in the DYto2L_2Jets_50 / WtoLNu_2Jets NanoAODv12 files):**
- `LHEPart.fields = [pdgId,status,spin,pt,eta,phi,mass,incomingpz]`.
- `LHEPart.status==1` → outgoing (mean 2.66/evt); filter partons by |pdgId|≤5 or ==21 (drop the
  status-1 leptons). `status==-1` → the 2 incoming partons (flavor flags). `status==2` → the Z.
- `GenPart` hard-process partons (statusFlags isHardProcess bit 1<<7): mean 2.66, **max 5** →
  matches the paper's "up to 5 outgoing partons". status==23 = outgoing-hard subset.
- genWeight frac>0: **~0.83 inclusive** vs ~0.70 in the *selected* SR parquets (selection
  concentrates the high-neg-fraction region). Both in the paper's regime.
- **These "2Jets" FxFx samples are INCLUSIVE**: `LHE.Njets` mean ~0.64 (most events are 0/1-parton
  ME; extra jets from the shower). So outgoing status-1 partons/evt ≈0.64 is CORRECT, not a bug.
  → backbone features = **`events.LHE.*` scalars** (flat per-event, dump directly):
  `Njets, Nb, Nc, Nuds, Nglu, NpNLO, HT, HTIncoming, Vpt, AlphaS` — these ARE the paper's hand-built
  parton-count / HT / V-pT / merging features. LHEPart leading-parton kinematics supplement them.

**Processor integration is CONFIG-ONLY (no base.py edit):** features are `histogram_config.axes`
whose `expression` is eval'd against `events`/`objects` (base.py:128-129) and written to parquet
via `variables_map`. Add gen-parton axes to a new workflow YAML in `analysis/workflows/`.
Fileset: `analysis/filesets/fileset_2022postEE_nanov12_lxplus.json.bak_presiteredir` (53 samples;
the non-bak .json was truncated to 1 signal sample mid-work). Redirectors: FNAL/gridka work.

**Phase 1 DONE (validated end-to-end):** added `select_gen_partons` to
`analysis/selections/object_selections.py` + a new `analysis/workflows/hww_genrw_train.yaml`
(vjets-only datasets `dy_nlo`+`v+jets`, loose `train` category, gen-parton feature axes). Smoke
test dumped all **21 gen columns** (lhe_* + genparton*+ genweight_sign), 100% non-null, physical
values. **No base.py edit** — pure config.

**xrootd gotcha for local testing:** NO grid proxy on lxplus (`voms-proxy-init` needs the user's
passphrase, interactive). FNAL/gridka redirectors → "Auth failed: No protocols left to try". Use
the **`root://eoscms.cern.ch//eos/cms/...`** redirector (native lxplus access, no proxy) — pick it
from the fileset bak with `"eoscms.cern.ch" in url`. Not all samples have an eoscms copy.
Smoke driver: `~/smoke_genrw.py` on lxplus.

**Training selection = WIDEST (user chose drop-dilepton):** `hww_genrw_train` `train` category =
goodvertex+lumimask+met_filters+trigger only. Validated: 1 chunk of 8k entries → **67,775 feature
rows** (vs 26 with one_ll_pair), all 21 gen cols dump cleanly, no reco-axis errors on pairless
events. Coverage will be checked in gen-feature space (not reco).

**WEIGHT COLUMN:** use **`weight_nominal`** for BOTH the classifier label (`>0`) and the closure
weight — it's the fully-populated signed weight (nonnull 1.0, frac>0 0.843, ±1e5–1e6). NOT
`weight_genweight` (sparsely written, nonnull ~0.16) nor `genweight_sign` (sign only, no magnitude).

**Phase 2 script DONE:** `/eos/user/c/cgupta/HToWW/b-hive/scripts/negweight_reweight_train.py` —
20× HistGradientBoostingClassifier (sklearn 1.4.2; no xgboost; torch 2.5.1 avail) ensemble modeling
P+, g=2P+-1, class-imbalance aware, prints coverage + lhe_vpt closure + N_eff gain, saves
`negrw_models.joblib`. FEATURES list = the 20 lhe_*/genparton* cols (label/weight excluded).

**2026-07-11 UPDATE — training-region redesign + Phase-1 SUBMITTED.** Full write-up:
`Projects/HToWW/2026-07-11-negweight-reweight-training-region.md` (has a ⏳ RESUME STATE
section — read it first if resuming). Key changes since the memory above:
- Training selection is NO LONGER "widest/drop-dilepton". It is now
  **base cuts + `veto_emu_sr`** = veto ONLY the exactly-one-eμ-pair SR topology, keeping
  the no-pair bulk + same-flavor pairs. Reason (paper §V.4, verified): train/infer must be
  event-DISJOINT (else overfitting bias); this makes them disjoint by construction while
  staying in the same phase space (disjoint EVENTS yes, orthogonal PHASE SPACE no).
- **Veto gotcha:** `select_hww_ll_pair` uses `ak.mask` → pairless events are `None`, not
  `[]`; naive veto drops them ALL (~1000× over-veto). Fix = `~ak.fill_none((num==1)&
  ak.firsts(is_emu), False)`. Verified: 22.7% efficiency, 0 eμ leaked, hard tail present.
- **Phase-1 jobs SUBMITTED (idle):** clusters **9071462/9071463/9071464** (DY-50 / DY-10to50
  / W), 35 files/dataset (NOT full 989 — overkill), ~5M rows target. Output
  `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/`. Check
  `condor_q 9071462 9071463 9071464 -totals`.
- **Grid proxy IS valid** (`/tmp/x509up_u151861`, ~191h) — the earlier "no proxy" note is
  STALE; grid redirectors (FNAL/gridka) work for the DY samples (no eoscms copies).
**2026-07-12 — PHASE 1 + 2 COMPLETE, both gates PASS.** All 9 Phase-1 jobs done →
**9.72M training rows** (502 parquet), veto held (**0 eμ leaked**), COVERAGE PASS
(SR-proxy = same-flavor pairs ⊂ training domain in all 9 gen features, interpolation only).
**Phase-2 ensemble trained** (`negrw_out/negrw_models.joblib`, 8 MB, 20× HistGBDT):
YIELD CLOSURE ratio **0.994**, N_eff **2.91M→4.67M (+60%)** with **3–4× lift in the
hard-Vpt tail** (the starved SR bins). g(x⃗) mean 0.672, ensemble δg max 0.424.
Run gotchas: `micromamba` not on nohup PATH (use `$MAMBA_EXE`), script glob is
non-recursive (pass `.../2022postEE/*/train/*.parquet`).
**2026-07-12 — PHASE 3 (SR inference) IN PROGRESS. Code done + smoke-validated; ONE blocker.**
Chosen design (user-confirmed): inject the reweight AT THE PROCESSOR STAGE — re-run ONLY
vjets on `hww_combine_fixed`, dumping 2 extra parquet cols: `weight_negrw`=g=2·P̄₊−1 and
`weight_negrw_std`=2·std(P₊). Combine then fills vjets with `|weight_nominal|·weight_negrw`
+ ±std PCA shape nuisance. **vjets ONLY** (gate: datasets [DYto2L, WtoLNu]).
Code (LIVE repo, committed): workflow_config(_builder).py `negrw` passthrough; base.py
`_score_negrw` method + `_dataset_matches` + lazy `_negrw_bundle`; hww_combine_fixed.yaml
gains `gen_partons` field + 20 gen axes + `negrw:` block. Smoke-validated in b_hive: DY SR
file → 364 rows, g varies (30 distinct, [−0.33,0.80], std 0.31), δg~0.011, all g∈[−1,1].
**BLOCKER:** model trained sklearn 1.4.2 (b_hive) but Condor image
`coffea-base-almalinux9:0.7.30-py3.10` has sklearn 1.7.2 → `joblib.load` FAILS on workers
(`AttributeError __pyx_unpickle_CyHalfBinomialLoss`). **DECIDED FIX = retrain the ensemble
INSIDE the image** (image has pandas/pyarrow/sklearn1.7.2/HistGBDT; training parquets exist)
→ save `negrw_out_img/negrw_models.joblib`, point yaml at it, re-smoke in image, then submit.
**FULL handoff with exact commands + next steps:**
`Projects/HToWW/2026-07-12-negweight-phase3-SR-inference-handoff.md` (pinned; READ FIRST).
Phases 1&2 closure/N_eff: `Projects/HToWW/2026-07-11-negweight-reweight-training-region.md`.

**2026-07-15 — RETRAIN-IN-IMAGE via CONDOR (fixes the sklearn blocker).**
Host retrain kept OOM-dying on shared login node (4GB free) → moved to Condor.
**Cluster `9086952`**, submit dir `/afs/cern.ch/user/c/cgupta/negrw_condor/`, image
coffea-base-almalinux9:0.7.30-py3.10 (sklearn 1.7.2 = SR-worker match, confirmed
submit_condor.py default). Data tar'd (664MB, 502 parquet) + transferred (container
can't read /eos). Job runs `negrw_diag.py` (same training + diagnostics npz) then
`make_negrw_plots.py` (8 PNGs). Outputs → submit `out/`, then copy to
`/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/`. User wants a **Marp .md deck**
(he renders it) at `Projects/HToWW/negrw-training/` — plots+slides.md.
**FULL resume state: `Projects/HToWW/negrw-training/RESUME-condor-retrain.md` (READ FIRST).**

Correctness side-bug to fix opportunistically: `TbarBQ`/`TBbarQ` xsec=0.
See [[Meta/claude-memory/_history/workflow/vault/lxplus-coffea-env|lxplus-coffea-env]] [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]].
