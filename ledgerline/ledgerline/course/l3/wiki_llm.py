"""The one model the L3 wiki uses (gemini-3.8-flash through OpenRouter), recorded to cassettes, with $ per call.

    from ledgerline.course.l3.wiki_llm import WikiLLM
    llm = WikiLLM("L3_wiki_ingest")          # cassette ledgerline/cassettes/L3_wiki_ingest.jsonl (or $LEDGER_CASSETTES)
    r = llm.chat([...], response_format={"type": "json_object"})
    llm.stats()                              # calls, tokens in/out, seconds, usd

It is ledgerline.llm.LLM with two changes: the cassette is read once and kept in memory (many threads record at
once during an ingest; the base class re-reads the whole file whenever it changes), and cost is in USD at the
shared harness's price (evaluate.PRICE_USD: $0.825 / $4.125 per million, OpenRouter's list price on 3 Nov 2026), so
the wiki's numbers compare with RAG's. A probe on 3 Nov 2026 was billed $0.75 / $3.75 per million (usage.cost), about
9% less; reasoning tokens are billed as completion tokens.
"""
from __future__ import annotations

import json
import threading

from ...llm import LLM, Reply

MODEL = "openrouter:google/gemini-3.8-flash"
from .evaluate import PRICE_USD

USD_PER_M = PRICE_USD["gemini-3.8-flash"]   # the harness's price (see docstring)
BILLED_PROBE_USD_PER_M = (0.75, 3.75)        # what OpenRouter billed in our 3 Nov probe
REASONING_LOW = {"extra_body": {"reasoning": {"effort": "low"}}}


def usd(tokens_in: int, tokens_out: int) -> float:
    return (tokens_in * USD_PER_M[0] + tokens_out * USD_PER_M[1]) / 1e6


class WikiLLM(LLM):
    def __init__(self, cassette: str, mode: str | None = None, max_tokens: int = 8192, model: str = MODEL):
        super().__init__(model, cassette=cassette, mode=mode, temperature=0.0, max_tokens=max_tokens)
        self._mem: dict | None = None
        self._mlock = threading.Lock()

    def _load(self):
        if self._mem is None:
            self._mem = {}
            p = self._path()
            if p.exists():
                for line in p.open():
                    if line.strip():
                        d = json.loads(line)
                        self._mem.setdefault(d["key"], d)

    def _lookup(self, key):
        with self._mlock:
            self._load()
            return self._mem.get(key)

    def _store(self, key, r: Reply):
        d = {"key": key, "model": r.model, "content": r.content,
             "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments, "extra": t.extra}
                            for t in r.tool_calls],
             "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}
        with self._mlock:
            self._load()
            if key in self._mem:
                return
            self._mem[key] = d
            p = self._path()
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a") as f:
                f.write(json.dumps(d) + "\n")

    def stats(self, since: int = 0) -> dict:
        log = self.log[since:]
        ti, to = sum(r.tokens_in for r in log), sum(r.tokens_out for r in log)
        return {"calls": len(log), "tokens_in": ti, "tokens_out": to,
                "llm_seconds": round(sum(r.seconds for r in log), 1), "usd": round(usd(ti, to), 4),
                "replayed": sum(1 for r in log if r.replayed)}


def reply_usd(r: Reply) -> float:
    return usd(r.tokens_in, r.tokens_out)
