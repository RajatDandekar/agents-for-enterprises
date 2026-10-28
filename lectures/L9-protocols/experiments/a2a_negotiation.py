"""Ask Rasoi negotiates with Deccan Polymers' sales agent over A2A (a2a-sdk 1.2.3, spec 1.0), recorded.

    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/a2a_negotiation.py              # record
    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/a2a_negotiation.py --mode replay # prove replay
-> logs/a2a_negotiation.json, logs/a2a_agent_card.json   (record)
-> logs/a2a_replay_check.json                            (replay)
Cassettes: bahi/cassettes/IND9_a2a_rasoi.jsonl, IND9_a2a_deccan.jsonl
"""
import json
import os
import pathlib
import subprocess
import sys

try:
    import a2a  # noqa: F401
    from importlib.metadata import version
    assert version("a2a-sdk") == "1.2.3"
except Exception:  # pin it on the Modal container
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "a2a-sdk[http-server]==1.2.3"], check=True)

sys.path.insert(0, "/course/bahi")
from importlib.metadata import version  # noqa: E402

from bahi.course.protocols.deccan import plain_sequence, run_negotiation  # noqa: E402
from bahi.erp.engine import ERP  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
mode = os.environ.get("BAHI_LLM_MODE", "auto")
out = run_negotiation(ERP(), mode=mode)
out["versions"] = {p: version(p) for p in ("a2a-sdk", "protobuf", "httpx", "starlette", "uvicorn")}
out["mode"] = mode

for t in out["turns"]:
    print(f"\n=== turn {t['turn']} ({'stream' if t['streaming'] else 'send'}) {t['wall_seconds']} s, "
          f"{t['http_requests']} HTTP, to Deccan {t['a2a_messages_to_deccan']}, events back {t['a2a_events_from_deccan']}, "
          f"states {t['task_states']}")
    print("  Kavita   :", t["kavita"])
    print("  AskRasoi :", t["ask_rasoi"])
    print("  llm rasoi:", t["llm_ask_rasoi"], "\n  llm deccan:", t["llm_deccan"])
for e in out["sequence"]:
    print(f"{e['t_ms']:>9} {e['from']:>13} -> {e['to']:<13} {e['kind']:<20} {e['summary'][:150]}")
print("\nbahi:", {k: (v.get("request_no") or v.get("po_no"), v.get("status")) for k, v in out["bahi"].items()})
print("totals:", out["totals"], "live calls:", out["live_calls"])

LOGS.mkdir(exist_ok=True)
if mode == "replay":
    rec = json.loads((LOGS / "a2a_negotiation.json").read_text())
    a, b = plain_sequence(rec["sequence"]), plain_sequence(out["sequence"])
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    check = {"mode": "replay", "recorded_events": len(a), "replayed_events": len(b), "identical": a == b,
             "first_differences": [{"i": i, "recorded": a[i], "replayed": b[i]} for i in diff[:5]],
             "live_calls": out["live_calls"], "turns": [{k: t[k] for k in ("turn", "wall_seconds", "http_requests",
                                                                          "a2a_messages_to_deccan", "a2a_events_from_deccan",
                                                                          "task_states")} for t in out["turns"]],
             "answers_identical": [t["ask_rasoi"] for t in rec["turns"]] == [t["ask_rasoi"] for t in out["turns"]]}
    (LOGS / "a2a_replay_check.json").write_text(json.dumps(check, indent=1, ensure_ascii=False))
    print("REPLAY:", {k: check[k] for k in ("identical", "answers_identical", "live_calls", "recorded_events", "replayed_events")})
else:
    (LOGS / "a2a_negotiation.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    (LOGS / "a2a_agent_card.json").write_text(json.dumps(next(e["resp"] for e in out["wire"] if e["method"] == "GET"),
                                                        indent=1, ensure_ascii=False))
