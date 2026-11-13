"""Summarize existing A held-out inference; never train, score or mutate models."""
import json
from pathlib import Path
import numpy as np
import yaml
from sklearn.metrics import roc_curve, auc, confusion_matrix

ROOT = Path('/eos/user/c/cgupta/HToWW/b-hive')
WORK = Path('/afs/cern.ch/user/c/cgupta/bhive_prod_20261112_sol/A')
TARGET = WORK/'performance_20261113.json'
if TARGET.exists():
    raise FileExistsError(TARGET)
config = yaml.safe_load((ROOT/'config/HPlusCHToWW_2dcats.yml').read_text())
classes = [x.removeprefix('is_') for x in config['truths']]
split = json.loads((ROOT/'output/prod_20261112_sol_A_split/split_manifest.json').read_text())
probs, labels, records, curves = [], [], [], []
for fold in range(5):
    version = f'hwwAv2sol_fde9a35d_f{fold}'
    training = ROOT/'output/TrainingTask/HPlusCHToWW_2dcats'/f'{version}_train'/version/'SimpleMLP_MultiClass/epochs_30/nominal'
    inference = ROOT/'output/InferenceTask/HPlusCHToWW_2dcats'/f'{version}_train'/f'{version}_test'/version/'SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal'
    record = json.loads((training/'training_provenance.json').read_text())
    assert record['status'] == 'completed'
    logits = np.load(inference/'prediction.npy')
    truth = np.load(inference/'truth.npy')
    assert logits.shape == (split['models'][str(fold)]['rows']['test'], len(classes))
    assert truth.shape == (len(logits),) and np.isin(truth, np.arange(len(classes))).all()
    assert np.isfinite(logits).all()
    p = np.exp(logits.astype(np.float64)-logits.max(axis=1, keepdims=True))
    p /= p.sum(axis=1, keepdims=True)
    assert np.isfinite(p).all() and np.allclose(p.sum(axis=1), 1.)
    probs.append(p.astype(np.float32)); labels.append(truth)
    records.append({'fold': fold, 'rows': len(truth), 'prediction': str(inference/'prediction.npy'),
                    'truth': str(inference/'truth.npy'), 'training_provenance': str(training/'training_provenance.json')})
    trace = {'fold': fold}
    for role in ('training', 'validation'):
        with np.load(training/f'{role}_metrics.npz') as data:
            trace[role] = {key: data[key].tolist() for key in ('loss', 'acc')}
            assert len(trace[role]['loss']) == 30 and len(trace[role]['acc']) == 30
            assert np.isfinite(data['loss']).all() and np.isfinite(data['acc']).all()
    curves.append(trace)
    print(f'loaded fold{fold}: {len(truth)} held-out rows', flush=True)
p = np.concatenate(probs); truth = np.concatenate(labels)
assert len(truth) == 6959308
grid = np.r_[0., np.geomspace(1e-6, 1., 512)]
metrics = {}
for i, name in enumerate(classes):
    fpr, tpr, _ = roc_curve(truth == i, p[:, i], drop_intermediate=True)
    metrics[name] = {'auc': float(auc(fpr, tpr)), 'n_positive': int((truth == i).sum()),
                     'fpr': grid.tolist(), 'tpr': np.interp(grid, fpr, tpr).tolist()}
    print(name, metrics[name]['auc'], flush=True)
cm = confusion_matrix(truth, p.argmax(axis=1), labels=np.arange(len(classes)))
report = {'arm': 'A', 'rows': len(truth), 'classes': classes, 'folds': records,
          'weighting': 'unweighted held-out MC events; not luminosity-weighted yields',
          'prediction_transform': 'row-wise softmax of saved logits',
          'one_vs_rest': metrics, 'confusion_counts': cm.tolist(),
          'accuracy': float(np.trace(cm)/cm.sum()), 'training_curves': curves}
TARGET.write_text(json.dumps(report, indent=2)+'\n')
print(TARGET)
