#!/usr/bin/env python3
"""
negweight_reweight_train_diag.py -- SAME training as negweight_reweight_train.py
(production-equivalent: identical FEATURES, N_MODELS, hyperparameters, seeding) but
additionally persists a rich diagnostics bundle for plotting:

  <outdir>/negrw_models.joblib      -- the ensemble (identical schema to production)
  <outdir>/negrw_diagnostics.npz    -- everything needed for the training PPT plots

Run this INSIDE the Condor worker singularity image so the pickle is sklearn-version
matched to the workers (fixes the 1.4.2 vs 1.7.2 load blocker).
"""
import sys, os, argparse, glob, json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, roc_auc_score, roc_curve

FEATURES = [
    "lhe_njets", "lhe_nb", "lhe_nc", "lhe_nuds", "lhe_nglu", "lhe_npnlo",
    "lhe_ht", "lhe_htincoming", "lhe_vpt", "lhe_alphas",
    "genparton_multiplicity", "genparton_n_pt20", "genparton_n_pt100", "genparton_n_pt200",
    "genparton_incoming1_pdgId", "genparton_incoming2_pdgId",
    "genparton1_pt", "genparton1_eta", "genparton2_pt", "genparton2_eta",
]
N_MODELS = 20
SUBSAMPLE_FRAC = 0.6


def load(paths):
    # only read the columns we actually need (features + weight) to keep peak
    # memory low -- the parquets carry ~40 reco columns we never touch here.
    want = FEATURES + ["weight_nominal"]
    dfs = []
    for p in paths:
        for f in glob.glob(p):
            dfs.append(pd.read_parquet(f, columns=want))
    if not dfs:
        sys.exit(f"no parquet found under {paths}")
    return pd.concat(dfs, ignore_index=True)


def prep(df):
    y = (df["weight_nominal"].to_numpy() > 0).astype(int)
    X = df[FEATURES].to_numpy(dtype=np.float32)
    return X, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", required=True)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    df = load(args.train)
    X, y = prep(df)
    n = len(y); fpos = float(y.mean())
    print(f"loaded {n} events; frac positive = {fpos:.3f}  (neg = {1-fpos:.3f})", flush=True)
    if fpos in (0.0, 1.0):
        sys.exit("degenerate: all weights same sign, nothing to learn")

    rng = np.random.default_rng(args.seed)
    models = []
    train_curves = []       # per-model training log-loss trajectory (-train_score_)
    val_curves = []         # per-model validation log-loss trajectory (-validation_score_)
    n_iters = []
    for m in range(N_MODELS):
        idx = rng.choice(n, size=int(SUBSAMPLE_FRAC * n), replace=False)
        clf = HistGradientBoostingClassifier(
            loss="log_loss", max_iter=200, learning_rate=0.05,
            max_depth=4, l2_regularization=1.0,
            early_stopping=True, validation_fraction=0.15,
            random_state=args.seed + m,
        )
        clf.fit(X[idx], y[idx])
        models.append(clf)
        # sklearn stores these as negative loss (higher = better). Negate -> log-loss.
        tr = -np.asarray(clf.train_score_, dtype=float)
        train_curves.append(tr)
        if getattr(clf, "validation_score_", None) is not None:
            val_curves.append(-np.asarray(clf.validation_score_, dtype=float))
        else:
            val_curves.append(np.array([]))
        n_iters.append(int(clf.n_iter_))
        if m == 0 or (m + 1) % 5 == 0:
            print(f"  trained model {m+1}/{N_MODELS} (n_iter={clf.n_iter_})", flush=True)

    # ----- ensemble predictions on full training set -----
    P = np.stack([clf.predict_proba(X)[:, 1] for clf in models], axis=0)   # (20, n)
    p_mean = P.mean(axis=0)
    g_central = 2 * p_mean - 1
    g_std = (2 * P).std(axis=0)
    print(f"\ng(x): mean {g_central.mean():.3f}  in [{g_central.min():.3f},{g_central.max():.3f}]", flush=True)
    print(f"delta_g (ensemble std): mean {g_std.mean():.3f}  max {g_std.max():.3f}", flush=True)

    # ensemble metrics
    ll = float(log_loss(y, p_mean))
    auc = float(roc_auc_score(y, p_mean))
    fpr, tpr, _ = roc_curve(y, p_mean)
    print(f"ensemble log-loss {ll:.4f}   AUC {auc:.4f}", flush=True)

    # ----- feature importance via single-pass permutation on a subsample -----
    imp_rng = np.random.default_rng(args.seed + 999)
    sub = imp_rng.choice(n, size=min(200_000, n), replace=False)
    Xs, ys = X[sub], y[sub]
    base_ll = log_loss(ys, np.stack([m.predict_proba(Xs)[:, 1] for m in models]).mean(0))
    importances = np.zeros(len(FEATURES))
    for j in range(len(FEATURES)):
        Xp = Xs.copy()
        Xp[:, j] = imp_rng.permutation(Xp[:, j])
        pll = log_loss(ys, np.stack([m.predict_proba(Xp)[:, 1] for m in models]).mean(0))
        importances[j] = pll - base_ll   # increase in log-loss when feature scrambled

    # ----- closure on lhe_vpt: Sum w  vs  Sum|w|*g, with N_eff -----
    w = df["weight_nominal"].to_numpy()
    vpt = df["lhe_vpt"].to_numpy()
    bins = np.linspace(0, 400, 21)
    nom, _ = np.histogram(vpt, bins=bins, weights=w)
    rw, _ = np.histogram(vpt, bins=bins, weights=np.abs(w) * g_central)
    var_nom, _ = np.histogram(vpt, bins=bins, weights=w**2)
    var_rw, _ = np.histogram(vpt, bins=bins, weights=(np.abs(w) * g_central)**2)
    neff_nom = np.where(var_nom > 0, nom**2 / var_nom, 0)
    neff_rw = np.where(var_rw > 0, rw**2 / var_rw, 0)
    print("\nCLOSURE on lhe_vpt:", flush=True)
    print(f" TOTAL yield nominal {nom.sum():.1f}  reweight {rw.sum():.1f}  "
          f"(ratio {rw.sum()/nom.sum() if nom.sum() else float('nan'):.3f})", flush=True)
    print(f" Neff sum nominal {neff_nom.sum():.0f}  reweight {neff_rw.sum():.0f}", flush=True)

    # ----- per-feature histograms split by weight sign (for input-feature plots) -----
    feat_hists = {}
    pos = y == 1
    for j, f in enumerate(FEATURES):
        col = X[:, j]
        finite = col[np.isfinite(col)]
        if finite.size == 0:
            continue
        lo, hi = np.percentile(finite, [0.5, 99.5])
        if lo == hi:
            hi = lo + 1.0
        edges = np.linspace(lo, hi, 41)
        hp, _ = np.histogram(col[pos & np.isfinite(col)], bins=edges)
        hn, _ = np.histogram(col[~pos & np.isfinite(col)], bins=edges)
        nan_frac = float(np.mean(~np.isfinite(col)))
        feat_hists[f + "__edges"] = edges
        feat_hists[f + "__pos"] = hp
        feat_hists[f + "__neg"] = hn
        feat_hists[f + "__nanfrac"] = np.array([nan_frac])

    # P+ distribution and g distribution histograms
    p_edges = np.linspace(0, 1, 51)
    p_hist_pos, _ = np.histogram(p_mean[pos], bins=p_edges)
    p_hist_neg, _ = np.histogram(p_mean[~pos], bins=p_edges)
    g_edges = np.linspace(-1, 1, 61)
    g_hist, _ = np.histogram(g_central, bins=g_edges)
    gstd_edges = np.linspace(0, max(0.01, g_std.max()), 61)
    gstd_hist, _ = np.histogram(g_std, bins=gstd_edges)

    # ----- persist diagnostics -----
    np.savez_compressed(
        os.path.join(args.outdir, "negrw_diagnostics.npz"),
        features=np.array(FEATURES),
        n_events=n, frac_pos=fpos, n_models=N_MODELS,
        subsample_frac=SUBSAMPLE_FRAC,
        n_iters=np.array(n_iters),
        # per-model curves are ragged -> object array
        train_curves=np.array(train_curves, dtype=object),
        val_curves=np.array(val_curves, dtype=object),
        ensemble_logloss=ll, ensemble_auc=auc,
        roc_fpr=fpr, roc_tpr=tpr,
        importances=importances,
        vpt_bins=bins, vpt_nom=nom, vpt_rw=rw,
        vpt_neff_nom=neff_nom, vpt_neff_rw=neff_rw,
        g_central_mean=float(g_central.mean()),
        g_central_min=float(g_central.min()), g_central_max=float(g_central.max()),
        g_std_mean=float(g_std.mean()), g_std_max=float(g_std.max()),
        p_edges=p_edges, p_hist_pos=p_hist_pos, p_hist_neg=p_hist_neg,
        g_edges=g_edges, g_hist=g_hist,
        gstd_edges=gstd_edges, gstd_hist=gstd_hist,
        hyperparams=json.dumps(dict(loss="log_loss", max_iter=200, learning_rate=0.05,
                                    max_depth=4, l2_regularization=1.0,
                                    early_stopping=True, validation_fraction=0.15)),
        **feat_hists,
    )
    print(f"saved diagnostics -> {os.path.join(args.outdir, 'negrw_diagnostics.npz')}", flush=True)

    import joblib
    out = os.path.join(args.outdir, "negrw_models.joblib")
    joblib.dump({"models": models, "features": FEATURES,
                 "n_models": N_MODELS, "frac_pos": fpos}, out)
    # record sklearn version alongside so the loader can sanity-check
    import sklearn
    with open(os.path.join(args.outdir, "sklearn_version.txt"), "w") as fh:
        fh.write(sklearn.__version__ + "\n")
    print(f"saved {N_MODELS}-model ensemble -> {out}  (sklearn {sklearn.__version__})", flush=True)


if __name__ == "__main__":
    main()
