# Data card — CURA credibility-evidence corpus

## Provenance

One row per registered clinical study that mentions an AI/ML component. Built from a complete
snapshot of the **ClinicalTrials.gov v2 study registry** — 601,694 study records across 602
shards — **processed 7 September 2026**. 9,484 studies (1.58%) matched a 20-term whole-word
lexicon covering named model families, AI/ML terminology and clinical decision support; the bare
token "AI" was excluded to avoid chemistry false positives.

**Modifications made to the source data**, as ClinicalTrials.gov's Terms and Conditions ask to be
stated: records were filtered to the matching 9,484; structured fields were extracted to a flat
table; free text (title, summaries, keywords, intervention descriptions, outcome measures) was
extracted to a second table; each record was scored against the CURA rubric published here as
`src/cura_rubric.json`; and enrollment was winsorized at the 99th percentile wherever used. No
record was altered, and no value in the registry was corrected or imputed.

## What is in this repository

- `data/processed/adjudication_labels.csv` — 3,931 B — the author's 200 adjudication labels
  (`idx`, `nct_id`, `adj_influence`, `adj_consequence`). Author-generated; no registry text.
- `data/processed/adjudication_key.csv` — 9,283 B — the corresponding automated scores for the
  same 200 studies (`nct_id`, `tier`, `influence`, `consequence`, channel scores, `E_norm`).
  Derived; no registry text.
- `results/*.json` — 12 files — every aggregate number reported in the article. No study
  identifiers and no registry text appear in any of them.
- `src/cura_rubric.json` — the rubric, as data: ordinal anchors, the 4x4 risk matrix, the five
  evidence dimensions and their items, and the declared sufficiency thresholds.
- `src/`, `figures/` — the full pipeline, in order, plus the manuscript verifier.
- `notes/`, `supplementary/`, `REVIEW-FINDINGS.md` — the pre-specification, the analysis plan,
  the design-confound write-up, three supplementary tables, and the adversarial review.

## What is not, and why

`MANIFEST.json` records every excluded artifact with its size and SHA-256, so you can verify you
hold the same bytes without them being republished here.

The two derived corpus tables are the substantive exclusions:

- `aiml_evidence_text.csv` — 39,044,555 B — sha256
  `fadf02dd5480c34ad593eb7f03df7046b9cd9a45b8e6a59c74a6a46840725974`
- `cura_scores.csv` — 7,239,104 B — sha256
  `7b41eae662f133c8484058d0e9b1060fdbfde0c5e606caf9069a3cca86d64605`

Both carry registered text authored by study sponsors. ClinicalTrials.gov's Terms and Conditions
state that its data carry an international copyright outside the United States and its
Territories or Possessions, and that some data may be subject to third-party copyright, so that
content is not redistributed. The first two digests are also recorded inside
`results/03_scoring_summary.json`, which is in this repository, so the exclusion is independently
checkable. Both tables regenerate from the public registry by `src/00_scan_corpus.py` and
`src/02_extract_evidence_text.py`.

## Reproducibility, stated honestly

**The snapshot is not independently re-obtainable.** ClinicalTrials.gov serves current state, and
no public archive of the 7 September 2026 snapshot exists. Re-running the pipeline against the
registry today will produce a different corpus, because records are added and revised daily. That
is a real limit and it is stated rather than implied otherwise. The digests above are what a
reader can check a copy against; they are not a substitute for an archived snapshot.

## Known limitations

Lexicon membership is a noisy definition of "AI study" and no gold standard exists in either
direction, so neither the false-positive nor the false-negative rate is measured. Registration is
self-reported and unaudited. Phase, allocation, masking and primary purpose are absent for 55.6%
of records because observational studies carry none by construction — this is the design confound
that the analysis is largely about. Two evidence dimensions are structurally unobservable in the
structured channel. The 200 adjudication labels were produced by the same automated annotator
that produced the scores, so they establish internal consistency and not accuracy; they are
published here so a domain expert can audit them. Supplementary Table S1 collects every disclosed
defect with its handling.

## Attribution

Source of the underlying data: **ClinicalTrials.gov**, US National Library of Medicine. Data
processed 7 September 2026. Nothing here redistributes ClinicalTrials.gov record content.
