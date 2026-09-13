"""Figure 6: the tier-evidence association is a between-design artefact.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; FIG = ROOT/"figures"
plt.rcParams.update({
 "pdf.fonttype":42,"ps.fonttype":42,
 "font.family":"serif","font.serif":["DejaVu Serif"],
 "font.size":9,"axes.titlesize":9.5,"axes.titleweight":"bold","axes.labelsize":9,
 "legend.fontsize":7.5,"legend.frameon":False,"figure.dpi":300,"savefig.dpi":300,
 "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False,
 "axes.grid":True,"grid.alpha":0.15,"lines.linewidth":1.7,"xtick.labelsize":8,"ytick.labelsize":8})
C=["#264653","#2A9D8F","#E9C46A","#F4A261","#E76F51"]; ACC="#E76F51"; GREY="#B0BEC5"
T=["low","moderate","high","very_high"]; TLAB=["Low","Moderate","High","Very high"]
R=json.loads((ROOT/"results/11_completeness.json").read_text())
df=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)
df["ti"]=df.tier.map({t:i for i,t in enumerate(T)}); IV=df.study_type.eq("INTERVENTIONAL")

fig,axes=plt.subplots(1,3,figsize=(7.0,2.75))

# (a) adjustment ladder
ax=axes[0]
lad=R["F_adjustment_ladder"]
order=[("raw","unadjusted"),("given_length_only","+ record length"),
       ("given_completeness","+ completeness"),("given_study_type","+ study design"),
       ("given_all_three","+ all three")]
y=np.arange(len(order))[::-1]
vals=[lad[k]["rho"] if "rho" in lad[k] else lad[k]["partial_rho"] for k,_ in order]
los=[v-lad[k]["ci95"][0] for v,(k,_) in zip(vals,order)]
his=[lad[k]["ci95"][1]-v for v,(k,_) in zip(vals,order)]
cols=[C[0]]+[GREY]*2+[ACC,ACC]
ax.errorbar(vals,y,xerr=[los,his],fmt="none",ecolor="#666",elinewidth=1,capsize=2,zorder=1)
ax.scatter(vals,y,c=cols,s=34,zorder=3)
ax.axvline(0,color="#999",lw=0.8)
ax.set_yticks(y); ax.set_yticklabels([l for _,l in order],fontsize=7.5)
ax.set_xlabel(r"$\rho$(risk tier, evidence)"); ax.set_xlim(-0.02,0.28)
ax.set_title("(a) What explains the association",fontsize=9)
ax.annotate("84% removed",xy=(vals[1],y[3]),xytext=(0.10,y[3]-0.42),fontsize=7,color=ACC)

# (b) Simpson's paradox
ax=axes[1]
x=np.arange(4)
for lab,mask,col,mk in [("Pooled",slice(None),C[0],"o"),
                        ("Interventional",IV,C[1],"s"),
                        ("Observational",~IV,C[3],"^")]:
    s=df if isinstance(mask,slice) else df[mask]
    m=[s.E_norm[s.ti==i].mean() if (s.ti==i).any() else np.nan for i in range(4)]
    ax.plot(x,m,marker=mk,color=col,label=lab,markersize=4.5)
# mark the thin cells so the observational "high" point is not over-read
n_obs_high=int(((~IV)&(df.ti==2)).sum())
ax.annotate(f"n={n_obs_high}",xy=(2,df.E_norm[(~IV)&(df.ti==2)].mean()),
            textcoords="offset points",xytext=(4,-11),fontsize=6.8,color=C[3])
ax.annotate("no very-high\nobservational cases",xy=(3,0.113),fontsize=6.5,color=C[3],ha="center")
ax.set_xticks(x); ax.set_xticklabels(TLAB,fontsize=7.5)
ax.set_ylabel(r"Mean evidence $\bar{E}$"); ax.set_ylim(0.10,0.24)
ax.legend(loc="upper left",fontsize=7)
ax.set_title("(b) Pooled slope, flat strata",fontsize=9)

# (c) pre-specified contrast vs threshold
ax=axes[2]
items=[("Pooled\n(n=9,484)",R["C_estimator"]["PRE_SPECIFIED_low_to_very_high"],C[0]),
       ("Interventional\nonly (n=4,214)",R["E_within_study_type"]["interventional"]["delta_prespec"],ACC)]
xs=np.arange(len(items))
v=[i[1]["delta_low_to_very_high"] for i in items]
lo=[a-i[1]["ci95"][0] for a,i in zip(v,items)]; hi=[i[1]["ci95"][1]-a for a,i in zip(v,items)]
ax.bar(xs,v,0.45,color=[i[2] for i in items],edgecolor="white")
ax.errorbar(xs,v,yerr=[lo,hi],fmt="none",ecolor="#333",capsize=4,lw=1.2)
ax.axhline(0.20,color=ACC,ls="--",lw=1.4)
ax.text(1.42,0.205,"pre-specified\nthreshold 0.20",fontsize=7,color=ACC,ha="right",va="bottom")
ax.axhline(0,color="#999",lw=0.8)
for xi,vi in zip(xs,v): ax.annotate(f"{vi:+.4f}",(xi,vi),textcoords="offset points",
                                    xytext=(0,7 if vi>0 else -12),ha="center",fontsize=7.5)
ax.set_xticks(xs); ax.set_xticklabels([i[0] for i in items],fontsize=7.5)
ax.set_ylabel(r"$\Delta\bar{E}$ low $\rightarrow$ very high"); ax.set_ylim(-0.02,0.235)
ax.set_title("(c) Pre-specified contrast",fontsize=9)

fig.tight_layout()
fig.savefig(FIG/"fig6_design_confound.pdf"); fig.savefig(FIG/"fig6_design_confound.png")
print("figures/fig6_design_confound.pdf written")
