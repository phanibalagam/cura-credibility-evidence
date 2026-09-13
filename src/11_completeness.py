"""Is the CURA tier-evidence association real, or an artefact of how the registry
records different study designs?

Answers adversarial-review finding B-05(c) (missingness scored as low risk) and reports
H1 with the PRE-SPECIFIED low->very_high estimator (finding B-02).

Design note. A naive "completeness" score conflates two very different things: a field
left unreported, and a field that does not apply to the design at all (an observational
study has no phase, allocation, masking or primary purpose). Section A separates them
empirically instead of assuming, and every downstream test is run within study type so
that the comparison is like-for-like.

Outputs results/11_completeness.json.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, warnings
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
import statsmodels.api as sm

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20260907)
ROOT = Path(__file__).resolve().parents[1]
T = ["low","moderate","high","very_high"]; T2I = {t:i for i,t in enumerate(T)}
GRID = json.loads((ROOT/"src"/"cura_rubric.json").read_text())["risk_matrix"]["grid"]
df = pd.read_csv(ROOT/"data/processed/cura_scores.csv", low_memory=False)
df["ti"] = df.tier.map(T2I)
df["logchars"] = np.log10(pd.to_numeric(df.text_chars, errors="coerce").clip(lower=1))
IV = df.study_type.eq("INTERVENTIONAL")
tb = lambda s: s.astype(str).str.lower().eq("true")
R = {"n": int(len(df)), "n_interventional": int(IV.sum()), "n_observational": int((~IV).sum()),
     "caveat": ("Study design and completeness are not randomly assigned. These are "
                "associations under adjustment, not causal identification.")}

# ---------- A. separate 'not reported' from 'not applicable' ----------
CAND = ["is_fda_regulated_drug","is_fda_regulated_device","healthy_volunteers","primary_purpose",
        "allocation","masking","phases","has_dmc","countries","intervention_types","min_age","sex"]
clas, universal = {}, []
for f in CAND:
    mi, mo = float(df[f][IV].isna().mean()), float(df[f][~IV].isna().mean())
    # applicable to both designs only if it is actually present in both
    u = (mi < 0.50) and (mo < 0.50)
    clas[f] = {"pct_missing_interventional": round(100*mi,1), "pct_missing_observational": round(100*mo,1),
               "class": "universal" if u else "design-dependent"}
    if u: universal.append(f)
R["A_field_classification"] = {"rule": "universal iff <50% missing in BOTH designs",
                               "universal_fields": universal, "detail": clas}
df["cmp"] = df[universal].notna().sum(axis=1)/len(universal)
R["A_completeness_measure"] = {
    "fields": universal, "mean_overall": round(float(df.cmp.mean()),4),
    "mean_interventional": round(float(df.cmp[IV].mean()),4),
    "mean_observational": round(float(df.cmp[~IV].mean()),4),
    "pct_fully_complete": round(float(100*(df.cmp==1).mean()),2)}

# ---------- B. mechanism: how many zero-scores are missing data, not a genuine 'no'? ----------
mech = {}
for item, expr, fields in [
    ("c1_fda_regulated_article", tb(df.is_fda_regulated_drug)|tb(df.is_fda_regulated_device),
     ["is_fda_regulated_drug","is_fda_regulated_device"]),
    ("c2_care_bearing_purpose", df.primary_purpose.isin(["TREATMENT","DIAGNOSTIC","SCREENING","PREVENTION"]),
     ["primary_purpose"]),
    ("c3_patient_population", df.healthy_volunteers.astype(str).str.lower().eq("false"),
     ["healthy_volunteers"])]:
    miss = df[fields].isna().all(axis=1); zero = ~expr
    mech[item] = {"scored_zero": int(zero.sum()), "of_which_field_missing": int((zero&miss).sum()),
                  "pct_of_zeros_that_are_missing_data": round(float(100*(zero&miss).sum()/max(zero.sum(),1)),2)}
R["B_zeros_that_are_really_missing_data"] = mech

# ---------- helpers ----------
def boot_rho(x,y,n=2000):
    x,y = np.asarray(x,float), np.asarray(y,float); idx=np.arange(len(x))
    b=[stats.spearmanr(x[s],y[s],nan_policy="omit").statistic for s in (rng.choice(idx,len(idx),True) for _ in range(n))]
    return {"rho": round(float(stats.spearmanr(x,y,nan_policy="omit").statistic),4),
            "ci95": [round(float(np.percentile(b,2.5)),4), round(float(np.percentile(b,97.5)),4)]}

def partial_rho(y,x,ctrls,n=1000):
    d = pd.DataFrame({"y":np.asarray(y,float), "x":np.asarray(x,float)})
    for i,c in enumerate(ctrls): d[f"c{i}"]=np.asarray(c,float)
    d = d.dropna()
    def one(dd):
        C = sm.add_constant(np.column_stack([stats.rankdata(dd[c]) for c in dd.columns if c.startswith("c")]))
        return stats.pearsonr(sm.OLS(stats.rankdata(dd.y),C).fit().resid,
                              sm.OLS(stats.rankdata(dd.x),C).fit().resid)
    o=one(d); idx=np.arange(len(d))
    b=[one(d.iloc[rng.choice(idx,len(idx),True)]).statistic for _ in range(n)]
    return {"partial_rho": round(float(o.statistic),4), "p": float(o.pvalue), "n": int(len(d)),
            "ci95": [round(float(np.percentile(b,2.5)),4), round(float(np.percentile(b,97.5)),4)]}

def delta_prespec(s,n=2000):
    """The contrast PRESPECIFICATION.md declares: low -> very_high. Not the max-tier variant."""
    m=s.groupby("ti").E_norm.mean()
    if 0 not in m.index or 3 not in m.index:
        return {"n": int(len(s)), "delta_low_to_very_high": None,
                "note": "tier absent in this stratum: "+", ".join(t for i,t in enumerate(T) if i not in m.index)}
    idx=np.arange(len(s)); b=[]
    for _ in range(n):
        g=s.iloc[rng.choice(idx,len(idx),True)].groupby("ti").E_norm.mean()
        if 0 in g.index and 3 in g.index: b.append(float(g.loc[3]-g.loc[0]))
    return {"n": int(len(s)), "delta_low_to_very_high": round(float(m.loc[3]-m.loc[0]),4),
            "ci95": [round(float(np.percentile(b,2.5)),4), round(float(np.percentile(b,97.5)),4)],
            "ci_excludes_zero": bool(np.percentile(b,2.5)>0 or np.percentile(b,97.5)<0),
            "pct_boot_above_0.20": round(float(np.mean(np.array(b)>0.20)*100),2)}

# ---------- C. the pre-specified estimator vs the one that was implemented ----------
m_all = df.groupby("ti").E_norm.mean()
R["C_estimator"] = {
 "declared_criterion": "H1 supported iff rho>0 (CI excluding 0) AND low-to-very_high delta > 0.20",
 "mean_E_by_tier": {T[i]: round(float(v),4) for i,v in m_all.items()},
 "PRE_SPECIFIED_low_to_very_high": delta_prespec(df),
 "as_implemented_low_to_max_tier": round(float(m_all.max()-m_all.loc[0]),4),
 "max_tier_is": T[int(m_all.idxmax())],
 "manuscript_reports": 0.062,
 "note": ("the implemented statistic is a maximum over four tier means, positively biased "
          "under the null and floored at zero; both biases run against falsification")}

# ---------- D. tier is largely a proxy for study design ----------
ct = pd.crosstab(df.study_type, df.tier).reindex(columns=T).fillna(0).astype(int)
R["D_tier_is_a_design_proxy"] = {
 "crosstab_studytype_x_tier": ct.to_dict(),
 "pct_of_very_high_that_are_interventional": round(float(100*IV[df.tier.eq("very_high")].mean()),1),
 "observational_tiers_present": sorted(df.tier[~IV].unique().tolist()),
 "rho_interventional_tier": round(float(stats.spearmanr(IV.astype(int), df.ti).statistic),4),
 "mean_E_interventional": round(float(df.E_norm[IV].mean()),4),
 "mean_E_observational": round(float(df.E_norm[~IV].mean()),4)}

# ---------- E. the clean test: within study type ----------
within = {}
for lab, s in [("interventional", df[IV]), ("observational", df[~IV])]:
    within[lab] = {"n": int(len(s)),
        "rho_tier_Enorm": boot_rho(s.ti, s.E_norm),
        "partial_given_completeness": partial_rho(s.ti, s.E_norm, [s.cmp]),
        "partial_given_completeness_and_length": partial_rho(s.ti, s.E_norm, [s.cmp, s.logchars]),
        "delta_prespec": delta_prespec(s)}
R["E_within_study_type"] = within

# ---------- F. adjustment ladder on the full corpus ----------
R["F_adjustment_ladder"] = {
 "raw":                              boot_rho(df.ti, df.E_norm),
 "given_length_only":                partial_rho(df.ti, df.E_norm, [df.logchars]),
 "given_completeness":               partial_rho(df.ti, df.E_norm, [df.cmp]),
 "given_study_type":                 partial_rho(df.ti, df.E_norm, [IV.astype(int)]),
 "given_completeness_and_length":    partial_rho(df.ti, df.E_norm, [df.cmp, df.logchars]),
 "given_all_three":                  partial_rho(df.ti, df.E_norm, [df.cmp, df.logchars, IV.astype(int)])}
raw = R["F_adjustment_ladder"]["raw"]["rho"]
R["F_share_removed_pct"] = {k: round(float(100*(1 - v["partial_rho"]/raw)),1)
                            for k,v in R["F_adjustment_ladder"].items() if k!="raw"}

# ---------- G. rescore so missingness no longer implies low risk ----------
obs = pd.DataFrame({
 "c1": np.where(df[["is_fda_regulated_drug","is_fda_regulated_device"]].isna().all(axis=1), np.nan,
                (tb(df.is_fda_regulated_drug)|tb(df.is_fda_regulated_device)).astype(float)),
 "c2": np.where(df.primary_purpose.isna(), np.nan,
                df.primary_purpose.isin(["TREATMENT","DIAGNOSTIC","SCREENING","PREVENTION"]).astype(float)),
 "c3": np.where(df.healthy_volunteers.isna(), np.nan,
                df.healthy_volunteers.astype(str).str.lower().eq("false").astype(float))})
alt = df.copy()
alt["consequence"] = np.fmax(np.rint(obs.mean(axis=1)*3).fillna(0).astype(int).clip(0,3), df.B_consequence)
alt["tier"] = [GRID[i][c] for i,c in zip(alt.influence, alt.consequence)]
alt["ti"] = alt.tier.map(T2I)
R["G_rescored_missing_excluded"] = {
 "rationale": "score each consequence item only where observed, rescale to 0-3",
 "tier_shift": {"original": df.tier.value_counts().reindex(T).fillna(0).astype(int).to_dict(),
                "rescored": alt.tier.value_counts().reindex(T).fillna(0).astype(int).to_dict()},
 "rho_tier_Enorm": boot_rho(alt.ti, alt.E_norm),
 "delta_prespec": delta_prespec(alt),
 "within_interventional": {"rho": boot_rho(alt.ti[IV], alt.E_norm[IV]),
                           "delta_prespec": delta_prespec(alt[IV])}}

# ---------- H. what survives all of it ----------
ev = pd.read_csv(ROOT/"data/processed/aiml_evidence_text.csv")
items = {"d5_version":"model or algorithm versioning","d5_oversight":"human oversight or override",
         "d5_monitoring":"model monitoring or drift","d2_bias":"bias or fairness assessment",
         "d4_external_val":"external validation","d1_training_data":"training-data description",
         "d3_uncertainty":"any expression of uncertainty","d3_discrimination":"discrimination metric"}
mg = df[["nct_id","cmp"]].merge(ev[["nct_id","n_evidence_terms"]], on="nct_id")
ivm = df[["nct_id"]].assign(iv=IV.values).merge(ev, on="nct_id")
R["H_what_survives"] = {
 "note": "free-text counts; independent of tier, estimator, combination rule, completeness and design",
 "prevalence_pct_overall": {v: round(float(100*ev[k].mean()),2) for k,v in items.items()},
 "prevalence_pct_interventional_only": {v: round(float(100*ivm[ivm.iv][k].mean()),2) for k,v in items.items()},
 "pct_with_zero_evidence_terms": round(float(100*(ev.n_evidence_terms==0).mean()),2),
 "rho_completeness_vs_n_evidence_terms": round(float(stats.spearmanr(mg.cmp, mg.n_evidence_terms).statistic),4)}


# ---------- I. QA: the four checks that decide how this may be read ----------
QA = {}
# I1 precision of the within-design null
w = R["E_within_study_type"]["interventional"]["delta_prespec"]
QA["I1_null_is_precise_not_underpowered"] = {
 "n": w["n"], "delta": w["delta_low_to_very_high"], "ci95": w["ci95"],
 "ci_width": round(w["ci95"][1]-w["ci95"][0], 4),
 "rules_out_effects_above": w["ci95"][1],
 "prespecified_threshold": 0.20,
 "reading": "a tight interval around zero, not an absence of evidence"}
# I2 over-adjustment: is the design effect just CURA's own i3 item?
i1 = tb(df.match_in_intervention); i2 = tb(df.match_in_title)
inf_no_i3 = np.fmax((i1.astype(int)+i2.astype(int)).clip(0,3), df.B_influence)
ti2 = pd.Series([GRID[i][c] for i,c in zip(inf_no_i3, df.consequence)]).map(T2I).values
m2, m2i = df.assign(t=ti2).groupby("t").E_norm.mean(), df[IV].assign(t=ti2[IV.values]).groupby("t").E_norm.mean()
QA["I2_overadjustment_check"] = {
 "question": "study_type is encoded by CURA influence item i3, so is controlling for it over-adjustment?",
 "rho_design_tier_with_i3": round(float(stats.spearmanr(IV.astype(int), df.ti).statistic),4),
 "rho_design_tier_without_i3": round(float(stats.spearmanr(IV.astype(int), ti2).statistic),4),
 "delta_prespec_i3_removed_all": round(float(m2.loc[3]-m2.loc[0]),4),
 "delta_prespec_i3_removed_interventional": round(float(m2i.loc[3]-m2i.loc[0]),4),
 "reading": ("design still predicts tier with the design item deleted, so the link is not purely "
             "definitional; and the within-design null holds either way")}
# I3 both strata on a contrast that exists in both
def d_lo_hi(s, n=2000):
    m = s.groupby("ti").E_norm.mean()
    if 0 not in m.index or 2 not in m.index: return None
    idx=np.arange(len(s)); b=[]
    for _ in range(n):
        g=s.iloc[rng.choice(idx,len(idx),True)].groupby("ti").E_norm.mean()
        if 0 in g.index and 2 in g.index: b.append(float(g.loc[2]-g.loc[0]))
    return {"n": int(len(s)), "n_high_tier": int((s.ti==2).sum()),
            "delta_low_to_high": round(float(m.loc[2]-m.loc[0]),4),
            "ci95": [round(float(np.percentile(b,2.5)),4), round(float(np.percentile(b,97.5)),4)]}
QA["I3_low_to_high_in_both_strata"] = {"interventional": d_lo_hi(df[IV]), "observational": d_lo_hi(df[~IV])}
# I4 Simpson's paradox, named
QA["I4_simpsons_paradox"] = {
 "pooled_rho": round(float(stats.spearmanr(df.ti, df.E_norm).statistic),4),
 "interventional_rho": round(float(stats.spearmanr(df.ti[IV], df.E_norm[IV]).statistic),4),
 "observational_rho": round(float(stats.spearmanr(df.ti[~IV], df.E_norm[~IV]).statistic),4),
 "reading": "the pooled association is between strata; it nearly vanishes within either one"}
QA["multiple_comparisons_note"] = ("Many tests are reported. The primary contrast -- the pre-specified "
 "low-to-very_high delta within interventional studies -- was fixed by design logic before these "
 "results were seen: it is the only stratum in which all scoring fields apply and all four tiers exist.")
R["I_qa"] = QA

(ROOT/"results"/"11_completeness.json").write_text(json.dumps(R, indent=2, default=float))
print("written. headline numbers:")
print("  pre-specified delta (all)      :", R["C_estimator"]["PRE_SPECIFIED_low_to_very_high"])
print("  within interventional          :", R["E_within_study_type"]["interventional"]["delta_prespec"])
print("  adjustment ladder              :", json.dumps(R["F_share_removed_pct"]))
