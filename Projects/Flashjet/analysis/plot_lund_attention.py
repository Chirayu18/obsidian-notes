"""Plot Lund attention share vs training iteration, per class.

Reads lund_attention.json from lund_attn.py. Two panels:
  left  -- CLS attention ratio (jet-level decision's reliance on lund tokens)
  right -- encoder self-attention ratio (how much particle reps are shaped by them)

Ratio = measured share / uniform share, so 1.0 means "attended exactly as much
as their token count warrants". The RATIO is the interpretable quantity; the raw
percentage is not, because the number of valid lund tokens varies per jet.

Sitian's hypothesis predicts a DECAYING curve. A flat curve falsifies it.
"""
import json, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv) > 1 else "lund_attention.json"
d = json.load(open(SRC))
iters = sorted(int(k) for k in d)
classes = list(d[str(iters[0])].keys())

INK="#1a1f27"; SUB="#4a5462"; GRID="#dfe3e8"
# the classes Sitian named as largest "lund attention loss"
NAMED = {"HToBB","TTBar","HToWW4Q","HToCC"}
cmap = plt.get_cmap("tab10")

fig,axes = plt.subplots(1,2,figsize=(13.2,5.0))
for ax,key,ttl in [(axes[0],"cls_ratio","CLS attention  (the jet-level decision)"),
                   (axes[1],"self_ratio","encoder self-attention  (particle reps)")]:
    for i,c in enumerate(classes):
        y=[d[str(it)][c][key] for it in iters]
        named = c in NAMED
        ax.plot(iters,y,"-o",ms=5.5,lw=2.2 if named else 1.2,
                color=cmap(i%10), alpha=1.0 if named else .45,
                label=c+("  *" if named else ""),zorder=3 if named else 2)
    ax.axhline(1.0,color=SUB,ls="--",lw=1.2,zorder=1)
    ax.annotate("uniform — attended exactly as often as their token count warrants",
                (iters[-1],1.0),textcoords="offset points",xytext=(-4,6),
                ha="right",fontsize=9,color=SUB)
    ax.set_xscale("log")
    ax.set_xlabel("training iteration",fontsize=11,color=SUB)
    ax.set_title(ttl,fontsize=12.5,color=INK,weight="bold",pad=14)
    ax.grid(True,color=GRID,lw=.8); ax.set_axisbelow(True)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)
for a in axes: a.set_ylim(0.15,1.05)
axes[0].set_ylabel("attention on Lund tokens / uniform",fontsize=11,color=SUB)
axes[1].legend(fontsize=8.6,ncol=2,frameon=False,loc="lower right")

fig.suptitle("ParT attends to Lund tokens far LESS than chance — and the jet-level decision walks away",
             fontsize=13.5,weight="bold",color=INK,y=.985)
fig.text(.5,.925,"every curve is BELOW 1 at every stage: 48 Lund tokens are ~46 % of the sequence "
                 "but never get their share of attention   ·   * = classes named as largest “Lund attention loss”",
         ha="center",fontsize=10.2,color=SUB)
fig.tight_layout(rect=(0,0,1,.905))
fig.savefig("lund_attention.png",dpi=200,facecolor="white")
print("wrote lund_attention.png")

# the numbers the caption will quote
print("\nCLS ratio (measured / uniform):")
hdr="  %-12s"%"class" + "".join("%10s"%f"{it//1000}k" for it in iters)
print(hdr)
for c in classes:
    r=[d[str(it)][c]["cls_ratio"] for it in iters]
    print("  %-12s"%c + "".join("%10.3f"%v for v in r) + ("   *" if c in NAMED else ""))
print("\nraw CLS share %% (uniform in parens):")
for c in classes:
    r=[d[str(it)][c] for it in iters]
    print("  %-12s"%c + "".join("%8.2f(%4.1f)"%(x["cls_share"]*100,x["cls_unif"]*100) for x in r))
allc=np.array([[d[str(it)][c]["cls_ratio"] for it in iters] for c in classes])
print("\nmean over classes:", "  ".join("%.3f"%v for v in allc.mean(0)))
print("decay 1st->last: %.1f%%"%(100*(allc.mean(0)[-1]/allc.mean(0)[0]-1)))
