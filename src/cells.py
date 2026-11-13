"""2x2 contingency-cell arithmetic used by the Second Opinion verifier.

Every number in a diagnostic meta-analysis is ultimately derived from four
integers per study: TP, FP, FN, TN. This module is the layer that must be
provably correct before anything else matters.
"""
import math


def metrics(tp, fp, fn, tn):
    for name, v in (("tp", tp), ("fp", fp), ("fn", fn), ("tn", tn)):
        if not isinstance(v, int) or v < 0:
            raise ValueError(f"{name} must be a non-negative int, got {v!r}")
    n1, n0 = tp + fn, fp + tn
    if n1 == 0 or n0 == 0:
        raise ValueError("degenerate table: a group has zero subjects")
    sens = tp / n1
    spec = tn / n0
    # Haldane-Anscombe correction for zero cells
    a, b, c, d = tp, fp, fn, tn
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    dor = (a * d) / (b * c)
    return {
        "n_diseased": n1, "n_healthy": n0,
        "sens": sens, "spec": spec,
        "lr_pos": sens / (1 - spec) if spec < 1 else math.inf,
        "lr_neg": (1 - sens) / spec if spec > 0 else math.inf,
        "dor": dor, "ln_dor": math.log(dor),
        "ln_dor_se": math.sqrt(1 / a + 1 / b + 1 / c + 1 / d),
    }


def pool_dl(effects, variances):
    """DerSimonian-Laird random-effects pooling on a log scale."""
    k = len(effects)
    if k == 0:
        raise ValueError("nothing to pool")
    w = [1 / v for v in variances]
    sw, sw2 = sum(w), sum(x * x for x in w)
    mu_fe = sum(wi * yi for wi, yi in zip(w, effects)) / sw
    q = sum(wi * (yi - mu_fe) ** 2 for wi, yi in zip(w, effects))
    c = sw - sw2 / sw
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    wr = [1 / (v + tau2) for v in variances]
    swr = sum(wr)
    mu = sum(wi * yi for wi, yi in zip(wr, effects)) / swr
    se = math.sqrt(1 / swr)
    return {"k": k, "est": mu, "se": se, "ci_lo": mu - 1.96 * se,
            "ci_hi": mu + 1.96 * se, "tau2": tau2, "q": q}


if __name__ == "__main__":
    # Regression tests against hand-computable values.
    m = metrics(90, 10, 10, 90)
    assert abs(m["sens"] - 0.9) < 1e-12, m
    assert abs(m["spec"] - 0.9) < 1e-12, m
    assert abs(m["dor"] - 81.0) < 1e-9, m

    # Zero-cell handling must not raise or produce inf/nan.
    z = metrics(40, 0, 5, 60)
    assert z["dor"] > 0 and math.isfinite(z["dor"]), z

    # Single-study pooling must return that study's estimate.
    p1 = pool_dl([1.0], [0.25])
    assert abs(p1["est"] - 1.0) < 1e-12 and p1["k"] == 1, p1

    # Pooling two identical studies: estimate unchanged, SE shrinks by sqrt(2).
    p2 = pool_dl([1.0, 1.0], [0.25, 0.25])
    assert abs(p2["est"] - 1.0) < 1e-12, p2
    assert abs(p2["se"] - math.sqrt(0.125)) < 1e-12, p2
    assert p2["tau2"] == 0.0, p2

    # Degenerate input must fail loudly, not silently.
    # n0 == 0 (no healthy subjects) must be rejected, not silently divided by zero.
    try:
        metrics(5, 0, 5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for degenerate table")

    # A table with a zero cell but valid groups must still compute (Haldane correction).
    assert math.isfinite(metrics(5, 0, 5, 10)["dor"])
    # Negative or non-integer cells must be rejected.
    for bad in ((-1, 0, 5, 5), (1.5, 2, 3, 4)):
        try:
            metrics(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")

    print("all cells.py tests passed")
    ex = metrics(34, 12, 8, 71)
    print("example table 34/12/8/71 ->",
          {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ex.items()})
