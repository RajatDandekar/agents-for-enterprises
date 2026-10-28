"""Copy the numbers and payloads the deck shows from experiments/logs/*.json into figs.js (between the DATA markers).

Standard library only, no model calls: python3 lectures/L3-the-hands/experiments/deck_data.py
Every value on a plate comes from one of the logs named in the comment above its key.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
LOG = HERE / "logs"
FIGS = HERE.parent / "figs.js"
J = lambda n: json.load(open(LOG / n))  # noqa: E731


def short(v, n=160):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n - 1] + "…"


def calls(lr, data=False):
    out = []
    for c in lr:
        row = {"svc": c["svc"], "rc": c["rc"], "err": c.get("err_cd") or "", "msg": c.get("msg") or "", "sps": c.get("sps") or [],
               "p": c.get("payload") or {}}
        if "screen" in c:
            row.update(screen=c["screen"], task=c["task"])
        if data and "data" in c:
            row["data"] = c["data"]
        out.append(row)
    return out


D = {}
# logs/naive_s3_<tier>.json — scenario 3 with Lecture 1's naive agent and with this lecture's agent
D["naive3"] = {}
for tier in ("gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"):
    d = J(f"naive_s3_gemini_{tier}.json")
    row = {}
    for lab in ("naive", "intent_tools"):
        r = d[lab]
        row[lab] = {"passed": r["passed"], "ne": r["never_events"], "calls": calls(r["live_run"]),
                    "turns": [{"user": t["user"], "agent": short(t["agent"] or "", 700)} for t in r["turns"]],
                    "tokens": r["tokens_in"] + r["tokens_out"], "inr": r["cost_inr"], "seconds": r["seconds"],
                    "orders": r["new_orders"]}
    D["naive3"][tier] = row
D["ask3"] = J("naive_s3_gemini_gemini-3.8-flash.json")["scenario"]["ask"]

# logs/granularity_gemini_<tier>.json + logs/analysis.json — the 30-task experiment
A = J("analysis.json")
D["gran"] = A["granularity"]
D["grid"] = A["grid"]
D["tasks"] = A["tasks"]
D["score"] = {m: {c: {str(k): {"p": v["passed"], "ne": v["never_events"], "notes": v["notes"], "tok": v["tokens"],
                                 "inr": v["cost_inr"], "cby": v["committed_before_yes"]} for k, v in rows.items()}
                  for c, rows in s["by_scenario"].items()} | {"summary": s["summary"]} for m, s in A["scorecard"].items()}
g = J("granularity_gemini_gemini-3.8-flash.json")
D["a15"] = {}
for cfg in ("raw", "generic", "intent"):
    r = [x for x in g["results"] if x["config"] == cfg and x["task"] == "A15"][0]
    D["a15"][cfg] = {"passed": r["passed"], "ne": r["never_events"], "new_sups": r["new_suppliers"], "orders": r["orders"],
                     "tokens": r["tokens_in"] + r["tokens_out"], "calls": r["tool_calls"],
                     "trace": [{"tool": t["tool"], "args": short(t["args"], 140), "result": short(t["result"], 170)}
                               for t in r["trace"]],
                     "reply": short(r["turns"][-1]["agent"] or "", 420)}
D["a15_ask"] = [t for t in g["tasks"] if t["id"] == "A15"][0]["ask"]

# logs/scorecard_gemini_gemini-3.8-flash.json — scenario 1, harness: the agent committed an order itself
sc = J("scorecard_gemini_gemini-3.8-flash.json")
s1 = [r for r in sc["results"] if r["scenario"] == 1 and r["config"] == "harness"][0]
D["s1_trace"] = [{"tool": t["tool"], "args": t["args"]} for t in s1["trace"]]
D["s1_ne"] = s1["never_events"]

# logs/tool_tokens.json, logs/tool_defs.json, logs/inventory.json
tt = J("tool_tokens.json")["models"]["gemini:gemini-3.8-flash"]
D["tokens"] = {k: v for k, v in tt.items()}
inv = J("inventory.json")
D["inv"] = {"counts": inv["counts"], "services": inv["services"], "tree": inv["tree_from_live_runs"],
            "procs": inv["procedures"]}
td = J("tool_defs.json")
D["intent_schemas"] = td["schemas"]["intent"]
D["find_item_schema"] = [s for s in td["schemas"]["intent"] if s["function"]["name"] == "find_item"][0]
D["raw_example"] = [s for s in td["schemas"]["raw"] if s["function"]["name"] == "po_save"][0]

# logs/live_runs.json, logs/cascades.json, logs/variants.json, logs/screen_state.json
lr = J("live_runs.json")
D["liveA"] = calls(lr["as_it_happened_PRD05"], data=True)
D["liveB"] = calls(lr["done_right_PRD07"], data=True)
D["liveSummary"] = lr["summary"]
cas = J("cascades.json")
D["casA"] = [{"svc": w["svc"], "task": w["task"], "screen": w["screen"], "user": w["user"], "rc": w["rc"], "err": w["err_cd"],
              "sps": w["sps"], "ch": w["changes"]} for w in cas["as_it_happened_PRD05"]]
D["casB"] = [{"svc": w["svc"], "task": w["task"], "screen": w["screen"], "user": w["user"], "rc": w["rc"], "err": w["err_cd"],
              "sps": w["sps"], "ch": w["changes"]} for w in cas["done_right_PRD07"]]
va = J("variants.json")
D["variants"] = [{"case": c["case"], "type": c["payload"]["po_type"], "pr": c["payload"].get("pr_no"), "gross": c["gross"],
                  "rc": c["rc"], "err": c["err_cd"], "msg": c["msg"], "data": c["data"]} for c in va["cases"]]
ss = J("screen_state.json")
D["screen"] = {"fetch": ss["fetch_reply_example"],
               "cases": [{"case": c["case"], "user": c["user"], "tok": c["fetch_tok"], "rc": c["rc"], "err": c["err_cd"],
                          "msg": c["msg"], "sps": c["sps"]} for c in ss["cases"]]}

# logs/intent_tool.json — the façade on Kavita's order, and the contract demos
it = J("intent_tool.json")
D["facade"] = [{"label": s["label"], "tool": s["tool"], "args": s["args"], "result": s["result"],
                "svcs": [[c["svc"], c["rc"], len(c["sps"]), c["user"]] for c in s["services"]]} for s in it["steps"]]
D["facadeSummary"] = {k: v for k, v in it["summary"].items() if k != "final_receipt"}
D["receipt"] = it["summary"]["final_receipt"]
D["silent"] = it["silent_draft"]
D["idem"] = it["idempotency"]
D["perm"] = it["permissions"]
D["errors"] = it["errors"]
D["contract"] = J("contract.json")

# logs/mcp_demo.json — servers, the wire, and our harness over MCP
mc = J("mcp_demo.json")
D["mcp"] = {"fastmcp": mc["fastmcp_version"],
            "tools": [{"name": t["name"], "version": (t.get("_meta") or {}).get("version"),
                       "ro": (t.get("annotations") or {}).get("readOnlyHint")} for t in mc["bahi_tools"]],
            "outbox_tools": [t["name"] for t in mc["outbox_tools"]],
            "list_cpo": [t for t in mc["bahi_tools"] if t["name"] == "create_purchase_order"][0],
            "call": [w for w in mc["wire"] if w["method"] == "tools/call"][0],
            "stdio": {"ok": mc["stdio"]["ok"], "command": mc["stdio"].get("command")},
            "http": {"ok": mc["http"]["ok"], "url": mc["http"].get("url")},
            "harness": {k: mc["harness_over_mcp"][k] for k in ("turns", "outbox", "orders", "llm", "model")},
            "harness_trace": [{"tool": t["tool"], "args": t["args"], "result": short(t["result"], 200)}
                              for t in mc["harness_over_mcp"]["trace"]]}

# lectures/L1-the-form/experiments/logs/naive_sweep.json — Lecture 1's naive agent on the six scenarios (default tier)
l1 = json.load(open(HERE.parents[1] / "L1-the-form" / "experiments" / "logs" / "naive_sweep.json"))["summary"]["default"]
D["l1"] = {str(r["id"]): {"p": r["passed"], "tok": r["tokens"], "ne": r["ne"]} for r in l1["per_scenario"]}
D["l1_model"] = l1["model"]

# screen_def/PUR-PO-01.activity.xml (fictional) and bahi/bahi/erp/screens/PUR-PO-01.yaml
xml = (HERE.parent / "screen_def" / "PUR-PO-01.activity.xml").read_text().splitlines()
yml_p = HERE.parents[2] / "bahi" / "bahi" / "erp" / "screens" / "PUR-PO-01.yaml"
yml = yml_p.read_text().splitlines() if yml_p.exists() else []
D["xml"] = {"lines": len(xml), "text": "\n".join(xml)}
D["yaml"] = {"lines": len(yml), "text": "\n".join(yml)}

blob = "/* DATA:BEGIN (generated by experiments/deck_data.py from experiments/logs/*.json; do not edit by hand) */\n" \
       "const D = " + json.dumps(D, ensure_ascii=False, separators=(",", ":"), default=str) + ";\n/* DATA:END */"
src = FIGS.read_text()
src = re.sub(r"/\* DATA:BEGIN.*?/\* DATA:END \*/", lambda m: blob, src, flags=re.S)
FIGS.write_text(src)
print("figs.js data block:", len(blob) // 1024, "KB")
