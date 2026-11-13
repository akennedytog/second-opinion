# Worked example: what a single case can and cannot show

**Status: substantially withdrawn.** The version shipped in v0.1.0 claimed that re-extracted cells
"reproduce the paper" and that the review's cells were wrong. Re-checking against the primary
source shows that claim was overstated. This document records what survives and what does not.

## The primary source

Yeung et al., *Canadian Journal of Neurological Sciences*, 2009.
doi:10.1017/S0317167100006533

Verified directly from the PDF:

- 286 patients screened between January 2001 and February 2007; **55 patients formed the study
  cohort** ("Fifty five patients met inclusion criteria").
- Diagnostic yield for DSA was **45% (25/55)** — i.e. 25 patients had a vascular lesion, 30 did not.
- Table 1 reports accuracy **per reader**, and an "Overall" row:

| | Sensitivity | Specificity |
|---|---|---|
| Reader 1 | 88 | 90 |
| Reader 2 | 92 | 97 |
| Reader 3 | 88 | 90 |
| **Overall** | **89** | **92** |

## What this means — and it undercuts the original example

**The "Overall" row is the mean of the three readers, not a single 2×2 table.**

- (88 + 92 + 88) / 3 = 89.3 → 89
- (90 + 97 + 90) / 3 = 92.3 → 92

Therefore **no single contingency table reproduces the published 89% / 92%**. Any claim that our
cells "reproduce the paper's figures" is wrong in principle, not merely imprecise.

## The two candidate tables, checked honestly

| Source | TP | FP | FN | TN | N | sens | spec |
|---|---|---|---|---|---|---|---|
| Cells recorded as extracted (JAMA dataset) | 20 | 3 | 0 | 24 | 47 | **100.0%** | 88.9% |
| Cells recorded as re-extracted (JAMA dataset) | 22 | 2 | 3 | 28 | **55** | 88.0% | 93.3% |

- The 47-patient version cannot be right: the cohort is 55.
- The 55-patient version has a defensible N, and its sensitivity (88.0%) matches **Reader 1 and
  Reader 3** exactly.
- But its specificity (93.3%) matches **no** reader (90, 97, 90) and is 1.3 pp away from the
  averaged 92%.

**Correction to the v0.1.0 text:** the original example described 88.0% and 93.3% as "consistent
with the paper within rounding." They are 1.0 and 1.3 percentage points away respectively. That is
not rounding, and the earlier phrasing concealed a real mismatch.

**Correction to the v0.1.0 arithmetic:** one version of the text compared `27/30` for specificity.
The correct figure from the recorded cells is `24/27 = 88.9%` (extracted) and `28/30 = 93.3%`
(re-extracted). The `27/30` line was an error.

## What remains supportable

1. The recorded extracted cells imply a 47-patient sample; the published cohort is 55. That is a
   discrepancy on its face.
2. No reader reports 100% sensitivity, so a 100% implied sensitivity is not supported by the paper.
3. **We cannot confirm what the review actually printed.** Cochrane full text returns HTTP 412 to
   automated requests, so the "extracted cells" are known to us only second-hand, from the JAMA
   dataset. We never saw the review's table.

## Who found this first

**The source study did.** This trial is one of their 338 flagged rows. We rediscovered a
previously reported discrepancy — the same error the Maya case made. There is no novel finding
here, and the earlier framing implied there was.

## The honest summary

This case demonstrates that a flagged discrepancy can be *plausible* — the 55-patient version is
close to the published values — without being *demonstrated*. Under examination it does not cleanly
reconcile with any table in the paper. The correct conclusion is that **this specific case remains
unresolved and needs the review's own table plus expert adjudication**, not that we caught an error.
