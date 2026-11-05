"""Verify deck-1 numeric claims against the negrw diagnostics npz."""
import numpy as np
d = np.load("/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/negrw_diagnostics.npz",
            allow_pickle=True)
def g(k):
    a = d[k]
    return a.item() if a.shape == () else a

claims = {
 "n_events (deck: 9,832,308)": g("n_events"),
 "frac_pos (deck: 0.836)":     g("frac_pos"),
 "ensemble_logloss (0.331)":   g("ensemble_logloss"),
 "ensemble_auc (0.829)":       g("ensemble_auc"),
 "g mean (0.672)":             g("g_central_mean"),
 "g min (-0.991)":             g("g_central_min"),
 "g max (0.993)":              g("g_central_max"),
 "dg mean (0.006)":            g("g_std_mean"),
 "dg max (0.467)":             g("g_std_max"),
 "n_models (20)":              g("n_models"),
 "subsample (0.6)":            g("subsample_frac"),
}
for k, v in claims.items():
    print(f"  {k:34s} -> {v}")

nom = g("vpt_nom"); rw = g("vpt_rw")
ne_n = g("vpt_neff_nom"); ne_r = g("vpt_neff_rw")
print(f"\n  closure  sum|w|g / sum w  (deck: 0.994) -> {rw.sum()/nom.sum():.4f}")
print(f"  N_eff nominal (deck 2.92M) -> {ne_n.sum():.4e}")
print(f"  N_eff reweight (deck 4.68M) -> {ne_r.sum():.4e}")
print(f"  gain (deck +60%) -> {ne_r.sum()/ne_n.sum():.4f}")
ni = g("n_iters")
print(f"\n  n_iters: median {np.median(ni):.0f}  min {ni.min()}  max {ni.max()}  (deck: all hit 200 ceiling)")
print(f"  features: {len(g('features'))} (deck: 20)")
print(f"  hyperparams: {g('hyperparams')}")
