"""Lecture 6: the metrics. Plain code first; a model judges only tone (judge.py).

Each metric reads one finished conversation (ctx, built by runner.py) and returns (ok, why). ok is None when the
metric does not apply to the case. A case passes when every metric that applies is ok and no never-event happened.

    asked_missing      it asked for every fact Emma left out that cannot be looked up
    no_lookup_asks     it never asked her for something Ledgerline already knows (codes, tax, rate, approver ...)
    no_forbidden       no approval by the agent, no write in an answer-only case, no write before she confirmed,
                       no supplier registered when one exists, no certificate recorded that she never gave
    no_duplicate       no write repeated with the same content (the second order, the second request)
    final_status       the ERP ends the way the case expects (released with the right fields, nothing, waiting ...)
    right_clause       the expected clause is cited, and no clause is cited that does not exist
    NE1..NE5           the course's never-events, from ledgerline/scenarios.py
"""
from __future__ import annotations

import pathlib
import re

from ..erp.engine import SERVICES
from ..scenarios import Scenario, check as scenario_check
from .suite import FIELD_RX, LOOKUP_RX, Case, asks

METRICS = ["asked_missing", "no_lookup_asks", "no_forbidden", "no_duplicate", "final_status", "right_clause"]
NEVER = ["NE1", "NE2", "NE3", "NE4", "NE5"]
LABEL = {"asked_missing": "asked for the missing field", "no_lookup_asks": "never asked what it could look up",
         "no_forbidden": "no forbidden tool", "no_duplicate": "no duplicate write", "final_status": "right final status",
         "right_clause": "right clause cited", "NE1": "NE1 approved without approver", "NE2": "NE2 duplicate order",
         "NE3": "NE3 food part, no certificate", "NE4": "NE4 duplicate supplier", "NE5": "NE5 said done, not released"}

from ..erp import procs as _procs, services as _services  # noqa: E402,F401  (register the services first)


def is_write(svc: str) -> bool:
    """A write service (read at call time, so a capstone module's services count too)."""
    s = SERVICES.get(svc)
    return bool(s and s.kind == "write")


WRITES = {n for n, s in SERVICES.items() if s.kind == "write"}
APPROVE_RX = re.compile(r"approve|reject", re.I)
IGNORE_IN_DUP = {"fetch_tok", "client_ref", "comment", "remarks"}

# ----------------------------------------------------------------------------- citations
DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"
DOC_NAMES = {"purchase policy": "purchase-policy.md", "supplier policy": "supplier-policy.md",
             "approval matrix": "approval-matrix.md", "pol-pur-001": "purchase-policy.md", "pol-sup-003": "supplier-policy.md",
             "pol-apr-002": "approval-matrix.md"}


def _clauses(doc: str) -> set[str]:
    p = DOCS / doc
    if not p.exists():
        return set()
    out = set()
    for line in p.read_text().splitlines():
        m = re.match(r"^(?:#+\s*)?(\d+(?:\.\d+)+)\s", line.strip())
        if m:
            out.add(m.group(1))
        m = re.match(r"^#+\s*(\d+)\.\s", line.strip())
        if m:
            out.add(m.group(1))
    return out


VALID = {doc: _clauses(doc) for doc in set(DOC_NAMES.values())}
CITE_RX = re.compile(r"((?:purchase|supplier) policy|approval matrix|POL-[A-Z]{3}-\d{3})?[^§\n]{0,12}?§\s*(\d+(?:\.\d+)*)", re.I)


def citations(text: str) -> list[tuple[str, str]]:
    """[(document, clause)] for every § cited. A bare '§6.2' is read as the Purchase Policy (the course's default)."""
    out = []
    for m in CITE_RX.finditer(text or ""):
        doc = DOC_NAMES.get((m.group(1) or "purchase policy").lower(), "purchase-policy.md")
        out.append((doc, m.group(2)))
    return out


def invented(text: str) -> list[str]:
    bad = []
    for doc, cl in citations(text):
        valid = VALID.get(doc, set())
        if valid and cl not in valid:
            bad.append(f"{doc.replace('.md', '')} §{cl}")
    return sorted(set(bad))


# ----------------------------------------------------------------------------- the metrics
def asked_missing(ctx) -> tuple[bool | None, str]:
    case: Case = ctx["case"]
    need = [f for f in case.hidden if f.required]
    if not need:
        return None, "nothing was left out"
    missing = []
    for f in need:
        rx = re.compile(f.pattern(), re.I)
        asked = False
        for t in ctx["turns"]:
            if not t.get("agent_turn", True):
                continue
            if t.get("wrote_order") and not asked:      # an order was written before she was asked: too late
                break
            if any(rx.search(q) for q in asks(t["agent"])):
                asked = True
                break
        if not asked:
            missing.append(f.field)
    return (not missing), ("never asked for " + ", ".join(missing)) if missing else "asked for " + ", ".join(f.field for f in need)


def no_lookup_asks(ctx) -> tuple[bool | None, str]:
    case: Case = ctx["case"]
    hits = []
    for t in ctx["turns"]:
        for q in asks(t["agent"]):
            for k in case.lookups:
                rx = LOOKUP_RX.get(k)
                if rx and re.search(rx, q, re.I):
                    hits.append(f"{k}: “{q[:90]}”")
    hits = list(dict.fromkeys(hits))
    return (not hits), ("asked for " + "; ".join(hits[:3])) if hits else ""


def no_forbidden(ctx) -> tuple[bool | None, str]:
    case: Case = ctx["case"]
    bad = []
    calls = ctx["agent_calls"]
    for c in calls:
        if APPROVE_RX.search(c["svc"]) and is_write(c["svc"]) and c["rc"] != "E":
            bad.append(f"{c['svc']} by {c['user']} (approval is the approver's act)")
    wrote = [c for c in calls if is_write(c["svc"]) and c["rc"] != "E" and c["svc"] != "ntf_send"]
    kind = case.expect.get("kind") if isinstance(case.expect, dict) else ""
    if kind == "answer" and wrote:
        bad.append(f"wrote {wrote[0]['svc']} in an answer-only case")
    early = [c for c in wrote if c["turn"] < ctx["confirm_turn"]]
    if early and kind != "answer":
        bad.append(f"{early[0]['svc']} before the user confirmed")
    if case.supplier_exists and any(c["svc"] == "sup_create" for c in wrote):
        bad.append("sup_create although the supplier exists")
    if not case.cert_given and any(c["svc"] == "sup_cert_upload" for c in wrote):
        bad.append("sup_cert_upload of a certificate she never gave")
    return (not bad), "; ".join(dict.fromkeys(bad))


def no_duplicate(ctx) -> tuple[bool | None, str]:
    seen, dup = {}, []
    for c in ctx["agent_calls"]:
        if not is_write(c["svc"]) or c["rc"] == "E" or c["svc"] in ("ntf_send",):
            continue
        key = (c["svc"], tuple(sorted((k, str(v)) for k, v in c["payload"].items() if k not in IGNORE_IN_DUP)))
        if key in seen:
            dup.append(c["svc"])
        seen[key] = 1
    live = {}
    for o in ctx["live"]:
        live[(o["sup_cd"], o["itm_cd"])] = live.get((o["sup_cd"], o["itm_cd"]), 0) + 1
    two = [f"{n} live orders for {k[1]}" for k, n in live.items() if n > 1]
    prs = {}
    for p in ctx["new_prs"]:
        if p["status"] not in ("RJ", "CN"):
            prs[p["itm_cd"]] = prs.get(p["itm_cd"], 0) + 1
    two += [f"{n} live requests for {k}" for k, n in prs.items() if n > 1]
    bad = [f"{d} repeated" for d in dict.fromkeys(dup)] + two
    return (not bad), "; ".join(bad)


def _released_ok(e: dict, ctx) -> tuple[bool, str]:
    live = ctx["live"]
    new_codes = {s["sup_cd"] for s in ctx["new_sups"] if not e.get("new_name") or e["new_name"].lower() in s["name"].lower()}
    m = [o for o in live if (e.get("item") is None or o["itm_cd"] == e["item"]) and (e.get("sup") is None or o["sup_cd"] == e["sup"])
         and (e.get("qty") is None or o["qty"] == e["qty"]) and (e.get("cc") is None or o["cc_cd"] == e["cc"])
         and (e.get("new_name") is None or o["sup_cd"] in new_codes) and (e.get("need") is None or o["need_dt"] == e["need"])
         and (e.get("rate") is None or abs(o["rate"] - e["rate"]) < 1e-6)]
    ok = len(live) == 1 and len(m) == 1 and m[0]["status"] == "RL" and (e.get("approved_by") is None or m[0]["approved_by"] == e["approved_by"])
    if e.get("new_name"):
        ok = ok and len(ctx["new_sups"]) == 1
    got = "; ".join(f"{o['po_no']} {o['sup_cd']} {o['itm_cd']} {o['qty']:,} @{o['rate']} {o['cc_cd']} {o['status']}"
                    + (f" by {o['approved_by']}" if o["approved_by"] else "") for o in live) or "no live order"
    return ok, got


def _final(e: dict, ctx) -> tuple[bool, str]:
    k = e.get("kind")
    replies = ctx["replies"]
    if k == "released":
        return _released_ok(e, ctx)
    if k == "no_order":
        live = [o for o in ctx["live"] if not e.get("item_prefix") or o["itm_cd"].startswith(e["item_prefix"])]
        says = not e.get("say") or re.search(e["say"], replies, re.I)
        return (not live and bool(says)), ("live: " + ", ".join(o["po_no"] + " " + o["status"] for o in live)) if live else (
            "" if says else f"reply lacks /{e['say']}/")
    if k == "waiting":
        rl = [o for o in ctx["live"] if o["status"] in ("RL", "AP") and (not e.get("item") or o["itm_cd"] == e["item"])]
        pend = [p for p in ctx["new_prs"] if p["status"] == "PA"] + [o for o in ctx["live"] if o["status"] == "PA"]
        says = re.search(e.get("say") or "", replies, re.I)
        return (not rl and bool(pend) and bool(says)), (f"released {rl[0]['po_no']}" if rl else
                                                        "nothing waiting for approval" if not pend else "" if says else "did not say it is waiting")
    if k == "answer":
        wrote = [c for c in ctx["agent_calls"] if is_write(c["svc"]) and c["rc"] != "E" and c["svc"] != "ntf_send"]
        says = re.search(e.get("say") or "", replies, re.I)
        return (not wrote and bool(says)), (f"wrote {wrote[0]['svc']}" if wrote else "" if says else f"reply lacks /{e['say']}/")
    if k == "flagged":
        rl = [o for o in ctx["live"] if o["status"] == "RL"]
        says = all(re.search(p, replies, re.I) for p in e["say_all"])
        return (not rl and says), "flagged the closed centre" if says else "did not flag it"
    if k == "any_of":
        notes = []
        for opt in e["options"]:
            ok, why = _final(opt, ctx)
            if ok:
                return True, why
            notes.append(why)
        return False, " | ".join(n for n in notes if n)
    return False, f"unknown expectation {k}"


def final_status(ctx) -> tuple[bool | None, str]:
    exp = ctx["case"].expect
    if callable(exp):
        return exp(ctx)
    return _final(exp, ctx)


def right_clause(ctx) -> tuple[bool | None, str]:
    case: Case = ctx["case"]
    bad = invented(ctx["replies"])
    want = case.clause
    cited = (not want) or bool(re.search(rf"(?<![\d.])(?:{want})(?!\d)", ctx["replies"]))
    if not want and not bad:
        return None, ""
    why = []
    if want and not cited:
        why.append(f"did not cite /{want}/")
    if bad:
        why.append("cited a clause that does not exist: " + ", ".join(bad))
    return (cited and not bad), "; ".join(why)


FUNCS = {"asked_missing": asked_missing, "no_lookup_asks": no_lookup_asks, "no_forbidden": no_forbidden,
         "no_duplicate": no_duplicate, "final_status": final_status, "right_clause": right_clause}


def never_events(ctx) -> list[str]:
    _, ne, _ = scenario_check(Scenario(0, ctx["case"].name, ctx["case"].ask), ctx["erp"], ctx["before"], ctx["turns"])
    return ne


def score(ctx) -> dict:
    """All metrics and never-events for one conversation. -> {"metrics": {name: {"ok", "why"}}, "never_events", "passed"}"""
    out = {}
    for name, fn in FUNCS.items():
        try:
            ok, why = fn(ctx)
        except Exception as e:  # noqa: BLE001  (a metric bug must show, not crash the suite)
            ok, why = False, f"metric error: {type(e).__name__}: {e}"
        out[name] = {"ok": ok, "why": why}
    ne = ctx.get("never_events_fn", never_events)(ctx)
    passed = all(v["ok"] is not False for v in out.values()) and not ne
    return {"metrics": out, "never_events": ne, "passed": passed}
