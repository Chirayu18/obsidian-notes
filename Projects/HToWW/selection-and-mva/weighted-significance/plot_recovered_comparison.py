"""Plot recovered cache metrics; no refitting or threshold optimization."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).parent
r = json.loads((root / 'recovered_comparison.json').read_text())
fig, (ax, ratio) = plt.subplots(2, 1, figsize=(8, 6), sharex=True,
                               gridspec_kw={'height_ratios': [2, 1]}, constrained_layout=True)
for version, label, color in [('v32', 'κ-HCE v32-v9 (13 classes)', '#21854a'),
                               ('v11', 'CE v11 (6 classes)', '#2565a8')]:
    curve = r['count_eff_curves'][version]
    ax.plot([v['target'] for v in curve], [v['Z']*1000 for v in curve], label=label, color=color)
ax.set_ylabel('Signed-yield S/√B × 10³')
ax.legend(frameon=False, fontsize=10)
ax.set_title('HToWW: recovered 2022postEE cache comparison', loc='left')
ratio.plot([v['target'] for v in r['ratios']], [v['v32_over_v11'] for v in r['ratios']], color='#6d479e')
ratio.axhline(1, color='gray', linestyle='--', linewidth=1)
ratio.scatter([.5], [1.1441967157251531], color='#6d479e')
ratio.annotate('+14.4% at 50%', (.5, 1.1441967157251531), xytext=(.56, 1.35), fontsize=10,
               arrowprops={'arrowstyle': '-', 'color': '#6d479e'})
ratio.set_ylabel('κ-HCE / CE')
ratio.set_xlabel('Count-based signal efficiency (historical plot convention)')
for a in (ax, ratio):
    a.grid(alpha=.2)
    a.set_xlim(.05, .95)
fig.supxlabel('Agent-reported · full-sample historical cache · model configurations differ\n'
               'Signed weights retained; curves are descriptive, not a loss-only validation.', fontsize=9)
fig.savefig(root/'recovered_weighted_ratio.png', dpi=160)
