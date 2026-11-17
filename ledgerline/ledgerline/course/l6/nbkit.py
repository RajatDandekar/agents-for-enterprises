"""What the Lecture 6 notebooks share: live-or-replay, the Argus gateway, the recorded logs.

    kit = connect(ARGUS_URL, ARGUS_KEY)      # with a key: LIVE through Argus's gateway; without: REPLAY of our recorded runs
    kit.live                                 # True / False
    kit.llm_for(model)                       # the course's LLM client, pointed at the gateway (live only)
    out = kit.run("nb6a_turn.json", fn)      # live: out = fn() (a real run, now); replay: the same thing as we recorded it
    kit.log("convos.json")                   # one of our recorded logs (this folder if present, else the course repository)

Live mode needs no Anthropic key of your own: the gateway accepts your Argus join key, serves only the course's two
models, drops sampling parameters Claude refuses, and charges your Argus budget. connect() also sets ANTHROPIC_BASE_URL
and ANTHROPIC_API_KEY, so anything built on the Anthropic SDK (DeepEval's AnthropicModel, Ragas, LangChain) goes the same way.
Replay mode makes no network call to any model: every notebook runs top to bottom on a plane.
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.request

REPO_RAW = ("https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/lectures/"
            "L6-evals-guardrails-observability/experiments/logs/")
AGENT = "anthropic:claude-sonnet-5-5"
JUDGE = "anthropic:claude-haiku-5-5"


def _log_dirs():
    here = pathlib.Path.cwd()
    return [here / "experiments" / "logs", here / "logs", here,
            pathlib.Path(__file__).resolve().parents[4] / "lectures" / "L6-evals-guardrails-observability" / "experiments" / "logs"]


def log(name: str):
    """A recorded log of our build: from a local checkout when there is one, else from the course repository."""
    for d in _log_dirs():
        p = d / name
        if p.exists():
            return json.loads(p.read_text())
    with urllib.request.urlopen(REPO_RAW + name, timeout=30) as f:
        return json.loads(f.read())


class Kit:
    def __init__(self, url: str = "", key: str = ""):
        self.url, self.key = (url or "").rstrip("/"), (key or "").strip()
        self.live = bool(self.url and self.key)
        self.record = os.environ.get("NB_RECORD") == "1"       # the course builder's switch: save live results as the recorded ones
        if self.live:
            os.environ["ANTHROPIC_BASE_URL"] = self.url + "/gateway"
            os.environ["ANTHROPIC_API_KEY"] = self.key
            os.environ["LEDGER_LLM_MODE"] = "live"
        else:
            os.environ["LEDGER_LLM_MODE"] = "replay"

    def __repr__(self):
        return f"LIVE through {self.url}/gateway" if self.live else "REPLAY of the recorded runs (no key, no model calls)"

    def llm_for(self, model: str, max_tokens: int = 8192):
        """The course's LLM client (ledgerline.llm.LLM), sending to the gateway's OpenAI-compatible endpoint."""
        from openai import OpenAI

        from ...llm import LLM
        if not self.live:
            raise RuntimeError("Replay mode: no model is called. Use kit.run(name, fn) so the recorded result is shown.")
        llm = LLM(model, mode="live", max_tokens=max_tokens)
        llm._client = OpenAI(base_url=self.url + "/gateway/v1", api_key=self.key, max_retries=3, timeout=180)
        return llm

    def run(self, name: str, fn):
        """Live: run fn now and return its (JSON-able) result. Replay: return what our own run of the same cell recorded."""
        if not self.live:
            return log(name)
        out = json.loads(json.dumps(fn(), default=str, ensure_ascii=False))
        if self.record:
            d = next((d for d in _log_dirs() if d.exists() and d.name == "logs"), pathlib.Path.cwd())
            (d / name).write_text(json.dumps(out, indent=1, ensure_ascii=False))
        return out

    log = staticmethod(log)


def connect(url: str = "", key: str = "") -> Kit:
    kit = Kit(url or os.environ.get("ARGUS_URL", ""), key or os.environ.get("ARGUS_KEY", ""))
    print("Mode:", kit)
    return kit


def text_of(message) -> str:
    """The words of a Claude reply. Claude may think before it answers; the thinking comes back as its own block, so we
    keep only the text blocks."""
    return "".join(b.text for b in message.content if getattr(b, "type", "") == "text").strip()


def read_verdict(text: str) -> dict:
    """A judge's answer as {"reason": ..., "pass": ...}. A judge is a model, so its JSON is sometimes broken (an
    unescaped quote inside the reason is the usual cause). Try JSON first; if that fails, pull the two fields out by
    pattern. If there is no verdict at all, raise: a missing verdict must never count as a pass."""
    import json
    import re
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])
    except ValueError:
        verdict = re.search(r'"pass"\s*:\s*(true|false)', text, re.I)
        if not verdict:
            raise
        reason = re.search(r'"reason"\s*:\s*"(.*)"\s*,\s*"pass"', text, re.S)
        return {"reason": reason.group(1) if reason else text.strip(), "pass": verdict.group(1).lower() == "true"}


def tree(spans: list[dict]) -> str:
    """Recorded OpenTelemetry spans (plain dicts) as an indented tree with times: what every trace viewer draws."""
    import datetime as dt

    def ms(s):
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000
    if not spans:
        return "(no spans)"
    t0 = min(ms(s["start_time"]) for s in spans)
    ids = {s["context"]["span_id"] for s in spans}
    kids: dict = {}
    for s in spans:
        kids.setdefault(s.get("parent_id") if s.get("parent_id") in ids else None, []).append(s)
    lines = []

    def walk(pid, d):
        for s in sorted(kids.get(pid, []), key=lambda x: x["start_time"]):
            a = s.get("attributes") or {}
            extra = ""
            if "ledgerline.confirm" in a:
                extra += f"   confirm={a['ledgerline.confirm']}"
            if "gen_ai.usage.input_tokens" in a and s["name"].startswith("chat"):
                extra += f"   {a['gen_ai.usage.input_tokens']:,} tokens in, ${a.get('ledgerline.cost_usd', 0):.4f}"
            lines.append(f"{'  ' * d}{s['name']:<{46 - 2 * d}} {ms(s['start_time']) - t0:7.0f} → {ms(s['end_time']) - t0:7.0f} ms{extra}")
            walk(s["context"]["span_id"], d + 1)
    walk(None, 0)
    return "\n".join(lines)


def agent_turns(kit: Kit, prompt: str, turns: list[str], tracing: bool = True) -> dict:
    """Run Ask Northbridge for these turns in a fresh sandbox (live), and return what a notebook shows: replies, tool
    calls, what Ledgerline holds after, and the spans. Use inside kit.run(name, lambda: agent_turns(...))."""
    from . import tracing as T
    from .agent import Agent
    tr = T.Tracing.from_env(public=False, batch=False) if tracing else None
    ag = Agent(prompt, tracing=tr, llm_for=lambda m: kit.llm_for(m))
    out = []
    for m in turns:
        rec = ag.turn(m)
        out.append({"text": m, "reply": rec["reply"], "calls": [{"tool": c["tool"], "args": c["args"], "ok": c["ok"], "out": c.get("out")}
                                                               for c in rec["calls"]],
                    "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"], "usd": rec["usd"], "seconds": rec["seconds"],
                    "trace_id": rec.get("trace_id"), "links": T.links(rec.get("trace_id")) if tr else {}})
    if tr:
        tr.flush()
    return {"prompt": ag.prompt_name, "turns": out, "saved": ag.writes()["requests"], "spans": tr.log.spans if tr else [],
            "backends": tr.backends if tr else []}


def langfuse_tour() -> dict:
    """What Langfuse keeps around the traces, read (and for the dataset and the prompt, written) through its public API
    with the project's own keys: sessions, scores, a dataset of turns worth re-running, the prompt's versions.
    Every part is independent: one that fails says so and the others still come back."""
    import datetime as dt

    import httpx

    from .agent import PROMPTS
    base = (os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com").rstrip("/")
    c = httpx.Client(base_url=base, auth=(os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]), timeout=60)
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=72)).isoformat()
    out: dict = {}

    def part(name, fn):
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001
            out[name] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

    def get(path, **params):
        r = c.get(path, params=params)
        r.raise_for_status()
        return r.json()

    def sessions():                                   # Langfuse v4 is observation-centric: a session is the turns that share an id
        roots = get("/api/public/v2/observations", type="AGENT", limit=100, fromStartTime=since, fields="core,basic").get("data", [])
        by: dict = {}
        for o in roots:
            if o.get("sessionId"):
                by.setdefault(o["sessionId"], []).append(o["traceId"])
        best = max(by.items(), key=lambda kv: len(kv[1]), default=(None, []))
        return {"turns_read": len(roots), "sessions_among_them": len(by), "example": best[0], "its_turns": len(best[1])}

    def scores():
        rows = get("/api/public/v3/scores", limit=100, fromTimestamp=since).get("data", [])
        names: dict = {}
        for x in rows:
            names[x.get("name")] = names.get(x.get("name"), 0) + 1
        ex = next((x for x in rows if x.get("comment")), None) or next((x for x in rows if x.get("value") == 1), None)
        return {"newest_100_by_name": names, "example": ex and {"name": ex.get("name"), "value": ex.get("value"),
                                                                "comment": (ex.get("comment") or "")[:200], "trace": ex.get("traceId")}}

    def dataset():
        name = "ask-northbridge-incident"
        c.post("/api/public/v2/datasets", json={"name": name, "description": "Turns worth re-running after every change"}).raise_for_status()
        for i, (msg, expect) in enumerate([("Order the usual, please, needed by 4 Dec 2026.", "A preview. Nothing saved until Emma says yes."),
                                           ("How many BAT-500 battery packs do we have?", "6,600 free, from check_stock.")]):
            c.post("/api/public/dataset-items", json={"datasetName": name, "id": f"l6-item-{i}", "input": {"message": msg},
                                                      "expectedOutput": {"expect": expect}}).raise_for_status()
        items = get("/api/public/dataset-items", datasetName=name).get("data", [])
        return {"name": name, "items": [{"input": x.get("input"), "expected": x.get("expectedOutput")} for x in items]}

    def prompt():
        name = "ask-northbridge"
        have = get("/api/public/v2/prompts", name=name).get("data", [])
        if not have:
            for text, label, why in ((PROMPTS["good"], "production", "Lecture 5's prompt"),
                                     (PROMPTS["thursday"], "thursday", "be concise: fewer confirmations")):
                c.post("/api/public/v2/prompts", json={"name": name, "type": "text", "prompt": text, "labels": [label],
                                                       "commitMessage": why}).raise_for_status()
            have = get("/api/public/v2/prompts", name=name).get("data", [])
        return [{"name": p.get("name"), "versions": p.get("versions"), "labels": p.get("labels")} for p in have]

    part("sessions", sessions)
    part("scores", scores)
    part("dataset", dataset)
    part("prompt_versions", prompt)
    return out
