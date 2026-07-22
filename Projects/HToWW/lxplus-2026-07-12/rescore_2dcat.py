#!/usr/bin/env python3
"""Re-score mva/ parquets in place with the 2D-cat model.

The combine mva/ parquets already carry all 26 config features (kinematics + the
11 cjet_cand_ctag2d_* one-hots appended by append_onehot.py), so we don't need to
re-run the full merged-input inference. This just reloads each mva/<sample>.parquet,
builds the feature matrix in config order, runs the 2D-cat SimpleMLP, and OVERWRITES
the mva_score_<class> columns (softmax probabilities). Atomic .tmp rename; leaves a
.bak_pre_2dcatscore backup of the baseline-scored file once.

Model call mirrors analysis/postprocess/inference.py exactly:
    model((global_feat, zeros(N,0,0), zeros(N,0,0)))  with model.for_inference=True

Usage:
  B_HIVE_DIR=<bhive> python rescore_2dcat.py --mva-dir <dir> \
       --config HPlusCHToWW_2dcats --model-name SimpleMLP_MultiClass \
       --model-path <best_model.pt> --bhive <bhive>
"""
import argparse
import glob
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mva-dir", required=True)
    ap.add_argument("--config", default="HPlusCHToWW_2dcats")
    ap.add_argument("--model-name", default="SimpleMLP_MultiClass")
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--bhive", required=True)
    args = ap.parse_args()

    os.environ.setdefault("B_HIVE_DIR", args.bhive)
    sys.path.insert(0, args.bhive)
    os.chdir(args.bhive)
    from utils.config.config_loader import ConfigLoader
    from utils.models.models import BTaggingModels

    cfg = ConfigLoader.load_config(args.config)
    features = cfg["global_features"]
    model = BTaggingModels(args.model_name, cfg)
    model.create_integers_defaults()
    model.create_feature_shapes()
    ckpt = torch.load(args.model_path, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    model.for_inference = True
    class_names = list(model.classes.keys())
    print(f"[rescore] {args.mva_dir}: {len(features)} feats, classes={class_names}")

    fs = sorted(f for f in glob.glob(os.path.join(args.mva_dir, "*.parquet"))
                if not f.endswith(".tmp")
                and not f.endswith(".bak_pre_2dcatscore")
                and not f.endswith(".bak_pre_ctag2dsf")
                and not f.endswith(".bak_pre_negrw"))

    for path in fs:
        cols = pq.read_schema(path).names
        miss = [f for f in features if f not in cols]
        if miss:
            print(f"  [MISS] {os.path.basename(path)}: missing {len(miss)} feats {miss[:3]}...")
            continue
        df = pd.read_parquet(path)
        if len(df) == 0:
            print(f"  [empty] {os.path.basename(path)}")
            continue

        X = np.column_stack([df[f].to_numpy() for f in features]).astype(np.float32)
        X[~np.isfinite(X)] = 0.0

        scores = []
        with torch.no_grad():
            for s in range(0, len(X), 4096):
                b = torch.tensor(X[s:s + 4096])
                out = model((b, torch.zeros(b.shape[0], 0, 0),
                             torch.zeros(b.shape[0], 0, 0)))
                scores.append(out.cpu().numpy())
        scores = np.concatenate(scores, axis=0)

        bak = path + ".bak_pre_2dcatscore"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        for i, cls in enumerate(class_names):
            df[f"mva_score_{cls}"] = scores[:, i]
        tmp = path + ".tmp"
        df.to_parquet(tmp, index=False)
        os.replace(tmp, path)
        ssum = scores.sum(axis=1).mean()
        print(f"  [ok]  {os.path.basename(path):40s} n={len(df):7d} "
              f"<P_hplusc>={scores[:,0].mean():.4f} sum~{ssum:.3f}")


if __name__ == "__main__":
    main()
