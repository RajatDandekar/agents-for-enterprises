"""Lecture 4, sections 3 and the film "tool": the anatomy of check_stock, from one real call.

    python lectures/L4-the-hands/experiments/anatomy.py          (light, local; no model call)

1 the files        toolbox/check_stock/tool.json and tool.py, verbatim
2 the services     itm_get, whs_list, stk_query: their definitions from erp/services.py (name, legacy title, fields,
                   kind, screen) and their source
3 one real call    the model's request (taken from the recorded run of our harness, logs/our_harness.json, when it
                   exists), then every legacy service request and reply in the {rc, err_cd, msg, data} envelope, then
                   the tool's clean result, and the same call as MCP JSON-RPC
4 the error path   a bad item code (BAT-5000): the legacy ERR-ITM-0010 reply and the structured error the model gets
Writes logs/anatomy_check_stock.json.
"""
import inspect
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))

from ledgerline.erp import services  # noqa: E402,F401  (registers the services)
from ledgerline.erp.engine import ERP, SERVICES  # noqa: E402
from ledgerline.toolbox import REGISTRY, Toolbox  # noqa: E402

TOOL = "check_stock"
spec = REGISTRY[TOOL]
out = {"tool": TOOL, "files": {"tool.json": (spec.folder / "tool.json").read_text(), "tool.py": spec.source,
                               "path": str(spec.folder.relative_to(ROOT))}}

# 2 the services inside it, as Ledgerline defines them
out["services"] = []
for name in spec.spec["services"]:
    sv = SERVICES[name]
    out["services"].append({"name": name, "legacy_title": sv.doc, "kind": sv.kind, "screen": sv.screen,
                            "fields": [{"name": f.name, "type": f.type, "required": f.required, "desc": f.desc} for f in sv.fields],
                            "source": inspect.getsource(sv.fn), "defined_in": "ledgerline/ledgerline/erp/services.py"})
out["services_found_in"] = ("ledgerline/ledgerline/erp/services.py (the 38 purchasing services). The northbridge-docs repo's "
                            "04_service_definitions folder must match it exactly (L3 STORY_V4); it was not generated on this "
                            "machine on 3 Nov 2026, so the definitions here are read from the code.")

# 3 one real call: the model's request, from the recorded run when there is one
model_request = None
src = HERE / "logs" / "our_harness.json"
if src.exists():
    run = json.loads(src.read_text())
    for step in run.get("single", {}).get("steps", []):
        for tc in step.get("tool_calls", []):
            if tc["name"] == TOOL:
                model_request = {"source": "logs/our_harness.json (single question, recorded run)", "model": run["single"].get("model"),
                                 "assistant_tool_call": tc}
                break
        if model_request:
            break
if model_request is None:
    model_request = {"source": "tool.json example (no recorded run found)", "assistant_tool_call":
                     {"id": "call_0", "name": TOOL, "arguments": spec.spec["example"]}}
out["model_request"] = model_request
args = model_request["assistant_tool_call"]["arguments"]

erp = ERP()
tb = Toolbox(erp, "ECLARKE")
clean = spec.check(args)
n0 = len(erp.calls)
result = tb.call(TOOL, args)
out["checked_at_the_door"] = {"arguments_in": args, "arguments_clean": clean,
                              "against": spec.spec["input_schema"]}
out["legacy_calls"] = [{"seq": i + 1, "service": c["svc"], "request": c["payload"],
                        "reply": {"rc": c["rc"], "err_cd": c["err_cd"], "msg": c["msg"],
                                  "data": next(r.data for r in erp.calls if r.seq == c["seq"])},
                        "stored_procedures": c["sps"]} for i, c in enumerate(erp.live_run(n0))]
out["tool_result"] = result
out["sizes"] = {"legacy_replies_bytes": sum(len(json.dumps(c["reply"], default=str)) for c in out["legacy_calls"]),
                "tool_result_bytes": len(json.dumps(result, default=str)),
                "legacy_calls": len(out["legacy_calls"])}
out["what_the_model_sees"] = ("Only tool_result, as JSON text (plus, over MCP, the same dict as structuredContent). "
                              "Not tool.py, not the services, their replies, the database, Emma's session or her password.")

# the same call over MCP, as JSON-RPC (in-memory transport)
try:
    from ledgerline.mcp_server import MCPClient
    from ledgerline.toolbox.mcp import build_toolbox_server
    c = MCPClient(build_toolbox_server(ERP(), "ECLARKE", names=[TOOL]))
    res = c.call_tool(TOOL, args).model_dump(mode="json", by_alias=True, exclude_none=True)
    out["mcp"] = {"request": {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": TOOL, "arguments": args}},
                  "response": {"jsonrpc": "2.0", "id": 2, "result": res},
                  "note": "the shape of the messages; logs/mcp_raw.json has the bytes captured from a real stdio session"}
    c.close()
except ImportError as e:
    out["mcp"] = {"not_run": f"fastmcp not installed here ({e})"}

# 4 the error path: a bad item code
erp2 = ERP()
tb2 = Toolbox(erp2, "ECLARKE")
bad = {"item_code": "BAT-5000"}
n1 = erp2.calls[-1].seq if erp2.calls else 0
err = tb2.call(TOOL, bad)
out["error_path"] = {"model_request": {"name": TOOL, "arguments": bad},
                     "legacy_calls": [{"service": c["svc"], "request": c["payload"],
                                       "reply": {"rc": c["rc"], "err_cd": c["err_cd"], "msg": c["msg"], "data": None}}
                                      for c in erp2.live_run(n1)],
                     "tool_result": err,
                     "how": "_ledgerline() turns rc=E into a ToolError: the message in words, next_step from ERR_HELP, "
                            "and the legacy code kept as ledgerline_code. Toolbox.call returns it as ok=false."}
# and a wrong type, refused at the door before any Ledgerline call
erp3 = ERP()
tb3 = Toolbox(erp3, "ECLARKE")
n2 = len(erp3.calls)
out["error_path_wrong_type"] = {"model_request": {"name": TOOL, "arguments": {"item_code": 500}},
                                "tool_result": tb3.call(TOOL, {"item_code": 500}),
                                "ledgerline_calls": len(erp3.calls) - n2}

(HERE / "logs").mkdir(exist_ok=True)
(HERE / "logs" / "anatomy_check_stock.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("model request:", model_request["source"], json.dumps(args))
for c in out["legacy_calls"]:
    print(f"  {c['service']:10} {json.dumps(c['request'])}  -> rc={c['reply']['rc']} {json.dumps(c['reply']['data'], default=str)[:110]}")
print("tool result:", json.dumps(result)[:300])
print("error path:", json.dumps(err))
print("sizes:", out["sizes"])
