"""Build figdata.js (window.FD) for the Lecture 11 deck from experiments/logs. Standard library only.

    python3 lectures/L11-production/gen_figdata.py

Every number a figure draws comes from one of these logs; the deck never types a measured number by hand
without a data-fd binding or a comment naming its log.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "experiments" / "logs"


def load(name):
    p = LOGS / name
    return json.loads(p.read_text()) if p.exists() else None


FD = {}
g = load("guard_eval.json")
if g:
    FD["guard"] = {
        "n": g["n"], "versions": g["versions"],
        "guards": {k: {kk: v.get(kk) for kk in ("recall", "fpr", "caught", "attacks_n", "false_positives", "benign_n",
                                                "lookalike_fp", "offtopic_blocked", "latency_ms_p50", "latency_ms_p95",
                                                "usd_total", "usd_per_message", "per_category", "tokens_in_mean", "errors")}
                   for k, v in g["guards"].items()},
        "messages": g["messages"],
        "dec": {i: {k: bool(v.get("block")) for k, v in d.items()} for i, d in g["per_message"].items()},
        "why": {i: {"keyword": d.get("keyword", {}).get("why"), "llamaguard": d.get("llamaguard", {}).get("raw"),
                    "safeguard": d.get("safeguard", {}).get("rationale"), "nemo_topic": (d.get("nemo_topic") or {}).get("response", "")[:90]}
                for i, d in g["per_message"].items()},
        "output": [{"id": r["id"], "label": r["label"], "reply": r["reply"], "nemo": r.get("nemo_block"),
                    "lg": r.get("llamaguard_block")} for r in g["output_rails"]["rows"]],
        "output_summary": {k: v for k, v in g["output_rails"].items() if k != "rows"},
    }
inj = load("injection_eval.json")
if inj:
    FD["inj"] = {
        "summary": inj["summary"], "poison": inj.get("poison_city"), "wordings": inj["wordings"],
        "rows": [{"cond": r["cond"], "tier": r["tier"], "w": r["w"], "ne3": r["ne3"], "released": r["kaveri_released"],
                  "deccan": any(o["po_no"] > "PO/2026/01152" for o in r["deccan_orders"]),
                  "refused": [x["never_event"] for x in r["trust_refused"]], "tools": r["tools"],
                  "reply": (r["turns"][-1].get("agent") or r["turns"][-1].get("error") or "")[:420],
                  "turns": len(r["turns"]), "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"]} for r in inj["rows"]],
        "scan": [{k: s[k] for k in ("sample", "label", "llamaguard", "llamaguard_raw", "safeguard", "safeguard_rationale")}
                 for s in inj["scan"]],
        "supplier": inj["find_supplier_poisoned"],
    }
d = load("durable_order.json")
if d:
    hist = json.loads((LOGS / "durable_history.json").read_text())["events"]
    slim = []
    for e in hist:
        t = e["eventType"].replace("EVENT_TYPE_", "")
        name = ""
        for k, v in e.items():
            if k.endswith("Attributes") and isinstance(v, dict):
                name = (v.get("activityType") or {}).get("name") or v.get("signalName") or v.get("identity") or ""
                if t == "TIMER_STARTED":
                    name = v.get("startToFireTimeout", "")
        slim.append({"id": int(e["eventId"]), "type": t, "name": name, "time": e.get("eventTime", "")[11:19]})
    FD["dur"] = {"events": d["events"], "counts": d["counts"], "model_calls": d["model_calls"], "history": slim,
                 "by_type": d["history"]["by_type"], "activities": d["history"]["activities"],
                 "workers": d["history"]["workers"], "replay": d.get("replay"), "versions": d.get("versions"),
                 "replies": [{"user": r["user"], "agent": str(r["agent"])[:400]} for r in d["result"]["replies"]],
                 "killed2": d.get("killed2"), "model": d.get("model"),
                 "model_http": [{"worker": c["worker"], "messages": c["messages"], "status": c["status"]} for c in d.get("model_http", [])],
                 "model_activities": sum(1 for a in d["history"]["activities"] if a == "invoke_model_activity")}
m = load("memory_prod.json")
if m:
    FD["mem"] = {k: m.get(k) for k in ("retrieval", "permissions", "scale", "persistence", "redis_session", "redis_failover",
                                       "rate_limit", "chunks_kavita", "chunks_all", "pgvector_ext", "postgres",
                                       "hnsw_build_seconds_scaled", "scale_insert_seconds", "agree_top5_l3_vs_pg_exact",
                                       "redis_version", "l3_build_seconds")}
gw = load("gateway.json")
if gw:
    FD["gw"] = {k: gw.get(k) for k in ("budget", "fallback", "model_access", "model_access_ok", "rate_limit", "team_spend",
                                       "key_spend", "setup", "proxy_start_seconds", "litellm_version")}
c = load("cost_model.json")
if c:
    FD["cost"] = {"summary": c["summary"], "by_model": c["by_model"], "prices": c["prices_usd_per_m"], "usd_inr": c["usd_inr"],
                  "guard": c["guard_per_message"],
                  "runs": [{k: r[k] for k in ("source", "task", "model", "tokens_in", "tokens_out", "model_calls", "inr", "passed", "person_messages")}
                           for r in c["runs"]]}
(HERE / "figdata.js").write_text("/* generated by gen_figdata.py from experiments/logs; do not edit by hand */\nwindow.FD = "
                                 + json.dumps(FD, ensure_ascii=False) + ";\n")
print("figdata.js:", {k: len(json.dumps(v)) for k, v in FD.items()})
