"""In-process API test of Hephaestus (FastAPI TestClient, no modal.Dict), with the live model.

    /Users/raj/.venv/bin/modal run deploy/hephaestus_modal.py::test            # everything, live gemini-3.8-flash
    /Users/raj/.venv/bin/modal run deploy/hephaestus_modal.py::test --quick    # no six-question run, no attack comparison
"""
import json
import os
import sys
import time

sys.path.insert(0, "/app/ledgerline")
from fastapi.testclient import TestClient  # noqa: E402

from ledgerline.hephaestus.app import Store, create_app  # noqa: E402

QUICK = os.environ.get("HEPH_QUICK") == "1"
app = create_app(Store(None))
c = TestClient(app)
fails, n = [], 0


def ok(cond, what, extra=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + what + (f"  [{extra}]" if extra else ""))
    if not cond:
        fails.append(what)


def poll(jid, h, limit=600):
    t0 = time.time()
    while time.time() - t0 < limit:
        j = c.get(f"/api/job/{jid}", headers=h).json()
        if j["state"] != "running":
            return j
        time.sleep(1.5)
    return j


r = c.post("/api/join", json={"name": "Test Student"})
ok(r.status_code == 200, "join")
me = r.json()
key = me["key"]
h = {"X-Forge-Key": key}
ok(len(key) > 20 and me["mcp_url"].endswith(key), "secret key and MCP address")
ok([d["name"] for d in me["definitions"]] == ["find_item", "check_stock", "find_supplier", "supplier_certificates",
                                               "check_budget", "create_purchase_request", "approve_purchase_request"],
   "seven starter tools listed")
ok(c.get("/api/me").status_code == 401, "no key, no forge")
ok(c.get("/api/catalog").status_code == 200, "catalogue")

# MCP over HTTP, the same app
mh = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
r = c.post(f"/mcp/{key}", headers=mh, json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "claude-ai", "version": "0.1"}}})
ok(r.status_code == 200 and r.json()["result"]["protocolVersion"] == "2025-06-18" and r.headers.get("mcp-session-id"),
   "MCP initialize")
sid = r.headers.get("mcp-session-id")
mh2 = {**mh, "Mcp-Session-Id": sid}
ok(c.post(f"/mcp/{key}", headers=mh2, json={"jsonrpc": "2.0", "method": "notifications/initialized"}).status_code == 202,
   "MCP notification -> 202")
r = c.post(f"/mcp/{key}", headers=mh2, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
ok(len(r.json()["result"]["tools"]) == 7, "MCP tools/list: 7")
r = c.post(f"/mcp/{key}", headers=mh2, json={"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                             "params": {"name": "check_stock", "arguments": {"item_code": "BAT-500"}}})
res = r.json()["result"]
ok(res["isError"] is False and res["structuredContent"]["free_total"] == 6600, "MCP tools/call check_stock")
ok(c.post("/mcp/hx-nope", headers=mh, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).status_code == 404,
   "unknown key -> 404")
ok(c.get(f"/mcp/{key}").status_code == 405, "GET -> 405")
ok(c.get("/.well-known/oauth-protected-resource").status_code == 404, "no OAuth metadata")
calls = c.get("/api/calls", headers=h).json()
ok(calls["connected"] and calls["connected"]["client"] == "claude-ai", "connected to Claude (client name)", str(calls["connected"]))

# a knob change shows in tools/list
cfg = me["config"]
cfg["tools"]["check_stock"]["name"] = "legacy"
cfg["tools"]["check_stock"]["description"] = "vague"
cfg["tools"]["check_stock"]["output"] = "minimal"
r = c.post("/api/config", headers=h, json={"config": cfg})
ok(r.status_code == 200 and r.json()["new_notes"], "config + release note")
r = c.post(f"/mcp/{key}", headers=mh2, json={"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
t = {x["name"]: x for x in r.json()["result"]["tools"]}
ok("stk_qry" in t and t["stk_qry"]["description"] == "Gets item data." and "-forge." in t["stk_qry"]["_meta"]["ledgerline/version"],
   "knob change visible in tools/list")
r = c.post("/api/tool/try", headers=h, json={"tool": "check_stock", "args": {"item_code": "BAT-500"}})
ok(json.loads(r.json()["text"]) == {"ok": True, "item_code": "BAT-500", "free_total": 6600}, "minimal output trims", r.json()["text"][:120])
cfg["tools"]["check_stock"].update({"name": "clear", "description": "precise", "output": "all"})
c.post("/api/config", headers=h, json={"config": cfg})

# Ask
r = c.post("/api/ask", headers=h, json={"text": "How many BAT-500 battery packs do we have in Manchester?"})
ok(r.status_code == 200 and "5,400" in r.json()["reply"].replace("5400", "5,400"), "ask q1", r.text[:300])
if r.status_code == 200:
    ok(r.json()["cards"] and r.json()["model_steps"], "trace has tool cards and model steps")

# production checks without the model
for cid in ("schema", "reliability", "latency", "payload", "idempotency", "timeouts", "permissions", "audit", "change"):
    r = c.post(f"/api/prod/{cid}", headers=h)
    j = poll(r.json()["id"], h)
    ch = (j.get("result") or {}).get("checks", [{}])[0]
    ok(j["state"] == "done", f"prod {cid}: {ch.get('pass')} · {ch.get('headline', j.get('error'))}")

# SVC identity fails permissions
cfg["identity"] = "SVC_AGENT"
c.post("/api/config", headers=h, json={"config": cfg})
j = poll(c.post("/api/prod/permissions", headers=h).json()["id"], h)
ok(j["result"]["checks"][0]["pass"] is False, "service account fails permissions", j["result"]["checks"][0]["headline"])
cfg["identity"] = "ECLARKE"
c.post("/api/config", headers=h, json={"config": cfg})

if not QUICK:
    r = c.post("/api/six", headers=h)
    j = poll(r.json()["id"], h, 900)
    ok(j["state"] == "done", "six questions", j.get("error") or "")
    if j["state"] == "done":
        for row in j["result"]["rows"]:
            print(f"   q{row['n']} {'RIGHT' if row['right'] else 'WRONG'} {row['why']} | tools {row['tools']} | "
                  f"{row['model_calls']} calls, {row['tokens_in']} tokens in, {row['seconds']} s")
        print("   totals", j["result"]["totals"])
    j = poll(c.post("/api/shield/run", headers=h).json()["id"], h, 600)
    ok(j["state"] == "done", "attacks", j.get("error") or "")
    if j["state"] == "done":
        for a in j["result"]["rows"]:
            print(f"   {a['id']:10} {'HELD' if a['held'] else 'BROKE'} {a['what']} (stopped by {a['stopped_by']})")
    j = poll(c.post("/api/prod/usability", headers=h).json()["id"], h, 300)
    ok(j["state"] == "done", "usability", (j.get("result") or {}).get("checks", [{}])[0].get("headline", j.get("error")))

w = c.get("/api/wall").json()
ok(w["agg"]["forges"] == 1, "wall")
print(f"\n{n - len(fails)} of {n} passed" + (f"; FAILED: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
