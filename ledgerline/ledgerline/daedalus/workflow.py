"""Workflows from blocks (Lecture 5, Section 5): the steps are written down in advance, and the code follows them.

    from ledgerline.daedalus.workflow import Workflow, SHIPPED_BLOCKS
    wf = Workflow(SHIPPED_BLOCKS)                         # Emma's order, step by step
    run = wf.start("Order 2,000 BAT-500 packs from Voltway on PRD-07, needed by 9 November 2026.", toolbox, llm)
    wf.go(run, toolbox, llm)                              # until it is done, stopped, failed or waiting
    run["status"]                                         # "waiting": PR/2026/04417 waits for Daniel; run is plain JSON
    ...  Daniel approves in his own inbox  ...
    wf.resume(run, toolbox, llm)                          # reads Ledgerline again, carries on from the approval step

A workflow is a list of steps. Each step is one block:
    a model step   read the request: the one place a model is used, to turn Emma's words into fields
    a tool step    one tool from the toolbox, with arguments taken from the facts found so far
    a gate         a written-down decision: stop the run here (or switch to the preferred supplier) when a check fails
    approval       read the request's status in Ledgerline: approved, carry on; waiting, save the run and stop; rejected, stop
    reply          tell Emma what happened, from the facts (no model)
Every step reads named facts (item_code, quantity, ...) and adds new ones. A step that needs a fact no earlier step
found fails and says which block to put before it. A run is a JSON document: it can wait for days.
"""
from __future__ import annotations

import copy
import json
import re
import time
import uuid

from ..llm import LLM

PREFERRED = {"BAT-500": "VC-EIN-0042"}   # the preferred-supplier table a real workflow keeps (gate option "switch")

# id: (title, kind, needs, gives, plain line)
BLOCKS = {
    "read":     ("Read the request", "model", ["text"], ["item_hint", "quantity", "supplier_hint", "cost_centre", "need_by"],
                 "One model call turns Emma's words into fields."),
    "item":     ("Find the item", "tool", ["item_hint"], ["item_code"], "find_item: the item code for her words."),
    "stock":    ("Check stock", "tool", ["item_code"], ["free", "cover_days"], "check_stock: free stock and days of cover."),
    "supplier": ("Find the supplier", "tool", ["supplier_hint"], ["supplier_code"], "find_supplier: the supplier's code."),
    "cert":     ("Check the certificate", "gate", ["supplier_code", "item_code"], ["certified"],
                 "supplier_certificates: a lithium-cell part needs a valid UN 38.3."),
    "budget":   ("Check the budget", "gate", ["cost_centre"], ["budget_left"],
                 "check_budget: stop if the cost centre is closed."),
    "request":  ("Raise the request", "tool", ["item_code", "quantity", "cost_centre", "need_by"], ["request_no", "request_status"],
                 "create_purchase_request, saved (confirm=true)."),
    "approval": ("Wait for approval", "approval", ["request_no"], ["approved_by"],
                 "Waiting? Save the run and stop until Ledgerline says APPROVED."),
    "order":    ("Create the order", "tool", ["supplier_code", "request_no"], ["po_no"],
                 "create_purchase_order from the approved request."),
    "release":  ("Release the order", "tool", ["po_no"], ["po_status"], "release_purchase_order: only now does the supplier get it."),
    "reply":    ("Tell Emma", "reply", [], [], "A short reply from the facts. No model."),
}
FIRST_BLOCK_FOR = {f: b for b, (_, _, _, gives, _) in BLOCKS.items() for f in gives}
DEFAULT_OPTS = {"retries": 1, "on_fail": "stop", "stop_days": 0}
SHIPPED_BLOCKS = [{"block": b, **DEFAULT_OPTS} for b in
                  ["read", "item", "stock", "supplier", "cert", "budget", "request", "approval", "order", "release", "reply"]]

READ_PROMPT = """Today is Monday 26 October 2026. Turn Emma's message into the fields of a purchase request.
Reply with one JSON object and nothing else:
{"is_order": true if she asks to order or reorder something, else false,
 "item": the item as she named it (a code like BAT-500 if she gave one), or null,
 "quantity": a whole number, or null,
 "supplier": the supplier's name as she wrote it, or null,
 "cost_centre": a code like PRD-07, or null,
 "need_by": the date needed as YYYY-MM-DD, or null}
Never guess a field she did not give: use null."""


def clean_blocks(blocks) -> list[dict]:
    out = []
    for b in (blocks or [])[:20]:
        if not isinstance(b, dict) or b.get("block") not in BLOCKS:
            continue
        o = {"block": b["block"]}
        o["retries"] = max(0, min(3, int(b.get("retries", DEFAULT_OPTS["retries"]) or 0)))
        o["on_fail"] = b.get("on_fail") if b.get("on_fail") in ("stop", "switch") else "stop"
        o["stop_days"] = max(0, min(120, int(b.get("stop_days", 0) or 0)))
        out.append(o)
    return out or copy.deepcopy(SHIPPED_BLOCKS)


def describe(blocks) -> list[str]:
    """What differs from the shipped workflow, in plain words."""
    names = [b["block"] for b in blocks]
    ship = [b["block"] for b in SHIPPED_BLOCKS]
    out = [f"no '{BLOCKS[b][0]}'" for b in ship if b not in names]
    out += [f"extra '{BLOCKS[b][0]}'" for b in names if b not in ship]
    if [b for b in names if b in ship] != [b for b in ship if b in names]:
        out.append("steps in another order")
    for b in blocks:
        if b["block"] == "cert" and b.get("on_fail") == "switch":
            out.append("certificate: use the preferred supplier")
        if b["block"] == "stock" and b.get("stop_days"):
            out.append(f"stop if cover ≥ {b['stop_days']} days")
        if b["block"] in ("request", "order", "release") and b.get("retries", 1) != 1:
            out.append(f"{BLOCKS[b['block']][0]}: {b['retries']} retries")
    return out


def _parse_json(text: str) -> dict:
    text = (text or "").strip()
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


class Workflow:
    def __init__(self, blocks=None, read_llm: LLM | None = None):
        self.blocks = clean_blocks(blocks if blocks is not None else SHIPPED_BLOCKS)

    # ------------------------------------------------------------------------------------------- a run
    def start(self, text: str, flaky: bool = False) -> dict:
        return {"id": "w" + uuid.uuid4().hex[:8], "blocks": copy.deepcopy(self.blocks), "text": text, "status": "running",
                "at": 0, "steps": [], "facts": {"text": text}, "waiting_for": None, "reply": "", "model_calls": 0,
                "tool_calls": 0, "tokens_in": 0, "tokens_out": 0, "seconds": 0.0, "usd": 0.0, "flaky": flaky,
                "started": time.time(), "saved_bytes": None}

    def go(self, run: dict, tb, llm_for=None, one: bool = False) -> dict:
        """Run the next step (one=True) or every step until the run is done, stopped, failed or waiting."""
        while run["status"] == "running" and run["at"] < len(run["blocks"]):
            self._step(run, tb, llm_for)
            if one:
                break
        if run["status"] == "running" and run["at"] >= len(run["blocks"]):
            run["status"] = "done"
            if not run["reply"]:
                run["reply"] = self._reply(run)
        if run["status"] == "waiting":
            run["saved_bytes"] = len(json.dumps(run, default=str))
        return run

    def resume(self, run: dict, tb, llm_for=None) -> dict:
        """The run was saved while waiting for an approver. Read Ledgerline again; carry on only if it is approved."""
        if run["status"] != "waiting":
            return run
        run["status"] = "running"   # the approval step runs again and reads the real status
        return self.go(run, tb, llm_for)

    # ------------------------------------------------------------------------------------------- one step
    def _step(self, run, tb, llm_for):
        b = run["blocks"][run["at"]]
        title, kind, needs, gives, _ = BLOCKS[b["block"]]
        f = run["facts"]
        rec = {"n": run["at"] + 1, "block": b["block"], "title": title, "kind": kind, "status": "done", "calls": [],
               "note": "", "t": time.time()}
        if run["steps"] and run["steps"][-1]["block"] == b["block"] and run["steps"][-1]["status"] == "waiting":
            run["steps"].pop()   # resuming: the approval step's old 'waiting' line is replaced by its new reading
        missing = [n for n in needs if f.get(n) in (None, "")]
        if missing:
            src = {n: FIRST_BLOCK_FOR.get(n) for n in missing}
            have_src = all(any(x["block"] == s for x in run["blocks"][:run["at"]]) for s in src.values() if s)
            if have_src:   # the earlier block ran but found nothing: the request did not give it
                rec.update(status="stopped", note=f"The request does not say {', '.join(_words(n) for n in missing)}.")
                return self._end(run, rec, "stopped",
                                 f"I could not do this as an order: it does not say {', '.join(_words(n) for n in missing)}. "
                                 f"This workflow only raises orders.")
            rec.update(status="error", note="Needs " + ", ".join(missing) + ": put " +
                       " and ".join(f"'{BLOCKS[s][0]}'" for s in dict.fromkeys(src.values()) if s) + " before this step.")
            return self._end(run, rec, "failed", f"The workflow is broken at step {rec['n']} ({title}): {rec['note']}")
        try:
            getattr(self, "_b_" + b["block"])(run, b, rec, tb, llm_for)
        except _Stop as s:
            rec.update(status=s.status, note=s.note)
            return self._end(run, rec, {"stopped": "stopped", "error": "failed", "waiting": "waiting"}[s.status], s.reply)
        run["steps"].append(rec)
        run["at"] += 1

    def _end(self, run, rec, status, reply):
        run["steps"].append(rec)
        run["status"] = status
        if status == "waiting":
            run["waiting_for"] = rec.get("waiting_for")
            run["reply"] = reply
        else:
            run["reply"] = reply
            run["at"] = len(run["blocks"]) if status != "waiting" else run["at"]
        return run

    def _tool(self, run, rec, tb, name, args, retries=0):
        """One tool call, retried on a lost reply (the tool looks itself up, so a retry finds what the first one made)."""
        for attempt in range(retries + 1):
            if run.get("flaky") and name == "create_purchase_request" and not run.get("_flaked") and args.get("confirm"):
                run["_flaked"] = True
                tb.erp.inject("pr_submit", "timeout_after_commit", 1)
            t0 = time.perf_counter()
            out = tb.call(name, args)
            rec["calls"].append({"name": name, "args": args, "ok": bool(out.get("ok")), "result": out,
                                 "ms": round((time.perf_counter() - t0) * 1000, 1), "attempt": attempt + 1})
            run["tool_calls"] += 1
            if out.get("ok") or out.get("ledgerline_code") != "TIMEOUT":
                return out
        return out

    # ------------------------------------------------------------------------------------------- the blocks
    def _b_read(self, run, b, rec, tb, llm_for):
        llm = (llm_for or (lambda m: LLM(m, cassette="L5v4_workflow", max_tokens=1024)))("gemini:gemini-3.8-flash")
        r = llm.chat([{"role": "system", "content": READ_PROMPT}, {"role": "user", "content": run["text"]}],
                     reasoning_effort="low")
        got = _parse_json(r.content)
        run["model_calls"] += 1
        run["tokens_in"] += r.tokens_in
        run["tokens_out"] += r.tokens_out
        run["seconds"] = round(run["seconds"] + r.seconds, 2)
        run["usd"] = round(run["usd"] + (r.tokens_in * 0.5 + r.tokens_out * 3.0) / 1e6, 6)
        rec["model"] = {"text": r.content, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}
        q = got.get("quantity")
        f = run["facts"]
        f.update(item_hint=got.get("item"), quantity=int(q) if isinstance(q, (int, float)) and q > 0 else None,
                 supplier_hint=got.get("supplier"), cost_centre=(got.get("cost_centre") or None),
                 need_by=got.get("need_by"), is_order=bool(got.get("is_order")))
        rec["got"] = {k: f.get(k) for k in ("is_order", "item_hint", "quantity", "supplier_hint", "cost_centre", "need_by")}
        if not got:
            raise _Stop("error", "The model's reply was not JSON.", "I could not read the request. Try again.")
        if not f["is_order"]:
            raise _Stop("stopped", "Not an order.", "This is not an order, and this workflow only raises orders.")

    def _b_item(self, run, b, rec, tb, llm_for):
        out = self._tool(run, rec, tb, "find_item", {"query": str(run["facts"]["item_hint"])})
        items = out.get("items") or []
        exact = [i for i in items if i["item_code"].upper() == str(run["facts"]["item_hint"]).strip().upper()]
        if not out.get("ok") or not items:
            raise _Stop("stopped", "No such item.", f"I could not find the item '{run['facts']['item_hint']}' in Ledgerline.")
        run["facts"]["item_code"] = (exact or items)[0]["item_code"]
        rec["note"] = run["facts"]["item_code"]

    def _b_stock(self, run, b, rec, tb, llm_for):
        out = self._tool(run, rec, tb, "check_stock", {"item_code": run["facts"]["item_code"]})
        if not out.get("ok"):
            raise _Stop("error", out.get("error", ""), f"check_stock failed: {out.get('error')}")
        run["facts"]["free"] = out.get("free_total", sum(w.get("free", 0) for w in out.get("warehouses", [])))
        run["facts"]["cover_days"] = out.get("cover_days")
        rec["note"] = f"{run['facts']['free']:,} free" + (f", {out.get('cover_days')} days of cover" if out.get("cover_days") is not None else "")
        if b.get("stop_days") and (out.get("cover_days") or 0) >= b["stop_days"]:
            raise _Stop("stopped", f"Cover is {out.get('cover_days')} days: no order needed.",
                        f"No order needed: {out.get('cover_days')} days of cover.")

    def _b_supplier(self, run, b, rec, tb, llm_for):
        out = self._tool(run, rec, tb, "find_supplier", {"name": str(run["facts"]["supplier_hint"])})
        act = [m for m in out.get("matches") or [] if m.get("status") == "ACTIVE"]
        if not act:
            raise _Stop("stopped", "No such supplier.", f"I could not find an active supplier called '{run['facts']['supplier_hint']}'.")
        run["facts"]["supplier_code"] = act[0]["supplier_code"]
        rec["note"] = f"{act[0]['name']} ({act[0]['supplier_code']})"

    def _b_cert(self, run, b, rec, tb, llm_for):
        f = run["facts"]
        out = self._tool(run, rec, tb, "supplier_certificates", {"supplier_code": f["supplier_code"], "item_code": f["item_code"]})
        item = out.get("item") or {}
        if not out.get("ok"):
            raise _Stop("error", out.get("error", ""), f"supplier_certificates failed: {out.get('error')}")
        ok = bool(item.get("supplier_qualifies")) or not item.get("needs_un38_3")
        if ok:
            f["certified"] = True
            rec["note"] = "passes: " + (f"UN 38.3 {out.get('un38_3')}" if item.get("needs_un38_3") else "no certificate needed")
            return
        if b.get("on_fail") == "switch" and PREFERRED.get(f["item_code"]) and PREFERRED[f["item_code"]] != f["supplier_code"]:
            old, f["supplier_code"] = f["supplier_code"], PREFERRED[f["item_code"]]
            again = self._tool(run, rec, tb, "supplier_certificates", {"supplier_code": f["supplier_code"], "item_code": f["item_code"]})
            if again.get("un38_3") == "valid":
                f["certified"], f["switched_from"] = True, old
                rec["note"] = f"{old}: UN 38.3 {out.get('un38_3')}; switched to the preferred supplier {f['supplier_code']}"
                return
        raise _Stop("stopped", f"UN 38.3 {out.get('un38_3')} for {f['supplier_code']}.",
                    f"Stopped: {out.get('supplier_name', f['supplier_code'])} has no valid UN 38.3 certificate "
                    f"({out.get('un38_3')}), and {f['item_code']} contains lithium cells (Purchase Policy §6.2). Nothing was ordered.")

    def _b_budget(self, run, b, rec, tb, llm_for):
        out = self._tool(run, rec, tb, "check_budget", {"cost_centre": run["facts"]["cost_centre"]})
        if not out.get("ok"):
            raise _Stop("stopped", out.get("error", ""), f"Stopped: {out.get('error')}")
        if not out.get("open"):
            raise _Stop("stopped", f"{out.get('code')} is closed.",
                        f"Stopped: cost centre {out.get('code')} is closed (since {out.get('closed_on')}). Nothing was saved. "
                        f"Which open cost centre should it go on?")
        run["facts"]["budget_left"] = out.get("budget_left")
        rec["note"] = f"open, £{out.get('budget_left', 0):,.0f} left"

    def _b_request(self, run, b, rec, tb, llm_for):
        f = run["facts"]
        out = self._tool(run, rec, tb, "create_purchase_request", {"item_code": f["item_code"], "quantity": f["quantity"],
                         "cost_centre": f["cost_centre"], "need_by": f["need_by"], "confirm": True}, b.get("retries", 1))
        if not out.get("ok"):
            raise _Stop("error", out.get("error", ""), f"The request was not saved: {out.get('error')} {out.get('next_step', '')}".strip())
        f["request_no"], f["request_status"] = out["request_no"], out.get("status_code")
        retried = len(rec["calls"]) > 1
        rec["note"] = f"{out['request_no']} · {out.get('status')}" + (
            " (the retry found the one the lost reply had saved)" if out.get("already_done") and retried else
            " (it already existed: the tool found it instead of raising a second)" if out.get("already_done") else "")

    def _b_approval(self, run, b, rec, tb, llm_for):
        f = run["facts"]
        out = self._tool(run, rec, tb, "order_status", {"request_no": f["request_no"]})
        code = out.get("status_code")
        if code in ("AP", "CL"):   # approved (CL: approved, and an order was already made from it)
            f["approved_by"] = out.get("approved_by")
            rec["note"] = f"APPROVED by {out.get('approved_by')}" + (" (within Emma's limit)" if out.get("approved_by") == "ECLARKE" else "")
            return
        if code == "RJ":
            raise _Stop("stopped", "Rejected.", f"{f['request_no']} was rejected. Nothing was ordered.")
        if code != "PA":
            raise _Stop("error", f"Status {out.get('status')}.", f"{f['request_no']} is {out.get('status')}: not something this workflow can wait for.")
        rec["waiting_for"] = {"doc": f["request_no"], "approver": out.get("approver"), "since": time.time()}
        raise _Stop("waiting", f"{f['request_no']} waits for {out.get('approver')}.",
                    f"{f['request_no']} is waiting for {out.get('approver')} to approve it. The run is saved; it carries "
                    f"on when Ledgerline says APPROVED.")

    def _b_order(self, run, b, rec, tb, llm_for):
        f = run["facts"]
        out = self._tool(run, rec, tb, "create_purchase_order", {"supplier_code": f["supplier_code"], "request_no": f["request_no"],
                         "confirm": True}, b.get("retries", 1))
        if not out.get("ok"):
            raise _Stop("error", out.get("error", ""), f"The order was not created: {out.get('error')}")
        f["po_no"] = out["po_no"]
        rec["note"] = f"{out['po_no']} · £{out.get('gross_value', 0):,.0f} · {out.get('status')}"

    def _b_release(self, run, b, rec, tb, llm_for):
        out = self._tool(run, rec, tb, "release_purchase_order", {"po_no": run["facts"]["po_no"]}, b.get("retries", 1))
        if not out.get("ok"):
            raise _Stop("error", out.get("error", ""), f"The order was not released: {out.get('error')}")
        run["facts"]["po_status"] = out.get("status_code")
        rec["note"] = out.get("status", "")

    def _b_reply(self, run, b, rec, tb, llm_for):
        run["reply"] = self._reply(run)
        rec["note"] = run["reply"]

    @staticmethod
    def _reply(run) -> str:
        f = run["facts"]
        if f.get("po_no") and f.get("po_status") == "RL":
            return (f"Done: {f['po_no']} for {f.get('quantity'):,} {f.get('item_code')} is released to {f.get('supplier_code')}"
                    + (f" (approved by {f.get('approved_by')})" if f.get("approved_by") and f.get("approved_by") != "ECLARKE" else "")
                    + (f"; {f['switched_from']} had no valid certificate" if f.get("switched_from") else "") + ".")
        if f.get("po_no"):
            return f"{f['po_no']} is created but not released."
        if f.get("request_no"):
            return f"{f['request_no']} is saved ({f.get('request_status')}). No order yet."
        return "Nothing was saved."


class _Stop(Exception):
    def __init__(self, status, note, reply):
        super().__init__(note)
        self.status, self.note, self.reply = status, note, reply


def _words(field: str) -> str:
    return {"item_hint": "which item", "quantity": "how many", "supplier_hint": "which supplier", "cost_centre": "which cost centre",
            "need_by": "when it is needed", "item_code": "the item", "supplier_code": "the supplier",
            "request_no": "a request", "po_no": "an order"}.get(field, field)
