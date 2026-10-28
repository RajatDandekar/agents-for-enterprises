"""MCP in depth, on the wire: the official SDK (mcp 2.3.0) server for Rasoi, both protocol eras.

    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/mcp_sdk_wire.py
-> logs/mcp_sdk_wire.json

1. In-process: tools, resources, resource template, prompts, and a write that asks Kavita to confirm (elicitation).
2. Streamable HTTP, 2026-07-28 (stateless): every request recorded by an ASGI recorder.
3. Streamable HTTP, legacy handshake (mode="legacy", 2025-11-25): the same calls, for comparison with L4.
4. A tampered requestState sent by hand: the server must refuse it.
"""
import asyncio
import json
import pathlib
import sys
import time

sys.path.insert(0, "/course/bahi")
import mcp  # noqa: E402
import mcp_types as t  # noqa: E402
from mcp import Client  # noqa: E402

from bahi.course.protocols.rasoi_mcp import build_rasoi_server  # noqa: E402
from bahi.course.protocols.wire import Recorder, serve  # noqa: E402
from bahi.erp.engine import ERP  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
OUT = {"versions": {"mcp": getattr(mcp, "__version__", None)}}
try:
    from importlib.metadata import version
    OUT["versions"] = {p: version(p) for p in ("mcp", "mcp-types", "fastmcp", "uvicorn", "starlette")}
except Exception as e:  # noqa: BLE001
    OUT["versions_err"] = str(e)
print(OUT["versions"])


def dump(x):
    if hasattr(x, "model_dump"):
        return x.model_dump(mode="json", by_alias=True, exclude_none=True)
    return x


def make_answer(decision, seen):
    async def answer(context, params):
        seen.append(dump(params))
        if decision == "accept":
            return t.ElicitResult(action="accept", content={"confirm": True})
        return t.ElicitResult(action="decline")
    return answer


PR_ARGS = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09",
           "confirm": True}


async def session(target, label, decision="accept", mode=None):
    seen = []
    kw = {"elicitation_callback": make_answer(decision, seen)}
    if mode:
        kw["mode"] = mode
    res = {"label": label, "steps": []}

    def step(name, t0, out):
        res["steps"].append({"step": name, "ms": round((time.perf_counter() - t0) * 1000, 1), "out": out})

    async with Client(target, **kw) as c:
        res["protocol_version"] = c.protocol_version
        res["server_info"] = dump(c.server_info)
        res["server_capabilities"] = dump(c.server_capabilities)
        t0 = time.perf_counter(); r = await c.list_tools()
        step("tools/list", t0, {"n": len(r.tools), "names": [x.name for x in r.tools],
                                "read_only": [x.name for x in r.tools if x.annotations and x.annotations.read_only_hint],
                                "ttl_ms": getattr(r, "ttl_ms", None), "first": dump(r.tools[1])})
        t0 = time.perf_counter(); r = await c.list_resources()
        step("resources/list", t0, [dump(x) for x in r.resources])
        t0 = time.perf_counter(); r = await c.list_resource_templates()
        step("resources/templates/list", t0, [dump(x) for x in r.resource_templates])
        t0 = time.perf_counter(); r = await c.read_resource("rasoi://policy/purchase")
        txt = r.contents[0].text
        step("resources/read policy", t0, {"chars": len(txt), "head": txt[:400],
                                           "s6": txt[txt.find("## 6"):txt.find("## 7")][:900]})
        t0 = time.perf_counter(); r = await c.read_resource("rasoi://stock/GSK-SIL-05L")
        step("resources/read stock", t0, json.loads(r.contents[0].text))
        t0 = time.perf_counter(); r = await c.list_prompts()
        step("prompts/list", t0, [dump(x) for x in r.prompts])
        t0 = time.perf_counter()
        r = await c.get_prompt("raise_a_pr", {"item": "5-litre silicone gasket", "quantity": "20000", "need_by": "2026-11-09"})
        step("prompts/get raise_a_pr", t0, {"messages": [
            {"role": m.role, "type": m.content.type,
             "text": (m.content.text if m.content.type == "text" else f"[embedded resource {m.content.resource.uri}, "
                      f"{len(m.content.resource.text)} chars]")} for m in r.messages]})
        t0 = time.perf_counter(); r = await c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"})
        step("tools/call check_stock", t0, dump(r))
        t0 = time.perf_counter(); r = await c.call_tool("create_purchase_request", PR_ARGS)
        step(f"tools/call create_purchase_request ({decision})", t0, dump(r))
    res["elicitations_seen_by_client"] = seen
    return res


async def main():
    # 1. in-process, modern protocol by default
    erp = ERP()
    srv = build_rasoi_server(erp, "KJOSHI")
    OUT["inproc_accept"] = await session(srv, "in-process, Kavita accepts", "accept")
    erp2 = ERP()
    OUT["inproc_decline"] = await session(build_rasoi_server(erp2, "KJOSHI"), "in-process, Kavita declines", "decline")
    OUT["inproc_decline"]["prs_after"] = erp2.q("SELECT pr_no,status FROM pr_hdr WHERE raised_by='KJOSHI' AND need_dt='2026-11-09'")
    OUT["inproc_accept"]["prs_after"] = erp.q("SELECT pr_no,status FROM pr_hdr WHERE raised_by='KJOSHI' AND need_dt='2026-11-09'")

    # 2 + 3. streamable HTTP, recorded, both eras
    for label, mode, port in [("http_modern", None, 8931), ("http_legacy", "legacy", 8932)]:
        rec = Recorder()
        s = build_rasoi_server(ERP(), "KJOSHI")
        base = serve(rec.wrap(s.streamable_http_app()), port=port)
        OUT[label] = await session(base + "/mcp", f"streamable HTTP, {label}", "accept", mode=mode)
        OUT[label]["wire"] = rec.log
        OUT[label]["rpc"] = rec.rpc_calls()
        OUT[label]["http_requests"] = len(rec.log)
        print(label, OUT[label]["protocol_version"], len(rec.log), "requests:", rec.rpc_calls())

    # 4. tamper: replay the retry of create_purchase_request with a changed quantity but the old signed state
    import httpx
    wire = OUT["http_modern"]["wire"]
    retry = next(e for e in wire if isinstance(e["req"], dict) and e["req"].get("method") == "tools/call"
                 and (e["req"].get("params") or {}).get("requestState"))
    body = json.loads(json.dumps(retry["req"]))
    body["id"] = 991
    body["params"]["arguments"]["quantity"] = 200000
    hdr = {k: v for k, v in retry["req_headers"].items() if k in ("content-type", "accept", "mcp-method", "mcp-name",
                                                                  "mcp-protocol-version")}
    rec = Recorder()
    s = build_rasoi_server(ERP(), "KJOSHI")
    base = serve(rec.wrap(s.streamable_http_app()), port=8933)
    r = httpx.post(base + "/mcp", json=body, headers=hdr, timeout=30)
    OUT["tamper"] = {"sent": body, "headers": hdr, "status": r.status_code, "reply": rec.log[-1]["resp"] if rec.log else r.text}
    body2 = json.loads(json.dumps(retry["req"])); body2["id"] = 992
    body2["params"]["requestState"] = body2["params"]["requestState"][:-4] + "0000"
    r2 = httpx.post(base + "/mcp", json=body2, headers=hdr, timeout=30)
    OUT["tamper_mac"] = {"status": r2.status_code, "reply": rec.log[-1]["resp"] if rec.log else r2.text}
    print("tamper:", OUT["tamper"]["status"], str(OUT["tamper"]["reply"])[:300])
    print("tamper mac:", OUT["tamper_mac"]["status"], str(OUT["tamper_mac"]["reply"])[:300])


asyncio.run(main())
LOGS.mkdir(exist_ok=True)
(LOGS / "mcp_sdk_wire.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False, default=str))
for k in ("inproc_accept", "inproc_decline"):
    v = OUT[k]
    print(k, v["protocol_version"], [(s["step"], s["ms"]) for s in v["steps"]])
    print("  last:", json.dumps(v["steps"][-1]["out"], default=str)[:600])
    print("  seen:", json.dumps(v["elicitations_seen_by_client"], default=str)[:400], v.get("prs_after"))
