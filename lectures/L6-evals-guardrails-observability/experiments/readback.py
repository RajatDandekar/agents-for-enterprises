"""Read the v2 demo traces back from every tool they were sent to, through each tool's own API, and say what arrived:
input, output, tokens, cost. LangSmith: also make a public share link per trace (so the deck can use logged-out screens).

    tools/mrun.sh .../l6_modal.py --script readback.py            (keys come from the course .env at run time; never printed)

Writes logs/readback.json. Nothing here prints a key, a header or a DSN.
"""
import base64
import json
import os
import time
import uuid

import httpx

from _common import LOGS, now, write

tv = json.loads((LOGS / "traces_v2.json").read_text())
turns = [(name, i, t) for name, r in tv["rows"].items() for i, t in enumerate(r["turns"], 1)]
out = {"at": now(), "traces": []}


def short(x, n=160):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, default=str)
    return s[:n]


# ------------------------------------------------------------------------------------------------ Langfuse
def langfuse(tid):
    """Langfuse v4 is observation-centric: the old GET /traces/{id} answers 410. Read the trace's observations instead."""
    base = (os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL")).rstrip("/")
    c = httpx.Client(base_url=base, auth=(os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]), timeout=60)
    for attempt in range(6):
        r = c.get("/api/public/v2/observations", params={"traceId": tid, "limit": 100, "fields": "core,basic,io,usage,metadata"})
        if r.status_code != 429:
            break
        time.sleep(8 * (attempt + 1))
    if r.status_code != 200:
        return {"arrived": False, "status": r.status_code, "body": r.text[:160]}
    obs = r.json().get("data") or []
    if not obs:
        return {"arrived": False, "why": "no observations for this trace id"}
    root = next((o for o in obs if o.get("type") == "AGENT" or not o.get("parentObservationId")), obs[0])
    gens = [o for o in obs if o.get("type") == "GENERATION"]
    tools = [o for o in obs if o.get("type") == "TOOL"]

    def cost(o):
        return float(o.get("totalCost") or (o.get("costDetails") or {}).get("total") or o.get("calculatedTotalCost") or 0)
    return {"arrived": True, "observations": len(obs), "root": root.get("name"), "input": short(root.get("input")), "output": short(root.get("output")),
            "has_input": root.get("input") is not None, "has_output": root.get("output") is not None,
            "generations": len(gens), "generations_with_io": sum(1 for g in gens if g.get("input") is not None and g.get("output") is not None),
            "tools": len(tools), "tools_with_io": sum(1 for t in tools if t.get("input") is not None and t.get("output") is not None),
            "tokens_in": sum(int((g.get("usageDetails") or {}).get("input", 0) or 0) for g in gens),
            "tokens_out": sum(int((g.get("usageDetails") or {}).get("output", 0) or 0) for g in gens),
            "cost_usd": round(sum(cost(g) for g in gens), 6), "session": root.get("sessionId"), "user": root.get("userId")}


# ------------------------------------------------------------------------------------------------ LangSmith
LS = (os.environ.get("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com").rstrip("/")
_ls = {}


def ls_client():
    if "c" not in _ls:
        _ls["c"] = httpx.Client(base_url=LS, headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=60)
        r = _ls["c"].get("/api/v1/sessions", params={"name": os.environ.get("LANGSMITH_PROJECT", "ask-northbridge")})
        d = (r.json() or [None])[0] if r.status_code < 300 else None
        _ls["project"] = d and d["id"]
        _ls["tenant"] = d and d.get("tenant_id")
    return _ls["c"]


def langsmith(tid):
    """LangSmith gives an OTLP span the run id 00000000-0000-0000-<span id>, and a trace the id of its root run; the
    OpenTelemetry ids are kept in metadata (OTEL_TRACE_ID, OTEL_SPAN_ID). So: find the root by OTEL_TRACE_ID, then its runs."""
    c = ls_client()
    if not _ls.get("project"):
        return {"arrived": False, "why": "project not found"}
    if "roots" not in _ls:
        q = c.post("/api/v2/runs/query", json={"project_ids": [_ls["project"]], "is_root": True, "page_size": 200,
                                               "selects": ["ID", "NAME", "TRACE_ID", "METADATA", "START_TIME"]})
        q.raise_for_status()
        _ls["roots"] = {(x.get("metadata") or {}).get("OTEL_TRACE_ID"): x for x in q.json().get("items", [])}
    root0 = _ls["roots"].get(tid)
    if not root0:
        return {"arrived": False, "why": "no root run with this OTEL_TRACE_ID in the newest 200"}
    sel = ["ID", "NAME", "RUN_TYPE", "INPUTS", "OUTPUTS", "TOTAL_TOKENS", "PROMPT_TOKENS", "COMPLETION_TOKENS", "TOTAL_COST", "IS_ROOT",
           "TRACE_ID", "THREAD_ID", "METADATA"]
    r = c.post("/api/v2/runs/query", json={"project_ids": [_ls["project"]], "trace_id": root0["id"], "selects": sel, "page_size": 100})
    if r.status_code >= 300:
        return {"arrived": False, "status": r.status_code, "body": r.text[:200]}
    runs = r.json().get("items") or []
    root = next((x for x in runs if x.get("is_root")), None) or root0
    llm = [x for x in runs if (x.get("run_type") or "").lower() == "llm"]
    tools = [x for x in runs if (x.get("run_type") or "").lower() == "tool"]
    res = {"arrived": True, "runs": len(runs), "root": root.get("name"), "run_id": root0["id"], "input": short(root.get("inputs")),
           "output": short(root.get("outputs")), "has_input": bool(root.get("inputs")), "has_output": bool(root.get("outputs")),
           "llm_runs": len(llm), "llm_with_io": sum(1 for x in llm if x.get("inputs") and x.get("outputs")),
           "tool_runs": len(tools), "tool_with_io": sum(1 for x in tools if x.get("inputs") and x.get("outputs")),
           "tokens_in": sum(x.get("prompt_tokens") or 0 for x in llm), "tokens_out": sum(x.get("completion_tokens") or 0 for x in llm),
           "cost_usd": round(sum(float(x.get("total_cost") or 0) for x in llm), 6), "root_total_tokens": root.get("total_tokens"),
           "root_cost_usd": float(root.get("total_cost") or 0), "thread": root.get("thread_id"),
           "priced_as": next(((x.get("metadata") or {}).get("ls_model_name") for x in llm), None)}
    # a public link (anyone with the link can read this one trace, no account): made once, returned again on later calls
    s = c.post(f"/api/v2/runs/{root0['id']}/share", json={"session_id": _ls["project"], "trace_id": root0["id"]})
    res["share_status"] = s.status_code
    if s.status_code < 300:
        tok = (s.json() or {}).get("share_token")
        res["public_url"] = f"https://smith.langchain.com/public/{tok}/r" if tok else None
    else:
        res["share_error"] = s.text[:200]
    u = c.get(f"/api/v2/runs/{root0['id']}/url", params={"project_id": _ls["project"], "trace_id": root0["id"]})
    res["ui_url"] = (u.json() or {}).get("url") if u.status_code < 300 else f"({u.status_code})"
    return res


# ------------------------------------------------------------------------------------------------ Sentry
def sentry(tid):
    org = os.environ["SENTRY_ORG"]
    h = {"Authorization": "Bearer " + os.environ["SENTRY_AUTH_TOKEN"]}
    res = {"arrived": False}
    for host in ("https://us.sentry.io", "https://sentry.io"):
        c = httpx.Client(base_url=host, headers=h, timeout=60)
        fields = ["id", "span.op", "span.description", "span.duration", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens",
                  "gen_ai.cost.total_tokens", "gen_ai.request.model", "gen_ai.tool.name", "project"]
        r = c.get(f"/api/0/organizations/{org}/events/", params=[("dataset", "spans"), ("query", f"trace:{tid}"), ("statsPeriod", "24h"),
                                                                  ("per_page", "100")] + [("field", f) for f in fields])
        res["events_status"] = r.status_code
        if r.status_code == 200:
            rows = r.json().get("data") or []
            chat = [x for x in rows if x.get("span.op") == "gen_ai.chat"]
            tools = [x for x in rows if x.get("span.op") == "gen_ai.execute_tool"]
            res.update({"arrived": bool(rows), "host": host, "spans": len(rows), "ops": sorted({x.get("span.op") for x in rows if x.get("span.op")}),
                        "chat_spans": len(chat), "tool_spans": len(tools),
                        "tokens_in": sum(int(x.get("gen_ai.usage.input_tokens") or 0) for x in chat),
                        "tokens_out": sum(int(x.get("gen_ai.usage.output_tokens") or 0) for x in chat),
                        "cost_usd": round(sum(float(x.get("gen_ai.cost.total_tokens") or 0) for x in chat), 6)})
        else:
            res["events_body"] = r.text[:200]
        t = c.get(f"/api/0/organizations/{org}/trace/{tid}/", params=[("statsPeriod", "24h")] + [("additional_attributes", a) for a in (
            "gen_ai.input.messages", "gen_ai.output.messages", "gen_ai.tool.call.arguments", "gen_ai.tool.call.result", "gen_ai.cost.total_tokens")])
        res["trace_status"] = t.status_code
        if t.status_code == 200:
            flat = []

            def walk(n):
                flat.append(n)
                for k in n.get("children") or []:
                    walk(k)
            for n in t.json() if isinstance(t.json(), list) else []:
                walk(n)
            aa = [n.get("additional_attributes") or {} for n in flat]
            res.update({"trace_nodes": len(flat), "nodes_with_input": sum(1 for a in aa if a.get("gen_ai.input.messages")),
                        "nodes_with_output": sum(1 for a in aa if a.get("gen_ai.output.messages")),
                        "nodes_with_tool_args": sum(1 for a in aa if a.get("gen_ai.tool.call.arguments")),
                        "nodes_with_tool_result": sum(1 for a in aa if a.get("gen_ai.tool.call.result")),
                        "input": short(next((a["gen_ai.input.messages"] for a in aa if a.get("gen_ai.input.messages")), "")),
                        "output": short(next((a["gen_ai.output.messages"] for a in aa if a.get("gen_ai.output.messages")), ""))})
            res["arrived"] = res["arrived"] or bool(flat)
        else:
            res["trace_body"] = t.text[:200]
        if res["arrived"]:
            break
    return res


have = {"langfuse": bool(os.environ.get("LANGFUSE_SECRET_KEY")), "langsmith": bool(os.environ.get("LANGSMITH_API_KEY")),
        "sentry": bool(os.environ.get("SENTRY_AUTH_TOKEN") and os.environ.get("SENTRY_ORG"))}
out["keys_present"] = have
for name, i, t in turns:
    row = {"run": name, "turn": i, "text": t["text"], "trace_id": t["trace_id"], "sent": {"tokens_in": t["tokens_in"], "tokens_out": t["tokens_out"], "usd": t["usd"]}}
    for tool, fn in (("langfuse", langfuse), ("langsmith", langsmith), ("sentry", sentry)):
        if not have[tool]:
            row[tool] = {"arrived": None, "why": "no key"}
            continue
        try:
            row[tool] = fn(t["trace_id"])
        except Exception as e:  # noqa: BLE001
            row[tool] = {"arrived": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}
    out["traces"].append(row)
    time.sleep(0.3)
out["langsmith_project"] = {"tenant": _ls.get("tenant"), "project": _ls.get("project")}
write("readback.json", out)
for r in out["traces"]:
    print(f"\n{r['run']} turn {r['turn']} · {r['trace_id']} · sent {r['sent']}")
    for tool in ("langfuse", "langsmith", "sentry"):
        print(f"  {tool:9}", json.dumps(r[tool], ensure_ascii=False)[:900])
