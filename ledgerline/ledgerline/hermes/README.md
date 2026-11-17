# Hermes: the habits lab (Lecture 5, live)

**Live URL:** https://rajatworkspace--northbridge-hermes.us-east.modal.run
(the class wall for the projector: `/wall`; the operator's page: `/admin`)

Modal app `northbridge-hermes`, workspace rajatworkspace, deployed from `deploy/hermes_modal.py`. Contract:
`lectures/L5-the-habits/SPEC.md` ("The lab: Hermes"). Rails copied from Hephaestus and Daedalus; neither is touched.

## What a student does
A student types a name and gets **their lab**: a secret key (`hm-…`, kept in the browser), their own Ledgerline sandbox
(goods receipts, accounts payable and the week's data), their own simulated clock (Mon 26 Oct 2026, 09:00; the top bar's
**Tomorrow 09:00** and **+1 week**), memory, routines, background agents, listeners and chat. Every tab opens with a
three-part guide: what to try, what to notice, next.

1. **Mnemosyne · memory.** Five designs (No memory · Full history · Profile file (USER.md) · Notes + search, OpenClaw-like ·
   Background writer, Instinct-like as reported) and five knobs (window budget, always loaded, search, who writes,
   provenance). **Run Emma's week**: 8 conversations (13 messages) Mon–Fri, nights in between (Dreaming / nightly ingestion
   / profile rewrite), then 10 questions in fresh conversations, scored in code (right, stale, poisoned, missing, wrong).
   Every turn shows the context window part by part (system, profile, memory files, retrieved notes, history, tool calls,
   the message, tool definitions) and the exact text; the memory files day by day with the diff. **Compare all five**
   runs the five designs side by side. **Use the selected design in Ask Northbridge.**
2. **Workflows · the builder.** "What do you do often?" (or one of five starters) → the model drafts a workflow JSON from
   the 26 tools only; code checks every node against each tool's tool.json (names, arguments, required ones, types,
   enums, {{ }} references, parameters, ports, one trigger, no loops, reachability) and sends problems back at most
   twice; the canvas animates in node by node; the parameters it lifted out become a form; **Run with these values**
   (per-node status, output, time, cost; a batch node shows a grid of items filling in); approvals wait in Daniel's
   inbox (top bar) and **Resume**; **Save as my routine** (a tool in Ask Northbridge; on the clock if scheduled).
3. **Background agents.** Three-way match (Wed 02:00, as Luis), late-order chaser (weekdays 09:00, as Emma), certificate
   watch (Mon 08:00, as Luis), reorder watch (weekdays 07:00, previews only), Daniel's approvals digest (weekdays
   08:00). On/off, schedule, parameters, limits (max steps, token budget, may commit), **Run now**, **Stop all**.
   **+1 week** plays every run in time order (same-day runs side by side). Each run: a health check first (Ledgerline
   is down Wed 28 Oct 02:00–02:20: the run fails without spending a token and retries at 02:15 and 02:30), what it did,
   what it changed (read from Ledgerline before and after), what it left for a person; its summary is given to its next
   run. E-mails out are drafts only.
4. **Triggers.** AP mailbox (polled every 5 minutes), #purchasing (pushed), Ledgerline events (pushed). Six listeners,
   eight events: invoice e-mail → the one-invoice workflow; the same e-mail twice → ignored by the listener (event key);
   the resent invoice → refused by `record_invoice` (DUPLICATE); Aiko's Slack request → an agent previews a request,
   **Confirm as Emma**; goods receipt posted → match that order's invoices, post, tell the buyer; Voltway +8% → flag
   open orders; the poisoned e-mail → with provenance on, the note is quarantined; off, it is filed like Emma's words;
   a certificate expiring → the certificate watch runs now. Every chain: event → listener → action → result; replay.
5. **Ask Northbridge, complete.** The chat with the student's memory design (or the class's recorded OpenClaw-like week),
   all 26 tools, their routines as tools (`run_routine`, or three class routines if none saved), "While you were away"
   (agent runs, events, approvals, drafts, held invoices) loaded into the window, and the window shown part by part.

## Ledgerline additions (additive; the base ERP and the 16 tools are unchanged)
- `erp/payables.py` (+ `erp/payables_seed.py`): supplier invoices (`inv_hdr`, `inv_line`; RC received, MT matched, HD held,
  PS posted), the three-way match (released order, same supplier and item, goods received, quantity billed ≤ received −
  already billed, price ≤ order + tolerance; 2% default, policy cap 5%), hold, post (due date from payment terms), open
  late orders, expiring certificates, items below reorder level, the AP mailbox, message drafts. Services register only
  when the module is imported; tables, permissions and data appear only after `install_payables(erp)`.
- The week's data: 40 invoice e-mails in three layouts (31 clean, 1 within tolerance +1.2%, 3 over price +3.5/+6.0/+8.1%,
  2 billing more than received, 1 resent duplicate, 1 with an order number that does not exist, 1 before the goods
  arrived), 8 invoices already recorded last week (5 match, 1 price, 1 quantity, 1 no receipt), 9 late orders (3–17
  days), Halden Cells and Kestrel Power (UN 38.3 expiring in 25 and 39 days), BAT-375 and BEL-STD-01 below reorder,
  Laura Hughes (LHUGHES, purchase manager).
- Ten tools (toolbox `AP_ONLY`, served only when named; `HABITS` = the 16 + these): `list_open_orders`, `read_mailbox`,
  `record_invoice`, `match_invoice`, `hold_invoice`, `post_invoice`, `list_invoices`, `expiring_certificates`,
  `low_stock`, `draft_message`. `SPECS` (15) and `ALL` (16) are unchanged; `tests_toolbox.py` passes as before.

## Running it in class
```
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd purge-tests   # remove Probe/Load/Test/Film/Shot/Rec labs
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd warm          # 30 minutes before class: keep one container on
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd status
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd pause --reason "back in 5 minutes"   # or resume
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd cap --cap 60          # class US$ a day (default 40)
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd student-cap --cap 2   # per student (default 1.5)
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd purge-all     # an empty wall
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::admin --cmd cool          # after class (a cron also does it, 04:00 UTC)
```
- Limits per student: 6 memory weeks and 3 compares per 10 minutes, 12 drafts per 5 minutes, 40 workflow runs, 20 clock
  moves, 40 events and 24 chat messages a minute; at most 64 model calls in flight in the container.
- Keys only from the Modal secret `rasoi-experience`; the OpenRouter key is removed at start; a transient provider error
  is retried twice.
- `min_containers=0` in the file. **Do not redeploy during class**: sandboxes, running jobs and memory-run details live in
  the one container. Names, memory files, routines, agent settings and logs, events and the chat survive in the
  modal.Dict `northbridge-hermes-state`; a restart re-seeds a fresh sandbox (press nothing: the clock is kept).

## Tests and jobs
```
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::test                  # the API test on the live URL (live model)
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::load --n 40           # 40 students at once
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::experiments --which all   # the deck's measured runs -> experiments/logs
/Users/raj/.venv/bin/modal run deploy/hermes_modal.py::record --which shots,week,finale
```
Screenshots land in `lectures/L5-the-habits/figs/hermes/*.png` (3200×1800) and recordings in
`lectures/L5-the-habits/films/hermes_*.mp4` (gitignored). The client code is `lectures/L5-the-habits/experiments/hermes_lab.py`
and `hermes_record.py`.

## Files
| File | What |
|---|---|
| `world.py` | the sandbox (ERP + receipts + payables + the week), people, the simulated clock, Ledgerline's maintenance window |
| `memory.py`, `week.json` | the five memory designs, their tools, hybrid search, the flush, Dreaming, nightly ingestion, the probes |
| `engine.py` | the workflow engine (the Studio's, copied and extended: params, foreach, multi-document approvals, cost) |
| `builder.py` | prompt → workflow JSON → checks → repair rounds |
| `routines.py` | the five starters, their hand-built routines, the one-invoice and goods-arrived workflows |
| `agents.py` | the five background agents and their harness (schedule, health check, retries, limits, run log) |
| `triggers.py` | sources, events, listeners, dedupe, provenance, the trigger agents |
| `chat.py` | Ask Northbridge, complete |
| `app.py` | FastAPI: students, guard (pause, caps, rate limits, model slots), jobs, every tab's API, wall, admin |
| `static/` | `hermes.html/css/js` (no build step), `wall.html`, `admin.html` |
| `default_memory.json` | the class's recorded OpenClaw-like week, used in the finale until a student runs their own |
| `agents.json` | the agents and the recorded week, day by day (for the deck) |

## Measured (12 Nov 2026, gemini-3.8-flash, `lectures/L5-the-habits/experiments/logs/`)
- `hermes_mnemosyne.json`: questions right of 10 on Emma's week (window 3,000): No memory 1 · Full history 10 (1,176
  tokens per turn) · Profile file 10 (1,307) · Notes + search 10 (2,201) · Background writer 9 (627; stale on the
  same-day question). Poisoned answers: 0 in every design, provenance on or off.
- `hermes_workflows.json`: 5 starters drafted twice each, every draft passed the checks (1 round), ~31–34 s and
  ~US$0.005 a draft; the batch of 40: 32 posted, 7 held (3 price, 2 quantity, 1 no order, 1 no receipt), 1 duplicate,
  41 s, US$0.021 (tolerance 0% → 31 posted, 5% → 33).
- `hermes_background.json`: a week with all five agents: 17 runs, US$0.10; Wed 02:00 failed, 02:15 failed, 02:30 ok.
- `hermes_triggers.json`, `hermes_finale.json`, `hermes_load_40.json`, `hermes_api_test.json` (30 / 30).
