# Keeper 2026-11-13: blind Asimov (r=1) likelihood scan of r on the October four-era card full_run3.ws.root.
# Points from lxplus:~/htoww_submit_logs/scan_oct691_20261113/scan_points.json (MultiDimFit --algo grid, 41 points, r in [-1000,1000]).
import sys, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open(sys.argv[1]))
T,O,INK,MUT,GRID='#0a85b0','#d9701a','#1f2a30','#6b7780','#e3e8eb'
def curve(k):
    a=np.array(sorted((r,q) for r,q,_ in d[k])); return a[:,0],a[:,1]
def cross(r,q,level):
    out=[]
    for i in range(len(r)-1):
        if (q[i]-level)*(q[i+1]-level)<0: out.append(r[i]+(level-q[i])*(r[i+1]-r[i])/(q[i+1]-q[i]))
    return out
res={}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,ax=plt.subplots(figsize=(7.4,5.0),dpi=160)
for k,c,lab in (('total',T,'All uncertainties'),('stat','#d9701a','Statistical only')):
    r,q=curve(k); ax.plot(r,q,color=c,lw=2,label=lab)
    res[k]={'1sigma':cross(r,q,1.0),'2sigma':cross(r,q,3.84)}
for lv,txt in ((1,'68% CL'),(3.84,'95% CL')):
    ax.axhline(lv,color=MUT,lw=0.9,ls='--'); ax.text(-990,lv+0.12,txt,color=MUT,fontsize=9)
ax.set_xlim(-1000,1000); ax.set_ylim(0,8)
ax.set_xlabel('Signal strength μ = r',color=INK); ax.set_ylabel('−2 Δ ln L',color=INK)
ax.grid(True,color=GRID,lw=0.8); ax.set_axisbelow(True)
for s in ('top','right'): ax.spines[s].set_visible(False)
ax.tick_params(colors=MUT,length=0); ax.legend(frameon=False,loc='upper right',fontsize=10)
ax.text(0.01,0.97,'CMS Internal · expected (Asimov, μ = 1) · 61.9 fb⁻¹ (13.6 TeV)',transform=ax.transAxes,ha='left',va='top',fontsize=8.5,color=MUT)
fig.tight_layout(); fig.savefig(sys.argv[2])
print(json.dumps(res))
