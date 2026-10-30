# Lecture 1: where every number comes from (v4, Northbridge Cycles, runs of 30 Oct 2026)

Every number on a plate comes from one of the logs below. `gen_figdata.py` copies them into `figdata.js` (`window.L1`), and `figs.js` reads them from there. No number from the earlier v3 runs is left. All runs were on Modal (app `enterprise-agents-course`, workspace rajatworkspace) on a fresh in-memory Ledgerline. The sandbox clock is Mon 26 Oct 2026 09:00 GMT.

| Log | Made by | Command (from the course root) |
|---|---|---|
| `logs/before_measure.json` | `before_measure.py` | `sh tools/mrun.sh tools/modal_run.py --script lectures/L1-before-and-after/experiments/before_measure.py` |
| `logs/after_run.json` | `after_run.py`, recorded (`--mode auto`, cassette `L1v4_after`, 37 model calls, all live) | `... --script .../after_run.py --mode auto` |
| `logs/after_run_replay.json` | the same script with `--mode replay`: 37 of 37 calls replayed, and every reply, tool sequence and Ledgerline row is identical to the recorded run | `... --script .../after_run.py --mode replay` |
| `logs/services_blackbox.json` | `services_blackbox.py` | `... --script .../services_blackbox.py` |
| `logs/legacy_shots.json` + `../figs/legacy/*.jpg` | `legacy_shots.py`: Chromium (Playwright) on Modal, clicking the real legacy client at `/legacy` | `sh tools/mrun.sh lectures/L1-before-and-after/experiments/legacy_shots.py` |
| `ledgerline/ledgerline/toolbox/*/tool.json`, `create_purchase_order/tool.py` | the toolbox itself (read by `gen_figdata.py`) | none |

Model cost of the recorded After: $0.084 (gemini-3.8-flash, 156,504 tokens in and 1,995 out, at `llm.PRICES` list prices). A replay costs nothing.

## The Before (`before_measure.json`, figdata `before`, `facts`, `careful_facts`, `traps`)
The five missions, driven through the legacy screens by `ledgerline.legacy_ui.driver.Desk`. These are the same screen files, services and headers the client uses.

| Number | Value | JSON path |
|---|---|---|
| Screens opened, first time | 14 | `first_time.totals["screens opened"]` |
| Fields typed | 29 | `first_time.totals["fields typed"]` |
| Codes typed | 14 | `first_time.totals["codes typed"]` |
| Characters typed | 247 | `first_time.totals["characters typed"]` |
| Buttons pressed | 28 | `first_time.totals["buttons pressed"]` |
| Sign-ins | 3 | `first_time.totals["sign-ins"]` |
| Error codes hit | 2 (ERR-PO-0412, ERR-PO-0715) | `first_time.totals["error codes"]`, `first_time.missions[3].errors` |
| Service calls | 25 | `first_time.totals["service calls"]` |
| Distinct screens | 10 (incl. SYS-LGN-01 and PUR-POM-06) | `first_time.distinct_screens` |
| Hands-on time, first time | ≈5.6 min (KLM **estimate**, not measured) | `first_time.klm_minutes` |
| Careful path (Luis) | 12 screens, 27 fields, 12 codes, 221 characters, 23 buttons, 3 sign-ins, 0 errors, 20 service calls, ≈4.8 min | `careful.totals`, `careful.klm_minutes` |
| Per mission (first time): stock / request / approve / order / receive | screens 3/1/2/5/3; codes 1/1/1/9/2; ≈0.9/0.7/0.8/2.0/1.3 min | `first_time.missions[i].counts`, `.klm_seconds` |
| Stock | 5,400 on hand in WH-MAN-STR, 600 a day, 9 days of cover | `first_time.missions[0].facts` (also `careful_facts.stock`) |
| Items that look alike | 4 rows for "battery pack 5" (BAT-500, BAT-500-R, BAT-375, BAT-750) | `facts.stock.item_rows` |
| Request | PR/2026/04417, est. £273,600 (2,000 × £114.00 + 20% VAT), Fetch's default cost centre PRD-05 | `facts.request` |
| Order | PO/2026/01182, Voltway Cells VC-EIN-0042, contract rate £119.00, basic £238,000, gross £285,600, VAT20-RC, PRD-07 | `facts.order.po_db`, `careful_facts.order.po_db` |
| Fetch defaults on the order | tax VAT20-UK, cost centre PRD-05 | `facts.order.fetched` |
| The silent Draft | status bar "PO/2026/01182 SAVED", status field DR | `facts.order.save_status_bar`, `.save_status_field` |
| Release refused | "ERR-PO-0715: DOCUMENT NOT IN RELEASABLE STATUS (DR)" | `facts.order.first_release` |
| Receipts | GRN/2026/30001 1,200 (DN-4471), GRN/2026/30002 800 (DN-4486); order CL; on hand 7,400 | `facts.receive` |
| Direct-order cap | "ERR-PO-0610: DIRECT PO LIMIT 50000 EXCEEDED, RAISE PR" | `traps.direct_po_cap` |
| Save without Fetch | "ERR-SCR-0221: FETCH NOT DONE" | `traps.save_without_fetch` |
| Which Voltway | 3 rows: VC-EIN-0042 ACTIVE, VC-EIN-0009 BLOCKED, VPC-ROT-0107 (Paints & Coatings) | `traps.supplier_lookup_voltway.rows` |
| Brightcell Energy | 0 rows: not in the supplier master | `traps.supplier_lookup_brightcell` |
| Cost centres and items for the master-data plate | rows as returned | `traps.cost_centres`, `traps.battery_pack_items` |

The minutes come from the keystroke-level model: 0.28 s a key, 1.1 s a point, 1.35 s to think, and 2 s for each screen or service reply. They count only hands-on time. Waiting for Daniel and the call to IT are left out. Say "estimate" on the plate.

## The After (`after_run.json`, figdata `after`, `after_summary`, `after_tools_over_mcp`, `wire`)
Ask Northbridge is `ledgerline.course.l1.AskNorthbridge`: gemini-3.8-flash, plus the 15 tools found over MCP. Each person has their own session. The person's answers follow fixed rules (`course.l1.answer`). "Done" is read from Ledgerline's tables, not from the reply.

| Number | Value | JSON path |
|---|---|---|
| Missions done | 6 of 6: stock, request, approve, order, and the receive mission's two deliveries | `summary.all_done`, `missions[i].done` |
| Messages sent | 12 | `summary.messages` (deck: sum of `after[i].user_turns`) |
| Taps (a "Yes, go ahead." to a preview) | 6 | `summary.taps`, `after[i].taps` |
| Typed messages | 6: one sentence per mission, no follow-up questions needed | `summary.typed_messages` |
| Characters typed (taps excluded) | 453 (77 words) | `summary.chars_typed`, `summary.words_typed` |
| Screens, fields, sign-ins, error codes shown to Emma | 0, 0, 0, 0 | `summary.screens_opened` |
| Codes typed | 1: the PO number in Aiko's sentence | `summary.codes_typed` |
| Tool calls | 20; 1 returned ok=false (in the stock mission), which the assistant handled without showing Emma an error | `summary.tool_calls`, `summary.tool_errors` |
| Waiting time (model + tools, measured) | 113.1 s ≈ 1.9 min | `summary.seconds` (sum of `missions[i].seconds`) |
| Model time alone, all seven questions including the Brightcell one | ≈2.0 min (119.1 s). This is what NB1 shows: the recorded seconds of each model call, which a replay keeps | `llm_totals_by_user` / NB1 section 4 |
| Per mission: messages / taps / tools / seconds | stock 1/0/4/22.2 · request 2/1/4/20.1 · approve 2/1/3/21.1 · order 3/2/5/23.1 · receive 2/1/2/15.2 · receive2 2/1/2/11.4 | `missions[i]` |
| Ledgerline afterwards | PR/2026/04417 CL, PRD-07, £273,600; PO/2026/01182 CL, VAT20-RC, PRD-07, gross £285,600, approved by DOKAFOR; two GRNs 1,200 + 800; on hand 7,400; Brightcell not registered | `ledgerline_after` |
| Brightcell question (extra) | "Not right now": not in the master, no UN 38.3 certificate (POL-PUR-001 §6.2), order already released; 4 tool calls | `missions[6]` |
| Tools discovered over MCP | 15 | `tools_discovered_over_mcp` |
| The plug on the wire | `tools/list`, then the first `tools/call` | `wire_sample` |

**One difference to say out loud.** In the stock mission, the Before reads one warehouse: Manchester, 5,400 packs, 9 days. Ask Northbridge reported both warehouses: 6,600 packs (Manchester 5,400 + Leeds 1,200), 11 days. Both numbers are true; they answer slightly different questions.

## NB1 (`NB1_before_and_after.ipynb`, run on Modal with `--mode replay`: 25 code cells, 0 errors)
NB1 recomputes the Before live in the notebook. It gets the same totals as `before_measure.json`: 14 / 29 / 14 / 247 / 28 / 3 / 2, ≈5.6 min. It replays the After from `L1v4_after`: 12 messages, 6 taps, 453 characters, 20 tool calls.

## Services as black boxes (`services_blackbox.json`, figdata `blackbox`, `services_in_catalogue`)
The calls, in order (the `FIGS.blackbox` plate uses indexes 0, 6 and 7):
0. `stk_query`: 5,400 / 600 / 9.
1. `itm_search`: 4 rows.
2. `pr_save` on PRD-05: PR/2026/04417, £273,600, DR.
3. `pr_submit`: PA.
4. `pr_approve` as DOKAFOR: AP.
5. `po_fetch`: rate 119.0, VAT20-UK, PRD-05.
6. `po_save` with Fetch's tax code: rc E, "ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (NL)".
7. `po_save` with VAT20-RC: rc S, "PO/2026/01182 SAVED", data.status DR.

The catalogue has 38 services (`services_in_catalogue`).

## Screenshots (`figs/legacy/*.jpg`, `legacy_shots.json`, figdata `shots`)
There are 19 shots, 01_signin to 19_no_fetch. Each caption's numbers were read off the rendered page during the run: 4 item rows; 5,400 / 600 / 9 days; PRD-05 and VAT20-UK defaults; DR; and 800 still to come after the 1,200 receipt. The status bar text of each shot is in `legacy_shots.json[i].status_bar`. Renamed: the two approval shots now carry Daniel's name, `07_daniel_inbox` and `08_daniel_approved`. Deleted: the old-name 07, 08 and 10 shots from v3.

## Tools (`gen_figdata.py` reads the toolbox; figdata `tools`, `po_tool_json`, `po_tool_py`)
The toolbox has 15 tools. In `check_budget`, `create_purchase_request` and `create_purchase_order`, the money fields were still described in the old currency. They now say pounds (GBP), fixed on 30 Oct before the After was recorded.
