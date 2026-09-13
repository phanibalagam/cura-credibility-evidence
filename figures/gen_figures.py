"""All paper figures. Every value is read from results/*.json or the scored corpus.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/"figures"
plt.rcParams.update({
 "pdf.fonttype":42,"ps.fonttype":42,   # embed TrueType, never Type 3 (arXiv)
 "font.family":"serif","font.serif":["DejaVu Serif"],
 "font.size":9,"axes.titlesize":9.5,"axes.titleweight":"bold","axes.labelsize":9,
 "legend.fontsize":7.5,"legend.frameon":False,"figure.dpi":300,"savefig.dpi":300,
 "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False,
 "axes.grid":True,"grid.alpha":0.15,"lines.linewidth":1.6,"xtick.labelsize":8,"ytick.labelsize":8})
C=["#264653","#2A9D8F","#E9C46A","#F4A261","#E76F51"]; ACC="#E76F51"; GREY="#B0BEC5"
TIERS=["low","moderate","high","very_high"]; TLAB=["Low","Moderate","High","Very high"]
df=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)
S=json.loads((ROOT/"results/03_scoring_summary.json").read_text())
V=json.loads((ROOT/"results/05_validity_baselines.json").read_text())
Rl=json.loads((ROOT/"results/04_reliability.json").read_text())
A=json.loads((ROOT/"results/07_adjudication.json").read_text())
DIMS=["D1_data_quality_provenance","D2_representativeness_bias","D3_uncertainty_performance",
      "D4_independent_validation","D5_lifecycle_monitoring"]
DLAB=["D1 Data quality\n& provenance","D2 Representativeness\n& bias","D3 Uncertainty\n& performance",
      "D4 Independent\nvalidation","D5 Lifecycle\nmonitoring"]

# ---- Fig 1: the framework, drawn as the risk grid + evidence requirement ----
fig,axes=plt.subplots(1,2,figsize=(6.9,2.9),gridspec_kw={"width_ratios":[1,1.15]})
ax=axes[0]
grid=json.loads((ROOT/"src/cura_rubric.json").read_text())["risk_matrix"]["grid"]
cmap={"low":"#EAF2F0","moderate":"#BFE0D8","high":"#F1C08A","very_high":"#E0765A"}
for i in range(4):
    for j in range(4):
        ax.add_patch(Rectangle((j,i),1,1,facecolor=cmap[grid[i][j]],edgecolor="white",lw=1.6))
        n=int(((df.influence==i)&(df.consequence==j)).sum())
        ax.text(j+.5,i+.5,f"{n:,}",ha="center",va="center",fontsize=7.5,
                color="white" if grid[i][j]=="very_high" else "#264653")
ax.set_xlim(0,4); ax.set_ylim(0,4); ax.set_xticks(np.arange(4)+.5); ax.set_yticks(np.arange(4)+.5)
ax.set_xticklabels(range(4)); ax.set_yticklabels(range(4))
ax.set_xlabel("Decision consequence"); ax.set_ylabel("Model influence")
ax.set_title("(a) Risk grid, cases per cell"); ax.grid(False)
ax=axes[1]
x=np.arange(4)
mE=[V["H1_risk_proportionality"]["mean_E_norm_by_tier"][t] for t in TIERS]
sd=[V["H1_risk_proportionality"]["sd_E_norm_by_tier"][t] for t in TIERS]
n=[V["H1_risk_proportionality"]["n_by_tier"][t] for t in TIERS]
se=[s/np.sqrt(k) for s,k in zip(sd,n)]
thr=[json.loads((ROOT/"src/cura_rubric.json").read_text())["sufficiency_thresholds"][t] for t in TIERS]
ax.plot(x,thr,color=GREY,ls="--",marker="s",label="Evidence required by tier ($\\theta$)")
ax.errorbar(x,mE,yerr=[1.96*s for s in se],color=ACC,marker="o",capsize=3,
            label="Evidence observed ($\\bar{E}$, 95% CI)")
for xi,m,k in zip(x,mE,n): ax.annotate(f"{m:.3f}",(xi,m),textcoords="offset points",
                                       xytext=(0,-13),ha="center",fontsize=7,color="#8A3E2A")
ax.fill_between(x,mE,thr,color=ACC,alpha=0.07)
ax.axhline(0.30,color=C[1],ls=":",lw=1.4)
ax.text(3.05,0.315,"flat 0.30 reference",color=C[1],fontsize=6.8,ha="right")
ax.set_xticks(x); ax.set_xticklabels(TLAB); ax.set_ylim(0,1.0)
ax.set_ylabel("Normalised credibility evidence $E$")
ax.set_title("(b) Evidence observed vs. required"); ax.legend(loc="upper left")
fig.savefig(FIG/"fig1_framework.pdf"); fig.savefig(FIG/"fig1_framework.png"); plt.close(fig)

# ---- Fig 2: item-level prevalence of auditable evidence ----
ev=pd.read_csv(ROOT/"data/processed/aiml_evidence_text.csv")
items=[c for c in ev.columns if c.split("_")[0] in ("d1","d2","d3","d4","d5")]
pv=(100*ev[items].mean()).sort_values()
fig,ax=plt.subplots(figsize=(6.9,3.4))
cols=[C[int(i.split("_")[0][1])-1] for i in pv.index]
b=ax.barh(range(len(pv)),pv.values,color=cols,edgecolor="white",lw=.5)
ax.set_yticks(range(len(pv)))
ax.set_yticklabels([i.replace("_"," ").replace("d1 ","D1: ").replace("d2 ","D2: ")
    .replace("d3 ","D3: ").replace("d4 ","D4: ").replace("d5 ","D5: ") for i in pv.index],fontsize=7.5)
for r,v in zip(b,pv.values): ax.text(v+.3,r.get_y()+r.get_height()/2,f"{v:.2f}%",va="center",fontsize=7)
ax.set_xlabel("Percentage of 9,484 registered AI studies whose public record mentions the item")
ax.set_xlim(0,20); ax.set_title("Prevalence of auditable credibility-evidence items")
ax.grid(axis="y",alpha=0)
fig.savefig(FIG/"fig2_evidence_prevalence.pdf"); fig.savefig(FIG/"fig2_evidence_prevalence.png"); plt.close(fig)

# ---- Fig 3: robustness of the flat-evidence finding ----
rob=Rl["H6_robustness"]
labels,vals=[],[]
for k,v in rob["risk_matrix_form"].items(): labels.append(f"matrix: {k}"); vals.append(v["delta_low_to_top"])
for k,v in rob["consensus_rule"].items(): labels.append(f"channels: {k}"); vals.append(v["delta_low_to_top"])
for k,v in rob["corpus_strictness"].items(): labels.append(f"corpus: {k.replace('_',' ')}"); vals.append(v["delta_low_to_top"])
for k,v in rob["temporal_split"].items(): labels.append(f"period: {k.replace('_',' ')}"); vals.append(v["delta_low_to_top"])
labels.append("adjudicated tiers")
ar=A["H1_replication_on_adjudicated_tiers"]["mean_E_norm_by_adjudicated_tier"]
vals.append(round(max(v for v in ar.values() if v is not None)-ar["low"],4))
wp=rob["weight_perturbation"]
fig,ax=plt.subplots(figsize=(6.9,3.6))
y=np.arange(len(labels))
ax.barh(y,vals,color=C[0],edgecolor="white",lw=.5)
ax.axvline(0.20,color=ACC,ls="--",lw=1.6)
ax.text(0.205,len(labels)-0.6,"pre-specified threshold\nfor a substantive effect (0.20)",
        color=ACC,fontsize=7.5,va="top")
ax.errorbar([wp["delta_low_to_top_mean"]],[len(labels)+0.6],
            xerr=[[wp["delta_low_to_top_mean"]-wp["delta_low_to_top_ci95"][0]],
                  [wp["delta_low_to_top_ci95"][1]-wp["delta_low_to_top_mean"]]],
            fmt="o",color=C[1],capsize=3)
ax.text(wp["delta_low_to_top_ci95"][1]+0.005,len(labels)+0.6,"1,000 Dirichlet weight draws",
        fontsize=7.5,va="center",color=C[1])
ax.set_yticks(list(y)+[len(labels)+0.6]); ax.set_yticklabels(labels+["weights (mean, 95% CI)"],fontsize=7.5)
ax.set_xlim(0,0.30); ax.set_xlabel("$\\Delta \\bar{E}$ from lowest to highest risk tier")
ax.set_title("The evidence gradient is small under every analytic choice"); ax.grid(axis="y",alpha=0)
fig.savefig(FIG/"fig3_robustness.pdf"); fig.savefig(FIG/"fig3_robustness.png"); plt.close(fig)

# ---- Fig 4: measurement failure - channels and adjudication ----
fig,axes=plt.subplots(1,3,figsize=(6.9,2.6))
ax=axes[0]
ks=[Rl["H3_channel_agreement"]["influence"],Rl["H3_channel_agreement"]["consequence"],
    Rl["H3_channel_agreement"]["tier"]]
kn=["Influence","Consequence","Tier"]
ax.bar(range(3),[k["weighted_kappa"] for k in ks],color=GREY,edgecolor="white",
       yerr=[[k["weighted_kappa"]-k["ci95"][0] for k in ks],[k["ci95"][1]-k["weighted_kappa"] for k in ks]],
       capsize=3)
ax.axhline(0.40,color=ACC,ls="--",lw=1.4); ax.text(2.45,0.42,"0.40",color=ACC,fontsize=7,ha="right")
ax.set_xticks(range(3)); ax.set_xticklabels(kn,fontsize=7.5,rotation=15)
ax.set_ylim(0,1); ax.set_ylabel("Quadratic weighted $\\kappa$")
ax.set_title("(a) Channel A vs B",fontsize=9)
ax=axes[1]
ka=[A["influence"],A["consequence"],A["tier"]]
ax.bar(range(3),[k["quadratic_weighted_kappa"] for k in ka],color=C[1],edgecolor="white",
       yerr=[[k["quadratic_weighted_kappa"]-k["kappa_ci95"][0] for k in ka],
             [k["kappa_ci95"][1]-k["quadratic_weighted_kappa"] for k in ka]],capsize=3)
ax.axhline(0.60,color=ACC,ls="--",lw=1.4); ax.text(2.45,0.62,"0.60",color=ACC,fontsize=7,ha="right")
ax.set_xticks(range(3)); ax.set_xticklabels(kn,fontsize=7.5,rotation=15); ax.set_ylim(0,1)
ax.set_title("(b) Automated vs adjudicated\n(n=200)",fontsize=9)
ax=axes[2]
cm=np.array(A["tier"]["confusion"])
im=ax.imshow(cm,cmap="YlOrRd")
for i in range(4):
    for j in range(4):
        ax.text(j,i,cm[i,j],ha="center",va="center",fontsize=7,
                color="white" if cm[i,j]>cm.max()*0.6 else "#333")
ax.set_xticks(range(4)); ax.set_yticks(range(4))
ax.set_xticklabels(["L","M","H","VH"],fontsize=7.5); ax.set_yticklabels(["L","M","H","VH"],fontsize=7.5)
ax.set_xlabel("Automated",fontsize=8); ax.set_ylabel("Adjudicated",fontsize=8)
ax.set_title("(c) Tier confusion",fontsize=9); ax.grid(False)
fig.tight_layout()
fig.savefig(FIG/"fig4_measurement.pdf"); fig.savefig(FIG/"fig4_measurement.png"); plt.close(fig)

# ---- Fig 5: dimension means by tier + growth of the corpus ----
fig,axes=plt.subplots(1,2,figsize=(6.9,2.7))
ax=axes[0]
w=0.18
for i,(d,l) in enumerate(zip(DIMS,DLAB)):
    m=[df.loc[df.tier==t,d].mean() for t in TIERS]
    ax.bar(np.arange(4)+(i-2)*w,m,w*0.92,label=l.replace("\n"," "),color=C[i],edgecolor="white",lw=.4)
ax.set_xticks(range(4)); ax.set_xticklabels(TLAB,fontsize=8)
ax.set_ylabel("Mean dimension score (0-3)"); ax.set_ylim(0,3)
ax.legend(fontsize=6.2,ncol=2,loc="upper left"); ax.set_title("(a) Evidence by dimension and risk tier",fontsize=9)
ax=axes[1]
df["_yr"]=pd.to_datetime(df.first_post_date,errors="coerce",format="mixed").dt.year
g=df[(df._yr>=2010)&(df._yr<=2025)].groupby(["_yr","tier"]).size().unstack().reindex(columns=TIERS).fillna(0)
ax.stackplot(g.index,[g[t] for t in TIERS],labels=TLAB,colors=[cmap[t] for t in TIERS],edgecolor="white",lw=.4)
ax.set_xlabel("Year first posted"); ax.set_ylabel("Registered AI studies")
ax.legend(fontsize=6.5,loc="upper left"); ax.set_title("(b) Corpus growth by risk tier",fontsize=9)
fig.tight_layout()
fig.savefig(FIG/"fig5_dimensions_growth.pdf"); fig.savefig(FIG/"fig5_dimensions_growth.png"); plt.close(fig)
print("figures written:", sorted(p.name for p in FIG.glob("*.pdf")))
