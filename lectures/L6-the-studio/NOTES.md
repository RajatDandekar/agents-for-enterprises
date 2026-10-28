# Lecture 6 · The Studio — speaker notes

Sun 15 Nov 2026, 7–9 AM IST. 58 slides (50 numbered plates, the title, six part slides and next time). About 2 hours.
Demo links: Studio `https://rajatworkspace--rasoi-experience.us-east.modal.run/studio` (check `bahi/bahi/experience/DEPLOYED.md` for the live URL), Ask Rasoi `…/after?stage=agent`.
Every number on a plate comes from `experiments/logs/` (see the table at the end).

## Opening (0:00–0:12)

| # | Plate | What Rajat says | Time |
|---|---|---|---|
| 1 | Title | Today Ask Rasoi gets a second door: not a chat, a canvas. | 1 |
| 2 | Last time, this time | L5 built the loop: the model chooses each next tool. Today: when do we *not* want the model to choose? | 2 |
| 3 | Monday at Rasoi | Walk the week grid step by step: Kavita every Monday, Neha on delivery days, dealers every day. "Same steps, only the numbers change." | 3 |
| 4 | Not a chat for everything | Anand's three asks: it should just happen, be the same every time, and Suresh wants to build his own without IT. Your brief: the Workflow Studio. | 3 |
| 5 | The question | Read it out. Pause. Ask the room: "Who would trust a model to pick the steps of Monday's reorder, every Monday, forever?" | 2 |

## Part One · Workflow or agent (0:12–0:35)

| # | Plate | What Rajat says | Time |
|---|---|---|---|
| 7 | Two ways | Define both. Re-explain agent = model + tools + loop + state (L5). Same 15 tools; only the chooser differs. | 3 |
| 8 | Same task, two ways | **Interactive.** Click Workflow: one path, every run. Click Ask Rasoi, scrub runs 1–10: run with `find_item` added. Read one transcript: it needed Kavita's "yes". | 5 |
| 9 | Predictable | Be honest: the agent got it right 10/10 at both temperatures. The difference is that the path is fixed before vs chosen during the run. | 3 |
| 10 | Cost and time | ₹0 vs about ₹1.18 per run; ms vs ~26 s; ~6 model calls. 52 Mondays. "Small money, but it is the same answer bought again every week." | 3 |
| 11 | Auditable | Rohit's question "why 36,000?" Canvas: the set node says `reorder_level * 3`. Agent: read the transcript. Rule of thumb on the card. | 3 |
| 12 | When to use which | **Interactive.** Click all six jobs. Spend time on the dealer email (workflow + LLM node) and the stock desk (agent node). | 4 |
| 13 | Check yourself | Ask; reveal one answer at a time. | 2 |

## Part Two · Anatomy (0:35–1:05)

| # | Plate | What Rajat says | Time |
|---|---|---|---|
| 15 | Seven parts | The map of today's vocabulary. Point at each callout once; we take them in turn. | 1 |
| 16 | Triggers | Five kinds with Rasoi examples. The event trigger is `check_stock` on a list of items: fires for whistles (8,000 vs 12,000). | 3 |
| 17 | Nodes | One tool, one person: Neha can receive goods but not approve; only RMEHTA signs Rohit's approvals. Commit = `confirm`, set in config, never by a template. | 3 |
| 18 | Tools become nodes | Callback to L4: the six cards stand for 26 Bahi services (from each tool.json). This is why a non-programmer can draw it. | 2 |
| 19 | Edges and ports | out, true/false, rejected, error. "Skipped" flows downstream. | 2 |
| 20 | Templates | **Interactive.** Click 1–6 on the real PR output. 2: the number stays a number. 4: text. 5: expression = 36,000. 6: the error that names the field. | 4 |
| 21 | Branches | **Interactive.** Whistles → true side; gaskets → false side, PR skipped. "Every branch is a case you thought of in advance." | 3 |
| 22 | Approval node | Durable wait: read status, save, stop. Rohit signs as himself. | 3 |
| 23 | Waiting run | Show the JSON. "The server can restart; the run is a document." | 2 |
| 24 | Error paths | Real messages: the closed PO, the time-out after commit, and the PRD-05 warning. Warnings stop by default. | 2 |
| 25 | Retries | Time-out after commit. Retry is safe only because of idempotency. The save-then-time-out case is now recovered inside the tool itself. | 3 |
| 26 | Idempotency | Content key, never uuid4. The engine gets it free because writes go through the toolbox. | 2 |
| 27 | Run it twice | Every template twice: nothing ordered twice. Read the Diwali row: every write found (already_done), but Tell Rohit ran again: messages have no idempotency key. | 2 |
| 28 | Check yourself | | 2 |

**Break, 5 minutes (≈1:05).**

## Part Three · Models inside workflows (1:10–1:25)

| # | Plate | What Rajat says | Time |
|---|---|---|---|
| 30 | LLM node | Build the dealer email: the four fields, ~250 tokens, then fixed nodes. "The model reads; tools do." | 4 |
| 31 | Keep it small | Name the fields; look codes up after; decide the commit. | 2 |
| 32 | Agent node | Instructions + tools + model = your own agent; may_commit forces previews; max_steps. | 3 |
| 33 | Build your own agent | Suresh's stock desk, real two turns: preview, then "Yes, raise it" → PR waiting for Rohit. Six tools of fifteen. | 4 |
| 34 | Check yourself | | 2 |

## Part Four · Inside the engine (1:25–1:38)

| # | Plate | What Rajat says | Time |
|---|---|---|---|
| 36 | How an engine runs | Four steps in a loop; the three ways to stop. | 3 |
| 37 | The loop in code | Read `run_until_pause` and `step` from NB6. "You write this in the notebook." | 4 |
| 38 | Scrub a real run | **Interactive.** Drag through the Diwali run: waiting → signed → done. Right panel = each node's real output. | 4 |

## Part Five · The Studio (1:38–1:54)

| Slide | Plate | What Rajat says | Time |
|---|---|---|---|
| 40 | The Studio as a system | Canvas → JSON → engine → the same toolbox → your own Rasoi. **Demo: open /studio.** | 2 |
| 41 | First look | The welcome sheet: five templates and a blank canvas; the palette groups. | 1 |
| 42 | Diwali · it waits | **Live demo:** use the template, Run; three nodes green, "Rohit approves" waiting. Why: ₹2,69,040 > ₹2,50,000. | 3 |
| 43 | Diwali · Rohit signs | Open the approval sheet, Approve as Rohit; it finishes; click the PO node: inputs filled, real output. Read Rohit's message. | 3 |
| 44 | Reorder when low (log) | **Interactive** run log: set node, on-order check, wait, PO. | 1 |
| 45 | Reorder in the Studio | Canvas view: yes side ran, "Tell Kavita" skipped. | 1 |
| 46 | Goods arrived | Neha's form; GRN/2026/30001; run twice: stops, order CLOSED. | 1 |
| 47 | Dealer email (log) | Scrub to `extract`. | 1 |
| 48 | Dealer email in the Studio | The LLM node's panel: prompt, tokens, JSON, "replayed from the cassette". | 1 |
| 49 | Build your own agent | The node's JSON: this is all an agent is. | 1 |
| 50 | Your agent in the Studio | Configure (six tools, May commit) and Chat. Untick a tool live. | 1 |
| 51 | What we measured | Table: nodes, waits, engine time, tokens, ₹, model time, documents. | 1 |
| 52 | Workflow or Ask Rasoi | The three cards; the takeaway. | 2 |

## Part Six · Your turn (1:54–2:02)

| Slide | Plate | What Rajat says | Time |
|---|---|---|---|
| 54 | Open the Studio | Students do steps 1–5 in the session (or at home). The "Whistles running low" exercise. | 3 |
| 55 | Notebook | NB6 map; five exercises. | 1 |
| 56 | Assignment A6 | Two workflows and one agent for their module; run twice; report. | 2 |
| 57 | Where we are | The architecture with the Studio lit; workflows call the toolbox through the engine. | 1 |
| 58 | Next time | Trust: identity, approvals, evals, traces, recovery, deploy. | 1 |

## Demo fallbacks
- If `/studio` is down: slides 38 and 41–50 show the same runs (screenshots from `studio/shots/`, logs from our run) from `templates_fresh.json`; scrub them instead.
- If the model is slow in the Studio's LLM/agent templates: they replay from the Studio's cassettes when recorded; otherwise use plates 30 and 33.

## Where each number comes from
| Plate | Numbers | Log |
|---|---|---|
| 8–10, 52 | 10/10, paths, ~24,100 tokens, ₹1.18/₹1.17, 25.8 s/28.0 s, 6.1 calls, 2 turns; workflow ₹0, 0.0053 s | `experiments/logs/wf_vs_agent.json` (wf_vs_agent.py, gemini-3.8-flash live, 28 Oct 2026) |
| 16, 21 | whistles 8,000 free / 12,000 reorder / 2 days; gaskets 66,000 / 30,000 / 11 days | `experiments/logs/probe.json` (probe.py) |
| 20, 23, 27, 30, 33, 38, 42–52 | template runs, outputs, errors, tokens, ₹ | `experiments/logs/templates_fresh.json` (templates_fresh.py) |
| 24 | time-out text, PRD-05 warning, closed PO | `retry_idem.json`, `probe.json`, `templates_fresh.json` |
| 25 | retry outcomes | `experiments/logs/retry_idem.json` (retry_idem.py) |
| 18 | services per tool | each tool's `tool.json` ("services") |
| 42–43 | ₹2,69,040, ₹2,80,840, PR/2026/04417, PO/2026/01182 | `templates_fresh.json` (Diwali run 1) |
