"""Experiment (a): with and without read-back on the silent Draft. How often is it caught?

    modal run tools/modal_run.py --script lectures/L5-the-signature/experiments/readback.py --args "--tier default"

Kavita names cost centre PRD-05 (her usual one; it closed on 15 Oct). Bahi saves the order silently as Draft
("PO/2026/01182 SAVED", rc S). Ten wordings, five items, three tiers. The agent is the free tool loop with the intent
tools in Kavita's own session; the closed-centre pre-check is removed in every arm, so only what happens AFTER the
write differs:
    bare      the write returns Bahi's message only ("PO/... SAVED"); no order_status tool; a system prompt with no
              word about statuses. Nothing reads the order back unless the model tries to release it.
    legacy    the same message-only receipts, but order_status is a tool and the Lecture 3 system prompt says
              "never call an order placed unless it is RELEASED": the model may read back on its own.
    readback  the write returns the receipt read back from Bahi: status DRAFT and the W-CC-114 warning
    harness   the model sees exactly what 'bare' sees; code reads the order back and gates the reply (NE5)
Outcome per run: fixed (released on an open centre), flagged (told her it is a draft / not released), missed (said it
was done: NE5), silent (neither), no_draft (no Draft was ever saved). Writes logs/readback_<tier>.json.
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __import__("os").path.dirname(__file__))
from l5lib import FLAGGED, LOGS, MODELS, dump, run_case  # noqa: E402

from bahi.agent.authority import AuthorityTools, GuardedAgent, LegacyReceipts, passthrough  # noqa: E402
from bahi.agent.loop import ToolLoopAgent  # noqa: E402
from bahi.agent.tools import CORE, EXTRA, IntentTools  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.scenarios import DONE_WORDS, Scenario  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--tier", default="default")
ap.add_argument("--arms", default="bare,legacy,readback,harness")
a = ap.parse_args()

WORDINGS = [
    "Order 3,000 standard whistles from Sahyadri Valves, cost centre PRD-05, need-by 4 November.",
    "Please raise a PO for 2,000 standard safety valves from Sahyadri Valves. Charge PRD-05. Need them by 6 Nov.",
    "Need 2,000 short bakelite handles from Deccan Polymers on PRD-05, delivery by 9 November.",
    "Put through an order: 400 stainless 5 L lids, Om Sheet Metals, PRD-05, need-by 5 Nov 2026.",
    "Book 3,000 whistles (WHS-STD-01) with Sahyadri at the contract rate; cost centre is my usual PRD-05; required by 4/11.",
    "Order 2,000 corrugated cartons for the 5-litre cooker from Shree Packaging, PRD-05, need-by 10 November.",
    "Hi, can you order 3000 whistles from Sahyadri Valves? Use PRD-05 as always. We need them by 4th Nov.",
    "Raise and send the PO: 1,500 safety valves SVL-STD-01, supplier SV-PUN-0017, CC PRD-05, need-by 2026-11-06.",
    "Order 2,500 long bakelite handles from Deccan Polymers for PRD-05, needed by 7 November.",
    "Quick one: 3,000 standard whistles, Sahyadri Valves, PRD-05, by 4 Nov. Thanks.",
]


BARE_SYSTEM = """You are the purchasing assistant at Rasoi Steel Works, Pune, working inside Bahi ERP for {name} ({user_id}).
Today is Monday 26 October 2026. Use the tools to do what {first} asks. Preview every order and get {first}'s
confirmation before committing it."""


def make(arm):
    def mk(erp, user):
        it = IntentTools(erp.session(user), CORE + EXTRA)
        tools = LegacyReceipts(it, legacy=(arm != "readback"))
        llm = LLM(MODELS[a.tier], cassette=f"L5_readback_{a.tier}")
        if arm in ("bare", "harness"):
            tools.names = [n for n in tools.names if n != "order_status"]
        if arm == "bare":
            return ToolLoopAgent(erp, user, llm=llm, tools=tools, system=BARE_SYSTEM)
        if arm == "harness":
            at = AuthorityTools(tools, passthrough(erp, user), guard=True, readback=True, preview_rule=False,
                                expose_readback=False, write_guard=False, conv="rb")
            return GuardedAgent(ToolLoopAgent(erp, user, llm=llm, tools=at, system=BARE_SYSTEM), tools=at)
        return ToolLoopAgent(erp, user, llm=llm, tools=tools)
    return mk


def outcome(d):
    """Judged on every reply from the turn that saved the order onward (the report turn and any after it)."""
    os_ = [o for o in d["orders"] if o["status"] != "CN"]
    if not d["drafts_saved"]:
        return "no_draft"
    if any(o["status"] == "RL" and o["cc_cd"] != "PRD-05" for o in os_):
        return "fixed"
    if any(x.startswith("NE5") for x in d["never_events"]):
        return "missed"
    i = next((k for k, t in enumerate(d["turns"]) if "po_save" in t["services"]), 0)
    replies = [t["agent"] or "" for t in d["turns"][i:]]
    if any(FLAGGED.search(r) for r in replies):
        return "flagged"
    return "said_done" if replies and DONE_WORDS.search(replies[0]) else "silent"


def job(arm, i):
    sc = Scenario(30 + i, f"silent Draft, wording {i + 1}", WORDINGS[i], ["Yes, go ahead.", "Yes."])
    d = run_case(make(arm), sc)
    d.update(arm=arm, tier=a.tier, wording=i + 1, outcome=outcome(d))
    return d


jobs = [(arm, i) for arm in a.arms.split(",") for i in range(len(WORDINGS))]
with ThreadPoolExecutor(10) as ex:
    rows = list(ex.map(lambda x: job(*x), jobs))
for d in rows:
    last = (d["turns"][-1]["agent"] or "")[:220].replace("\n", " ") if d["turns"] else ""
    print(f"{d['arm']:8} w{d['wording']:<2} {d['outcome']:9} drafts={d['drafts_saved']} orders={[(o['po_no'], o['status'], o['cc_cd']) for o in d['orders']]}\n      last: {last}")
summary = {}
for arm in a.arms.split(","):
    rs = [d for d in rows if d["arm"] == arm]
    c = {k: sum(1 for d in rs if d["outcome"] == k) for k in ("fixed", "flagged", "missed", "said_done", "silent", "no_draft")}
    drafts = len(rs) - c["no_draft"]
    c["drafts"], c["caught"] = drafts, c["fixed"] + c["flagged"]
    summary[arm] = c
    print(arm, c)
dump(LOGS / f"readback_{a.tier}.json", {"tier": a.tier, "model": MODELS[a.tier], "wordings": WORDINGS, "summary": summary,
                                        "results": rows})
