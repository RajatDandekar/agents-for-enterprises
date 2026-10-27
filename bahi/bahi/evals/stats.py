"""Small statistics for the inspector: intervals, percentiles and agreement. Standard library only."""
from __future__ import annotations

import math


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for k passes out of n. Better than p ± 1.96·sqrt(p(1-p)/n) when p is near 0 or 1."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def percentile(xs: list[float], q: float) -> float:
    """Nearest-rank percentile (q in 0..100): the smallest value with at least q% of the values at or below it."""
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return 0.0
    rank = max(1, math.ceil(q / 100 * len(xs)))
    return xs[rank - 1]


def agreement(a: list[bool], b: list[bool]) -> dict:
    """Raw agreement and Cohen's kappa between two raters on the same yes/no items."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if not n:
        return {"n": 0, "agree": 0, "rate": None, "kappa": None}
    agree = sum(1 for x, y in pairs if x == y)
    po = agree / n
    pa = sum(1 for x, _ in pairs if x) / n
    pb = sum(1 for _, y in pairs if y) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = None if pe == 1 else (po - pe) / (1 - pe)
    both = {"yes_yes": sum(1 for x, y in pairs if x and y), "yes_no": sum(1 for x, y in pairs if x and not y),
            "no_yes": sum(1 for x, y in pairs if not x and y), "no_no": sum(1 for x, y in pairs if not x and not y)}
    return {"n": n, "agree": agree, "rate": round(po, 3), "kappa": None if kappa is None else round(kappa, 3), **both}
