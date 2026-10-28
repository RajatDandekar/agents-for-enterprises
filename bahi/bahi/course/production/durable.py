"""Lecture 11, durable execution: Ask Rasoi's order as a Temporal workflow, with the OpenAI Agents SDK inside it.

    the conversation is the workflow     Kavita's messages and Rohit's decision arrive as SIGNALS
    the agent loop runs in the workflow  Runner.run(...) from the OpenAI Agents SDK, unchanged
    every model call is an activity      the Temporal plugin turns each call into a recorded activity
    every Bahi tool is an activity       activity_as_tool(...) (durable_activities.py)

    Kavita: "Reorder 20,000 ..."  ──► agent turn 1: check stock, find supplier, PREVIEW the request ──► wait for Kavita
    Kavita: "Yes, go ahead."      ──► agent turn 2: commit the request ──► read back ──► PR waits for Rohit
                                        wait for Rohit (signal), remind every `remind_after_s`, give up after 5 reminders
    Rohit approves in Bahi        ──► read back (believe Bahi, not the signal) ──► agent turn 3: order + release
                                  ──► read back the order ──► done

Workflow code must be deterministic: after a crash Temporal rebuilds the workflow by running this code again
against the recorded history, so it never calls Bahi, a model, a clock or a random number itself.

Run pieces (the experiment, lectures/L11-production/experiments/durable_order.py, starts them as processes):
    python -m bahi.course.production.durable worker worker-1     a worker (kill it with SIGKILL to test)
    python -m bahi.course.production.durable host                Bahi as its own HTTP service
NB11 replays the recorded history with no key and no server: replay_history(json_text).
Versions: temporalio 1.34.0, temporalio-openai-agents 1.1.0, openai-agents 0.22.3, openai 3.39.0.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from agents import Agent, ModelSettings, Runner
    from temporalio.openai_agents.workflow import activity_as_tool

    from bahi.course.production import durable_activities as A

TASK_QUEUE = "rasoi-orders"
MODEL = os.environ.get("L11_AGENT_MODEL", "google/gemini-3.8-flash")   # through OpenRouter
WORKFLOW_ID = "ask-rasoi-order-KJOSHI-GSK-SIL-05L-20000"

INSTRUCTIONS = """You are Ask Rasoi, the purchasing assistant of Rasoi Steel Works, Pune, a maker of pressure cookers.
You work for Kavita Joshi (KJOSHI), purchase executive, with her own Bahi permissions. Today is Monday 26 October 2026.
- Every fact comes from a tool. Never guess a number.
- To save a request or an order: first call the tool with confirm=false and show the preview in a short list
  (item, quantity, value in rupees, cost centre, need-by date, who must approve). Ask Kavita to confirm. Call it
  again with confirm=true only after she says yes.
- A request above Kavita's limit waits for Rohit Mehta (RMEHTA). Say so; it is not an order yet.
- Once Rohit has approved the request, make the purchase order from it with Deccan Polymers (DP-RJK-0042) with
  confirm=true and release it, without asking Kavita again. Then report the order number and its status.
- Never say an order is placed unless its status is RELEASED.
- The 5-litre silicone gasket is GSK-SIL-05L. The Diwali run is cost centre PRD-07; if no date is given, propose
  9 November 2026 (2026-11-09).
- Short, plain replies, two to six lines. Money with Indian commas, like ₹2,80,840. No emoji."""


def tools():
    t = timedelta(seconds=40)
    rp = RetryPolicy(maximum_attempts=5, initial_interval=timedelta(seconds=1))
    return [activity_as_tool(f, start_to_close_timeout=t, retry_policy=rp) for f in A.TOOLS]


@workflow.defn(name="AskRasoiOrder")
class AskRasoiOrder:
    def __init__(self) -> None:
        self.inbox: list[str] = []          # Kavita's messages, in order
        self.approval: dict | None = None   # Rohit's decision, as signalled
        self.stage = "starting"
        self.replies: list[dict] = []
        self.diary: list[dict] = []
        self.reminders = 0
        self.request_no: str | None = None

    # ---------------------------------------------------------------- messages in (signals) and status out (query)
    @workflow.signal
    def user_says(self, text: str) -> None:
        self.inbox.append(text)

    @workflow.signal
    def approval_decided(self, by: str, decision: str) -> None:
        self.approval = {"by": by, "decision": decision}

    @workflow.query
    def status(self) -> dict:
        return {"stage": self.stage, "request_no": self.request_no, "reminders": self.reminders,
                "replies": self.replies, "diary": self.diary}

    def _log(self, what: str, **kw) -> None:
        self.diary.append({"at": workflow.now().isoformat(timespec="seconds"), "what": what, **kw})

    async def _turn(self, agent, history: list, text: str) -> list:
        self._log("agent turn", user=text[:80])
        res = await Runner.run(agent, history + [{"role": "user", "content": text}], max_turns=12)
        self.replies.append({"user": text, "agent": res.final_output})
        self._log("agent replied", reply=str(res.final_output)[:160])
        return res.to_input_list()

    # ---------------------------------------------------------------- the run
    @workflow.run
    async def run(self, ask: str, remind_after_s: int = 86400, max_reminders: int = 5) -> dict:
        agent = Agent(name="Ask Rasoi", instructions=INSTRUCTIONS, model=MODEL, tools=tools(),
                      model_settings=ModelSettings(temperature=0))
        self._log("started")
        self.stage = "agent: preview"
        history = await self._turn(agent, [], ask)

        # 1. wait for Kavita's yes (a person, so it may take minutes or days)
        self.stage = "waiting for Kavita"
        await workflow.wait_condition(lambda: bool(self.inbox))
        self.stage = "agent: commit request"
        history = await self._turn(agent, history, self.inbox.pop(0))

        # 2. read back what Bahi holds (never trust the model's words for it)
        pr = await workflow.execute_activity(A.read_back_request, "KJOSHI", start_to_close_timeout=timedelta(seconds=20))
        self.request_no = pr.get("pr_no")
        self._log("read back request", **pr)
        if pr.get("status") == "PA":
            self.stage = "waiting for Rohit"
            while True:
                try:
                    await workflow.wait_condition(lambda: self.approval is not None,
                                                  timeout=timedelta(seconds=remind_after_s))
                except asyncio.TimeoutError:
                    if self.reminders >= max_reminders:
                        self.stage = "gave up: no decision"
                        return self._done("no decision")
                    self.reminders += 1
                    self._log("timer fired: remind Rohit", n=self.reminders)
                    await workflow.execute_activity(
                        A.remind, args=["RMEHTA", f"Reminder {self.reminders}: {self.request_no} for 20,000 GSK-SIL-05L "
                                                  "is waiting for your approval in Bahi."],
                        start_to_close_timeout=timedelta(seconds=20))
                    continue
                self._log("signal: approval decided", **self.approval)
                pr = await workflow.execute_activity(A.read_back_request, "KJOSHI",
                                                     start_to_close_timeout=timedelta(seconds=20))
                self._log("read back request", **pr)
                if pr.get("status") == "PA":       # the signal said so, Bahi does not: keep waiting
                    self.approval = None
                    continue
                break
        if pr.get("status") != "AP":
            self.stage = f"stopped: request {pr.get('status')}"
            return self._done(f"request {pr.get('status')}")

        # 3. the order
        self.stage = "agent: order and release"
        history = await self._turn(agent, history, f"Rohit Mehta has approved {self.request_no} in Bahi.")
        st = await workflow.execute_activity(A.order_status, self.request_no, start_to_close_timeout=timedelta(seconds=20))
        self._log("read back order", status=json.dumps(st)[:300])
        self.stage = "done"
        return self._done("finished", order_status=st)

    def _done(self, outcome: str, **kw) -> dict:
        self._log("finished", outcome=outcome)
        return {"outcome": outcome, "request_no": self.request_no, "reminders": self.reminders,
                "replies": self.replies, "diary": self.diary, **kw}


# ====================================================================== outside the workflow: worker, client, replay
def model_provider(log_path: str | None = None):
    """The Agents SDK reaches the model through OpenRouter's OpenAI-compatible API. Every HTTP call is counted in
    log_path (one JSON line per request), so the drill can show which worker really called the model."""
    import time

    import httpx
    from agents import OpenAIChatCompletionsModel
    from agents.models.interface import ModelProvider
    from openai import AsyncOpenAI

    class Counting(httpx.AsyncBaseTransport):
        def __init__(self):
            self.inner = httpx.AsyncHTTPTransport()

        async def handle_async_request(self, request):
            t0 = time.time()
            resp = await self.inner.handle_async_request(request)
            if log_path:
                try:
                    body = json.loads(request.content or b"{}")
                    n = len(body.get("messages", []))
                except Exception:  # noqa: BLE001
                    n = None
                with open(log_path, "a") as f:
                    f.write(json.dumps({"t": round(t0, 3), "worker": os.environ.get("L11_WORKER", "?"),
                                        "url": str(request.url.path), "messages": n, "status": resp.status_code}) + "\n")
            return resp

    class OpenRouter(ModelProvider):
        def __init__(self):
            self.client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1",
                                      api_key=os.environ.get("OPENROUTER_API_KEY", "replay-needs-no-key"),
                                      http_client=httpx.AsyncClient(transport=Counting(), timeout=120))

        def get_model(self, model_name):
            return OpenAIChatCompletionsModel(model=model_name or MODEL, openai_client=self.client)

    return OpenRouter()


def plugin(log_path: str | None = None):
    from temporalio.openai_agents import ModelActivityParameters, OpenAIAgentsPlugin

    return OpenAIAgentsPlugin(model_params=ModelActivityParameters(start_to_close_timeout=timedelta(seconds=120),
                                                                   retry_policy=RetryPolicy(maximum_attempts=4)),
                              model_provider=model_provider(log_path))


def _runner():
    """The workflow sandbox re-imports workflow code on every run; the course package is passed through as is."""
    from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

    return SandboxedWorkflowRunner(restrictions=SandboxRestrictions.default.with_passthrough_modules("bahi"))


async def run_worker(identity: str, address: str = "localhost:7233", log_path: str | None = None):
    from temporalio.client import Client
    from temporalio.worker import Worker

    os.environ["L11_WORKER"] = identity
    client = await Client.connect(address, plugins=[plugin(log_path)])
    worker = Worker(client, task_queue=TASK_QUEUE, workflows=[AskRasoiOrder],
                    activities=[*A.TOOLS, *A.WORKFLOW_ACTIVITIES], identity=identity, workflow_runner=_runner())
    print(f"{identity} polling {TASK_QUEUE}", flush=True)
    await worker.run()


def quiet():
    """For notebooks: keep the Rust core's warnings (a failing replay prints one per attempt) out of the cell output.
    Call before the first Replayer or Worker is made. Production keeps the default logging."""
    import logging
    import warnings

    warnings.filterwarnings("ignore", category=UserWarning, module="temporalio")
    for name in ("temporalio.worker._workflow_instance", "temporalio.worker._replayer", "temporalio.activity"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    try:
        from temporalio.runtime import LoggingConfig, Runtime, TelemetryConfig, TelemetryFilter

        Runtime.set_default(Runtime(telemetry=TelemetryConfig(logging=LoggingConfig(
            filter=TelemetryFilter(core_level="ERROR", other_level="ERROR")))), error_if_already_set=False)
    except Exception:  # noqa: BLE001
        pass


async def replay_history(history_json: str, workflow_id: str = WORKFLOW_ID, workflow_cls=None,
                         sandboxed: bool = True) -> dict:
    """Run the workflow code against a recorded history: no server, no model, no key. Reports a non-determinism
    error if the code no longer makes the same decisions as the recording.
    sandboxed=False runs it without Temporal's import sandbox: use it in a notebook kernel that has already imported
    other libraries (the sandbox re-imports modules and refuses some of them); the replay check is the same."""
    from temporalio.client import WorkflowHistory
    from temporalio.worker import Replayer, UnsandboxedWorkflowRunner

    h = WorkflowHistory.from_json(workflow_id, history_json)
    runner = _runner() if sandboxed else UnsandboxedWorkflowRunner()
    r = await Replayer(workflows=[workflow_cls or AskRasoiOrder], plugins=[plugin(None)],
                       workflow_runner=runner).replay_workflow(h, raise_on_replay_failure=False)
    return {"ok": r.replay_failure is None, "error": None if r.replay_failure is None else
            f"{type(r.replay_failure).__name__}: {str(r.replay_failure)[:400]}"}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "worker":
        asyncio.run(run_worker(sys.argv[2], log_path=sys.argv[3] if len(sys.argv) > 3 else None))
    elif cmd == "host":
        import uvicorn

        uvicorn.run(A.erp_host_app(), host="127.0.0.1", port=8711, log_level="warning")
