"""Prove my temp-dir run_inference path is byte-identical to the production scoring.
Score the OLD (pre-negrw) merged DYto2L_2Jets_50 -- same features that produced the
existing mva/ file -- and diff mva_score_* against the existing production mva file."""
import sys, os, tempfile, shutil
from pathlib import Path
import numpy as np, pandas as pd

R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
os.chdir(R); sys.path.insert(0, R)
from analysis.postprocess.inference import run_inference
from analysis.workflows.config import WorkflowConfigBuilder

D = Path("/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE")
cfg = WorkflowConfigBuilder(workflow="hww_combine_fixed").build_workflow_config().inference

stage = Path(tempfile.mkdtemp(prefix="idtest_"))
# use the OLD merged file (pre-negrw) so features match the existing mva file exactly
os.symlink((D / "DYto2L_2Jets_50.parquet.bak_pre_negrw").resolve(), stage / "DYto2L_2Jets_50.parquet")
run_inference(output_dir=stage, model_path=cfg["model_path"], bhive_path=cfg["bhive_path"],
              config_name=cfg["bhive_config"], model_name=cfg["bhive_model_name"],
              split="full", split_field="event", split_modulo=None, split_remainder=None)

mine = pd.read_parquet(stage / "mva" / "DYto2L_2Jets_50.parquet")
prod = pd.read_parquet(D / "mva" / "DYto2L_2Jets_50.parquet")
score_cols = [c for c in mine.columns if c.startswith("mva_score_")]
print("rows mine:", len(mine), "| prod:", len(prod))
print("score cols:", score_cols)
if len(mine) == len(prod):
    for c in score_cols:
        d = np.abs(mine[c].to_numpy() - prod[c].to_numpy())
        print(f"  {c}: max|diff|={d.max():.3e} mean={d.mean():.3e}")
    allmatch = all(np.allclose(mine[c], prod[c], atol=1e-6) for c in score_cols)
    print("IDENTICAL (atol 1e-6):", allmatch)
else:
    print("ROW COUNT DIFFERS -> not directly comparable")
shutil.rmtree(stage, ignore_errors=True)
