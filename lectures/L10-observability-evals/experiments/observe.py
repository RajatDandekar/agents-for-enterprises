"""Lecture 10, Part 1: Ask Rasoi traced with OpenTelemetry, sent to Langfuse and to a local Phoenix, and screenshotted.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/observe.py

What it does, in order (every output lands in logs/ or figs/):
  1. starts Phoenix locally (/opt/phx/bin/phoenix serve, no key) and checks Langfuse's keys
  2. prompt management: puts Ask Rasoi's two system prompts in Langfuse as versions of "ask-rasoi-system"
     (v-experience = the Experience's prompt, production = Lecture 7's one-line fix) and fetches "production"
  3. runs the six scenarios with the trust layer on gemini-3.8-flash, every turn one trace, every scenario one session,
     spans to three places at once: SpanLog (JSON for the plates), Langfuse (OTLP), Phoenix (OTLP)
  4. scores every session in Langfuse: the code check (erp_check), never-events, the L7 judge (words only)
  5. a dataset of the six scenarios and an experiment run per prompt version (Langfuse SDK run_experiment)
  6. reads it all back through Langfuse's API (what Langfuse stored), and the public trace URL of the gasket order
  7. screenshots: the public Langfuse trace (no login), and Phoenix's trace view, in headless Chromium
Cassette: bahi/cassettes/IND10_obs_flash.jsonl (and IND10_obs_judge.jsonl).
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

from bahi.course.l7 import AskRasoi, PROMPTS
from bahi.course.l7.evals import JUDGE, transcript
from bahi.course.obs import lf as LF, use_obs_caches
from bahi.course.obs.otel import SpanLog, instrument, provider
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS, run_scenario

import argparse  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--cassette", default="IND10_obs_flash")
ap.add_argument("--suffix", default="", help="log-name suffix for a second run, e.g. _r2")
ap.add_argument("--skip-exp", action="store_true")
ap.add_argument("--gasket-tries", type=int, default=1, help="re-run scenario 2 with fresh cassettes until it passes")
A = ap.parse_args()
HERE = pathlib.Path(__file__).parent
LOGS, FIGS = HERE / "logs", HERE.parent / "figs"
MODEL = "gemini:gemini-3.8-flash"
RUN = "l10-" + time.strftime("%m%d-%H%M")
OUT = {"run": RUN, "model": MODEL, "date": time.strftime("%Y-%m-%d %H:%M")}


def log(name, d):
    name = name.replace(".json", A.suffix + ".json")
    (LOGS / name).write_text(json.dumps(d, indent=1, default=str, ensure_ascii=False))
    print("wrote", name)


# ------------------------------------------------------------------------------------------------ 1. Phoenix
phx = subprocess.Popen(["/opt/phx/bin/phoenix", "serve"], stdout=open("/tmp/phx.log", "w"), stderr=subprocess.STDOUT,
                       env={**os.environ, "PHOENIX_WORKING_DIR": "/tmp/phx", "PHOENIX_PORT": "6006"})
for _ in range(90):
    try:
        urllib.request.urlopen("http://127.0.0.1:6006/healthz", timeout=2)
        break
    except Exception:  # noqa: BLE001
        time.sleep(2)
OUT["phoenix_up"] = phx.poll() is None
print("phoenix up:", OUT["phoenix_up"])

# One Langfuse SDK client. Its own spans (the experiment runs in step 5) go through tp_sdk, a provider the SDK exports
# itself. The six traced scenarios in step 3 use a separate provider and plain OTLP: no Langfuse SDK involved.
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
tp_sdk = TracerProvider()
lfc = LF.client(tracer_provider=tp_sdk, should_export_span=lambda span: True)
OUT["langfuse_auth"] = lfc.auth_check()

# ------------------------------------------------------------------------------------------------ 2. prompts
versions = LF.ensure_prompt_versions(lfc, [
    (PROMPTS["experience"], ["v-experience"], "The Rasoi Experience's prompt, as deployed on 28 Oct"),
    (PROMPTS["l7"], ["production"], "Lecture 7: a yes to the request covers the order made from it"),
])
tmpl, pversion = LF.system_prompt(lfc, "production")
OUT["prompt_versions"] = versions
OUT["production_version"] = pversion
OUT["production_equals_l7"] = tmpl == PROMPTS["l7"]
exp_tmpl, exp_version = LF.system_prompt(lfc, "v-experience")

# ------------------------------------------------------------------------------------------------ 3. traced runs
spans = SpanLog()
tp = provider(spans, langfuse=True, phoenix=True)
tracer = tp.get_tracer("ask-rasoi", "l10")
judge_llm = LLM("openrouter:google/gemini-3.8-flash", cassette="IND10_obs_judge")
sessions = []
use_obs_caches()
plan = [(sc, A.cassette, 1) for sc in SCENARIOS]
attempt_of = {}

while plan:
    sc, cas, attempt = plan.pop(0)
    sid = f"{RUN}-s{sc.id}" + (f"-try{attempt}" if attempt > 1 else "")
    holder = {}

    def mk(erp, user, sid=sid, sc=sc, cas=cas):
        a = AskRasoi(erp, user, llm=LLM(MODEL, cassette=cas), trust=True, prompt=tmpl)
        instrument(a, tracer, conversation_id=sid, user=user, tags=("L10", f"scenario-{sc.id}"),
                   public=(sc.id == 2), metadata={"scenario": sc.id, "lecture": "L10"}, prompt=(LF.PROMPT_NAME, pversion))
        holder["a"] = a
        return a

    t0 = time.perf_counter()
    r = run_scenario(mk, sc)
    a = holder["a"]
    tp.force_flush()
    j = judge_llm.chat([{"role": "system", "content": JUDGE}, {"role": "user", "content": transcript(r.turns)}])
    txt = (j.content or "").strip()
    try:
        jv = json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
    except Exception:  # noqa: BLE001
        jv = {"pass": None, "reason": txt[:200]}
    s = {"scenario": sc.id, "name": sc.name, "session_id": sid, "trace_ids": a.trace_ids, "passed": r.passed,
         "never_events": r.never_events, "notes": r.notes, "turns": r.turns, "tokens_in": r.tokens_in,
         "tokens_out": r.tokens_out, "model_seconds": r.seconds, "cost_inr": r.cost_inr,
         "wall_s": round(time.perf_counter() - t0, 1), "judge": jv, "judge_cost_inr": j.cost_inr,
         "trust_events": a.trust.events}
    # ---- 4. scores: on the session (a conversation-level verdict) and on its last trace (where the job ended)
    for target in ({"session_id": sid}, {"trace_id": a.trace_ids[-1]}):
        lfc.create_score(name="erp_check", value=1 if r.passed else 0, data_type="BOOLEAN",
                         comment="; ".join(r.notes + r.never_events) or "Bahi's tables match the scenario", **target)
        lfc.create_score(name="never_events", value=len(r.never_events), data_type="NUMERIC", **target)
        if jv.get("pass") is not None:
            lfc.create_score(name="judge_words_only", value=1 if jv["pass"] else 0, data_type="BOOLEAN",
                             comment=jv.get("reason"), **target)
    s["attempt"], s["cassette"] = attempt, cas
    sessions.append(s)
    a.close()
    if sc.id == 2 and not r.passed and attempt < A.gasket_tries:
        plan.insert(0, (sc, f"{A.cassette}_try{attempt + 1}", attempt + 1))
    print(f"scenario {sc.id}: passed={r.passed} turns={len(r.turns)} traces={len(a.trace_ids)} judge={jv.get('pass')}")

tp.force_flush()
lfc.flush()
log("obs_sessions.json", {**OUT, "sessions": sessions})
log("spans_all.json", {"run": RUN, "spans": spans.spans})
gasket = ([s for s in sessions if s["scenario"] == 2 and s["passed"]] or [s for s in sessions if s["scenario"] == 2])[0]
gasket_spans = [sp for sp in spans.spans if format(int(sp["context"]["trace_id"], 16), "032x") in gasket["trace_ids"]]
log("spans_gasket.json", {"run": RUN, "session_id": gasket["session_id"], "trace_ids": gasket["trace_ids"],
                          "spans": gasket_spans})

# ------------------------------------------------------------------------------------------------ 5. dataset + experiments
DS = "ask-rasoi-six"
try:
    lfc.create_dataset(name=DS, description="The six course scenarios (bahi/scenarios.py); pass = Bahi's tables, by code",
                       metadata={"source": "bahi.scenarios.SCENARIOS"})
except Exception as e:  # noqa: BLE001  exists already
    print("dataset:", repr(e)[:120])
for sc in SCENARIOS:
    lfc.create_dataset_item(dataset_name=DS, id=f"ask-rasoi-six-s{sc.id}",
                            input={"ask": sc.ask, "followups": sc.followups, "user": sc.user},
                            expected_output={"check": "bahi.scenarios.check", "scenario": sc.id, "name": sc.name},
                            metadata={"scenario": sc.id})
ds = lfc.get_dataset(DS)
OUT["dataset_items"] = len(ds.items)

exp_results = {}
from langfuse import Evaluation  # noqa: E402

for label, template, version in (() if A.skip_exp else (("v-experience", exp_tmpl, exp_version), ("production", tmpl, pversion))):
    lfx, tp_x = lfc, tp_sdk
    tracer_x = tp_sdk.get_tracer("ask-rasoi", "l10")
    rows = []

    def task(*, item, label=label, template=template, version=version, tracer_x=tracer_x, rows=rows, **kw):
        scid = (item.metadata or {}).get("scenario") if not isinstance(item, dict) else item["metadata"]["scenario"]
        sc = next(s for s in SCENARIOS if s.id == scid)
        hold = {}

        def mk(erp, user):
            a = AskRasoi(erp, user, llm=LLM(MODEL, cassette="IND10_obs_flash"), trust=True, prompt=template)
            instrument(a, tracer_x, conversation_id=f"{RUN}-exp-{label}-s{scid}", user=user, tags=("L10", "experiment"),
                       prompt=(LF.PROMPT_NAME, version))
            hold["a"] = a
            return a
        r = run_scenario(mk, sc)
        hold["a"].close()
        rows.append({"scenario": scid, "passed": r.passed, "never_events": r.never_events, "cost_inr": r.cost_inr,
                     "notes": r.notes, "replies": [t["agent"] for t in r.turns]})
        return {"passed": r.passed, "never_events": r.never_events, "last_reply": r.turns[-1]["agent"] if r.turns else ""}

    def erp_eval(*, input, output, expected_output=None, **kw):
        return Evaluation(name="erp_check", value=1.0 if output["passed"] else 0.0,
                          comment="; ".join(output["never_events"]) or None)

    try:
        res = lfx.run_experiment(name="ask-rasoi-six prompt check", run_name=f"{RUN} {label} v{version}",
                                 description=f"system prompt {LF.PROMPT_NAME} v{version} ({label})", data=ds.items,
                                 task=task, evaluators=[erp_eval], max_concurrency=3,
                                 metadata={"prompt_label": label, "prompt_version": str(version)})
        info = {"rows": sorted(rows, key=lambda r: r["scenario"]), "passed": sum(r["passed"] for r in rows),
                "n": len(rows), "dataset_run_id": getattr(res, "dataset_run_id", None),
                "dataset_run_url": getattr(res, "dataset_run_url", None)}
        try:
            info["formatted"] = res.format()[:3000]
        except Exception:  # noqa: BLE001
            pass
    except Exception as e:  # noqa: BLE001
        info = {"error": repr(e)[:600], "rows": rows}
    lfx.flush()
    tp_x.force_flush()
    exp_results[label] = info
    print("experiment", label, {k: v for k, v in info.items() if k in ("passed", "n", "error")})
if not A.skip_exp:
    log("obs_experiments.json", {**OUT, "experiments": exp_results})

# ------------------------------------------------------------------------------------------------ 6. read back from Langfuse
# (what Langfuse stored is read back by online_evals.py, through the v2 observations API)
urls = {tid: lfc.get_trace_url(trace_id=tid) for tid in gasket["trace_ids"]}
log("langfuse_urls.json", {"session_id": gasket["session_id"], "urls": urls})

# ------------------------------------------------------------------------------------------------ 7. screenshots
shots = {}
from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5, color_scheme="light")
    pg = ctx.new_page()
    for i, tid in enumerate(gasket["trace_ids"]):
        u = urls[tid]
        if not u:
            continue
        try:
            pg.goto(u, wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(25000)
            f = FIGS / f"langfuse{A.suffix}_turn{i + 1}.png"
            pg.screenshot(path=str(f))
            shots[f.name] = {"url": u, "title": pg.title(), "text": pg.inner_text("body")[:1500]}
            for label, fname in (("chat gemini-3.8-flash", "gen"), ("release_purchase_order", "release")):
                try:
                    pg.get_by_text(label).last.click(timeout=8000)
                    pg.wait_for_timeout(15000)
                    f2 = FIGS / f"langfuse{A.suffix}_turn{i + 1}_{fname}.png"
                    pg.screenshot(path=str(f2))
                    shots[f2.name] = {"url": u, "clicked": label, "text": pg.inner_text("body")[:1500]}
                except Exception as e:  # noqa: BLE001
                    shots[f"click_{i + 1}_{fname}"] = repr(e)[:200]
        except Exception as e:  # noqa: BLE001
            shots[f"langfuse_turn{i + 1}"] = {"error": repr(e)[:300]}
    try:
        projects = json.loads(urllib.request.urlopen("http://127.0.0.1:6006/v1/projects").read())
        shots["phoenix_projects"] = projects
        pid = next((x["id"] for x in projects.get("data", []) if x["name"] == "ask-rasoi"), None)
        base = f"http://127.0.0.1:6006/projects/{pid}" if pid else "http://127.0.0.1:6006/projects"
        pg.goto(base, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(5000)
        pg.screenshot(path=str(FIGS / f"phoenix{A.suffix}_traces.png"))
        shots["phoenix_traces.png"] = {"url": base, "text": pg.inner_text("body")[:1500]}
        last = gasket["trace_ids"][-1]
        for path in (f"{base}/traces/{last}", f"{base}/traces/{last}?selected"):
            try:
                pg.goto(path, wait_until="networkidle", timeout=60000)
                pg.wait_for_timeout(5000)
                pg.screenshot(path=str(FIGS / f"phoenix{A.suffix}_trace_last.png"))
                shots["phoenix_trace_turn3.png"] = {"url": path, "text": pg.inner_text("body")[:1500]}
                break
            except Exception as e:  # noqa: BLE001
                shots["phoenix_trace_err"] = repr(e)[:300]
    except Exception as e:  # noqa: BLE001
        shots["phoenix_error"] = repr(e)[:400]
    b.close()
log("screens.json", shots)
phx.terminate()
print("phoenix log tail:", open("/tmp/phx.log").read()[-1500:])
