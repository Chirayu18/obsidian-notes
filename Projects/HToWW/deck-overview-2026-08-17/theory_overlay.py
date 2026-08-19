"""Decompose each theory variation into RATE vs SHAPE in the v32 SR.
If the +315 theory tax is MIGRATION, the shape-after-renorm part is large.
If it is pure normalization, shape part ~ 0 and the fix is a norm/shape split."""
import numpy as np, uproot

F="/eos/home-c/cgupta/HToWW/b-hive/combine_inputs/v11_hplusc_v32_v9.root"
CH="SR_hplusc"
PROCS=["tt","vjets","st","diboson","higgsbkg"]
VARS=["scalevar_muR","scalevar_muF","scalevar_muR_muF","ps_isr","ps_fsr"]

f=uproot.open(F)
ks={k.split(';')[0] for k in f.keys()}
def get(n):
    return f[n].to_numpy()[0] if n in ks else None

sig=get(f"{CH}_hplusc")
live=None
print(f"{'process':<10}{'variation':<18}{'rate%':>9}{'shapeRMS%':>11}{'maxbin%':>9}{'shape/rate':>11}  verdict")
print("-"*82)
rows=[]
for p in PROCS:
    nom=get(f"{CH}_{p}")
    if nom is None or nom.sum()<=0: continue
    if live is None: live=nom>0
    m=nom>0
    for v in VARS:
        up,dn=get(f"{CH}_{p}_{v}Up"),get(f"{CH}_{p}_{v}Down")
        if up is None or dn is None: continue
        for tag,var in (("Up",up),("Dn",dn)):
            rate=var.sum()/nom.sum()-1.0
            # renormalize variation to nominal yield -> pure shape residual
            ren=var*(nom.sum()/var.sum()) if var.sum()>0 else var
            resid=np.zeros_like(nom); resid[m]=ren[m]/nom[m]-1.0
            # weight shape residual by nominal yield (bins that matter)
            w=nom[m]/nom[m].sum()
            srms=np.sqrt(np.sum(w*resid[m]**2))
            smax=np.max(np.abs(resid[m])) if m.any() else 0
            ratio=srms/abs(rate) if abs(rate)>1e-9 else np.inf
            rows.append((p,v,tag,rate,srms,smax,ratio))

for p,v,tag,rate,srms,smax,ratio in rows:
    verdict = "SHAPE/migration" if ratio>1.0 else ("mixed" if ratio>0.3 else "RATE-dominated")
    rs = "inf" if not np.isfinite(ratio) else f"{ratio:10.2f}"
    print(f"{p:<10}{v+' '+tag:<18}{rate*100:8.2f}%{srms*100:10.2f}%{smax*100:8.2f}%{rs}  {verdict}")

# aggregate: how much of the total theory effect is rate vs shape, yield-weighted
print("\n=== aggregate over tt+vjets (the SR-dominant bkgs) ===")
for p in ["tt","vjets"]:
    sel=[r for r in rows if r[0]==p]
    if not sel: continue
    mr=np.mean([abs(r[3]) for r in sel]); ms=np.mean([r[4] for r in sel])
    print(f"  {p:<8} mean|rate|={mr*100:6.2f}%   mean shapeRMS={ms*100:6.2f}%   -> "
          + ("SHAPE dominates" if ms>mr else "RATE dominates"))

# where does the signal live, and what is the shape residual THERE?
print("\n=== shape residual in the SIGNAL-WEIGHTED bins (what the limit feels) ===")
sw=sig/sig.sum() if sig is not None and sig.sum()>0 else None
if sw is not None:
    for p in ["tt","vjets"]:
        nom=get(f"{CH}_{p}"); m=nom>0
        for v in VARS:
            up=get(f"{CH}_{p}_{v}Up")
            if up is None: continue
            ren=up*(nom.sum()/up.sum())
            resid=np.zeros_like(nom); resid[m]=ren[m]/nom[m]-1.0
            eff=np.sum(sw[m]*resid[m])
            print(f"  {p:<8}{v:<18} signal-weighted shape shift = {eff*100:+7.2f}%")
