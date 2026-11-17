"""Build figdata.js (window.L6) for the Lecture 6 deck. Nothing measured is typed on a slide: every number about OUR
system comes from experiments/logs/, read here. Facts about other tools and the market are written on the slides with
their source (research/TOOLS_RESEARCH.md, cited in NOTES.md).

    python3 lectures/L6-evals-guardrails-observability/gen_figdata.py     (standard library only; re-run any time)

A missing log leaves its slots showing "from the run" on the slide (never a made-up value).
"""
import json
import pathlib
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "experiments" / "logs"
ROOT = HERE.parents[1]
MEDIA_EXT = (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm")


def load(name):
    p = LOGS / name
    if not p.exists():
        print("  missing:", name)
        return None
    try:
        return json.loads(p.read_text())
    except ValueError as e:
        print("  unreadable:", name, e)
        return None


def q(xs, p):
    xs = sorted(x for x in xs if x is not None)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


m = {}
# ------------------------------------------------------------------------------------------- the incident
inc = {t: load(f"incident_{t}.json") for t in ("r1", "r2", "r3")}
sp3 = load("incident_spans_r3.json") or {}
if all(inc.values()):
    def agg(tags, p):
        s = [inc[t]["summary"].get(p, {}) for t in tags]
        return {"runs": sum(x.get("runs", 0) for x in s), "committed": sum(x.get("committed_without_yes", 0) for x in s),
                "asked_date": sum(x.get("no_pr_call", 0) for x in s)}
    m["incident"] = {"nodate": {"good": agg(["r1", "r2"], "good"), "thursday": agg(["r1", "r2"], "thursday")},
                     "dated": {"good": agg(["r3"], "good"), "thursday": agg(["r3"], "thursday")},
                     "msg_dated": inc["r3"]["message"], "msg_nodate": inc["r1"]["message"]}
    nd = m["incident"]["nodate"]["thursday"]
    p = nd["committed"] / nd["runs"]
    m["incident"]["nodate_rate"] = round(p, 3)
    m["incident"]["vibe3_miss"] = round((1 - p) ** 3, 3)     # three tries, all look fine
    m["incident"]["vibe3_miss_pct"] = round(100 * (1 - p) ** 3)
    bad = next(r for r in inc["r3"]["rows"] if r["prompt"] == "thursday" and r["committed"])
    good = next(r for r in inc["r3"]["rows"] if r["prompt"] == "good")
    good2 = next((r for r in inc["r1"]["rows"] if r["prompt"] == "good" and r.get("turn2")), None)

    def slim_tree(spans):
        if not spans:
            return []
        import datetime as dt

        def ms(s):
            return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000
        t0 = min(ms(s["start_time"]) for s in spans)
        kids = {}
        for s in spans:
            kids.setdefault(s.get("parent_id"), []).append(s)
        ids = {s["context"]["span_id"] for s in spans}
        out = []

        def walk(s, d):
            a = s.get("attributes") or {}
            out.append({"name": s["name"], "depth": d, "kind": a.get("gen_ai.operation.name", "span"),
                        "start": round(ms(s["start_time"]) - t0), "end": round(ms(s["end_time"]) - t0),
                        "confirm": a.get("ledgerline.confirm"), "preview": a.get("ledgerline.preview_only"),
                        "tin": a.get("gen_ai.usage.input_tokens"), "tout": a.get("gen_ai.usage.output_tokens"),
                        "usd": a.get("ledgerline.cost_usd"), "refused": a.get("ledgerline.refused_by"),
                        "decision": a.get("ledgerline.guard.decision")})
            for k in sorted(kids.get(s["context"]["span_id"], []), key=lambda x: x["start_time"]):
                walk(k, d + 1)
        for r in sorted([s for s in spans if not s.get("parent_id") or s["parent_id"] not in ids], key=lambda x: x["start_time"]):
            walk(r, 0)
        return out

    def span_attrs(spans, confirm):
        for s in spans:
            a = s.get("attributes") or {}
            if s["name"] == "execute_tool create_purchase_request" and a.get("ledgerline.confirm") is confirm:
                keep = {k: v for k, v in a.items() if k.startswith(("gen_ai.", "ledgerline."))}
                for k in ("gen_ai.tool.call.arguments", "gen_ai.tool.call.result"):
                    try:
                        keep[k] = json.loads(keep[k])
                    except (KeyError, ValueError, TypeError):
                        pass
                return {"name": s["name"], "trace_id": s["context"]["trace_id"][2:], "span_id": s["context"]["span_id"][2:],
                        "parent_id": (s.get("parent_id") or "")[2:], "start": s["start_time"], "end": s["end_time"],
                        "status": (s.get("status") or {}).get("status_code"), "attributes": keep}
        return None
    bspans = sp3.get(bad["session"], [])
    m["incident"]["bad"] = {k: bad.get(k) for k in ("reply", "trace_id", "url", "tokens_in", "tokens_out", "usd", "seconds", "model_calls")}
    m["incident"]["bad"]["calls"] = [{"tool": c["tool"], "args": c["args"], "step": c["step"]} for c in bad["calls"]]
    m["incident"]["bad"]["tools"] = len(bad["calls"])
    m["incident"]["bad"]["saved"] = bad["saved_requests"][0] if bad["saved_requests"] else None
    m["incident"]["good"] = {k: good.get(k) for k in ("reply", "trace_id", "url", "tokens_in", "usd", "seconds")}
    m["incident"]["good2"] = {"reply1": good2["reply"], "reply2": good2["turn2"]["reply"], "url1": good2.get("url"),
                              "url2": good2["turn2"].get("url")} if good2 else None
    m["incident"]["trace"] = slim_tree(bspans)
    m["incident"]["trace_good"] = slim_tree(sp3.get(good["session"], []))
    m["incident"]["commit_span"] = span_attrs(bspans, True)
    m["incident"]["preview_span"] = span_attrs(bspans, False)
    cs = m["incident"]["commit_span"] or {}
    m["incident"]["commit_receipt"] = {"request_no": (cs.get("attributes") or {}).get("ledgerline.receipt.request_no"),
                                       "status": (cs.get("attributes") or {}).get("ledgerline.receipt.status")}
    m["incident"]["usd"] = round(sum(x["usd"] for x in inc.values()), 2)

# ------------------------------------------------------------------------------------------- the suite
def suite_sum(d):
    return {"runs": d["runs"], "passed": d["passed_runs"], "errors": d["errors"], "by_kind": d["by_kind"], "pass_k": d["pass_k"],
            "agent_usd": d["agent_usd"], "judge_usd": d["judge_usd"], "k": d["k"]}


sv = {k: load(f"suite_{k}.json") for k in ("v1_good_k3", "v1_thursday_k1", "good_k3", "thursday_k1")}
if sv["good_k3"] and sv["thursday_k1"]:
    m["suite"] = {k: suite_sum(v) for k, v in sv.items() if v}
    g, t = sv["good_k3"], sv["thursday_k1"]
    titles = {r["task"]: r["title"] for r in g["rows"]}
    grid = []
    for tid in sorted(titles):
        cells = [next((r for r in g["rows"] if r["task"] == tid and r["rep"] == i), None) for i in range(3)] + \
                [next((r for r in t["rows"] if r["task"] == tid), None)]
        grid.append({"task": tid, "title": titles[tid], "cells": [None if c is None else ("e" if c["error"] else "p" if c["pass"] else "f")
                                                                   for c in cells],
                     "why": [None if (c is None or c["pass"]) else "; ".join(f"{x['kind']}: {x['why'][:90]}" for x in c["checks"] if not x["pass"])
                             for c in cells]})
    m["suite"]["grid"] = grid
    m["suite"]["fails"] = [{"prompt": p, "task": r["task"], "rep": r["rep"], "title": r["title"],
                            "why": [f"{x['kind']}: {x['why'][:160]}" for x in r["checks"] if not x["pass"]]}
                           for p, d in (("good", g), ("thursday", t)) for r in d["rows"] if not r["pass"]]
    runs = g["rows"] + t["rows"]
    m["suite"]["per_run_usd"] = round(statistics.mean(r["usd"] for r in runs), 4)
    m["suite"]["per_run_s"] = round(statistics.mean(r["seconds"] for r in runs), 1)
    m["suite"]["judge_per_check_usd"] = round(g["judge_usd"] / max(1, g["by_kind"].get("words", {}).get("checks", 1)), 5)
    # examples for the slides: a number the judge passed and the code flagged
    ex = []
    for r in g["rows"]:
        num = [x for x in r["checks"] if x["kind"] == "numbers" and not x["pass"]]
        wrd = [x for x in r["checks"] if x["kind"] == "words"]
        if num and wrd and wrd[0]["pass"]:
            ex.append({"task": r["task"], "rep": r["rep"], "numbers": num[0]["why"], "judge": wrd[0]["why"][:240],
                       "reply": r["turns"][-1]["reply"][:600]})
    m["suite"]["judge_vs_code"] = ex
    # the Thursday failures (what the suite caught)
    m["suite"]["thursday_caught"] = [f for f in m["suite"]["fails"] if f["prompt"] == "thursday"]
    for tag in ("v1_good_k3",):
        if sv[tag]:
            v1 = sv[tag]
            cats = {}
            for r in v1["rows"]:
                for x in r["checks"]:
                    if not x["pass"]:
                        cats.setdefault(x["kind"], 0)
                        cats[x["kind"]] += 1
            m["suite"]["v1_fail_checks"] = cats
            m["suite"]["v1_errors"] = sum(1 for r in v1["rows"] if r["error"])
            m["suite"]["v1_judge_empty"] = sum(1 for r in v1["rows"] for x in r["checks"] if x["kind"] == "words" and not x["pass"]
                                               and (not x["why"].strip() or x["why"].strip().startswith("{")))

ea = load("error_analysis.json")
if ea:
    m["error_analysis"] = ea
rc = load("suite_recheck.json")
if rc:
    m["recheck"] = rc

# ------------------------------------------------------------------------------------------- judges, DeepEval
cal = load("judge_calibration.json")
if cal:
    m["calib"] = {"items": cal["items"], "summary": cal["summary"], "usd": cal["usd"], "model": cal["judge_model"],
                  "examples": [{"id": r["id"], "label": r["label"], "naive": r["judges"]["naive"]["pass"],
                                "grounded": r["judges"]["grounded"]["pass"], "note": r["note"],
                                "naive_reason": r["judges"]["naive"]["reason"][:220], "grounded_reason": r["judges"]["grounded"]["reason"][:220]}
                               for r in cal["rows"] if r["kind"] == "planted"][:16]}
de = load("deepeval_run.json")
if de:
    m["deepeval"] = {"version": de["deepeval"], "tool": {k: de["tool_correctness"][k] for k in ("runs", "passed")},
                     "geval": {k: v for k, v in de["geval"].items() if k != "rows"}}
de1 = load("deepeval_run_v1.json")
if de1:
    m["deepeval_v1"] = {k: v for k, v in de1["geval"].items() if k != "rows"}

# ------------------------------------------------------------------------------------------- guards
det = load("guards_detectors.json")
if det:
    m["detectors"] = {k: {x: det[k].get(x) for x in ("attacks", "caught", "catch_rate", "benign", "false_alarms", "false_alarm_rate",
                                                     "median_ms", "usd", "usd_per_check", "model", "missed", "false_alarm_ids", "errors", "checked")}
                      for k in ("deberta", "nemo", "presidio")}
    m["detectors"]["set"] = det["set"]
    d_ = m["detectors"]
    m["detector_rows"] = [
        {"name": "Injection classifier · ProtectAI DeBERTa v3 (CPU)", "catch": d_["deberta"]["catch_rate"], "fa": d_["deberta"]["false_alarm_rate"],
         "ms": f"{d_['deberta']['median_ms']:.0f} ms", "cost": "$0 (your CPU)"},
        {"name": "NeMo Guardrails · self check input (Claude Haiku)", "catch": d_["nemo"]["catch_rate"], "fa": d_["nemo"]["false_alarm_rate"],
         "ms": f"{(d_['nemo']['median_ms'] or 0) / 1000:.1f} s", "cost": f"${d_['nemo']['usd_per_check']:.5f}" if d_["nemo"].get("usd_per_check") else "–"},
        {"name": "PII · Presidio + spaCy small", "catch": d_["presidio"]["catch_rate"], "fa": d_["presidio"]["false_alarm_rate"],
         "ms": f"{d_['presidio']['median_ms']:.0f} ms", "cost": "$0 (your CPU)"}]
    rows = det["rows"]
    m["detectors"]["mail_rows"] = [{"id": r["id"], "label": r["label"], "deberta_p": r["deberta_p"], "nemo": r.get("nemo")}
                                   for r in rows if r["id"].startswith("mail")]
    m["detectors"]["fa_rows"] = [{"id": r["id"], "text": r["text"][:140], "deberta_p": r["deberta_p"], "nemo": r.get("nemo")}
                                 for r in rows if not r["label"] and r["deberta"]]
ga = {"good": load("guards_attacks_r1.json"), "thursday": load("guards_attacks_thu.json"), "a10": load("guards_attacks_a10.json")}
if ga["good"] and ga["thursday"]:
    from collections import defaultdict
    table = defaultdict(dict)
    for p in ("good", "thursday"):
        for r in ga[p]["rows"]:
            if p == "good" and r["id"] == "A10" and r["set"] == "all" and ga["a10"]:
                r = next(x for x in ga["a10"]["rows"] if x["id"] == "A10")   # rerun after the PII fix (16 Nov)
            table[r["id"]].update({"id": r["id"], "title": r["title"], "owasp": r["owasp"], "channel": r["channel"],
                                   f"{p}_{r['set']}": r["succeeded"], f"{p}_{r['set']}_why": r["why"],
                                   f"{p}_{r['set']}_stopped": r["stopped_by"]})
    t = sorted(table.values(), key=lambda r: r["id"])
    asr = {f"{p}_{s}": round(sum(1 for r in t if r.get(f"{p}_{s}")) / len(t), 3) for p in ("good", "thursday") for s in ("off", "all")}
    asr_n = {f"{p}_{s}": sum(1 for r in t if r.get(f"{p}_{s}")) for p in ("good", "thursday") for s in ("off", "all")}
    lat = defaultdict(list)
    for p in ("good", "thursday"):
        for r in ga[p]["rows"]:
            for e in r["guard_events"]:
                if e.get("ms"):
                    lat[e["guard"]].append(e["ms"])
    m["attacks"] = {"rows": t, "asr": asr, "n": asr_n, "of": len(t),
                    "guard_ms": {k: {"median": round(q(v, .5), 2), "p95": round(q(v, .95), 2), "n": len(v)} for k, v in lat.items()},
                    "usd": round((ga["good"]["usd"] or 0) + (ga["thursday"]["usd"] or 0), 2),
                    "stopped_counts": {}}
    sc = defaultdict(int)
    for r in t:
        for g_ in r.get("thursday_all_stopped") or []:
            sc[g_] += 1
    m["attacks"]["stopped_counts"] = dict(sc)

rp = load("replay.json")
if rp:
    r0 = rp["rows"][0]
    m["replay"] = {"turns": r0["turns"], "saved1": r0["saved_after_turn_1"], "saved2": r0["saved_after_turn_2"],
                   "runs": len(rp["rows"]), "refused_all": all(any(c.get("refused_by") for c in r["turns"][0]["calls"]) for r in rp["rows"]),
                   "committed_after_yes": all(bool(r["saved_after_turn_2"]) for r in rp["rows"])}
rpb = load("replay_v1_bug.json")
if rpb:
    m["replay_bug"] = {"saved2": [bool(r["saved_after_turn_2"]) for r in rpb["rows"]], "runs": len(rpb["rows"])}

# ------------------------------------------------------------------------------------------- online, promptfoo, CI
on = load("online_evals.json")
if on:
    m["online"] = {k: on[k] for k in ("traces", "sampled_for_judge", "scores_posted", "dashboard", "cost_per_conversation_usd", "judge_usd",
                                      "window_hours")}
    m["online"]["commit_without_yes"] = sum(1 for r in on["rows"] if r["commit_without_yes"])
    m["online"]["unsupported"] = sum(1 for r in on["rows"] if r["unsupported_amount"])
    m["online"]["grounded_fail"] = sum(1 for r in on["rows"] if r.get("grounded_reply") is False)
    m["online"]["grounded_n"] = sum(1 for r in on["rows"] if "grounded_reply" in r)
pf = load("promptfoo_eval.json")
if pf:
    cells = pf.get("cells") or []

    def lab(c):
        return "Thursday" if str(c["prompt"]).lower().startswith("thursday") else "good"
    m["promptfoo"] = {"version": pf.get("version"), "by_prompt": {}}
    for c in cells:
        d = m["promptfoo"]["by_prompt"].setdefault(lab(c), {"tests": 0, "passed": 0, "asserts": 0, "asserts_passed": 0, "cost": 0.0, "failed": []})
        d["tests"] += 1
        d["passed"] += int(bool(c["pass"]))
        d["asserts"] += len(c["asserts"])
        d["asserts_passed"] += sum(1 for a in c["asserts"] if a["pass"])
        d["cost"] = round(d["cost"] + (c["cost"] or 0), 4)
        if not c["pass"]:
            d["failed"].append({"test": c["test"], "asserts": [a["metric"] for a in c["asserts"] if not a["pass"]]})
rt = load("promptfoo_redteam.json")
if rt:
    m["redteam"] = {"by_target": rt.get("by_target"), "version": rt.get("version"),
                    "cells": [{k: c[k] for k in ("target", "plugin", "pass")} | {"attack": c["attack"][:160], "reason": c["reason"][:200]}
                              for c in rt.get("cells") or []]}
ci, ci1 = load("ci_gate.json"), load("ci_gate_v1.json")
if ci or ci1:
    m["ci"] = {**((ci1 or {}).get("runs") or {}), **((ci or {}).get("runs") or {})}
    if ci1:
        m["ci_v1"] = ci1["runs"]

# ------------------------------------------------------------------------------------------- spend, Argus
spend_parts = sorted((json.loads(f.read_text()) for f in (LOGS / "spend_parts").glob("*.json")), key=lambda r: r["at"]) \
    if (LOGS / "spend_parts").exists() else []
if spend_parts:
    by = {}
    for r in spend_parts:
        e = by.setdefault(r["experiment"], {"usd": 0.0, "calls": 0})
        e["usd"] = round(e["usd"] + r["usd"], 4)
        e["calls"] += r["calls"]
    m["spend"] = {"total": round(sum(r["usd"] for r in spend_parts), 2), "by": by}
    NAMES = {"incident": "The incident, reproduced (55 runs)", "suite_good_k3": "Suite, good prompt, k=3 (v1 + v2)",
             "suite_thursday_k1": "Suite, Thursday prompt (v1 + v2)", "guards_attacks_r1": "Attacks, good prompt, off/all",
             "guards_attacks_thu": "Attacks, Thursday prompt, off/all", "guards_attacks_a10": "Attack A10 rerun",
             "guards_detectors_nemo": "NeMo self-check (Haiku)", "online_evals_judge": "Online judge, sampled (Haiku)",
             "promptfoo_eval": "promptfoo eval", "promptfoo_redteam": "promptfoo red team (2 runs)",
             "judge_calibration": "Judge calibration, 3 judges (Haiku)", "deepeval_geval": "DeepEval GEval (Haiku)",
             "ci_gate": "CI gate runs (estimate)", "replay": "Incident replay with guards",
             "argus_api_test_and_record": "Argus: API test + screenshots", "argus_load": "Argus load test (Haiku)"}
    m["spend_rows"] = sorted([{"name": NAMES.get(k, k), "usd": v["usd"], "calls": v["calls"]} for k, v in by.items()],
                             key=lambda r: -r["usd"])
    (LOGS / "spend.json").write_text(json.dumps({"note": "Every model call our experiments made for Lecture 6 (US$ from token counts x "
                                                          "list prices; Argus's own spend is in its admin status).",
                                                  "total_usd": m["spend"]["total"], "by_experiment": by, "runs": spend_parts}, indent=1))
at = load("argus_api_test.json")
if at:
    m["argus_test"] = {"passed": at["passed"], "of": at["of"], "at": at["at"], "failed": [c["check"] for c in at["checks"] if not c["ok"]]}
for n in (30,):
    ld = load(f"argus_load_{n}.json")
    if ld:
        m["argus_load"] = {k: ld[k] for k in ("n", "students_ok", "chat_s", "attack_s", "join_s", "wall_s", "wall_seconds", "model_for_test")}
        m["argus_load"]["errors"] = len(ld["errors"])
ar = load("argus_record.json")
if ar:
    m["argus_record"] = ar
pr = HERE / "experiments" / "promptfoo" / "prompts"
if (pr / "good.txt").exists():
    m["prompts"] = {"good": (pr / "good.txt").read_text(), "thursday": (pr / "thursday.txt").read_text()}
m["argus_url"] = "https://rajatworkspace--northbridge-argus.us-east.modal.run"

# =========================================================================================== v2 (16 Nov): Observability and Evals
# ------------------------------------------------------------------------------------------- the demo turns, in three tools
tv, tsp, rb = load("traces_v2.json"), load("traces_v2_spans.json") or {}, load("readback.json")


def _cut(x, n=260):
    s_ = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, default=str)
    s_ = re.sub(r"\s+", " ", s_.replace("**", "")).strip()
    return s_ if len(s_) <= n else s_[:n].rsplit(" ", 1)[0] + " …"


def _whole(x):
    """Only whole sentences: a text the notebook stored cut mid-sentence loses its unfinished last sentence, not its meaning."""
    s_ = re.sub(r"\s+", " ", str(x or "").replace("**", "")).strip()
    if s_.endswith((".", "!", "?", ".'", '."', ".”")):
        return s_
    ends = [m_.end() for m_ in re.finditer(r"[.!?]['\"”]?(?= )", s_)]
    return s_[:ends[-1]] if ends else s_


def _dur(s_):
    import datetime as dt
    f = lambda x: dt.datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp()
    return round((f(s_["end_time"]) - f(s_["start_time"])) * 1000)


def _j(v):
    try:
        return json.loads(v) if isinstance(v, str) else v
    except ValueError:
        return v


if tv and "slim_tree" in dir():
    back = {(t["run"], t["turn"]): t for t in (rb or {}).get("traces", [])}
    demo = {"backends": tv["backends"], "at": tv["at"][:10]}
    for run, r in tv["rows"].items():
        for i, t in enumerate(r["turns"], 1):
            key = run if len(r["turns"]) == 1 else f"{run}_t{i}"
            spans = [s_ for s_ in tsp.get(run, []) if s_["context"]["trace_id"][2:] == t["trace_id"]]
            chats = sorted([s_ for s_ in spans if s_["name"].startswith("chat ")], key=lambda s_: s_["start_time"])
            tools = sorted([s_ for s_ in spans if s_["name"].startswith("execute_tool ")], key=lambda s_: s_["start_time"])
            root = next((s_ for s_ in spans if s_["name"].startswith("invoke_agent")), None)
            b = back.get((run, i), {})
            d = {"text": t["text"], "reply": t["reply"], "reply_short": _cut(t["reply"], 420), "trace_id": t["trace_id"], "tokens_in": t["tokens_in"],
                 "tokens_out": t["tokens_out"], "tokens": t["tokens_in"] + t["tokens_out"], "usd": t["usd"], "seconds": t["seconds"],
                 "model_calls": t["model_calls"], "tools": len(t["calls"]), "spans": len(spans), "session": r["session"], "prompt": r["prompt"],
                 "calls": [{"tool": c["tool"], "confirm": c["args"].get("confirm")} for c in t["calls"]],
                 "links": {**t["links"], "langsmith_public": (b.get("langsmith") or {}).get("public_url"),
                           "langsmith": (b.get("langsmith") or {}).get("ui_url") or t["links"].get("langsmith")},
                 "trace": slim_tree(spans), "saved": r["saved"][0] if (r["saved"] and i == len(r["turns"])) else None}
            if root:
                a = root["attributes"]
                d["labels"] = {"user": a.get("user.id"), "session": a.get("session.id"), "prompt": a.get("ledgerline.prompt"),
                               "tags": a.get("langfuse.trace.tags"), "usd": a.get("ledgerline.cost_usd"), "tokens": a.get("gen_ai.usage.total_tokens")}
            if chats:
                c0 = chats[0]["attributes"]
                out0 = _j(c0.get("output.value"))
                d["gen"] = {"title": chats[0]["name"], "rows": [
                    ["what it is", "one call to the model", 0, False],
                    ["model", c0.get("gen_ai.request.model"), 0, False],
                    ["took", f"{_dur(chats[0]) / 1000:.2f} s", 0, False],
                    ["went in", f"{c0.get('gen_ai.usage.input_tokens'):,} tokens: the system prompt, Emma's memory, the tool list, her message", 1, False],
                    ["last message in", _cut(c0.get("input.value"), 150), 1, False],
                    ["came out", f"{c0.get('gen_ai.usage.output_tokens'):,} tokens", 2, False],
                    ["the output", ("a request to call " + ", ".join(f"{x['tool']}({json.dumps(x['args'])})" for x in out0)) if isinstance(out0, list)
                     else _cut(out0, 150), 2, True],
                    ["cost", f"${c0.get('ledgerline.cost_usd'):.4f}  =  tokens × the model's price", 3, True]]}
                d["gens"] = [{"n": j + 1, "tin": c["attributes"].get("gen_ai.usage.input_tokens"), "tout": c["attributes"].get("gen_ai.usage.output_tokens"),
                              "usd": c["attributes"].get("ledgerline.cost_usd"), "s": round(_dur(c) / 1000, 2)} for j, c in enumerate(chats)]
            if tools:
                pick = next((x for x in reversed(tools) if x["attributes"].get("ledgerline.confirm") is True), tools[0])
                ta = pick["attributes"]
                res = _j(ta.get("gen_ai.tool.call.result"))
                d["tool"] = {"title": pick["name"], "rows": [
                    ["what it is", "one tool call: our code, acting in Ledgerline", 0, False],
                    ["tool", ta.get("gen_ai.tool.name"), 0, False],
                    ["took", f"{_dur(pick)} ms", 0, False],
                    ["arguments", _cut(ta.get("gen_ai.tool.call.arguments"), 200), 1, True],
                    ["result", _cut({k: v for k, v in res.items() if k in ("ok", "request_no", "status", "free_total", "item_code", "quantity",
                                                                           "estimated_value", "approver")} if isinstance(res, dict) else res, 230), 2, True],
                    ["succeeded", str(ta.get("ledgerline.ok")), 2, False]]}
            d["back"] = {k: ({x: v.get(x) for x in ("arrived", "has_input", "has_output", "tokens_in", "tokens_out", "cost_usd", "runs", "spans",
                                                    "observations", "nodes_with_input", "nodes_with_output", "nodes_with_tool_args")} if v else None)
                         for k, v in ((k, b.get(k)) for k in ("langfuse", "langsmith", "sentry"))}
            d["talk"] = [{"who": "emma", "text": t["text"]}, {"who": "bot", "text": _cut(t["reply"], 380), "n_tools": len(t["calls"])}]
            demo[key] = d
    inc_sp = [s_ for s_ in tsp.get("incident", [])]
    demo["incident"]["commit_span"] = span_attrs(inc_sp, True)
    demo["incident"]["preview_span"] = span_attrs(inc_sp, False)
    # one row per tool for the "three tools, one trace" table: what each read back, by its own API
    if rb:
        rows = []
        for t in rb["traces"]:
            for tool, nm in (("langfuse", "Langfuse"), ("langsmith", "LangSmith"), ("sentry", "Sentry")):
                v = t.get(tool) or {}
                rows.append({"turn": {"ordinary": "Stock question", "good2": f"The usual, turn {t['turn']}", "incident": "Friday's turn"}[t["run"]],
                             "tool": nm, "arrived": bool(v.get("arrived")),
                             "io": bool(v.get("has_input") and v.get("has_output")) if tool != "sentry" else bool(v.get("nodes_with_input") and v.get("nodes_with_output")),
                             "tokens": (v.get("tokens_in") or 0) + (v.get("tokens_out") or 0), "sent_tokens": t["sent"]["tokens_in"] + t["sent"]["tokens_out"],
                             "cost": v.get("cost_usd"), "sent_cost": t["sent"]["usd"]})
        demo["readback"] = rows
        demo["readback_by_tool"] = {nm: {"traces": sum(1 for x in rows if x["tool"] == nm and x["arrived"]), "of": sum(1 for x in rows if x["tool"] == nm),
                                         "io": sum(1 for x in rows if x["tool"] == nm and x["io"]),
                                         "tokens_match": sum(1 for x in rows if x["tool"] == nm and x["tokens"] == x["sent_tokens"]),
                                         "cost_match": sum(1 for x in rows if x["tool"] == nm and x["cost"] is not None and abs(x["cost"] - x["sent_cost"]) < 1e-6)}
                                    for nm in ("Langfuse", "LangSmith", "Sentry")}
    rb1 = load("readback_first.json")      # the first send (16 Nov), before we sent Sentry our own cost figure
    if rb1:
        t1 = next((t for t in rb1["traces"] if t["run"] == "incident"), None)
        if t1:
            demo["sentry_first"] = {"cost": (t1.get("sentry") or {}).get("cost_usd"), "sent": t1["sent"]["usd"]}
    m["demo"] = demo

# the same input, twenty runs: what each run of the no-date message did under the Thursday prompt
if all(inc.values()):
    m["incident"]["nodate_runs"] = [{"i": j + 1, "saved": bool(r.get("committed")), "tools": len(r["calls"])}
                                    for j, r in enumerate([r for tg in ("r1", "r2") for r in inc[tg]["rows"] if r["prompt"] == "thursday"])]
    nd = m["incident"]["nodate"]["thursday"]
    m["incident"]["nodate_fine"] = nd["runs"] - nd["committed"]
    m["incident"]["nodate_fine_pct"] = round(100 * (nd["runs"] - nd["committed"]) / nd["runs"])
    m["incident"]["nodate_rate_pct"] = round(100 * nd["committed"] / nd["runs"])
    m["incident"]["fine1"] = f"{(nd['runs'] - nd['committed']) / nd['runs']:.2f}"

# what Thursday broke, in full sentences (one row per failing task; nothing cut)
if sv.get("thursday_k1"):
    rows = []
    for r in sv["thursday_k1"]["rows"]:
        if r["pass"]:
            continue
        said = " Then: ".join(f"“{t['text']}”" for t in r["turns"])
        prs = [(i, c["args"].get("confirm")) for i, t in enumerate(r["turns"], 1) for c in t["calls"] if c["tool"] == "create_purchase_request" and c.get("ok", True)]
        if any(cf for _, cf in prs):
            first = next(i for i, cf in prs if cf)
            did = f"It saved the request in turn {first}" + (", before Emma had answered anything." if first == 1 else ".")
        else:
            # nothing is cut on this slide: quote, whole, the one line of the reply that the failed check objected to
            needle = {"T10": "under £250,000", "T20": "£1,000,000"}.get(r["task"])
            lines = [x.strip().lstrip("-").strip().replace("**", "") for x in r["turns"][-1]["reply"].split("\n") if x.strip()]
            line = next((x for x in lines if needle and needle in x), lines[0])
            did = f"It saved nothing. It told Emma: “{line}”"
        KIND = {"outcome": "Ledgerline (code)", "trajectory": "tool calls (code)", "numbers": "£ figures (code)", "words": "judge"}
        failed = [f"{KIND.get(x['kind'], x['kind'])}: {x['why']}" for x in r["checks"] if not x["pass"]]
        rows.append({"task": r["task"], "title": r["title"], "asked": said, "did": did, "failed": " · ".join(failed), "n_failed": len(failed),
                     "agent_fault": any(x["kind"] in ("outcome", "trajectory") and not x["pass"] for x in r["checks"])})
    m["suite"]["thursday_sentences"] = rows
    m["suite"]["thursday_failed_tasks"] = len(rows)
    m["suite"]["thursday_confirm_tasks"] = sum(1 for x in rows if x["agent_fault"])

# a real judge verdict for the judge-prompt slide: T03 under the Thursday prompt (the judge failed the reply, with its reason)
if sv.get("thursday_k1"):
    r = next((x for x in sv["thursday_k1"]["rows"] if x["task"] == "T03"), None)
    if r:
        w = next(x for x in r["checks"] if x["kind"] == "words")
        ev = [e for e in r["evidence"] if e.get("tool") == "create_purchase_request"]
        res_ = (ev[-1].get("result") or {}) if ev else {}
        m["judge_example"] = {"task": "T03", "reply": _cut(r["turns"][-1]["reply"], 215), "reason": w["why"], "pass": w["pass"],
                              "evidence": (f"create_purchase_request(confirm={str((ev[-1].get('args') or {}).get('confirm')).lower()}) returned "
                                           f"request_no {res_.get('request_no')}, status {res_.get('status')}") if ev else None, "usd": w.get("judge_usd"), "tokens": w.get("judge_tokens")}

# ------------------------------------------------------------------------------------------- multi-turn: simulated conversations
cv = load("convos.json")
if cv:
    PERS = ["terse", "impatient"]
    order = []
    for r in cv["rows"]:
        if r["scenario"] not in order:
            order.append(r["scenario"])
    grid = []
    for sc in order:
        row = {"scenario": sc, "title": next(r["title"] for r in cv["rows"] if r["scenario"] == sc), "cells": [], "why": []}
        for prompt in ("good", "thursday"):
            for pe in PERS:
                r = next((x for x in cv["rows"] if x["scenario"] == sc and x["prompt"] == prompt and x["persona"] == pe), None)
                row["cells"].append(None if r is None else ("e" if r["error"] else "p" if r["pass"] else "f"))
                row["why"].append(None if (r is None or r["pass"]) else "; ".join(f"{c['name']}: {c['why']}" for c in r["checks"] if not c["pass"]))
        grid.append(row)
    fails = []
    for r in cv["rows"]:
        if r["pass"]:
            continue
        for c in r["checks"]:
            if not c["pass"]:
                fails.append({"prompt": "Thursday" if r["prompt"] == "thursday" else "good", "persona": r["persona"], "title": r["title"],
                              "check": c["name"], "who": "code" if c["kind"] in ("outcome", "trajectory", "turns") else "judge", "why": c["why"],
                              "turns": len(r["turns"])})
    one = next((r for r in cv["rows"] if r["scenario"] == "change_mind" and r["prompt"] == "good" and r["persona"] == "impatient"), cv["rows"][0])
    thu = next((r for r in cv["rows"] if r["scenario"] == "change_mind" and r["prompt"] == "thursday" and r["persona"] == "impatient"), None)

    def talk(r, n=330):
        out = []
        for t in r["turns"]:
            out.append({"who": "emma", "text": t["emma"]})
            prs = [f"create_purchase_request({'save' if c['args'].get('confirm') else 'preview'}, {c['args'].get('quantity'):,})" for c in t["calls"]
                   if c["tool"] == "create_purchase_request" and c["args"].get("quantity")]
            out.append({"who": "bot", "text": _cut(t["reply"], n), "tools": prs, "n_tools": len(t["calls"])})
            out[-2]["text"] = _cut(t["emma"], 200)
        return out
    m["convos"] = {"summary": cv["summary"], "grid": grid, "fails": fails, "n": len(cv["rows"]), "usd": cv.get("usd"),
                   "personas": PERS, "scenarios": [{"key": sc, "title": g["title"]} for sc, g in zip(order, grid)],
                   "example": {"goal": one["goal"], "expect": one["expect"], "persona": one["persona"], "talk": talk(one, 225), "pass": one["pass"],
                               "checks": [{"name": c["name"], "who": "code" if c["kind"] in ("outcome", "trajectory", "turns") else "judge", "pass": c["pass"],
                                           "why": c["why"]} for c in one["checks"]], "turns": len(one["turns"]), "usd": one["usd"],
                               "session": one["session"], "saved": one["writes"]["requests"] if isinstance(one.get("writes"), dict) else None},
                   "example_thursday": thu and {"talk": talk(thu, 250), "pass": thu["pass"], "turns": len(thu["turns"]),
                                                "failed": [{"name": c["name"], "why": c["why"]} for c in thu["checks"] if not c["pass"]],
                                                "checks": [{"name": c["name"], "who": "code" if c["kind"] in ("outcome", "trajectory", "turns") else "judge",
                                                            "pass": c["pass"], "why": c["why"]} for c in thu["checks"]],
                                                "saved": thu["writes"]["requests"] if isinstance(thu.get("writes"), dict) else None},
                   "rescored": cv.get("rescored"), "rejudged": cv.get("rejudged")}
    cv1 = load("convos_v1.json")
    if cv1:
        m["convos"]["first_pass"] = {k: {"passed": v["passed"], "conversations": v["conversations"]} for k, v in cv1["summary"].items()}

# ------------------------------------------------------------------------------------------- the notebooks' own recorded runs
nb = {}
for name in ("nb6a_turn", "nb6a_incident", "nb6a_langfuse_tour", "nb6b_good_t02", "nb6b_judge", "nb6b_deepeval", "nb6b_thursday_t02",
             "nb6c_scripted", "nb6c_sim_good", "nb6c_judge_good", "nb6c_sim_thursday", "nb6c_deepeval_good", "nb6c_deepeval_thursday",
             "nb6c_deepeval_sim", "nb6d_rag", "nb6d_ragas_rag", "nb6d_ragas_broken", "nb6d_agent_good", "nb6d_agent_thursday", "nb6d_ragas_agent"):
    if (LOGS / f"{name}.json").exists():
        nb[name] = json.loads((LOGS / f"{name}.json").read_text())
if "nb6c_scripted" in nb:
    sc = nb["nb6c_scripted"]
    m["scripted"] = {"talk": [x for t in sc["turns"] for x in ({"who": "script", "text": t["text"]}, {"who": "bot", "text": _cut(t["reply"], 420),
                                                                                                    "n_tools": len(t["calls"])})],
                     "saved": len(sc["saved"]), "asked": _cut(sc["turns"][0]["reply"].strip().split("\n")[-1], 160)}
if "nb6a_langfuse_tour" in nb:
    t = nb["nb6a_langfuse_tour"]
    m["tour"] = {"sessions": t.get("sessions"), "scores": t.get("scores"), "dataset_items": len((t.get("dataset") or {}).get("items") or []),
                 "dataset": (t.get("dataset") or {}).get("name"), "prompt": ((t.get("prompt_versions") or [{}])[0])}
    sn = (t.get("scores") or {}).get("newest_100_by_name") or {}
    m["tour"]["score_names"] = ", ".join(sorted(sn)) or None
if "nb6c_deepeval_good" in nb and "nb6c_deepeval_thursday" in nb:
    rows = []
    for k in nb["nb6c_deepeval_good"]:
        g, t = nb["nb6c_deepeval_good"][k], nb["nb6c_deepeval_thursday"].get(k, {})
        rows.append({"metric": k, "good": g.get("score"), "good_pass": g.get("passed"), "thursday": t.get("score"), "thursday_pass": t.get("passed"),
                     "reason": _whole(t.get("reason") or g.get("reason") or g.get("error") or "")})
    m["deepeval_conv"] = rows
if "nb6c_deepeval_sim" in nb:
    m["deepeval_sim"] = {"turns": len(nb["nb6c_deepeval_sim"]["turns"]), "saved": len(nb["nb6c_deepeval_sim"]["saved"])}
if "nb6d_ragas_rag" in nb:
    m["ragas"] = {"rows": [{"q": r["question"], "faithfulness": r.get("faithfulness"), "precision": r.get("context_precision"),
                            "recall": r.get("context_recall")} for r in nb["nb6d_ragas_rag"]]}
    if "nb6d_ragas_broken" in nb:
        m["ragas"]["broken"] = [{"case": k, "faithfulness": v.get("faithfulness"), "precision": v.get("context_precision"), "recall": v.get("context_recall")}
                                for k, v in nb["nb6d_ragas_broken"].items()]
    if "nb6d_ragas_agent" in nb:
        m["ragas"]["agent"] = nb["nb6d_ragas_agent"]
    if "nb6d_rag" in nb:
        m["ragas"]["found"] = [{"q": r["question"], "found": ", ".join(c.split("]")[0][1:] for c in r["contexts"][:3]), "answer": _cut(r["answer"], 200)}
                               for r in nb["nb6d_rag"]]
sc2 = load("scores_v2.json")
if sc2:
    NAMES2 = {("ordinary", 1): "Stock question", ("good2", 1): "The usual, turn 1 (preview)", ("good2", 2): "The usual, turn 2 (the yes)",
              ("incident", 1): "Friday's turn (Thursday prompt)"}
    m["scores_v2"] = [{"turn": NAMES2.get((r["run"], r["turn"]), r["run"]), "value": r["commit_without_yes"], "why": r["why"],
                       "langfuse": r.get("langfuse") == 200, "langsmith": r.get("langsmith") == 200} for r in sc2["rows"]]
rd = load("redact_demo.json")
if rd:
    m["redact"] = {"before": rd["before"], "after": rd["after"], "ms": rd["ms"], "found": ", ".join(f["type"] for f in rd["found"]), "n": len(rd["found"])}
m["nb_html"] = sorted(str(f.relative_to(HERE)) for f in (HERE / "nb").glob("*.html")) if (HERE / "nb").exists() else []
m["nb_have"] = sorted(nb)
m["nb_runs"] = {}
for f in sorted((HERE / "nb").glob("*.txt")) if (HERE / "nb").exists() else []:
    head = f.read_text().split("\n")[:2]
    m["nb_runs"][f.stem] = {"line": head[0], "ok": len(head) > 1 and head[1].strip() == "OK"}
m["colab"] = {k: f"https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/{k}.ipynb"
              for k in ("NB6a_tracing", "NB6b_evals_deepeval", "NB6c_multiturn_evals", "NB6d_ragas")}

# ------------------------------------------------------------------------------------------- spend: v1 kept, v2 added
if spend_parts:
    v2 = [r for r in spend_parts if r["experiment"].startswith("v2_")]
    v1 = [r for r in spend_parts if not r["experiment"].startswith("v2_")]
    m["spend"]["v1"] = round(sum(r["usd"] for r in v1), 2)
    m["spend"]["v2"] = round(sum(r["usd"] for r in v2), 2)
    V2N = {"v2_traces": "The demo turns, traced to three tools", "v2_convos": "20 simulated conversations (agent + Emma + judge)",
           "v2_convos_rejudge": "Conversations: one check re-judged"}
    by2 = {}
    for r in v2:
        k = "Notebooks, run live through the gateway" if r["experiment"].startswith("v2_nb_") else V2N.get(r["experiment"], r["experiment"])
        e = by2.setdefault(k, {"name": k, "usd": 0.0, "calls": 0})
        e["usd"] = round(e["usd"] + r["usd"], 4)
        e["calls"] += r["calls"]
    m["spend_rows_v2"] = sorted(by2.values(), key=lambda r: -r["usd"])
    EV = ("incident", "suite_", "judge_calibration", "deepeval", "online_evals", "promptfoo_eval", "ci_gate")
    m["spend_rows_evals"] = [r for r in m["spend_rows"] if not r["name"].startswith(("Attack", "NeMo", "promptfoo red", "Incident replay", "Argus", "v2_"))][:9]
    sj = json.loads((LOGS / "spend.json").read_text())
    sj["v1_total_usd"], sj["v2_total_usd"] = m["spend"]["v1"], m["spend"]["v2"]
    sj["v2"] = {"note": "Lecture 6 v2 (review of 16 Nov): the demo traces, the simulated conversations, the notebooks run live through Argus's "
                        "gateway (charged to Argus's budget; read back from the test students' spend).", "rows": m["spend_rows_v2"]}
    (LOGS / "spend.json").write_text(json.dumps(sj, indent=1))

media = sorted(str(p.relative_to(HERE)) for p in (HERE / "figs").rglob("*") if p.suffix.lower() in MEDIA_EXT) if (HERE / "figs").exists() else []
out = {"_source": "gen_figdata.py from lectures/L6-evals-guardrails-observability/experiments/logs", "m": m, "media": media}
js = "/* generated by gen_figdata.py; do not edit */\nwindow.L6 = " + json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=str) + ";\n"
(HERE / "figdata.js").write_text(js)
print("figdata.js:", len(js), "bytes;", "sections:", sorted(m), "; media:", len(media))
