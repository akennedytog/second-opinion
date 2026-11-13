# Second Opinion

Verifies the arithmetic inside published diagnostic meta-analyses and reports any
disagreement with a source line.

It does not judge science. It checks whether the numbers a paper prints are consistent with the
numbers it reports, and whether a pooled estimate follows from the cells that produced it.

## What is established

| Claim | Evidence |
|---|---|
| Reproduces published pooled estimates | sensitivity 136/137 within 0.01 (median error 0.00042); specificity 137/137 (median 0.00013) |
| Ranking is model-robust | DerSimonian–Laird vs fixed-effect top-30 overlap 25/30 |
| Finds a cell that contradicts its source paper | `examples/yeung-2009.md` |
| Refuses to guess | `extract.py` labels every row `resolved` / `mismatch` / `resolved_ambiguous_order` / `unparseable` |

## What this does *not* do

- It does not produce an error rate for a field, a journal, or an author.
- It cannot detect a transcription error when a review prints only percentages, because a wrong
  percentage and a right percentage are indistinguishable without the primary paper.
- It does not attribute intent. "Does not reproduce" is not "is wrong" and is certainly not
  "is misconduct."

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.9+.

## Quickstart

```bash
# 1. fetch the validation dataset (open, not redistributed here)
python3 src/fetch_data.py

# 2. validate the pooling against published estimates
python3 src/model_check.py

# 3. self-test the contingency arithmetic
python3 src/cells.py

# 4. extract 2x2 cells from open-access full text
python3 src/extract.py PMC13456766
```

## Data

The validation target is the trial-level dataset released with:

> Huang Z, Tian Y, Gong P, Zhang T, Tang H. *Data Extraction Errors and Diagnostic Conclusions of
> Meta-Analyses: A Systematic Review.* JAMA Network Open. 2026;9(10):e2640850.
> doi:10.1001/jamanetworkopen.2026.40850 · data: https://osf.io/pb3q2/

`fetch_data.py` downloads it from OSF at run time. **We do not redistribute the file**: the OSF
project carries no explicit licence tag, so we fetch rather than mirror. If you intend commercial
use, confirm terms with the corresponding author first.

## Method

Pooling is DerSimonian–Laird on logit-transformed sensitivity and specificity, with a
Haldane–Anscombe correction for zero cells. This is a univariate approximation to the bivariate
models many reviews use. The validation in `model_check.py` compares against a source study that
re-analysed all meta-analyses with a common estimator, so the agreement demonstrates reproduction
of *that* estimator — not of each review's original bivariate output.

## Licence

MIT for the code. The dataset is not ours to license; see above.
