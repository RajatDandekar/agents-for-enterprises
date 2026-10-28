"""Lecture 9 · self-hosted n8n runs the L6 Diwali workflow, every Bahi step an MCP call to the Rasoi toolbox.

    cd /Users/raj/Claude_Brain/enterprise-agents-course
    tools/mrun.sh lectures/L9-protocols/experiments/n8n_modal.py --mode probe   # which MCP nodes n8n ships
    tools/mrun.sh lectures/L9-protocols/experiments/n8n_modal.py               # the real run + screenshots

Everything runs in one throwaway Modal container on localhost:
  * one Python thread serves the toolbox over streamable HTTP on ONE shared Bahi sandbox:
      /kavita/mcp  = build_toolbox_server(erp, "KJOSHI")   (Kavita's own permissions)
      /rohit/mcp   = build_toolbox_server(erp, "RMEHTA")   (Rohit's, used only by the script acting as Rohit)
  * n8n 2.45.5 (`n8n start`, sqlite) with a generated test owner account (never printed or saved)
  * the workflow experiments/n8n/diwali_mcp.json is imported, triggered by its webhook, pauses at a Wait node,
    the script approves PR as Rohit over MCP, then calls the Wait node's resume URL
  * Playwright screenshots -> figs/shots/n8n_*.png ; log -> experiments/logs/n8n_run.json
"""
import json
import os
import pathlib
import subprocess
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = "lectures/L9-protocols"
SKIP = {".git", "node_modules", "__pycache__", "cassettes", "_index", ".ipynb_checkpoints", "qa", "site-dist", ".venv"}
NODE = "v24.22.1"
N8N = "2.45.5"
FASTMCP = "4.1.4"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "xz-utils", "ca-certificates")
    .run_commands(
        f"curl -fsSL https://nodejs.org/dist/{NODE}/node-{NODE}-linux-x64.tar.xz -o /tmp/node.tar.xz",
        "mkdir -p /opt/node && tar -xJf /tmp/node.tar.xz -C /opt/node --strip-components=1 && rm /tmp/node.tar.xz",
    )
    .env({"PATH": "/opt/node/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"})
    .run_commands(f"npm install -g n8n@{N8N} --no-audit --no-fund --loglevel=error")
    .pip_install(f"fastmcp=={FASTMCP}", "mcp", "uvicorn", "starlette", "httpx", "pydantic>=2", "pyyaml", "pandas",
                 "openai>=1.50", "playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or "archive" in pathlib.Path(p).parts
                   or str(p).endswith((".ipynb", ".jsonl", ".mp4", ".mov", ".zip", ".env", ".png", ".jpg")))
)
app = modal.App("l9-n8n-mcp", image=image)

N8N_ENV = {"N8N_USER_FOLDER": "/tmp/n8n", "DB_TYPE": "sqlite", "N8N_DIAGNOSTICS_ENABLED": "false",
           "N8N_SECURE_COOKIE": "false", "N8N_PORT": "5678", "N8N_HOST": "localhost", "N8N_PROTOCOL": "http",
           "WEBHOOK_URL": "http://localhost:5678/", "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": "false",
           "N8N_PERSONALIZATION_ENABLED": "false", "N8N_VERSION_NOTIFICATIONS_ENABLED": "false",
           "N8N_TEMPLATES_ENABLED": "false", "N8N_HIRING_BANNER_ENABLED": "false", "GENERIC_TIMEZONE": "Asia/Kolkata",
           "N8N_RUNNERS_ENABLED": "true", "N8N_BLOCK_ENV_ACCESS_IN_NODE": "false", "N8N_LOG_LEVEL": "info"}


def _sh(cmd, **kw):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return (p.stdout + p.stderr).strip()


# ----------------------------------------------------------------------------------------------- probe
@app.function(timeout=900, cpu=2, memory=4096)
def probe() -> dict:
    out = {"node": _sh("node --version"), "n8n": _sh("n8n --version")}
    root = _sh("npm root -g")
    out["npm_root"] = root
    out["mcp_files"] = _sh(f"find {root}/n8n -path '*nodes*' -iname '*mcp*' -name '*.node.js' 2>/dev/null | head -40").splitlines()
    out["mcp_dirs"] = _sh(f"find {root}/n8n -type d -ipath '*nodes*mcp*' 2>/dev/null | grep -v node_modules/.*/node_modules | head -40").splitlines()
    # describe each MCP node: name, displayName, version, top-level parameter names
    js = r"""
const path=require('path');const files=process.argv.slice(2);const out=[];
for(const f of files){try{const m=require(f);for(const k of Object.keys(m)){const C=m[k];if(typeof C!=='function')continue;
 let inst;try{inst=new C();}catch(e){continue}
 const descs=[];if(inst.description)descs.push(inst.description);
 if(inst.nodeVersions){for(const v of Object.values(inst.nodeVersions)){if(v.description)descs.push(v.description)}}
 for(const d of descs){out.push({file:path.basename(f),cls:k,name:d.name,displayName:d.displayName,version:d.version,
   defaultVersion:d.defaultVersion,group:d.group,inputs:d.inputs,outputs:d.outputs,credentials:(d.credentials||[]).map(c=>c.name),
   params:(d.properties||[]).map(p=>({name:p.name,type:p.type,default:p.default,options:(p.options||[]).map(o=>o.value||o.name).slice(0,12),
     show:p.displayOptions&&p.displayOptions.show}))})}}}catch(e){out.push({file:f,err:String(e).slice(0,300)})}}
console.log(JSON.stringify(out));"""
    pathlib.Path("/tmp/desc.js").write_text(js)
    if out["mcp_files"]:
        raw = _sh("cd /tmp && node /tmp/desc.js " + " ".join(out["mcp_files"]))
        try:
            out["mcp_nodes"] = json.loads(raw.splitlines()[-1])
        except Exception:
            out["mcp_nodes_raw"] = raw[-4000:]
    # credentials for MCP
    out["mcp_creds"] = _sh(f"find {root}/n8n -path '*credentials*' -iname '*mcp*' 2>/dev/null | head -20").splitlines()
    import fastmcp
    from fastmcp import FastMCP
    out["fastmcp"] = fastmcp.__version__
    out["fastmcp_app_methods"] = [m for m in dir(FastMCP) if "app" in m.lower() or "http" in m.lower()]
    import inspect
    if hasattr(FastMCP, "http_app"):
        out["http_app_sig"] = str(inspect.signature(FastMCP.http_app))
    return {f"{HERE}/experiments/logs/n8n_probe.json": json.dumps(out, indent=1).encode()}


# ----------------------------------------------------------------------------------------------- toolbox servers
REQS = []  # the HTTP requests the toolbox received


def start_toolbox(port=8765):
    import threading

    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Mount

    from bahi.erp.engine import ERP
    from bahi.toolbox.mcp import build_toolbox_server

    erp = ERP()
    kav = build_toolbox_server(erp, "KJOSHI", name="bahi-toolbox-kavita")
    roh = build_toolbox_server(erp, "RMEHTA", name="bahi-toolbox-rohit")
    kapp, rapp = kav.http_app(path="/mcp"), roh.http_app(path="/mcp")

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(a):
        async with kapp.lifespan(kapp), rapp.lifespan(rapp):
            yield

    star = Starlette(routes=[Mount("/kavita", app=kapp), Mount("/rohit", app=rapp)], lifespan=lifespan)

    class Log:
        def __init__(self, inner):
            self.inner = inner

        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                return await self.inner(scope, receive, send)
            body = b""
            chunks = []

            async def rcv():
                m = await receive()
                if m["type"] == "http.request":
                    chunks.append(m.get("body", b""))
                return m

            rec = {"t": round(time.time(), 3), "method": scope["method"], "path": scope["path"],
                   "ua": dict((k.decode(), v.decode()) for k, v in scope["headers"]).get("user-agent", "")[:60]}

            async def snd(m):
                if m["type"] == "http.response.start":
                    rec["status"] = m["status"]
                return await send(m)

            await self.inner(scope, rcv, snd)
            body = b"".join(chunks)
            try:
                j = json.loads(body) if body else None
                if isinstance(j, dict):
                    rec["rpc"] = j.get("method")
                    if j.get("method") == "tools/call":
                        rec["tool"] = j["params"].get("name")
                        rec["args"] = j["params"].get("arguments")
            except Exception:
                rec["body"] = body[:120].decode(errors="replace")
            REQS.append(rec)

    th = threading.Thread(target=lambda: uvicorn.run(Log(star), host="127.0.0.1", port=port, log_level="warning"),
                          daemon=True)
    th.start()
    for _ in range(60):
        try:
            import httpx
            httpx.get(f"http://127.0.0.1:{port}/kavita/mcp", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    return erp


async def mcp_call(url, tool, args):
    from fastmcp import Client
    async with Client(url) as c:
        r = await c.call_tool(tool, args)
        return json.loads(r.content[0].text)


# ----------------------------------------------------------------------------------------------- the run
@app.function(timeout=2400, cpu=4, memory=8192)
def run(workflow_json: str) -> dict:
    import asyncio

    import httpx

    t_start = time.time()
    files, log = {}, {"versions": {"node": _sh("node --version"), "n8n": _sh("n8n --version"), "fastmcp": FASTMCP}}
    erp = start_toolbox()
    log["toolbox_check"] = asyncio.run(mcp_call("http://127.0.0.1:8765/kavita/mcp", "check_stock",
                                                {"item_code": "GSK-SIL-05L"}))
    REQS.clear()

    env = {**os.environ, **N8N_ENV}
    n8n_log = open("/tmp/n8n.log", "w")
    proc = subprocess.Popen(["n8n", "start"], env=env, stdout=n8n_log, stderr=subprocess.STDOUT)
    base = "http://localhost:5678"
    for i in range(240):
        try:
            if httpx.get(base + "/healthz", timeout=2).status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)
    time.sleep(3)
    log["n8n_boot_seconds"] = round(time.time() - t_start, 1)

    import secrets
    email, pw = "owner@rasoi.test", "T" + secrets.token_hex(8) + "a1!"  # throwaway test owner, never logged
    s = httpx.Client(base_url=base, timeout=60)
    r = s.post("/rest/owner/setup", json={"email": email, "firstName": "Course", "lastName": "Builder", "password": pw})
    log["owner_setup_status"] = r.status_code
    r = s.post("/rest/login", json={"emailOrLdapLoginId": email, "email": email, "password": pw})
    log["login_status"] = r.status_code
    if r.status_code >= 400:
        log["login_err"] = r.text[:300]
    # skip the personalization survey if asked
    for path, body in [("/rest/me/survey", {"version": "v4", "personalization_survey_submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "personalization_survey_n8n_version": N8N})]:
        try:
            log.setdefault("survey", s.post(path, json=body).status_code)
        except Exception as e:
            log["survey"] = str(e)[:100]

    wf = json.loads(workflow_json)
    body = {k: wf[k] for k in ("name", "nodes", "connections", "settings") if k in wf}
    r = s.post("/rest/workflows", json=body)
    log["import_status"] = r.status_code
    if r.status_code >= 400:
        log["import_err"] = r.text[:1500]
    wid = r.json()["data"]["id"]
    vid = r.json()["data"].get("versionId")
    log["workflow_id"] = wid
    # activate (n8n 2: POST /rest/workflows/:id/activate with versionId; older: PATCH active)
    act = s.post(f"/rest/workflows/{wid}/activate", json={"versionId": vid})
    if act.status_code >= 400:
        act2 = s.patch(f"/rest/workflows/{wid}", json={"active": True, "versionId": vid})
        log["activate"] = [act.status_code, act.text[:300], act2.status_code, act2.text[:300]]
    else:
        log["activate"] = [act.status_code]
    time.sleep(2)

    # --- trigger
    t_trig = time.time()
    trig = httpx.post(base + "/webhook/diwali-gasket-order", json={"item_code": "GSK-SIL-05L", "quantity": 20000},
                      timeout=120)
    log["trigger"] = {"status": trig.status_code, "body": trig.text[:600]}

    def executions():
        r = s.get("/rest/executions", params={"filter": json.dumps({"workflowId": wid}), "limit": 10})
        d = r.json().get("data", {})
        return d.get("results", d if isinstance(d, list) else [])

    ex = None
    for _ in range(90):
        rows = executions()
        if rows:
            ex = rows[0]
            if ex.get("status") in ("waiting", "success", "error", "crashed"):
                break
        time.sleep(1)
    log["waiting_execution"] = {k: ex.get(k) for k in ("id", "status", "startedAt", "waitTill", "mode")} if ex else None
    eid = ex["id"] if ex else None

    # --- screenshots helper
    from playwright.sync_api import sync_playwright
    pw_ctx = sync_playwright().start()
    browser = pw_ctx.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(base + "/signin")
    page.wait_for_timeout(2500)
    try:
        page.fill("input[type=email], input[name=emailOrLdapLoginId], input[name=email]", email)
        page.fill("input[type=password]", pw)
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)
    except Exception as e:
        log["ui_login_err"] = str(e)[:300]

    def tidy():
        # dismiss modals, toasts and banners that cover the canvas
        for _ in range(3):
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
        page.evaluate("""() => { for (const sel of ['.el-overlay','.el-notification','[data-test-id=\"banners\"]',
            '.n8n-callout','[class*=\"Banner\"]','[data-test-id=\"ask-assistant-floating-button\"]']) {
            document.querySelectorAll(sel).forEach(e => e.remove()) } }""")
        page.wait_for_timeout(300)

    def shot(name):
        tidy()
        data = page.screenshot()
        files[f"{HERE}/figs/shots/{name}.png"] = data
        return name

    shots = log.setdefault("screenshots", {})
    page.goto(f"{base}/workflow/{wid}")
    page.wait_for_timeout(5000)
    tidy()
    try:
        page.keyboard.press("Shift+1")  # zoom to fit
    except Exception:
        pass
    page.wait_for_timeout(800)
    shots["n8n_01_canvas"] = shot("n8n_01_canvas")
    # open an MCP node's parameter panel
    try:
        page.get_by_text("Raise the PR", exact=True).first.dblclick()
        page.wait_for_timeout(2500)
        shots["n8n_02_mcp_node_params"] = shot("n8n_02_mcp_node_params")
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
    except Exception as e:
        log["shot_params_err"] = str(e)[:300]

    if eid:
        page.goto(f"{base}/workflow/{wid}/executions/{eid}")
        page.wait_for_timeout(6000)
        shots["n8n_03_waiting_for_rohit"] = shot("n8n_03_waiting_for_rohit")

    # --- Rohit approves, as himself, over MCP
    full = s.get(f"/rest/executions/{eid}").json().get("data", {}) if eid else {}
    pr_no = None
    try:
        from bahi.erp.engine import ERP  # noqa: F401
        rd = full.get("data")
        log["waiting_data_type"] = type(rd).__name__
    except Exception:
        pass
    # the PR number: read from the toolbox requests' result is not logged, so ask Rohit's inbox
    inbox = asyncio.run(mcp_call("http://127.0.0.1:8765/rohit/mcp", "list_my_approvals", {}))
    log["rohit_inbox"] = inbox
    try:
        w = inbox.get("waiting") or []
        pr_no = next(x.get("request_no") or x.get("doc_no") for x in w if "PR/" in json.dumps(x))
    except Exception:
        pr_no = None
    log["pr_no_from_inbox"] = pr_no
    t_appr = time.time()
    log["rohit_approval"] = asyncio.run(mcp_call("http://127.0.0.1:8765/rohit/mcp", "approve_purchase_request",
                                                 {"request_no": pr_no, "decision": "approve",
                                                  "comment": "Approved for the Diwali run."}))
    log["rohit_approval_seconds"] = round(time.time() - t_appr, 3)
    # resume the Wait node
    resume = f"{base}/webhook-waiting/{eid}"
    rr = httpx.post(resume, json={"approved_by": "RMEHTA", "request_no": pr_no}, timeout=120)
    log["resume"] = {"url": resume.replace(base, ""), "status": rr.status_code, "body": rr.text[:300]}
    for _ in range(90):
        ex = s.get(f"/rest/executions/{eid}").json().get("data", {})
        if ex.get("status") in ("success", "error", "crashed"):
            break
        time.sleep(1)
    log["final_status"] = ex.get("status")
    log["execution_id"] = eid
    log["startedAt"], log["stoppedAt"] = ex.get("startedAt"), ex.get("stoppedAt")
    log["trigger_to_finish_seconds"] = round(time.time() - t_trig, 1)

    # per-node results (n8n stores run data "flatted"; ask the API for the parsed form via includeData)
    run_data = None
    raw = ex.get("data")
    if isinstance(raw, str):
        try:
            run_data = _unflatten(json.loads(raw))
        except Exception as e:
            log["unflatten_err"] = str(e)[:200]
    elif isinstance(raw, dict):
        run_data = raw
    nodes = []
    if run_data:
        rd = run_data.get("resultData", {}).get("runData", {})
        for name, runs in rd.items():
            for r_ in runs:
                outj = None
                try:
                    outj = [it.get("json") for it in r_["data"]["main"][0]][:2]
                except Exception:
                    outj = r_.get("error")
                nodes.append({"node": name, "status": r_.get("executionStatus"), "startTime": r_.get("startTime"),
                              "executionTime_ms": r_.get("executionTime"),
                              "output": json.loads(json.dumps(outj, default=str)[:3000]) if outj else None})
        nodes.sort(key=lambda n: n["startTime"] or 0)
    log["nodes_run"] = nodes

    page.goto(f"{base}/workflow/{wid}/executions/{eid}")
    page.wait_for_timeout(6000)
    shots["n8n_04_finished"] = shot("n8n_04_finished")
    # open the PR node in the finished execution to show its output
    for label, nm in [("Raise the PR", "n8n_05_pr_output"), ("Release to supplier", "n8n_06_release_output")]:
        try:
            frame = page.frame_locator("iframe").first if page.locator("iframe").count() else page
            frame.get_by_text(label, exact=True).first.dblclick()
            page.wait_for_timeout(2500)
            shots[nm] = shot(nm)
            page.keyboard.press("Escape")
            page.wait_for_timeout(800)
        except Exception as e:
            log[f"shot_{nm}_err"] = str(e)[:300]
    browser.close()
    pw_ctx.stop()

    # Bahi's final state, read back directly
    from bahi.toolbox import Toolbox
    tb = Toolbox(erp, "KJOSHI")
    st = tb.call("check_stock", {"item_code": "GSK-SIL-05L"})
    po_no = None
    for n in nodes:
        o = n.get("output")
        if isinstance(o, list) and o and isinstance(o[0], dict):
            po_no = po_no or _dig(o[0], "po_no")
    log["bahi_final"] = {"pr": tb.call("order_status", {"request_no": pr_no}) if pr_no else None,
                         "po": tb.call("order_status", {"po_no": po_no}) if po_no else None,
                         "stock": st}
    log["toolbox_requests"] = REQS
    log["toolbox_request_count"] = len(REQS)
    log["tools_called"] = [r["tool"] for r in REQS if r.get("tool")]
    log["total_wall_seconds"] = round(time.time() - t_start, 1)
    proc.terminate()
    n8n_log.close()
    log["n8n_log_tail"] = pathlib.Path("/tmp/n8n.log").read_text()[-3000:]
    files[f"{HERE}/experiments/logs/n8n_run.json"] = json.dumps(log, indent=1, ensure_ascii=False, default=str).encode()
    return files


def _dig(o, key):
    if isinstance(o, dict):
        if key in o and o[key]:
            return o[key]
        for v in o.values():
            r = _dig(v, key)
            if r:
                return r
    if isinstance(o, list):
        for v in o:
            r = _dig(v, key)
            if r:
                return r
    if isinstance(o, str) and o.startswith("{"):
        try:
            return _dig(json.loads(o), key)
        except Exception:
            return None
    return None


def _unflatten(arr):
    """n8n stores execution data with the `flatted` format: a list where strings that are digits point to indexes."""
    seen = {}

    def rev(i):
        if i in seen:
            return seen[i]
        v = arr[i]
        if isinstance(v, dict):
            out = {}
            seen[i] = out
            for k, x in v.items():
                out[k] = rev(int(x)) if isinstance(x, str) and x.isdigit() else x
            return out
        if isinstance(v, list):
            out = []
            seen[i] = out
            for x in v:
                out.append(rev(int(x)) if isinstance(x, str) and x.isdigit() else x)
            return out
        return v

    return rev(0)


@app.local_entrypoint()
def main(mode: str = "run"):
    if mode == "probe":
        files = probe.remote()
    else:
        wf = (ROOT / HERE / "experiments" / "n8n" / "diwali_mcp.json").read_text()
        files = run.remote(wf)
    for rel, data in files.items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", rel, len(data))
    k = [r for r in files if r.endswith(".json") and "/logs/" in r]
    if k:
        print(files[k[0]].decode()[:6000])
