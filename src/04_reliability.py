"""H2 discrimination, H3 channel agreement, and the H6 robustness battery.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, itertools
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
from sklearn.metrics import cohen_kappa_score

rng = np.random.default_rng(20260907)
ROOT = Path(__file__).resolve().parents[1]
RUB = json.loads((ROOT/"src"/"cura_rubric.json").read_text())
GRID = RUB["risk_matrix"]["grid"]; THR = RUB["sufficiency_thresholds"]
TIERS = ["low","moderate","high","very_high"]; T2I = {t:i for i,t in enumerate(TIERS)}
DIMS = list(RUB["evidence_dimensions"])
df = pd.read_csv(ROOT/"data"/"processed"/"cura_scores.csv", low_memory=False)
R = {}

# ---------- H2 discrimination ----------
p = df.tier.value_counts(normalize=True).reindex(TIERS).fillna(0).values
H = -(p[p>0]*np.log2(p[p>0])).sum()
R["H2_discrimination"] = {"tier_shares": dict(zip(TIERS, p.round(4))),
    "entropy_bits": round(float(H),4), "normalised_entropy": round(float(H/np.log2(4)),4),
    "largest_tier_share": round(float(p.max()),4),
    "supported": bool(H/np.log2(4) >= 0.50 and p.max() <= 0.80)}

# ---------- H3 channel agreement ----------
def wkappa_ci(a, b, n_boot=2000):
    a = np.asarray(a); b = np.asarray(b)
    k = cohen_kappa_score(a, b, weights="quadratic")
    idx = np.arange(len(a))
    bs = []
    for _ in range(n_boot):
        s = rng.choice(idx, len(idx), replace=True)
        if len(np.unique(a[s])) < 2 or len(np.unique(b[s])) < 2: continue
        bs.append(cohen_kappa_score(a[s], b[s], weights="quadratic"))
    lo, hi = np.percentile(bs, [2.5, 97.5]) if bs else (np.nan, np.nan)
    return {"weighted_kappa": round(float(k),4), "ci95": [round(float(lo),4), round(float(hi),4)],
            "exact_agreement": round(float((a==b).mean()),4), "n": int(len(a))}
ch = {"influence": wkappa_ci(df.A_influence, df.B_influence),
      "consequence": wkappa_ci(df.A_consequence, df.B_consequence)}
for d in DIMS:
    if df["A_"+d].isna().all():
        ch[d] = {"note": "channel A structurally unobservable; no agreement computable"}
    else:
        ch[d] = wkappa_ci(df["A_"+d].fillna(0).astype(int), df["B_"+d].astype(int))
tierA = [GRID[i][c] for i,c in zip(df.A_influence, df.A_consequence)]
tierB = [GRID[i][c] for i,c in zip(df.B_influence, df.B_consequence)]
ch["tier"] = wkappa_ci([T2I[t] for t in tierA], [T2I[t] for t in tierB])
ch["supported"] = bool(ch["influence"]["weighted_kappa"] >= 0.40 and ch["consequence"]["weighted_kappa"] >= 0.40)
ch["interpretation_note"] = ("measurement-channel agreement, not inter-rater reliability: "
    "no human rater and no second rater exists in this design")
R["H3_channel_agreement"] = ch

# ---------- H6 robustness ----------
# Both statistics are reported for every variant. delta_low_to_very_high is the
# PRE-SPECIFIED contrast; delta_low_to_top (low to highest-scoring tier) is a maximum
# over tier means, positively biased under the null, and is a secondary sensitivity only.
def dlvh(mE):
    if mE.get("low") is None or mE.get("very_high") is None: return None
    return round(mE["very_high"] - mE["low"], 4)
rob = {}
# (a) consensus rule
rob["consensus_rule"] = {}
for sfx,name in [("","max"),("_min","min"),("_mean","mean")]:
    d = df["tier"+sfx].map(T2I); e = df["E_norm"+sfx]
    rho = stats.spearmanr(d, e)
    rob["consensus_rule"][name] = {
      "tier_shares": df["tier"+sfx].value_counts(normalize=True).reindex(TIERS).fillna(0).round(4).to_dict(),
      "spearman_rho": round(float(rho.statistic),4), "p": float(rho.pvalue),
      "mean_E_by_tier": {t: round(float(e[df["tier"+sfx]==t].mean()),4) if (df["tier"+sfx]==t).any() else None for t in TIERS},
      "delta_low_to_top": None}
    m = rob["consensus_rule"][name]["mean_E_by_tier"]
    top = [m[t] for t in TIERS[::-1] if m[t] is not None][0]
    rob["consensus_rule"][name]["delta_low_to_top"] = round(top - m["low"], 4)
    rob["consensus_rule"][name]["delta_low_to_very_high"] = dlvh(m)

# (b) risk-matrix form
def tier_from(i,c,form):
    if form=="grid": return GRID[i][c]
    if form=="sum":  s=i+c; return TIERS[min(3, 0 if s<=1 else 1 if s<=2 else 2 if s<=4 else 3)]
    if form=="max":  return TIERS[max(i,c)]
    if form=="prod": pr=i*c; return TIERS[0 if pr==0 else 1 if pr<=2 else 2 if pr<=4 else 3]
rob["risk_matrix_form"] = {}
for form in ("grid","sum","max","prod"):
    t = pd.Series([tier_from(i,c,form) for i,c in zip(df.influence, df.consequence)])
    o = t.map(T2I); rho = stats.spearmanr(o, df.E_norm)
    mE = {k: round(float(df.E_norm[t==k].mean()),4) if (t==k).any() else None for k in TIERS}
    top = [mE[k] for k in TIERS[::-1] if mE[k] is not None][0]
    rob["risk_matrix_form"][form] = {"shares": t.value_counts(normalize=True).reindex(TIERS).fillna(0).round(4).to_dict(),
        "spearman_rho": round(float(rho.statistic),4), "p": float(rho.pvalue),
        "mean_E_by_tier": mE, "delta_low_to_top": round(top-mE["low"],4),
        "delta_low_to_very_high": dlvh(mE)}

# (c) Dirichlet weight perturbation on the five evidence dimensions
base = df[DIMS].values/3.0
taus, deltas, dvh = [], [], []
base_rank = stats.rankdata(base.mean(axis=1))
for _ in range(1000):
    w = rng.dirichlet(np.ones(5)*5)
    e = base @ w
    taus.append(stats.kendalltau(base_rank, stats.rankdata(e)).statistic)
    g = pd.DataFrame({"t": df.tier.map(T2I), "e": e}).groupby("t").e.mean()
    deltas.append(float(g.max()-g.loc[0]))
    dvh.append(float(g.loc[3]-g.loc[0]))
rob["weight_perturbation"] = {"kendall_tau_mean": round(float(np.mean(taus)),4),
    "kendall_tau_p2_5": round(float(np.percentile(taus,2.5)),4),
    "delta_low_to_top_mean": round(float(np.mean(deltas)),4),
    "delta_low_to_top_ci95": [round(float(np.percentile(deltas,2.5)),4), round(float(np.percentile(deltas,97.5)),4)],
    "delta_low_to_very_high_mean": round(float(np.mean(dvh)),4),
    "delta_low_to_very_high_ci95": [round(float(np.percentile(dvh,2.5)),4), round(float(np.percentile(dvh,97.5)),4)],
    "pct_draws_delta_gt_0.20": round(float(np.mean(np.array(deltas)>0.20)*100),2),
    "pct_draws_delta_vh_gt_0.20": round(float(np.mean(np.array(dvh)>0.20)*100),2)}

# (d) sufficiency threshold sweep
sweep = {}
for base_t in np.arange(0.1, 0.95, 0.1):
    thr = {t: round(min(0.95, base_t + 0.2*i),3) for i,t in enumerate(TIERS)}
    ad = df.E_norm >= df.tier.map(thr)
    sweep[f"low_threshold_{base_t:.1f}"] = {"thresholds": thr,
        "sufficient_pct_overall": round(float(ad.mean()*100),2),
        "sufficient_pct_by_tier": {t: round(float(ad[df.tier==t].mean()*100),2) for t in TIERS}}
rob["threshold_sweep"] = sweep
# flat threshold (removes the by-construction gap widening)
flat = {}
for th in np.arange(0.1, 0.85, 0.1):
    ad = df.E_norm >= th
    flat[f"flat_{th:.1f}"] = {t: round(float(ad[df.tier==t].mean()*100),2) for t in TIERS}
rob["flat_threshold_check"] = {"note":"a flat threshold removes the tautology that the gap must widen when theta rises and E is flat",
                               "sufficient_pct_by_tier": flat}

# (e) corpus strictness
strict = {}
for name, mask in [("any_field", pd.Series(True, index=df.index)),
                   ("title_match", df.match_in_title.astype(str).str.lower().eq("true")),
                   ("intervention_match", df.match_in_intervention.astype(str).str.lower().eq("true"))]:
    s = df[mask]
    rho = stats.spearmanr(s.tier.map(T2I), s.E_norm)
    mE = {t: round(float(s.E_norm[s.tier==t].mean()),4) if (s.tier==t).any() else None for t in TIERS}
    top = [mE[t] for t in TIERS[::-1] if mE[t] is not None][0]
    strict[name] = {"n": int(mask.sum()), "spearman_rho": round(float(rho.statistic),4),
                    "p": float(rho.pvalue), "mean_E_by_tier": mE, "delta_low_to_top": round(top-mE["low"],4),
                    "delta_low_to_very_high": dlvh(mE)}
rob["corpus_strictness"] = strict

# (f) temporal split
df["_yr"] = pd.to_datetime(df.first_post_date, errors="coerce", format="mixed").dt.year
tmp = {}
for name, mask in [("pre_2022", df._yr < 2022), ("2022_onward", df._yr >= 2022)]:
    s = df[mask]; rho = stats.spearmanr(s.tier.map(T2I), s.E_norm)
    mE = {t: round(float(s.E_norm[s.tier==t].mean()),4) if (s.tier==t).any() else None for t in TIERS}
    top = [mE[t] for t in TIERS[::-1] if mE[t] is not None][0]
    tmp[name] = {"n": int(mask.sum()), "spearman_rho": round(float(rho.statistic),4), "p": float(rho.pvalue),
                 "mean_E_norm": round(float(s.E_norm.mean()),4), "mean_E_by_tier": mE,
                 "delta_low_to_top": round(top-mE["low"],4),
                 "delta_low_to_very_high": dlvh(mE)}
rob["temporal_split"] = tmp
R["H6_robustness"] = rob

(ROOT/"results"/"04_reliability.json").write_text(json.dumps(R, indent=2, default=float))
print(json.dumps({"H2":R["H2_discrimination"],
                  "H3":{k:v for k,v in R["H3_channel_agreement"].items()},
                  "H6_keys":list(rob)}, indent=2, default=float))
