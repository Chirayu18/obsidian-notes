---
tags:
  - reference
status: active
date: 2026-07-12
source: lxplus
pinned: true
---

# Neg-weight reweighting — Phase 3 (SR inference) handoff

**Read this first if resuming.** Phases 1 & 2 are DONE and validated (see
[[2026-07-11-negweight-reweight-training-region]] for the full closure table). Phase 3 =
inject the reweight into the vjets **SR** parquets. All the code is written and
smoke-validated; there is **ONE blocker** (a sklearn version mismatch on Condor workers)
with a decided-but-not-yet-executed fix. Everything below is durable.

---

## Where we are (2026-07-12 ~01:20)

**Goal of Phase 3:** re-run ONLY the vjets datasets on the `hww_combine_fixed` (tight SR)
workflow so the output parquets carry two extra columns:
- `weight_negrw`     = g(x⃗) = 2·P̄₊(x⃗) − 1   (the per-event reweight factor, ∈ [−1,1])
- `weight_negrw_std` = 2·std_m P₊,m(x⃗)       (ensemble spread → shape systematic)

Then the combine histogram builder fills the vjets template with **|weight_nominal|·weight_negrw**
(instead of weight_nominal), and uses ±weight_negrw_std (PCA over the 20-member covariance)
as the shape nuisance. Expected result: autoMCStats contribution collapses, r₉₅ drops from 1742.

**vjets ONLY.** The user confirmed explicitly: the SR re-run touches only the vjets
datasets (`DYto2L*`, `WtoLNu*`). tt/WW/signal/etc. SR parquets stay as-is from the existing
`hww_combine_fixed` production. Two-level gate guarantees this: (1) submit only vjets
datasets; (2) the `negrw:` YAML block's `datasets: [DYto2L, WtoLNu]` gate means only those
get the column even if something else were run.

---

## ✅ Code changes made this session (on disk / AFS, NOT git-committed)

Repo: `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
(edited via mount `/home/cgupta/mnt/lxplus/...`). **NOT committed** — that repo already had
many unrelated dirty files (jec params, filesets, postprocessor, object_selections, etc.),
so I deliberately did NOT `git add`/push to avoid entangling half-finished work. My 4 edits
live on the persistent AFS mount (durable). `hww_combine_fixed.yaml` is UNTRACKED (`??`) in
that repo — it was never git-added upstream. Remote is `git@github.com:Chirayu18/higgscharm.git`
(`chirayu`). If you want these committed, cherry-pick just these 4 paths:
`analysis/processors/base.py`, `analysis/workflows/config/workflow_config.py`,
`analysis/workflows/config/workflow_config_builder.py`, `analysis/workflows/hww_combine_fixed.yaml`.
To review my exact diff tomorrow: `cd <repo> && git diff -- analysis/processors/base.py
analysis/workflows/config/workflow_config.py analysis/workflows/config/workflow_config_builder.py`
(the yaml is untracked → just open it).

1. **`analysis/workflows/config/workflow_config.py`** — added `negrw=None` param + attr +
   to_dict passthrough (sibling of mva/inference/combine).
2. **`analysis/workflows/config/workflow_config_builder.py`** — `negrw=self.config.get("negrw")`.
3. **`analysis/processors/base.py`**:
   - `__init__`: `self._negrw_bundle = None` (lazy model cache).
   - In `process_shift`, right after `variables_map["event"]` is set: if
     `self.workflow_config.negrw` and `_dataset_matches(dataset, negrw_cfg["datasets"])`,
     call `self._score_negrw(...)` → add `weight_negrw` + `weight_negrw_std` to variables_map.
   - New method `_score_negrw(negrw_cfg, variables_map)`: lazy `joblib.load(model)`; builds
     the (n_events, 20) matrix in the persisted `features` order (jagged/option axes →
     `ak.firsts` then `fill_none(NaN)`, matching training NaN handling); ensemble
     `predict_proba` → `g_central`, `g_std`. Returns numpy arrays.
   - New module fn `_dataset_matches(dataset, patterns)`: substring match (falsy → all).
4. **`analysis/workflows/hww_combine_fixed.yaml`**:
   - Added `gen_partons: {field: select_gen_partons}` to `object_selection`.
   - Added the **20 gen axes** (lhe_njets…genparton2_eta) at the top of `histogram_config.axes`
     — identical to the train yaml. (For parquet, axes ⇒ columns; `layout` is coffea-only,
     so no layout edit needed.)
   - Added top-level `negrw:` block:
     ```yaml
     negrw:
       model: /eos/user/c/cgupta/HToWW/b-hive/negrw_out/negrw_models.joblib
       datasets: [DYto2L, WtoLNu]
     ```

## ✅ Smoke-validated end-to-end in `b_hive` (py3.11 / sklearn 1.4.2)

- **WtoLNu file** (eoscms, 6 chunks): SR parquet has `weight_negrw` + `_std`, 100% non-null,
  g ∈ [−1,1], gen features present. Only 13 SR rows (W rarely makes tight eμ SR) — too few
  to see spread.
- **DYto2L_2Jets_50 file** (gridka, 8 chunks): **364 SR rows**, g 100% non-null, **g VARIES**
  (30 distinct values, range [−0.330, 0.798], mean 0.416, std 0.311), δg mean 0.011, all
  g ∈ [−1,1]. g median 0.517 → P₊≈0.76 vs `weight_nominal` frac>0 = 0.679 in that SR sample
  → consistent. **The scoring path is correct.** Smoke drivers:
  `~/.claude/jobs/af76ec6a/tmp/smoke_sr_negrw.py` (W), `smoke_sr_dy.py` (DY).

---

## ⛔ THE BLOCKER — sklearn version mismatch on Condor workers

- Model was trained in **`b_hive`: sklearn 1.4.2, py3.11**.
- Condor image (submit_condor.py `--image` default) =
  **`coffea-base-almalinux9:0.7.30-py3.10` → sklearn 1.7.2, py3.10**.
- `joblib.load(negrw_models.joblib)` **FAILS inside the image**:
  `AttributeError: Can't get attribute '__pyx_unpickle_CyHalfBinomialLoss' on
  sklearn._loss._loss`. The HistGradientBoosting Cython loss internals changed between
  1.4 and 1.7 → the pickle is not loadable there. **If submitted as-is, every vjets SR
  job crashes on load.** (Verified by `singularity exec <image> python -c "joblib.load(...)"`.)
- Also saw a `PermissionError` reading the model from `/eos/...` under `singularity -B /eos`
  — copying to `/tmp` fixed the read; the real fix path must ensure the model is readable
  on the worker (transfer_input_files, or an AFS/EOS path the job can read).

### DECIDED FIX (chosen, not yet executed): **Retrain the ensemble inside the Condor image**
The training parquets already exist (9.72M rows,
`/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/*/train/*.parquet`).
Re-run the SAME training script but **inside the singularity image** so the saved model is
native to the workers' sklearn 1.7.2. Verified the image has pandas 2.3.3 / pyarrow 19.0.1 /
sklearn 1.7.2 / HistGBDT — so the retrain will run there. ~20 min. This keeps SR scoring on
Condor (no separate local pass) and re-prints the closure/N_eff for re-confirmation.

**Exact command to run tomorrow (retrain in image):**
```bash
ssh lxplus
IMG=/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-base-almalinux9:0.7.30-py3.10
cd /eos/user/c/cgupta/HToWW/b-hive
mkdir -p negrw_out_img
nohup singularity exec -B /eos -B /afs -B /tmp "$IMG" python3 scripts/negweight_reweight_train.py \
  --train "/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/*/train/*.parquet" \
  --outdir /eos/user/c/cgupta/HToWW/b-hive/negrw_out_img \
  > /eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/train.log 2>&1 &
```
Then **point the yaml at the new model**:
`negrw.model: /eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/negrw_models.joblib`
and re-verify it loads in the image (`singularity exec … joblib.load`). Confirm the closure
table in the new train.log still shows ratio ≈0.994 and N_eff ~2.9M→~4.7M (should reproduce;
tiny differences from sklearn 1.4→1.7 tree internals are fine as long as closure holds).

**Alternative fix (rejected for now):** local scoring pass — run the gen-augmented vjets SR
on Condor WITHOUT scoring, then a local `b_hive` post-pass adds `weight_negrw`. Decouples
sklearn from Condor but is a 2nd step rewriting every SR parquet. Only fall back to this if
the retrained-in-image model's closure looks wrong.

---

## NEXT STEPS (in order, for tomorrow)

1. **Retrain the ensemble in the Condor image** (command above). Wait ~20 min. Confirm
   closure ratio ≈0.994 and N_eff lift reproduce in the new `negrw_out_img/train.log`.
2. **Verify the new model loads in the image:**
   `singularity exec -B /eos <IMG> python3 -c "import joblib; b=joblib.load('/eos/.../negrw_out_img/negrw_models.joblib'); print(len(b['models']))"`.
3. **Point the yaml at it:** edit `hww_combine_fixed.yaml` `negrw.model:` →
   `.../negrw_out_img/negrw_models.joblib`. (Also ensure the worker can READ that path —
   if EOS-under-singularity perms bite, add it to `transfer_input_files` or stage to AFS.)
4. **Re-smoke in the image** (not just b_hive): run one DY file through `hww_combine_fixed`
   inside the image, confirm `weight_negrw` column appears and g varies. This is the real
   worker-environment test.
5. **Submit vjets SR re-run** on Condor. Use the SAME runner as Phase-1 but for the
   `hww_combine_fixed` workflow, **vjets datasets only** (DYto2L_2Jets_50, DYto2L_2Jets_10to50,
   WtoLNu_2Jets). Full file count this time (not the 35-file cap — SR needs the full stats).
   Watch: jobs must not crash on joblib.load; parquets must carry weight_negrw[_std].
   NOTE: full vjets SR is many more files than Phase-1 — check fileset isn't still capped at
   35 (`fileset_2022postEE_nanov12_lxplus.json` was truncated to 3 samples @35 during Phase-1;
   restore from `.bak_presiteredir` or `.bak_pre_genrw` and DON'T slice).
6. **Merge SR parquets**, sanity-check weight_negrw distribution + veto (SR is eμ, disjoint
   from the veto_emu_sr training region by construction).
7. **Wire into combine:** the b-hive histogram builder
   (`/eos/user/c/cgupta/HToWW/b-hive/scripts/make_combine_histograms_v11_v32.py` +
   `dy_template_smooth.py`) — fill the vjets template with `|weight_nominal|·weight_negrw`
   and add the ±`weight_negrw_std` PCA shape nuisance. (Inspect these scripts first — how they
   currently read `weight_nominal`.)
8. **Re-run the limit**; check autoMCStats contribution (was ~81% of syst) collapses and r₉₅
   drops from 1742.

---

## Handles / paths (quick ref)

- **Trained model (b_hive/1.4.2, NOT worker-loadable):**
  `/eos/user/c/cgupta/HToWW/b-hive/negrw_out/negrw_models.joblib`
- **To-be-retrained model (image/1.7.2):** `.../negrw_out_img/negrw_models.joblib`
- **Training parquets (9.72M rows):**
  `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/*/train/*.parquet`
- **Training script:** `/eos/user/c/cgupta/HToWW/b-hive/scripts/negweight_reweight_train.py`
  (FEATURES = 20 lhe_*/genparton* cols; label `weight_nominal>0`; N_MODELS=20).
- **Condor image:** `/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-base-almalinux9:0.7.30-py3.10`
  (sklearn 1.7.2). `b_hive` micromamba env = sklearn 1.4.2 (`$MAMBA_EXE` =
  `/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba`; note micromamba is NOT on
  the nohup PATH — use `$MAMBA_EXE run -n b_hive`).
- **Grid proxy:** `/tmp/x509up_u151861` valid (~189h left as of 2026-07-12). For DY/W grid
  reads set `X509_USER_PROXY=/tmp/x509up_u151861`.
- **Connection recovery (no kinit/password):** `python3 ~/bin/lxplus-connect.py` (self-heals
  stale sockets). See [[lxplus-workflow]].
- **Smoke drivers:** `~/.claude/jobs/af76ec6a/tmp/smoke_sr_negrw.py` (W, eoscms),
  `smoke_sr_dy.py` (DY, gridka). Also on lxplus at `/tmp/smoke_sr_*.py`.

## One gotcha to remember
The runner writes per-dataset partition subdirs (`<dataset>_<jobid>`). The `negrw` gate is a
**substring** match, so `DYto2L_2Jets_50_3` etc. all match `DYto2L`. Good.

Related: [[2026-07-11-negweight-reweight-training-region]] ·
[[2026-06-23-automcstats-rootcause]] · [[ProposedFix-Automcstats]]
