"""P1 v2: SR/CR vjets template before vs after negrw, with the 0-over-0 pathology annotated."""
import numpy as np, uproot, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="/eos/user/c/cgupta/HToWW/plots/negrw"
CUR="/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root"
BAK="/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root.bak_pre_negrw"
def get(fn,key):
    with uproot.open(fn) as f:
        h=f[key]; return h.values(), np.sqrt(h.variances())

for CH,tag,ttl in (("SR_hplusc","SR","Signal region  (SR_hplusc)"),
                   ("CR_vjets","CRvjets","V+jets control region  (CR_vjets)")):
    vb,eb=get(BAK,f"{CH}_vjets"); vn,en=get(CUR,f"{CH}_vjets")
    live=(vb!=0)|(vn!=0)|(eb!=0)|(en!=0)
    x=np.arange(len(vb))
    fig,(ax,axr)=plt.subplots(2,1,figsize=(8.6,6.4),sharex=True,
                              gridspec_kw={"height_ratios":[2.3,1]})
    ax.errorbar(x[live],vb[live],yerr=eb[live],fmt="o",ms=7,color="#b2182b",capsize=4,
                lw=1.8,label=r"baseline  $\sum_i w_i$   (signed amc@NLO)")
    ax.errorbar(x[live],vn[live],yerr=en[live],fmt="s",ms=7,color="#2166ac",capsize=4,
                lw=1.8,label=r"negrw  $\sum_i |w_i|\,g(\vec{x}_i)$  (renorm.)")
    ax.axhline(0,color="k",lw=.8,ls=":")
    ax.set_ylabel("V+jets yield / bin"); ax.set_title(ttl)
    ax.legend(fontsize=10.5,loc="upper left"); ax.grid(alpha=.3)

    with np.errstate(divide="ignore",invalid="ignore"):
        rb=np.where(vb>0,100*eb/vb,np.nan); rn=np.where(vn>0,100*en/vn,np.nan)
    # bins where baseline yield collapsed to 0 but error is finite -> undefined rel err
    bad=(vb<=0)&(eb>0)
    rbp=np.where(bad,3e3,rb)                     # park at top of axis
    axr.plot(x[live],rbp[live],"o-",color="#b2182b",lw=1.8,ms=7,label="baseline")
    axr.plot(x[live],rn[live],"s-",color="#2166ac",lw=1.8,ms=7,label="negrw")
    for i in np.flatnonzero(bad):
        axr.annotate(r"$0\pm\infty$",(i,3e3),textcoords="offset points",xytext=(0,-26),
                     ha="center",color="#b2182b",fontsize=12,fontweight="bold")
        ax.annotate("total\ncancellation",(i,0),textcoords="offset points",xytext=(0,26),
                    ha="center",color="#b2182b",fontsize=9.5)
    axr.set_yscale("log"); axr.set_ylim(5,6e3)
    axr.set_ylabel("rel. MC-stat err [%]"); axr.set_xlabel("discriminant bin")
    axr.set_xticks(x[live]); axr.grid(alpha=.3); axr.legend(fontsize=9.5,loc="upper left")
    fig.tight_layout(); fig.savefig(f"{OUT}/P1_{tag}_vjets_template.png",dpi=150); plt.close(fig)
    ok=np.isfinite(rb)&np.isfinite(rn)&live
    print(f"{tag}: mean rel err (finite bins) {np.nanmean(rb[ok]):.1f}% -> {np.nanmean(rn[ok]):.1f}%"
          f"   | pathological bins: {list(np.flatnonzero(bad))}")
