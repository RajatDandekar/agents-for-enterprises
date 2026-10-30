"""Run the five missions on one stack and one model, traced, scored from Ledgerline, and costed.

    from ledgerline.course.l1.production.runner import Rig
    rig = Rig(langfuse=True)                                     # the gateway, the tracer, Langfuse
    rows = rig.run_suite("ours", "google/gemini-3.8-flash", run=1)
    rig.close()

One mission = a fresh Ledgerline set to the state before it, one MCP tool server per person, one conversation, one
trace. The person's side is scripted (missions.answer), so every stack and model hears the same words.
"""
from __future__ import annotations

import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from ....erp.engine import ERP
from . import tracing as T
from .gateway import Gateway
from .missions import MISSIONS, answer, score, snapshot
from .prompt import system_for
from .toolserver import ToolServer

MAX_TURNS = 5   # messages from the person per mission


def stack_class(name: str):
    if name == "ours":
        from .ours import OurHarness
        return OurHarness
    if name == "openai_agents":
        from .agents_sdk import AgentsSDKStack
        return AgentsSDKStack
    if name == "langgraph":
        from .langgraph_agent import LangGraphStack
        return LangGraphStack
    raise ValueError(name)


def slug(model: str) -> str:
    return model.split("/")[-1].replace(":", "-")


def cassette_name(stack: str, model: str, run: int) -> str:
    return f"L1v4_prod_{stack}_{slug(model)}_r{run}"


class Rig:
    def __init__(self, langfuse: bool = True, budget_usd: float = 3.0, mode: str | None = None):
        self.tp, self.spans = T.provider(langfuse=langfuse)
        self.tracer = self.tp.get_tracer("ask-northbridge", "l1-production")
        self.gw = Gateway(self.tracer, mode=mode, budget_usd=budget_usd).start()
        import os
        self.scores = bool(langfuse and os.environ.get("LANGFUSE_PUBLIC_KEY"))   # erp_check + never_events on each trace

    # ------------------------------------------------------------------------------------------- one mission
    def run_mission(self, stack: str, model: str, mission, run: int, public: bool = False) -> dict:
        tag = f"{stack}-{slug(model)}-r{run}-{mission.id}"
        session = f"L1prod-{stack}-{slug(model)}-r{run}"
        erp = ERP()
        ctx = mission.setup(erp) or {}
        before = snapshot(erp)
        srv = ToolServer(erp, mission.user, self.tracer)
        root = T.start_mission(self.tracer, mission, stack, model, run, session, public)
        trace_id = T.hex_id(root)
        root_span_id = format(root.get_span_context().span_id, "016x")
        url = self.gw.base_url(tag, cassette_name(stack, model, run))
        turns, replies, said, error, agent = [], [], [], None, None
        t0 = time.perf_counter()
        try:
            cls = stack_class(stack)
            kw = {"group": tag} if stack == "openai_agents" else {}
            agent = cls(system_for(erp, mission.user), srv.url, url, model, **kw)
            stage, text = 0, mission.opening(ctx)
            for turn in range(1, MAX_TURNS + 1):
                said.append(text)
                srv.turn = turn
                sp = T.start_turn(self.tracer, root, turn, text, stack, model, session)
                self.gw.parent[tag] = sp
                srv.parent = sp
                t1 = time.perf_counter()
                try:
                    reply = agent.respond(text)
                except Exception as e:  # noqa: BLE001  (a crash is a result too)
                    T.end_turn(sp, "", error=f"{type(e).__name__}: {e}")
                    raise
                T.end_turn(sp, reply)
                replies.append(reply)
                turns.append({"turn": turn, "user": text, "reply": reply, "seconds": round(time.perf_counter() - t1, 2),
                              "tools": [c["name"] for c in srv.calls if c["turn"] == turn]})
                done = score(mission, erp, ctx, before, srv.calls, replies)["passed"]
                if done:
                    break
                if mission.stage_done and stage + 1 < len(mission.script) and mission.stage_done(erp, ctx, stage):
                    stage += 1
                    text = mission.script[stage].format(**ctx)
                elif mission.stage_done and stage + 1 < len(mission.script) and turn >= 3:
                    stage += 1                       # it is past time for the second delivery: say it anyway
                    text = mission.script[stage].format(**ctx)
                else:
                    text = answer(mission, reply, said, ctx)
        except Exception as e:  # noqa: BLE001
            error = f"{type(e).__name__}: {str(e)[:400]}"
            traceback.print_exc()
        wall = round(time.perf_counter() - t0, 2)
        res = score(mission, erp, ctx, before, srv.calls, replies)
        if error:
            res["passed"] = False
        recs = self.gw.records(tag)
        res.update({"mission": mission.id, "title": mission.title, "stack": stack, "model": model, "run": run,
                    "tag": tag, "trace_id": trace_id, "root_span_id": root_span_id, "session": session, "replies": replies, "turns": turns,
                    "error": error, "wall_s": wall, "model_calls": len([r for r in recs if "error" not in r]),
                    "model_errors": [r["error"] for r in recs if "error" in r][:3],
                    "tokens_in": sum(r.get("tokens_in", 0) for r in recs),
                    "tokens_out": sum(r.get("tokens_out", 0) for r in recs),
                    "model_s": round(sum(r.get("seconds", 0) for r in recs), 2),
                    "cost_usd": round(sum(float(r.get("cost_usd") or 0) for r in recs), 6),
                    "replayed_calls": sum(1 for r in recs if r.get("replayed")),
                    "providers": sorted({str(r.get("provider")) for r in recs if r.get("provider")}),
                    "tool_calls": [{k: c[k] for k in ("turn", "name", "args", "ok", "ms", "error", "status")} for c in srv.calls],
                    "stops": getattr(agent, "stops", []) if agent else [],
                    "native": (agent.native[-200:] if agent is not None and hasattr(agent, "native") else None)})
        res["tokens"] = res["tokens_in"] + res["tokens_out"]
        res["cost_gbp"] = round(res["cost_usd"] * T.USD_GBP, 6)
        T.end_mission(root, said[0] if said else "", res)
        if self.scores:   # the code checks, attached to the trace as Langfuse scores
            from .langfuse_api import post_score
            try:
                post_score(trace_id, "erp_check", 1 if res["passed"] else 0, "BOOLEAN",
                           "; ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in res["checks"].items()))
                post_score(trace_id, "never_events", len(res["never_events"]), "NUMERIC",
                           "; ".join(res["never_events"]) or "none")
            except Exception as e:  # noqa: BLE001
                res["score_error"] = repr(e)[:200]
        try:
            if agent is not None:
                agent.close()
        finally:
            srv.stop()
        return res

    def run_suite(self, stack: str, model: str, run: int, missions=None, parallel: int = 5, public=()) -> list[dict]:
        ms = missions or MISSIONS
        with ThreadPoolExecutor(parallel) as ex:
            futs = [ex.submit(self.run_mission, stack, model, m, run, m.id in public) for m in ms]
            return [f.result() for f in futs]

    def close(self):
        self.tp.force_flush()
        self.gw.stop()
