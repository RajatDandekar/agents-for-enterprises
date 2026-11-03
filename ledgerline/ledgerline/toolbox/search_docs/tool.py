"""Search documents: search all of Northbridge's documentation (northbridge-docs) with the Lecture 3 race winner.

Input and output are described in tool.json next to this file."""
def run(s, question, k=10):
    """The best measured RAG configuration (BM25 + reranker over structure-aware chunks), filtered by the signed-in
    user's role before ranking, plus the withheld notice when a confidential HR document would have matched.
    (No timing in the result: what the model reads stays the same run to run, so recorded runs replay.)"""
    from ledgerline.course.l3.rag import rag_search

    k = max(1, min(int(k or 10), 15))
    hits = rag_search(question, user=s.user_id, k=k, withheld=True)
    out = []
    for i, h in enumerate(hits, 1):
        m = h.get("meta") or {}
        status = ("withheld" if m.get("withheld") else "superseded" if m.get("superseded")
                  else "not yet in force" if m.get("future") else "current")
        out.append({"n": i, "cite": h["cite"], "status": status, "text": h["text"]})
    return {"ok": True, "passages": out, "withheld": any(p["status"] == "withheld" for p in out),
            "method": "RAG: BM25 + bge-reranker-base, structure-aware 200-token chunks"}
