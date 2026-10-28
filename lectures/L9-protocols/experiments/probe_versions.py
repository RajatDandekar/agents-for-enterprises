"""Which versions of the L9 tools exist today (run on Modal). -> logs/probe_versions.json"""
import json
import pathlib
import subprocess
import sys
import urllib.request

LOGS = pathlib.Path(__file__).parent / "logs"
out = {}
for pkg in ["mcp", "fastmcp", "a2a-sdk", "httpx", "uvicorn", "starlette", "sse-starlette"]:
    p = subprocess.run([sys.executable, "-m", "pip", "index", "versions", pkg], capture_output=True, text=True)
    out[pkg] = (p.stdout.strip().splitlines() or [p.stderr[-300:]])[:2]
    try:
        d = json.loads(urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30).read())
        rel = d["releases"]
        latest = d["info"]["version"]
        out[pkg + "_latest"] = latest
        out[pkg + "_latest_date"] = (rel.get(latest) or [{}])[0].get("upload_time")
        out[pkg + "_recent"] = sorted(rel, key=lambda v: (rel[v] or [{}])[0].get("upload_time", ""))[-8:]
    except Exception as e:
        out[pkg + "_err"] = str(e)
for npkg in ["n8n", "@modelcontextprotocol/inspector"]:
    try:
        d = json.loads(urllib.request.urlopen(f"https://registry.npmjs.org/{npkg.replace('/', '%2F')}", timeout=30).read())
        out[npkg] = {"latest": d["dist-tags"].get("latest"), "tags": d["dist-tags"],
                     "time_latest": d["time"].get(d["dist-tags"].get("latest"))}
    except Exception as e:
        out[npkg] = str(e)
try:
    req = urllib.request.Request("https://api.github.com/repos/github/github-mcp-server/releases?per_page=3",
                                 headers={"User-Agent": "course"})
    rels = json.loads(urllib.request.urlopen(req, timeout=30).read())
    out["github-mcp-server"] = [{"tag": r["tag_name"], "date": r["published_at"],
                                 "assets": [a["name"] for a in r["assets"]][:12]} for r in rels]
except Exception as e:
    out["github-mcp-server"] = str(e)
for node in ["https://nodejs.org/dist/index.json"]:
    try:
        d = json.loads(urllib.request.urlopen(node, timeout=30).read())
        out["node_lts"] = [(x["version"], x["lts"]) for x in d if x["lts"]][:3]
    except Exception as e:
        out["node_lts"] = str(e)
LOGS.mkdir(exist_ok=True)
(LOGS / "probe_versions.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
