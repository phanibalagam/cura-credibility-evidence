# Phase 1 — Grounding report (paper 03)

## 1. What the workbook asks for

Row 3 of `Data_ML_AI_Pharma_Research_Ideas.xlsx`, sheet **Research Ideas**:

| Field | Value |
|---|---|
| Title | Context-of-Use and Model-Risk Framework for AI Across Drug Development |
| Area | Regulatory science / AI governance |
| Research question | How can FDA context-of-use and model-risk principles be converted into an auditable AI credibility score? |
| Method | Framework design, Delphi/expert review, case-study benchmarking |
| Data | FDA and EMA guidance; published AI case studies |
| Claimed contribution | A reusable scoring rubric for data quality, bias, uncertainty, validation and monitoring |
| Validation | Inter-rater reliability; construct validity; case discrimination |
| Novelty / Impact / Feasibility | High / Medium / High |
| Note | "Strong thought-leadership topic; must add an original validated framework" |

Prioritization sheet: novelty 5, feasibility 4, impact 5, strategic 5, composite **4.75 — Priority**.

## 2. What the fetch script provisioned

`fetch_paper_data.py`, `PAPERS[3]`: `openfda=[]`, `dashboard=[]`, `extra=[]`, comment
`# guidance PDFs only — see README-manual.md`. Paper 3 was deliberately given **no
automated data**. `data/raw/` contains exactly two files: `MANIFEST.json`
(`"sources": {}`, `"openfda_export_dates": {}`) and `README-manual.md` listing three
manual URLs (FDA AI guidance, CDER AI page, CDER FRAME). None of the three PDFs/pages
were ever saved. **Empirical starting state for this paper: zero bytes of data.**

Shared corpora that do exist and are reachable (`Papers/_shared/`): openFDA
drug/{enforcement,event,label,ndc,drugsfda,shortages} + other/nsde (33 GB),
FAERS 2019Q1–2025Q4 (1.8 GB), ClinicalTrials.gov v2 full registry
(11 GB, 602 shards), FDA Data Dashboard compliance_actions /
inspections_citations / inspections_classifications (502 MB), Orange Book, Synthea.

## 3. Substrate selected and profiled

Nothing in `_shared` is *about* AI model credibility. The only corpus that contains a
large, dated, structured population of **AI/ML applications in drug and biological
product development** is the ClinicalTrials.gov snapshot. Built
`src/00_scan_corpus.py` (whole-word regex over title, official title, brief summary,
detailed description, keywords, intervention names/descriptions; 20 terms; bare "AI"
excluded to avoid chemistry false positives).

- Scanned **601,694** studies across 602 shards
- Matched **9,484** studies (**1.58 %**), unique NCT IDs, no duplicates
- First-posted range 1999-11-03 – 2026-09-04; start dates 1979 – 2030 (future starts are real registry values)
- Growth: 180 (2017) → 596 (2020) → 1,062 (2023) → 1,585 (2025) → 1,642 (2026 partial, snapshot 2026-09-07)
- Study type: 5,269 observational / 4,214 interventional / 1 expanded access
- Sponsor class: OTHER 8,258 · INDUSTRY 787 · OTHER_GOV 303 · FED 53 · NIH 39
- FDA-regulated **drug** = True: 139 (1.5 %); FDA-regulated **device** = True: 511 (5.4 %)
- `hasResults` = True: 327 (3.4 %)
- DMC present: 2,235; absent 5,663; **missing 1,586 (16.7 %)**
- Phase missing for 55.6 % (all observational studies carry no phase); allocation,
  masking, primary purpose, intervention model missing at the same ~55.6 % rate
- `is_us_export` missing 84.3 %; intervention types missing 21.6 %; countries missing 10.5 %
- Enrollment: median 241, p75 1,000, **max 50,000,000** — heavy right tail with
  implausible values; needs winsorising/log and explicit outlier reporting
- Term mix: artificial intelligence 4,490 · machine learning 2,784 · prediction model
  1,460 · deep learning 1,151 · clinical decision support 944 · radiomics 488 ·
  LLM 212. Match falls in the title for 3,702 and in an intervention for 1,925.

Files: `data/processed/aiml_studies.csv` (9,484 rows, 42 cols),
`results/01_profile.json`, `results/00_scan_summary_*.json`.

Quality problems that must be disclosed, not smoothed over: (i) regex membership is a
noisy definition of "AI study" with no gold standard — false positives (a trial
mentioning a "prediction model" in background text) and false negatives (a model
described without any of the 20 terms); (ii) registration is self-reported and
unaudited; (iii) 2026 is right-censored at the snapshot date; (iv) `UNKNOWN` status
for 1,884 studies means the record is stale, not that the study is running.

## 4. Regulatory ground truth (verified against primary source)

FDA draft guidance, *Considerations for the Use of Artificial Intelligence To Support
Regulatory Decision-Making for Drug and Biological Products*, January 2025, docket
FDA-2024-D-4689, **still draft (Level 1, "not for implementation") as of 2026-09-07**.
Seven-step risk-based credibility assessment framework, verbatim:

1. Define the question of interest that will be addressed by the AI model
2. Define the COU for the AI model
3. Assess the AI model risk
4. Develop a plan to establish the credibility of AI model output within the COU
5. Execute the plan
6. Document the results of the credibility assessment plan and discuss deviations from the plan
7. Determine the adequacy of the AI model for the COU

COU = "the specific role and scope of the AI model used to address a question of
interest". Model risk is a function of **model influence** (the contribution of
AI-derived evidence relative to other evidence for the question) and **decision
consequence** ("the significance of an adverse outcome resulting from an incorrect
decision concerning the question of interest"). Scope excludes AI used in drug
discovery and AI used for operational efficiency that does not affect patient safety,
drug quality, or reliability of results.

## 5. Mismatch between the claimed contribution and the data

| Workbook promises | Supportable here? |
|---|---|
| Framework converting COU + model risk into an auditable score | **Yes**, as design work — but this is an *operationalisation* of FDA's existing two-axis construct, not a new construct. Must be claimed that way. |
| Rubric covering data quality, bias, uncertainty, validation, monitoring | **Design yes, measurement mostly no.** Registry metadata carries validation-design proxies (allocation, masking, DMC, multi-site, results posted) and nothing at all on data quality, bias, or uncertainty quantification. |
| Delphi / expert review | **No.** There are no experts and no panel. Cannot be claimed in any form. |
| Inter-rater reliability | **No.** IRR requires ≥2 independent human raters. The rubric as automated is deterministic, so agreement with itself is 1.0 and meaningless. The honest substitute is *measurement-channel agreement* — structured-field scoring vs. independent free-text scoring — reported as such, plus bootstrap CIs and weight-sensitivity. This is weaker evidence than the workbook claims and must be relabelled in the paper. |
| Construct validity | **Partially.** Known-groups (FDA-regulated drug/device flag, phase, interventional vs observational, sponsor class), dimensionality, internal consistency. Not full construct validity — there is no external credibility criterion to converge on. |
| Case discrimination | **Yes**, on 9,484 real cases; this is the strongest available evidence. |
| "FDA and EMA guidance; published AI case studies" as the data | **Half.** FDA guidance is verifiable primary text. "Published AI case studies" were never collected and are not in `_shared`; the trial registry is a defensible substitute but is a *different* population — registered clinical studies, not regulatory submissions. |

**Bottom line.** The framework-design half of row 3 is supportable. The validation half
as written (Delphi, IRR) is not, with the data on this machine. The paper is therefore
honest only if it is positioned as: *a specified, computable operationalisation of
FDA's COU/model-risk construct, plus a 9,484-case measurement study of how much
credibility evidence is actually observable in the public record* — with the null
result (whether evidence scales with risk) reported whichever way it falls, and with
"validated framework" downgraded to "specified framework with partial validity
evidence".

The workbook's own note — "must add an original validated framework" — is the risk
this paper faces. The original part is defensible. The *validated* part will be thin,
and a reviewer will say so.
