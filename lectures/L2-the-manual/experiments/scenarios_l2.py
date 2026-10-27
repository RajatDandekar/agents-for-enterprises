"""Lecture 2: scenario 1 three ways, the six-scenario scorecard at this layer, and one turn's context window, counted.

  naive        Lecture 1's agent: 38 raw services, the service account, no documents        (cassette L2_naive)
  toolloop     Lecture 3's tool loop with the intent tools, no documents                    (cassette L2_toolloop)
  policy       the same loop + search_policy (+ a system line: rules come from search_policy) (cassette L2_policy_agent)
Writes logs/scenarios_l2.json.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from questions import Q
from bahi.agent.naive import NaiveAgent
from bahi.agent.loop import ToolLoopAgent
from bahi.agent.retrieval import make_policy_agent, context_budget, erp_fact, count_tokens
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS, run_scenario, scorecard

MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemini:gemini-3.8-flash"
OUT = pathlib.Path(__file__).parent / "logs"; OUT.mkdir(exist_ok=True)


def spy(llm):
    calls = []
    orig = llm.chat

    def chat(messages, tools=None, **kw):
        calls.append({"messages": json.loads(json.dumps(messages, default=str)), "tools": tools})
        return orig(messages, tools=tools, **kw)
    llm.chat = chat
    return calls


def trace(msgs):
    out = []
    for m in msgs:
        if m["role"] == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                out.append({"call": tc["function"]["name"], "args": json.loads(tc["function"]["arguments"])})
        elif m["role"] == "tool":
            out.append({"result": m["content"][:700]})
        elif m["role"] == "assistant":
            out.append({"reply": m["content"]})
        elif m["role"] == "user":
            out.append({"user": m["content"]})
    return out


def res_dict(r):
    return {k: v for k, v in r.__dict__.items()}


log = {"model": MODEL}
s1 = SCENARIOS[0]
agents = {}
for name, cas in (("naive", "L2_naive"), ("toolloop", "L2_toolloop"), ("policy", "L2_policy_agent")):
    llm = LLM(MODEL, cassette=cas)
    calls = spy(llm)
    holder = []
    if name == "naive":
        mk = lambda erp, user: holder.append(NaiveAgent(erp, user, llm=llm)) or holder[-1]
    elif name == "toolloop":
        mk = lambda erp, user: holder.append(ToolLoopAgent(erp, user, llm=llm)) or holder[-1]
    else:
        base = make_policy_agent(llm)
        mk = lambda erp, user: holder.append(base(erp, user)) or holder[-1]
    r = run_scenario(mk, s1, verbose=True)
    agent = holder[-1]
    log[name] = {"result": res_dict(r), "trace": trace(agent.messages[1:]),
                 "per_call_tokens_in": [x.tokens_in for x in llm.log], "per_call_tokens_out": [x.tokens_out for x in llm.log]}
    if name == "policy":
        budgets = []
        for i, c in enumerate(calls):
            b = context_budget(c["messages"], c["tools"] or [])
            budgets.append({"call": i + 1, "measured_tokens_in": llm.log[i].tokens_in, "parts": b,
                            "sum_counted": sum(x["tokens"] for x in b)})
        log["policy"]["context_budget"] = budgets
        log["policy"]["system_prompt"] = calls[0]["messages"][0]["content"]
        agents["policy_llm"] = llm
    print(name, "PASS" if r.passed else "FAIL", r.notes, r.tokens_in, r.tokens_out)
# ---- the six scenarios with the Lecture 2 agent (intent tools + search_policy)
llm = agents["policy_llm"]
res = [run_scenario(make_policy_agent(llm), sc) for sc in SCENARIOS]
log["scorecard"] = [res_dict(r) for r in res]
print(scorecard(res).to_string())
# ---- the ERP-fact router, v2, on all 40 questions
flag = {q["id"]: erp_fact(q["q"]) for q in Q}
log["router_v2"] = {"flagged": {k: v for k, v in flag.items() if v},
                    "traps_flagged": sum(1 for q in Q if q["kind"] == "trap" and flag[q["id"]]),
                    "non_traps_flagged": sum(1 for q in Q if q["kind"] != "trap" and flag[q["id"]])}
print(log["router_v2"])
(OUT / "scenarios_l2.json").write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str))
print(json.dumps(log["policy"]["context_budget"], indent=1))
print(json.dumps(log["naive"]["trace"][-3:], indent=1, ensure_ascii=False))
