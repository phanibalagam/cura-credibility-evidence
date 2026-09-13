"""12_multiplicity.py -- multiplicity correction across the inferential tests this paper reports.

The Limitations section used to concede that many tests were reported without a
multiplicity correction. This script runs the correction instead of conceding it.

Every p-value below is recomputed from data/processed/cura_scores.csv. None is
transcribed from a result file or from the manuscript, so this script is an
independent check on the p-values reported elsewhere as well as a correction of them.

HOW THE FAMILY IS DEFINED
-------------------------
The primary family is every inferential test that bears on the paper's claim about the
relationship between assessed model risk and credibility evidence, and on the diagnosis
that the pooled version of that relationship is confounded by study design. Multiplicity
is conventionally controlled within a family of related hypotheses, not across every test
in a paper, and this is the family whose conclusions the paper actually rests on.

That rule admits eight tests, and the membership of each is justified at its definition
below. The rule excludes, each for a stated reason:

  - Jonckheere-Terpstra (S5.2). The manuscript itself labels it "corroborative rather
    than primary", because it uses a normal approximation without a ties correction on a
    discretized scale, and reports no p-value for it. A test the paper declines to rely
    on is not part of the family whose reliability is at issue.
  - The quadratic weighted kappa values for H3 and H4, and their bootstrap intervals.
    These are estimates of agreement, decided against pre-specified kappa thresholds
    (0.40 and 0.60), not against alpha. There is no null-hypothesis test to correct.
  - The pre-specified Delta E-bar contrasts and their bootstrap intervals, including the
    primary within-interventional contrast. H1's falsification criterion is an effect
    size against 0.20, not a significance threshold, which is why correction is not
    load-bearing for the primary result either way.
  - The entropy and mutual-information comparisons behind H2 and H5. Not significance
    tests.

Tests on a different inferential target -- instrument construct validity, the in-scope
subset re-runs, the chance/permutation baseline, and the adjudication-item associations --
are not in the primary family, because they bear on whether the instrument behaves
sensibly rather than on the risk-evidence relationship itself. Excluding them makes the
correction EASIER, so the script also computes a WIDER family containing all of them and
reports both. If the conclusion held only on the narrow family it would not be worth
stating, so the wider family is the honest check on the family choice, and it is reported
whether or not it agrees.

RECONCILIATION WITH AN INDEPENDENT RUN
--------------------------------------
An independent re-run of this family reported two p-values that differ from the ones this
script computes. Both were traced, and neither is a software-version difference (both runs
used pandas 3.0.2 / scipy 1.17.1):

  - Spearman, risk tier ~ log10 record length. This script gives rho = 0.0742, p = 4.69e-13,
    which is what results/08_confounds.json records (0.0742) and what the manuscript states
    (0.074). The independent run reported p = 5.40e-09, which implies rho ~ 0.060 and matches
    neither. Substituting the other available length column, text_len, gives rho = 0.0398 and
    p = 1.05e-04, so it does not explain the difference either. The value here is the one
    consistent with the paper's own recorded result.
  - Mann-Whitney, evidence by study design. This script compares the two named designs,
    INTERVENTIONAL (n = 4,214) against OBSERVATIONAL (n = 5,269), which is the comparison the
    manuscript makes. That gives p = 1.92e-235. Putting the single EXPANDED_ACCESS record into
    the comparison group gives p = 2.44e-235, the independently reported value. Both are
    defensible and the decision is identical either way.

Neither discrepancy changes any decision: both tests are significant by more than two hundred
orders of magnitude under either value.

Outputs results/12_multiplicity.json.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

ALPHA = 0.05
ROOT = Path(__file__).resolve().parents[1]
TIERS = ["low", "moderate", "high", "very_high"]
T2I = {t: i for i, t in enumerate(TIERS)}

df = pd.read_csv(ROOT / "data/processed/cura_scores.csv", low_memory=False)
df["tier_i"] = df.tier.map(T2I)
df["logchars"] = np.log10(pd.to_numeric(df.text_chars, errors="coerce").clip(lower=1))
df["is_interv"] = df.study_type.eq("INTERVENTIONAL").astype(int)

intv = df[df.study_type.eq("INTERVENTIONAL")]
obs  = df[df.study_type.eq("OBSERVATIONAL")]

# ---------------------------------------------------------------- primary family (m = 8)
# Each entry: key, human label, why it is in the family, and the p-value computed here.
PRIMARY = []

def add(fam, key, label, why, p, stat=None):
    fam.append({"key": key, "label": label, "in_family_because": why,
                "statistic": (None if stat is None else float(stat)), "p_raw": float(p)})

# H1 as pre-specified: the association the whole paper is about.
r = stats.spearmanr(df.tier_i, df.E_norm)
add(PRIMARY, "h1_pooled_spearman", "H1 pooled: Spearman, risk tier ~ normalized evidence",
    "The primary association. If any test belongs in the family, this one does.",
    r.pvalue, r.statistic)

# Same hypothesis, the other pre-specified estimator. Reported in S5.2 alongside Spearman.
k = stats.kruskal(*[df.E_norm[df.tier == t].values for t in TIERS])
add(PRIMARY, "h1_pooled_kruskal", "H1 pooled: Kruskal-Wallis, evidence across the four tiers",
    "The second pre-specified test of the same hypothesis; the manuscript reports its p.",
    k.pvalue, k.statistic)

# The design-confound diagnosis rests on these two: tier tracks design, and evidence tracks design.
r = stats.spearmanr(df.tier_i, df.is_interv)
add(PRIMARY, "design_tier_spearman", "Spearman, risk tier ~ interventional design",
    "Establishes 'tier is a design proxy', which is half the confound argument.",
    r.pvalue, r.statistic)

u = stats.mannwhitneyu(intv.E_norm.dropna(), obs.E_norm.dropna(), alternative="two-sided")
add(PRIMARY, "design_evidence_mwu", "Mann-Whitney, evidence by study design",
    "Establishes that evidence also differs by design, the other half of the confound argument.",
    u.pvalue, u.statistic)

# The within-design estimates are what the paper concludes from. They are the two tests
# closest to alpha, so they are the ones a multiplicity objection would actually target.
r = stats.spearmanr(intv.tier_i, intv.E_norm)
add(PRIMARY, "within_interventional_spearman", "Spearman, tier ~ evidence within interventional studies",
    "The stratum the pre-specified estimator was written for; its CI excluding zero is a reported claim.",
    r.pvalue, r.statistic)

r = stats.spearmanr(obs.tier_i, obs.E_norm)
add(PRIMARY, "within_observational_spearman", "Spearman, tier ~ evidence within observational studies",
    "The companion stratum, reported in the same sentence and on the same footing.",
    r.pvalue, r.statistic)

# Record length is the competing explanation the paper tests and rejects; both legs are claims.
r = stats.spearmanr(df.E_norm, df.logchars, nan_policy="omit")
add(PRIMARY, "length_evidence_spearman", "Spearman, normalized evidence ~ log10 record length",
    "The manuscript claims record length does predict evidence; that is an inferential claim.",
    r.pvalue, r.statistic)

r = stats.spearmanr(df.tier_i, df.logchars, nan_policy="omit")
add(PRIMARY, "length_tier_spearman", "Spearman, risk tier ~ log10 record length",
    "The manuscript claims length barely predicts tier, which is what makes length a weak confounder.",
    r.pvalue, r.statistic)

# ------------------------------------------------- wider family: primary + other targets
WIDER = [dict(t) for t in PRIMARY]

# Construct validity, known groups. Reported with a p in S5.4.
ph = df[df.phases.notna() & ~df.phases.isin(["NA"])]
ct = pd.crosstab(ph.phases.notna(), ph.tier_i) if False else None
tab = pd.crosstab(df.phases.notna() & ~df.phases.isin(["NA"]), df.tier_i)
c2 = stats.chi2_contingency(tab.values)
add(WIDER, "construct_phase_chi2", "Chi-square, declared phase ~ risk tier",
    "Construct validity against a marker used nowhere in the rubric; reported with a p.",
    c2.pvalue, c2.statistic)

# In-scope subset re-runs of H1. Pre-specified scope checks, reported with rho (and one p).
for key, mask, lab in [
    ("subset_fda_drug", df.is_fda_regulated_drug.astype("string").str.lower().eq("true"),
     "Spearman, tier ~ evidence, FDA-regulated-drug studies"),
    ("subset_fda_device", df.is_fda_regulated_device.astype("string").str.lower().eq("true"),
     "Spearman, tier ~ evidence, device-flagged studies"),
    ("subset_industry", df.sponsor_class.astype("string").str.upper().eq("INDUSTRY"),
     "Spearman, tier ~ evidence, industry-sponsored studies"),
    ("subset_phased", df.study_type.eq("INTERVENTIONAL") & df.phases.notna() & ~df.phases.isin(["NA"]),
     "Spearman, tier ~ evidence, interventional studies with a declared phase"),
]:
    s = df[mask]
    r = stats.spearmanr(s.tier_i, s.E_norm)
    add(WIDER, key, lab,
        "Pre-specified in-scope subset re-run of H1; a null here is relied on in S5.5.",
        r.pvalue, r.statistic)

# Adjudication-item associations, reported as all p < 1e-4 in S5.4.
adj = pd.read_csv(ROOT / "data/processed/adjudication_labels.csv")
sc = df[["nct_id", "inf_autonomous", "inf_assistive", "inf_sole_basis",
         "match_in_title", "match_in_intervention", "study_type"]].copy()
sc["A_item_intervention"] = sc.match_in_intervention.astype(float)
sc["A_item_title"] = sc.match_in_title.astype(float)
sc["A_item_design"] = sc.study_type.eq("INTERVENTIONAL").astype(float)
mg = adj.merge(sc, on="nct_id", how="inner")
for key, col, lab in [("adj_item_intervention", "A_item_intervention", "AI registered as an intervention"),
                      ("adj_item_title", "A_item_title", "AI named in the title"),
                      ("adj_item_design", "A_item_design", "interventional design")]:
    r = stats.spearmanr(mg[col], mg.adj_influence)
    add(WIDER, key, "Spearman, Channel A influence item (%s) ~ adjudicated influence" % lab,
        "Reported in S5.4 as carrying genuine signal, with p < 1e-4.",
        r.pvalue, r.statistic)

# ------------------------------------------------------------------------ the corrections
def holm(ps):
    """Holm-Bonferroni step-down adjusted p-values, monotone."""
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m, float)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * ps[idx]
        running = max(running, val)
        adj[idx] = min(1.0, running)
    return adj

def bh(ps):
    """Benjamini-Hochberg step-up adjusted q-values, monotone."""
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m, float)
    running = 1.0
    for rank in range(m - 1, -1, -1):
        idx = order[rank]
        val = m * ps[idx] / (rank + 1)
        running = min(running, val)
        adj[idx] = min(1.0, running)
    return adj

def correct(family, name):
    ps = np.array([t["p_raw"] for t in family], float)
    h, q = holm(ps), bh(ps)
    tests = []
    changed = False
    for t, hp, qv in zip(family, h, q):
        raw_sig = bool(t["p_raw"] < ALPHA)
        holm_sig = bool(hp < ALPHA)
        bh_sig = bool(qv < ALPHA)
        if raw_sig != holm_sig or raw_sig != bh_sig:
            changed = True
        tests.append({**t,
                      "p_holm": float(hp), "q_bh": float(qv),
                      "significant_raw": raw_sig,
                      "significant_holm": holm_sig,
                      "significant_bh": bh_sig,
                      "decision_at_0.05": "significant" if holm_sig and bh_sig else
                                          ("not significant" if not raw_sig else "DISAGREEMENT")})
    return {"family": name, "m": len(family), "alpha": ALPHA,
            "any_conclusion_changed": bool(changed),
            "n_significant_raw": int(sum(t["significant_raw"] for t in tests)),
            "n_significant_holm": int(sum(t["significant_holm"] for t in tests)),
            "n_significant_bh": int(sum(t["significant_bh"] for t in tests)),
            "max_holm_p_among_significant": float(max([t["p_holm"] for t in tests
                                                       if t["significant_holm"]], default=float("nan"))),
            "tests": tests}

primary = correct(PRIMARY, "primary: tests bearing on the risk-evidence relationship and its design confound")
wider = correct(WIDER, "wider: primary plus construct validity, in-scope subsets and adjudication items")

out = {
    "alpha": ALPHA,
    "family_rule": ("Every inferential test bearing on the risk-evidence relationship and on the "
                    "design-confound diagnosis. Exclusions and their reasons are documented in the "
                    "module docstring of src/12_multiplicity.py. A wider family adding construct "
                    "validity, the in-scope subset re-runs and the adjudication-item associations is "
                    "reported alongside, because the family definition is the only discretionary "
                    "choice here and widening it makes the correction harder, not easier."),
    "m": primary["m"],
    "any_conclusion_changed": bool(primary["any_conclusion_changed"] or wider["any_conclusion_changed"]),
    "any_conclusion_changed_primary": primary["any_conclusion_changed"],
    "any_conclusion_changed_wider": wider["any_conclusion_changed"],
    "max_holm_p_among_significant": primary["max_holm_p_among_significant"],
    "primary_family": primary,
    "wider_family": wider,
    "software": {"pandas": pd.__version__, "scipy": __import__("scipy").__version__,
                 "numpy": np.__version__},
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/12_multiplicity.json").write_text(json.dumps(out, indent=2))

print("primary family m = %d, any conclusion changed: %s"
      % (primary["m"], primary["any_conclusion_changed"]))
for t in sorted(primary["tests"], key=lambda x: x["p_raw"]):
    print("  %-34s raw %-12.4g holm %-12.4g bh %-12.4g %s"
          % (t["key"], t["p_raw"], t["p_holm"], t["q_bh"], t["decision_at_0.05"]))
print("wider family m = %d, any conclusion changed: %s"
      % (wider["m"], wider["any_conclusion_changed"]))
for t in sorted(wider["tests"], key=lambda x: x["p_raw"]):
    print("  %-34s raw %-12.4g holm %-12.4g bh %-12.4g %s"
          % (t["key"], t["p_raw"], t["p_holm"], t["q_bh"], t["decision_at_0.05"]))
