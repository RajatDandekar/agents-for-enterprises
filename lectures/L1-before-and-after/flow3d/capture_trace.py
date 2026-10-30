"""Record the real trace the 3D "How it works" animation plays: Ask Northbridge (L1) answering Emma, step by step.

    sh tools/mrun.sh tools/modal_run.py --script lectures/L1-before-and-after/flow3d/capture_trace.py --mode auto
-> flow3d/trace.json (+ trace.js, the same data as a classic script for decks opened without a server)

What is recorded, all from the run itself (nothing typed in by hand):
  * every model call: messages in, tokens in/out, seconds, the tool calls it chose (name + argument JSON) or its text;
  * every tool call: the guard's check of the arguments against tool.json, the MCP JSON-RPC frame that went over the
    plug, each Ledgerline service the tool called (data in, rc, ms, data out), the result JSON and the wall time;
  * the context split (system prompt / chat history / 15 tool schemas), measured by difference: the same request
    is sent again without the tools, and with the system prompt alone (cassette L1v4_flow3d_measure);
  * Daniel's approval inbox before and after, read with list_my_approvals as DOKAFOR.
Cassette L1v4_flow3d: the first run records, later runs replay with the recorded tokens and seconds.
"""
import datetime as dt
import json
import pathlib
import time

from ledgerline.course import l1
from ledgerline.course.l1 import AskNorthbridge
from ledgerline.erp.engine import ERP
from ledgerline.llm import LLM
from ledgerline.toolbox import SPECS, Toolbox

OUT = pathlib.Path(__file__).parent
CASSETTE = "L1v4_flow3d"
TURNS = ["How many city e-bike battery packs do we have?",
         "Order 2,000 battery packs from Voltway Cells for the spring launch run, cost centre PRD-07, needed by 9 November."]


def answer(reply: str, said: list[str]) -> str:
    """Emma's answers to a question, fixed rules so a replay is identical (as ledgerline.course.l1.answer)."""
    r = (reply or "").lower()
    if ("cost centre" in r or "cost center" in r) and not any("PRD-07" in s for s in said):
        return "Charge it to PRD-07, the spring launch run."
    if ("need" in r and ("date" in r or "when" in r or "by" in r)) and not any("November" in s for s in said):
        return "We need them by 9 November."
    if "voltway" in r and ("which" in r or "two" in r) and not any("Eindhoven" in s for s in said):
        return "Voltway Cells, Eindhoven."
    return "Yes, go ahead."


def compact(v, depth=0):
    """A short, faithful view of a service payload or reply (cut, never changed)."""
    if isinstance(v, dict):
        items = list(v.items())[:10]
        return {k: compact(x, depth + 1) for k, x in items}
    if isinstance(v, list):
        return [compact(x, depth + 1) for x in v[:3]] + ([f"... {len(v) - 3} more"] if len(v) > 3 else [])
    if isinstance(v, str) and len(v) > 120:
        return v[:117] + "..."
    return v


erp = ERP()
a = AskNorthbridge(erp, "ECLARKE", cassette=CASSETTE)
daniel = Toolbox(erp, "DOKAFOR")
inbox_before = daniel.call("list_my_approvals", {})
events: list[dict] = []
measure = LLM(a.llm.model, cassette=CASSETTE + "_measure")
split = {}

orig_chat = a.llm.chat


def chat(messages, tools=None, **kw):
    r = orig_chat(messages, tools=tools, **kw)
    if not split and tools:
        # measured by difference: the same request without the tools, and the system prompt alone
        no_tools = measure.chat(messages)
        sys_only = measure.chat(messages[:1] + [{"role": "user", "content": "."}])  # Gemini needs one user turn
        split.update({"total": r.tokens_in, "with_system_only": sys_only.tokens_in,
                      "without_tools": no_tools.tokens_in,
                      "system": sys_only.tokens_in, "history": no_tools.tokens_in - sys_only.tokens_in,
                      "schemas": r.tokens_in - no_tools.tokens_in,
                      "method": "tokens_in of the real request, minus the same request sent without tools, minus "
                                "the system prompt sent with a one-character user turn (provider-reported prompt_tokens)"})
    events.append({"kind": "llm", "messages": len(messages), "roles": [m["role"] for m in messages],
                   "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                   "replayed": bool(getattr(r, "replayed", False)),
                   "tool_calls": [{"id": tc.id, "name": tc.name, "arguments": tc.arguments} for tc in r.tool_calls],
                   "content": r.content})
    return r


a.llm.chat = chat
orig_call = a.tools.call


def call(name, args):
    n0, w0, t0 = len(erp.calls), len(a.client.wire), time.perf_counter()
    try:  # the guard: the same check Toolbox.call makes at the door, against tool.json
        clean = SPECS[name].check(args or {})
        props = SPECS[name].spec["input_schema"].get("properties", {})
        guard = {"ok": True, "checked": [{"arg": k, "type": props[k].get("type"), "value": v} for k, v in clean.items()],
                 "required": SPECS[name].spec["input_schema"].get("required", []),
                 "writes": SPECS[name].writes}
    except Exception as e:
        guard = {"ok": False, "error": str(e), "writes": SPECS[name].writes if name in SPECS else None}
    out = orig_call(name, args)
    ms = round((time.perf_counter() - t0) * 1000, 1)
    wire = a.client.wire[w0:]
    try:
        res = json.loads(out)
    except Exception:
        res = out
    svcs = [{"svc": c.svc, "in": compact(c.payload), "rc": c.rc, "err_cd": c.err_cd, "msg": c.msg,
             "ms": round(c.ms, 2), "out": compact(c.data)} for c in erp.calls[n0:]]
    events.append({"kind": "tool", "name": name, "args": args, "guard": guard,
                   "mcp": {"request": {"jsonrpc": "2.0", "method": "tools/call",
                                       "params": {"name": name, "arguments": args}},
                           "wire": [{"method": w["method"], "is_error": bool((w.get("result") or {}).get("isError"))
                                     if isinstance(w.get("result"), dict) else None} for w in wire]},
                   "services": svcs, "result": res, "ms": ms})
    return out


a.tools.call = call

turns, said = [], []
t_all = time.perf_counter()
for i, first in enumerate(TURNS):
    text = first
    for _ in range(4):
        said.append(text)
        e0 = len(events)
        t0 = time.perf_counter()
        reply = a.ask(text)
        turns.append({"user": text, "reply": reply, "seconds": round(time.perf_counter() - t0, 2),
                      "events": events[e0:]})
        print(f"\n> {text}\n< {reply}")
        for e in events[e0:]:
            if e["kind"] == "llm":
                print(f"   llm in={e['tokens_in']} out={e['tokens_out']} {e['seconds']}s ->",
                      [(t['name'], t['arguments']) for t in e["tool_calls"]] or "text")
            else:
                print(f"   tool {e['name']} {json.dumps(e['args'])} guard={e['guard']['ok']} "
                      f"svcs={[s['svc'] + ':' + s['rc'] for s in e['services']]} ms={e['ms']}")
        if i == 0:
            break
        pa = erp.q("SELECT pr_no, status FROM pr_hdr WHERE raised_on >= '2026-10-26' AND status='PA'") + \
            erp.q("SELECT po_no, status FROM po_hdr WHERE created_on >= '2026-10-26' AND status='PA'")
        if pa:
            break
        text = answer(reply, said)

inbox_after = daniel.call("list_my_approvals", {})
u = erp.user("ECLARKE")
trace = {
    "meta": {"fixture": False, "what": "Ask Northbridge (Lecture 1) answering Emma Clarke, one real recorded run",
             "model": a.llm.model, "cassette": CASSETTE, "measure_cassette": CASSETTE + "_measure",
             "script": "lectures/L1-before-and-after/flow3d/capture_trace.py",
             "assistant": "ledgerline.course.l1.AskNorthbridge (ToolLoopAgent + toolbox over MCP)",
             "mcp_server": "ledgerline-toolbox (ledgerline.toolbox.mcp, in memory)",
             "run_at": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
             # the model replies were recorded live into the cassette on this date; later runs replay them only if
             # every request (system prompt, history, tool schemas) hashes the same, so a replay proves they are current
             "recorded_live": "2026-10-30 04:15 UTC, recorded live after the tool descriptions and policy documents were finalised",
             "llm_mode": a.llm.mode, "replayed": all(e.get("replayed") for e in events if e["kind"] == "llm"),
             "sandbox_clock": "Mon 26 Oct 2026, 09:00 GMT", "user": "ECLARKE", "user_name": u["name"],
             "wall_seconds": round(time.perf_counter() - t_all, 2), "totals": a.llm.totals()},
    "system_prompt": a.agent.messages[0]["content"],
    "context_split": split,
    "tools": [{"name": n, "title": s.spec["title"], "category": s.spec["category"], "writes": s.writes,
               "description": s.spec["description"], "params": list(s.spec["input_schema"].get("properties", {})),
               "required": s.spec["input_schema"].get("required", []), "services": s.spec.get("services", [])}
              for n, s in SPECS.items()],
    "tools_over_mcp": a.tools.names,
    "turns": turns,
    "inbox": {"user": "DOKAFOR", "before": inbox_before, "after": inbox_after},
}
(OUT / "trace.json").write_text(json.dumps(trace, indent=1, default=str, ensure_ascii=False))
(OUT / "trace.js").write_text("window.FLOW3D_TRACE = " + json.dumps(trace, default=str, ensure_ascii=False) + ";\n")
print("\ncontext split:", split)
print("totals:", a.llm.totals(), "| inbox after:", json.dumps(inbox_after, default=str)[:400])
a.close()
