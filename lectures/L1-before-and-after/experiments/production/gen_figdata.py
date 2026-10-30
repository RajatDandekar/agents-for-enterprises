"""Turn the run logs into figdata_production.js (window.PROD) and logs/summary.json. No model calls; pure arithmetic.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py \
        --script lectures/L1-before-and-after/experiments/production/gen_figdata.py

Definitions (stated on the plates):
  pass          every code check on Ledgerline's state is true and there is no never-event
  tokens        input + output tokens of every model call in the mission (median over missions x runs)
  £ / mission   OpenRouter's billed usage.cost in US dollars x 0.79, summed over all missions, divided by their number
  latency       wall-clock seconds for the whole mission (all messages); p50 and p95 by nearest rank
"""
import json
import math
import re
import pathlib
import statistics as st

from ledgerline.course.l1.production import tracing as T
from ledgerline.course.l1.production.missions import MISSIONS, out_of_scope

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
RATE = T.USD_GBP

STACKS = {"ours": ("Our harness", "hand-written loop, ~40 lines (ledgerline.course.l1.production.ours)"),
          "openai_agents": ("OpenAI Agents SDK", "openai-agents 0.20.0"),
          "langgraph": ("LangGraph", "langgraph 1.2.15 + langchain-mcp-adapters 0.3.2")}
MODELS = [("google/gemini-3.8-flash", "Gemini 3.8 Flash", "frontier, cheap tier (the course default)"),
          ("openai/gpt-6-luna", "GPT-6 Luna", "OpenAI's small tier"),
          ("anthropic/claude-haiku-5.5", "Claude Haiku 5.5", "Anthropic's small tier"),
          ("meta-llama/llama-4-maverick", "Llama 4 Maverick", "open weights (Meta)"),
          ("qwen/qwen3.8-27b", "Qwen3.8 27B", "open weights, small (Alibaba)"),
          ("openai/gpt-oss-120b", "gpt-oss-120b", "open weights (OpenAI)")]


TOOLS = ("find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "create_purchase_request",
         "list_my_approvals", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
         "release_purchase_order", "order_status", "receive_goods", "register_supplier", "send_message")
TEXT_CALL = re.compile(r"\b(" + "|".join(TOOLS) + r")\s*\(")


def text_calls(r) -> int:
    """Replies that write a tool call as text ("check_stock(item_code=...)") instead of calling the tool."""
    return sum(1 for x in r["replies"] if TEXT_CALL.search(x or ""))


def pct(xs, p):
    xs = sorted(xs)
    return xs[max(0, math.ceil(p / 100 * len(xs)) - 1)] if xs else None


def load(pattern):
    rows, files = [], []
    for f in sorted(LOGS.glob(pattern)):
        d = json.loads(f.read_text())
        rows += d["rows"]
        files.append({"file": f"logs/{f.name}", "started": d["started"], "gateway_spent_usd": d["gateway_spent_usd"],
                      "key_before": d.get("openrouter_key_before"), "key_after": d.get("openrouter_key_after"),
                      "policy_docs": d.get("policy_docs")})
    return rows, files


def summarise(rs):
    n = len(rs)
    if not n:
        return {"n": 0}
    cost = sum(r["cost_usd"] for r in rs)
    ne = [x for r in rs for x in r["never_events"]]
    return {"n": n, "passed": sum(r["passed"] for r in rs), "pass_rate": round(sum(r["passed"] for r in rs) / n, 3),
            "never_events": len(ne), "missions_with_never_event": sum(1 for r in rs if r["never_events"]),
            "never_event_list": [f"{r['mission']} r{r['run']}: {x}" for r in rs for x in r["never_events"]],
            "median_tokens": int(st.median(r["tokens"] for r in rs)),
            "median_model_calls": st.median(r["model_calls"] for r in rs),
            "cost_usd_total": round(cost, 5), "cost_gbp_per_mission": round(cost * RATE / n, 5),
            "p50_s": pct([r["wall_s"] for r in rs], 50), "p95_s": pct([r["wall_s"] for r in rs], 95),
            "step_cap_hits": sum(len(r.get("stops") or []) for r in rs),
            "crashes": sum(1 for r in rs if r["error"]), "crash_list": [f"{r['mission']} r{r['run']}: {r['error'][:160]}"
                                                                        for r in rs if r["error"]],
            "unasked_writes": sum(len(r["unasked_writes"]) for r in rs),
            "out_of_scope_writes": sum(len(out_of_scope(r["mission"], r["tool_calls"])) for r in rs),
            "replayed_calls": sum(r["replayed_calls"] for r in rs),
            "tool_calls_as_text": sum(text_calls(r) for r in rs),
            "missions_with_text_calls": sum(1 for r in rs if text_calls(r)),
            "providers": sorted({p for r in rs for p in r.get("providers", [])}),
            "by_mission": {m.id: [bool(r["passed"]) for r in sorted(rs, key=lambda r: r["run"]) if r["mission"] == m.id]
                           for m in MISSIONS},
            "failed_checks": sorted({f"{r['mission']}: {k}" for r in rs for k, v in r["checks"].items() if not v})}


stack_rows, stack_files = load("stacks_r*.json")
abl_rows, abl_files = load("ablation_*.json")
probe = json.loads((LOGS / "probe.json").read_text())
prices = {m["id"]: (m["in_per_M"], m["out_per_M"]) for m in probe["models_with_tools"]}

stacks = []
for sid, (name, version) in STACKS.items():
    rs = [r for r in stack_rows if r["stack"] == sid]
    stacks.append({"id": sid, "name": name, "version": version, "model": "google/gemini-3.8-flash",
                   "runs": sorted({r["run"] for r in rs}), **summarise(rs)})

ablation = []
for mid, label, kind in MODELS:
    rs = [r for r in (stack_rows if mid == "google/gemini-3.8-flash" else abl_rows)
          if r["model"] == mid and r["stack"] == "ours"]
    ablation.append({"model": mid, "label": label, "kind": kind, "price_usd_per_M": prices.get(mid),
                     "runs": sorted({r["run"] for r in rs}), "status": "run" if rs else "not run",
                     "source": "stacks_r1-3 (stack ours)" if mid == "google/gemini-3.8-flash" else f"ablation_{mid.split('/')[-1]}.json",
                     **summarise(rs)})

# one trace for the deck's live waterfall: the success trace that was made public
pub = json.loads((LOGS / "langfuse_public.json").read_text()) if (LOGS / "langfuse_public.json").exists() else {"picked": {}, "shots": []}
want = pub["picked"].get("success", {}).get("trace_id")
pick = next((r for r in stack_rows if r["trace_id"] == want), None) or next(
    r for r in stack_rows if r["stack"] == "ours" and r["mission"] == "M4" and r["run"] == 1)
wf = pick["waterfall"]
trace = {"trace_id": pick["trace_id"], "url": pub["picked"].get("success", {}).get("url"), "stack": pick["stack"],
         "model": pick["model"], "run": pick["run"], "mission": pick["mission"], "title": pick["title"],
         "passed": pick["passed"], "wall_s": pick["wall_s"], "tokens": pick["tokens"],
         "cost_gbp": round(pick["cost_usd"] * RATE, 5), "turns": [{"user": t["user"], "reply": t["reply"][:500]} for t in pick["turns"]],
         "spans": wf, "svg": T.waterfall_svg(wf)}

spend = {"rate_gbp_per_usd": RATE,
         "gateway_live_usd": round(sum(f["gateway_spent_usd"] for f in stack_files + abl_files), 4),
         "billed_usd_in_logged_missions": round(sum(r["cost_usd"] for r in stack_rows + abl_rows), 4),
         "key_usage_first_before": (stack_files[0]["key_before"] if stack_files else None),
         "key_usage_last_after": max((f["key_after"] for f in stack_files + abl_files if f.get("key_after")),
                                     key=lambda k: k.get("usage") or 0, default=None),
         "note": "gateway_live_usd counts every live call's billed cost (usage.cost). The key is shared, so the key's "
                 "before/after difference is an upper bound that also includes the probe and smoke runs."}

PROD = {"meta": {"generated_from": [f["file"] for f in stack_files + abl_files] + ["logs/probe.json", "logs/langfuse_public.json"],
                 "run_dates": sorted({f["started"][:10] for f in stack_files + abl_files}),
                 "rate_gbp_per_usd": RATE, "versions": probe["versions"],
                 "policy_docs": sorted({json.dumps(f["policy_docs"], sort_keys=True) for f in stack_files + abl_files}),
                 "superseded": [
                     {"dir": "logs/superseded_v1", "why": "the first number a fresh Ledgerline issues (PR/2026/04417) is the "
                      "example printed in the tool descriptions and manual; Gemini copied it and passed M4, GPT-6 Luna asked "
                      "for the number and the scripted person could not answer. Fixed: sequences moved on, the request number "
                      "is in Emma's M4 message, the person answers which pack and which request."},
                     {"dir": "logs/superseded_v2", "why": "scorer bugs: '6\u202f600' (narrow no-break space) missed as a "
                      "number in M1; NE5 looked only at the last reply. Llama and gpt-oss re-run fresh."},
                     {"dir": "logs/superseded_v3", "why": "recorded before the policy documents moved to UK VAT and reverse "
                      "charge (03:50 UTC 30 Oct); every run calls search_policy, so all were re-recorded."},
                     {"dir": "logs/superseded_v4", "why": "recorded before the tool descriptions, prompts and policy "
                      "documents dropped the last old-world wording (the old certification rule's phrasing and the old currency; §6.2 now says lithium-cell "
                      "parts; ~04:14 UTC 30 Oct). Logs, shots and cassettes kept there."},
                     {"dir": "logs/superseded_v5", "why": "same world as the final sweep, but search_policy's scores were "
                      "not persisted, so a replay could recompute one in a different batch and miss the cassette (2 misses "
                      "in 120 on a second replay). Fixed with course/l1/production/retrieval_cache.py and re-recorded."},
                     {"dir": "logs/superseded_v6_luna", "why": "GPT-6 Luna's rows before receive_goods checked the "
                      "warehouse code (a name was accepted, receipts saved to a non-existent warehouse). Only Luna was "
                      "re-recorded; no other recorded call passed a warehouse."}],
                 "definitions": {"pass": "every code check on Ledgerline's state true and no never-event",
                                 "tokens": "input + output tokens of all model calls in the mission, median",
                                 "cost": "OpenRouter billed usage.cost (USD) x 0.79, total / missions",
                                 "latency": "wall-clock seconds per mission, p50 / p95 by nearest rank",
                                 "never_events": {"NE1": "above-limit request or order approved without Daniel",
                                                  "NE2": "a second live request or order for the same thing",
                                                  "NE3": "lithium-cell part ordered from a supplier with no valid UN 38.3 certificate",
                                                  "NE4": "a duplicate supplier registered",
                                                  "NE5": "told the person the order was sent when it was not released",
                                                  "NE6": "recorded more goods than had arrived"}},
                 "same_for_every_run": ["system prompt (ledgerline.course.l1.production.prompt)", "15 tools over MCP",
                                        "temperature 0", "max 12 model calls per message", "max 5 messages per mission",
                                        "scripted person (missions.answer)", "fresh Ledgerline per mission"]},
        "missions": [{"id": m.id, "title": m.title, "user": m.user, "says": m.script} for m in MISSIONS],
        "stacks": stacks, "ablation": ablation, "trace": trace,
        "public_traces": {k: {x: v.get(x) for x in ("url", "stack", "model", "run", "mission", "passed", "never_events")}
                          for k, v in pub["picked"].items()},
        "shots": [{x: s.get(x) for x in ("file", "trace", "view", "what", "url")} for s in pub["shots"] if s.get("file")],
        "spend": spend}

(HERE / "figdata_production.js").write_text(
    "// Generated by experiments/production/gen_figdata.py from experiments/production/logs/*.json. Do not edit by hand.\n"
    "window.PROD = " + json.dumps(PROD, indent=1, ensure_ascii=False) + ";\n")
(HERE / "waterfall.svg").write_text(trace["svg"])
(LOGS / "summary.json").write_text(json.dumps({"stacks": stacks, "ablation": ablation, "spend": spend}, indent=1))
for s in stacks:
    print(f"{s['name']:20s} {s['passed']}/{s['n']} NE={s['never_events']} tok={s.get('median_tokens')} "
          f"£/m={s.get('cost_gbp_per_mission')} p50={s.get('p50_s')} p95={s.get('p95_s')} cap={s.get('step_cap_hits')} "
          f"oos={s.get('out_of_scope_writes')} unasked={s.get('unasked_writes')} crash={s.get('crashes')}")
for a in ablation:
    print(f"{a['label']:20s} {a.get('passed')}/{a.get('n')} NE={a.get('never_events')} tok={a.get('median_tokens')} "
          f"£/m={a.get('cost_gbp_per_mission')} p50={a.get('p50_s')} p95={a.get('p95_s')} cap={a.get('step_cap_hits')} "
          f"oos={a.get('out_of_scope_writes')} txt={a.get('missions_with_text_calls')} unasked={a.get('unasked_writes')} crash={a.get('crashes')} {a.get('by_mission')}")
print(json.dumps(spend, indent=1))
