# Lecture 4 · The Hands: Tools and MCP · speaker notes

Sun 8 Nov 2026, 7:00–9:00 AM IST · Dr. Rajat Dandekar · deck `lectures/L4-the-hands/index.html` (55 slides, 47 plates)
Notebook `NB4_the_hands.ipynb` · assignment `A4.md` · numbers from `experiments/logs/` (see the table at the end).

**The one sentence to land:** a model only writes text; function calling makes that text a structured request that *our code* checks and runs in the user's own Bahi session; MCP is the standard plug that lets any app discover and call those tools.

**Live links.** Ask Rasoi at this stage: `https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=hands` · tools explorer `/tools`. The Experience app was not deployed when this deck was built (no `bahi/bahi/experience/DEPLOYED.md` yet). Open both links before class; if either is down, slide 50 is a replay of our recorded run and carries the demo on its own.

**Timing plan (120 min):** opening 10 · Part 1 function calling 20 · Part 2 JSON Schema 13 · Part 3 tool design 20 · Part 4 contract 20 · toolbox folder 7 · Part 5 MCP 20 · ending and NB4/A4 10.

---

## Opening (0:00–0:10)

**1 · Title.** "Last week Ask Rasoi learnt to read Rasoi's rules. Today it gets hands." Name the three deliverables: toolbox over MCP, NB4, A4.

**2 · Last time, this time.** Two cards. Step 1: today's piece. Step 2: the running example: 20,000 gaskets, ₹2,69,040 estimate, above Kavita's ₹2,50,000, so Rohit signs. Say "Keep this number in your head; it comes back on every plate."

**3 · Monday morning at Rasoi (cold open).** "You are Kavita; you open Ask Rasoi as Lecture 3 left it." Step through the recorded chat: first, the Shakti Seals question, answered with §6.2 (good). Then the real work: it says it has *no direct access* and tells her to type it into Bahi herself. Pause on that sentence. "Everything it knows, and it still sends her back to the eight screens." Recorded: `logs/cold_open.json`.

**4 · The question.** Read it slowly: *A model can only produce text. How can text change an ERP?* Take two or three answers from chat before revealing the one-line answer. (2 min.)

## Part 1 · Function calling (0:10–0:30)

**5 · Part 1.**

**6 · Function calling.** Definition first. Then the PaperBanana sequence: walk the six arrows. Stop at arrow 3: "This is the only arrow that touches Bahi, and the model is not on it." Say "our code decides whether, and in whose session."

**7 · What we send.** Click `check_stock`, then `find_item`, then `create_purchase_request` in the list: show that a tool definition is just name + description + parameters. Point at the measured note: 8,535 bytes, 2,040 prompt tokens for one short question.

**8 · The real round trip (scrubber).** The heart of Part 1. Six step presses, one per message. At each, say who is sending to whom (left list). Stops to make:
- reply 1: `finish_reason: "tool_calls"`, no content: "It did not answer. It asked."
- our code runs `find_item`: six Bahi service calls behind one tool call.
- request 2: the tool message goes back with the same `tool_call_id`.
- reply 3: words.

**9 · Read the tool call.** Four facts about the JSON: no content; the name was chosen from the descriptions; `arguments` is a *string* we must parse; `id` links the result. Mention the Gemini thought signature in one line; do not dwell. **Check yourself:** where does 54,000 first enter the conversation? Let students answer before revealing.

**10 · Two requests, then words.** Rounds 1–3, tokens growing 2,040 → 2,384 → 2,668, 9.4 s. "That chaining is a loop, which is Lecture 5. Today Ask Rasoi gets one tool round per message." Then the honest surprise: the answer says **11 days**, the story says 9. Pune alone is 9; the tool adds Chakan's 12,000. "The model can only say what the tool returns." This sets up Part 3.

## Part 2 · JSON Schema (0:30–0:43)

**11 · Part 2.**

**12 · JSON Schema.** Definition; the six types with Kavita's values; read the smallest schema aloud as a sentence.

**13 · create_purchase_request · tool.json.** Four steps highlight in turn: properties, required, confirm, description. On confirm: "false means preview. Part 4 explains why."

**14 · Required, enum, default.** Rohit's `decision` enum. "Only two words allowed; 'yes' is not one of them."

**15 · Checked once, at the door (interactive).** Click the five mistakes. Make two points: a clear miss becomes an instruction (`next_step: "Ask the user for need_by."`), and harmless text "20000" is quietly cleaned to an integer.

**16 · Descriptions are prompts.** Why the model picked `find_item` first. Then the **check yourself** on "Is PRD-05 still open?" → `check_budget`. (Answer: the words in the description match the words in the question.)

## Part 3 · One tool per business activity (0:43–1:03)

**17 · Part 3.**

**18 · Two ways to give a model Bahi.** 41 raw services (28 reads, 13 writes) vs 15 tools (8 write). Remind: services are black boxes; we never open them.

**19 · What a raw service looks like.** `po_save` as the model sees it. List what it would need to know: fetch token first, GST18-INTER for Rajkot, STD needs an approved request. "That is Kavita's ten years of experience. A raw service makes the model relearn it every call."

**20 · Intent, not screens.** `check_stock` = four Bahi calls in order. Three steps: the services appear, then the arithmetic. Tie back to 11 days.

**21 · The experiment.** 30 tasks, two agents, same model, same prompt, same simple loop, Kavita's session. Point at A01, A15, A10 in the table. Mention honestly: design reused from v2 L3; L04/L11 replaced.

**22 · Measured · definition tokens.** 2,880 vs 1,912. Over MCP the same 1,912. Biggest single tool: `create_purchase_order`, 304.

**23 · Measured · 30 tasks.** Two steps reveal the rows. Headline on gemini-3.8-flash: toolbox **29/30** vs raw **25/30**; **31,425 vs 81,236** tokens per task; 6.2 vs 13.4 tool calls; Bahi refused **4 vs 23** calls; **₹1.51 vs ₹3.73** per task; never-events 0 vs 1. Switch to flash-lite: 28 vs 26, 14,170 vs 38,469 tokens. Read the footnote aloud: five cells hit a client import error and were re-run alone.

**24 · Where each one failed (interactive).** Click A15 (raw: duplicate Deccan, a never-event), A10, L04, then L02 (toolbox: 11 days).

**25 · What the failures teach.** Three cards. The last one is important and honest: on flash-lite the toolbox agent registered Shakti Seals with `confirm=true` without asking. "The tool previewed; the model skipped the question. Tools are not guarantees. Lectures 5 and 7."

## Part 4 · The tool contract (1:03–1:23)

**26 · Part 4.**

**27 · Six promises.** Reveal one at a time. Promise 1 was Part 2. The card: "a model is a fast, tireless, literal new joiner."

**28 · Errors that say what to do next (interactive).** Click the three cases; contrast `DOCUMENT NOT IN RELEASABLE STATUS (PA)` with the toolbox's next_step.

**29 · Preview, then confirm.** Step 1: preview, with PR rows in Bahi 0 before and 0 after. Step 2: the receipt WAITING FOR APPROVAL. Step 3: Rohit approves in his own session; Kavita cannot (ERR-SEC-0001).

**30 · Idempotency keys.** Definition. Then the lost reply, `erp.inject("po_save", "timeout_after_commit")`. Raw retry: two orders, PO/2026/01182 and 01183, ₹24,072 each. Toolbox: one order, `already_done: true`. "A retry after a timeout must not create a second PO."

**31 · Idempotency, in code.** The three places. Then the measured finding, said plainly: on the request path, the retry returns a misleading "not approved (status CL)" error (still no second order), and a lost `pr_save` reply leaves the request stuck in DRAFT. "We found these in our own toolbox while building this lecture; they are filed as fixes." Good moment to say testing tools with fault injection finds real bugs.

**32 · Receipts read back.** SAVED vs DRAFT on PRD-05. "rc S means success. The code DR is easy to miss. The receipt cannot be missed."

**33 · The user's own permissions.** The same `approve_purchase_order("PO/2026/01179")`, ₹4,53,120: as KJOSHI denied, as SVC_AGENT approved. "The tool cannot tell the difference. Only the session can."

**34 · Check yourself · the contract.** Four questions. Give 60 seconds each in chat, then reveal.

## The toolbox folder (1:23–1:30)

**35 · The toolbox folder.** tool.json + tool.py; one folder feeds four surfaces. **Demo moment:** open the tools explorer (`/tools`) and show `create_purchase_request`'s JSON and Python side by side.

**36 · tool.py, line by line.** Key, ask Bahi, preview, write, receipt. "It never copies Bahi's rules; it asks Bahi."

**37 · Writing a new tool.** The gap from Part 3 ("what did we pay last time?") filled by `purchase_history` over `po_hist`. The measured note: in NB4 the model found the new tool over MCP and answered ₹11.40 on PO/2026/01120.

## Part 5 · MCP (1:30–1:50)

**38 · Part 5.**

**39 · The N × M problem.** 3 × 3 = 9 vs 3 + 3 = 6. Definition of MCP.

**40 · Host, client, server.** One step per role. "The model still only writes tool calls; the host routes them."

**41 · JSON-RPC from first principles.** Request (id, method, params), response (same id, result), notification (no id). These are the real first three messages.

**42 · Discovery and calls, on the wire (scrubber).** Three steps: `tools/list`, its 9,488-byte reply, `tools/call check_stock`, its result. Click the `no_such_tool` line to show `isError: true`.

**43 · Discovered, not hard-coded.** One real tools/list entry; `readOnlyHint` (7 reads true, 8 writes false); the host converts back to function definitions: the same 1,912 tokens.

**44 · Transports.** stdio vs streamable HTTP; "the same messages, two pipes."

**45 · Streamable HTTP, really.** Four POSTs; 202 for the notification; the `mcp-session-id`.

**46 · The same server in Claude Desktop.** The config snippet. Be honest: the stdio command was tested on Modal; Claude Desktop itself was not run there. **Optional live demo** if Claude Desktop is on the presenter laptop with the course package installed: add the config, restart, ask "check stock of GSK-SIL-05L".

**47 · The same server in Ask Rasoi.** The code: build_toolbox_server → MCPClientTools → one_round.

**48 · Whose permissions does a server carry?** The two stdio replies. Three rules: bind to the signed-in person; install servers only from people you trust (their descriptions become your prompt); put sign-in in front of HTTP (Lecture 7).

**49 · Check yourself · MCP.** Four questions.

## Ending (1:50–2:00)

**50 · Ask Rasoi gets its hands.** Five steps through the recorded run: Kavita checks stock (one round, `check_stock`), asks for the PR (preview, ₹2,69,040, RMEHTA), says yes (PR/2026/04417 WAITING FOR APPROVAL); Rohit's own Ask Rasoi lists his approvals and approves; read back from Bahi: AP, approved by RMEHTA. **Demo moment:** click "Try it live" and do the same three messages in `/after?stage=hands`.

**51 · What one round cannot do.** Without the item code, the model calls find_item and wants check_stock next, and at this stage it cannot. "Kavita's full order needs a loop. Lecture 5."

**52 · Build · NB4.** Walk the six sections and five exercises. It runs with no key (cassette L4v3_nb).

**53 · A4.** 3–4 tool folders over your module's services, the six promises, a lost-reply test, served over MCP. Tools · 20 points.

**54 · Where we are.** Press once: the map with MCP and the toolbox lit. "Brain, knowledge, hands. Next: the loop."

**55 · Next time.** The Loop, Sat 14 Nov.

---

## Where every number comes from

| Plate(s) | Number | Log |
|---|---|---|
| 3 | cold open transcript | `logs/cold_open.json` (cassette L4v3_coldopen) |
| 7–10 | 8,535 bytes; 2,040 / 2,384 / 2,668 prompt tokens; 3.42 / 2.03 / 3.97 s; find_item then check_stock; 66,000 free, 11 days | `logs/roundtrip.json` (raw HTTP to gemini-3.8-flash) |
| 15, 28, 29, 30, 32, 33 | contract replies, PR preview ₹2,69,040, idempotency 2 orders vs 1, Draft receipt, permissions | `logs/contract.json` (no model) |
| 18 | 41 raw services (28 read, 13 write), 15 tools (8 write) | `logs/contract.json` (inventory) |
| 20 | check_stock's four services | `logs/contract.json` (check_stock_services) |
| 22 | 2,880 vs 1,912 tokens; per tool | `logs/tool_tokens.json` (cassette L4v3_tooltokens) |
| 23–25 | 30-task results, both models | `logs/analysis.json` ← `logs/granularity_*.json` (cassettes L4v3_granularity, L4v3_granularity_lite) |
| 31 | the two idempotency gaps | `logs/contract.json` (idem_retry_pr_path, idem_pr) |
| 37 | ₹11.40 on PO/2026/01120 via the new tool over MCP | NB4 §8 output (cassette L4v3_nb) |
| 41–45, 48 | JSON-RPC wire, stdio and HTTP; whose-session replies | `logs/mcp_wire.json` |
| 50–51 | the hands-stage conversation, tokens, seconds, ₹ | `logs/demo_hands.json` (cassette L4v3_demo) |
| A4 | scaffold tested on hr_leave | `logs/a4_check.json` |

Spend on model calls (at the course's assumed list prices): the 30-task experiment ₹172.00 across both models (as merged in analysis.json; the five errored first attempts cost a little more); the round trip, demo, cold open and notebook together under ₹5.
