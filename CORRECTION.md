# Correction notice — v0.1.0 claims withdrawn

**Date:** 2026-11-12
**Affects:** commit `16efb70` and everything derived from it (README, PREPRINT-DRAFT, BLOG-POST,
COURTESY-EMAIL, SUBMISSION-CHECKLIST)

## What we claimed

> "Reproduces published pooled estimates: sensitivity 136/137 within 0.01; specificity 137/137."

presented in the README as validation of the pooling engine, and in the preprint as establishing
that the harness reproduces the source study's estimator.

## Why it was wrong

The published pooled estimates in the source supplement are **anonymised** ("Meta ID 1…N") with no
mapping to review, outcome, or dataset version. We matched each published value to the *nearest*
computed value across 437 candidates at tolerance 0.01, and reported the hit rate.

That procedure has no discriminating power. With 137 published values and 437 computed values
spread over the same range, a nearest neighbour within 0.01 exists almost always, whether or not
the two sets correspond at all.

`src/matching_null_test.py` measures this directly:

| Method | Observed | Null mean | Null max |
|---|---|---|---|
| Single-parameter nearest match, sensitivity | 0.993 | **1.000** | 1.000 |
| Single-parameter nearest match, specificity | 1.000 | **1.000** | 1.000 |
| Joint (sens, spec) unique match | 50/137 | **40.9/137** | 53/137 |

The observed single-parameter rate is *below* the null. The joint match falls inside the null
range. **Neither establishes study-level reproduction.**

## What is withdrawn

- "136/137" and "137/137" as validation. Removed from README, preprint, blog and email.
- "Reproduces published pooled estimates." Withdrawn.
- The Yeung 2009 finding as a demonstrated error. Downgraded to unresolved; see
  `examples/yeung-2009.md`. In particular:
  - the paper's "Overall" row is the **mean of three readers**, so no single 2×2 can reproduce it;
  - 88.0% vs 89% and 93.3% vs 92% are 1.0 and 1.3 pp apart, **not rounding**;
  - a `27/30` line in the earlier text was an arithmetic error (`24/27 = 88.9%`);
  - the discrepancy was already identified by the source study — no novel contribution.
- The "table header defect" finding (PMC13456766 Table 2). **Withdrawn as unsubstantiated.** The
  data columns could not be resolved from the XML with confidence, and a column-order conflict is
  as likely to be an artefact of our parsing as a defect in the paper.

## What still stands

- The released dataset's own counts reconcile with the paper: 6,173 trials; 338 flagged (5.48%);
  46 reviews; 34 with at least one error. These are direct recounts, not a matching exercise.
- The nearest-match critique itself is a legitimate methodological point and is now pinned by a
  test that fails loudly.
- The extraction layer now treats explicit headers as authoritative and abstains on ambiguity.

## Process failure

The v0.1.0 gate was a script that printed `PASS`. It passed because it asked a question that could
not fail. A validation that cannot fail is not a validation, and shipping it as one was the same
error this project exists to criticise.

`src/model_check.py` now reports the pooling validation as **BLOCKED** and exits non-zero.
