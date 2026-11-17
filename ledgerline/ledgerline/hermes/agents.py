"""Background agents: agents that run on a schedule, without a person (Lecture 5, The Habits, station 3).

Five agents, each an agent loop (a model with a few tools) inside a harness that makes it safe to leave alone:
    schedule       when it runs, on the student's simulated clock ("+1 week" plays every run of the week in order)
    idempotency    a run has a key (agent + scheduled time): the same run never happens twice; tools are idempotent too
    a health check before the first model call: if Ledgerline is down, the run fails without spending a token and is
                   retried 15 and 30 minutes later (the planted failure: Ledgerline's maintenance, Wed 28 Oct 02:00-02:20)
    draft, not send  e-mails to anyone outside Northbridge become drafts (draft_message); only @handles get messages
    previews       an agent that may not commit (the reorder watch) has every write forced to a preview
    a budget       at most max_steps model calls and max_tokens input tokens per run
    a kill switch  each agent on or off, and "Stop all"
    a run log      what it did (tool calls), what it changed (read from Ledgerline before and after), what it left for a
                   person (drafts to send, invoices held, requests to confirm, approvals waiting)
    its own notes  the run log's last summary is given to the next run (a background agent's memory)
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import time

from ..llm import PRICES
from .engine import DAYS, schedule_text
from .world import PEOPLE

AGENTS = [
    {"id": "match", "title": "Three-way match", "icon": "scale", "as": "LMORENO", "default_on": False,
     "schedule": {"every": "week", "day": "Wed", "at": "02:00"},
     "what": "Matches every received invoice against its order and goods receipt; posts the ones that agree, holds the "
             "rest with the reason, and messages accounts payable.",
     "tools": ["list_invoices", "match_invoice", "post_invoice", "hold_invoice", "send_message"],
     "limits": {"max_steps": 8, "max_tokens": 80000, "may_commit": True},
     "params": {"tolerance_pct": 2},
     "instructions": "You are the weekly three-way match for accounts payable. 1) list_invoices with status received. "
                     "2) match_invoice each one (price tolerance {tolerance_pct}%). 3) For each matched one, post_invoice with "
                     "confirm=true{commit_note}. For each one that does not match, hold_invoice with the match note as the "
                     "reason. 4) Send @luis one short Slack message: how many posted, how many held and why. Do all the "
                     "invoices in as few steps as you can (call tools for several invoices at once)."},
    {"id": "chase", "title": "Late-order chaser", "icon": "clock", "as": "ECLARKE", "default_on": False,
     "schedule": {"every": "weekday", "at": "09:00"},
     "what": "Every weekday: finds orders that are late, drafts a chasing e-mail to each supplier (never sends it), and "
             "tells the buyer.",
     "tools": ["list_open_orders", "draft_message", "send_message"],
     "limits": {"max_steps": 8, "max_tokens": 60000, "may_commit": True},
     "params": {"min_days_late": 7},
     "instructions": "You chase late purchase orders for Emma Clarke. 1) list_open_orders with min_days_late={min_days_late}. "
                     "2) For each order, draft_message to its supplier_email, subject exactly 'Late order <po_no>', a polite "
                     "e-mail under 70 words asking for a delivery date for the outstanding quantity, signed Emma Clarke, "
                     "Northbridge Cycles; draft them all in one step (several tool calls at once). A draft that is already pending is "
                     "not saved twice: that is fine. 3) Send @emma one "
                     "short Slack message listing the orders and which drafts are new today. Never e-mail a supplier yourself."},
    {"id": "certs", "title": "Certificate watch", "icon": "badge", "as": "LMORENO", "default_on": False,
     "schedule": {"every": "week", "day": "Mon", "at": "08:00"},
     "what": "Every Monday: UN 38.3 certificates expired or expiring within 60 days (AMD-SUP-2026-02); drafts a renewal "
             "request to each supplier and tells Luis which open orders are at risk.",
     "tools": ["expiring_certificates", "draft_message", "send_message"],
     "limits": {"max_steps": 5, "max_tokens": 30000, "may_commit": True},
     "params": {"within_days": 60},
     "instructions": "You watch supplier certificates. 1) expiring_certificates with within_days={within_days}. 2) For each "
                     "supplier whose UN 38.3 is EXPIRING, draft_message to its supplier_email, subject 'UN 38.3 renewal: "
                     "<supplier_name>', asking for the renewed test summary before it expires on its valid_to date. Skip "
                     "suppliers already EXPIRED (they are blocked; say so). 3) Send @luis one short Slack message: who "
                     "expires when, and which open orders are at risk."},
    {"id": "reorder", "title": "Reorder watch", "icon": "box", "as": "ECLARKE", "default_on": False,
     "schedule": {"every": "weekday", "at": "07:00"},
     "what": "Every weekday: items below their reorder level; prepares a purchase request for each as a preview "
             "(never submits) and asks Emma to confirm.",
     "tools": ["low_stock", "create_purchase_request", "send_message"],
     "limits": {"max_steps": 5, "max_tokens": 40000, "may_commit": False},
     "params": {"multiple": 3, "cost_centre": "PRD-07"},
     "instructions": "You watch stock for Emma Clarke. 1) low_stock. 2) For each item, create_purchase_request with "
                     "quantity = {multiple} x its reorder_level, cost_centre {cost_centre}, need_by two weeks from today, "
                     "confirm=false (a preview: you never submit). 3) Send @emma one short Slack message with each preview "
                     "(item, quantity, estimated value, who must approve) and ask her to confirm in Ask Northbridge."},
    {"id": "digest", "title": "Daniel's approvals digest", "icon": "inbox", "as": "DOKAFOR", "default_on": False,
     "schedule": {"every": "weekday", "at": "08:00"},
     "what": "Every weekday at 08:00: what waits for Daniel's signature, oldest first, in one message.",
     "tools": ["list_my_approvals", "send_message"],
     "limits": {"max_steps": 3, "max_tokens": 20000, "may_commit": True},
     "params": {},
     "instructions": "You prepare Daniel Okafor's morning approvals digest. 1) list_my_approvals. 2) Send @daniel one short "
                     "Slack message: how many documents wait, oldest first, each with its number, value in pounds and who "
                     "raised it. If nothing waits, say so in one line."},
]
BY_ID = {a["id"]: a for a in AGENTS}
SYSTEM = """{instructions}

You are a background agent at Northbridge Cycles (Manchester, e-bikes), working in its Ledgerline ERP as {name} ({user},
{role}), with that person's permissions only. Nobody is watching this run: it is {now} (scheduled run). Use the tools;
if a tool returns ok=false, read its next_step. Be brief. Finish with one plain sentence on what you did and what you
left for a person.
Your notes from your last run: {notes}"""


def fires(sched: dict, a: dt.datetime, b: dt.datetime) -> list[dt.datetime]:
    """Every time in (a, b] this schedule fires."""
    hh, mm = (int(x) for x in sched.get("at", "09:00").split(":"))
    out, d = [], a.date()
    while d <= b.date():
        t = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=dt.timezone.utc)
        ok = {"day": True, "weekday": d.weekday() < 5, "week": DAYS[d.weekday()] == sched.get("day", "Mon"),
              "month": d.day == int(sched.get("day_of_month", 1))}.get(sched.get("every", "day"), False)
        if ok and a < t <= b:
            out.append(t)
        d += dt.timedelta(days=1)
    return out


def _usd(r) -> float:
    p = PRICES.get(r.model.split(":", 1)[-1].split("/")[-1], (0.5, 3.0))
    return round((r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6, 6)


def ledger_state(erp) -> dict:
    with erp.lock:
        return {"inv": {r["inv_no"]: r["status"] for r in erp.q("SELECT inv_no, status FROM inv_hdr")},
                "drafts": {r["id"]: r for r in erp.q("SELECT id, recipient, subject, ref FROM ntf_draft")},
                "sent": {r["id"]: r for r in erp.q("SELECT id, channel, recipient, body FROM ntf_queue")},
                "prs": {r["pr_no"]: r["status"] for r in erp.q("SELECT pr_no, status FROM pr_hdr")},
                "pos": {r["po_no"]: r["status"] for r in erp.q("SELECT po_no, status FROM po_hdr")}}


def what_changed(before: dict, after: dict) -> list[dict]:
    out = []
    names = {"PS": "posted", "HD": "held", "MT": "matched", "RC": "recorded"}
    for k, v in after["inv"].items():
        if before["inv"].get(k) != v:
            out.append({"kind": "invoice", "ref": k, "text": f"{k} {names.get(v, v)}" + ("" if k in before["inv"] else " (new)")})
    for k, v in after["drafts"].items():
        if k not in before["drafts"]:
            out.append({"kind": "draft", "ref": v["ref"], "text": f"draft to {v['recipient']}: {v['subject']}"})
    for k, v in after["sent"].items():
        if k not in before["sent"]:
            out.append({"kind": "message", "ref": v["recipient"], "text": f"{v['channel'].lower()} to {v['recipient']}: {v['body'][:140]}"})
    for k, v in after["prs"].items():
        if before["prs"].get(k) != v:
            out.append({"kind": "request", "ref": k, "text": f"{k} {v}"})
    for k, v in after["pos"].items():
        if before["pos"].get(k) != v:
            out.append({"kind": "order", "ref": k, "text": f"{k} {v}"})
    return out


def changes_from_calls(calls) -> list[dict]:
    """What a run changed, read from the Ledgerline service calls its own tool calls made (each tool call runs under the
    sandbox's lock, so its service calls are contiguous even when other agents run at the same time)."""
    out = []
    for c in calls:
        if c.rc == "E":
            continue
        d, pl = c.data or {}, c.payload or {}
        if c.svc == "inv_post":
            out.append({"kind": "invoice", "ref": d.get("inv_no"), "text": f"{d.get('inv_no')} posted (due {d.get('due_dt')})"})
        elif c.svc == "inv_hold":
            out.append({"kind": "invoice", "ref": d.get("inv_no"), "text": f"{d.get('inv_no')} held: {pl.get('reason', '')[:120]}"})
        elif c.svc == "inv_match":
            out.append({"kind": "invoice", "ref": d.get("inv_no"), "text": f"{d.get('inv_no')} {str(d.get('result', '')).replace('_', ' ')}"})
        elif c.svc == "inv_save":
            out.append({"kind": "invoice", "ref": d.get("inv_no"), "text": f"{d.get('inv_no')} recorded"})
        elif c.svc == "ntf_draft_save" and not d.get("already_done"):
            out.append({"kind": "draft", "ref": pl.get("ref"), "text": f"draft to {pl.get('recipient')}: {pl.get('subject')}"})
        elif c.svc == "ntf_send":
            out.append({"kind": "message", "ref": pl.get("recipient"), "text": f"{str(pl.get('channel', '')).lower()} to {pl.get('recipient')}: {str(pl.get('msg', ''))[:140]}"})
        elif c.svc in ("pr_save", "pr_submit", "po_save", "po_release", "grn_save"):
            out.append({"kind": "document", "ref": d.get("pr_no") or d.get("doc_no") or d.get("po_no") or d.get("grn_no"),
                        "text": f"{c.svc}: {d.get('pr_no') or d.get('doc_no') or d.get('po_no') or d.get('grn_no')} {d.get('status', '')}"})
    return out


def left_for_person(erp) -> list[dict]:
    with erp.lock:
        drafts = erp.q("SELECT id, recipient, subject FROM ntf_draft WHERE status='PENDING' ORDER BY id")
        held = erp.q("SELECT inv_no, hold_reason FROM inv_hdr WHERE status='HD' ORDER BY inv_no")
        waiting = erp.q("SELECT doc_no, approver FROM approval WHERE status='PENDING' ORDER BY appr_id")
    out = [{"kind": "draft", "text": f"{len(drafts)} draft(s) to read and send", "items": [d["subject"] for d in drafts][:12]}] if drafts else []
    if held:
        out.append({"kind": "held", "text": f"{len(held)} invoice(s) held for a person", "items": [f"{h['inv_no']}: {h['hold_reason']}" for h in held][:12]})
    if waiting:
        out.append({"kind": "approval", "text": f"{len(waiting)} document(s) waiting for a signature",
                    "items": [f"{w['doc_no']} ({PEOPLE.get(w['approver'], {}).get('name', w['approver'])})" for w in waiting][:12]})
    return out


class Runner:
    """Runs background agents for one student. call_tool(user, name, args, at) and llm_for come from the app."""

    def __init__(self, erp, call_tool, llm_for, health):
        self.erp, self.call_tool, self.llm_for, self.health = erp, call_tool, llm_for, health

    def run(self, cfg: dict, at: dt.datetime, notes: str = "", attempt_log=None) -> dict:
        """One run of one agent at simulated time `at`, with retries when Ledgerline is down."""
        a = BY_ID[cfg["id"]]
        params = {**a["params"], **(cfg.get("params") or {})}
        limits = {**a["limits"], **(cfg.get("limits") or {})}
        rec = {"agent": a["id"], "title": a["title"], "key": f"{a['id']}@{at.isoformat()}", "scheduled": at.isoformat(),
               "attempts": [], "status": None, "steps": [], "tool_calls": [], "changed": [], "left": [], "summary": "",
               "tokens_in": 0, "tokens_out": 0, "usd": 0.0, "seconds": 0.0, "as": a["as"], "params": params, "limits": limits}
        t = at
        for k in range(3):
            ok, why = self.health(t)
            rec["attempts"].append({"at": t.isoformat(), "ok": ok, "why": why})
            if ok:
                break
            t = at + dt.timedelta(minutes=15 * (k + 1))
        else:
            rec["status"], rec["summary"] = "failed", "Ledgerline did not answer at three tries; nothing was done. It runs again at its next time."
            return rec
        if rec["attempts"][-1]["at"] != at.isoformat():
            rec["ran_at"] = t.isoformat()
        self.mine = []
        t0 = time.time()
        who = PEOPLE[a["as"]]
        commit_note = "" if limits.get("may_commit", True) else " (you may not commit: every write is a preview)"
        instructions = a["instructions"].format(**params, commit_note=commit_note if a["id"] == "match" else "")
        if a["id"] == "match" and not limits.get("may_commit", True):
            instructions = instructions.replace("post_invoice with confirm=true", "post_invoice with confirm=false (a preview for Luis)")
        system = SYSTEM.format(instructions=instructions, name=who["name"], user=a["as"], role=who["role"],
                               now=t.strftime("%A %-d %B %Y, %H:%M"), notes=notes or "(none: this is the first run)")
        from .engine import SPECS
        schemas = [SPECS[n].schema() for n in a["tools"]]
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": "Run now."}]
        llm = self.llm_for("gemini:gemini-3.8-flash")
        reply = None
        for step in range(limits["max_steps"]):
            if rec["tokens_in"] > limits["max_tokens"]:
                rec["stopped"] = f"token budget reached ({rec['tokens_in']:,} of {limits['max_tokens']:,})"
                break
            r = llm.chat(msgs, tools=schemas)
            rec["tokens_in"] += r.tokens_in
            rec["tokens_out"] += r.tokens_out
            rec["usd"] = round(rec["usd"] + _usd(r), 6)
            step_rec = {"n": step + 1, "text": (r.content or "")[:400], "calls": [], "tokens_in": r.tokens_in, "seconds": r.seconds}
            rec["steps"].append(step_rec)
            msgs.append(r.message())
            if not r.tool_calls:
                reply = (r.content or "").strip()
                break
            for tc in r.tool_calls:
                args = dict(tc.arguments or {})
                out = self.guarded(a, limits, tc.name, args, t)
                c = {"tool": tc.name, "args": args, "ok": bool(out.get("ok")), "summary": _sum(out)}
                step_rec["calls"].append(c)
                rec["tool_calls"].append(c)
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)[:12000]})
        else:
            rec["stopped"] = f"step limit reached ({limits['max_steps']})"
        if reply is None:   # a limit stopped the loop: the harness asks for one last sentence, without tools
            msgs.append({"role": "user", "content": f"[harness] Stop here: {rec['stopped']}. In one or two sentences, say what "
                                                    "you did and what is left for a person. No tools."})
            r = llm.chat(msgs, tools=schemas, tool_choice="none")
            rec["tokens_in"] += r.tokens_in
            rec["tokens_out"] += r.tokens_out
            rec["usd"] = round(rec["usd"] + _usd(r), 6)
            reply = (r.content or "").strip() or None
        rec["summary"] = reply or rec.get("stopped") or "(no summary)"
        rec["status"] = "retried" if len(rec["attempts"]) > 1 else "ok"
        rec["seconds"] = round(time.time() - t0, 2)
        rec["changed"] = changes_from_calls(self.mine)
        rec["left"] = left_for_person(self.erp)
        return rec

    def guarded(self, a, limits, name, args, t) -> dict:
        """The harness between the agent and its tools: only its own tools; no e-mail out; previews when it may not commit."""
        if name not in a["tools"]:
            return {"ok": False, "error": f"{name} is not one of this agent's tools.", "next_step": "Use only your tools."}
        if name == "send_message" and not str(args.get("to", "")).startswith("@"):
            return {"ok": False, "error": "A background agent may not e-mail anyone outside Northbridge.",
                    "next_step": "Use draft_message: a person reads it and sends it."}
        if not limits.get("may_commit", True) and "confirm" in args:
            args["confirm"] = False
        with self.erp.lock:
            n0 = len(self.erp.calls)
            out = self.call_tool(a["as"], name, args, t)
            self.mine += self.erp.calls[n0:]
        return out


def _sum(out: dict) -> str:
    from .engine import summary
    return summary(out)[:200]


def plan(agents_cfg: dict, routines: list[dict], a: dt.datetime, b: dt.datetime) -> list[tuple]:
    """Every run due in (a, b]: (time, "agent"|"routine", id)."""
    out = []
    for aid, cfg in agents_cfg.items():
        if cfg.get("on"):
            out += [(t, "agent", aid) for t in fires(cfg.get("schedule") or BY_ID[aid]["schedule"], a, b)]
    for r in routines:
        trig = next((n for n in r["workflow"]["nodes"] if n["type"] == "trigger"), {})
        c = trig.get("config", {})
        if r.get("scheduled") and c.get("kind") == "schedule":
            out += [(t, "routine", r["id"]) for t in fires(c, a, b)]
    return sorted(out, key=lambda x: (x[0], x[1], x[2]))


def default_config() -> dict:
    return {a["id"]: {"on": a["default_on"], "schedule": copy.deepcopy(a["schedule"]), "params": dict(a["params"]),
                      "limits": dict(a["limits"])} for a in AGENTS}


def catalog() -> list[dict]:
    return [{"id": a["id"], "title": a["title"], "icon": a["icon"], "as": a["as"], "as_name": PEOPLE[a["as"]]["name"],
             "what": a["what"], "tools": a["tools"], "schedule": a["schedule"], "schedule_text": schedule_text(a["schedule"]),
             "limits": a["limits"], "params": a["params"]} for a in AGENTS]
