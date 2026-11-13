"""Validate the pooling engine against published pooled estimates.

Reads the trial-level cells (data/final_data.xlsx, fetched by fetch_data.py) and the
published pooled values (data/published_estimates.json). The published values are
anonymised, so validation is a blind nearest-value match: if the engine reproduces
the source study's estimator, most rows land within a tight tolerance.

Exit code is non-zero if the match rate falls below the published threshold, so this
can run in CI.
"""
import json, math, statistics, sys
from collections import defaultdict
import openpyxl

DATASET = "data/final_data.xlsx"
PUBLISHED = "data/published_estimates.json"
TOL = 0.01
MIN_PCT = 95.0


def as_int(x):
    try:
        v = int(float(x))
        return v if v >= 0 else None
    except (TypeError, ValueError):
        return None


def logit(x, n, eps=0.5):
    if n == 0:
        return None
    k, nn = x + eps, n + 2 * eps
    return math.log(k / (nn - k)), 1 / k + 1 / (nn - k)


def pool(items, fixed=False):
    y = [a for a, _ in items]
    v = [b for _, b in items]
    w = [1 / x for x in v]
    sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    if fixed or len(y) < 2:
        tau2 = 0.0
    else:
        q = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))
        c = sw - sum(x * x for x in w) / sw
        tau2 = max(0.0, (q - (len(y) - 1)) / c) if c > 0 else 0.0
    wr = [1 / (x + tau2) for x in v]
    return sum(wi * yi for wi, yi in zip(wr, y)) / sum(wr)


def inv(z):
    return 1 / (1 + math.exp(-z))


def main():
    rows = list(openpyxl.load_workbook(DATASET, read_only=True, data_only=True)
                .worksheets[0].iter_rows(values_only=True))[1:]
    groups = defaultdict(list)
    for r in rows:
        groups[(str(r[1]), str(r[13]))].append(r)

    pub = json.load(open(PUBLISHED))
    PARAMS = {"sensitivity": (14, (14, 16)), "specificity": (17, (15, 17))}
    ok = True
    for name, (num_c, den_cs) in PARAMS.items():
        computed = []
        for (sr, meta), rs in groups.items():
            items = []
            for r in rs:
                num = as_int(r[num_c])
                den = sum(as_int(r[c]) or 0 for c in den_cs)
                if num is None or den == 0:
                    continue
                z = logit(num, den)
                if z:
                    items.append(z)
            if items:
                computed.append(inv(pool(items)))
        diffs, matches = [], 0
        for row in pub[name]:
            best = min(computed, key=lambda c: abs(c - row["original"]))
            d = abs(best - row["original"])
            diffs.append(d)
            matches += d <= TOL
        pct = 100 * matches / len(pub[name])
        print(f"{name:12s} published={len(pub[name]):3d} matched={matches:3d} "
              f"({pct:5.1f}%)  median_abs_diff={statistics.median(diffs):.5f}  "
              f"max={max(diffs):.4f}")
        ok = ok and pct >= MIN_PCT

    # rank robustness
    dl, fe = [], []
    for (sr, meta), rs in groups.items():
        it_dl, it_fe = [], []
        for r in rs:
            num, den = as_int(r[14]), (as_int(r[14]) or 0) + (as_int(r[16]) or 0)
            if num is None or den == 0:
                continue
            z = logit(num, den)
            if z:
                it_dl.append(z)
                it_fe.append(z)
        if it_dl:
            dl.append(((sr, meta), inv(pool(it_dl))))
            fe.append(((sr, meta), inv(pool(it_fe, fixed=True))))
    top_dl = {k for k, _ in sorted(dl, key=lambda x: -x[1])[:30]}
    top_fe = {k for k, _ in sorted(fe, key=lambda x: -x[1])[:30]}
    print(f"rank robustness: {len(top_dl & top_fe)}/30 top meta-analyses unchanged "
          f"between DL and fixed-effect")

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
