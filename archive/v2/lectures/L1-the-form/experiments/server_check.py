"""Checks for the Bahi server, the screen files, the HTTP client and the legacy client page.

    modal run tools/modal_run.py --script lectures/L1-the-form/experiments/server_check.py
-> logs/server_check.json (every check with its result)
"""
import json
import pathlib
import subprocess
import sys

from fastapi.testclient import TestClient

from bahi.client import BahiClient
from bahi.erp.engine import SERVICES, ServiceTimeout
from bahi.erp.seed import ROLE_PERMS
from bahi.server import create_app, load_screens, serve

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)
checks = []


def check(name, cond, detail=""):
    checks.append({"check": name, "ok": bool(cond), "detail": str(detail)[:400]})
    print(("PASS " if cond else "FAIL ") + name, "·", str(detail)[:200])


# ---------------------------------------------------------------- the screen files
screens = load_screens()
check("ten screen files load", len(screens) == 10, sorted(screens))
for code, sc in screens.items():
    check(f"{code}: file name matches code", sc["code"] == code)
    names = {f["name"] for f in sc["fields"]}
    for t in sc["tasks"]:
        svc = t.get("service")
        if svc in (None, "login"):
            continue
        check(f"{code}/{t['button']}: service {svc} exists", svc in SERVICES)
        sfields = {f.name for f in SERVICES[svc].fields}
        bad = [k for k in t.get("sends", []) if k not in sfields]
        check(f"{code}/{t['button']}: sends only fields {svc} accepts", not bad, bad)
        miss = [k for k in t.get("sends", []) if k not in names]
        check(f"{code}/{t['button']}: sends only fields on the screen", not miss, miss)
        req = [f.name for f in SERVICES[svc].fields if f.required and f.name not in t.get("sends", [])]
        check(f"{code}/{t['button']}: sends every required field of {svc}", not req, req)
        fills = t.get("fills") or []
        targets = fills.values() if isinstance(fills, dict) else fills
        check(f"{code}/{t['button']}: fills only fields on the screen", all(x in names for x in targets), list(targets))
        buttons = {x["button"] for x in sc["tasks"]}
        check(f"{code}/{t['button']}: needs is a list of buttons on this screen",
              isinstance(t.get("needs", []), list) and all(n in buttons for n in t.get("needs", [])), t.get("needs"))
    for k in ("code", "title", "menu", "roles", "fields", "tasks"):
        check(f"{code}: has {k} (modules/README.md format)", k in sc)
    check(f"{code}: field keys follow the format",
          all(set(f) <= {"name", "label", "type", "req", "help", "readonly", "lookup", "default", "columns", "pick"}
              and f.get("type") in ("str", "int", "float", "date", "grid") for f in sc["fields"]),
          [f for f in sc["fields"] if f.get("type") not in ("str", "int", "float", "date", "grid")])
    for f in sc["fields"]:
        if f.get("lookup"):
            check(f"{code}: lookup {f['lookup']} exists", f["lookup"] in SERVICES)
    # roles: the screen's first write task must be allowed for exactly the roles listed
    writes = [t["service"] for t in sc["tasks"] if t.get("service") in SERVICES and SERVICES[t["service"]].kind == "write"]
    if writes and "ALL" not in sc["roles"]:
        allowed = sorted(r for r, svcs in ROLE_PERMS.items() if writes[0] in svcs or "*" in svcs)
        check(f"{code}: roles match who may call {writes[0]}", sorted(sc["roles"]) == allowed, (sc["roles"], allowed))

# ---------------------------------------------------------------- the server, in process
app = create_app()
c = TestClient(app)
r = c.post("/login", json={"user_id": "KJOSHI", "password": "wrong"})
check("wrong password refused", r.status_code == 401 and r.json()["err_cd"] == "ERR-SEC-0002", r.json())
r = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123", "ou_cd": "RSW-CHK-01"})
check("wrong organisation unit refused", r.status_code == 401 and r.json()["err_cd"] == "ERR-SEC-0007", r.json())
r = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123", "ou_cd": "RSW-PUN-01"})
tok = r.json()["token"]
check("sign in", r.status_code == 200 and r.json()["role_cd"] == "PUR-EXEC", {k: v for k, v in r.json().items() if k != "token"})
h = {"Authorization": f"Bearer {tok}"}
check("GET /screens", len(c.get("/screens").json()) == 10)
check("GET /screens/PUR-PO-01", c.get("/screens/PUR-PO-01").json()["title"] == "PURCHASE ORDER ENTRY")
check("GET /screens/NOPE is 404", c.get("/screens/NOPE").status_code == 404)
check("GET /services lists 38", len(c.get("/services").json()) == 38, len(c.get("/services").json()))
r = c.post("/svc/stk_query", json={"itm_cd": "GSK-SIL-05L"}, headers={**h, "X-Screen": "INV-STK-02", "X-Task": "Query"})
check("service call stk_query", r.json()["data"]["cover_days"] == 9, r.json())
r = c.post("/svc/stk_query", json={"itm_cd": "GSK-SIL-05L"})
check("call without a token is 401", r.status_code == 401)
r = c.post("/svc/pr_approve", json={"pr_no": "PR/2026/00001", "decision": "A"}, headers=h)
check("Kavita may not approve (role)", r.json()["err_cd"] == "ERR-SEC-0001", r.json())
lr = c.get("/live-run?since=0").json()
check("live run records the sign-in under SYS-LGN-01", lr[0]["screen"] == "SYS-LGN-01" and lr[0]["task"] == "Sign in", lr[0])
q = [x for x in lr if x["svc"] == "stk_query"][0]
check("live run records X-Screen and X-Task", q["screen"] == "INV-STK-02" and q["task"] == "Query", q)
r = c.get("/legacy")
check("legacy client page served", r.status_code == 200 and "Bahi ERP 7.2" in r.text and "X-Screen" in r.text, len(r.text))
c.post("/admin/fault", json={"svc": "stk_query", "mode": "timeout_after_commit"})
r = c.post("/svc/stk_query", json={"itm_cd": "GSK-SIL-05L"}, headers=h)
check("fault gives HTTP 504", r.status_code == 504, r.json())
check("tenants are separate", c.post("/login", headers={"X-Tenant": "class-a"},
                                     json={"user_id": "RMEHTA", "password": "rohit@123"}).status_code == 200)

# ---------------------------------------------------------------- a capstone module's screens appear for its tenant
from bahi import ERP  # noqa: E402

cm = TestClient(create_app(lambda: ERP(modules=["hr_leave"])))
codes = sorted(cm.get("/screens").json())
check("module screens served when the module is installed", "HR-LV-02" in codes and "PUR-PO-01" in codes, codes)

# ---------------------------------------------------------------- the naive agent's tools: only installed services
import bahi.modules.hr_leave  # noqa: E402,F401  (registers lv_* services globally)
from bahi.agent.naive import raw_tools  # noqa: E402

names = [t["function"]["name"] for t in raw_tools(ERP())]
check("raw_tools(purchasing ERP) = the 38 purchasing services", len(names) == 38 and not any(n.startswith("lv_") for n in names), len(names))
names2 = [t["function"]["name"] for t in raw_tools(ERP(modules=["hr_leave"]))]
check("raw_tools(ERP with hr_leave) adds lv_* services", len(names2) > 38 and any(n.startswith("lv_") for n in names2), len(names2))

# ---------------------------------------------------------------- BahiClient over TestClient and over real HTTP
k = BahiClient("", "KJOSHI", "kavita@123", http=TestClient(create_app()))
d = k.call("pr_fetch", screen="PUR-PR-01", task="Fetch", itm_cd="GSK-SIL-05L")
check("BahiClient (TestClient) pr_fetch", d["data"]["cc_cd"] == "PRD-05" and d["data"]["est_rate"] == 11.4, d)
url = serve(port=8091)
k2 = BahiClient(url, "KJOSHI", "kavita@123")
d = k2.call("itm_search", q="gasket 5")
check("BahiClient over real HTTP", d["rc"] == "S" and d["data"]["rows"][0]["itm_cd"].startswith("GSK"), d["msg"])
import httpx  # noqa: E402

httpx.post(url + "/admin/fault", json={"svc": "po_hist", "mode": "timeout_after_commit"})
try:
    k2.call("po_hist", itm_cd="GSK-SIL-05L")
    check("BahiClient raises ServiceTimeout on 504", False)
except ServiceTimeout as e:
    check("BahiClient raises ServiceTimeout on 504", True, e)
check("BahiClient.live_run", len(k2.live_run()) >= 3, len(k2.live_run()))
p = subprocess.run([sys.executable, "-m", "bahi.server", "--help"], capture_output=True, text=True)
check("python -m bahi.server --help", p.returncode == 0 and "--port" in p.stdout, p.stdout[:120])

ok = all(x["ok"] for x in checks)
(OUT / "server_check.json").write_text(json.dumps({"ok": ok, "n": len(checks), "checks": checks}, indent=1))
print(f"\n{sum(x['ok'] for x in checks)}/{len(checks)} checks pass")
sys.exit(0 if ok else 1)
