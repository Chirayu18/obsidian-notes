#!/usr/bin/env python3
"""Surgical vjets-only MVA scoring that is BYTE-IDENTICAL to run_inference.py.

run_inference() scores every *.parquet in output_dir and writes output_dir/mva/.
It has NO other path dependency (no scale/sumw reads happen here). So scoring a dir
that contains ONLY symlinks to the 3 vjets merged parquets yields exactly the same
scored files as the full run would for those samples -- the model, config, feature
extraction, batching and score columns are the identical repo code path. We then move
the produced mva/<vjets>.parquet into the REAL <variation>/mva/, leaving the other 50
samples' mva/ files untouched.

Model/config resolution copies run_inference.py:main() exactly (from the yaml's
inference: block). Runs nominal + all discovered shift variations.
"""
import sys, os, shutil, tempfile
from pathlib import Path

R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
os.chdir(R)                          # run_inference.py runs from repo root
sys.path.insert(0, R)

from analysis.postprocess.inference import run_inference
from analysis.workflows.config import WorkflowConfigBuilder
# reuse run_inference.py's own variation discovery so the set of shifts is identical
from scripts.mva.run_inference import discover_variations

WORKFLOW = "hww_combine_fixed"
YEAR = "2022postEE"
VJETS = ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]

base_dir = Path("outputs") / WORKFLOW / YEAR   # relative, matches run_inference.py

cfg = WorkflowConfigBuilder(workflow=WORKFLOW).build_workflow_config()
inf = cfg.inference
model_path = inf["model_path"]
bhive_path = inf["bhive_path"]
bhive_config = inf["bhive_config"]
bhive_model_name = inf["bhive_model_name"]
print("model_path:", model_path)
print("bhive:", bhive_path, bhive_config, bhive_model_name)

# real variations only: nominal + the 12 object shifts (drop training-label dirs like
# mva_labeled / mva_labeled_v32 which discover_variations also returns).
ALLOWED = {"nominal"} | {f"CMS_{a}_{b}_2022{d}"
                         for a in ("res", "scale") for b in ("e", "j", "m")
                         for d in ("Up", "Down")}
for variation in discover_variations(base_dir, None):
    if variation not in ALLOWED:
        print(f"[{variation}] not a real object-shift variation, skip")
        continue
    var_dir = base_dir / variation if variation != "nominal" else base_dir
    real_mva = var_dir / "mva"
    real_mva.mkdir(parents=True, exist_ok=True)

    # stage a temp dir with ONLY the vjets merged parquets for this variation
    present = [s for s in VJETS if (var_dir / f"{s}.parquet").exists()]
    if not present:
        print(f"[{variation}] no vjets parquets, skip")
        continue
    stage = Path(tempfile.mkdtemp(prefix=f"negrw_infer_{variation}_"))
    for s in present:
        os.symlink((var_dir / f"{s}.parquet").resolve(), stage / f"{s}.parquet")

    print(f"[{variation}] scoring {present} in {stage}")
    run_inference(
        output_dir=stage,
        model_path=model_path,
        bhive_path=bhive_path,
        config_name=bhive_config,
        model_name=bhive_model_name,
        split="full",
        split_field="event",
        split_modulo=None,
        split_remainder=None,
    )

    # move the freshly-scored vjets mva files into the REAL mva/ dir
    for s in present:
        src = stage / "mva" / f"{s}.parquet"
        dst = real_mva / f"{s}.parquet"
        if dst.exists():
            shutil.copy2(dst, str(dst) + ".bak_pre_negrw") if not os.path.exists(str(dst)+".bak_pre_negrw") else None
        shutil.move(str(src), str(dst))
        print(f"  -> {dst}")
    shutil.rmtree(stage, ignore_errors=True)

print("\nVJETS INFERENCE DONE (identical to run_inference, vjets-only)")
