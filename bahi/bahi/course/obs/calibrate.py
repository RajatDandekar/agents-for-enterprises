"""Calibrating an LLM judge against code checks, from first principles. Pure Python, no model is called here.

    from bahi.course.obs.calibrate import confusion, report
    m = confusion(rows, truth="code", pred="judge")    # {"tp":63, "fn":9, "fp":24, "tn":48}
    report(m)                                           # agreement, Cohen's kappa, true-pass rate, true-fail rate ...

The code check reads Bahi's tables, so we treat it as the truth for "did the job really get done safely".
A judge's verdict is a prediction of it. Vocabulary (pass = the positive class):
  tp  both say pass                      fn  code pass, judge fail  (the judge is stricter than the truth)
  fp  code fail, judge pass  (the judge is kinder: the dangerous cell, a broken run waved through)
  tn  both say fail
"""
from __future__ import annotations


def confusion(rows: list[dict], truth: str = "code", pred: str = "judge") -> dict:
    m = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "skipped": 0}
    for r in rows:
        t, p = r.get(truth), r.get(pred)
        if t is None or p is None:
            m["skipped"] += 1
            continue
        m[("t" if t == p else "f") + ("p" if p else "n")] += 1
    return m


def report(m: dict) -> dict:
    tp, fn, fp, tn = m["tp"], m["fn"], m["fp"], m["tn"]
    n = tp + fn + fp + tn
    po = (tp + tn) / n if n else 0.0                                   # observed agreement
    pe = (((tp + fn) * (tp + fp)) + ((fp + tn) * (fn + tn))) / (n * n) if n else 0.0  # agreement by chance
    kappa = (po - pe) / (1 - pe) if pe < 1 else 0.0
    return {"n": n, "agree": tp + tn, "agreement": round(po, 3), "chance_agreement": round(pe, 3),
            "kappa": round(kappa, 3),
            "true_pass_rate": round(tp / (tp + fn), 3) if tp + fn else None,   # of runs that passed, judge said pass
            "true_fail_rate": round(tn / (tn + fp), 3) if tn + fp else None,   # of runs that failed, judge said fail
            "judge_pass_precision": round(tp / (tp + fp), 3) if tp + fp else None,  # when judge says pass, how often true
            "missed_failures": fp, "false_alarms": fn,
            "code_pass_rate": round((tp + fn) / n, 3) if n else None, "judge_pass_rate": round((tp + fp) / n, 3) if n else None}


def kappa_label(k: float) -> str:
    """Landis and Koch's usual words for kappa (a convention, not a law)."""
    return ("poor" if k < 0 else "slight" if k < .2 else "fair" if k < .4 else "moderate" if k < .6
            else "substantial" if k < .8 else "almost perfect")
