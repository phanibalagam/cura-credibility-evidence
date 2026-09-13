"""H1 (primary), H5 (added information over comparators), and construct-validity
evidence: known-groups on markers NOT used in scoring, internal consistency,
and dimensionality.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
from sklearn.metrics import mutual_info_score, adjusted_rand_score

rng = np.random.default_rng(20260907)
ROOT = Path(__file__).resolve().parents[1]
RUB = json.loads((ROOT/"src"/"cura_rubric.json").read_text())
TIERS = ["low","moderate","high","very_high"]; T2I = {t:i for i,t in enumerate(TIERS)}
DIMS = list(RUB["evidence_dimensions"])
df = pd.read_csv(ROOT/"data"/"processed"/"cura_scores.csv", low_memory=False)
df["tier_i"] = df.tier.map(T2I)
R = {}

# ================= H1 primary =================
rho = stats.spearmanr(df.tier_i, df.E_norm)
groups = [df.E_norm[df.tier_i==i].values for i in range(4)]
kw = stats.kruskal(*groups)
eps2 = (kw.statistic - 4 + 1) / (len(df) - 4)
# Jonckheere-Terpstra via normal approximation on Mann-Whitney U sum
def jonckheere(gs):
    """Jonckheere-Terpstra for an increasing trend across ordered groups.
    U counts, for every ordered pair of groups a<b, the number of (x in a, y in b)
    with y > x (ties at 0.5), so a positive z means E rises with tier."""
    U = 0.0
    for a in range(len(gs)):
        for b in range(a + 1, len(gs)):
            x, y = gs[a], gs[b]
            gt = stats.mannwhitneyu(y, x, alternative="greater").statistic
            U += gt
    n = sum(len(g) for g in gs)
    EU = (n**2 - sum(len(g)**2 for g in gs)) / 4
    VU = (n**2*(2*n+3) - sum(len(g)**2*(2*len(g)+3) for g in gs)) / 72
    z = (U - EU) / np.sqrt(VU)
    return float(z), float(2*(1-stats.norm.cdf(abs(z))))
jt_z, jt_p = jonckheere(groups)
# H1 pre-specified estimator: low -> very_high (tier_i 0 -> 3). The low -> max-tier
# variant is retained only as a secondary sensitivity; it is NOT the pre-specified
# contrast and is not used for the falsification decision (adversarial finding B-02).
boot, boot_max = [], []
idx = np.arange(len(df))
for _ in range(5000):
    s = rng.choice(idx, len(idx), replace=True)
    m = df.iloc[s].groupby("tier_i").E_norm.mean()
    if 0 in m.index and 3 in m.index: boot.append(float(m.loc[3] - m.loc[0]))
    if 0 in m.index: boot_max.append(float(m.max() - m.loc[0]))
_m = df.groupby("tier_i").E_norm.mean()
delta = float(_m.loc[3] - _m.loc[0])
delta_max = float(_m.max() - _m.loc[0])
R["H1_risk_proportionality"] = {
  "spearman_rho": round(float(rho.statistic),4), "spearman_p": float(rho.pvalue),
  "kruskal_H": round(float(kw.statistic),3), "kruskal_p": float(kw.pvalue),
  "epsilon_squared": round(float(eps2),5),
  "jonckheere_z": round(jt_z,3), "jonckheere_p": jt_p, "jonckheere_direction": "positive z = evidence increases with tier",
  "mean_E_norm_by_tier": {t: round(float(df.E_norm[df.tier==t].mean()),4) for t in TIERS},
  "sd_E_norm_by_tier": {t: round(float(df.E_norm[df.tier==t].std()),4) for t in TIERS},
  "n_by_tier": {t: int((df.tier==t).sum()) for t in TIERS},
  "delta_low_to_very_high": round(delta,4),
  "delta_ci95": [round(float(np.percentile(boot,2.5)),4), round(float(np.percentile(boot,97.5)),4)],
  "secondary_delta_low_to_max_tier": round(delta_max,4),
  "secondary_delta_low_to_max_tier_ci95": [round(float(np.percentile(boot_max,2.5)),4),
                                           round(float(np.percentile(boot_max,97.5)),4)],
  "estimator_note": ("delta_low_to_very_high is the pre-specified contrast used for the H1 "
                     "decision; the low-to-max-tier variant is reported for transparency only."),
  "monotone_across_all_four_tiers": bool(all(
      df.E_norm[df.tier==TIERS[i]].mean() <= df.E_norm[df.tier==TIERS[i+1]].mean() for i in range(3))),
  "prespecified_criterion": "rho>0 with CI excluding 0 AND delta > 0.20",
  "criterion_rho_met": bool(rho.statistic > 0 and rho.pvalue < 0.05),
  "criterion_delta_met": bool(np.percentile(boot,2.5) > 0.20),
  "SUPPORTED": bool(rho.statistic > 0 and rho.pvalue < 0.05 and np.percentile(boot,2.5) > 0.20)}

# ================= comparators (H5) =================
# B1 EU AI Act-style category tiering (Annex III / safety-component analogue)
dev = df.is_fda_regulated_device.astype(str).str.lower().eq("true")
b1 = np.where(dev | df.primary_purpose.isin(["DIAGNOSTIC","TREATMENT","SCREENING"]), "high",
     np.where(df.inf_assistive.astype(bool), "limited", "minimal"))
# B2 risk tier only (CURA without the evidence layer)
b2 = df.tier.values
# B3 flat reporting-completeness quartile (CURA without the risk layer)
b3 = pd.qcut(df.n_evidence_terms.rank(method="first"), 4, labels=["q1","q2","q3","q4"]).astype(str).values
# CURA output = tier x sufficiency
cura = (df.tier + "|" + df.sufficient.astype(str)).values

def ent(x):
    p = pd.Series(x).value_counts(normalize=True).values
    return float(-(p*np.log2(p)).sum())
def cond_ent(y, x):   # H(Y|X) in bits
    return ent(y) - mutual_info_score(x, y)/np.log(2)
comp = {}
for name, b in [("B1_eu_ai_act_style", b1), ("B2_risk_tier_only", b2), ("B3_reporting_count_only", b3)]:
    mi = mutual_info_score(b, cura)/np.log(2)
    comp[name] = {"n_levels": int(pd.Series(b).nunique()),
        "H_comparator_bits": round(ent(b),4), "H_CURA_bits": round(ent(cura),4),
        "mutual_information_bits": round(float(mi),4),
        "H_CURA_given_comparator_bits": round(float(cond_ent(cura, b)),4),
        "normalised_MI": round(float(mi/np.sqrt(ent(b)*ent(cura))),4),
        "adjusted_rand_index": round(float(adjusted_rand_score(b, cura)),4),
        "criterion_H_ge_0.30": bool(cond_ent(cura, b) >= 0.30)}
comp["SUPPORTED"] = bool(all(v["criterion_H_ge_0.30"] for k,v in comp.items() if k.startswith("B")))
comp["crosstab_B1_vs_tier"] = pd.crosstab(pd.Series(b1,name="B1"), df.tier).reindex(columns=TIERS).fillna(0).astype(int).to_dict()
R["H5_added_information"] = comp

# ================= construct validity: known groups =================
# markers NOT used anywhere in the rubric: phase, sponsor class, enrollment, n_conditions
kg = {}
ph = df.phases.fillna("NONE").apply(lambda s: "PHASED" if s not in ("NONE","NA") else s)
ct = pd.crosstab(ph, df.tier).reindex(columns=TIERS).fillna(0)
chi = stats.chi2_contingency(ct.values)
kg["phase"] = {"crosstab": ct.astype(int).to_dict(), "chi2": round(float(chi.statistic),2),
   "p": float(chi.pvalue), "cramers_v": round(float(np.sqrt(chi.statistic/(len(df)*min(ct.shape)-1))),4),
   "mean_tier_ord": {k: round(float(df.tier_i[ph==k].mean()),3) for k in ct.index}}
sc = df.sponsor_class.fillna("UNKNOWN")
top = sc.value_counts().head(4).index
ct2 = pd.crosstab(sc[sc.isin(top)], df.tier[sc.isin(top)]).reindex(columns=TIERS).fillna(0)
chi2 = stats.chi2_contingency(ct2.values)
kg["sponsor_class"] = {"crosstab": ct2.astype(int).to_dict(), "chi2": round(float(chi2.statistic),2),
   "p": float(chi2.pvalue), "mean_tier_ord": {k: round(float(df.tier_i[sc==k].mean()),3) for k in top}}
enr = pd.to_numeric(df.enrollment, errors="coerce")
enr_w = enr.clip(upper=enr.quantile(0.99))
kg["enrollment"] = {"spearman_rho_tier": round(float(stats.spearmanr(df.tier_i, enr_w, nan_policy="omit").statistic),4),
   "p": float(stats.spearmanr(df.tier_i, enr_w, nan_policy="omit").pvalue),
   "median_by_tier": {t: float(enr_w[df.tier==t].median()) for t in TIERS},
   "note": "winsorised at p99; raw max 50,000,000 is an unvalidated registry value"}
R["construct_validity_known_groups"] = kg

# ================= internal consistency & dimensionality =================
X = df[DIMS].values.astype(float)
k = X.shape[1]
alpha = k/(k-1) * (1 - X.var(axis=0, ddof=1).sum()/X.sum(axis=1).var(ddof=1))
corr = pd.DataFrame(X, columns=DIMS).corr(method="spearman")
ev = np.linalg.eigvalsh(np.corrcoef(X, rowvar=False))[::-1]
R["scale_structure"] = {
 "cronbach_alpha": round(float(alpha),4),
 "interpretation": ("CURA's evidence layer is a FORMATIVE index, not a reflective scale: "
   "the five dimensions are distinct evidentiary obligations, not interchangeable indicators "
   "of one latent trait. A low alpha is the expected and correct result here; a high alpha "
   "would indicate redundant dimensions."),
 "spearman_inter_dimension": corr.round(3).to_dict(),
 "max_abs_offdiagonal_rho": round(float(np.abs(corr.values - np.eye(k)).max()),4),
 "eigenvalues": [round(float(e),4) for e in ev],
 "variance_explained_pc1": round(float(ev[0]/ev.sum()),4)}

(ROOT/"results"/"05_validity_baselines.json").write_text(json.dumps(R, indent=2, default=float))
print(json.dumps({"H1":R["H1_risk_proportionality"],"H5":{k:v for k,v in comp.items() if k!="crosstab_B1_vs_tier"},
  "alpha":R["scale_structure"]["cronbach_alpha"],"pc1":R["scale_structure"]["variance_explained_pc1"],
  "kg_phase_mean_tier":kg["phase"]["mean_tier_ord"],"kg_sponsor":kg["sponsor_class"]["mean_tier_ord"],
  "kg_enroll":kg["enrollment"]["spearman_rho_tier"]}, indent=2, default=float))
