# Lecture 1 · The Before and the After: speaker notes (v4, Northbridge)

Sat 31 Oct 2026, 7:00–9:00 AM IST. 103 slides: 13 part slides and 14 "Ask the class" slides go by fast; about 75 content plates.
Slide numbers below are the deck's counter (bottom right). `[click]` = one step. Timings are targets; the running clock is in brackets.

Everything on a plate is either Northbridge seed data (WORLD_V4.md), a run of ours (experiments/logs, experiments/production),
or a cited public source written on the plate. If a figure shows a green **TODO(v4 data)** card, the run behind it has not
landed yet: say "this one fills in from our run" and move on.

Live links: the Experience is `https://rajatworkspace--northbridge-experience.us-east.modal.run` (`/`, `/before`, `/brief`, `/after`, `/tools`, `/studio`).
Do not redeploy it during class (a new container re-seeds every player's Northbridge).

---

## Part 0 · Opening (7:00–7:04)

**1 · Title.** While people join: "Drop your role and your city in the chat." Then: "Today has three halves. Why agents matter right now and where they break. A real company that needs one, where you do the work by hand. And then the agent doing the same work, opened up all the way to production."

**2 · Ask the class 1: did an agent do real work for you this week?** Read out a few. Most will say writing or code; almost nobody says "inside a work system". "Hold on to that gap. That gap is this course."

## Part 1 · Why agents, and why now (7:04–7:22)

**3 · Part One.** "Let's start with how fast this moved."

**4 · The loop that started it.** "October 2022, a paper called ReAct. The idea is almost embarrassingly simple." [click] "The model writes a thought: I need the item code." [click] "It takes an action, a tool call, and reads the observation." [click] "Thought again, until it can answer." Point at the loop on the left: "Thought, action, observation. Every agent you will ever build is this loop with more engineering around it." This is written out by hand on Emma's question with seed numbers; it is not a recorded run.

**5 · From a loop to production.** Click through the seven points. One line each:
- ReAct: the loop is a prompt pattern.
- Function calling, June 2023: the model returns JSON arguments; no more parsing free text.
- Computer use, Oct 2024: it can drive a screen. Slow and error-prone, but it reaches software with no API.
- MCP, Nov 2024: a standard plug for tools.
- Coding agents, Feb 2025: the first agents doing hours of real work.
- Dec 2025: MCP goes to the Linux Foundation; 97M+ monthly SDK downloads.
- 2026: over half of teams surveyed run agents in production. "The hard part is no longer the demo."

**6 · What companies are doing now.** Left column first, [click] three times: momentum. Then the right column: the other side. Say clearly: "These are other people's numbers. Gartner's are forecasts. The MIT 95% is a narrow six-month P&L measure, and people argue about it. Klarna is the honest story: big claims in 2024, hiring people again in 2025." Do not defend any number beyond its source.

**7 · Ask the class 2: why do agent projects get cancelled?** Let them vote. Most pick 1 (the model). "Hold your answer for ten minutes."

**8 · Works on Friday, dies on Monday.** The FDE-lecture move. Friday: one person, happy path, admin account, nobody checks the ERP. [click] Monday: real people, real limits, a lost reply, a Draft. [click] "Four ways the pilot breaks. All four happened in our own sandbox."

**9–12 · The four incidents.** Same rhythm each time: the story (Northbridge words), [click] what we saw in our sandbox runs (no numbers: these are earlier sandbox runs), [click] the industry parallel with its source, then [click ×3] "follow the why".
- **9, the all-powerful account.** SVC_AGENT approves anything. Industry: the July 2025 coding agent that deleted a production database during a code freeze. Ask the three whys out loud. Land on: "Should an assistant ever have more power than the person it works for?"
- **10, the rule it had just quoted.** It quotes UN 38.3 and then offers to order from Brightcell anyway. Industry: Moffatt v. Air Canada; the company was held responsible for what its chatbot said.
- **11, two orders after a lost reply.** The save happened, the reply was lost, the retry made a second order. Industry: Stripe's idempotency keys exist for exactly this.
- **12, SAVED but in Draft.** The agent reported what the system *said*, not what it *holds*. "Every legacy system has a message like this one."

**13 · Ask the class 3: which could happen in your company?** Expect ALL. "Now go back to your answer to question 2."

**14 · Not a model problem.** Pause on the big line. [click] "A better model fixes none of them." [click] The four fixes, each with its lecture. [click] "Building that system is the job this course is named after."

**15 · The mistakes people make.** Six cards, [click] each. Spend the most time on "rules only in the prompt" and "trust the reply, not the record": they are incidents 2 and 4 in one sentence each.

## Part 2 · How we will learn it (7:22–7:26)

**16 · Part Two.**

**17 · Our approach.** The PaperBanana figure. "One company, one agent, Ask Northbridge, growing one piece per lecture. Lectures 1 to 7: we build every piece by hand. 8 to 11: the same agent on the tools industry runs, measured. 12: your own module." [click ×4] build, break, measure, meet the industry tool. [click] "Tools change every quarter. The pieces don't."

**18 · Ask the class 4: one AI tool you use but couldn't explain.** Read a few. "By Lecture 12 you'll be able to explain each of those from first principles, and build it."

## Part 3 · Northbridge needs you (7:26–7:32)

**19 · Part Three, with the QR.** "Everyone open this now, on your phone or laptop, and type your name." Wait about 60 seconds.

**20 · Open the Experience.** [click] the route table. [click] "Stop at the brief. Don't peek at the After."

**21 · A letter from Manchester.** [click ×3], then let the letter appear and read the last line slowly: "Please read what is happening here. Then tell me what you would do." Everything is fictional.

**22 · What the bike shops say.** Hartley Cycles in Bristol, Velo Centraal in Utrecht. [click] [click] Brisa Bikes, two minutes in a chat. "Nobody complains about the bikes. They complain about everything around the bikes."

**23 · One order, five people.** [click ×5] the cast. [click] the order: BAT-500, Voltway Cells, £119.00, £285,600 with VAT, so Daniel must approve. "You will be each of these people in ten minutes."

## Part 4 · What an ERP is (7:32–7:46)

**24 · Part Four.**

**25 · Ask the class 5: have you used an ERP? Which one, how did it feel?** Expect SAP, Oracle, Dynamics, some Odoo. Read out the feelings: "slow", "confusing", "powerful". "Keep that word. Every one of those products is now adding agents on top, for exactly that reason."

**26 · The ERPs the world runs on.** [click ×6]. One sentence each, from the plate; each has its source. SAP's 2027 maintenance deadline is the one to dwell on: "Thousands of companies are migrating right now. Every migration is a chance to put an agent on top."

**27 · One shared record.** Definition; [click] all departments; [click] module.

**28 · Why one record.** Press "Each desk keeps its own book", then "One record, shared". "That is the whole reason companies bought ERPs in the 1990s." (Order number and value come from our careful Before run.)

**29 · Master data.** [click] through the four cards: BAT-500, VC-EIN-0042, PRD-07, ECLARKE with the £250,000 limit.

**30 · Transactions.** [click] the order points at master data by code; [click] it points at the request.

**31 · Status.** [click] DR, waiting, AP, RL, CL. "Only Released means Voltway has it. Watch DR: it was incident 4, and you are about to meet it."

**32 · Procure-to-pay.** [click ×5], who does each step on which screen.

**33 · Who has to sign?** Seed numbers: 5,400 in Manchester, 600 a day, 9 days; 1,200 in Leeds. Estimate £273,600, order £285,600. Let someone drag the slider below about 1,800 packs: Emma can sign alone.

**34 · A button calls a service.** Three buttons: a read, a refused write (ERR-PO-0412), a write that "worked" and is a Draft. "Remember this box. In Part 9 the agent calls these same services."

## Part 5 · The Before (7:46–8:06, includes 15 minutes hands-on)

**35 · Part Five.** "Open /before. Fifteen minutes. The timer counts your clicks, keys and errors."

**36 · Your turn.** [click ×5] the missions. Then start a 15-minute timer and stay quiet. Walk the chat for "stuck" messages. Common sticking points: the item code, the Fetch button, ERR-PO-0412, the grey DR.

**37–40 · Replays** (after the 15 minutes, 1 minute each). Each click shows the next real legacy screenshot.
- 37 the stock: lookalike codes; one warehouse per screen.
- 38 request and approval: Fetch fills PRD-05, closed on 15 Oct, and nothing warns. Daniel is phoned to look at his inbox.
- 39 which Voltway: the blocked duplicate, Voltway Paints & Coatings, then ERR-PO-0412: "a UK tax code for a Dutch supplier".
- 40 saved is not done: SAVED with DR; Friday's ERR-PO-0715; amend to PRD-07; release; Aiko receives 1,200 then 800.

**41 · The traps.** Click through the six. The last one is not in Ledgerline at all: Brightcell.

**42 · The Before, measured.** First time vs careful, counted by our legacy driver. [click] careful. "Knowing every trap removes errors, not steps." Ask: "Who beat the careful run's estimate?"

**43 · Where the knowledge lives.** [click ×6]. "The ERP holds the rules. People hold the route." This is why the next part asks you questions instead of telling you answers.

## Part 6 · What should it be like? (8:06–8:16) — top priority

**44 · Part Six.** "You do not need to know ERPs for this. You only need to have used software at work."

**45 · Your brief.** "Open /brief." The four questions are the same as on the next slides. Give them five minutes to type; then go through the four slides as a discussion while the wall fills.

**46–50 · Ask the class 6–10.** One minute each. Read two answers aloud per slide, ideally one common, one unusual.
- 46 how should it feel? Push for concrete words: "like asking a colleague", "it remembers", "I never type a code".
- 47 never without asking? The line between reading and writing almost always appears. "Hold that: it becomes the preview-and-yes rule."
- 48 how would you know? Receipts, steps you can see, tests. "Which one would you actually trust?"
- 49 wrong, and who is responsible? Bring back the tribunal from incident 2. There is no single right answer; the point is that someone must be.
- 50 click or say? Good answers: say it for once-a-year jobs, click for the same job a hundred times a day. "Lecture 6 is about exactly that."

**51 · The class wall.** Read the top three picks and two unusual answers to question 2. "Keep your tab open. You will tick what the After does."

## Part 7 · The After (8:16–8:28)

**52 · Part Seven.** "Open /after, sign in as Emma. Same Ledgerline underneath."

**53 · Northbridge's new home page.** [click ×3]. "Ledgerline has not changed. Only how people reach it."

**54–59 · The missions** (2 minutes each; do them live in the Experience if it is responsive, otherwise use the recorded replies on the plates). Each [click] reveals the next turn.
- 54 the stock: both plants, no codes. Say aloud: Ask Northbridge reported both warehouses, 6,600 packs and 11 days; the Before showed Manchester only, 5,400 and 9 days. Both are true; a good assistant says which one it means.
- 55 the request: it found PRD-07 by itself, showed a preview, asked for a yes.
- 56 Daniel's yes: approved by DOKAFOR. "Compare incident 1."
- 57 order and release: right tax, open cost centre, says what Ledgerline holds. "Compare incident 4."
- 58 Aiko's receipt: 1,200 now, 800 to come.
- 59 the certification question: no, with §6.2 cited; registers nobody. "Compare incident 2."

**60 · The scorecard.** [click]. After: 12 messages (6 typed, 6 taps on “Yes, go ahead”), 453 characters, 20 tool calls (one returned ok=false in the stock mission and was handled without showing Emma an error), about 1.9 minutes of waiting. Before, first time: 14 screens, 14 codes, 3 sign-ins, 2 error codes, about 5.6 minutes, and that time is a keystroke-level estimate, not a measurement. "Not always fewer keystrokes. Words people already know, and no route to remember." Ask them to tick their brief on /after.

## Part 8 · What is behind this? (8:28–8:32)

**61 · Part Eight.** "Before I open it: your guesses."

**62 · Ask the class 11: how did we do this?** Most pick B (clicking the screens) or D (SQL). The answer is C. Do not reveal yet; say "we'll see".

**63 · Ask the class 12: what parts would you need?** Collect a list in the chat: "a model", "the ERP's API", "permissions", "a confirm step", "logs". Keep the list visible; plates 66 and 71 check it.

## Part 9 · How it works (8:32–8:42)

**64 · Part Nine.**

**65 · One request, end to end (3D).** Full-bleed, 20 clicks for 21 stages (stage 0 is the overview); a forward click plays the stage (5–20 s), going back jumps to its end. It is one real recorded run (flow3d/trace.json, gemini-3.8-flash): Emma asks for the stock, then raises the request. Narrate in one sentence per stage; each stage's caption is on screen, and the stage table is in flow3d/README.md. The arc:
- Turn 1, the stock: Emma's message arrives; the harness assembles the context (system prompt, history, 15 tool schemas) before the model has read a word of her request. The LLM picks one tool of 15 (find_item); the guard checks the arguments against tool.json; the call rides MCP as a JSON-RPC frame; Ledgerline's services answer. Then search_policy, check_stock, and a check_stock that returns ok:false with a next step, handled without showing Emma an error. Then the answer.
- Turn 2, the order: find_supplier, search_policy, then the talking point: Ask Northbridge first tries create_purchase_order and the ERP refuses: "A direct order is limited to £50,000; this one is £285,600." The guard and the ERP's own rule caught the wrong path. It then takes the right one: check_budget, the create_purchase_request preview with confirm=false (£273,600, approver DOKAFOR, nothing saved), and the question to Emma.
- Turn 3: "Yes, go ahead"; the write lands in Daniel's inbox; the receipt is read back from Ledgerline: WAITING FOR APPROVAL. "Incident 4, fixed." If one model call is visibly slow in the recording, say so: that is why production teams trace latency.
The standalone version is flow3d/index.html (?autoplay). Without WebGL the slide shows a poster.

**66 · The pieces.** The PaperBanana overview. "Count your list against this. Who had the harness? Who had MCP?" (answer to question 11: C).

**67 · One tool per activity.** Click check_stock, create_purchase_order. "A tool is a job, not a screen. The ember edge means it saves something, so it previews first."

**68 · A tool is a contract (tool.json).** [click] JSON schema definition, [click ×3] name/description, input schema with confirm, output schema with the real status. "That output field is incident 4, fixed."

**69 · The LLM chooses.** The recorded decisions. "This is the Thought–Action–Observation loop from slide 4. The tool result is the observation." [click] [click] the certification question: it read policy and wrote nothing.

**70 · MCP, the plug.** [click ×2] tools/list, then tools/call. "Lecture 4 builds this; Lecture 9 goes deep."

**71 · So this is an agent.** [click ×4] model + tools + loop + a person. Read the definition. Compare with the class list from question 12.

## Part 10 · In production (8:42–8:51)

All numbers on these plates come from window.PROD (experiments/production/figdata_production.js, from logs/stacks_r1-3.json and logs/ablation_*.json, run 30 Oct 2026). Screenshots are real Langfuse pages of those runs.

**72 · Part Ten.** "A demo runs on one laptop. This is what a production team does with the same agent."

**73 · Same agent, three runtimes.** The figure: same toolbox over MCP, three runtimes, one model API, traces into Langfuse, the same checks on Ledgerline.

**74 · Who makes these, and what for.** [click ×3] OpenAI Agents SDK, LangGraph, Langfuse, each mapped to the lecture where they build the piece by hand.

**75 · Does the runtime matter?** [click] define never-event (NE1–NE6 in the logs: unapproved, duplicate, uncertified supplier, duplicate supplier, "sent" when not released, more goods than arrived). Read the table row by row: all three 15/15 with 0 never-events. Median tokens: harness 17,141, Agents SDK 15,550, LangGraph 14,629. Cost per mission £0.0115 / £0.0122 / £0.0122. p50 / p95: 36.0 / 68.1 s, 38.7 / 62.2 s, 34.0 / 57.6 s. [click] "The gap between stacks is smaller than the spread between runs of the same stack." [click] Daniel's mission (M3): in 5 of 9 runs his assistant reached for create_purchase_order after approving (a line in our own prompt, written for Emma), and Ledgerline refused every save with ERR-SEC-0001. Six of the nine M3 runs also hit the 12-call cap while checking the lithium-cell rule; they still passed on Ledgerline's state. "Least privilege in the ERP held, not the prompt. None of the three frameworks stopped it." Pick a framework for what it gives around the loop (sessions, checkpoints, handoffs, guardrails, an auditable graph), not for accuracy.

**76 · Reading a trace.** The real, public Langfuse trace of mission M4 on our harness (Gemini 3.8 Flash). One view per click: the tree (header: time, cost, tokens, user, and our two scores erp_check and never_events); the release_purchase_order span (arguments in, Ledgerline's receipt out: "this is how you audit 'did it really happen' without trusting the reply"); the timeline (tools take milliseconds, the model takes the seconds: "cut model calls or pick a faster model, don't optimise the ERP"); one model call (what it saw and the tools it chose, with tokens and cost: "this is where you debug why").

**77 · Incident 4, for real.** Llama 4 Maverick, M4. Emma says "Yes, go ahead"; it replies "The order PO/2026/01190 is RELEASED." No order existed (2 of 3 runs of M4: NE5). [click] The tree: model calls and no tool span; it wrote its tool calls as text, in 12 of 15 missions. [click] "The reply looked perfect. The check on Ledgerline's state caught it. If we had graded the reply, it would have passed." Tie it back to slide 12.

**78 · Which model? An ablation.** Click the four metrics; the sentences on the left are filled from the data. Five of six models passed 15/15 with no never-event (GPT-6 Luna: median 14,838 tokens, £0.00045 a mission, 19.3 / 42.2 s). Llama 4 Maverick passed 4/15, with 2 never-events (NE5). Teaching point on GPT-6 Luna, from an earlier sweep, before we fixed the tool (not in the final numbers): it passed the warehouse name "Manchester stores" instead of the code to receive_goods; the tool's next step failed, Luna told Aiko the receipts were not recorded, but Ledgerline had saved them against a warehouse that does not exist. Only the read-back check caught it. "The check on the ERP's state caught what the reply hid, and we fixed the tool." Cost: at the same pass rate, gpt-oss-120b costs about 1/50 of the course default. Caveats aloud: 15 missions per model, read differences under ~2× as noise; a p95 is partly which provider OpenRouter routed you to. And: in our first sweep a leaked example request number made the test too easy. "Your eval can be wrong too. Read the transcripts."

**79 · Ask the class 13: what would you look at first?** Most say pass rate. For Northbridge the first answer is never-events, then where the data goes, then cost.

## Part 11 · The 2026 agent stack (8:50–8:54)

**80 · Part Eleven.**

**81 · The stack.** Nine clicks, one layer each, bottom up: model, gateway, harness, tools and MCP, knowledge, workflows, trust, observability and evals, durable execution and deployment. For each: read the question it answers in quotes, name two tools, say the lecture. The tenth click shows Ask Northbridge on every layer. Anyone can click a layer afterwards.

**82 · Ask Northbridge, whole.** The master architecture. "Every lecture's last slide lights up its piece of this."

## Part 12 · Twelve lectures (8:54–8:57, fast)

**83 · Part Twelve.** "One slide per lecture. I'll go quickly; the slides stay on the hub."

**84–95 · Lectures 1–12.** For each: the story beat, the project, the assignment, in one breath. Slow down on L7 (Trust: Henrik's "can we switch it on?") and L8 (the frameworks the class just saw).

## Part 13 · Your capstone (8:57–8:59)

**96 · Part Thirteen.**

**97 · Your domain, your agent.** [click ×4] the path A1 → demo day. [click] the two options: your own domain from modules/TEMPLATE, or a kit. "Keep it fictional; never bring an employer's real data."

**98 · Graded out of 100, and demo day.** The seven lines; the two overriding rules. [click] the 8-minute slot on Sun 6 Dec.

**99 · Ask the class 14: one job you would hand to an agent tomorrow.** "That may be your capstone."

## Close (8:59–9:00)

**100 · What this course gives you.** [click ×4] role, skills, portfolio, judgement.

**101 · NB1.** Runs in Colab with no key. (Check the cell names against the rebuilt NB1 before class.)

**102 · A1.** Due before Lecture 3, Sat 7 Nov, 7 AM IST.

**103 · Next time: The Brain.** "Tomorrow we take the tools away, and it makes up the stock figure. Then we open the model."

---

### If time runs short
Skip in this order: 28 (why one record), 67 (tool grid), 84–95 (say "the lecture slides are on the hub"), 50, 26's sources.

### Sources on the plates (for questions)
- ReAct: Yao et al., arXiv 2210.03629 (6 Oct 2022). Function calling: OpenAI, 13 Jun 2023. Computer use: Anthropic, 22 Oct 2024. MCP: Anthropic, 25 Nov 2024; donated to the Agentic AI Foundation (Linux Foundation) 9 Dec 2025 with 97M+ monthly SDK downloads and 10,000+ active public servers. Claude Code: 24 Feb 2025.
- LangChain, State of Agent Engineering: 1,340 responses, 18 Nov–2 Dec 2025; 57.3% in production; 89% observability; 62% step tracing; 52.4% offline evals; 37.3% online; quality the top barrier (about a third).
- Gartner: 25 Jun 2025 (40%+ of agentic AI projects cancelled by end 2027; about 130 real vendors); 26 Aug 2025 (up to 40% of enterprise apps with task-specific agents by end 2026, from under 5%).
- MIT Project NANDA, The GenAI Divide: State of AI in Business 2025 (95% of pilots, no measurable P&L impact; a narrow, debated measure).
- Klarna press release 27 Feb 2024; CEO interview with Bloomberg, May 2025.
- Replit/SaaStr incident, Jul 2025 (eWeek, The Register). Moffatt v. Air Canada, 2024 BCCRT 149. Stripe API reference, idempotent requests.
- SAP: S/4HANA launched 2015; Business Suite 7 mainstream maintenance to 2027 (The Register). NetSuite: founded 1998; Oracle completed the purchase 7 Nov 2016, about $9.3bn. Dynamics 365: GA 1 Nov 2016. Odoo: odoo.com says over 28 million users. Workday: over 60% of the Fortune 500 (Fortune, 1 Apr 2025). Infor: Koch Industries completed the acquisition in May 2020.
- OpenAI Agents SDK: 11 Mar 2025, successor to Swarm. LangGraph 1.0: Oct 2025. Langfuse: MIT-licensed, acquired by ClickHouse 16 Jan 2026.
- LinkedIn Jobs on the Rise 2026 (US): AI engineer first.
