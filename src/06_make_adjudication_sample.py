"""Draw a stratified random sample for blind adjudication (H4).
Emits data/processed/adjudication_sample.csv WITHOUT any automated score, so the
annotator works only from the study's own registered text and the rubric anchors.

Independent work. Carried out on personal time and equipment, not connected to the
author's employment, using only public data. No proprietary, confidential or internal
data of any organization was used. See the Disclaimer in main.tex.
"""
import json, numpy as np, pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(20260907)
sc=pd.read_csv(ROOT/"data/processed/cura_scores.csv",low_memory=False)
tx=pd.read_csv(ROOT/"data/processed/aiml_evidence_text.csv",usecols=["nct_id","text_snapshot"])
d=sc.merge(tx,on="nct_id")
parts=[]
for t in ["low","moderate","high","very_high"]:
    s=d[d.tier==t]
    parts.append(s.sample(n=50,random_state=int(rng.integers(1e6))))
smp=pd.concat(parts).sample(frac=1,random_state=7).reset_index(drop=True)
smp["snippet"]=smp.text_snapshot.fillna("").str.slice(0,620)
# blind file for the annotator
smp[["nct_id","snippet"]].to_csv(ROOT/"data/processed/adjudication_sample.csv",index=False)
# sealed key, not read until after adjudication is written
smp[["nct_id","tier","influence","consequence","A_influence","A_consequence",
     "B_influence","B_consequence","E_norm"]].to_csv(ROOT/"data/processed/adjudication_key.csv",index=False)
print("sample n =",len(smp),"strata:",smp.tier.value_counts().to_dict())
