# Supplementary Table S1 — Known corpus defects and their handling

Generated from the analysis pipeline. Every defect below is disclosed in the manuscript rather
than corrected; this table collects them in one place with the handling applied.

This work was carried out independently, on personal time and equipment, and is not connected to
the author's employment. The views expressed are the author's own and do not represent the views,
positions or policies of any current, former or future employer or client. No proprietary,
confidential or internal data of any organization was used.

| # | Defect | Handling | Effect on conclusions |
|---|--------|----------|----------------------|
| 1 | Lexicon membership is a noisy definition of "AI study". No gold standard exists in either direction, so neither false-positive nor false-negative rate is measured. | Three corpus strictness levels are reported (any field n = 9,484; title match n = 3,702; intervention match n = 1,925). | Bounds sensitivity to the definition; does not measure the error. Stated as a limitation. |
| 2 | Registration is self-reported and unaudited. | None available. | All findings are about the public record, not about what sponsors did or filed. |
| 3 | Phase, allocation, masking and primary purpose are absent for 55.6% of records, because observational studies carry none by construction. | Treated as a primary analysis, not a robustness check: the completeness measure uses only the eight fields recorded in both designs (Table S2), and H1 is re-estimated within study design. | This is the design confound. It removes 84.4% of the pooled association. |
| 4 | Enrollment is right-skewed with implausible extremes (maximum 50,000,000). | Winsorized at the 99th percentile wherever used. | Affects the enrollment correlation only, which is reported as a null. |
| 5 | 2026 is right-censored at the snapshot date (7 September 2026). | 2026 omitted from the annual registration series (Figure 5b). | Presentational only. |
| 6 | Two evidence dimensions are structurally unobservable in Channel A: no ClinicalTrials.gov field carries training-data provenance (D1) or model performance characterization (D3). | Recorded as a property of the record rather than scored as zero. | D1 and D3 rest on Channel B alone; both are near zero at every risk tier. |
| 7 | Channel B is sparse on both risk axes (86.1% of records score zero on influence, 76.5% on consequence). | Reported, and the resulting marginal degeneracy is stated as the reason the channel-agreement kappa is depressed. | kappa <= 0.06 means the channels are not interchangeable; it is not a calibrated effect size. |
| 8 | The corpus snapshot is not independently re-obtainable: ClinicalTrials.gov serves current state and no public archive of the 7 September 2026 snapshot exists. | SHA-256 digests of both derived tables are published so a reader can verify a copy against the one used here. | A real limit on reproducibility, stated rather than implied otherwise. |
