"""Phase-2 morphing validation plots in the layout of the Phase-1 PR validation (cms-sw/cmssw#49991)."""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

RUN = "/eos/user/c/cgupta/phase2morph/run"
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
ON, OFF, BOTH = "#2a78d6", "#8a8a85", "#1baf7a"
INK, MUTED, GRID = "#1f1f1e", "#6b6b66", "#e4e3df"
plt.rcParams.update({
    "font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "legend.frameon": False, "figure.dpi": 130, "savefig.bbox": "tight", "lines.linewidth": 2})
LAB = "CMS Phase-2 simulation, TTbar PU200, 100 events"
def head(ax, t): ax.set_title(t, loc="left", fontsize=9.5, color=MUTED)

out = {}

# ---- 1. count differences, morphing off: this branch vs master (same events, stock config)
def counts(fn):
    t = uproot.open(fn)["dump/dump"]   # highest cycle
    a = t.arrays(["event", "clus", "moduleId"], library="np")
    res = {}
    for ev, cl, mo in zip(a["event"], a["clus"], a["moduleId"]):
        mo = np.asarray(mo); cl = np.asarray(cl)
        ok = (mo != 65535) & (mo < 4000) & (cl >= 0)
        mo, cl = mo[ok], cl[ok]
        mods, npix = np.unique(mo, return_counts=True)
        key = mo.astype(np.int64) * 10**7 + cl
        u = np.unique(key) // 10**7
        cm, nclus = np.unique(u, return_counts=True)
        res[int(ev)] = (dict(zip(mods.tolist(), npix.tolist())), dict(zip(cm.tolist(), nclus.tolist())))
    return res
b = counts(f"{RUN}/dump_branch_numEvent100.root")
m = counts(f"{RUN}/dump_master_numEvent100.root")
dpix, dclus = [], []
for ev in sorted(set(b) & set(m)):
    for mod in set(b[ev][0]) | set(m[ev][0]):
        dpix.append(b[ev][0].get(mod, 0) - m[ev][0].get(mod, 0))
        dclus.append(b[ev][1].get(mod, 0) - m[ev][1].get(mod, 0))
dpix, dclus = np.array(dpix), np.array(dclus)
out["count_diff"] = {"events": len(set(b) & set(m)), "module_events": int(len(dpix)),
                     "pix_nonzero": int((dpix != 0).sum()), "clus_nonzero": int((dclus != 0).sum())}
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
for ax, d, name in ((axs[0], dpix, "pixels"), (axs[1], dclus, "clusters")):
    ax.hist(d, bins=np.arange(-5.5, 6.5, 1), color=ON)
    ax.set_xlabel(f"{name} per module: this branch $-$ master")
    ax.set_ylabel("module-events")
    head(ax, "PU200 TTbar, 100 events, morphing off, all IT modules")
    ax.text(0.03, 0.92, f"{len(d):,} module-events, {int((d != 0).sum())} differ", transform=ax.transAxes)
fig.savefig(f"{OUT}/count_difference.png"); plt.close(fig)

# ---- 2. cluster size without / with morphing (GPU), TBPX L1
c = uproot.open(f"{RUN}/validate_numEvent100.root")["validation/clusters"].arrays(library="np")
off, on = c["morphing"] == 0, c["morphing"] == 1
bins = np.arange(0.5, 61.5, 1)
fig, axs = plt.subplots(2, 2, figsize=(11, 7.5))
for ax, sel, col, name in ((axs[0, 0], off, OFF, "without morphing"), (axs[0, 1], on, ON, "with morphing")):
    ax.hist(np.clip(c["npix"][sel], 1, 60), bins, color=col)
    ax.set_xlabel("cluster size (number of pixels, last bin: overflow)"); ax.set_ylabel("clusters")
    head(ax, f"{LAB}, TBPX L1, {name}")
    ax.text(0.45, 0.85, f"{sel.sum():,} clusters, mean {c['npix'][sel].mean():.2f}", transform=ax.transAxes)
ax = axs[1, 0]
for sel, col, name in ((off, OFF, "without"), (on, ON, "with")):
    ax.hist(np.clip(c["npix"][sel], 1, 60), bins, histtype="step", color=col, density=True, label=f"{name} morphing")
ax.set_yscale("log"); ax.set_xlabel("cluster size (number of pixels)"); ax.set_ylabel("normalised")
ax.legend(); head(ax, "both overlapped (normalised)")
# per module-event: mean cluster size with minus without
key = c["event"].astype(np.int64) * 2**32 + c["detId"].astype(np.int64)
def mean_by(sel):
    k, inv = np.unique(key[sel], return_inverse=True)
    return dict(zip(k.tolist(), (np.bincount(inv, c["npix"][sel]) / np.bincount(inv)).tolist()))
mo, mf = mean_by(on), mean_by(off)
d = np.array([mo[k] - mf[k] for k in mo if k in mf])
ax = axs[1, 1]
ax.hist(d, bins=np.linspace(-0.2, 1.2, 57), color=ON)
ax.set_xlabel("mean cluster size per module: with $-$ without morphing"); ax.set_ylabel("module-events")
head(ax, "cluster-size difference per module")
ax.text(0.45, 0.85, f"mean {d.mean():+.3f} pixels\n{(d < 0).sum()} module-events < 0", transform=ax.transAxes)
fig.tight_layout(); fig.savefig(f"{OUT}/cluster_size_phase1style.png"); plt.close(fig)
out["cluster_size"] = {"off_n": int(off.sum()), "on_n": int(on.sum()),
                       "off_mean": float(c["npix"][off].mean()), "on_mean": float(c["npix"][on].mean()),
                       "per_module_diff_mean": float(d.mean()), "per_module_diff_negative": int((d < 0).sum()),
                       "module_events": int(len(d))}

# ---- 3. fake-digi monitoring table (same entries as the Phase-1 DQM table)
mt = uproot.open(f"{RUN}/validate_numEvent100.root")["validation/modules"].arrays(library="np")
fake = mt["nFakeGPU"]; ev = mt["event"]; evs = np.unique(ev)
def stat(v): v = np.asarray(v, float); return {"entries": int(len(v)), "mean": float(v.mean()) if len(v) else 0.0, "rms": float(v.std()) if len(v) else 0.0}
per_event = [fake[ev == e].sum() for e in evs]
table = {
    "FakeDigisPerEvent": stat(per_event),
    "FakeDigisPerModule": stat(fake[fake > 0]),
    "ModulesWithFakeDigis": stat([(fake[ev == e] > 0).sum() for e in evs]),
    "NFakeDigisBarrel": stat([fake[(ev == e) & (mt["barrel"] == 1)].sum() for e in evs]),
    "NFakeDigisEndcap": stat([fake[(ev == e) & (mt["barrel"] == 0)].sum() for e in evs]),
}
for L in (1, 2, 3, 4):
    table[f"NFakeDigisLayer{L}"] = stat([fake[(ev == e) & (mt["barrel"] == 1) & (mt["layer"] == L)].sum() for e in evs])
table["RealDigisPerModule_L1"] = stat(mt["nReal"][(mt["barrel"] == 1) & (mt["layer"] == 1)])
out["fake_table"] = table
json.dump(out, open(f"{OUT}/phase1style_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
