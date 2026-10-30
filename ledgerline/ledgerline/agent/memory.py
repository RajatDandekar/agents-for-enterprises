"""Lecture 4: memory at four levels, and what each one puts into a single turn.

    level      lives in                                  lasts          example for Emma's order
    draft      the graph's state (state["draft"])        one order      item BAT-500, 2,000, PRD-07, need-by 2 Nov
    session    the checkpointer, one thread per chat     one chat       "we asked her for a cost centre; she said PRD-07"
    user       UserMemory, a small JSON store            across chats   usual cost centre PRD-05, battery packs from Voltway
    company    the policy documents (search_policy)      years          Purchase Policy §6.2: lithium cells needs a cert

The model never sees the whole of any level. Each step takes the slice it needs: Understand sees the draft and the
last question; Collect reads the user level (in code, as suggestions the gates still check); the cert question and
policy answers read the company level. context_for_turn() shows exactly what each level contributed to one turn.

Company level: if Lecture 2's ledgerline.agent.retrieval exposes search_policy(), we use it; otherwise a small stand-in
(PolicyIndex below) that scores the numbered clauses of ledgerline/docs/purchase-policy.md by word overlap.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
from collections import Counter

DOCS = pathlib.Path(__file__).resolve().parents[1] / "docs"
STOP = set("a an the of to in on for and or is are be by with from at as it its this that any not no may must only "
           "we our you your can do does i my me them they their there what which who how if than then so".split())


def _words(t: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9§.]+", t.lower().replace("-", " ")):
        w = w.strip(".")
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        if w and w not in STOP:
            out.append(w)
    return out


# ----------------------------------------------------------------------------- level 4: the company
class PolicyIndex:
    """Stand-in for Lecture 2's search_policy: numbered clauses of the Purchase Policy, scored by word overlap (BM25-ish)."""

    def __init__(self, path: pathlib.Path | None = None):
        path = path or DOCS / "purchase-policy.md"
        text = path.read_text()
        self.doc = re.search(r"^title:\s*(.+)$", text, re.M).group(1).strip() if "title:" in text else path.stem
        self.clauses, head = [], ""
        for line in text.splitlines():
            m = re.match(r"^##\s+(\d+)\.\s+(.*)", line)
            if m:
                head = m.group(2).strip()
                continue
            m = re.match(r"^(\d+\.\d+)\s+(.*)", line)
            if m:
                self.clauses.append({"id": m.group(1), "section": head, "text": m.group(2).replace("**", "")})
        self.df = Counter(w for c in self.clauses for w in set(_words(c["section"] + " " + c["text"])))

    def search(self, query: str, k: int = 3) -> list[dict]:
        q = _words(query)
        n = len(self.clauses)
        scored = []
        for c in self.clauses:
            tf = Counter(_words(c["section"] + " " + c["text"]))
            s = sum(math.log(1 + n / self.df[w]) * tf[w] / (tf[w] + 1.2) for w in set(q) if w in tf)
            scored.append((round(s, 4), c["id"], c))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [{**c, "doc": self.doc, "score": s, "cite": f"{self.doc} §{c['id']}"} for s, _, c in scored[:k] if s > 0]


class CompanyMemory:
    """Level 4. search(query) -> clauses with a citation. Uses Lecture 2's retrieval when it is installed."""

    def __init__(self, use_lecture2: bool = False):
        self.backend = "stand-in: PolicyIndex over docs/purchase-policy.md"
        self._l2 = None
        if use_lecture2:
            try:
                from .retrieval import search_policy  # Lecture 2
                self._l2, self.backend = search_policy, "ledgerline.agent.retrieval.search_policy (Lecture 2)"
            except Exception:
                pass
        self._index = PolicyIndex()

    def search(self, query: str, k: int = 3) -> list[dict]:
        if self._l2 is not None:
            try:
                hits = self._l2(query, k=k)
                return [h if isinstance(h, dict) else {"text": str(h)} for h in hits][:k]
            except Exception:
                pass
        return self._index.search(query, k)


# ----------------------------------------------------------------------------- level 3: the user
class UserMemory:
    """Level 3: a small store of what we have learned about each user, with where each fact came from.

    learn(session) reads the user's own order history from Ledgerline (po_search, as her) and her user record (usr_get),
    and keeps: usual cost centre, preferred supplier per item, last order per item. Facts are suggestions: the route's
    gates still check them (her usual cost centre, PRD-05, is closed, and the centre_closed gate catches it)."""

    def __init__(self, path: str | None = None):
        self.path = pathlib.Path(path) if path else None
        self.data: dict = json.loads(self.path.read_text()) if self.path and self.path.exists() else {}

    def learn(self, session) -> dict:
        uid = session.user_id
        me = session.call("usr_get", user_id=uid)["data"] or {}
        rows = [r for r in (session.call("po_search", from_dt="2026-01-01")["data"] or {}).get("rows", [])
                if r["created_by"] == uid]
        rows.sort(key=lambda r: r["created_on"])
        ccs = Counter()
        for r in rows:
            h = session.call("po_get", po_no=r["po_no"])["data"] or {}
            ccs[h.get("cc_cd")] += 1
        u = {"user_id": uid, "name": me.get("name"), "approval_limit": me.get("appr_limit"),
             "manager": me.get("manager_id"), "facts": {}}
        if ccs:
            cc, n = sorted(ccs.items(), key=lambda kv: (-kv[1], kv[0]))[0]
            u["facts"]["usual_cost_centre"] = {"value": cc, "source": f"{n} of your {len(rows)} orders in Ledgerline"}
        elif me.get("default_cc"):
            u["facts"]["usual_cost_centre"] = {"value": me["default_cc"], "source": "your Ledgerline user record"}
        by_item: dict[str, list] = {}
        for r in rows:
            by_item.setdefault(r["itm_cd"], []).append(r)
        pref, last = {}, {}
        for itm in sorted(by_item):
            rs = by_item[itm]
            sup, n = sorted(Counter(r["sup_cd"] for r in rs).items(), key=lambda kv: (-kv[1], kv[0]))[0]
            pref[itm] = {"value": sup, "source": f"{n} of your {len(rs)} orders for {itm}"}
            r = rs[-1]
            last[itm] = {"value": {"po_no": r["po_no"], "supplier_code": r["sup_cd"], "qty": r["qty"], "rate": r["rate"],
                                   "date": r["created_on"][:10]}, "source": r["po_no"]}
        u["facts"]["preferred_supplier"] = pref
        u["facts"]["last_order"] = last
        self.data[uid] = u
        self.save()
        return u

    def get(self, user_id: str) -> dict:
        return self.data.get(user_id, {"user_id": user_id, "facts": {}})

    def fact(self, user_id: str, name: str, key: str | None = None):
        f = self.get(user_id)["facts"].get(name)
        if f is not None and key is not None:
            f = f.get(key)
        return f

    def remember(self, user_id: str, name: str, value, source: str):
        self.data.setdefault(user_id, {"user_id": user_id, "facts": {}})["facts"][name] = {"value": value, "source": source}
        self.save()

    def save(self):
        if self.path:
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True))


# ----------------------------------------------------------------------------- levels 1 and 2, as views
def draft_view(state: dict) -> dict:
    """Level 1: the half-filled order, exactly as the graph holds it."""
    return {k: v for k, v in (state.get("draft") or {}).items() if v not in (None, "")}


def session_view(agent) -> dict:
    """Level 2: what the checkpointer holds for this thread."""
    hist = list(agent.graph.get_state_history(agent.config))
    st = agent.graph.get_state(agent.config)
    msgs = (st.values or {}).get("messages", [])
    return {"thread_id": agent.config["configurable"]["thread_id"], "checkpoints": len(hist),
            "messages": len(msgs), "last_question": (st.values or {}).get("asked", ""),
            "waiting": [i.value.get("kind") for t in st.tasks for i in (t.interrupts or [])]}


def context_for_turn(agent, text: str, company_query: str | None = None) -> dict:
    """What each memory level contributes to the next turn, measured in characters of what would be used.

    company_query: what the step that reads the company level searches for (default: her message).
    Returns {level: {"content": ..., "chars": n, "used_by": step}}."""
    st = agent.graph.get_state(agent.config).values or {}
    d = draft_view(st)
    sess = session_view(agent)
    recent = [{"role": m["role"], "content": m["content"]} for m in st.get("messages", [])[-4:]]
    u = agent.memory_user.get(agent.user)
    hits = agent.memory_company.search(company_query or text, k=2)
    out = {
        "draft": {"content": d, "used_by": "Understand (what is already filled), every gate"},
        "session": {"content": {**sess, "recent": recent}, "used_by": "Understand (what we asked; her answer)"},
        "user": {"content": u.get("facts", {}), "used_by": "Collect (suggestions the gates still check)"},
        "company": {"content": [{"cite": h.get("cite"), "text": h.get("text")} for h in hits],
                    "used_by": "Check and answers (citations)"},
    }
    for v in out.values():
        v["chars"] = len(json.dumps(v["content"], ensure_ascii=False))
    return out
