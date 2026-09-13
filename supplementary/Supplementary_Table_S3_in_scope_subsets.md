# Supplementary Table S3 — H1 re-estimated on every in-scope subset, with per-tier cell counts

The pre-specified substantive threshold is Delta E-bar > 0.20. No subset reaches it.

Per-tier cell counts are given because every subset contrast is anchored on its low-tier cell,
and in two subsets that cell is very small (n = 4 and n = 9). Those point estimates are unstable
and are reported as such in the manuscript.

| Subset | n | low | mod | high | v.high | Spearman rho | p | Delta E-bar (low to top) | mean E |
|---|---|---|---|---|---|---|---|---|---|
| all 9,484 | 9,484 | 3,304 | 4,863 | 983 | 334 | 0.2287 | 8.48e-113 | 0.0619 | 0.1562 |
| FDA-regulated drug = True | 139 | 4 | 54 | 66 | 15 | 0.3410 | 3.98e-05 | 0.0909 | 0.1885 |
| FDA-regulated device = True | 511 | 37 | 231 | 137 | 106 | 0.2804 | 1.1e-10 | 0.0708 | 0.1671 |
| either flag = True | 638 | 41 | 279 | 199 | 119 | 0.2903 | 7.45e-14 | 0.0762 | 0.1718 |
| interventional with a declared phase (drug/biologic development) | 379 | 9 | 213 | 127 | 30 | -0.0097 | 0.851 | 0.0000 | 0.2011 |
| industry-sponsored | 787 | 295 | 373 | 81 | 38 | 0.2514 | 8.18e-13 | 0.0870 | 0.1571 |

Mean normalized evidence by tier, per subset:

| Subset | low | moderate | high | very high |
|---|---|---|---|---|
| all 9,484 | 0.1339 | 0.1616 | 0.1958 | 0.1828 |
| FDA-regulated drug = True | 0.1333 | 0.1481 | 0.2242 | 0.1911 |
| FDA-regulated device = True | 0.1261 | 0.1449 | 0.1927 | 0.1969 |
| either flag = True | 0.1268 | 0.1460 | 0.2030 | 0.1955 |
| interventional with a declared phase (drug/biologic development) | 0.2222 | 0.2009 | 0.2031 | 0.1867 |
| industry-sponsored | 0.1336 | 0.1560 | 0.2206 | 0.2140 |

Note from the analysis: FDA's draft guidance covers drug and biological products. Only 139 of 9484 corpus studies carry the FDA-regulated-drug flag (1.5%). This is the corpus's most serious scope limitation.

Source: `results/08_confounds.json`.
