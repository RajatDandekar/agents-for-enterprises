"""Lecture 3: intent tools. Each one hides a sequence of screens and services behind one sentence-sized job.

Tool set v1. The tool contract, applied to every tool here (TOOL_CONTRACT below is the checklist):
  1. Types        a typed input schema, a description written for a model, and arguments checked once at the door.
  2. Errors       say what went wrong in words and what to do next (never a bare legacy code).
  3. Preview      writes preview first (confirm=false) and commit only on confirm=true.
  4. Idempotency  every write carries a key; a retry with the same key finds the first result instead of a second order.
                  The key is derived from the order's content when the model leaves it out (a hash, never uuid4()).
  5. Receipt      every write returns a receipt with the document's real status, read back from Bahi after the write.
  6. Validate once  the tools never re-implement Bahi's rules; they call the services (tax engine, budget check)
                  and report what Bahi says.
  7. Permissions  tools act through the user's own Session, so they can do exactly what the user can do in Bahi.
  8. Timeout/retry  reads are retried; a write that times out is never blindly retried: the tool looks it up by key.
  9. Version      every tool has a version; receipts carry it, and the MCP server publishes it.

The names and arguments of the eight CORE tools and the three EXTRA tools are stable: Lectures 4, 5 and 7 import them.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Callable

from ..erp.engine import SERVICES, ServiceTimeout, Session
from ..llm import tool_schema

TOOLSET_VERSION = "1.0"

STATUS = {"DR": "DRAFT (saved, not sent to the supplier)", "PA": "WAITING FOR APPROVAL", "AP": "APPROVED, NOT YET RELEASED",
          "RL": "RELEASED to the supplier", "RJ": "REJECTED", "CN": "CANCELLED", "CL": "CLOSED (converted to an order)"}

TOOL_CONTRACT = [
    ("Types", "Typed input schema; arguments checked once, at the door, with a readable error."),
    ("Errors that say what to do next", "Every failure returns ok=false, what went wrong, and next_step."),
    ("Preview", "A write previews first (confirm=false) and commits only on confirm=true."),
    ("Idempotency key", "A retry with the same key returns the first result, never a second document."),
    ("Receipt", "The document's real status, read back from Bahi after the write."),
    ("Validate once", "Bahi's procedures enforce the rules; the tool asks them, never copies them."),
    ("Permissions = the user's", "The tool runs in the user's own Bahi session, never a service account."),
    ("Timeout and retry", "Reads retry; a write that times out is looked up by its key before anything else."),
    ("Version", "Each tool has a version number, carried on receipts and published over MCP."),
]

# Legacy error codes, rewritten as instructions a model can act on.
ERR_HELP = {
    "ERR-PO-0412": "The tax code does not match the supplier's state. Use a -INTER code for suppliers outside Maharashtra, -INTRA inside.",
    "ERR-PO-0610": "Orders above ₹50,000 gross need a purchase request first. create_purchase_order does this for you; do not call services directly.",
    "ERR-PO-0715": "The order cannot be released in its current status. Check order_status: a DRAFT usually means the cost centre is closed; WAITING FOR APPROVAL means the approver has not signed yet.",
    "ERR-PO-0702": "The order is not waiting for approval, so there is nothing to approve or reject.",
    "ERR-PO-0801": "The order is closed or cancelled and cannot be changed.",
    "ERR-PO-0001": "No order with that number. Check the number with the user, or use order_status with the idempotency_key.",
    "ERR-SCR-0221": "Bahi needs its defaults fetched before saving. Retry the tool; it fetches first.",
    "ERR-SUP-0030": "No supplier with that code. Use find_supplier with the supplier's name.",
    "ERR-SUP-0031": "That supplier code is blocked. Use find_supplier to get the active code.",
    "ERR-SUP-0118": "A supplier with this GSTIN already exists. Use find_supplier; do not register them again.",
    "ERR-ITM-0010": "No item with that code. Use find_item with a description.",
    "ERR-ITM-0011": "That item is inactive. Use find_item to pick an active item.",
    "ERR-CC-0009": "No such cost centre. Use check_cost_centre without a code to list the open ones.",
    "ERR-BUD-0207": "The cost centre does not have enough budget left. Ask the user which cost centre to use.",
    "ERR-SEC-0001": "The user is not allowed to do this in Bahi. Tell the user; do not try another way round.",
    "ERR-APR-0003": "Nobody may approve their own document. It must go to the approver.",
    "ERR-APR-0004": "The value is above this approver's limit.",
    "ERR-PR-0105": "The need-by date is in the past. Ask the user for a future date.",
    "ERR-PO-0105": "The need-by date is in the past. Ask the user for a future date.",
    "ERR-SYS-0503": "Bahi is busy. The tool already retried; try again in a minute, or tell the user.",
}


class ToolError(Exception):
    def __init__(self, what: str, next_step: str = "", code: str = ""):
        super().__init__(what)
        self.what, self.next_step, self.code = what, next_step, code

    def as_dict(self):
        return {"ok": False, "error": self.what, "next_step": self.next_step, "bahi_code": self.code}


READ_RETRIES = 2


def _bahi(s: Session, svc: str, **payload) -> dict:
    """Call a service; turn a legacy error into a ToolError that says what to do next.

    Reads are safe to repeat, so a busy server or a lost reply is retried. Writes are never retried here:
    the write tools handle a lost reply themselves, by looking the document up by its key."""
    is_read = SERVICES[svc].kind == "read" if svc in SERVICES else True
    for attempt in range(READ_RETRIES + 1 if is_read else 1):
        try:
            r = s.call(svc, **payload)
        except ServiceTimeout:
            if is_read and attempt < READ_RETRIES:
                continue
            raise
        if r["rc"] == "E" and r["err_cd"] == "ERR-SYS-0503" and is_read and attempt < READ_RETRIES:
            continue
        break
    if r["rc"] == "E":
        raise ToolError(f"Bahi refused {svc}: {r['msg'].capitalize()} ({r['err_cd']}).",
                        ERR_HELP.get(r["err_cd"], "Tell the user what Bahi said."), r["err_cd"])
    return r["data"] or {}


def _peek(s: Session, sql: str, *args) -> dict | None:
    """A read Bahi's service layer does not offer (e.g. 'the approval for this document', 'the plant's state').
    This is our own small agent API in front of the ERP: in a real build, ask IT for a read-only view."""
    return s.erp.q1(sql, *args)


def content_key(*parts) -> str:
    """An idempotency key derived from what the order IS, so the same order always gets the same key."""
    raw = "|".join(str(p).strip().upper() for p in parts)
    return "K" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


@dataclass
class Tool:
    name: str
    description: str
    params: dict
    required: list
    fn: Callable
    writes: bool = False
    version: str = "1.0"
    services: tuple = ()  # the Bahi services this tool may call, for the manifest and the deck

    def schema(self) -> dict:
        return tool_schema(self.name, self.description, self.params, self.required)

    def manifest(self) -> dict:
        return {"name": self.name, "version": self.version, "writes": self.writes, "services": list(self.services),
                "required": self.required, "params": list(self.params)}


TOOLS: dict[str, Tool] = {}


def tool(name, description, params, required=(), writes=False, version="1.0", services=()):
    def deco(fn):
        TOOLS[name] = Tool(name, description, params, list(required), fn, writes, version, tuple(services))
        return fn
    return deco


S = {"type": "string"}
I = {"type": "integer"}
N = {"type": "number"}
B = {"type": "boolean"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_args(t: Tool, args: dict) -> dict:
    """Contract item 1, done once at the door: names, required fields, types, dates. Returns clean arguments."""
    clean = {}
    for k, v in (args or {}).items():
        if k not in t.params:
            raise ToolError(f"{t.name} has no argument '{k}'.", f"Use only: {', '.join(t.params)}.")
        if v is None or v == "":
            continue
        want = t.params[k].get("type")
        try:
            if want == "integer":
                v = int(float(str(v).replace(",", "")))
            elif want == "number":
                v = float(str(v).replace(",", "").replace("₹", ""))
            elif want == "boolean" and not isinstance(v, bool):
                v = str(v).lower() in ("true", "yes", "1")
            elif want == "string":
                v = str(v).strip()
        except ValueError:
            raise ToolError(f"'{k}' must be a {want}, got {v!r}.", "Fix the argument and call again.")
        if k in ("need_by", "valid_to") and not DATE.match(v):
            raise ToolError(f"'{k}' must be a date written YYYY-MM-DD, got {v!r}.",
                            "Rewrite the date as YYYY-MM-DD (today is 2026-10-26) and call again.")
        clean[k] = v
    missing = [r for r in t.required if r not in clean]
    if missing:
        raise ToolError(f"{t.name} needs {', '.join(missing)}.", "Ask the user for it, or look it up with a find_ tool.")
    return clean


# ----------------------------------------------------------------------------- reads
_UNIT = {"litre": "l", "liter": "l", "ltr": "l", "litres": "l", "liters": "l"}


def _norm_words(text: str) -> list[str]:
    out = []
    for w in re.split(r"[^a-z0-9.]+", text.lower()):
        if not w:
            continue
        w = _UNIT.get(w, w)
        if len(w) > 3 and w.endswith("s"):
            w = w[:-1]  # handles -> handle, gaskets -> gasket
        out.append(w)
    return out


@tool("find_item", "Find stock items by description or code (e.g. '5 litre silicone gasket'). Returns active items, best "
      "match first, with their code, unit and whether they touch food.",
      {"query": {**S, "description": "words describing the item, or its code"}}, ["query"],
      services=("itm_search", "itm_get"))
def find_item(s: Session, query: str):
    words = _norm_words(query)
    hits: dict[str, dict] = {}
    for q in [query] + [w for w in words if len(w) >= 3]:
        for r in _bahi(s, "itm_search", q=q)["rows"]:
            hits[r["itm_cd"]] = r
        if q == query and hits:
            break  # the whole phrase matched: no need to search word by word
    scored = []
    for r in hits.values():
        if not r["active"]:
            continue
        d = set(_norm_words(r["itm_cd"] + " " + r["descr"]))
        scored.append((sum(1 for w in words if w in d), r))
    scored.sort(key=lambda x: -x[0])
    out = []
    for _, r in scored[:6]:
        i = _bahi(s, "itm_get", itm_cd=r["itm_cd"])
        out.append({"item_code": r["itm_cd"], "description": r["descr"], "unit": r["uom_cd"],
                    "food_contact": bool(i["food_contact"])})
    inactive = [r["itm_cd"] for r in hits.values() if not r["active"]]
    note = "" if out else "No active item matched. Ask the user to describe it differently."
    if inactive:
        note += f" Inactive (cannot be ordered): {', '.join(inactive)}."
    return {"ok": True, "items": out, "note": note.strip()}


@tool("stock_position", "Stock on hand, on order and days of cover for an item, in every warehouse.",
      {"item_code": {**S, "description": "Bahi item code, e.g. GSK-SIL-05L"}}, ["item_code"],
      services=("whs_list", "stk_query"))
def stock_position(s: Session, item_code: str):
    out = []
    for w in _bahi(s, "whs_list")["rows"]:
        r = s.call("stk_query", itm_cd=item_code, whs_cd=w["whs_cd"])
        if r["rc"] == "S":
            d = r["data"]
            out.append({"warehouse": w["whs_cd"], "on_hand": d["on_hand"], "on_order": d["on_order"],
                        "average_daily_use": d["avg_daily_issue"], "days_of_cover": d["cover_days"],
                        "reorder_level": d["reorder_lvl"]})
    if not out:
        raise ToolError(f"No stock record for {item_code}.", "Check the code with find_item.")
    return {"ok": True, "item_code": item_code, "warehouses": out}


@tool("last_purchase", "Recent released orders for an item (supplier, quantity, rate, date) and each supplier's CURRENT "
      "contract rate. Use the contract rate for a new order, not an old order's rate.",
      {"item_code": S, "supplier_code": {**S, "description": "optional, to see one supplier only"}}, ["item_code"],
      services=("po_hist", "sup_rate_get"))
def last_purchase(s: Session, item_code: str, supplier_code: str | None = None):
    rows = _bahi(s, "po_hist", itm_cd=item_code, **({"sup_cd": supplier_code} if supplier_code else {}))["rows"]
    sups = {r["sup_cd"] for r in rows} | ({supplier_code} if supplier_code else set())
    if not supplier_code:  # suppliers with a rate contract but no recent order still count
        sups |= {r["sup_cd"] for r in s.erp.q("SELECT DISTINCT sup_cd FROM sup_rate WHERE itm_cd=?", item_code)}
    rates = {}
    for sc in sorted(sups):
        cur = _bahi(s, "sup_rate_get", sup_cd=sc, itm_cd=item_code)["current"]
        rates[sc] = cur["rate"] if cur else None
    return {"ok": True, "orders": [{"po_no": r["po_no"], "supplier_code": r["sup_cd"], "supplier": r["sup_name"],
                                    "quantity": r["qty"], "rate": r["rate"], "date": r["created_on"][:10]} for r in rows[:5]],
            "current_contract_rate": rates}


_LEGAL = {"industries", "industry", "pvt", "private", "ltd", "limited", "llp", "co", "company", "and", "the",
          "enterprises", "corporation", "corp", "inc", "products", "works", "india"}


def name_key(name: str) -> str:
    """'Deccan Polymer Industries Pvt. Ltd.' -> 'deccan polymer': lower case, no brackets, no legal words, no plurals."""
    n = re.sub(r"\(.*?\)", " ", name.lower()).replace("&", " ")
    return " ".join(w[:-1] if len(w) > 4 and w.endswith("s") else w
                    for w in re.split(r"[^a-z0-9]+", n) if w and w not in _LEGAL)


@tool("find_supplier", "Look a supplier up by name, tolerating different spellings. Returns the closest matches with "
      "their status and food-grade certificate. ALWAYS use this before registering a supplier.",
      {"name": {**S, "description": "supplier name as the user said it"}, "city": {**S, "description": "optional"}}, ["name"],
      services=("sup_search", "sup_cert_get"))
def find_supplier(s: Session, name: str, city: str | None = None):
    seen = {}
    words = [w for w in re.split(r"\W+", name) if len(w) >= 3 and w.lower() not in _LEGAL]
    for q in [name] + words:
        for r in _bahi(s, "sup_search", q=q)["rows"]:
            seen[r["sup_cd"]] = r
    out = []
    k = name_key(name)
    for r in seen.values():
        score = difflib.SequenceMatcher(None, k, name_key(r["name"])).ratio()
        if city and city.lower() in (r["city"] or "").lower():
            score += 0.1
        certs = _bahi(s, "sup_cert_get", sup_cd=r["sup_cd"])["rows"]
        food = [c for c in certs if c["cert_type"] == "FOOD-GRADE"]
        valid = any(c["valid_to"] >= s.erp.today for c in food)
        out.append({"supplier_code": r["sup_cd"], "name": r["name"], "city": r["city"], "state": r["state"],
                    "status": r["status"], "match": round(min(score, 1.0), 2),
                    "food_grade_certificate": "valid" if valid else ("expired" if food else "none")})
    out.sort(key=lambda x: (x["status"] != "ACTIVE", -x["match"]))
    best = out[0] if out else None
    hint = ""
    if best and best["status"] == "ACTIVE" and best["match"] >= 0.8:
        if best["name"].lower() != name.lower():
            hint = (f"'{name}' is almost certainly {best['name']} ({best['supplier_code']}), already in Bahi. "
                    f"Confirm with the user and use that code. Do NOT register a new supplier.")
    elif not out or best["match"] < 0.6:
        hint = "No existing supplier matches. A new supplier must be onboarded (Supplier Policy) before any order."
    else:
        hint = "Only partial matches. Show them to the user and ask which one they mean."
    blocked = [o["supplier_code"] for o in out if o["status"] != "ACTIVE"]
    if blocked:
        hint += f" Blocked codes, never use: {', '.join(blocked)}."
    return {"ok": True, "matches": out[:5], "hint": hint.strip()}


@tool("check_cost_centre", "Is a cost centre open, and how much budget is left this quarter? Without a code, lists every "
      "open cost centre.", {"code": {**S, "description": "e.g. PRD-07; omit to list open ones"}},
      services=("cc_list", "cc_get", "bud_check"))
def check_cost_centre(s: Session, code: str | None = None):
    if not code:
        rows = _bahi(s, "cc_list")["rows"]
        return {"ok": True, "open": [{"code": r["cc_cd"], "name": r["name"]} for r in rows if r["status"] == "OPEN"]}
    cc = _bahi(s, "cc_get", cc_cd=code)
    b = _bahi(s, "bud_check", cc_cd=code, amount=0)
    out = {"ok": True, "code": code, "name": cc["name"], "open": cc["status"] == "OPEN",
           "closed_on": cc["closed_on"], "budget_left": b["available"]}
    if not out["open"]:
        out["note"] = (f"{code} is CLOSED. Bahi will silently save any order on it as a DRAFT that never reaches the "
                       f"supplier. Ask the user for an open cost centre.")
    return out


@tool("order_status", "The real status of a purchase order, with its approval and any warning, read from Bahi.",
      {"po_no": {**S, "description": "e.g. PO/2026/01182"}, "idempotency_key": {**S, "description": "or the key it was created with"}},
      services=("po_search", "po_get"))
def order_status(s: Session, po_no: str | None = None, idempotency_key: str | None = None):
    if not po_no and idempotency_key:
        rows = _bahi(s, "po_search", client_ref=idempotency_key)["rows"]
        if not rows:
            return {"ok": True, "found": False, "note": "No order carries this key, so it was never saved."}
        po_no = rows[0]["po_no"]
    if not po_no:
        raise ToolError("Give a po_no or an idempotency_key.", "Ask the user for the order number.")
    return {"ok": True, "found": True, **_receipt(s, po_no, tool="order_status")}


def _receipt(s: Session, po_no: str, tool: str = "create_purchase_order") -> dict:
    """Contract item 5: read the document back from Bahi after the write, and say what its status really means."""
    h = _bahi(s, "po_get", po_no=po_no)
    line = h["lines"][0]
    warn = None
    if h["warn_cd"] == "W-CC-114":
        warn = (f"Saved as DRAFT because cost centre {h['cc_cd']} is closed. It will NOT reach the supplier. "
                f"Ask the user for an open cost centre, then amend.")
    appr = _peek(s, "SELECT doc_no,approver,status FROM approval WHERE doc_no IN (?,?) ORDER BY appr_id DESC",
                 po_no, h["pr_no"] or "")
    return {"po_no": po_no, "status": STATUS.get(h["status"], h["status"]), "status_code": h["status"],
            "supplier_code": h["sup_cd"], "item_code": line["itm_cd"], "quantity": line["qty"], "rate": line["rate"],
            "gross_value": h["gross_value"], "cost_centre": h["cc_cd"], "need_by": h["need_dt"],
            "request_no": h["pr_no"], "created_by": h["created_by"], "approved_by": h["approved_by"],
            "approval": appr, "warning": warn, "idempotency_key": h["client_ref"],
            "sent_to_supplier": h["status"] == "RL", "tool": tool, "tool_version": TOOLS[tool].version}


# ----------------------------------------------------------------------------- writes
def _tax_code(s: Session, sup_cd: str) -> str:
    """Bahi's Fetch defaults the tax code to the plant's own state (the ERR-PO-0412 trap). We pick the code from the
    supplier's state; Bahi's sp_tax_region_chk still checks it on Save (validate once)."""
    sup = _bahi(s, "sup_get", sup_cd=sup_cd)
    me = _bahi(s, "usr_get", user_id=s.user_id)
    ou_state = _peek(s, "SELECT state FROM org_unit WHERE ou_cd=?", me["ou_cd"])["state"]
    return "GST18-INTRA" if sup["state"] == ou_state else "GST18-INTER"


def _find_request(s: Session, key: str, item_code, quantity, cost_centre, need_by) -> dict | None:
    """An open purchase request for this order: by key first, then by content (same item, qty, cost centre, date)."""
    rows = _bahi(s, "pr_search", raised_by=s.user_id)["rows"]
    for p in rows:
        if f"key:{key}" in (p["remarks"] or "") and p["status"] != "RJ":
            return p
    for p in rows:
        if p["status"] in ("PA", "AP") and p["cc_cd"] == cost_centre and p["need_dt"] == need_by:
            line = _bahi(s, "pr_get", pr_no=p["pr_no"])["lines"][0]
            if line["itm_cd"] == item_code and line["qty"] == quantity:
                return p
    return None


@tool("create_purchase_order",
      "Order an item from a supplier. With confirm=false (the default) it only PREVIEWS: price, tax, gross value, whether "
      "approval is needed and who approves. Show the preview to the user; call again with confirm=true to commit. "
      "Above ₹50,000 it raises the purchase request first; if that needs approval it returns WAITING FOR APPROVAL and you "
      "call again with the same arguments once approved. Returns a receipt with the real status.",
      {"supplier_code": S, "item_code": S, "quantity": I, "cost_centre": S,
       "need_by": {**S, "description": "date, YYYY-MM-DD"},
       "rate": {**N, "description": "omit to use the current contract rate"},
       "idempotency_key": {**S, "description": "optional; reuse it on retries. Omit it and the tool derives one from "
                                                "the order's content"},
       "confirm": {**B, "description": "false = preview only; true = commit"}},
      ["supplier_code", "item_code", "quantity", "cost_centre", "need_by"], writes=True,
      services=("po_search", "sup_get", "itm_get", "sup_rate_get", "usr_get", "tax_compute", "bud_check", "sup_cert_get",
                "pr_search", "pr_get", "pr_save", "pr_submit", "po_fetch", "po_save", "po_get"))
def create_purchase_order(s: Session, supplier_code, item_code, quantity, cost_centre, need_by, idempotency_key=None,
                          rate=None, confirm=False):
    key = idempotency_key or content_key(s.user_id, supplier_code, item_code, quantity, cost_centre, need_by)
    # 1. Idempotency: has this key (or this exact order, today) already produced an order?
    rows = _bahi(s, "po_search", client_ref=key)["rows"]
    if not rows:
        rows = [r for r in _bahi(s, "po_search", sup_cd=supplier_code, itm_cd=item_code, from_dt=s.erp.today)["rows"]
                if r["created_by"] == s.user_id and r["qty"] == quantity and r["status"] not in ("CN", "RJ")]
    if rows:
        return {"ok": True, "already_done": True,
                "note": "This order already exists; nothing new was written. Here is its receipt.",
                **_receipt(s, rows[0]["po_no"])}
    sup = _bahi(s, "sup_get", sup_cd=supplier_code)
    if sup["status"] != "ACTIVE":
        raise ToolError(f"{supplier_code} is {sup['status']}.", ERR_HELP["ERR-SUP-0031"], "ERR-SUP-0031")
    itm = _bahi(s, "itm_get", itm_cd=item_code)
    contract = _bahi(s, "sup_rate_get", sup_cd=supplier_code, itm_cd=item_code)["current"]
    if rate is None:
        if not contract:
            raise ToolError(f"No current rate contract with {supplier_code} for {item_code}.",
                            "Ask the user for the agreed rate.")
        rate = contract["rate"]
    tax_cd = _tax_code(s, supplier_code)
    basic = round(quantity * rate, 2)
    gross = _bahi(s, "tax_compute", basic=basic, tax_cd=tax_cd)["gross"]       # Bahi's shared tax engine
    me = _bahi(s, "usr_get", user_id=s.user_id)
    budget = _bahi(s, "bud_check", cc_cd=cost_centre, amount=0)               # Bahi's own budget procedure
    certs = _bahi(s, "sup_cert_get", sup_cd=supplier_code)["rows"]
    food = [c for c in certs if c["cert_type"] == "FOOD-GRADE"]
    cert = "valid" if any(c["valid_to"] >= s.erp.today for c in food) else ("expired" if food else "none")
    preview = {"supplier": f"{sup['name']} ({supplier_code})", "item": f"{itm['descr']} ({item_code})",
               "quantity": quantity, "rate": rate, "contract_rate": contract["rate"] if contract else None,
               "basic_value": basic, "tax_code": tax_cd, "gross_value": gross, "cost_centre": cost_centre,
               "cost_centre_state": budget["cc_state"], "need_by": need_by, "path": "request first" if gross > 50000 else "direct order",
               "needs_approval": gross > me["appr_limit"], "your_limit": me["appr_limit"],
               "approver": me["manager_id"] if gross > me["appr_limit"] else None,
               "food_contact_item": bool(itm["food_contact"]), "supplier_food_grade_certificate": cert,
               "idempotency_key": key}
    warnings = []
    if budget["cc_state"] == "CLOSED":
        warnings.append(f"Cost centre {cost_centre} is CLOSED: Bahi would save this order as a DRAFT that never reaches "
                        f"the supplier. Ask the user for an open cost centre.")
    if itm["food_contact"] and cert != "valid":
        warnings.append(f"This item touches food and {supplier_code}'s food-grade certificate is {cert.upper()}.")
    if not confirm:
        return {"ok": True, "preview": preview, "warnings": warnings,
                "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    # 2. Big orders go through a purchase request (variant STD); small ones go direct (variant DIR).
    pr_no = None
    if gross > 50000:
        pr = _find_request(s, key, item_code, quantity, cost_centre, need_by)
        if pr:
            pr_no = pr["pr_no"]
        else:
            pr_no = _bahi(s, "pr_save", cc_cd=cost_centre, need_dt=need_by, itm_cd=item_code, qty=quantity,
                          est_rate=rate, remarks=f"key:{key}")["pr_no"]
            _bahi(s, "pr_submit", pr_no=pr_no)
        st = _bahi(s, "pr_get", pr_no=pr_no)["status"]
        if st == "PA":
            appr = _peek(s, "SELECT approver FROM approval WHERE doc_no=? AND status='PENDING'", pr_no)
            return {"ok": True, "status": "WAITING FOR APPROVAL", "request_no": pr_no,
                    "approver": appr["approver"] if appr else None, "gross_value": gross, "idempotency_key": key,
                    "next_step": "Tell the user the request has gone to the approver. Nothing is ordered yet. Call "
                                 "again with the same arguments after approval to create the order."}
        if st == "RJ":
            raise ToolError(f"Request {pr_no} was rejected.", "Tell the user; do not resubmit without their say-so.")
    # 3. Screen state: Fetch, then Save with the fetch token and the key.
    f = _bahi(s, "po_fetch", sup_cd=supplier_code, itm_cd=item_code, **({"pr_no": pr_no} if pr_no else {}))
    payload = dict(po_type="STD" if pr_no else "DIR", sup_cd=supplier_code, itm_cd=item_code, qty=quantity, rate=rate,
                   tax_cd=tax_cd, cc_cd=cost_centre, need_dt=need_by, fetch_tok=f["fetch_tok"], client_ref=key)
    if pr_no:
        payload["pr_no"] = pr_no
    try:
        saved = _bahi(s, "po_save", **payload)
    except ServiceTimeout:
        rows = _bahi(s, "po_search", client_ref=key)["rows"]  # 4. a lost reply: look it up before anything else
        if not rows:
            raise ToolError("Bahi timed out and the order was not saved.", "Call again with the same arguments.")
        saved = {"doc_no": rows[0]["po_no"]}
    # 5. Read back: the receipt carries the status Bahi actually holds, not the message it printed.
    out = {"ok": True, **_receipt(s, saved["doc_no"])}
    if out["status_code"] == "AP":
        out["next_step"] = "Approved but NOT yet sent to the supplier. Call release_purchase_order to release it."
    return out


@tool("release_purchase_order", "Release an APPROVED order to the supplier. Returns a receipt with the real status.",
      {"po_no": S}, ["po_no"], writes=True, services=("po_get", "po_release"))
def release_purchase_order(s: Session, po_no: str):
    h = _bahi(s, "po_get", po_no=po_no)
    if h["status"] == "RL":
        return {"ok": True, "already_done": True, **_receipt(s, po_no, tool="release_purchase_order")}
    try:
        _bahi(s, "po_release", po_no=po_no)
    except ServiceTimeout:
        pass  # the reply was lost; the read-back below says whether it was released
    return {"ok": True, **_receipt(s, po_no, tool="release_purchase_order")}


@tool("amend_purchase_order", "Change an order's quantity, need-by date or cost centre (e.g. to move a DRAFT off a closed "
      "cost centre). Bahi re-checks budget and approval. Returns a receipt with the real status.",
      {"po_no": S, "quantity": I, "need_by": {**S, "description": "YYYY-MM-DD"}, "cost_centre": S}, ["po_no"], writes=True,
      services=("po_amend", "po_get"))
def amend_purchase_order(s: Session, po_no, quantity=None, need_by=None, cost_centre=None):
    args = {k: v for k, v in (("qty", quantity), ("need_dt", need_by), ("cc_cd", cost_centre)) if v}
    if not args:
        raise ToolError("Nothing to change.", "Give a quantity, need_by or cost_centre.")
    try:
        _bahi(s, "po_amend", po_no=po_no, **args)
    except ServiceTimeout:
        pass  # amending to the same values twice is harmless; the read-back shows what Bahi holds
    out = {"ok": True, **_receipt(s, po_no, tool="amend_purchase_order")}
    if out["status_code"] == "AP":
        out["next_step"] = "Approved but NOT yet sent to the supplier. Call release_purchase_order to release it."
    return out


@tool("register_supplier", "Register a NEW supplier. Only after find_supplier shows no existing match and the user has "
      "confirmed the details. Food-contact parts still need a food-grade certificate before any order.",
      {"name": S, "city": S, "state": {**S, "description": "two-letter state code, e.g. GJ"}, "gstin": S,
       "confirm": B}, ["name", "city", "state", "gstin"], writes=True,
      services=("sup_search", "sup_get", "sup_create"))
def register_supplier(s: Session, name, city, state, gstin, confirm=False):
    # Bahi only refuses a duplicate GSTIN. A near-duplicate NAME in the same city is our own guard (NE4),
    # written in front of Bahi because Bahi does not have it.
    near = [m for m in find_supplier(s, name, city)["matches"]
            if m["match"] >= 0.8 and (m["city"] or "").lower() == city.lower()]
    same_gstin = []
    for m in near:
        if _bahi(s, "sup_get", sup_cd=m["supplier_code"]).get("gstin") == gstin:
            same_gstin.append(m)
    if same_gstin:  # idempotent: registering the same supplier twice returns the first
        m = same_gstin[0]
        return {"ok": True, "already_done": True, "supplier_code": m["supplier_code"], "name": m["name"],
                "status": m["status"], "food_grade_certificate": m["food_grade_certificate"]}
    if any(m["status"] == "ACTIVE" for m in near):
        m = [m for m in near if m["status"] == "ACTIVE"][0]
        raise ToolError(f"'{name}' looks like {m['name']} ({m['supplier_code']}), already active in {m['city']}.",
                        "Use that supplier code. Register a new supplier only if the user confirms it is a different firm.",
                        "NEAR-DUPLICATE")
    preview = {"name": name, "city": city, "state": state.upper()[:2], "gstin": gstin}
    if not confirm:
        return {"ok": True, "preview": preview, "note": "Nothing saved. Confirm with the user first."}
    try:
        r = _bahi(s, "sup_create", name=name, city=city, state=state, gstin=gstin)
        code = r["sup_cd"]
    except ServiceTimeout:
        rows = [x for x in _bahi(s, "sup_search", q=name)["rows"] if x["name"] == name]
        if not rows:
            raise ToolError("Bahi timed out and the supplier was not saved.", "Call again with the same arguments.")
        code = rows[0]["sup_cd"]
    sup = _bahi(s, "sup_get", sup_cd=code)  # read back
    return {"ok": True, "supplier_code": code, "name": sup["name"], "status": sup["status"],
            "food_grade_certificate": "none", "tool": "register_supplier", "tool_version": TOOLS["register_supplier"].version,
            "next_step": "Before any order for a food-contact part, record the supplier's food-grade certificate."}


@tool("record_certificate", "Record a supplier's food-grade certificate that the user has provided (document reference and "
      "expiry). Never invent one.", {"supplier_code": S, "document_ref": S, "valid_to": {**S, "description": "YYYY-MM-DD"}},
      ["supplier_code", "document_ref", "valid_to"], writes=True, services=("sup_cert_get", "sup_cert_upload"))
def record_certificate(s: Session, supplier_code, document_ref, valid_to):
    if valid_to < s.erp.today:
        raise ToolError(f"The certificate expired on {valid_to}.", "An expired certificate counts as none. Ask the user for a current one.")
    rows = _bahi(s, "sup_cert_get", sup_cd=supplier_code)["rows"]
    if not any(r["doc_ref"] == document_ref for r in rows):  # idempotent on the document reference
        _bahi(s, "sup_cert_upload", sup_cd=supplier_code, cert_type="FOOD-GRADE", doc_ref=document_ref, valid_to=valid_to)
    rows = _bahi(s, "sup_cert_get", sup_cd=supplier_code)["rows"]  # read back
    ok = any(r["doc_ref"] == document_ref and r["valid_to"] >= s.erp.today for r in rows)
    return {"ok": True, "supplier_code": supplier_code, "food_grade_certificate": "valid" if ok else "none",
            "valid_to": valid_to, "document_ref": document_ref, "tool": "record_certificate",
            "tool_version": TOOLS["record_certificate"].version}


CORE = ["find_item", "stock_position", "last_purchase", "find_supplier", "check_cost_centre", "create_purchase_order",
        "release_purchase_order", "order_status"]
EXTRA = ["amend_purchase_order", "register_supplier", "record_certificate"]  # used by the Lecture 4 detours
ALL = CORE + EXTRA


class IntentTools:
    """The intent tools bound to one user's session (contract item 7: the user's own permissions)."""

    def __init__(self, session: Session, names: list[str] | None = None):
        self.s = session
        self.names = list(names or CORE)

    def schemas(self) -> list[dict]:
        return [TOOLS[n].schema() for n in self.names]

    def manifest(self) -> list[dict]:
        return [TOOLS[n].manifest() for n in self.names]

    def call(self, name: str, args: dict) -> dict:
        if name not in self.names:
            return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}
        t = TOOLS[name]
        try:
            return t.fn(self.s, **check_args(t, args))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Bahi did not reply in time ({e}).",
                    "next_step": "Check with order_status before trying again.", "bahi_code": "TIMEOUT"}
        except TypeError as e:
            return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}

    def call_json(self, name: str, args: dict) -> str:
        return json.dumps(self.call(name, args), default=str)


# ----------------------------------------------------------------------------- the two other granularities (experiment)
TYPES = {"str": "string", "int": "integer", "float": "number", "date": "string"}


class RawServiceTools:
    """All 38 Bahi services as tools, described exactly as the service catalogue describes them, run in the user's
    session (unlike Lecture 1's naive agent, which ran as the service account). The finest granularity."""

    def __init__(self, session: Session):
        self.s = session
        self.names = list(SERVICES)

    def schemas(self) -> list[dict]:
        return [tool_schema(v.name, v.doc, {f.name: {"type": TYPES[f.type], "description": f.desc} for f in v.fields},
                            [f.name for f in v.fields if f.required]) for v in SERVICES.values()]

    def call(self, name: str, args: dict) -> dict:
        try:
            return self.s.call(name, **(args or {}))
        except ServiceTimeout as e:
            return {"rc": "E", "err_cd": "TIMEOUT", "msg": str(e)}
        except TypeError as e:
            return {"rc": "E", "err_cd": "BAD-ARGS", "msg": str(e)}


class GenericServiceTool:
    """One generic tool, call_service(name, payload), whose description is the whole service catalogue.
    The coarsest granularity: one tool that can do anything."""

    def __init__(self, session: Session):
        self.s = session
        self.names = ["call_service"]

    def schemas(self) -> list[dict]:
        cat = "; ".join(f"{v.name}({', '.join(f.name + ('*' if f.required else '') for f in v.fields)}) {v.doc}"
                        for v in SERVICES.values())
        return [tool_schema("call_service", "Call any Bahi ERP service by name with a flat payload. * = mandatory. "
                            "Services: " + cat,
                            {"name": {"type": "string", "description": "service name, e.g. itm_search"},
                             "payload": {"type": "string", "description": 'the payload as a JSON object, e.g. {"q": "gasket"}'}},
                            ["name"])]

    def call(self, name: str, args: dict) -> dict:
        if name != "call_service":
            return {"rc": "E", "err_cd": "NO-TOOL", "msg": "Only call_service exists."}
        p = (args or {}).get("payload") or "{}"
        if isinstance(p, str):
            try:
                p = json.loads(p)
            except json.JSONDecodeError:
                return {"rc": "E", "err_cd": "BAD-JSON", "msg": "payload is not valid JSON"}
        try:
            return self.s.call(str(args.get("name", "")), **(p or {}))
        except ServiceTimeout as e:
            return {"rc": "E", "err_cd": "TIMEOUT", "msg": str(e)}
        except TypeError as e:
            return {"rc": "E", "err_cd": "BAD-ARGS", "msg": str(e)}
