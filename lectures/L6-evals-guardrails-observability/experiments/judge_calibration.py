"""Judge calibration (Lecture 6, Section 2): three judges against labels, on 56 replies (40 real, 16 planted wrong).

    tools/mrun.sh .../l6_modal.py --script judge_calibration.py

Judges (all claude-haiku-5-5, ledgerline.course.l6.judges):
    naive      "Is this reply helpful, accurate and professional?", the reply alone
    specific   the task's one criterion, no evidence
    grounded   the task's criterion + the tool results the agent saw (+ memory), reason first, binary
Measures per judge: agreement with the labels, how many planted wrong replies it caught (its recall on "fail"), how many
correct replies it failed (false alarms), Cohen's kappa. Writes logs/judge_calibration.json.
"""
import json

from _common import LOGS, now, pmap, spend, write

from ledgerline.course.l6 import calibration as CAL
from ledgerline.course.l6.judges import judge
from ledgerline.course.l6.suite import BY_ID

rows = {}
for tag, f in (("good", "suite_good_k3.json"), ("thursday", "suite_thursday_k1.json")):
    for r in json.loads((LOGS / f).read_text())["rows"]:
        rows[(tag, r["task"], r["rep"])] = r
items = []
for k in CAL.REAL:
    r = rows[k]
    items.append({"id": "/".join(map(str, k)), "kind": "real", "task": k[1], "reply": r["turns"][-1]["reply"], "label": CAL.LABELS[k],
                  "evidence": r["evidence"], "user": " / ".join(BY_ID[k[1]]["turns"]), "note": CAL.NOTES.get(k, "")})
skipped = []
for base, old, new in CAL.PLANTED:
    r = rows[base]
    rep = r["turns"][-1]["reply"]
    if old not in rep:
        skipped.append({"base": "/".join(map(str, base)), "old": old})
        continue
    items.append({"id": "planted:" + "/".join(map(str, base)) + f":{old}->{new}", "kind": "planted", "task": base[1],
                  "reply": rep.replace(old, new), "label": False, "evidence": r["evidence"],
                  "user": " / ".join(BY_ID[base[1]]["turns"]), "note": f"planted: '{old}' -> '{new}'"})


def run(it):
    out = {}
    rub = BY_ID[it["task"]]["words"]
    for style in ("naive", "specific", "grounded"):
        if style == "naive":
            v = judge(rub, it["reply"], None, it["user"], style="naive", cassette="L6E_calib", mode="record")
        elif style == "specific":
            v = judge(rub, it["reply"], None, it["user"], style="grounded", cassette="L6E_calib", mode="record")
        else:
            v = judge(rub, it["reply"], it["evidence"], it["user"], style="grounded", cassette="L6E_calib", mode="record")
        out[style] = {"pass": v["pass"], "reason": v["reason"][:300], "usd": v["usd"]}
    return out


res = pmap(run, items, workers=12)
for it, r in zip(items, res):
    it["judges"] = r
    it.pop("evidence")


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


labels = [it["label"] for it in items]
summary = {}
for style in ("naive", "specific", "grounded"):
    pred = [it["judges"][style]["pass"] for it in items]
    tp = sum(1 for l, p in zip(labels, pred) if l and p)
    tn = sum(1 for l, p in zip(labels, pred) if not l and not p)
    fp = sum(1 for l, p in zip(labels, pred) if not l and p)      # passed a wrong reply
    fn = sum(1 for l, p in zip(labels, pred) if l and not p)      # failed a right reply
    summary[style] = {"agreement": round((tp + tn) / len(items), 3), "kappa": kappa(labels, pred),
                      "caught_planted": tn, "planted": labels.count(False), "missed_planted": fp,
                      "false_alarms": fn, "real": labels.count(True),
                      "confusion": {"label_pass_judge_pass": tp, "label_pass_judge_fail": fn,
                                    "label_fail_judge_pass": fp, "label_fail_judge_fail": tn}}
usd = sum(j["usd"] for it in items for j in it["judges"].values())
write("judge_calibration.json", {"at": now(), "judge_model": "claude-haiku-5-5", "items": len(items), "skipped_plants": skipped,
                                 "summary": summary, "rows": items, "usd": round(usd, 5)})
spend("judge_calibration", usd, 3 * len(items), 0, 0, "claude-haiku-5-5", "3 judges x items")
print(json.dumps(summary, indent=1), "skipped", skipped)
