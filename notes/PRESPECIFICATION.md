# Analysis pre-specification

Written after descriptive scoring (`results/03_scoring_summary.json`) and **before**
any inferential test was run. Descriptives seen at the time of writing: tier counts
low 3,304 / moderate 4,863 / high 983 / very_high 334; mean E_norm by tier
0.134 / 0.162 / 0.196 / 0.183; adequacy 27.9 / 2.7 / 0.31 / 0.0 %. This ordering was
therefore known when the tests below were specified, and the hypotheses are confirmatory
only in the weak sense of fixing the estimator, the effect-size metric and the
falsification threshold in advance. Stated plainly so no stronger claim is read into it.

## H1 — Risk-proportionality (primary)
Credibility evidence increases with assessed model risk.
- Estimator: Spearman rho between tier ordinal (0..3) and E_norm; Jonckheere-Terpstra
  trend test; Kruskal-Wallis with epsilon-squared. 5,000-resample bootstrap percentile CIs.
- **Supported** if rho > 0 with a 95% CI excluding 0 AND the low-to-very_high difference
  in mean E_norm exceeds 0.20 (one fifth of the scale).
- **Falsified** if either condition fails. A statistically significant but negligible
  rise counts as falsification of the substantive claim; this is stated in advance
  because n = 9,484 makes trivial effects significant.

## H2 — Discrimination
The rubric separates cases rather than collapsing them.
- Estimator: normalised Shannon entropy of the tier distribution; largest tier share.
- **Supported** if normalised entropy >= 0.50 and no tier holds > 0.80 of cases.

## H3 — Channel agreement
Structured-metadata and free-text channels measure the same construct.
- Estimator: quadratic-weighted Cohen's kappa per axis and per evidence dimension,
  bootstrap CIs. Reported as measurement-channel agreement, **not** inter-rater
  reliability: there is no second rater and no human rater anywhere in this design.
- **Supported** if weighted kappa >= 0.40 on both risk axes.

## H4 — Adjudication accuracy
Automated scoring reproduces case-by-case reading of the study record.
- Stratified random sample of n = 200 (50 per tier), adjudicated from each study's own
  registered text by a single automated annotator working from the rubric anchors,
  blind to the automated score.
- Estimator: exact-agreement rate and quadratic-weighted kappa per axis, Wilson CIs.
- **Supported** if weighted kappa >= 0.60 on both axes.

## H5 — Added information over comparators
CURA is not a relabelling of a simpler scoring.
- Comparators, each computed on the identical corpus: (B1) EU AI Act-style tiering by
  application category; (B2) a bare two-axis influence x consequence grid with no
  evidence layer; (B3) a flat count of reporting items, no risk weighting.
- Estimator: normalised mutual information and conditional entropy H(CURA | comparator);
  adjusted Rand index; cross-tabulation.
- **Supported** if H(CURA | B) >= 0.30 bits for every comparator, i.e. CURA tier is not
  nearly deterministic given any single comparator.
- **Falsified** if any comparator determines the CURA tier, in which case the framework
  is a repackaging and the paper must say so.

## H6 — Robustness
Conclusions do not depend on discretionary choices.
- Corpus definition at 3 strictness levels (title-match only / any-field / intervention match).
- Channel-combination rule: max, min, mean.
- Risk-matrix form: declared grid, sum-based, max-based, product-based.
- Dirichlet-perturbed dimension weights, 1,000 draws; Kendall tau of the induced ranking.
- Adequacy thresholds swept 0.1 to 0.9.
- Temporal split: first-posted before 2022 vs 2022 onward.
- **Supported** if the sign and rough magnitude of H1 hold in every variant.
- Any variant that flips a conclusion is reported as a failure of robustness, not dropped.

## Stopping rule
No hypothesis is dropped or rewritten after seeing its result. Failed hypotheses appear
in the results section with the same prominence as supported ones.
