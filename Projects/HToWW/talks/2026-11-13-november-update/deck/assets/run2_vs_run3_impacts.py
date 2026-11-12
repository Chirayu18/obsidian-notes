# Run 2 (HIG-24-009 Table 3, 1POI) vs October Run 3 card group-freeze impacts.
# Values copied from Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3.md
import sys, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[("Statistical (data)",60.0,57.2,57.2),("cH flavour-scheme modelling",22.1,25.0,3.2),
("Scale / PDF / PS",None,46.1,11.3),("Higgs background",21.4,7.3,0.3),("Other backgrounds",4.5,0.0,0.0),
("tt modelling",None,23.2,2.7),("MC statistics",6.2,44.9,10.6),("Pileup",4.3,0.5,0.0),
("Leptons",4.6,26.0,3.4),("JES / JER",6.0,17.4,1.5),("c-tagging",5.9,23.5,2.8),
("tt normalisation",5.6,0.0,0.0),("Luminosity",None,3.1,0.0)]
T,O,INK,MUT,GRID='#0a85b0','#d9701a','#1f2a30','#6b7780','#e3e8eb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14})
fig,ax=plt.subplots(figsize=(9.6,5.6),dpi=160)
h=0.26; n=len(rows)
for i,(lab,r2,q,l) in enumerate(rows):
    y=n-1-i
    if r2 is None:
        ax.text(0.6,y+h,'Run 2: inside group above' if lab!='Luminosity' else 'Run 2: not listed',va='center',fontsize=11,color=MUT,style='italic')
    else:
        ax.barh(y+h,r2,h*0.9,color=T); ax.text(r2+0.8,y+h,f'{r2:g}',va='center',fontsize=11,color=INK)
    ax.barh(y,q,h*0.9,color=O); ax.text(q+0.8,y,f'{q:g}',va='center',fontsize=11,color=INK)
    ax.barh(y-h,l,h*0.9,facecolor='white',edgecolor=O,linewidth=1.2)
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1],color=INK); ax.tick_params(axis='y',labelcolor=INK)
ax.set_xlim(0,66); ax.set_xlabel('Impact on σ(μ) when the group is frozen [%]',color=INK)
ax.xaxis.grid(True,color=GRID,lw=0.8); ax.set_axisbelow(True)
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(MUT); ax.tick_params(colors=MUT,length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=T,label='Run 2, 138 fb⁻¹ (HIG-24-009 Tab. 3, 1POI)'),
 Patch(color=O,label='Run 3 Oct. card, 61.9 fb⁻¹: √(σ²−σ²_frozen)/σ'),
 Patch(facecolor='white',edgecolor=O,label='Run 3 Oct. card: (σ−σ_frozen)/σ')],
 loc='lower right',fontsize=11,frameon=False)
fig.tight_layout(); fig.savefig(sys.argv[1]); print('ok')
