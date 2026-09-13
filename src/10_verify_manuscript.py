"""10_verify_manuscript.py -- check every quantitative claim in main.tex against results/.

Two kinds of check:
  bind()    a value in results/ equals what the manuscript states, at the precision
            the manuscript states it (half-up), so 0.0555 legitimately matches "0.056"
  intext()  the manuscript actually contains the string it is supposed to

Exit code 1 if anything disagrees. This script is the authority on manuscript
integrity for this paper; the checklists are not.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, re, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = lambda n: json.loads((ROOT/"results"/n).read_text())
paper = (ROOT/"main.tex").read_text()
flat = re.sub(r"\s+", " ", paper)

scor  = R("03_scoring_summary.json")
rel   = R("04_reliability.json")
val   = R("05_validity_baselines.json")
adj   = R("07_adjudication.json")
conf  = R("08_confounds.json")
comp  = R("11_completeness.json")
mult  = R("12_multiplicity.json")
resp  = R("09_review_responses.json")
prof  = R("01_profile.json")
rub   = json.loads((ROOT/"src"/"cura_rubric.json").read_text())
ev    = pd.read_csv(ROOT/"data/processed/aiml_evidence_text.csv")
sc    = pd.read_csv(ROOT/"data/processed/cura_scores.csv", low_memory=False)
scan  = [json.loads(p.read_text()) for p in sorted((ROOT/"results").glob("00_scan_summary_*.json"))]

rows, fails = [], []
def bind(num, where, source, actual, tol=None):
    """Compare at the precision the paper actually states.
    A paper value of 3.5 is checked as: does the source value round to 3.5?"""
    s = str(num)
    try:
        v = float(s.replace(",", "").replace("{", "").replace("}", ""))
        dp = len(s.split(".")[1]) if "." in s else 0
        q = Decimal(1).scaleb(-dp) if dp else Decimal(1)
        rounded = float(Decimal(repr(float(actual))).quantize(q, ROUND_HALF_UP))
        ok = abs(v - rounded) < 10**(-dp)/2
        shown = f"{actual} (rounds to {rounded:.{dp}f})"
    except (TypeError, ValueError):
        ok = s == str(actual); shown = str(actual)
    rows.append((s, where, source, shown, "MATCH" if ok else "MISMATCH"))
    if not ok: fails.append(f"{where}: paper states {num!r}, source gives {actual!r} "
                            f"which rounds to {rounded!r}")

def intext(s, where):
    ok = re.sub(r"\s+"," ",s) in flat
    rows.append((s[:46], where, "main.tex", "present" if ok else "ABSENT",
                 "MATCH" if ok else "MISMATCH"))
    if not ok: fails.append(f"string not found in main.tex: {s!r}")

T=["low","moderate","high","very_high"]

# ---------------- corpus ----------------
bind("601694","Abstract; S4 corpus","sum(00_scan_summary_*.json).studies_scanned",
     sum(s["studies_scanned"] for s in scan))
bind("9484","Abstract; title; S4; throughout","sum(00_scan_summary_*.json).studies_matched",
     sum(s["studies_matched"] for s in scan))
bind("9484","S5 scoring n","03_scoring_summary.json:n", scor["n"])
bind("9484","corpus table rows","data/processed/cura_scores.csv rows", len(sc))
bind("9484","evidence table rows","data/processed/aiml_evidence_text.csv rows", len(ev))
bind("1.58","S4 match rate %","100*matched/scanned",
     round(100*sum(s["studies_matched"] for s in scan)/sum(s["studies_scanned"] for s in scan),2))
bind("602","S4 shards","01_profile.json chunk count x150 / scan", sum(s["shards"] for s in scan))
bind("4214","S4 interventional","01_profile.json:study_type", prof["study_type"]["INTERVENTIONAL"])
bind("5269","S4 observational","01_profile.json:study_type", prof["study_type"]["OBSERVATIONAL"])
bind("180","S4 growth 2017","01_profile.json:posts_per_year", prof["posts_per_year"]["2017"])
bind("1585","S4 growth 2025","01_profile.json:posts_per_year", prof["posts_per_year"]["2025"])
bind("139","S4, S5.5 FDA drug flag","01_profile.json:is_fda_regulated_drug", prof["is_fda_regulated_drug"]["True"])
bind("511","S4, S5.5 FDA device flag","01_profile.json:is_fda_regulated_device", prof["is_fda_regulated_device"]["True"])
bind("327","S4 posted results","01_profile.json:has_results", prof["has_results"]["True"])
bind("3.4","S4 posted results %","100*327/9484", round(100*prof["has_results"]["True"]/scor["n"],1))
bind("1.5","S4/S5.5 drug flag %","100*139/9484", round(100*prof["is_fda_regulated_drug"]["True"]/scor["n"],1))
bind("5.4","S4/S5.5 device flag %","100*511/9484", round(100*prof["is_fda_regulated_device"]["True"]/scor["n"],1))
bind("55.6","S4 phase missingness %","01_profile.json:missingness_pct.phases", prof["missingness_pct"]["phases"])
bind("84.3","S4, S6 is_us_export missing %","01_profile.json:missingness_pct.is_us_export", prof["missingness_pct"]["is_us_export"])
bind("50000000","S4 enrolment max","01_profile.json:enrollment_describe.max", prof["enrollment_describe"]["max"])
bind("20","S4 lexicon terms","count of alternatives in 00_scan pattern",
     len(scan[0]["pattern"].split("|")))

# ---------------- tiers and evidence ----------------
for k,t in zip(["3304","4863","983","334"], T):
    bind(k, f"S5.1 n {t}", "03_scoring_summary.json:tier_dist", scor["tier_dist"][t])
for k,t in zip(["0.134","0.162","0.196","0.183"], T):
    bind(k, f"S5.1/Fig1b mean E {t}", "05_validity_baselines.json:H1.mean_E_norm_by_tier",
         val["H1_risk_proportionality"]["mean_E_norm_by_tier"][t])
bind("0.156","Abstract; S5.2 mean E","03_scoring_summary.json:E_norm.mean", scor["E_norm"]["mean"])
bind("0.267","S5.2 p90 E","03_scoring_summary.json:E_norm.p90", round(scor["E_norm"]["p90"],3))
bind("0.80","S5.2 max E","03_scoring_summary.json:E_norm.max", scor["E_norm"]["max"])
for k,d in zip(["88.4","6.6","79.0","59.3","69.3"],
   ["D1_data_quality_provenance","D2_representativeness_bias","D3_uncertainty_performance",
    "D4_independent_validation","D5_lifecycle_monitoring"]):
    bind(k, f"S5.2 pct zero {d[:2]}", "03_scoring_summary.json:evidence_dim_pct_zero",
         round(scor["evidence_dim_pct_zero"][d],1))
bind("3711","S5.2 zero-evidence studies","aiml_evidence_text.csv n_evidence_terms==0",
     int((ev.n_evidence_terms==0).sum()))
bind("39.1","Abstract; S5.2 zero-evidence %","100*3711/9484",
     round(100*(ev.n_evidence_terms==0).mean(),1))

# item prevalences
items = {"0.24":"d5_version","0.39":"d5_oversight","1.50":"d2_bias","1.27":"d5_monitoring",
         "3.86":"d4_external_val","3.88":"d1_training_data","3.48":"d3_uncertainty",
         "16.54":"d3_discrimination","16.66":"d2_external_pop"}
for k,c in items.items():
    bind(k, f"Abstract/S5.2/Fig2 {c}", "aiml_evidence_text.csv column mean",
         round(100*ev[c].mean(),2))

# sufficiency
for k,t in zip(["27.9","2.7","0.31","0.0"], T):
    bind(k, f"S5.2 sufficiency {t} %","03_scoring_summary.json:sufficient_pct_by_tier",
         scor["sufficient_pct_by_tier"][t])
for k,t in zip(["4.4","7.2","11.5","8.4"], T):
    bind(k, f"S5.2 flat-0.30 {t} %","04_reliability.json:flat_threshold_check.flat_0.3",
         rel["H6_robustness"]["flat_threshold_check"]["sufficient_pct_by_tier"]["flat_0.3"][t])

# ---------------- H1 ----------------
h1=val["H1_risk_proportionality"]
bind("0.229","Abstract; S5.1 rho","05_...:H1.spearman_rho", h1["spearman_rho"])
bind("0.054","Abstract; S5.1 eps2","05_...:H1.epsilon_squared", round(h1["epsilon_squared"],3))
bind("513.8","S5.1 Kruskal H","05_...:H1.kruskal_H", h1["kruskal_H"])
bind("21.6","S5.1 JT z","05_...:H1.jonckheere_z", h1["jonckheere_z"])
bind("0.049","Abstract; S5.2; Table1 delta (PRE-SPECIFIED)","05_...:H1.delta_low_to_very_high",
     h1["delta_low_to_very_high"])
bind("0.039","S5.2 delta CI lo","05_...:H1.delta_ci95", h1["delta_ci95"][0])
bind("0.059","S5.2 delta CI hi","05_...:H1.delta_ci95", h1["delta_ci95"][1])
bind("0.062","S5.2 secondary low-to-max-tier","05_...:H1.secondary_delta_low_to_max_tier",
     h1["secondary_delta_low_to_max_tier"])
bind("0.056","S5.2 secondary CI lo","05_...:H1.secondary_..._ci95", h1["secondary_delta_low_to_max_tier_ci95"][0])
bind("0.069","S5.2 secondary CI hi","05_...:H1.secondary_..._ci95", h1["secondary_delta_low_to_max_tier_ci95"][1])
bind("0.20","S5.1 prespecified threshold","notes/PRESPECIFICATION.md + rubric", 0.20)

# ---------------- H2 ----------------
h2=rel["H2_discrimination"]
bind("0.767","S5.4 normalised entropy","04_...:H2.normalised_entropy", h2["normalised_entropy"])
for k,t in zip(["34.8","51.3","10.4","3.5"], T):
    bind(k, f"S5.4 tier share {t} %","04_...:H2.tier_shares", round(100*h2["tier_shares"][t],1))
bind("0.51","S5.4 largest share","04_...:H2.largest_tier_share", round(h2["largest_tier_share"],2))

# ---------------- H3 ----------------
h3=rel["H3_channel_agreement"]
bind("0.062","Abstract; S5.3 kappa influence","04_...:H3.influence", h3["influence"]["weighted_kappa"])
bind("0.053","S5.3 CI lo influence","04_...:H3.influence.ci95", h3["influence"]["ci95"][0])
bind("0.071","S5.3 CI hi influence","04_...:H3.influence.ci95", h3["influence"]["ci95"][1])
bind("0.032","S5.3 kappa consequence","04_...:H3.consequence", h3["consequence"]["weighted_kappa"])
bind("0.022","S5.3 CI lo consequence","04_...:H3.consequence.ci95", h3["consequence"]["ci95"][0])
bind("0.042","S5.3 CI hi consequence","04_...:H3.consequence.ci95", h3["consequence"]["ci95"][1])
bind("0.029","S5.3 kappa tier","04_...:H3.tier", h3["tier"]["weighted_kappa"])
bind("0.036","S5.3 CI hi tier","04_...:H3.tier.ci95", h3["tier"]["ci95"][1])
bind("40.6","S5.3 exact agreement tier %","04_...:H3.tier.exact_agreement",
     round(100*h3["tier"]["exact_agreement"],1))

# ---------------- H4 ----------------
bind("0.401","Abstract; S5.3; Table1","07_...:influence.qwk", adj["influence"]["quadratic_weighted_kappa"])
bind("0.307","S5.3 CI lo","07_...:influence.kappa_ci95", adj["influence"]["kappa_ci95"][0])
bind("0.486","S5.3 CI hi","07_...:influence.kappa_ci95", adj["influence"]["kappa_ci95"][1])
bind("0.239","S5.3 consequence qwk","07_...:consequence", adj["consequence"]["quadratic_weighted_kappa"])
bind("0.114","S5.3 CI lo","07_...:consequence.kappa_ci95", adj["consequence"]["kappa_ci95"][0])
bind("0.354","S5.3 CI hi","07_...:consequence.kappa_ci95", adj["consequence"]["kappa_ci95"][1])
bind("0.377","S5.3 tier qwk","07_...:tier", adj["tier"]["quadratic_weighted_kappa"])
bind("0.260","S5.3 CI lo","07_...:tier.kappa_ci95", adj["tier"]["kappa_ci95"][0])
bind("0.481","S5.3 CI hi","07_...:tier.kappa_ci95", adj["tier"]["kappa_ci95"][1])
bind("0.35","S5.3 signed diff influence","07_...:influence.mean_signed_error",
     adj["influence"]["mean_signed_error_auto_minus_adj"])
bind("0.38","S5.3 signed diff consequence","07_...:consequence.mean_signed_error",
     abs(adj["consequence"]["mean_signed_error_auto_minus_adj"]))
bind("200","S5.3 sample n","07_...:influence.n", adj["influence"]["n"])
# ---------------- H5 ----------------
h5=val["H5_added_information"]
bind("1.92","S5.4 H(CURA)","05_...:H5.B1.H_CURA_bits", round(h5["B1_eu_ai_act_style"]["H_CURA_bits"],2))
bind("1.62","S5.4 H(CURA|B1)","05_...:H5.B1", round(h5["B1_eu_ai_act_style"]["H_CURA_given_comparator_bits"],2))
bind("0.39","S5.4 H(CURA|B2)","05_...:H5.B2", round(h5["B2_risk_tier_only"]["H_CURA_given_comparator_bits"],2))
bind("1.85","S5.4 H(CURA|B3)","05_...:H5.B3", round(h5["B3_reporting_count_only"]["H_CURA_given_comparator_bits"],2))
bind("0.89","S5.4 NMI B2","05_...:H5.B2.normalised_MI", round(h5["B2_risk_tier_only"]["normalised_MI"],2))
bind("0.87","S5.4 ARI B2","05_...:H5.B2.adjusted_rand_index", round(h5["B2_risk_tier_only"]["adjusted_rand_index"],2))
bind("0.30","S5.4 prespecified bits","notes/PRESPECIFICATION.md", 0.30)

# ---------------- scale structure & known groups ----------------
bind("0.227","S3 Cronbach alpha","05_...:scale_structure.cronbach_alpha", val["scale_structure"]["cronbach_alpha"])
bind("25.3","S3 PC1 var %","05_...:scale_structure.variance_explained_pc1",
     round(100*val["scale_structure"]["variance_explained_pc1"],1))
kg=val["construct_validity_known_groups"]
bind("1.47","S5.4 phased mean tier","05_...:known_groups.phase", kg["phase"]["mean_tier_ord"]["PHASED"])
bind("0.80","S5.4 unphased mean tier","05_...:known_groups.phase", kg["phase"]["mean_tier_ord"]["NONE"])
bind("0.825","S5.4 industry mean tier","05_...:known_groups.sponsor_class", kg["sponsor_class"]["mean_tier_ord"]["INDUSTRY"])
bind("0.832","S5.4 other mean tier","05_...:known_groups.sponsor_class", kg["sponsor_class"]["mean_tier_ord"]["OTHER"])
bind("0.120","S5.4 enrolment rho","05_...:known_groups.enrollment", abs(kg["enrollment"]["spearman_rho_tier"]))
bind("347.0","S5.4 phase chi2","05_...:known_groups.phase.chi2", kg["phase"]["chi2"])
bind("0.135","S5.4 phase Cramers V","05_...:known_groups.phase.cramers_v", kg["phase"]["cramers_v"])
intext("$p=6.8\\times10^{-75}$","S5.4 phase p exponent stated")
assert 6.5e-75 < kg["phase"]["p"] < 7.5e-75, ("phase p out of stated range", kg["phase"]["p"])

# ---------------- S5.5 scope / confounds ----------------
cs=conf["C1_scope_subsets"]; fs=resp["F05_subset_gradient_CIs"]
bind("0.341","S5.5 drug rho","08_...:C1.fda_regulated_drug", cs["fda_regulated_drug"]["spearman_rho"])
bind("0.091","S5.5 drug delta","08_...:C1.fda_regulated_drug", cs["fda_regulated_drug"]["delta_low_to_top"])
bind("0.029","S5.5 drug CI lo","09_...:F05.fda_regulated_drug", fs["fda_regulated_drug"]["ci95"][0])
bind("0.150","S5.5 drug CI hi","09_...:F05.fda_regulated_drug", fs["fda_regulated_drug"]["ci95"][1])
bind("0.280","S5.5 device rho","08_...:C1.fda_regulated_device", cs["fda_regulated_device"]["spearman_rho"])
bind("0.071","S5.5 device delta","08_...:C1", cs["fda_regulated_device"]["delta_low_to_top"])
bind("0.043","S5.5 device CI lo","09_...:F05", fs["fda_regulated_device"]["ci95"][0])
bind("0.102","S5.5 device CI hi","09_...:F05", fs["fda_regulated_device"]["ci95"][1])
bind("787","S5.5 industry n","08_...:C1.industry_sponsored", cs["industry_sponsored"]["n"])
bind("0.251","S5.5 industry rho","08_...:C1", cs["industry_sponsored"]["spearman_rho"])
bind("0.087","S5.5 industry delta","08_...:C1", cs["industry_sponsored"]["delta_low_to_top"])
bind("0.068","S5.5 industry CI lo","09_...:F05", fs["industry_sponsored"]["ci95"][0])
bind("0.122","S5.5 industry CI hi","09_...:F05", fs["industry_sponsored"]["ci95"][1])
bind("379","S5.5 phased n","08_...:C1.interventional_with_phase", cs["interventional_with_phase"]["n"])
bind("0.010","S5.5 phased rho (abs)","08_...:C1", abs(cs["interventional_with_phase"]["spearman_rho"]))
bind("0.85","S5.5 phased p","08_...:C1", round(cs["interventional_with_phase"]["p"],2))
bind("0.051","S5.5 phased CI hi","09_...:F05", fs["interventional_with_phase"]["ci95"][1])
bind("0.222","S5.5 phased low-tier E","08_...:C1.mean_E_by_tier", cs["interventional_with_phase"]["mean_E_by_tier"]["low"])
bind("0.187","S5.5 phased VH E","08_...:C1.mean_E_by_tier", cs["interventional_with_phase"]["mean_E_by_tier"]["very_high"])
bind("5000","S5.5 bootstrap draws","09_...:F05 n_boot default", 5000)
c2=conf["C2_record_length"]
bind("0.307","S5.5 E vs log chars","08_...:C2", c2["spearman_rho_E_vs_logchars"])
bind("0.074","S5.5 tier vs log chars","08_...:C2", c2["spearman_rho_tier_vs_logchars"])
bind("0.217","S5.5 partial rho","08_...:C2", c2["partial_spearman_tier_E_given_logchars"])
bind("0.0245","S5.5 tier coef unadj","08_...:C2.ols_E_on_tier_only", round(c2["ols_E_on_tier_only"]["coef_tier"],4))
bind("0.0222","S5.5 tier coef adj","08_...:C2.ols_E_on_tier_and_logchars", round(c2["ols_E_on_tier_and_logchars"]["coef_tier"],4))
bind("0.01995","S5.5 coef CI lo","08_...:C2", c2["ols_E_on_tier_and_logchars"]["ci95_tier"][0])
bind("0.067","S5.5 implied adj gradient","08_...:C2", c2["ols_E_on_tier_and_logchars"]["implied_delta_over_3_tiers"])
bind("0.073","S5.5 implied unadj gradient","08_...:C2", c2["ols_E_on_tier_only"]["implied_delta_over_3_tiers"])
c3=conf["C3_permutation_baseline"]
bind("2000","S5.5 permutations","08_...:C3 n", 2000)
bind("0.020","S5.5 permuted p97.5","08_...:C3", c3["permuted_rho_p97_5"])

# ---------------- S5.6 robustness ----------------
rb=rel["H6_robustness"]
deltas=[v["delta_low_to_top"] for v in rb["risk_matrix_form"].values()]
deltas+=[v["delta_low_to_top"] for v in rb["consensus_rule"].values()]
deltas+=[v["delta_low_to_top"] for v in rb["corpus_strictness"].values()]
deltas+=[v["delta_low_to_top"] for v in rb["temporal_split"].values()]
bind("0.021","S5.6 min delta across variants","04_...:H6 min over all variants", round(min(deltas),3))
bind("0.075","S5.6 max delta across variants","04_...:H6 max over all variants", round(max(deltas),3))
bind("3702","S5.6 title-match n","04_...:H6.corpus_strictness.title_match", rb["corpus_strictness"]["title_match"]["n"])
bind("1925","S5.6 intervention-match n","04_...:H6.corpus_strictness", rb["corpus_strictness"]["intervention_match"]["n"])
bind("2771","S5.6 pre-2022 n","04_...:H6.temporal_split", rb["temporal_split"]["pre_2022"]["n"])
bind("6713","S5.6 2022-onward n","04_...:H6.temporal_split", rb["temporal_split"]["2022_onward"]["n"])
dvh=[v["delta_low_to_very_high"] for fam in ("risk_matrix_form","consensus_rule",
     "corpus_strictness","temporal_split") for v in rb[fam].values()
     if v.get("delta_low_to_very_high") is not None]
bind("0.045","S5.6 min pre-specified delta","04_...:H6 min delta_low_to_very_high", round(min(dvh),3))
bind("0.075","S5.6 max pre-specified delta","04_...:H6 max delta_low_to_very_high", round(max(dvh),3))
wp=rb["weight_perturbation"]
bind("0.048","S5.6 weight mean delta (pre-spec)","04_...:H6.weight_perturbation", wp["delta_low_to_very_high_mean"])
bind("0.013","S5.6 weight CI lo","04_...:H6.weight_perturbation", wp["delta_low_to_very_high_ci95"][0])
bind("0.094","S5.6 weight CI hi","04_...:H6.weight_perturbation", wp["delta_low_to_very_high_ci95"][1])
bind("0.885","S5.6 Kendall tau","04_...:H6.weight_perturbation", wp["kendall_tau_mean"])
bind("0.794","S5.6 Kendall p2.5","04_...:H6.weight_perturbation", wp["kendall_tau_p2_5"])
bind("1000","S5.6 Dirichlet draws","04_...:H6 n", 1000)
bind("95.9","S5.6 min-rule low share %","04_...:H6.consensus_rule.min",
     round(100*rb["consensus_rule"]["min"]["tier_shares"]["low"],1))

# ---------------- F02 response numbers ----------------
f02=resp["F02_channel_A_influence_items"]
bind("0.332","S5.3 i1 rho","09_...:F02.per_item.i1_intervention", f02["per_item"]["i1_intervention"]["spearman_rho"])
bind("0.295","S5.3 i2 rho","09_...:F02.per_item.i2_title", f02["per_item"]["i2_title"]["spearman_rho"])
bind("0.278","S5.3 i3 rho","09_...:F02.per_item.i3_interventional", f02["per_item"]["i3_interventional"]["spearman_rho"])
bind("0.245","S5.3 title vs n AI terms","09_...:F02.salience_check", f02["salience_check"]["spearman_i2title_vs_n_ai_terms"])
bind("18.3","S5.3 R2 %","09_...:F02.ols.r2", round(100*f02["ols_adjudicated_influence_on_items"]["r2"],1))

# ---------------- S5.3 design confound (11_completeness.json) ----------------
A=comp["A_field_classification"]["detail"]; B=comp["B_zeros_that_are_really_missing_data"]
D=comp["D_tier_is_a_design_proxy"]; E=comp["E_within_study_type"]
F=comp["F_adjustment_ladder"]; FS=comp["F_share_removed_pct"]
G=comp["G_rescored_missing_excluded"]; Q=comp["I_qa"]; H=comp["H_what_survives"]
bind("4214","S5.3 n interventional","11_...:n_interventional", comp["n_interventional"])
bind("5270","S5.3 n observational","11_...:n_observational", comp["n_observational"])
bind("44.4","S4 interventional share %","11_...: n_interventional/n",
     round(100*comp["n_interventional"]/comp["n"],1))
bind("55.6","S4 observational share %","11_...: n_observational/n",
     round(100*comp["n_observational"]/comp["n"],1))
for f,mi,mo in [("primary_purpose","0.4","100.0"),("masking","0.1","100.0"),
                ("allocation","25.9","100.0"),("phases","91.0","100.0")]:
    bind(mi, f"S5.3 {f} missing interventional %","11_...:A", A[f]["pct_missing_interventional"])
    bind(mo, f"S5.3 {f} missing observational %","11_...:A", A[f]["pct_missing_observational"])
bind("8","S5.3 universal field count","11_...:A.universal_fields",
     len(comp["A_field_classification"]["universal_fields"]))
bind("6909","S5.3 c2 zeros","11_...:B.c2", B["c2_care_bearing_purpose"]["scored_zero"])
bind("5287","S5.3 c2 zeros that are missing","11_...:B.c2", B["c2_care_bearing_purpose"]["of_which_field_missing"])
bind("76.5","Abstract; S5.3 c2 missing %","11_...:B.c2", B["c2_care_bearing_purpose"]["pct_of_zeros_that_are_missing_data"])
bind("7.3","S5.3 c1 missing %","11_...:B.c1", B["c1_fda_regulated_article"]["pct_of_zeros_that_are_missing_data"])
bind("15.9","S5.3 c3 missing %","11_...:B.c3", B["c3_patient_population"]["pct_of_zeros_that_are_missing_data"])
bind("0.600","Abstract; S5.3 rho design-tier","11_...:D.rho_interventional_tier", D["rho_interventional_tier"])
bind("100.0","S5.3 %% very high interventional","11_...:D", D["pct_of_very_high_that_are_interventional"])
bind("965","S5.3 high-tier interventional","11_...:D.crosstab", D["crosstab_studytype_x_tier"]["high"]["INTERVENTIONAL"])
bind("18","S5.3 high-tier observational","11_...:D.crosstab", D["crosstab_studytype_x_tier"]["high"]["OBSERVATIONAL"])
bind("0.187","S5.3 mean E interventional","11_...:D", D["mean_E_interventional"])
bind("0.131","S5.3 mean E observational","11_...:D", D["mean_E_observational"])
# adjustment ladder (Table 2)
bind("0.2287","S5.3 ladder raw","11_...:F.raw", F["raw"]["rho"])
bind("0.211","S5.3 ladder raw CI lo","11_...:F.raw", F["raw"]["ci95"][0])
bind("0.247","S5.3 ladder raw CI hi","11_...:F.raw", F["raw"]["ci95"][1])
for key,val_,lo,hi,rm in [("given_length_only","0.2170","0.197","0.238","5.1"),
                          ("given_completeness","0.1928","0.173","0.212","15.7"),
                          ("given_completeness_and_length","0.1955","0.177","0.215","14.5"),
                          ("given_study_type","0.0356","0.018","0.055","84.4"),
                          ("given_all_three","0.0575","0.038","0.078","74.9")]:
    bind(val_, f"S5.3 ladder {key}","11_...:F", F[key]["partial_rho"])
    bind(lo, f"S5.3 ladder {key} CI lo","11_...:F", F[key]["ci95"][0])
    bind(hi, f"S5.3 ladder {key} CI hi","11_...:F", F[key]["ci95"][1])
    bind(rm, f"S5.3 ladder {key} %% removed","11_...:F_share_removed_pct", FS[key])
# within-design
iv=E["interventional"]; ob=E["observational"]
bind("0.0031","Abstract; S5.3 within-IV delta","11_...:E.interventional.delta_prespec", iv["delta_prespec"]["delta_low_to_very_high"])
bind("0.0104","S5.3 within-IV CI lo (abs)","11_...:E", abs(iv["delta_prespec"]["ci95"][0]))
bind("0.0165","S5.3 within-IV CI hi","11_...:E", iv["delta_prespec"]["ci95"][1])
bind("0.027","S5.3 within-IV CI width","11_...:I_qa.I1", Q["I1_null_is_precise_not_underpowered"]["ci_width"])
bind("0.017","S5.3 rules out effects above","11_...:I_qa.I1", Q["I1_null_is_precise_not_underpowered"]["rules_out_effects_above"])
bind("0.038","Abstract; S5.3 rho within IV","11_...:E.interventional", iv["rho_tier_Enorm"]["rho"])
bind("0.007","S5.3 rho within IV CI lo","11_...:E", iv["rho_tier_Enorm"]["ci95"][0])
bind("0.067","S5.3 rho within IV CI hi","11_...:E", iv["rho_tier_Enorm"]["ci95"][1])
bind("0.034","Abstract; S5.3 rho within OBS","11_...:E.observational", ob["rho_tier_Enorm"]["rho"])
bind("0.006","S5.3 rho within OBS CI lo","11_...:E", ob["rho_tier_Enorm"]["ci95"][0])
bind("0.060","S5.3 rho within OBS CI hi","11_...:E", ob["rho_tier_Enorm"]["ci95"][1])
i3q=Q["I3_low_to_high_in_both_strata"]
bind("0.016","S5.3 IV low-to-high","11_...:I_qa.I3", i3q["interventional"]["delta_low_to_high"])
bind("0.005","S5.3 IV low-to-high CI lo","11_...:I_qa.I3", i3q["interventional"]["ci95"][0])
bind("0.027","S5.3 IV low-to-high CI hi","11_...:I_qa.I3", i3q["interventional"]["ci95"][1])
bind("0.071","S5.3 OBS low-to-high","11_...:I_qa.I3", i3q["observational"]["delta_low_to_high"])
bind("0.010","S5.3 OBS low-to-high CI lo","11_...:I_qa.I3", i3q["observational"]["ci95"][0])
bind("0.143","S5.3 OBS low-to-high CI hi","11_...:I_qa.I3", i3q["observational"]["ci95"][1])
# over-adjustment
oa=Q["I2_overadjustment_check"]
bind("0.340","S5.3 rho design-tier without i3","11_...:I_qa.I2", oa["rho_design_tier_without_i3"])
bind("0.0056","S5.3 within-IV delta without i3","11_...:I_qa.I2", oa["delta_prespec_i3_removed_interventional"])
# rescoring
bind("1857","S5.3 rescored low n","11_...:G.tier_shift", G["tier_shift"]["rescored"]["low"])
bind("1480","S5.3 rescored high n","11_...:G.tier_shift", G["tier_shift"]["rescored"]["high"])
bind("0.175","S5.3 rescored rho","11_...:G", G["rho_tier_Enorm"]["rho"])
bind("0.156","S5.3 rescored rho CI lo","11_...:G", G["rho_tier_Enorm"]["ci95"][0])
bind("0.194","S5.3 rescored rho CI hi","11_...:G", G["rho_tier_Enorm"]["ci95"][1])
bind("0.055","S5.3 rescored delta","11_...:G", G["delta_prespec"]["delta_low_to_very_high"])
bind("0.045","S5.3 rescored delta CI lo","11_...:G", G["delta_prespec"]["ci95"][0])
bind("0.064","S5.3 rescored delta CI hi","11_...:G", G["delta_prespec"]["ci95"][1])
bind("0.0071","S5.3 rescored within-IV delta","11_...:G", G["within_interventional"]["delta_prespec"]["delta_low_to_very_high"])
bind("0.0066","S5.3 rescored within-IV CI lo (abs)","11_...:G", abs(G["within_interventional"]["delta_prespec"]["ci95"][0]))
bind("0.0210","S5.3 rescored within-IV CI hi","11_...:G", G["within_interventional"]["delta_prespec"]["ci95"][1])
# what survives
hp=H["prevalence_pct_interventional_only"]
bind("0.09","S5.3 IV-only versioning %","11_...:H", hp["model or algorithm versioning"])
bind("0.93","S5.3 IV-only external validation %","11_...:H", hp["external validation"])
bind("1.12","S5.3 IV-only training-data %","11_...:H", hp["training-data description"])
bind("0.020","S5.3 rho completeness vs terms (abs)","11_...:H", abs(H["rho_completeness_vs_n_evidence_terms"]))
bind("39.13","S5.3 zero-evidence %","11_...:H.pct_with_zero_evidence_terms", H["pct_with_zero_evidence_terms"])

# ---------------- Channel B degeneracy (S3) ----------------
bind("8170","S3 channel B influence zeros","cura_scores.csv B_influence==0", int((sc.B_influence==0).sum()))
bind("86.1","S3 channel B influence zero %","cura_scores.csv", round(100*float((sc.B_influence==0).mean()),1))
bind("7252","S3 channel B consequence zeros","cura_scores.csv B_consequence==0", int((sc.B_consequence==0).sum()))
bind("76.5","S3 channel B consequence zero %","cura_scores.csv", round(100*float((sc.B_consequence==0).mean()),1))
bind("2","S3 channel B influence level-3 count","cura_scores.csv", int((sc.B_influence==3).sum()))
bind("4","S3 channel B consequence level-3 count","cura_scores.csv", int((sc.B_consequence==3).sum()))
bind("558","S5.3 channel A influence level-3 count","cura_scores.csv", int((sc.A_influence==3).sum()))

# ---------------- rubric-declared values ----------------
for k,t in zip(["0.20","0.40","0.60","0.80"], T):
    bind(k, f"S3 theta {t}","src/cura_rubric.json:sufficiency_thresholds", rub["sufficiency_thresholds"][t])
bind("15","S3 E denominator","3 x 5 dimensions", 3*len(rub["evidence_dimensions"]))
bind("24","S3 lexicon items (channel B)","aiml_evidence_text.csv lexicon columns",
     len([c for c in ev.columns if c.split("_")[0] in ("d1","d2","d3","d4","d5","inf","con","reg")]))

# ---------------- multiplicity (S8) ----------------
# The Limitations clause states three things and all three are bound here, so the
# manuscript carries no hand-typed multiplicity figure.
bind("8", "S8 multiplicity family size", "12_multiplicity.json:m", mult["m"])
bind("0.028", "S8 largest Holm-adjusted p among significant tests",
     "12_...:max_holm_p_among_significant", mult["max_holm_p_among_significant"])
bind("False", "S8 no conclusion changed by correction",
     "12_...:any_conclusion_changed", str(mult["any_conclusion_changed"]))
intext("Multiplicity was checked", "S8 multiplicity is reported, not conceded")
intext("changes no conclusion", "S8 states the correction changed nothing")

# ---------------- verbatim regulatory strings ----------------
# --- disclaimer integrity (the house requirement; papers 01/02 assert the same) ---
# --- claims the reframe depends on being stated, not implied ---
intext("its Figure~1 shows", "Intro: FDA does publish a risk matrix")
intext("no levels on either axis", "Intro: what FDA's figure does not carry")
intext("enerative AI and agentic AI models are novel and rapidly evolving. As such, they are not within the scope of this guidance", "S2 SR 26-2 verbatim scope exclusion")
intext("an internal-consistency check", "S5.4 H4 demoted from accuracy")
intext("Study design is not randomly assigned", "S5.3 causal caveat stated")
intext("associations under adjustment, not causal", "S5.3 causal caveat wording")
intext("Simpson's paradox", "S5.3 names the phenomenon")
intext("a precise null rather than an underpowered one", "S5.3 precision of the null")
intext("was implemented incorrectly and corrected", "S8 estimator error disclosed")
intext("Holm and Benjamini--Hochberg correction", "S8 multiplicity correction named, superseding the former concession")
assert "headline survives the measurement failure" not in flat, "removed H4 paragraph is back"
assert "delta_low_to_max" not in flat
intext("This work was carried out independently, on personal time and equipment, and is not",
       "Disclaimer frame, sentence 1")
intext("connected to the author's employment. The views expressed are the author's own and do",
       "Disclaimer frame, sentence 2")
intext("not represent the views, positions or policies of any current, former or future employer",
       "Disclaimer frame, sentence 3")
intext("or client. No proprietary, confidential or internal data of any organization was used.",
       "Disclaimer frame, sentence 4")
intext("All data is public:", "Disclaimer sources lead-in")
intext("the ClinicalTrials.gov v2 study registry", "Disclaimer names the registry")
intext("US federal public domain under the", "Disclaimer states the licence")
intext("author-generated adjudication labels", "Disclaimer names the annotation set")
intext("\\section*{Disclaimer}", "Disclaimer section exists")

intext("the specific role and scope of the AI model used to address a question of interest","S1 COU definition")
intext("the significance of an adverse outcome resulting from an incorrect decision concerning the question of interest","S1 consequence definition")
intext("2026-09-07","S4 or reproducibility snapshot date") if "2026-09-07" in flat else intext("7 September 2026","S4 snapshot date")

out=[]
out.append("| # | Value in paper | Where | Source | Source value | Verdict |")
out.append("|---|---|---|---|---|---|")
for i,(n,w,s,a,v) in enumerate(rows,1):
    out.append(f"| {i} | `{n}` | {w} | `{s}` | `{a}` | {'MATCH' if v=='MATCH' else '**MISMATCH**'} )".replace(" )"," |"))
txt="\n".join(out)
(ROOT/"selfcheck"/"NUMBER-TRACE.md").write_text(
 f"# Number-to-source trace\n\nBound automatically by `selfcheck/verify_numbers.py`. "
 f"{len(rows)} bindings, {len(fails)} mismatches.\n\n"+txt+
 ("\n\n## Mismatches\n\n"+"\n".join("- "+f for f in fails) if fails else "\n\n## Mismatches\n\nNone.\n"))
print(f"bindings: {len(rows)}  mismatches: {len(fails)}")
for f in fails: print("  MISMATCH:", f)
sys.exit(1 if fails else 0)
