"""Extra negrw plots for the deck, built from the REAL combine templates.

P1  SR vjets template: pre-negrw vs negrw, with per-bin MC-stat error bars  (the smoking gun)
P2  Per-bin relative MC-stat error, pre vs post, SR + CR_vjets
P3  Limit cascade: stat-only -> freeze-autoMCStats -> full, baseline vs negrw, v11 + v32
"""
import numpy as np, uproot, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/eos/user/c/cgupta/HToWW/plots/negrw"
import os; os.makedirs(OUT, exist_ok=True)

CUR = "/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root"
BAK = "/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root.bak_pre_negrw"

def get(fn, key):
    with uproot.open(fn) as f:
        keys = {k.split(";")[0] for k in f.keys()}
        if key not in keys:
            return None, None
        h = f[key]
        return h.values(), np.sqrt(h.variances())

# ---------------- P1 : SR vjets template, before vs after ----------------
for CH, tag in (("SR_hplusc", "SR"), ("CR_vjets", "CRvjets")):
    kb = f"{CH}/vjets"
    vb, eb = get(BAK, kb)
    vn, en = get(CUR, kb)
    if vb is None or vn is None:
        print(f"  skip {CH}: missing"); continue
    x = np.arange(len(vb))
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(8.2, 6.2), sharex=True,
                                  gridspec_kw={"height_ratios": [2.4, 1]})
    ax.errorbar(x, vb, yerr=eb, fmt="o", ms=6, color="#b2182b", capsize=3,
                label="baseline  $\\sum w$  (amc@NLO signed)")
    ax.errorbar(x, vn, yerr=en, fmt="s", ms=6, color="#2166ac", capsize=3,
                label="negrw  $\\sum |w|\\,g$  (renorm.)")
    ax.set_ylabel("V+jets yield / bin")
    ax.set_title(f"{CH}: V+jets template, MC-stat errors")
    ax.legend(fontsize=10); ax.grid(alpha=.3)

    with np.errstate(divide="ignore", invalid="ignore"):
        rb = np.where(vb > 0, eb / vb, np.nan)
        rn = np.where(vn > 0, en / vn, np.nan)
    axr.plot(x, 100 * rb, "o-", color="#b2182b", label="baseline")
    axr.plot(x, 100 * rn, "s-", color="#2166ac", label="negrw")
    axr.set_yscale("log")
    axr.set_ylabel("rel. MC-stat err [%]")
    axr.set_xlabel("discriminant bin")
    axr.grid(alpha=.3); axr.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{OUT}/P1_{tag}_vjets_template.png", dpi=150)
    plt.close(fig)
    print(f"  P1_{tag}: baseline mean rel err "
          f"{100*np.nanmean(rb):.1f}%  ->  negrw {100*np.nanmean(rn):.1f}%")
    # print per-bin for the note
    for i in range(len(vb)):
        print(f"     bin{i}: base {vb[i]:9.2f} +- {eb[i]:8.2f}   "
              f"negrw {vn[i]:9.2f} +- {en[i]:8.2f}")

# ---------------- P3 : limit cascade ----------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
data = {
    "v11": dict(base=[771, 1032, 1742], negrw=[788, 1100, 1343]),
    "v32": dict(base=[600, 1068, 1935], negrw=[599, 1083, 1491]),
}
stages = ["stat-only", "freeze\nautoMCStats", "full\n(all syst)"]
for ax, (name, d) in zip(axes, data.items()):
    x = np.arange(3)
    ax.plot(x, d["base"], "o-", ms=9, lw=2.2, color="#b2182b", label="baseline")
    ax.plot(x, d["negrw"], "s-", ms=9, lw=2.2, color="#2166ac", label="negrw")
    for xi, (b, n) in enumerate(zip(d["base"], d["negrw"])):
        ax.annotate(f"{b}", (xi, b), textcoords="offset points",
                    xytext=(0, 11), ha="center", color="#b2182b", fontsize=10)
        ax.annotate(f"{n}", (xi, n), textcoords="offset points",
                    xytext=(0, -17), ha="center", color="#2166ac", fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(stages, fontsize=10)
    ax.set_title(f"{name} builder"); ax.grid(alpha=.3)
    ax.set_ylim(400, 2150)
axes[0].set_ylabel("expected $r_{95}$")
axes[0].legend(fontsize=10)
fig.suptitle("The autoMCStats inflation is what collapses", y=1.0)
fig.tight_layout()
fig.savefig(f"{OUT}/P3_limit_cascade.png", dpi=150)
plt.close(fig)
print("wrote P3_limit_cascade")
