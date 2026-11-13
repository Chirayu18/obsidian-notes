"""Render existing measured A metrics; no model fitting or data processing."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

folder = Path(__file__).resolve().parent
r = json.loads((folder/'performance.json').read_text())
plt.rcParams.update({'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.dpi': 180, 'font.family': 'DejaVu Sans'})
names = {'hplusc': 'H+c', 'higgsbkg': 'Higgs backgrounds', 'tt': 'tt̄', 'st': 'Single top',
         'diboson': 'Diboson', 'vjets': 'V+jets'}
colors = ['#0072b2', '#e69f00', '#009e73', '#cc79a7', '#d55e00', '#56b4e9']
fig, ax = plt.subplots(figsize=(9.5, 6.2))
for color, cls in zip(colors, r['classes']):
    d = r['one_vs_rest'][cls]
    ax.plot(d['fpr'], d['tpr'], lw=2, color=color,
            label=f"{names[cls]}   AUC {d['auc']:.3f}")
chance = np.geomspace(1e-5, 1., 512)
ax.plot(chance, chance, color='#777777', lw=1, ls='--')
ax.set(xscale='log', xlim=(1e-5, 1), ylim=(0, 1.02),
       xlabel='False positive rate (all other classes)', ylabel='True positive rate',
       title='Arm A · held-out classification performance')
ax.grid(alpha=.18, which='both')
ax.legend(loc='lower right', fontsize=10, frameon=True)
fig.text(.13, .025, f"{r['rows']:,} MC events · five held-out folds · unweighted one-vs-rest", fontsize=10)
fig.subplots_adjust(bottom=.15, top=.9, right=.97)
fig.savefig(folder/'A_heldout_roc.png'); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for fold, color in zip(r['training_curves'], colors):
    x = np.arange(1, 31)
    for ax, key in zip(axes, ['loss', 'acc']):
        ax.plot(x, fold['training'][key], color=color, lw=1.5, label=f"Fold {fold['fold']}")
        ax.plot(x, fold['validation'][key], color=color, lw=1.5, ls='--')
for ax, label in zip(axes, ['Reported training objective', 'Reported classification accuracy']):
    ax.set(xlabel='Epoch', ylabel=label, xlim=(1, 30))
    ax.grid(alpha=.2)
axes[0].legend(fontsize=9, ncol=2)
fig.suptitle('Arm A · training and internal validation', fontsize=15)
fig.text(.5, .025, 'Solid: training   Dashed: b-hive internal validation   ·   30 epochs per fold', ha='center', fontsize=10)
fig.tight_layout(rect=(0, .07, 1, .93))
fig.savefig(folder/'A_training_curves.png'); plt.close(fig)

cm = np.asarray(r['confusion_counts'], dtype=float)
cm /= cm.sum(axis=1, keepdims=True)
fig, ax = plt.subplots(figsize=(8.5, 6.5))
im = ax.imshow(cm, vmin=0, vmax=1, cmap='Blues')
for i in range(len(cm)):
    for j in range(len(cm)):
        ax.text(j, i, f'{100*cm[i,j]:.1f}%', ha='center', va='center', fontsize=10,
                color='white' if cm[i,j]>.5 else '#222222')
labels = [names[c] for c in r['classes']]
ax.set(xticks=range(len(cm)), yticks=range(len(cm)), xticklabels=labels, yticklabels=labels,
       xlabel='Predicted class', ylabel='True class', title='Arm A · held-out confusion matrix')
plt.setp(ax.get_xticklabels(), rotation=35, ha='right')
fig.colorbar(im, ax=ax, label='Fraction within true class')
fig.text(.5, .025, 'Unweighted MC events · rows normalized separately · no luminosity weighting', ha='center', fontsize=10)
fig.tight_layout(rect=(0, .07, 1, 1))
fig.savefig(folder/'A_confusion_matrix.png'); plt.close(fig)
