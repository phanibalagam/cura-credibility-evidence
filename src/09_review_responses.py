"""Analyses required by the adversarial review.
F02: do Channel A's influence items carry signal for adjudicated influence, or is
     Channel A measuring salience rather than FDA's influence construct?
F05: bootstrap CIs for the subset gradients in the scope analysis.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
import statsmodels.api as sm

rng=np.random.default_rng(20260907)
ROOT=Path(__file__).resolve().parents[1]
TIERS=["low","moderate","high","very_high"]; T2I={t:i for i,t in enumerate(TIERS)}
sc=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)
sc["tier_i"]=sc.tier.map(T2I)
lab=pd.read_csv(ROOT/"data/processed/adjudication_labels.csv")
d=lab.merge(sc,on="nct_id",validate="1:1")
tb=lambda s: s.astype(str).str.lower().eq("true")
R={}

# ---------- F02 ----------
d["i1_intervention"]=tb(d.match_in_intervention).astype(int)
d["i2_title"]=tb(d.match_in_title).astype(int)
d["i3_interventional"]=d.study_type.eq("INTERVENTIONAL").astype(int)
items=["i1_intervention","i2_title","i3_interventional"]
f02={"n":int(len(d)),
 "adjudicated_influence_dist":d.adj_influence.value_counts().sort_index().to_dict(),
 "per_item":{}}
for it in items:
    a=d.adj_influence[d[it]==1]; b=d.adj_influence[d[it]==0]
    u=stats.mannwhitneyu(a,b,alternative="two-sided")
    # rank-biserial effect size
    rb=1-2*u.statistic/(len(a)*len(b)) if len(a) and len(b) else np.nan
    f02["per_item"][it]={"n_present":int(d[it].sum()),
      "mean_adj_influence_present":round(float(a.mean()),4) if len(a) else None,
      "mean_adj_influence_absent":round(float(b.mean()),4) if len(b) else None,
      "spearman_rho":round(float(stats.spearmanr(d[it],d.adj_influence).statistic),4),
      "p":float(stats.spearmanr(d[it],d.adj_influence).pvalue),
      "rank_biserial":round(float(-rb),4)}
X=sm.add_constant(d[items].astype(float))
m=sm.OLS(d.adj_influence.astype(float),X).fit()
f02["ols_adjudicated_influence_on_items"]={
  "r2":round(float(m.rsquared),4),"adj_r2":round(float(m.rsquared_adj),4),
  "f_pvalue":float(m.f_pvalue),
  "coefficients":{k:{"coef":round(float(m.params[k]),4),"se":round(float(m.bse[k]),4),
                     "p":float(m.pvalues[k]),
                     "ci95":[round(float(x),4) for x in m.conf_int().loc[k]]} for k in m.params.index}}
# the competing hypothesis: are the items better explained as salience?
# proxy for salience: number of AI lexicon terms matched, and AI term in title
d["n_terms"]=d.matched_terms.fillna("").apply(lambda s: len([x for x in s.split("|") if x]))
f02["salience_check"]={
  "spearman_i2title_vs_n_ai_terms":round(float(stats.spearmanr(d.i2_title,d.n_terms).statistic),4),
  "spearman_i2title_vs_adj_influence":round(float(stats.spearmanr(d.i2_title,d.adj_influence).statistic),4),
  "reading":("if a Channel A item tracks how prominently the record is about AI more strongly "
             "than it tracks adjudicated influence, it is a salience proxy, not an influence measure")}
f02["verdict"]=None
R["F02_channel_A_influence_items"]=f02

# ---------- F05 bootstrap subset gradients ----------
def boot_delta(s,n=5000):
    if s.tier_i.nunique()<2 or len(s)<30: return None
    obs=s.groupby("tier_i").E_norm.mean()
    base=obs.loc[obs.index.min()]
    d0=float(obs.max()-base)
    bs=[]
    idx=np.arange(len(s))
    for _ in range(n):
        q=s.iloc[rng.choice(idx,len(idx),replace=True)]
        g=q.groupby("tier_i").E_norm.mean()
        if len(g)<2: continue
        bs.append(float(g.max()-g.loc[g.index.min()]))
    return {"n":int(len(s)),"delta":round(d0,4),
            "ci95":[round(float(np.percentile(bs,2.5)),4),round(float(np.percentile(bs,97.5)),4)],
            "pct_boot_above_0.20":round(float(np.mean(np.array(bs)>0.20)*100),2)}
subs={
 "full_corpus": sc,
 "fda_regulated_drug": sc[tb(sc.is_fda_regulated_drug)],
 "fda_regulated_device": sc[tb(sc.is_fda_regulated_device)],
 "fda_regulated_either": sc[tb(sc.is_fda_regulated_drug)|tb(sc.is_fda_regulated_device)],
 "interventional_with_phase": sc[sc.study_type.eq("INTERVENTIONAL")&sc.phases.notna()&~sc.phases.isin(["NA"])],
 "industry_sponsored": sc[sc.sponsor_class.eq("INDUSTRY")]}
R["F05_subset_gradient_CIs"]={k:boot_delta(v) for k,v in subs.items()}

(ROOT/"results"/"09_review_responses.json").write_text(json.dumps(R,indent=2,default=float))
print(json.dumps(R,indent=2,default=float))
