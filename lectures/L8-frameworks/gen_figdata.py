"""Turn experiments/logs/*.json into figdata.js (the deck) and the notebook fixtures (stdlib only; safe on the laptop).

    python3 lectures/L8-frameworks/gen_figdata.py

Reads   experiments/logs/fw_<setup>[ _rep2 | _rep2b | _replay ].json, gateway.json, desks.json, loc.json
Writes  figdata.js                                  window.FD for figs.js
        bahi/bahi/course/frameworks/recorded/*.json  what NB8 shows when it has no key (bahi.course.frameworks.fixtures)
Every number on a plate is one of these, or is computed here from them.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "experiments" / "logs"
FIX = HERE.parents[1] / "bahi/bahi/course/frameworks/recorded"
FIX.mkdir(parents=True, exist_ok=True)

SETUPS = [  # key, label, short
    ("ours", "Our harness (L5, every part)", "Our harness"),
    ("bare", "Our harness, loop only", "Loop only"),
    ("openai_agents", "OpenAI Agents SDK", "Agents SDK"),
    ("openai_agents_guarded", "Agents SDK + guardrails", "SDK + guardrails"),
    ("adk", "Google ADK", "ADK"),
    ("langgraph", "LangGraph agent", "LangGraph agent"),
    ("control", "LangGraph control graph (L5)", "Control graph"),
]
LOC = json.loads((LOGS / "loc.json").read_text())
LOC_OF = {"ours": LOC["ours"]["port_lines"], "bare": LOC["ours"]["loop_only_lines"],
          "openai_agents": LOC["openai_agents"]["port_lines"],
          "openai_agents_guarded": LOC["openai_agents"]["port_lines"] + LOC["guardrail_checks_lines"],
          "adk": LOC["adk"]["port_lines"], "langgraph": LOC["langgraph"]["port_lines"], "control": LOC["control"]["port_lines"]}


def load(name):
    p = LOGS / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def short(s, n):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def merged(key, tag):
    """A run; for _rep2 the tasks that hit OpenRouter's rate limit were re-run in _rep2b (same cassette)."""
    d = load(f"fw_{key}{tag}")
    if not d:
        return None
    rows = {r["id"]: r for r in d["results"]}
    if tag == "_rep2":
        for extra in sorted(LOGS.glob(f"fw_{key}_rep2b*.json")):
            for r in json.loads(extra.read_text())["results"]:
                rows[r["id"]] = r
    return [rows[k] for k in sorted(rows)]


def summ(rows):
    ok = [r for r in rows if "turns" in r]
    return {"tasks": len(rows), "passed": sum(bool(r.get("passed")) for r in rows),
            "ne": sum(1 for r in ok if r["never_events"]), "crash": sum(1 for r in rows if r.get("crashed")),
            "calls": sum(r.get("model_calls", 0) for r in ok), "tools": sum(r.get("mcp_calls", 0) for r in ok),
            "tin": sum(r.get("tokens_in", 0) for r in ok), "tout": sum(r.get("tokens_out", 0) for r in ok),
            "inr": round(sum(r.get("cost_inr", 0) for r in ok), 2),
            "model_s": round(sum(r.get("model_seconds", 0) for r in ok), 1),
            "ne_text": [ne for r in ok for ne in r["never_events"]]}


def task_row(r):
    return {"id": r["id"], "p": bool(r.get("passed")), "ne": bool(r.get("never_events")),
            "crash": bool(r.get("crashed")), "calls": r.get("model_calls", 0),
            "inr": round(r.get("cost_inr", 0), 2), "s": round(r.get("model_seconds", 0), 1),
            "note": short(r.get("note") or r.get("crashed") or "", 120),
            "last": short(([t["agent"] for t in r.get("turns", []) if t["who"] == "KJOSHI"] or [""])[-1], 200)}


FD = {"setups": [], "tasks": [], "grid": {}}
from_l5 = json.loads((HERE.parents[0] / "L5-the-loop/experiments/logs/tasks_harness_or.json").read_text())["results"]
FD["tasks"] = [{"id": r["id"], "name": r["name"]} for r in from_l5]
for key, label, sh in SETUPS:
    r1 = merged(key, "")
    if not r1:
        continue
    r2 = merged(key, "_rep2")
    FD["setups"].append({"key": key, "label": label, "short": sh, "loc": LOC_OF[key], "run1": summ(r1),
                         "run2": summ(r2) if r2 else None})
    FD["grid"][key] = {"run1": [task_row(r) for r in r1], "run2": [task_row(r) for r in r2] if r2 else None}

# ---------------------------------------------------------------- T04 side by side (the uniform trace + replies)
FD["t04"] = {}
for key in ("ours", "openai_agents", "adk", "langgraph"):
    r = [x for x in merged(key, "") if x["id"] == "T04"][0]
    tools = [{"turn": t["turn"], "name": t["name"], "ok": t.get("ok", True),
              "args": short(json.dumps({k: v for k, v in (t.get("args") or {}).items()}, ensure_ascii=False), 90)}
             for t in r["traces"].get("KJOSHI", []) if t.get("kind") == "tool"]
    FD["t04"][key] = {"tools": tools, "calls": r["model_calls"], "inr": round(r["cost_inr"], 2),
                      "turns": [{"who": t["who"], "kind": t["kind"], "user": short(t["user"], 120),
                                 "agent": short(t["agent"], 240)} for t in r["turns"]],
                      "orders": r.get("orders")}

# ---------------------------------------------------------------- the framework's own trace for T04
oa = [x for x in merged("openai_agents", "") if x["id"] == "T04"][0]
spans = []
for turn in oa["native"].get("openai_agents-T04-KJOSHI") or []:
    for s in turn["spans"]:
        row = {"turn": turn["turn"], "type": s["type"], "name": s.get("name") or s.get("server") or ""}
        if s["type"] == "generation" and s.get("usage"):
            row["tok"] = s["usage"].get("input_tokens")
            calls = re.findall(r'"name": "([a-z_]+)"', s.get("output") or "")
            row["detail"] = ", ".join(calls) if calls else "words"
        if s["type"] == "function":
            row["detail"] = short(s.get("input"), 70)
        if s["type"] == "mcp_tools":
            row["detail"] = f"{len(s.get('result') or [])} tools"
        spans.append(row)
FD["spans_t04"] = spans
ad = [x for x in merged("adk", "") if x["id"] == "T04"][0]
FD["events_t04"] = [dict(turn=t["turn"], **{k: (short(v, 90) if isinstance(v, str) else v) for k, v in e.items()
                                           if k in ("author", "final", "text", "usage")},
                         calls=[c["name"] for c in e.get("calls", [])], results=[c["name"] for c in e.get("responses", [])])
                    for t in ad["native"].get("adk-T04-KJOSHI") or [] for e in t["events"]]
lg = [x for x in merged("langgraph", "") if x["id"] == "T04"][0]
FD["steps_t04"] = [dict(turn=t["turn"], node=s["node"], calls=[c["name"] for c in s.get("calls", [])],
                        results=[c["name"] for c in s.get("results", [])], text=short(s.get("text"), 90))
                   for t in lg["native"].get("langgraph-T04-KJOSHI") or [] for s in t["steps"]]

# ---------------------------------------------------------------- what each framework sends (T03, first call)
FD["shapes"] = {}
for key in ("openai_agents", "adk", "langgraph"):
    r = [x for x in merged(key, "") if x["id"] == "T03"][0]
    sh = r["request_shapes"]
    FD["shapes"][key] = {"tools_bytes": sh[0]["tools_bytes"], "system_bytes": sh[0]["system_bytes"],
                         "tin": [s["tokens_in"] for s in sh]}
ours_t03 = [x for x in merged("ours", "") if x["id"] == "T03"][0]
FD["shapes"]["ours_tin_total"] = ours_t03["tokens_in"]
# the replay runs captured the first request on the wire (T03, T04): ADK's additions to the system prompt
rep = load("fw_adk_replay")
oar = load("fw_openai_agents_replay")
if rep and oar:
    fa = [x for x in rep["results"] if x["id"] == "T03"][0].get("first_request")
    fo = [x for x in oar["results"] if x["id"] == "T03"][0].get("first_request")
    if fa and fo:
        sa = next(m["content"] for m in fa["messages"] if m["role"] == "system")
        so = next(m["content"] for m in fo["messages"] if m["role"] == "system")
        FD["shapes"]["adk_added"] = [l for l in sa.splitlines() if l not in so.splitlines()][:8]
        po = lambda f: next(t for t in f["tools"] if t["function"]["name"] == "create_purchase_order")
        FD["shapes"]["po_schema"] = {"openai_agents": json.dumps(po(fo), indent=1)[:1400],
                                     "adk": json.dumps(po(fa), indent=1)[:1400],
                                     "oa_bytes": len(json.dumps(po(fo))), "adk_bytes": len(json.dumps(po(fa)))}

# ---------------------------------------------------------------- overhead: replay runs, model replies instant
FD["overhead"] = {}
common = None
reps = {}
for key, *_ in SETUPS:
    d = load(f"fw_{key}_replay")
    if d:
        reps[key] = {r["id"]: r for r in d["results"] if not r.get("crashed")}
        common = set(reps[key]) if common is None else common & set(reps[key])
for key, rr in reps.items():
    ids = sorted(common)
    FD["overhead"][key] = {"tasks": ids, "wall": round(sum(rr[i]["wall_seconds"] for i in ids), 1),
                           "per_task": [rr[i]["wall_seconds"] for i in ids],
                           "model_calls": sum(rr[i]["model_calls"] for i in ids),
                           "tool_ms": round(sum(rr[i].get("tool_ms", 0) for i in ids), 1)}

# ---------------------------------------------------------------- guardrails, desks, gateway, ollama, loc
g = load("fw_openai_agents_guarded")
grep_ = load("fw_openai_agents_guarded_replay")
trips = [{"id": r["id"], "guardrail": x["guardrail"], "problem": x.get("problem"), "reply": short(x.get("reply"), 160)}
         for r in (grep_ or g)["results"] for x in r.get("guard_log", []) if x.get("tripped") or x.get("blocked")]
blocks = sum(1 for r in g["results"] for x in r.get("guard_log", []) if x.get("guardrail") == "food_grade" and x.get("blocked"))
checks = sum(1 for r in g["results"] for x in r.get("guard_log", []) if x.get("guardrail") == "food_grade")
g2 = load("fw_openai_agents_guarded_rep2")
blocks2 = [{"id": r["id"], **x} for r in (g2 or {"results": []})["results"] for x in r.get("guard_log", [])
           if x.get("guardrail") == "food_grade" and x.get("blocked")]
FD["guarded"] = {"run2_blocks": blocks2, "run2_block_tasks": [b["id"] for b in blocks2],"trips_total": sum(1 for r in g["results"] for x in r.get("guard_log", []) if x.get("tripped")),
                 "trip_tasks": sorted({r["id"] for r in g["results"] for x in r.get("guard_log", []) if x.get("tripped")}),
                 "food_checks": checks, "food_blocks": blocks, "trips": trips[:6]}
d = load("desks")
FD["desks"] = {"sdk": [{"who": m["who"], "msg": short(m["message"], 110), "by": m["answered_by"],
                        "reply": short(m["reply"], 170), "guard": m["guardrail"],
                        "spans": [s["type"] + (":" + (s.get("name") or s.get("to") or "")) for s in m["spans"]
                                  if s["type"] in ("guardrail", "handoff", "function", "agent")]} for m in d["agents_sdk"]],
               "adk": [{"who": m["who"], "msg": short(m["message"], 110), "by": m.get("answered_by"),
                        "reply": short(m.get("reply"), 170),
                        "transfers": [e["transfer"] for e in m.get("events", []) if e.get("transfer")]} for m in d["adk"]],
               "session_items": d["session"]["items_after_day1"], "inr": d["cost_inr"]}
gw = load("gateway")
FD["gateway"] = {"q": gw["question"], "models": gw["models"], "router": gw["router"], "inr": gw["cost_inr"]}
FD["loc"] = LOC
oll = []
for p in sorted(LOGS.glob("fw_ours_ollama_*.json")):
    if "T03_T04" in p.name:
        continue
    dd = json.loads(p.read_text())
    s = summ(dd["results"])
    s["model"] = dd["summary"]["model"].split(":", 1)[1]
    s["per_task"] = [task_row(r) for r in dd["results"]]
    s["s_per_call"] = round(s["model_s"] / max(1, s["calls"]), 1)
    oll.append(s)
FD["ollama"] = oll
FD["versions"] = load("fw_openai_agents")["summary"].get("versions")
spent = sum(json.loads(p.read_text())["summary"]["cost_inr"] for p in LOGS.glob("fw_*.json")
            if "_replay" not in p.name and "ollama" not in p.name and "T03_T04" not in p.name)
FD["spend_inr"] = round(spent + d["cost_inr"] + gw["cost_inr"], 1)

(HERE / "figdata.js").write_text("/* generated by gen_figdata.py from experiments/logs; do not edit */\nwindow.FD = "
                                 + json.dumps(FD, ensure_ascii=False) + ";\n")

# ---------------------------------------------------------------- notebook fixtures
board = [{"setup": s["label"], "tasks": s["run1"]["tasks"], "passed": s["run1"]["passed"],
          "never_event_tasks": s["run1"]["ne"], "model_calls": s["run1"]["calls"], "tokens_in": s["run1"]["tin"],
          "tokens_out": s["run1"]["tout"], "cost_inr": s["run1"]["inr"], "model_seconds": s["run1"]["model_s"],
          "passed_run2": s["run2"]["passed"] if s["run2"] else None, "lines_of_code": s["loc"]} for s in FD["setups"]]
(FIX / "scoreboard.json").write_text(json.dumps(board, indent=1, ensure_ascii=False))
(FIX / "guarded.json").write_text(json.dumps({
    "summary_line": (f"Agents SDK + guardrails: {g['summary']['passed']}/12 passed, {g['summary']['never_event_tasks']} "
                     f"never-event tasks; the food-grade check ran {checks} times and blocked {blocks}; the verify "
                     f"guardrail tripped {FD['guarded']['trips_total']} times."), "trips": trips}, indent=1, ensure_ascii=False))
(FIX / "desks.json").write_text(json.dumps({"agents_sdk": [{k: m[k] for k in ("who", "message", "answered_by", "reply",
                                                                               "guardrail")} for m in d["agents_sdk"]],
                                            "adk": d["adk"], "session": d["session"]}, indent=1, ensure_ascii=False, default=str))
(FIX / "gateway.json").write_text(json.dumps({"models": gw["models"], "router": gw["router"]}, indent=1, ensure_ascii=False))
(FIX / "gateway_question.json").write_text(json.dumps(
    [{"role": "system", "content": "You are Ask Rasoi at Rasoi Steel Works. Answer in two sentences."},
     {"role": "user", "content": gw["question"]}], ensure_ascii=False))
(FIX / "ollama.json").write_text(json.dumps([{k: o[k] for k in ("model", "tasks", "passed", "ne", "calls", "tin", "tout",
                                                                  "model_s", "s_per_call")} for o in oll], indent=1))
print("figdata.js:", len(json.dumps(FD)) // 1024, "KB ·", len(FD["setups"]), "setups ·", len(oll), "local models ·",
      "spend ₹", FD["spend_inr"])
