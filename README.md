# Second Opinion

A verifier for the arithmetic of published diagnostic meta-analyses.

> **⚠️ Read [CORRECTION.md](CORRECTION.md) first.** v0.1.0 claimed "136/137" and "137/137"
> reproduction of published pooled estimates. Those claims were unsupported: they came from
> nearest-value matching against anonymised values and are indistinguishable from chance
> (`src/matching_null_test.py` demonstrates a null hit rate of 1.000). They have been withdrawn.

## Current status: development halted pending validation

This repository is a working extraction and pooling library. It is **not** a validated audit tool,
and no error rate, reproduction rate, or accuracy figure should be taken from it.

## What is actually supported

| Claim | Status |
|---|---|
| The released dataset's counts match the paper it accompanies | **Supported** — 6,173 trials, 338 flagged (5.48%), 46 reviews, 34 with ≥1 error. Direct recounts. |
| Nearest-value matching against anonymised published values is invalid | **Supported** — null hit rate 1.000 for single parameters; joint matching inside the null range. |
| The pooling is validated against published estimates | **BLOCKED** — no verified mapping between published values and meta-analyses exists. |
| Any specific review contains an error | **Not established** — see `examples/yeung-2009.md`, substantially withdrawn. |
| Automated extraction finds real errors at scale | **Not established** — no independent reference labels; 96% of table rows contain no cells (manual inspection of 7 tables). |

## What this does not do

- It does not produce an error rate for a field, a journal, or an author.
- It cannot detect a transcription error when a review prints only percentages.
- It does not attribute intent. "Does not reproduce" is not "is wrong" and is not misconduct.

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.9+.

## Run

```bash
python3 src/fetch_data.py         # fetch the dataset from OSF (not redistributed here)
python3 src/model_check.py        # validation status: recounts pass, pooling BLOCKED
python3 src/matching_null_test.py # why nearest-value matching cannot serve as validation
python3 src/cells.py              # arithmetic self-test
python3 tests/test_extract.py     # synthetic extraction tests (behaviour, not performance)
python3 src/extract.py PMC13456766  # extraction on one open-access paper
```

## Data

> Huang Z, Tian Y, Gong P, Zhang T, Tang H. *Data Extraction Errors and Diagnostic Conclusions of
> Meta-Analyses: A Systematic Review.* JAMA Network Open. 2026;9(10):e2640850.
> doi:10.1001/jamanetworkopen.2026.40850 · data: https://osf.io/pb3q2/

`fetch_data.py` downloads it at run time. We do not redistribute the file: the OSF project carries
no licence tag (`node_license: null`), so fetching does not resolve data-use permissions for
redistribution or commercial use. Written terms are required before either.

**Expected checksum** (verify after fetch):

```
sha256  2855274585d14feb7df40df2a96ebe284ab968454ca9325c7fed0a4f4d4c0151
size    1,006,491 bytes
```

## Reproducibility notes

- Recorded 2026-11-12, Python 3.9.6, `openpyxl>=3.1`.
- Clean-environment check: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
  then `python3 src/model_check.py` — reproduces the output above.
- The dataset is fetched, not vendored, so a checksum mismatch means the OSF file changed and every
  number in this repository needs re-running.

## Method

DerSimonian–Laird on logit-transformed sensitivity and specificity, with a Haldane–Anscombe
correction for zero cells. This is a univariate approximation to the bivariate models many reviews
use. It has **not** been shown to reproduce any published bivariate analysis.

## Licence

MIT for the code. The dataset is not ours to license.
