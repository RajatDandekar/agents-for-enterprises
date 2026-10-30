"""Make search_policy's results reproducible, so the recorded runs replay exactly.

    use_own_caches()     # call once before any mission (Rig does)

search_policy ranks clauses with an embedding model and a cross-encoder (ledgerline.agent.retrieval). Their scores are
cached, rounded, in docs/_index/*.jsonl, but the shared cache is not written back from a Modal run, and a score
computed in a different batch can differ in the last decimal. With missions running in parallel, which batch a pair
lands in depends on timing, so a replay could see a different ranking from the recording and miss the cassette
(we measured 2 misses in 120 missions before this fix).

The fix is plain production hygiene: one embedder and one reranker shared by every person, a cache this package owns
(course/l1/production/_index/, written back with the run), read before the shared one, where the first value
written for a key wins. Every value the recording saw is then on disk, and a replay never recomputes one.
"""
from __future__ import annotations

import json
import pathlib
import threading

from ....agent import retrieval as R

IDX = pathlib.Path(__file__).parent / "_index"
USERS = ("ECLARKE", "DOKAFOR", "ATANAKA", "LMORENO", "HWEBER", "SVC_AGENT")
_done: list = []


class OwnCache(R._JsonlCache):
    """Read this package's cache, then the shared one. Write only this package's. The first value for a key wins."""

    def __init__(self, own: pathlib.Path, shared: pathlib.Path):
        super().__init__(own)
        self.shared = R._JsonlCache(shared)
        self._lock = threading.Lock()

    def get(self, k):
        v = self.d.get(k)
        return v if v is not None else self.shared.get(k)

    def put(self, k, v):
        with self._lock:
            if self.get(k) is not None:      # first write wins: everyone sees the value the first caller stored
                return
            self.d[k] = v
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as f:
                f.write(json.dumps({"k": k, "v": v}) + "\n")


def use_own_caches():
    if _done:
        return
    e, rr = R.Embedder(), R.Reranker()
    e.cache = OwnCache(IDX / "embeddings.jsonl", R.INDEX_DIR / "embeddings.jsonl")
    rr.cache = OwnCache(IDX / "rerank.jsonl", R.INDEX_DIR / "rerank.jsonl")
    for user in USERS:
        R._PS[(user, R.TODAY)] = R.PolicySearch(user, retriever=R.Retriever(user, embedder=e, reranker=rr))
    _done.append(True)
