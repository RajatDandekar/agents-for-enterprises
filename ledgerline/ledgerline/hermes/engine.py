"""Hermes's workflow engine: the Workflow Studio's engine (experience/studio/engine.py), copied and extended for
Lecture 5. The Studio's SPEC.md still describes the base: nodes, edges, ports, {{ }} templates, approvals as a saved
wait. What is new here:

    params      a workflow has parameters: [{name, label, type, default, help}]; nodes read them as {{params.days_late}}.
                What changes per run is a parameter; what never changes is written into the node.
    foreach     a batch node: run a short list of steps once for every item of a list, several at a time, e.g. every
                invoice in the AP inbox. Inside, {{item}} is the current item and {{steps.<id>}} an earlier step's
                output. A step may have "when" (run it only if true) and "outcome" (what the item counts as when that
                step ran: "posted", "held"). The node's output tallies the outcomes: {"posted": 32, "held": 7, ...}.
    approvals   an approval node may wait on a list of documents (every request a batch raised).
    the clock   {{today}} and {{now}} are the student's simulated time; every node runs at that time.
    cost        every node records seconds, tokens and US$ (model nodes), so a run shows what it cost.

    eng = Engine(toolbox_for, llm_for, now=lambda: clock.t)
    eng.validate(wf)          # -> problems (each names the node), checked against the toolbox's own tool.json
    run = eng.start(wf, trigger_data, params)
    eng.run_until_pause(run)  # -> "done", "failed" or "waiting" (for an approval)
"""
from __future__ import annotations

import ast
import copy
import datetime as dt
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ..llm import PRICES
from ..toolbox import HABITS, REGISTRY
from .world import PEOPLE

DEFAULT_MODEL = "gemini:gemini-3.8-flash"
NODE_TYPES = ["trigger", "tool", "condition", "approval", "llm", "message", "set", "foreach"]
INNER_TYPES = ["tool", "llm", "message", "set"]
TRIGGER_KINDS = ["manual", "schedule", "event", "form"]
PORTS = {"condition": ["true", "false"], "approval": ["out", "rejected"]}
FINISHED = {"done", "warning", "error", "skipped"}
SPECS = {n: REGISTRY[n] for n in HABITS}
PARAM_TYPES = ["number", "text", "choice", "boolean", "date", "person"]


class FlowError(Exception):
    """A problem a student can fix: the message says what is wrong, next_step says what to do."""

    def __init__(self, message: str, next_step: str = ""):
        super().__init__(message)
        self.next_step = next_step


# =====================================================================================================================
# 1. Templates (as the Studio's, with params, item, steps, now and a few more functions)
# =====================================================================================================================
TEMPLATE = re.compile(r"\{\{(.*?)\}\}", re.S)


def num(v) -> str:
    return f"{int(round(float(v))):,}"


def _money(v) -> str:
    v = float(v)
    return f"£{v:,.2f}" if abs(v - round(v)) > 0.004 else f"£{int(round(v)):,}"


def _dt(d) -> dt.date:
    return dt.date.fromisoformat(str(d)[:10])


FUNCS = {"min": min, "max": max, "round": round, "int": int, "float": float, "str": str, "len": len, "abs": abs,
         "sum": lambda xs: sum(float(x) for x in xs), "upper": lambda s: str(s).upper(), "lower": lambda s: str(s).lower(),
         "money": _money, "num": num, "pct": lambda v: f"{float(v):g}%",
         "add_days": lambda d, n: (_dt(d) + dt.timedelta(days=int(n))).isoformat(),
         "days_between": lambda a, b: (_dt(b) - _dt(a)).days,
         "date": lambda d: _dt(d).strftime("%-d %b %Y"),
         "join": lambda xs, sep=", ": sep.join(str(x) for x in xs),
         "pluck": lambda xs, k: [x.get(k) if isinstance(x, dict) else None for x in (xs or [])],
         "first": lambda xs: (xs or [None])[0], "count": lambda xs: len(xs or []),
         "tally": lambda d: ", ".join(f"{v} {k}" for k, v in (d or {}).items()) or "nothing"}
NAMES = {"true": True, "false": False, "null": None, "True": True, "False": False, "None": None}
BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
          ast.Div: lambda a, b: a / b, ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b}
CMPOPS = {ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b, ast.Lt: lambda a, b: a < b,
          ast.LtE: lambda a, b: a <= b, ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
          ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}


def _get(obj, key, where: str):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        raise FlowError(f"{where} has no field '{key}' (it has: {', '.join(map(str, obj)) or 'nothing yet'}).",
                        "Pick a field the earlier step really returns.")
    if isinstance(obj, list):
        try:
            return obj[int(key)]
        except (ValueError, IndexError):
            raise FlowError(f"{where} has no item [{key}] (it has {len(obj)}).", "Check the list is not empty.")
    raise FlowError(f"{where} is {obj!r}, not something with fields.", "Check the path.")


def evaluate(expr: str, ctx: dict):
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError:
        raise FlowError(f"Cannot read the expression '{expr.strip()}'.", "Write a path like nodes.pr.request_no.")

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            if n.id in NAMES:
                return NAMES[n.id]
            return _get(ctx, n.id, "the run")
        if isinstance(n, ast.Attribute):
            return _get(ev(n.value), n.attr, ast.unparse(n.value))
        if isinstance(n, ast.Subscript):
            return _get(ev(n.value), ev(n.slice), ast.unparse(n.value))
        if isinstance(n, ast.BinOp) and type(n.op) in BINOPS:
            return BINOPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp):
            v = ev(n.operand)
            return {ast.Not: lambda: not v, ast.USub: lambda: -v, ast.UAdd: lambda: +v}[type(n.op)]()
        if isinstance(n, ast.BoolOp):
            vals = [ev(v) for v in n.values]
            return all(vals) if isinstance(n.op, ast.And) else next((v for v in vals if v), vals[-1])
        if isinstance(n, ast.Compare) and all(type(o) in CMPOPS for o in n.ops):
            left = ev(n.left)
            for op, right in zip(n.ops, n.comparators):
                right = ev(right)
                if not CMPOPS[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(n, ast.IfExp):
            return ev(n.body) if ev(n.test) else ev(n.orelse)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and not n.keywords:
            return FUNCS[n.func.id](*[ev(a) for a in n.args])
        if isinstance(n, (ast.List, ast.Tuple)):
            return [ev(e) for e in n.elts]
        raise FlowError(f"'{ast.unparse(n)}' is not allowed in a template.",
                        "Use paths, numbers, + - * /, comparisons, and/or/not and the listed functions.")

    try:
        return ev(tree)
    except FlowError:
        raise
    except Exception as e:  # noqa: BLE001
        raise FlowError(f"'{expr.strip()}' failed: {e}.", "Check the values it uses.")


def fill(value, ctx: dict):
    if isinstance(value, dict):
        return {k: fill(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [fill(v, ctx) for v in value]
    if not isinstance(value, str) or "{{" not in value:
        return value
    whole = TEMPLATE.fullmatch(value.strip())
    if whole and "{{" not in whole.group(1) and "}}" not in whole.group(1):
        return evaluate(whole.group(1), ctx)

    def text(m):
        v = evaluate(m.group(1), ctx)
        return json.dumps(v, default=str) if isinstance(v, (dict, list)) else ("" if v is None else str(v))

    return TEMPLATE.sub(text, value)


def references(value, root="nodes") -> set[str]:
    found = set()
    for s in re.findall(r"\{\{(.*?)\}\}", json.dumps(value)):
        found |= set(re.findall(rf"\b{root}\.([A-Za-z_][A-Za-z0-9_]*)", s))
    return found


def summary(out) -> str:
    """A one-line receipt for a node card and the run log."""
    if not isinstance(out, dict):
        return str(out)[:120]
    if out.get("ok") is False:
        return out.get("error", "failed")
    if "preview" in out:
        p = out["preview"]
        v = p.get("gross_value", p.get("estimated_value", p.get("gross", p.get("net"))))
        return "Preview only, nothing saved" + (f" · {_money(v)}" if isinstance(v, (int, float)) else "")
    if "tally" in out:
        return " · ".join(f"{v} {k}" for k, v in out["tally"].items()) or "nothing to do"
    if "orders" in out and isinstance(out["orders"], list):
        return f"{len(out['orders'])} open order{'s' if len(out['orders']) != 1 else ''}"
    if "messages" in out and isinstance(out["messages"], list):
        return f"{out.get('count', len(out['messages']))} message(s) in {out.get('folder', 'the mailbox')}"
    if "invoices" in out and isinstance(out["invoices"], list):
        return f"{len(out['invoices'])} invoice(s)"
    if "certificates" in out:
        return f"{out.get('count', 0)} certificate(s) to watch"
    if out.get("items") and isinstance(out["items"], list) and "shortfall" in str(out["items"][:1]):
        return f"{len(out['items'])} item(s) below reorder level"
    if "matches" in out and isinstance(out["matches"], list):
        return (f"{len(out['matches'])} match(es): " + ", ".join(m.get("name", "") for m in out["matches"][:3])) if out["matches"] \
            else "No existing supplier matches"
    if "open" in out and isinstance(out["open"], list):
        return f"{len(out['open'])} open cost centres"
    if "budget_left" in out:
        return f"{out.get('code')}: {_money(out['budget_left'])} left" + ("" if out.get("open", True) else " (closed)")
    if "result" in out and "invoice_no" in out:
        return f"{out['invoice_no']}: {out['result'].replace('_', ' ')}"
    main = next((out[k] for k in ("invoice_no", "grn_no", "po_no", "request_no", "supplier_code", "draft_id") if out.get(k)), None)
    parts = [str(x) for x in (main, out.get("status")) if x]
    if "cover_days" in out and out.get("item_code"):
        parts = [f"{out['item_code']}: {num(out.get('free_total', 0))} free, {out['cover_days']} days of cover"]
    if out.get("queued"):
        parts = [f"Sent to {out.get('to')}"]
    if "draft_id" in out:
        parts = [f"Draft for {out.get('to')} saved (not sent)"]
    if "text" in out and len(out) <= 2:
        parts = [str(out["text"])[:110]]
    if out.get("already_done"):
        parts.append("(already done)")
    return " · ".join(parts) or ", ".join(f"{k}: {v}" for k, v in list(out.items())[:3])[:120]


# =====================================================================================================================
# 2. Node types
# =====================================================================================================================
class Result:
    def __init__(self, status="done", output=None, port="out", text="", inputs=None, waiting=None, meta=None):
        self.status, self.output, self.port, self.text = status, output if output is not None else {}, port, text
        self.inputs, self.waiting, self.meta = inputs, waiting, meta or {}


def _warnings(out: dict) -> str:
    w = out.get("warning") or out.get("warnings")
    return "; ".join(w) if isinstance(w, list) else (w or "")


def _cost(r) -> dict:
    p = PRICES.get(r.model.split(":", 1)[-1].split("/")[-1], (0.5, 3.0))
    return {"model": r.model, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
            "usd": round((r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6, 6)}


def TRIGGER(eng, run, node, ctx):
    cfg, data = node.get("config", {}), dict(run.get("trigger_data") or {})
    kind = cfg.get("kind", "manual")
    if kind == "manual":
        return Result(output={**cfg.get("data", {}), **data}, text="Started by hand")
    if kind == "form":
        out = {f["name"]: data.get(f["name"], f.get("default")) for f in cfg.get("fields", [])}
        return Result(output=out, text="Form: " + ", ".join(f"{k}={v}" for k, v in out.items()))
    if kind == "schedule":
        return Result(output={"fired_at": ctx["now"], "schedule": schedule_text(cfg), **data}, text=f"Scheduled: {schedule_text(cfg)}")
    if kind == "event":
        ev = data.get("event") or {}
        return Result(output={"event": cfg.get("event"), **ev, **data}, text=f"Event: {cfg.get('event', 'event')}")
    raise FlowError(f"Unknown trigger kind '{kind}'.", f"Use one of {TRIGGER_KINDS}.")


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def schedule_text(cfg: dict) -> str:
    every, at = cfg.get("every", "week"), cfg.get("at", "09:00")
    if every == "week":
        return f"every {cfg.get('day', 'Mon')} at {at}"
    if every == "weekday":
        return f"every weekday at {at}"
    if every == "month":
        return f"on day {cfg.get('day_of_month', 1)} of every month at {at}"
    return f"every day at {at}"


def _tool_call(eng, cfg, ctx, ident):
    name = cfg.get("tool")
    if name not in SPECS:
        raise FlowError(f"There is no tool '{name}'.", "Pick a tool from the toolbox.")
    args = {k: v for k, v in fill(cfg.get("args", {}), ctx).items() if v not in (None, "")}
    if "confirm" in SPECS[name].spec["input_schema"].get("properties", {}):
        # the node's Commit switch; a literal true/false written among the arguments counts too (never a template)
        literal = (cfg.get("args") or {}).get("confirm")
        args["confirm"] = bool(cfg["confirm"]) if "confirm" in cfg else (literal is True)
    else:
        args.pop("confirm", None)
    props = SPECS[name].spec["input_schema"].get("properties", {})
    for k, v in list(args.items()):   # "6,000" or "£19.15" from a model step: numbers, as Ledgerline's own forms accept
        want = props.get(k, {}).get("type")
        if want in ("integer", "number") and isinstance(v, str):
            t = v.replace(",", "").replace("£", "").strip()
            try:
                f = float(t)
                args[k] = int(f) if want == "integer" and f.is_integer() else f
            except ValueError:
                pass
    out = eng.call_tool(cfg.get("as", "ECLARKE"), name, args, ident)
    return args, out


def TOOL(eng, run, node, ctx):
    cfg = node.get("config", {})
    args, out = _tool_call(eng, cfg, ctx, node["id"])
    if not out.get("ok"):
        return Result("error", out, port="error", inputs=args, text=f"{out.get('error', 'failed')} {out.get('next_step', '')}".strip())
    warn = _warnings(out)
    if warn:
        return Result("warning", out, inputs=args, text=f"Warning: {warn}")
    return Result(output=out, inputs=args, text=summary(out))


def CONDITION(eng, run, node, ctx):
    expr = str(node.get("config", {}).get("if", "")).strip()
    if not expr:
        raise FlowError("This condition has no test.", "Write one, e.g. {{ nodes.orders.count > 0 }}.")
    inner = TEMPLATE.fullmatch(expr)
    value = evaluate(inner.group(1) if inner else expr, ctx)
    branch = "true" if value else "false"
    return Result(output={"branch": branch, "value": value}, port=branch, text=f"{node.get('title') or expr} → {branch}")


APPROVED = {"AP", "RL", "CL"}


def APPROVAL(eng, run, node, ctx):
    """Wait for a signature on one document or on every document of a list (e.g. the requests a batch raised)."""
    cfg = node.get("config", {})
    raw = fill(cfg.get("doc_no", ""), ctx)
    docs = [str(d).strip() for d in (raw if isinstance(raw, list) else [raw]) if str(d or "").strip()]
    if not docs:
        return Result(output={"docs": [], "approved": 0}, text="Nothing to approve")
    rec = run["nodes"][node["id"]]
    rows, waiting, rejected = [], [], []
    for doc in docs:
        args = {"request_no": doc} if doc.upper().startswith("PR") else {"po_no": doc}
        st = eng.call_tool(cfg.get("as", "ECLARKE"), "order_status", args, node["id"])
        if not st.get("ok"):
            return Result("error", st, port="error", text=st.get("error", ""))
        code = st.get("status_code")
        approver = st.get("approver") or cfg.get("approver", "DOKAFOR")
        rows.append({"doc_no": doc, "status": st.get("status"), "status_code": code, "approver": approver,
                     "approved_by": st.get("approved_by")})
        if code == "PA":
            waiting.append(doc)
        elif code == "RJ":
            rejected.append(doc)
        elif code not in APPROVED:
            return Result("error", {"ok": False, "error": f"{doc} is {st.get('status')}: nobody will be asked to sign it.",
                                    "next_step": "Check the document with order_status."}, port="error",
                          text=f"{doc} is {st.get('status')}; it will never reach an approver")
    out = {"docs": rows, "doc_no": docs[0] if len(docs) == 1 else docs, "approved": len(docs) - len(waiting) - len(rejected),
           "waited": bool(rec.get("waited"))}
    if waiting:
        who = rows[[r["doc_no"] for r in rows].index(waiting[0])]["approver"]
        return Result("waiting", out, waiting={"node": node["id"], "doc_no": waiting[0], "docs": waiting, "approver": who,
                                               "approver_name": PEOPLE.get(who, {}).get("name", who)},
                      text=f"Waiting for {PEOPLE.get(who, {}).get('name', who)} to approve {', '.join(waiting)}")
    if rejected:
        return Result("error", {**out, "ok": False, "error": f"{', '.join(rejected)} rejected."}, port="rejected",
                      text=f"{', '.join(rejected)} rejected")
    return Result(output=out, text=f"{len(docs)} approved" + ("" if rec.get("waited") else " (no wait: within the limit)"))


def _llm_call(eng, cfg, ctx):
    prompt = fill(cfg.get("prompt", ""), ctx)
    if not str(prompt).strip():
        raise FlowError("The prompt is empty.", "Write a prompt; use {{ }} to put earlier outputs in it.")
    messages = [{"role": "system", "content": cfg["system"]}] if cfg.get("system") else []
    want_json = cfg.get("output", "text") == "json"
    if want_json:
        keys = ", ".join(cfg.get("fields", [])) or "the fields the prompt asks for"
        prompt = f"{prompt}\n\nReply with one JSON object only, no other text, with these keys: {keys}."
    messages.append({"role": "user", "content": str(prompt)})
    r = eng.llm_for(cfg.get("model") or DEFAULT_MODEL).chat(messages, **({"response_format": {"type": "json_object"}} if want_json else {}))
    meta = _cost(r)
    text = (r.content or "").strip()
    if not want_json:
        return {"text": text}, {"prompt": str(prompt)[:4000]}, meta, text[:110]
    m = re.search(r"\{.*\}", text, re.S)
    try:
        out = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        out = None
    if not isinstance(out, dict):
        raise FlowError(f"The model did not reply with JSON: {text[:160]!r}", "Make the prompt ask for JSON only.")
    missing = [k for k in cfg.get("fields", []) if k not in out]
    if missing:
        raise FlowError(f"The model's JSON has no {', '.join(missing)}.", "Name those fields in the prompt.")
    return out, {"prompt": str(prompt)[:4000]}, meta, ", ".join(f"{k}: {v}" for k, v in out.items())[:120]


def LLM_NODE(eng, run, node, ctx):
    out, inputs, meta, text = _llm_call(eng, node.get("config", {}), ctx)
    return Result(output=out, inputs=inputs, meta=meta, text=text)


def _message(eng, cfg, ctx, ident):
    to, text = fill(cfg.get("to", ""), ctx), fill(cfg.get("text", ""), ctx)
    out = eng.call_tool(cfg.get("as", "ECLARKE"), "send_message", {"to": str(to), "text": str(text)}, ident)
    return {"to": to, "text": text}, ({**out, "text": text} if out.get("ok") else out)


def MESSAGE(eng, run, node, ctx):
    inputs, out = _message(eng, node.get("config", {}), ctx, node["id"])
    if not out.get("ok"):
        return Result("error", out, port="error", inputs=inputs, text=out.get("error", ""))
    return Result(output=out, inputs=inputs, text=f"To {inputs['to']}: {str(inputs['text'])[:90]}")


def SET(eng, run, node, ctx):
    values = fill(node.get("config", {}).get("values", {}), ctx)
    return Result(output=values, text=", ".join(f"{k} = {v}" for k, v in values.items())[:120])


def _inner(eng, step, ctx, ident):
    """One step inside a foreach: returns (status, output, text, meta)."""
    typ, cfg = step.get("type"), step.get("config", {})
    if typ == "tool":
        args, out = _tool_call(eng, cfg, ctx, ident)
        if not out.get("ok"):
            return "error", out, f"{out.get('error', 'failed')}", {}, args
        return ("warning" if _warnings(out) else "done"), out, summary(out), {}, args
    if typ == "llm":
        out, inputs, meta, text = _llm_call(eng, cfg, ctx)
        return "done", out, text, meta, inputs
    if typ == "message":
        inputs, out = _message(eng, cfg, ctx, ident)
        return ("done" if out.get("ok") else "error"), out, f"To {inputs['to']}", {}, inputs
    if typ == "set":
        v = fill(cfg.get("values", {}), ctx)
        return "done", v, ", ".join(f"{k} = {x}" for k, x in v.items())[:100], {}, None
    raise FlowError(f"A step inside a batch cannot be a '{typ}'.", f"Use one of {INNER_TYPES}.")


def FOREACH(eng, run, node, ctx):
    """Run the steps once per item, several items at a time; tally what each item ended as."""
    cfg = node.get("config", {})
    items = fill(cfg.get("items", ""), ctx)
    if not isinstance(items, list):
        raise FlowError(f"'items' must be a list, got {type(items).__name__}.", "Point it at a list, e.g. {{nodes.inbox.messages}}.")
    limit = int(cfg.get("limit") or 200)
    items = items[:limit]
    steps = cfg.get("steps", [])
    rec = run["nodes"][node["id"]]
    # every outcome the steps can give starts at 0, so {{nodes.x.tally.posted}} exists even when nothing was posted
    prog = {"of": len(items), "done": 0, "items": [None] * len(items), "tally": {s["outcome"]: 0 for s in steps if s.get("outcome")}}
    with eng.lock:
        rec["progress"] = prog
    totals = {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "model_seconds": 0.0}

    def one(i):
        item = items[i]
        ictx = {**ctx, "item": item, "steps": {}, "index": i}
        if cfg.get("as"):
            ictx[cfg["as"]] = item
        lab = fill(cfg.get("label", ""), ictx) if cfg.get("label") else None
        row = {"i": i, "label": str(lab or (item.get("subject") or item.get("po_no") or item.get("item_code") or f"item {i + 1}")
                                    if isinstance(item, dict) else item)[:90], "steps": {}, "outcome": None, "status": "running"}
        with eng.lock:
            prog["items"][i] = row
        outcome = None
        for st in steps:
            sid = st.get("id")
            t0 = time.perf_counter()
            try:
                if st.get("when") and not fill(st["when"], ictx):
                    row["steps"][sid] = {"status": "skipped"}
                    continue
                status, out, text, meta, _ = _inner(eng, st, ictx, f"{node['id']}.{sid}")
            except FlowError as e:
                status, out, text, meta = "error", {"ok": False, "error": str(e), "next_step": e.next_step}, str(e), {}
            except Exception as e:  # noqa: BLE001  a model or network failure must not lose the batch
                status, out, text, meta = "error", {"ok": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}, type(e).__name__, {}
            ictx["steps"][sid] = out
            row["steps"][sid] = {"status": status, "summary": text[:140], "seconds": round(time.perf_counter() - t0, 2),
                                 **({"usd": meta.get("usd")} if meta else {})}
            if meta:
                with eng.lock:
                    totals["tokens_in"] += meta.get("tokens_in", 0)
                    totals["tokens_out"] += meta.get("tokens_out", 0)
                    totals["usd"] += meta.get("usd", 0.0)
                    totals["model_seconds"] += meta.get("seconds", 0.0)
            if status == "error":
                code = (out.get("ledgerline_code") or "").lower() if isinstance(out, dict) else ""
                outcome = code if code in ("duplicate",) else f"stopped at {st.get('title') or sid}"
                row["error"] = text[:200]
                break
            if status == "warning" and st.get("stop_on_warning", True):
                outcome = f"warning at {st.get('title') or sid}"
                break
            if st.get("outcome"):
                outcome = st["outcome"]
        row["outcome"] = outcome or "done"
        row["status"] = "error" if row.get("error") else "done"
        row["result"] = {k: v for k, v in (ictx["steps"].items())}  # every step's output, for the inspector
        with eng.lock:
            prog["done"] += 1
            prog["tally"][row["outcome"]] = prog["tally"].get(row["outcome"], 0) + 1
        return row

    t0 = time.perf_counter()
    par = max(1, min(int(cfg.get("parallel") or 6), 10))
    with ThreadPoolExecutor(par) as ex:
        rows = list(ex.map(one, range(len(items))))
    out = {"count": len(items), "tally": dict(prog["tally"]), "items": [{k: r[k] for k in ("i", "label", "outcome", "status", "steps")}
                                                                       | ({"error": r["error"]} if r.get("error") else {}) for r in rows],
           "results": [r["result"] for r in rows], "tokens_in": totals["tokens_in"], "tokens_out": totals["tokens_out"],
           "usd": round(totals["usd"], 6), "seconds": round(time.perf_counter() - t0, 2)}
    meta = {"tokens_in": totals["tokens_in"], "tokens_out": totals["tokens_out"], "usd": round(totals["usd"], 6),
            "seconds": round(totals["model_seconds"], 2), "model": DEFAULT_MODEL if totals["tokens_in"] else None}
    return Result(output=out, meta=meta, text=summary(out))


HANDLERS = {"trigger": TRIGGER, "tool": TOOL, "condition": CONDITION, "approval": APPROVAL, "llm": LLM_NODE,
            "message": MESSAGE, "set": SET, "foreach": FOREACH}


# =====================================================================================================================
# 3. Checking a workflow against the toolbox
# =====================================================================================================================
def _check_tool(nid, cfg, problems, checks, params, scope="nodes"):
    name = cfg.get("tool")
    if name not in SPECS:
        problems.append(f"{nid}: there is no tool '{name}' in the toolbox.")
        checks.append({"node": nid, "ok": False, "text": f"tool '{name}' is not in the toolbox"})
        return
    props = SPECS[name].spec["input_schema"].get("properties", {})
    req = SPECS[name].spec["input_schema"].get("required", [])
    args = cfg.get("args", {}) or {}
    bad = [k for k in args if k not in props]
    for k in bad:
        problems.append(f"{nid}: {name} has no argument '{k}' (it has: {', '.join(props) or 'none'}).")
    miss = [r for r in req if r not in args]
    for r in miss:
        problems.append(f"{nid}: {name} needs '{r}'.")
    if cfg.get("confirm") and "confirm" not in props:
        problems.append(f"{nid}: {name} has no confirm switch (only tools that save something do).")
    for k, v in args.items():
        if k in props and not (isinstance(v, str) and "{{" in v):
            want = props[k].get("type")
            if want == "integer" and not (isinstance(v, int) and not isinstance(v, bool)):
                problems.append(f"{nid}: {name}.{k} must be a whole number, got {v!r}.")
            if want == "number" and not isinstance(v, (int, float)):
                problems.append(f"{nid}: {name}.{k} must be a number, got {v!r}.")
            if "enum" in props[k] and v not in props[k]["enum"]:
                problems.append(f"{nid}: {name}.{k} must be one of {props[k]['enum']}, got {v!r}.")
    who = cfg.get("as", "ECLARKE")
    if who not in PEOPLE:
        problems.append(f"{nid}: '{who}' is not one of {list(PEOPLE)}.")
    if not bad and not miss:
        checks.append({"node": nid, "ok": True, "text": f"{name}({', '.join(args) or 'no arguments'}) as {who}: "
                                                         f"{len(args)} of {len(props)} arguments, required all given"})


def validate(wf: dict) -> tuple[list[str], list[dict]]:
    """Every problem a run would hit, found before it runs, each naming the node. Also the checks that passed."""
    problems, checks = [], []
    nodes = wf.get("nodes", [])
    ids = [n.get("id") for n in nodes]
    by_id = {n.get("id"): n for n in nodes}
    params = {p.get("name"): p for p in wf.get("params", []) or []}
    for p in params.values():
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", str(p.get("name", ""))):
            problems.append(f"Parameter name {p.get('name')!r} must be lowercase letters, digits and _.")
        if p.get("type", "text") not in PARAM_TYPES:
            problems.append(f"Parameter {p.get('name')}: type must be one of {PARAM_TYPES}.")
    for i in set(ids):
        if ids.count(i) > 1:
            problems.append(f"Two nodes are called '{i}'.")
    if len(nodes) > 16:
        problems.append(f"{len(nodes)} nodes: keep a workflow to 16 nodes or fewer.")
    for n in nodes:
        nid, typ, cfg = n.get("id"), n.get("type"), n.get("config", {}) or {}
        if not isinstance(nid, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nid):
            problems.append(f"Node id {nid!r} must be letters, digits and _.")
        if typ not in HANDLERS:
            problems.append(f"{nid}: unknown node type '{typ}' (use {', '.join(NODE_TYPES)}).")
            continue
        if typ == "tool":
            _check_tool(nid, cfg, problems, checks, params)
        if typ == "trigger" and cfg.get("kind", "manual") not in TRIGGER_KINDS:
            problems.append(f"{nid}: trigger kind '{cfg.get('kind')}' is not one of {TRIGGER_KINDS}.")
        if typ == "approval" and not cfg.get("doc_no"):
            problems.append(f"{nid}: an approval needs doc_no, e.g. {{{{nodes.pr.request_no}}}}.")
        if typ == "message" and not (cfg.get("to") and cfg.get("text")):
            problems.append(f"{nid}: a message needs 'to' and 'text'.")
        if typ == "condition" and not cfg.get("if"):
            problems.append(f"{nid}: a condition needs 'if'.")
        if typ == "llm" and not cfg.get("prompt"):
            problems.append(f"{nid}: a model step needs a prompt.")
        if typ == "foreach":
            if not cfg.get("items"):
                problems.append(f"{nid}: a batch needs 'items', e.g. {{{{nodes.inbox.messages}}}}.")
            steps = cfg.get("steps") or []
            if not steps:
                problems.append(f"{nid}: a batch needs at least one step.")
            sids = [s.get("id") for s in steps]
            for s in steps:
                sid = f"{nid}.{s.get('id')}"
                if s.get("type") not in INNER_TYPES:
                    problems.append(f"{sid}: a step inside a batch must be one of {INNER_TYPES}.")
                    continue
                if s.get("type") == "tool":
                    _check_tool(sid, s.get("config", {}) or {}, problems, checks, params)
                for ref in references(s, "steps"):
                    if ref not in sids or sids.index(ref) >= sids.index(s.get("id")):
                        problems.append(f"{sid} reads steps.{ref}, but no earlier step in the batch is called '{ref}'.")
        for who in [cfg.get("as"), cfg.get("approver")]:
            if who and typ not in ("foreach",) and who not in PEOPLE:
                problems.append(f"{nid}: '{who}' is not one of {list(PEOPLE)}.")
        for ref in references(cfg):
            if ref not in by_id:
                problems.append(f"{nid} reads nodes.{ref}, but there is no node '{ref}'.")
        for ref in references(cfg, "params"):
            if ref not in params:
                problems.append(f"{nid} reads params.{ref}, but the workflow has no parameter '{ref}'.")
        try:
            for s in re.findall(r"\{\{(.*?)\}\}", json.dumps(cfg)):
                ast.parse(json.loads('"' + s + '"').strip(), mode="eval")
        except (SyntaxError, json.JSONDecodeError):
            problems.append(f"{nid}: a {{{{ }}}} expression cannot be read.")
    triggers = [n for n in nodes if n.get("type") == "trigger"]
    if len(triggers) != 1:
        problems.append(f"A workflow needs exactly one trigger (it has {len(triggers)}).")
    for e in wf.get("edges", []):
        if e.get("from") not in by_id or e.get("to") not in by_id:
            problems.append(f"An edge joins {e.get('from')} → {e.get('to')}, but one of them does not exist.")
            continue
        typ = by_id[e["from"]].get("type")
        if e.get("port", "out") not in PORTS.get(typ, ["out"]) + ["error"]:
            problems.append(f"{e['from']} has no '{e.get('port')}' exit (it has {PORTS.get(typ, ['out'])}).")
        if by_id[e["to"]].get("type") == "trigger":
            problems.append(f"Nothing can lead into the trigger ({e['from']} → {e['to']}).")
    if not problems:
        if _has_cycle(wf):
            problems.append("The workflow has a loop; a workflow must flow one way (use a batch for repeats).")
        reach = _reachable(wf)
        for n in nodes:
            if n["id"] not in reach:
                problems.append(f"{n['id']}: nothing leads to it from the trigger.")
    used = set()
    for n in nodes:
        used |= references(n.get("config", {}), "params")
    for p in params:
        if p not in used:
            checks.append({"node": "params", "ok": True, "text": f"parameter '{p}' is not used by any node (harmless)"})
    return problems, checks


def _has_cycle(wf) -> bool:
    out = {}
    for e in wf.get("edges", []):
        out.setdefault(e["from"], []).append(e["to"])
    state = {}

    def visit(n):
        if state.get(n) == 1:
            return True
        if state.get(n) == 2:
            return False
        state[n] = 1
        if any(visit(m) for m in out.get(n, [])):
            return True
        state[n] = 2
        return False

    return any(visit(n["id"]) for n in wf.get("nodes", []))


def _reachable(wf) -> set:
    trig = next((n["id"] for n in wf.get("nodes", []) if n.get("type") == "trigger"), None)
    out, seen, todo = {}, set(), [trig]
    for e in wf.get("edges", []):
        out.setdefault(e["from"], []).append(e["to"])
    while todo:
        n = todo.pop()
        if n in seen or n is None:
            continue
        seen.add(n)
        todo += out.get(n, [])
    return seen


def layout(wf: dict, gap_x: int = 300, gap_y: int = 170) -> dict:
    """Place the nodes left to right by depth; a branch's two sides go above and below. The model never places nodes."""
    nodes = wf.get("nodes", [])
    by = {n["id"]: n for n in nodes}
    out = {}
    for e in wf.get("edges", []):
        out.setdefault(e["from"], []).append(e)
    trig = next((n["id"] for n in nodes if n.get("type") == "trigger"), nodes[0]["id"] if nodes else None)
    depth, lane = {trig: 0}, {trig: 0.0}
    order = [trig]
    i = 0
    while i < len(order):
        a = order[i]
        i += 1
        kids = out.get(a, [])
        for j, e in enumerate(kids):
            b = e["to"]
            if b not in by:
                continue
            d = depth[a] + 1
            if e.get("port") in ("false", "rejected", "error"):
                ln = lane[a] + 1
            elif e.get("port") == "true" and len(kids) > 1:
                ln = lane[a] - 0.0
            else:
                ln = lane[a] + (j if len(kids) > 1 and e.get("port") in (None, "out") else 0)
            if b not in depth or d > depth[b]:
                depth[b] = d
                lane[b] = ln if b not in lane else min(lane[b], ln)
                order.append(b)
    for n in nodes:
        d, ln = depth.get(n["id"], len(depth)), lane.get(n["id"], 0)
        n["x"], n["y"] = 60 + d * gap_x, 120 + ln * gap_y
    return wf


# =====================================================================================================================
# 4. The run loop
# =====================================================================================================================
class Engine:
    def __init__(self, toolbox_for, llm_for, now=None, on_save=None):
        """toolbox_for(user) -> Toolbox; llm_for(model) -> LLM; now() -> the simulated datetime."""
        self._make, self._tbs = toolbox_for, {}
        self.llm_for = llm_for
        self.now = now or (lambda: dt.datetime(2026, 10, 26, 9, 0, tzinfo=dt.timezone.utc))
        self.on_save = on_save or (lambda run: None)
        self.lock = threading.RLock()
        self.calls: list[dict] = []

    def toolbox_for(self, user: str):
        if user not in self._tbs:
            self._tbs[user] = self._make(user)
        return self._tbs[user]

    def call_tool(self, user, name, args, ident=""):
        tb = self.toolbox_for(user)
        with tb.erp.lock:
            tb.erp._clock = self.now()
            out = tb.call(name, args)
        return out

    def validate(self, wf):
        return validate(wf)

    def context(self, run: dict) -> dict:
        trig = next(n["id"] for n in run["workflow"]["nodes"] if n["type"] == "trigger")
        outs = {nid: r["output"] for nid, r in run["nodes"].items() if r["status"] in ("done", "warning", "error")}
        t = self.now()
        return {"nodes": outs, "trigger": outs.get(trig, {}), "params": run.get("params", {}), "today": t.date().isoformat(),
                "now": t.strftime("%Y-%m-%d %H:%M"), "run": {"id": run["id"]}}

    def start(self, wf: dict, trigger_data: dict | None = None, params: dict | None = None, rid: str | None = None) -> dict:
        problems, _ = validate(wf)
        if problems:
            raise FlowError("This workflow cannot run yet: " + " ".join(problems[:4]), "Fix these first.")
        vals = clean_params(wf, params)
        trig = next(n for n in wf["nodes"] if n["type"] == "trigger")
        run = {"id": rid or ("run-" + format(int(time.time() * 1000) % 10**9, "x")), "workflow_id": wf.get("id"),
               "workflow_name": wf.get("name"), "workflow": copy.deepcopy(wf), "status": "running",
               "trigger_kind": trig.get("config", {}).get("kind", "manual"), "trigger_data": trigger_data or {}, "params": vals,
               "started": self.now().isoformat(), "wall_t0": time.time(), "finished": None, "error": None, "waiting_for": None,
               "edges_taken": [], "log": [], "current": None,
               "nodes": {n["id"]: {"status": "pending", "output": None, "error": None, "seconds": None} for n in wf["nodes"]}}
        self._log(run, None, "started", f"Run of “{wf.get('name', 'workflow')}”"
                  + (" with " + ", ".join(f"{k}={v}" for k, v in vals.items()) if vals else ""))
        self._execute(run, trig["id"])
        return run

    def next_ready(self, run: dict):
        wf, recs = run["workflow"], run["nodes"]
        taken = {(a, b, p) for a, b, p in run["edges_taken"]}
        order = sorted(wf["nodes"], key=lambda n: (n.get("x", 0), n.get("y", 0)))
        changed = True
        while changed:
            changed = False
            for n in order:
                if recs[n["id"]]["status"] != "pending" or n["type"] == "trigger":
                    continue
                inc = [e for e in wf["edges"] if e["to"] == n["id"]]
                settled = all(recs[e["from"]]["status"] in FINISHED for e in inc)
                if settled and not any((e["from"], e["to"], e.get("port", "out")) in taken for e in inc):
                    recs[n["id"]]["status"] = "skipped"
                    changed = True
        for n in order:
            if recs[n["id"]]["status"] != "pending" or n["type"] == "trigger":
                continue
            inc = [e for e in wf["edges"] if e["to"] == n["id"]]
            if inc and all(recs[e["from"]]["status"] in FINISHED for e in inc):
                return n["id"]
        return None

    def step(self, run: dict) -> dict:
        if run["status"] != "running":
            return run
        nid = self.next_ready(run)
        if nid is None:
            run["status"], run["finished"] = "done", self.now().isoformat()
            run["wall_seconds"] = round(time.time() - run["wall_t0"], 2)
            self._log(run, None, "done", "Run finished")
        else:
            self._execute(run, nid)
        self.on_save(run)
        return run

    def run_until_pause(self, run: dict, max_nodes: int = 60) -> dict:
        for _ in range(max_nodes):
            if run["status"] != "running":
                break
            self.step(run)
        return run

    def _execute(self, run: dict, nid: str):
        node = next(n for n in run["workflow"]["nodes"] if n["id"] == nid)
        rec = run["nodes"][nid]
        with self.lock:
            rec.update(status="running", started=self.now().isoformat(), error=None)
            run["current"] = nid
        t0 = time.perf_counter()
        try:
            res = HANDLERS[node["type"]](self, run, node, self.context(run))
        except FlowError as e:
            res = Result("error", {"ok": False, "error": str(e), "next_step": e.next_step}, port="error", text=f"{e} {e.next_step}".strip())
        except Exception as e:  # noqa: BLE001
            res = Result("error", {"ok": False, "error": f"{type(e).__name__}: {e}"[:600], "next_step": "Try again."},
                         port="error", text=f"{type(e).__name__}: {str(e)[:200]}")
        with self.lock:
            rec.update(status=res.status, output=res.output, inputs=res.inputs, meta=res.meta, summary=res.text,
                       seconds=round(time.perf_counter() - t0, 3), port=res.port)
            run["current"] = None
        if res.status == "error":
            rec["error"] = res.output.get("error") or res.text
        self._log(run, nid, res.status, res.text)
        stop_on_warning = node.get("config", {}).get("stop_on_warning", True)
        if res.status == "waiting":
            run["status"], run["waiting_for"] = "waiting", res.waiting
            return
        if res.status == "warning" and stop_on_warning:
            res.port = "error"
        if res.status == "error" or (res.status == "warning" and stop_on_warning):
            exits = [e for e in run["workflow"]["edges"] if e["from"] == nid and e.get("port", "out") == res.port]
            if not exits:
                run["status"], run["finished"] = "failed", self.now().isoformat()
                run["wall_seconds"] = round(time.time() - run["wall_t0"], 2)
                run["error"] = f"{node.get('title', nid)}: {rec['error'] or res.text}"
                self._log(run, None, "failed", run["error"])
                return
        rec["port"] = res.port
        for e in run["workflow"]["edges"]:
            if e["from"] == nid and e.get("port", "out") == res.port:
                run["edges_taken"].append([e["from"], e["to"], e.get("port", "out")])

    def resume(self, run: dict) -> dict:
        if run["status"] != "waiting":
            return run
        w = run["waiting_for"]
        run["nodes"][w["node"]].update(status="pending", waited=True)
        run["status"], run["waiting_for"] = "running", None
        self._execute(run, w["node"])
        self.on_save(run)
        return run

    def _log(self, run, nid, event, text):
        with self.lock:
            run["log"].append({"t": self.now().strftime("%H:%M"), "wall": round(time.time() - run["wall_t0"], 2),
                               "node": nid, "event": event, "text": text})


def clean_params(wf: dict, given: dict | None) -> dict:
    out = {}
    for p in wf.get("params", []) or []:
        v = (given or {}).get(p["name"], p.get("default"))
        t = p.get("type", "text")
        if t == "number" and v not in (None, ""):
            try:
                v = float(v)
                v = int(v) if v.is_integer() else v
            except (TypeError, ValueError):
                raise FlowError(f"Parameter '{p.get('label', p['name'])}' must be a number, got {v!r}.", "Type a number.")
        if t == "boolean":
            v = v if isinstance(v, bool) else str(v).lower() in ("true", "yes", "1", "on")
        if t == "choice" and p.get("options") and v not in p["options"]:
            raise FlowError(f"Parameter '{p.get('label', p['name'])}' must be one of {p['options']}.", "Pick one.")
        out[p["name"]] = v
    return out


def cost_of(run: dict) -> dict:
    """Tokens, US$ and model seconds of a run, from every node's meta."""
    t = {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "model_calls": 0, "tool_calls": 0}
    for nid, r in run["nodes"].items():
        m = r.get("meta") or {}
        t["tokens_in"] += m.get("tokens_in", 0) or 0
        t["tokens_out"] += m.get("tokens_out", 0) or 0
        t["usd"] += m.get("usd", 0.0) or 0.0
    t["usd"] = round(t["usd"], 6)
    return t
