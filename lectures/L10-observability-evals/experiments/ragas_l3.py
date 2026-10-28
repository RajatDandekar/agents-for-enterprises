"""Lecture 10, Part 2: Ragas on Lecture 3's retriever and its 40 questions, next to Lecture 3's own code checks.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/ragas_l3.py

Two retrieval set-ups, the same 40 questions (bahi/course/l3/questions.py), the same answer prompt (R.ANSWER_SYSTEM):
  l3      Lecture 3's search_policy: BM25 + embeddings, RRF, rerank, top 4, permissions and freshness.
          Answers are Lecture 3's own recorded answers (lectures/L3-the-memory/experiments/logs/answers_eval.json).
  weak    a deliberately poor retriever: BM25 alone, top 1 clause (L3's logged BM25 ranking), no freshness filter.
          Answers generated here by gemini-3.8-flash (cassette IND10_ragas_answers).
Graded twice:
  code    Lecture 3's grader (facts by regex, citations by clause id): no model.
  ragas   IDBasedContextRecall / IDBasedContextPrecision (clause ids, no model), Faithfulness and ContextRecall
          (a model reads the claims), judge = google/gemini-3.8-flash via OpenRouter (ragas.llm_factory).
Writes logs/ragas_l3.json.
"""
import asyncio
import json
import os
import pathlib
import time

from bahi.agent import retrieval as R
from bahi.course import l3
from bahi.course.l3.questions import Q, grade
from bahi.llm import LLM

HERE = pathlib.Path(__file__).parent
L3LOG = HERE.parents[1] / "L3-the-memory" / "experiments" / "logs"
answers = {r["id"]: r for r in json.loads((L3LOG / "answers_eval.json").read_text())["rows"] if r["system"] == "rag"}
reteval = {q["id"]: q for q in json.loads((L3LOG / "retrieval_eval.json").read_text())["questions"]}
docs = R.load_corpus()
CHUNKS = {c.id: c for d in docs for c in R.chunk_by_section(d)}
ALL_IDS = set(CHUNKS)
ps = l3.policy_search("KJOSHI", route_facts=False)
llm = LLM("gemini:gemini-3.8-flash", cassette="IND10_ragas_answers", max_tokens=4096)

rows = []
for q in Q:
    # ---- l3: re-run the search (deterministic, cached) to get the clause texts; the answer is L3's recorded one
    res = ps.search(q["q"])
    ids = [c["cite"] for c in res["clauses"]]
    a = answers[q["id"]]
    texts = [CHUNKS[i].render() if i in CHUNKS else "" for i in ids]
    rows.append({"setup": "l3", "id": q["id"], "kind": q["kind"], "q": q["q"], "gold": q["gold"], "context_ids": ids,
                 "context_ids_match_l3_log": ids == a["context_ids"], "contexts": texts, "answer": a["answer"],
                 "code": {k: a[k] for k in ("correct", "gold_cited", "context_has_gold")}})
    # ---- weak: BM25 alone, top 1
    top = (reteval.get(q["id"], {}).get("bm25", {}).get("top5") or [None])[0]
    if top is None:  # questions L3 did not rank (no gold): rank them with BM25 now
        hits = l3.retriever("KJOSHI").bm25_search(q["q"], 1) if hasattr(l3.retriever("KJOSHI"), "bm25_search") else []
        top = hits[0].chunk.id if hits else None
    chunk = CHUNKS.get(top)
    ctx = R.build_context([chunk]) if chunk else "(no extracts)"
    out = R.answer_with(llm, q["q"], ctx)
    cc = R.check_citations(out["answer"], [top] if top else [], ALL_IDS)
    g = grade(q, out["answer"], cc["cites"])
    rows.append({"setup": "weak", "id": q["id"], "kind": q["kind"], "q": q["q"], "gold": q["gold"],
                 "context_ids": [top] if top else [], "contexts": [chunk.render()] if chunk else [],
                 "answer": out["answer"], "tokens_in": out.get("tokens_in"), "tokens_out": out.get("tokens_out"),
                 "code": {"correct": g["correct"], "gold_cited": g["gold_cited"],
                          "context_has_gold": (top in q["gold"]) if q["gold"] else None}})
print("answers ready:", len(rows), "l3 contexts identical to L3's log:",
      sum(r.get("context_ids_match_l3_log", False) for r in rows if r["setup"] == "l3"), "/ 40")

# ---------------------------------------------------------------------------------------------- Ragas
from openai import AsyncOpenAI  # noqa: E402
from ragas.llms import llm_factory  # noqa: E402
from ragas.metrics.collections import ContextRecall, Faithfulness  # noqa: E402

client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
try:  # ragas' default output budget truncated long claim lists (IncompleteOutputException in our first run)
    judge = llm_factory("google/gemini-3.8-flash", provider="openai", client=client, max_tokens=8192)
except TypeError:
    judge = llm_factory("google/gemini-3.8-flash", provider="openai", client=client)
faith, crecall = Faithfulness(llm=judge), ContextRecall(llm=judge)
try:
    from ragas.metrics.collections import IDBasedContextPrecision, IDBasedContextRecall  # noqa: E402
    ID_API = "collections"
except ImportError:
    from ragas.metrics import IDBasedContextPrecision, IDBasedContextRecall  # noqa: E402
    ID_API = "legacy"
from ragas import SingleTurnSample  # noqa: E402

idr, idp = IDBasedContextRecall(), IDBasedContextPrecision()
sem = asyncio.Semaphore(8)


async def id_scores(r):
    if not r["gold"]:
        return None, None
    if ID_API == "collections":
        a = await idr.ascore(retrieved_context_ids=r["context_ids"], reference_context_ids=r["gold"])
        b = await idp.ascore(retrieved_context_ids=r["context_ids"], reference_context_ids=r["gold"])
        return a.value, b.value
    s = SingleTurnSample(retrieved_context_ids=r["context_ids"], reference_context_ids=r["gold"])
    return await idr.single_turn_ascore(s), await idp.single_turn_ascore(s)


async def one(r):
    async with sem:
        r["ragas"] = {}
        r["ragas"]["id_context_recall"], r["ragas"]["id_context_precision"] = await id_scores(r)
        t0 = time.perf_counter()
        try:
            f = await faith.ascore(user_input=r["q"], response=r["answer"], retrieved_contexts=r["contexts"] or [""])
            r["ragas"]["faithfulness"] = f.value
            r["ragas"]["faithfulness_reason"] = getattr(f, "reason", None)
        except Exception as e:  # noqa: BLE001
            r["ragas"]["faithfulness"], r["ragas"]["faithfulness_error"] = None, repr(e)[:300]
        if r["gold"]:
            ref = "\n".join(CHUNKS[g].text for g in r["gold"] if g in CHUNKS)
            try:
                c = await crecall.ascore(user_input=r["q"], retrieved_contexts=r["contexts"] or [""], reference=ref)
                r["ragas"]["context_recall"] = c.value
            except Exception as e:  # noqa: BLE001
                r["ragas"]["context_recall"], r["ragas"]["context_recall_error"] = None, repr(e)[:300]
        r["ragas"]["seconds"] = round(time.perf_counter() - t0, 2)


async def main():
    await asyncio.gather(*(one(r) for r in rows))

t0 = time.perf_counter()
asyncio.run(main())
wall = round(time.perf_counter() - t0, 1)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


summary = {}
for s in ("l3", "weak"):
    rs = [r for r in rows if r["setup"] == s]
    g = [r for r in rs if r["gold"]]
    summary[s] = {"n": len(rs), "code_correct": sum(r["code"]["correct"] for r in rs),
                  "code_context_has_gold": sum(bool(r["code"]["context_has_gold"]) for r in g), "n_gold": len(g),
                  "id_context_recall": mean([r["ragas"]["id_context_recall"] for r in g]),
                  "id_context_precision": mean([r["ragas"]["id_context_precision"] for r in g]),
                  "faithfulness": mean([r["ragas"]["faithfulness"] for r in rs]),
                  "context_recall_llm": mean([r["ragas"].get("context_recall") for r in g]),
                  "faithful_but_wrong": sum(1 for r in rs if (r["ragas"]["faithfulness"] or 0) >= 0.8 and not r["code"]["correct"]),
                  "unfaithful_but_right": sum(1 for r in rs if r["ragas"]["faithfulness"] is not None
                                              and r["ragas"]["faithfulness"] < 0.5 and r["code"]["correct"]),
                  "id_recall_vs_code_context_has_gold_agree": sum(1 for r in g if ((r["ragas"]["id_context_recall"] or 0) > 0)
                                                                  == bool(r["code"]["context_has_gold"]))}
out = {"date": time.strftime("%Y-%m-%d %H:%M"), "judge": "openrouter google/gemini-3.8-flash via ragas.llm_factory",
       "ragas_id_api": ID_API, "wall_s": wall, "summary": summary, "rows": rows}
(HERE / "logs" / "ragas_l3.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print(json.dumps(summary, indent=1))
