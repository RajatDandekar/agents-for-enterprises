"""Lecture 3 experiment, part 3: why our first Ask Rasoi missed §6.2 on the Shakti question, and what fixed it.

story.py showed it: Kavita's words ("gaskets", "Shakti Seals", "quote ₹10.40") never say food or certificate, so
neither her words nor the model's own search queries found POL-PUR-001 §6.2. Here we measure three fixes:
  A. rewrite   the model writes the search query, with one line of company context: first one long query
               (l3.REWRITE_SYSTEM_V1, "rewrite_one"), then one short query per rule (l3.REWRITE_SYSTEM, "rewrite")
  B. wiki      the LLM wiki: the model reads the index of compiled pages and picks the ones to read
  C. agent     Ask Rasoi at the knowledge stage with the same context line (l3.SYSTEM_KNOWLEDGE)
and check that the context line does not hurt other questions: agent V0 vs V1 on six of the 40 questions.
Cassettes L3v3_story, L3v3_knowledge. Writes logs/finding62.json.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from questions import Q as QS, grade
from bahi.agent import retrieval as R
from bahi.course import l3
from bahi.erp.engine import ERP
from bahi.llm import LLM

import os
os.environ.setdefault("L3_ROUTE", "openrouter:google/gemini-3.8-flash")  # the Gemini prepay ran out on 2026-10-28 (l3.RoutedLLM)
OUT = pathlib.Path(__file__).parent / "logs"
Q = l3.SHAKTI
llm = l3.RoutedLLM(l3.MODEL, cassette="L3v3_story", max_tokens=4096)
ps = l3.policy_search("KJOSHI", route_facts=False)
ret = ps.r
log = {"question": Q, "company_context": l3.COMPANY_CONTEXT, "rewrite_system": l3.REWRITE_SYSTEM,
       "rewrite_system_v1": l3.REWRITE_SYSTEM_V1, "agent_max_steps": 10,
       "system_knowledge": l3.SYSTEM_KNOWLEDGE}

# A1. one long rewritten query, with context
rw1 = l3.rewrite_query(Q, llm)
a1 = l3.rag_answer(Q, llm, ps, query=rw1["query"])
a1["rewrite"] = rw1
a1["search_detail"] = [{"id": h.chunk.id, **h.why} for h in ret.search(rw1["query"], k=8)]
log["rewrite_one"] = a1
# A2. one short query per rule
rw = l3.rewrite_queries(Q, llm)
a = l3.rag_answer(Q, llm, ps, queries=rw["queries"])
a["rewrite"] = rw
a["search_detail"] = {q: [{"id": h.chunk.id, **h.why} for h in ret.search(q, k=6)] for q in rw["queries"]}
a["prompt_tokens"] = l3.count_tokens(a["prompt"][1]["content"])
log["rewrite"] = a

# B. the wiki
wiki = R.Wiki(R.WIKI_DIR)
w = wiki.answer(Q, llm, "KJOSHI")
w["check"] = R.check_citations(w["answer"], w["context_ids"], R.corpus_ids())
w["index"] = wiki.index_for(R.clearance_for("KJOSHI"))
log["wiki"] = w


def ctx_ids(agent):
    out = []
    for t in agent.trace:
        try:
            out += [c["cite"] for c in json.loads(t["result"]).get("clauses", [])]
        except Exception:
            pass
    return out


def run_agent(question, system):
    kllm = l3.RoutedLLM(l3.MODEL, cassette="L3v3_knowledge", max_tokens=4096)
    agent = l3.knowledge_agent(ERP(), kllm, system=system)
    ans = agent.respond(question)
    ids = ctx_ids(agent)
    return {"answer": ans, "trace": agent.trace, "routes": sorted({x.model for x in kllm.log}), "messages": agent.messages, "llm": kllm.totals(),
            "calls": [{"tokens_in": x.tokens_in, "tokens_out": x.tokens_out, "seconds": x.seconds} for x in kllm.log],
            "context_ids": ids, "check": R.check_citations(ans, ids, R.corpus_ids()),
            "found_62": "POL-PUR-001 §6.2" in ids, "cites_62": "POL-PUR-001 §6.2" in R.extract_citations(ans)}


# C. the agent with the context line
log["agent"] = run_agent(Q, l3.SYSTEM_KNOWLEDGE)
log["agent"]["tools"] = l3.knowledge_agent(ERP(), llm).schemas()

# D. does the line hurt elsewhere? six questions, V0 vs V1
pick = ["P01", "P17", "M01", "F02", "T01", "H01"]
log["check6"] = []
for qid in pick:
    q = next(x for x in QS if x["id"] == qid)
    row = {"id": qid, "q": q["q"]}
    for name, sysm in (("v0", l3.SYSTEM_KNOWLEDGE_V0), ("v1", l3.SYSTEM_KNOWLEDGE)):
        r = run_agent(q["q"], sysm)
        g = grade(q, r["answer"], r["check"]["cites"])
        row[name] = {"correct": g["correct"], "gold_cited": g["gold_cited"], "cites": r["check"]["cites"],
                     "invented": r["check"]["invented"], "ungrounded": r["check"]["ungrounded"],
                     "searches": [t["args"].get("question") for t in r["trace"]], "tokens_in": r["llm"]["tokens_in"],
                     "cost_inr": r["llm"]["cost_inr"], "answer": r["answer"]}
    log["check6"].append(row)

log["routes_story"] = sorted({x.model for x in llm.log})
(OUT / "finding62.json").write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str))
print("REWRITE1 |", rw1["query"], [c["cite"] for c in a1["clauses"]])
print("REWRITE |", rw["queries"])
print("  clauses", [c["cite"] for c in a["clauses"]], "|", a["answer"][:500])
print("  per query", a["per_query"])
print("WIKI | pages", w["pages"], "|", w["answer"][:500], w["check"])
g = log["agent"]
print("AGENT | searches", [t["args"] for t in g["trace"]], "found62", g["found_62"], "cites62", g["cites_62"])
print("  ", g["answer"][:900], g["check"], g["llm"])
for r in log["check6"]:
    print(r["id"], "v0", r["v0"]["correct"], r["v0"]["gold_cited"], r["v0"]["cost_inr"], "| v1", r["v1"]["correct"], r["v1"]["gold_cited"], r["v1"]["cost_inr"], r["v1"]["searches"])
