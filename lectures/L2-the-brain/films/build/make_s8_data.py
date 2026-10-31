#!/usr/bin/env python3
"""Light, stdlib only: films/build/data/s8_weights_data.json for the s8_weights film, from
  - the corpus generator ledgerline/ledgerline/course/l2/corpus.py (rebuilt and checked against northbridge_corpus.md),
  - experiments/logs/tinygpt.json (the logged run),
  - data/s8_weights_tiny.json (the same run re-recorded on Modal by capture_params.py; its loss curve must match the log).
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L2 = os.path.dirname(os.path.dirname(HERE))
COURSE = os.path.dirname(os.path.dirname(L2))
PKG = os.path.join(COURSE, "ledgerline", "ledgerline", "course", "l2")
sys.path.insert(0, PKG)
import corpus  # noqa: E402

text = open(os.path.join(PKG, "northbridge_corpus.md")).read()
assert corpus.build() == text
LOG = json.load(open(os.path.join(L2, "experiments", "logs", "tinygpt.json")))
TINY = json.load(open(os.path.join(HERE, "data", "s8_weights_tiny.json")))
assert [(c["step"], c["train"]) for c in TINY["curve"]] == [(c["step"], c["train"]) for c in LOG["curve"]], "re-run differs from the log"
assert len(text) == LOG["corpus_chars"] == 122069

# ---- which kind of text every character belongs to (0 generated, 1 e-mail, 2 policy, 3 separator)
notes = corpus.notes(random.Random(7), 700)
pol = corpus.policy_lines()
kind = bytearray([3]) * len(text)
spans = {0: 0, 1: 0, 2: 0}
docs = {0: set(notes), 1: set(corpus.EMAILS), 2: set(pol)}
pos = 0
rng = random.Random(7)
corpus.notes(rng, 700)
parts = notes + corpus.EMAILS * 3 + pol * 2
rng.shuffle(parts)
for p in parts:
    i = text.index(p, pos)
    k = 0 if p in docs[0] else 1 if p in docs[1] else 2
    for j in range(i, i + len(p)):
        kind[j] = k
    spans[k] += len(p)
    pos = i + len(p)
assert sum(spans.values()) + kind.count(3) == len(text)

W = TINY["batch1"]["starts"][TINY["batch1"]["pick"]]
assert text[W:W + 128] == TINY["batch1"]["windows"][TINY["batch1"]["pick"]]
S0, S1 = W - 4900, W + 228


def kinds_of(a, b):
    return "".join(str(kind[i]) for i in range(a, b))


stock = [l for l in notes if l.startswith("Stores")]
gen_kinds = {}
for l in notes:
    k = l.split(",")[0].split(" ")[0]
    gen_kinds[k] = gen_kinds.get(k, 0) + 1
out = {
    "source": "ledgerline/ledgerline/course/l2/corpus.py (seed 7) -> northbridge_corpus.md; experiments/logs/tinygpt.json; "
              "data/s8_weights_tiny.json (capture_params.py re-run, loss curve identical to the log)",
    "corpus": {"chars": len(text), "words": len(text.split()), "distinct": len(set(text)), "first_day": LOG["corpus_first_day"],
               "last_day": LOG["corpus_last_day"], "train_chars": TINY["train_chars"], "val_chars": TINY["val_chars"],
               "kinds": [
                   {"name": "Generated from the seed data", "docs": len(notes), "copies": 1, "chars": spans[0],
                    "breakdown": gen_kinds},
                   {"name": "E-mails between the staff", "docs": len(corpus.EMAILS), "copies": 3, "chars": spans[1]},
                   {"name": "Purchase policy, supplier policy, approval matrix", "docs": len(pol), "copies": 2, "chars": spans[2]}],
               "separator_chars": kind.count(3),
               "count_5400_bat500": text.count("Manchester stores has 5,400")},
    "snippets": {
        "generated": [next(l for l in stock if "BAT-500" in l), next(l for l in stock if "BAT-500" not in l and len(l) <= 100),
                      min((l for l in notes if l.startswith("Approval")), key=len)],
        "email": corpus.EMAILS[0],
        "policy": [l for l in pol if l.startswith("5.1")][0:1] + [l for l in pol if l.startswith("5.3")][0:1]},
    "strip": {"start": S0, "end": S1, "window_at": W, "text": text[S0:S1], "kinds": kinds_of(S0, S1)},
    "batch": {"starts": TINY["batch1"]["starts"], "pick": TINY["batch1"]["pick"], "windows": TINY["batch1"]["windows"],
              "kinds": [kinds_of(s, s + 128) for s in TINY["batch1"]["starts"]]},
    "chars": TINY["chars"],
    "example": {"pos": 38},
    "full_before": TINY["full_before"][38], "full_after": TINY["full_after"][38],
    "row_before": TINY["probs_before"][38], "row_after": TINY["probs_after"][38],
    "digit_after": TINY["probs_after"][29],
    "patch": TINY["patch"], "track_weight": TINY["track_weight"], "step1": TINY["step1"],
    "log": {k: LOG[k] for k in ("config", "params", "uniform_loss", "train_seconds_cpu2", "curve", "sample_untrained",
                                "stock_prompt", "stock_samples", "stock_figures", "stock_5400")},
    "sample_trained": LOG["samples"]["Stores, 26 Oct 2026: BAT-500 in Manchester stores,"]["0.8"],
}
ex = out["row_before"]
assert ex["inp"] == " " and ex["target"] == "h"
json.dump(out, open(os.path.join(HERE, "data", "s8_weights_data.json"), "w"), ensure_ascii=False, indent=0)
print("ok", spans, kind.count(3), out["corpus"]["count_5400_bat500"], W, out["row_before"]["p_target"], out["row_after"]["p_target"])
