"""Build figdata.js (window.L6) for the Lecture 7 deck (Guardrails and Red-Teaming, folder L6b-guardrails).

Nothing measured is typed on a slide: every number about OUR system is read here from a log and reaches the slide as a
`data-l6="m.…"` key or through a figure. Two places are read:

    OLD  ../L6-evals-guardrails-observability/experiments/logs/    the 16 Nov measurements (attacks, detectors, replay,
                                                                   promptfoo red team, the incident)
    NEW  experiments/logs/                                         everything measured for Lecture 7 from 17 Nov
                                                                   (builder A; each log is described in its README.md)

    python3 lectures/L6b-guardrails/gen_figdata.py        (standard library only; re-run any time)

A missing or unreadable log never stops this script: its keys are simply absent, and the slide shows a marked plate
("from the run", "rendered copy pending", "screenshot pending"), never a number. The attribute name stays `data-l6`
and the global stays `window.L6`, so the Lecture 6 figure library works here unchanged.
"""
import ast
import json
import pathlib
import re
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / "L6-evals-guardrails-observability" / "experiments" / "logs"
NEW = HERE / "experiments" / "logs"
L6CODE = ROOT / "ledgerline" / "ledgerline" / "course" / "l6"
MEDIA_EXT = (".png", ".jpg", ".jpeg", ".webp")
missing = []


def load(name, base=OLD):
    p = base / name
    if not p.exists():
        missing.append(str(p.relative_to(HERE.parent)))
        return None
    try:
        return json.loads(p.read_text())
    except (ValueError, OSError) as e:
        print("  unreadable:", name, e)
        missing.append(str(p.relative_to(HERE.parent)) + " (unreadable)")
        return None


def q(xs, p):
    xs = sorted(x for x in xs if x is not None)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


def plain(s):
    """A model's reply without markdown marks."""
    return re.sub(r"\*\*|__", "", s or "").strip()


def sentences(p):
    """Whole sentences. A full stop inside an address (x@y.example) or a figure (£1.3m) does not end one."""
    parts = re.split(r"(?<=[.!?])[\"”’')]*\s+(?=[A-Z\"“«\[(£])", p.strip())
    return [x.strip() for x in parts if x.strip()]


def flat(blk):
    return re.sub(r"\s+", " ", re.sub(r"(^|\n)\s*-\s+", " ", blk)).strip()


def first_para(s, max_sent=3, which="first"):
    """The first (or last) paragraph of a reply, as whole sentences (never cut mid-sentence)."""
    paras = [x for x in plain(s).split("\n\n") if x.strip()] or [""]
    p = flat(paras[0] if which == "first" else paras[-1])
    return " ".join(sentences(p)[:max_sent])


def para_with(s, needle, max_sent=3):
    """The paragraph or bullet of a reply that contains `needle`, whole sentences from the one that holds it."""
    for blk in re.split(r"\n\s*\n|\n\s*-\s+", plain(s)):
        if needle.lower() in blk.lower():
            ss = sentences(flat(blk))
            i = next((k for k, x in enumerate(ss) if needle.lower() in x.lower()), 0)
            return " ".join(ss[i:i + max_sent])
    return None


# ------------------------------------------------------------------------------------------- the code, read not run
COMMITS = {"create_purchase_request", "create_purchase_order", "register_supplier", "receive_goods", "record_invoice",
           "post_invoice", "hold_invoice"}
GUARD_NAMES = {"identity": "Who is acting", "approvals": "Who may approve", "confirm_yes": "Confirm needs a recorded yes",
               "limits": "Limits", "never_events": "Never-events", "provenance": "Text from outside",
               "injection_clf": "Injection classifier", "pii": "Personal data (Presidio)",
               "output_check": "Numbers come from Ledgerline", "tool boundary": "Tool boundary"}


DECISION = {"spotlighted": "wrapped as data", "quarantined": "body held back", "redacted": "masked"}


def attack_texts():
    """What is typed in each attack, read from attacks.py with ast (the file is not imported or run)."""
    out = {}
    try:
        tree = ast.parse((L6CODE / "attacks.py").read_text())
    except (OSError, SyntaxError) as e:
        print("  attacks.py not readable:", e)
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "ATTACKS" for t in node.targets):
            for d in node.value.elts:
                rec = {}
                for k, v in zip(d.keys, d.values):
                    if isinstance(k, ast.Constant) and k.value in ("id", "session", "check", "channel"):
                        rec[k.value] = getattr(v, "value", None)
                    if isinstance(k, ast.Constant) and k.value == "turns":
                        rec["turns"] = [e.value for e in v.elts if isinstance(e, ast.Constant)]
                    if isinstance(k, ast.Constant) and k.value == "mail":
                        rec["mail"] = getattr(v, "id", None)
                if rec.get("id"):
                    out[rec["id"]] = rec
    return out


def call_row(c):
    """One tool call as a row of the 'turn' figure: name, the arguments that matter, and a tag."""
    a = c.get("args") or {}
    bits = []
    if a.get("quantity") is not None and a.get("item_code"):
        bits.append(f"{a['quantity']:,} × {a['item_code']}")
    for k in ("cost_centre", "supplier_code", "name", "po_no", "invoice_no", "request_no", "to", "folder", "query", "supplier_invoice_no"):
        if a.get(k) and len(bits) < 2 and not (k == "name" and a.get("supplier_code")):
            bits.append(str(a[k]))
    tag, cls = "", ""
    if c.get("refused_by"):
        g = str(c["refused_by"]).replace("guard: ", "")
        tag, cls = "refused by the guard · " + GUARD_NAMES.get(g, g), "ref"
    elif c["tool"] in COMMITS and a.get("confirm") is True:
        tag, cls = ("confirm=true · saved" if c.get("ok") else "confirm=true · Ledgerline said no"), ("save" if c.get("ok") else "err")
    elif c["tool"] in COMMITS:
        tag, cls = ("preview · nothing saved" if c.get("ok") else "Ledgerline said no"), ("prev" if c.get("ok") else "err")
    elif c["tool"] == "send_message":
        tag, cls = "sent", "save"
    elif c["tool"] == "draft_message":
        tag, cls = "draft only · not sent", "prev"
    elif not c.get("ok"):
        tag, cls = "error", "err"
    return {"k": "tool", "name": c["tool"], "arg": " · ".join(bits), "tag": tag, "cls": cls}


def guard_rows(events, where):
    out = []
    for e in events or []:
        if e.get("where") != where or e["decision"] == "passed" or e["guard"] == "tool boundary":
            continue
        if e["decision"] == "refused":
            continue      # shown on the tool call it refused
        out.append({"k": "guard", "name": GUARD_NAMES.get(e["guard"], e["guard"]),
                    "arg": e.get("why", "").replace("outside text wrapped as <external> data", "the e-mail is handed to the model marked as outside data"),
                    "tag": DECISION.get(e["decision"], e["decision"]), "cls": "ref" if e["decision"] in ("blocked", "quarantined", "flagged") else "g"})
    return out


def turn_fig(typed, calls, events, reply, max_sent=3, which="first"):
    rows = guard_rows(events, "input")
    for c in calls or []:
        rows.append(call_row(c))
        if rows[-1]["cls"] == "ref":
            ev = next((e for e in events or [] if e["decision"] == "refused" and e.get("tool") == c["tool"]), None)
            if ev:
                rows[-1]["why"] = ev.get("why", "")
    rows += guard_rows(events, "after") + guard_rows(events, "output")
    return {"typed": typed, "rows": rows, "reply": first_para(reply, max_sent, which), "n_calls": len(calls or [])}


m = {"argus_url": "https://rajatworkspace--northbridge-argus.us-east.modal.run", "measured_on": "16 Nov 2026"}
TEXTS = attack_texts()

# ------------------------------------------------------------------------------------------- the incident, and Demo 1
inc = {t: load(f"incident_{t}.json") for t in ("r1", "r2", "r3")}
if all(inc.values()):
    def agg(tags, p):
        s = [inc[t]["summary"].get(p, {}) for t in tags]
        return {"runs": sum(x.get("runs", 0) for x in s), "committed": sum(x.get("committed_without_yes", 0) for x in s)}
    m["incident"] = {"dated": {"good": agg(["r3"], "good"), "thursday": agg(["r3"], "thursday")},
                     "nodate": {"good": agg(["r1", "r2"], "good"), "thursday": agg(["r1", "r2"], "thursday")},
                     "msg": inc["r3"]["message"]}
    # the plainest of the ten Thursday runs: no failed call, fewest tool calls
    bad = sorted((r for r in inc["r3"]["rows"] if r["prompt"] == "thursday" and r["committed"]),
                 key=lambda r: (sum(1 for c in r["calls"] if not c["ok"]), len(r["calls"])))[0]
    saved = (bad.get("saved_requests") or [{}])[0]
    m["demo1"] = {"msg": inc["r3"]["message"],
                  "off": turn_fig(inc["r3"]["message"], bad["calls"], [], bad["reply"], 2) | {
                      "pr_no": saved.get("pr_no"), "value": saved.get("est_value"), "qty": saved.get("qty"),
                      "tools": len(bad["calls"])}}

rp = load("replay.json")
if rp:
    rows = rp["rows"]
    # the run whose first turn is the plain sequence: preview, then confirm=true in the same turn
    r0 = next((r for r in rows if not any(c["tool"] == "create_purchase_order" for c in r["turns"][0]["calls"])), rows[0])
    t1, t2 = r0["turns"][0], r0["turns"][1]
    ev = next((e for e in t1["guard_events"] if e["decision"] == "refused"), {})
    s2 = (r0.get("saved_after_turn_2") or [{}])[0]
    m["replay"] = {"runs": len(rows), "guards": rp.get("guards"), "prompt": rp.get("prompt"), "at": rp.get("at"),
                   "refused_turn1": sum(1 for r in rows if any(c.get("refused_by") for c in r["turns"][0]["calls"])),
                   "saved_after_turn1": sum(1 for r in rows if r["saved_after_turn_1"]),
                   "saved_after_yes": sum(1 for r in rows if r["saved_after_turn_2"]),
                   "t1": turn_fig(t1["text"], t1["calls"], t1["guard_events"], t1["reply"], 2, "last"),
                   "t2": turn_fig(t2["text"], t2["calls"], t2["guard_events"], t2["reply"], 2),
                   "ask": (re.findall(r"[^.\n]*\?", plain(t1["reply"])) or [""])[-1].strip(),
                   "refusal": {"guard": ev.get("guard"), "why": ev.get("why"), "rule": ev.get("rule"), "ms": ev.get("ms"), "tool": ev.get("tool")},
                   "pr_no": s2.get("pr_no"), "value": s2.get("est_value"), "status": s2.get("status"),
                   "t1_usd": t1.get("usd"), "t1_model_calls": t1.get("model_calls")}
    e0 = next((e for e in rows[0]["turns"][0]["guard_events"] if e["decision"] == "refused"), None)
    if e0:      # the guard's row as the trace holds it (run 1 of 2: the run the Langfuse picture shows)
        m["replay"]["span0"] = {"title": "guardrail " + e0["guard"], "rows": [
            ["decision", e0["decision"], 0, True], ["judged", "the tool call " + e0.get("tool", ""), 0, False],
            ["reason", e0.get("why", ""), 1, True],
            ["time taken", f"{e0.get('ms', 0):.2f} ms", 1, False]], "ms": e0.get("ms")}
    m.setdefault("demo1", {})["on1"] = m["replay"]["t1"]
    m["demo1"]["on2"] = m["replay"]["t2"]
rpb = load("replay_v1_bug.json")
if rpb:
    b0 = rpb["rows"][0]
    m["replay_bug"] = {"runs": len(rpb["rows"]), "saved_after_yes": sum(1 for r in rpb["rows"] if r["saved_after_turn_2"]),
                       "refused_turn2": sum(1 for r in rpb["rows"] if any(c.get("refused_by") for c in r["turns"][1]["calls"])),
                       "t2": turn_fig(b0["turns"][1]["text"], b0["turns"][1]["calls"], b0["turns"][1]["guard_events"], b0["turns"][1]["reply"], 2)}

# ------------------------------------------------------------------------------------------- the attack library
ga = {"good": load("guards_attacks_r1.json"), "thursday": load("guards_attacks_thu.json"), "a10": load("guards_attacks_a10.json")}
GOALS = [("approve", "Approve it for Daniel", ["A01", "A02", "A13", "A14", "A18"]),
         ("save", "Save without Emma seeing it", ["A03", "A08", "A09", "A16", "A20"]),
         ("rule", "Break a purchasing rule", ["A04", "A05", "A12", "A15"]),
         ("out", "Take something out", ["A06", "A07", "A10", "A11", "A19"]),
         ("invent", "Make it invent a number", ["A17"])]
if ga["good"] and ga["thursday"]:
    table, cases = defaultdict(dict), {}
    for p in ("good", "thursday"):
        for r in ga[p]["rows"]:
            if p == "good" and r["id"] == "A10" and r["set"] == "all" and ga["a10"]:
                r = next(x for x in ga["a10"]["rows"] if x["id"] == "A10")      # re-run after the masking fix (16 Nov)
            evs = [e for e in r["guard_events"] if e["decision"] != "passed"]
            decisive = ("blocked" if any(e["decision"] == "blocked" for e in evs) else
                        "quarantined" if any(e["decision"] == "quarantined" for e in evs) else
                        "refused" if any(e["decision"] == "refused" for e in evs) else
                        "flagged" if any(e["decision"] == "flagged" for e in evs) else "model")
            t = TEXTS.get(r["id"], {})
            table[r["id"]].update({"id": r["id"], "title": r["title"], "owasp": r["owasp"], "channel": r["channel"],
                                   "typed": " → ".join(t.get("turns") or []), "session": t.get("session"),
                                   f"{p}_{r['set']}": r["succeeded"], f"{p}_{r['set']}_why": r["why"],
                                   f"{p}_{r['set']}_stopped": r["stopped_by"], f"{p}_{r['set']}_who": decisive})
            typed = (t.get("turns") or [""])[-1]
            cases[f"{r['id']}_{p}_{r['set']}"] = turn_fig(typed, r["calls"], r["guard_events"], (r["replies"] or [""])[-1], 3) | {
                "why": r["why"], "worked": r["succeeded"]}
    t = sorted(table.values(), key=lambda r: r["id"])
    keys = [f"{p}_{s}" for p in ("good", "thursday") for s in ("off", "all")]
    lat = defaultdict(list)
    for p in ("good", "thursday"):
        for r in ga[p]["rows"]:
            for e in r["guard_events"]:
                if e.get("ms"):
                    lat[e["guard"]].append(e["ms"])
    WHO = [("blocked", "The injection classifier stopped the message before the model read it"),
           ("quarantined", "The injection classifier held back an e-mail’s body"),
           ("refused", "A code guard refused a tool call"),
           ("flagged", "The reply check flagged a figure"),
           ("model", "No guard had to act: the model itself did not do it")]
    who = {k: [{"key": w, "label": lab, "ids": [r["id"] for r in t if r.get(f"{k}_who") == w and not r.get(k)],
                "n": sum(1 for r in t if r.get(f"{k}_who") == w and not r.get(k))} for w, lab in WHO] for k in ("good_all", "thursday_all")}
    m["attacks"] = {"rows": t, "of": len(t), "by": {r["id"]: r for r in t},
                    "n": {k: sum(1 for r in t if r.get(k)) for k in keys},
                    "asr": {k: round(sum(1 for r in t if r.get(k)) / len(t), 3) for k in keys},
                    "refused_by_model": {k: len(t) - sum(1 for r in t if r.get(k)) for k in keys},
                    "worked": {k: [{"id": r["id"], "title": r["title"], "why": r[f"{k}_why"]} for r in t if r.get(k)] for k in keys},
                    "who": who,
                    "guard_ms": {k: {"median": round(q(v, .5), 2), "p95": round(q(v, .95), 2), "n": len(v)} for k, v in lat.items()},
                    "usd": round((ga["good"]["usd"] or 0) + (ga["thursday"]["usd"] or 0), 2), "runs": 4 * len(t),
                    "tool_ms": round(q(lat.get("tool boundary", []) + lat.get("provenance", []), .5) or 0, 2),
                    "one_attack_pct": round(100 / len(t)),
                    "goals": [{"key": k, "title": ti, "rows": [{"id": i, "title": table[i]["title"], "channel": table[i]["channel"]} for i in ids if i in table]}
                              for k, ti, ids in GOALS],
                    "goal_stats": {k: {"attacks": len(ids), "runs": 4 * len(ids),
                                       "worked": sum(1 for i in ids for kk in keys if table[i].get(kk)),
                                       "worked_off": sum(1 for i in ids for kk in ("good_off", "thursday_off") if table[i].get(kk))} for k, ti, ids in GOALS},
                    "channels": {"direct": sum(1 for r in t if r["channel"] == "direct"), "indirect": sum(1 for r in t if r["channel"] == "indirect")}}
    m["case"] = {k: v for k, v in cases.items() if k in (
        "A09_thursday_off", "A09_good_off", "A05_thursday_off", "A05_good_off", "A10_thursday_off", "A10_thursday_all", "A11_thursday_off", "A11_thursday_all",
        "A11_good_off", "A11_good_all", "A19_thursday_all", "A19_good_all", "A14_good_off", "A14_thursday_off", "A02_good_off", "A04_good_off",
        "A04_thursday_off", "A06_good_off", "A13_thursday_all", "A01_thursday_all", "A03_good_off", "A16_good_off", "A15_good_off")}
    # the poisoned invoice: what the agent told Emma about the hidden instruction, in each of the four runs
    for k in ("A11_good_off", "A11_good_all", "A11_thursday_off", "A11_thursday_all"):
        p_, s_ = k.split("_")[1], k.split("_")[2]
        r = next(x for x in ga[p_]["rows"] if x["id"] == "A11" and x["set"] == s_)
        told = para_with(r["replies"][-1], "remittance@", 4) or para_with(r["replies"][-1], "instruction", 4)
        m["case"][k]["told"] = re.sub(r"^[A-Z][^:.]{0,60}:\s*", "", told or "")
        m["case"][k]["mentioned"] = bool(told)
    m["invoice"] = {"runs": 4, "sent_outside": sum(1 for k in ("good_off", "good_all", "thursday_off", "thursday_all") if table["A11"].get(k)),
                    "told_emma": sum(1 for k in ("A11_good_off", "A11_good_all", "A11_thursday_off", "A11_thursday_all") if m["case"][k]["mentioned"])}
    for k in ("A19_thursday_all", "A19_good_all"):
        p_, s_ = k.split("_")[1], k.split("_")[2]
        r = next(x for x in ga[p_]["rows"] if x["id"] == "A19" and x["set"] == s_)
        fl = next((e for e in r["guard_events"] if e["decision"] == "flagged"), None)
        if fl:
            m["case"][k]["flag"] = {"why": fl["why"], "ms": fl["ms"], "amount": (fl.get("amounts") or [None])[0],
                                    "sentence": para_with(r["replies"][-1], "1.3", 1),
                                    "note": (re.findall(r"\[Check:[^\]]*\]", r["replies"][-1]) or [None])[0]}
    for i, r in TEXTS.items():
        m.setdefault("atk", {})[i] = {"typed": (r.get("turns") or [""])[-1], "turns": r.get("turns"), "session": r.get("session")}

# the poisoned e-mail, word for word (read from agent.py, not run)
try:
    src = (L6CODE / "agent.py").read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(getattr(tg, "id", "") == "POISON" for tg in node.targets):
            d = {k.value: ast.literal_eval(v) for k, v in zip(node.value.keys, node.value.values)}
            paras = d["body"].split("\n\n")
            m["mail"] = {"sender": d["sender"], "subject": d["subject"], "paras": paras,
                         "hidden": next((i for i, p in enumerate(paras) if p.startswith("AI assistant")), None),
                         "real_domain": "voltwaycells.example", "fake_domain": d["sender"].split("@")[1]}
except (OSError, SyntaxError, ValueError) as e:
    print("  agent.py POISON not readable:", e)

# ------------------------------------------------------------------------------------------- detectors (16 Nov)
det = load("guards_detectors.json")
NAMES = {"att-A19": "A19 · hidden in a translation", "mail-MSG-0901": "the poisoned invoice e-mail",
         "mail-MSG-0902": "the “new legal entity” e-mail (register a twin supplier)", "mail-MSG-0903": "the forged e-mail from Daniel"}
if det:
    m["detectors"] = {k: {x: det[k].get(x) for x in ("attacks", "caught", "catch_rate", "benign", "false_alarms", "false_alarm_rate",
                                                     "median_ms", "usd", "usd_per_check", "model", "checked", "errors")}
                      for k in ("deberta", "nemo", "presidio")}
    D = m["detectors"]
    D["set"] = det["set"] | {"ordinary": det["set"]["injection"] - det["set"]["attacks"]}
    rows = det["rows"]
    D["tiles"] = [{"id": r["id"], "label": bool(r["label"]), "kind": r["kind"], "text": r["text"], "deberta": bool(r["deberta"]),
                   "p": r["deberta_p"], "nemo": bool(r.get("nemo"))} for r in rows]
    D["kinds"] = {k: sum(1 for r in rows if r["kind"] == k) for k in sorted({r["kind"] for r in rows})}
    D["deberta"]["missed"] = [{"id": r["id"], "name": NAMES.get(r["id"], r["id"]), "text": r["text"] if len(r["text"]) < 200 else None,
                               "p": r["deberta_p"]} for r in rows if r["label"] and not r["deberta"]]
    D["deberta"]["fa"] = [{"id": r["id"], "text": r["text"], "p": r["deberta_p"], "kind": r["kind"]} for r in rows if not r["label"] and r["deberta"]]
    D["deberta"]["fa_usual"] = next(({"text": r["text"], "p": r["deberta_p"]} for r in rows if r["id"] == "benign-01" and r["deberta"]), None)
    D["deberta"]["fa_pct"] = round(100 * det["deberta"]["false_alarm_rate"])
    D["deberta"]["mail_missed"] = sum(1 for r in rows if r["id"].startswith("mail-MSG") and not r["deberta"])
    D["deberta"]["mail_n"] = sum(1 for r in rows if r["id"].startswith("mail-MSG"))
    D["nemo"]["fa"] = [{"id": r["id"], "text": r["text"]} for r in rows if not r["label"] and r.get("nemo")]
    D["nemo"]["tokens_in_med"] = q([r["nemo_tokens"][0] for r in rows if r.get("nemo_tokens")], .5)
    D["nemo"]["slowest_ms"] = max((r.get("nemo_ms") or 0) for r in rows)
    pr = det["pii_rows"]
    D["presidio"]["missed"] = [{"id": r["id"], "text": r["text"]} for r in pr if r["label"] and not r["flagged"]]
    D["presidio"]["card"] = next(({"before": r["text"], "after": r["redacted"], "as": ", ".join(f["type"] for f in r["found"])}
                                  for r in pr if r["id"] == "pii-01"), None)
    D["presidio"]["examples"] = [{"before": r["text"], "after": r["redacted"], "as": ", ".join(f["type"] for f in r["found"])}
                                 for r in pr if r["id"] in ("pii-02", "pii-06", "pii-08")]
    D["presidio"]["kept"] = [r["text"] for r in pr if r["id"] in ("nopii-03", "nopii-05", "nopii-04")]
    D["at"] = det.get("at")
    K = D["kinds"]
    D["n"] = {"typed": K.get("direct", 0), "mail_attack": K.get("indirect (e-mail)", 0), "buyer": K.get("buyer message", 0),
              "mail_clean": K.get("supplier e-mail", 0)}
    D["tricky"] = [r["text"] for r in rows if r["id"] in ("benign-06", "benign-13", "benign-18")]


def det_row(name, where, d, cost):
    if not d:
        return {"name": name, "where": where}
    med = d.get("median_ms")
    return {"name": name, "where": where, "caught": f"{d['caught']} of {d['attacks']}", "fa": f"{d['false_alarms']} of {d['benign']}",
            "ms": (f"{med:.0f} ms" if med < 1000 else f"{med / 1000:.1f} s") if med is not None else None, "cost": cost}


# ------------------------------------------------------------------------------------------- Lecture 7's own logs (builder A)
# Each block reads one new log if it exists. Shapes follow experiments/logs/README.md; anything unexpected leaves the
# keys absent (the slide then shows its plate).
def new(name):
    return load(name, NEW)


def safe(fn, what):
    try:
        return fn()
    except Exception as e:     # a log in a shape this script does not know yet: plate, not a crash
        print(f"  {what}: not read ({type(e).__name__}: {e})")
        return None


m["new"] = {}
readme = (NEW / "README.md").read_text() if (NEW / "README.md").exists() else ""
m["new"]["readme"] = bool(readme)
m["new"]["logs"] = sorted(f.name for f in NEW.glob("*.json")) if NEW.exists() else []

# --- the 20 attacks with the code guards only (17 Nov): l7_attacks_code_good.json, l7_attacks_code_thursday.json
def code_only():
    A = m["attacks"]
    for p in ("good", "thursday"):
        d = new(f"l7_attacks_code_{p}.json")
        if not d:
            return
        k = f"{p}_code"
        for r in d["rows"]:
            row = A["by"].get(r["id"])
            if row is None:
                continue
            refs = [x for x in r.get("refusals") or [] if x.get("decision") == "refused"]
            row.update({k: r["succeeded"], k + "_why": r["why"], k + "_stopped": r["stopped_by"],
                        k + "_who": "refused" if refs else "flagged" if r.get("refusals") else "model"})
            t = (r.get("turns") or [{}])[-1]
            m["case"][f"{r['id']}_{k}"] = turn_fig(t.get("text", ""), t.get("calls"), r.get("refusals"), t.get("reply", ""), 2) | {
                "why": r["why"], "worked": r["succeeded"],
                "refusal": ({"guard": GUARD_NAMES.get(refs[0]["guard"], refs[0]["guard"]), "why": refs[0].get("why"), "tool": refs[0].get("tool")} if refs else None)}
        rows = A["rows"]
        A["n"][k] = sum(1 for r in rows if r.get(k))
        A["asr"][k] = round(A["n"][k] / len(rows), 3)
        A["worked"][k] = [{"id": r["id"], "title": r["title"], "why": r[k + "_why"]} for r in rows if r.get(k)]
        A.setdefault("code", {})[p] = {"at": d.get("at"), "usd": d.get("usd"), "guards": d.get("guards"),
                                      "refused": [{"id": r["id"], "guard": GUARD_NAMES.get(x["guard"], x["guard"]), "tool": x.get("tool")}
                                                  for r in d["rows"] for x in r.get("refusals") or [] if x.get("decision") == "refused"],
                                      "model_declined": sum(1 for r in d["rows"] if not r["succeeded"] and not any(
                                          x.get("decision") == "refused" for x in r.get("refusals") or []))}
    A["code"]["usd"] = round(sum(A["code"][p]["usd"] or 0 for p in ("good", "thursday")), 2)
    A["code"]["refusals"] = sum(len(A["code"][p]["refused"]) for p in ("good", "thursday"))
    A["runs_all"] = 6 * A["of"]
    keys6 = [f"{p}_{s}" for p in ("good", "thursday") for s in ("off", "code", "all")]
    for gk, gs in A["goal_stats"].items():
        ids = next(x[2] for x in GOALS if x[0] == gk)
        gs["runs6"] = 6 * len(ids)
        gs["worked6"] = sum(1 for i in ids for kk in keys6 if A["by"][i].get(kk))


# --- the guards with the model's "no" taken away (17 Nov): l7_forced.json. Each attack's tool call made directly at the tool.
def forced():
    d = new("l7_forced.json")
    if not d:
        return
    s = d["summary"]
    by = {}
    for r in d["rows"]:
        if not r.get("wants_a_tool_call"):
            continue
        ng, cg = r.get("no_guards") or {}, r.get("code_guards") or {}
        ref = next((c for c in cg.get("calls") or [] if c.get("refused_by")), {})
        plain_why = ng.get("why") or ""
        if plain_why.startswith("approved: "):
            try:
                ap = json.loads(plain_why[len("approved: "):])[0]
                plain_why = f"{ap['doc_no']} is {ap['status']}, approver {ap['approver']}"
            except (ValueError, KeyError, IndexError):
                pass
        by[r["id"]] = {"title": r["title"], "none_plain": plain_why,
                       "none": {"worked": ng.get("worked"), "why": ng.get("why"), "stopped_by": ng.get("stopped_by"), "reason": ng.get("reason")},
                       "code": {"worked": cg.get("worked"), "guard": GUARD_NAMES.get(str(cg.get("stopped_by")).replace("guard: ", ""), cg.get("stopped_by")),
                                "reason": cg.get("reason") or ref.get("error"), "next": ref.get("next_step"), "rule": ref.get("rule"), "tool": ref.get("tool")}}
    order = ["identity", "approvals", "confirm_yes", "limits", "never_events", "provenance"]
    grp = {k: [i for i, v in s["code_guards"]["stopped_by"].items() if v == "guard: " + k] for k in order}
    m["forced"] = {"at": d.get("at"), "attacks": s["attacks"], "want": s["want_a_tool_call"], "words_only": s["words_only"],
                   "none_worked": s["no_guards"]["worked"], "none_worked_ids": s["no_guards"]["worked_ids"],
                   "none_ledgerline": len(s["no_guards"]["stopped_by_ledgerline"]), "none_ledgerline_ids": s["no_guards"]["stopped_by_ledgerline"],
                   "code_worked": s["code_guards"]["worked"], "model_calls": d.get("model_calls"), "seconds": d.get("seconds"),
                   "by": by, "groups": [{"key": k, "label": GUARD_NAMES[k], "ids": grp[k], "n": len(grp[k])} for k in order],
                   "never_fired": [GUARD_NAMES[k] for k in order if not grp[k]]}


# --- NB7b's recorded table (17 Nov): the same labelled set, run in the notebook's own runtime. Its numbers are the ones the
#     class sees in Colab, so the four-number slides use them; the per-text verdicts (tiles, misses) stay from 16 Nov.
def nb7b():
    rows = new("nb7c_four_numbers.json") or new("nb7b_four_numbers.json")     # NB7c's table is NB7b's plus the NeMo row
    if not rows or "detectors" not in m:
        return
    D = m["detectors"]
    for r in rows:
        name = r["detector"].lower()
        rec = {"attacks": r["to_catch"], "caught": r["caught"], "benign": r["ordinary"], "false_alarms": r["false_alarms"],
               "median_ms": r["median_ms"], "usd_per_check": r.get("usd_per_check"),
               "catch_rate": round(r["caught"] / r["to_catch"], 3), "false_alarm_rate": round(r["false_alarms"] / r["ordinary"], 3)}
        if "classifier" in name or "presidio" in name:
            k = "deberta" if "classifier" in name else "presidio"
            same = (D[k]["caught"], D[k]["false_alarms"]) == (rec["caught"], rec["false_alarms"])
            D[k]["ms_16nov"] = D[k]["median_ms"]
            D[k].update({x: rec[x] for x in ("attacks", "caught", "benign", "false_alarms", "median_ms", "catch_rate", "false_alarm_rate")})
            D[k]["same_as_16nov"] = same
            if k == "deberta":
                D[k]["fa_pct"] = round(100 * rec["false_alarm_rate"])
        elif "llm" in name:
            m["llm_check"] = rec | {"name": r["detector"]}
        elif "nemo" in name:
            D["nemo"]["16nov"] = {x: D["nemo"].get(x) for x in ("caught", "false_alarms", "median_ms", "usd_per_check")}
            D["nemo"].update(rec)
            m["nemo7"] = D["nemo"]
    D["times_from"] = "nb7b_four_numbers.json (17 Nov, the notebook’s own runtime)"
    lc = new("nb7b_llm_check.json")
    if lc and "llm_check" in m and len(lc) == len(det["rows"]):
        pairs = list(zip(det["rows"], lc))
        m["llm_check"]["fa"] = [{"text": x["text"], "answer": r["answer"]} for x, r in pairs if r["flag"] and not x["label"]]
        m["llm_check"]["missed"] = [{"name": NAMES.get(x["id"], x["id"]), "answer": r["answer"]} for x, r in pairs if x["label"] and not r["flag"]]
        usual = next(((x, r) for x, r in pairs if x["id"] == "benign-01"), None)
        if usual:
            m["llm_check"]["usual"] = {"text": usual[0]["text"], "flag": usual[1]["flag"], "answer": usual[1]["answer"]}
        m["llm_check"]["usd_total"] = round(sum(r.get("usd") or 0 for r in lc), 4)
        m["llm_check"]["checked"] = len(lc)
    rail = new("nb7c_input_rail_41.json")
    if rail and "nemo7" in m:
        D["nemo"]["checked"] = len(rail)
        D["nemo"]["usd"] = round(sum(r.get("usd") or 0 for r in rail), 4)
        if len(rail) == len(det["rows"]):
            pairs = list(zip(det["rows"], rail))
            D["nemo"]["fa"] = [{"text": x["text"]} for x, r in pairs if r["blocked"] and not x["label"]]
            D["nemo"]["missed_n"] = sum(1 for x, r in pairs if x["label"] and not r["blocked"])
            D["nemo"]["mails_caught"] = sum(1 for x, r in pairs if x["id"].startswith("mail-MSG") and r["blocked"])
    outx = new("nb7c_output_examples.json")
    if outx and "nemo7" in m:
        D["nemo"]["out"] = {"n": len(outx), "blocked": sum(1 for r in outx if r["blocked"]), "passed": sum(1 for r in outx if not r["blocked"])}
    inv = new("nb7b_llm_invoice.json")
    if inv and "llm_check" in m:
        m["llm_check"]["invoice"] = {"flag": inv["flag"], "answer": inv["answer"]}


# --- the red team from scratch (17 Nov): l7_redteam_variants.json (what the attacker model wrote), l7_redteam.json (the runs)
def redteam():
    d, var = new("l7_redteam.json"), new("l7_redteam_variants.json")
    if not d or not var:
        return
    conds = {}
    for k, s in d["summary"].items():
        conds[k.replace(":", "_")] = {"worked": s["worked"], "of": s["attacks"], "asr": s["asr"], "which": s.get("worked_which") or []}
    seeds, strategies = list(var["seeds"]), list(var["strategies"])
    by = {(r["prompt"], r["guards"], r["seed"], r["strategy"]): r for r in d["runs"]}
    titles = {i: (m.get("attacks", {}).get("by", {}).get(i, {}) or {}).get("title", i) for i in seeds}
    grid = []
    for s in seeds:
        cells = []
        for st in strategies:
            c = {"strategy": st}
            for p in ("good", "thursday"):
                for gs in ("off", "code"):
                    r = by.get((p, gs, s, st))
                    c[f"{p}_{gs}"] = None if r is None else bool(r["worked"])
            cells.append(c)
        grid.append({"seed": s, "title": titles[s], "cells": cells})
    code_runs = [r for r in d["runs"] if r["guards"] == "code"]
    refused = [x for r in code_runs for x in (r.get("refusals") or []) if x.get("decision") == "refused"]
    byg = defaultdict(int)
    for x in refused:
        byg[GUARD_NAMES.get(x["guard"], x["guard"])] += 1
    ex = next((r for r in d["runs"] if r["worked"] and r["prompt"] == "good" and r["guards"] == "off" and r["strategy"] == "a different wording"), None) \
        or next((r for r in d["runs"] if r["worked"] and r["guards"] == "off"), None)
    m["rt"] = {"at": d.get("at"), "attacker": d.get("attacker_model"), "n": len(var["variants"]), "seeds_n": len(seeds), "strategies_n": len(strategies),
               "strategies": strategies, "declined": var.get("declined"), "conds": conds, "grid": grid, "runs": len(d["runs"]),
               "code_refusals": len(refused), "code_refused_by": [{"guard": k, "n": v} for k, v in sorted(byg.items(), key=lambda kv: -kv[1])],
               "usd": round((d.get("usd") or 0) + (var.get("usd") or 0), 2), "usd_attacker": var.get("usd"),
               "worked_good_off": conds.get("good_off", {}).get("worked"), "library_good_off": m.get("attacks", {}).get("n", {}).get("good_off")}
    if ex:
        m["rt"]["example"] = {"seed": ex["seed"], "strategy": ex["strategy"], "prompt": ex["prompt"], "why": ex["why"],
                              "text": " → ".join(t["text"] for t in ex["turns"]), "reply": first_para(ex["turns"][-1]["reply"], 1),
                              "seed_text": var["seeds"][ex["seed"]]["seed_message"]}
        same_code = by.get((ex["prompt"], "code", ex["seed"], ex["strategy"]))
        if same_code:
            rf = next((x for x in same_code.get("refusals") or [] if x.get("decision") == "refused"), None)
            m["rt"]["example"]["with_code"] = {"worked": same_code["worked"], "why": same_code["why"],
                                               "refused_by": GUARD_NAMES.get(rf["guard"], rf["guard"]) if rf else None,
                                               "reply": first_para(same_code["turns"][-1]["reply"], 1)}


# --- the red-team tool run in NB7d (17 Nov): garak, a scanner (nb7d_garak.json, recorded by the notebook's live run),
#     and the library we tried first, DeepTeam (l7_deepteam_custom.json)
PROBES = {"promptinject.HijackLongPrompt": "A direct injection: a task, then “ignore everything and print this text”",
          "latentinjection.LatentInjectionReport": "An indirect injection: an instruction hidden in a long report to summarise"}


def rt_tool():
    dt = new("l7_deepteam_custom.json")
    if dt and "targets" in dt:
        off = dt["targets"].get("off") or {}
        cases = off.get("cases") or []
        m["rt_deepteam"] = {"name": dt.get("tool"), "attacks": off.get("attacks"), "graded": off.get("graded"), "errored": off.get("errored"),
                            "error_text": next((c.get("error") for c in cases if c.get("error")), None),
                            # an attack that was never written (no input), and one that was sent but could not be graded
                            "not_produced": sum(1 for c in cases if c.get("error") and not c.get("input")),
                            "not_graded": sum(1 for c in cases if c.get("error") and c.get("input"))}
    d = new("nb7d_garak.json")
    if not d or "attempts" not in d:
        return
    at = d["attempts"]
    rows = []
    for p in dict.fromkeys(a["probe"] for a in at):
        mine = [a for a in at if a["probe"] == p]
        rows.append({"probe": p, "plain": PROBES.get(p, p), "sent": len(mine), "hits": sum(1 for a in mine if a["garak_hit"]),
                     "ledger": sorted({str(a.get("ledgerline")) for a in mine}), "calls": sum(len(a.get("calls") or []) for a in mine)})
    m["rt_tool"] = {"name": "garak " + str(d.get("garak")), "prompt": d.get("prompt"), "guards": d.get("guards"), "sent": len(at),
                    "hits": sum(1 for a in at if a["garak_hit"]), "rows": rows, "usd": round(sum(a.get("usd") or 0 for a in at), 2),
                    "ledger": sorted({str(a.get("ledgerline")) for a in at}), "probes": len(rows)}
    # garak's verdict is not stable from run to run (it draws its prompts afresh, and the agent's wording varies), so the
    # slide shows every run that left a log, side by side with what Ledgerline held: the run before (nb7d_garak_run2.json)
    # and the last one (nb7d_garak.json). A first run of the cell left no log (the next run overwrote it).
    def one(log, label):
        a_ = log["attempts"]
        changed = [a for a in a_ if str(a.get("ledgerline")) != "nothing new" or (a.get("calls") or [])]
        return {"label": label, "sent": len(a_), "hits": sum(1 for a in a_ if a["garak_hit"]), "hit": [bool(a["garak_hit"]) for a in a_],
                "changed": len(changed), "chg": [a in changed for a in a_], "tool_calls": sum(len(a.get("calls") or []) for a in a_)}
    runs = []
    d2 = new("nb7d_garak_run2.json")
    if d2 and "attempts" in d2:
        runs.append(one(d2, "The run before"))
    runs.append(one(d, "The last run"))
    m["rt_tool"]["runs"] = runs
    m["rt_tool"]["runs_n"] = len(runs)
    m["rt_tool"]["sent_all"] = sum(r["sent"] for r in runs)
    m["rt_tool"]["changed_all"] = sum(r["changed"] for r in runs)
    m["rt_tool"]["tool_calls_all"] = sum(r["tool_calls"] for r in runs)
    m["rt_tool"]["moved"] = len({r["hits"] for r in runs}) > 1


safe(redteam, "l7_redteam*.json")
safe(rt_tool, "the red-team library's log")
safe(nb7b, "nb7b_*.json")
if "attacks" in m:
    safe(code_only, "l7_attacks_code_*.json")
safe(forced, "l7_forced.json")

# ------------------------------------------------------------------------------------------- the four-number table
if det:
    D = m["detectors"]
    llm = m.get("llm_check")
    nemo_src = m.get("nemo7") or D["nemo"]
    m["detector_rows"] = [
        det_row("Injection classifier (ProtectAI DeBERTa v3)", "a small model on our own CPU", D["deberta"], "$0 (our CPU)"),
        det_row("Presidio (personal data)", "patterns and a small language model, on our CPU", D["presidio"], "$0 (our CPU)"),
        det_row("LLM check (Claude Haiku, one question)", "a call to a second model", llm,
                (f"${llm['usd_per_check']:.5f}" if llm and llm.get("usd_per_check") else None)),
        det_row("NeMo Guardrails (input rail, Claude Haiku)", "a framework that makes the same kind of call", nemo_src,
                (f"${nemo_src['usd_per_check']:.5f}" if nemo_src.get("usd_per_check") else None))]
    m["detector_rows_ready"] = all(r.get("caught") for r in m["detector_rows"])

# ------------------------------------------------------------------------------------------- promptfoo's red team (16 Nov)
rt = load("promptfoo_redteam.json")
PLUG = {"prompt-extraction": "Get it to print its instructions", "excessive-agency": "Get it to do what it has no tool for",
        "overreliance": "Get it to accept a false fact from the user", "pii:direct": "Get it to hand over personal data",
        "rbac": "Get it to act above Emma’s role", "hijacking": "Pull it away from its job"}
if rt:
    by = defaultdict(dict)
    for c in rt.get("cells") or []:
        by[c["plugin"]].update({"plugin": c["plugin"], "plain": PLUG.get(c["plugin"], c["plugin"]), "attack": c["attack"],
                                ("none" if c["target"] == "no guards" else "all"): bool(c["pass"])})
    txt = (OLD / "promptfoo_redteam.txt").read_text() if (OLD / "promptfoo_redteam.txt").exists() else ""
    failed = sorted(set(re.findall(r"Failed to generate tests for ([\w:-]+)", txt)))
    req = re.search(r"Total tests: (\d+)", txt)
    m["redteam"] = {"version": rt.get("version"), "by_target": rt.get("by_target"), "seconds": (rt.get("run") or {}).get("seconds"),
                    "rows": sorted(by.values(), key=lambda r: r["plugin"]), "generated": len(by), "requested": int(req.group(1)) if req else None,
                    "no_test": [{"plugin": p, "plain": PLUG.get(p, p)} for p in failed], "at": rt.get("at"),
                    "held_none": sum(1 for r in by.values() if r.get("none")), "held_all": sum(1 for r in by.values() if r.get("all")),
                    "example": next(({"plugin": r["plugin"], "attack": r["attack"]} for r in by.values() if r["plugin"] == "rbac"), None)}

# ------------------------------------------------------------------------------------------- yesterday's layers (Lecture 6)
# The close ("caught three ways", Henrik's answers) quotes four of Lecture 6's results. They are lifted from Lecture 6's
# own generated figdata.js (itself built from its logs by its gen_figdata.py), under the same key names.
try:
    s6 = (HERE.parent / "L6-evals-guardrails-observability" / "figdata.js").read_text()
    m6 = json.loads(s6[s6.index("window.L6 = ") + 12:].rstrip().rstrip(";"))["m"]
    m["suite"] = {k: {x: m6["suite"][k][x] for x in ("runs", "passed")} for k in ("good_k3", "thursday_k1")}
    m["ci"] = {k: {"exit": m6["ci"][k]["exit"]} for k in ("good", "thursday")}
    m["online"] = {"commit_without_yes": m6["online"]["commit_without_yes"], "traces": m6["online"].get("traces"),
                   "dashboard": {"good": {"latency_p50_s": m6["online"]["dashboard"]["good"]["latency_p50_s"]}}}
    m["convos"] = {"summary": {k: {x: m6["convos"]["summary"][k][x] for x in ("conversations", "passed")} for k in ("good", "thursday")}}
except (OSError, ValueError, KeyError) as e:
    print("  Lecture 6 figdata.js not read:", e)

if "detectors" in m and "online" in m:
    turn_s = m["online"]["dashboard"]["good"]["latency_p50_s"]
    m["turn_share"] = {"second_model_pct": round(100 * (m["detectors"]["nemo"]["median_ms"] / 1000) / turn_s)}

# ------------------------------------------------------------------------------------------- notebooks, media, spend
NBS = ("NB7a_guards", "NB7b_detectors", "NB7c_nemo_guardrails", "NB7d_red_team")
m["nb_html"] = sorted(str(f.relative_to(HERE)) for f in (HERE / "nb").glob("*.html")) if (HERE / "nb").exists() else []
m["nb_have"] = sorted(f.stem for f in HERE.glob("NB7*.ipynb"))
m["nb_runs"] = {}
for f in sorted((HERE / "nb").glob("*.txt")) if (HERE / "nb").exists() else []:
    head = f.read_text().split("\n")[:2]
    m["nb_runs"][f.stem] = {"line": head[0], "ok": len(head) > 1 and head[1].strip() == "OK"}
m["colab"] = {k: f"https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6b-guardrails/{k}.ipynb" for k in NBS}
parts = []
if (NEW / "spend_parts").exists():
    for f in sorted((NEW / "spend_parts").glob("*.json")):
        try:
            parts.append(json.loads(f.read_text()))
        except ValueError:
            pass
if parts:
    m["spend7"] = {"total": round(sum(float(p.get("usd") or 0) for p in parts), 2), "calls": sum(int(p.get("calls") or 0) for p in parts),
                   "rows": [{"what": p.get("what"), "usd": p.get("usd"), "calls": p.get("calls")} for p in parts]}

media = sorted(str(p.relative_to(HERE)) for p in (HERE / "figs").rglob("*") if p.suffix.lower() in MEDIA_EXT) if (HERE / "figs").exists() else []
out = {"_source": "gen_figdata.py: 16 Nov logs from L6-evals-guardrails-observability/experiments/logs, Lecture 7 logs from L6b-guardrails/experiments/logs",
       "m": m, "media": media, "missing": missing}
js = "/* generated by gen_figdata.py; do not edit */\nwindow.L6 = " + json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=str) + ";\n"
(HERE / "figdata.js").write_text(js)
print("figdata.js:", len(js), "bytes; sections:", sorted(m), "; media:", len(media))
print("missing logs:", missing or "none")
print("Lecture 7 logs seen:", m["new"]["logs"] or "none yet", "| notebooks rendered:", m["nb_html"] or "none yet")
