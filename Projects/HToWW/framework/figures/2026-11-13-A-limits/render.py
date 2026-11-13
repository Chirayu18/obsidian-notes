import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

folder = Path(__file__).resolve().parent
r = json.loads((folder/'summary.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(10, 4.6))
rows = [('stat_only', 'Statistical uncertainties'), ('rate_systematics', 'Statistical + configured rates')]
for i, (mode, label) in enumerate(rows):
    q = r['modes'][mode]['values']; y = 1-i
    ax.broken_barh([(q[0], q[4]-q[0])], (y-.18, .36), facecolors='#f2ce45')
    ax.broken_barh([(q[1], q[3]-q[1])], (y-.18, .36), facecolors='#62b778')
    ax.plot([q[2], q[2]], [y-.23, y+.23], color='#171717', lw=2)
    ax.text(q[2], y+.31, f"{q[2]:.1f}", ha='center', fontweight='bold')
ax.set(yticks=[1,0], yticklabels=[x[1] for x in rows], ylim=(-.6, 1.7), xlim=(0,1100),
       xlabel='95% CL upper limit on signal strength r')
ax.grid(axis='x', alpha=.2); ax.set_axisbelow(True)
fig.suptitle('Arm A · combined expected limits', fontsize=17, y=.96)
ax.set_title('2022–2023 four eras · blind Asimov · one merged signal region', fontsize=11, pad=10)
fig.legend(handles=[Line2D([0],[0],color='black',lw=2,label='Expected median'),
                   Patch(color='#62b778',label='68% expected band'),
                   Patch(color='#f2ce45',label='95% expected band')],
           loc='lower center', bbox_to_anchor=(.62,.075), ncol=3, fontsize=9, frameon=False)
fig.text(.5,.025,'Both retain autoMCStats and free tt normalization; modelling shape uncertainties are excluded.',
         ha='center',fontsize=9)
fig.subplots_adjust(left=.29,bottom=.27,right=.97,top=.8)
fig.savefig(folder/'A_expected_limits.png',dpi=180)
