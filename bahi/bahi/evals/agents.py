"""The agents the suite runs, as factories that build a fresh agent per conversation with traced model calls.

    GraphFactory("gemini:gemini-3.8-flash")                      Lecture 4's control graph, one model everywhere
    GraphFactory(words=PRO, route=LITE, fill=LITE)               a large model for the replies, a small one for
                                                                 routing (typed decisions) and form filling (extraction)
    LoopFactory("gemini:gemini-3.8-flash")                       Lecture 3's free tool loop with the intent tools
    NaiveFactory("gemini:gemini-3.8-flash")                      Lecture 1's naive agent: 38 raw services, service account
    PlainFactory(make_agent)                                     any make_agent(erp, user) (your module's agent)

A factory has .name, .models and .build(erp, user, tracer) -> agent with respond(text) -> str.
"""
from __future__ import annotations

from ..agent.decide import GeminiBackend
from ..agent.graph import GraphAgent
from ..agent.loop import ToolLoopAgent
from ..agent.memory import CompanyMemory
from ..agent.naive import NaiveAgent
from ..agent.tools import CORE, EXTRA, IntentTools
from ..llm import tool_schema

FLASH, PRO, LITE = "gemini:gemini-3.8-flash", "gemini:gemini-3.1-pro-preview", "gemini:gemini-3.5-flash-lite"


class TieredGraphAgent(GraphAgent):
    """GraphAgent with a model per job: words (the replies), route (typed decisions), fill (field extraction)."""

    def __init__(self, erp, user="KJOSHI", llm=None, llm_route=None, llm_fill=None, **kw):
        self.llm_fill = llm_fill
        super().__init__(erp, user, llm=llm, decide_backend=GeminiBackend(llm_route or llm), **kw)

    def _extract(self, st, text):
        if self.llm_fill is None or self.llm_fill is self.llm:
            return super()._extract(st, text)
        words, self.llm = self.llm, self.llm_fill
        try:
            return super()._extract(st, text)
        finally:
            self.llm = words


class GraphFactory:
    kind = "graph"

    def __init__(self, model: str = FLASH, cassette: str = "L6_graph", words: str | None = None, route: str | None = None,
                 fill: str | None = None, k: int = 3, cls=TieredGraphAgent, name: str | None = None):
        self.models = {"words": words or model, "route": route or model, "fill": fill or model}
        self.cassette, self.k, self.cls = cassette, k, cls
        tiers = {m.split("-", 1)[-1] for m in self.models.values()}
        self.name = name or ("graph · " + (" / ".join(f"{k}={v.split(':')[-1]}" for k, v in self.models.items())
                                           if len(tiers) > 1 else self.models["words"].split(":")[-1]))

    def build(self, erp, user, tracer):
        llms = {}
        for job, m in self.models.items():
            if m not in llms:
                llms[m] = tracer.llm(m, self.cassette)
        w, r, f = (llms[self.models[j]] for j in ("words", "route", "fill"))
        return self.cls(erp, user, llm=w, llm_route=r, llm_fill=f, k=self.k)


class PolicyTool:
    """search_policy for the free loop, over the same company memory the graph uses (as in Lecture 4)."""
    names = ["search_policy"]

    def __init__(self):
        self.mem = CompanyMemory()

    def schemas(self):
        return [tool_schema("search_policy", "Search the Purchase Policy. Returns the clauses that answer the question, "
                            "each with a citation such as 'Purchase Policy §6.2' to quote.",
                            {"question": {"type": "string"}}, ["question"])]

    def call(self, name, args):
        hits = self.mem.search(args.get("question") or args.get("query") or "", 3)
        return {"ok": True, "clauses": [{"cite": h["cite"], "text": h["text"]} for h in hits]}


class Belt:
    def __init__(self, *sets):
        self.sets = sets
        self.names = [n for s in sets for n in s.names]

    def schemas(self):
        return [x for s in self.sets for x in s.schemas()]

    def call(self, name, args):
        for s in self.sets:
            if name in s.names:
                return s.call(name, args)
        return {"ok": False, "error": f"Unknown tool {name}."}


class LoopFactory:
    kind = "loop"

    def __init__(self, model: str = FLASH, cassette: str = "L6_loop", max_steps: int = 20):
        self.models = {"words": model, "route": model, "fill": model}
        self.cassette, self.max_steps = cassette, max_steps
        self.name = "tool loop · " + model.split(":")[-1]

    def build(self, erp, user, tracer):
        tools = Belt(IntentTools(erp.session(user), CORE + EXTRA), PolicyTool())
        return ToolLoopAgent(erp, user, llm=tracer.llm(self.models["words"], self.cassette), tools=tools,
                             max_steps=self.max_steps)


class NaiveFactory:
    kind = "naive"

    def __init__(self, model: str = FLASH, cassette: str = "L6_naive"):
        self.models = {"words": model, "route": model, "fill": model}
        self.cassette = cassette
        self.name = "naive · " + model.split(":")[-1]

    def build(self, erp, user, tracer):
        return NaiveAgent(erp, user, llm=tracer.llm(self.models["words"], self.cassette))


class PlainFactory:
    """Wrap any make_agent(erp, user). Model calls are read from agent.llm.log after each turn (no node labels)."""
    kind = "plain"

    def __init__(self, make_agent, name: str = "your agent", models: dict | None = None):
        self.make_agent, self.name, self.models = make_agent, name, models or {}

    def build(self, erp, user, tracer):
        return self.make_agent(erp, user)


def factory(spec: str, cassette: str = "", model: str = FLASH):
    """'graph' | 'loop' | 'naive' | 'graph:words=..,route=..,fill=..' | 'py:package.module:make_agent'."""
    if spec.startswith("py:"):
        import importlib
        mod, fn = spec[3:].rsplit(":", 1)
        return PlainFactory(getattr(importlib.import_module(mod), fn), name=fn)
    kind, _, rest = spec.partition(":")
    if kind == "graph":
        kw = dict(x.split("=", 1) for x in rest.split(",") if "=" in x)
        return GraphFactory(model, cassette or "L6_graph", **kw)
    if kind == "loop":
        return LoopFactory(model, cassette or "L6_loop")
    if kind == "naive":
        return NaiveFactory(model, cassette or "L6_naive")
    raise ValueError(f"unknown agent {spec}")
