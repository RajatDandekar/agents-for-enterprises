"""The Workflow Studio's web API and page, as one FastAPI router the experience app mounts:

    from ledgerline.experience.studio.api import make_router
    app.include_router(make_router(players))

The page is at /studio; the JSON API is under /api/studio (SPEC.md §3). The player is the cookie `pid` or the
header `X-Player`; with neither, a guest player is joined and the cookie is set.
"""
from __future__ import annotations

import copy
import pathlib
import re
import threading
from collections import defaultdict

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

from ...toolbox import SPECS
from .engine import PEOPLE, ROLES, TRIGGER, Engine, Store, StudioError
from .templates import TEMPLATES, catalog, template

STATIC = pathlib.Path(__file__).parent / "static"
MEDIA = {".js": "application/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png",
         ".html": "text/html", ".json": "application/json"}

# The palette's built-in node types (tools come from the toolbox's tool.json files).
TYPES = [
    {"type": "trigger", "group": "Triggers", "kind": "manual", "title": "Manual start", "description": "Run it with the Run button."},
    {"type": "trigger", "group": "Triggers", "kind": "form", "title": "Form", "description": "A short form starts the run, e.g. goods at the gate."},
    {"type": "trigger", "group": "Triggers", "kind": "event", "title": "Stock below reorder", "description": "Fires when a watched item falls below its reorder level."},
    {"type": "trigger", "group": "Triggers", "kind": "schedule", "title": "Schedule", "description": "Every day, hour or week."},
    {"type": "trigger", "group": "Triggers", "kind": "chat", "title": "Chat message", "description": "A message in the chat panel starts the run."},
    {"type": "condition", "group": "Logic", "title": "Condition", "description": "Branch: a yes path and a no path."},
    {"type": "approval", "group": "Logic", "title": "Approval", "description": "Pause until the approver signs in their inbox."},
    {"type": "set", "group": "Logic", "title": "Set values", "description": "Compute values from earlier outputs."},
    {"type": "llm", "group": "AI", "title": "LLM", "description": "A prompt in; text or JSON out. E.g. read an email."},
    {"type": "agent", "group": "AI", "title": "Agent", "description": "Your own agent: instructions, chosen tools, a model."},
    {"type": "message", "group": "Messaging", "title": "Message", "description": "Send a Slack or email message."},
]


def make_router(players, store: Store | None = None) -> APIRouter:
    store = store or Store()
    router = APIRouter()
    locks: dict[str, threading.RLock] = defaultdict(threading.RLock)  # one player's Northbridge runs one thing at a time

    # ------------------------------------------------------------------ who is asking
    def pid_of(request: Request, response: Response) -> str:
        pid = request.headers.get("X-Player") or request.cookies.get("pid")
        if pid and not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", pid):
            raise HTTPException(400, "Bad player id.")
        if not pid:
            pid = players.join("Guest engineer").pid
            response.set_cookie("pid", pid, max_age=60 * 60 * 24 * 60, samesite="lax")
        elif players.get(pid) is None:
            players.join("Engineer", pid=pid)
        return pid

    def engine(pid: str) -> Engine:
        return Engine(toolbox_for=lambda user, names=None: players.toolbox(pid, user, names), store=store, pid=pid)

    def guard(fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except StudioError as e:
            raise HTTPException(400, f"{e} {e.next_step}".strip())

    def get_wf(pid, wid):
        wf = store.workflow(pid, wid)
        if not wf:
            raise HTTPException(404, f"No workflow '{wid}'.")
        return wf

    def get_run(pid, rid):
        run = store.run(pid, rid)
        if not run:
            raise HTTPException(404, f"No run '{rid}'.")
        return run

    def new_id(pid, base):
        base = re.sub(r"[^a-z0-9-]+", "-", (base or "workflow").lower()).strip("-")[:40] or "workflow"
        wid, i = base, 2
        while store.workflow(pid, wid):
            wid, i = f"{base}-{i}", i + 1
        return wid

    # ------------------------------------------------------------------ the page
    def page(request: Request):
        resp = HTMLResponse((STATIC / "index.html").read_text())
        pid = request.headers.get("X-Player") or request.cookies.get("pid")
        if not pid:
            resp.set_cookie("pid", players.join("Guest engineer").pid, max_age=60 * 60 * 24 * 60, samesite="lax")
        return resp

    router.add_api_route("/studio", page, methods=["GET"], include_in_schema=False)
    router.add_api_route("/studio/", page, methods=["GET"], include_in_schema=False)
    router.add_api_route("/studio/w/{wid}", page, methods=["GET"], include_in_schema=False)

    @router.get("/studio/static/{name}", include_in_schema=False)
    def static(name: str):
        f = STATIC / name
        if name not in {p.name for p in STATIC.iterdir()} or not f.is_file():
            raise HTTPException(404)
        return FileResponse(f, media_type=MEDIA.get(f.suffix, "application/octet-stream"),
                            headers={"Cache-Control": "no-cache"})

    # ------------------------------------------------------------------ palette, templates
    @router.get("/api/studio/me")
    def me(pid: str = Depends(pid_of)):
        p = players.get(pid)
        return {"pid": pid, "name": p.name if p else "Engineer",
                "people": {k: {"name": v, "role": ROLES[k]} for k, v in PEOPLE.items()}}

    @router.get("/api/studio/nodes")
    def nodes():
        tools = [{k: v for k, v in s.card().items() if k != "python"} for s in SPECS.values()]
        return {"types": TYPES, "tools": tools,
                "people": {k: {"name": v, "role": ROLES[k]} for k, v in PEOPLE.items()}}

    @router.get("/api/studio/templates")
    def templates():
        return catalog()

    @router.get("/api/studio/templates/{tid}")
    def template_json(tid: str):
        if tid not in TEMPLATES:
            raise HTTPException(404, f"No template '{tid}'.")
        return template(tid)

    @router.post("/api/studio/templates/{tid}/use")
    def use_template(tid: str, pid: str = Depends(pid_of)):
        if tid not in TEMPLATES:
            raise HTTPException(404, f"No template '{tid}'.")
        wf = template(tid)
        wf["id"], wf["template"] = new_id(pid, tid), tid
        return store.save_workflow(pid, wf)

    # ------------------------------------------------------------------ workflows
    @router.get("/api/studio/workflows")
    def workflows(pid: str = Depends(pid_of)):
        return [{"id": w["id"], "name": w.get("name"), "description": w.get("description", ""),
                 "nodes": len(w.get("nodes", [])), "template": w.get("template")} for w in store.workflows(pid)]

    @router.post("/api/studio/workflows")
    def create_workflow(wf: dict = Body(...), pid: str = Depends(pid_of)):
        wf = copy.deepcopy(wf)
        wf.setdefault("nodes", []), wf.setdefault("edges", [])
        wf["id"] = wf.get("id") if wf.get("id") and not store.workflow(pid, wf["id"]) else new_id(pid, wf.get("name"))
        store.save_workflow(pid, wf)
        return {**wf, "problems": engine(pid).validate(wf)}

    @router.get("/api/studio/workflows/{wid}")
    def read_workflow(wid: str, pid: str = Depends(pid_of)):
        wf = get_wf(pid, wid)
        return {**wf, "problems": engine(pid).validate(wf)}

    @router.put("/api/studio/workflows/{wid}")
    def save_workflow(wid: str, wf: dict = Body(...), pid: str = Depends(pid_of)):
        wf = {k: v for k, v in wf.items() if k != "problems"}
        wf["id"] = wid
        wf.setdefault("nodes", []), wf.setdefault("edges", [])
        store.save_workflow(pid, wf)
        return {**wf, "problems": engine(pid).validate(wf)}

    @router.delete("/api/studio/workflows/{wid}")
    def delete_workflow(wid: str, pid: str = Depends(pid_of)):
        store.delete_workflow(pid, wid)
        return {"ok": True}

    # ------------------------------------------------------------------ runs
    @router.post("/api/studio/workflows/{wid}/run")
    def run_workflow(wid: str, body: dict = Body(default={}), pid: str = Depends(pid_of)):
        wf, eng = get_wf(pid, wid), engine(pid)
        with locks[pid]:
            run = guard(eng.start, wf, body.get("trigger") or {})
            if body.get("mode", "step") == "all":
                eng.run_until_pause(run)
        return run

    @router.get("/api/studio/runs")
    def runs(workflow_id: str | None = None, pid: str = Depends(pid_of)):
        return [{k: r[k] for k in ("id", "workflow_id", "workflow_name", "status", "started", "finished", "error",
                                   "waiting_for", "trigger_kind")} for r in store.runs(pid, workflow_id)][:50]

    @router.get("/api/studio/runs/{rid}")
    def read_run(rid: str, pid: str = Depends(pid_of)):
        return get_run(pid, rid)

    @router.post("/api/studio/runs/{rid}/step")
    def step(rid: str, pid: str = Depends(pid_of)):
        with locks[pid]:
            return engine(pid).step(get_run(pid, rid))

    @router.post("/api/studio/runs/{rid}/continue")
    def cont(rid: str, pid: str = Depends(pid_of)):
        with locks[pid]:
            return engine(pid).run_until_pause(get_run(pid, rid))

    @router.post("/api/studio/runs/{rid}/approve")
    def approve(rid: str, body: dict = Body(default={}), pid: str = Depends(pid_of)):
        with locks[pid]:
            return guard(engine(pid).approve, get_run(pid, rid), body.get("decision", "approve"), body.get("comment", ""))

    @router.post("/api/studio/runs/{rid}/resume")
    def resume(rid: str, pid: str = Depends(pid_of)):
        with locks[pid]:
            return engine(pid).resume(get_run(pid, rid))

    # ------------------------------------------------------------------ chat with a chat-triggered workflow
    @router.get("/api/studio/workflows/{wid}/chat")
    def chat_history(wid: str, pid: str = Depends(pid_of)):
        return {"history": store.chat(pid, wid)}

    @router.post("/api/studio/workflows/{wid}/chat")
    def chat(wid: str, body: dict = Body(...), pid: str = Depends(pid_of)):
        msg = str(body.get("message", "")).strip()
        if not msg:
            raise HTTPException(400, "Type a message.")
        wf = get_wf(pid, wid)
        with locks[pid]:
            reply, run = guard(engine(pid).chat, wf, msg)
        return {"reply": reply, "run": run, "history": store.chat(pid, wid)}

    @router.delete("/api/studio/workflows/{wid}/chat")
    def clear_chat(wid: str, pid: str = Depends(pid_of)):
        store.save_chat(pid, wid, [])
        return {"ok": True}

    # ------------------------------------------------------------------ the approver's side
    @router.get("/api/studio/approvals")
    def approvals(user: str = "DOKAFOR", pid: str = Depends(pid_of)):
        if user not in PEOPLE:
            raise HTTPException(400, f"Unknown person {user}.")
        return players.toolbox(pid, user).call("list_my_approvals", {})

    @router.get("/api/studio/document")
    def document(doc_no: str, user: str = "DOKAFOR", pid: str = Depends(pid_of)):
        if user not in PEOPLE:
            raise HTTPException(400, f"Unknown person {user}.")
        args = {"request_no": doc_no} if doc_no.upper().startswith("PR") else {"po_no": doc_no}
        return players.toolbox(pid, user).call("order_status", args)

    # ------------------------------------------------------------------ events and the scheduler
    @router.post("/api/studio/events/check")
    def check_events(pid: str = Depends(pid_of)):
        eng, started = engine(pid), []
        with locks[pid]:
            for wf in store.workflows(pid):
                trig = next((n for n in wf.get("nodes", []) if n.get("type") == "trigger"), None)
                if not trig or trig.get("config", {}).get("kind") != "event" or eng.validate(wf):
                    continue
                probe = {"trigger_data": {}, "nodes": {trig["id"]: {}}}
                res = TRIGGER(eng, probe, trig, {"today": None})
                if res.output.get("fired"):
                    run = eng.run_until_pause(eng.start(wf, {"item_code": res.output["item_code"]}))
                    started.append({"workflow_id": wf["id"], "run_id": run["id"], "status": run["status"],
                                    "item_code": res.output["item_code"]})
        return {"started": started}

    @router.post("/api/studio/tick")
    def tick(pid: str = Depends(pid_of)):
        eng, started = engine(pid), []
        with locks[pid]:
            for wf in store.workflows(pid):
                trig = next((n for n in wf.get("nodes", []) if n.get("type") == "trigger"), None)
                if trig and trig.get("config", {}).get("kind") == "schedule" and not eng.validate(wf):
                    run = eng.run_until_pause(eng.start(wf))
                    started.append({"workflow_id": wf["id"], "run_id": run["id"], "status": run["status"]})
        return {"started": started}

    @router.post("/api/studio/reset")
    def reset(pid: str = Depends(pid_of)):
        with locks[pid]:
            players.reset(pid)
            store.clear(pid)
        return {"ok": True}

    return router
