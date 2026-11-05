#!/usr/bin/env python3
"""Generate all training-diagnostic plots for the negrw Marp deck from
negrw_diagnostics.npz. Writes PNGs into --outdir."""
import os, json, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 11,
    "axes.grid": True, "grid.alpha": 0.3, "figure.autolayout": True,
})
POS_C, NEG_C = "#2166ac", "#b2182b"   # blue = positive weight, red = negative

def save(fig, outdir, name):
    p = os.path.join(outdir, name)
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    d = np.load(args.npz, allow_pickle=True)
    features = list(d["features"])
    od = args.outdir

    # ---------- 1. training + validation loss curves (all 20 members) ----------
    train_curves = d["train_curves"]; val_curves = d["val_curves"]
    fig, ax = plt.subplots(figsize=(7, 4.3))
    for i, c in enumerate(train_curves):
        c = np.asarray(c, dtype=float)
        ax.plot(np.arange(1, len(c) + 1), c, color=POS_C, alpha=0.25, lw=1,
                label="train (per member)" if i == 0 else None)
    for i, c in enumerate(val_curves):
        c = np.asarray(c, dtype=float)
        if c.size:
            ax.plot(np.arange(1, len(c) + 1), c, color=NEG_C, alpha=0.25, lw=1,
                    label="validation (per member)" if i == 0 else None)
    ax.set_xlabel("boosting iteration"); ax.set_ylabel("log-loss")
    ax.set_title("Training / validation loss — 20-member ensemble")
    ax.legend(frameon=False)
    save(fig, od, "01_loss_curves.png")

    # ---------- 2. n_iter (early-stopping) distribution ----------
    n_iters = d["n_iters"]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.hist(n_iters, bins=np.arange(min(n_iters)-2, max(n_iters)+3), color=POS_C, alpha=0.85)
    ax.set_xlabel("boosting iterations at early stop"); ax.set_ylabel("# members")
    ax.set_title(f"Early-stopping n_iter  (median {int(np.median(n_iters))})")
    save(fig, od, "02_niter_hist.png")

    # ---------- 3. ROC curve ----------
    fpr, tpr = d["roc_fpr"], d["roc_tpr"]; auc = float(d["ensemble_auc"])
    fig, ax = plt.subplots(figsize=(5.2, 5))
    ax.plot(fpr, tpr, color=POS_C, lw=2, label=f"ensemble (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, lw=1)
    ax.set_xlabel("false positive rate"); ax.set_ylabel("true positive rate")
    ax.set_title("ROC — P(genWeight>0 | x)"); ax.legend(frameon=False, loc="lower right")
    save(fig, od, "03_roc.png")

    # ---------- 4. permutation feature importance ----------
    imp = d["importances"]
    order = np.argsort(imp)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh([features[i] for i in order], imp[order], color=POS_C)
    ax.set_xlabel("Δ log-loss when feature permuted")
    ax.set_title("Permutation feature importance")
    save(fig, od, "04_feature_importance.png")

    # ---------- 5. P+ distribution split by true weight sign ----------
    pe = d["p_edges"]; pc = 0.5 * (pe[:-1] + pe[1:])
    hp, hn = d["p_hist_pos"], d["p_hist_neg"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.step(pc, hp / max(hp.sum(), 1), where="mid", color=POS_C, label="true w > 0")
    ax.step(pc, hn / max(hn.sum(), 1), where="mid", color=NEG_C, label="true w < 0")
    ax.set_xlabel("predicted P₊(x)"); ax.set_ylabel("normalized")
    ax.set_title("Classifier output by true weight sign"); ax.legend(frameon=False)
    save(fig, od, "05_pplus_by_sign.png")

    # ---------- 6. g(x) and δg distributions ----------
    ge = d["g_edges"]; gc = 0.5 * (ge[:-1] + ge[1:]); gh = d["g_hist"]
    se = d["gstd_edges"]; sc = 0.5 * (se[:-1] + se[1:]); sh = d["gstd_hist"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].step(gc, gh, where="mid", color=POS_C)
    axes[0].axvline(float(d["g_central_mean"]), color="k", ls="--", lw=1,
                    label=f"mean {float(d['g_central_mean']):.3f}")
    axes[0].set_xlabel("g(x) = 2·P̄₊ − 1"); axes[0].set_ylabel("events")
    axes[0].set_title("Per-event reweight factor g(x)"); axes[0].legend(frameon=False)
    axes[1].step(sc, sh, where="mid", color=NEG_C)
    axes[1].set_xlabel("δg = 2·std(P₊)  (ensemble spread)"); axes[1].set_ylabel("events")
    axes[1].set_title(f"Ensemble uncertainty  (mean {float(d['g_std_mean']):.3f})")
    save(fig, od, "06_g_and_dg.png")

    # ---------- 7. closure + N_eff on lhe_vpt ----------
    b = d["vpt_bins"]; ctr = 0.5 * (b[:-1] + b[1:])
    nom, rw = d["vpt_nom"], d["vpt_rw"]
    ne_n, ne_r = d["vpt_neff_nom"], d["vpt_neff_rw"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].step(ctr, nom, where="mid", color="k", label="nominal  Σw")
    axes[0].step(ctr, rw, where="mid", color=POS_C, ls="--", label="reweighted  Σ|w|·g")
    axes[0].set_xlabel("LHE V pT [GeV]"); axes[0].set_ylabel("weighted yield")
    axes[0].set_title("Yield closure"); axes[0].legend(frameon=False)
    axes[1].step(ctr, ne_n, where="mid", color="k", label="nominal")
    axes[1].step(ctr, ne_r, where="mid", color=POS_C, label="reweighted")
    axes[1].set_xlabel("LHE V pT [GeV]"); axes[1].set_ylabel("N_eff per bin")
    axes[1].set_title(f"Effective statistics  (+{100*(ne_r.sum()/max(ne_n.sum(),1)-1):.0f}% total)")
    axes[1].legend(frameon=False)
    save(fig, od, "07_closure_neff.png")

    # ---------- 8. input feature panels split by weight sign ----------
    ncol = 4; nrow = int(np.ceil(len(features) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 2.6 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for k, f in enumerate(features):
        ax = axes[k]
        edges = d[f + "__edges"]; c = 0.5 * (edges[:-1] + edges[1:])
        hp = d[f + "__pos"].astype(float); hn = d[f + "__neg"].astype(float)
        nanfrac = float(d[f + "__nanfrac"][0])
        ax.step(c, hp / max(hp.sum(), 1), where="mid", color=POS_C, lw=1)
        ax.step(c, hn / max(hn.sum(), 1), where="mid", color=NEG_C, lw=1)
        ttl = f if nanfrac < 0.005 else f"{f}  (NaN {nanfrac:.0%})"
        ax.set_title(ttl, fontsize=8); ax.tick_params(labelsize=7)
    for k in range(len(features), len(axes)):
        axes[k].axis("off")
    fig.suptitle("Input features — blue: w>0,  red: w<0", y=1.005, fontsize=12)
    save(fig, od, "08_input_features.png")

    # ---------- summary numbers for the deck ----------
    summary = dict(
        n_events=int(d["n_events"]), frac_pos=float(d["frac_pos"]),
        n_models=int(d["n_models"]), subsample_frac=float(d["subsample_frac"]),
        ensemble_logloss=float(d["ensemble_logloss"]), ensemble_auc=float(d["ensemble_auc"]),
        g_mean=float(d["g_central_mean"]), g_min=float(d["g_central_min"]),
        g_max=float(d["g_central_max"]), dg_mean=float(d["g_std_mean"]),
        dg_max=float(d["g_std_max"]),
        yield_nom=float(nom.sum()), yield_rw=float(rw.sum()),
        yield_ratio=float(rw.sum() / max(nom.sum(), 1)),
        neff_nom=float(ne_n.sum()), neff_rw=float(ne_r.sum()),
        neff_gain_pct=float(100 * (ne_r.sum() / max(ne_n.sum(), 1) - 1)),
        hyperparams=json.loads(str(d["hyperparams"])),
        median_niter=int(np.median(n_iters)),
        features=features,
    )
    with open(os.path.join(od, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("wrote", os.path.join(od, "summary.json"))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
