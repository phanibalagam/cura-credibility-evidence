"""H4: agreement between automated CURA scoring and case-by-case adjudication.
The adjudicator is a single automated annotator working only from each study's
registered text and the rubric anchors, blind to the automated score. This is
NOT human expert review and NOT inter-rater reliability.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from statsmodels.stats.proportion import proportion_confint

ROOT=Path(__file__).resolve().parents[1]
RUB=json.loads((ROOT/"src"/"cura_rubric.json").read_text())
GRID=RUB["risk_matrix"]["grid"]; TIERS=["low","moderate","high","very_high"]
T2I={t:i for i,t in enumerate(TIERS)}
rng=np.random.default_rng(20260907)
lab=pd.read_csv(ROOT/"data/processed/adjudication_labels.csv")
key=pd.read_csv(ROOT/"data/processed/adjudication_key.csv")
d=lab.merge(key,on="nct_id",validate="1:1"); assert len(d)==200, len(d)
d["adj_tier"]=[GRID[i][c] for i,c in zip(d.adj_influence,d.adj_consequence)]

def block(a,b,name,n_boot=5000):
    a=np.asarray(a); b=np.asarray(b)
    k=cohen_kappa_score(a,b,weights="quadratic")
    acc=float((a==b).mean()); w1=float((np.abs(a-b)<=1).mean())
    lo_a,hi_a=proportion_confint(int((a==b).sum()),len(a),method="wilson")
    bs=[]
    for _ in range(n_boot):
        s=rng.choice(len(a),len(a),replace=True)
        if len(np.unique(a[s]))<2 or len(np.unique(b[s]))<2: continue
        bs.append(cohen_kappa_score(a[s],b[s],weights="quadratic"))
    return {"metric":name,"n":int(len(a)),
        "exact_agreement":round(acc,4),"exact_ci95":[round(lo_a,4),round(hi_a,4)],
        "within_one_level":round(w1,4),
        "quadratic_weighted_kappa":round(float(k),4),
        "kappa_ci95":[round(float(np.percentile(bs,2.5)),4),round(float(np.percentile(bs,97.5)),4)],
        "mean_signed_error_auto_minus_adj":round(float((b-a).mean()),4),
        "confusion":confusion_matrix(a,b).tolist()}

R={"design_note":("single automated annotator, blind to automated scores, working from each "
   "study's registered text and the rubric anchors; not human expert review, not inter-rater reliability"),
   "sample":"stratified by automated tier, 50 per tier, seed 20260907"}
R["influence"]=block(d.adj_influence, d.influence, "influence")
R["consequence"]=block(d.adj_consequence, d.consequence, "consequence")
R["tier"]=block(d.adj_tier.map(T2I), d.tier.map(T2I), "tier")
R["influence_channelA_only"]=block(d.adj_influence, d.A_influence, "influence vs channel A")
R["influence_channelB_only"]=block(d.adj_influence, d.B_influence, "influence vs channel B")
R["consequence_channelA_only"]=block(d.adj_consequence, d.A_consequence, "consequence vs channel A")
R["consequence_channelB_only"]=block(d.adj_consequence, d.B_consequence, "consequence vs channel B")
R["adjudicated_tier_distribution"]=d.adj_tier.value_counts().reindex(TIERS).fillna(0).astype(int).to_dict()
R["automated_tier_distribution_in_sample"]=d.tier.value_counts().reindex(TIERS).fillna(0).astype(int).to_dict()
R["prespecified_criterion"]="quadratic weighted kappa >= 0.60 on both axes"
R["SUPPORTED"]=bool(R["influence"]["quadratic_weighted_kappa"]>=0.60 and R["consequence"]["quadratic_weighted_kappa"]>=0.60)
# does the adjudicated label reproduce the flat-evidence finding?
sc=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)[["nct_id","E_norm"]]
dd=d.drop(columns=["E_norm"]).merge(sc,on="nct_id")
rho=stats.spearmanr(dd.adj_tier.map(T2I), dd.E_norm)
R["H1_replication_on_adjudicated_tiers"]={
  "spearman_rho":round(float(rho.statistic),4),"p":float(rho.pvalue),
  "mean_E_norm_by_adjudicated_tier":{t: (round(float(dd.E_norm[dd.adj_tier==t].mean()),4)
      if (dd.adj_tier==t).any() else None) for t in TIERS},
  "n_by_adjudicated_tier":{t:int((dd.adj_tier==t).sum()) for t in TIERS}}
(ROOT/"results"/"07_adjudication.json").write_text(json.dumps(R,indent=2,default=float))
print(json.dumps({k:v for k,v in R.items() if k not in ("design_note","sample")},indent=2,default=float))
