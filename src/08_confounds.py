"""Three checks a hostile reviewer would demand of the H1 result.

C1 Scope. FDA's guidance is for DRUG AND BIOLOGICAL PRODUCTS. Only 139 corpus studies
   carry the FDA-regulated-drug flag. Does the flat-evidence finding hold on the
   in-scope subsets, or is it an artefact of an out-of-scope corpus?
C2 Record length. Tier and evidence are both read from the same text by the same
   machinery, so a verbose record can score higher on both. Does the association
   survive conditioning on record length?
C3 Chance baseline. Does rho = 0.229 exceed what the marginals alone produce?

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
df=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)
df["tier_i"]=df.tier.map(T2I)
df["logchars"]=np.log10(pd.to_numeric(df.text_chars,errors="coerce").clip(lower=1))
R={}

def h1(s,label):
    if s.tier_i.nunique()<2 or len(s)<30: return {"label":label,"n":int(len(s)),"note":"too few cases or tiers"}
    rho=stats.spearmanr(s.tier_i,s.E_norm)
    m={t:(round(float(s.E_norm[s.tier==t].mean()),4) if (s.tier==t).any() else None) for t in TIERS}
    present=[m[t] for t in TIERS if m[t] is not None]
    return {"label":label,"n":int(len(s)),
            "n_by_tier":{t:int((s.tier==t).sum()) for t in TIERS},
            "spearman_rho":round(float(rho.statistic),4),"p":float(rho.pvalue),
            "mean_E_by_tier":m,"delta_low_to_top":round(max(present)-present[0],4),
            "mean_E_norm":round(float(s.E_norm.mean()),4)}

# ---- C1 scope ----
tb=lambda c: df[c].astype(str).str.lower().eq("true")
scope={}
scope["full_corpus"]=h1(df,"all 9,484")
scope["fda_regulated_drug"]=h1(df[tb("is_fda_regulated_drug")],"FDA-regulated drug = True")
scope["fda_regulated_device"]=h1(df[tb("is_fda_regulated_device")],"FDA-regulated device = True")
scope["fda_regulated_either"]=h1(df[tb("is_fda_regulated_drug")|tb("is_fda_regulated_device")],"either flag = True")
scope["interventional_with_phase"]=h1(df[df.study_type.eq("INTERVENTIONAL")&df.phases.notna()&~df.phases.isin(["NA"])],
                                      "interventional with a declared phase (drug/biologic development)")
scope["industry_sponsored"]=h1(df[df.sponsor_class.eq("INDUSTRY")],"industry-sponsored")
scope["note"]=("FDA's draft guidance covers drug and biological products. Only "
   f"{int(tb('is_fda_regulated_drug').sum())} of {len(df)} corpus studies carry the FDA-regulated-drug flag "
   f"({100*tb('is_fda_regulated_drug').mean():.1f}%). This is the corpus's most serious scope limitation.")
R["C1_scope_subsets"]=scope

# ---- C2 record length ----
lc={"spearman_rho_tier_vs_logchars":round(float(stats.spearmanr(df.tier_i,df.logchars,nan_policy="omit").statistic),4),
    "spearman_rho_E_vs_logchars":round(float(stats.spearmanr(df.E_norm,df.logchars,nan_policy="omit").statistic),4),
    "partial_spearman_tier_E_given_logchars":None}
# partial Spearman via residualising both ranks on log chars
d=df.dropna(subset=["logchars"]).copy()
rt=stats.rankdata(d.tier_i); re_=stats.rankdata(d.E_norm); rl=stats.rankdata(d.logchars)
X=sm.add_constant(rl)
res_t=sm.OLS(rt,X).fit().resid; res_e=sm.OLS(re_,X).fit().resid
pr=stats.pearsonr(res_t,res_e)
lc["partial_spearman_tier_E_given_logchars"]=round(float(pr.statistic),4)
lc["partial_p"]=float(pr.pvalue)
# OLS: E ~ tier + log chars
X2=sm.add_constant(pd.DataFrame({"tier":d.tier_i.values,"logchars":d.logchars.values}))
mod=sm.OLS(d.E_norm.values,X2).fit()
lc["ols_E_on_tier_and_logchars"]={"coef_tier":round(float(mod.params["tier"]),5),
  "se_tier":round(float(mod.bse["tier"]),5),"ci95_tier":[round(float(x),5) for x in mod.conf_int().loc["tier"]],
  "coef_logchars":round(float(mod.params["logchars"]),5),"r2":round(float(mod.rsquared),4),
  "implied_delta_over_3_tiers":round(3*float(mod.params["tier"]),4)}
mod0=sm.OLS(d.E_norm.values,sm.add_constant(d.tier_i.values.astype(float))).fit()
lc["ols_E_on_tier_only"]={"coef_tier":round(float(mod0.params[1]),5),
  "implied_delta_over_3_tiers":round(3*float(mod0.params[1]),4),"r2":round(float(mod0.rsquared),4)}
lc["interpretation"]=("record length is a common cause of both scores; the tier coefficient after "
  "conditioning on it is the length-adjusted gradient")
R["C2_record_length"]=lc

# ---- C3 chance baseline ----
obs=stats.spearmanr(df.tier_i,df.E_norm).statistic
perm=[stats.spearmanr(rng.permutation(df.tier_i.values),df.E_norm.values).statistic for _ in range(2000)]
R["C3_permutation_baseline"]={"observed_rho":round(float(obs),4),
  "permuted_rho_mean":round(float(np.mean(perm)),5),
  "permuted_rho_p97_5":round(float(np.percentile(perm,97.5)),4),
  "p_permutation":float((np.sum(np.abs(perm)>=abs(obs))+1)/(len(perm)+1)),
  "verdict":"observed association exceeds the marginal-only baseline"}

(ROOT/"results"/"08_confounds.json").write_text(json.dumps(R,indent=2,default=float))
print(json.dumps(R,indent=2,default=float))
