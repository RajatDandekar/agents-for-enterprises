"""Turn the experiment logs into figdata.js for the deck (stdlib only; safe to run on the laptop).

    python3 lectures/L5-the-loop/experiments/export_figdata.py

Reads logs/tasks_<agent>_or[_lite].json (run B, the run the deck reports) and logs/v2_L4_forty_summary.json.
Failure modes are recomputed here from the saved traces so every agent is counted the same way:
  loop            the same tool with the same arguments 3+ times within one message
  false_done      a reply to Kavita says placed / released / sent while no order of hers is RELEASED or CLOSED
  skipped_release an order left APPROVED but not released, on a task whose right outcome is a released order
  rohit_twice     more than one message sent to Rohit, or a second live request for the same job
  empty_reply     a reply with no words at all
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
OUT = HERE.parent / "figdata.js"
AGENTS = ["hands", "react", "bare", "prompt", "harness", "graph"]
MODELS = {"flash": "_or", "lite": "_or_lite"}
FALSE_DONE = re.compile(r"\b(placed|released|sent to (?:the )?(?:supplier|deccan|sahyadri)|on its way|has been ordered)\b", re.I)
HEDGE = re.compile(r"\bnot (?:yet )?(?:been )?(?:released|sent|placed)|draft|waiting|pending|once (?:rohit|it is|he)|"
                   r"after (?:rohit|approval|he)|cannot|can't|unable|not able|hold|before (?:i|we) can|rejected|"
                   r"preview|nothing (?:is|has been) (?:ordered|saved)|shall i|should i|would you like", re.I)


def load(agent, m):
    name = f"tasks_{agent}{MODELS[m]}{'_nudge' if agent == 'hands' else ''}.json"
    p = LOGS / name
    return json.loads(p.read_text()) if p.exists() else None, name


def short(s, n):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def failures(r):
    counts = {}
    for who, tr in r["traces"].items():
        for t in tr:
            if t.get("kind") == "tool":
                k = (who, t.get("turn"), t.get("name"), json.dumps(t.get("args"), sort_keys=True))
                counts[k] = counts.get(k, 0) + 1
    kav = [t for t in r["turns"] if t["who"] == "KJOSHI"]
    fd = [t for t in kav if t["agent"] and FALSE_DONE.search(t["agent"]) and not HEDGE.search(t["agent"])
          and not any(st in ("RL", "CL") for _, st in t["orders_after"])]
    f = dict(r["failures"])
    f["loop"] = max(counts.values(), default=0) >= 3
    f["false_done"] = bool(fd)
    f["empty_reply"] = any(not (t["agent"] or "").strip() for t in r["turns"])
    return {k: bool(f.get(k)) for k in ("loop", "false_done", "skipped_release", "rohit_twice", "empty_reply")}


res, files = {}, {}
for m in MODELS:
    for a in AGENTS:
        d, name = load(a, m)
        if not d:
            continue
        files[f"{a}_{m}"] = name
        rows = d["results"]
        fl = [failures(r) for r in rows]
        res[f"{a}_{m}"] = {
            "agent": a, "model": d["summary"]["model"], "tasks": len(rows), "passed": sum(r["passed"] for r in rows),
            "ne_tasks": sum(1 for r in rows if r["never_events"]), "ne": [ne.split(":")[0] for r in rows for ne in r["never_events"]],
            "msgs": sum(r["person_messages"] for r in rows), "nudges": sum(r["nudges"] for r in rows),
            "calls": sum(r["model_calls"] for r in rows), "tools": sum(r["tool_calls"] for r in rows),
            "tokens": sum(r["tokens_in"] + r["tokens_out"] for r in rows), "inr": round(sum(r["cost_inr"] for r in rows), 2),
            "fail": {k: sum(1 for f in fl if f[k]) for k in fl[0]},
            "per": [{"id": r["id"], "ok": r["passed"], "ne": bool(r["never_events"]), "calls": r["model_calls"],
                     "tokens": r["tokens_in"] + r["tokens_out"], "msgs": r["person_messages"],
                     "f": [k for k, v in f.items() if v], "note": short(r["note"], 90)} for r, f in zip(rows, fl)]}

TASKS = [{"id": r["id"], "name": r["name"]} for r in load("harness", "flash")[0]["results"]]


def by_id(agent, m, tid):
    d, _ = load(agent, m)
    return next(r for r in d["results"] if r["id"] == tid)


# ---- cold open: the one-round agent (L4) vs the harness on the whole job, T01, flash
def convo(r, n=260, who=None):
    return [{"who": t["who"], "day": t["day"], "kind": t["kind"], "user": short(t["user"], 200), "agent": short(t["agent"], n),
             "orders": t["orders_after"]} for t in r["turns"] if who is None or t["who"] == who]


cold = {"hands": convo(by_id("hands", "flash", "T01")), "harness": convo(by_id("harness", "flash", "T01"))}


# ---- the ReAct transcript (T01, flash): every Thought / Action / Observation of Kavita's thread
def react_steps(r):
    out = []
    for t in r["traces"]["KJOSHI"]:
        raw = (t.get("raw") or "").split("\nObservation:")[0]
        out.append({"turn": t["turn"], "raw": short(raw, 1100), "thought": short(t.get("thought"), 260),
                    "action": t.get("action"), "input": t.get("action_input"), "final": short(t.get("final"), 420),
                    "obs": short(json.dumps(t.get("observation"), ensure_ascii=False), 420) if t.get("observation") else None,
                    "err": t.get("error"), "tin": t.get("tokens_in"), "tout": t.get("tokens_out")})
    return out


r_react = by_id("react", "flash", "T01")
react = {"turns": convo(r_react, 220, "KJOSHI"), "steps": react_steps(r_react)}


# ---- the native transcript (T01, flash): the harness's model steps and tool messages
def native_steps(r, who="KJOSHI"):
    out = []
    for t in r["traces"][who]:
        if t["kind"] == "model":
            out.append({"turn": t["turn"], "k": "assistant", "text": short(t.get("thought"), 300), "calls": t.get("calls"),
                        "tin": t.get("tokens_in"), "tout": t.get("tokens_out")})
        elif t["kind"] == "tool":
            out.append({"turn": t["turn"], "k": "tool", "name": t["name"], "args": t.get("args"), "ok": t.get("ok"),
                        "blocked": t.get("blocked"), "result": short(json.dumps(t.get("result"), ensure_ascii=False), 380)})
        else:
            out.append({"turn": t.get("turn"), "k": "harness", "part": t.get("part"), "note": short(str(t.get("note") or t.get("name") or ""), 220)})
    return out


r_h = by_id("harness", "flash", "T01")
native = {"turns": convo(r_h, 220, "KJOSHI"), "steps": native_steps(r_h)}

# ---- tokens in, per model call, across the whole job (history grows)
grow = [{"turn": s["turn"], "tin": s["tin"]} for s in native["steps"] if s["k"] == "assistant"]

# ---- steps (model calls) per person message, harness and bare, flash: for the max-steps slider
def steps_per_message(agent, m):
    d, _ = load(agent, m)
    out = []
    for r in d["results"]:
        for who, tr in r["traces"].items():
            per = {}
            for t in tr:
                if t.get("kind") == "model" and t.get("node") is None:
                    per[t["turn"]] = per.get(t["turn"], 0) + 1
            out += list(per.values())
    return sorted(out)


spm = {"harness": steps_per_message("harness", "flash"), "bare": steps_per_message("bare", "flash")}

# ---- the never-event: the harness on Shakti Seals (T06, flash) against the graph
ne3 = {"harness": convo(by_id("harness", "flash", "T06"), 300, "KJOSHI"),
       "graph": convo(by_id("graph", "flash", "T06"), 300, "KJOSHI"),
       "harness_tools": [s for s in native_steps(by_id("harness", "flash", "T06")) if s["k"] == "tool"]}

# ---- the graph on the whole job: path and replies
r_g = by_id("graph", "flash", "T01")
graph = {"turns": convo(r_g, 330), "path": r_g["paths"].get("KJOSHI"),
         "model_calls": r_g["model_calls"], "tokens": r_g["tokens_in"] + r_g["tokens_out"],
         "tools": [{"node": t.get("node"), "name": t["name"], "ok": t.get("ok")} for t in r_g["traces"]["KJOSHI"] if t["kind"] == "tool"]}

# ---- the pause: T10 (Rohit has not answered), harness flash
r_p = by_id("harness", "flash", "T10")
pause = {"turns": convo(r_p, 320, "KJOSHI"), "events": [s for s in native_steps(r_p) if s["k"] == "harness"]}

# ---- harness parts at work, counted over run B
parts = {}
for m in MODELS:
    d, _ = load("harness", m)
    c = {}
    for r in d["results"]:
        for tr in r["traces"].values():
            for t in tr:
                if t.get("kind") == "harness":
                    key = t.get("part") + (":" + t["note"] if t.get("part") in ("stop", "recovery") and t.get("note") else "")
                    c[key] = c.get(key, 0) + 1
                if t.get("blocked"):
                    c["blocked:" + t["blocked"]] = c.get("blocked:" + t["blocked"], 0) + 1
    parts[m] = c
examples = {}
for m in MODELS:
    d, _ = load("harness", m)
    for r in d["results"]:
        for tr in r["traces"].values():
            for t in tr:
                if t.get("kind") == "harness" and t.get("part") in ("verify", "recovery") and t.get("part") not in examples:
                    examples[t["part"]] = {"model": m, "task": r["id"], "note": short(str(t.get("note")), 300)}

v2 = json.loads((LOGS / "v2_L4_forty_summary.json").read_text())
runA = {}
for p in sorted((LOGS / "runA_or").glob("tasks_*.json")):
    d = json.loads(p.read_text())
    runA[p.stem] = {"passed": d["summary"]["passed"],
                    "empty_tasks": sum(1 for r in d["results"] if any(not (t["agent"] or "").strip() for t in r["turns"]))}

data = {"res": res, "tasks": TASKS, "cold": cold, "react": react, "native": native, "grow": grow, "spm": spm, "ne3": ne3,
        "graph": graph, "pause": pause, "parts": parts, "examples": examples, "files": files,
        "v2": {k: {kk: v[kk] for kk in ("agent", "model", "cases", "passed", "never_event_cases", "model_calls", "tokens_in",
                                         "tokens_out", "cost_inr")} for k, v in v2["runs"].items()}, "runA": runA}
OUT.write_text("/* Generated by experiments/export_figdata.py from experiments/logs/tasks_*_or*.json (run B, 2026-10-28)\n"
               "   and logs/v2_L4_forty_summary.json. Do not edit by hand. */\nwindow.FD = " +
               json.dumps(data, ensure_ascii=False, default=str) + ";\n")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
for k, v in res.items():
    print(f"{k:14} {v['passed']:>2}/12 NE {v['ne_tasks']} msgs {v['msgs']:>3} calls {v['calls']:>4} tools {v['tools']:>4} "
          f"tok {v['tokens']:>8,} ₹{v['inr']:>6} {v['fail']}")
print("parts", parts)
print("examples", examples)
print("runA", runA)
print("spm", {k: (len(v), max(v), sum(v) / len(v)) for k, v in spm.items()})
