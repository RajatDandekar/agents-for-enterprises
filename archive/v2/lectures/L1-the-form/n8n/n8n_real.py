"""Run the happy-path workflow in real n8n (on Modal): install Node 20 and n8n, start Bahi, import, execute.

    modal run tools/modal_run.py --script lectures/L1-the-form/n8n/n8n_real.py
-> ../experiments/logs/n8n_real.json
"""
import io
import json
import os
import pathlib
import subprocess
import tarfile
import time
import urllib.request

HERE = pathlib.Path(__file__).parent
LOGS = HERE.parent / "experiments" / "logs"
NODE = "v20.18.0"
N8N = "1.64.3"
res = {"node": NODE, "n8n": N8N}

t0 = time.time()
root = pathlib.Path("/tmp/node")
if not root.exists():
    data = urllib.request.urlopen(f"https://nodejs.org/dist/{NODE}/node-{NODE}-linux-x64.tar.xz", timeout=120).read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as t:
        t.extractall("/tmp")
    os.rename(f"/tmp/node-{NODE}-linux-x64", root)
env = {**os.environ, "PATH": f"{root}/bin:" + os.environ["PATH"], "N8N_USER_FOLDER": "/tmp/n8nhome",
       "N8N_DIAGNOSTICS_ENABLED": "false", "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": "false", "DB_TYPE": "sqlite"}
p = subprocess.run(["npm", "install", "-g", f"n8n@{N8N}", "--no-audit", "--no-fund", "--loglevel=error"],
                   env=env, capture_output=True, text=True, timeout=1200)
res["install_rc"], res["install_tail"] = p.returncode, (p.stdout + p.stderr)[-1500:]
res["install_seconds"] = round(time.time() - t0)
print("npm install rc", p.returncode, res["install_seconds"], "s")

from bahi.server import serve  # noqa: E402
import httpx  # noqa: E402

url = serve(port=8077)


def run_wf(wf, label):
    """Import one workflow (the CLI wants a list) and execute it; return n8n's output and Bahi's live run."""
    n0 = len(httpx.get(url + "/live-run").json())
    path = pathlib.Path(f"/tmp/{wf['id']}.json")
    path.write_text(json.dumps([wf]))
    p = subprocess.run(["n8n", "import:workflow", f"--input={path}"], env=env, capture_output=True, text=True, timeout=600)
    imp = (p.returncode, (p.stdout + p.stderr)[-600:])
    p = subprocess.run(["n8n", "execute", f"--id={wf['id']}", "--rawOutput"], env=env, capture_output=True, text=True, timeout=600)
    out = p.stdout + p.stderr
    live = httpx.get(url + "/live-run").json()[n0:]
    print(f"--- {label}: import rc {imp[0]}, execute rc {p.returncode}")
    print(out[-1500:])
    for c in live:
        print(f"   {c['seq']:>3} {c['screen'] or '':<11} {c['task'] or '':<9} {c['svc']:<12} {c['rc']} {c['err_cd'] or ''} {c['msg']}")
    return {"import_rc": imp[0], "import_out": imp[1], "execute_rc": p.returncode, "execute_out": out[-5000:],
            "live_run": [{k: c[k] for k in ("seq", "screen", "task", "svc", "rc", "err_cd", "msg")} for c in live]}


happy = json.loads((HERE / "bahi_happy_path.json").read_text())
sol = json.loads((HERE / "bahi_variants_solution.json").read_text())
res["happy_15000"] = run_wf(happy, "happy path, 15,000 (as shipped)")
httpx.post(url + "/admin/reset")
big = json.loads(json.dumps(happy))
big["id"], big["name"] = "BahiL1Happy20000", happy["name"] + " (20,000)"
for n in big["nodes"]:
    if n["name"] == "Order":
        for a in n["parameters"]["assignments"]["assignments"]:
            if a["name"] == "qty":
                a["value"] = 20000
res["happy_20000"] = run_wf(big, "happy path on Kavita's real order, 20,000")
httpx.post(url + "/admin/reset")
res["solution_15000"] = run_wf(sol, "variants solution, 15,000")
httpx.post(url + "/admin/reset")
sol2 = json.loads(json.dumps(sol))
sol2["id"], sol2["name"] = "BahiL1Variant20k", sol["name"] + " (20,000)"
for n in sol2["nodes"]:
    if n["name"] == "Order":
        for a in n["parameters"]["assignments"]["assignments"]:
            if a["name"] == "qty":
                a["value"] = 20000
res["solution_20000"] = run_wf(sol2, "variants solution, 20,000 (approval branch)")
LOGS.mkdir(parents=True, exist_ok=True)
(LOGS / "n8n_real.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
