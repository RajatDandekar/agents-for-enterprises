"""Lecture 5: the signature. Jobs 6 and 7 of the form: doing only what the user may do, and proving what was done.

The form did these two jobs without anyone noticing. Emma's role greyed out the menus she could not use; Daniel
signed in a second time to approve; the status bar printed a document number. Delete the form and the harness
must do all three, in code, whatever the model says. This file is that code. It wraps the Lecture 4 GraphAgent and
the Lecture 3 IntentTools from the outside; neither file is changed.

    from ledgerline.agent.authority import AuthorityAgent, ApprovalInbox
    inbox = ApprovalInbox(erp)
    agent = AuthorityAgent(erp, "ECLARKE", llm=LLM(...), inbox=inbox)
    agent.respond("Reorder 2,000 of the city e-bike battery packs ...")     # preview, asks to confirm
    agent.respond("Yes, go ahead.")                                 # request raised, one item in Daniel's inbox
    inbox.decide(inbox.pending(erp.session("DOKAFOR"))[0]["id"], erp.session("DOKAFOR"), "approve")  # Daniel's own session
    agent.after_decision()                                          # read back from Ledgerline, order, release, read back
    agent.audit.joined()                                            # who asked, what it saw, what it did, who approved

The seven pieces, in the order the lecture teaches them:

  1. Identity       passthrough(erp, user) binds every tool to the user's own Ledgerline session; service_account() is
                    the integration account IT made "for the bot". scopes() is the greyed-out menu, as data.
  2. The matrix     POL-APR-002 read from ledgerline/docs/approval-matrix.md into MATRIX; route() walks it.
  3. The inbox      ApprovalInbox: pending items from Ledgerline's own approval table, one-tap decide() done in the
                    APPROVER's session (never the agent's), a Slack-style message through the Lecture 3 outbox
                    MCP server, and the Supplier Policy §3.4 onboarding file (Ledgerline has no screen for it).
  4. Preview/commit a commit is refused unless the same order was previewed in an EARLIER user turn.
  5. Read-back      after every write, the document is read back from Ledgerline in the user's session.
  6. Audit          AuditLog joins the agent's own trace with Ledgerline's audit_trail rows each step caused.
  7. Guardrails     NeverEventGuard refuses writes that would cause NE1 to NE5, and gates the reply (NE5).

Everything here is deterministic code: no model is called in this file.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import pathlib
import re
import threading
from dataclasses import dataclass, field

from ..erp.engine import ERP, SERVICES, ServiceTimeout, Session
from ..scenarios import DONE_WORDS
from .tools import CORE, EXTRA, STATUS, TOOLS, IntentTools, name_key

DOCS = pathlib.Path(__file__).resolve().parents[1] / "docs"
NOT_DONE = re.compile(r"draft|pending|approval|waiting|not (?:yet )?released|closed", re.I)
SERVICE_ROLES = {"SYS-ADMIN"}  # POL-APR-002 §4.2: integration and service accounts


def inr(x) -> str:
    """£ with digit grouping: 285600 -> £285,600."""
    if x is None:
        return "-"
    x = float(x)
    whole, paise = int(round(x * 100)) // 100, int(round(x * 100)) % 100
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        s = head + "," + tail
    return "£" + s + (f".{paise:02d}" if paise else "")


# =============================================================================== 1. identity
@dataclass
class Identity:
    """Who the tools act as. `user` asked; `acts_as` is the Ledgerline user whose session runs every call."""
    kind: str               # "passthrough" | "service_account"
    user: str               # the person in the chat (ECLARKE)
    acts_as: str            # the Ledgerline user the session belongs to (ECLARKE, or SVC_AGENT)
    session: Session

    @property
    def erp(self) -> ERP:
        return self.session.erp

    def as_dict(self) -> dict:
        return {"kind": self.kind, "user": self.user, "acts_as": self.acts_as}


def passthrough(erp: ERP, user: str | None = None, token: str | None = None) -> Identity:
    """The agent acts AS the user. In the app the user comes from her own sign-in token (erp.sessions[token]),
    so the agent can never hold more rights than the person typing."""
    if token is not None:
        if token not in erp.sessions:
            raise PermissionError("ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
        user = erp.sessions[token]
    u = erp.session(user)
    return Identity("passthrough", u.user_id, u.user_id, u)


def service_account(erp: ERP, on_behalf_of: str = "ECLARKE", account: str = "SVC_AGENT") -> Identity:
    """The integration account IT made "for the bot": role SYS-ADMIN, every service, no limit. Lecture 1's agent."""
    return Identity("service_account", on_behalf_of.upper(), account, erp.session(account))


def scopes(erp: ERP, user: str) -> dict:
    """The greyed-out menu, as data: which screens, services and intent tools this user's role allows.
    Read through the user's own session (usr_roles), so it is exactly what Ledgerline enforces."""
    from ..server import load_screens

    s = erp.session(user)
    u = s.call("usr_get", user_id=user)["data"]
    svcs = set(s.call("usr_roles", user_id=user)["data"]["svcs"])
    ok = lambda svc: "*" in svcs or svc in svcs  # noqa: E731
    menu = []
    for code, sc in sorted(load_screens().items()):
        roles = sc.get("roles") or ["ALL"]
        allowed = "ALL" in roles or u["role_cd"] in roles or u["role_cd"] == "SYS-ADMIN"
        menu.append({"screen": code, "menu": sc.get("menu", code), "allowed": allowed})
    tools = []
    for n in CORE + EXTRA:
        t = TOOLS[n]
        missing = [x for x in t.services if not ok(x)]
        tools.append({"tool": n, "writes": t.writes, "allowed": not missing, "missing_services": missing})
    writes = sorted(n for n, sv in SERVICES.items() if sv.kind == "write" and ok(n))
    return {"user": user, "name": u["name"], "role": u["role_cd"], "limit": u["appr_limit"],
            "manager": u["manager_id"], "services": len(SERVICES) if "*" in svcs else len(svcs),
            "write_services": writes, "menu": menu, "tools": tools}


def tools_for(identity: Identity, names: list[str] | None = None) -> IntentTools:
    """IntentTools bound to the identity's session, showing the model only the tools its role allows
    (the greyed-out menu, reborn as a shorter tool list)."""
    sc = scopes(identity.erp, identity.acts_as)
    allowed = {t["tool"] for t in sc["tools"] if t["allowed"]}
    return IntentTools(identity.session, [n for n in (names or CORE + EXTRA) if n in allowed])


class MCPIntentTools:
    """The intent tools reached over MCP (Lecture 3's server), the server bound to ONE user's session.
    Same .names / .schemas() / .call() shape as IntentTools, so anything above cannot tell the difference."""

    def __init__(self, session: Session, names: list[str] | None = None):
        from ..mcp_server import MCPClient, build_ledgerline_server

        self.s = session
        self.names = list(names or CORE + EXTRA)
        self._schemas = IntentTools(session, self.names).schemas()
        self.server = build_ledgerline_server(session.erp, session.user_id, self.names)
        self.client = MCPClient(self.server)

    def schemas(self):
        return self._schemas

    def call(self, name: str, args: dict) -> dict:
        res = self.client.call_tool(name, {k: v for k, v in (args or {}).items() if v is not None})
        txt = self.client.text(res)
        try:
            return json.loads(txt)
        except ValueError:
            return {"ok": False, "error": txt}

    def call_json(self, name, args):
        return json.dumps(self.call(name, args), default=str)

    def close(self):
        self.client.close()


# =============================================================================== 2. the approval matrix
def load_matrix(path: pathlib.Path = DOCS / "approval-matrix.md") -> dict:
    """POL-APR-002 §3.1 as data: {role: limit}. Read from the policy document itself, so the code and the
    document cannot drift apart without a test noticing (NB5 compares it with Ledgerline's user records)."""
    out = {}
    for line in path.read_text().splitlines():
        m = re.match(r"\|\s*([A-Z]+-?[A-Z]*)\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
        if not m or m.group(1) in ("Role",):
            continue
        role, name, lim = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        if role.startswith("-"):
            continue
        num = re.sub(r"[^\d]", "", lim)
        out[role] = {"role": role, "title": name, "limit": float(num) if num else 0.0, "text": lim}
    return out


MATRIX = load_matrix()
RULES = [
    ("POL-APR-002 §2.1", "Every limit is on the gross value including VAT of one document."),
    ("POL-APR-002 §3.2", "Within the raiser's own limit, the document is approved when submitted."),
    ("POL-APR-002 §3.3", "Above it, the raiser's manager; if the manager's limit does not cover it, up the line."),
    ("POL-APR-002 §3.4", "Above £5,000,000: the Managing Director, in writing, outside Ledgerline."),
    ("POL-APR-002 §4.1", "Nobody approves a document they raised."),
    ("POL-APR-002 §4.2", "Service accounts (SYS-ADMIN, e.g. SVC_AGENT) have no approval authority."),
    ("POL-SUP-003 §3.4", "The purchase manager approves a new supplier's onboarding file before it is created."),
]


def _limit(erp: ERP, uid: str) -> float:
    u = erp.user(uid)
    if u["role_cd"] in SERVICE_ROLES:
        return 0.0
    return MATRIX.get(u["role_cd"], {}).get("limit", 0.0)


def route(erp: ERP, requester: str, gross: float) -> dict:
    """Who must sign a document of this gross value raised by `requester`: POL-APR-002 walked as data.
    A service account as requester is routed as nobody: it has no authority and no manager (§4.2)."""
    u = erp.user(requester)
    hops = [{"user": requester, "name": u["name"], "role": u["role_cd"], "limit": _limit(erp, requester),
             "covers": gross <= _limit(erp, requester), "why": "raiser"}]
    if u["role_cd"] in SERVICE_ROLES:
        return {"requester": requester, "gross": gross, "needs_approval": True, "approver": None, "hops": hops,
                "rule": "POL-APR-002 §4.2", "outside_ledgerline": False,
                "note": "A service account has no approval authority and no manager: nobody can be routed."}
    if hops[0]["covers"]:
        return {"requester": requester, "gross": gross, "needs_approval": False, "approver": requester, "hops": hops,
                "rule": "POL-APR-002 §3.2", "outside_ledgerline": False, "note": "within the raiser's own limit"}
    nxt = u["manager_id"]
    while nxt:
        m = erp.user(nxt)
        lim = _limit(erp, nxt)
        hops.append({"user": nxt, "name": m["name"], "role": m["role_cd"], "limit": lim, "covers": gross <= lim,
                     "why": "manager"})
        if gross <= lim:
            return {"requester": requester, "gross": gross, "needs_approval": True, "approver": nxt, "hops": hops,
                    "rule": "POL-APR-002 §3.3", "outside_ledgerline": False,
                    "note": f"above {u['name'].split()[0]}'s {inr(hops[0]['limit'])}: {m['name']} signs"}
        nxt = m["manager_id"]
    return {"requester": requester, "gross": gross, "needs_approval": True, "approver": None, "hops": hops,
            "rule": "POL-APR-002 §3.4", "outside_ledgerline": True, "note": "the Managing Director, in writing, outside Ledgerline"}


def route_onboarding(erp: ERP, proposer: str) -> dict:
    """Supplier Policy §3.4: the purchase manager above the proposer approves the onboarding file."""
    hops, nxt = [], erp.user(proposer)["manager_id"]
    while nxt:
        m = erp.user(nxt)
        hops.append({"user": nxt, "role": m["role_cd"]})
        if m["role_cd"] == "PUR-MGR":
            return {"approver": nxt, "hops": hops, "rule": "POL-SUP-003 §3.4"}
        nxt = m["manager_id"]
    return {"approver": None, "hops": hops, "rule": "POL-SUP-003 §3.4"}


def may_approve(erp: ERP, approver: str, requester: str, gross: float | None) -> tuple[bool, str]:
    """POL-APR-002 §4.1, §4.2 and §3.1 for one approver and one document."""
    a = erp.user(approver)
    if not a:
        return False, "no such user"
    if a["role_cd"] in SERVICE_ROLES:
        return False, "a service account has no approval authority (POL-APR-002 §4.2)"
    if approver == requester:
        return False, "nobody approves a document they raised (POL-APR-002 §4.1)"
    if gross is not None and _limit(erp, approver) < gross:
        return False, f"{inr(gross)} is above {a['name']}'s limit of {inr(_limit(erp, approver))} (POL-APR-002 §3.1)"
    return True, "ok"


def properly_approved(erp: ERP, po: dict) -> tuple[bool, str]:
    """Is this order's approval one the matrix accepts? approved_by must be a person whose limit covers the gross;
    it may be the raiser only when the gross is within the raiser's own limit (§3.2)."""
    by, raiser, gross = po.get("approved_by"), po.get("created_by"), po.get("gross_value") or 0
    if not by:
        return False, "nobody has approved it"
    if erp.user(by)["role_cd"] in SERVICE_ROLES:
        return False, f"approved by the service account {by}, which has no approval authority (POL-APR-002 §4.2)"
    if by == raiser:
        return (gross <= _limit(erp, raiser),
                "within the raiser's own limit" if gross <= _limit(erp, raiser) else
                f"self-approved above the raiser's limit of {inr(_limit(erp, raiser))} (POL-APR-002 §4.1)")
    ok, why = may_approve(erp, by, raiser, gross)
    return ok, ("approved by " + erp.user(by)["name"]) if ok else why


# =============================================================================== 6. the audit log
class AuditLog:
    """Who asked, what the agent saw, what it did, who approved; joined with the rows Ledgerline wrote for each step.

    Every entry records the Ledgerline audit_trail rows that appeared while it ran (ids after `mark()`), so the join is
    exact: a tool call owns the service calls it caused. Rows nobody claimed (a graph node's own reads, a workflow
    running in the background) are attached to the turn they happened in, so every Ledgerline row lands somewhere."""

    def __init__(self, erp: ERP):
        self.erp = erp
        self.entries: list[dict] = []
        self.claimed: set[int] = set()
        self._lock = threading.RLock()

    def mark(self) -> int:
        r = self.erp.q1("SELECT max(id) m FROM audit_trail")
        return (r or {}).get("m") or 0

    def rows_since(self, mark: int) -> list[dict]:
        rows = self.erp.q("SELECT id, ts, user_id, svc, rc, err_cd, payload FROM audit_trail WHERE id>? ORDER BY id", mark)
        out = []
        for r in rows:
            if r["id"] in self.claimed:
                continue
            self.claimed.add(r["id"])
            out.append({"id": r["id"], "ts": r["ts"], "user": r["user_id"], "svc": r["svc"], "rc": r["rc"],
                        "err": r["err_cd"], "kind": SERVICES[r["svc"]].kind if r["svc"] in SERVICES else "?"})
        return out

    def add(self, kind: str, actor: str, conv: str = "", mark: int | None = None, **fields) -> dict:
        with self._lock:
            e = {"seq": len(self.entries) + 1, "t": self.erp._clock.isoformat(timespec="seconds"), "conv": conv,
                 "kind": kind, "actor": actor, **fields}
            if mark is not None:
                e["ledgerline"] = self.rows_since(mark)
            self.entries.append(e)
            return e

    def for_conv(self, conv: str) -> list[dict]:
        return [e for e in self.entries if e.get("conv") == conv]

    def joined(self, conv: str | None = None) -> list[dict]:
        """The audit trail of a conversation: agent entries in order, each with its Ledgerline rows."""
        return copy.deepcopy(self.entries if conv is None else self.for_conv(conv))

    def ledgerline_rows(self) -> list[dict]:
        return self.erp.q("SELECT id, ts, user_id, svc, rc, err_cd FROM audit_trail ORDER BY id")

    def summary(self, conv: str | None = None) -> dict:
        es = self.joined(conv)
        rows = [r for e in es for r in e.get("ledgerline", [])]
        return {"entries": len(es), "ledgerline_rows": len(rows),
                "ledgerline_writes": sum(1 for r in rows if r["kind"] == "write" and r["rc"] != "E"),
                "users_in_ledgerline": sorted({r["user"] for r in rows}),
                "refusals": sum(1 for e in es if e["kind"] == "refused"),
                "read_backs": sum(1 for e in es if e.get("read_back"))}


def summarize(name: str, out: dict) -> str:
    """What the agent saw from a tool, in one line (for the trace beside the chat and the audit viewer)."""
    if not isinstance(out, dict):
        return str(out)[:160]
    if not out.get("ok", True):
        return f"refused: {out.get('error', '')}"[:220]
    if out.get("preview"):
        p = out["preview"]
        s = f"preview · {inr(p.get('gross_value'))} gross"
        if p.get("needs_approval"):
            s += f" > limit {inr(p.get('your_limit'))} → {p.get('approver')}"
        return s + (f" · warnings: {len(out.get('warnings') or [])}" if out.get("warnings") else "")
    if out.get("status") == "WAITING FOR APPROVAL":
        return f"{out.get('request_no')} · WAITING FOR APPROVAL by {out.get('approver')}"
    if out.get("po_no"):
        s = f"{out['po_no']} · {out.get('status_code') or out.get('status') or out.get('message', '')}"
        if out.get("approved_by"):
            s += f" · approved by {out['approved_by']}"
        if out.get("warning"):
            s += " · " + str(out["warning"])[:80]
        return s
    if name == "find_item":
        return "; ".join(f"{i['item_code']}" for i in out.get("items", [])[:3]) or out.get("note", "")
    if name == "find_supplier":
        m = out.get("matches") or []
        return (f"{m[0]['name']} {m[0]['supplier_code']} ({m[0]['match']})" if m else "no match") + \
            (f" · {out['hint'][:60]}" if out.get("hint") else "")
    if name == "check_cost_centre":
        if "open" in out and isinstance(out["open"], bool):
            return f"{out.get('code')} {'open' if out['open'] else 'CLOSED ' + str(out.get('closed_on'))}"
        return "open: " + ", ".join(c["code"] for c in out.get("open", []))
    if name == "stock_position":
        w = (out.get("warehouses") or [{}])[0]
        return f"{w.get('on_hand', 0):,} on hand, {w.get('days_of_cover')} days"
    if out.get("supplier_code"):
        return f"{out['supplier_code']} · {out.get('status', '')} · certificate {out.get('cell_safety_certificate', '')}"
    return json.dumps(out, default=str)[:160]


# =============================================================================== 3. the inbox, and how it is announced
class Notifier:
    """Posts Slack-style messages through the Lecture 3 marketplace outbox, over MCP (post_message).
    In the sandbox nothing leaves the machine: messages land in an Outbox you can read."""

    def __init__(self, outbox=None, use_mcp: bool = True):
        from ..mcp_server import Outbox

        self.outbox = outbox or Outbox()
        self.use_mcp, self.client, self.via = use_mcp, None, "direct"
        self.meta: dict[str, dict] = {}
        if use_mcp:
            try:
                from ..mcp_server import MCPClient, build_outbox_server

                self.client = MCPClient(build_outbox_server(self.outbox))
                self.via = "mcp"
            except Exception as e:  # noqa: BLE001  (no fastmcp installed: fall back, and say so)
                self.via = f"direct ({type(e).__name__})"

    def post(self, channel: str, text: str, **meta) -> dict:
        if self.client is not None:
            res = self.client.call_tool("post_message", {"channel": channel, "text": text})
            try:
                msg = json.loads(self.client.text(res))
            except ValueError:
                msg = self.outbox.items[-1]
        else:
            msg = {"ok": True, **self.outbox.add("chat", channel=channel, text=text)}
        self.meta[msg["id"]] = meta
        return {**msg, **meta}

    def messages(self) -> list[dict]:
        return [{**m, **self.meta.get(m["id"], {})} for m in self.outbox.items]

    def close(self):
        if self.client is not None:
            self.client.close()


@dataclass
class DocKind:
    """How the inbox reads one kind of document and how its approver decides it, both in a given session."""
    doc_type: str
    read: object      # (session, doc_no) -> {"value", "title", "summary", "status"}
    decide: object    # (session, doc_no, approve: bool, comment) -> Ledgerline envelope {rc, err_cd, msg, data}
    rule: str = "POL-APR-002 §3.3"


def _read_pr(s, doc_no):
    d = s.call("pr_get", pr_no=doc_no)["data"] or {}
    ln = (d.get("lines") or [{}])[0]
    return {"value": d.get("est_value"), "title": f"Purchase request {doc_no}", "status": d.get("status"),
            "summary": f"{ln.get('qty', 0):,} × {ln.get('itm_cd')} · {d.get('cc_cd')} · {inr(d.get('est_value'))} gross (est.)"}


def _read_po(s, doc_no):
    d = s.call("po_get", po_no=doc_no)["data"] or {}
    ln = (d.get("lines") or [{}])[0]
    return {"value": d.get("gross_value"), "title": f"Purchase order {doc_no}", "status": d.get("status"),
            "summary": f"{ln.get('qty', 0):,} × {ln.get('itm_cd')} @ {inr(ln.get('rate'))} · {d.get('sup_cd')} · "
                       f"{inr(d.get('gross_value'))} gross"}


PR_KIND = DocKind("PR", _read_pr, lambda s, n, ok, c: s.call("pr_approve", pr_no=n, decision="A" if ok else "R", comment=c))
PO_KIND = DocKind("PO", _read_po, lambda s, n, ok, c: s.call("po_approve", po_no=n, comment=c) if ok
                  else s.call("po_reject", po_no=n, comment=c or "rejected"))


SLACK = {"ECLARKE": "@emma", "DOKAFOR": "@daniel", "LMORENO": "@luis", "HWEBER": "@henrik", "ATANAKA": "@aiko"}


class ApprovalInbox:
    """Pending approvals for a person, and the one-tap decision, done in THAT person's own Ledgerline session.

    Purchase requests and orders: Ledgerline's own approval table is the record (sp_appr_route writes it); the inbox reads
    it through the approver's session (po_pending_appr) and decides through it (pr_approve / po_approve / po_reject),
    so Ledgerline itself checks the approver's limit and that he did not raise the document.
    Supplier onboarding (Supplier Policy §3.4): Ledgerline has no approval for it, so the inbox keeps that file itself.
    The agent never holds an approver's session: decide() must be handed one, and in the app it comes from the
    approver's own sign-in."""

    def __init__(self, erp: ERP, notifier: Notifier | None = None, audit: AuditLog | None = None, durable=None,
                 base_url: str = "/app/inbox"):
        self.erp, self.notifier, self.audit, self.durable = erp, notifier, audit, durable
        self.base_url = base_url
        self.items: dict[str, dict] = {}
        self._lock = threading.RLock()
        self.kinds: dict[str, DocKind] = {"PR": PR_KIND, "PO": PO_KIND}

    def register_kind(self, kind: "DocKind"):
        """A capstone module's own document (leave, payment, claim ...): how to read it and how its approver decides.
        Ledgerline's approval table carries every module's documents, so the rest of the inbox works unchanged (A5)."""
        self.kinds[kind.doc_type] = kind

    def _new_id(self) -> str:
        return f"APR-{len(self.items) + 1:04d}"

    def _announce(self, it: dict):
        if not self.notifier:
            return
        who = SLACK.get(it["approver"], it["approver"])
        txt = (f"{it['title']} · {it['summary']} · raised by {self.erp.user(it['requested_by'])['name']} "
               f"[Approve] [Reject] {self.base_url}#{it['id']}")
        m = self.notifier.post(who, txt, item=it["id"], actions=["approve", "reject"], approver=it["approver"])
        it["messages"].append(m["id"])
        if self.audit:
            self.audit.add("notify", "agent", it.get("conv", ""), what=f"posted to {who} via {self.notifier.via}",
                           item=it["id"], message=m["id"], text=txt)

    # ---- filing
    def track(self, doc_no: str, requester: str, conv: str = "", summary: str = "", announce: bool = True) -> dict | None:
        """A document Ledgerline has routed for approval: make it an inbox item (once) and announce it."""
        with self._lock:
            for it in self.items.values():
                if it["doc_no"] == doc_no and it["status"] == "PENDING":
                    return it
            row = self.erp.q1("SELECT * FROM approval WHERE doc_no=? AND status='PENDING' ORDER BY appr_id DESC", doc_no)
            if not row:
                return None
            s = self.erp.session(requester)
            k = self.kinds.get(row["doc_type"])
            if k is None:
                return None
            info = k.read(s, doc_no)
            value, title = info.get("value"), info.get("title") or f"{row['doc_type']} {doc_no}"
            summary = summary or info.get("summary", "")
            r = route(self.erp, requester, value) if value is not None else {"rule": k.rule, "note": ""}
            r.setdefault("rule", k.rule)
            it = {"id": self._new_id(), "kind": row["doc_type"], "doc_no": doc_no, "title": title, "summary": summary,
                  "value": value, "requested_by": requester, "approver": row["approver"], "status": "PENDING",
                  "ledgerline_appr_id": row["appr_id"], "conv": conv, "route": r, "messages": [], "decided_by": None,
                  "rule": k.rule or r["rule"]}
            self.items[it["id"]] = it
            if self.audit:
                self.audit.add("approval_request", "agent", conv, item=it["id"], doc=doc_no, approver=row["approver"],
                               what=f"{doc_no} routed by Ledgerline to {row['approver']} ({r['rule']}: {r['note']})")
            if announce:
                self._announce(it)
            return it

    def file_onboarding(self, proposer: str, supplier: dict, conv: str = "") -> dict:
        """Supplier Policy §3.4: the onboarding file goes to the purchase manager before the supplier is created."""
        with self._lock:
            hit = self.onboarding_for(supplier.get("name"), supplier.get("vat_no"))
            if hit:
                return hit
            r = route_onboarding(self.erp, proposer)
            it = {"id": self._new_id(), "kind": "SUP", "doc_no": f"ONB/{supplier.get('vat_no') or name_key(supplier['name'])}",
                  "title": f"New supplier onboarding · {supplier['name']}",
                  "summary": f"{supplier['name']}, {supplier.get('city')}, {supplier.get('state')} · VAT number {supplier.get('vat_no')}",
                  "value": None, "requested_by": proposer, "approver": r["approver"], "status": "PENDING",
                  "supplier": supplier, "conv": conv, "route": r, "messages": [], "decided_by": None,
                  "rule": "POL-SUP-003 §3.4"}
            self.items[it["id"]] = it
            if self.audit:
                self.audit.add("approval_request", "agent", conv, item=it["id"], doc=it["doc_no"], approver=r["approver"],
                               what=f"onboarding file for {supplier['name']} sent to {r['approver']} (POL-SUP-003 §3.4)")
            self._announce(it)
            return it

    def onboarding_for(self, name: str | None, vat_no: str | None) -> dict | None:
        for it in self.items.values():
            if it["kind"] != "SUP" or it["status"] == "REJECTED":
                continue
            s = it["supplier"]
            if (vat_no and s.get("vat_no") == vat_no) or (name and name_key(s["name"]) == name_key(name)):
                return it
        return None

    # ---- reading
    def pending(self, session: Session) -> list[dict]:
        """What waits for this person: Ledgerline's approval table read in HIS session, plus onboarding files."""
        me = session.user_id
        rows = (session.call("po_pending_appr")["data"] or {}).get("rows", [])
        out = []
        for r in rows:
            it = next((x for x in self.items.values() if x["doc_no"] == r["doc_no"] and x["status"] == "PENDING"), None)
            if it is None:  # routed in Ledgerline but not by our agent (e.g. raised on the old screen): still show it
                it = self.track(r["doc_no"], r["requested_by"], announce=False) or {"doc_no": r["doc_no"]}
            out.append(it)
        out += [x for x in self.items.values() if x["kind"] == "SUP" and x["status"] == "PENDING" and x["approver"] == me]
        return copy.deepcopy(out)

    def get(self, item_id: str) -> dict:
        return self.items[item_id]

    # ---- deciding
    def decide(self, item_id: str, session: Session, decision: str = "approve", comment: str = "") -> dict:
        """One tap. Runs in the APPROVER's session; Ledgerline checks his limit and that he did not raise it."""
        with self._lock:
            it = self.items[item_id]
            by = session.user_id
            mark = self.audit.mark() if self.audit else None
            approve = decision.lower().startswith("a")
            if it["status"] != "PENDING":
                return {"ok": False, "error": f"{it['doc_no']} is already {it['status']}", "item": copy.deepcopy(it)}
            if it["kind"] == "SUP":
                ok, why = may_approve(self.erp, by, it["requested_by"], None)
                if ok and self.erp.user(by)["role_cd"] not in ("PUR-MGR", "PLANT-HEAD"):
                    ok, why = False, "only the purchase manager approves an onboarding file (POL-SUP-003 §3.4)"
                if not ok:
                    res = {"rc": "E", "err_cd": "POL-SUP-003", "msg": why.upper()}
                else:
                    it["status"] = "APPROVED" if approve else "REJECTED"
                    res = {"rc": "S", "msg": f"ONBOARDING FILE {it['status']} BY {by}"}
            else:
                wid = self._workflow_for(it["doc_no"]) if (self.durable and it["kind"] == "PR") else None
                k = self.kinds[it["kind"]]
                if wid:  # Lecture 7: Daniel's session approves in Ledgerline, then the workflow is signalled
                    res = self.durable.approve(wid, by=by, decision="A" if approve else "R", comment=comment)
                else:
                    res = k.decide(session, it["doc_no"], approve, comment)
                if res["rc"] != "E":  # read the decision back from Ledgerline, in the approver's session
                    st = k.read(session, it["doc_no"]).get("status")
                    it["status"] = {"AP": "APPROVED", "RJ": "REJECTED", "RL": "APPROVED"}.get(st, it["status"])
                    it["ledgerline_status"] = st
            if res["rc"] == "E":
                out = {"ok": False, "error": f"Ledgerline refused: {res['msg']} ({res.get('err_cd')})", "item": copy.deepcopy(it)}
                if self.audit:
                    self.audit.add("refused", by, it.get("conv", ""), mark=mark, item=item_id, doc=it["doc_no"],
                                   what=f"{by} tried to {'approve' if approve else 'reject'} {it['doc_no']}: {res['msg']}")
                return out
            it.update(decided_by=by, comment=comment, decided_at=self.erp._clock.isoformat(timespec="seconds"))
            if self.audit:
                self.audit.add("approval", by, it.get("conv", ""), mark=mark, item=item_id, doc=it["doc_no"],
                               decision=it["status"], what=f"{self.erp.user(by)['name']} {it['status'].lower()} "
                               f"{it['doc_no']} in his own session ({it['rule']})")
            if self.notifier:
                self.notifier.post(SLACK.get(it["requested_by"], it["requested_by"]),
                                   f"{it['doc_no']} {it['status'].lower()} by {self.erp.user(by)['name']}.",
                                   item=item_id, actions=[])
            return {"ok": True, "ledgerline": res, "item": copy.deepcopy(it)}

    def _workflow_for(self, doc_no: str) -> str | None:
        for wid in list(self.durable.handles):
            try:
                st = self.durable.status(wid)
            except Exception:  # noqa: BLE001
                continue
            if st.get("request_no") == doc_no and st.get("stage") == "waiting for approval":
                return wid
        return None


# =============================================================================== 7. never-events, refused in code
class NeverEventGuard:
    """Refuses writes that would cause a never-event, whatever the model asked for. Reads Ledgerline itself; trusts nothing
    the model says ("Daniel said it's fine" changes nothing here).

        NE1  above-limit order approved without a human approver   release/commit/approve checks, identity check
        NE2  duplicate order in one conversation                   a second live order for the same item+supplier
        NE3  lithium-cell part from a supplier with no certificate  certificate re-read from Ledgerline at commit
        NE4  duplicate supplier                                     near-match or same VAT number; plus §3.4 approval
        NE5  "done" while the order sits in Draft                   reply gate on the read-back status
    """

    def __init__(self, erp: ERP, end_user: str, identity: Identity, inbox: ApprovalInbox | None = None):
        self.erp, self.end_user, self.identity, self.inbox = erp, end_user, identity, inbox
        self.refusals: list[dict] = []

    def _no(self, ne: str, rule: str, why: str, next_step: str) -> dict:
        r = {"ok": False, "refused": ne, "rule": rule, "error": f"Refused by the guardrail ({ne}): {why}",
             "next_step": next_step, "ledgerline_code": "GUARD-" + ne}
        self.refusals.append(r)
        return r

    # ---- facts read from Ledgerline
    def _cert_ok(self, sup: str) -> bool:
        return bool(self.erp.q1("SELECT 1 FROM sup_cert WHERE sup_cd=? AND cert_type='UN38.3' AND valid_to>=?",
                                sup, self.erp.today))

    def _food(self, itm: str) -> bool:
        r = self.erp.q1("SELECT cell_safety FROM item WHERE itm_cd=?", itm)
        return bool(r and r["cell_safety"])

    def _gross(self, qty, rate, tax_cd) -> float:
        t = self.erp.q1("SELECT rate FROM tax_code WHERE tax_cd=?", tax_cd) or {"rate": 0.20}
        return round(qty * rate * (1 + t["rate"]), 2)

    def _live_today(self, sup: str, itm: str) -> list[dict]:
        return [o for o in self.erp.orders(sup_cd=sup, itm_cd=itm) if o["created_on"] >= self.erp.today
                and o["status"] not in ("CN", "RJ")]

    # ---- the checks
    def check_order(self, sup: str, itm: str, gross: float | None, key: str | None = None) -> dict | None:
        """Before an order is written (NE1 for a service account, NE2, NE3)."""
        if itm and sup and self._food(itm) and not self._cert_ok(sup):
            return self._no("NE3", "Purchase Policy §6.2", f"{itm} is a lithium-cell part and {sup} has no valid battery-safety "
                            "certificate in Ledgerline.", "Ask the user for the certificate's reference and expiry, record it, "
                            "then try again. Nothing was written.")
        live = [o for o in self._live_today(sup, itm) if not key or o["client_ref"] != key]
        if live:
            return self._no("NE2", "POL-APR-002 §2.3", f"{live[0]['po_no']} for {itm} from {sup} already exists today "
                            f"({live[0]['status']}). A second order would duplicate (or split) it.",
                            f"Use {live[0]['po_no']}: amend it if the quantity must change.")
        if self.identity.kind == "service_account" and gross is not None and gross > _limit(self.erp, self.end_user):
            return self._no("NE1", "POL-APR-002 §4.2", f"{inr(gross)} is above {self.end_user}'s limit of "
                            f"{inr(_limit(self.erp, self.end_user))}, and on the service account Ledgerline would approve it "
                            "itself. A service account has no approval authority.",
                            "Run the agent as the user (identity passthrough) so Ledgerline routes it to her manager.")
        return None

    def check_release(self, po_no: str) -> dict | None:
        po = self.erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
        if not po or po["status"] != "AP":
            return None  # only an approved order can be released; Ledgerline refuses the rest itself (ERR-PO-0715)
        ok, why = properly_approved(self.erp, po)
        if not ok:
            return self._no("NE1", "POL-APR-002 §3–4", f"{po_no} ({inr(po['gross_value'])}) is not properly approved: {why}.",
                            "It must be approved by a person whose limit covers it, in that person's own session.")
        return None

    def check_amend(self, po_no: str, qty) -> dict | None:
        """An amendment that grows an order is a new approval question (v2 of the guard: v1 missed this path;
        the adversarial run found it, a split order amended back up to £285,600 on the service account)."""
        po = self.erp.q1("SELECT h.*, l.qty, l.rate FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE h.po_no=?", po_no or "")
        if not po or qty in (None, ""):
            return None
        try:
            gross = self._gross(int(float(qty)), po["rate"], po["tax_cd"])
        except (TypeError, ValueError):
            return None
        if self.identity.kind == "service_account" and gross > _limit(self.erp, self.end_user) and gross > po["gross_value"]:
            return self._no("NE1", "POL-APR-002 §4.2", f"amending {po_no} to {inr(gross)} takes it above {self.end_user}'s "
                            "limit, and on the service account Ledgerline would approve it itself.",
                            "Run as the user so Ledgerline sends the amendment to her manager.")
        return None

    def check_supplier(self, name: str, city: str, vat_no: str | None) -> dict | None:
        same = self.erp.q1("SELECT sup_cd, name, status FROM supplier WHERE vat_no=?", vat_no) if vat_no else None
        if same:
            return self._no("NE4", "Supplier Policy §6.1", f"VAT number {vat_no} is already {same['name']} ({same['sup_cd']}).",
                            f"Use {same['sup_cd']}; do not register them again.")
        k = name_key(name)
        for s in self.erp.q("SELECT sup_cd, name, city, status FROM supplier WHERE status='ACTIVE'"):
            if (s["city"] or "").lower() == (city or "").lower() and \
                    difflib.SequenceMatcher(None, k, name_key(s["name"])).ratio() >= 0.8:
                return self._no("NE4", "Supplier Policy §6.2", f"'{name}' in {city} is {s['name']} ({s['sup_cd']}).",
                                f"Use {s['sup_cd']}. A new code needs proof it is a different firm (a different VAT number).")
        return None

    def check_approval_by_agent(self, what: str) -> dict:
        return self._no("NE1", "POL-APR-002 §4.1–4.2", f"the agent tried to {what}. Approval is the approver's own act, "
                        "in his own session, never the agent's.", "Send it to the approver's inbox and wait.")

    def gate_reply(self, reply: str, docs: dict[str, dict]) -> tuple[str, dict | None]:
        """NE5. If the reply claims done while an order written in this conversation is not released, the reply is
        replaced by one written by code from the read-back status."""
        live = {k: v for k, v in docs.items() if v.get("status_code") not in ("CN", "RJ", None)}
        if not live or not DONE_WORDS.search(reply or "") or NOT_DONE.search(reply or ""):
            return reply, None
        if all(v.get("status_code") == "RL" for v in live.values()):
            return reply, None
        lines = []
        for po, v in live.items():
            if v.get("status_code") == "RL":
                continue
            s = f"{po} is {STATUS.get(v['status_code'], v['status_code'])} in Ledgerline, not released to the supplier."
            if v.get("warning") == "W-CC-114":
                s += f" Cost centre {v.get('cost_centre')} is closed; it needs an open cost centre."
            lines.append(s)
        r = self._no("NE5", "Purchase Policy §4.2", "the reply said done while " + "; ".join(lines), "Tell the user the real status.")
        return "\n".join(lines), r


# =============================================================================== 4, 5. the wrapper around the tools
def _order_sig(args: dict) -> tuple:
    return (args.get("supplier_code"), args.get("item_code"), int(float(args.get("quantity") or 0)),
            args.get("cost_centre"), args.get("need_by"))


class AuthorityTools:
    """The intent tools with authority and proof around them. Same .names / .schemas() / .call() as IntentTools.

    On every call: audit it (with the Ledgerline rows it caused). On every write: the guardrail first; preview-then-commit
    across a user turn; Supplier Policy §3.4 for a new supplier; after the write, read the document back from Ledgerline in
    the identity's session; if Ledgerline routed it for approval, file it in the inbox (one Slack-style message)."""

    WRITES = {"create_purchase_order", "release_purchase_order", "amend_purchase_order", "register_supplier",
              "record_certificate"}

    def __init__(self, inner, identity: Identity, audit: AuditLog | None = None, inbox: ApprovalInbox | None = None,
                 guard: bool = True, readback: bool = True, preview_rule: bool = True, conv: str = "c1",
                 expose_readback: bool = True, write_guard: bool = True):
        self.inner, self.identity = inner, identity
        self.write_guard = write_guard
        self.expose_readback = expose_readback
        self.erp = identity.erp
        self.audit = audit or AuditLog(self.erp)
        self.inbox, self.conv = inbox, conv
        self.guard = NeverEventGuard(self.erp, identity.user, identity, inbox) if guard else None
        self.readback, self.preview_rule = readback, preview_rule
        self.names = list(inner.names)
        self.s = identity.session
        self.turn = 0
        self.previews: dict[tuple, int] = {}   # order signature -> the user turn it was previewed in
        self.docs: dict[str, dict] = {}        # every order this conversation wrote, with its read-back
        self.requests: dict[str, dict] = {}

    def schemas(self):
        return self.inner.schemas()

    def manifest(self):
        return self.inner.manifest() if hasattr(self.inner, "manifest") else []

    def begin_turn(self):
        self.turn += 1

    def call_json(self, name, args):
        return json.dumps(self.call(name, args), default=str)

    # ---- the one entry point
    def call(self, name: str, args: dict) -> dict:
        args = dict(args or {})
        mark = self.audit.mark()
        writes = name in self.WRITES and (name not in ("create_purchase_order", "register_supplier") or bool(args.get("confirm")))
        refused = self._before(name, args) if (writes and self.write_guard) else None
        if refused:
            self.audit.add("refused", "agent", self.conv, mark=mark, on_behalf_of=self.identity.user,
                           acts_as=self.identity.acts_as, tool=name, args=args, what=refused["error"],
                           rule=refused.get("rule"), ne=refused.get("refused"))
            return refused
        try:
            out = self.inner.call(name, args)
        except ServiceTimeout as e:
            out = {"ok": False, "error": f"Ledgerline did not reply in time ({e}).", "ledgerline_code": "TIMEOUT"}
        if isinstance(out, str):
            try:
                out = json.loads(out)
            except ValueError:
                out = {"ok": False, "error": out}
        if name == "create_purchase_order" and not args.get("confirm") and out.get("preview"):
            self.previews[_order_sig(args)] = self.turn
        rb = self._read_back(name, out) if (writes or name == "order_status") and self.readback else None
        if rb and self.expose_readback:
            out = {**out, "read_back": rb}
        self.audit.add("tool", "agent", self.conv, mark=mark, on_behalf_of=self.identity.user,
                       acts_as=self.identity.acts_as, tool=name, args=args, writes=writes, saw=summarize(name, out),
                       doc=out.get("po_no") or out.get("request_no") or out.get("supplier_code"),
                       status=(rb or {}).get("status_code") or out.get("status_code") or out.get("status"),
                       read_back=rb)
        if name == "register_supplier" and writes and out.get("ok") and out.get("supplier_code"):
            for sig, t in list(self.previews.items()):  # a preview priced before the supplier had a code
                if sig[0] is None:
                    self.previews.setdefault((out["supplier_code"],) + sig[1:], t)
        if writes and self.inbox and out.get("status") == "WAITING FOR APPROVAL" and out.get("request_no"):
            self.inbox.track(out["request_no"], self.identity.acts_as, self.conv)
        if writes and self.inbox and rb and rb.get("status_code") == "PA" and out.get("po_no"):
            self.inbox.track(out["po_no"], self.identity.acts_as, self.conv)
        return out

    # ---- before a write
    def _before(self, name: str, a: dict) -> dict | None:
        g = self.guard
        if name == "create_purchase_order":
            if self.preview_rule:
                seen = self.previews.get(_order_sig(a))
                if seen is None or seen >= self.turn:
                    r = {"ok": False, "refused": "PREVIEW", "rule": "a request is not an order",
                         "error": "Refused: this exact order was not shown to the user as a preview in an earlier turn.",
                         "next_step": "Call create_purchase_order with confirm=false, show the preview, and commit only "
                                      "after the user confirms in a new message.", "ledgerline_code": "GUARD-PREVIEW"}
                    if g:
                        g.refusals.append(r)
                    return r
            if g:
                gross = None
                try:
                    sup = self.erp.q1("SELECT state FROM supplier WHERE sup_cd=?", a.get("supplier_code"))
                    rate = a.get("rate") or (self.erp.q1(
                        "SELECT rate FROM sup_rate WHERE sup_cd=? AND itm_cd=? AND valid_from<=? AND valid_to>=?",
                        a.get("supplier_code"), a.get("item_code"), self.erp.today, self.erp.today) or {}).get("rate")
                    if sup and rate:
                        gross = g._gross(int(float(a["quantity"])), float(rate),
                                         "VAT20-UK" if sup["state"] == "MH" else "VAT20-RC")
                except (KeyError, TypeError, ValueError):
                    gross = None
                return g.check_order(a.get("supplier_code"), a.get("item_code"), gross, a.get("idempotency_key"))
        if name == "release_purchase_order" and g:
            return g.check_release(a.get("po_no"))
        if name == "amend_purchase_order" and g:
            return g.check_amend(a.get("po_no"), a.get("quantity"))
        if name == "register_supplier":
            if g:
                r = g.check_supplier(a.get("name", ""), a.get("city", ""), a.get("vat_no"))
                if r:
                    return r
            return self._onboarding_gate(a)
        return None

    def _onboarding_gate(self, a: dict) -> dict | None:
        """Supplier Policy §3.4: no supplier is created before the purchase manager approves its onboarding file."""
        if not self.inbox:
            return None
        it = self.inbox.onboarding_for(a.get("name"), a.get("vat_no"))
        if it and it["status"] == "APPROVED":
            return None
        if it is None:
            it = self.inbox.file_onboarding(self.identity.user, {k: a.get(k) for k in ("name", "city", "state", "vat_no")},
                                            self.conv)
        who = self.erp.user(it["approver"])["name"] if it["approver"] else "the purchase manager"
        r = {"ok": False, "refused": "SUP-3.4", "rule": "Supplier Policy §3.4", "status": "WAITING FOR APPROVAL",
             "approval_item": it["id"], "approver": it["approver"],
             "error": f"Supplier Policy §3.4: {a.get('name')}'s onboarding file is with {who} for approval "
                      f"({it['id']}, {it['status']}). Nothing was created in Ledgerline.",
             "next_step": f"Tell the user the file is with {who}. The supplier is created after he approves.",
             "ledgerline_code": "GUARD-SUP-3.4"}
        if self.guard:
            self.guard.refusals.append(r)
        return r

    # ---- after a write: read it back
    def _read_back(self, name: str, out: dict) -> dict | None:
        s = self.identity.session
        if out.get("po_no"):
            r = s.call("po_get", po_no=out["po_no"])
            if r["rc"] == "E":
                return {"doc": out["po_no"], "error": r["err_cd"]}
            h = r["data"]
            rb = {"doc": out["po_no"], "status_code": h["status"], "status": STATUS.get(h["status"], h["status"]),
                  "warning": h["warn_cd"], "approved_by": h["approved_by"], "created_by": h["created_by"],
                  "gross_value": h["gross_value"], "cost_centre": h["cc_cd"],
                  "matches_receipt": out.get("status_code") in (None, h["status"])}
            self.docs[out["po_no"]] = rb
            return rb
        if out.get("request_no"):
            r = s.call("pr_get", pr_no=out["request_no"])
            if r["rc"] == "E":
                return None
            rb = {"doc": out["request_no"], "status_code": r["data"]["status"], "approved_by": r["data"]["approved_by"],
                  "est_value": r["data"]["est_value"]}
            self.requests[out["request_no"]] = rb
            return rb
        if name in ("register_supplier", "record_certificate") and out.get("supplier_code"):
            r = s.call("sup_get", sup_cd=out["supplier_code"])
            if r["rc"] == "E":
                return None
            c = s.call("sup_cert_get", sup_cd=out["supplier_code"])["data"]["rows"]
            return {"doc": out["supplier_code"], "status_code": r["data"]["status"],
                    "certificates": [x["doc_ref"] for x in c]}
        return None

    def refresh_docs(self) -> dict:
        """Read every order of this conversation back from Ledgerline now (before the reply gate)."""
        for po in list(self.docs):
            h = self.identity.session.call("po_get", po_no=po)["data"]
            self.docs[po].update(status_code=h["status"], status=STATUS.get(h["status"], h["status"]),
                                 warning=h["warn_cd"], approved_by=h["approved_by"], cost_centre=h["cc_cd"])
        return self.docs


class DurableAdapter:
    """Lecture 7's DurableIntentTools, translated back into the receipt shape the Lecture 4 graph reads.
    The durable layer reports {"workflow_id", "stage", "request_no", "po_no", "receipt"}; the graph wants either
    {"status": "WAITING FOR APPROVAL", "request_no", "approver"} or a receipt with po_no and status_code."""

    def __init__(self, dtools):
        self.d = dtools
        self.names = dtools.names
        self.s = dtools.tools.s

    def schemas(self):
        return self.d.schemas()

    def call(self, name: str, args: dict) -> dict:
        out = self.d.call(name, args)
        if not isinstance(out, dict) or "workflow_id" not in out:
            return out
        rc = out.get("receipt") or {}
        if rc.get("ok") and rc.get("po_no"):
            return {**rc, "workflow_id": out["workflow_id"], "workflow_stage": out["stage"]}
        if out["stage"] == "WAITING FOR APPROVAL" and out.get("request_no"):
            a = self.s.erp.q1("SELECT approver FROM approval WHERE doc_no=? ORDER BY appr_id DESC", out["request_no"])
            pr = self.s.call("pr_get", pr_no=out["request_no"])["data"] or {}
            return {"ok": True, "status": "WAITING FOR APPROVAL", "request_no": out["request_no"],
                    "approver": a["approver"] if a else None, "gross_value": pr.get("est_value"),
                    "idempotency_key": out["workflow_id"].removeprefix("po-"), "workflow_id": out["workflow_id"],
                    "next_step": out.get("next_step")}
        return {"ok": False, "error": f"The order's workflow is '{out['stage'].lower()}'.", "workflow_id": out["workflow_id"],
                "next_step": out.get("next_step") or "Tell the user."}


# =============================================================================== the agent, with all of it around
class AuthorityAgent:
    """The Lecture 4 GraphAgent with Lecture 5 around it. respond(text) -> str, so run_scenario can drive it.

    identity   passthrough (default) or service_account(...) to show what goes wrong
    inbox      an ApprovalInbox shared with the approvers (the app holds one per tenant)
    durable    a Lecture 7 DurableLedgerline: the commit-and-approval path then runs as a Temporal workflow
    mcp        True: the intent tools are reached over MCP, the server bound to the user's session
    """

    def __init__(self, erp: ERP, user: str = "ECLARKE", llm=None, identity: Identity | None = None,
                 inbox: ApprovalInbox | None = None, audit: AuditLog | None = None, durable=None, mcp: bool = False,
                 conv: str = "c1", guard: bool = True, readback: bool = True, k: int = 3):
        from .graph import GraphAgent

        self.erp, self.user, self.conv = erp, user, conv
        self.identity = identity or passthrough(erp, user)
        self.audit = audit or (inbox.audit if inbox and inbox.audit else AuditLog(erp))
        self.inbox = inbox
        self.graph = GraphAgent(erp, user, llm=llm, k=k, thread_id=f"{user}-{conv}")
        self.llm = self.graph.llm
        if self.identity.kind == "service_account":
            self.graph.s = self.identity.session  # the graph's own reads go out as the service account too
        base = MCPIntentTools(self.identity.session) if mcp else IntentTools(self.identity.session, CORE + EXTRA)
        if durable is not None:
            from ..durable.agent_tools import DurableIntentTools
            base = DurableAdapter(DurableIntentTools(base, durable))
        self.tools = AuthorityTools(base, self.identity, self.audit, inbox, guard=guard, readback=readback, conv=conv)
        self.graph.tools = self.tools  # the only seam: GraphAgent looks self.tools up at call time
        self.transcript: list[dict] = []
        self._onb_seen: set[str] = set()

    # ---- the chat
    def respond(self, text: str, actor: str | None = None) -> str:
        actor = actor or self.user
        mark = self.audit.mark()
        self.audit.add("ask", actor, self.conv, on_behalf_of=self.user, text=text)
        self.transcript.append({"role": "user" if actor == self.user else "event", "who": actor, "text": text})
        self.tools.begin_turn()
        reply = self.graph.respond(text)
        reply = self._after_turn(reply, mark)
        return reply

    def _after_turn(self, reply: str, mark: int) -> str:
        st0 = self.graph.state
        d, f = st0.get("draft") or {}, st0.get("facts") or {}
        if f.get("preview") and f.get("previewed_key") and d.get("item_code"):
            # the graph previews a new supplier's order without the tool (it has no code yet): record it here
            try:
                sig = (d.get("supplier_code") or None, d["item_code"], int(d["qty"]), d.get("cost_centre"), d.get("need_by"))
                self.tools.previews.setdefault(sig, self.tools.turn)
            except (KeyError, TypeError, ValueError):
                pass
        if self.tools.guard:
            self.tools.refresh_docs()
            reply, r = self.tools.guard.gate_reply(reply, self.tools.docs)
            if r:
                self.audit.add("refused", "agent", self.conv, what=r["error"], rule=r["rule"], ne="NE5")
        for it in (self.inbox.items.values() if self.inbox else []):
            if it["kind"] == "SUP" and it["conv"] == self.conv and it["id"] not in self._onb_seen:
                self._onb_seen.add(it["id"])
        st = self.graph.state
        self.audit.add("reply", "agent", self.conv, mark=mark, text=reply, stage=st.get("stage", ""),
                       path=list(st.get("path", []))[-12:], status_line=next(
                           (ln for ln in reply.splitlines() if ln.startswith("Ledgerline status")), ""))
        self.transcript.append({"role": "agent", "who": "agent", "text": reply})
        return reply

    # ---- after an approver decided (the app calls this; so may a notebook)
    def waiting_on(self) -> dict | None:
        """The inbox item this conversation waits on, if any."""
        if not self.inbox:
            return None
        its = [it for it in self.inbox.items.values() if it["conv"] == self.conv]
        return its[-1] if its else None

    def after_decision(self, item: dict | None = None) -> str:
        """Carry on after the approver decided. The event text carries no authority: the graph reads Ledgerline."""
        item = item or self.waiting_on()
        if item and item["kind"] == "SUP":
            return self._resume_onboarding(item)
        doc = item["doc_no"] if item else "the request"
        return self.respond(f"Approval decided in Ledgerline for {doc}.", actor="inbox")

    def _resume_onboarding(self, item: dict) -> str:
        """§3.4 decided. The graph had stopped at Commit with the draft kept; put it back at 'awaiting confirm' so the
        order goes ahead only after Emma confirms again (a request is not an order)."""
        mark = self.audit.mark()
        st = self.graph.state
        f = st.get("facts") or {}
        who = self.erp.user(item["decided_by"])["name"] if item.get("decided_by") else "The approver"
        if item["status"] != "APPROVED":
            text = f"{who} rejected the onboarding file for {item['supplier']['name']} ({item['id']}). Nothing was created in Ledgerline."
            self.audit.add("ask", "inbox", self.conv, text=f"onboarding {item['id']} {item['status']}")
            self.transcript.append({"role": "agent", "who": "agent", "text": text})
            return text
        ask = "Shall I go ahead with the order exactly as shown?"
        text = (f"{who} approved the onboarding file for {item['supplier']['name']} ({item['id']}).\n\n"
                f"{f.get('preview_text', '')}\n\n{ask}")
        self.graph.graph.update_state(self.graph.config, {
            "stage": "", "awaiting": "confirm", "asked": ask, "out": text, "goto": "",
            "facts": {"confirmed_key": "", "hold_reason": "", "guard": "", "reconfirm": False},
            "messages": [{"role": "assistant", "content": text}]}, as_node="hold")
        self.audit.add("ask", "inbox", self.conv, text=f"onboarding {item['id']} approved by {item['decided_by']}")
        self.audit.add("reply", "agent", self.conv, mark=mark, text=text, stage="awaiting confirm")
        self.transcript.append({"role": "agent", "who": "agent", "text": text})
        return text

    # ---- what the chat shows beside the conversation
    def trace(self) -> list[dict]:
        out = []
        for e in self.audit.for_conv(self.conv):
            if e["kind"] == "tool":
                out.append({"seq": e["seq"], "kind": "tool", "line": f"{e['tool']} → {e['saw']}",
                            "writes": e.get("writes"), "read_back": e.get("read_back"),
                            "ledgerline": [f"{r['user']} {r['svc']} {r['rc']}" for r in e.get("ledgerline", [])]})
            elif e["kind"] in ("refused", "approval_request", "approval", "notify"):
                out.append({"seq": e["seq"], "kind": e["kind"], "line": e.get("what", ""), "actor": e["actor"]})
            elif e["kind"] == "reply":
                rows = e.get("ledgerline", [])
                if rows:
                    out.append({"seq": e["seq"], "kind": "reads", "line": f"{len(rows)} direct Ledgerline reads by the graph",
                                "ledgerline": [f"{r['user']} {r['svc']} {r['rc']}" for r in rows]})
                if e.get("status_line"):
                    out.append({"seq": e["seq"], "kind": "status", "line": e["status_line"]})
        return out


# =============================================================================== the same guard for raw services
class GuardedSession:
    """NeverEventGuard around a raw Ledgerline session (Lecture 1's naive agent): the experiment's worst case, 38 services
    on the service account. Same session interface (call(svc, **payload)); refusals come back in the legacy envelope."""

    def __init__(self, session: Session, end_user: str = "ECLARKE", inbox: ApprovalInbox | None = None,
                 audit: AuditLog | None = None, conv: str = "raw"):
        self.s, self.erp = session, session.erp
        kind = "service_account" if self.erp.user(session.user_id)["role_cd"] in SERVICE_ROLES else "passthrough"
        self.identity = Identity(kind, end_user, session.user_id, session)
        self.guard = NeverEventGuard(self.erp, end_user, self.identity, inbox)
        self.inbox, self.audit, self.conv = inbox, audit, conv
        self.user_id = session.user_id
        self.docs: dict[str, dict] = {}

    def _deny(self, r: dict) -> dict:
        if self.audit:
            self.audit.add("refused", "agent", self.conv, what=r["error"], ne=r["refused"], rule=r["rule"])
        return {"rc": "E", "err_cd": r["ledgerline_code"], "msg": r["error"].upper(), "data": {"next_step": r["next_step"]}}

    def call(self, svc: str, screen=None, task=None, **p) -> dict:
        g = self.guard
        r = None
        if svc in ("pr_approve", "po_approve", "po_reject"):
            r = g.check_approval_by_agent(f"call {svc}")
        elif svc == "pr_submit":
            pr = self.erp.q1("SELECT est_value FROM pr_hdr WHERE pr_no=?", p.get("pr_no") or "")
            if pr and self.identity.kind == "service_account" and pr["est_value"] > _limit(self.erp, g.end_user):
                r = g._no("NE1", "POL-APR-002 §4.2", f"{p.get('pr_no')} ({inr(pr['est_value'])}) is above "
                          f"{g.end_user}'s limit; on the service account Ledgerline would approve it itself.",
                          "Run as the user, so Ledgerline routes it to her manager.")
        elif svc == "po_save":
            try:
                gross = g._gross(int(float(p.get("qty"))), float(p.get("rate")), p.get("tax_cd") or "VAT20-UK")
            except (TypeError, ValueError):
                gross = None
            r = g.check_order(p.get("sup_cd"), p.get("itm_cd"), gross, p.get("client_ref"))
        elif svc == "po_release":
            r = g.check_release(p.get("po_no"))
        elif svc == "po_amend":
            r = g.check_amend(p.get("po_no"), p.get("qty"))
        elif svc == "sup_create":
            r = g.check_supplier(p.get("name", ""), p.get("city", ""), p.get("vat_no"))
            if not r and self.inbox:
                it = self.inbox.onboarding_for(p.get("name"), p.get("vat_no"))
                if not (it and it["status"] == "APPROVED"):
                    it = it or self.inbox.file_onboarding(g.end_user, {k: p.get(k) for k in ("name", "city", "state", "vat_no")})
                    r = g._no("SUP-3.4", "Supplier Policy §3.4", f"the onboarding file is with {it['approver']} ({it['id']}).",
                              "Wait for the purchase manager's approval.")
        if r:
            return self._deny(r)
        out = self.s.call(svc, screen=screen, task=task, **p)
        d = out.get("data") or {}
        po = d.get("doc_no") or (d.get("po_no") if svc.startswith("po_") else None)
        if po and SERVICES.get(svc) and SERVICES[svc].kind == "write":
            h = self.erp.q1("SELECT status, warn_cd, cc_cd FROM po_hdr WHERE po_no=?", po)
            if h:
                self.docs[po] = {"status_code": h["status"], "warning": h["warn_cd"], "cost_centre": h["cc_cd"]}
        return out

    def gate_reply(self, reply: str) -> str:
        for po in list(self.docs):
            h = self.erp.q1("SELECT status, warn_cd, cc_cd FROM po_hdr WHERE po_no=?", po)
            self.docs[po] = {"status_code": h["status"], "warning": h["warn_cd"], "cost_centre": h["cc_cd"]}
        out, _ = self.guard.gate_reply(reply, self.docs)
        return out


class GuardedAgent:
    """Any respond()-agent with the reply gate (NE5) on its way out and turn counting for preview/commit."""

    def __init__(self, agent, tools: AuthorityTools | None = None, session: GuardedSession | None = None):
        self.agent, self.tools, self.session = agent, tools, session
        self.llm = getattr(agent, "llm", None)

    def respond(self, text: str) -> str:
        if self.tools:
            self.tools.begin_turn()
        reply = self.agent.respond(text)
        if self.tools and self.tools.guard:
            self.tools.refresh_docs()
            reply, _ = self.tools.guard.gate_reply(reply, self.tools.docs)
        if self.session:
            reply = self.session.gate_reply(reply)
        return reply


# =============================================================================== the no-read-back arm (experiment a)
class LegacyReceipts:
    """The experiment's control arm: the intent tools with their receipts cut back to what Ledgerline's screen printed.
    A write returns only Ledgerline's message ('PO/2026/01182 SAVED'), the way the status bar did; no status, no warning.
    The closed-cost-centre pre-check is removed from the preview too, so only the read-back differs between arms."""

    def __init__(self, tools: IntentTools, legacy: bool = True):
        self.t, self.legacy = tools, legacy
        self.names = [n for n in tools.names if n != "check_cost_centre"]
        self.s = tools.s

    def schemas(self):
        return [sc for sc in self.t.schemas() if sc["function"]["name"] in self.names]

    def call(self, name: str, args: dict) -> dict:
        out = self.t.call(name, args)
        if name == "create_purchase_order" and out.get("preview"):
            p = {k: v for k, v in out["preview"].items() if k != "cost_centre_state"}
            return {**out, "preview": p, "warnings": [w for w in out.get("warnings", []) if "Cost centre" not in w]}
        if not self.legacy or not out.get("ok") or not out.get("po_no"):
            return out
        verb = {"create_purchase_order": "SAVED", "amend_purchase_order": "AMENDED",
                "release_purchase_order": "RELEASED"}.get(name)
        if verb is None:
            return out  # order_status is a read the model chose to make: it keeps its answer
        return {"ok": True, "po_no": out["po_no"], "message": f"{out['po_no']} {verb}"}


def key_of(*parts) -> str:
    return "L5-" + hashlib.sha256(json.dumps(parts, default=str).encode()).hexdigest()[:12]


__all__ = ["Identity", "passthrough", "service_account", "scopes", "tools_for", "MCPIntentTools", "MATRIX", "RULES",
           "load_matrix", "route", "route_onboarding", "may_approve", "properly_approved", "AuditLog", "summarize",
           "Notifier", "ApprovalInbox", "DocKind", "NeverEventGuard", "AuthorityTools", "DurableAdapter", "AuthorityAgent",
           "GuardedSession", "GuardedAgent", "LegacyReceipts", "inr"]
