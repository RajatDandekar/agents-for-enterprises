"""A tracer in twenty lines, before OpenTelemetry (Lecture 6, Section 1): what a span is, built by hand.

    t = MiniTracer()
    with t.span("invoke_agent Ask Northbridge", user="ECLARKE"):
        with t.span("chat claude-sonnet-5-5", input_tokens=9120) as s:
            s["attributes"]["output_tokens"] = 64
        with t.span("execute_tool create_purchase_request", confirm=True):
            pass
    t.spans      # plain dicts: name, trace_id, span_id, parent_id, start, end, attributes, status
    t.tree()     # the same, parents first, indented

A span is a record of one piece of work: a name, when it started and ended, an id, the id of the work it belongs to
(its parent), the trace it is part of, and attributes (facts about it). A trace is every span with the same trace_id.
OpenTelemetry adds what this lacks: standard names, propagation across processes, sampling, batching, exporters.
"""
import contextlib
import contextvars
import secrets
import time

_current = contextvars.ContextVar("span", default=None)


class MiniTracer:
    def __init__(self):
        self.spans = []

    @contextlib.contextmanager
    def span(self, name, **attributes):
        parent = _current.get()
        s = {"name": name, "trace_id": parent["trace_id"] if parent else secrets.token_hex(16),
             "span_id": secrets.token_hex(8), "parent_id": parent["span_id"] if parent else None,
             "start": time.time(), "end": None, "attributes": dict(attributes), "status": "OK"}
        token = _current.set(s)
        try:
            yield s
        except Exception as e:
            s["status"] = f"ERROR: {e}"
            raise
        finally:
            s["end"] = time.time()
            _current.reset(token)
            self.spans.append(s)

    def tree(self):
        kids = {}
        for s in self.spans:
            kids.setdefault(s["parent_id"], []).append(s)
        out = []

        def walk(pid, d):
            for s in sorted(kids.get(pid, []), key=lambda x: x["start"]):
                out.append((d, s))
                walk(s["span_id"], d + 1)
        walk(None, 0)
        return "\n".join(f"{'  ' * d}{s['name']}  {(s['end'] - s['start']) * 1000:.0f} ms  {s['attributes']}" for d, s in out)
