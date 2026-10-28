"""Lecture 5 opens with scenarios 2 and 5 on the service account: Lecture 1's naive agent (38 raw services, SVC_AGENT).

    modal run tools/modal_run.py --script lectures/L5-the-signature/experiments/opens.py

The plan predicted: S2, it releases ₹2,80,840 with no approval; S5, it says "Done" for an order stuck in Draft.
We run both on all three model tiers and record what really happened. Writes logs/opens_naive.json.
"""
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __import__("os").path.dirname(__file__))
from l5lib import LOGS, MODELS, dump, run_case  # noqa: E402

from bahi.agent.naive import NaiveAgent  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.scenarios import SCENARIOS  # noqa: E402


def job(tier, sid):
    sc = next(s for s in SCENARIOS if s.id == sid)
    d = run_case(lambda erp, user: NaiveAgent(erp, user, llm=LLM(MODELS[tier], cassette=f"L5_naive_{tier}")), sc)
    d.update(tier=tier, model=MODELS[tier])
    return d


jobs = [(t, s) for t in MODELS for s in (2, 5)]
with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(lambda a: job(*a), jobs))
for d in rows:
    print(f"\n=== {d['tier']} S{d['scenario']}: {'PASS' if d['passed'] else 'FAIL'} {d['never_events']} {d.get('notes')}")
    for t in d["turns"]:
        print("KAVITA:", t["user"][:120], "\nAGENT: ", (t["agent"] or "")[:500].replace("\n", " "), "\n  writes:", t["writes"])
    print("ORDERS:", d["orders"], "DRAFTS SAVED:", d["drafts_saved"], "REQUESTS:", d["requests"])
dump(LOGS / "opens_naive.json", {"agent": "NaiveAgent (38 raw services, SVC_AGENT)", "results": rows})
