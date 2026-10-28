"""Lecture 3 experiment, part 2: Kavita's Shakti Seals question, from the bare brain to Ask Rasoi with search_policy.

    Kavita: "Can I buy the gaskets from Shakti Seals? They quote ₹10.40"
The right answer is no: gaskets are food-contact parts, and Purchase Policy POL-PUR-001 §6.2 allows them only from a
supplier with a valid food-grade certificate on file. Shakti Seals is not in the supplier master and has none.

  1. brain       Ask Rasoi at the 'brain' stage (Lecture 2's system prompt), three Gemini tiers
  2. with62      the same brain with only §6.2 pasted into the prompt (the context window is the memory)
  3. full        every document Kavita may read, pasted whole
  4. rag_raw     RAG searching with Kavita's own words
  5. rag_rewrite the model first writes the search query, then RAG
  6. knowledge   Ask Rasoi at the 'knowledge' stage: brain + the search_policy tool from bahi/toolbox (a real trace)
  7. checker     check_citations on the knowledge answer, and on the same answer with §6.2 edited to §6.9 (labelled)
Model calls recorded in cassettes L3v3_coldopen, L3v3_story, L3v3_knowledge. Writes logs/story.json.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bahi.agent import retrieval as R
from bahi.course import l3
from bahi.erp.engine import ERP
from bahi.llm import LLM

OUT = pathlib.Path(__file__).parent / "logs"
Q = l3.SHAKTI
log = {"question": Q, "date": "2026-10-28", "system_brain": l3.SYSTEM_BRAIN, "system_knowledge": l3.SYSTEM_KNOWLEDGE_V0,
       "answer_system": R.ANSWER_SYSTEM, "rewrite_system": l3.REWRITE_SYSTEM_V0}

# 1. the bare brain, three tiers
log["brain"] = {}
for m in ("gemini:gemini-3.5-flash-lite", "gemini:gemini-3.8-flash", "gemini:gemini-3.1-pro-preview"):
    llm = LLM(m, cassette="L3v3_coldopen", max_tokens=4096)
    log["brain"][m] = l3.brain_answer(Q, llm)

llm = LLM(l3.MODEL, cassette="L3v3_story", max_tokens=4096)
corpus = R.load_corpus()
ret = l3.retriever("KJOSHI")
c62 = next(c for c in ret.chunks if c.id == "POL-PUR-001 §6.2")

# 2. only §6.2 in the prompt
msgs = l3.rag_prompt(Q, [R.Hit(c62, 0).as_clause()])
r = llm.chat(msgs)
log["with62"] = {"prompt": msgs, "answer": r.content, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
                 "cost_inr": round(r.cost_inr, 4), "seconds": r.seconds}

# 3. everything Kavita may read, pasted whole
K = R.clearance_for("KJOSHI")
VISIBLE = [d for d in corpus if R.allowed(d, K)]
FULL_CTX = "\n\n".join(
    f"===== {d.doc_id}: {d.title} v{d.version}, effective {d.effective}"
    + (f", amends {', '.join(d.amends)}" if d.amends else "") + f" =====\n{d.body}" for d in VISIBLE)
o = R.answer_with(llm, Q, FULL_CTX)
o["cost_inr"] = round(llm.log[-1].cost_inr, 4)
o.pop("context", None)
o["check"] = R.check_citations(o["answer"], sorted(R.corpus_ids(VISIBLE)), R.corpus_ids())
log["full"] = o

# 4. RAG with her own words; 5. the model writes the query first
ps = l3.policy_search("KJOSHI", route_facts=False)
log["rag_raw"] = l3.rag_answer(Q, llm, ps)
rw = l3.rewrite_query(Q, llm, system=l3.REWRITE_SYSTEM_V0)
log["rewrite"] = rw
log["rag_rewrite"] = l3.rag_answer(Q, llm, ps, query=rw["query"])
log["rag_rewrite"]["search_detail"] = [{"id": h.chunk.id, **h.why} for h in ret.search(rw["query"], k=8)]
log["rag_rewrite"]["prompt_tokens"] = l3.count_tokens(log["rag_rewrite"]["prompt"][1]["content"])

# 6. Ask Rasoi at the knowledge stage, with search_policy from the toolbox
erp = ERP()
kllm = LLM(l3.MODEL, cassette="L3v3_knowledge", max_tokens=4096)
agent = l3.knowledge_agent(erp, kllm, system=l3.SYSTEM_KNOWLEDGE_V0)
ans = agent.respond(Q)
ctx_ids = []
for t in agent.trace:
    try:
        ctx_ids += [c["cite"] for c in json.loads(t["result"]).get("clauses", [])]
    except Exception:
        pass
log["knowledge"] = {"answer": ans, "trace": agent.trace, "messages": agent.messages, "tools": agent.schemas(),
                    "llm": kllm.totals(), "calls": [{"tokens_in": x.tokens_in, "tokens_out": x.tokens_out,
                                                    "seconds": x.seconds} for x in kllm.log],
                    "check": R.check_citations(ans, ctx_ids, R.corpus_ids()), "erp_writes": len(getattr(erp, "audit", []) or [])}

# 7. the checker, on the real answer and on a copy edited by hand (labelled as such on the plate)
edited = ans.replace("§6.2", "§6.9")
log["checker"] = {"real": R.check_citations(ans, ctx_ids, R.corpus_ids()),
                  "edited_to_6_9": R.check_citations(edited, ctx_ids, R.corpus_ids()),
                  "edited_text": edited}

(OUT / "story.json").write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str))
for m, v in log["brain"].items():
    print("BRAIN", m, "|", v["answer"][:500].replace("\n", " "))
print("WITH62 |", log["with62"]["answer"][:400])
print("FULL |", log["full"]["answer"][:400], log["full"]["tokens_in"], log["full"]["cost_inr"])
print("RAG RAW |", [c["cite"] for c in log["rag_raw"]["clauses"]], log["rag_raw"]["answer"][:300])
print("REWRITE |", rw["query"])
print("RAG RW |", [c["cite"] for c in log["rag_rewrite"]["clauses"]], log["rag_rewrite"]["answer"][:500], log["rag_rewrite"]["check"])
print("KNOW trace |", [(t["tool"], t["args"]) for t in agent.trace])
print("KNOW |", ans[:700], log["knowledge"]["check"], log["knowledge"]["llm"])
