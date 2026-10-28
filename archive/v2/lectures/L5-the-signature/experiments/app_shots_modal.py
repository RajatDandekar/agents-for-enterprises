"""Screenshots of the real reference app, rendered on Modal in headless Chromium (never on the laptop).

    /Users/raj/.venv/bin/modal run lectures/L5-the-signature/experiments/app_shots_modal.py

Starts bahi.app (uvicorn) inside the container with the journey's recorded model replies (cassette L5_app, mode auto),
drives Kavita's order through the HTTP API exactly as the journey test does, and photographs the four pages at the
moments the deck shows: Kavita's chat waiting on Rohit, Rohit's inbox and his Slack-style message, the chat after
his tap, and the audit viewer. PNGs go to lectures/L5-the-signature/shots/.
"""
import os
import pathlib

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[3] if len(_P.parents) > 3 else pathlib.Path("/course")  # inside the container the script sits in /root
ENV_FILE = os.environ.get("BAHI_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SKIP = {".git", "node_modules", "__pycache__", ".ipynb_checkpoints", "qa", "shots"}


def _secret_env():
    env = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "pandas", "langgraph>=0.2",
                 "langchain-core", "fastmcp", "mcp", "temporalio", "rank_bm25", "numpy", "playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".ipynb", ".mp4", ".png", ".mov", ".zip")))
)
app = modal.App("forms-to-agents-l5-shots", image=image)


@app.function(secrets=[modal.Secret.from_dict(_secret_env())], timeout=1200, cpu=2, memory=4096)
def shots() -> dict:
    import threading
    import time

    import httpx
    import uvicorn
    from playwright.sync_api import sync_playwright

    os.environ["BAHI_LLM_MODE"] = "auto"
    from bahi.app.journey import OPENING, kavita_answer
    from bahi.app.main import create_app

    web = create_app(cassette="L5_app", durable=True, mcp=True)
    srv = uvicorn.Server(uvicorn.Config(web, host="127.0.0.1", port=8090, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.1)
    print("server up", flush=True)
    base = "http://127.0.0.1:8090"
    c = httpx.Client(base_url=base, timeout=300)
    K = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123"}).json()["token"]
    hk = {"Authorization": f"Bearer {K}"}
    conv = c.post("/api/chat", headers=hk).json()["conv"]
    text, log = OPENING, []
    for _ in range(7):
        r = c.post(f"/api/chat/{conv}/message", headers=hk, json={"text": text}).json()
        log.append(r["reply"][:200])
        print("turn:", r["reply"][:80].replace("\n", " "), flush=True)
        if r["waiting_on"]:
            break
        text = kavita_answer(r["reply"])
    R = c.post("/login", json={"user_id": "RMEHTA", "password": "rohit@123"}).json()["token"]
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)

        def snap(name, url, wait="body", full=False):
            print("snap", name, flush=True)
            pg.goto(base + url, wait_until="domcontentloaded")
            pg.wait_for_selector(wait, timeout=20000)
            time.sleep(1.5)
            out[name] = pg.screenshot(full_page=full)

        snap("chat_waiting", f"/app/chat#token={K}&conv={conv}", ".msg.ag")
        snap("inbox", f"/app/inbox#token={R}", ".card")
        snap("slack", f"/app/slack#token={R}", ".slack .m")
        item = [i for i in c.get("/api/inbox", headers={"Authorization": f"Bearer {R}"}).json()["items"] if i.get("conv") == conv][-1]
        d = c.post(f"/api/inbox/{item['id']}", headers={"Authorization": f"Bearer {R}"},
                   json={"decision": "approve", "comment": "ok, Diwali run"}).json()
        log.append((d.get("conversation") or {}).get("reply", "")[:200])
        snap("chat_released", f"/app/chat#token={K}&conv={conv}", ".msg.ag")
        snap("audit", f"/app/audit#token={K}&conv={conv}", "table")
        b.close()
    web.state.l5.close()
    return {"pngs": out, "log": log}


@app.local_entrypoint()
def main():
    res = shots.remote()
    d = ROOT / "lectures" / "L5-the-signature" / "shots"
    d.mkdir(parents=True, exist_ok=True)
    for k, v in res["pngs"].items():
        (d / f"{k}.png").write_bytes(v)
        print("wrote", d / f"{k}.png", len(v))
    print("\n".join(res["log"]))
