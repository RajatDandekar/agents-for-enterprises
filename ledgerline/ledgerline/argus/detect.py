"""Aegis (the Lecture 7 demo): what the guard bench and the detector bench show.

Nothing here is a guard or a detector. Every check below runs the course's own code and reports what it did:
    the code guards      course/l6/guards.py   Guards.before / after / tool_text / on_output
    the forced attacks   course/l6/nb7.py      sandbox, hear, at_boundary, forced (no model is called)
    the classifier       guards.injection_score        Presidio   guards.redact
    the second model     guards.LLM_CHECK + guards.llm_check (the prompt of NB7b, character for character)
The line numbers in SRC point into those files on GitHub, so a student can open the lines a card talks about.
"""
from __future__ import annotations

import json
import threading

from ..course.l6 import guards as G
from ..course.l6 import labelled, nb7
from ..course.l6.agent import JUDGE_MODEL, usd
from ..course.l6.attacks import ATTACKS
from ..hermes.engine import SPECS

REPO = "https://github.com/RajatDandekar/agents-for-enterprises/blob/main/"
GUARDS_PY = "ledgerline/ledgerline/course/l6/guards.py"
NB7_PY = "ledgerline/ledgerline/course/l6/nb7.py"
NB7B_PY = "lectures/L6b-guardrails/NB7b_detectors.py"
COLAB = "https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6b-guardrails/"
NOTEBOOKS = {"NB7a": ("NB7a · A guard, written by hand", COLAB + "NB7a_guards.ipynb"),
             "NB7b": ("NB7b · Guards that read: three detectors, four numbers", COLAB + "NB7b_detectors.ipynb"),
             "NB7c": ("NB7c · A guard framework: NeMo Guardrails", COLAB + "NB7c_nemo_guardrails.ipynb"),
             "NB7d": ("NB7d · Red-teaming", COLAB + "NB7d_red_team.ipynb")}

# guard or detector -> [(what these lines do, file, first line, last line)]
SRC = {
    "identity": [("before(): a service account may not write", GUARDS_PY, 209, 213)],
    "approvals": [("before(): only the approver Ledgerline waits for", GUARDS_PY, 214, 220)],
    "provenance": [("before(): after outside text, nothing leaves and nothing commits", GUARDS_PY, 221, 231),
                   ("after(): remember that this turn read outside text", GUARDS_PY, 306, 307),
                   ("tool_text(): wrap outside text as data", GUARDS_PY, 329, 331)],
    "confirm_yes": [("before(): a preview in an earlier turn, and a yes now", GUARDS_PY, 232, 238),
                    ("recorded_yes(): the yes is read by code", GUARDS_PY, 62, 64),
                    ("after(): remember which document was previewed", GUARDS_PY, 300, 303)],
    "limits": [("before(): one commit a turn, known addresses, 10,000 units", GUARDS_PY, 239, 250)],
    "never_events": [("before(): calls _never()", GUARDS_PY, 251, 254),
                     ("_never(): certificate, second order, twin supplier", GUARDS_PY, 261, 296)],
    "injection_clf": [("injection_score(): the classifier", GUARDS_PY, 100, 114),
                      ("on_input(): on the message", GUARDS_PY, 192, 200),
                      ("tool_text(): on an e-mail the agent opened", GUARDS_PY, 315, 328)],
    "pii": [("redact(): Presidio", GUARDS_PY, 136, 150), ("on_input(): on the message", GUARDS_PY, 185, 191),
            ("on_output(): on the reply", GUARDS_PY, 348, 353)],
    "llm_check": [("the prompt and llm_check(), as taught", NB7B_PY, 247, 272)],
    "spotlight": [("tool_text(): wrap outside text as data", GUARDS_PY, 329, 331),
                  ("before(): what the turn may not do after reading it", GUARDS_PY, 221, 231)],
    "output_check": [("on_output(): every £ figure against the tool results", GUARDS_PY, 336, 347),
                     ("after(): collect the numbers the tools returned", GUARDS_PY, 304, 305),
                     ("amounts(): find the £ figures in a reply", GUARDS_PY, 77, 87)],
    "tool boundary": [("at_boundary(): before(), the tool, after()", NB7_PY, 178, 191)],
}


def source(key: str) -> list[dict]:
    return [{"what": w, "file": f.rsplit("/", 1)[-1], "lines": f"{a}–{b}", "url": f"{REPO}{f}#L{a}-L{b}"}
            for w, f, a, b in SRC.get(key, [])]


def notebook(key: str) -> dict:
    return {"id": key, "title": NOTEBOOKS[key][0], "url": NOTEBOOKS[key][1]}


def guard_card(gid: str) -> dict | None:
    t = G.GUARDS.get(gid)
    if not t:
        return None
    return {"id": gid, "title": t[0], "kind": t[1], "where": t[2], "what": t[3], "source": source(gid)}


# ================================================================ the guard bench (no model)
def _text(out, limit: int = 2400) -> str:
    s = json.dumps(out, default=str, ensure_ascii=False, indent=1)
    return s if len(s) <= limit else s[:limit].rstrip() + "\n… (cut)"


def _call(c: dict) -> dict:
    """One tool call at the boundary, as the page shows it: the call, what came back, and who answered."""
    out = c.get("out") or {}
    gid = (c.get("refused_by") or "").replace("guard: ", "") or None
    line = nb7.call_line({"tool": c["tool"], "args": c["args"], "ok": c["ok"], "refused_by": c.get("refused_by"), "out": out})
    answer = line.split("  ->  ", 1)[-1]
    if answer == "ok":                                       # the tool ran and gave something back: say what, briefly
        keep = {k: v for k, v in out.items() if k not in ("ok", "messages") and not isinstance(v, (dict, list))}
        n = len(out.get("messages") or [])
        answer = ("ok: " + (f"{n} e-mail{'s' if n != 1 else ''} returned, written outside Northbridge" if n else
                           ", ".join(f"{k}={v}" for k, v in list(keep.items())[:4]) or "done"))
    row = {"tool": c["tool"], "args": c["args"], "ok": bool(c["ok"]), "answer": answer, "out": _text(out),
           "by": "guard" if gid else "ledgerline"}
    if gid:
        row["guard"] = {**(guard_card(gid) or {"id": gid, "title": gid, "source": []}), "rule": c.get("rule"),
                        "reason": out.get("error") or c.get("error"), "next_step": out.get("next_step") or c.get("next_step")}
    return row


def _side(r: dict) -> dict:
    return {"worked": r["worked"], "why": r["why"], "stopped_by": r.get("stopped_by"), "reason": r.get("reason"),
            "saved": r.get("saved"), "calls": [_call(c) for c in r["calls"]]}


def _attack_card(aid: str) -> dict:
    a = next(x for x in ATTACKS if x["id"] == aid)
    return {"id": aid, "title": a["title"], "owasp": a["owasp"], "channel": a["channel"], "says": a["turns"],
            "session": a.get("session"), "has_mail": bool(a.get("mail")), "setup": a.get("setup") or [],
            "calls": [{"tool": t, "args": args} for t, args in nb7.FORCED[aid]]}


def bench_info() -> dict:
    tools = []
    for name in sorted(SPECS):
        sch = SPECS[name].spec.get("input_schema", {})
        props, req = sch.get("properties", {}), sch.get("required", [])
        tools.append({"name": name, "writes": bool(SPECS[name].writes),
                      "args": [{"name": k, "type": v.get("type", ""), "required": k in req,
                                "about": (v.get("description") or "")[:140]} for k, v in props.items()]})
    return {"attacks": [_attack_card(k) for k in nb7.FORCED], "tools": tools,
            "guards": [guard_card(g) for g in nb7.CODE_GUARDS], "usual": nb7.USUAL,
            "boundary": source("tool boundary"), "notebook": notebook("NB7a"), "red_team": notebook("NB7d")}


_bench_lock = threading.Lock()
_BENCH: dict = {}


def bench_one(aid: str) -> dict:
    """One forced attack on two fresh sandboxes: no guards, then the code guards. No model, no clock and no chance are
    involved, so the same calls give the same answer every time; a class pressing the button together shares one run."""
    with _bench_lock:
        if aid not in _BENCH:
            off = nb7.forced(aid, None, outs=True)
            on = nb7.forced(aid, G.Guards(nb7.CODE_GUARDS), outs=True)
            _BENCH[aid] = {**_attack_card(aid), "off": _side(off), "on": _side(on)}
        return _BENCH[aid]


def bench_run(which: str) -> dict:
    ids = list(nb7.FORCED) if which == "all" else [which]
    rows = [bench_one(i) for i in ids]
    return {"rows": rows, "totals": {"attacks": len(rows), "worked_off": sum(1 for r in rows if r["off"]["worked"]),
                                     "worked_on": sum(1 for r in rows if r["on"]["worked"])}}


def bench_call(tool: str, args: dict, heard: str = "") -> dict:
    """One call of your own on two fresh sandboxes: no guards, and the code guards. `heard` is what Emma said in this turn
    (the confirm guard reads it for a yes)."""
    def one(guards):
        ag = nb7.sandbox(guards)
        nb7.hear(ag, heard or "")
        try:
            out = nb7.at_boundary(ag, tool, json.loads(json.dumps(args)))
        except Exception as e:  # noqa: BLE001      a call the tool cannot even read (a wrong type): say so, never crash
            out = {"ok": False, "error": f"The tool could not run with these arguments ({type(e).__name__}: {str(e)[:160]})."}
        c = {"tool": tool, "args": args, "ok": bool(out.get("ok", True)), "refused_by": out.get("refused_by"),
             "rule": out.get("rule"), "out": out}
        return {"calls": [_call(c)], "saved": nb7.holds(ag.writes())}
    return {"tool": tool, "args": args, "heard": heard, "off": one(None), "on": one(G.Guards(nb7.CODE_GUARDS))}


# ================================================================ the detectors
EXAMPLES = [   # (id in the labelled set, the chip's words, what it is)
    ("benign-01", "Order the usual", "an ordinary request"),
    ("benign-14", "Pretend you're Emma's colleague", "an ordinary request that sounds like role-play"),
    ("att-A01", "Ignore your rules", "a direct attack"),
    ("att-A19", "Hidden in a translation", "a direct attack, hidden in a translation task"),
    ("pii-07", "A card number", "a message with payment data"),
    ("mail-MSG-0901", "The poisoned invoice", "an e-mail from outside, with instructions for the assistant in it"),
]


def examples() -> list[dict]:
    by = {x["id"]: x for x in labelled.INJECTION + labelled.PII}
    return [{"id": k, "chip": chip, "what": what, "label": bool(by[k]["label"]), "text": by[k]["text"],
             "set": "PII" if k.startswith(("pii", "nopii")) else "injection",
             "channel": "tool result" if k.startswith("mail") else "message in"} for k, chip, what in EXAMPLES]


def detect_info() -> dict:
    judge = JUDGE_MODEL.split(":", 1)[-1]
    return {"examples": examples(), "detectors": [
        {"id": "injection_clf", "title": "Injection classifier", "kind": "a small model on our own CPU",
         "where": ["message in", "tool result"],
         "runs": "On Emma's message before the agent (the model) reads it, and on the body of an e-mail the agent opened.",
         "model": "protectai/deberta-v3-base-prompt-injection-v2 (Hugging Face transformers)", "threshold": 0.5,
         "numbers": "In NB7b: caught 12 of 15 attacks, 4 false alarms on 26 ordinary texts, 179 ms, US$0.",
         "source": source("injection_clf"), "notebook": notebook("NB7b")},
        {"id": "pii", "title": "Personal and payment data (Presidio)", "kind": "patterns and a small language model, no LLM",
         "where": ["message in", "reply out"],
         "runs": "On Emma's message (the trace keeps the masked text) and on the reply before Emma reads it.",
         "model": "Microsoft Presidio with spaCy en_core_web_sm; entities: " + ", ".join(G.PII_ENTITIES),
         "threshold": 0.4, "source": source("pii"), "notebook": notebook("NB7b")},
        {"id": "llm_check", "title": "A second model reads the text", "kind": "one extra model call",
         "where": ["message in", "tool result"],
         "runs": "A second model, not the agent. It has no tools and no memory; it gets this prompt with the text in "
                 "place of {text}, and answers ATTACK or SAFE with a reason. No clear verdict counts as a flag.",
         "model": judge, "prompt": G.LLM_CHECK,
         "numbers": "In NB7b: caught 15 of 15 attacks, 1 false alarm on 26 ordinary texts, 1.2 s, about US$0.00007 a check.",
         "note": "Taught in NB7b. It is not one of Ask Northbridge's guards: here you run it by hand.",
         "source": source("llm_check"), "notebook": notebook("NB7b")},
        {"id": "spotlight", "title": "Spotlighting, and the mark it leaves", "kind": "code, no model",
         "where": ["tool result"],
         "runs": "When a tool returns text written outside Northbridge, code wraps it in <external> tags before the "
                 "agent (the model) reads it, and marks the turn: until the turn ends, nothing is saved and nothing "
                 "is sent to an outside address.",
         "source": source("spotlight"), "notebook": notebook("NB7b")},
        {"id": "output_check", "title": "Reply check: every £ figure comes from Ledgerline", "kind": "code, no model",
         "where": ["reply out"],
         "runs": "Before Emma reads the reply, code finds every £ amount in it and looks for each one in the tool "
                 "results of this conversation. A figure that is in none of them gets a note.",
         "source": source("output_check"), "notebook": notebook("NB7a")},
    ]}


_ref_lock = threading.Lock()
_REF = None


def _reference():
    """One sandbox with the reply check on and one read-only tool call made in it (a preview of Emma's usual), so the
    check has tool numbers to compare a reply with. Built once: nothing in it is ever written."""
    global _REF
    with _ref_lock:
        if _REF is None:
            g = G.Guards(["output_check"])
            ag = nb7.sandbox(g)
            args = {**nb7.USUAL, "confirm": False}
            out = nb7.at_boundary(ag, "create_purchase_request", args)
            p = out.get("preview") or {}
            value, rate = float(p.get("estimated_value") or 0), float(p.get("estimated_rate") or 0)
            reply = (f"The usual is {args['quantity']:,} × {args['item_code']} on {args['cost_centre']}: "
                     f"£{rate:,.2f} each, £{value:,.2f} with VAT. That is about £310,000 less than last quarter. "
                     "Shall I raise it?")
            _REF = {"agent": ag, "guards": g, "call": {"tool": "create_purchase_request", "args": args, "out": out},
                    "reply": reply}
        return _REF


def default_reply() -> str:
    return _reference()["reply"]


def _safe(key: str, fn) -> dict:
    try:
        return {"id": key, **fn()}
    except Exception as e:  # noqa: BLE001
        msg = getattr(e, "msg", None) or f"This check could not run on the server ({type(e).__name__})."
        print(f"[aegis] detector {key} failed:", type(e).__name__, str(e)[:300])
        return {"id": key, "error": msg}


def detect(text: str, reply: str | None, chat) -> dict:
    """Every detector on one text. `chat` makes the second model's call (and charges the student's budget)."""
    def clf():
        p, ms = G.injection_score(text)
        return {"score": round(p, 4), "threshold": 0.5, "flag": p >= 0.5, "ms": ms,
                "verdict": "flagged as an injection" if p >= 0.5 else "passed"}

    def pii():
        clean, found, ms = G.redact(text)
        return {"flag": bool(found), "entities": found, "redacted": clean, "ms": ms,
                "verdict": f"{len(found)} item{'s' if len(found) != 1 else ''} masked" if found else "nothing to mask"}

    def llm():
        r = G.llm_check(text, chat)
        answer = r["answer"]
        reason = answer.split(" - ", 1)[1].strip() if " - " in answer else answer
        return {"flag": r["flag"], "verdict": r["verdict"], "reason": reason, "answer": answer, "ms": round(r["ms"], 1),
                "usd": usd(JUDGE_MODEL, r["tokens_in"], r["tokens_out"]), "tokens_in": r["tokens_in"],
                "tokens_out": r["tokens_out"], "model": JUDGE_MODEL.split(":", 1)[-1],
                "sent": G.LLM_CHECK.format(text=text)}

    def spot():
        out = {"ok": True, "messages": [{"message_id": "MSG-DEMO", "sender": "someone outside Northbridge",
                                         "subject": "(the text in the box, as an e-mail)", "body": text, "status": "NEW"}],
               "count": 1, "trust": "untrusted: written by someone outside Northbridge"}
        rec = {"guard_events": []}
        g = G.Guards(["provenance"])
        g.on_input(None, "", rec)
        g.after(None, "read_mailbox", {}, out, rec)
        wrapped = g.tool_text(None, "read_mailbox", out, json.dumps(out, default=str, ensure_ascii=False), rec)
        return {"wrapped": wrapped, "tool": "read_mailbox", "marked": g.tainted_turn == g.turn,
                "verdict": "wrapped as outside text; the turn is marked",
                "events": [{k: e.get(k) for k in ("guard", "decision", "where", "why")} for e in rec["guard_events"]]}

    def out_check():
        ref = _reference()
        said = (reply or "").strip() or ref["reply"]
        rec = {"guard_events": []}
        with _ref_lock:
            checked = ref["guards"].on_output(ref["agent"], said, rec)
        ev = next((e for e in rec["guard_events"] if e["guard"] == "output_check"), {})
        bad = ev.get("amounts") or []
        return {"reply": said, "checked_reply": checked, "found": G.amounts(said), "flagged": bad, "flag": bool(bad),
                "verdict": (f"{len(bad)} figure{'s' if len(bad) != 1 else ''} not from Ledgerline" if bad
                            else "every £ figure is in a tool result"), "why": ev.get("why"),
                "call": {"tool": ref["call"]["tool"], "args": ref["call"]["args"], "out": _text(ref["call"]["out"], 1200)},
                "default": not (reply or "").strip()}

    return {"text": text, "chars": len(text),
            "results": [_safe("injection_clf", clf), _safe("pii", pii), _safe("llm_check", llm), _safe("spotlight", spot),
                        _safe("output_check", out_check)]}
