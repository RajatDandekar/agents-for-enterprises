# Workflow Studio: spec

The Workflow Studio is the n8n-like playground of the Northbridge Experience (`/studio`). Students stitch toolbox
tools into workflows ("create PR → approval → create PO → release → receive goods") and build agents of their
own. Lecture 6 teaches with it; Lecture 1 shows it in the After reveal.

Files (all in `ledgerline/ledgerline/experience/studio/`):

| File | What it is |
|---|---|
| `engine.py` | the workflow engine: node types, templates `{{ }}`, the run loop, approval waits. Students read it in L6. |
| `templates.py` | the five ready-made workflows (Spring launch battery order, Reorder when low, Goods arrived, Dealer email to order, Build your own agent) |
| `api.py` | `make_router(players) -> fastapi.APIRouter`: the page at `/studio`, JSON under `/api/studio/*` |
| `static/` | the canvas UI (vanilla JS + inline SVG, no build step) |
| `cassettes/` | recorded LLM replies, so the LLM and agent templates replay with no key |
| `tests/` | engine tests (`test_engine.py`) and the Playwright UI test (`test_ui.py`), run on Modal by `tests/modal_studio.py`; `studio_app.py` is the router in a minimal app |
| `shots/` | 1600x900 screenshots from the UI test |

---

## 1. The workflow JSON

```json
{
  "id": "spring-battery-order",
  "name": "Spring launch battery order",
  "description": "Emma's 2,000 battery packs, from stock check to a released order.",
  "nodes": [
    {"id": "start", "type": "trigger", "title": "Start", "x": 60, "y": 240,
     "config": {"kind": "manual"}},
    {"id": "stock", "type": "tool", "title": "Check stock", "x": 340, "y": 240,
     "config": {"tool": "check_stock", "as": "ECLARKE", "args": {"item_code": "BAT-500"}}},
    {"id": "pr", "type": "tool", "title": "Raise the PR", "x": 620, "y": 240,
     "config": {"tool": "create_purchase_request", "as": "ECLARKE", "confirm": true,
                "args": {"item_code": "{{nodes.stock.item_code}}", "quantity": 2000,
                         "cost_centre": "PRD-07", "need_by": "2026-11-09"}}},
    {"id": "daniel", "type": "approval", "title": "Daniel approves", "x": 900, "y": 240,
     "config": {"doc_no": "{{nodes.pr.request_no}}", "approver": "DOKAFOR"}}
  ],
  "edges": [
    {"from": "start", "to": "stock"},
    {"from": "stock", "to": "pr"},
    {"from": "pr", "to": "daniel"}
  ]
}
```

- `id` (node): short, unique, lowercase, used in templates (`nodes.pr`). Letters, digits and `_` only.
- `x`, `y`: canvas position, for the UI only.
- `title`: what the card shows. `config`: depends on the type (below).
- An edge is `{"from": node_id, "to": node_id, "port": "out"}`. `port` is the exit the edge leaves from; it is
  `"out"` when left out. Condition nodes exit by `"true"` or `"false"`; approval nodes by `"out"` (approved) or
  `"rejected"`; any node that fails exits by `"error"` if such an edge exists.

### People a node can act as

| id | person | can |
|---|---|---|
| `ECLARKE` | Emma Clarke, purchase executive | look up, raise P£and POs, release, receive, message |
| `DOKAFOR` | Daniel Okafor, purchase manager | look up, approve, release, message |
| `ATANAKA` | Aiko Tanaka, stores | look up, receive goods, send messages |

A node acts **with that person's own Ledgerline permissions**, nothing more: the toolbox is
`players.toolbox(pid, user)`. There is no super-user.

### Node types and their `config`

| type | config | output (`nodes.<id>`) |
|---|---|---|
| `trigger` | `kind`: `manual` \| `schedule` \| `event` \| `chat` \| `form`, plus the kind's fields (below) | the data the run started with |
| `tool` | `tool` (a toolbox name), `as` (person), `args` {field: value or template}, `confirm` (bool: the node's *Commit* switch, only for tools whose schema has `confirm`), `stop_on_warning` (bool, default true) | the tool's own result dict |
| `condition` | `if`: an expression, e.g. `{{ nodes.stock.below_reorder }}` | `{"branch": "true"\|"false", "value": ...}` |
| `approval` | `doc_no` (template, a PR/ or PO/ number), `approver` (person; who must sign), `as` (who reads the status, default ECLARKE) | `{"doc_no", "status", "approved_by", "waited"}` |
| `llm` | `prompt` (template), `output`: `text` \| `json`, `fields` (for json: the keys wanted, e.g. `["item","quantity","need_by"]`), `model` (default `gemini:gemini-3.8-flash`), `system` (optional) | text: `{"text"}`; json: the parsed object, e.g. `{"item": ..., "quantity": ...}` |
| `agent` | `instructions`, `tools` (a list of toolbox names), `as` (person), `model`, `input` (template, default `{{ trigger.message }}`), `may_commit` (bool: when false every write is forced to a preview), `max_steps` (default 12) | `{"reply", "tool_calls": [{"tool","args","ok"}], "steps"}` |
| `message` | `to` (`@daniel`, `@emma` or an email; template), `text` (template), `as` (sender) | the `send_message` result |
| `set` | `values`: {name: value or template} | the values, computed, e.g. `{"quantity": 36000}` |

Trigger kinds:

| kind | fields | what starts it | output |
|---|---|---|---|
| `manual` | `data` (optional default object) | the Run button | `data`, merged with what Run passed |
| `form` | `fields`: [{`name`, `label`, `type`: text\|number\|date, `default`}] | Run opens the form | the submitted fields, numbers as numbers |
| `chat` | none | a message in the chat panel | `{"message", "history"}` |
| `schedule` | `every`: `day`\|`hour`\|`week`, `at` (e.g. `09:00`) | `POST /api/studio/tick` (the scheduler) or Run | `{"fired_at"}` |
| `event` | `event`: `stock_below_reorder`, `item_codes` (list), `as` | `POST /api/studio/events/check` or Run ("check now") | `{"fired", "item_code", "free", "on_order", "reorder_level", "cover_days"}` |

An event trigger looks at stock with `check_stock` (through the toolbox). If no item is below its reorder level
it does not fire: its output has `"fired": false`, every other node is skipped, and the run ends `done`.

### Templates: how one node uses another's output

A field holds a literal (`2000`, `"PRD-07"`) or a template with `{{ ... }}`:

- `{{nodes.pr.request_no}}`: the `request_no` field of node `pr`'s output.
- `{{nodes.stock.warehouses[0].on_hand}}`: lists by index.
- `{{trigger.po_no}}`: the data the trigger started the run with. `{{today}}` is the Northbridge sandbox date.
- **Whole-field rule.** If the field is exactly one `{{ ... }}`, the value keeps its type (a number stays a number,
  a dict stays a dict). Otherwise each `{{ ... }}` is turned into text inside the string:
  `"PR {{nodes.pr.request_no}} is {{nodes.pr.status}}"`.
- Inside `{{ }}` you may write a small expression: arithmetic (`+ - * / // %`), comparisons, `and or not`,
  `true false null`, and the functions `min max round int float str len abs upper lower add_days(date, n) money(v) num(v)` (`money(285600)` → `£285,600`). Example:
  `{{ nodes.stock.reorder_level * 3 }}`. Nothing else runs: no imports, no attribute calls.
- A path that does not exist is an error that names it: `nodes.pr has no field 'po_no' (it has: request_no, status, ...)`.

---

## 2. Run semantics

1. **Start.** A run starts at the workflow's trigger node (exactly one) with the trigger data.
   The run is saved at once (`status: running`).
2. **Ready.** A node is *ready* when every node with an edge into it has finished, and at least one of those
   edges was *taken*. An edge is taken when its source finished and left by that edge's port.
   If every incoming edge is settled and none was taken, the node is **skipped** (and so on downstream).
   So a branch runs only its own side, and a node after a merge waits for both sides.
3. **Step.** One step runs one ready node (in canvas order, left to right): its templates are filled from the
   outputs so far, it runs, and it records `status`, `output`, `error`, `started`, `seconds`. Each node runs at
   most once per run.
4. **Statuses.** `pending → running → done | warning | error | waiting | skipped`.
   - A tool result with `ok: false` is an **error**; the message is the tool's own `error` and `next_step`.
   - A tool result with a `warning` or non-empty `warnings` (e.g. the closed cost centre PRD-05: "saved as DRAFT")
     is a **warning**. With `stop_on_warning` (the default) the run stops there, `failed`, so a person looks.
   - A writing tool with Commit off returns a **preview**; the node is `done` and its output has `preview`.
5. **Errors.** If a node fails and has an edge from its `error` port, the run follows that edge (the failed
   node's output is `{"ok": false, "error", "next_step"}`). Otherwise the run stops: `status: failed`, with
   `error` naming the node.
6. **Approval = a persisted wait.** An approval node reads the document's real status from Ledgerline
   (`order_status`, through the toolbox):
   - already APPROVED (within the raiser's limit, or signed already) → `done`, `waited: false`;
   - WAITING FOR APPROVAL → the node is `waiting`, the run is `waiting` with
     `waiting_for = {"node", "doc_no", "approver", "approver_name"}`, and the run is **saved and the step returns**.
     Nothing in memory holds it: the run is a JSON document in the store;
   - REJECTED → leaves by the `rejected` port if there is one, else the run fails.
   The approver signs in their own inbox (the experience's approvals inbox, or the Studio's approval sheet, which
   calls `approve_purchase_request` / `approve_purchase_order` **as the approver**). `resume` re-reads the status
   and the run carries on from the approval node. Resuming before anyone signed keeps it waiting.
7. **End.** When no node is ready: `done` (or `failed`). The run log lists every node's events in order.
8. **Writes go through the toolbox only**, so previews and confirm, idempotency keys and permissions all hold.
   Running the spring-launch workflow twice on the same Northbridge finds the same PR (`already_done: true`) instead of raising a second.
9. **Agent node** = the L5 loop inside one node: system = `instructions` (+ who it acts for and today's date),
   tools = the chosen subset of the toolbox as that person, the model calls tools until it answers in text or
   reaches `max_steps`. In a chat workflow the history of the conversation is passed in by the trigger.

### The run JSON

```json
{"id": "r-3f2a91", "workflow_id": "spring-battery-order", "workflow": {"...": "a frozen copy"},
 "status": "waiting", "trigger": {"kind": "manual"}, "started": "...", "finished": null,
 "nodes": {"pr": {"status": "done", "output": {"ok": true, "request_no": "PR/2026/04417", "...": "..."},
                  "error": null, "seconds": 0.02, "inputs": {"item_code": "BAT-500", "...": "..."}},
           "daniel": {"status": "waiting", "...": "..."}},
 "edges_taken": [["start", "stock", "out"], ["stock", "pr", "out"]],
 "waiting_for": {"node": "daniel", "doc_no": "PR/2026/04417", "approver": "DOKAFOR", "approver_name": "Daniel Okafor"},
 "log": [{"t": "...", "node": "pr", "event": "done", "text": "PR/2026/04417 · WAITING FOR APPROVAL"}]}
```

### Python

```python
from ledgerline.experience.studio.engine import Engine, Run
eng = Engine(toolbox_for=lambda user, names=None: players.toolbox(pid, user, names), store=store, pid=pid)
run = eng.start(workflow, trigger_data={})     # saved, trigger done
eng.step(run)                                   # one node
eng.run_until_pause(run)                        # until done, failed or waiting
eng.approve(run, decision="approve")            # as the approver named in run.waiting_for, through the toolbox
eng.resume(run); eng.run_until_pause(run)       # carries on after the approval
eng.validate(workflow)                          # -> list of problems ("node pr: tool 'x' does not exist")
reply, run = eng.chat(workflow, "How many days of cover for the 5 litre battery pack?")   # a chat-triggered workflow
```

---

## 3. The API (`make_router(players)`)

Mount: `app.include_router(make_router(players))` (from `ledgerline.experience.studio.api import make_router`).
The player is the cookie `pid` or the header `X-Player` (either). With neither, the Studio joins a guest player
and sets the `pid` cookie. All JSON; errors are `{"detail": "..."}` with status 4xx.

| Method & path | Body | Returns |
|---|---|---|
| `GET /studio`, `GET /studio/w/{id}` | | the canvas page |
| `GET /studio/static/{file}` | | JS/CSS |
| `GET /api/studio/me` | | `{pid, name, people}` |
| `GET /api/studio/nodes` | | the palette: `{"types": [...], "tools": [tool.json + no python], "people": {...}}` |
| `GET /api/studio/templates` | | `[{id, name, description, trigger, nodes: n}]` |
| `POST /api/studio/templates/{tid}/use` | | a new workflow copied from the template, saved for this player |
| `GET /api/studio/workflows` | | this player's workflows (summary) |
| `POST /api/studio/workflows` | workflow JSON | saved workflow (an `id` is given if missing) |
| `GET /api/studio/workflows/{id}` | | the workflow |
| `PUT /api/studio/workflows/{id}` | workflow JSON | saved workflow + `problems` |
| `DELETE /api/studio/workflows/{id}` | | `{ok}` |
| `POST /api/studio/workflows/{id}/run` | `{"trigger": {...}, "mode": "step"\|"all"}` | the run (step: only the trigger has run; all: until it pauses) |
| `POST /api/studio/workflows/{id}/chat` | `{"message": "..."}` | `{reply, run}`; history kept per workflow |
| `DELETE /api/studio/workflows/{id}/chat` | | clears the chat history |
| `GET /api/studio/runs?workflow_id=` | | run summaries, newest first |
| `GET /api/studio/runs/{rid}` | | the run |
| `POST /api/studio/runs/{rid}/step` | | the run after one more node |
| `POST /api/studio/runs/{rid}/continue` | | the run after running until it pauses |
| `POST /api/studio/runs/{rid}/approve` | `{"decision": "approve"\|"reject", "comment"}` | the run, approved as the waiting approver, resumed (still stepped by the client) |
| `POST /api/studio/runs/{rid}/resume` | | the run, after re-reading the approval status |
| `GET /api/studio/approvals?user=DOKAFOR` | | `list_my_approvals` as that person |
| `GET /api/studio/document?doc_no=&user=` | | `order_status` of a PR/PO as that person (for the approval sheet) |
| `POST /api/studio/events/check` | | starts a run for every saved workflow whose event trigger fires |
| `POST /api/studio/tick` | | starts a run for every saved scheduled workflow (the sandbox clock is fixed, so the tick *is* the schedule) |
| `POST /api/studio/reset` | | a fresh Northbridge for this player (and clears the Studio's runs) |

LLM and agent nodes use `ledgerline.llm.LLM` (`gemini:gemini-3.8-flash` by default) with the cassette
`studio/cassettes/studio.jsonl`: a recorded request replays instantly with no key; anything new calls the model
live when a key is set (`LEDGER_LLM_MODE=auto`). If Gemini's own API cannot answer (no `GEMINI_API_KEY`, or HTTP 402
"credits depleted", as on 28 Oct 2026), the same model is called through OpenRouter (`google/gemini-3.8-flash`)
when `OPENROUTER_API_KEY` is set; the reply is recorded under the node's model name either way.

Storage: workflows, runs and chats live in the `Store` (memory; also JSON files under `STUDIO_DATA` if that
environment variable names a folder, so a waiting run survives a restart of the web process).
