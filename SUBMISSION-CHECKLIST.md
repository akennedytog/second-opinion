# Submission checklist — HALTED

**Nothing goes public.** The project is on hold at the validation stage.

## Blocked on

| Blocker | Why it stops everything | What unblocks it |
|---|---|---|
| No verified mapping between published pooled values and meta-analyses | Without it, no pool of results can be validated. Nearest-value matching is provably invalid (`src/matching_null_test.py`). | Request the mapping from the corresponding author (draft email ready, unsent). |
| No independent reference labels | Cannot measure false positives, false negatives, or coverage against ground truth. | A hand-adjudicated gold set of ~50 rows by someone with clinical/statistical expertise. |
| Primary documents at 12–45% open access | The dominant error class needs the source papers. | Institutional access, or restrict claims to the open subset and report coverage. |
| Review full text unreachable (HTTP 412) | We never saw the review whose data we were discussing. | Institutional access. |

## Completed before the halt

- [x] Repo scaffolded, MIT licensed, CI-able
- [x] Correction notice written and linked from README
- [x] Invalid matching test pinned as code, not prose
- [x] Explicit headers now authoritative in the extractor; ambiguity abstains
- [x] Synthetic behaviour tests (6 passing)
- [x] Yeung 2009 example re-checked against the paper — substantially withdrawn
- [x] Header-defect finding withdrawn as unsubstantiated

## Do not do, at all

- Do not publish, submit, or send anything in this repository's `PREPRINT-DRAFT.md`,
  `BLOG-POST.md`, or `COURTESY-EMAIL.md`.
- Do not create a release or tag.
- Do not describe any number as a validation, a reproduction rate, or an error rate.
- Do not mirror the OSF dataset until written terms exist.
- Do not approach a journal or a client with this until the first two blockers clear.

## Before any future release

1. Verified mapping, or an explicit statement that validation is impossible and the paper is a
   methods critique only.
2. A gold set adjudicated by someone qualified, with precision/recall/abstention reported.
3. A null distribution reported alongside every agreement statistic.
4. Independent review of the manuscript by a statistician who has not worked on it.
5. Check venue policy on AI-assisted drafting before submission.
