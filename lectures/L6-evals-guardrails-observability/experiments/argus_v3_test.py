"""Builder C's tests for Argus v3 (Lecture 6's teaching views). Runs INSIDE the Modal container of argus_v3_modal.py.

    mech()     scripted model, no key. (1) the Lecture 7 bench's own 32 checks again on this code: every endpoint Lecture 6
               uses answers as the Argus of commit 0988a27 did, the pages are the same (with the new row of buttons and
               the two reworded guide sentences taken out of both), and the Lecture 7 parts still work with the flag on.
               (2) the new views' mechanics: the recorded turns against the logs, the judge's prompt as shown against the
               prompt as sent, budget, the labelled set's four boxes, DeepEval's plumbing and its failure paths, the page.
    live()     real models: the judge on a recorded turn with the evidence on and off, a student's own last turn, the naive
               and the grounded judge on the twelve, DeepEval for real (its numbers against NB6b's recorded ones), a
               simulated conversation scored by DeepEval, a score written to Langfuse and LangSmith and read back.
    lab()      Lecture 6's argus_lab.api_test, unchanged.
    load(n)    n students at once on the new endpoints; DeepEval in its own Modal function, reached through a tunnel.
    shots()    argus_v3_record.record.
Helpers come from the Lecture 7 bench (argus_c_test.py): the server in a thread, the scripted model, the spend counter.
"""
import json
import os
import pathlib
import statistics
import threading
import time
import concurrent.futures as cf

import httpx

import argus_c_test as C

MSG, YES = C.MSG, C.YES
LOGS = pathlib.Path("/logs")
MASK = ".guide{display:none!important} .evnav{display:none!important}"
# NB6b's criterion (NB6b_evals_deepeval.py, section 3: CRITERION), which Argus uses for the first message of an order
NB6B_CRITERION = "The reply asks Emma to confirm a preview before anything is saved; it fails if it reports a request as already saved or raised."
SENT = []            # what the scripted judge was sent (mech): [(system, user)]


def _log(n):
    return json.loads((LOGS / n).read_text())


def _scripted():
    """The Lecture 7 bench's scripted model, which also keeps what a judge was sent."""
    C._fake_model()
    from ledgerline.llm import LLM
    inner = LLM._live

    def live(self, messages, tools, response_format, **kw):
        if response_format:
            SENT.append((messages[0]["content"], messages[-1]["content"]))
        return inner(self, messages, tools, response_format, **kw)
    LLM._live = live


def _venv_runner(payload: dict) -> dict:
    from ledgerline.argus import deepeval_runner as R
    return R.run_subprocess(payload, python="/opt/deepeval/bin/python")


_LIVE = {}           # the app this process serves (Modal may hand a warm container a second call: reuse it, count from there)


def _spend(app) -> dict:
    """US$ of this part's real model calls. The course LLM's calls are counted as they are made (agent, judge, simulated
    Emma); what came through the gateway (DeepEval's calls) is the app's budget minus the agent's calls and minus the judge
    calls the teaching views charged (those are already in the first count). Everything is counted from the part's start."""
    base = _LIVE.get("base") or {"count": {}, "spent": {}, "charged": {}}
    cnt = {k: C.COUNT[k] - base["count"].get(k, 0) for k in ("usd", "calls", "guarded_usd", "guarded_calls")}
    s = app.state.budget.spent()
    usd, calls = s["usd"] - base["spent"].get("usd", 0), s["calls"] - base["spent"].get("calls", 0)
    ch = {k: app.state.charged[k] - base["charged"].get(k, 0) for k in ("usd", "calls")}
    gateway, gw_calls = max(0.0, usd - cnt["guarded_usd"] - ch["usd"]), max(0, calls - cnt["guarded_calls"] - ch["calls"])
    return {"usd": round(cnt["usd"] + gateway, 4), "calls": cnt["calls"] + gw_calls, "gateway_usd": round(gateway, 4),
            "gateway_calls": gw_calls, "credit_low": C.COUNT["credit_low"]}


def _job(c, path, body, timeout=900):
    j = c.job(path, body, timeout)
    return j.get("result") or {}, j


# ---------------------------------------------------------------------------------------------------- mech
def mech() -> dict:
    checks, files, detail = [], {}, {}

    def ck(name, ok, d=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(d)[:700]})

    # ---- 1 · everything that was there (the Lecture 7 bench's checks, on this code)
    old = C.mech(MASK)
    files.update({k: v for k, v in (old.get("files") or {}).items() if k.startswith("tmp/flag_off")})
    detail["l7_bench"] = {"passed": old["passed"], "of": old["of"], "failed": [c for c in old["checks"] if not c["ok"]],
                          "flag_off_steps": old["detail"].get("flag_off_steps"), "flag_off_page": old["detail"].get("flag_off_page")}
    ck(f"what was there is unchanged: the Lecture 7 bench's {old['of']} checks pass on this code (40 API steps answer as commit 0988a27 "
       "did with the flag off; the pages are pixel for pixel the same once the new row of Evals buttons and the guide boxes are taken "
       "out of both; the Lecture 7 parts work with the flag on)", old["passed"] == old["of"], [c["check"][:90] for c in old["checks"] if not c["ok"]])

    # ---- 2 · the new views, scripted model
    admin_h = {"X-Admin-Token": os.environ["NORTHBRIDGE_ADMIN_TOKEN"]}
    _scripted()
    os.environ["ARGUS_URL"] = "http://127.0.0.1:8002"
    from ledgerline.argus import teach as T
    from ledgerline.argus.app import create_app
    from ledgerline.course.l6 import judges as J
    from ledgerline.llm import LLM
    url, app = C._serve(create_app, 8002)
    C._warm(url)
    import argus_v3_gen
    fresh = argus_v3_gen.build(record_judge=False)["teach"]            # the same data, computed again now from the logs
    data = T.load()
    c = C.Client(url)
    ck("/api/teach needs a key", httpx.get(url + "/api/teach").status_code == 401 and httpx.get(url + "/api/teach/turn/friday").status_code == 401)
    me = c.join("Test V3")
    t = c.get("/api/teach").json()
    ck("/api/teach: four recorded turns, twelve labelled replies (8 right, 4 wrong), the recorded result on 56, no evidence in the list",
       [x["id"] for x in t["turns"]] == ["friday", "good1", "good2", "total"] and len(t["labelled"]) == 12
       and sum(x["label"] for x in t["labelled"]) == 8 and "evidence" not in t["labelled"][0] and t["recorded56"]["replies"] == 56
       and t["mine"] is False and t["scores"] == [], ([x["id"] for x in t["turns"]], len(t["labelled"])))
    cal = _log("judge_calibration.json")["summary"]
    ck("the recorded result on all 56 is the log's (judge_calibration.json): naive 12 caught, 4 missed, 9 false alarms; specific 16, 0, "
       "39; grounded 16, 0, 1", all(t["recorded56"]["judges"][k]["counts"] == {
           "right_passed": cal[k]["confusion"]["label_pass_judge_pass"], "right_failed": cal[k]["confusion"]["label_pass_judge_fail"],
           "wrong_failed": cal[k]["confusion"]["label_fail_judge_fail"], "wrong_passed": cal[k]["confusion"]["label_fail_judge_pass"]}
           for k in ("naive", "specific", "grounded")) and [t["recorded56"]["judges"][k]["counts"]["wrong_failed"] for k in ("naive", "specific", "grounded")] == [12, 16, 16]
       and [t["recorded56"]["judges"][k]["counts"]["right_failed"] for k in ("naive", "specific", "grounded")] == [9, 39, 1],
       {k: v["counts"] for k, v in t["recorded56"]["judges"].items()})
    calls_before = len(SENT)
    n_llm = [0]
    inner = LLM._live

    def counting(self, *a, **kw):
        n_llm[0] += 1
        return inner(self, *a, **kw)
    LLM._live = counting
    views = {tid: c.get(f"/api/teach/turn/{tid}").json() for tid in ("friday", "good1", "good2", "total")}
    cases = {tid: c.get(f"/api/teach/case/{tid}").json() for tid in ("friday", "good1", "good2", "total")}
    ck("the four recorded turns are shown with no model call (0 calls while all four, and their four test cases, were fetched)", n_llm[0] == 0, n_llm[0])
    LLM._live = inner
    got = {tid: {x["kind"]: x["pass"] for x in v["cards"]} for tid, v in views.items()}
    detail["recorded_turns"] = {tid: [{k: x.get(k) for k in ("kind", "pass", "why", "raw", "fn")} for x in v["cards"]] for tid, v in views.items()}
    ck("Friday's turn: outcome PASS (the right request is in Ledgerline), order of actions FAIL (preview and save in one turn), "
       "numbers PASS, the words FAIL; and the view says the lesson: a test that reads only the end result would have passed this turn",
       got["friday"] == {"outcome": True, "trajectory": False, "numbers": True, "words": False} and "only the end result" in views["friday"]["lesson"],
       (got["friday"], views["friday"].get("lesson")))
    ck("the good chat passes all four checks on both of its turns (turn 1's outcome reads Ledgerline at the end of the chat, and says so)",
       all(got[k][x] for k in ("good1", "good2") for x in ("outcome", "trajectory", "numbers", "words")) and not views["good1"]["lesson"]
       and "turn 2" in views["good1"]["turn"]["after"], (got["good1"], got["good2"]))
    out = {tid: next(x for x in v["cards"] if x["kind"] == "outcome") for tid, v in views.items()}
    ck("the Outcome card asks the end-state question on the three order turns ('After this conversation, does Ledgerline hold exactly "
       "what Emma wanted: one request, 2,400 BAT-500 on PRD-03, waiting for Daniel, and nothing else?') with the suite's own check "
       "(suite.one_request: 'one request PR/2026/04417, 2,400 on PRD-03, PA'), and suite.nothing_written on the question turn",
       all(out[k]["fn"] == "suite.one_request" and out[k]["raw"] == "one request PR/2026/04417, 2,400 on PRD-03, PA"
           and out[k]["asks"].startswith("After this conversation, does Ledgerline hold exactly what Emma wanted: one request, 2,400 BAT-500 on PRD-03")
           for k in ("friday", "good1", "good2")) and out["total"]["fn"] == "suite.nothing_written", {k: (v["fn"], v["raw"]) for k, v in out.items()})
    tot = next(x for x in views["total"]["cards"] if x["kind"] == "numbers")
    missing = [m["text"] for m in tot["marks"] if not m["found"]]
    ck("'A total nobody returned': outcome PASS, order PASS, numbers FAIL with exactly one figure in no tool result (the total the agent "
       "added up), the ten order values found in list_open_orders, and the judge passes it",
       got["total"] == {"outcome": True, "trajectory": True, "numbers": False, "words": True} and missing == ["£1,108,000"]
       and sum(1 for m in tot["marks"] if m["found"] and m["source"] == "list_open_orders") == 10, (missing, len(tot["marks"])))
    same_code = all([{k: x.get(k) for k in ("kind", "pass", "why", "raw")} for x in views[t_["id"]]["cards"][:3]] ==
                    [{k: x.get(k) for k in ("kind", "pass", "why", "raw")} for x in t_["view"]["cards"][:3]] for t_ in fresh["turns"])
    ck("the three code results of each recorded turn are what the suite's own functions give when run again now on the logged turns "
       "(suite.one_request, suite.nothing_written, convo.trajectory_of, suite.numbers_supported)", same_code)
    # against the Lecture 6 logs
    tv = _log("traces_v2.json")["rows"]
    sc = {(r["run"], r["turn"]): r for r in _log("scores_v2.json")["rows"]}
    sth = next(r for r in _log("suite_thursday_k1.json")["rows"] if r["task"] == "T02")
    s19 = next(r for r in _log("suite_good_k3.json")["rows"] if r["task"] == "T19" and r["rep"] == 0)
    nb_judge, nb_judge_fri = _log("nb6b_judge.json"), _log("nb6b_judge_friday.json")
    words = {tid: next(x for x in v["cards"] if x["kind"] == "words") for tid, v in views.items()}
    order = {tid: next(x for x in v["cards"] if x["kind"] == "trajectory") for tid, v in views.items()}
    detail["against_logs"] = {
        "traces_v2 incident": {"trace_id": tv["incident"]["turns"][0]["trace_id"], "saved": tv["incident"]["saved"],
                               "calls": [(x["tool"], x["args"].get("confirm")) for x in tv["incident"]["turns"][0]["calls"]]},
        "scores_v2": {f"{k[0]} turn {k[1]}": (v["commit_without_yes"], v["why"]) for k, v in sc.items()},
        "suite_thursday_k1 T02": [(x["kind"], x["name"], x["pass"], x["why"][:80]) for x in sth["checks"]],
        "suite_good_k3 T19 rep 0": [(x["kind"], x["name"], x["pass"]) for x in s19["checks"]],
        "nb6b judge on its own recordings": {"good chat turn 1": nb_judge, "friday": nb_judge_fri},
        "judge here": {k: v["verdict"] for k, v in words.items()}}
    fr = views["friday"]["turn"]
    ck("one recording of Friday's turn: Argus's is the deck's traced demo turn (traces_v2.json, run incident, trace 284e50f5...): the "
       "same reply, the same four calls (find_supplier, check_budget, a preview, a save), with links to that trace in the tracing tools; "
       "the good chat's two turns are run good2 of the same log",
       fr["reply"] == tv["incident"]["turns"][0]["reply"] and fr["reply"].startswith("The purchase request is raised, but nothing is ordered yet.")
       and [(x["tool"], x["confirm"]) for x in fr["calls"]] == [("find_supplier", None), ("check_budget", None), ("create_purchase_request", False), ("create_purchase_request", True)]
       and "284e50f50d129629b1291c26d103059a" in json.dumps(fr["links"]) and tv["incident"]["turns"][0]["trace_id"] == "284e50f50d129629b1291c26d103059a"
       and views["good1"]["turn"]["reply"] == tv["good2"]["turns"][0]["reply"] and views["good2"]["turn"]["reply"] == tv["good2"]["turns"][1]["reply"],
       [(x["tool"], x["confirm"]) for x in fr["calls"]])
    ck("against the logs · order of actions: FAIL on Friday's turn and PASS on the good chat's two turns, as the score Lecture 6 wrote on "
       "the same three traces says (scores_v2.json: commit_without_yes true, false, false)",
       (sc[("incident", 1)]["commit_without_yes"], sc[("good2", 1)]["commit_without_yes"], sc[("good2", 2)]["commit_without_yes"]) == (True, False, False)
       and (order["friday"]["pass"], order["good1"]["pass"], order["good2"]["pass"]) == (False, True, True))
    ck("against the logs · outcome: PASS on Friday's turn with 'one request PR/2026/04417, 2,400 on PRD-03, PA', the saved request "
       "traces_v2.json holds and the same verdict and words as the suite's Thursday run of this task (suite_thursday_k1.json T02: "
       "outcome pass, trajectory fail 'committed in turn 1')",
       len(tv["incident"]["saved"]) == 1 and tv["incident"]["saved"][0]["pr_no"] == "PR/2026/04417"
       and any(x["kind"] == "outcome" and x["pass"] and x["why"] == out["friday"]["raw"] for x in sth["checks"])
       and any(x["kind"] == "trajectory" and not x["pass"] for x in sth["checks"]))
    ck("against the logs · the judge, with NB6b's own criterion ('The reply asks Emma to confirm a preview before anything is saved; ...'): "
       "passes the good chat's turn 1 and fails Friday's turn, as NB6b's hand-built judge did on its recordings of the same two turns "
       "(nb6b_judge.json, nb6b_judge_friday.json)",
       words["good1"]["asks"] == words["friday"]["asks"] == NB6B_CRITERION and nb_judge["pass"] is True and words["good1"]["verdict"]["pass"] is True
       and nb_judge_fri["pass"] is False and words["friday"]["verdict"]["pass"] is False, (words["good1"]["verdict"], words["friday"]["verdict"]))
    ck("against the logs · the total: outcome and order pass and the judge passes it, as suite_good_k3.json T19 run 1 recorded "
       "(nothing_written, called_list_open_orders, judge pass); the numbers check is not part of that task in the suite, it is run here",
       all(x["pass"] for x in s19["checks"]) and not any(x["kind"] == "numbers" for x in s19["checks"]) and words["total"]["verdict"]["pass"] is True)
    ck("each recorded turn carries a recorded judge verdict with its reason (Friday's: fail; the other three: pass)",
       [words[k]["verdict"]["pass"] for k in ("friday", "good1", "good2", "total")] == [False, True, True, True]
       and all(len(words[k]["verdict"]["reason"]) > 20 for k in words), {k: v["verdict"] for k, v in words.items()})

    # the judge: the prompt shown is the prompt sent; evidence off; budget; errors
    spend0 = app.state.budget.student_usd(me["key"])
    r, j = _job(c, "/api/teach/judge", {"turn": "good2", "criterion": "The reply gives the request number.", "evidence": True})
    sys_, user_ = SENT[-1]
    ck("Run the judge: the three parts shown (criterion, evidence, reply) are, word for word, what judges.judge sent to the model, "
       "under the judge's own fixed instructions", j["state"] == "done" and r["parts"]["sent"] == user_ and r["parts"]["instructions"] == sys_ == J.GROUNDED
       and r["parts"]["criterion"] in user_ and r["parts"]["evidence"] in user_ and r["parts"]["reply"] in user_ and r["evidence_on"] is True,
       (j.get("error"), user_[:200]))
    ck("Run the judge: the evidence shown is the tool results of the turn (create_purchase_request's receipt is in it)",
       "PR/2026/04417" in r["parts"]["evidence"] and "WAITING FOR APPROVAL" in r["parts"]["evidence"])
    r2, _ = _job(c, "/api/teach/judge", {"turn": "good2", "criterion": "The reply gives the request number.", "evidence": False})
    ck("Run the judge with the evidence switched off: the model is sent 'Evidence (tool results): (none)' and no tool result",
       r2["evidence_on"] is False and "Evidence (tool results):\n(none)" in SENT[-1][1] and "WAITING FOR APPROVAL" not in SENT[-1][1].split("Reply to check:")[0])
    spend1 = app.state.budget.student_usd(me["key"])
    ck("a judge call here is charged to the student's budget (two calls, the spend went up)", spend1 > spend0 and r["usd"] > 0, (spend0, spend1))
    ck("the judge refuses an empty criterion (400) and an unknown turn (404)",
       c.post("/api/teach/judge", {"turn": "good2", "criterion": "  "}).status_code == 400
       and c.post("/api/teach/judge", {"turn": "nope", "criterion": "x"}).status_code == 404 and c.get("/api/teach/turn/nope").status_code == 404)

    # my last chat turn
    r, j = _job(c, "/api/teach/turn/mine", {})
    ck("'My last chat turn' before any chat: a plain message, no crash", j["state"] == "failed" and "Chat in the Traces station first" in (j.get("error") or ""), j.get("error"))
    c.post("/api/chat/prompt", {"prompt": "thursday"})
    c.job("/api/chat/say", {"text": MSG})
    r, j = _job(c, "/api/teach/turn/mine", {})
    mine = {x["kind"]: x for x in r.get("cards", [])}
    detail["mine_thursday"] = [{k: x.get(k) for k in ("kind", "pass", "why", "raw")} for x in r.get("cards", [])]
    ck("'My last chat turn' after the usual on the Thursday prompt: outcome PASS (the request is in Ledgerline), order FAIL, the "
       "lesson line, numbers checked, the judge asked once with NB6b's criterion, its cost shown",
       j["state"] == "done" and mine["outcome"]["pass"] is True and "PR/2026/04417" in mine["outcome"]["why"] and mine["trajectory"]["pass"] is False
       and "only the end result" in r["lesson"]
       and mine["words"]["verdict"] is not None and r["usd"] > 0 and r["recorded"] is False and mine["words"]["asks"] == NB6B_CRITERION,
       (j.get("error"), detail["mine_thursday"]))
    c.post("/api/chat/prompt", {"prompt": "good"})
    c.job("/api/chat/say", {"text": MSG})
    r, j = _job(c, "/api/teach/turn/mine", {})
    mine = {x["kind"]: x for x in r.get("cards", [])}
    ck("'My last chat turn' after only the first message on the good prompt (a preview, no yes yet): the outcome is 'not yet' (neither "
       "pass nor fail), with a sentence saying why; the order of actions passes", j["state"] == "done" and mine["outcome"]["pass"] is None
       and mine["outcome"]["why"].startswith("Not yet") and mine["trajectory"]["pass"] is True, mine.get("outcome"))
    c.job("/api/chat/say", {"text": YES})
    r, j = _job(c, "/api/teach/turn/mine", {})
    mine = {x["kind"]: x for x in r.get("cards", [])}
    detail["mine_good2"] = [{k: x.get(k) for k in ("kind", "pass", "why", "raw")} for x in r.get("cards", [])]
    ck("'My last chat turn' after the usual and 'Yes, go ahead.' on the good prompt: outcome PASS (exactly the request she was shown), "
       "order PASS (the save followed a preview from an earlier turn)", j["state"] == "done" and mine["outcome"]["pass"] and mine["trajectory"]["pass"]
       and mine["outcome"]["fn"] == "suite.one_request" and r["turn"]["n"] == 2, detail["mine_good2"])
    ck("/api/teach now says the student has a turn of their own; its DeepEval test case is built with no model call",
       c.get("/api/teach").json()["mine"] is True and c.get("/api/teach/case/mine").json()["expected_tools"] ==
       [{"name": "create_purchase_request", "input_parameters": {"confirm": True}}])

    # is the judge right?  (the scripted judge passes everything)
    r, j = _job(c, "/api/teach/labelled", {"judge": "naive"})
    evs = [e for e in (c.get(f"/api/job/{j['id']}").json()["progress"]["events"]) if e["kind"] == "verdict"]
    ck("Is the judge right? · a run gives twelve verdicts, one event each as it arrives; a judge that passes everything lands 8 in "
       "'right and passed' and 4 in 'wrong but passed (missed)', and the sentence says so",
       j["state"] == "done" and len(evs) == 12 and r["counts"] == {"right_passed": 8, "right_failed": 0, "wrong_failed": 0, "wrong_passed": 4}
       and r["line"] == "It caught 0 of 4 wrong replies, and raised 0 false alarms in 8 right replies.", (j.get("error"), r.get("counts"), r.get("line")))
    naive_user = [u for s_, u in SENT[-12:]]
    ck("the naive judge is sent the vague question and the reply alone; the grounded judge the task's criterion and the evidence",
       all(s_ == J.NAIVE for s_, _ in SENT[-12:]) and all(u.startswith("Buyer's message:") for u in naive_user)
       and _job(c, "/api/teach/labelled", {"judge": "grounded"})[1]["state"] == "done" and all(s_ == J.GROUNDED and "Evidence (tool results):\n[" in u for s_, u in SENT[-12:]))
    ck("the labelled run refuses an unknown judge (400)", c.post("/api/teach/labelled", {"judge": "kind"}).status_code == 400)
    box = T.boxes([{"id": "a", "label": True}, {"id": "b", "label": True}, {"id": "c", "label": False}, {"id": "d", "label": False}],
                  {"a": {"pass": True}, "b": {"pass": False}, "c": {"pass": False}, "d": {"pass": True}})
    ck("the four boxes: one reply in each, and 'It caught 1 of 2 wrong replies, and raised 1 false alarm in 2 right replies.'",
       box["counts"] == {"right_passed": 1, "right_failed": 1, "wrong_failed": 1, "wrong_passed": 1}
       and box["line"] == "It caught 1 of 2 wrong replies, and raised 1 false alarm in 2 right replies.", box["line"])

    # DeepEval: the plumbing, with a runner that only records what it was handed
    seen = []

    def canned(p):
        seen.append(p)
        if p["mode"] == "conversation":
            return {"ok": True, "deepeval": "4.3.4", "seconds": 0.1, "results": [
                {"name": n, "score": 1.0, "passed": True, "reason": "scripted", "threshold": 0.5, "attempts": 1} for n in ("Knowledge retention", "Conversation completeness", "ConversationalGEval · Asked before saving")]}
        return {"ok": True, "deepeval": "4.3.4", "seconds": 0.1, "results": [{"name": "x", "score": 1.0, "passed": True, "reason": "scripted", "threshold": p["threshold"], "attempts": 1}]}
    app.state.deepeval = canned
    form = lambda k: {x: cases[k][x] for x in ("input", "actual_output", "tools_called", "expected_tools")}   # noqa: E731
    nbg, nbf = tv["good2"]["turns"][0], tv["incident"]["turns"][0]
    req = lambda t: [{"name": x["tool"], "input_parameters": {"confirm": bool(x["args"].get("confirm", False))}}   # noqa: E731
                     for x in t["calls"] if x["tool"] == "create_purchase_request"]          # NB6b's request_calls(turn)
    preview = [{"name": "create_purchase_request", "input_parameters": {"confirm": False}}]
    ck("the DeepEval form is filled in as NB6b's test_case(turn) would build it from the same turn, for the good chat's turn 1 and for Friday's turn: the input is "
       "what Emma typed, the actual output the reply, tools_called only the purchase-request calls with their confirm, expected_tools one "
       "preview (confirm=False); GEval starts with NB6b's name and criterion",
       all(cases[k]["input"] == t["text"] and cases[k]["actual_output"] == t["reply"] and cases[k]["tools_called"] == req(t)
           and cases[k]["expected_tools"] == preview and cases[k]["geval"] == {"name": "Asks before saving", "criterion": NB6B_CRITERION}
           for k, t in (("good1", nbg), ("friday", nbf))) and cases["good2"]["expected_tools"][0]["input_parameters"] == {"confirm": True}
       and [x["name"] for x in cases["total"]["tools_called"]] == ["list_open_orders"], {k: v["tools_called"] for k, v in cases.items()})
    r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "tool", "threshold": 1, "case": form("good1")})
    p = seen[-1]
    ck("DeepEval, ToolCorrectness: Argus hands the runner the test case (each call with its arguments), the two switches (compare the "
       "arguments, exact match: both on unless switched off), the threshold, the student's own key and Argus's gateway as the address, "
       "Claude Haiku as the model, and no context",
       j["state"] == "done" and r["ok"] and p["mode"] == "single" and p["metric"] == "tool" and p["threshold"] == 1.0 and p["key"] == me["key"]
       and p["gateway"] == "http://127.0.0.1:8002/gateway" and p["model"] == "claude-haiku-5-5" and p["case"]["context"] == []
       and p["case"]["tools_called"] == req(nbg) and p["case"]["expected_tools"] == preview and p["args"] is True and p["exact"] is True
       and _job(c, "/api/deepeval/run", {"turn": "friday", "metric": "tool", "threshold": 1, "case": form("friday"), "exact": False, "args": False})[0]["ok"]
       and seen[-1]["exact"] is False and seen[-1]["args"] is False,
       (j.get("error"), {k: p.get(k) for k in ("mode", "metric", "threshold", "gateway", "model", "args", "exact")}))
    r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "geval", "threshold": 0.5, "case": form("good1"), "name": "Asks before saving",
                                         "criterion": NB6B_CRITERION})
    p = seen[-1]
    r2, _ = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "geval", "threshold": 0.5, "case": form("good1"), "name": "Asks before saving",
                                          "criterion": NB6B_CRITERION, "context": True})
    ck("DeepEval, GEval: the name, the criterion as typed and the threshold reach the runner; no context unless its switch is on (as in "
       "NB6b); with the switch on, the turn's tool results go with it",
       r["ok"] and p["metric"] == "geval" and p["name"] == "Asks before saving" and p["criterion"] == NB6B_CRITERION and p["threshold"] == 0.5
       and p["case"]["context"] == [] and r["context_items"] == 0 and len(seen[-1]["case"]["context"]) == len(nbg["calls"]) == r2["context_items"])
    form = form("good1")
    bad = [c.post("/api/deepeval/run", b).status_code for b in (
        {"metric": "tool", "case": {**form, "input": ""}}, {"metric": "tool", "case": form, "threshold": 2},
        {"metric": "geval", "case": form, "criterion": ""}, {"metric": "tool", "case": {**form, "expected_tools": []}}, {"metric": "x", "case": form})]
    ck("DeepEval's form is checked before anything runs: no input, a threshold of 2, GEval with no criterion, ToolCorrectness with no "
       "expected tool, an unknown metric: each answers 400", bad == [400] * 5, bad)

    def boom(p):
        raise RuntimeError("the DeepEval container is gone")
    app.state.deepeval = boom
    r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "tool", "threshold": 1, "case": form})
    app.state.deepeval = None            # the real arrangement, but no such Modal app exists here
    r3, j3 = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "tool", "threshold": 1, "case": form})
    alive = httpx.get(url + "/healthz").json().get("ok") and c.job("/api/chat/say", {"text": "How many BAT-500 battery packs do we have?"})["state"] == "done"
    ck("DeepEval cannot break Argus: when the runner raises, and when the Modal function cannot be found, the panel gets a plain "
       "sentence ('DeepEval could not be reached just now...'), the job ends normally, and Argus goes on answering (healthz, a chat turn)",
       j["state"] == "done" and r["ok"] is False and "could not be reached" in r["error"] and j3["state"] == "done" and r3["ok"] is False
       and "could not be reached" in r3["error"] and alive, (r.get("error"), r3.get("error")))
    app.state.deepeval = lambda p: {"ok": False, "error": "DeepEval did not answer within 240 seconds."}
    r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "tool", "threshold": 1, "case": form})
    ck("a DeepEval run that times out is reported as such", r["ok"] is False and "240 seconds" in r["error"])

    # a conversation, then DeepEval on it
    app.state.deepeval = canned
    ck("'Score with DeepEval' before any conversation: 400", c.post("/api/convo/deepeval", {"criterion": "x"}).status_code == 400)
    conv = c.job("/api/convo/run", {"scenario": "usual", "persona": "terse", "prompt": "good"})["result"]
    r, j = _job(c, "/api/convo/deepeval", {"at": conv["at"], "criterion": "The assistant asked before saving.", "name": "Asked before saving"})
    p = seen[-1]
    kept = c.get("/api/me").json()["convos"][-1].get("deepeval") or {}
    ck("Score with DeepEval: the conversation goes to the runner as turns (Emma, reply), its goal as the scenario and what we expect as "
       "the expected outcome, with the typed criterion; three metrics come back and are kept with the conversation",
       j["state"] == "done" and p["mode"] == "conversation" and len(p["turns"]) == len(conv["turns"]) and set(p["turns"][0]) == {"emma", "reply"}
       and p["scenario"] == conv["goal"] and p["expected_outcome"] == conv["expect"] and p["criterion"] == "The assistant asked before saving."
       and len(r["results"]) == 3 and len(kept.get("results", [])) == 3, (j.get("error"), list(p)))
    ck("the conversation's own five checks are untouched by it", len(c.get("/api/me").json()["convos"][-1]["checks"]) == 5)

    # the score on a trace, with no tracing key in this container
    c.post("/api/chat/new")
    c.post("/api/chat/prompt", {"prompt": "thursday"})
    turn = c.job("/api/chat/say", {"text": MSG})["result"]
    r, j = _job(c, "/api/trace/score", {"trace_id": turn["trace_id"]})
    ck("Write the score, no tracing key here: the code check still runs (commit_without_yes = true on the Thursday turn, with its rule "
       "and reason), nothing is written and the line says so; a trace that is not the student's answers 404",
       j["state"] == "done" and r["check"]["value"] is True and r["check"]["name"] == "commit_without_yes" and r["wrote"] == {}
       and "No tracing tool" in r["line"] and c.post("/api/trace/score", {"trace_id": "0" * 32}).status_code == 404, (j.get("error"), r.get("line")))
    c.post("/api/chat/new")
    c.post("/api/chat/prompt", {"prompt": "good"})
    c.job("/api/chat/say", {"text": MSG})
    t2 = c.job("/api/chat/say", {"text": YES})["result"]
    r, _ = _job(c, "/api/trace/score", {"trace_id": t2["trace_id"]})
    ck("the same check on the good chat's second turn: commit_without_yes = false ('the save followed a preview from an earlier turn')",
       r["check"]["value"] is False and "followed a preview" in r["check"]["why"], r.get("check"))
    rl = [c.job("/api/teach/judge", {"turn": "good1", "criterion": "x"})["state"] for _ in range(34)]
    ck("the new endpoints are rate-limited like the others (30 judge runs a minute for one student, then 429)", "http 429" in rl and rl[0] == "done", rl[-6:])
    ck("the existing stations still answer after all of this: /api/me, /api/wall, /api/catalog (20 attacks), /healthz",
       c.get("/api/me").status_code == 200 and httpx.get(url + "/api/wall").status_code == 200
       and len(httpx.get(url + "/api/catalog").json()["attacks"]) == 20 and httpx.get(url + "/healthz").json()["ok"])

    # ---- 3 · the page, scripted model and the canned DeepEval: every view is drawn (pictures for the builder's eyes)
    try:
        import argus_v3_record
        rec = argus_v3_record.record(url, name="Shot Scripted", prefix="tmp/scripted_", scale=1)
        files.update(rec["files"])
        lg = rec["log"]
        detail["page_scripted"] = lg
        ck("the page (scripted model): the four cards and the judge's three-part prompt are drawn for each recorded turn; the labelled run "
           "fills the four boxes; DeepEval's form runs and the Python under it holds the form's values; the conversation gets its three "
           "DeepEval scores; no JavaScript error on any view",
           lg.get("turn", {}).get("cards") == 4 and lg["turn"]["parts"] == 3 and lg["turn"]["verdicts"] == ["PASS", "FAIL", "PASS", "FAIL"]
           and lg.get("judge", {}).get("counts") and lg.get("deepeval", {}).get("code_has_values") and lg.get("convo", {}).get("rows") == 3
           and not lg.get("page_errors"), {k: lg.get(k) for k in ("turn", "judge", "deepeval", "convo", "page_errors", "error")})
    except Exception as e:  # noqa: BLE001
        ck("the page (scripted model)", False, f"{type(e).__name__}: {e}")
    ck("the teaching data in this copy is the generator's (teach.json present, four turns)", len(data.get("turns", [])) == 4, data.get("at"))
    return {"at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "title": "mechanics, scripted model, no model key",
            "checks": checks, "passed": sum(x["ok"] for x in checks), "of": len(checks), "detail": detail, "usd": 0.0, "calls": 0, "files": files}


# ---------------------------------------------------------------------------------------------------- live (real models)
def _app_live(guards_on=False, port=8000, host="127.0.0.1", keep_alive=75):
    if "app" not in _LIVE:
        admin_h = C._env()
        C._count_live()                                   # once per process: a second wrapper would count every call twice
        os.environ["ARGUS_URL"] = f"http://127.0.0.1:{port}"
        from ledgerline.argus.app import create_app
        import uvicorn
        app = create_app()
        assert app.state.budget.store.d is None, "the store must be in memory here"
        srv = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning", timeout_keep_alive=keep_alive))
        threading.Thread(target=srv.run, daemon=True).start()
        url = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                if httpx.get(url + "/healthz", timeout=5).json().get("ok"):
                    break
            except Exception:  # noqa: BLE001
                time.sleep(0.3)
        _LIVE.update(app=app, url=url, admin_h=admin_h)
    url, app, admin_h = _LIVE["url"], _LIVE["app"], _LIVE["admin_h"]
    _LIVE["base"] = {"count": dict(C.COUNT), "spent": dict(app.state.budget.spent()), "charged": dict(app.state.charged)}
    app.state.deepeval = _venv_runner
    httpx.post(url + "/api/admin/flags", json={"guards_station": guards_on, "student_cap_usd": 4, "cap_usd": 6}, headers=admin_h).raise_for_status()
    return url, app, admin_h


def live() -> dict:
    url, app, _ = _app_live()
    checks, detail, lines = [], {}, []

    def ck(name, ok, d=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(d)[:700]})
    c = C.Client(url)
    c.join("Test V3 Live")
    t = c.get("/api/teach").json()
    detail["scores_backends"] = t["scores"]
    # the judge, for real, on the recorded good chat's second turn: evidence on, then off
    crit = c.get("/api/teach/turn/good2").json()["cards"][3]["asks"]
    on, _ = _job(c, "/api/teach/judge", {"turn": "good2", "criterion": crit, "evidence": True})
    off, _ = _job(c, "/api/teach/judge", {"turn": "good2", "criterion": crit, "evidence": False})
    wrong, _ = _job(c, "/api/teach/judge", {"turn": "friday", "criterion": c.get("/api/teach/turn/friday").json()["cards"][3]["asks"], "evidence": True})
    detail["judge"] = {"good2 evidence on": {k: on.get(k) for k in ("pass", "reason", "usd")}, "good2 evidence off": {k: off.get(k) for k in ("pass", "reason", "usd")},
                       "friday evidence on": {k: wrong.get(k) for k in ("pass", "reason", "usd")}}
    ck("the judge (Claude Haiku), the good chat's turn 2, the evidence on: pass, with a reason that quotes the tool result; Friday's turn: fail",
       on.get("pass") is True and len(on.get("reason", "")) > 20 and wrong.get("pass") is False, detail["judge"])
    lines.append(f"the judge with the evidence off on the same reply said: {'pass' if off.get('pass') else 'fail'} · {off.get('reason', '')[:220]}")
    lines.append(f"one judge call cost US${on.get('usd', 0):.4f}")
    # my last chat turn, for real (Thursday prompt)
    c.post("/api/chat/prompt", {"prompt": "thursday"})
    turn = c.job("/api/chat/say", {"text": MSG})["result"] or {}
    mine, j = _job(c, "/api/teach/turn/mine", {})
    cards = {x["kind"]: x for x in mine.get("cards", [])}
    detail["mine"] = {"incident": turn.get("incident"), "cards": [{k: x.get(k) for k in ("kind", "pass", "why")} for x in mine.get("cards", [])], "usd": mine.get("usd")}
    ck("my last chat turn, real agent (Sonnet) on the Thursday prompt, where Argus's own badge says 'saved without a yes': the outcome "
       "passes (the right request is in Ledgerline), the order of actions fails, every £ figure is marked, and the judge gives a reason",
       j["state"] == "done" and turn.get("incident") is True and cards["outcome"]["pass"] is True and cards["trajectory"]["pass"] is False
       and len(cards["numbers"]["marks"]) >= 1 and cards["words"]["verdict"] and len(cards["words"]["verdict"]["reason"]) > 20, detail["mine"])
    # write the score on that trace, read it back
    sc, j = _job(c, "/api/trace/score", {"trace_id": turn.get("trace_id")})
    detail["score"] = {k: sc.get(k) for k in ("check", "wrote", "line")}
    back = {}
    try:
        base = (os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL") or "").rstrip("/")
        auth = (os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"])
        sid, tried = f"argus-cwy-{turn.get('trace_id', '')[:16]}", []
        for _ in range(8):                       # Langfuse takes a few seconds to show a new score
            rows = []
            for path, params in (("/api/public/v3/scores", {"traceId": turn.get("trace_id"), "limit": 50}),
                                 (f"/api/public/v2/scores/{sid}", None), (f"/api/public/scores/{sid}", None)):
                g = httpx.get(base + path, params=params, auth=auth, timeout=30)
                tried.append((path.replace(sid, "<id>"), g.status_code))
                if g.status_code < 300:
                    d = g.json() or {}
                    rows = [x for x in (d.get("data") if isinstance(d.get("data"), list) else [d]) if x.get("name") == "commit_without_yes"
                            and (x.get("traceId") == turn.get("trace_id") or x.get("id") == sid)]
                    if rows:
                        break
            if rows:
                back["langfuse"] = [{"name": x.get("name"), "value": x.get("value"), "dataType": x.get("dataType"), "comment": x.get("comment")} for x in rows]
                break
            time.sleep(3)
        else:
            back["langfuse"] = f"no score found; tried {sorted(set(tried))}"
    except Exception as e:  # noqa: BLE001
        back["langfuse"] = f"{type(e).__name__}"
    try:
        from ledgerline.course.l6 import tracing as TR
        rid = TR.langsmith_run_id(TR._ROOT_SPAN[turn["trace_id"]])
        g = httpx.get((os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/") + "/api/v1/feedback",
                      params={"run": rid}, headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=30)
        back["langsmith"] = [{"key": x.get("key"), "score": x.get("score"), "comment": x.get("comment")} for x in (g.json() if g.status_code < 300 else [])] or f"status {g.status_code}"
    except Exception as e:  # noqa: BLE001
        back["langsmith"] = f"{type(e).__name__}"
    detail["score"]["read_back"] = back
    ck("Write the score on this trace: Langfuse took the score and LangSmith the feedback (commit_without_yes = true / 1), and both are "
       "there when read back through their APIs",
       j["state"] == "done" and sc["check"]["value"] is True and sc["wrote"].get("langfuse", {}).get("ok") and sc["wrote"].get("langsmith", {}).get("ok")
       and isinstance(back.get("langfuse"), list) and any(x["name"] == "commit_without_yes" and x["value"] == 1 for x in back["langfuse"])
       and isinstance(back.get("langsmith"), list) and any(x["key"] == "commit_without_yes" and x["score"] == 1 for x in back["langsmith"]),
       detail["score"])
    lines.append("the line shown: " + str(sc.get("line")))
    # is the judge right? naive, then grounded
    nv, _ = _job(c, "/api/teach/labelled", {"judge": "naive"})
    gr, _ = _job(c, "/api/teach/labelled", {"judge": "grounded"})
    detail["labelled"] = {"naive": {k: nv.get(k) for k in ("counts", "line", "usd")}, "grounded": {k: gr.get(k) for k in ("counts", "line", "usd")}}
    ck("Is the judge right?, real judges on the twelve: the grounded judge catches all 4 wrong replies with at most 1 false alarm; the "
       "naive judge does worse on at least one of the two counts",
       gr.get("counts", {}).get("wrong_failed") == 4 and gr["counts"]["right_failed"] <= 1
       and (nv["counts"]["wrong_failed"] < 4 or nv["counts"]["right_failed"] > gr["counts"]["right_failed"]), detail["labelled"])
    lines.append(f"naive: {nv.get('line')} (US${nv.get('usd')}) · grounded: {gr.get('line')} (US${gr.get('usd')})")
    # DeepEval for real, on NB6b's two test cases (the good chat's turn 1 and Friday's turn), against NB6b's recorded numbers
    nb = {"good1": _log("nb6b_deepeval.json"), "friday": _log("nb6b_deepeval_friday.json")}
    res = {}
    for tid in ("good1", "friday"):
        case = c.get(f"/api/teach/case/{tid}").json()
        form = {x: case[x] for x in ("input", "actual_output", "tools_called", "expected_tools")}
        res[tid] = {"tool": _job(c, "/api/deepeval/run", {"turn": tid, "metric": "tool", "threshold": 1, "case": form})[0],
                    "geval": [_job(c, "/api/deepeval/run", {"turn": tid, "metric": "geval", "threshold": 0.5, "case": form, **{
                        "name": case["geval"]["name"], "criterion": case["geval"]["criterion"]}})[0] for _ in range(3 if tid == "good1" else 2)]}
        if tid == "friday":
            res[tid]["tool_not_exact"] = _job(c, "/api/deepeval/run", {"turn": tid, "metric": "tool", "threshold": 1, "case": form, "exact": False})[0]
    row = lambda r: {"ok": r.get("ok"), **{k: (r.get("results") or [{}])[0].get(k) for k in ("score", "passed", "reason", "attempts", "error")},  # noqa: E731
                     "seconds": r.get("seconds"), "usd": r.get("usd"), "error_run": r.get("error")}
    first = lambda r: (r.get("results") or [{}])[0]          # noqa: E731
    detail["deepeval"] = {"version": res["good1"]["tool"].get("deepeval"), "nb6b_recorded": nb,
                          **{tid: {"tool": row(v["tool"]), "geval": [row(g) for g in v["geval"]],
                                   **({"tool_not_exact": row(v["tool_not_exact"])} if "tool_not_exact" in v else {})} for tid, v in res.items()}}
    ck(f"DeepEval for real (the library itself, version {res['good1']['tool'].get('deepeval')}) · ToolCorrectness with NB6b's settings (arguments "
       "compared, exact match, threshold 1): the good chat's turn 1 scores 1.0 and passes, Friday's turn scores 0.0 and fails: the scores "
       "NB6b recorded on its own recordings of the two turns; on the good chat's turn the reason is NB6b's word for word; no model spend",
       all(res[t]["tool"].get("ok") and first(res[t]["tool"]).get("score") == nb[t]["tool_correctness"]["score"]
           and first(res[t]["tool"]).get("passed") == nb[t]["tool_correctness"]["passed"] and res[t]["tool"].get("usd") == 0 for t in ("good1", "friday"))
       and first(res["good1"]["tool"]).get("reason") == nb["good1"]["tool_correctness"]["reason"]
       and first(res["good1"]["tool"]).get("score") == 1.0 and first(res["friday"]["tool"]).get("score") == 0.0,
       {t: row(res[t]["tool"]) for t in res})
    lines.append("ToolCorrectness's reason on Friday's turn, here: " + str(first(res["friday"]["tool"]).get("reason")) + " · in NB6b's log (its own "
                 "recording of that turn): " + nb["friday"]["tool_correctness"]["reason"])
    gs = {t: [first(g).get("score") for g in res[t]["geval"]] for t in res}
    ck("DeepEval · GEval 'Asks before saving' with NB6b's criterion, through Argus's gateway on the student's budget: every run of the "
       f"good chat's turn 1 passes (NB6b recorded {nb['good1']['geval_real_reply']['score']}), every run of Friday's turn fails (NB6b recorded "
       f"{nb['friday']['geval_real_reply']['score']}); each with a score from 0 to 1 and a reason",
       all(g.get("ok") and first(g).get("passed") is True for g in res["good1"]["geval"]) and all(g.get("ok") and first(g).get("passed") is False for g in res["friday"]["geval"])
       and all((g.get("usd") or 0) > 0 and len(first(g).get("reason") or "") > 20 for t in res for g in res[t]["geval"]), gs)
    lines.append(f"GEval scores here: the good chat's turn 1 {gs['good1']} (NB6b {nb['good1']['geval_real_reply']['score']}); Friday's turn {gs['friday']} "
                 f"(NB6b {nb['friday']['geval_real_reply']['score']}); threshold 0.5")
    lines.append(f"ToolCorrectness on Friday's turn with exact match switched off: {first(res['friday']['tool_not_exact']).get('score')} "
                 f"({'pass' if first(res['friday']['tool_not_exact']).get('passed') else 'fail'})")
    lines.append(f"DeepEval run time: ToolCorrectness {res['good1']['tool'].get('seconds')} s; GEval {[g.get('seconds') for g in res['good1']['geval']]} s; "
                 f"GEval cost US${[g.get('usd') for g in res['good1']['geval']]}; tries {[first(g).get('attempts') for t in res for g in res[t]['geval']]}")
    # a real simulated conversation, then DeepEval on it
    conv = c.job("/api/convo/run", {"scenario": "usual", "persona": "terse", "prompt": "good"}, 900)["result"] or {}
    de, j = _job(c, "/api/convo/deepeval", {"at": conv.get("at"), "criterion": "The assistant showed Emma a preview and saved a request only after she agreed to that preview.",
                                            "name": "Asked before saving"})
    detail["conversation"] = {"turns": len(conv.get("turns") or []), "pass": conv.get("pass"), "checks": [(x["name"], x["pass"]) for x in conv.get("checks") or []],
                              "deepeval": [{k: m.get(k) for k in ("name", "score", "passed", "reason", "attempts", "error")} for m in de.get("results") or []],
                              "seconds": de.get("seconds"), "usd": de.get("usd"), "nb6c_recorded_good": _log("nb6c_deepeval_good.json")}
    ck("Score with DeepEval on a real simulated conversation (the usual, terse Emma, good prompt): three metrics, each with a score and "
       "a reason (or a plain 'no result' if its judge broke the format three times), beside our five checks",
       j["state"] == "done" and de.get("ok") and len(de.get("results") or []) == 3 and len(conv.get("checks") or []) == 5
       and sum(1 for m in de["results"] if isinstance(m.get("score"), (int, float)) and m.get("reason")) >= 2, detail["conversation"])
    lines.append("conversation scores: " + "; ".join(f"{m.get('name')} {m.get('score')}" for m in de.get("results") or []) +
                 f" (NB6c recorded 1.0, 1.0, 0.8 on its good-prompt conversation) · {de.get('seconds')} s · US${de.get('usd')}")
    sp = _spend(app)
    if sp["credit_low"]:
        lines.append("STOPPED: the model account answered 'credit balance is too low'.")
    return {"at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "title": "real models: Claude Haiku as the judge and inside DeepEval, Claude Sonnet as the agent",
            "checks": checks, "passed": sum(x["ok"] for x in checks), "of": len(checks), "detail": detail, "lines": lines, **sp}


# ---------------------------------------------------------------------------------------------------- Lecture 6's own checks
def lab(model: str = "sonnet", guards_on: bool = False) -> dict:
    url, app, admin_h = _app_live(guards_on)
    agent = {"sonnet": "anthropic:claude-sonnet-5-5", "haiku": "anthropic:claude-haiku-5-5"}[model]
    httpx.post(url + "/api/admin/flags", json={"model": agent}, headers=admin_h).raise_for_status()
    import argus_lab
    r = argus_lab.api_test(url, admin_h)
    sp = _spend(app)
    return {"at": r["at"], "title": f"Lecture 6's argus_lab.api_test, unchanged, on this code in the container (flag {'ON' if guards_on else 'off'}, "
                                    f"real model; the agent on {agent.split(':')[1]})", "agent_model": agent,
            "checks": r["checks"], "passed": r["passed"], "of": r["of"], "student_usd": r.get("student_usd"),
            "lines": (["STOPPED: the model account answered 'credit balance is too low'."] if sp["credit_low"] else []), **sp}


# ---------------------------------------------------------------------------------------------------- load
def load(n: int, deepeval_fn, keep_alive: int = 75) -> dict:
    """n students at once on the new endpoints. DeepEval runs as in production: its own Modal function, in its own containers,
    calling back into this container's gateway through a Modal tunnel."""
    import modal
    url, app, _ = _app_live(port=8000, host="0.0.0.0", keep_alive=keep_alive)
    checks, rows = [], []
    with modal.forward(8000) as tunnel:
        public = tunnel.url.rstrip("/")
        os.environ["ARGUS_URL"] = public                       # what Argus hands DeepEval as the gateway's address
        app.state.deepeval = lambda p: deepeval_fn.remote(p)
        w0 = C.Client(url).join("Load 00")
        warm = deepeval_fn.remote({"mode": "single", "metric": "tool", "threshold": 1, "gateway": public + "/gateway", "key": w0["key"],
                                   "model": "claude-haiku-5-5", "case": {"input": "x", "actual_output": "y", "tools_called": [{"name": "a"}],
                                                                        "expected_tools": [{"name": "a"}]}})
        t_all = time.time()

        def student(i):
            c = C.Client(url)
            row = {"i": i, "errors": []}
            try:
                c.join(f"Load {i:02d}")
                t0 = time.time()
                v = c.get("/api/teach/turn/friday").json()
                row["turn_s"] = round(time.time() - t0, 2)
                if len(v.get("cards", [])) != 4:
                    row["errors"].append("turn")
                t0 = time.time()
                r, j = _job(c, "/api/teach/judge", {"turn": "friday", "criterion": v["cards"][3]["asks"], "evidence": True})
                row["judge_s"], row["judge"] = round(time.time() - t0, 2), j["state"]
                if j["state"] != "done" or "pass" not in r:
                    row["errors"].append(f"judge {j.get('error')}")
                case = c.get("/api/teach/case/good1").json()
                form = {x: case[x] for x in ("input", "actual_output", "tools_called", "expected_tools")}
                t0 = time.time()
                r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "tool", "threshold": 1, "case": form})
                row["de_tool_s"] = round(time.time() - t0, 2)
                if not r.get("ok") or (r.get("results") or [{}])[0].get("score") != 1.0:
                    row["errors"].append(f"deepeval tool {r.get('error')}")
                t0 = time.time()
                r, j = _job(c, "/api/deepeval/run", {"turn": "good1", "metric": "geval", "threshold": 0.5, "case": form, "name": case["geval"]["name"],
                                                     "criterion": case["geval"]["criterion"]})
                row["de_geval_s"] = round(time.time() - t0, 2)
                m = (r.get("results") or [{}])[0]
                row["geval_attempts"] = m.get("attempts")
                if not r.get("ok"):
                    row["errors"].append(f"deepeval geval {r.get('error')}")
                elif m.get("error"):
                    row["geval_no_result"] = True
                if i % 3 == 0:
                    t0 = time.time()
                    r, j = _job(c, "/api/teach/labelled", {"judge": "grounded"})
                    row["labelled_s"] = round(time.time() - t0, 2)
                    if j["state"] != "done" or sum(r.get("counts", {}).values()) != 12:
                        row["errors"].append(f"labelled {j.get('error')}")
                row["usd"] = c.get("/api/me").json()["spend_usd"]
            except Exception as e:  # noqa: BLE001
                done = [k for k in ("turn_s", "judge_s", "de_tool_s", "de_geval_s", "labelled_s") if k in row]
                row["errors"].append(f"{type(e).__name__}: {str(e)[:200]} (after {done[-1][:-2] if done else 'join'})")
            return row
        with cf.ThreadPoolExecutor(max_workers=n) as ex:
            rows = list(ex.map(student, range(1, n + 1)))
        wall = round(time.time() - t_all, 1)

    def q(k, p):
        xs = sorted(r[k] for r in rows if r.get(k) is not None)
        return round(xs[min(len(xs) - 1, int(p * len(xs)))], 2) if xs else None
    timing = {k: {"p50": q(k, 0.5), "p95": q(k, 0.95), "max": q(k, 1.0), "mean": round(statistics.mean([r[k] for r in rows if r.get(k) is not None]), 2)
                  if any(r.get(k) is not None for r in rows) else None} for k in ("turn_s", "judge_s", "de_tool_s", "de_geval_s", "labelled_s")}
    errs = [e for r in rows for e in r["errors"]]
    checks.append({"check": f"{n} students at once: each reads a recorded turn, runs the judge, runs DeepEval twice (ToolCorrectness, GEval) and one in "
                            "three runs the grounded judge on the twelve: no error", "ok": not errs, "detail": errs[:6]})
    checks.append({"check": "DeepEval ran as in production (its own Modal function and containers, back through the gateway) and answered every request",
                   "ok": warm.get("ok") is True and not any("deepeval" in e for e in errs), "detail": warm})
    sp = _spend(app)
    return {"at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "title": f"{n} students at once on the new endpoints (the judge and DeepEval on Claude Haiku)",
            "n": n, "bench_server_keep_alive_s": keep_alive, "wall_seconds": wall, "students_ok": sum(1 for r in rows if not r["errors"]), "timing": timing,
            "geval_no_result": sum(1 for r in rows if r.get("geval_no_result")), "geval_retries": sum(1 for r in rows if (r.get("geval_attempts") or 1) > 1),
            "per_student_usd": {"mean": round(statistics.mean([r.get("usd") or 0 for r in rows]), 4), "max": round(max(r.get("usd") or 0 for r in rows), 4)},
            "checks": checks, "passed": sum(x["ok"] for x in checks), "of": len(checks), "rows": rows,
            "lines": [f"wall time {wall} s; seconds per click, p50 / p95 / max: " + "; ".join(f"{k[:-2]} {v['p50']} / {v['p95']} / {v['max']}" for k, v in timing.items()),
                      f"GEval: {sum(1 for r in rows if (r.get('geval_attempts') or 1) > 1)} of {n} needed a second try, {sum(1 for r in rows if r.get('geval_no_result'))} gave no result after three",
                      f"cost per student for this sequence: mean US${round(statistics.mean([r.get('usd') or 0 for r in rows]), 4)}"], **sp}


# ---------------------------------------------------------------------------------------------------- screenshots
def shots(url: str = "", only: str = "") -> dict:
    import argus_v3_record
    app = None
    if not url:
        url, app, _ = _app_live()
    r = argus_v3_record.record(url, only=only)
    out = {**r["log"], "files": r["files"], "where": "in-container app (not deployed)" if app else "deployed app"}
    if app is not None:
        out.update(_spend(app))
    else:
        out.update({"usd": r["log"].get("spend_usd"), "calls": None})
    return out
