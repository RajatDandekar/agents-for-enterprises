"""Lecture 1 v3: Bahi's services as black boxes. An input goes in, the legacy envelope comes out.

Calls a few services over HTTP exactly as the legacy client does (POST /svc/<name>, Bearer token), and records the
real request and reply for the plates: a read (stk_query), a refused write (po_save with Fetch's default tax code),
a write that "succeeds" into a Draft (po_save on the closed PRD-05), and the catalogue size.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L1-before-and-after/experiments/services_blackbox.py
-> logs/services_blackbox.json
"""
import json
import pathlib

from fastapi.testclient import TestClient

from bahi.server import create_app

OUT = pathlib.Path(__file__).parent / "logs"
http = TestClient(create_app())
tok = http.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123", "ou_cd": "RSW-PUN-01"}).json()["token"]
rohit = http.post("/login", json={"user_id": "RMEHTA", "password": "rohit@123", "ou_cd": "RSW-PUN-01"}).json()["token"]
calls = []


def svc(name, body, t=tok, screen=None, task=None):
    h = {"Authorization": f"Bearer {t}"}
    if screen:
        h.update({"X-Screen": screen, "X-Task": task})
    env = http.post(f"/svc/{name}", json=body, headers=h).json()
    calls.append({"service": name, "request": body, "reply": env})
    print(name, json.dumps(body), "->", json.dumps(env, default=str)[:300])
    return env


svc("stk_query", {"itm_cd": "GSK-SIL-05L", "whs_cd": "WH-PUN-STR"}, screen="INV-STK-02", task="Query")
svc("itm_search", {"q": "gasket 5"}, screen="INV-ITM-03", task="Search")
pr = svc("pr_save", {"pr_type": "STD", "cc_cd": "PRD-05", "need_dt": "09-11-2026", "itm_cd": "GSK-SIL-05L", "qty": "20000",
                     "whs_cd": "WH-PUN-STR", "est_rate": "11.4", "remarks": "Diwali run"}, screen="PUR-PR-01", task="Save")
pr_no = pr["data"]["pr_no"]
svc("pr_submit", {"pr_no": pr_no}, screen="PUR-PR-01", task="Submit")
svc("pr_approve", {"pr_no": pr_no, "decision": "A", "comment": "ok"}, t=rohit, screen="PUR-PR-04", task="Confirm")
f = svc("po_fetch", {"sup_cd": "DP-RJK-0042", "itm_cd": "GSK-SIL-05L", "pr_no": pr_no}, screen="PUR-PO-01", task="Fetch")["data"]
body = {"po_type": "STD", "pr_no": pr_no, "sup_cd": "DP-RJK-0042", "itm_cd": "GSK-SIL-05L", "qty": str(f["qty"]),
        "rate": str(f["rate"]), "tax_cd": f["tax_cd"], "cc_cd": f["cc_cd"], "need_dt": f["need_dt"], "whs_cd": f["whs_cd"],
        "fetch_tok": f["fetch_tok"]}
svc("po_save", body, screen="PUR-PO-01", task="Save")
svc("po_save", {**body, "tax_cd": "GST18-INTER"}, screen="PUR-PO-01", task="Save")
catalogue = http.get("/services").json()
res = {"what": "Real requests and replies of Bahi services, as the legacy client sends them", "calls": calls,
       "services_in_catalogue": len(catalogue),
       "catalogue_sample": [{k: s[k] for k in ("name", "doc", "kind")} for s in catalogue[:40]]}
(OUT / "services_blackbox.json").write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
print("services:", len(catalogue))
