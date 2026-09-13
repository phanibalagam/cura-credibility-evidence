# Phase 2 plan — what we will prove, and what we will not

## Provable with the evidence on hand

| # | Claim | Evidence that establishes it | Can it come out null? |
|---|---|---|---|
| C1 | FDA's COU/model-risk construct can be specified as a computable function with a declared rubric, thresholds and tie-breaks | The rubric spec (`src/cura_rubric.json`) executes over 9,484 cases without manual intervention; every case receives a tier | No — constructive |
| C2 | The score discriminates among real cases rather than collapsing them | Tier distribution entropy, pairwise separation, comparison against degenerate scorers | Yes — could collapse to one tier |
| C3 | Two independent measurement channels (structured metadata vs. free text) agree at a measurable rate | Cohen's / quadratic-weighted kappa with bootstrap CIs, per axis and per dimension | Yes — could disagree |
| C4 | Automated scoring agrees with case-by-case adjudication of the study text | Stratified n=200 adjudicated sample, per-item accuracy and kappa with 95% CIs | Yes |
| C5 | Assessed risk tier tracks independent regulatory markers (FDA-regulated drug/device flag, phase, purpose, sponsor class) | Known-groups analysis; ordinal association with CIs | Yes |
| C6 | **Risk-proportionality**: credibility evidence increases with assessed risk tier | Pre-registered test, evidence score regressed on tier | **Yes — this is the paper's live null** |
| C7 | Credibility evidence in the public record is dominated by structural absence: provenance, representativeness and uncertainty are near-unobservable | Free-text prevalence of evidence terms across 9,484 cases | Partly — magnitudes are what they are |
| C8 | The rubric adds discriminative information beyond simpler comparator scorings | Comparator scorers on the identical corpus; conditional entropy, rank correlation, tier cross-tabulation | **Yes — could add nothing** |
| C9 | Results are robust to corpus definition, weighting and threshold choices | 3 corpus-strictness levels; Dirichlet weight perturbation; threshold sweep; temporal split | Yes |

## Deliberately NOT claimed

- No Delphi, no expert panel, no human inter-rater reliability. C4 is single-annotator
  automated adjudication and is labelled as such throughout.
- No claim that the score predicts regulatory acceptance. No outcome label exists.
- No external corpus. Two FDA file endpoints (AI-Enabled Medical Device List CSV/XLSX)
  are blocked from both the analysis container and the local machine; every other
  local corpus (openFDA, FAERS, Data Dashboard, Orange Book, Synthea) contains no
  population of AI use cases. Single-corpus evidence is a stated limitation and is
  the honest reason this is positioned as a measurement study, not a validated instrument.
- No claim about drug discovery or operational-efficiency AI — outside FDA's stated scope.

## Strengthening moves added beyond the original scope

1. **Comparator baselines** (C8). Three independent scorings of the same corpus: an
   EU AI Act-style tiering, a bare two-axis influence x consequence grid with no
   evidence layer, and a reporting-completeness count. An ML reviewer's first question
   is "compared to what"; framework papers in this space almost never answer it.
2. **Adjudicated gold sample** (C4), n=200 stratified, scored by reading each study's
   own text, with a spot-check CSV so a domain expert can audit it by hand.
3. **Dual measurement channels** (C3) in place of the unattainable inter-rater reliability.
4. **Pre-registered falsification criteria** written before the results are computed.
5. **Framework crosswalk** to SR 11-7, ICH Q9(R1), GAMP 5, ASME V&V 40, EU AI Act,
   EMA reflection paper, ICH E6(R3) and TRIPOD+AI, claiming only the delta.
6. **Sensitivity battery** (C9) on corpus definition, weights, thresholds, and time.
7. **Reproducibility pack**: rubric as data, corpus SHA-256, one-command rerun.
