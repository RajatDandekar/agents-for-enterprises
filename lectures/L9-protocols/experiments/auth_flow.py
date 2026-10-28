"""A remote MCP server behind OAuth 2.1, on the wire, plus three identity demos. No model calls.

    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/auth_flow.py
-> logs/auth_flow.json    every HTTP exchange of Kavita's first sign-in, and a numbered sequence for the deck
-> logs/auth_demos.json   (a) whose token, whose session  (b) the confused deputy  (c) scopes and audience

Secrets never reach a log: Authorization headers are redacted by the recorder; codes, verifiers, challenges,
client secrets and tokens are redacted below before anything is written.
"""
import asyncio
import json
import pathlib
import re
import sys

sys.path.insert(0, "/course/bahi")
import httpx  # noqa: E402

from bahi.course.protocols.auth import READ, WRITE, start_protected_toolbox, sign_in  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
SECRET_KEYS = ("code", "code_verifier", "code_challenge", "state", "client_secret", "access_token", "refresh_token",
               "client_id")


def redact(x):
    if isinstance(x, dict):
        return {k: ("<redacted>" if k in SECRET_KEYS and isinstance(v, str) else redact(v)) for k, v in x.items()}
    if isinstance(x, list):
        return [redact(v) for v in x]
    if isinstance(x, str):
        return re.sub(r"((?:^|[?&])(?:code|code_verifier|code_challenge|state|client_id|client_secret|"
                      r"access_token|refresh_token)=)[^&\s\"]+", r"\1<redacted>", x)
    return x


def rx(e):
    e = json.loads(json.dumps(e, default=str))
    e["path"] = redact(e["path"])
    for k in ("req", "resp"):
        e[k] = redact(e[k])
    e["resp_headers"] = {k: redact(v) for k, v in e["resp_headers"].items()}
    return e


def body(r):
    sc = r.structured_content
    if sc is None:
        try:
            sc = json.loads(r.content[0].text)
        except Exception:  # noqa: BLE001
            sc = r.content[0].text if r.content else None
    return sc


def summary(e):
    p, s = e["path"].split("?")[0], e["status"]
    r = e["req"] if isinstance(e["req"], dict) else {}
    if p == "/mcp":
        m = r.get("method") or ("(reply to server)" if "result" in r else e["method"])
        if s == 401:
            return f"{m} without a token: 401, WWW-Authenticate names the resource metadata"
        return f"{m} with Bearer token: {s}"
    if "oauth-protected-resource" in p:
        return "protected resource metadata: which sign-in server, which scopes (RFC 9728)"
    if "oauth-authorization-server" in p:
        return "sign-in server metadata: endpoints, PKCE S256, registration (RFC 8414)"
    if p == "/register":
        return "dynamic client registration (RFC 7591): client id issued"
    if p == "/authorize":
        return "authorize with PKCE: user signs in, 302 to the redirect with code and iss"
    if p == "/token":
        return "code + verifier exchanged for an access token (sub, scope, audience)"
    return p


def sequence(log):
    out = []
    for i, e in enumerate(sorted(log, key=lambda e: e["at_ms"]), 1):
        frm, to = "client", ("toolbox" if e["tag"] in ("toolbox", "deputy", "reports") else "sign-in")
        if e["path"].startswith("/authorize"):
            frm = "browser"
        out.append({"n": i, "from": frm, "to": to, "method": e["method"], "path": redact(e["path"]).split("?")[0],
                    "status": e["status"], "ms": e["ms"], "summary": summary(e)})
    return out


async def flow():
    w = start_protected_toolbox()
    res = {"urls": {"sign_in": w.issuer, "toolbox": w.toolbox_url}}
    # 0. the bare 401, by hand, so the header is visible
    r = httpx.post(w.toolbox_url, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                   headers={"accept": "application/json, text/event-stream"})
    res["bare_401"] = {"status": r.status_code, "www_authenticate": r.headers.get("www-authenticate"),
                       "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text}
    prm = httpx.get(w.toolbox_url.replace("/mcp", "/.well-known/oauth-protected-resource/mcp"))
    res["protected_resource_metadata"] = prm.json()
    asm = httpx.get(w.issuer + "/.well-known/oauth-authorization-server")
    res["authorization_server_metadata"] = asm.json()
    w.rec_as.log.clear(); w.rec_rs.log.clear()
    # 1. Kavita's first sign-in, driven entirely by the SDK's OAuthClientProvider
    async with sign_in(w, "KJOSHI", [READ, WRITE]) as (c, storage):
        res["protocol_version"] = c.protocol_version
        tl = await c.list_tools()
        res["tools_listed"] = len(tl.tools)
        st = await c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"})
        res["check_stock"] = body(st)
        res["token_scope"] = storage.tokens.scope if storage.tokens else None
        res["client_registered"] = bool(storage.client)
    wire = [rx(e) for e in w.rec_as.log + w.rec_rs.log]
    res["wire"] = sorted(wire, key=lambda e: e["at_ms"])
    res["sequence"] = sequence(wire)
    res["signin_events"] = redact(w.signin.events)
    res["server_saw"] = w.server.seen
    return res


async def demos():
    out = {}
    # (a) whose token, whose session
    w = start_protected_toolbox()
    a = {}
    async with sign_in(w, "KJOSHI", [READ, WRITE]) as (c, _):
        a["kavita_check_stock"] = body(await c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"}))
        a["kavita_raise_pr"] = body(await c.call_tool("create_purchase_request", {
            "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09",
            "confirm": True}))
        pr = a["kavita_raise_pr"].get("request_no")
        a["kavita_approves_own"] = body(await c.call_tool("approve_purchase_request",
                                                          {"request_no": pr, "decision": "approve"}))
    async with sign_in(w, "RMEHTA", [READ, WRITE]) as (c, _):
        a["rohit_inbox"] = body(await c.call_tool("list_my_approvals", {}))
        a["rohit_approves"] = body(await c.call_tool("approve_purchase_request",
                                                     {"request_no": pr, "decision": "approve"}))
    a["bahi_after"] = w.erp.q("SELECT pr_no,status,approved_by FROM pr_hdr WHERE pr_no=?", pr)
    a["server_saw"] = w.server.seen
    out["a_whose_session"] = a

    # (b) the confused deputy: the same Kavita token, sent to a server that acts as SVC_AGENT
    w = start_protected_toolbox()
    b = {"service_account": w.erp.q("SELECT user_id,name,role_cd,appr_limit FROM app_user WHERE user_id='SVC_AGENT'")}
    async with sign_in(w, "KJOSHI", [READ, WRITE]) as (c, _):
        b["kavita_raise_pr"] = body(await c.call_tool("create_purchase_request", {
            "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09",
            "confirm": True}))
        pr = b["kavita_raise_pr"].get("request_no")
        b["fix_right_server_refuses"] = body(await c.call_tool("approve_purchase_request",
                                                               {"request_no": pr, "decision": "approve"}))
    b["status_before_deputy"] = w.erp.q("SELECT pr_no,status,approved_by FROM pr_hdr WHERE pr_no=?", pr)
    async with sign_in(w, "KJOSHI", [READ, WRITE], url=w.deputy_url) as (c, _):
        b["deputy_approves"] = body(await c.call_tool("approve_purchase_request",
                                                      {"request_no": pr, "decision": "approve"}))
    b["status_after_deputy"] = w.erp.q("SELECT pr_no,status,approved_by FROM pr_hdr WHERE pr_no=?", pr)
    b["audit"] = w.erp.q("SELECT user_id,svc FROM audit_trail WHERE svc LIKE 'pr_appr%' OR svc LIKE 'pr_approve%'")
    b["deputy_saw"] = w.deputy.seen
    b["right_server_saw"] = w.server.seen
    out["b_confused_deputy"] = b

    # (c) scopes and audience
    w = start_protected_toolbox()
    cc = {}
    async with sign_in(w, "KJOSHI", [READ]) as (c, st):
        tl = await c.list_tools()
        cc["read_only_token"] = {"scope": st.tokens.scope, "tools_listed": len(tl.tools),
                                 "names": [x.name for x in tl.tools]}
        cc["read_only_write_call"] = body(await c.call_tool("create_purchase_request", {
            "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09",
            "confirm": True}))
        good_token = st.tokens.access_token  # held in memory only, never written
    cc["prs_after_read_only"] = w.erp.q("SELECT pr_no FROM pr_hdr WHERE need_dt='2026-11-09'")
    async with sign_in(w, "KJOSHI", [READ, WRITE]) as (c, st):
        tl = await c.list_tools()
        cc["read_write_token"] = {"scope": st.tokens.scope, "tools_listed": len(tl.tools)}
    async with sign_in(w, "KJOSHI", [READ, WRITE], url=w.reports_url) as (c, st):
        await c.list_tools()
        other = st.tokens.access_token
    probe = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "probe", "version": "1"}}}
    hdr = {"accept": "application/json, text/event-stream", "content-type": "application/json"}
    r1 = httpx.post(w.toolbox_url, json=probe, headers={**hdr, "authorization": f"Bearer {other}"})
    r2 = httpx.post(w.toolbox_url, json=probe, headers={**hdr, "authorization": f"Bearer {good_token}"})
    cc["audience"] = {
        "token_for_reports_sent_to_toolbox": {"status": r1.status_code, "www_authenticate": r1.headers.get("www-authenticate")},
        "token_for_toolbox_sent_to_toolbox": {"status": r2.status_code},
        "token_audiences": [e.get("aud") for e in w.signin.events if e["event"] == "token issued"]}
    cc["server_saw"] = w.server.seen
    out["c_scopes_audience"] = cc
    return out


res = asyncio.run(flow())
dem = asyncio.run(demos())
LOGS.mkdir(exist_ok=True)
(LOGS / "auth_flow.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
(LOGS / "auth_demos.json").write_text(json.dumps(redact(dem), indent=1, ensure_ascii=False, default=str))
print("bare 401:", res["bare_401"])
for s in res["sequence"]:
    print(f"{s['n']:>2} {s['from']:>7} -> {s['to']:<7} {s['method']:<5} {s['path']:<48} {s['status']} {s['summary']}")
print("token scope:", res["token_scope"], "tools:", res["tools_listed"], "server saw:", res["server_saw"])
print(json.dumps(redact(dem), indent=1, default=str)[:6000])
