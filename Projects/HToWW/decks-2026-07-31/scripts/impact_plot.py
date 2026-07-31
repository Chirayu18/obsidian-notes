"""D1: our uncertainty breakdown vs AN-23-102 Table 17, on the AN's OWN metric."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="/eos/user/c/cgupta/HToWW/plots/negrw"

# linear drop in the 1-sigma width, (sig_full - sig_frozen)/sig_full  -- the AN's definition
labels = ["MC\nstatistical","Signal theory\n(cH/bH)","tt norm.","Charm\ntagging",
          "Bkg-Higgs","JES/JER","Lepton","Pileup"]
ours   = [24.5, 29.7, 3.5, 2.7, 1.8, 1.4, 0.1, 0.0]
an     = [ 5.4,  8.5, 0.7, 1.1, 7.6, 1.1, 0.4, 0.4]

x=np.arange(len(labels)); w=0.38
fig,ax=plt.subplots(figsize=(10.5,4.4))
b1=ax.bar(x-w/2, ours, w, label="this analysis (26.7 fb$^{-1}$)",
          color="#2166ac", edgecolor="k", lw=.5)
b2=ax.bar(x+w/2, an,  w, label="AN-23-102 Table 17 (1POI, 138 fb$^{-1}$)",
          color="#999999", edgecolor="k", lw=.5)
for b in list(b1)+list(b2):
    h=b.get_height()
    ax.annotate(f"{h:.1f}", (b.get_x()+b.get_width()/2, h), textcoords="offset points",
                xytext=(0,2), ha="center", fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel(r"$(\sigma_{\rm full}-\sigma_{\rm frozen})/\sigma_{\rm full}$  [%]")
ax.set_title("Uncertainty breakdown vs the published analysis\n"
             "(both on the AN's metric: linear drop in the 1$\\sigma$ width when frozen)",
             fontsize=11)
ax.legend(fontsize=9.5); ax.grid(alpha=.3, axis="y"); ax.set_ylim(0,33)
# shade the two genuinely-different groups
for i in (0,1):
    ax.axvspan(i-0.5, i+0.5, color="#b2182b", alpha=.07)
ax.text(0.5, 31, "the two real gaps", ha="center", fontsize=9.5,
        color="#b2182b", fontweight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/D1_breakdown_vs_AN.png", dpi=150); plt.close(fig)
print("wrote D1_breakdown_vs_AN.png")
for l,o,a in zip(labels,ours,an):
    print(f"  {l.replace(chr(10),' '):24s} ours {o:5.1f}%   AN {a:4.1f}%")
