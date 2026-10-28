"""The GitHub MCP server (github/github-mcp-server v2.0.3) as a real-world MCP server, measured on Modal.

    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/github_mcp.py
-> logs/github_mcp.json   (+ cassette bahi/cassettes/IND9_github.jsonl)

1. Download the official release tarball and verify it against the release's checksums file.
2. Run it over stdio with a DUMMY token (no real token is used anywhere): tools/list needs no GitHub call.
3. For each configuration (default toolsets, all, all + read-only, one toolset at a time) record the tools,
   how many are read-only, and the bytes of their definitions.
4. Real prompt cost: one request per configuration to gemini-3.5-flash-lite with those tools as function
   definitions; tokens_in minus the same request with no tools. Same for the Rasoi toolbox's 15 tools.
A tools/call would need a real GitHub token (it calls the GitHub API): not run in our build.
"""
import asyncio
import hashlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import time
import urllib.request

sys.path.insert(0, "/course/bahi")
from mcp import Client, StdioServerParameters  # noqa: E402

from bahi.erp.engine import ERP  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.toolbox import Toolbox  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
VER = "2.0.3"
BASE = f"https://github.com/github/github-mcp-server/releases/download/v{VER}"
ASSET = "github-mcp-server_Linux_x86_64.tar.gz"
TOOLSETS = ["context", "actions", "code_quality", "code_security", "copilot", "copilot_issue_intents", "dependabot",
            "discussions", "gists", "git", "governance", "issues", "labels", "notifications", "orgs", "projects",
            "pull_requests", "repos", "secret_protection", "security_advisories", "stargazers", "users"]
OUT = {"version": VER, "asset": ASSET, "token": "dummy (no real token used)"}

# ---- 1. download + verify
data = urllib.request.urlopen(f"{BASE}/{ASSET}", timeout=120).read()
sums = urllib.request.urlopen(f"{BASE}/github-mcp-server_{VER}_checksums.txt", timeout=60).read().decode()
want = next(l.split()[0] for l in sums.splitlines() if l.strip().endswith(ASSET))
got = hashlib.sha256(data).hexdigest()
OUT["sha256"] = {"expected": want, "got": got, "match": want == got, "bytes": len(data)}
assert want == got, "checksum mismatch"
d = pathlib.Path("/tmp/ghmcp")
d.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(data)) as t:
    t.extractall(d)
BIN = str(next(p for p in d.rglob("github-mcp-server") if p.is_file()))
os.chmod(BIN, 0o755)
ENV = {"PATH": os.environ["PATH"], "HOME": "/tmp", "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_dummy_not_a_real_token"}
OUT["help"] = subprocess.run([BIN, "--help"], capture_output=True, text=True, env=ENV).stdout[-4000:]
OUT["stdio_help"] = subprocess.run([BIN, "stdio", "--help"], capture_output=True, text=True, env=ENV).stdout[-6000:]
OUT["version_out"] = subprocess.run([BIN, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()[:300]
print(OUT["version_out"])
print(OUT["stdio_help"][:3000])


def dump(x):
    return x.model_dump(mode="json", by_alias=True, exclude_none=True) if hasattr(x, "model_dump") else x


async def listing(flags, mode=None):
    params = StdioServerParameters(command=BIN, args=["stdio", *flags], env=ENV)
    kw = {"mode": mode} if mode else {}
    t0 = time.perf_counter()
    async with Client(params, **kw) as c:
        r = await c.list_tools()
        info = {"protocol_version": c.protocol_version, "server_info": dump(c.server_info),
                "capabilities": dump(c.server_capabilities), "instructions": (c.instructions or "")[:1500]}
        try:
            pr = await c.list_prompts()
            info["prompts"] = [p.name for p in pr.prompts]
        except Exception as e:  # noqa: BLE001
            info["prompts_err"] = str(e)[:200]
        try:
            rt = await c.list_resource_templates()
            info["resource_templates"] = [x.uri_template for x in rt.resource_templates]
        except Exception as e:  # noqa: BLE001
            info["resource_templates_err"] = str(e)[:200]
    tools = [dump(x) for x in r.tools]
    info["seconds"] = round(time.perf_counter() - t0, 2)
    return tools, info


def summary(tools):
    ro = [t["name"] for t in tools if (t.get("annotations") or {}).get("readOnlyHint")]
    return {"n": len(tools), "read_only": len(ro), "writes": len(tools) - len(ro),
            "bytes": len(json.dumps(tools, separators=(",", ":"))), "names": [t["name"] for t in tools]}


def as_functions(tools):
    return [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                              "parameters": t.get("inputSchema", {"type": "object"})}} for t in tools]


llm = LLM("gemini:gemini-3.5-flash-lite", cassette="IND9_github", max_tokens=8)
MSG = [{"role": "user", "content": "Reply with the single word OK."}]


def cost(funcs):
    try:
        r = llm.chat(MSG, tools=funcs) if funcs else llm.chat(MSG)
        return {"tokens_in": r.tokens_in, "served_by": r.model, "replayed": r.replayed}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:400]}


async def main():
    configs = {"default": [], "all": ["--toolsets=all"], "all_read_only": ["--toolsets=all", "--read-only"],
               "default_read_only": ["--read-only"]}
    OUT["configs"] = {}
    for name, flags in configs.items():
        try:
            tools, info = await listing(flags)
            OUT["configs"][name] = {"flags": flags, **summary(tools), "info": info}
            OUT["configs"][name]["_tools"] = tools
            print(name, OUT["configs"][name]["n"], "tools,", OUT["configs"][name]["read_only"], "read-only,",
                  OUT["configs"][name]["bytes"], "bytes,", info["protocol_version"])
        except Exception as e:  # noqa: BLE001
            OUT["configs"][name] = {"flags": flags, "error": str(e)[:500]}
            print(name, "ERROR", str(e)[:300])
    # legacy handshake reply, for comparison with the modern discover
    try:
        _, info = await listing([], mode="legacy")
        OUT["legacy_handshake"] = info
    except Exception as e:  # noqa: BLE001
        OUT["legacy_handshake"] = {"error": str(e)[:300]}
    OUT["by_toolset"] = {}
    for ts in TOOLSETS:
        try:
            tools, _ = await listing([f"--toolsets={ts}"])
            s = summary(tools)
            OUT["by_toolset"][ts] = {"n": s["n"], "read_only": s["read_only"], "bytes": s["bytes"], "names": s["names"]}
        except Exception as e:  # noqa: BLE001
            OUT["by_toolset"][ts] = {"error": str(e)[:200]}


asyncio.run(main())

# ---- 4. what the tool definitions cost in a real prompt
base = cost(None)
OUT["tokens"] = {"no_tools": base}
rasoi = Toolbox(ERP(), "KJOSHI").schemas()
OUT["rasoi"] = {"n": len(rasoi), "bytes": len(json.dumps([f["function"] for f in rasoi], separators=(",", ":")))}
r = cost(rasoi)
OUT["tokens"]["rasoi_15"] = r
for name in ("default", "all", "all_read_only"):
    c = OUT["configs"].get(name, {})
    if "_tools" in c:
        OUT["tokens"][f"github_{name}"] = cost(as_functions(c["_tools"]))
for k, v in OUT["tokens"].items():
    if "tokens_in" in v and "tokens_in" in base:
        v["tool_tokens"] = v["tokens_in"] - base["tokens_in"]
    print("tokens", k, v)
for c in OUT["configs"].values():
    c.pop("_tools", None)
OUT["tools_call"] = "not run in our build: every GitHub tool calls the GitHub API and needs a real token"
LOGS.mkdir(exist_ok=True)
(LOGS / "github_mcp.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False, default=str))
