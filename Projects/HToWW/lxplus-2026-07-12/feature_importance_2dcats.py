#!/usr/bin/env python3
"""Gradient-based feature importance for the 2D-CTAG MVA (and the baseline).

Method (same as scripts/feature_importance.py, adapted to the v11 6-class setup):
  importance(feature f, class k) = mean | dP_hplusc/dx_f - dP_k/dx_f |
evaluated over signal+background events, with gradients taken w.r.t. the
standardized feature z = (x-mean)/std so all features sit on a 1-sigma scale
(otherwise raw-unit features like pT dominate trivially).

Overall importance = sum over background classes weighted by
alpha_k = sigmoid(cos_sim(W_sig, W_k)/tau) — backgrounds whose output-layer
direction is most aligned with signal count most.

Handles BOTH models:
  --variant 2dcats : 26 inputs (15 kinematic + 11 one-hot ctag2d), config HPlusCHToWW_2dcats
  --variant base   : 17 inputs (15 kinematic + cvsl/cvsb),        config HPlusCHToWW_multiclass

Usage:
  python feature_importance_2dcats.py --variant 2dcats
  python feature_importance_2dcats.py --variant base
"""
import argparse
import glob
import os

import lz4.frame
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

OUTPUT_ROOT = "/eos/user/c/cgupta/EPR_task/b-hive/output"

# 6-class v11 setup
CLASSES = ["hplusc", "higgsbkg", "tt", "st", "diboson", "vjets"]
NUM_TRUTHS = len(CLASSES)

# feature order must match global_features in the config yaml
KINEMATIC = [
    "dilepton_pt", "lepton1_pt", "lepton2_pt", "cjet_cand_pt", "met_pt",
    "mtl1", "mtl2", "dilepton_mass",
    "delta_R_ll_l1", "delta_R_ll_l2", "delta_R_ll_c",
    "delta_phi_l1PlusMET_c", "delta_phi_l1_MET", "delta_phi_l2_MET",
]
CTAG2D = ["cjet_cand_ctag2d_" + c for c in
          ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]]

VARIANTS = {
    "2dcats": {
        "features": KINEMATIC + CTAG2D + ["nSV"],
        "model": (OUTPUT_ROOT + "/TrainingTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train"
                  "/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt"),
        "data": OUTPUT_ROOT + "/DatasetConstructorTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_test",
    },
    "base": {
        "features": KINEMATIC + ["cjet_cand_cvsl_pnet", "cjet_cand_cvsb_pnet", "nSV"],
        "model": (OUTPUT_ROOT + "/TrainingTask/HPlusCHToWW_multiclass/hwwcom_v11_train"
                  "/hwwcom_multiclass_v11/SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt"),
        "data": OUTPUT_ROOT + "/DatasetConstructorTask/HPlusCHToWW_multiclass/hwwcom_v11_test",
    },
}


def load_lz4(path, n_truths=NUM_TRUTHS):
    with lz4.frame.open(path, mode="r") as f:
        raw = f.read()
    s = np.frombuffer(raw, dtype="float32").copy()
    n_cols = int(s[1])
    s = s[2:].reshape(-1, n_cols, order="C")
    labels = s[:, -(n_truths + 1):-1]
    truth = np.zeros(s.shape[0], dtype=int)
    for i in range(n_truths):
        truth[labels[:, i] == 1] = i
    X = s[:, :-(n_truths + 2)]
    return X, truth


def load_data(data_dir, max_files, n_features):
    files = sorted(glob.glob(os.path.join(data_dir, "*.lz4")))[:max_files]
    Xs, Ts = [], []
    for f in files:
        try:
            X, t = load_lz4(f)
        except Exception:
            continue
        if X.shape[1] != n_features:
            continue
        Xs.append(X)
        Ts.append(t)
    if not Xs:
        raise RuntimeError("no usable lz4 files with %d features in %s" % (n_features, data_dir))
    return np.concatenate(Xs), np.concatenate(Ts)


def build_net(n_in, n_out):
    return nn.Sequential(
        nn.Linear(n_in, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(128, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(32, n_out),
    )


def load_model(path, n_in, n_out):
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    net = build_net(n_in, n_out)
    state = {k.replace("net.", ""): v for k, v in ckpt["model_state_dict"].items()
             if k.startswith("net.")}
    net.load_state_dict(state)
    net.eval()
    return net, ckpt


def grad_importance(net, X, cls_idx, mean, std, batch=4000):
    """mean |dP_sig/dz - dP_cls/dz| over events, z = standardized feature."""
    Xn = (X - mean) / std
    std_t = torch.tensor(std, dtype=torch.float32)
    mean_t = torch.tensor(mean, dtype=torch.float32)
    grads = []
    for s in range(0, len(Xn), batch):
        zb = torch.tensor(Xn[s:s + batch], dtype=torch.float32, requires_grad=True)
        xb = zb * std_t + mean_t
        p = F.softmax(net(xb), dim=1)
        d = (p[:, 0] - p[:, cls_idx]).sum()
        g, = torch.autograd.grad(d, zb)
        grads.append(g.abs().detach().numpy())
    return np.concatenate(grads).mean(axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=list(VARIANTS), default="2dcats")
    ap.add_argument("--max-files", type=int, default=250)
    ap.add_argument("--tau", type=float, default=0.3)
    args = ap.parse_args()

    cfg = VARIANTS[args.variant]
    feats = cfg["features"]
    X, truth = load_data(cfg["data"], args.max_files, len(feats))
    net, ckpt = load_model(cfg["model"], len(feats), NUM_TRUTHS)
    print("variant=%s  events=%d  features=%d" % (args.variant, len(X), len(feats)))

    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0

    # alpha weights from output-layer geometry
    W = ckpt["model_state_dict"]["net.12.weight"]
    cos = [F.cosine_similarity(W[0].unsqueeze(0), W[i].unsqueeze(0)).item()
           for i in range(NUM_TRUTHS)]
    alpha = [1.0 / (1.0 + np.exp(-c / args.tau)) for c in cos]

    per_class = {}
    for k in range(1, NUM_TRUTHS):
        sel = (truth == 0) | (truth == k)
        if sel.sum() < 100:
            continue
        per_class[CLASSES[k]] = grad_importance(net, X[sel], k, mean, std)

    overall = np.zeros(len(feats))
    wsum = 0.0
    for k in range(1, NUM_TRUTHS):
        name = CLASSES[k]
        if name in per_class:
            overall += alpha[k] * per_class[name]
            wsum += alpha[k]
    overall /= max(wsum, 1e-9)

    order = np.argsort(overall)[::-1]
    print("\n=== OVERALL feature importance (%s), alpha-weighted, standardized ===" % args.variant)
    print("%-30s %12s  %s" % ("feature", "importance", "rel%"))
    tot = overall.sum()
    for i in order:
        print("%-30s %12.5f  %5.1f%%" % (feats[i], overall[i], 100 * overall[i] / tot))

    print("\n=== per-class importance (top 8 each) ===")
    for name, v in per_class.items():
        o = np.argsort(v)[::-1][:8]
        print("\n[%s]  alpha=%.3f" % (name, alpha[CLASSES.index(name)]))
        for i in o:
            print("   %-28s %10.5f" % (feats[i], v[i]))

    # grouped: charm-tag block vs the rest
    ctag_idx = [i for i, f in enumerate(feats)
                if ("ctag2d" in f) or ("cvsl_pnet" in f) or ("cvsb_pnet" in f)]
    print("\n=== grouped ===")
    print("charm-tag block total: %.5f (%.1f%% of total)"
          % (overall[ctag_idx].sum(), 100 * overall[ctag_idx].sum() / tot))
    print("all other features   : %.5f (%.1f%%)"
          % (tot - overall[ctag_idx].sum(), 100 * (tot - overall[ctag_idx].sum()) / tot))


if __name__ == "__main__":
    main()
