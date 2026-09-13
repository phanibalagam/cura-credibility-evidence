"""Merge chunk CSVs into one corpus and profile it (row counts, date ranges,
missingness, obvious quality problems). Outputs results/01_profile.json + .md

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, glob
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
fs=sorted((ROOT/"data"/"processed"/"chunks").glob("aiml_*.csv"))
df=pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[""]) for f in fs], ignore_index=True)
assert df.nct_id.is_unique, "duplicate NCT ids"
df.to_csv(ROOT/"data"/"processed"/"aiml_studies.csv", index=False)

def yr(s):
    return pd.to_datetime(s, errors="coerce", format="mixed")
df["_start"]=yr(df.start_date); df["_post"]=yr(df.first_post_date)
prof={
 "n_rows": int(len(df)), "n_unique_nct": int(df.nct_id.nunique()),
 "chunk_files":[f.name for f in fs],
 "first_post_date_range":[str(df._post.min().date()), str(df._post.max().date())],
 "start_date_range":[str(df._start.min().date()), str(df._start.max().date())],
 "missingness_pct": {c: round(100*df[c].isna().mean(),2) for c in df.columns if not c.startswith("_")},
 "study_type": df.study_type.value_counts(dropna=False).to_dict(),
 "overall_status": df.overall_status.value_counts(dropna=False).head(12).to_dict(),
 "phases": df.phases.value_counts(dropna=False).head(12).to_dict(),
 "sponsor_class": df.sponsor_class.value_counts(dropna=False).to_dict(),
 "primary_purpose": df.primary_purpose.value_counts(dropna=False).head(12).to_dict(),
 "is_fda_regulated_drug": df.is_fda_regulated_drug.value_counts(dropna=False).to_dict(),
 "is_fda_regulated_device": df.is_fda_regulated_device.value_counts(dropna=False).to_dict(),
 "has_results": df.has_results.value_counts(dropna=False).to_dict(),
 "has_dmc": df.has_dmc.value_counts(dropna=False).to_dict(),
 "match_in_title": df.match_in_title.value_counts(dropna=False).to_dict(),
 "match_in_intervention": df.match_in_intervention.value_counts(dropna=False).to_dict(),
 "top_matched_terms": pd.Series([t for s in df.matched_terms.dropna() for t in s.split("|")]).value_counts().head(20).to_dict(),
 "posts_per_year": df._post.dt.year.value_counts().sort_index().to_dict(),
 "enrollment_describe": pd.to_numeric(df.enrollment, errors="coerce").describe().round(2).to_dict(),
}
(ROOT/"results").mkdir(exist_ok=True)
(ROOT/"results"/"01_profile.json").write_text(json.dumps(prof, indent=2, default=str))
print(json.dumps({k:v for k,v in prof.items() if k not in ("missingness_pct","posts_per_year")}, indent=2, default=str))
print("\nMISSINGNESS >0:"); print({k:v for k,v in prof["missingness_pct"].items() if v>0})
print("\nPOSTS/YEAR:", prof["posts_per_year"])
