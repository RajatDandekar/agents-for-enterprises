"""The Workflow Studio engine: run a workflow (nodes + edges) against one player's Northbridge.

A workflow is JSON (see SPEC.md): a trigger node, tool nodes, conditions, approvals, LLM and agent nodes, messages
and "set" nodes, joined by edges. This file is everything that runs it, in four parts:

    1. Templates     "{{nodes.pr.request_no}}" -> "PR/2026/04417"   (fill)
    2. The store     workflows, runs and chats, as plain JSON          (Store)
    3. Node types    one small function per type                       (TRIGGER ... SET)
    4. The run loop  start -> step -> step ... -> done | waiting | failed   (Engine)

Every write goes through the toolbox (`toolbox_for(user)` returns `players.toolbox(pid, user)`), so the person a
node acts as, their permissions, previews (confirm), idempotency keys and receipts all hold, exactly as in chat.

    eng = Engine(toolbox_for=lambda user, names=None: players.toolbox(pid, user, names), store=Store(), pid=pid)
    run = eng.start(workflow)          # the trigger has run
    eng.run_until_pause(run)           # -> run["status"] is "done", "failed" or "waiting" (for an approval)
    eng.approve(run); eng.run_until_pause(run)
"""
from __future__ import annotations

import ast
import copy
import datetime as dt
import json
import os
import pathlib
import re
import threading
import time

from ...llm import LLM
from ...toolbox import SPECS

HERE = pathlib.Path(__file__).parent
PEOPLE = {"ECLARKE": "Emma Clarke", "DOKAFOR": "Daniel Okafor", "ATANAKA": "Aiko Tanaka"}
ROLES = {"ECLARKE": "purchase executive", "DOKAFOR": "purchase manager", "ATANAKA": "stores"}
DEFAULT_MODEL = os.environ.get("STUDIO_MODEL", "gemini:gemini-3.8-flash")
NODE_TYPES = ["trigger", "tool", "condition", "approval", "llm", "agent", "message", "set"]
TRIGGER_KINDS = ["manual", "schedule", "event", "chat", "form"]
PORTS = {"condition": ["true", "false"], "approval": ["out", "rejected"]}  # every other type: "out"
FINISHED = {"done", "warning", "error", "skipped"}


class StudioError(Exception):
    """A problem a student can fix: the message says what is wrong, next_step says what to do."""

    def __init__(self, message: str, next_step: str = ""):
        super().__init__(message)
        self.next_step = next_step


# =====================================================================================================================
# 1. Templates: {{ ... }} in a field is a tiny expression over the outputs so far
# =====================================================================================================================
TEMPLATE = re.compile(r"\{\{(.*?)\}\}", re.S)


def num(v) -> str:
    """6600 -> "6,600"; 285600 -> "285,600"."""
    return f"{int(round(float(v))):,}"

FUNCS = {"min": min, "max": max, "round": round, "int": int, "float": float, "str": str, "len": len, "abs": abs,
         "upper": lambda s: str(s).upper(), "lower": lambda s: str(s).lower(),
         "money": lambda v: "£" + num(v), "num": num,
         "add_days": lambda d, n: (dt.date.fromisoformat(str(d)[:10]) + dt.timedelta(days=int(n))).isoformat()}
NAMES = {"true": True, "false": False, "null": None, "True": True, "False": False, "None": None}
BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
          ast.Div: lambda a, b: a / b, ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b}
CMPOPS = {ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b, ast.Lt: lambda a, b: a < b,
          ast.LtE: lambda a, b: a <= b, ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
          ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}


def _get(obj, key, where: str):
    """One step of a path, with an error that names what IS there."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        raise StudioError(f"{where} has no field '{key}' (it has: {', '.join(map(str, obj)) or 'nothing yet'}).",
                          "Pick a field from the output picker, or run the earlier node first.")
    if isinstance(obj, list):
        try:
            return obj[int(key)]
        except (ValueError, IndexError):
            raise StudioError(f"{where} has no item [{key}] (it has {len(obj)}).", "Check the list is not empty.")
    raise StudioError(f"{where} is {obj!r}, not something with fields.", "Check the path.")


def evaluate(expr: str, ctx: dict):
    """Evaluate one expression such as `nodes.stock.reorder_level * 3`. Only paths, numbers, strings, arithmetic,
    comparisons, and/or/not and the FUNCS above are allowed; anything else is refused."""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError:
        raise StudioError(f"Cannot read the expression '{expr.strip()}'.", "Write a path like nodes.pr.request_no.")

    def ev(n, where=""):
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
        raise StudioError(f"'{ast.unparse(n)}' is not allowed in a template.",
                          "Use paths, numbers, + - * /, comparisons, and/or/not, min/max/round/int/len.")

    try:
        return ev(tree)
    except StudioError:
        raise
    except Exception as e:  # e.g. "abc" * {} or a division by zero
        raise StudioError(f"'{expr.strip()}' failed: {e}.", "Check the values it uses in the earlier nodes' outputs.")


def fill(value, ctx: dict):
    """Fill templates in a field (recursively for dicts and lists).
    A field that is exactly one {{ ... }} keeps the value's type; otherwise each {{ ... }} becomes text."""
    if isinstance(value, dict):
        return {k: fill(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [fill(v, ctx) for v in value]
    if not isinstance(value, str) or "{{" not in value:
        return value
    whole = TEMPLATE.fullmatch(value.strip())
    if whole:
        return evaluate(whole.group(1), ctx)

    def text(m):
        v = evaluate(m.group(1), ctx)
        return json.dumps(v, default=str) if isinstance(v, (dict, list)) else ("" if v is None else str(v))

    return TEMPLATE.sub(text, value)


def references(value) -> set[str]:
    """Which nodes a field reads from: {{nodes.pr.request_no}} -> {"pr"}. Used by validate()."""
    found = set()
    for s in re.findall(r"\{\{(.*?)\}\}", json.dumps(value)):
        found |= set(re.findall(r"\bnodes\.([A-Za-z_][A-Za-z0-9_]*)", s))
    return found


# =====================================================================================================================
# 2. The store: workflows, runs and chat histories, per player, as JSON (and files, if STUDIO_DATA is set)
# =====================================================================================================================
class Store:
    def __init__(self, folder: str | None = None):
        self.folder = pathlib.Path(folder) if folder else (pathlib.Path(os.environ["STUDIO_DATA"])
                                                           if os.environ.get("STUDIO_DATA") else None)
        self.data: dict[str, dict] = {}  # pid -> {"workflows": {}, "runs": {}, "chats": {}}
        self._lock = threading.RLock()

    def _p(self, pid: str) -> dict:
        with self._lock:
            if pid not in self.data:
                self.data[pid] = {"workflows": {}, "runs": {}, "chats": {}}
                f = self.folder / f"{pid}.json" if self.folder else None
                if f and f.exists():
                    self.data[pid] = json.loads(f.read_text())
            return self.data[pid]

    def _flush(self, pid: str):
        if self.folder:
            self.folder.mkdir(parents=True, exist_ok=True)
            tmp = self.folder / f"{pid}.json.tmp"
            tmp.write_text(json.dumps(self.data[pid], default=str))
            tmp.replace(self.folder / f"{pid}.json")

    # workflows
    def workflows(self, pid):
        return list(self._p(pid)["workflows"].values())

    def workflow(self, pid, wid):
        return self._p(pid)["workflows"].get(wid)

    def save_workflow(self, pid, wf):
        with self._lock:
            self._p(pid)["workflows"][wf["id"]] = wf
            self._flush(pid)
        return wf

    def delete_workflow(self, pid, wid):
        with self._lock:
            self._p(pid)["workflows"].pop(wid, None)
            self._p(pid)["chats"].pop(wid, None)
            self._flush(pid)

    # runs
    def new_run_id(self, pid):
        return f"run-{len(self._p(pid)['runs']) + 1:04d}"

    def runs(self, pid, workflow_id=None):
        rs = [r for r in self._p(pid)["runs"].values() if not workflow_id or r["workflow_id"] == workflow_id]
        return sorted(rs, key=lambda r: r["id"], reverse=True)

    def run(self, pid, rid):
        return self._p(pid)["runs"].get(rid)

    def save_run(self, pid, run):
        with self._lock:
            self._p(pid)["runs"][run["id"]] = run
            self._flush(pid)
        return run

    # chats (the conversation with a chat-triggered workflow, e.g. your own agent)
    def chat(self, pid, wid):
        return self._p(pid)["chats"].get(wid, [])

    def save_chat(self, pid, wid, history):
        with self._lock:
            self._p(pid)["chats"][wid] = history
            self._flush(pid)

    def clear(self, pid, runs=True):
        with self._lock:
            if runs:
                self._p(pid)["runs"] = {}
                self._p(pid)["chats"] = {}
            self._flush(pid)


class StudioLLM(LLM):
    """ledgerline.llm.LLM with its cassette kept in studio/cassettes/, so the Studio's LLM nodes replay with no key.
    If Gemini's own API cannot answer (no key, or no credits left: HTTP 402), the same Gemini model is called
    through OpenRouter (google/<model>) when OPENROUTER_API_KEY is set. Replies are recorded under the model name
    the node chose, so a cassette replays whichever road the reply came by."""

    gemini_down = False  # set once Gemini's own API said 402/429, for the rest of the process

    def _path(self):
        return pathlib.Path(os.environ.get("STUDIO_CASSETTES", HERE / "cassettes")) / f"{self.cassette}.jsonl"

    def _can_detour(self):
        return self.provider == "gemini" and bool(os.environ.get("OPENROUTER_API_KEY"))

    def _has_key(self):
        return super()._has_key() or self._can_detour()

    def _live(self, messages, tools, response_format, **kw):
        if self._can_detour() and (StudioLLM.gemini_down or not super()._has_key()):
            return self._detour(messages, tools, response_format, **kw)
        try:
            return super()._live(messages, tools, response_format, **kw)
        except RuntimeError as e:
            if self._can_detour() and any(c in str(e) for c in ("402", "RESOURCE_EXHAUSTED", "429")):
                StudioLLM.gemini_down = True
                return self._detour(messages, tools, response_format, **kw)
            raise

    def _detour(self, messages, tools, response_format, **kw):
        alt = LLM("openrouter:google/" + self.model_id, mode="live", temperature=self.temperature,
                  max_tokens=self.max_tokens)
        r = alt._live(messages, tools, response_format, **kw)
        r.model = self.model
        return r


# =====================================================================================================================
# 3. Node types. Each takes (engine, run, node, ctx) and returns a Result.
# =====================================================================================================================
class Result:
    def __init__(self, status="done", output=None, port="out", text="", inputs=None, waiting=None, meta=None):
        self.status, self.output, self.port, self.text = status, output if output is not None else {}, port, text
        self.inputs, self.waiting, self.meta = inputs, waiting, meta


def summary(out: dict) -> str:
    """A one-line receipt for the node card and the run log."""
    if not isinstance(out, dict):
        return str(out)[:120]
    if out.get("ok") is False:
        return out.get("error", "failed")
    if "preview" in out:
        p = out["preview"]
        v = p.get("gross_value", p.get("estimated_value"))
        return "Preview only, nothing saved" + (f" · £{num(v)}" if isinstance(v, (int, float)) else "")
    main = next((out[k] for k in ("grn_no", "po_no", "request_no") if out.get(k)), None)  # the document it made
    parts = [str(x) for x in (main, out.get("status")) if x]
    if "cover_days" in out and out.get("item_code"):
        parts = [f"{out['item_code']}: {num(out.get('free_total', 0))} free, {out['cover_days']} days of cover"]
    if out.get("items") and isinstance(out["items"], list):
        parts = [f"{len(out['items'])} found · {out['items'][0].get('item_code')}"]
    if out.get("queued"):
        parts = [f"Sent to {out.get('to')}"]
    if "reply" in out:
        parts = [str(out["reply"])[:110]]
    if "text" in out and len(out) == 1:
        parts = [str(out["text"])[:110]]
    if out.get("already_done"):
        parts.append("(already done)")
    return " · ".join(parts) or ", ".join(f"{k}: {v}" for k, v in list(out.items())[:3])[:120]


def _warnings(out: dict) -> str:
    w = out.get("warning") or out.get("warnings")
    return "; ".join(w) if isinstance(w, list) else (w or "")


def TRIGGER(eng, run, node, ctx):
    """Start the run with its data. Each kind gets its data in its own way (SPEC §1, trigger kinds)."""
    cfg, data = node.get("config", {}), dict(run.get("trigger_data") or {})
    kind = cfg.get("kind", "manual")
    if kind == "manual":
        return Result(output={**cfg.get("data", {}), **data}, text="Started by hand")
    if kind == "form":
        out = {}
        for f in cfg.get("fields", []):
            v = data.get(f["name"], f.get("default"))
            if v in (None, ""):
                raise StudioError(f"The form field '{f.get('label', f['name'])}' is empty.", "Fill in the form.")
            if f.get("type") == "number":
                try:
                    v = int(v) if float(v).is_integer() else float(v)
                except (TypeError, ValueError):
                    raise StudioError(f"'{f.get('label', f['name'])}' should be a number, got {v!r}.", "Type a number.")
            out[f["name"]] = v
        return Result(output=out, text="Form: " + ", ".join(f"{k}={v}" for k, v in out.items()))
    if kind == "chat":
        if not data.get("message"):
            raise StudioError("A chat workflow starts with a message.", "Type a message in the chat panel.")
        return Result(output={"message": data["message"], "history": data.get("history", [])},
                      text=f"“{data['message'][:80]}”")
    if kind == "schedule":
        when = f"every {cfg.get('every', 'day')} at {cfg.get('at', '09:00')}"
        return Result(output={"fired_at": f"{ctx['today']} {cfg.get('at', '09:00')}", "schedule": when},
                      text=f"Scheduled: {when}")
    if kind == "event":  # stock_below_reorder: look at each watched item through the toolbox
        tb = eng.toolbox_for(cfg.get("as", "ECLARKE"))
        items = [data["item_code"]] if data.get("item_code") else cfg.get("item_codes", [])
        looked = []
        for code in items:
            st = tb.call("check_stock", {"item_code": code})
            if not st.get("ok"):
                raise StudioError(f"Could not check stock of {code}: {st.get('error')}", st.get("next_step", ""))
            looked.append(f"{code} {num(st['free_total'])}/{num(st['reorder_level'])}")
            if st.get("below_reorder"):
                return Result(output={"fired": True, "event": "stock_below_reorder", "item_code": code,
                                      "free": st["free_total"], "on_order": st["on_order_total"],
                                      "reorder_level": st["reorder_level"], "cover_days": st["cover_days"]},
                              text=f"{code} is below its reorder level ({num(st['free_total'])} < {num(st['reorder_level'])})")
        return Result(output={"fired": False, "event": "stock_below_reorder", "checked": looked}, port="none",
                      text="No watched item is below its reorder level; nothing to do")
    raise StudioError(f"Unknown trigger kind '{kind}'.", f"Use one of {TRIGGER_KINDS}.")


def _specs(eng, user="ECLARKE") -> dict:
    """The tools this engine's toolbox offers: purchasing's SPECS, or a module kit's own toolbox specs (L6, A6)."""
    try:
        return getattr(eng.toolbox_for(user), "specs", None) or SPECS
    except Exception:
        return SPECS


def TOOL(eng, run, node, ctx):
    """Call one toolbox tool as the chosen person. confirm comes from the node's Commit switch, never a template."""
    cfg = node.get("config", {})
    name = cfg.get("tool")
    specs = _specs(eng, cfg.get("as", "ECLARKE"))
    if name not in specs:
        raise StudioError(f"There is no tool '{name}'.", "Pick a tool from the palette.")
    args = {k: v for k, v in fill(cfg.get("args", {}), ctx).items() if v not in (None, "")}
    if "confirm" in specs[name].spec["input_schema"].get("properties", {}):
        args["confirm"] = bool(cfg.get("confirm", False))
    else:
        args.pop("confirm", None)
    out = eng.toolbox_for(cfg.get("as", "ECLARKE")).call(name, args)
    if not out.get("ok"):
        return Result("error", out, port="error", inputs=args,
                      text=f"{out.get('error', 'failed')} {out.get('next_step', '')}".strip())
    warn = _warnings(out)
    if warn:
        return Result("warning", out, inputs=args, text=f"Warning: {warn}")
    return Result(output=out, inputs=args, text=summary(out))


def CONDITION(eng, run, node, ctx):
    """Branch: leave by the "true" or the "false" port."""
    expr = str(node.get("config", {}).get("if", "")).strip()
    if not expr:
        raise StudioError("This condition has no test.", "Write one, e.g. {{ nodes.stock.below_reorder }}.")
    inner = TEMPLATE.fullmatch(expr)
    value = evaluate(inner.group(1) if inner else expr, ctx)
    branch = "true" if value else "false"
    return Result(output={"branch": branch, "value": value}, port=branch, text=f"{expr} → {branch}")


APPROVED = {"AP", "RL", "CL"}  # approved, released, closed: someone with the authority signed


def APPROVAL(eng, run, node, ctx):
    """Wait for a signature. Reads the document's real status from Ledgerline; if it is waiting, the run pauses here."""
    cfg = node.get("config", {})
    doc = str(fill(cfg.get("doc_no", ""), ctx) or "").strip()
    if not doc:
        raise StudioError("This approval has no document.", "Set doc_no, e.g. {{nodes.pr.request_no}}.")
    args = {"request_no": doc} if doc.upper().startswith("PR") else {"po_no": doc}
    st = eng.toolbox_for(cfg.get("as", "ECLARKE")).call("order_status", args)
    if not st.get("ok"):
        return Result("error", st, port="error", text=st.get("error", ""))
    code, rec = st.get("status_code"), run["nodes"][node["id"]]
    approver = st.get("approver") or (st.get("approval") or {}).get("approver") or cfg.get("approver", "DOKAFOR")
    out = {"doc_no": doc, "status": st.get("status"), "status_code": code, "approved_by": st.get("approved_by"),
           "approver": approver, "waited": bool(rec.get("waited"))}
    if code in APPROVED:
        who = PEOPLE.get(st.get("approved_by"), st.get("approved_by") or "Ledgerline")
        note = f"approved by {who}" + ("" if rec.get("waited") else " (no wait: within the limit, or signed already)")
        return Result(output=out, text=f"{doc} {note}")
    if code == "PA":
        return Result("waiting", out, waiting={"node": node["id"], "doc_no": doc, "approver": approver,
                                               "approver_name": PEOPLE.get(approver, approver)},
                      text=f"Waiting for {PEOPLE.get(approver, approver)} to approve {doc}")
    if code == "RJ":
        return Result("error", {**out, "ok": False, "error": f"{doc} was rejected."}, port="rejected",
                      text=f"{doc} was rejected by {PEOPLE.get(approver, approver)}")
    return Result("error", {**out, "ok": False, "error": f"{doc} is {st.get('status')}: nobody will be asked to sign it.",
                            "next_step": st.get("warning") or "Check the document with order_status."},
                  port="error", text=f"{doc} is {st.get('status')}; it will never reach an approver")


def LLM_NODE(eng, run, node, ctx):
    """One model call: a prompt template in, text (or a JSON object with the fields you asked for) out."""
    cfg = node.get("config", {})
    prompt = fill(cfg.get("prompt", ""), ctx)
    if not str(prompt).strip():
        raise StudioError("The prompt is empty.", "Write a prompt; use {{ }} to put earlier outputs in it.")
    messages = [{"role": "system", "content": cfg["system"]}] if cfg.get("system") else []
    want_json = cfg.get("output", "text") == "json"
    if want_json:
        keys = ", ".join(cfg.get("fields", [])) or "the fields the prompt asks for"
        prompt = f"{prompt}\n\nReply with one JSON object only, no other text, with these keys: {keys}."
    messages.append({"role": "user", "content": str(prompt)})
    r = eng.llm_for(cfg.get("model") or DEFAULT_MODEL).chat(messages)
    meta = {"model": r.model, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
            "replayed": r.replayed, "cost_inr": r.cost_inr}
    text = (r.content or "").strip()
    if not want_json:
        return Result(output={"text": text}, inputs={"prompt": prompt}, meta=meta, text=text[:110])
    m = re.search(r"\{.*\}", text, re.S)
    try:
        out = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        out = None
    if not isinstance(out, dict):
        raise StudioError(f"The model did not reply with JSON: {text[:160]!r}", "Make the prompt ask for JSON only.")
    missing = [k for k in cfg.get("fields", []) if k not in out]
    if missing:
        raise StudioError(f"The model's JSON has no {', '.join(missing)}.", "Name those fields in the prompt.")
    return Result(output=out, inputs={"prompt": prompt}, meta=meta,
                  text=", ".join(f"{k}: {v}" for k, v in out.items())[:120])


AGENT_SYSTEM = """{instructions}

You work at Northbridge Cycles, Manchester, inside Ledgerline ERP, for {name} ({user}, {role}). Today is {today}.
Use the tools to do what is asked. If a tool returns ok=false, read its next_step and follow it.
{commit_rule}
Report the status the tools give you, in plain words."""


def AGENT(eng, run, node, ctx):
    """Build-your-own agent: instructions + a chosen subset of tools + a model, in the L5 loop."""
    cfg = node.get("config", {})
    user = cfg.get("as", "ECLARKE")
    names = [t for t in cfg.get("tools", []) if t in _specs(eng, user)]
    if not names:
        raise StudioError("This agent has no tools.", "Tick at least one tool in the agent's panel.")
    tb = eng.toolbox_for(user, names)
    may_commit = bool(cfg.get("may_commit", False))
    system = AGENT_SYSTEM.format(
        instructions=cfg.get("instructions", "You are a helpful purchasing assistant."), name=PEOPLE.get(user, user),
        user=user, role=ROLES.get(user, ""), today=ctx["today"],
        commit_rule=("Preview every write first (confirm=false), show it, and commit (confirm=true) only after the "
                     "user says yes." if may_commit else
                     "You may only preview writes (confirm=false); tell the user a person must commit them."))
    question = fill(cfg.get("input", "{{ trigger.message }}"), ctx)
    history = ctx.get("trigger", {}).get("history", []) if isinstance(ctx.get("trigger"), dict) else []
    messages = [{"role": "system", "content": system}, *history, {"role": "user", "content": str(question)}]
    llm, calls, reply = eng.llm_for(cfg.get("model") or DEFAULT_MODEL), [], None
    max_steps = int(cfg.get("max_steps", 12))
    for _ in range(max_steps):
        r = llm.chat(messages, tools=tb.schemas())
        messages.append(r.message())
        if not r.tool_calls:
            reply = r.content or ""
            break
        for tc in r.tool_calls:
            args = dict(tc.arguments or {})
            if not may_commit and "confirm" in args:
                args["confirm"] = False  # the node's switch wins over the model
            out = tb.call(tc.name, args)
            calls.append({"tool": tc.name, "args": args, "ok": bool(out.get("ok")), "summary": summary(out)})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)})
    if reply is None:
        reply = f"(stopped after {max_steps} steps without an answer)"
    t = llm.totals()
    return Result(output={"reply": reply, "tool_calls": calls, "steps": len(calls)}, inputs={"input": question},
                  meta={"model": llm.model, **t}, text=reply[:110])


def MESSAGE(eng, run, node, ctx):
    """send_message through the toolbox, as the chosen sender."""
    cfg = node.get("config", {})
    to, text = fill(cfg.get("to", ""), ctx), fill(cfg.get("text", ""), ctx)
    out = eng.toolbox_for(cfg.get("as", "ECLARKE")).call("send_message", {"to": to, "text": text})
    if not out.get("ok"):
        return Result("error", out, port="error", inputs={"to": to, "text": text}, text=out.get("error", ""))
    return Result(output={**out, "text": text}, inputs={"to": to, "text": text}, text=f"To {to}: {text[:90]}")


def SET(eng, run, node, ctx):
    """Compute named values from earlier outputs, e.g. quantity = {{ trigger.reorder_level * 3 }}."""
    values = fill(node.get("config", {}).get("values", {}), ctx)
    return Result(output=values, text=", ".join(f"{k} = {v}" for k, v in values.items())[:120])


HANDLERS = {"trigger": TRIGGER, "tool": TOOL, "condition": CONDITION, "approval": APPROVAL, "llm": LLM_NODE,
            "agent": AGENT, "message": MESSAGE, "set": SET}


# =====================================================================================================================
# 4. The run loop
# =====================================================================================================================
GMT = dt.timezone(dt.timedelta(hours=5, minutes=30))


def _now():
    return dt.datetime.now(GMT).isoformat(timespec="seconds")


class Engine:
    def __init__(self, toolbox_for, store: Store | None = None, pid: str = "local", llm_for=None):
        """toolbox_for(user, names=None) -> Toolbox for that person in this player's Northbridge."""
        self._make_toolbox, self._toolboxes = toolbox_for, {}
        self.store = store or Store()
        self.pid = pid
        self.llm_for = llm_for or (lambda model: StudioLLM(model, cassette="studio"))

    def toolbox_for(self, user: str, names: list[str] | None = None):
        """The toolbox as one person (optionally only some tools). Made once per engine and reused."""
        key = (user, tuple(names or ()))
        if key not in self._toolboxes:
            self._toolboxes[key] = self._make_toolbox(user, names) if names else self._make_toolbox(user)
        return self._toolboxes[key]

    # ---------------------------------------------------------------- checking a workflow before it runs
    def validate(self, wf: dict) -> list[str]:
        problems, nodes = [], wf.get("nodes", [])
        ids = [n.get("id") for n in nodes]
        by_id = {n.get("id"): n for n in nodes}
        for i in set(ids):
            if ids.count(i) > 1:
                problems.append(f"Two nodes are called '{i}'.")
        for n in nodes:
            nid, typ, cfg = n.get("id"), n.get("type"), n.get("config", {})
            if not isinstance(nid, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nid):
                problems.append(f"Node id {nid!r} must be letters, digits and _ (it is used in templates).")
            if typ not in HANDLERS:
                problems.append(f"Node {nid}: unknown type '{typ}'.")
                continue
            if typ == "tool" and cfg.get("tool") not in _specs(self, cfg.get("as", "ECLARKE")):
                problems.append(f"Node {nid}: tool '{cfg.get('tool')}' does not exist.")
            if typ == "trigger" and cfg.get("kind", "manual") not in TRIGGER_KINDS:
                problems.append(f"Node {nid}: trigger kind '{cfg.get('kind')}' is not one of {TRIGGER_KINDS}.")
            if typ == "agent":
                bad = [t for t in cfg.get("tools", []) if t not in _specs(self, cfg.get("as", "ECLARKE"))]
                if bad:
                    problems.append(f"Node {nid}: agent tools {bad} do not exist.")
            for who in [cfg.get("as"), cfg.get("approver")]:
                if who and who not in PEOPLE:
                    problems.append(f"Node {nid}: '{who}' is not one of {list(PEOPLE)}.")
            for ref in references(cfg):
                if ref not in by_id:
                    problems.append(f"Node {nid} reads nodes.{ref}, but there is no node '{ref}'.")
        triggers = [n for n in nodes if n.get("type") == "trigger"]
        if len(triggers) != 1:
            problems.append(f"A workflow needs exactly one trigger (it has {len(triggers)}).")
        for e in wf.get("edges", []):
            if e.get("from") not in by_id or e.get("to") not in by_id:
                problems.append(f"An edge joins {e.get('from')} → {e.get('to')}, but one of them does not exist.")
                continue
            typ = by_id[e["from"]].get("type")
            if e.get("port", "out") not in PORTS.get(typ, ["out"]) + ["error"]:
                problems.append(f"{e['from']} has no '{e.get('port')}' exit.")
            if by_id[e["to"]].get("type") == "trigger":
                problems.append(f"Nothing can lead into the trigger ({e['from']} → {e['to']}).")
        if not problems and self._has_cycle(wf):
            problems.append("The workflow has a loop; a workflow must flow one way.")
        return problems

    @staticmethod
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

    # ---------------------------------------------------------------- the run
    def start(self, wf: dict, trigger_data: dict | None = None) -> dict:
        """Freeze a copy of the workflow, save the run, and run the trigger."""
        problems = self.validate(wf)
        if problems:
            raise StudioError("This workflow cannot run yet: " + " ".join(problems), "Fix these in the canvas.")
        trig = next(n for n in wf["nodes"] if n["type"] == "trigger")
        run = {"id": self.store.new_run_id(self.pid), "workflow_id": wf.get("id"), "workflow_name": wf.get("name"),
               "workflow": copy.deepcopy(wf), "status": "running", "trigger_kind": trig.get("config", {}).get("kind", "manual"),
               "trigger_data": trigger_data or {}, "started": _now(), "finished": None, "error": None,
               "waiting_for": None, "edges_taken": [], "log": [],
               "nodes": {n["id"]: {"status": "pending", "output": None, "error": None, "seconds": None}
                         for n in wf["nodes"]}}
        self._log(run, None, "started", f"Run of “{wf.get('name', 'workflow')}”")
        self._execute(run, trig["id"])
        return self.store.save_run(self.pid, run)

    def context(self, run: dict) -> dict:
        """What templates can read: the outputs so far, the trigger's data, today's date in the sandbox."""
        trig = next(n["id"] for n in run["workflow"]["nodes"] if n["type"] == "trigger")
        outs = {nid: r["output"] for nid, r in run["nodes"].items() if r["status"] in ("done", "warning", "error")}
        try:
            today = self.toolbox_for("ECLARKE").erp.today
        except Exception:
            today = "2026-10-26"
        return {"nodes": outs, "trigger": outs.get(trig, {}), "today": today, "run": {"id": run["id"]}}

    def next_ready(self, run: dict) -> str | None:
        """The first node (left to right) whose inputs have all settled and at least one of which was taken.
        Nodes that can no longer be reached are marked skipped on the way."""
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
                    recs[n["id"]]["status"] = "skipped"  # no edge leads here on this run (or nothing joins it)
                    changed = True
        for n in order:
            if recs[n["id"]]["status"] != "pending" or n["type"] == "trigger":
                continue
            inc = [e for e in wf["edges"] if e["to"] == n["id"]]
            if inc and all(recs[e["from"]]["status"] in FINISHED for e in inc):
                return n["id"]
        return None

    def step(self, run: dict) -> dict:
        """Run one more node. Returns the run (saved)."""
        if run["status"] != "running":
            return run
        nid = self.next_ready(run)
        if nid is None:
            run["status"], run["finished"] = "done", _now()
            self._log(run, None, "done", "Run finished")
        else:
            self._execute(run, nid)
        return self.store.save_run(self.pid, run)

    def run_until_pause(self, run: dict, max_nodes: int = 200) -> dict:
        for _ in range(max_nodes):
            if run["status"] != "running":
                break
            self.step(run)
        return run

    def _execute(self, run: dict, nid: str):
        node = next(n for n in run["workflow"]["nodes"] if n["id"] == nid)
        rec = run["nodes"][nid]
        rec.update(status="running", started=_now(), error=None)
        t0 = time.perf_counter()
        try:
            res = HANDLERS[node["type"]](self, run, node, self.context(run))
        except StudioError as e:
            res = Result("error", {"ok": False, "error": str(e), "next_step": e.next_step}, port="error",
                         text=f"{e} {e.next_step}".strip())
        except Exception as e:  # a model or network failure must not lose the run
            res = Result("error", {"ok": False, "error": f"{type(e).__name__}: {e}"[:600],
                                   "next_step": "Try again; if it repeats, check the node's settings."},
                         port="error", text=f"{type(e).__name__}: {str(e)[:200]}")
        rec.update(status=res.status, output=res.output, inputs=res.inputs, meta=res.meta, summary=res.text,
                   seconds=round(time.perf_counter() - t0, 3), port=res.port)
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
            if not exits:  # no error path drawn: the run stops here
                run["status"], run["finished"] = "failed", _now()
                run["error"] = f"{node.get('title', nid)}: {rec['error'] or res.text}"
                self._log(run, None, "failed", run["error"])
                return
        rec["port"] = res.port
        for e in run["workflow"]["edges"]:
            if e["from"] == nid and e.get("port", "out") == res.port:
                run["edges_taken"].append([e["from"], e["to"], e.get("port", "out")])

    # ---------------------------------------------------------------- approvals: a persisted wait
    def approve(self, run: dict, decision: str = "approve", comment: str = "") -> dict:
        """Sign the document the run waits on, AS the approver, through the toolbox (their inbox action)."""
        w = run.get("waiting_for")
        if run["status"] != "waiting" or not w:
            raise StudioError("This run is not waiting for an approval.", "")
        tb = self.toolbox_for(w["approver"])
        if w["doc_no"].upper().startswith("PR"):
            out = tb.call("approve_purchase_request", {"request_no": w["doc_no"], "decision": decision,
                                                       **({"comment": comment} if comment else {})})
        elif decision == "approve":
            out = tb.call("approve_purchase_order", {"po_no": w["doc_no"], **({"comment": comment} if comment else {})})
        else:
            raise StudioError("Orders are rejected in the approvals inbox, not here.", "Approve, or open the inbox.")
        self._log(run, w["node"], "signed", f"{w['approver_name']}: {decision} {w['doc_no']}"
                  + ("" if out.get("ok") else f" failed: {out.get('error')}"))
        if not out.get("ok"):
            self.store.save_run(self.pid, run)
            raise StudioError(out.get("error", "The approval failed."), out.get("next_step", ""))
        return self.resume(run)

    def resume(self, run: dict) -> dict:
        """Carry on after a wait: the approval node runs again and re-reads the status from Ledgerline."""
        if run["status"] != "waiting":
            return run
        w = run["waiting_for"]
        rec = run["nodes"][w["node"]]
        rec.update(status="pending", waited=True)
        run["status"], run["waiting_for"] = "running", None
        self._execute(run, w["node"])  # still unsigned? it simply waits again
        return self.store.save_run(self.pid, run)

    # ---------------------------------------------------------------- chat: talk to a chat-triggered workflow
    def chat(self, wf: dict, message: str) -> tuple[str, dict]:
        """One turn: start a run with the message and the history so far; the reply is the last agent's answer."""
        history = self.store.chat(self.pid, wf["id"])
        run = self.run_until_pause(self.start(wf, {"message": message, "history": history}))
        agents = [n["id"] for n in run["workflow"]["nodes"] if n["type"] in ("agent", "llm")
                  and run["nodes"][n["id"]]["status"] == "done"]
        out = run["nodes"][agents[-1]]["output"] if agents else {}
        reply = out.get("reply") or out.get("text") or (run.get("error") or "The workflow finished without a reply.")
        self.store.save_chat(self.pid, wf["id"], history + [{"role": "user", "content": message},
                                                          {"role": "assistant", "content": reply}])
        return reply, run

    @staticmethod
    def _log(run, nid, event, text):
        run["log"].append({"t": _now(), "node": nid, "event": event, "text": text})
