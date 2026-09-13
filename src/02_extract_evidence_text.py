"""Second pass over the registry shards. For the 9,484 matched studies only,
mine the free text for statements that would constitute auditable credibility
evidence about the AI model, and keep a truncated text snapshot for adjudication.

Channel B of the two-channel measurement design. Channel A (structured metadata)
comes from 00_scan_corpus.py.

Usage: python 02_extract_evidence_text.py <shard_start> <shard_end>

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, re, sys, csv
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SHARDS = sorted((ROOT.parents[0] / "_shared" / "clinicaltrials").glob("studies_*.json"))
KEEP = set(pd.read_csv(ROOT/"data"/"processed"/"aiml_studies.csv", usecols=["nct_id"]).nct_id)

# Evidence-term lexicon. Each key is a rubric item; the regex is what a reader
# would have to see in the public record to credit that item at all. These are
# deliberately generous — a mention counts, even without any detail — so the
# resulting prevalences are UPPER BOUNDS on observable evidence.
LEX = {
 # D1 data quality & provenance
 "d1_training_data":   r"\b(training (set|data|cohort|dataset)|training and (test|validation)|derivation cohort|development (set|cohort|dataset))\b",
 "d1_data_source":     r"\b(electronic health record|EHR|registry data|claims data|imaging database|data warehouse|curated dataset|public dataset)\b",
 "d1_data_quality":    r"\b(data quality|data curation|data cleaning|missing data (handling|imputation)|imputation|annotation protocol|ground truth label)\b",
 # D2 representativeness & bias
 "d2_external_pop":    r"\b(external (cohort|population|site|centre|center)|multi-?(centre|center)|multi-?site|geographic(ally)? (diverse|external))\b",
 "d2_subgroup":        r"\b(subgroup analys[ei]s|stratified by (age|sex|race|ethnicity)|demographic (subgroup|parity)|by race|by ethnicity)\b",
 "d2_bias":            r"\b(algorithmic bias|model bias|fairness|equit(y|able) (of|in) (the )?(model|algorithm)|bias (audit|assessment|mitigation)|disparit(y|ies))\b",
 # D3 uncertainty & performance characterisation
 "d3_discrimination":  r"\b(AUC|AUROC|area under the (receiver|curve)|c-statistic|c-index|sensitivity and specificity|F1[ -]score|precision and recall)\b",
 "d3_calibration":     r"\b(calibrat(ion|ed)|Brier score|Hosmer-?Lemeshow|calibration (curve|plot|slope))\b",
 "d3_uncertainty":     r"\b(uncertaint(y|ies)|confidence interval|credible interval|prediction interval|conformal prediction|predictive uncertainty)\b",
 # D4 independent validation
 "d4_external_val":    r"\b(external(ly)? validat(e|ed|ion)|independent (validation|test set|cohort)|held-?out (set|cohort|data)|temporal validation|out-of-sample)\b",
 "d4_prospective":     r"\b(prospective(ly)? (validat|evaluat|test)|prospective cohort|prospective study of the (model|algorithm))\b",
 "d4_comparator":      r"\b(compared (with|to) (standard of care|clinicians?|radiologists?|usual care|conventional)|versus (standard|usual) care|non-?inferiority|superiority)\b",
 "d4_prereg_analysis": r"\b(pre-?specified (analysis|endpoint|primary outcome)|statistical analysis plan|sample size calculation|power(ed)? to detect)\b",
 # D5 lifecycle monitoring & change control
 "d5_monitoring":      r"\b(model (monitoring|drift|degradation|update|retrain)|performance monitoring|post-?deployment|continuous (monitoring|learning)|drift detection)\b",
 "d5_version":         r"\b(model version|algorithm version|locked (algorithm|model)|frozen (model|weights)|version control)\b",
 "d5_oversight":       r"\b(human[- ]in[- ]the[- ]loop|clinician (review|oversight|override)|human oversight|override the (model|algorithm)|final decision rests)\b",
 # influence / autonomy cues
 "inf_autonomous":     r"\b(autonomous(ly)?|without (clinician|physician|human) (input|review|intervention)|fully automated (diagnosis|decision|triage))\b",
 "inf_assistive":      r"\b(decision support|assist(ive|ing)? (the )?(clinician|physician|radiologist)|second reader|aid(e)?s? (diagnosis|interpretation)|recommendation to the (clinician|physician))\b",
 "inf_sole_basis":     r"\b(based solely on the (model|algorithm)|algorithm[- ]determined|model[- ]guided (therapy|dosing|treatment)|AI[- ]driven (allocation|randomi[sz]ation))\b",
 # consequence cues
 "con_treatment":      r"\b(treatment (decision|selection|allocation)|dos(e|ing) (adjustment|selection|titration)|therap(y|eutic) decision|withhold(ing)? treatment)\b",
 "con_safety":         r"\b(patient safety|adverse event (detection|prediction)|mortality|deterioration|sepsis|life-?threatening|serious adverse)\b",
 "con_triage":         r"\b(triage|prioriti[sz]ation of (patients|cases)|screening decision|referral decision|rule[- ]out)\b",
 # regulatory framing
 "reg_submission":     r"\b(regulatory submission|FDA (clearance|approval|submission)|CE[- ]mark|510\(k\)|De Novo|premarket|marketing authori[sz]ation)\b",
 "reg_gxp":            r"\b(GCP|good clinical practice|21 CFR Part 11|GxP|computeri[sz]ed system validation|audit trail)\b",
}
LEXC = {k: re.compile(v, re.I) for k, v in LEX.items()}
FIELDS = ["nct_id"] + list(LEX) + ["n_evidence_terms", "text_chars", "text_snapshot"]

def blob(s):
    ps = s.get("protocolSection", {})
    de = ps.get("descriptionModule", {}) or {}
    idm = ps.get("identificationModule", {}) or {}
    cm = ps.get("conditionsModule", {}) or {}
    ai = ps.get("armsInterventionsModule", {}) or {}
    om = ps.get("outcomesModule", {}) or {}
    parts = [idm.get("briefTitle"), idm.get("officialTitle"),
             de.get("briefSummary"), de.get("detailedDescription"),
             " ".join(cm.get("keywords") or [])]
    parts += [(i.get("name") or "") + " " + (i.get("description") or "")
              for i in (ai.get("interventions") or [])]
    parts += [(o.get("measure") or "") + " " + (o.get("description") or "")
              for o in (om.get("primaryOutcomes") or []) + (om.get("secondaryOutcomes") or [])]
    return " ".join(p for p in parts if p)

def main():
    a, b = int(sys.argv[1]), int(sys.argv[2])
    out = ROOT/"data"/"processed"/"chunks_text"/f"ev_{a:04d}_{b:04d}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for sh in SHARDS[a:b]:
            d = json.loads(sh.read_text(encoding="utf-8"))
            for s in d.get("studies", []):
                nct = (s.get("protocolSection", {}).get("identificationModule", {}) or {}).get("nctId")
                if nct not in KEEP:
                    continue
                t = blob(s)
                r = {"nct_id": nct, "text_chars": len(t),
                     "text_snapshot": t[:6000].replace("\r", " ").replace("\n", " ")}
                hits = 0
                for k, rx in LEXC.items():
                    v = bool(rx.search(t)); r[k] = v; hits += v
                r["n_evidence_terms"] = hits
                w.writerow(r); n += 1
    print(f"{a}-{b}: wrote {n} rows -> {out.name}")

if __name__ == "__main__":
    main()
