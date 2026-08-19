import uproot, numpy as np
C = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/outputs/combine"
old = uproot.open(C + "/v11_hplusc_v4.root.bak_pre_negrw")
new = uproot.open(C + "/v11_hplusc_v4.root")
for key in ["SR_hplusc_vjets", "CR_vjets_vjets"]:
    ko = [k for k in old.keys() if k.split(";")[0] == key]
    kn = [k for k in new.keys() if k.split(";")[0] == key]
    if not ko or not kn:
        print(key, "MISSING (old:", bool(ko), "new:", bool(kn), ")"); continue
    ho, hn = old[ko[0]], new[kn[0]]
    co, eo = ho.values(), ho.errors()
    cn, en = hn.values(), hn.errors()
    print("\n=== %s ===" % key)
    print("  yield:      old %.3f -> new %.3f  (ratio %.3f)" % (co.sum(), cn.sum(), cn.sum()/co.sum() if co.sum() else 0))
    ro = np.where(co>0, eo/co, 0); rn = np.where(cn>0, en/cn, 0)
    print("  mean rel MC-stat err/bin: old %.3f -> new %.3f" % (ro[co>0].mean() if (co>0).any() else 0, rn[cn>0].mean() if (cn>0).any() else 0))
    print("  bin | old_c old_relerr | new_c new_relerr")
    for b in range(len(co)):
        print("  %3d | %8.3f %6.1f%% | %8.3f %6.1f%%" % (b, co[b], 100*ro[b], cn[b], 100*rn[b]))
