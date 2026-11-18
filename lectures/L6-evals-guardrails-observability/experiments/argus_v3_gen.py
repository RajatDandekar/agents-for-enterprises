"""Builds ledgerline/ledgerline/argus/teach.json: the recorded data behind Argus's v3 teaching views (Lecture 6).

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/argus_v3_modal.py::gen

Runs inside the bench's Modal container (argus_v3_modal.py), reads the Lecture 6 logs mounted at /logs, and returns the
file. Nothing is invented: every reply, tool call and tool result is from a recorded run.

turns      four recorded turns for "One turn, four checks", each with its four results already computed, so the page
           shows them with no model call:
             friday   traces_v2.json, run incident     Thursday prompt, "Order the usual, please, needed by 4 Dec 2026."
                      (trace 284e50f5...: the deck's traced demo turn; tool arguments and results from traces_v2_spans.json)
             good1    traces_v2.json, run good2, turn 1   the good prompt, the same message
             good2    traces_v2.json, run good2, turn 2   "Yes, go ahead."
             total    suite_good_k3.json, T19, rep 0   "Which of my orders are late?": the reply ends with a total the
                                                       agent added up itself
           The three code checks are the course's own functions (argus/teach.py calls suite.py and convo.py). The judge's
           verdict is recorded here once, with judges.judge (claude-haiku-5-5) and the same evidence the suite gives it.
           The criterion of the two first turns is NB6b's own sentence ("The reply asks Emma to confirm a preview before
           anything is saved ..."); the yes turn's and the total's are the suite's (tasks T02 and T19).
           The Outcome card reads Ledgerline at the END of the conversation (the suite's end-state check): for the
           good chat's turn 1 that is after turn 2.
           If traces_v2.json is ever recorded again, run `::gen` again, so Argus and the deck show the same turn.
           For `total` the log kept only the first 1,800 characters of the tool result; the same call (list_open_orders,
           the same arguments) is made again on a fresh sandbox, which is the same data, and checked against the logged part.
labelled   twelve of the 56 labelled replies of judge_calibration.json (course/l6/calibration.py): rep 0 of eight tasks
           with short replies, which a person marked right, and four of the planted wrong ones (one fact changed in
           T04, T07, T11, T13), with the criterion, the evidence and what the three judges said in the recorded run.
recorded56 the recorded result on all 56, as the four boxes, per judge.
"""
import json
import pathlib
import time

LOGS = pathlib.Path("/logs")
RIGHT = ["T04", "T07", "T08", "T11", "T12", "T13", "T14", "T20"]
WRONG = ["T04", "T07", "T11", "T13"]


def _log(name):
    return json.loads((LOGS / name).read_text())


def build(record_judge: bool = True) -> dict:
    from ledgerline.argus import teach as T
    from ledgerline.course.l6 import calibration as CAL
    from ledgerline.course.l6 import judges as J
    from ledgerline.course.l6 import suite as S
    from ledgerline.course.l6.agent import Agent

    ref = {p: Agent(p) for p in ("good", "thursday")}        # for the agent's window (prompt, memory, briefing); no model call
    window = {p: [list(x) for x in a.segments(a.clock)] for p, a in ref.items()}
    notes, usd = {}, 0.0

    def view(prompt, turns, requests):
        return T.View(turns, {**T.EMPTY_WRITES, "requests": requests}, window[prompt], ref[prompt].clock)

    # Friday's turn and the good chat: the traced demo turns of the deck (traces_v2.json; the tool arguments and results are
    # in the spans, traces_v2_spans.json), so Argus, the slides and the three tracing tools show one recording.
    tv, spans = _log("traces_v2.json")["rows"], _log("traces_v2_spans.json")

    def traced(run):
        out = []
        for t in tv[run]["turns"]:
            sp = sorted((x for x in spans[run] if x["context"]["trace_id"].replace("0x", "") == t["trace_id"]
                         and x["name"].startswith("execute_tool")), key=lambda x: x["start_time"])
            calls = [{"tool": x["attributes"]["gen_ai.tool.name"], "args": json.loads(x["attributes"]["gen_ai.tool.call.arguments"]),
                      "ok": bool(x["attributes"].get("ledgerline.ok", True)), "out": json.loads(x["attributes"]["gen_ai.tool.call.result"])} for x in sp]
            assert [(c["tool"], c["args"]) for c in calls] == [(c["tool"], c["args"]) for c in t["calls"]], (run, "the spans and the log disagree")
            assert not any("(cut)" in x["attributes"]["gen_ai.tool.call.result"] for x in sp)
            out.append({"text": t["text"], "reply": t["reply"], "calls": calls, "trace_id": t["trace_id"], "links": t.get("links") or {}})
        return out, tv[run]["saved"]
    h, h_saved = traced("incident")
    g, g_saved = traced("good2")
    notes["traced_turns"] = {"incident": {"trace_id": h[0]["trace_id"], "calls": [(c["tool"], c["args"].get("confirm")) for c in h[0]["calls"]], "saved": h_saved},
                             "good2": {"trace_ids": [t["trace_id"] for t in g], "calls": [[(c["tool"], c["args"].get("confirm")) for c in t["calls"]] for t in g], "saved": g_saved},
                             "what_the_checks_need": "tool results for every call (from the spans, none cut) and the saved request (traces_v2.json 'saved'): all there"}
    # the fourth turn: a real reply of the suite whose last line is a total no tool returned
    row = next(r for r in _log("suite_good_k3.json")["rows"] if r["task"] == "T19" and r["rep"] == 0)
    call = row["turns"][0]["calls"][0]
    full = ref["good"].call_tool(call["tool"], call["args"], ref["good"].clock)
    logged = next(e for e in row["evidence"] if e.get("tool") == call["tool"])["result"]
    cut = logged.get("_cut") if isinstance(logged, dict) else None
    notes["total_tool_result"] = {
        "tool": call["tool"], "args": call["args"], "characters_now": len(json.dumps(full, default=str)),
        "characters_logged": len(cut or ""), "logged_part_matches_the_fresh_call": bool(cut) and json.dumps(full, default=str).startswith(cut[:1500]),
        "top_level_keys": sorted(full) if isinstance(full, dict) else None}
    tot = [{"text": row["turns"][0]["text"], "reply": row["turns"][0]["reply"],
            "calls": [{"tool": call["tool"], "args": call["args"], "ok": True, "out": full}]}]
    deck = "the deck's traced demo turn (traces_v2.json, run '{}', trace {}…)"
    spec = [   # id, label, sub, prompt, the turns up to this one, Ledgerline at the END of that conversation, criterion, source, a note
        ("friday", "Friday's turn", "Thursday prompt · “Order the usual, please, needed by 4 Dec 2026.”", "thursday", h[:1], h_saved, T.ASKS_FIRST,
         deck.format("incident", h[0]["trace_id"][:8]), ""),
        ("good1", "The good chat, turn 1", "Good prompt · “Order the usual, please, needed by 4 Dec 2026.”", "good", g[:1], g_saved, T.ASKS_FIRST,
         deck.format("good2", g[0]["trace_id"][:8]), "This chat went on: Emma said “Yes, go ahead.” in turn 2, and the request was saved then."),
        ("good2", "The good chat, turn 2", "Good prompt · “Yes, go ahead.”", "good", g[:2], g_saved, S.BY_ID["T02"]["words"],
         deck.format("good2", g[1]["trace_id"][:8]), ""),
        ("total", "A total nobody returned", "Good prompt · “Which of my orders are late?”", "good", tot, row["writes"]["requests"],
         S.BY_ID["T19"]["words"], "the suite's recorded run (suite_good_k3.json, task T19, run 1)", ""),
    ]
    turns = []
    for tid, label, sub, prompt, ts, reqs, crit, source, after in spec:
        v = view(prompt, ts, reqs)
        ev, user = T.evidence_of(v), " / ".join(x["text"] for x in ts)
        verdict = None
        if record_judge:
            r = T.run_judge(crit, ts[-1]["reply"], ev, user)
            usd += r["usd"]
            verdict = {"pass": r["pass"], "reason": r["reason"], "recorded": "17 Nov 2026 · claude-haiku-5-5 · the evidence on"}
        fc = T.four_checks(v, crit, verdict)
        fc["turn"]["after"], fc["turn"]["links"] = after, ts[-1].get("links") or {}
        turns.append({"id": tid, "label": label, "sub": sub, "prompt": prompt, "source": source, "view": fc,
                      "judge_input": {"reply": ts[-1]["reply"], "evidence": ev, "user": user}})

    # what the Lecture 6 logs say about the same things (for the bench's comparison; not shown on the page)
    sth = next(r for r in _log("suite_thursday_k1.json")["rows"] if r["task"] == "T02")
    inc = _log("incident_r3.json")["summary"]
    notes["logs"] = {
        "scores_v2 (commit_without_yes on the same traces)": [r for r in _log("scores_v2.json")["rows"] if r["run"] in ("incident", "good2")],
        "friday": {"incident_r3_thursday": inc["thursday"], "suite_thursday_k1_T02": [(c["kind"], c["name"], c["pass"], c["why"][:120]) for c in sth["checks"]]},
        "nb6b (its own recordings of the same two first turns)": {
            "nb6b_judge (the good chat, turn 1)": _log("nb6b_judge.json"), "nb6b_judge_friday": _log("nb6b_judge_friday.json"),
            "nb6b_deepeval": _log("nb6b_deepeval.json"), "nb6b_deepeval_friday": _log("nb6b_deepeval_friday.json")},
        "total": {"suite_good_k3_T19_rep0": [(c["kind"], c["name"], c["pass"], c["why"][:200]) for c in row["checks"]]},
    }
    # the suggestion in the brief (suite task T14): checked, and why it is not the example
    v1 = next(r for r in _log("suite_v1_good_k3.json")["rows"] if r["task"] == "T14" and r["rep"] == 1)
    c14 = v1["turns"][0]["calls"][0]
    out14 = ref["good"].call_tool(c14["tool"], c14["args"], ref["good"].clock)
    v14 = view("good", [{"text": v1["turns"][0]["text"], "reply": v1["turns"][-1]["reply"],
                         "calls": [{"tool": c14["tool"], "args": c14["args"], "ok": True, "out": out14}]}], [])
    n14 = T.numbers(v14)
    notes["t14_v1_rep1"] = {"logged_numbers_check": [c["why"] for c in v1["checks"] if c["kind"] == "numbers"],
                            "numbers_check_today": {"pass": n14["pass"], "raw": n14["raw"]},
                            "marks": [(m["text"], m["found"], m["source"]) for m in n14["marks"]]}

    cal = _log("judge_calibration.json")
    rows = {r["id"]: r for r in cal["rows"]}
    suite = {(r["task"], r["rep"]): r for r in _log("suite_good_k3.json")["rows"]}
    labelled = []
    for t in RIGHT:
        r = rows[f"good/{t}/0"]
        labelled.append({"id": r["id"], "task": t, "user": r["user"], "reply": r["reply"], "label": True, "note": "a person marked it right",
                         "changed": None, "criterion": S.BY_ID[t]["words"], "evidence": suite[(t, 0)]["evidence"],
                         "recorded": {k: {"pass": v["pass"], "reason": v["reason"]} for k, v in r["judges"].items()}})
    for t in WRONG:
        base, old, new = next(p for p in CAL.PLANTED if p[0] == ("good", t, 0))
        r = next(x for x in cal["rows"] if x["kind"] == "planted" and x["id"].startswith(f"planted:good/{t}/0:"))
        assert r["reply"] == rows[f"good/{t}/0"]["reply"].replace(old, new)
        labelled.append({"id": f"planted/{t}", "task": t, "user": r["user"], "reply": r["reply"], "label": False,
                         "note": f"one fact changed on purpose: “{old.strip('*')}” became “{new.strip('*')}”",
                         "changed": {"old": old.strip("*"), "new": new.strip("*")}, "criterion": S.BY_ID[t]["words"],
                         "evidence": suite[(t, 0)]["evidence"],
                         "recorded": {k: {"pass": v["pass"], "reason": v["reason"]} for k, v in r["judges"].items()}})
    rec56 = {}
    for style, s in cal["summary"].items():
        c = s["confusion"]
        counts = {"right_passed": c["label_pass_judge_pass"], "right_failed": c["label_pass_judge_fail"],
                  "wrong_failed": c["label_fail_judge_fail"], "wrong_passed": c["label_fail_judge_pass"]}
        fa = counts["right_failed"]
        rec56[style] = {"counts": counts, "wrong": s["planted"], "right": s["real"],
                        "line": f"It caught {counts['wrong_failed']} of {s['planted']} wrong replies, and raised {fa} false alarm"
                                + ("" if fa == 1 else "s") + f" in {s['real']} right replies."}
    data = {"at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "by": "experiments/argus_v3_gen.py",
            "judge_model": "claude-haiku-5-5", "naive_question": J.NAIVE.split(" Answer with JSON")[0].split("buyer. ", 1)[-1],
            "turns": turns, "labelled": labelled,
            "recorded56": {"at": cal["at"], "replies": cal["items"], "judges": rec56,
                           "source": "experiments/logs/judge_calibration.json (40 real replies, 16 with one planted error)"}}
    return {"teach": data, "notes": notes, "usd": round(usd, 5), "calls": 4 if record_judge else 0}
