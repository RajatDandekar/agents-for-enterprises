"""From a sentence to a workflow: the model drafts, code checks, the person confirms (Lecture 5, The Habits).

    d = draft("Every Monday, chase orders more than 7 days late", llm)
    d["workflow"]       # the workflow JSON, laid out for the canvas
    d["params"]         # what the model lifted out as parameters (days_late=7, buyer=ECLARKE, ...)
    d["problems"]       # [] when every node passed the checks
    d["checks"]         # what code checked, node by node, against each tool's own tool.json
    d["rounds"]         # each model call: problems found, tokens, seconds, US$ (a repair round follows a failed check)

The model never places nodes and never runs anything: it writes JSON. Code checks every tool name, every argument
against the toolbox's tool.json, every {{ }} reference, the parameters, the ports and the shape of the graph. When a
check fails, the problems go back to the model, at most twice. Only a draft with no problems can run.
"""
from __future__ import annotations

import json
import re
import time

from .engine import SPECS, layout, validate
from .world import PEOPLE

MAX_REPAIRS = 2


def _shape(prop: dict) -> str:
    t = prop.get("type", "any")
    if "enum" in prop:
        return "|".join(json.dumps(e) for e in prop["enum"])
    return t


def catalog() -> str:
    """Every tool, one paragraph each: name(arguments) -> outputs, then what it is for. From tool.json, nothing else."""
    lines = []
    for n, s in SPECS.items():
        sch = s.spec["input_schema"]
        req = set(sch.get("required", []))
        args = ", ".join(f"{k}{'' if k in req else '?'}: {_shape(v)}" for k, v in sch.get("properties", {}).items())
        outs = []
        for k, v in (s.spec.get("output_schema") or {}).get("properties", {}).items():
            if k == "ok":
                continue
            d = v.get("description", "")
            outs.append(f"{k}" + (f"[] ({d})" if v.get("type") == "array" else ""))
        lines.append(f"- {n}({args}) -> {', '.join(outs) or 'ok'}{'  [saves]' if s.writes else ''}\n  {s.spec['description']}")
    return "\n".join(lines)


EXAMPLE_ASK = "Every Thursday at 4pm, check the stock of BAT-500 and MNT-FRM-01 and tell Emma which have less than 10 days of cover."
EXAMPLE = {
    "name": "Thursday cover check", "description": "Every Thursday: days of cover for two spring-launch parts; tell Emma which are short.",
    "params": [{"name": "min_cover_days", "label": "Warn below (days of cover)", "type": "number", "default": 10},
               {"name": "tell", "label": "Tell", "type": "text", "default": "@emma"}],
    "nodes": [
        {"id": "start", "type": "trigger", "title": "Thursday 16:00", "config": {"kind": "schedule", "every": "week", "day": "Thu", "at": "16:00"}},
        {"id": "parts", "type": "set", "title": "The parts", "config": {"values": {"codes": "{{ ['BAT-500', 'MNT-FRM-01'] }}"}}},
        {"id": "each", "type": "foreach", "title": "For each part", "config": {
            "items": "{{nodes.parts.codes}}", "label": "{{item}}", "parallel": 2, "steps": [
                {"id": "stock", "type": "tool", "title": "Check stock", "config": {"tool": "check_stock", "as": "ECLARKE", "args": {"item_code": "{{item}}"}}},
                {"id": "short", "type": "set", "title": "Short?", "when": "{{ steps.stock.cover_days < params.min_cover_days }}",
                 "outcome": "short", "config": {"values": {"line": "{{item}}: {{steps.stock.cover_days}} days"}}}]}},
        {"id": "tell", "type": "message", "title": "Tell Emma", "config": {"to": "{{params.tell}}", "as": "ECLARKE",
         "text": "Cover check: {{ tally(nodes.each.tally) }} of {{nodes.each.count}} parts under {{params.min_cover_days}} days."}}],
    "edges": [{"from": "start", "to": "parts"}, {"from": "parts", "to": "each"}, {"from": "each", "to": "tell"}]}

SYSTEM = """You turn a person's description of a task they do often into a workflow for Hermes, the workflow engine of
Northbridge Cycles (Manchester, e-bikes), which runs on its Ledgerline ERP. Reply with ONE JSON object and nothing else.

THE WORKFLOW JSON
{"name": "2-5 words", "description": "one sentence",
 "params": [{"name": "snake_case", "label": "plain words", "type": "number|text|choice|boolean|date|person",
             "default": <the value the person said>, "options": [..] (choice only), "help": "one line"}],
 "nodes": [ {"id": "snake_case", "type": "...", "title": "2-5 words", "config": {...}} ],
 "edges": [ {"from": "id", "to": "id", "port": "out|true|false|rejected"} ]}

PARAMETERS. Every value the person might want to change from one run to the next (a number of days, a threshold or
tolerance, a multiple, a person or channel to tell, a cost centre, a mailbox) is a parameter whose default is what they
said. Nodes read it as {{params.<name>}}. Values that never change are written into the node. Usually 2 to 4 parameters.

NODE TYPES
- trigger: exactly one, where the flow starts. config.kind is one of
    "schedule" {"every": "day"|"weekday"|"week"|"month", "day": "Mon".."Sun" (week), "day_of_month": 1 (month), "at": "HH:MM"}
    "manual" {} · "form" {"fields": [{"name", "label", "type": "text|number|date", "default"}]} (read as {{trigger.<name>}})
    "event" {"event": "invoice_email"|"slack_message"|"goods_receipt"}
- tool: {"tool": name, "as": person id, "args": {...}, "confirm": true|false}. confirm exists only on tools marked
  [saves] that list it; true saves, false only previews. Output: the tool's fields, {{nodes.<id>.<field>}}.
- condition: {"if": "{{ expression }}"}. Leaves by the edge with port "true" or "false" (draw both).
- approval: {"doc_no": "{{ ... }}" (a request/order number, or a list of them), "approver": person id}. The run waits
  until the approver signs in their inbox. Output {{nodes.<id>.approved}} (how many).
- llm: {"prompt": "text with {{ }}", "output": "text"|"json", "fields": [...] (json only)}. One model call. Output
  {{nodes.<id>.text}} or the json fields.
- message: {"to": "@emma" | an e-mail | "{{ ... }}", "text": "... {{ }} ...", "as": person id}. Sent at once.
- set: {"values": {"name": "{{ expression }}"}}.
- foreach (a batch over a list): {"items": "{{nodes.<id>.<list field>}}", "label": "{{item.<field>}}", "parallel": 1-10,
  "steps": [ {"id", "type": "tool"|"llm"|"message"|"set", "title", "config": {as above},
              "when": "{{ expression }}" (optional: run the step only if true),
              "outcome": "posted" (optional: what the item counts as when this step ran)} ]}
  Inside steps: {{item}} is the current item ({{item.<field>}}), {{steps.<step id>.<field>}} an earlier step's output.
  The batch's output: {{nodes.<id>.count}}, {{nodes.<id>.tally}} (outcome counts, a dict) and {{nodes.<id>.results}}
  (one dict per item, step id -> that step's output). Use a foreach whenever the job touches many documents.

EXPRESSIONS inside {{ }}: paths (nodes.x.y, item.y, steps.s.y, params.p, trigger.f, today), numbers, 'strings',
+ - * /, == != < <= > >=, and or not, a if c else b, [a, b], and only these functions: min max round int len sum num(v)
money(v) date(d) add_days(d, n) days_between(a, b) join(list) pluck(list, 'field') first(list) count(list) tally(dict).
A field that is exactly one {{ }} keeps its type (a number stays a number). num() and money() make text for messages:
never use them in a tool's arguments.

PEOPLE (the "as" and "approver" ids; a node acts with that person's own Ledgerline permissions)
{people}

RULES
- Use only the tools below and only their listed arguments; give every required one (no "?").
- confirm true only when the person asked for the thing to be done; otherwise leave it false (a preview).
- Invoices are Luis's job: record, match, hold and post them as LMORENO. Requests and orders are Emma's (ECLARKE).
- A purchase request above the raiser's limit waits for Daniel: after a batch that raises requests, add an approval.
- A foreach over documents that a model step reads: "parallel": 8. To report a batch, write {{ tally(nodes.<id>.tally) }}.
- At most 12 nodes. Edges flow one way from the trigger; a condition has a true and a false edge.
- No "x" or "y": code lays the canvas out.

TOOLS
{tools}

EXAMPLE (another task). The person wrote: "{ask}"
{example}"""


def system_prompt() -> str:
    people = "\n".join(f"- {k}: {v['name']}, {v['role']} ({v['handle']})" for k, v in PEOPLE.items() if k != "LHUGHES")
    return (SYSTEM.replace("{people}", people).replace("{tools}", catalog()).replace("{ask}", EXAMPLE_ASK)
            .replace("{example}", json.dumps(EXAMPLE, ensure_ascii=False)))


def _parse(text: str):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def normalise(wf: dict) -> dict:
    """Small, safe tidying of what the model wrote (never changes meaning): ids, missing titles, edge ports."""
    wf = dict(wf or {})
    wf["params"] = [p for p in (wf.get("params") or []) if isinstance(p, dict) and p.get("name")]
    for p in wf["params"]:
        p["name"] = re.sub(r"[^a-z0-9_]", "_", str(p["name"]).strip().lower())
        p.setdefault("label", p["name"].replace("_", " ").capitalize())
        p.setdefault("type", "text")
    nodes = [n for n in (wf.get("nodes") or []) if isinstance(n, dict)]
    for n in nodes:
        n.pop("x", None)
        n.pop("y", None)
        n.setdefault("config", {})
        n.setdefault("title", str(n.get("id", "")).replace("_", " ").capitalize())
        if n.get("type") == "foreach":
            for s in n["config"].get("steps") or []:
                s.setdefault("config", {})
                s.setdefault("title", str(s.get("id", "")).replace("_", " ").capitalize())
    wf["nodes"] = nodes
    wf["edges"] = [{"from": e.get("from"), "to": e.get("to"), **({"port": e["port"]} if e.get("port") not in (None, "out") else {})}
                   for e in (wf.get("edges") or []) if isinstance(e, dict)]
    wf.setdefault("name", "My routine")
    wf.setdefault("description", "")
    return wf


def draft(ask: str, llm, on_round=None, today: str = "2026-10-26") -> dict:
    """Draft a workflow from the person's words; check it; repair at most twice. Returns the full record."""
    t0 = time.time()
    msgs = [{"role": "system", "content": system_prompt()},
            {"role": "user", "content": f"The person wrote: \"{ask.strip()}\"\nToday is {today}. Reply with the workflow JSON."}]
    rounds, wf, problems, checks = [], None, ["no reply"], []
    for k in range(MAX_REPAIRS + 1):
        r = llm.chat(msgs, response_format={"type": "json_object"})
        raw = _parse(r.content)
        from .engine import _cost
        cost = _cost(r)
        if raw is None:
            problems, checks = ["The reply was not one JSON object."], []
        else:
            wf = normalise(raw)
            problems, checks = validate(wf)
        rounds.append({"round": k + 1, "problems": problems, "ok": not problems, **cost})
        if on_round:
            on_round(rounds[-1])
        if not problems:
            break
        msgs += [{"role": "assistant", "content": r.content or ""},
                 {"role": "user", "content": "Code checked your workflow against the toolbox and found these problems:\n- "
                  + "\n- ".join(problems[:12]) + "\nReply with the whole corrected workflow JSON object."}]
    if wf:
        layout(wf)
    return {"ask": ask, "workflow": wf, "problems": problems, "checks": checks, "rounds": rounds, "ok": not problems,
            "params": (wf or {}).get("params", []), "seconds": round(time.time() - t0, 2),
            "usd": round(sum(x["usd"] for x in rounds), 6), "tokens_in": sum(x["tokens_in"] for x in rounds),
            "tokens_out": sum(x["tokens_out"] for x in rounds)}
