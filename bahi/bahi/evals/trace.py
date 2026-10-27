"""Lecture 6: traces. Every model call and every Bahi service call of a conversation, in order, with tokens,
seconds and ₹. Stored locally (JSON lines); exported to Langfuse only if LANGFUSE_* keys are set.

    tracer = Tracer()
    llm = tracer.llm("gemini:gemini-3.8-flash", cassette="L6_graph")   # an LLM that records a span per call
    ... run the conversation; tracer.attach(erp) so service calls are read back from erp.calls ...
    spans = tracer.spans(erp)        # [{"seq", "kind": "llm"|"svc", "name", "node", "turn", "seconds", "tokens", "inr"}]

Seconds: a model span carries the seconds the provider took (recorded in the cassette, so a replay shows the
original run's seconds); a service span carries the sandbox's own milliseconds. The timeline lays the spans end to
end in the order they happened (the agents here call one thing at a time).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

from ..llm import LLM, Reply
from .stats import percentile

PURPOSE = {"_say": "words", "_extract": "fill", "sample": "decide", "respond": "loop"}


def _where() -> tuple[str, str]:
    """Which graph node and which purpose made this model call (read off the call stack)."""
    f = sys._getframe(2)
    node = purpose = ""
    while f is not None:
        n = f.f_code.co_name
        if not purpose and n in PURPOSE:
            purpose = PURPOSE[n]
        if not node and n.startswith("n_"):
            node = n[2:]
        f = f.f_back
    return node, purpose


class TracedLLM(LLM):
    """An LLM that reports every reply to a Tracer. role: agent (counts towards the agent's bill) | sim | judge."""

    def __init__(self, model: str, cassette: str, tracer: "Tracer", role: str = "agent", **kw):
        super().__init__(model, cassette=cassette, **kw)
        self.tracer, self.role = tracer, role

    def chat(self, messages, tools=None, response_format=None, **kw) -> Reply:
        r = super().chat(messages, tools=tools, response_format=response_format, **kw)
        node, purpose = _where()
        self.tracer._llm_span(self, r, node, purpose)
        return r


class Tracer:
    def __init__(self):
        self._spans: list[dict] = []
        self.erp = None
        self.turn = 0
        self.llms: list[TracedLLM] = []

    def llm(self, model: str, cassette: str, role: str = "agent", **kw) -> TracedLLM:
        x = TracedLLM(model, cassette, self, role, **kw)
        self.llms.append(x)
        return x

    def attach(self, erp):
        self.erp = erp

    def _llm_span(self, llm: TracedLLM, r: Reply, node: str, purpose: str):
        self._spans.append({"kind": "llm", "role": llm.role, "name": r.model.split(":", 1)[-1], "node": node,
                            "purpose": purpose, "turn": self.turn, "erp_at": len(self.erp.calls) if self.erp else 0,
                            "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                            "inr": r.cost_inr, "replayed": r.replayed,
                            "tool_calls": [t.name for t in r.tool_calls]})

    def add_foreign(self, replies: list[Reply], role: str = "agent"):
        """For an agent built outside the tracer (a plain make_agent(erp, user)): add its llm.log afterwards."""
        for r in replies:
            self._spans.append({"kind": "llm", "role": role, "name": r.model.split(":", 1)[-1], "node": "",
                                "purpose": "", "turn": self.turn, "erp_at": len(self.erp.calls) if self.erp else 0,
                                "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                                "inr": r.cost_inr, "replayed": r.replayed, "tool_calls": []})

    def spans(self, erp=None, turn_ranges: list[tuple[int, int, int]] | None = None, start: int = 0) -> list[dict]:
        """Model spans and service spans merged in order. turn_ranges: [(turn, first_call, last_call)] of the agent's
        own service calls (calls made by the harness, like Rohit's approval, are left out)."""
        erp = erp or self.erp
        svc = []
        for t, a, b in turn_ranges or []:
            for c in erp.calls[a:b]:
                svc.append({"kind": "svc", "role": "agent", "name": c.svc, "node": c.screen or "", "purpose": "",
                            "turn": t, "erp_at": c.seq - 1, "user": c.user, "rc": c.rc, "err": c.err_cd,
                            "seconds": round(c.ms / 1000, 5), "tokens_in": 0, "tokens_out": 0, "inr": 0.0,
                            "timed_out": c.timed_out})
        llm = [s for s in self._spans if s["role"] == "agent"]
        merged = sorted(llm + svc, key=lambda s: (s["erp_at"], 0 if s["kind"] == "llm" else 1))
        # stable order: model spans keep their own order among themselves
        out, at = [], 0.0
        for i, s in enumerate(merged):
            s = dict(s, seq=i, start=round(at, 4))
            at += s["seconds"] or 0
            out.append(s)
        return out

    def role_totals(self, role: str) -> dict:
        xs = [s for s in self._spans if s["role"] == role]
        return {"calls": len(xs), "tokens_in": sum(s["tokens_in"] for s in xs), "tokens_out": sum(s["tokens_out"] for s in xs),
                "seconds": round(sum(s["seconds"] for s in xs), 3), "inr": round(sum(s["inr"] for s in xs), 4)}


# ----------------------------------------------------------------------------- the local store
class TraceStore:
    """One JSON line per conversation: run id, case, agent, versions, spans, totals. Plain files, easy to diff."""

    def __init__(self, path: str | os.PathLike):
        self.path = pathlib.Path(path)

    def write(self, run: dict, records: list[dict]):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            for r in records:
                f.write(json.dumps({"run": run.get("run_id"), "agent": run.get("agent"), "versions": run.get("versions"),
                                    "case": r["id"], "passed": r["passed"], "spans": r.get("spans", []),
                                    "turns": [{"seconds": t.get("seconds"), "inr": t.get("inr")} for t in r["turns"]]},
                                   default=str) + "\n")

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.open() if l.strip()]


def turn_stats(records: list[dict]) -> dict:
    """Steps, tokens, seconds and ₹ per conversation and per turn, with p50/p95 (nearest rank)."""
    turns = [t["seconds"] for r in records for t in r["turns"] if t.get("seconds") is not None and t.get("agent_turn", True)]
    convo = [r["totals"]["seconds"] for r in records]
    steps = [r["totals"]["llm_calls"] + r["totals"]["services"] for r in records]
    return {"turns": len(turns), "turn_p50": round(percentile(turns, 50), 2), "turn_p95": round(percentile(turns, 95), 2),
            "turn_max": round(max(turns), 2) if turns else 0, "convo_p50": round(percentile(convo, 50), 2),
            "convo_p95": round(percentile(convo, 95), 2), "steps_p50": percentile(steps, 50),
            "steps_p95": percentile(steps, 95)}


# ----------------------------------------------------------------------------- optional: Langfuse
def langfuse_ready() -> tuple[bool, str]:
    keys = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY") if not os.environ.get(k)]
    if keys:
        return False, "not exported: " + ", ".join(keys) + " not set (traces stay in the local store)"
    try:
        import langfuse  # noqa: F401
    except ImportError:
        return False, "not exported: the langfuse package is not installed (pip install langfuse)"
    return True, "ready"


def export_langfuse(records: list[dict], run: dict) -> dict:
    """Send each conversation as a Langfuse trace with one span per step. Used only when LANGFUSE_* keys are set.
    Written against the Langfuse Python SDK's span API; we had no keys, so this path has NOT been run by the course team."""
    ok, why = langfuse_ready()
    if not ok:
        return {"exported": 0, "reason": why}
    from langfuse import Langfuse

    lf = Langfuse()
    n = 0
    for r in records:
        if hasattr(lf, "trace"):   # SDK v2
            tr = lf.trace(name=f"{run.get('agent')}:{r['id']}", metadata={"versions": run.get("versions"), "passed": r["passed"]})
            for s in r.get("spans", []):
                if s["kind"] == "llm":
                    tr.generation(name=s.get("purpose") or "llm", model=s["name"],
                                  usage={"input": s["tokens_in"], "output": s["tokens_out"]}, metadata=s)
                else:
                    tr.span(name=s["name"], metadata=s)
        else:                      # SDK v3 (OpenTelemetry based)
            with lf.start_as_current_span(name=f"{run.get('agent')}:{r['id']}") as root:
                root.update(metadata={"versions": run.get("versions"), "passed": r["passed"]})
                for s in r.get("spans", []):
                    with lf.start_as_current_span(name=s.get("purpose") or s["name"]) as sp:
                        sp.update(metadata=s)
        n += 1
    lf.flush()
    return {"exported": n, "reason": "ok"}
