"""v11 vs v32: per-bin vjets population + N_eff, to explain why v32's stat-only
floor is lower yet freeze-autoMCStats converges with v11.

N_eff per bin = (sum w)^2 / sum w^2  =  counts^2 / sumw2   (Poisson-equivalent MC events)
rel MC-stat err per bin = sqrt(sumw2)/counts = 1/sqrt(N_eff)
"""
import numpy as np, uproot

FILES = {
    "v11": "/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root",
    "v32": "/eos/home-c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc_v32_v9.root",
}
CHANNELS = ["SR_hplusc", "CR_vjets"]
PROCS = ["hplusc", "higgsbkg", "tt", "st", "diboson", "vjets"]


def bin_table(path, ch, proc):
    with uproot.open(path) as f:
        key = f"{ch}_{proc}"
        if key not in {k.split(";")[0] for k in f.keys()}:
            return None
        h = f[key]
        c, edges = h.to_numpy()
        s2 = h.errors() ** 2
    return c, s2, edges


for tag, path in FILES.items():
    print("=" * 78)
    print(f"### {tag}   {path}")
    for ch in CHANNELS:
        r = bin_table(path, ch, "vjets")
        if r is None:
            print(f"  [{ch}] vjets: MISSING")
            continue
        c, s2, edges = r
        with np.errstate(divide="ignore", invalid="ignore"):
            neff = np.where(s2 > 0, c**2 / s2, 0.0)
            rel = np.where(c != 0, np.sqrt(s2) / np.abs(c), np.inf)
        # total bkg for context
        tot = np.zeros_like(c)
        for p in ["higgsbkg", "tt", "st", "diboson", "vjets"]:
            rr = bin_table(path, ch, p)
            if rr is not None:
                tot += rr[0]
        sig = bin_table(path, ch, "hplusc")
        sigc = sig[0] if sig else np.zeros_like(c)

        print(f"\n  [{ch}]  nbins={len(c)}")
        print(f"  {'bin':>3} {'lo':>7} {'hi':>7} {'vjets':>11} {'N_eff':>9} "
              f"{'rel_err':>8} {'totbkg':>11} {'sig':>8} {'S/sqrt(B)':>9}")
        for i in range(len(c)):
            ssb = sigc[i] / np.sqrt(tot[i]) if tot[i] > 0 else 0.0
            re_s = "inf" if not np.isfinite(rel[i]) else f"{rel[i]*100:7.1f}%"
            print(f"  {i:>3} {edges[i]:7.3f} {edges[i+1]:7.3f} {c[i]:11.3f} "
                  f"{neff[i]:9.1f} {re_s:>8} {tot[i]:11.3f} {sigc[i]:8.4f} {ssb:9.4f}")
        good = np.isfinite(rel) & (c != 0)
        print(f"  --> vjets total={c.sum():.2f}  N_eff(total)={c.sum()**2/s2.sum():.1f}  "
              f"mean rel_err(bins w/ counts)={rel[good].mean()*100:.1f}%  "
              f"bins with N_eff<10: {(neff[good] < 10).sum()}/{good.sum()}")
