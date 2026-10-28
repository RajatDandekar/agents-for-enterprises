"""Lecture 3, The Memory: giving Ask Rasoi knowledge. Helpers shared by the L3 deck experiments and NB3.

    from bahi.course import l3
    r = l3.retriever("KJOSHI")                     # Kavita's index: BM25 + embeddings + reranker, L3's own caches
    out = l3.rag_answer(l3.SHAKTI, llm)            # retrieved clauses, the exact prompt, the answer, the citation check
    agent = l3.knowledge_agent(erp, llm)           # Ask Rasoi at the 'knowledge' stage: search_policy is its one tool

The retrieval code itself is bahi.agent.retrieval (kept from v2). This file only adds:
  * caches  L3 keeps its own vectors, reranker scores and token counts in bahi/course/l3/_index/, reading the shared
            bahi/docs/_index/ first, so nothing shared is rewritten and a notebook replays with no key and no model download;
  * prompts Ask Rasoi at the 'brain' stage (Lecture 2's prompt, unchanged) and at the 'knowledge' stage;
  * the cold-open question, Kavita's Shakti Seals question.
"""
from __future__ import annotations

import json
import os
import pathlib
import re

from ...agent import retrieval as R
from ...llm import LLM

HERE = pathlib.Path(__file__).parent
IDX = HERE / "_index"
MODEL = "gemini:gemini-3.8-flash"

SHAKTI = "Can I buy the gaskets from Shakti Seals? They quote ₹10.40"

try:  # Lecture 2's brain-stage prompt, so the cold open continues where L2 stopped
    from ..l2.brain import SYSTEM_BRAIN
except Exception:  # pragma: no cover
    SYSTEM_BRAIN = ("You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of "
                    "pressure cookers. You help Rasoi's staff with purchasing, stores and suppliers. "
                    "Answer the question directly and briefly.")

SYSTEM_KNOWLEDGE_V0 = SYSTEM_BRAIN + (
    " You are talking to {name} ({user_id}). Today is Monday 26 October 2026."
    " For any question about Rasoi's rules (may we, must we, who approves, what an error means), call search_policy"
    " first and answer only from the clauses it returns, citing each rule you use like (POL-PUR-001 §6.2)."
    " If the clauses do not answer the question, say the documents do not cover it. You cannot see live data yet"
    " (stock, budgets, the supplier master); say so when the answer depends on it.")

# What we added after our first knowledge-stage run missed §6.2 (logs/story.json): Kavita's words never say "food",
# so no search found the food-grade rule. One line of company context, and an instruction to search for each rule
# the question could depend on, not for the question's words (logs/finding62.json measures the change).
COMPANY_CONTEXT = (" Rasoi makes pressure cookers, so many of the parts it buys touch food. Before you answer, think which"
                   " of Rasoi's rules the question could depend on (the kind of part, the supplier, the amount, the price)"
                   " and search for each of them separately.")
SYSTEM_KNOWLEDGE = SYSTEM_KNOWLEDGE_V0 + COMPANY_CONTEXT


# ------------------------------------------------------------------------------------------------ the model's route
class RoutedLLM(LLM):
    """The same model (gemini-3.8-flash), reached through another gateway when L3_ROUTE is set.

    On 2026-10-28 the course's Gemini prepaid credit ran out in the middle of our runs. The calls recorded after that
    went to the same model through OpenRouter (L3_ROUTE=openrouter:google/gemini-3.8-flash). They are stored under the
    usual request key, so a notebook replays them as gemini-3.8-flash, and each record's "model" field names the
    route it really took. With L3_ROUTE unset this is exactly bahi.llm.LLM."""

    def _live(self, messages, tools, response_format, **kw):
        route = os.environ.get("L3_ROUTE")
        if not route:
            return super()._live(messages, tools, response_format, **kw)
        alt = LLM(route, cassette="_route", mode="live", temperature=self.temperature, max_tokens=self.max_tokens)
        return alt._live(messages, tools, response_format, **kw)


# ------------------------------------------------------------------------------------------------ caches
class LayeredCache(R._JsonlCache):
    """Read L3's own cache, then the shared one; write only to L3's own."""

    def __init__(self, own: pathlib.Path, shared: pathlib.Path):
        super().__init__(own)
        self.shared = R._JsonlCache(shared)

    def get(self, k):
        v = self.d.get(k)
        return v if v is not None else self.shared.get(k)


def embedder() -> R.Embedder:
    e = R.Embedder()
    e.cache = LayeredCache(IDX / "embeddings.jsonl", R.INDEX_DIR / "embeddings.jsonl")
    return e


def reranker() -> R.Reranker:
    r = R.Reranker()
    r.cache = LayeredCache(IDX / "rerank.jsonl", R.INDEX_DIR / "rerank.jsonl")
    return r


_E = _RR = None


def _shared():
    global _E, _RR
    if _E is None:
        _E, _RR = embedder(), reranker()
    return _E, _RR


def retriever(user: str | None = "KJOSHI", **kw) -> R.Retriever:
    e, rr = _shared()
    kw.setdefault("embedder", e)
    kw.setdefault("reranker", rr)
    return R.Retriever(user, **kw)


def policy_search(user: str = "KJOSHI", **kw) -> R.PolicySearch:
    rkw = {k: kw.pop(k) for k in ("permissions", "freshness", "clearance", "docs", "as_of") if k in kw}
    return R.PolicySearch(user, retriever=retriever(user, **rkw), **kw)


def count_tokens(text: str) -> int:
    """Gemini's exact count, cached in L3's own file (falls back to len/4 only when uncached and keyless)."""
    return R.count_tokens(text, cache=IDX / "tokens.jsonl")


def use_l3_caches():
    """Point the search_policy tool (bahi.toolbox) at L3's caches for this process: same search, L3's cache files."""
    for user in ("KJOSHI", "RMEHTA", "SKULKARNI", "APATIL", "NDESAI"):
        R._PS[(user, R.TODAY)] = policy_search(user)


# ------------------------------------------------------------------------------------------------ RAG, end to end
def rag_prompt(question: str, clauses: list[dict], system: str = R.ANSWER_SYSTEM) -> list[dict]:
    ctx = R.build_context(clauses)
    return [{"role": "system", "content": system},
            {"role": "user", "content": f"EXTRACTS:\n{ctx}\n\nQUESTION: {question}"}]


REWRITE_SYSTEM_V0 = ("You turn a question from a member of staff at Rasoi Steel Works into one search query for the "
                  "company's policy documents and ERP manual. Name, in plain words, the rules the question depends on "
                  "(for example the kind of part, supplier rules, approval limits, prices, tax). Reply with the query only, "
                  "in one line.")
REWRITE_SYSTEM_V1 = REWRITE_SYSTEM_V0 + COMPANY_CONTEXT.replace(" Before you answer,", " Before you write the query,").replace(
    " and search for each of them separately.", " and name each of them in the query.")
# Our second try (logs/finding62_run1.json): one long rewritten query put §6.2 first, but the reranker scored that
# pair -1.25, below the cut at 0, because one query mixed four topics. So: one short query per rule, searched one by one.
REWRITE_SYSTEM = ("You turn a question from a member of staff at Rasoi Steel Works into search queries for the company's "
                  "policy documents and ERP manual." + COMPANY_CONTEXT.replace(" Before you answer, think", " Think").replace(
                      " and search for each of them separately.", " and write one short query for each rule, in plain words,"
                      " one per line, at most four lines.") + " Reply with the queries only.")


def rewrite_queries(question: str, llm: LLM, system: str | None = None) -> dict:
    """The model writes one short search query per rule the answer could depend on."""
    r = llm.chat([{"role": "system", "content": system or REWRITE_SYSTEM}, {"role": "user", "content": question}])
    qs = [re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", l).strip().strip('"') for l in (r.content or "").splitlines()]
    return {"queries": [q for q in qs if q][:4], "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
            "seconds": r.seconds, "cost_inr": round(r.cost_inr, 4)}


def multi_search(ps: R.PolicySearch, queries: list[str], k: int = 5) -> dict:
    """Search each query; keep every clause that clears the cut, at its best score; return the top k."""
    best, by = {}, {}
    for q in queries:
        for c in ps.search(q)["clauses"]:
            if c["cite"] not in best or c["score"] > best[c["cite"]]["score"]:
                best[c["cite"]] = c
            by.setdefault(q, []).append([c["cite"], c["score"]])
    clauses = sorted(best.values(), key=lambda c: -c["score"])[:k]
    return {"clauses": clauses, "per_query": by, "answer_in_documents": bool(clauses)}


def rewrite_query(question: str, llm: LLM, system: str | None = None) -> dict:
    """Step 0 of RAG when the question does not use the words of the rule: the model writes the search query."""
    r = llm.chat([{"role": "system", "content": system or REWRITE_SYSTEM_V1}, {"role": "user", "content": question}])
    return {"query": (r.content or "").strip().strip('"'), "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
            "seconds": r.seconds, "cost_inr": round(r.cost_inr, 4)}


def rag_answer(question: str, llm: LLM, ps: R.PolicySearch | None = None, query: str | None = None,
               queries: list[str] | None = None) -> dict:
    """Retrieve → build the prompt → answer → check the citations. Every intermediate is returned for the plates.
    query: one search (default: the question itself); queries: several, merged by multi_search.
    The prompt always carries the user's own question."""
    ps = ps or policy_search("KJOSHI", route_facts=False)
    res = multi_search(ps, queries) if queries else ps.search(query or question)
    msgs = rag_prompt(question, res["clauses"])
    r = llm.chat(msgs)
    ids = [c["cite"] for c in res["clauses"]]
    return {"question": question, "query": query or question, "queries": queries, "per_query": res.get("per_query"), "clauses": res["clauses"], "prompt": msgs,
            "answer": r.content or "",
            "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds, "cost_inr": round(r.cost_inr, 4),
            "check": R.check_citations(r.content or "", ids, R.corpus_ids())}


def brain_answer(question: str, llm: LLM) -> dict:
    r = llm.chat([{"role": "system", "content": SYSTEM_BRAIN}, {"role": "user", "content": question}])
    return {"answer": r.content or "", "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}


def knowledge_agent(erp, llm: LLM, user: str = "KJOSHI", system: str | None = None):
    """Ask Rasoi at the 'knowledge' stage: the brain plus one tool, search_policy, from the course toolbox."""
    from ...agent.loop import ToolLoopAgent
    from ...toolbox import Toolbox
    use_l3_caches()
    return ToolLoopAgent(erp, user, llm=llm, tools=Toolbox(erp, user, names=["search_policy"]), max_steps=10,
                         system=system or SYSTEM_KNOWLEDGE)


def load_log(name: str) -> dict:
    """An L3 experiment log, from the course folder when it is here, else from the course repository."""
    import urllib.request
    for p in [HERE.parents[3] / "lectures" / "L3-the-memory" / "experiments" / "logs" / name,
              pathlib.Path("experiments/logs") / name]:
        if p.exists():
            return json.loads(p.read_text())
    url = ("https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/"
           f"lectures/L3-the-memory/experiments/logs/{name}")
    return json.loads(urllib.request.urlopen(url).read())
