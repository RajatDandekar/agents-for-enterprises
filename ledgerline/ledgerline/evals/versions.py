"""Lecture 6: versions of everything that can change an agent's behaviour, recorded with every run.

An agent's behaviour is a function of four things: the prompts, the tools, the models and the route. A test result
means nothing unless you know which of each it was measured on. fingerprint() hashes each one, so the regression
gate can say *what* changed between a baseline and a candidate, not only *that* the pass rate moved.
"""
from __future__ import annotations

import hashlib
import json


def h(obj) -> str:
    s = obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()[:10]


def prompts() -> dict:
    from ..agent import decide, graph, loop, naive
    from . import judge, simulator
    return {
        "graph.SAY": h(graph.SAY), "graph.EXTRACT": h([graph.EXTRACT, graph.FLAGS]),
        "decide.SPECS": h({k: [v.question, v.options, v.fields, v.guide] for k, v in decide.SPECS.items()}),
        "loop.SYSTEM": h(loop.SYSTEM), "naive.SYSTEM": h(naive.SYSTEM),
        "sim.SYSTEM": h(simulator.SIM_SYSTEM), "judge.TONE": h(judge.TONE), "judge.CHECKS": h(judge.CHECKS),
    }


def tools() -> dict:
    from ..agent import tools as T
    return {"TOOLSET_VERSION": T.TOOLSET_VERSION, "tools": {n: T.TOOLS[n].version for n in T.ALL},
            "schemas": h([T.TOOLS[n].schema() for n in T.ALL])}


def route() -> dict:
    from ..agent import route_spec as R
    return {"gates": [g.name for g in R.GATES], "spine": R.SPINE_NAMES,
            "hash": h([[g.name, g.description, g.policy] for g in R.GATES] + [[s.name, s.does] for s in R.SPINE])}


def fingerprint(fac=None, cases=None) -> dict:
    from .suite import suite_hash
    return {"models": getattr(fac, "models", {}) if fac is not None else {}, "agent": getattr(fac, "name", ""),
            "prompts": prompts(), "tools": tools(), "route": route(), "suite": suite_hash(cases)}


def diff(a: dict, b: dict, path: str = "") -> list[str]:
    """What changed between two fingerprints, as 'prompts.graph.SAY: 3f2a… -> 9c1e…' lines."""
    out = []
    if a == b:
        return out
    if not a or not b:
        return [f"{path or 'fingerprint'}: not recorded in one of the two runs"]
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        p = f"{path}.{k}" if path else k
        if x is None or y is None:
            out.append(f"{p}: not recorded in one of the two runs")
        elif isinstance(x, dict) and isinstance(y, dict):
            out += diff(x, y, p)
        elif x != y:
            out.append(f"{p}: {x} -> {y}")
    return out
