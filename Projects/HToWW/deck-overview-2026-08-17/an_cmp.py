import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
# 16/50/84 from the group scan (current 1034 card)
G = {
 "FULL":(706.8359,1034,1598.6549), "STAT":(460.9535,641,893.9503),
 "MCSTAT":(655.8788,956,1470.4387), "SIGTH":(662.3060,921,1306.4702),
 "BKGH":(705.4688,1032,1595.5626), "OTHBKG":(706.1523,1033,1597.1088),
 "TTNORM":(684.6804,1011,1575.1844), "CTAG":(651.8356,964,1505.7988),
 "JESJER":(699.3164,1023,1581.6479),
}
def sig(t): lo,med,hi=t; return (hi-lo)/2.0
sf, rf = sig(G["FULL"]), G["FULL"][1]
def pct(k):
    s=sig(G[k]); v=sf**2-s**2
    return 100*np.sqrt(max(v,0.0))/rf
ours={"Statistical":pct("STAT"),"MC statistical":pct("MCSTAT"),
      "Signal theory\n(cH/bH)":pct("SIGTH"),"Bkg-Higgs":pct("BKGH"),
      "Other background":pct("OTHBKG"),"tt norm.":pct("TTNORM"),
      "Charm tagging":pct("CTAG"),"JES/JER":pct("JESJER")}
an={"Statistical":73.8,"MC statistical":5.4,"Signal theory\n(cH/bH)":8.5,
    "Bkg-Higgs":7.6,"Other background":1.4,"tt norm.":0.7,
    "Charm tagging":1.1,"JES/JER":1.1}
ks=list(ours); x=np.arange(len(ks)); w=.38
fig,ax=plt.subplots(figsize=(11,4.9))
ax.bar(x-w/2,[ours[k] for k in ks],w,label="this analysis (26.7 fb$^{-1}$)",color="#1f4e79")
ax.bar(x+w/2,[an[k]   for k in ks],w,label="AN-23-102 Table 17 (1POI, 138 fb$^{-1}$)",color="#8c959d")
for i,k in enumerate(ks):
    ax.text(i-w/2,ours[k]+0.7,f"{ours[k]:.1f}",ha="center",fontsize=10,fontweight="bold",color="#1f4e79")
    ax.text(i+w/2,an[k]+0.7,f"{an[k]:.1f}",ha="center",fontsize=9,color="#5a6169")
ax.set_xticks(x); ax.set_xticklabels(ks,fontsize=10)
ax.set_ylabel(r"$|\Delta r|/r$  [%]",fontsize=12)
ax.legend(fontsize=10); ax.grid(alpha=.25,axis="y")
ax.set_title("Uncertainty breakdown vs the published analysis (AN metric)",fontsize=13,fontweight="bold")
fig.tight_layout(); fig.savefig("/home/cgupta/obsidian-notes/Projects/HToWW/deck-overview-2026-08-17/img/breakdown_vs_AN_new.png",dpi=160)
print(f"{'group':22s} {'ours':>7s} {'AN':>7s}")
for k in ks: print(f"{k.replace(chr(10),' '):22s} {ours[k]:7.1f} {an[k]:7.1f}")
