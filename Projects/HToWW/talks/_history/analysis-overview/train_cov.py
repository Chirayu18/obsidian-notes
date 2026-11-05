"""Was the v11 TRAINING set already SR-cut? If yes the 'internalised cut' is trivial.

Reads a sample of the b-hive lz4 training shards and reports the mtl2 / dilepton_mass
coverage of the hplusc (signal) class. mtll is not a feature so it cannot be read here;
mtl2>30 and mll are the checkable halves of the SR definition.
"""
import glob, sys
import numpy as np, lz4.frame, pickle

FEATURES = ["dilepton_pt","lepton1_pt","lepton2_pt","cjet_cand_pt","met_pt","mtl1","mtl2",
            "dilepton_mass","delta_R_ll_l1","delta_R_ll_l2","delta_R_ll_c",
            "delta_phi_l1PlusMET_c","delta_phi_l1_MET","delta_phi_l2_MET",
            "cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","nSV"]
I_MTL2 = FEATURES.index("mtl2")
I_MLL  = FEATURES.index("dilepton_mass")

D = "/eos/user/c/cgupta/EPR_task/b-hive/output/DatasetConstructorTask/HPlusCHToWW_multiclass/hwwcom_v11_train"
files = sorted(glob.glob(f"{D}/*.lz4"))
print(f"total shards: {len(files)}")
sample = files[::max(1, len(files)//400)][:400]
print(f"reading {len(sample)} shards\n")

X, Y = [], []
bad = 0
for f in sample:
    try:
        with lz4.frame.open(f, "rb") as fh:
            obj = pickle.load(fh)
    except Exception:
        bad += 1
        continue
    if isinstance(obj, dict):
        x = obj.get("global_features", obj.get("features", obj.get("x")))
        y = obj.get("truth", obj.get("y", obj.get("labels")))
    elif isinstance(obj, (tuple, list)) and len(obj) >= 2:
        x, y = obj[0], obj[1]
    else:
        bad += 1
        continue
    if x is None:
        bad += 1
        continue
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[None, :]
    X.append(x)
    if y is not None:
        y = np.asarray(y)
        Y.append(y.reshape(len(x), -1) if y.size >= len(x) else y)

if not X:
    print(f"could not parse any shard (bad={bad}); dumping one for inspection")
    with lz4.frame.open(sample[0], "rb") as fh:
        o = pickle.load(fh)
    print("type:", type(o))
    if isinstance(o, dict): print("keys:", list(o.keys()))
    elif isinstance(o,(tuple,list)): print("len:", len(o), "elem types:", [type(e) for e in o[:4]])
    sys.exit(0)

X = np.concatenate(X, axis=0)
print(f"parsed events: {len(X):,}  (bad shards: {bad})  X shape {X.shape}")

mtl2 = X[:, I_MTL2]; mll = X[:, I_MLL]
def rep(name, a, cuts):
    print(f"\n{name}: min={a.min():.3f} max={a.max():.3f} mean={a.mean():.3f}")
    for c in cuts:
        print(f"   frac <= {c:<5}: {(a<=c).mean():7.4f}   (N={int((a<=c).sum()):,})")
rep("mtl2 (ALL classes)", mtl2, [10,20,30,40])
rep("dilepton_mass (ALL classes)", mll, [12,30,72,100])

if Y:
    Y = np.concatenate(Y, axis=0)
    print("\nY shape:", Y.shape)
    if Y.ndim == 2 and Y.shape[1] >= 6:
        cls = np.argmax(Y, axis=1)
    else:
        cls = Y.ravel().astype(int)
    n = min(len(cls), len(mtl2))
    cls, m2, ml = cls[:n], mtl2[:n], mll[:n]
    names = ["hplusc","higgsbkg","tt","st","diboson","vjets"]
    print(f"\n{'class':<10s} {'N':>9s} {'mtl2<=30':>10s} {'mtl2 min':>9s} {'mll>100':>9s} {'mll max':>9s}")
    for i, nm in enumerate(names):
        m = (cls == i)
        if not m.any(): continue
        print(f"{nm:<10s} {int(m.sum()):>9d} {100*(m2[m]<=30).mean():>9.2f}% "
              f"{m2[m].min():>9.2f} {100*(ml[m]>100).mean():>8.2f}% {ml[m].max():>9.2f}")
