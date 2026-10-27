"""Kavita's whole order through the app's HTTP API, the way the browser pages drive it. Used by the Lecture 5 test
(lectures/L5-the-signature/experiments/app_journey.py), by NB5, and by Lecture 8's final demo.

    from fastapi.testclient import TestClient
    from bahi.app.main import create_app
    from bahi.app.journey import run_journey
    with TestClient(create_app()) as c:
        j = run_journey(c)          # j["checks"] all True; j["transcript"], j["trace"], j["audit"]

Kavita's side is adaptive but deterministic: each of her answers is chosen by code from what the agent just asked.
"""
from __future__ import annotations

import re

OPENING = ("We need 20,000 silicone gaskets for the 5-litre cooker before the Diwali run. "
           "Same supplier as last time.")


def kavita_answer(reply: str) -> str:
    """Kavita answers the agent's last question (the last line with a question mark)."""
    qs = [ln for ln in reply.splitlines() if "?" in ln]
    q = (qs[-1] if qs else reply).lower()
    if "go ahead" in q or "shall i" in q or "confirm" in q:
        return "Yes, go ahead."
    if "cost centre" in q:
        return "PRD-07, the Diwali production run. Need-by 2 November."
    if "need" in q or "date" in q:
        return "2 November."
    if "supplier" in q:
        return "Deccan Polymers, DP-RJK-0042."
    return "Yes, go ahead."


def run_journey(c, max_turns: int = 7) -> dict:
    """c: a TestClient (or anything with .post/.get like httpx.Client on the app's base URL)."""
    out = {"steps": [], "checks": {}}

    def step(who, what, body=None, resp=None):
        out["steps"].append({"who": who, "what": what, **({"body": body} if body is not None else {}),
                             **({"response": resp} if resp is not None else {})})

    # 1. Kavita signs in to the app. Her token is the only identity the agent will ever act with.
    k = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123"}).json()
    K = {"Authorization": f"Bearer {k['token']}"}
    step("KJOSHI", "sign in", resp={"user_id": k["user_id"], "role_cd": k["role_cd"]})
    me = c.get("/api/me", headers=K).json()
    conv = c.post("/api/chat", headers=K).json()
    step("KJOSHI", "new conversation", resp=conv)
    cid = conv["conv"]

    # 2. The conversation, until the order waits on Rohit
    text = OPENING
    for _ in range(max_turns):
        r = c.post(f"/api/chat/{cid}/message", headers=K, json={"text": text}).json()
        step("KJOSHI", "message", body={"text": text}, resp={"reply": r["reply"], "waiting_on": r["waiting_on"],
                                                             "trace": [t["line"] for t in r["trace"]]})
        if r["waiting_on"] and r["waiting_on"]["status"] == "PENDING":
            break
        text = kavita_answer(r["reply"])

    # 3. Unauthorised attempts are refused by the app (and would be by Bahi)
    out["checks"]["no_token_refused"] = c.get("/api/inbox").status_code == 401
    waiting = r["waiting_on"] or {}
    if waiting:
        kd = c.post(f"/api/inbox/{waiting['id']}", headers=K, json={"decision": "approve"})
        out["checks"]["kavita_cannot_approve"] = kd.status_code == 403
        step("KJOSHI", "tries to approve her own request", resp={"status": kd.status_code, "detail": kd.json().get("detail")})

    # 4. Rohit, on his own phone: his own sign-in, his inbox, one tap
    rr = c.post("/login", json={"user_id": "RMEHTA", "password": "rohit@123"}).json()
    R = {"Authorization": f"Bearer {rr['token']}"}
    slack = c.get("/api/outbox", headers=R, params={"channel": "@rohit"}).json()
    inbox = c.get("/api/inbox", headers=R).json()["items"]
    step("RMEHTA", "opens the inbox", resp={"items": [{k_: i.get(k_) for k_ in ("id", "kind", "doc_no", "summary", "value",
                                                                               "rule")} for i in inbox],
                                             "slack": [m["text"] for m in slack["messages"]]})
    mine = [i for i in inbox if i.get("conv") == cid]
    d = c.post(f"/api/inbox/{mine[-1]['id']}", headers=R, json={"decision": "approve", "comment": "ok, Diwali run"}).json()
    step("RMEHTA", "one tap: approve", body={"item": mine[-1]["id"]},
         resp={"bahi": d["result"]["bahi"], "item_status": d["result"]["item"]["status"],
               "kavita_sees": (d.get("conversation") or {}).get("reply")})

    # 5. What Kavita's chat now shows, and the proof
    st = c.get(f"/api/chat/{cid}", headers=K).json()
    au = c.get("/api/audit", headers=K, params={"conv": cid}).json()
    erp = c.app.state.l5.erp if hasattr(c, "app") else None
    po = None
    m = re.search(r"PO/\d{4}/\d{5}", (d.get("conversation") or {}).get("reply") or "")
    if m:
        po = c.post("/svc/po_get", headers=K, json={"po_no": m.group(0)}).json()["data"]
    out.update(conv=cid, me=me, transcript=st["transcript"], trace=st["trace"], audit=au["entries"],
               audit_summary=au["summary"], bahi_rows=au["bahi_rows"], outbox=c.get("/api/outbox", headers=K).json(),
               final_po=po, acts_as=st["acts_as"], llm=st.get("llm"))
    users = {x["user_id"] for x in au["bahi_rows"]}
    writes = [e for e in au["entries"] if e["kind"] == "tool" and e.get("writes")]
    out["checks"].update(
        released=bool(po) and po["status"] == "RL",
        po_is_01182=bool(po) and po["po_no"] == "PO/2026/01182",
        approved_by_rohit=bool(po) and po["approved_by"] == "RMEHTA",
        created_by_kavita=bool(po) and po["created_by"] == "KJOSHI",
        gross_280840=bool(po) and abs(po["gross_value"] - 280840) < 0.01,
        no_service_account_in_bahi="SVC_AGENT" not in users,
        every_write_read_back=all(e.get("read_back") for e in writes) and bool(writes),
        rohit_got_slack=any(mi.get("channel") == "@rohit" for mi in out["outbox"]["messages"]),
        approval_in_audit=any(e["kind"] == "approval" and e["actor"] == "RMEHTA" for e in au["entries"]),
    )
    if erp is not None:
        out["checks"]["one_gasket_order"] = len([o for o in erp.orders(itm_cd="GSK-SIL-05L")
                                                 if o["created_on"] >= "2026-10-26"]) == 1
    out["ok"] = all(out["checks"].values())
    return out
