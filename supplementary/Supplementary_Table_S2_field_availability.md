# Supplementary Table S2 — Field availability by study design, all twelve candidate fields

Rule: universal iff <50% missing in BOTH designs.
n = 9,484 (4,214 interventional, 5,270 observational).

The completeness measure used in the manuscript is built from the eight universal fields only,
so that "incomplete" never means "a design that has no such field".

| Field | % missing, interventional | % missing, observational | Class |
|---|---|---|---|
| `is_fda_regulated_drug` | 7.5 | 6.5 | universal |
| `is_fda_regulated_device` | 7.5 | 6.7 | universal |
| `healthy_volunteers` | 0.1 | 10.2 | universal |
| `primary_purpose` | 0.4 | 100.0 | **design-dependent** |
| `allocation` | 25.9 | 100.0 | **design-dependent** |
| `masking` | 0.1 | 100.0 | **design-dependent** |
| `phases` | 91.0 | 100.0 | **design-dependent** |
| `has_dmc` | 12.5 | 20.1 | universal |
| `countries` | 9.5 | 11.3 | universal |
| `intervention_types` | 0.0 | 38.8 | universal |
| `min_age` | 7.5 | 12.5 | universal |
| `sex` | 0.0 | 0.0 | universal |

Mean completeness over the eight universal fields: 0.9015 overall, 0.9444 interventional, 0.8672 observational; 48.88% of records are complete on all eight.

Source: `results/11_completeness.json`.
