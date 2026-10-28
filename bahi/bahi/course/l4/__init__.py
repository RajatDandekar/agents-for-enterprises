"""Lecture 4, The Hands: small helpers the notebook (NB4), the experiments and the assignment (A4) share.

    from bahi.course.l4 import add_tool_dir, validate_args, one_round, stdio_wire, HANDS_SYSTEM

Nothing here changes the shared toolbox. A new tool folder is loaded next to the 15 shipped ones, in this process only:

    names = add_tool_dir("my_tools")          # every <folder>/tool.json + tool.py under my_tools/
    tb = Toolbox(erp, "KJOSHI", names=TOOLBOX + names)
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

from bahi.toolbox import ORDER, SPECS, Toolbox, ToolSpec  # noqa: F401

TOOLBOX = list(ORDER)  # the 15 shipped tools, in the order the course shows them

HANDS_SYSTEM = """You are Ask Rasoi, the assistant on Rasoi Steel Works' home page, working in Bahi ERP for {name} ({user_id}).
Today is Monday 26 October 2026. Use the tools to look things up and to do what {first} asks. Every write tool
previews first (confirm=false); show the preview and commit (confirm=true) only after {first} says yes.
If a tool returns ok=false, read its next_step. Report the status the receipt gives you, in plain words."""


# ----------------------------------------------------------------------------- tool folders
def add_tool_folder(folder) -> str:
    """Load one tool folder (tool.json + tool.py) next to the shipped ones. Returns its name."""
    spec = ToolSpec(pathlib.Path(folder))
    SPECS[spec.name] = spec
    return spec.name


def add_tool_dir(root) -> list[str]:
    """Load every tool folder under root (each sub-folder with a tool.json)."""
    return [add_tool_folder(p.parent) for p in sorted(pathlib.Path(root).glob("*/tool.json"))]


REQUIRED_KEYS = ["name", "title", "category", "description", "writes", "input_schema"]


def lint_tool(name: str) -> list[str]:
    """The checks A4 grades a tool folder by. Returns a list of problems (empty = good)."""
    s = SPECS[name]
    j, probs = s.spec, []
    probs += [f"tool.json has no '{k}'" for k in REQUIRED_KEYS if k not in j]
    if j.get("name") != s.folder.name:
        probs.append(f"folder is {s.folder.name} but tool.json says {j.get('name')}")
    props = j.get("input_schema", {}).get("properties", {})
    probs += [f"argument '{k}' has no description" for k, v in props.items() if not v.get("description")]
    probs += [f"argument '{k}' has no type" for k, v in props.items() if not v.get("type")]
    probs += [f"required '{r}' is not a property" for r in j.get("input_schema", {}).get("required", []) if r not in props]
    if j.get("writes") and "confirm" not in props:
        probs.append("a write tool must take confirm (preview first)")
    if len(j.get("description", "")) < 40:
        probs.append("description is too short to choose by (under 40 characters)")
    if not hasattr(s.module, "run"):
        probs.append("tool.py has no run(s, **args)")
    if j.get("example"):
        try:
            s.check(j["example"])
        except Exception as e:  # noqa: BLE001
            probs.append(f"example fails its own schema: {e}")
    return probs


def validate_args(name: str, args: dict) -> list[str]:
    """Check arguments against tool.json's input_schema with a real JSON Schema validator (jsonschema).
    The toolbox's own check (ToolSpec.check) does the same job at the door; this shows what the standard says."""
    import jsonschema

    v = jsonschema.Draft202012Validator(SPECS[name].spec["input_schema"])
    return [f"{'/'.join(map(str, e.path)) or '(top)'}: {e.message}" for e in sorted(v.iter_errors(args), key=str)]


# ----------------------------------------------------------------------------- the hands stage: one tool round
def one_round(llm, tools, messages: list[dict]) -> dict:
    """Ask Rasoi at the 'hands' stage: the model may call tools once; our code runs every call; the results go back;
    the model answers. If it asks for a second round of tools we do not run them (that is the loop, Lecture 5).

    tools: anything with .schemas() and .call(name, args) (a Toolbox, or MCPClientTools).
    Appends to messages in place and returns {answer, calls, replies, wanted_more}."""
    schemas = tools.schemas()
    r1 = llm.chat(messages, tools=schemas)
    messages.append(r1.message())
    calls, replies = [], [r1]
    if not r1.tool_calls:
        return {"answer": r1.content or "", "calls": calls, "replies": replies, "wanted_more": []}
    for tc in r1.tool_calls:
        out = tools.call(tc.name, tc.arguments)
        content = out if isinstance(out, str) else json.dumps(out, default=str)
        calls.append({"tool": tc.name, "args": tc.arguments, "result": json.loads(content)})
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
    r2 = llm.chat(messages, tools=schemas)
    replies.append(r2)
    wanted = [{"tool": t.name, "args": t.arguments} for t in r2.tool_calls]
    if wanted:  # keep the conversation valid: answer each un-run call with a note, then ask for words only
        messages.append(r2.message())
        for t in r2.tool_calls:
            messages.append({"role": "tool", "tool_call_id": t.id, "content": json.dumps(
                {"ok": False, "error": "Only one round of tools per message at this stage.",
                 "next_step": "Answer the user with what you have, and say what you would do next."})})
        r3 = llm.chat(messages, tools=schemas)
        replies.append(r3)
        messages.append(r3.message())
        return {"answer": r3.content or "", "calls": calls, "replies": replies, "wanted_more": wanted}
    messages.append(r2.message())
    return {"answer": r2.content or "", "calls": calls, "replies": replies, "wanted_more": []}


# ----------------------------------------------------------------------------- MCP on the wire, as raw text
def stdio_wire(requests: list[dict], user: str = "KJOSHI", timeout: float = 60) -> list[dict]:
    """Start the toolbox MCP server as a child process (the way Claude Desktop does) and talk JSON-RPC to it over
    stdin/stdout, one JSON message per line. Returns every line that crossed the pipe: {dir: '->'|'<-', msg}."""
    env = {**os.environ, "FASTMCP_SHOW_CLI_BANNER": "false", "FASTMCP_LOG_LEVEL": "ERROR"}
    p = subprocess.Popen([sys.executable, "-m", "bahi.toolbox.mcp", "--user", user], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env, bufsize=1)
    wire = []
    try:
        for req in requests:
            line = json.dumps(req)
            p.stdin.write(line + "\n")
            p.stdin.flush()
            wire.append({"dir": "->", "msg": req})
            if "id" not in req:  # a notification gets no reply
                continue
            while True:
                out = p.stdout.readline()
                if not out:
                    raise RuntimeError("the server closed the pipe")
                msg = json.loads(out)
                wire.append({"dir": "<-", "msg": msg})
                if msg.get("id") == req["id"]:
                    break
    finally:
        p.stdin.close()
        try:
            p.wait(5)
        except subprocess.TimeoutExpired:
            p.kill()
    return wire


def handshake(client="nb4", version="1.0", protocol="2025-06-18") -> list[dict]:
    """The two messages every MCP session starts with."""
    return [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": protocol, "capabilities": {},
                        "clientInfo": {"name": client, "version": version}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"}]
