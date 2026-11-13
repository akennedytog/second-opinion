"""Validation status for Second Opinion.

v0.1.0 reported "136/137 and 137/137" as validation. That was a nearest-value
match against anonymised published values. `src/matching_null_test.py` shows this
is vacuous: with 137 published values and 437 computed values, randomly generated
"published" values also match 100% of the time at tolerance 0.01. The observed
rate was BELOW the null mean.

This script therefore reports what is actually checkable and marks the rest BLOCKED.
It exits non-zero, so CI cannot pass on an unsupported claim.
"""
import json, sys
from collections import defaultdict
import openpyxl

DATASET = "data/final_data.xlsx"
PUBLISHED_COUNTS = {"flagged_trials": 338, "total_trials": 6173, "reviews_with_error": 34,
                    "total_reviews": 46}


def main():
    rows = list(openpyxl.load_workbook(DATASET, read_only=True, data_only=True)
                .worksheets[0].iter_rows(values_only=True))[1:]

    # --- Check 1: direct counts. These are checkable and are not a matching exercise. ---
    flagged = sum(1 for r in rows if str(r[22]).strip().upper() == "NO")
    reviews = {str(r[1]) for r in rows}
    reviews_with_error = {str(r[1]) for r in rows if str(r[22]).strip().upper() == "NO"}

    checks = [
        ("total trials", len(rows), PUBLISHED_COUNTS["total_trials"]),
        ("flagged trials", flagged, PUBLISHED_COUNTS["flagged_trials"]),
        ("total reviews", len(reviews), PUBLISHED_COUNTS["total_reviews"]),
        ("reviews with >=1 error", len(reviews_with_error),
         PUBLISHED_COUNTS["reviews_with_error"]),
    ]
    ok = True
    print("A. DIRECT RECOUNTS against the published figures")
    for name, got, want in checks:
        good = got == want
        ok = ok and good
        print(f"   {name:26s} dataset={got:6d}  published={want:6d}  "
              f"{'MATCH' if good else 'MISMATCH'}")
    print("   These establish only that the released file is consistent with the paper's")
    print("   own reported counts. They are not a test of the pooling engine.\n")

    # --- Check 2: pooling validation ---
    print("B. POOLING VALIDATION against published pooled estimates")
    print("   STATUS: BLOCKED")
    print("   Reason: the published values are anonymised ('Meta ID 1..N') with no mapping")
    print("   to review, outcome or dataset version. There is no verified correspondence to")
    print("   test against, so no correct/incorrect verdict can be computed.")
    print("   See src/matching_null_test.py: single-parameter nearest matching yields a null")
    print("   hit rate of 1.000; joint matching yields 50/137 observed against a null mean of")
    print("   40.9 (max 53). Neither establishes study-level reproduction.\n")

    # --- Check 3: guard rail ---
    print("C. GUARD RAIL")
    print("   Any claim of the form 'reproduces N/M published estimates' is unsupported and")
    print("   must not appear in README, preprint, blog or correspondence until a verified")
    print("   mapping exists.\n")

    print("RESULT:", "counts PASS, validation BLOCKED" if ok else "counts FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
