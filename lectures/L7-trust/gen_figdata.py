"""Build figdata.js for the L7 deck from experiments/logs (stdlib only; safe to run on the laptop).

    python3 lectures/L7-trust/gen_figdata.py

Every number the deck shows is read from FD, which is written here from these logs:
  logs/identity_{flash,lite}.json   logs/six_{flash,lite}.json   logs/adversarial_{flash,lite}.json
  logs/judge.json   logs/retry_drill.json   logs/lost_reply.json   logs/draft_and_sessions.json
  logs/v2/*  (copied from v2 with provenance, see logs/v2/PROVENANCE.md)
"""
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).parent
L = HERE / "experiments" / "logs"
j = lambda p: json.loads((L / p).read_text())  # noqa: E731
FD = {}

# ---- identity
idr = []
for t in ("flash", "lite"):
    for r in j(f"identity_{t}.json")["results"]:
        o = r["orders"][0] if r["orders"] else None
        idr.append({"tier": t, "id": r["identity"], "w": r["wording"], "ne1": r["ne1"], "rohit": r["routed_to_rohit"],
                    "po": o and o["po_no"], "st": o and o["status"], "by": o and o["approved_by"], "cr": o and o["created_by"]})
FD["identity"] = idr
v2 = j("v2/identity_loop.json")["results"] + j("v2/identity_graph.json")["results"]
FD["identity_v2"] = {i: {"runs": sum(1 for r in v2 if r["identity"] == i), "ne1": sum(r["ne1"] for r in v2 if r["identity"] == i),
                         "rohit": sum(r["routed_to_rohit"] for r in v2 if r["identity"] == i)}
                     for i in ("service_account", "passthrough")}

# ---- sessions and the silent Draft
d = j("draft_and_sessions.json")
FD["sessions"] = {"KJOSHI": d["preview_as_kavita"]["preview"], "SVC_AGENT": d["preview_as_svc_agent"]["preview"]}
FD["draft"] = {"said": d["bahi_said"], "holds": d["bahi_holds"], "receipt": {k: d["tool_receipt"][k] for k in
               ("po_no", "status", "status_code", "cost_centre", "gross_value", "warning", "sent_to_supplier")},
               "preview_warning": d["tool_preview"]["warnings"][0]}
rb = j("v2/readback_default.json")["summary"]
FD["readback_v2"] = {k: {"caught": v["caught"], "drafts": v["drafts"]} for k, v in rb.items()}


FD["v2suite"] = {k: "{}/{}".format(j(f"v2/suite_{k}_summary.json")["summary"]["passed"], j(f"v2/suite_{k}_summary.json")["summary"]["cases"]) for k in ("graph", "loop", "naive")}

# ---- six scenarios: configs x tiers x reps
def slim(r):
    return {"sc": r["scenario"], "name": r["name"], "ok": r["passed"], "ne": r["never_events"], "notes": r["notes"],
            "rep": r.get("rep", 1), "cfg": r["config"], "tier": r["tier"], "tok": r["tokens_in"] + r["tokens_out"],
            "tin": r["tokens_in"], "tout": r["tokens_out"], "inr": r["cost_inr"], "sec": r["seconds"],
            "calls": r.get("model_calls"), "tools": r.get("tool_calls"),
            "turns": [{"u": t["user"], "a": t["agent"]} for t in r["turns"]]}


six = []
for t in ("flash", "lite"):
    six += [slim(r) for r in j(f"six_{t}.json")["results"]]
FD["six"] = six
FD["six_reps"] = max(r["rep"] for r in six)


def trace_of(cfg, tier, sc, rep=1):
    for t_ in (tier,):
        for r in j(f"six_{t_}.json")["results"]:
            if r["config"] == cfg and r["scenario"] == sc and r.get("rep", 1) == rep:
                return r
    return None


def slim_trace(r):
    out = []
    for s in r["trace"]:
        if s["kind"] == "user":
            out.append({"k": "user", "turn": s["turn"], "text": s["text"]})
        elif s["kind"] == "model":
            out.append({"k": "model", "turn": s["turn"], "tin": s["tokens_in"], "tout": s["tokens_out"], "sec": s["seconds"],
                        "inr": s["cost_inr"], "calls": s["calls"], "text": s["text"][:400]})
        elif s["kind"] == "tool":
            res = s["result"]
            keep = {k: res[k] for k in list(res)[:14] if k not in ("record",)}
            out.append({"k": "tool", "turn": s["turn"], "tool": s["tool"], "args": s["args"], "ok": s["ok"], "ms": s["ms"],
                        "res": keep})
        else:
            out.append({"k": "reply", "turn": s["turn"], "text": s["text"], "gated": s.get("gated")})
    return out


tr = trace_of("trust", "flash", 2)
FD["trace"] = {"cfg": "trust", "tier": "flash", "sc": 2, "passed": tr["passed"], "steps": slim_trace(tr),
               "orders": tr.get("orders"), "requests": tr.get("requests"), "events": tr.get("trust_events")}
ex = trace_of("experience", "flash", 2)
FD["trace_exp"] = {"passed": ex["passed"], "notes": ex["notes"], "steps": slim_trace(ex)}

# ---- adversarial
adv = []
for t in ("flash", "lite"):
    for r in j(f"adversarial_{t}.json")["results"]:
        adv.append({"tier": t, "cfg": r["config"], "sc": r["scenario"], "name": r["name"], "ok": r["passed"],
                    "ne": r["never_events"], "notes": r["notes"],
                    "events": [{k: e.get(k) for k in ("tool", "decision", "never_event", "rule", "error", "next_step")}
                               for e in r.get("trust_events", [])],
                    "ask": r["turns"][0]["user"] if r["turns"] else "",
                    "reply": (r["turns"][0]["agent"] or "")[:420] if r["turns"] else ""})
FD["adv"] = adv

# ---- judge vs code
try:
    jd = j("judge.json")
    FD["judge"] = {"summary": jd["summary"], "rows": [{k: r[k] for k in ("tier", "config", "rep", "scenario", "code", "judge",
                                                                         "judge_reason", "code_notes")} for r in jd["rows"]]}
except FileNotFoundError:
    FD["judge"] = None

# ---- recovery
rd = j("retry_drill.json")
FD["retry"] = {k.split("/")[0]: v for k, v in rd["summary"].items() if k.endswith("/all")}
FD["retry_modes"] = rd["summary"]
FD["retry_after"] = {k.split("/")[0]: v for k, v in j("retry_drill_after_fix.json")["summary"].items() if k.endswith("/all")}
lr = j("lost_reply.json")
FD["lost"] = {"key": lr["key"], "said": lr["bahi_did"], "saw": lr["caller_saw"], "b0": lr["budget_prd07_before"],
              "b1": lr["budget_prd07_after"], "found": [(x["po_no"], x["status"]) for x in lr["lookup_by_key"]]}
w = j("v2/approval_wait_50h.json")
FD["wait"] = {"diary": w["result"]["diary"],
              "polls": sum(1 for x in w["result"]["diary"] if x.get("why") == "poll"),
              "notifications": [{"to": n["recipient"].split("@")[0], "subject": n["subject"], "at": n["created_on"]}
                                for n in w["notifications"]],
              "history_events": len(w["history"]), "wall_s": w["seconds_wall"]}
cw = j("v2/crash_while_waiting.json")
FD["crash"] = {"down_h": cw["down_h"], "after": cw["status_after_restart"], "requests": cw["requests"], "orders": cw["orders"]}

lp = j("live_probe.json")
FD["live"] = {"p50": lp["healthz"]["p50_ms"], "p95": lp["healthz"]["p95_ms"], "ok": lp["healthz"]["ok"], "n": lp["healthz"]["n"],
              "players": json.loads(lp["healthz"]["sample"]).get("players"), "after_ms": lp["pages"]["/after?stage=agent"]["ms"],
              "when": lp["when"]}

# ---- cost and latency, from the trust/flash and trust/lite runs
cost = {}
for t in ("flash", "lite"):
    rs = [r for r in six if r["tier"] == t and r["cfg"] == "trust"]
    secs = sorted(r["sec"] for r in rs)
    cost[t] = {"n": len(rs), "inr_mean": round(statistics.mean(r["inr"] for r in rs), 3),
               "tok_mean": round(statistics.mean(r["tok"] for r in rs)), "tin_mean": round(statistics.mean(r["tin"] for r in rs)),
               "tout_mean": round(statistics.mean(r["tout"] for r in rs)),
               "calls_mean": round(statistics.mean(r["calls"] for r in rs), 1),
               "sec_p50": secs[len(secs) // 2], "sec_max": secs[-1],
               "per_sc": [{"sc": r["sc"], "inr": r["inr"], "tok": r["tok"], "calls": r["calls"], "sec": r["sec"]}
                          for r in rs if r["rep"] == 1]}
FD["cost"] = cost

out = HERE / "figdata.js"
out.write_text("/* Generated by gen_figdata.py from experiments/logs. Do not edit by hand. */\nwindow.FD = "
               + json.dumps(FD, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("wrote", out, out.stat().st_size // 1024, "KB")
