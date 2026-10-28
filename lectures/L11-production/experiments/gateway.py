"""Lecture 11 experiment 5: a model gateway in front of Ask Rasoi, the LiteLLM proxy (litellm 1.106.5).

    L11_IMAGE=data tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/gateway.py

Inside one Modal container: Postgres 15 (keys and spend) and `litellm --config` on localhost:4000.
Three model names, all through OpenRouter: rasoi-default (gemini-3.8-flash), rasoi-cheap (gemini-3.5-flash-lite) and
rasoi-primary (a model id that does not exist, to force the fallback to rasoi-cheap).
Two teams with budgets (purchase, stores); virtual keys for Kavita (purchase, tiny budget), Neha (stores, only
rasoi-cheap) and a rate-limited key. We measure: which request the budget stops, the fallback, model access,
the rate limit, and spend per key and team as the proxy records it.
The master key is a throwaway value for this local drill. Writes logs/gateway.json and fixtures/gateway_runs.json.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import httpx

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"; LOGS.mkdir(exist_ok=True)
import bahi.course.production as P

FIX = pathlib.Path(P.__file__).parent / "fixtures"
MASTER = "sk-l11-local-drill-" + os.urandom(6).hex()
H = {"Authorization": f"Bearer {MASTER}"}
URL = "http://127.0.0.1:4000"
out = {"date": "2026-10-28"}


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


ver = sh("ls /usr/lib/postgresql").split()[-1]
sh(f"pg_ctlcluster {ver} main start")
sh("su postgres -c \"psql -c \\\"ALTER USER postgres PASSWORD 'drill'\\\"\"")
sh("su postgres -c \"psql -c 'CREATE DATABASE litellm'\"")

CONFIG = """model_list:
  - model_name: rasoi-default
    litellm_params:
      model: openrouter/google/gemini-3.8-flash
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: rasoi-cheap
    litellm_params:
      model: openrouter/google/gemini-3.5-flash-lite
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: rasoi-primary
    litellm_params:
      model: openrouter/google/gemini-0-no-such-model
      api_key: os.environ/OPENROUTER_API_KEY
router_settings:
  num_retries: 0
  fallbacks:
    - rasoi-primary: ["rasoi-cheap"]
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL
  proxy_batch_write_at: 2
litellm_settings:
  drop_params: true
"""
open("/tmp/litellm.yaml", "w").write(CONFIG)
out["config"] = CONFIG
env = {**os.environ, "LITELLM_MASTER_KEY": MASTER, "DATABASE_URL": "postgresql://postgres:drill@localhost:5432/litellm",
       "STORE_MODEL_IN_DB": "False", "LITELLM_LOG": "ERROR"}
log = open("/tmp/litellm.log", "w")
proxy = subprocess.Popen(["litellm", "--config", "/tmp/litellm.yaml", "--port", "4000", "--host", "127.0.0.1"],
                         stdout=log, stderr=subprocess.STDOUT, env=env)
t0 = time.time()
while time.time() - t0 < 300:
    if proxy.poll() is not None:
        raise SystemExit("litellm proxy exited: " + open("/tmp/litellm.log").read()[-1500:].replace(MASTER, "<master>"))
    try:
        if httpx.get(f"{URL}/health/liveliness", timeout=2).status_code == 200:
            break
    except Exception:  # noqa: BLE001
        pass
    time.sleep(2)
out["proxy_start_seconds"] = round(time.time() - t0, 1)
print("proxy up after", out["proxy_start_seconds"], "s", flush=True)
c = httpx.Client(base_url=URL, timeout=120)


def post(path, body, key=None):
    r = c.post(path, json=body, headers={"Authorization": f"Bearer {key}"} if key else H)
    try:
        return r.status_code, r.json(), r.headers
    except Exception:  # noqa: BLE001
        return r.status_code, {"text": r.text[:300]}, r.headers


try:
    # ---------------------------------------------------------------- teams and virtual keys
    _, purchase, _ = post("/team/new", {"team_alias": "purchase", "max_budget": 0.02})
    _, stores, _ = post("/team/new", {"team_alias": "stores", "max_budget": 0.01})
    _, kk, _ = post("/key/generate", {"team_id": purchase["team_id"], "key_alias": "ask-rasoi-kavita", "max_budget": 0.002,
                                      "models": ["rasoi-default", "rasoi-cheap", "rasoi-primary"], "user_id": "KJOSHI"})
    _, nk, _ = post("/key/generate", {"team_id": stores["team_id"], "key_alias": "stores-neha", "models": ["rasoi-cheap"],
                                      "user_id": "NDESAI"})
    _, rk, _ = post("/key/generate", {"team_id": purchase["team_id"], "key_alias": "notebook-rate-limited", "rpm_limit": 3,
                                      "models": ["rasoi-cheap"]})
    KAV, NEHA, RL = kk["key"], nk["key"], rk["key"]
    out["setup"] = {"teams": {"purchase": {"max_budget": 0.02}, "stores": {"max_budget": 0.01}},
                    "keys": {"ask-rasoi-kavita": {"team": "purchase", "max_budget": 0.002, "models": kk.get("models")},
                             "stores-neha": {"team": "stores", "models": nk.get("models")},
                             "notebook-rate-limited": {"team": "purchase", "rpm_limit": 3}}}

    QS = ["How many days of cover do 54,000 gaskets give at 6,000 a day? Answer in one line.",
          "Explain in three short lines why a purchase request above ₹2,50,000 needs Rohit's approval.",
          "Write a two-line reminder to Rohit Mehta about PR/2026/04417 for 20,000 gaskets.",
          "In two lines: what is the difference between a purchase request and a purchase order?"]

    def chat(key, model, q, max_tokens=200):
        t = time.perf_counter()
        code, body, hd = post("/chat/completions", {"model": model, "messages": [{"role": "user", "content": q}],
                                                    "max_tokens": max_tokens, "temperature": 0}, key)
        row = {"status": code, "ms": round((time.perf_counter() - t) * 1000), "model_asked": model,
               "served_by": body.get("model") if code == 200 else None,
               "cost_usd": float(hd.get("x-litellm-response-cost") or 0) if code == 200 else 0.0,
               "tokens_in": (body.get("usage") or {}).get("prompt_tokens") if code == 200 else None,
               "tokens_out": (body.get("usage") or {}).get("completion_tokens") if code == 200 else None,
               "fallbacks_header": hd.get("x-litellm-attempted-fallbacks"),
               "error": None if code == 200 else json.dumps(body)[:260]}
        return row

    # ---------------------------------------------------------------- 1. the budget stops Kavita's key
    budget = []
    for i in range(40):
        r = chat(KAV, "rasoi-default", QS[i % len(QS)])
        r["n"] = i + 1
        budget.append(r)
        print("budget", r["n"], r["status"], r["cost_usd"], (r["error"] or "")[:120], flush=True)
        if r["status"] != 200:
            break
        time.sleep(1.0)
    out["budget"] = {"key_budget_usd": 0.002, "requests": budget,
                     "first_refused": next((r["n"] for r in budget if r["status"] != 200), None),
                     "spent_before_refusal_usd": round(sum(r["cost_usd"] for r in budget), 6)}

    # ---------------------------------------------------------------- 2. fallback, 3. model access, 4. rate limit
    _, k2, _ = post("/key/generate", {"team_id": purchase["team_id"], "key_alias": "ask-rasoi-fallback-test",
                                      "models": ["rasoi-primary", "rasoi-cheap"]})
    out["fallback"] = [chat(k2["key"], "rasoi-primary", QS[0]) for _ in range(2)]
    out["model_access"] = chat(NEHA, "rasoi-default", QS[0])
    out["model_access_ok"] = chat(NEHA, "rasoi-cheap", QS[0])
    out["rate_limit"] = [chat(RL, "rasoi-cheap", QS[0], 30) for _ in range(5)]
    for r in out["rate_limit"]:
        print("rate", r["status"], (r["error"] or "")[:100], flush=True)
    for i in range(6):
        chat(NEHA, "rasoi-cheap", QS[i % len(QS)])

    # ---------------------------------------------------------------- 5. spend as the proxy records it
    time.sleep(8)
    def info(path, params):
        r = c.get(path, params=params, headers=H)
        return r.json() if r.status_code == 200 else {"status": r.status_code, "text": r.text[:200]}
    ti = {n: info("/team/info", {"team_id": t["team_id"]}) for n, t in (("purchase", purchase), ("stores", stores))}
    out["team_spend"] = {n: {"spend": (d.get("team_info") or {}).get("spend"), "max_budget": (d.get("team_info") or {}).get("max_budget")}
                         for n, d in ti.items()}
    ki = {n: info("/key/info", {"key": k}) for n, k in (("ask-rasoi-kavita", KAV), ("stores-neha", NEHA), ("notebook-rate-limited", RL))}
    out["key_spend"] = {n: {"spend": (d.get("info") or {}).get("spend"), "max_budget": (d.get("info") or {}).get("max_budget")}
                        for n, d in ki.items()}
    logs = c.get("/spend/logs", headers=H)
    rows = logs.json() if logs.status_code == 200 else []
    out["spend_logs"] = {"n": len(rows) if isinstance(rows, list) else None,
                         "sample": [{k: r.get(k) for k in ("model", "model_group", "spend", "total_tokens", "team_id", "user", "status")}
                                    for r in (rows[:8] if isinstance(rows, list) else [])]}
    print("teams", out["team_spend"], "keys", out["key_spend"], flush=True)
finally:
    proxy.terminate()
    out["proxy_log_tail"] = open("/tmp/litellm.log").read()[-3000:].replace(MASTER, "<master>")
    from importlib.metadata import version
    out["litellm_version"] = version("litellm")
    txt = json.dumps(out, indent=1, ensure_ascii=False, default=str)
    txt = txt.replace(MASTER, "<master>")
    for k in ("KAV", "NEHA", "RL"):
        if k in globals():
            txt = txt.replace(globals()[k], f"<{k.lower()}-key>")
    if "k2" in globals() and isinstance(globals()["k2"], dict) and globals()["k2"].get("key"):
        txt = txt.replace(globals()["k2"]["key"], "<fallback-test-key>")
    (LOGS / "gateway.json").write_text(txt)
    (FIX / "gateway_runs.json").write_text(txt)
    print("wrote gateway.json")
