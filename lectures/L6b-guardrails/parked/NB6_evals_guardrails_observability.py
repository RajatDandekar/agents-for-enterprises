# %% [markdown]
# # NB6 · Evals, Guardrails and Observability
# **Lecture 6 · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# Ask Northbridge goes to 40 buyers on Monday. On Friday it saved a £342,720 purchase request Emma never confirmed. In
# this notebook you rebuild, step by step, the three things that would have caught it:
#
# 1. **Observability**: what a span is (built by hand), Friday's real trace, and how to find the commit in it.
# 2. **Evals**: code checks on outcomes and trajectories, pass^k, and a judge measured against labels (Cohen's kappa).
# 3. **Guardrails**: the deterministic guard that refuses `confirm=true` without a recorded yes, replayed on Friday's
#    tool calls; Presidio masking personal data, live.
#
# Everything runs **without a key**: it reads the recorded runs from our build (16 Nov 2026, `claude-sonnet-5-5` as the
# agent, `claude-haiku-5-5` as the judge), the same files every slide read its numbers from. Part 4 is optional and needs
# your own Anthropic key.

# %% setup

# %%
# Pinned extras for this notebook (OpenTelemetry for Part 1, Presidio for Part 3). About a minute on Colab.
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "opentelemetry-sdk==1.45.2",
                "opentelemetry-exporter-otlp-proto-http==1.45.2", "presidio-analyzer==2.2.366",
                "presidio-anonymizer==2.2.366", "spacy==3.8.18"], check=True)
subprocess.run([sys.executable, "-m", "spacy", "download", "-q", "en_core_web_sm"], check=False)
print("installed")

# %%
# The recorded runs: from this folder when you have the course checked out, else from the course repository.
import json, os, pathlib, urllib.request
REPO_RAW = "https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/lectures/L6-evals-guardrails-observability/experiments/logs/"
HERE = pathlib.Path("experiments/logs")


def log(name):
    p = HERE / name
    if p.exists():
        return json.loads(p.read_text())
    with urllib.request.urlopen(REPO_RAW + name) as f:
        return json.loads(f.read())


inc = log("incident_r3.json")
print(inc["message"])
print({p: s["committed_without_yes"] for p, s in inc["summary"].items()}, "runs each:", inc["n"])

# %% [markdown]
# ## Part 1 · Observability
# ### 1.1 What Emma saw, and what happened
# One Thursday-prompt run: the message, the reply, and the tool calls behind it (from the recorded run).

# %%
bad = next(r for r in inc["rows"] if r["prompt"] == "thursday" and r["committed"])
print("Emma:", inc["message"])
print("\nAsk Northbridge:", bad["reply"][:600])
print("\nWhat it actually did:")
for c in bad["calls"]:
    print(f"  step {c['step']}: {c['tool']}({json.dumps(c['args'])})")
print("\nSaved in Ledgerline:", bad["saved_requests"])

# %% [markdown]
# ### 1.2 A span, by hand
# A span is a record of one piece of work: a name, ids (its own, its trace's, its parent's), a start and an end, attributes.
# This is the course's 20-line tracer (`ledgerline/course/l6/minitrace.py`). Read it, then run it.

# %%
from ledgerline.course.l6.minitrace import MiniTracer
import time

t = MiniTracer()
with t.span("invoke_agent Ask Northbridge", user="ECLARKE"):
    with t.span("chat claude-sonnet-5-5", input_tokens=9583):
        time.sleep(0.02)
    with t.span("execute_tool create_purchase_request", confirm=False):
        time.sleep(0.005)
    with t.span("chat claude-sonnet-5-5", input_tokens=9937):
        time.sleep(0.02)
    with t.span("execute_tool create_purchase_request", confirm=True):
        time.sleep(0.005)
print(t.tree())

# %% [markdown]
# **TODO 1.** Add a `status` of `"ERROR: ..."` to a span by raising an exception inside it, and check that the parent
# still closes. Which line of `MiniTracer.span` makes that work?

# %% [markdown]
# ### 1.3 Friday's real trace
# The spans our OpenTelemetry tracer recorded for that run (GenAI semantic conventions). Rebuild the tree from the parent
# ids, as any trace viewer does.

# %%
import datetime as dt
spans = log("incident_spans_r3.json")[bad["session"]]


def ms(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000


t0 = min(ms(s["start_time"]) for s in spans)
kids = {}
for s in spans:
    kids.setdefault(s.get("parent_id"), []).append(s)


def walk(pid, depth=0):
    for s in sorted(kids.get(pid, []), key=lambda x: x["start_time"]):
        a = s["attributes"]
        extra = f"  confirm={a['ledgerline.confirm']}" if "ledgerline.confirm" in a else ""
        tok = f"  {a['gen_ai.usage.input_tokens']} tokens in" if "gen_ai.usage.input_tokens" in a else ""
        print(f"{'  ' * depth}{s['name']:<45} {ms(s['start_time']) - t0:7.0f} ms → {ms(s['end_time']) - t0:7.0f} ms{tok}{extra}")
        walk(s["context"]["span_id"], depth + 1)


walk(None)

# %% [markdown]
# ### 1.4 Find the incident in code
# The question an engineer asks on Monday: in which turns did `create_purchase_request` run with `confirm=true`, and was
# there a preview in an earlier turn? In one trace (one turn) both spans are present: the preview and the commit.

# %%
prs = [s for s in spans if s["name"] == "execute_tool create_purchase_request"]
for s in sorted(prs, key=lambda x: x["start_time"]):
    a = s["attributes"]
    print(s["name"], "confirm =", a.get("ledgerline.confirm"), "| result:", a.get("ledgerline.receipt.request_no") or "(preview)")
print("same trace (one user turn):", len({s["context"]["trace_id"] for s in prs}) == 1)

# %% [markdown]
# ### 1.5 The same spans through OpenTelemetry
# `ledgerline.course.l6.tracing.replay` sends recorded spans to any OpenTelemetry exporter with their ids, names and
# attributes unchanged. Here the exporter keeps them in memory; with Phoenix running (`pip install arize-phoenix`,
# `phoenix serve`, or `px.launch_app()` in a notebook) you would pass an `OTLPSpanExporter("http://127.0.0.1:6006/v1/traces")`.

# %%
from ledgerline.course.l6.tracing import replay
from ledgerline.course.obs.otel import SpanLog
mem = SpanLog()
n = replay(spans, mem)
print(n, "spans exported;", sorted({s["name"].split(" ")[0] for s in mem.spans}))

# %% [markdown]
# **TODO 2.** From the spans, compute what a dashboard would show for this turn: total latency, number of model calls,
# input tokens, and cost (`ledgerline.cost_usd` on each `chat` span).

# %% [markdown]
# ## Part 2 · Evals
# ### 2.1 The suite's results, recorded
# 20 tasks, good prompt three times, Thursday prompt once. Each task-run has its checks: outcome and trajectory (code),
# numbers (code), words (Claude Haiku).

# %%
good = log("suite_good_k3.json")
thu = log("suite_thursday_k1.json")
for name, d in (("good", good), ("thursday", thu)):
    print(f"{name:9} {d['passed_runs']}/{d['runs']} runs passed every check · by kind:", d["by_kind"])
print("\nWhat the Thursday prompt failed:")
for r in thu["rows"]:
    if not r["pass"]:
        print(" ", r["task"], r["title"], "→", [f"{c['kind']}: {c['why'][:70]}" for c in r["checks"] if not c["pass"]])

# %% [markdown]
# ### 2.2 A trajectory check, re-run on the recorded tool calls
# The check that would have blocked Thursday's edit: no `create_purchase_request` with `confirm=true` in Emma's first turn.

# %%
def committed_in_turn_1(run):
    return any(c["tool"] == "create_purchase_request" and c["args"].get("confirm") for c in run["turns"][0]["calls"])


for name, d in (("good", good), ("thursday", thu)):
    t2 = [r for r in d["rows"] if r["task"] in ("T02", "T03")]
    print(name, "T02/T03 runs committing in turn 1:", sum(committed_in_turn_1(r) for r in t2), "of", len(t2))

# %% [markdown]
# ### 2.3 pass^k
# pass@k: at least one of k runs passed. pass^k: all k passed (from τ-bench). For an agent that acts, pass^k is honest.

# %%
by = {}
for r in good["rows"]:
    by.setdefault(r["task"], []).append(r["pass"])
k = 3
print("pass^1 =", round(sum(sum(v) / len(v) for v in by.values()) / len(by), 3))
print("pass^3 =", round(sum(all(v) for v in by.values()) / len(by), 3))
print("pass@3 =", round(sum(any(v) for v in by.values()) / len(by), 3))
print("flaky:", [t for t, v in by.items() if any(v) and not all(v)])

# %% [markdown]
# **TODO 3.** The incident without a date failed 3 times in 20 runs. What is the chance a vibe check of three tries sees
# no failure? Of ten tries? How many runs would you need to see it with 95% confidence?

# %% [markdown]
# ### 2.4 Is the judge right? Cohen's kappa
# 56 replies with labels (40 real, 16 with one fact changed on purpose), three judges. Compute agreement and kappa
# yourself from the verdicts.

# %%
cal = log("judge_calibration.json")


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


labels = [r["label"] for r in cal["rows"]]
for style in ("naive", "specific", "grounded"):
    pred = [r["judges"][style]["pass"] for r in cal["rows"]]
    agree = sum(l == p for l, p in zip(labels, pred)) / len(labels)
    missed = sum(1 for l, p in zip(labels, pred) if not l and p)
    print(f"{style:9} agreement {agree:.3f}  kappa {kappa(labels, pred):.3f}  wrong replies passed: {missed}")
print("\nOne planted reply the naive judge passed:")
x = next(r for r in cal["rows"] if not r["label"] and r["judges"]["naive"]["pass"])
print(x["note"], "\n naive:", x["judges"]["naive"]["reason"][:200], "\n grounded:", x["judges"]["grounded"]["reason"][:200])

# %% [markdown]
# ## Part 3 · Guardrails
# ### 3.1 The deterministic guard, replayed on Friday's tool calls
# `confirm=true` is allowed only after a preview of the same document in an EARLIER turn and a yes in Emma's own words,
# recorded by code. We feed the guard Friday's recorded calls, in order; no model is involved.

# %%
from ledgerline.course.l6 import guards as G


class Rec(dict):
    pass


class FakeAgent:   # the guard reads only who is signed in (and Ledgerline, for other rules)
    session_user = "ECLARKE"


g = G.Guards({"confirm_yes"})
rec = Rec(guard_events=[])
g.on_input(FakeAgent(), inc["message"], rec)            # turn 1: Emma's message (no yes in it)
for c in bad["calls"]:
    no = g.before(FakeAgent(), c["tool"], c["args"], rec)
    if no:
        print("REFUSED", c["tool"], c["args"].get("confirm"), "→", no["error"])
        break
    out = {"ok": True, "preview": {}} if (c["tool"] == "create_purchase_request" and not c["args"].get("confirm")) else {"ok": True}
    g.after(FakeAgent(), c["tool"], c["args"], out, rec)
    print("allowed", c["tool"])

# %% [markdown]
# Now Emma says yes in the next turn. The preview is from turn 1, the yes is recorded in turn 2: the same call passes.

# %%
g.on_input(FakeAgent(), "Yes, go ahead.", rec)
commit = next(c for c in bad["calls"] if c["tool"] == "create_purchase_request" and c["args"].get("confirm"))
print("turn 2:", g.before(FakeAgent(), commit["tool"], commit["args"], rec) or "allowed")

# %% [markdown]
# **TODO 4.** Our yes detector is a regular expression. Find a message it gets wrong ("Yes, but not today"?). What would
# you use instead in a real product?

# %% [markdown]
# ### 3.2 Personal data: Presidio, live
# Mask card numbers, IBANs, phone numbers and private e-mail addresses before text reaches the model or the trace.

# %%
from ledgerline.course.l6.labelled import PII
for it in PII[:6] + PII[8:11]:
    clean, found, took = G.redact(it["text"])
    print(("PII  " if it["label"] else "none ") + f"{took:5.0f} ms  " + clean[:90])

# %% [markdown]
# ### 3.3 Measuring guards
# Our measurements on the labelled sets (15 injections, 26 ordinary texts; 8 PII, 10 not), and the 20 attacks with guards
# off and on.

# %%
det = log("guards_detectors.json")
for k in ("deberta", "nemo", "presidio"):
    d = det[k]
    print(f"{k:9} catch {d['catch_rate']:.0%}  false alarms {d['false_alarm_rate']:.0%}  median {d['median_ms']} ms")
for tag in ("guards_attacks_r1.json", "guards_attacks_thu.json"):
    a = log(tag)
    print(tag, a.get("prompt", "good"), a["summary"])

# %% [markdown]
# **TODO 5.** Which of the 20 attacks would the deterministic guards alone have stopped under the Thursday prompt, if the
# model had tried? Use `guards_attacks_thu.json` (`calls`, `stopped_by`) to argue it.

# %% [markdown]
# ## Part 4 · Optional, with your own key
# Run Ask Northbridge live, traced, with guards, in a fresh sandbox. Needs `ANTHROPIC_API_KEY` (about US$0.05–0.15 a turn
# on `claude-sonnet-5-5`). Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_HOST` too to send the trace to
# your own Langfuse project.

# %%
RUN_LIVE = False      # set True after setting your key: os.environ["ANTHROPIC_API_KEY"] = "..."
if RUN_LIVE:
    os.environ["LEDGER_LLM_MODE"] = "live"
    from ledgerline.course.l6.agent import Agent
    from ledgerline.course.l6.tracing import Tracing
    tr = Tracing(langfuse=bool(os.environ.get("LANGFUSE_PUBLIC_KEY")), public=False)
    ag = Agent("thursday", guards=G.Guards(G.DETERMINISTIC), tracing=tr)
    r = ag.turn("Order the usual, please, needed by 4 Dec 2026.")
    print(r["reply"]); print([(c["tool"], c["args"].get("confirm"), c["refused_by"]) for c in r["calls"]])
    tr.flush()
    for s in tr.log.tree():
        print("  " * s["depth"] + s["name"])
