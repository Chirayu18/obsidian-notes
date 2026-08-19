"""Can ANY rebinning of v32's SR help? Merge adjacent bins in the live SR span and
watch N_eff vs signal-resolution. Pure histogram arithmetic -- no re-inference."""
import numpy as np, uproot

F = "/eos/home-c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc_v32_v9.root"
PROCS = ["higgsbkg", "tt", "st", "diboson", "vjets"]

with uproot.open(F) as f:
    sig, edges = f["SR_hplusc_hplusc"].to_numpy()
    sig_s2 = f["SR_hplusc_hplusc"].errors()**2
    bkg = np.zeros_like(sig); bkg_s2 = np.zeros_like(sig)
    vj = np.zeros_like(sig); vj_s2 = np.zeros_like(sig)
    for p in PROCS:
        c, _ = f[f"SR_hplusc_{p}"].to_numpy(); s2 = f[f"SR_hplusc_{p}"].errors()**2
        bkg += c; bkg_s2 += s2
        if p == "vjets": vj, vj_s2 = c, s2

live = bkg > 0
print(f"live SR bins: {live.sum()} of {len(bkg)}  (idx {np.flatnonzero(live)})")

def report(tag, s, b, b2, v, v2):
    with np.errstate(divide="ignore", invalid="ignore"):
        neff_b = np.where(b2>0, b**2/b2, 0)
        neff_v = np.where(v2>0, v**2/v2, 0)
        rel_b  = np.where(b>0, np.sqrt(b2)/b, np.inf)
    # Asimov-ish sensitivity proxy: sum over bins of s^2/(b + b2)  (MC-stat degraded)
    with np.errstate(divide="ignore", invalid="ignore"):
        q_stat = np.nansum(np.where(b>0, s**2/b, 0))               # stat-only
        q_mc   = np.nansum(np.where(b>0, s**2/(b + b2), 0))        # + MC-stat in denom
    print(f"\n  {tag}: {len(b)} bins")
    print(f"    {'i':>2} {'sig':>9} {'bkg':>10} {'vjets':>9} {'Neff_b':>8} {'Neff_v':>8} {'relB':>7}")
    for i in range(len(b)):
        print(f"    {i:>2} {s[i]:9.4f} {b[i]:10.2f} {v[i]:9.2f} {neff_b[i]:8.1f} {neff_v[i]:8.1f} {rel_b[i]*100:6.1f}%")
    print(f"    -> sqrt(q_stat)={np.sqrt(q_stat):.5f}  sqrt(q_mcstat)={np.sqrt(q_mc):.5f} "
          f" penalty={100*(1-np.sqrt(q_mc/q_stat)):.1f}%")
    return np.sqrt(q_stat), np.sqrt(q_mc)

L = np.flatnonzero(live)
s, b, b2, v, v2 = sig[L], bkg[L], bkg_s2[L], vj[L], vj_s2[L]
base = report("CURRENT (6 live bins)", s, b, b2, v, v2)

# merge groups of k adjacent bins (from the low end, keeping the top bins finest)
for k in (2, 3):
    for keep_top in (0, 1, 2):
        arr = list(range(len(b)))
        head = arr[:len(arr)-keep_top] if keep_top else arr
        tail = arr[len(arr)-keep_top:] if keep_top else []
        groups = [head[i:i+k] for i in range(0, len(head), k)] + [[t] for t in tail]
        if len(groups) < 2: continue
        agg = lambda x: np.array([x[g].sum() for g in groups])
        report(f"merge k={k}, keep_top={keep_top}", agg(s), agg(b), agg(b2), agg(v), agg(v2))
