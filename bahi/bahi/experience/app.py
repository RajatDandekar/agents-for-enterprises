"""The Rasoi Experience: one web app the whole cohort uses from one link (Lecture 1, and every lecture after).

    /            the invitation: your name, then Anand Patil's letter to you
    /brief       your wishlist, before anything is revealed, and the class wall
    /before      the legacy Bahi ERP 7.2: "ERP in 5 minutes", then five missions, timed and counted
    /after       Rasoi's new home page: Ask Rasoi (chat), the approvals inbox, the order tracker, your scorecard
                 ?stage=brain|knowledge|hands|agent   Ask Rasoi as it is at each lecture
    /tools       the toolbox explorer: every tool.json and tool.py, and a form to try each one
    /studio      the Workflow Studio (bahi/experience/studio, mounted if present)
    /admin       the operator's page: kill switch, budget, players (admin token)

    uvicorn bahi.experience.app:app          (deployed by deploy/experience_modal.py)

Every player has their own Rasoi: players.erp(pid), a freshly seeded Bahi sandbox in memory.
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import missions as M
from .guard import Guard, Refused
from .harness import STAGES, Agents
from .legacy import make_legacy_router
from .players import PEOPLE, Players
from .store import Store

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
PERSONS = {"kavita": "KJOSHI", "rohit": "RMEHTA", "neha": "NDESAI", "KJOSHI": "KJOSHI", "RMEHTA": "RMEHTA",
           "NDESAI": "NDESAI"}
PICKS = ["Order in one sentence", "Ask stock in plain words", "Show the real status, never a guess",
         "Preview before anything is saved", "Approve in one tap", "Explain errors in plain words",
         "Catch the closed cost centre", "Never act above someone's limit", "Quote the policy rule",
         "Tell dealers where their order is", "Work on the phone", "Count goods in at stores"]
QUESTIONS = [("one_sentence", "What should Kavita be able to do in one sentence?"),
             ("never", "What must never happen?"),
             ("approve", "Who should approve what?"),
             ("dealers", "What would you show the dealers?")]


def create_app(store: Store | None = None) -> FastAPI:
    app = FastAPI(title="The Rasoi Experience", docs_url=None, redoc_url=None)
    store = store or Store()
    players = Players()
    guard = Guard(store)
    agents = Agents(players, guard)
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("RASOI_CHAT_THREADS", "96")))
    app.state.players, app.state.store, app.state.guard, app.state.agents = players, store, guard, agents

    # ------------------------------------------------------------------ players (restored from the store)
    for k in store.keys("p:"):
        v = store.get(k) or {}
        p = players.join(v.get("name", "Engineer"), k[2:])
        p.joined_on, p.data = v.get("joined_on", p.joined_on), v.get("data", {})

    def save(p):
        store.put(f"p:{p.pid}", {"name": p.name, "joined_on": p.joined_on, "data": p.data})

    def known(pid: str) -> bool:
        return bool(pid) and players.get(pid) is not None

    def player(req: Request):
        pid = req.headers.get("x-player") or req.cookies.get("rx_pid") or req.cookies.get("pid")
        p = players.get(pid) if pid else None
        if p is None:
            raise HTTPException(401, "Join first: open the home page and enter your name.")
        return p

    def admin(req: Request):
        want = os.environ.get("RASOI_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    @app.exception_handler(Refused)
    async def _refused(_, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    app.include_router(make_legacy_router(players, known))

    # ------------------------------------------------------------------ pages
    def page(name):
        return FileResponse(STATIC / name, headers={"Cache-Control": "no-cache"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page("index.html")

    @app.get("/brief", response_class=HTMLResponse)
    def brief_page():
        return page("brief.html")

    @app.get("/before", response_class=HTMLResponse)
    def before_page():
        return page("before.html")

    @app.get("/after", response_class=HTMLResponse)
    def after_page():
        return page("after.html")

    @app.get("/tools", response_class=HTMLResponse)
    def tools_page():
        return page("tools.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "players": len(players.all()), "conversations": agents.count(),
                "studio": STUDIO.get("ok", False)}

    # ------------------------------------------------------------------ joining
    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Please type your name.")
        p = players.join(name)
        p.data.setdefault("joined", time.time())
        save(p)
        players.erp(p.pid)
        resp = JSONResponse({"pid": p.pid, "name": p.name})
        https = req.url.scheme == "https" or req.headers.get("x-forwarded-proto") == "https"
        for c in ("rx_pid", "pid"):  # the Workflow Studio reads "pid"
            resp.set_cookie(c, p.pid, max_age=60 * 60 * 24 * 60, samesite="lax", secure=https)
        return resp

    @app.get("/api/me")
    def me(req: Request):
        p = player(req)
        d = p.data
        return {"pid": p.pid, "name": p.name, "wishlist": d.get("wishlist"),
                "before": M.Missions(d).totals(), "before_done": M.Missions(d).current is None,
                "after": d.get("after"), "people": PEOPLE}

    @app.post("/api/rename")
    async def rename(req: Request):
        p = player(req)
        b = await req.json()
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) >= 2:
            p.name = name
            save(p)
        return {"name": p.name}

    # ------------------------------------------------------------------ the brief
    @app.get("/api/brief/questions")
    def questions():
        return {"questions": [{"id": k, "text": t} for k, t in QUESTIONS], "picks": PICKS}

    @app.post("/api/wishlist")
    async def wishlist(req: Request):
        p = player(req)
        b = await req.json()
        answers = {k: str((b.get("answers") or {}).get(k, ""))[:400].strip() for k, _ in QUESTIONS}
        picks = [x for x in (b.get("picks") or []) if x in PICKS][:12]
        p.data["wishlist"] = {"answers": answers, "picks": picks, "at": time.time()}
        save(p)
        return p.data["wishlist"]

    @app.get("/api/wall")
    def wall():
        rows, counts = [], {k: 0 for k in PICKS}
        for p in players.all():
            w = p.data.get("wishlist")
            if not w:
                continue
            rows.append({"name": p.name, "answers": w["answers"], "picks": w["picks"], "at": w["at"]})
            for x in w["picks"]:
                counts[x] = counts.get(x, 0) + 1
        rows.sort(key=lambda r: -r["at"])
        return {"count": len(rows), "rows": rows[:120], "picks": counts}

    # ------------------------------------------------------------------ the Before missions
    @app.post("/api/missions")
    async def missions(req: Request):
        """Body: {"action": "start" | "check" | "reset", "counters": {...}}. Returns the mission panel's state."""
        p = player(req)
        b = await req.json()
        erp = players.erp(p.pid)
        ms = M.Missions(p.data)
        act = b.get("action", "check")
        if act == "reset":
            players.reset(p.pid)
            agents.drop(p.pid)
            p.data["before"] = {}
            p.data.pop("after_rewound", None)
            save(p)
            return M.Missions(p.data).view()
        if act == "start":
            ms.start(erp)
        out = ms.update(erp, b.get("counters"), b.get("mission"))
        save(p)
        out["class"] = class_before()
        return out

    def class_before():
        tot = [M.Missions(p.data).totals() for p in players.all()]
        tot = [t for t in tot if t and t["missions_done"] == len(M.MISSIONS)]
        if not tot:
            return None
        n = len(tot)
        return {"players": n, **{k: round(sum(t[k] for t in tot) / n, 1) for k in ("seconds", "clicks", "keys",
                                                                                 "screens", "errors", "signins")}}

    # ------------------------------------------------------------------ the After
    def inr(n):
        """Indian digit grouping: 280840 -> 2,80,840."""
        s_ = f"{int(round(n or 0))}"
        if len(s_) <= 3:
            return s_
        head, tail = s_[:-3], s_[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        return ",".join(([head] if head else []) + parts) + "," + tail

    WORD = {"DR": "draft", "PA": "waiting for approval", "AP": "approved", "RL": "released", "CL": "closed"}

    def track(pid):
        st = M.state_of(players.erp(pid))
        pr, po = st["pr"], st["po"]
        steps = [
            {"k": "request", "label": "Request raised", "done": bool(pr and pr["status"] in ("PA", "AP", "CL")),
             "detail": f"{pr['pr_no']} · est ₹{inr(pr['est_value'])}" if pr else ""},
            {"k": "approved", "label": "Approved by Rohit", "done": bool(pr and pr["status"] in ("AP", "CL")),
             "detail": (f"by {pr['approved_by']}" if pr and pr["approved_by"] else
                        ("waiting for Rohit" if pr and pr["status"] == "PA" else ""))},
            {"k": "order", "label": "Purchase order", "done": bool(po and po["status"] in ("AP", "RL", "CL")),
             "detail": f"{po['po_no']} · {WORD.get(po['status'], po['status'])} · ₹{inr(po['gross_value'])}" if po else ""},
            {"k": "released", "label": "Released to Deccan", "done": bool(po and po["status"] in ("RL", "CL")),
             "detail": ("Monday " + po["released_on"][11:16]) if po and po["released_on"] else ""},
            {"k": "received", "label": "Received at stores", "done": bool(po and po["status"] == "CL"),
             "detail": f"{inr(st['received'])} of 20,000" if po and st["received"] else ""},
        ]
        return {"steps": steps, "pr": pr and {k: pr[k] for k in ("pr_no", "status", "est_value", "cc_cd", "approved_by")},
                "po": po and {k: po[k] for k in ("po_no", "status", "gross_value", "cc_cd", "released_on")},
                "grns": st["grns"], "stock": st["stock"]}

    def after_metrics(p, pid, kind: str, text: str = "", res: dict | None = None, tap: bool = False):
        a = p.data.setdefault("after", {})
        now = time.time()
        if kind == "message":
            a.setdefault("t_first", now)
            a["messages"] = a.get("messages", 0) + 1
            if tap:
                a["taps"] = a.get("taps", 0) + 1
            else:
                a["chars"] = a.get("chars", 0) + len(text)
            if res:
                a["tool_calls"] = a.get("tool_calls", 0) + len(res.get("cards") or [])
                a["tool_errors"] = a.get("tool_errors", 0) + sum(
                    1 for c in res.get("cards") or [] if isinstance(c.get("result"), dict) and c["result"].get("ok") is False)
                a["model_calls"] = a.get("model_calls", 0) + res.get("model_calls", 0)
                a["cost_inr"] = round(a.get("cost_inr", 0) + res.get("cost_inr", 0), 4)
                a["tokens"] = a.get("tokens", 0) + res.get("tokens_in", 0) + res.get("tokens_out", 0)
        elif kind == "tap":
            a.setdefault("t_first", now)
            a["taps"] = a.get("taps", 0) + 1
        t = track(pid)
        s = {x["k"]: x["done"] for x in t["steps"]}
        for k in ("request", "approved", "released", "received"):
            if s[k] and f"t_{k}" not in a and "t_first" in a:
                a[f"t_{k}"] = now
                a[f"msgs_{k}"] = a.get("messages", 0)
                a[f"cost_{k}"] = a.get("cost_inr", 0)
        save(p)
        return t

    @app.post("/api/after/enter")
    def after_enter(req: Request):
        """First visit to the After: if the Before left an order in this Rasoi, rewind it to Monday 9:00, so the
        same order can be placed again with the same numbers (PR/2026/04417, PO/2026/01182)."""
        p = player(req)
        rewound = False
        if not p.data.get("after_rewound"):
            erp = players.erp(p.pid)
            with erp.lock:
                used = erp.q1("SELECT COUNT(*) n FROM pr_hdr")["n"] + erp.q1(
                    "SELECT COUNT(*) n FROM po_hdr WHERE po_no>='PO/2026/01182'")["n"]
            if used:
                players.reset(p.pid)
                agents.drop(p.pid)
                rewound = True
            p.data["after_rewound"] = True
            p.data["after"] = {}
            save(p)
        return {"rewound": rewound}

    @app.post("/api/after/reset")
    def after_reset(req: Request):
        p = player(req)
        players.reset(p.pid)
        agents.drop(p.pid)
        p.data["after"] = {}
        p.data["after_rewound"] = True
        save(p)
        return {"ok": True}

    @app.get("/api/after/state")
    def after_state(req: Request):
        p = player(req)
        tb = players.toolbox(p.pid, "RMEHTA", ["list_my_approvals"])
        inbox = tb.call("list_my_approvals", {})
        ms = M.Missions(p.data)
        return {"track": track(p.pid), "inbox": inbox.get("waiting", []), "after": p.data.get("after", {}),
                "before": ms.totals(), "before_done": ms.current is None, "class_before": class_before(),
                "wishlist": p.data.get("wishlist"), "name": p.name, "budget_ok": guard.budget_ok(),
                "model_enabled": guard.flags().get("model_enabled", True)}

    @app.post("/api/inbox/decide")
    async def inbox_decide(req: Request):
        """Rohit's one tap: approve (or reject) with HIS OWN Bahi session, so Bahi checks his limit."""
        p = player(req)
        b = await req.json()
        doc_type, doc_no, decision = b.get("doc_type"), b.get("doc_no"), b.get("decision", "approve")
        tb = players.toolbox(p.pid, "RMEHTA")
        if doc_type == "PR":
            r = tb.call("approve_purchase_request", {"request_no": doc_no, "decision": decision,
                                                     "comment": "Approved in Ask Rasoi"})
        else:
            r = tb.call("approve_purchase_order", {"po_no": doc_no, "comment": "Approved in Ask Rasoi"}) \
                if decision == "approve" else {"ok": False, "error": "Reject an order in Bahi with a comment."}
        t = after_metrics(p, p.pid, "tap")
        return {"result": r, "track": t}

    @app.post("/api/chat")
    async def chat(req: Request):
        p = player(req)
        b = await req.json()
        text = str(b.get("text", "")).strip()[:1500]
        if not text:
            raise HTTPException(400, "Type a message.")
        user = PERSONS.get(str(b.get("person", "kavita")), "KJOSHI")
        stage = b.get("stage") if b.get("stage") in STAGES else "agent"
        guard.check(p.pid)
        a = agents.get(p.pid, user, stage)
        if not a.busy.acquire(blocking=False):
            raise HTTPException(409, "Still working on your last message.")
        try:
            res = await asyncio.get_running_loop().run_in_executor(pool, a.respond, text)
        except Refused:
            raise
        except Exception as e:  # noqa: BLE001
            print("[chat] error:", type(e).__name__, str(e)[:400])
            raise HTTPException(502, "Ask Rasoi could not reach its model just now. Try again in a moment.")
        finally:
            a.busy.release()
        guard.add(None, message=True)
        t = after_metrics(p, p.pid, "message", text, res, bool(b.get("tap"))) if stage == "agent" else track(p.pid)
        return {**res, "track": t}

    @app.get("/api/chat/history")
    def chat_history(req: Request, person: str = "kavita", stage: str = "agent"):
        p = player(req)
        a = agents.peek(p.pid, PERSONS.get(person, "KJOSHI"), stage if stage in STAGES else "agent")
        return {"transcript": a.transcript if a else []}

    # ------------------------------------------------------------------ the toolbox explorer
    @app.get("/api/tools")
    def tools():
        from ..toolbox import SPECS

        return {"tools": [s.card() for s in SPECS.values()]}

    @app.post("/api/tools/{name}")
    async def try_tool(name: str, req: Request):
        p = player(req)
        b = await req.json()
        user = PERSONS.get(str(b.get("person", "kavita")), "KJOSHI")
        guard_rate(p.pid)
        tb = players.toolbox(p.pid, user)
        t0 = time.perf_counter()
        out = await asyncio.get_running_loop().run_in_executor(pool, tb.call, name, b.get("args") or {})
        return {"result": out, "ms": round((time.perf_counter() - t0) * 1000), "person": user}

    def guard_rate(pid):
        from collections import deque
        now = time.monotonic()
        q = guard.hits.setdefault(pid + "/tools", deque())
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= 60:
            raise HTTPException(429, "Too many tool runs in a minute. Wait a little.")
        q.append(now)

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        ps = players.all()
        return {"flags": guard.flags(), "spend_today": guard.spent(), "day_ist": guard.today(),
                "players": len(ps), "conversations": agents.count(),
                "wishlists": sum(1 for p in ps if p.data.get("wishlist")),
                "before_finished": sum(1 for p in ps if M.Missions(p.data).current is None),
                "after_ordered": sum(1 for p in ps if (p.data.get("after") or {}).get("t_released")),
                "class_before": class_before(), "studio": STUDIO,
                "recent": [{"pid": p.pid, "name": p.name, "missions": len((p.data.get("before") or {}).get("results", {})),
                            "after": bool((p.data.get("after") or {}).get("t_released"))}
                           for p in sorted(ps, key=lambda p: -p.joined_on)[:60]]}

    @app.post("/api/admin/flags")
    async def admin_flags(req: Request):
        admin(req)
        b = await req.json()
        kw = {}
        if "model_enabled" in b:
            kw["model_enabled"] = bool(b["model_enabled"])
        if "reason" in b:
            kw["reason"] = str(b["reason"])[:200]
        if "cap_inr" in b:
            kw["cap_inr"] = float(b["cap_inr"])
        return guard.set_flags(**kw)

    @app.post("/api/admin/reset_player")
    async def admin_reset(req: Request):
        admin(req)
        b = await req.json()
        pid = b.get("pid")
        p = players.get(pid)
        if not p:
            raise HTTPException(404, "No such player.")
        players.reset(pid)
        agents.drop(pid)
        if b.get("wipe"):
            p.data = {}
            save(p)
        return {"ok": True}

    # ------------------------------------------------------------------ the Workflow Studio (another builder's)
    STUDIO = {"ok": False}
    try:
        try:
            from .studio import make_router  # noqa: WPS433
        except ImportError:
            from .studio.api import make_router  # noqa: WPS433

        app.include_router(make_router(players))
        STUDIO["ok"] = True
    except ImportError as e:
        STUDIO["error"] = f"not installed yet ({e})"

        @app.get("/studio", response_class=HTMLResponse)
        def studio_placeholder():
            return page("studio_soon.html")
    except Exception as e:  # noqa: BLE001  (a broken studio must not take the Experience down)
        STUDIO["error"] = f"{type(e).__name__}: {e}"[:300]

        @app.get("/studio", response_class=HTMLResponse)
        def studio_broken():
            return page("studio_soon.html")

    @app.get("/index.html")
    def index_alias():
        return RedirectResponse("/")

    def warm():  # build the policy index once, so the first policy question is not slow
        try:
            from ..agent.retrieval import search_policy
            search_policy("Can we buy food-contact parts from a supplier without a certificate?")
        except Exception as e:  # noqa: BLE001
            print("warm search_policy failed:", type(e).__name__, str(e)[:200])

    import threading
    threading.Thread(target=warm, daemon=True).start()
    return app


app = create_app() if os.environ.get("RASOI_NO_APP") != "1" else None
