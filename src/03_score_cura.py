"""Apply the CURA rubric to the corpus through both measurement channels.
Outputs data/processed/cura_scores.csv and results/03_scoring_summary.json.
Every number in the paper's scoring tables comes from here.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, hashlib
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUB = json.loads((ROOT/"src"/"cura_rubric.json").read_text())
GRID = RUB["risk_matrix"]["grid"]
THR = RUB["sufficiency_thresholds"]
TIERS = ["low", "moderate", "high", "very_high"]
DIMS = list(RUB["evidence_dimensions"])

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def tb(s):  # registry booleans arrive as strings
    return s.astype(str).str.lower().eq("true")

meta = pd.read_csv(ROOT/"data"/"processed"/"aiml_studies.csv", dtype=str)
txt  = pd.read_csv(ROOT/"data"/"processed"/"aiml_evidence_text.csv")
df = meta.merge(txt.drop(columns=["text_snapshot"]), on="nct_id", validate="1:1")
assert len(df) == len(meta) == 9484, len(df)

# ---------------- Channel A: structured registry metadata ----------------
df["n_locations_i"] = pd.to_numeric(df.n_locations, errors="coerce").fillna(0)
df["n_result_refs_i"] = pd.to_numeric(df.n_result_refs, errors="coerce").fillna(0)
df["n_countries"] = df.countries.fillna("").apply(lambda s: len([x for x in s.split("|") if x]))

a_i1 = tb(df.match_in_intervention)
a_i2 = tb(df.match_in_title)
a_i3 = df.study_type.eq("INTERVENTIONAL")
df["A_influence"] = (a_i1.astype(int) + a_i2.astype(int) + a_i3.astype(int)).clip(0, 3)

a_c1 = tb(df.is_fda_regulated_drug) | tb(df.is_fda_regulated_device)
a_c2 = df.primary_purpose.isin(["TREATMENT", "DIAGNOSTIC", "SCREENING", "PREVENTION"])
a_c3 = df.healthy_volunteers.astype(str).str.lower().eq("false")
df["A_consequence"] = (a_c1.astype(int) + a_c2.astype(int) + a_c3.astype(int)).clip(0, 3)

df["A_D1_data_quality_provenance"] = np.nan          # structurally unobservable
df["A_D3_uncertainty_performance"] = np.nan          # structurally unobservable
df["A_D2_representativeness_bias"] = ((df.n_countries > 1).astype(int)
                                      + (df.n_locations_i >= 5).astype(int)
                                      + df.sex.eq("ALL").astype(int))
df["A_D4_independent_validation"] = (df.allocation.eq("RANDOMIZED").astype(int)
                                     + (df.masking.notna() & df.masking.ne("NONE")).astype(int)
                                     + tb(df.has_results).astype(int))
df["A_D5_lifecycle_monitoring"] = (tb(df.has_dmc).astype(int)
                                   + (df.n_result_refs_i >= 1).astype(int)
                                   + (df.overall_status.isin(["ACTIVE_NOT_RECRUITING", "COMPLETED"])
                                      & tb(df.has_results)).astype(int))

# ---------------- Channel B: free-text lexicon ----------------
df["B_influence"] = np.select(
    [df.inf_sole_basis, df.inf_autonomous, df.inf_assistive], [3, 2, 1], default=0)
df["B_consequence"] = df[["con_treatment", "con_safety", "con_triage"]].sum(axis=1).clip(0, 3)
for d, items in RUB["channel_b_text"]["evidence"].items():
    df["B_" + d] = df[items].sum(axis=1).clip(0, 3)

# ---------------- consensus (max), plus min/mean variants ----------------
def combine(a, b, how):
    if how == "max":  return np.fmax(a, b)
    if how == "min":  return np.fmin(a, b)
    return np.nanmean(np.vstack([a, b]), axis=0)

for how in ("max", "min", "mean"):
    sfx = "" if how == "max" else "_" + how
    inf = combine(df.A_influence.values.astype(float), df.B_influence.values.astype(float), how)
    con = combine(df.A_consequence.values.astype(float), df.B_consequence.values.astype(float), how)
    df["influence" + sfx] = np.rint(inf).astype(int)
    df["consequence" + sfx] = np.rint(con).astype(int)
    df["tier" + sfx] = [GRID[i][c] for i, c in zip(df["influence"+sfx], df["consequence"+sfx])]
    tot = np.zeros(len(df))
    for d in DIMS:
        v = combine(df["A_"+d].values.astype(float), df["B_"+d].values.astype(float), how)
        v = np.where(np.isnan(v), df["B_"+d].values.astype(float), v)   # A unobservable -> B alone
        df[d + sfx] = np.rint(v).astype(int)
        tot += df[d + sfx]
    df["E_total" + sfx] = tot
    df["E_norm" + sfx] = tot / (3 * len(DIMS))
    df["threshold" + sfx] = df["tier" + sfx].map(THR)
    df["sufficient" + sfx] = df["E_norm" + sfx] >= df["threshold" + sfx]
    df["sufficiency_gap" + sfx] = (df["threshold" + sfx] - df["E_norm" + sfx]).clip(lower=0)

df["tier_ord"] = df.tier.map({t: i for i, t in enumerate(TIERS)})
out = ROOT/"data"/"processed"/"cura_scores.csv"
df.to_csv(out, index=False)

summ = {
 "n": int(len(df)),
 "rubric_version": RUB["version"],
 "corpus_sha256": {"aiml_studies.csv": sha(ROOT/"data/processed/aiml_studies.csv"),
                   "aiml_evidence_text.csv": sha(ROOT/"data/processed/aiml_evidence_text.csv")},
 "influence_dist": {"A": df.A_influence.value_counts().sort_index().to_dict(),
                    "B": pd.Series(df.B_influence).value_counts().sort_index().to_dict(),
                    "consensus": df.influence.value_counts().sort_index().to_dict()},
 "consequence_dist": {"A": df.A_consequence.value_counts().sort_index().to_dict(),
                      "B": df.B_consequence.value_counts().sort_index().to_dict(),
                      "consensus": df.consequence.value_counts().sort_index().to_dict()},
 "tier_dist": df.tier.value_counts().reindex(TIERS).to_dict(),
 "tier_dist_min": df.tier_min.value_counts().reindex(TIERS).to_dict(),
 "tier_dist_mean": df.tier_mean.value_counts().reindex(TIERS).to_dict(),
 "evidence_dim_mean": {d: round(float(df[d].mean()), 4) for d in DIMS},
 "evidence_dim_pct_zero": {d: round(float((df[d] == 0).mean()*100), 2) for d in DIMS},
 "E_norm": {"mean": round(float(df.E_norm.mean()), 4), "median": float(df.E_norm.median()),
            "p90": float(df.E_norm.quantile(.9)), "max": float(df.E_norm.max()),
            "pct_zero": round(float((df.E_total == 0).mean()*100), 2)},
 "sufficient_pct_overall": round(float(df.sufficient.mean()*100), 2),
 "sufficient_pct_by_tier": {t: round(float(df.loc[df.tier == t, "sufficient"].mean()*100), 2) for t in TIERS},
 "mean_E_norm_by_tier": {t: round(float(df.loc[df.tier == t, "E_norm"].mean()), 4) for t in TIERS},
 "channel_A_unobservable_dims": ["D1_data_quality_provenance", "D3_uncertainty_performance"],
}
(ROOT/"results"/"03_scoring_summary.json").write_text(json.dumps(summ, indent=2))
print(json.dumps(summ, indent=2))
