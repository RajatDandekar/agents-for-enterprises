# Lecture 1 · The Before and the After: speaker notes (v4, Northbridge)

Sat 31 Oct 2026, 7:00–9:00 AM IST. 106 slides: 13 part slides and 23 “Ask the class” slides go by fast; about 70 content plates.
Slide numbers below are the deck's counter (bottom right). `[click]` = one step. Timings are targets; the running clock is in brackets.

Everything on a plate is either Northbridge seed data (WORLD_V4.md), a run of ours (experiments/logs, experiments/production),
or a cited public source written on the plate. If a figure shows a green **TODO(v4 data)** card, the run behind it has not
landed yet: say "this one fills in from our run" and move on.

Live links: the Experience is `https://rajatworkspace--northbridge-experience.us-east.modal.run` (`/`, `/before`, `/brief`, `/after`, `/tools`, `/studio`).
Do not redeploy it during class (a new container re-seeds every player's Northbridge).

---

## Part 0 · Opening (7:00–7:06)

**1 · Title.** While people join: "Drop your role and your city in the chat."

**2 · Vizuara.** Plain words, no numbers: we teach AI from first principles, and we build AI systems with companies; what we teach is what we build. [click ×2] The three founders.

**3 · Your instructor.** One line of background (PhD Purdue; IIT Madras), what he teaches, and that he built the company, the ERP and the agent the class will use today. No follower or subscriber counts.

**4 · How we teach.** [click ×4] First principles; build it yourself; one running example; learn by doing. "You will never be asked to trust a tool you have not built a version of yourself."

**5 · Ask the class 1: did an AI agent do real work for you this week?** Read a few. "Hold on to the gap between 'it helped me write' and 'it did work inside a company system'. That gap is this course."

## Part 1 · Why agents, and why now (7:06–7:22)

**6 · Part One.**

**7 · The loop that started it.** [click ×3] Thought, action, observation, on Emma's question, written out by hand. "Every agent is this loop with more engineering around it."

**8 · From a loop to production.** Seven points, one line each, ending "the hard part is no longer the demo".

**9 · What companies are doing now.** Momentum on the left, the other side on the right. Read the sources; these are other people's numbers.

**10 · Ask the class 2: why do agent projects get cancelled?** Let them vote; most pick the model.

**11 · Works on Friday, dies on Monday.** The demo and the pilot. "Four ways agents fail in a pilot, in any job."

**12–15 · How agents fail, 01–04.** Keep them simple; no sandbox talk yet. Each slide: the name and one line; read the three everyday examples (finance, sales, HR, support, operations); [click] one real-world case; [click ×2] two "ask yourself" questions.
- 12 more power than the person asking (the July 2025 deleted database).
- 13 breaks a rule it has just quoted (Moffatt v. Air Canada).
- 14 does the same thing twice (why payment systems use a unique key per payment).
- 15 says "done" when it isn't ("sent" that never arrives).

**16 · Ask the class 3: where would you not trust an agent to act alone in your work today?** Money and anything a customer sees will come up.

**17 · None of these is a model problem.** [click] "A better model fixes none of them." [click] the four, all generic: who it acts as (your permissions); the rules it follows (enforced in code); doing things exactly once; proving it is done (checking the real result). [click] "Building that system is agentic systems engineering."

**18 · The mistakes people make.** [click ×4] Demoing only the easy cases; trusting the reply; one all-powerful login; never measuring. [click] "Each has a lecture."

## Part 2 · How we will learn it (7:22–7:26)

**19 · Part Two.**

**20 · Our approach.** The PaperBanana figure. "One company, one agent, Ask Northbridge, growing one piece per lecture. Lectures 1 to 7: we build every piece by hand. 8 to 11: the same agent on the tools industry runs, measured. 12: your own module." [click ×4] build, break, measure, meet the industry tool. [click] "Tools change every quarter. The pieces don't."

**21 · Ask the class 4: one AI tool you use but couldn't explain.** Read a few. "By Lecture 12 you'll be able to explain each of those from first principles, and build it."

## Part 3 · Northbridge needs you (7:26–7:32)

**22 · Part Three, with the QR.** "Everyone open this now, on your phone or laptop, and type your name." Wait about 60 seconds.

**23 · Open the Experience.** [click] the route table. [click] "Stop at the brief. Don't peek at the After."

**24 · A letter from Manchester.** [click ×3], then let the letter appear and read the last line slowly: "Please read what is happening here. Then tell me what you would do." Everything is fictional.

**25 · What the bike shops say.** Hartley Cycles in Bristol, Velo Centraal in Utrecht. [click] [click] Brisa Bikes, two minutes in a chat. "Nobody complains about the bikes. They complain about everything around the bikes."

**26 · One order, five people.** [click ×5] the cast. [click] the order: BAT-500, Voltway Cells, £119.00, £285,600 with VAT, so Daniel must approve. "You will be each of these people in ten minutes."

## Part 4 · What an ERP is (7:32–7:42)

**27 · Part Four.**

**28 · Ask the class: have you used an ERP? Which one, and how did it feel?**

**29 · The ERPs the world runs on.** [click ×6] One sentence each, with its source; dwell on SAP's 2027 deadline.

**30 · One shared record.** Definition; [click] every department reads and writes the same record; [click] a module.

**31 · Every document has a status.** [click] DR, waiting, AP, RL, CL. "Watch DR: it is failure 4, and you are about to meet it on a real screen."

**32 · Procure-to-pay.** [click ×5] who does each step, on which screen.

**33 · Who has to sign?** Seed numbers; let someone drag the slider.

**34 · What a screen is.** [click ×4] the menu of screens, the fields and codes, the buttons, the status bar.

**35 · What a button really does.** Four clicks: the press, the service call (real request), the black box, the reply that fills the screen; then "an agent calls the same services, without the screen".

## Part 5 · The Before (7:42–8:06, includes 15 minutes hands-on)

**36 · Part Five.** "Open /before."

**37 · Your five missions.** [click ×5] one row each. Start a 15-minute timer and stay quiet.

**38–42 · Missions 1 to 5** (after the hands-on, about 1 minute each). The goal, the screens, done looks like, the trap name, and the screen recording (press play; no autoplay; clicks on the video do not change slide).

**43–47 · The five traps.** One line each, with a short clip from mission 4 (traps 1–4) or the goods-receipt screen (trap 5). Read the line, play a few seconds of the clip, move on:
- 43 which Voltway: three suppliers called Voltway; one right, one blocked, one sells paint.
- 44 the overseas tax code: a UK code for a Dutch supplier, and the save is refused.
- 45 the silent Draft: SAVED, but only a Draft, and nobody is told. "Failure 4 on a real screen."
- 46 release refused: on Friday the Draft cannot be sent; four days lost.
- 47 a partial delivery: two trucks, two receipts.

**48 · The Before, measured.** [click] careful. "Knowing every trap removes errors, not steps."

**49 · Where the knowledge lives.** [click ×6] "The ERP holds the rules. People hold the route."

## Part 6 · What was it like? (8:06–8:14) — top priority

**50 · Part Six.**

**51 · Your brief.** Open /brief: the same five questions as the next slides, then the picks. Five minutes.

**52–56 · Ask the class, about the screens they just used.** One minute each; read two answers aloud per slide.
- 52 what felt bad about doing it through screens?
- 53 did it feel slow or boring? Where? (codes, the order of screens, the error messages, phoning someone, waiting for approval)
- 54 if you could change one thing, what would it be?
- 55 how should doing this feel? (think of the best app you use outside work)
- 56 what should it never do without asking you? "Hold that: it becomes the preview-and-yes rule."

**57 · The class wall.** Read the top picks and two unusual answers.

## Part 7 · The After (8:16–8:28)

**58 · Part Seven.** "Open /after, sign in as Emma. Same Ledgerline underneath."

**59 · Northbridge's new home page.** [click ×3]. "Ledgerline has not changed. Only how people reach it."

**60–64 · The missions** (2 minutes each). Each [click] reveals the next turn of the real recorded conversation: the stock across both plants (6,600 packs, 11 days, where the Before showed Manchester only: both are true); the request with a preview and a yes; Daniel's yes as himself (compare failure 1); order and release with the right tax and the open cost centre, saying what the ERP holds (compare failure 4); Aiko's partial receipt.

**65 · Ask the class: how did the After feel compared to the Before? How long did each take you?** Let them type their two times first. [click] the reveal from our runs: Before, first time, about 5.6 minutes of hands-on work by a keystroke estimate (14 screens, 14 codes, 2 error codes); After, 12 messages (6 typed, 6 taps on "yes") and about 1.9 minutes of waiting, measured.

## Part 8 · What is behind this? (8:24–8:27)

**66 · Part Eight.**

**67 · Ask the class: Ledgerline did not change. How did we do this?** Most pick clicking the screens or SQL. Do not reveal yet.

**68 · Ask the class: if you had to engineer it from scratch, what parts would you need?** Collect the list in the chat; slide 75 builds the definition from it.

## Part 9 · How it works (8:27–8:38)

**69 · Part Nine.**

**70 · How it works, underneath: the film (2:45).** Press "Present full screen". It never autoplays; clicks or keys inside it do not change slide. Narration: Daniel (ElevenLabs); music: "Observatory", Out To The World (Epidemic Sound). Let it play as the recap of everything they guessed.

**71 · The pieces.** The overview figure. "Count your list against this." (The answer to slide 67: a model calls the ERP's services through code we wrote.)

**72–74 · Ask the class, three questions instead of explanations.** Each has the teaser "We build each piece in Lectures 2–5." Take three or four answers each and write the good words down:
- 72 what does the AI need, to look up stock or place an order? (actions it may take: tools)
- 73 how does it know which action to take? (the model reads the request and the list of actions, and chooses)
- 74 how does it talk to the old system? (through the same services the buttons call, over a standard plug, MCP)

**75 · So this is an agent.** Built from their answers. [click ×4] an LLM, plus tools, plus a loop, plus rules. Read the definition: "an LLM that uses tools in a loop, under rules, to finish a job for someone."

## Part 10 · Thinking like a production engineer (8:38–8:46)

Model and token costs, where shown, are in US dollars as OpenRouter billed them; Northbridge's own money stays in £.

**76 · Part Ten.**

**77 · Ask the class: what does production grade mean to you?** Take answers: works for everyone, you can see what it did, it never does things twice, you know the cost.

**78 · What a production team does.** The same agent run three ways: our own loop, the OpenAI Agents SDK and LangGraph (two popular frameworks), all traced in Langfuse (an open-source tool companies use to see every step an agent takes), plus several models swapped one at a time. One line each; "we teach every one of these in Lectures 8–11". [click] the finding: all three frameworks finished every mission correctly; the model made the difference.

**79 · Every step, visible.** One real trace in Langfuse: every model call and every action, with its time and cost. Point at the tree; do not go deeper.

**80 · Which model did the job?** One chart; click the buttons if time allows. Five of six models did every mission correctly; Llama 4 Maverick did 4 of 15. The cheapest good model cost about 1/50 of the default. "Bigger is not always better; you choose with your own checks."

**81 · Start thinking like a production engineer.** [click] Every step visible; every result checked; every cost known.

**82 · Ask the class: if your AI assistant made a mistake at work, how would you find out what went wrong?** Good answers: look at what it did step by step; check the real record; ask who approved. "That is what a trace and a check are for."

## Part 11 · The 2026 agent stack (8:50–8:54)

**83 · Part Eleven.**

**84 · The stack.** Nine clicks, one layer each, bottom up: model, gateway, harness, tools and MCP, knowledge, workflows, trust, observability and evals, durable execution and deployment. For each: read the question it answers in quotes, name two tools, say the lecture. The tenth click shows Ask Northbridge on every layer. Anyone can click a layer afterwards.

**85 · Ask Northbridge, whole.** The master architecture. "Every lecture's last slide lights up its piece of this."

## Part 12 · Twelve lectures (8:54–8:57, fast)

**86 · Part Twelve.** "One slide per lecture. I'll go quickly; the slides stay on the hub."

**87–98 · Lectures 1–12.** For each: the story beat, the project, the assignment, in one breath. Slow down on L7 (Trust: Henrik's "can we switch it on?") and L8 (the frameworks the class just saw).

## Part 13 · Your capstone (8:57–8:59)

**99 · Part Thirteen.**

**100 · Your domain, your agent.** [click ×4] the path A1 → demo day. [click] the two options: your own domain from modules/TEMPLATE, or a kit. "Keep it fictional; never bring an employer's real data."

**101 · Graded out of 100, and demo day.** The seven lines; the two overriding rules. [click] the 8-minute slot on Sun 6 Dec.

**102 · Ask the class 14: one job you would hand to an agent tomorrow.** "That may be your capstone."

## Close (8:59–9:00)

**103 · What this course gives you.** [click ×4] role, skills, portfolio, judgement.

**104 · NB1.** Runs in Colab with no key. (Check the cell names against the rebuilt NB1 before class.)

**105 · A1.** Due before Lecture 3, Sat 7 Nov, 7 AM IST.

**106 · Next time: The Brain.** "Tomorrow we take the tools away, and it makes up the stock figure. Then we open the model."

---

### If time runs short
Skip in this order: 33 (the slider), 87–98 (say "the lecture slides are on the hub"), 80, 29's sources.

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
