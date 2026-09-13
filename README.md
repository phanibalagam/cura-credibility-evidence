# CURA — measuring credibility evidence for AI in the public clinical-research record

Code, rubric, result files and adjudication labels for:

> **Measuring Credibility Evidence for AI in Clinical Research: Scarcity, and a Risk Gradient
> That Is Study Design in Disguise.** Phani Kumar Balagam, Independent Researcher.
> Under review.

---

## Independence

This work was carried out independently, on personal time and equipment, and is not connected to
the author's employment. The views expressed are the author's own and do not represent the views,
positions or policies of any current, former or future employer or client. No proprietary,
confidential or internal data of any organization was used. All data is public: the
ClinicalTrials.gov v2 study registry, a complete 601,694-record snapshot retrieved 2026-09-07 (US
federal public domain under the National Library of Medicine copyright policy, which requests
source acknowledgment), and one set of author-generated adjudication labels covering 200 of those
records, produced for this work and released with it.

---

## What this is

A measurement study of what the public clinical-research record shows about AI model credibility.
FDA's January 2025 draft guidance asks for credibility evidence proportionate to model risk. This
work specifies that construct as an executable rubric — CURA, Context-of-Use Risk Assessment —
and applies it to 9,484 AI/ML studies drawn from a complete ClinicalTrials.gov snapshot.

Two results, both negative:

1. **Auditable credibility evidence is close to absent.** Model or algorithm versioning is
   mentioned in 0.24% of records, human oversight in 0.39%, model monitoring in 1.27%, bias
   assessment in 1.50%, external validation in 3.86%, training-data description in 3.88%. 39.1%
   contain no free-text mention of any rubric item. Every figure is an upper bound, because a
   bare mention counts.
2. **The apparent risk gradient is study design.** Pooled, evidence rises with assessed risk
   (Spearman rho = 0.229; mean-evidence difference 0.049 against a pre-specified 0.20).
   Conditioning on study design removes 84.4% of that association, and within interventional
   studies the pre-specified contrast is 0.0031, 95% CI -0.0104 to 0.0165.

Three of six pre-specified hypotheses fail. The failures are the paper.

Multiplicity across the eight tests behind H1 and the design diagnosis was checked rather than
conceded: Holm and Benjamini–Hochberg correction at α = 0.05 changes no conclusion, the two
within-design associations included (largest Holm p = 0.028). A wider family of sixteen tests,
adding construct validity, the in-scope subset re-runs and the adjudication-item associations,
changes no conclusion either (largest Holm p = 0.041). See `src/12_multiplicity.py`.

**CURA v1.0 should not be used to score real cases.** Its two measurement channels agree about
model risk at weighted kappa <= 0.06, and two readings of the same records by the same automated
annotator agree at kappa = 0.24-0.40. It is published as this study's instrument, failures
included, not as an assessment tool.

## Layout

```
src/cura_rubric.json        the rubric, as data
src/00..09_, 11_, 12_*.py   the pipeline, in order (12_ is the multiplicity correction)
src/10_verify_manuscript.py re-checks 283 numeric and verbatim claims; exits non-zero on any mismatch
figures/gen_*.py            both figure scripts
figures/*.pdf               the six figures
results/*.json              every aggregate number in the article
notes/                      pre-specification, grounding, plan, design-confound write-up
supplementary/              Supplementary Tables S1-S3
data/processed/             the 200 adjudication labels and their automated counterparts
REVIEW-FINDINGS.md          adversarial review and response table
DATA_CARD.md                provenance, modifications, limitations
MANIFEST.json               what is deliberately not redistributed, with sizes and SHA-256
```

## Rerun

```bash
python src/00_scan_corpus.py 0 150      # repeat for 150-300, 300-450, 450-700
python src/01_merge_profile.py
python src/02_extract_evidence_text.py 0 150   # same four ranges
python src/03_score_cura.py
python src/04_reliability.py
python src/05_validity_baselines.py
python src/06_make_adjudication_sample.py
python src/07_adjudication.py
python src/08_confounds.py
python src/09_review_responses.py
python src/11_completeness.py
python src/12_multiplicity.py
python figures/gen_figures.py
python figures/gen_fig6_confound.py
python src/10_verify_manuscript.py
```

Seed 20260907 throughout. Requires pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib.

**The snapshot is not independently re-obtainable.** ClinicalTrials.gov serves current state and
no public archive of the 2026-09-07 snapshot exists, so a rerun today yields a different corpus.
See `DATA_CARD.md`.

## Data

Source: **ClinicalTrials.gov**, US National Library of Medicine. Processed **2026-09-07**.
Modifications are described in `DATA_CARD.md`. This repository redistributes no ClinicalTrials.gov
record content — it carries study identifiers, the author's own scores and labels, and aggregate
statistics. See `MANIFEST.json` for what is excluded and its digests.

## Licenses

Code: MIT (`LICENSE`). Author-generated data and result files: CC BY 4.0 (`LICENSE-DATA`).

## Citation

See `CITATION.cff`.
