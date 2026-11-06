"""Bounded synthetic end-to-end check of build_cards_from_templates.main (no real data).

Run from the higgscharm repo root in the coffea 0.7.30 container with PYTHONPATH=<repo>:
  python3 chain_repro.py <new scratch dir>
Builds one synthetic RUN .coffea per expected 2022postEE MC sample (+1 data sample),
whose execution_checks list exactly the real fileset-JSON files, then runs the CLI.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, yaml
from coffea.util import save
from analysis.workflows.config import WorkflowConfigBuilder
from analysis.features.hww import signature, selection_signature
from analysis.filesets.utils import get_dataset_config
from analysis.processing_checks import expected_mc_samples, fileset_files, sample_kind
WF, YEAR = 'hww_allfix_4fs', '2022postEE'
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True)
cfg = WorkflowConfigBuilder(WF).build_workflow_config()
sys.path.insert(0, 'scripts/combine')
from build_cards_from_templates import configure_era
ecfg = configure_era(cfg, YEAR)
comb = ecfg.combine; cat = next(iter(cfg.event_selection['categories']))
chs = list(comb['channels']); nb = len(comb['binning']['edges']) - 1
ds = get_dataset_config(YEAR); expected = sorted(expected_mc_samples(WF, YEAR)); ref = fileset_files(YEAR)
data = sorted(s for s in ds if sample_kind(s, ds[s]) == 'data' and s in ref)[:1]
print('expected MC samples:', len(expected), ' WG:', [s for s in expected if ds[s]['process'] == 'WG'][:2], '...')
weights = ['nominal'] + [s + d for s in comb['shape_systematics'] for d in ('Up', 'Down')]


def rec(v, chunks, kind, neg=False):
    c = {ch: np.full(nb, float(v)) for ch in chs}
    if neg:
        c['SR_hplusc'][-1] = -50.
    return {'counts': c, 'sumw2': {ch: np.abs(x) for ch, x in c.items()}, 'norm_raw': 1., 'norm_rw': 1.,
            'negrw': {False}, 'kind': {kind}, 'chunks': set(chunks)}


def entry(s):
    chunks = {s + '-c0', s + '-c1'}
    if sample_kind(s, ds[s]) == 'data':
        return {'sumw': 1., 'sumw2': 1., 'events_read': 2, 'chunks_read': 2, 'chunks': chunks, 'selected_events': 0}
    vj = ds[s]['process'].strip() in comb['process_map']['vjets']
    r = {v: rec(1., chunks, 'weight', neg=vj) for v in weights}
    if vj:
        r.update({'CMS_negrw_vjets' + d: rec(1., chunks, 'weight', neg=True) for d in ('Up', 'Down')})
    r['JESUp'], r['JESDown'] = rec(1.1, chunks, 'object'), rec(0.9, chunks, 'object')
    return {'sumw': 1e4, 'sumw2': 1e4, 'events_read': 10, 'chunks_read': 2, 'chunks': chunks, 'selected_events': 5,
            'templates': {cat: r}, 'evaluated_shifts': {'JESUp': set(chunks), 'JESDown': set(chunks)}}


prov = {'mode': {'run'}, 'year': {YEAR}, 'features_hash': {signature(cfg)},
        'selection_hash': {selection_signature(cfg)}, 'folds': {5}, 'model_manifest_hash': {'synthetic'}}
files = []
for s in expected + data:
    p = OUT / f'{s}.coffea'
    save({'samples': {s: entry(s)}, 'provenance': prov,
          'execution_checks': {'expected_entries': 10, 'processed_entries': 10, 'files': {s: set(ref[s])}}}, p)
    files.append(str(p))


def build(name, inputs, extra=()):
    r = subprocess.run([sys.executable, 'scripts/combine/build_cards_from_templates.py', '-w', WF, '-y', YEAR,
                        '--inputs', *inputs, '--output', str(OUT / name), *extra], capture_output=True, text=True)
    last = (r.stderr.strip().splitlines() or [''])[-1]
    print(f'[{name}] exit={r.returncode}', r.stdout.strip()[-200:] if r.returncode == 0 else last)
    return r.returncode


assert build('cards_full', files) == 0
pol = json.loads((OUT / 'cards_full/template_policy.json').read_text())
print(' policy: nominal_bins_floored =', pol['nominal_bins_floored'], ' data skipped =', pol['data_samples_skipped'],
      ' empty-shift fallbacks =', len(pol['object_shift_empty_fallback']))
import uproot
with uproot.open(OUT / 'cards_full/templates.root') as f:
    names = [k for k in f.keys(cycle=False)]
    vj = [k for k in names if 'SR_hplusc' in k and k.endswith('vjets')]
    print(' n histograms:', len(names), ' SR vjets nominal last bin:', f[vj[0]].values()[-1] if vj else 'n/a', vj[:1])
    print(' min bin over all non-data templates:', min(f[k].values().min() for k in names if 'data_obs' not in k))
card = (OUT / 'cards_full/datacard.txt').read_text().splitlines()
print(' datacard lines:', len(card), '| JES row present:', any(l.split()[:2] == ['JES', 'shape'] for l in card))
drop = next(s for s in expected if ds[s]['process'] == 'WG')
partial = [f for f in files if not f.endswith(f'/{drop}.coffea')]
assert build('cards_missing_sample', partial) != 0
(OUT / 'excl.yaml').write_text(yaml.safe_dump({drop: 'synthetic test: deliberately absent'}))
assert build('cards_with_exclusion', partial, ['--exclusions', str(OUT / 'excl.yaml')]) == 0
bad = OUT / 'bad'; bad.mkdir()
s0 = expected[0]
save({'samples': {s0: entry(s0)}, 'provenance': prov,
      'execution_checks': {'expected_entries': 10, 'processed_entries': 10, 'files': {s0: set(sorted(ref[s0])[1:])}}},
     bad / f'{s0}.coffea')
assert build('cards_file_gap', [f for f in files if not f.endswith(f'/{s0}.coffea')] + [str(bad / f'{s0}.coffea')]) != 0
print('CHAIN REPRO DONE')
