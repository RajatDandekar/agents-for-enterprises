# Lecture 1 · The Before and the After: speaker notes

Sat 31 Oct 2026, 7:00–9:00 AM IST. 62 slides (54 plates and 8 hero slides). Deck: `lectures/L1-before-and-after/index.html`. Use the arrow keys or click to step through; every `.step` reveals one line, and every figure builds with it.

**Live links:**
- **Base:** https://rajatworkspace--rasoi-experience.us-east.modal.run
- **Pages:** `/` (invitation), `/before`, `/brief`, `/after`, `/tools`, `/studio`
- **Check before class:** if `bahi/bahi/experience/DEPLOYED.md` gives a different URL, use that one.
- **Backup if the app is down:** every live moment has a plate built from our own recorded run (`experiments/logs/`). Say "this is the run we recorded on Modal" and carry on.

**The one rule for Parts 1–5:**
- Say nothing technical until Part 6: no "tool", "model", "LLM", "MCP", "JSON", "API".
- In Part 5, Ask Rasoi is "the assistant on Rasoi's home page", and nothing more.
- There are no cost, latency or model comparisons anywhere in this lecture.

**Timings:** 120 minutes in all.

| Part | Minutes | Clock |
|---|---|---|
| 1 Rasoi needs you | 12 | 7:00–7:12 |
| 2 What an ERP is | 22 | 7:12–7:34 |
| 3 The Before, with 15 minutes hands-on | 34 | 7:34–8:08 |
| 4 Wishlist | 10 | 8:08–8:18 |
| 5 The After | 16 | 8:18–8:34 |
| 6 How it works | 16 | 8:34–8:50 |
| 7 Agent, series map, NB1, A1 | 10 | 8:50–9:00 |

---

## Part 1 · Rasoi needs you (12 min)

**Slide 1 · Title (1 min).** "This morning you are not a student. Rasoi Steel Works has hired you."
- Put the Experience link in the chat now.

**Slide 2 · Part One (hero).** Read the lede aloud.

**Plate 1 · Open the link together (4 min).** DEMO: open `/` on the projector and type your own name.
- Wait until most of the class has their letter.
- Point at the table: today we use `/`, `/before`, `/brief` and `/after`; `/tools` and `/studio` get a glimpse only.
- Tell them not to open `/after` yet. "You will write your wishlist first. That is the point."

**Plate 2 · A letter from Pune (3 min).** Read the letter aloud, slowly. It is addressed to them; the plate carries the app's own words.
- Pause on "codes, screens, and messages nobody can read".
- Say once that everything is fictional.

**Plate 3 · What the dealers say (2 min).** Two dealers, Nagpur and Coimbatore, in the Experience's words. Neither complains about the cookers; both complain about the paperwork.
- Then Kaveri: "confirms orders on WhatsApp in two minutes". That is the competitor.
- "Keep their words. You will write for them in Part 4."

**Plate 4 · The Ask (2 min).** The question of the lecture, then the four-part map.
- "By nine o'clock you will know what an ERP is, why it hurts, what the After looks like, and how it works."

## Part 2 · What an ERP is (22 min)

**Plate 5 · One shared record (2 min).**
- Definition first, then the PaperBanana figure.
- Six modules; each is a group of screens for one department.

**Plate 6 · Why one record (3 min).** INTERACTIVE: press "Each desk keeps its own book".
- Stores says "not expected yet" and finance says "no commitment". Then press "One record, shared".
- "This is the whole reason companies bought ERPs in the 1990s."

**Plate 7 · Master data (2 min).** Four cards build up: item, supplier, cost centre, person.
- Stress codes: `GSK-SIL-05L`, `DP-RJK-0042`, `PRD-07`, `KJOSHI`.
- People are master data too, including their approval limits.

**Plate 8 · Transactions (2 min).** PO/2026/01182 builds in three steps.
- Its own fields come first.
- Then the codes that point at master data (green highlights).
- Then the link to another document (PR/2026/04417).

**Plate 9 · Every document has a status (3 min).** The status machine lights up as the lines appear.
- Make them say it back: "Only RL means the supplier has it."
- "Keep an eye on DR."

**Plate 10 · Procure-to-pay (3 min).** Six steps appear one by one, each with who does it, the screen code, and what came out in our run.
- This chain is the running example for all eight lectures.

**Plate 11 · Kavita's numbers (3 min).** INTERACTIVE: drag the quantity slider.
- At 20,000 the estimate is ₹2,69,040, above ₹2,50,000, so it goes to Rohit.
- Drag down to about 18,000 and it is within her limit. Drag up past about 74,000 and it goes to Anand Patil.
- The order later uses ₹11.90, giving ₹2,80,840.

**Plate 12 · Why ERPs are screens (2 min).** A real screenshot of PUR-PO-01, taken on Modal.
- Point at the parts: bold code boxes with F2, the red stars, the buttons, the grey status bar.

**Plate 13 · A button calls a service (2 min).** INTERACTIVE: the three buttons.
- **A read** (stk_query).
- **A refused write:** ERR-PO-0412, `rc: "E"`.
- **A write that "worked":** `rc: "S"`, msg "SAVED", `status: "DR"`.
- "Input in, output out. We never look inside a service, in this lecture or any other."

**Plate 14 · Bahi ERP 7.2, since 1998 (1 min).** The canon numbers: 412 screens, about 3,100 stored procedures, about 1,200 plants.
- Key line: "Rasoi will not replace Bahi. The After sits on top of it."

**Plate 15 · Check yourself (1 min).** Ask the class; open the answers one at a time.

## Part 3 · The Before (34 min)

**Slide 19 · Part Three (hero).**

**Plate 16 · Your turn (15 min hands-on).** DEMO: open `/before`. Read the five missions aloud. Start them on the timer.
- Walk the room (or the chat). Common stalls are:
  - which gasket code to use;
  - the PRD-05 default;
  - ERR-PO-0412;
  - "it says SAVED, I'm done".
- **Do not rescue them from the Draft.** Let them find ERR-PO-0715 at Release.
- At 12 minutes, give a two-minute warning.

**Plates 17–23 · Replay (8 min, about a minute each).** Real screenshots of the legacy client. Each step flips to the next screenshot.
- **Plate 17:** four gaskets, then 54,000 and 9 days. This is one warehouse; the number comes back in Part 5.
- **Plate 18:** Fetch fills PRD-05. "Nothing warns her."
- **Plate 19:** Rohit's own PC. Kavita phones him. The approval screen is greyed in her menu.
- **Plate 20:** order history, and the F2 lookup with three Deccans: the blocked duplicate DP-RJK-0009 and the near-match.
- **Plate 21:** GST18-INTRA from Fetch gives ERR-PO-0412. She phones IT.
- **Plate 22 · Saved is not done:** the money plate. SAVED on the bar, DR in the field. On Friday, ERR-PO-0715. Ask the room: "How many of you stopped at SAVED?"
- **Plate 23:** amendment to PRD-07, released, then Neha's GRN.

**Plate 24 · The traps (2 min).** INTERACTIVE: click through all six buttons. Each shows its real screenshot and the exact words on the status bar.
- The sixth trap is not in Bahi: Shakti Seals.

**Plate 25 · The Before, measured (3 min).** INTERACTIVE: toggle "First time" and "Careful".
- **First time:** 14 screens, 29 fields, 14 codes, 2 errors, about 5.6 minutes.
- **Careful:** 12 screens, 27 fields, 12 codes, 0 errors, about 4.8 minutes.
- Both are keystroke-level estimates. Ask: "What did your timer say?" Most people take far longer than the estimate, because the estimate does not include finding things out.

**Plate 26 · Where the knowledge lives (2 min).** "The ERP holds the rules. People hold the route." Six cards.

**Plate 27 · The pain points (3 min).** The six-kind taxonomy, with evidence from our run.
- A1 asks them to sort their own module into these six, so name them clearly.

**Plate 28 · Check yourself (1 min).**

## Part 4 · Your wishlist (10 min)

**Slide 33 · Part Four (hero).** "Before you see anything new."

**Plate 29 · What would you build? (7 min).** DEMO: open `/brief`. Its four questions build up on the plate, then the twelve picks (screenshot on the right). Give them 6–7 quiet minutes.
- Encourage ambitious answers, and "what must never happen".

**Plate 30 · The class wall (3 min).** DEMO: show the live wall on `/brief` ("Most picked" bars and the cards). The plate's screenshot holds only test players, so use the live page. Read out three or four entries.
- Map what they wrote onto the six pains.
- "Keep the tab open; tick and circle in Part 5."

## Part 5 · The After (16 min)

**Slide 36 · Part Five (hero).** Pause before the reveal.

**Plate 31 · Ask Rasoi (2 min).** DEMO: open `/after` and choose Kavita under "You are talking as". The plate is the real home page.
- Say: "Nothing in Bahi changed."

**Plates 32–36 · The five missions (8 min).** Each plate is the real transcript from our run.
- **Live:** type the same sentence into `/after` on the projector first, then show the plate.
- **If the live reply differs**, say so. The plate is our recorded run; the model can phrase things differently.
- **32 Stock:** 66,000 across Pune and Chakan, so 11 days, not 9. The legacy screen showed one warehouse.
- **33 Request:** nobody gave a cost centre, and it found PRD-07 itself. Preview, then "Yes, go ahead.", then PR/2026/04417 waits for RMEHTA.
- **34 Rohit's yes:** sign in as Rohit on `/after` (or use the approvals inbox). One sentence, a preview, a yes.
- **35 Order and release:** no ERR-PO-0412, no Draft. It says "approved, not yet released" and asks before sending. Released.
- **36 Neha:** GRN/2026/30001, 12,000. The second delivery closes the order.

**Plate 37 · The Shakti question (2 min).** No screen answers this. It cites Purchase Policy §6.2, registers nobody and orders nothing.
- "This is pain 6 gone: the rule that lived in Suresh's head."

**Plate 38 · The scorecard (3 min).** Real numbers on both sides.
- **Be honest that the After types more characters:** 474 against 228. Those characters are words people already know, there are no codes or route to remember, and there are no errors.
- **6 of the 12 messages were "Yes, go ahead."**
- **Time:** about 2.5 minutes of typing (an estimate) plus 1.3 minutes waiting (measured), against about 4.8 minutes for the careful Before.

**Plate 39 · Your scorecard and the Studio (1 min).** DEMO: their own scorecard on `/after`. The plate shows the scripted test player, a robot, which is why its Before took 0:19; a person takes minutes. Then a ten-second peek at `/studio` ("Lecture 6"); the plate shows a finished run. Back to the wishlist: `/after` puts it next to what was built.

## Part 6 · How it works (16 min)

**Slide 46 · Part Six (hero).** "Only now do we open the box. From here, technical words are allowed."

**Plate 40 · The whole picture (2 min).** The PaperBanana figure, left to right:
- the sentence;
- the orchestrator LLM;
- MCP, the plug;
- the toolbox;
- Bahi, still a black box;
- the receipt coming back.

**Plate 41 · One tool per activity (2 min).** INTERACTIVE: click several tools.
- The ember edge marks tools that save something.
- "A tool is a job, not a screen." DEMO (optional): `/tools`.

**Plate 42 · Inside a tool (1 min).** A folder with two files. tool.json is what the model reads; tool.py is what runs.

**Plate 43 · tool.json (2 min).** Three highlights:
1. the name and description;
2. the input schema (`supplier_code` required, `confirm`);
3. the output schema.

Define JSON schema on the plate.

**Plate 44 · tool.py (3 min).** Five highlights, each a trap from Part 3 handled once in code:
1. the request supplies item, quantity and cost centre;
2. the tax code from the supplier's state (no ERR-PO-0412);
3. the closed cost centre warned about before saving (no silent Draft);
4. `confirm` = preview first;
5. the receipt read back, with `next_step`.

Folded lines (idempotency, timeout) belong to Lecture 7.

**Plate 45 · JSON in, JSON out (2 min).** INTERACTIVE: drag the scrubber through all of Ask Rasoi's tool calls from our run.
- The first view is create_purchase_order with `confirm=false`: the preview.

**Plate 46 · The LLM chooses (2 min).** INTERACTIVE: mission buttons.
- **Request:** check_budget with no arguments, to find an open cost centre. Nobody told it to.
- **Shakti:** find_supplier, then search_policy, and no write.
- Define the orchestrator.

**Plate 47 · MCP, the plug (2 min).** Three cards: tools/list (15 tools discovered), tools/call (find_item), and the result as text holding JSON.
- "The same server plugs into any MCP host. Lecture 4 builds it."

**Plate 48 · Check yourself (1 min).** DEMO: switch on "How it works" on `/after` and watch the cards appear. The screenshot on the plate shows one card with its JSON result.

## Part 7 · So this is an AI agent (10 min)

**Slide 56 · Part Seven (hero).** "Go back over what you saw and name it."

**Plate 49 · Building the definition (2 min).** Four pieces appear: a model, tools, a loop, a person. Then the definition.
- **AI agent:** a model that uses tools in a loop to finish a job for someone.
- **Enterprise agent:** one that does it inside the company's systems, as a named person, under the company's rules.

**Plate 50 · What makes it enterprise (2 min).** Permissions, approvals, proof, legacy systems, each with evidence from our run.

**Plate 51 · The series map (2 min).** INTERACTIVE: click L2 to L8 to light each piece.
- **The pieces:**
  - L2 the brain;
  - L3 the memory;
  - L4 the hands (toolbox and MCP);
  - L5 the loop;
  - L6 the studio;
  - L7 trust;
  - L8 your module.
- "By 22 November you will have built every piece of what you just used."
- The master architecture figure (`figures/ask_rasoi_architecture.png`) is the same picture, used at the end of every lecture.

**Plate 52 · NB1 (2 min).** Colab, replay mode, no key, six exercises. Show the four-line code block.

**Plate 53 · A1 (1 min).** Due before Lecture 3. Choose a module kit now; the table lists all eight.

**Plate 54 · Next time (1 min).** "Tomorrow we take the tools away and ask about the gaskets. With no tools, Ask Rasoi makes up a stock figure. To see why, we open the model."
- Link: `/after?stage=brain`.

---

## Where every number comes from

| Plate | Number | Log |
|---|---|---|
| 6–10 | codes, PO fields, statuses, P2P outputs | `experiments/logs/before_measure.json` (careful run) |
| 11 | ₹2,69,040 and ₹2,80,840 | `before_measure.json` (the PR estimate and the PO gross Bahi computed); rates and limits from `bahi/erp/seed.py` |
| 13 | envelopes, 38 services | `experiments/logs/services_blackbox.json` |
| 12, 14, 16–24 | screenshots and status-bar text | `experiments/legacy_shots.py` → `figs/legacy/*.jpg`, `experiments/logs/legacy_shots.json` |
| 25, 27 | screens, fields, codes, errors, minutes (KLM estimate) | `before_measure.json` |
| 32–38, 45–47, 50 | transcripts, tool calls, 6 of 12, 474 characters, 1.3 min waiting, 15 tools over MCP | `experiments/logs/after_run.json` (gemini-3.8-flash, cassette `L1v3_after`) |
| 14 | 412 screens, about 3,100 procedures, about 1,200 plants, 1998 | the story canon (BUILD.md §1), not measured |
| 1–3, 29–31, 39, 48 | the app's letter, quotes, brief, wall, home page, scorecard, Studio, tool cards | Experience screenshots (`bahi/bahi/experience/shots/`, `studio/shots/`) → `figs/app/*.jpg`; story numbers in the quotes (600 cookers, eleven days) are the Experience's fiction |

**How the figures were made:**
- **PaperBanana** (on Modal, `tools/pb_modal.py`; specs in `figs/figs.json`): `erp_shared_record`, `ask_rasoi_how_it_works` and `tool_anatomy` are used; `before_after` is spare.
- **Live SVG/HTML** in `figs.js`.
- **Regenerating:** `python3 gen_figdata.py` rebuilds `figdata.js` from the logs.
