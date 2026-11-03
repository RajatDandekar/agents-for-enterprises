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
    def __init__(self, cassette: str, mode: str | None = None, max_tokens: int = 8192, model: str = MODEL,
                 read_also: list[str] | None = None):
        super().__init__(model, cassette=cassette, mode=mode, temperature=0.0, max_tokens=max_tokens)
        self.read_also = read_also or []   # other cassettes to replay from (new records go to `cassette` only)
        self._mem: dict | None = None
        self._mlock = threading.Lock()

    def _load(self):
        if self._mem is None:
            self._mem = {}
            for p in [self._path()] + [self._path().with_name(f"{c}.jsonl") for c in self.read_also]:
                if p.exists():
                    for line in p.open():
                        if line.strip():
                            d = json.loads(line)
                            self._mem.setdefault(d["key"], d)

    def _has_key(self) -> bool:
        import os

        if provider() == "google-direct":  # live calls go to Google: its key counts, not OpenRouter's
            return bool(os.environ.get("GEMINI_API_KEY"))
        return super()._has_key()

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


GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"


def provider() -> str:
    """Where live calls go. 'openrouter' (default, google/gemini-3.8-flash) or 'google-direct' (the same model through
    Google's OpenAI-compatible endpoint, key GEMINI_API_KEY). The cassette key (a hash of the request, including the
    model string 'openrouter:google/gemini-3.8-flash') does not change, so calls recorded through either provider
    replay the same; each record's "model" field says which provider served it."""
    import os

    return os.environ.get("LEDGER_WIKI_PROVIDER", "openrouter")


def _google_live(self, messages, tools, response_format, **kw):
    import os
    import time as _t

    from openai import OpenAI

    from ...llm import ToolCall

    if getattr(self, "_gclient", None) is None:
        self._gclient = OpenAI(base_url=GOOGLE_BASE, api_key=os.environ["GEMINI_API_KEY"], max_retries=4, timeout=180)
    model_id = self.model_id.split("/")[-1]
    args = {"model": model_id, "messages": messages, "temperature": self.temperature, "max_tokens": self.max_tokens}
    eb = dict(kw.pop("extra_body", None) or {})
    if isinstance(eb.get("reasoning"), dict):  # OpenRouter's {"reasoning": {"effort": "low"}} -> Google's reasoning_effort
        eb["reasoning_effort"] = eb.pop("reasoning").get("effort", "low")
    args.update(kw)
    if eb:
        args["extra_body"] = eb
    if tools:
        args["tools"] = tools
    if response_format:
        args["response_format"] = response_format
    t0 = _t.perf_counter()
    try:
        resp = self._gclient.chat.completions.create(**args)
    except Exception as e:
        body = getattr(getattr(e, "response", None), "text", "")
        raise RuntimeError(f"google-direct:{model_id}: {e} {body[:400]}") from e
    secs = _t.perf_counter() - t0
    msg = resp.choices[0].message
    calls = []
    for i, tc in enumerate(msg.tool_calls or []):
        try:
            a = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            a = {"_unparsed": tc.function.arguments}
        calls.append(ToolCall(tc.id or f"call_{i}", tc.function.name, a, (tc.model_extra or {}).get("extra_content")))
    u = resp.usage
    ti = getattr(u, "prompt_tokens", 0) or 0
    to = getattr(u, "completion_tokens", 0) or 0
    tot = getattr(u, "total_tokens", 0) or 0
    to = max(to, tot - ti)  # thinking tokens are billed as output; Google reports them only in total_tokens
    return Reply(msg.content, calls, ti, to, round(secs, 3), f"google-direct:{model_id}")


def _install_backoff():
    """Rate limits (OpenRouter: 300 requests a minute across everyone; Google: per-key quotas) are retried with
    backoff, and the waiting is kept apart (WikiLLM.backoff_seconds) so latency excludes queueing."""
    import random
    import time as _t

    base_live = WikiLLM._live

    def _live(self, messages, tools, response_format, **kw):
        for attempt in range(10):
            try:
                if provider() == "google-direct":
                    return _google_live(self, messages, tools, response_format, **kw)
                return base_live(self, messages, tools, response_format, **kw)
            except RuntimeError as e:
                txt = str(e)
                if not ("429" in txt or "Rate limit" in txt or "RESOURCE_EXHAUSTED" in txt or "503" in txt) \
                        or attempt == 9:
                    raise
                wait = min(60.0, 4.0 * 2 ** attempt) * (0.75 + 0.5 * random.random())
                with self._mlock:
                    self.backoff_seconds = getattr(self, "backoff_seconds", 0.0) + wait
                    self.backoffs = getattr(self, "backoffs", 0) + 1
                _t.sleep(wait)

    WikiLLM._live = _live


_install_backoff()


def live_stats(llm) -> dict:
    """Calls this process actually sent (not replayed), by provider, with $ at the harness price."""
    out = {}
    for r in llm.log:
        if r.replayed:
            continue
        prov = r.model.split(":", 1)[0]
        d = out.setdefault(prov, {"calls": 0, "tokens_in": 0, "tokens_out": 0, "usd": 0.0})
        d["calls"] += 1
        d["tokens_in"] += r.tokens_in
        d["tokens_out"] += r.tokens_out
        d["usd"] = round(d["usd"] + usd(r.tokens_in, r.tokens_out), 5)
    return out
