"""Lecture 9 · MCP Inspector (v2.12.0) on Ask Rasoi's toolbox, in one throwaway Modal container on localhost.

    cd /Users/raj/Claude_Brain/enterprise-agents-course
    tools/mrun.sh lectures/L9-protocols/experiments/inspector_modal.py --mode probe   # connect, dump the UI
    tools/mrun.sh lectures/L9-protocols/experiments/inspector_modal.py               # CLI runs + screenshots

Inside the container:
  * our official-SDK server (bahi.course.protocols.rasoi_mcp, mcp 2.3.0) serves Kavita's toolbox over
    streamable HTTP at http://127.0.0.1:8765/mcp;
  * the Inspector's CLI mode lists tools / resources / prompts over stdio (the same server, spawned);
  * the Inspector's web UI (Node backend on :6274) is opened by headless Chromium with the per-launch API token
    (a random value generated in the container, never written to a file) through the documented deep link;
  * screenshots -> figs/shots/inspector_*.png, log -> experiments/logs/inspector_run.json
"""
import json
import os
import pathlib
import secrets
import subprocess
import time

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[3] if len(_P.parents) > 3 else pathlib.Path("/course")
HERE = "lectures/L9-protocols"
SKIP = {".git", "node_modules", "__pycache__", "cassettes", "_index", ".ipynb_checkpoints", "qa", "site-dist", ".venv"}
NODE = "v24.22.1"
INSPECTOR = "2.12.0"
MCP = "2.3.0"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "xz-utils", "ca-certificates")
    .run_commands(
        f"curl -fsSL https://nodejs.org/dist/{NODE}/node-{NODE}-linux-x64.tar.xz -o /tmp/node.tar.xz",
        "mkdir -p /opt/node && tar -xJf /tmp/node.tar.xz -C /opt/node --strip-components=1 && rm /tmp/node.tar.xz",
    )
    .env({"PATH": "/opt/node/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"})
    .run_commands(f"npm install -g @modelcontextprotocol/inspector@{INSPECTOR} --no-audit --no-fund --loglevel=error")
    .pip_install(f"mcp=={MCP}", "uvicorn", "starlette", "httpx", "pydantic>=2", "pyyaml", "pandas", "openai>=1.50",
                 "playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or "archive" in pathlib.Path(p).parts
                   or str(p).endswith((".ipynb", ".jsonl", ".mp4", ".mov", ".zip", ".env", ".png", ".jpg")))
)
app = modal.App("l9-mcp-inspector", image=image)

SERVER_CMD = ["python", "-m", "bahi.course.protocols.rasoi_mcp", "--user", "KJOSHI"]
MCP_URL = "http://127.0.0.1:8765/mcp"


def _sh(cmd, timeout=120, env=None):
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout, env=env)
    return {"rc": p.returncode, "out": p.stdout[-12000:], "err": p.stderr[-4000:]}


def _wait_port(port, secs=60):
    import socket
    t = time.time()
    while time.time() - t < secs:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


CATALOG = {"mcpServers": {
    "rasoi-toolbox-stdio": {"type": "stdio", "command": "python", "args": SERVER_CMD[1:],
                            "env": {"PYTHONPATH": "/course/bahi"}, "cwd": "/course", "protocolEra": "modern"},
    "rasoi-toolbox-http": {"type": "http", "url": MCP_URL, "protocolEra": "modern"}}}


def _start(log, mode="full"):
    env = {**os.environ, "HOME": "/tmp/insp_home"}
    os.makedirs("/tmp/insp_home", exist_ok=True)
    with open("/tmp/insp_home/rasoi.json", "w") as f:
        json.dump(CATALOG, f)
    log["catalog"] = CATALOG
    srv = subprocess.Popen(SERVER_CMD + ["--http", "8765"], cwd="/course", env=env,
                           stdout=open("/tmp/server.log", "w"), stderr=subprocess.STDOUT)
    log["server_up"] = _wait_port(8765)
    token = secrets.token_hex(16)
    ienv = {**env, "MCP_INSPECTOR_API_TOKEN": token, "MCP_AUTO_OPEN_ENABLED": "false", "CLIENT_PORT": "6274"}
    args = ["mcp-inspector", "--web"] + ([] if mode == "probe" else ["--catalog", "/tmp/insp_home/rasoi.json"])
    log["web_cmd"] = " ".join(args)
    insp = subprocess.Popen(args, env=ienv, cwd="/tmp",
                            stdout=open("/tmp/inspector.log", "w"), stderr=subprocess.STDOUT)
    log["inspector_up"] = _wait_port(6274, 90)
    time.sleep(2)
    return srv, insp, token


def _banner():
    txt = open("/tmp/inspector.log").read()
    # never keep the token: strip anything that looks like it
    import re
    return re.sub(r"[0-9a-f]{32}", "<token>", txt)[-3000:]


def _cli(log):
    env = {**os.environ, "HOME": "/tmp/insp_home"}
    runs = {}
    for name, args in [
        ("version", ["mcp-inspector", "--cli", "--version"]),
        ("initialize_stdio", ["mcp-inspector", "--cli", "--method", "initialize", "--format", "json", "--protocol-era", "modern", "-e", "PYTHONPATH=/course/bahi", "--cwd", "/course", "--"] + SERVER_CMD),
        ("tools_list_stdio", ["mcp-inspector", "--cli", "--method", "tools/list", "--format", "json", "--protocol-era", "modern", "-e", "PYTHONPATH=/course/bahi", "--cwd", "/course", "--"] + SERVER_CMD),
        ("resources_list_stdio", ["mcp-inspector", "--cli", "--method", "resources/list", "--format", "json", "--protocol-era", "modern", "-e", "PYTHONPATH=/course/bahi", "--cwd", "/course", "--"] + SERVER_CMD),
        ("templates_list_stdio", ["mcp-inspector", "--cli", "--method", "resources/templates/list", "--format", "json", "--protocol-era", "modern", "-e", "PYTHONPATH=/course/bahi", "--cwd", "/course", "--"] + SERVER_CMD),
        ("prompts_list_stdio", ["mcp-inspector", "--cli", "--method", "prompts/list", "--format", "json", "--protocol-era", "modern", "-e", "PYTHONPATH=/course/bahi", "--cwd", "/course", "--"] + SERVER_CMD),
        ("check_stock_http", ["mcp-inspector", "--cli", MCP_URL, "--transport", "http", "--method", "tools/call",
                              "--tool-name", "check_stock", "--tool-arg", "item_code=GSK-SIL-05L", "--format", "json"]),
        ("initialize_http", ["mcp-inspector", "--cli", MCP_URL, "--transport", "http", "--method", "initialize", "--format", "json"]),
        ("initialize_http_modern", ["mcp-inspector", "--cli", MCP_URL, "--transport", "http", "--protocol-era", "modern",
                                    "--method", "initialize", "--format", "json"]),
        ("initialize_http_legacy", ["mcp-inspector", "--cli", MCP_URL, "--transport", "http", "--protocol-era", "legacy",
                                    "--method", "initialize", "--format", "json"]),
        ("tools_list_strict", ["mcp-inspector", "--cli", MCP_URL, "--transport", "http", "--method", "tools/list", "--strict",
                               "--format", "json"]),
    ]:
        t = time.time()
        r = _sh(args, timeout=120, env=env)
        r["seconds"] = round(time.time() - t, 2)
        r["cmd"] = " ".join(args)
        runs[name] = r
        print(name, r["rc"], r["out"][:300].replace("\n", " "), r["err"][:200].replace("\n", " "))
    log["cli"] = runs


def _dump(pg):
    return pg.evaluate("""() => {
      const q = (s) => [...document.querySelectorAll(s)];
      return {
        title: document.title,
        testids: [...new Set(q('[data-testid]').map(e => e.getAttribute('data-testid')))].slice(0, 200),
        tabs: q('[role=tab]').map(e => e.innerText.trim()).slice(0, 60),
        buttons: q('button').map(e => (e.innerText || e.getAttribute('aria-label') || '').trim()).filter(Boolean).slice(0, 120),
        status: (document.querySelector('[data-testid=connection-status]') || {}).outerHTML?.slice(0, 600),
        text: document.body.innerText.slice(0, 5000)
      };
    }""")


@app.function(timeout=1500, cpu=2, memory=4096)
def run(mode: str = "full") -> dict:
    from playwright.sync_api import sync_playwright
    log = {"versions": {"node": _sh("node --version")["out"].strip(), "inspector": INSPECTOR, "mcp": MCP},
           "server": " ".join(SERVER_CMD), "url": MCP_URL, "mode": mode, "shots": {}}
    files = {}
    srv, insp, token = _start(log, mode)
    log["banner"] = _banner()
    _cli(log)
    from urllib.parse import quote
    deep = (f"http://127.0.0.1:6274/?serverUrl={quote(MCP_URL, safe='')}&transport=http&autoConnect={token}"
            f"&MCP_INSPECTOR_API_TOKEN={token}")
    if mode != "probe":
        deep = f"http://127.0.0.1:6274/?MCP_INSPECTOR_API_TOKEN={token}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        try:
            pg.goto(deep, wait_until="load", timeout=60000)
        except Exception as e:  # noqa: BLE001
            log["goto_err"] = str(e).replace(token, "<token>")[:300]
        try:
            if mode != "probe":
                raise RuntimeError("full mode connects by clicking, below")
            pg.wait_for_selector('[data-testid=connection-status][data-status=connected]', timeout=30000)
            log["connected"] = True
        except Exception as e:  # noqa: BLE001
            log["connected"] = False
            log["connect_err"] = str(e).replace(token, "<token>")[:300]
        pg.wait_for_timeout(1500)

        def shot(name, what):
            files[f"{HERE}/figs/shots/{name}.png"] = pg.screenshot()
            log["shots"][name] = what

        shot("inspector_00_probe" if mode == "probe" else "inspector_00_start", "first page")
        log["dom_connect"] = _dump(pg)
        if mode == "probe":
            for tab in ["Tools", "Resources", "Prompts"]:
                try:
                    pg.get_by_role("tab", name=tab).first.click(timeout=5000)
                except Exception:  # noqa: BLE001
                    try:
                        pg.get_by_text(tab, exact=True).first.click(timeout=5000)
                    except Exception as e:  # noqa: BLE001
                        log[f"click_{tab}"] = str(e)[:200]
                        continue
                pg.wait_for_timeout(1500)
                shot(f"inspector_00_probe_{tab.lower()}", f"probe: {tab} tab")
                log[f"dom_{tab.lower()}"] = _dump(pg)
        else:
            import sys
            sys.path.insert(0, "/course/lectures/L9-protocols/experiments")
            from inspector_ui import drive  # the click script, kept beside this file
            try:
                drive(pg, shot, log)
            except Exception as e:  # noqa: BLE001
                log["drive_err"] = str(e).replace(token, "<token>")[:1500]
                shot("inspector_99_error", "state when the UI script failed")
                log["dom_error"] = _dump(pg)
        log["page_errors"] = errs
        b.close()
    log["server_log"] = open("/tmp/server.log").read()[-3000:]
    log["inspector_log"] = _banner()
    for proc in (srv, insp):
        proc.terminate()
    name = "inspector_probe.json" if mode == "probe" else "inspector_run.json"
    files[f"{HERE}/experiments/logs/{name}"] = json.dumps(log, indent=1, ensure_ascii=False).encode()
    return files


@app.local_entrypoint()
def main(mode: str = "full"):
    files = run.remote(mode)
    for rel, data in files.items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", rel, len(data))
