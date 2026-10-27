"""Lecture 6, experiment (c): the model judge against the code metrics, and the tone judge against our labels.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/judge_eval.py

1. For every transcript of the main runs (graph, tool loop, naive: 180 conversations) the judge (gemini-3.8-flash,
   cassette L6_judge) answers, from the chat alone, the questions five code metrics answer from the ERP. We count
   how often they agree, per question, with Cohen's kappa, and keep the disagreements.
2. The tone judge on the 30 transcripts the course team labelled (bahi/evals/labels/tone_30.json; course-team labels,
   to be confirmed by Rajat) -> agreement and kappa. Then the tone judge on every transcript, and on the curt bot.
Writes logs/judge.json.
"""
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor

from bahi.evals import judge, suite
from bahi.evals.stats import agreement
from bahi.llm import LLM

LOGS = pathlib.Path(__file__).parent / "logs"
LABELS = pathlib.Path(judge.__file__).parent / "labels" / "tone_30.json"
llm = LLM("gemini:gemini-3.8-flash", cassette="L6_judge")


def load(tag):
    return json.loads((LOGS / f"suite_{tag}.json").read_text())["cases"]


recs = [(tag, r) for tag in ("graph", "loop", "naive") for r in load(tag)]


def checks(item):
    tag, r = item
    j = judge.judge_checks(suite.BY_ID[r["id"]], r["turns"], llm)
    return {"run": tag, "id": r["id"], "judge": j, "code": judge.code_view(r)}


with ThreadPoolExecutor(12) as ex:
    rows = list(ex.map(checks, recs))
per_q = {}
for q in judge.CHECK_KEYS:
    pairs = [(row["judge"][q], row["code"][q]) for row in rows if row["code"][q] is not None and row["judge"][q] is not None]
    ag = agreement([p[0] for p in pairs], [p[1] for p in pairs])
    dis = [{"run": row["run"], "id": row["id"], "judge": row["judge"][q], "code": row["code"][q], "reason": row["judge"]["reason"]}
           for row in rows if row["code"][q] is not None and row["judge"][q] is not None and row["judge"][q] != row["code"][q]]
    per_q[q] = {**ag, "code_metric": judge.COMPARE[q][0], "disagreements": dis}
    print(q, ag)

# ---- tone, against the course team's labels
labels = json.loads(LABELS.read_text())
by = {(t, r["id"]): r for t, r in recs}
bots = {}
for p in sorted(LOGS.glob("bots_*.json")):
    if p.name != "bots_p.json":
        d = json.loads(p.read_text())
        bots.update(d)


def turns_for(item):
    if item["run"].startswith("bot:"):
        b = bots[item["run"][4:]]
        return next(c for c in b["cases"] if c["id"] == item["id"])["turns"]
    return by[(item["run"], item["id"])]["turns"]


def tone(item):
    j = judge.judge_tone(turns_for(item), llm)
    return {**{k: item[k] for k in ("run", "id", "label", "note")}, "judge_ok": j["tone_ok"], "judge_reason": j["reason"],
            "worst_line": j["worst_line"]}


with ThreadPoolExecutor(12) as ex:
    tone_rows = list(ex.map(tone, labels["items"]))
tone_ag = agreement([r["label"] == "ok" for r in tone_rows], [bool(r["judge_ok"]) for r in tone_rows])
print("tone vs labels", tone_ag)

# ---- tone on every transcript (the judge's view only)
allt = [{"run": t, "id": r["id"], "label": "", "note": ""} for t, r in recs]
if "curt_tone" in bots:
    allt += [{"run": "bot:curt_tone", "id": c["id"], "label": "", "note": ""} for c in bots["curt_tone"]["cases"]]
if "reference" in bots:
    allt += [{"run": "bot:reference", "id": c["id"], "label": "", "note": ""} for c in bots["reference"]["cases"]]
with ThreadPoolExecutor(12) as ex:
    all_tone = list(ex.map(tone, allt))
tone_rate = {}
for run in dict.fromkeys(x["run"] for x in all_tone):
    xs = [x for x in all_tone if x["run"] == run]
    tone_rate[run] = {"n": len(xs), "tone_ok": sum(1 for x in xs if x["judge_ok"])}
print("tone ok by run", tone_rate)
out = {"model": llm.model, "checks": {"rows": rows, "per_question": per_q}, "tone_labels": {"labeller": labels["labeller"],
       "agreement": tone_ag, "rows": tone_rows}, "tone_all": {"by_run": tone_rate, "rows": all_tone},
       "cost": llm.totals()}
print("judge cost", llm.totals())
(LOGS / "judge.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
