# Adversarial review — paper 03

Role: hostile reviewer. Objective: reject. Applied to the draft at `main.tex`
(14 pp., compiled 2026-09-07) using the six ARA rigor dimensions. Written by the
same system that produced the draft, which is itself finding F09.

**Recommendation: Weak Accept at a regulatory-science or health-informatics venue
after major revision. Reject at an ML main track. The central *empirical* claim
holds. The central *framework* claim does not.**

| Dimension | Score /5 |
|---|---|
| D1 Evidence relevance | 4 |
| D2 Falsifiability quality | 5 |
| D3 Scope calibration | 3 |
| D4 Argument coherence | 4 |
| D5 Exploration integrity | 4 |
| D6 Methodological rigor | 3 |
| **Mean** | **3.83** |

---

## CRITICAL

### F01 — The paper offers as a contribution an instrument its own results show is unreliable
**Dimension** D3 scope calibration · **Location** Title; Abstract; Contributions bullet 1; §3

The title leads with "An Executable Rubric". Contribution 1 is the rubric. But H3
(κ ≤ 0.06 between channels) and H4 (κ = 0.24–0.40 against adjudication) are failures
of *the rubric's own operationalisation*. An instrument that two disciplined
applications cannot agree on, and that reproduces careful reading at κ = 0.38, is not
a contribution — it is a negative result about the feasibility of the thing it tried
to be.

**Why it matters** A reader who adopts CURA on the strength of the title will be using
a scoring instrument the paper itself demonstrates is unreliable. That is worse than
publishing nothing. It is also the exact failure mode the regulatory-science literature
is full of: frameworks proposed, never validated, cited as though validated.

**Fix** Retitle and re-scope. The paper is a measurement study whose instrument is the
method, not the product. Contribution 1 should read: *"a specification precise enough
to fail, and its failure characterised."* Remove any language inviting adoption of
CURA v1.0 as an assessment tool, and say plainly in the conclusion that it should not
be used as one.

### F02 — H3's failure is at least as likely a construct failure of the rubric as a failure of the record
**Dimension** D1 evidence relevance · **Location** §5.3, first paragraph; §3.1

The paper interprets κ = 0.03–0.06 between channels as "two disciplined readings of the
same public record reach nearly independent conclusions", i.e. as a property of the
record. That inference is unearned. Channel A's influence items are *AI registered as an
intervention*, *AI named in the title*, and *interventional design*. None of these
measures the contribution of AI-derived evidence relative to other evidence, which is
FDA's definition. They measure **salience**: how prominently the study is about AI. A
study can name AI in its title and have the model contribute nothing to any decision.

The paper's own H4 result corroborates this reading: automated scoring over-states
influence by +0.35 levels, exactly what a salience proxy standing in for an influence
construct would do.

**Why it matters** If Channel A does not measure influence, then H3 is not evidence that
the record is ambiguous; it is evidence that one channel measures the wrong thing. The
paper's headline policy conclusion — "the record is the bottleneck, not the framework" —
depends on the first reading and is unsupported under the second.

**Fix** Either (a) present both interpretations explicitly and decline to choose, or
(b) test them apart: on the 200 adjudicated cases, regress adjudicated influence on the
three Channel A items individually and report which, if any, carries signal. The data
to do this already exists in `adjudication_labels.csv`. This is a required revision,
not an optional one.

---

## MAJOR

### F03 — B2 is not a comparator, and presenting it as one inflates H5
**Dimension** D6 methodological rigor · **Location** §5.4; Table 1 row H5

"B2 risk tier only" is CURA's own risk layer with the evidence layer deleted. Comparing
CURA against a subset of CURA is an ablation, not a baseline. H5 is stated as "CURA is
not a relabelling of a simpler scoring", and B1 and B3 support that; B2 supports nothing
about external novelty, and the paper's most-quoted H5 number (0.39 bits) comes from it.

**Why it matters** The pre-specification lists three "comparators" and H5's support
condition requires all three to clear 0.30 bits. One of the three is not a comparator,
so the hypothesis as written was never testable as stated.

**Fix** Relabel B2 as an ablation in the pre-specification, the table and the text.
State H5's support on B1 and B3 only. Report the ablation separately, where its honest
reading — the evidence layer adds little because it nearly always returns the same
answer — is already correctly given in §5.4.

### F04 — The policy recommendation is not supported by anything in the paper
**Dimension** D3 scope calibration · **Location** §6, "For regulatory science", final sentence

"Five fields would do most of the work: model version, training-data provenance,
validation design, subgroup performance, and the human-oversight arrangement." No result
in this paper bears on whether adding registry fields would change sponsor behaviour,
improve assessability, or be completed if added. Registries are full of fields with high
non-completion rates; this paper's own data shows `is_us_export` missing in 84.3% of
records.

**Why it matters** It is the paper's only actionable recommendation and it is an opinion
dressed as a conclusion. A regulatory-affairs reviewer will notice immediately, and it
will colour how they read the empirical section.

**Fix** Either mark it explicitly as a suggestion beyond the evidence, or support it —
the corpus can show completion rates for existing optional fields as a base rate for
what a new field would achieve.

### F05 — Single corpus, and the in-scope subsets are small
**Dimension** D6 methodological rigor · **Location** §7; §5.5

A framework evaluated on one dataset is a case study of that dataset. §5.5 is a good
answer to the scope objection, but the in-scope arms have n = 139 (drug flag) and
n = 379 (phased interventional). The most striking single number in the paper —
Δ = 0.000, ρ = −0.010 on phased interventional studies — rests on 379 cases with 9 in
the low tier. That cell cannot carry the weight the sentence puts on it.

**Why it matters** The abstract now foregrounds this subset. A CI on Δ for that subset
would very likely be wide enough to include values above 0.20.

**Fix** Bootstrap Δ for every subset in §5.5 and report CIs. If the phased-interventional
CI is wide, say so in the abstract or drop it from the abstract.

### F06 — No human rater exists anywhere in the design, including in the "adjudication"
**Dimension** D6 methodological rigor · **Location** §5.3; §7

The paper is candid about this, which is to its credit, but candour does not repair the
gap. The adjudication is a single automated annotator, and the paper then uses it as the
*criterion* against which the automated score is judged: "automated scoring over-states
influence by +0.35". That direction is only interpretable if the adjudication is closer
to truth, which is asserted, not shown.

**Why it matters** The two most-quoted numbers in the measurement section (κ range, and
the signed error direction) both depend on a criterion whose validity is unestablished.

**Fix** State the signed error as a *disagreement direction*, not an error direction,
unless and until a domain expert audits a subsample. The paper already publishes the
labels for exactly this purpose; commit to it as a stated next step and remove the causal
phrasing ("over-states", "under-states") from the abstract and discussion.

### F07 — "Negligible" oversells the smallness
**Dimension** D1 evidence relevance · **Location** §5.1; Abstract

ε² = 0.054 is described as negligible. By the conventional benchmarks ε² ≈ 0.01 small,
0.06 medium, 0.14 large, 0.054 sits at the top of the small band, approaching medium.
The paper is entitled to say the effect fails *its own* pre-specified substantive
threshold; it is not entitled to relabel it negligible.

**Why it matters** The paper's rhetorical strength comes from its discipline about
effect sizes. One loose word undercuts that in the sentence where it matters most.

**Fix** Replace "substantively negligible" with "small, and below the pre-specified
threshold". State the conventional benchmark so the reader can judge.

---

## MINOR

### F08 — Jonckheere–Terpstra variance has no ties correction
**Dimension** D6 · **Location** §5.1, `src/05_validity_baselines.py`

E_norm is a 16-level discretised score with heavy ties; the normal approximation used
applies the untied variance formula, which is anti-conservative. With z = 21.6 the
conclusion is unaffected, but the statistic as reported is not exactly the one named.

**Fix** Either apply the tie-corrected variance or state that the untied approximation
is used and that the test is corroborative of the Spearman and Kruskal–Wallis results
rather than primary.

### F09 — The reviewer is the author
**Dimension** D5 exploration integrity · **Location** this file

This adversarial review was produced by the same system that wrote the draft, as was
the adjudication in §5.3. Independence is claimed nowhere and exists nowhere. Findings
an outside reviewer would raise and this one would not are, by construction, invisible.

**Fix** State this in the paper's acknowledgements or reproducibility section. Do not
cite the existence of an adversarial review as evidence of rigour.

### F10 — The lexicon has no measured error rate in either direction
**Dimension** D6 · **Location** §4; §7

Acknowledged in Limitations, but the paper had a cheap opportunity to bound it: the
200-case adjudication sample could have carried a third label — "is this actually an AI
study?" — yielding a precision estimate at no extra cost.

**Fix** Add that label on the existing sample and report precision. Recall would still
be unestimated, which should be said.

### F11 — Corpus is not re-obtainable
**Dimension** D6 · **Location** Reproducibility section

SHA-256 digests of the derived tables let a reader verify a copy they were given; they
do not let anyone reconstruct the corpus, because ClinicalTrials.gov serves only current
state and the 2026-09-07 snapshot has no public archive. "Reproducible" overstates it.

**Fix** Say "verifiable given the derived tables, not independently re-obtainable", and
deposit the two derived CSVs (≈ 40 MB) with the preprint.

### F12 — Figure 1(b) shading invites a stronger reading than the text supports
**Dimension** D3 · **Location** Figure 1

The shaded adequacy gap is visually dramatic and, as §5.2 concedes, partly definitional:
θ rises by construction while E does not. The figure makes the tautological version look
like the finding.

**Fix** Add the flat-threshold line to the panel, or move the θ curve to a secondary
panel so the primary visual carries the threshold-free claim.

---

## What a regulatory-affairs reviewer would say that an ML reviewer would miss

1. **ClinicalTrials.gov was never designed to carry model documentation.** Reading its
   silence as an accountability failure is a category error unless the paper argues that
   it *should* carry it. §6 gestures at this; it needs to be an argument, not a gesture.
2. **"Adequacy" is a regulatory term of art.** In FDA's framework, adequacy is the
   sponsor-and-regulator determination at step 7 after the credibility plan is executed.
   The paper computes something it also calls adequacy from public metadata. A regulatory
   reader will hear a determination being made about specific sponsors. Rename it
   (*observable evidence sufficiency*) throughout.
3. **The guidance is draft, non-binding, and explicitly excludes drug discovery and
   non-safety operational uses.** The paper states this once. It should also state that
   nothing in the corpus was subject to it at the time of registration — most records
   predate January 2025 entirely.
4. **139 drug-flagged studies is not "AI in drug development".** The paper is really
   about AI in clinical research. The framing should follow the data.

## What an ML reviewer would say that a regulatory reviewer would miss

1. **There is no learned model, no baseline in the ML sense, and no held-out prediction
   task.** The contribution is measurement, not method. At an ML venue this is a scope
   mismatch, not a quality problem — but it is fatal for a main track.
2. **κ against a single automated annotator is not validation**; it is self-consistency
   between two configurations of the same system.
3. **Formative-vs-reflective is asserted, not tested.** The paper says a low α is expected
   for a formative index. That is correct theory, but it is used to excuse a number rather
   than to make a prediction. A confirmatory factor model, or a stated prediction that
   inter-dimension ρ should stay below some bound, would turn an excuse into a test. Max
   off-diagonal Spearman ρ is reported; it should be given a pre-specified bound.

## Reproducibility: what a reader could not reproduce

| Item | Status |
|---|---|
| Corpus construction | Script published; **source snapshot not re-obtainable** |
| Scoring, all statistics, all figures | Fully reproducible from the two derived CSVs |
| Rubric | Published as data |
| Adjudication labels | Published; **annotator not reproducible** |
| Comparator B1 (EU AI Act-style mapping) | Implemented in code but **not defended anywhere in the text** |
| Pre-specification | Published, with its own weakness disclosed |
| Random seed | Fixed (20260907) throughout |

## The strongest single argument for rejection

Strip the paper to what it establishes and it says: *a scoring instrument we designed,
which fails its own reliability checks, applied to a corpus 98.5% outside the guidance's
remit, finds that a registry not designed to hold model documentation does not hold much
model documentation.* Each clause is defensible; together they describe a result that may
be true, robust, and not worth a venue's pages.

**The strongest counter, which the paper should make explicitly and currently does not:**
the flat-evidence finding survives every attempt made here to destroy it — four matrix
forms, three combination rules, three corpus definitions, 1,000 weight draws, two eras,
adjudicated tiers, record-length conditioning, permutation, and every FDA-in-scope subset
including the one where it is flattest of all. Findings that survive that many
falsification attempts are rare, and the negative measurement results are useful to
anyone building automated AI governance tooling. That is the case for publication, and
the paper should make it rather than leaving the reviewer to assemble it.

---

# Response to review — changes made to the draft

Applied in the same session as the review. Findings marked *outstanding* remain open
and are recorded in the paper's Limitations.

| ID | Severity | Status | What changed |
|---|---|---|---|
| F01 | Critical | **Fixed** | Retitled to "A Context-of-Use Model-Risk Rubric Specified Precisely Enough to Fail". Contribution 1 rewritten as a specification-and-its-failure. Conclusion now states explicitly that \cura v1.0 should not be used to score real cases. |
| F02 | Critical | **Fixed with a new analysis** | Ran the item-level test on the 200 adjudicated cases (`src/09_review_responses.py`). All three Channel A influence items carry real signal (ρ = 0.332 / 0.295 / 0.278, all p < 1e-4; each significant jointly), and the title item tracks adjudicated influence more strongly than it tracks AI-term count — so the pure-salience reading is wrong. But the three items explain only 18.3% of variance. §5.3 now reports both readings and states that this study cannot separate them; the conclusion no longer says "the record is the bottleneck". |
| F03 | Major | **Fixed** | B2 relabelled an ablation throughout; withdrawn from H5's support condition, which now rests on B1 and B3. |
| F04 | Major | **Fixed** | The five-fields recommendation is now explicitly marked as going beyond the evidence, with the 84.3% non-completion rate of an existing optional field given as the counter-consideration. |
| F05 | Major | **Fixed with a new analysis** | Bootstrap CIs computed for every subset gradient. Drug flag: 0.091 [0.029, 0.150]; phased interventional: 0.000 [0.000, 0.051]. In every subset, 0 of 5,000 replicates exceeds 0.20. Abstract claim survives. |
| F06 | Major | **Fixed** | "Over-states / under-states" replaced with a stated direction of *disagreement*, with the reason given. |
| F07 | Major | **Fixed** | "Substantively negligible" → "small", with the conventional ε² benchmarks stated. |
| F08 | Minor | **Fixed** | JT now labelled as an untied normal approximation and explicitly corroborative rather than primary. |
| F09 | Minor | **Fixed** | Reproducibility section states that the adjudicator and this reviewer are the same system as the author, and that the review is not offered as evidence of rigour. |
| F10 | Minor | *Outstanding* | The lexicon precision label was not added; doing it properly needs a re-read of the sample against a third criterion. Recorded in Limitations as an unmeasured error rate in both directions. |
| F11 | Minor | **Fixed** | Reproducibility reworded: verifiable given the derived tables, not independently re-obtainable; deposit of the two CSVs recommended. |
| F12 | Minor | **Fixed** | Figure 1(b) now carries a flat 0.30 reference line so the threshold-free reading is visible alongside the θ curve. |
| Reg-2 | — | **Fixed** | "Adequacy" renamed *observable evidence sufficiency* throughout, with an explicit note that adequacy is FDA's step-7 term of art and is not computable from public metadata. \cura's expansion changed to Context-of-Use Risk Assessment to remove the collision. |
| Reg-3 | — | **Fixed** | §4 now states that the guidance issued in January 2025, that most records predate it, and that none was subject to it. |
| Reg-4 | — | **Fixed** | Title and framing changed from "AI in Drug Development" to "Registered AI Studies". |
| ML-3 | — | *Outstanding* | Formative-index reasoning is still asserted rather than tested. A pre-specified bound on inter-dimension ρ would fix it; not done. |

**Verdict after revision.** The critical findings are addressed and one of them (F02)
produced a genuinely new result that made the paper's central claim *weaker and more
honest*: the paper no longer says the record is the bottleneck, because it cannot show
that. Recommendation moves from Weak Accept to **Accept at a regulatory-science or
health-informatics venue; still Reject at an ML main track** on scope, not quality.
