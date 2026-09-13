"""Scan the ClinicalTrials.gov snapshot for studies that describe an AI/ML
component, and emit a flat table of the structured fields we can audit.

Input : Papers/_shared/clinicaltrials/studies_*.json  (v2 API shards)
Output: data/processed/aiml_studies.csv, results/00_scan_summary.json

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, re, sys, csv, os, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARDS = sorted((ROOT.parents[0] / "_shared" / "clinicaltrials").glob("studies_*.json"))

# Terms must appear as whole words / phrases. Deliberately narrow: "AI" alone
# is excluded (too many false positives from chemistry and abbreviations).
POS = re.compile(
    r"\b(artificial intelligence|machine learning|deep learning|neural network"
    r"|convolutional neural|recurrent neural|random forest|gradient boosting"
    r"|support vector machine|natural language processing|large language model"
    r"|computer[- ]aided detection|computer[- ]aided diagnosis|radiomics"
    r"|predictive algorithm|prediction model|clinical decision support"
    r"|reinforcement learning|transformer model|foundation model)\b", re.I)

FIELDS = ["nct_id","brief_title","overall_status","study_type","phases","allocation",
          "masking","primary_purpose","intervention_model","enrollment","enrollment_type",
          "start_date","completion_date","first_post_date","last_update_date",
          "lead_sponsor","sponsor_class","n_conditions","conditions","intervention_types",
          "n_locations","countries","has_results","has_dmc","is_fda_regulated_drug",
          "is_fda_regulated_device","is_us_export","oversight_has_dmc","n_references",
          "n_result_refs","text_len","matched_terms","match_in_title","match_in_intervention",
          "n_primary_outcomes","n_secondary_outcomes","healthy_volunteers","min_age","sex"]

def g(d,*ks,default=None):
    for k in ks:
        if not isinstance(d,dict): return default
        d = d.get(k)
        if d is None: return default
    return d

def row(s):
    ps = s.get("protocolSection",{})
    idm=ps.get("identificationModule",{}); st=ps.get("statusModule",{})
    dm=ps.get("designModule",{}); di=dm.get("designInfo",{}) or {}
    sp=ps.get("sponsorCollaboratorsModule",{}); cm=ps.get("conditionsModule",{})
    ai=ps.get("armsInterventionsModule",{}); ov=ps.get("oversightModule",{}) or {}
    cl=ps.get("contactsLocationsModule",{}) or {}
    om=ps.get("outcomesModule",{}) or {}
    de=ps.get("descriptionModule",{}) or {}
    el=ps.get("eligibilityModule",{}) or {}
    ivs=ai.get("interventions",[]) or []
    title=" ".join(filter(None,[idm.get("briefTitle"),idm.get("officialTitle")]))
    ivtext=" ".join(filter(None,[ (i.get("name") or "")+" "+(i.get("description") or "") for i in ivs]))
    blob=" ".join(filter(None,[title, de.get("briefSummary"), de.get("detailedDescription"),
                               " ".join(cm.get("keywords") or []), ivtext]))
    m=POS.findall(blob)
    if not m: return None
    locs=cl.get("locations") or []
    return {
      "nct_id": idm.get("nctId"),
      "brief_title": (idm.get("briefTitle") or "").replace("\n"," ")[:300],
      "overall_status": st.get("overallStatus"),
      "study_type": dm.get("studyType"),
      "phases": "|".join(dm.get("phases") or []),
      "allocation": di.get("allocation"),
      "masking": g(di,"maskingInfo","masking"),
      "primary_purpose": di.get("primaryPurpose"),
      "intervention_model": di.get("interventionModel"),
      "enrollment": g(dm,"enrollmentInfo","count"),
      "enrollment_type": g(dm,"enrollmentInfo","type"),
      "start_date": g(st,"startDateStruct","date"),
      "completion_date": g(st,"completionDateStruct","date"),
      "first_post_date": g(st,"studyFirstPostDateStruct","date"),
      "last_update_date": g(st,"lastUpdatePostDateStruct","date"),
      "lead_sponsor": g(sp,"leadSponsor","name"),
      "sponsor_class": g(sp,"leadSponsor","class"),
      "n_conditions": len(cm.get("conditions") or []),
      "conditions": "|".join((cm.get("conditions") or [])[:6]),
      "intervention_types": "|".join(sorted({i.get("type","") for i in ivs})),
      "n_locations": len(locs),
      "countries": "|".join(sorted({l.get("country","") for l in locs})[:8]),
      "has_results": s.get("hasResults"),
      "has_dmc": ov.get("oversightHasDmc"),
      "is_fda_regulated_drug": ov.get("isFdaRegulatedDrug"),
      "is_fda_regulated_device": ov.get("isFdaRegulatedDevice"),
      "is_us_export": ov.get("isUsExport"),
      "oversight_has_dmc": ov.get("oversightHasDmc"),
      "n_references": len((ps.get("referencesModule",{}) or {}).get("references") or []),
      "n_result_refs": sum(1 for r in ((ps.get("referencesModule",{}) or {}).get("references") or [])
                           if r.get("type")=="RESULT"),
      "text_len": len(blob),
      "matched_terms": "|".join(sorted({t.lower() for t in m})),
      "match_in_title": bool(POS.search(title)),
      "match_in_intervention": bool(POS.search(ivtext)),
      "n_primary_outcomes": len(om.get("primaryOutcomes") or []),
      "n_secondary_outcomes": len(om.get("secondaryOutcomes") or []),
      "healthy_volunteers": el.get("healthyVolunteers"),
      "min_age": el.get("minimumAge"),
      "sex": el.get("sex"),
    }

def main():
    a=int(sys.argv[1]); b=int(sys.argv[2])
    shards = SHARDS[a:b]
    out = ROOT/"data"/"processed"/f"chunks/aiml_{a:04d}_{b:04d}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    total=0; kept=0; shards_done=0
    with out.open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for sh in shards:
            try:
                d=json.loads(sh.read_text(encoding="utf-8"))
            except Exception as e:
                print("skip", sh.name, e, file=sys.stderr); continue
            shards_done+=1
            for s in d.get("studies",[]):
                total+=1
                r=row(s)
                if r: w.writerow(r); kept+=1
            if shards_done % 50 == 0:
                print(f"  {shards_done} shards, {total} studies, {kept} matched", flush=True)
    summ={"shards":shards_done,"studies_scanned":total,"studies_matched":kept,
          "match_rate":round(kept/total,5) if total else None,
          "pattern":POS.pattern}
    (ROOT/"results").mkdir(exist_ok=True)
    (ROOT/"results"/f"00_scan_summary_{a:04d}_{b:04d}.json").write_text(json.dumps(summ,indent=2))
    print(json.dumps(summ,indent=2))

if __name__=="__main__":
    main()
