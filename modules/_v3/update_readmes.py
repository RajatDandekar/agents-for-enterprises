"""Rewrite the 'nine jobs' section of every kit README into the v3 After (stdlib only; run on the laptop).

    python3 modules/_v3/update_readmes.py
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plans import PLANS  # noqa: E402

MOD = HERE.parent


def section(kit: str, p: dict) -> str:
    starter = [t for t in p["tools"] if "starter" in t[4]][0][0]
    rows = "\n".join(f"| `{n}` | {act} | {svc} | {'yes, no preview: the instruction is the go-ahead' if w == 'np' else 'yes: preview, then confirm' if w else 'no'} | {note} |"
                     for n, act, svc, w, note in p["tools"])
    return f"""## The After: what you build (v3)

The Before above is three legacy screens. The After is one sentence to Ask Rasoi, signed in as {p['who']}. You build it
the way the course built purchasing, one lecture at a time, in the same folder format.

### 1 · Tools: one folder per business activity (Lectures 4, A4)

One folder per tool, `tool.json` + `tool.py`, exactly like `bahi/bahi/toolbox/`, in your own folder (A4 uses
`my_module_tools/<tool>/`). The first one, `{starter}`, ships in the kit at `bahi/bahi/modules/{kit}/toolbox/`:
copy it into your folder and copy its shape. Every loader in the course reads the same folders: `add_tool_dir`
(`bahi.course.l4`, A4), `FolderToolbox` (`bahi.course.l5.kit`, A5) and `ModuleToolbox` (`bahi.modules._toolbox`).

| Tool | Business activity | Bahi services behind it | Writes | Notes |
|---|---|---|---|---|
{rows}

Every write tool previews with `confirm=false`, carries an idempotency key made from its content (`content_key`), looks
that key up before it writes and again after a timeout, and returns a receipt read back from Bahi, with the status
in words. Every tool returns `ok=false` with `error` and `next_step` when it cannot do the job.

### 2 · MCP server (Lecture 4)

```python
from bahi.modules._toolbox import build_module_server
server = build_module_server(erp, "{p['speaker']}", folder="my_module_tools",
                             with_purchasing=["search_policy", "send_message"])
```

The same folders become MCP tools; Ask Rasoi discovers them with `tools/list`, Claude Desktop can too.

### 3 · Knowledge (Lecture 3)

The kit's own documents in `docs/`: index them for retrieval and cite clauses in answers. One is stale
(`{p['stale']}`): your retrieval must prefer the current one. The rule only the documents know:
{p['policy_rule']}.

### 4 · Harness and a workflow (Lectures 5 and 6)

- The Lecture 5 harness with your toolbox (A5): `Harness(FolderToolbox("my_module_tools", erp, "{p['speaker']}"), llm)`
  from `bahi.course.l5`, or Ask Rasoi itself over MCP: `AskRasoi(erp, "{p['speaker']}", tools=MCPClientTools(MCPClient(server)),
  prompt=YOUR_PROMPT)` from `bahi.course.l7`. Either way the loop, the preview rule and the receipts work as they do
  for Kavita's order.
- One workflow in the Studio: {p['workflow']}.

### 5 · Trust (Lecture 7, A7)

- **Identity:** the server is built for {p['who'].split(',')[0]}'s own session, never `SVC_AGENT`.
- **Guards:** one `TrustLayer` check per never-event below, each with a rule and a next step.
- **Read-back:** the silent outcome ({p['silent']}) is caught from the receipt and never reported as done.
- **Evals:** the four scenarios below are your suite (`run_module_scenario`), three runs each, code checks on Bahi,
  an LLM judge beside them, and the regression gate before every change.
- **Recovery:** `erp.inject("<save service>", "timeout_after_commit", 1)`; the retry finds the document by its key.
- **The demo-day change** (`CHANGE.md`): announced at the end of Lecture 7, absorbed by demo day.

### What is checked automatically

`modules/test_kits.py` lints every folder in `toolbox/` (tool.json complete, schema well formed, services exist,
`run()` takes the schema's arguments, write tools have `confirm` or say in `no_preview_because` why not), calls every tool's `example` as
`{p['speaker']}` and requires `ok=true`, and serves the folders over MCP.

"""


for kit, p in PLANS.items():
    f = MOD / kit / "README.md"
    s = f.read_text()
    new = section(kit, p)
    if "## The After: what you build (v3)" in s:
        s = re.sub(r"## The After: what you build \(v3\).*?(?=\n## Complexity budget)", new.rstrip() + "\n", s, flags=re.S)
    else:
        s = re.sub(r"## The nine jobs, in this module.*?(?=\n## Complexity budget)", new.rstrip() + "\n", s, flags=re.S)
    f.write_text(s)
    print("updated", f.relative_to(MOD.parent), "nine jobs" in s)
