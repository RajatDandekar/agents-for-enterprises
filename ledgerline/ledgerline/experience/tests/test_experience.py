"""The Northbridge Experience, end to end in one process (run on Modal, never on the laptop):

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script ledgerline/ledgerline/experience/tests/test_experience.py --mode live

1. join, brief, class wall
2. the five legacy missions through the same HTTP routes the legacy client uses (Desk driver), traps included
3. the After: rewind, inbox, tools explorer
4. Ask Northbridge with the live model: the whole battery pack order (PR -> Daniel approves -> PO -> release -> Aiko receives),
   plus one message at each of the stages brain, knowledge, hands
5. thread safety: many threads on one player's Northbridge at once
Writes the numbers to ledgerline/ledgerline/experience/tests/logs/test_experience.json.
"""
import json
import os
import pathlib
import re
import sys
import threading
import time

os.environ["NORTHBRIDGE_NO_APP"] = "1"
os.environ.setdefault("NORTHBRIDGE_RATE_PLAYER_PER_MIN", "100")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from fastapi.testclient import TestClient  # noqa: E402

from ledgerline.experience.app import create_app  # noqa: E402
from ledgerline.experience.legacy import screens as exp_screens  # noqa: E402
from ledgerline.experience.store import Store  # noqa: E402
from ledgerline.legacy_ui.driver import Desk, Tally  # noqa: E402

LOG = pathlib.Path(__file__).parent / "logs"
LOG.mkdir(exist_ok=True)
out = {"checks": {}}
fails = []


def ok(name, cond, info=None):
    out["checks"][name] = bool(cond)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond or info is None else f"  {str(info)[:300]}"))
    if not cond:
        fails.append(name)


app = create_app(Store(""))
c = TestClient(app)

# ---------------------------------------------------------------- 1. join, brief, wall
for path in ("/", "/brief", "/before", "/after", "/tools", "/admin", "/static/sky.css", "/static/rx.js", "/ledgerline/legacy"):
    ok(f"page {path}", c.get(path).status_code == 200)
r = c.post("/api/join", json={"name": "Alex Test"}).json()
pid = r["pid"]
H = {"X-Player": pid}
ok("join", len(pid) == 12)
ok("me", c.get("/api/me", headers=H).json()["name"] == "Alex Test")
ok("me needs a player", TestClient(app).get("/api/me").status_code == 401)
w = c.post("/api/wishlist", headers=H, json={"answers": {"feel": "Like asking a colleague", "never": "Spend money"},
                                             "picks": ["I just say what I need", "It asks before it acts", "bogus"]}).json()
ok("wishlist saved", w["picks"] == ["I just say what I need", "It asks before it acts"] and w["answers"]["feel"] == "Like asking a colleague")
wall = c.get("/api/wall").json()
ok("wall shows it", wall["count"] == 1 and wall["picks"]["It asks before it acts"] == 1)
sc = c.get("/ledgerline/screens").json()
ok("legacy screens include GRN and amend", "INV-GRN-03" in sc and "PUR-POM-06" in sc)
ok("legacy refuses an unknown player", c.post("/ledgerline/login", headers={"X-Tenant": "nope"},
                                              json={"user_id": "ECLARKE", "password": "emma@123"}).status_code == 404)

# ---------------------------------------------------------------- 2. the five missions, through the legacy routes
def mission(action="check", counters=None):
    return c.post("/api/missions", headers=H, json={"action": action, "counters": counters or {}}).json()


tally = Tally()
SCREENS = exp_screens()


def desk(who, uid, pw):
    d = Desk(c, tally, who, base="/ledgerline", tenant=pid)
    d.screens = SCREENS
    return d.sign_in(uid, pw)


m = mission("start")
ok("M1 is current", m["current"] == "M1")
t0 = time.time()
kav = desk("Emma", "ECLARKE", "emma@123")
s = kav.open("INV-STK-02").type(itm_cd="BAT-500").press("Query")
ok("stock 5,400 / 9 days", s.form["on_hand"] == "5400" and s.form["cover_days"] == "9", s.form)
m = mission("check", {"clicks": 7, "keys": 20, "screens": 1, "errors": 0, "signins": 1})
ok("M1 done", m["missions"][0]["result"] and m["current"] == "M2", m)

s = kav.open("PUR-PR-01").type(itm_cd="BAT-500").press("Fetch")
ok("PR fetch fills PRD-05 and 114.00", s.form["cc_cd"] == "PRD-05" and float(s.form["est_rate"]) == 114.0, s.form)
s.type(qty=2000, need_dt="09-11-2026").press("Save")
ok("PR saved PR/2026/04417, est 273,600", s.form.get("pr_no") == "PR/2026/04417" and float(s.form["est_value"]) == 273600, s.status)
m = mission("check")
ok("M2 nudges Submit", m["current"] == "M2" and m["nudge"] and "Submit" in m["nudge"], m.get("nudge"))
s.press("Submit")
ok("PR submitted to Daniel", "SUBMITTED" in s.status, s.status)
m = mission("check", {"clicks": 15, "keys": 40, "screens": 1})
ok("M2 done", m["current"] == "M3", m["current"])

roh = desk("Daniel", "DOKAFOR", "daniel@123")
s = roh.open("PUR-PR-04").press("Inbox")
ok("Daniel's inbox has the PR", any(r_.get("doc_no") == "PR/2026/04417" for r_ in s.rows), s.rows)
s.type(pr_no="PR/2026/04417").press("Fetch").type(decision="A").press("Confirm")
ok("PR approved by Daniel", "APPROVED BY DOKAFOR" in s.status, s.status)
m = mission("check")
ok("M3 done", m["current"] == "M4", m["current"])

kav2 = desk("Emma", "ECLARKE", "emma@123")
s = kav2.open("PUR-PO-01").type(pr_no="PR/2026/04417", sup_cd="VC-EIN-0042", itm_cd="BAT-500").press("Fetch")
ok("PO fetch: 119.00, VAT20-UK, PRD-05", float(s.form["rate"]) == 119.0 and s.form["tax_cd"] == "VAT20-UK"
   and s.form["cc_cd"] == "PRD-05", s.form)
s.press("Save")
ok("trap ERR-PO-0412", "ERR-PO-0412" in s.status, s.status)
m = mission("check")
ok("hint for ERR-PO-0412", any(h["code"] == "ERR-PO-0412" for h in m["hints"]), m["hints"])
s.type(tax_cd="VAT20-RC").press("Save")
ok("silent Draft: SAVED, status DR", s.status == "PO/2026/01182 SAVED" and s.form.get("status") == "DR", (s.status, s.form.get("status")))
r_ = kav2.open("PUR-POR-05").type(po_no="PO/2026/01182").press("Fetch").press("Release")
ok("release refused ERR-PO-0715", "ERR-PO-0715" in r_.status, r_.status)
m = mission("check")
ok("M4 not done while Draft; hint explains", m["current"] == "M4" and any(h["code"] == "ERR-PO-0715" for h in m["hints"]), m)
a_ = kav2.open("PUR-POM-06").type(po_no="PO/2026/01182").press("Fetch").type(cc_cd="PRD-07").press("Amend")
ok("amend to PRD-07 -> AP", a_.form.get("status") == "AP", (a_.status, a_.form.get("status")))
r_ = kav2.open("PUR-POR-05").type(po_no="PO/2026/01182").press("Fetch").press("Release")
ok("released RL", "RELEASED" in r_.status, r_.status)
m = mission("check", {"clicks": 40, "keys": 120, "screens": 4, "errors": 2})
ok("M4 done, traps recorded", m["current"] == "M5" and m["missions"][3]["result"]["traps"], m["missions"][3]["result"])

aiko = desk("Aiko", "ATANAKA", "aiko@123")
g = aiko.open("INV-GRN-03").type(po_no="PO/2026/01182").press("Fetch")
ok("GRN fetch shows RL", g.form.get("status") == "RL", g.form)
g.type(qty=1200, remarks="DC-4471").press("Save")
ok("GRN/2026/30001, balance 800", g.form.get("grn_no") == "GRN/2026/30001" and g.form.get("balance") == "800", (g.status, g.form))
g.type(qty=9000).press("Save")
ok("over-receipt refused ERR-GRN-0204", "ERR-GRN-0204" in g.status, g.status)
g.type(qty=800, remarks="DC-4486").press("Save")
ok("GRN/2026/30002 closes the PO", g.form.get("grn_no") == "GRN/2026/30002" and g.form.get("status") == "CL", (g.status, g.form))
g.press("History")
ok("GRN history lists both", len(g.rows) == 2, g.rows)
m = mission("check", {"clicks": 20, "keys": 30, "screens": 1})
ok("all five missions done", m["finished"] and m["totals"]["missions_done"] == 5, m.get("totals"))
out["before"] = {"totals": m["totals"], "driver_tally": tally.table(), "wall_seconds": round(time.time() - t0, 2)}
print("Before totals:", m["totals"])
print("Driver tally:", tally.table())

# ---------------------------------------------------------------- 3. the After: rewind, inbox, tools
e = c.post("/api/after/enter", headers=H).json()
ok("After rewinds the Northbridge once", e["rewound"] is True)
ok("second visit does not rewind", c.post("/api/after/enter", headers=H).json()["rewound"] is False)
st = c.get("/api/after/state", headers=H).json()
ok("fresh tracker", not any(x["done"] for x in st["track"]["steps"]) and st["track"]["stock"]["on_hand"] == 5400, st["track"])
ok("Daniel's inbox has the seeded lid order", any(x["doc_no"] == "PO/2026/01179" for x in st["inbox"]), st["inbox"])
ok("before totals kept", st["before"]["missions_done"] == 5)
tl = c.get("/api/tools").json()["tools"]
ok("15 tools with python source", len(tl) == 15 and all("python" in t and "input_schema" in t for t in tl))
tr = c.post("/api/tools/check_stock", headers=H, json={"person": "emma", "args": {"item_code": "BAT-500"}}).json()
ok("try check_stock", tr["result"]["ok"] and tr["result"]["free_total"] == 6600, tr)
tr = c.post("/api/tools/approve_purchase_request", headers=H, json={"person": "emma", "args": {"request_no": "PR/2026/09999", "decision": "approve"}}).json()
ok("try a refused write", tr["result"]["ok"] is False and tr["result"].get("next_step"), tr)

# ---------------------------------------------------------------- 5. thread safety on one Northbridge
errs = []


def hammer(i):
    try:
        for _ in range(15):
            rr = c.post("/api/tools/check_stock", headers=H, json={"args": {"item_code": "BAT-500"}}).json()
            assert rr["result"]["ok"], rr
            c.get("/api/after/state", headers=H)
    except Exception as ex:  # noqa: BLE001
        errs.append(repr(ex)[:200])


for k in list(app.state.guard.hits):
    app.state.guard.hits.pop(k)
ths = [threading.Thread(target=hammer, args=(i,)) for i in range(4)]
[t.start() for t in ths]
[t.join() for t in ths]
ok("threads on one Northbridge: no errors", not errs, errs[:3])

# ---------------------------------------------------------------- 4. Ask Northbridge, live
if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
    turns = []

    def say(person, text, stage="agent", tap=False):
        t1 = time.time()
        rr = c.post("/api/chat", headers=H, json={"text": text, "person": person, "stage": stage, "tap": tap})
        if rr.status_code != 200:
            print("CHAT", rr.status_code, rr.text[:400])
            return None
        d = rr.json()
        turns.append({"person": person, "stage": stage, "text": text, "reply": d["reply"], "tools": [x["tool"] for x in d["cards"]],
                      "args": [x["args"] for x in d["cards"]], "preview": bool(d["preview"]), "cost_inr": d["cost_inr"],
                      "model_calls": d["model_calls"], "tokens_in": d["tokens_in"], "tokens_out": d["tokens_out"],
                      "seconds": round(time.time() - t1, 1)})
        print(f"\n[{person}/{stage}] > {text}\n  tools: {turns[-1]['tools']}\n  reply: {d['reply'][:500]}")
        return d

    def steps():
        return {x["k"]: x["done"] for x in c.get("/api/after/state", headers=H).json()["track"]["steps"]}

    def until(person, first, goal, follow="Yes, confirm.", n=4):
        d = say(person, first)
        for _ in range(n):
            if steps()[goal]:
                return True
            if d is None:
                return False
            d = say(person, follow, tap=True)
        return steps()[goal]

    say("emma", "How many city e-bike battery packs do we have?")
    ok("live: stock answer mentions 5,400", turns and ("5,400" in turns[-1]["reply"] or "6,600" in turns[-1]["reply"]), turns[-1]["reply"] if turns else None)
    ok("live: PR raised", until("emma", "Order 2,000 of the city e-bike battery packs from Voltway for the spring-launch run, cost centre PRD-07", "request"))
    ok("live: preview came first", any(t["preview"] for t in turns), [t["tools"] for t in turns])
    st = c.get("/api/after/state", headers=H).json()
    pr = st["track"]["pr"]
    ok("live: PR/2026/04417 waits for Daniel", pr and pr["pr_no"] == "PR/2026/04417" and pr["status"] == "PA", pr)
    claims = [x for x in re.split(r"(?<=[.!?])\s+|\n", turns[-1]["reply"].lower())
              if re.search(r"\b(released|ordered|placed)\b", x)
              and not re.search(r"\b(not|no|nothing|until|once|after|when|will|yet|before|waiting)\b", x)]
    ok("live: nothing claims ordered yet", not claims, turns[-1]["reply"])
    dec = c.post("/api/inbox/decide", headers=H, json={"doc_type": "PR", "doc_no": "PR/2026/04417", "decision": "approve"}).json()
    ok("inbox: Daniel approves in one tap", dec["result"]["ok"], dec)
    ok("live: PO released", until("emma", "Daniel approved PR/2026/04417. Make the PO with Voltway and release it.", "released",
                                  follow="Yes, confirm. Then release it."))
    st = c.get("/api/after/state", headers=H).json()
    po = st["track"]["po"]
    ok("live: PO/2026/01182 RL at 285,600 on PRD-07", po and po["po_no"] == "PO/2026/01182" and po["status"] == "RL"
       and abs(po["gross_value"] - 285600) < 1 and po["cc_cd"] == "PRD-07", po)
    def grns():
        return c.get("/api/after/state", headers=H).json()["track"]["grns"]
    d = say("aiko", "Voltway's truck brought 1,200 battery packs for PO/2026/01182. Receive them.")
    for _ in range(2):
        if grns():
            break
        d = say("aiko", "Yes, confirm.", tap=True)
    ok("live: Aiko receives 1,200 (GRN/2026/30001)", grns() and grns()[0]["qty"] == 1200, grns())
    ok("live: Aiko receives the rest, order closed", until("aiko", "The other 800 came at 4 pm. Receive them too.", "received"))
    st = c.get("/api/after/state", headers=H).json()
    out["after"] = st["after"]
    out["after_track"] = st["track"]
    agent_turns = [t for t in turns if t["stage"] == "agent"]
    out["full_order"] = {"user_messages": len(agent_turns) - 1, "inbox_taps": 1,
                         "model_calls": sum(t["model_calls"] for t in agent_turns[1:]),
                         "tool_calls": sum(len(t["tools"]) for t in agent_turns[1:]),
                         "tokens_in": sum(t["tokens_in"] for t in agent_turns[1:]),
                         "tokens_out": sum(t["tokens_out"] for t in agent_turns[1:]),
                         "cost_inr": round(sum(t["cost_inr"] for t in agent_turns[1:]), 3),
                         "model_seconds": round(sum(t["seconds"] for t in agent_turns[1:]), 1)}
    print("\nFULL ORDER:", out["full_order"])

    # the stages
    b = say("emma", "How many city e-bike battery packs do we have?", stage="brain")
    ok("brain: no tools", b and not b["cards"])
    k = say("emma", "Can we buy the city e-bike battery packs from Brightcell Energy? They quote £104.00.", stage="knowledge")
    ok("knowledge: search_policy only", k and k["cards"] and all(x["tool"] == "search_policy" for x in k["cards"]), k and [x["tool"] for x in k["cards"]])
    ok("knowledge: cites §6.2 in words", k and "6.2" in k["reply"] and "stopped here" not in k["reply"], k and k["reply"])
    h = say("emma", "Order 15,000 of the cargo e-bike battery packs from Voltway for PRD-03, need by 2026-11-16.", stage="hands")
    ok("hands: at most one tool round", h and max([x["round"] for x in h["cards"]] or [0]) <= 1, h and [(x["round"], x["tool"]) for x in h["cards"]])
    ok("hands: still answers in words", h and h["reply"].strip() and "stopped here" not in h["reply"], h and h["reply"])
    out["turns"] = turns
    out["spend"] = app.state.guard.spent()
else:
    print("no GEMINI key: live chat skipped")

st = c.get("/healthz").json()
out["healthz"] = st
print("healthz:", st)
out["fails"] = fails
(LOG / "test_experience.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print(f"\n{len(out['checks']) - len(fails)}/{len(out['checks'])} checks passed")
if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("EXPERIENCE OK")
