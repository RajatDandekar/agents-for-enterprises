"""Lecture 10, Observability and Evals in Industry: the industry tools, mapped onto what Lectures 5 and 7 built.

    from bahi.course.obs.otel import provider, instrument, SpanLog   # OpenTelemetry spans, GenAI conventions
    from bahi.course.obs import lf                                    # Langfuse: scores, datasets, prompts
    from bahi.course.obs.calibrate import confusion, report          # an LLM judge against code checks
    from bahi.course.obs.redteam import CASES, run_attack            # what promptfoo runs against Ask Rasoi
    from bahi.course.obs.judges import CassetteJudge                 # DeepEval's judge through bahi.llm (replayable)

The agent is Lecture 7's Ask Rasoi (bahi.course.l7.AskRasoi): the Experience's harness and prompt, the 15-tool
toolbox over MCP, optionally behind the trust layer. Nothing here changes how it behaves; it only watches and grades.
"""

import pathlib as _pl

_IDX = _pl.Path(__file__).parent / "_index"


def use_obs_caches():
    """Point search_policy (bahi.toolbox) at caches this package owns: read L3's and the shared ones first, write only
    to bahi/course/obs/_index. Same search, same results; nothing shared is rewritten when a new query is embedded."""
    from ...agent import retrieval as R
    from ..l3 import IDX as L3IDX, LayeredCache

    class _Three(LayeredCache):
        def __init__(self, name):
            super().__init__(_IDX / name, L3IDX / name)
            self.shared2 = R._JsonlCache(R.INDEX_DIR / name)

        def get(self, k):
            v = super().get(k)
            return v if v is not None else self.shared2.get(k)

    e, rr = R.Embedder(), R.Reranker()
    e.cache, rr.cache = _Three("embeddings.jsonl"), _Three("rerank.jsonl")
    for user in ("KJOSHI", "RMEHTA", "SKULKARNI", "APATIL", "NDESAI", "SVC_AGENT"):
        R._PS[(user, R.TODAY)] = R.PolicySearch(user, retriever=R.Retriever(user, embedder=e, reranker=rr))


def load_log(name: str):
    """An L10 experiment log: from the course folder when it is here, else from the course repository on GitHub."""
    import json
    import urllib.request
    for p in [_pl.Path(__file__).resolve().parents[3] / "lectures" / "L10-observability-evals" / "experiments" / "logs" / name,
              _pl.Path("experiments/logs") / name]:
        if p.exists():
            return json.loads(p.read_text())
    url = ("https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/"
           f"lectures/L10-observability-evals/experiments/logs/{name}")
    return json.loads(urllib.request.urlopen(url).read())
