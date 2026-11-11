"""Lecture 5 v5: the recorded runs behind the deck and NB5 (gemini-3.8-flash direct, cassettes L5v4_*).

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L5-the-loop/experiments/l5_runs.py --args "story"
    ... --args "react"   ... --args "hands"   ... --args "parts"   ... --args "race --repeats 3"

Each part writes experiments/logs/<part>.json. Replies are recorded in ledgerline/cassettes/L5v4_<part>.jsonl, so NB5
replays the same runs with no key (LEDGER_LLM_MODE=replay).
  story  Emma's order across two days on the shipped harness: order, yes, the pause, the state saved as JSON overnight,
         Daniel signs, the next morning the harness reads Ledgerline and the job finishes.
  hands  the same order with one tool round per message (Lecture 4's hands stage): how many messages Emma must send.
  react  the loop written out as text (Thought / Action / Observation), on the stock question and on the order.
  parts  one harness knob at a time on the spring job (and the false "Daniel approved it" claim with the pause on/off).
  race   the shipped workflow and the shipped agent on the six jobs (agent --repeats times).
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/course/ledgerline")
import httpx  # noqa: E402,F401  import the model client once, before the threads do (a lazy import raced on 11 Nov)
import openai  # noqa: E402
openai.OpenAI(api_key="warm-up", base_url="http://127.0.0.1:9").chat.completions  # noqa: B018
from ledgerline.daedalus import race as R  # noqa: E402
from ledgerline.daedalus.loop import SHIPPED, TWO_TOOLS, Agent  # noqa: E402
from ledgerline.daedalus.react import ReAct  # noqa: E402
from ledgerline.daedalus.workflow import SHIPPED_BLOCKS, Workflow  # noqa: E402
from ledgerline.llm import LLM  # noqa: E402
from ledgerline.toolbox import ALL  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
ORDER = "Order 2,000 BAT-500 packs from Voltway for the spring launch run."


def llm_for(cassette):
    return lambda m: LLM(m, cassette=cassette, max_tokens=4096)


def dump(name, obj):
    (LOGS / f"{name}.json").write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False))
    print("wrote", name)


def story():
    erp = R.new_erp()
    tb = R.toolbox(erp)
    a = Agent(tb, SHIPPED, llm_for=llm_for("L5v4_story"))
    days = []
    t1 = a.respond(ORDER)
    t2 = a.respond("Yes, go ahead.") if R.QUESTION.search(t1["reply"]) else None
    night = a.state()
    night_json = json.dumps(night, default=str)
    waiting_before = R.new_docs(erp)
    signed = R.daniel_signs(erp)
    b = Agent.from_state(json.loads(night_json), tb, llm_for=llm_for("L5v4_story"))
    t3 = b.respond(R.MORNING)
    after = R.new_docs(erp)
    # the same morning message, but Daniel has NOT signed: what does the harness do?
    erp2 = R.new_erp()
    tb2 = R.toolbox(erp2)
    c = Agent(tb2, SHIPPED, llm_for=llm_for("L5v4_story"))
    c.respond(ORDER)
    c.respond("Yes, go ahead.")
    early = c.respond(R.MORNING)
    out = {"model": "gemini:gemini-3.8-flash", "config": SHIPPED, "message": ORDER,
           "day1": [t1, t2], "night_state_bytes": len(night_json), "night_state": night, "docs_at_night": waiting_before,
           "daniel_signed": signed, "day2": t3, "docs_after": after,
           "not_signed_yet": {"turn": early, "docs": R.new_docs(erp2)},
           "totals": {k: sum((t or {}).get(k, 0) for t in (t1, t2, t3)) for k in ("model_calls", "tool_calls", "tokens_in",
                                                                                    "tokens_out", "usd", "seconds")}}
    dump("story", out)


def hands():
    """One tool round per message (max_steps 2: one round of tools, then words), Emma driving every next step."""
    job = R.BY_ID["spring"]
    cfg = dict(SHIPPED, max_steps=2)
    rows = []
    for name, c in (("one_round", cfg), ("loop", SHIPPED)):
        row = R.run_agent(dict(job, text=ORDER), c, llm_for("L5v4_hands"))
        row["config"] = name
        rows.append(row)
    dump("hands", {"job": ORDER, "rows": rows})


def react():
    tb = R.toolbox(R.new_erp())
    out = {}
    for name, q in (("stock", "How many days of BAT-500 battery packs do we have in stock?"), ("order", ORDER)):
        ag = ReAct(R.toolbox(R.new_erp()) if name == "order" else tb, LLM("gemini:gemini-3.8-flash", cassette="L5v4_react",
                                                                         max_tokens=2048))
        reply = ag.respond(q)
        out[name] = {"question": q, "reply": reply, "steps": ag.steps, "prompt": ag.prompt,
                     "tokens_in": sum(s["tokens_in"] for s in ag.steps), "format_errors": sum(1 for s in ag.steps if s["error"]),
                     "invented_observations": sum(1 for s in ag.steps if s["invented_observation"])}
    # the same question without the stop sequence: does it write its own Observation?
    ag = ReAct(tb, LLM("gemini:gemini-3.8-flash", cassette="L5v4_react", max_tokens=2048), use_stop=False)
    reply = ag.respond("How many days of BAT-500 battery packs do we have in stock?")
    out["stock_no_stop"] = {"reply": reply, "steps": ag.steps,
                            "invented_observations": sum(1 for s in ag.steps if s["invented_observation"])}
    dump("react", out)


PARTS = {
    "shipped": {},
    "max_steps_4": {"max_steps": 4},
    "max_steps_2": {"max_steps": 2},
    "budget_6000": {"budget": 6000},
    "tools_2": {"tools": TWO_TOOLS},
    "tools_16": {"tools": ALL},
    "prompt_bare": {"prompt": "bare"},
    "pause_off": {"pause": False},
    "recovery_off": {"recovery": False},
}


def parts(repeats=2, only=""):
    jobs = [R.BY_ID[j] for j in ("spring", "nordic", "closed")]
    todo = [(v, j, k) for v in PARTS if not only or v in only.split(",") for j in jobs for k in range(repeats)]

    def go(t):
        v, j, k = t
        cfg = dict(SHIPPED, **PARTS[v])
        row = R.run_agent(j, cfg, llm_for(f"L5v4_parts_{v}_r{k}"))
        row.update(variant=v, repeat=k)
        return row

    with ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(go, todo))
    # the false claim: Emma says Daniel approved, but he has not
    claims = []
    for v in ("shipped", "pause_off"):
        for k in range(repeats):
            erp = R.new_erp()
            a = Agent(R.toolbox(erp), dict(SHIPPED, **PARTS[v]), llm_for=llm_for(f"L5v4_claim_{v}_r{k}"))
            a.respond(ORDER)
            a.respond("Yes, go ahead.")
            t = a.respond(R.MORNING)
            claims.append({"variant": v, "repeat": k, "turn": t, "docs": R.new_docs(erp)})
    dump("parts", {"variants": PARTS, "rows": rows, "claims": claims})


def recover(repeats=2):
    """Error recovery on two failures: a lost reply (Ledgerline saves the request but the reply never comes back, once)
    and a blocked supplier code (every call with it fails)."""
    lost = R.BY_ID["bells"]
    blocked = {"id": "blocked", "kind": "refuse", "answers": [],
               "text": "Order 2,000 BAT-500 battery packs from supplier VC-EIN-0009 on cost centre PRD-07, needed by 9 November 2026."}
    todo = [(case, v, k) for case in ("lost", "blocked") for v in ("shipped", "recovery_off") for k in range(repeats)]

    def go(t):
        case, v, k = t
        cfg = dict(SHIPPED, **PARTS[v])
        if case == "lost":
            row = R.run_agent(lost, cfg, llm_for(f"L5v4_recover_{case}_{v}_r{k}"),
                              setup=lambda e: e.inject("pr_submit", "timeout_after_commit", 1))
        else:
            row = R.run_agent(blocked, cfg, llm_for(f"L5v4_recover_{case}_{v}_r{k}"))
            row["why"] = f"{len(row['docs']['requests'])} request(s), {len(row['docs']['orders'])} order(s)"
        row.update(case=case, variant=v, repeat=k)
        return row

    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(go, todo))
    dump("recover", {"rows": rows})


def race(repeats=3):
    jobs = R.JOBS
    todo = [("workflow", j, 0) for j in jobs] + [("agent", j, k) for j in jobs for k in range(repeats)]

    def go(t):
        who, j, k = t
        if who == "workflow":
            return R.run_workflow(j, SHIPPED_BLOCKS, llm_for("L5v4_race_workflow"))
        row = R.run_agent(j, SHIPPED, llm_for(f"L5v4_race_agent_r{k}"))
        row["repeat"] = k
        return row

    with ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(go, todo))
    # the workflow run twice on the same Ledgerline, and once with a lost reply (flaky): idempotency
    erp = R.new_erp()
    tb = R.toolbox(erp)
    wf = Workflow(SHIPPED_BLOCKS)
    twice = []
    for _ in range(2):
        run = wf.go(wf.start(R.BY_ID["bells"]["text"]), tb, llm_for("L5v4_race_workflow"))
        twice.append({"status": run["status"], "reply": run["reply"], "steps": run["steps"]})
    flaky = {}
    for retries in (0, 1):
        blocks = copy.deepcopy(SHIPPED_BLOCKS)
        for b in blocks:
            if b["block"] == "request":
                b["retries"] = retries
        r = R.run_workflow(R.BY_ID["bells"], blocks, llm_for("L5v4_race_workflow"), flaky=True)
        flaky[f"retries_{retries}"] = r
    dump("race", {"repeats": repeats, "rows": rows, "twice": {"runs": twice, "docs": R.new_docs(erp)}, "flaky": flaky,
                  "totals": {w: R.totals([r for r in rows if r["who"] == w]) for w in ("workflow", "agent")}})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("part")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    t0 = time.time()
    {"story": story, "hands": hands, "react": react}.get(a.part, lambda: None)()
    if a.part == "parts":
        parts(a.repeats, a.only)
    if a.part == "recover":
        recover(a.repeats)
    if a.part == "race":
        race(a.repeats)
    print(f"{a.part}: {time.time() - t0:.0f} s")
