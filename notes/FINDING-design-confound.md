# The tier–evidence association is a between-design artefact

Analysis: `src/11_completeness.py` → `results/11_completeness.json`. Figure:
`figures/fig6_design_confound.pdf`. Seed 20260907. Answers adversarial-review findings
B-05(c) and B-02.

## The one-line result

**Within interventional studies — the only stratum where every scoring field applies and
all four risk tiers exist — credibility evidence does not rise with assessed model risk at
all: Δ = +0.0031, 95% CI [−0.0104, +0.0165], against a pre-specified threshold of 0.20.**

The manuscript's reported association (ρ = 0.229) is almost entirely a comparison between
interventional and observational studies, not a relationship between risk and evidence.

## How it was found

The adversarial review argued that missing registry fields fall through to zero points, so
incompletely registered studies score both lower risk and less evidence, manufacturing a
positive association. That is true but it is not the main story. Testing it properly
required separating two things a naive completeness score conflates:

- a field **not reported** (a real disclosure gap), and
- a field **not applicable to the design** — an observational study has no phase,
  allocation, masking or primary purpose.

Classifying each field empirically (universal iff <50% missing in *both* designs) leaves
eight universal fields and marks four as design-dependent. With that correction,
completeness explains far less than it first appeared, and study design explains far more.

## The adjustment ladder

ρ(risk tier, evidence), progressively controlled:

| Control | ρ | 95% CI | Share of association removed |
|---|---|---|---|
| unadjusted | +0.2287 | [0.211, 0.247] | — |
| + record length | +0.2170 | [0.197, 0.238] | 5.1% |
| + completeness | +0.1928 | [0.173, 0.212] | 15.7% |
| **+ study design** | **+0.0356** | **[0.018, 0.055]** | **84.4%** |
| + all three | +0.0575 | [0.038, 0.078] | 74.9% |

The manuscript's §5.5 controlled for record *length* and concluded the association was not
an artefact. Length removes 5.1%. The operative variable was never tested.

## Simpson's paradox, explicitly

| Stratum | n | ρ(tier, evidence) |
|---|---|---|
| Pooled | 9,484 | **+0.2287** |
| Interventional | 4,214 | +0.0378 |
| Observational | 5,270 | +0.0337 |

The pooled association is between strata. It nearly vanishes inside either one.

## Why the strata differ

CURA's tier is largely a design proxy: ρ(interventional, tier) = **+0.600**.
**All 334 very-high-risk cases are interventional.** Only 18 of 5,270 observational studies
reach high risk and none reaches very high. Interventional studies also carry more evidence
(mean E 0.187 vs 0.131) for reasons that have nothing to do with risk-proportionality —
they are the studies GCP and registration rules document most heavily.

## The scoring defect underneath it

Missing fields are scored as zero, i.e. as low consequence:

| Consequence item | scored 0 | of which the field was missing |
|---|---|---|
| c1 FDA-regulated article | 8,846 | 646 (7.3%) |
| **c2 care-bearing purpose** | 6,909 | **5,287 (76.5%)** |
| c3 patient population | 3,424 | 543 (15.9%) |

Three quarters of the zeros on the largest consequence item are absent data, not a
determination of low consequence.

## Four QA checks

1. **The null is precise, not underpowered.** CI width 0.027 on n = 4,214; rules out any
   effect above 0.017 against a threshold of 0.20.
2. **Not over-adjustment.** Study design is encoded in CURA influence item i3, so
   controlling for it could condition on part of the exposure. Deleting i3 entirely,
   design still predicts tier (ρ = +0.340, down from +0.600) — the link is not merely
   definitional — and the within-design contrast stays at +0.0056.
3. **Both strata, on a contrast that exists in both.** Interventional low→high
   Δ = +0.0159 [0.005, 0.027]; observational +0.0706 [0.010, 0.143] on just 18 high-tier
   records, so that interval is wide and should not be leaned on.
4. **Robust to rescoring.** Scoring each consequence item only where observed and
   rescaling shifts 1,447 studies out of the low tier, drops ρ to 0.175, and leaves the
   within-interventional contrast at +0.0071 [−0.0066, +0.0210] — still zero.

## What this does to the paper

**Strengthens the headline.** H1 was reported as "significant but small." It is not small,
it is **absent** once like is compared with like. The falsification is cleaner and the
effect-size argument no longer has to carry the weight.

**Fixes B-02 in passing.** Everything above uses the pre-specified low→very_high contrast.
Pooled, that is **0.0490** [0.039, 0.059] — not the 0.062 the manuscript reports, which
came from an undeclared low-to-max-tier estimator.

**Corrects a stated robustness claim.** §5.5's "the association is not a length artefact"
is true and irrelevant; the design confound was never tested.

**Adds a finding of its own.** An automated governance score computed from registry
metadata substantially measures *study design and form completion* rather than model risk.
That generalises well beyond this rubric and sharpens the paper's warning about automated
governance auditing.

## What is untouched

The scarcity prevalences do not depend on any of this — they are counts over free text,
independent of tier, estimator, combination rule, completeness and design: model or
algorithm versioning **0.24%**, human oversight **0.39%**, model monitoring **1.27%**, bias
assessment **1.50%**, external validation **3.86%**, training-data description **3.88%**,
any expression of uncertainty **3.48%**; **39.1%** of studies mention no auditable item at
all. Completeness barely relates to them (ρ = −0.055).

## Caveats

- Design and completeness are not randomly assigned. These are associations under
  adjustment, not causal identification.
- Restricting to interventional studies is a restriction, but a necessary one: it is the
  only stratum in which all four tiers occur and all scoring fields apply.
- Many tests are reported here. The primary contrast was fixed by design logic before the
  results were seen; the rest are supporting.
