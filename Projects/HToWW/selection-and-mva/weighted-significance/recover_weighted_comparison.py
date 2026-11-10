"""Read the existing paired cache; report signed-weight S/sqrt(B), without refitting.

Run on lxplus with its existing numpy/pandas/pyarrow environment. JSON goes to stdout.
The primary thresholds reproduce make_new_plots.py's COUNT-based signal percentiles.
No event weights are clipped. sumw2 errors are MC-only delta-method diagnostics.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/eos/user/c/cgupta/HToWW/b-hive')
CACHE = ROOT / 'combine_inputs/new_v9v11_scored_2022postEE.parquet'
df = pd.read_parquet(CACHE, columns=['v32_hplusc', 'v11_hplusc', 'v32cls', 'v11cls', 'w_lumi'])
sig = df.v32cls.to_numpy() == 'hplusc'
assert np.array_equal(sig, df.v11cls.to_numpy() == 'hplusc')
w = df.w_lumi.to_numpy(dtype=float)
assert np.isfinite(w).all()

def summary(mask):
    v = w[mask]
    return dict(n=int(mask.sum()), negative=int((v < 0).sum()), sumw=float(v.sum()),
                sumabsw=float(abs(v).sum()), sumw2=float((v*v).sum()))

def evaluate(score, threshold):
    passed = score >= threshold
    s, b = summary(passed & sig), summary(passed & ~sig)
    S, B = s['sumw'], b['sumw']
    z = S / np.sqrt(B) if B > 0 else None
    variance = s['sumw2']/B + S*S*b['sumw2']/(4*B**3) if B > 0 else None
    return dict(threshold=float(threshold), S=s, B=b, Z=z,
                mc_error=float(np.sqrt(variance)) if variance is not None else None,
                count_eff=s['n']/int(sig.sum()), weighted_eff=S/w[sig].sum())

result = dict(cache=str(CACHE), cache_bytes=CACHE.stat().st_size,
              cache_mtime_ns=CACHE.stat().st_mtime_ns, signal=summary(sig), background=summary(~sig),
              classes={str(c): summary(df.v32cls.to_numpy() == c) for c in df.v32cls.unique()},
              provenance={}, count_eff_curves={}, weighted_eff_curves={})
for relative in ['scripts/make_new_plots.py', 'scripts/build_v9v11_cache.py', 'train_v32.sh', 'train_v11.sh']:
    p = ROOT / relative
    result['provenance'][relative] = hashlib.sha256(p.read_bytes()).hexdigest()
effs = sorted(set(np.linspace(.05, .95, 50).tolist() + [.05, .1, .2, .3, .5, .7, .9]))
for version in ['v11', 'v32']:
    score = df[f'{version}_hplusc'].to_numpy(dtype=float)
    assert np.isfinite(score).all()
    result['count_eff_curves'][version] = [dict(target=e, **evaluate(score, np.percentile(score[sig], 100*(1-e)))) for e in effs]
    # Additional comparison at weighted efficiency is meaningful only for positive signal measure.
    if (w[sig] >= 0).all() and w[sig].sum() > 0:
        order = np.argsort(score[sig])[::-1]
        ss, ws = score[sig][order], w[sig][order]
        cs = np.cumsum(ws)
        result['weighted_eff_curves'][version] = [dict(target=e, **evaluate(score, ss[min(np.searchsorted(cs, e*cs[-1]), len(ss)-1)])) for e in [.05,.1,.2,.3,.5,.7,.9]]
result['ratios'] = []
for a,b in zip(result['count_eff_curves']['v32'], result['count_eff_curves']['v11']):
    assert a['target'] == b['target']
    result['ratios'].append(dict(target=a['target'], v32_over_v11=a['Z']/b['Z'] if a['Z'] is not None and b['Z'] is not None and b['Z'] > 0 else None))
print(json.dumps(result, indent=2, allow_nan=False))
