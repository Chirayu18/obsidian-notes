"""Deck-2 plots: the official 2D c-tag SF values and their uncertainty band."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import correctionlib

OUT="/eos/user/c/cgupta/HToWW/plots/ctag"
import os; os.makedirs(OUT,exist_ok=True)
SF="/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022postEE.json.gz"
cs=correctionlib.CorrectionSet.from_file(SF)
c=cs["ParticleNetAK4_pseudocontinuous"]

CATS=["L0","C0","C1","C2","C3","C4","B0","B1","B2","B3","B4"]
WP  =[0,40,41,42,43,44,50,51,52,53,54]
FLAV=[(0,"udsg"),(4,"c"),(5,"b")]
PT=60.0; ETA=1.0

cen=np.zeros((3,11)); up=np.zeros((3,11)); dn=np.zeros((3,11))
for i,(fl,_) in enumerate(FLAV):
    for j,wp in enumerate(WP):
        cen[i,j]=c.evaluate("central",fl,wp,ETA,PT)
        up[i,j] =c.evaluate("up_Total",fl,wp,ETA,PT)
        dn[i,j] =c.evaluate("down_Total",fl,wp,ETA,PT)

# ---- C1: SF heatmap ----
fig,ax=plt.subplots(figsize=(9,3.1))
im=ax.imshow(cen,cmap="RdBu_r",vmin=0.3,vmax=1.7,aspect="auto")
ax.set_xticks(range(11)); ax.set_xticklabels(CATS)
ax.set_yticks(range(3)); ax.set_yticklabels([f[1] for f in FLAV])
for i in range(3):
    for j in range(11):
        empty = abs(cen[i,j]-1.0)<1e-9 and abs(up[i,j]-1.0)<1e-9
        ax.text(j,i,f"{cen[i,j]:.2f}",ha="center",va="center",fontsize=9.5,
                color="grey" if empty else "black",
                fontweight="normal" if empty else "bold")
ax.set_title(f"Official PNet 2D c-tag SF — 2022postEE, $p_T$ = {PT:.0f} GeV (central)",pad=14)
fig.colorbar(im,ax=ax,label="SF")
# mark the uncalibrated band
ax.add_patch(plt.Rectangle((6.5,-0.5),4,3,fill=False,ec="k",lw=2.2,ls="--"))
ax.text(8.5,2.95,"B1-B4: receive ZERO candidate c-jets",ha="center",fontsize=9.5,va="top")
fig.tight_layout(); fig.savefig(f"{OUT}/C1_sf_matrix.png",dpi=150); plt.close(fig)

# ---- C2: uncertainty band, POPULATED categories only ----
# B1-B4 receive zero candidate c-jets and carry placeholder +-[0.3,3.0] bands;
# plotting them compresses everything real, so restrict to the 7 live categories.
LIVE = 7
fig,ax=plt.subplots(figsize=(9,3.6))
x=np.arange(LIVE); w=0.26
cols=["#7fbf7b","#af8dc3","#2166ac"]
for i,(fl,nm) in enumerate(FLAV):
    lo=np.abs(cen[i]-np.minimum(dn[i],up[i]))[:LIVE]
    hi=np.abs(np.maximum(dn[i],up[i])-cen[i])[:LIVE]
    ax.bar(x+(i-1)*w,cen[i][:LIVE],w,yerr=[lo,hi],capsize=3,color=cols[i],
           label=nm,edgecolor="k",lw=.5)
ax.axhline(1,color="k",lw=1,ls=":")
ax.set_xticks(x); ax.set_xticklabels(CATS[:LIVE])
ax.set_ylabel("SF"); ax.set_ylim(0,3.2)
ax.set_title("Central SF with the combined up/down_Total band\n"
             "(this band IS the $CMS\\_ctag2d\\_2022$ nuisance) - populated categories only",
             fontsize=11)
ax.legend(title="jet flavour",fontsize=9.5,ncol=3); ax.grid(alpha=.3,axis="y")
fig.tight_layout(); fig.savefig(f"{OUT}/C2_sf_band.png",dpi=150); plt.close(fig)

print("central SF matrix (pt=60):")
for i,(fl,nm) in enumerate(FLAV):
    print(f"  {nm:5s} " + " ".join(f"{v:5.3f}" for v in cen[i]))
print("\nrelative band (up_Total-1, 1-down_Total):")
for i,(fl,nm) in enumerate(FLAV):
    print(f"  {nm:5s} " + " ".join(f"+{(up[i,j]/cen[i,j]-1)*100:4.0f}/-{(1-dn[i,j]/cen[i,j])*100:4.0f}%"
                                   for j in range(11)))
