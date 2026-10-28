# TEMPLATE: invent your own module (v3)

Use this if none of the eight modules fits your work. Your module must live inside the same Rasoi Steel Works and the same Bahi sandbox, so it can reuse purchasing's people, cost centres, suppliers, items and shared procedures. Keep to the same complexity budget as everyone else, so that the grading is fair.

## Steps

1. **Pick the job.** It should be one a real person at a plant does on forms every week, and it should end in one sentence they would rather type. Write it down: *"…"*. It must create or change a document, not only look something up.
2. **Pick a prefix.** Two letters and an underscore, not used by any other module (`pa_ ap_ lv_ so_ wr_ tr_ tv_ ct_` are taken). Every service, table, procedure (`sp_<prefix>`), document series and approval `doc_type` starts with it.
3. **Copy the package.** Copy `modules/TEMPLATE/package/` to `bahi/bahi/modules/<your_module>/`. Replace `xx_`, `XX` and `XX-ABC` everywhere. It installs as it is (`ERP(modules=["<your_module>"])`), so you can grow it one piece at a time and keep it running.
4. **Design the three screens first** (`screens/*.yaml`, format in `modules/README.md`). Then write the services each button calls, then the procedures behind them.
5. **Seed about 50 records**, with the traps on purpose: a duplicate, a near-match name, a value just over a limit, a closed or expired record. Need people? Use `_kit.PEOPLE` (add_people). If you need a new person, ask the lead to add them there; never redefine an existing one.
6. **Write 4–6 policy documents.** Include at least one rule that Bahi does not enforce (it lives only in the document) and one stale, superseded document.
7. **Write `legacy.py`.** `happy_path(erp)` is your before, done screen by screen. `TRAPS` triggers each item of the budget.
8. **Write four scenarios and the never-events** in `scenarios.py`. Add a careful `REFERENCE` run and a careless `NAIVE` run for each one, to prove your `check()` is right.
9. **Build the After in the course's format (v3).** The package ships a `toolbox/` with two example tools:
   `list_documents` (a read) and `create_document` (a write with every promise: preview with `confirm=false`, a key
   made from the content, a look-up before the write and after a timeout, and a receipt read back from Bahi that names
   the silent outcome). Rename and grow them into one folder per business activity (4–6 tools), then:
   - serve them over MCP: `build_module_server(erp, "<speaker>", "<your_module>")` (`bahi.modules._toolbox`);
   - index your documents for retrieval (A3) and put Ask Rasoi or the Lecture 5 harness on the tools (A5);
   - draw one workflow in the Studio (A6);
   - add the trust layer and turn your four scenarios into a suite with a gate (A7);
   - put it on a production stack: at least two industry tools from Lectures 8–11, from two different layers (for
     example Langfuse traces and a DeepEval gate, or the OpenAI Agents SDK through LiteLLM), each with a written
     reason and one measured comparison in `STACK.md` (menu: `modules/README.md`, "The production stack").
10. **Test on Modal.** Run `/Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py --args "--only <your_module>"` until it says RESULT: PASS. It also lints every tool folder, calls each tool's `example` as your speaker, and lists the folders over MCP. Fill in the brief below with the measured numbers.

## The budget you must meet

| Item | Budget | Yours |
|---|---|---|
| Screens | 3 | |
| Services | ≈8, flat payloads, at most 12 fields | |
| Stored procedures | ≈10 | |
| Cascades | 2 (one save triggers other work) | |
| Variants | 2 (one screen, two paths) | |
| Screen-state rule | 1 (Fetch before Save → ERR-SCR-0221, using `sp_fetch_tok_new` / `sp_fetch_tok_chk`) | |
| Silent outcome | 1 (rc S, "… SAVED", but the document is stuck) | |
| Shared engine | 1 (reuse `sp_tax_compute`, `sp_tax_region_chk`, `sp_budget_chk` or `sp_appr_route`) | |
| Policy documents | 4–6 | |
| Seed records | ≈50 | |
| Scenarios | 4, with code checks and never-events | |
| Tools (v3) | 4–6 folders, `tool.json` + `tool.py`, at least one read and one write | |
| Production stack (v3.1) | 2 industry tools from 2 layers (L8–L11), each with a reason, in `STACK.md` | |

## Rules

- Everything is fictional. Do not use a real company, product, person, screen code or document from your workplace. Invent them in Bahi's style.
- Validate once. The rules live in your stored procedures. An agent calls your services and reports what Bahi says; it never re-implements a rule.
- Status always goes in `data`, never in `msg`. The message says only "… SAVED". That is what makes the silent outcome silent.
- `play_approvers` acts only on your own `doc_type`, so modules installed together do not approve each other's documents.

## Your brief (copy into `modules/<your_module>/README.md`)

```markdown
# <Area> · <module>

**After:** <who> types *"<the sentence>"*
**Before:** <three screens, the codes they must know, the trap>.

## The before, step by step
| # | Screen | Button | Service | What they type or read |
Measured on our run: N service calls, N screens, N fields typed.

## The After: what you build (v3)
### Tools: one folder per business activity
| Tool | Business activity | Bahi services behind it | Writes | Notes |
### MCP server · Knowledge (the stale document, the rule only the documents know) · Harness and a workflow
### Trust: identity, a guard per never-event, read-back of the silent outcome, the four scenarios as a suite, recovery
### Production stack: two industry tools from two layers, why each, the hand-built piece it replaces, one comparison

## Complexity budget
| Item | Budget | In this module |

## The traps
1. The silent outcome ... 2. The near-match ... 3. The rule only the policy knows ... 4. The stale document ... 5. The service account

## The four scenarios
| # | Who | Ask | Passes when |
Never-events: NE1 ... NE5
```
