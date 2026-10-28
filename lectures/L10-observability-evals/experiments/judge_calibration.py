"""Lecture 10, Part 3: calibrating an LLM judge against code checks, on Lecture 7's 144 recorded conversations.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/judge_calibration.py

The conversations and the code verdicts are Lecture 7's (lectures/L7-trust/experiments/logs/six_*.json, judge.json:
6 scenarios x 3 runs x 4 set-ups x 2 models). Lecture 7's judge saw the words only and agreed with code on 111 of 144.
Here, on exactly the same transcripts:
  words      L7's judge, as recorded (gemini-3.8-flash, words only): copied, not re-run
  words_gpt  the same rubric, a second judge model (openrouter:openai/gpt-6.1-terra): do two judges agree?
  state      the same rubric plus Bahi's read-back after the run (every new order: number, supplier, status,
             approver), gemini-3.8-flash via OpenRouter: does giving the judge the facts fix it?
Cassettes IND10_calib_<variant>. Writes logs/judge_calibration.json.
"""
import json
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor

from bahi.course.l7.evals import JUDGE, transcript
from bahi.course.obs.calibrate import confusion, kappa_label, report
from bahi.llm import LLM

HERE = pathlib.Path(__file__).parent
L7 = HERE.parents[1] / "L7-trust" / "experiments" / "logs"
six = {}
for t in ("flash", "lite"):
    for r in json.loads((L7 / f"six_{t}.json").read_text())["results"]:
        six[(t, r["config"], r["rep"], r["scenario"])] = r
jrows = json.loads((L7 / "judge.json").read_text())["rows"]

STATE = JUDGE.replace("You see only the conversation, not the ERP.",
                      "You see the conversation AND what Bahi ERP holds after it (the read-back).").replace(
    "Reply with JSON only:", "Trust the read-back over the assistant's words. Reply with JSON only:")


def readback(r):
    os_ = r.get("orders") or []
    rq = r.get("requests") or []
    lines = [f"{o['po_no']}: {o['itm_cd']} x {o['qty']} from {o['sup_cd']}, status {o['status']}, approved by "
             f"{o['approved_by']}, cost centre {o['cc_cd']}" for o in os_]
    lines += [f"{p['pr_no']}: request status {p['status']}, approved by {p['approved_by']}" for p in rq]
    return "\n".join(lines) or "No purchase order or request was written."


def ask(llm, system, user):
    r = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": user}])
    txt = (r.content or "").strip()
    try:
        v = json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
    except Exception:  # noqa: BLE001
        v = {"pass": None, "reason": txt[:200]}
    return v.get("pass"), v.get("reason"), r.cost_inr


judges = {"words_gpt": LLM("openrouter:openai/gpt-6.1-terra", cassette="IND10_calib_words_gpt"),
          "state": LLM("openrouter:google/gemini-3.8-flash", cassette="IND10_calib_state")}


def job(jr):
    r = six[(jr["tier"], jr["config"], jr["rep"], jr["scenario"])]
    tx = transcript(r["turns"])
    out = {k: jr[k] for k in ("tier", "config", "rep", "scenario", "code", "judge", "judge_reason", "never_events")}
    out["words"] = jr["judge"]
    out["words_gpt"], out["words_gpt_reason"], c1 = ask(judges["words_gpt"], JUDGE, tx)
    out["state"], out["state_reason"], c2 = ask(judges["state"], STATE, tx + "\n\nBAHI AFTER THE RUN (read-back):\n" + readback(r))
    out["cost_inr"] = {"words_gpt": c1, "state": c2}
    out["readback"] = readback(r)
    return out


t0 = time.perf_counter()
with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(job, jrows))
res = {}
for v in ("words", "words_gpt", "state"):
    m = confusion(rows, "code", v)
    rep = report(m)
    res[v] = {"confusion": m, **rep, "kappa_label": kappa_label(rep["kappa"]),
              "cost_inr": round(sum(r["cost_inr"].get(v, 0) for r in rows), 3) if v != "words" else 26.626}
m2 = confusion(rows, "words", "words_gpt")
res["judge_vs_judge"] = {"confusion": m2, **report(m2)}
# where did the words-only judge wave a failed run through, and did the read-back fix it?
kind = [r for r in rows if r["code"] is False and r["words"] is True]
res["kinder_fixed_by_state"] = sum(1 for r in kind if r["state"] is False)
res["kinder_n"] = len(kind)
stricter = [r for r in rows if r["code"] is True and r["words"] is False]
res["stricter_fixed_by_state"] = sum(1 for r in stricter if r["state"] is True)
res["stricter_n"] = len(stricter)
out = {"date": time.strftime("%Y-%m-%d %H:%M"), "wall_s": round(time.perf_counter() - t0, 1),
       "source": "lectures/L7-trust/experiments/logs/six_{flash,lite}.json and judge.json (L7's run, 28 Oct)",
       "state_prompt": STATE, "summary": res, "rows": rows}
(HERE / "logs" / "judge_calibration.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print(json.dumps(res, indent=1))
