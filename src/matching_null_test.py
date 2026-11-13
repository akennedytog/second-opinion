"""Is the 136/137 "validation" distinguishable from chance?

With 137 published values drawn from the same space as 438 computed values, a
nearest-value match at tolerance 0.01 will almost always succeed even if the two
sets are unrelated. This script measures that directly.

1. Observed nearest-match hit rate.
2. Null distribution: replace each published value with a draw from the computed
   distribution (i.e. destroy any true correspondence) and recompute. 500 reps.
3. Pair matching: match on (sensitivity, specificity) jointly with a uniqueness
   margin, which is far harder to satisfy by chance. Compare to its own null.
"""
import json, math, random, statistics
from collections import defaultdict
import openpyxl

random.seed(20261112)


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


def pool(items):
    if not items:
        return None
    y = [a for a, _ in items]
    v = [b for _, b in items]
    w = [1 / x for x in v]
    sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    if len(y) < 2:
        tau2 = 0.0
    else:
        q = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))
        c = sw - sum(x * x for x in w) / sw
        tau2 = max(0.0, (q - (len(y) - 1)) / c) if c > 0 else 0.0
    wr = [1 / (x + tau2) for x in v]
    return sum(wi * yi for wi, yi in zip(wr, y)) / sum(wr)


def inv(z):
    return 1 / (1 + math.exp(-z))


rows = list(openpyxl.load_workbook("data/final_data.xlsx", read_only=True, data_only=True)
            .worksheets[0].iter_rows(values_only=True))[1:]
groups = defaultdict(list)
for r in rows:
    groups[(str(r[1]), str(r[13]))].append(r)

computed = {}   # (sr, meta) -> (sens, spec)
for (sr, meta), rs in groups.items():
    sens_items, spec_items = [], []
    for r in rs:
        tp, fn = as_int(r[14]), as_int(r[16])
        fp, tn = as_int(r[15]), as_int(r[17])
        if None in (tp, fn, fp, tn):
            continue
        a = logit(tp, tp + fn)
        b = logit(tn, fp + tn)
        if a and b:
            sens_items.append(a)
            spec_items.append(b)
    if sens_items and spec_items:
        computed[(sr, meta)] = (inv(pool(sens_items)), inv(pool(spec_items)))

pub = json.load(open("data/published_estimates.json"))
ps = [r["original"] for r in pub["sensitivity"]]
pc = [r["original"] for r in pub["specificity"]]
cs = [v[0] for v in computed.values()]
cc = [v[1] for v in computed.values()]

print(f"computed meta-analyses: {len(computed)}")
print(f"published rows: sens={len(ps)} spec={len(pc)}\n")

# ---- 1. observed vs null, single parameter ----
def hit_rate(published, computed_vals, tol=0.01):
    return sum(1 for p in published if min(abs(p - c) for c in computed_vals) <= tol) / len(published)


obs_s = hit_rate(ps, cs)
obs_c = hit_rate(pc, cc)

null_s, null_c = [], []
for _ in range(500):
    fake_s = random.choices(cs, k=len(ps))
    fake_c = random.choices(cc, k=len(pc))
    null_s.append(hit_rate(fake_s, cs))
    null_c.append(hit_rate(fake_c, cc))

print("SINGLE-PARAMETER NEAREST MATCH (the method used in v0.1.0)")
print(f"  sensitivity observed {obs_s:.3f} | null mean {statistics.mean(null_s):.3f} "
      f"sd {statistics.stdev(null_s):.3f} | max {max(null_s):.3f}")
print(f"  specificity observed {obs_c:.3f} | null mean {statistics.mean(null_c):.3f} "
      f"sd {statistics.stdev(null_c):.3f} | max {max(null_c):.3f}")
print("  => if observed sits inside the null distribution, the match proves nothing.\n")

# ---- 2. pair matching with uniqueness margin ----
def pair_match(rows_pub, tol=0.01, margin=0.005):
    """Greedy unique assignment on the joint (sens, spec) distance."""
    cands = []
    for i, (s, c) in enumerate(rows_pub):
        for key, (cs_, cc_) in computed.items():
            d = max(abs(cs_ - s), abs(cc_ - c))
            if d <= tol:
                cands.append((d, i, key))
    cands.sort()
    used_i, used_k, matched = set(), set(), 0
    for d, i, key in cands:
        if i in used_i or key in used_k:
            continue
        # uniqueness: reject if a second candidate is within margin of this distance
        rivals = [x for x in cands if x[1] == i and x[2] != key and x[0] - d < margin]
        if rivals:
            continue
        used_i.add(i)
        used_k.add(key)
        matched += 1
    return matched


pair_rows = list(zip(ps, pc))
obs_pair = pair_match(pair_rows)
null_pair = []
for _ in range(200):
    shuffled = pair_rows[:]
    random.shuffle(shuffled)
    fake = [(random.choice(cs), random.choice(cc)) for _ in shuffled]
    null_pair.append(pair_match(fake))

print("JOINT (SENSITIVITY, SPECIFICITY) UNIQUE MATCH")
print(f"  observed pairs matched: {obs_pair}/{len(pair_rows)}")
print(f"  null mean {statistics.mean(null_pair):.1f} sd {statistics.stdev(null_pair):.1f} "
      f"max {max(null_pair)}")
print("  => a margin above the null range is the minimum bar for calling this validation.")

json.dump({"observed_single_sens": obs_s, "observed_single_spec": obs_c,
           "null_single_sens_mean": statistics.mean(null_s),
           "null_single_spec_mean": statistics.mean(null_c),
           "observed_pairs": obs_pair, "null_pairs_mean": statistics.mean(null_pair),
           "null_pairs_max": max(null_pair), "n_pairs": len(pair_rows)},
          open("data/matching_null_test.json", "w"), indent=1)
