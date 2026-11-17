"""The class suite on Ask Northbridge: 20 tasks x k runs, under a prompt; code checks + Claude Haiku as the judge.

    tools/mrun.sh .../l6_modal.py --script suite_run.py --args "--prompt good --k 3 --tag good_k3"
    tools/mrun.sh .../l6_modal.py --script suite_run.py --args "--prompt thursday --k 1 --tag thursday_k1"

Every run is traced to Langfuse (public, tags L6 suite <task>), every model reply recorded in a cassette per run
(cassettes/L6E_suite_<prompt>_r<i>.jsonl), so the notebook can replay any of them without a key.
Writes logs/suite_<tag>.json: per task-run every check (kind, pass, why), the reply, the tool calls, the writes Ledgerline
holds, tokens, cost, the trace id; and pass^k / pass@k.
"""
import argparse

from _common import now, pmap, spend, write

from ledgerline.course.l6 import suite as S
from ledgerline.course.l6.judges import judge
from ledgerline.course.l6.tracing import Tracing, trace_url
from ledgerline.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--prompt", default="good")
ap.add_argument("--k", type=int, default=1)
ap.add_argument("--tasks", default="all")
ap.add_argument("--tag", default="")
ap.add_argument("--workers", type=int, default=10)
a = ap.parse_args()
tag = a.tag or f"{a.prompt}_k{a.k}"
tasks = S.TASKS if a.tasks == "all" else [S.BY_ID[t] for t in a.tasks.split(",")]


def jfn(rubric, reply, ev, user):
    return judge(rubric, reply, ev, user, cassette="L6E_judge", mode="record")


def one(job):
    task, rep = job
    tr = Tracing.from_env(public=True, batch=False)
    llm_for = lambda m: LLM(m, cassette=f"L6E_suite_{a.prompt}_r{rep}", mode="record", max_tokens=8192)  # noqa: E731
    r = S.run_task(task, prompt=a.prompt, tracing=tr, llm_for=llm_for, judge_fn=jfn,
                   conv=f"l6-suite-{tag}-{task['id']}-r{rep}", tags=(tag, a.prompt))
    tr.flush()
    r["rep"] = rep
    for t in r["turns"]:
        if t.get("trace_id"):
            try:
                t["url"] = trace_url(t["trace_id"])
            except Exception:  # noqa: BLE001
                t["url"] = None
    return r


jobs = [(t, i) for i in range(a.k) for t in tasks]
rows = pmap(one, jobs, workers=a.workers)
by_kind = {}
for r in rows:
    for c in r["checks"]:
        d = by_kind.setdefault(c["kind"], {"checks": 0, "passed": 0})
        d["checks"] += 1
        d["passed"] += int(c["pass"])
judge_usd = sum(c.get("judge_usd", 0) for r in rows for c in r["checks"])
agent_usd = sum(r["usd"] for r in rows)
out = {"at": now(), "prompt": a.prompt, "k": a.k, "tasks": len(tasks), "runs": len(rows), "model": "claude-sonnet-5-5",
       "judge": "claude-haiku-5-5", "passed_runs": sum(r["pass"] for r in rows), "errors": sum(1 for r in rows if r["error"]),
       "by_kind": by_kind, "pass_k": S.pass_hat_k(rows, a.k), "agent_usd": round(agent_usd, 4), "judge_usd": round(judge_usd, 5),
       "rows": rows}
write(f"suite_{tag}.json", out)
spend(f"suite_{tag}", agent_usd + judge_usd, sum(r["model_calls"] for r in rows) + sum(1 for r in rows for c in r["checks"] if c["kind"] == "words"),
      sum(r["tokens_in"] for r in rows), sum(r["tokens_out"] for r in rows), "claude-sonnet-5-5 + haiku judge", f"{len(rows)} task runs")
print("passed", out["passed_runs"], "/", len(rows), "errors", out["errors"], out["by_kind"], out["pass_k"])
for r in sorted(rows, key=lambda r: (r["task"], r["rep"])):
    print(r["task"], r["rep"], "PASS" if r["pass"] else "FAIL", r["error"] or "",
          " | ".join(f"{c['kind']}:{'ok' if c['pass'] else 'X ' + c['why'][:90]}" for c in r["checks"] if not c["pass"]))
