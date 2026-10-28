"""Copy the measured numbers the Lecture 5 deck shows from experiments/logs/*.json into ../figdata.js.
Standard library only. Every key in figdata.js names the log it came from. Nothing on a plate is typed by hand."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
L = HERE / "logs"
T = ("small", "default", "large")
J = lambda n: json.loads((L / n).read_text())  # noqa: E731
D = {}

# ---- opens: the naive agent on scenarios 2 and 5 (logs/opens_naive.json)
op = J("opens_naive.json")["results"]
D["opens"] = [{"tier": r["tier"], "s": r["scenario"], "passed": r["passed"], "ne": r["never_events"],
               "writes": [w for t in r["turns"] for w in t["writes"]],
               "orders": [{k: o[k] for k in ("po_no", "status", "cc_cd", "approved_by", "gross_value")} for o in r["orders"]],
               "requests": r["requests"], "last": (r["turns"][-1]["agent"] or "")[:260] if r["turns"] else "",
               "tokens": r["tokens_in"] + r["tokens_out"], "inr": r["cost_inr"]} for r in op]

# ---- scopes and the matrix (logs/scopes.json, logs/matrix.json)
sc = J("scopes.json")["scopes"]
D["scopes"] = {u: {"role": s["role"], "limit": s["limit"], "services": s["services"], "writes": s["write_services"],
                   "menu": [[m["menu"], m["allowed"], m["screen"]] for m in s["menu"]],
                   "tools": [[t["tool"], t["allowed"], t["writes"]] for t in s["tools"]]} for u, s in sc.items()}
m = J("matrix.json")
D["matrix"] = {"roles": list(m["matrix"].values()), "rules": m["rules"], "agree": m["agree"], "n": m["n"],
               "kavita": m["kavita_280840"], "svc": m["svc_280840"], "preview": m["preview_by_identity"],
               "grid": [r for r in m["grid"] if r["requester"] == "KJOSHI"]}

# ---- experiment (b): identity (logs/identity_graph.json, logs/identity_loop.json)
idr = []
for ag in ("graph", "loop"):
    for r in J(f"identity_{ag}.json")["results"]:
        f = r["final"] or {}
        idr.append({"agent": ag, "id": r["identity"], "tier": r["tier"], "w": r["wording"], "ne1": r["ne1"],
                    "routed": r["routed_to_rohit"], "status": f.get("status"), "by": f.get("approved_by"),
                    "users": r["bahi_users"]})
D["identity"] = idr

# ---- experiment (a): read-back (logs/readback_<tier>.json)
rb = {t: J(f"readback_{t}.json") for t in T}
D["readback"] = {t: rb[t]["summary"] for t in T}
ex = {}
for t in T:
    for r in rb[t]["results"]:
        key = f"{r['arm']}_{t}"
        if key not in ex and r["wording"] == 1:
            i = next((k for k, x in enumerate(r["turns"]) if "po_save" in x["services"]), 0)
            ex[key] = {"reply": (r["turns"][i]["agent"] or "")[:300], "outcome": r["outcome"],
                       "after_save": r["turns"][i]["services"][r["turns"][i]["services"].index("po_save"):][:6]
                       if "po_save" in r["turns"][i]["services"] else []}
D["readback_examples"] = ex
D["readback_wordings"] = rb["default"]["wordings"]

# ---- experiment (c): adversarial (logs/adversarial_<arm>_<tier>.json)
arms = ["naive", "naive_guard_v1", "naive_guard", "loop_guard", "graph"]
adv = {}
for a in arms:
    for t in T:
        d = J(f"adversarial_{a}_{t}.json")
        adv[f"{a}_{t}"] = [{"attack": r["attack"], "target": r["target"], "ne": r["never_events"],
                            "refused": [x["refused"] for x in r["guard_refusals"]],
                            "why": [x["error"][:220] for x in r["guard_refusals"]][:3],
                            "orders": [[o["po_no"], o["status"], o["approved_by"], o["gross_value"]] for o in r["orders"]],
                            "last": (r["turns"][-1]["agent"] or "")[:240] if r["turns"] else ""} for r in d["results"]]
D["adversarial"] = adv
D["attacks"] = J("adversarial_naive_default.json")["attacks"]
hole = {}
for t in ("small", "large"):
    r = next(x for x in J(f"adversarial_naive_guard_v1_{t}.json")["results"] if x["attack"] == "split")
    hole[t] = {"services": [s_ for x in r["turns"] for s_ in x["services"] if s_ in ("po_save", "po_amend", "po_release",
                                                                                       "pr_save", "pr_submit", "po_cancel")],
               "refused": [x["refused"] for x in r["guard_refusals"]], "ne": r["never_events"],
               "orders": [[o["po_no"], o["status"], o["approved_by"], o["qty"], o["gross_value"]] for o in r["orders"]]}
    r2 = next(x for x in J(f"adversarial_naive_guard_{t}.json")["results"] if x["attack"] == "split")
    hole[t + "_v2"] = {"refused": [x["refused"] for x in r2["guard_refusals"]], "ne": r2["never_events"],
                       "why": [x["error"][:200] for x in r2["guard_refusals"]],
                       "orders": [[o["po_no"], o["status"], o["approved_by"], o["qty"], o["gross_value"]] for o in r2["orders"]]}
D["hole"] = hole

# ---- experiment (d): six scenarios at this layer (logs/six_l5_<tier>.json)
D["six"] = {t: [{"s": r["scenario"], "name": r["name"], "passed": r["passed"], "ne": r["never_events"],
                 "tokens": r["tokens_in"] + r["tokens_out"], "inr": r["cost_inr"], "audit": r["audit"],
                 "refusals": len(r["guard_refusals"])} for r in J(f"six_l5_{t}.json")["results"]] for t in T}

# ---- §3.4 onboarding (logs/onboarding_default.json)
ob = J("onboarding_default.json")
D["onboarding"] = {"steps": ob["steps"], "orders": ob["orders"], "suppliers": ob["suppliers"], "summary": ob["summary"],
                   "outbox": [x["channel"] + " · " + x["text"] for x in ob["outbox"]]}

# ---- the app journey (logs/journey.json)
j = J("journey.json")
D["journey"] = {"transcript": j["transcript"], "trace": j["trace"], "checks": j["checks"], "summary": j["audit_summary"],
                "audit": [{"seq": e["seq"], "kind": e["kind"], "actor": e["actor"], "tool": e.get("tool", ""),
                           "what": (e.get("saw") or e.get("what") or e.get("text") or "")[:150],
                           "rb": (e.get("read_back") or {}).get("status_code", ""),
                           "bahi": [[b["user"], b["svc"], b["rc"]] for b in e.get("bahi", [])]} for e in j["audit"]],
                "slack": [x["channel"] + " · " + x["text"] for x in j["outbox"]["messages"]],
                "final": {k: j["final_po"][k] for k in ("po_no", "status", "approved_by", "created_by", "gross_value")},
                "bahi_users": sorted({x["user_id"] for x in j["bahi_rows"]}), "bahi_rows": len(j["bahi_rows"]),
                "durable": j.get("durable"), "steps": [{"who": s["who"], "what": s["what"]} for s in j["steps"]]}

out = HERE.parent / "figdata.js"
out.write_text("/* Generated by experiments/deck_data.py from experiments/logs/*.json. Do not edit by hand.\n"
               "   opens <- opens_naive.json · scopes <- scopes.json · matrix <- matrix.json · identity <- identity_{graph,loop}.json\n"
               "   readback <- readback_{small,default,large}.json · adversarial <- adversarial_<arm>_<tier>.json\n"
               "   six <- six_l5_<tier>.json · onboarding <- onboarding_default.json · journey <- journey.json */\n"
               "window.L5 = " + json.dumps(D, ensure_ascii=False, default=str) + ";\n")
print(out, out.stat().st_size)
