"""Score runs_rescue2 (9 runs) on the 20 training-balance test subsamples, per the committed rule.
Replicates check/rescore_natural.py (subsamples, M1, M2, Hcc vs Hbb / QCD) without torch/side effects.
Selected logits: raw for ce_es/k2n ('ps'), logits - log w_c for k2t ('cor'), as hist.json['selected'] says.
Read-only on EOS inputs. usage: python3 score_rescue2.py <htoww_replica dir> <out.json>
"""
import json, sys, numpy as np
from sklearn.metrics import roc_auc_score
HERE, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, HERE)
from replica_spec import COUNTS, SIG
K = 20
BETA = {"ce_es": 0.0, "k2n": 0.0, "k2t": 0.5}

def lse(a): m = a.max(1, keepdims=True); return (m[:, 0] + np.log(np.exp(a - m).sum(1)))
def ovr(L): return L[:, SIG] - lse(np.delete(L, SIG, 1))

Y0 = np.load(f"{HERE}/runs_rescue2/ce_es_s0/test_truth.npy").astype(np.int64)
n_test = np.bincount(Y0, minlength=10); r = (n_test / COUNTS).min(); take = np.floor(COUNTS * r).astype(int)
byc = [np.flatnonzero(Y0 == c) for c in range(10)]
subs = []
for k in range(K):
    rng = np.random.default_rng(20261103 + k)
    subs.append(np.sort(np.concatenate([rng.choice(byc[c], take[c], replace=False) for c in range(10)])))
print("r", r, "take", take.tolist(), "total", take.sum(), flush=True)

def score(L, idx):
    s, y = ovr(L[idx]), Y0[idx]; sig = y == SIG
    m = {"M1": float(roc_auc_score(sig, s))}
    t = np.quantile(s[sig], 0.5); B = (s[~sig] > t).sum() / r
    m["M2"] = float(COUNTS[SIG] * (s[sig] > t).mean() / np.sqrt(B))
    for c, nm in ((1, "Hcc_vsHbb"), (0, "Hcc_vsQCD")):
        sel = (y == SIG) | (y == c)
        m[nm] = float(roc_auc_score(y[sel] == SIG, L[idx][sel, SIG] - L[idx][sel, c]))
    return m

res = {"r": float(r), "take": take.tolist(), "runs": {}}
for arm in ("ce_es", "k2n", "k2t"):
    logw = BETA[arm] * np.log(COUNTS.max() / COUNTS)
    for s in range(3):
        d = f"{HERE}/runs_rescue2/{arm}_s{s}"
        sel = json.load(open(f"{d}/hist.json"))["selected"]
        assert (np.load(f"{d}/test_truth.npy").astype(np.int64) == Y0).all()
        for tag, fn, shift in (("selected", "test_logits_selected_fp16.npy", logw if sel["score"] == "cor" else 0.0),
                               ("final_raw", "test_logits_fp16.npy", 0.0),
                               ("final_cor", "test_logits_fp16.npy", logw)):
            if tag == "final_cor" and BETA[arm] == 0: continue
            L = np.load(f"{d}/{fn}").astype(np.float32) - np.float32(shift) if not np.isscalar(shift) else np.load(f"{d}/{fn}").astype(np.float32)
            ms = [score(L, i) for i in subs]
            res["runs"][f"{arm}_s{s}:{tag}"] = {"sel": sel, **{k: [m[k] for m in ms] for k in ms[0]}}
            print(arm, s, tag, sel["it"], sel["score"], {k: round(ms[0][k], 5) for k in ms[0]}, flush=True)
            json.dump(res, open(OUT, "w"))
print("DONE")
