# Worked example: one cell that contradicts its source paper

This is the smallest complete unit of the audit. Everything below is reproducible from the
citation and the two public sources; no special access is required.

## The claim under test

A diagnostic meta-analysis (Cochrane review CD009372, "Computed tomography angiography or magnetic
resonance angiography for detection of intracranial vascular malformations in patients with
intracerebral haemorrhage") extracted four counts from one of its included trials:

**Yeung et al. 2009**, *Can J Neurol Sci* — doi:10.1017/S0317167100006533

| Source | TP | FP | FN | TN | Total N | Implied sensitivity | Implied specificity |
|---|---|---|---|---|---|---|---|
| Cells as extracted in the review | 20 | 3 | 0 | 24 | **47** | **100.0%** | 88.9% |
| Cells after re-extraction | 22 | 2 | 3 | 28 | **55** | 88.0% | 93.3% |
| Values printed in the primary paper (Table 1, "Overall") | — | — | — | — | **55** | **89%** | **92%** |

## Why the second two rows agree and the first does not

The paper reports 55 patients, 89% sensitivity and 92% specificity.

- Re-extracted cells: 22 / 25 = 88.0% sensitivity, 28 / 30 = 93.3% specificity. Consistent with
  the paper within rounding.
- Extracted cells: 20 / 20 = 100% sensitivity, 27 / 30 = 90% specificity, and a 47-patient sample
  that does not exist in the paper.

The review's version is internally coherent — 20/3/0/24 does give 100% and 88.9% — which is
exactly why it survives proofreading. It is only wrong against the source.

## Reproduce it

1. Read Table 1 of the primary paper. "Overall" row: sensitivity 89, specificity 92. The text
   states 55 patients (`45% (25/55)` for diagnostic yield).
2. Compute: 22/(22+3) = 0.880; 28/(28+2) = 0.933.
3. Compare with 20/(20+0) = 1.000 and 24/(24+3) = 0.889.

Or, with the harness:

```bash
python3 src/cells.py          # arithmetic self-test
```

and check the values by hand — this example is deliberately small enough that a script is not
required.

## Why this matters for the genre

The error is invisible from the review's own text, and invisible to a consistency checker, because
the review's arithmetic is self-consistent. Catching it required the primary document.

That is the central constraint of automated reproducibility auditing: **internal consistency checks
catch carelessness; only the source catches transcription.** Any tool that claims otherwise is
going to produce confident noise.
