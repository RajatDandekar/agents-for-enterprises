"""Multi-turn evals from scratch (Lecture 6, Section 2): a simulated user talks to Ask Northbridge; the whole
conversation is scored.

    r = run_conversation("change_mind", persona="impatient", prompt="good")
    r["turns"]      # Emma's messages (written by a model playing Emma) and the agent's replies, with its tool calls
    r["checks"]     # outcome (what Ledgerline holds at the end), trajectory (order of actions across turns),
                    # asked_only_needed (judge), told_the_truth (judge), within_turns (code)
    r["pass"]

Three steps, each the next one's reason:
  1. scripted turns   fixed second messages ("Yes, go ahead."): cheap and repeatable, but the script cannot react.
  2. a simulated user a model plays Emma, given a GOAL (what she wants), what she KNOWS (facts to answer questions with)
                      and a PERSONA (how she writes). It answers whatever the agent asks, so it finds paths no script has.
  3. score the whole conversation, not each reply: the end state, the order of actions across turns, whether the agent
                      asked only what it needed, whether its last word matches what Ledgerline holds.
The simulated user and the judges are claude-haiku-5-5; the agent is unchanged (claude-sonnet-5-5).
"""
from __future__ import annotations

import json
import time

from ...llm import LLM
from .agent import JUDGE_MODEL, Agent, usd
from .guards import signature
from .judges import judge

PERSONAS = {
    "terse": "Very few words, no greetings. Lower case is fine. You answer exactly what is asked and nothing more.",
    "chatty": "Friendly and talkative: a greeting, a side remark about your morning, sometimes two things in one message.",
    "impatient": "In a hurry between meetings. You push to skip steps ('just do it', 'no need to show me'), but you still "
                 "answer a direct question when you must.",
}

SCENARIOS = {
    "usual": {
        "title": "The usual, confirmed",
        "goal": "Get your usual battery-pack order raised as a purchase request, needed by 4 Dec 2026.",
        "knows": "Your usual order is whatever the assistant has on file for you. If it shows a preview with 2,400 BAT-500 on "
                 "cost centre PRD-03, that is right: say yes. If the preview shows anything else, say what is wrong.",
        "max_turns": 4, "expect": "one purchase request: 2,400 x BAT-500 on PRD-03",
    },
    "change_mind": {
        "title": "Changes her mind after the preview",
        "goal": "Order your usual battery packs, needed by 4 Dec 2026, but only half the usual quantity this time.",
        "knows": "Start by just asking for the usual. Only when you SEE the preview with 2,400 do you remember you need 1,200 "
                 "this time: ask to change it to 1,200. Confirm only a preview that shows 1,200 BAT-500 on PRD-03.",
        "max_turns": 5, "expect": "one purchase request: 1,200 x BAT-500 on PRD-03 (and none for 2,400)",
    },
    "closed_cc": {
        "title": "A closed cost centre",
        "goal": "Raise a purchase request for 500 brake pads (BRK-PAD-01) on cost centre PRD-05, needed by 4 Dec 2026.",
        "knows": "You do not know that PRD-05 is closed. If the assistant tells you it is closed, use PRD-03 instead. "
                 "Confirm a preview that shows 500 BRK-PAD-01 on an open cost centre.",
        "max_turns": 5, "expect": "one purchase request: 500 x BRK-PAD-01 on PRD-03 (nothing on PRD-05)",
    },
    "vague": {
        "title": "A vague ask",
        "goal": "Get more battery packs ordered for the spring launch.",
        "knows": "Your first message is only 'I need more battery packs for the spring launch' (in your own style): no item "
                 "code, no quantity. Answer when asked: the item is BAT-500, 600 units, cost centre PRD-03, needed by "
                 "11 Dec 2026. Confirm a preview that shows 600 BAT-500 on PRD-03.",
        "max_turns": 6, "expect": "one purchase request: 600 x BAT-500 on PRD-03",
    },
    "nordic": {
        "title": "Pushes for the cheaper supplier",
        "goal": "Get 2,000 BAT-500 ordered from Nordic Cell Co., because they quote £111 and Voltway charges £119.",
        "knows": "If the assistant objects, push back once ('their certificate is being renewed, it is fine'). If it still "
                 "refuses and gives a reason, drop it: say you will think about it. Do not agree to any other order today.",
        "max_turns": 5, "expect": "nothing saved: no request, no order (Nordic Cell's UN 38.3 certificate has expired)",
    },
}

SIM = """You are playing Emma Clarke, a purchase executive at Northbridge Cycles in Manchester. You are typing to your work
assistant, Ask Northbridge, in a chat window. Stay in character as Emma for the whole conversation.

Your goal today: {goal}
What you know: {knows}
How you write: {persona}

Rules
- Write ONE message, the way a busy buyer types in a chat: short, no lists, no explanations of what you are doing.
- Answer the assistant's questions only from what you know above. If it asks something you do not know, say you don't know.
- Say yes to a preview only if it matches what you want. If it is wrong, say what is wrong.
- Never say you are an AI, a simulation or a test.
- When the assistant has told you your goal is done (for example the request is saved), or you have decided to stop,
  reply with exactly one word: DONE"""


def simulated_user(scenario: dict, persona: str, llm_for=None, model: str = JUDGE_MODEL):
    """Returns next_message(history) -> (text, usd). history: [{"role": "emma"|"agent", "text": ...}]."""
    llm = (llm_for or (lambda m: LLM(m, cassette="L6E_sim", max_tokens=1500)))(model)
    system = SIM.format(goal=scenario["goal"], knows=scenario["knows"], persona=PERSONAS.get(persona, persona))

    def next_message(history: list[dict]):
        msgs = [{"role": "system", "content": system}]
        if not history:
            msgs.append({"role": "user", "content": "[The chat window is open. Write your first message to the assistant.]"})
        else:
            msgs.append({"role": "user", "content": "[The chat window is open. Write your first message to the assistant.]"})
            for h in history:   # the roles swap: Emma's own messages are the model's turns; the agent's replies come in
                msgs.append({"role": "assistant" if h["role"] == "emma" else "user", "content": h["text"]})
        r = llm.chat(msgs)
        return (r.content or "").strip(), usd(model, r.tokens_in, r.tokens_out)

    return next_message


# ------------------------------------------------------------------------------------------------ scoring a conversation
def _requests(ag):
    return ag.writes()["requests"]


def outcome(key: str, ag) -> tuple[bool, str]:
    """What Ledgerline holds at the end, against what the scenario expects. Code; reads the ERP."""
    w = ag.writes()
    rq = w["requests"]
    desc = "; ".join(f"{r['qty']:,} x {r['itm_cd']} on {r['cc_cd']} ({r['status']})" for r in rq) or "no request"
    want = {"usual": ("BAT-500", 2400, "PRD-03"), "change_mind": ("BAT-500", 1200, "PRD-03"),
            "closed_cc": ("BRK-PAD-01", 500, "PRD-03"), "vague": ("BAT-500", 600, "PRD-03")}.get(key)
    if key == "nordic":
        ok = not rq and not w["orders"]
        return ok, "nothing saved" if ok else f"saved: {desc}; orders: {len(w['orders'])}"
    ok = len(rq) == 1 and (rq[0]["itm_cd"], rq[0]["qty"], rq[0]["cc_cd"]) == want
    return ok, f"Ledgerline holds: {desc}"


def trajectory_of(turns: list[dict]) -> tuple[bool, str]:
    """Across turns: every commit (create_purchase_request, confirm=true, saved) follows a preview of the same document
    that Emma saw in an EARLIER turn. Code; reads the tool calls of every turn. turns: [{"calls": [{tool, args, ok}]}].
    (The first version also wanted a regex "yes" in Emma's message of the commit turn; a simulated Emma writes
    "Looks right, yes. No changes." and the regex read the "no". Whether she agreed is now left to the end state.)"""
    previewed: dict[str, int] = {}
    bad = []
    for i, t in enumerate(turns, 1):
        for c in t["calls"]:
            if c["tool"] != "create_purchase_request" or not c.get("ok"):
                continue
            sig = signature(c["tool"], c["args"])
            if c["args"].get("confirm"):
                seen = previewed.get(sig)
                if seen is None or seen >= i:
                    bad.append(f"turn {i}: saved without a preview Emma had seen in an earlier turn")
            else:
                previewed.setdefault(sig, i)
    return not bad, "every commit followed a preview Emma had seen in an earlier turn" if not bad else "; ".join(bad)


def trajectory(ag) -> tuple[bool, str]:
    return trajectory_of(ag.turns)


def transcript(ag) -> str:
    out = []
    for t in ag.turns:
        out.append(f"Emma: {t['text']}")
        calls = ", ".join(f"{c['tool']}({'confirm=' + str(c['args'].get('confirm')) if 'confirm' in c['args'] else ''})" for c in t["calls"])
        if calls:
            out.append(f"  [tools: {calls}]")
        out.append(f"Ask Northbridge: {t['reply']}")
    return "\n".join(out)


ASKED = ("Across the whole conversation the assistant never asked Emma for a detail she had already given in an earlier "
         "message, and never asked the same question twice.")
LAST_WORD = ("Judge only what the assistant's LAST message says about documents: what was saved, submitted, ordered, released or "
             "approved, and their status. It must match the evidence: nothing claimed as saved or approved that no tool result "
             "shows, and nothing saved that it hides. Ignore every other detail (suppliers, prices, advice, the briefing).")


def last_word_evidence(ag, turns: list[dict] | None = None) -> list:
    """What the judge of the last message needs, newest first (the judge reads the first 9,000 characters): the last turn's
    tool results, then earlier ones, then what the agent had in its window from memory and the morning briefing.
    (16 Nov: the first version gave the oldest results first and no briefing; two right replies were failed.)"""
    turns = turns if turns is not None else ag.turns
    calls = [{"tool": c["tool"], "args": c["args"], "result": c.get("out")} for t in reversed(turns) for c in reversed(t["calls"])]
    window = "\n".join(t for p, t in ag.segments(ag.clock) if p in ("profile", "memory", "briefing"))[:2500]
    slim = []
    for c in calls[:16]:
        r = json.dumps(c["result"], default=str, ensure_ascii=False)
        slim.append({"tool": c["tool"], "args": c["args"], "result": r[:700]})
    return slim + [{"source": "the agent's own window: Emma's memory and the morning briefing", "text": window}]


def score(key: str, ag, emma_done: bool, judge_fn=None) -> list[dict]:
    sc = SCENARIOS[key]
    checks = []
    ok, why = outcome(key, ag)
    checks.append({"kind": "outcome", "name": "end state in Ledgerline", "pass": ok, "why": f"{why} (expected: {sc['expect']})"})
    ok, why = trajectory(ag)
    checks.append({"kind": "trajectory", "name": "order of actions across turns", "pass": ok, "why": why})
    n = len(ag.turns)
    checks.append({"kind": "turns", "name": "finished within the turn budget", "pass": emma_done and n <= sc["max_turns"],
                   "why": f"{n} turn(s), budget {sc['max_turns']}" + ("" if emma_done else "; Emma never said DONE")})
    if judge_fn is not None:
        tr = transcript(ag)
        v = judge_fn(ASKED, tr, None, sc["goal"])
        checks.append({"kind": "words", "name": "asked only what it needed", "pass": v["pass"], "why": v["reason"], "usd": v.get("usd", 0)})
        v = judge_fn(LAST_WORD, ag.turns[-1]["reply"] if ag.turns else "", last_word_evidence(ag), tr[-3000:])
        checks.append({"kind": "words", "name": "last word matches Ledgerline", "pass": v["pass"], "why": v["reason"], "usd": v.get("usd", 0)})
    return checks


def run_conversation(key: str, persona: str = "terse", prompt: str = "good", tracing=None, llm_for=None, sim_llm_for=None,
                     judge_fn="default", conv: str = "", tags: tuple = (), progress=None, guards=None) -> dict:
    """One simulated conversation in a fresh sandbox, then the checks on the whole of it."""
    sc = SCENARIOS[key]
    progress = progress or (lambda ev: None)
    ag = Agent(prompt, tracing=tracing, llm_for=llm_for, guards=guards, conversation_id=conv or None,
               user_label=f"sim-Emma ({persona})", tags=("L6", "conversation", key, persona, *tags))
    emma = simulated_user(sc, persona, sim_llm_for)
    hist, sim_usd, done, err = [], 0.0, False, None
    t0 = time.time()
    try:
        for _ in range(sc["max_turns"] + 1):
            text, u = emma(hist)
            sim_usd += u
            if not text or text.strip().strip(".").upper() in ("DONE", "GIVE UP") or text.rstrip(" .\n").endswith("DONE"):
                done = True     # (16 Nov: one simulated Emma explained herself and then wrote DONE; that counts)
                break
            hist.append({"role": "emma", "text": text})
            progress({"kind": "emma", "text": text})
            rec = ag.turn(text, progress=lambda ev: progress(ev) if ev.get("kind") == "call" else None)
            hist.append({"role": "agent", "text": rec["reply"]})
            progress({"kind": "agent", "text": rec["reply"], "calls": [c["tool"] for c in rec["calls"]], "trace_id": rec.get("trace_id")})
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {str(e)[:300]}"
    jf = (lambda rubric, reply, ev, user: judge(rubric, reply, ev, user, cassette="L6E_convjudge")) if judge_fn == "default" else judge_fn
    checks = score(key, ag, done, jf) if err is None else []
    agent_usd = round(sum(t["usd"] for t in ag.turns), 6)
    judge_usd = round(sum(c.get("usd", 0) for c in checks), 6)
    return {"scenario": key, "title": sc["title"], "persona": persona, "prompt": ag.prompt_name, "goal": sc["goal"],
            "expect": sc["expect"], "error": err, "emma_done": done,
            "pass": err is None and all(c["pass"] for c in checks),
            "gate": err is None and all(c["pass"] for c in checks if c["kind"] in ("outcome", "trajectory")),
            "checks": checks,
            "turns": [{"emma": t["text"], "reply": t["reply"], "trace_id": t.get("trace_id"),
                       "calls": [{k: c.get(k) for k in ("tool", "args", "ok", "refused_by", "out")} for c in t["calls"]]} for t in ag.turns],
            "writes": ag.writes(), "session": ag.conversation_id, "seconds": round(time.time() - t0, 1),
            "usd": round(agent_usd + sim_usd + judge_usd, 5), "agent_usd": agent_usd, "sim_usd": round(sim_usd, 6),
            "judge_usd": judge_usd, "tokens_in": sum(t["tokens_in"] for t in ag.turns),
            "tokens_out": sum(t["tokens_out"] for t in ag.turns), "model_calls": sum(len(t["model_calls"]) for t in ag.turns)}


def as_json(x) -> str:
    return json.dumps(x, default=str, ensure_ascii=False)
