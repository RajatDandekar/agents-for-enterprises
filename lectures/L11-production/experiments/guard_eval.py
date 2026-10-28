"""Lecture 11 experiment 1: five input guards on the same 76 labelled messages to Ask Rasoi, plus output rails.

    tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --image guard --script lectures/L11-production/experiments/guard_eval.py

Guards (all measured here, on Modal, 2026-10-28):
  keyword      the regex list in bahi/course/production/guards.py (no model)
  llamaguard   meta-llama/llama-guard-4-12b through OpenRouter (cassette IND11_llamaguard)
  safeguard    openai/gpt-oss-safeguard-20b with Rasoi's written policy (cassette IND11_safeguard)
  nemo_input   NeMo Guardrails 0.24.1 'self check input' rail, main model google/gemini-3.5-flash-lite via OpenRouter
  nemo_topic   NeMo Guardrails dialogue rail (Colang 1.0): is it a purchasing conversation?
Output side: NeMo 'self check output' and Llama Guard (assistant turn) on 12 labelled replies.
Writes logs/guard_eval.json and bahi/course/production/fixtures/guard_runs.json (what NB11 replays).
"""
import asyncio
import json
import os
import pathlib
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"; LOGS.mkdir(exist_ok=True)
from bahi.llm import LLM
from bahi.course.production import guards as G

FIX = pathlib.Path(G.__file__).parent / "fixtures"
msgs = G.MESSAGES
out = {"date": "2026-10-28", "n": len(msgs), "versions": {}, "guards": {}, "per_message": {}}
from importlib.metadata import version
for p in ("nemoguardrails", "openai", "langchain-openai"):
    try:
        out["versions"][p] = version(p)
    except Exception:  # noqa: BLE001
        pass


def per(name, i, d):
    out["per_message"].setdefault(str(i), {})[name] = d


def finish(name, dec, lat, usd=0.0, extra=None):
    s = G.score(dec)
    s["latency_ms_p50"] = round(statistics.median(lat), 1) if lat else None
    s["latency_ms_p95"] = round(sorted(lat)[int(0.95 * (len(lat) - 1))], 1) if lat else None
    s["usd_total"] = round(usd, 6)
    s["usd_per_message"] = round(usd / len(dec), 8) if dec else None
    if extra:
        s.update(extra)
    out["guards"][name] = s
    print(f"{name:11} recall {s['recall']}  FPR {s['fpr']} ({s['false_positives']}/{s['benign_n']})  lookalike FP "
          f"{s['lookalike_fp']}  offtopic blocked {s['offtopic_blocked']}  p50 {s['latency_ms_p50']} ms  ${s['usd_total']}")
    sys.stdout.flush()


# ---------------------------------------------------------------- 1. keyword filter
dec, lat = {}, []
for i, who, cat, text in msgs:
    t0 = time.perf_counter(); r = G.keyword_guard(text); lat.append((time.perf_counter() - t0) * 1000)
    dec[i] = r["block"]; per("keyword", i, r)
finish("keyword", dec, lat)

# ---------------------------------------------------------------- 2. Llama Guard 4, 3. gpt-oss-safeguard
for name, model, fn, cas in (("llamaguard", G.LLAMA_GUARD, G.llama_guard, "IND11_llamaguard"),
                             ("safeguard", G.SAFEGUARD, G.safeguard, "IND11_safeguard")):
    def one(m):
        i, who, cat, text = m
        llm = LLM(model, cassette=cas, max_tokens=1024 if name == "safeguard" else 20)
        for attempt in range(3):
            try:
                return i, fn(text, llm)
            except Exception as e:  # noqa: BLE001
                err = str(e)[:200]; time.sleep(2 + 3 * attempt)
        return i, {"block": False, "error": err, "seconds": 0, "usd": 0}
    with ThreadPoolExecutor(8) as ex:
        res = dict(ex.map(one, msgs))
    dec = {i: r["block"] for i, r in res.items()}
    for i, r in res.items():
        per(name, i, {k: v for k, v in r.items() if k != "_t"})
    errs = sum(1 for r in res.values() if r.get("error"))
    finish(name, dec, [1000 * r["seconds"] for r in res.values() if r.get("seconds")], sum(r["usd"] for r in res.values()),
           {"errors": errs, "tokens_in_mean": round(statistics.mean(r.get("tokens_in", 0) for r in res.values()), 1)})

# ---------------------------------------------------------------- 4. NeMo Guardrails: input and output rails
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")
from nemoguardrails import LLMRails, RailsConfig

cfg = RailsConfig.from_content(yaml_content=G.NEMO_CONFIG_YML + "\n" + G.NEMO_PROMPTS_YML)
rails = LLMRails(cfg)


def blocked_by(res):
    log = getattr(res, "log", None)
    acts = getattr(log, "activated_rails", None) or []
    stops = [a.name for a in acts if getattr(a, "stop", False)]
    return bool(stops), stops, acts


def llm_usage(res):
    calls = getattr(getattr(res, "log", None), "llm_calls", None) or []
    tin = sum((c.prompt_tokens or 0) for c in calls)
    tout = sum((c.completion_tokens or 0) for c in calls)
    return len(calls), tin, tout


async def nemo_input():
    dec, lat, usd = {}, [], 0.0
    for i, who, cat, text in msgs:
        t0 = time.perf_counter()
        try:
            res = await rails.generate_async(messages=[{"role": "user", "content": text}],
                                             options={"rails": ["input"], "log": {"activated_rails": True, "llm_calls": True}})
            b, stops, _ = blocked_by(res)
            n, tin, tout = llm_usage(res)
            ms = (time.perf_counter() - t0) * 1000
            resp = res.response[-1]["content"] if isinstance(res.response, list) and res.response else str(res.response)
            d = {"block": b, "stops": stops, "llm_calls": n, "tokens_in": tin, "tokens_out": tout, "ms": round(ms, 1),
                 "response": resp[:160]}
        except Exception as e:  # noqa: BLE001
            ms = (time.perf_counter() - t0) * 1000
            d = {"block": False, "error": f"{type(e).__name__}: {str(e)[:200]}", "ms": round(ms, 1), "tokens_in": 0, "tokens_out": 0}
        usd += G.usd("openrouter:google/gemini-3.5-flash-lite", d["tokens_in"], d["tokens_out"])
        dec[i] = d["block"]; lat.append(ms); per("nemo_input", i, d)
    finish("nemo_input", dec, lat, usd, {"errors": sum(1 for i in dec if out["per_message"][str(i)]["nemo_input"].get("error"))})


async def nemo_output():
    rows = []
    for j, label, reply in G.OUTPUT_CASES:
        t0 = time.perf_counter()
        try:
            res = await rails.generate_async(messages=[{"role": "user", "content": "Help me with my order."},
                                                       {"role": "assistant", "content": reply}],
                                             options={"rails": ["output"], "log": {"activated_rails": True, "llm_calls": True}})
            b, stops, _ = blocked_by(res)
            n, tin, tout = llm_usage(res)
            rows.append({"id": j, "label": label, "nemo_block": b, "stops": stops, "ms": round((time.perf_counter() - t0) * 1000, 1),
                         "tokens_in": tin, "tokens_out": tout})
        except Exception as e:  # noqa: BLE001
            rows.append({"id": j, "label": label, "nemo_block": None, "error": f"{type(e).__name__}: {str(e)[:200]}"})
    return rows


asyncio.run(nemo_input())
orows = asyncio.run(nemo_output())
lg = LLM(G.LLAMA_GUARD, cassette="IND11_llamaguard", max_tokens=20)
for r, (j, label, reply) in zip(orows, G.OUTPUT_CASES):
    g = G.llama_guard("Help me with my order.", lg, reply=reply)
    r["llamaguard_block"], r["llamaguard_raw"] = g["block"], g["raw"]
    r["reply"] = reply
out["output_rails"] = {"rows": orows}
for k in ("nemo_block", "llamaguard_block"):
    ok = [r for r in orows if r.get(k) is not None]
    out["output_rails"][k] = {"caught": sum(1 for r in ok if r["label"] == "block" and r[k]),
                              "bad_n": sum(1 for r in ok if r["label"] == "block"),
                              "false_positives": sum(1 for r in ok if r["label"] == "allow" and r[k]),
                              "good_n": sum(1 for r in ok if r["label"] == "allow")}
print("output rails:", json.dumps({k: v for k, v in out["output_rails"].items() if k != "rows"}))

# ---------------------------------------------------------------- 5. NeMo dialogue rail (topical)
tcfg = RailsConfig.from_content(yaml_content=G.NEMO_TOPICAL_YML, colang_content=G.NEMO_TOPICAL_CO)
trails = LLMRails(tcfg)


async def topical():
    dec, lat, usd = {}, [], 0.0
    for i, who, cat, text in msgs:
        t0 = time.perf_counter()
        try:
            res = await trails.generate_async(messages=[{"role": "user", "content": text}],
                                              options={"log": {"activated_rails": True, "llm_calls": True}})
            resp = res.response[-1]["content"] if isinstance(res.response, list) and res.response else str(res.response)
            n, tin, tout = llm_usage(res)
            refused = "outside what I do" in resp
            d = {"block": refused, "handover": resp.strip() == "HANDOVER", "response": resp[:160], "llm_calls": n,
                 "tokens_in": tin, "tokens_out": tout}
        except Exception as e:  # noqa: BLE001
            d = {"block": False, "error": f"{type(e).__name__}: {str(e)[:200]}", "tokens_in": 0, "tokens_out": 0}
        ms = (time.perf_counter() - t0) * 1000
        d["ms"] = round(ms, 1)
        usd += G.usd("openrouter:google/gemini-3.5-flash-lite", d["tokens_in"], d["tokens_out"])
        dec[i] = d["block"]; lat.append(ms); per("nemo_topic", i, d)
    finish("nemo_topic", dec, lat, usd, {"handover": sum(1 for i in dec if out["per_message"][str(i)]["nemo_topic"].get("handover"))})


asyncio.run(topical())

# ---------------------------------------------------------------- layering: decisions combined after the fact
def comb(*names):
    return {i: any(out["per_message"][str(i)][n]["block"] for n in names) for i, *_ in msgs}


for combo in (("llamaguard", "safeguard"), ("llamaguard", "nemo_input"), ("keyword", "llamaguard")):
    out["guards"]["+".join(combo)] = G.score(comb(*combo))
out["messages"] = [{"id": i, "who": w, "cat": c, "text": t} for i, w, c, t in msgs]
(LOGS / "guard_eval.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
(FIX / "guard_runs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("wrote", LOGS / "guard_eval.json")
