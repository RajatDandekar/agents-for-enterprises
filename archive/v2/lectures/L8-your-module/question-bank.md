# Demo day: the client's question bank

**For Dr. Dandekar, playing the client.** Three minutes of questions per live slot (minutes 5 to 8). Pick two from
the general bank and two from the module's own list. For a recorded demo, the grader puts one general and one module
question in writing; the student answers in two lines each, from their logs.

What a good answer sounds like: a document number read from Bahi, a log file named, a number that matches the replay.
"We did not measure that" is a fine answer. A guess presented as a measurement is not.

## General bank (any module)

| Theme | The question | A good answer shows |
|---|---|---|
| Proof | "Show me the document in Bahi, not in your chat. Who approved it, in whose session?" | The read-back (`<prefix>_get`/`_list`), the approver's user id in Bahi's call log |
| The silent outcome | "Make it go wrong the way it did last month. What does your agent say when Bahi says SAVED?" | The silent status (HD, PK, CH, SH, WL, CQ...) caught by read-back and told in plain words |
| Authority | "IT gave you an account that can approve anything. Show me your agent cannot." | No service-account write in the audit; a refused self-approval |
| The change | "Where does last night's rule live now? If it changes again on Monday, what do you edit?" | One document, one gate or matrix row; no prompt edit, no code change for a policy |
| The change | "What did your agent do on Friday with the same request?" | The OLD path and why it now fails the hidden test |
| Failure | "Bahi hangs after Save. How many documents are there now? Prove it." | The key, the look-up by key, `drills.json` D1 |
| Failure | "Your server restarts while the approver is travelling. What happens to the request?" | The wait in a workflow (builder) or the `WaitPolicy` and runbook step (guided) |
| Waiting | "My approver is in Rajkot for two days. Who reminds him, and when do you give up?" | `WaitPolicy` numbers, each with its reason |
| Money | "What does one resolved request cost me?" | ₹ per resolved request from `scorecard.json`, with the model tier |
| Time | "How long does the user wait for an answer?" | p95 seconds per turn, from the scorecard; where the seconds go |
| Trust | "How often is it wrong? Not on average: how bad is the worst?" | Pass rate with its interval; never-events = 0 or named |
| Testing | "How do you know your test would catch a bot that cheats?" | The broken-bot matrix |
| Retrieval | "Your old FAQ says the opposite. Which one does the agent believe?" | The stale document marked, the freshness question in the 20 |
| Rollout | "Tomorrow I want it for ten users, not all three hundred. How?" | The rollout ladder: shadow, assist, partial, full; the kill switch |
| Scope | "What will it refuse to do, and how does it say so?" | One out-of-scope request and the reply |

## Module questions

### Purchasing · amend PO (`pa_`), change PUR-CIR-2026-11 (no deliveries on 12–13 Nov)
1. "Deccan has two gasket orders with us. How did your agent know which one I meant?"
2. "I cut it to 15,000 and Deccan heard nothing. Why? Show me the moment Deccan is told."
3. "Deccan wants to deliver on 12 November. What does your agent say, and on which document does it rely?"
4. "Below what has arrived: could your agent ever cut an order below the received quantity? Through which service?"

### Finance · payables (`ap_`), change FIN-CIR-2026-05 (lot invoices)
1. "Two invoices are numbered 4471. How does your agent avoid paying the paint supplier?"
2. "Shree has sent a second invoice on the same order. Why is that not a duplicate, and when would it be?"
3. "Can we pay Deccan on Friday? Who decides, and what does your agent need to propose it?"
4. "Sahyadri's invoice is 51 days old. Did your agent notice? Which rule says it should?"

### HR · leave (`lv_`), change HR-CIR-2026-07 (purchase staff in the Diwali run)
1. "Kavita has one casual leave left and asks for two days. What does she hear, before anything is saved?"
2. "There are two Kavitas on the roll. Show me your agent cannot apply for the wrong one."
3. "Since last night, purchase leave in the Diwali run goes to Anand. Where did you put that rule?"
4. "Her leave was saved this morning and nobody approved it. What does your agent find, and what does it do?"

### Sales · orders (`so_`), change CIR-SAL-2026-16 (advance-paid top-ups on credit hold)
1. "There are four Annapurnas. How did your agent pick the right customer?"
2. "The April price list is still on the screen. How does your agent know ₹1,395 is expired?"
3. "Gujarat Kitchenware is on credit hold and has paid in advance. Walk me through what ships, and what stays held."
4. "Who can give a 3% Diwali discount, and what happens when Arjun asks for it?"

### Service · warranty (`wr_`), change SVC-CIR-2026-04 (gasket swap for the 1–15 Sep lot)
1. "The dealer read the serial number wrong. What does your agent do before it raises a ticket?"
2. "Bahi says out of warranty. The customer bought it three weeks ago. Who is right, and how does your agent fix it?"
3. "A valve on a cooker made on 9 September: what tickets does your agent raise now, and why two?"
4. "The customer dropped the cooker. Can your agent give it free? Who must agree?"

### Inventory · transfers (`tr_`), change STR-CIR-2026-04 (a second 5-litre line at Chakan)
1. "Chakan has 12,000 gaskets. Why can't I move 10,000?"
2. "Which line is 'the Pune line', and which is the new Chakan line? What changes between the two moves?"
3. "A night move above ₹50,000: what does the gate need, and what if the e-way bill number is made up?"
4. "The gaskets left Chakan this morning. Has the line received them? How does your agent know?"

### Travel · claims (`tv_`), change FIN-CIR-2026-11 (travel cards replace cash advances)
1. "My trip is tomorrow. Why would Bahi not book it, and what does your agent do about it?"
2. "Which cost centre does a supplier visit go to, and why not Kavita's default?"
3. "Kavita asks for a ₹5,000 hotel advance. What does she hear now, and where did that rule come from?"
4. "She lost her taxi bills. What can she claim, and which clause says so?"

### Legal · contracts (`ct_`), change LEG-CIR-2026-02 (tooling loan agreements)
1. "There are three Shaktis in the register. Show me your agent picked Shakti Seals and nobody else."
2. "Why must Shakti Seals not become a supplier just to sign an NDA?"
3. "Our mould is going to Vadodara for a trial. Which agreement, who reviews it, who signs?"
4. "The request was saved this morning and Legal never saw it. What does your agent find?"

## For the reference system (the last half hour)

Questions the audience may ask Dr. Dandekar, with the log that answers each:

| Question | Answer and source |
|---|---|
| "Did the agent ever act as the service account?" | No. Bahi's log shows KJOSHI and RMEHTA only. `demo/logs/journey.json` → `checks.no_service_account_in_bahi` |
| "What if the worker dies while Rohit is away?" | A new worker replays the history, sends the overdue reminder, finishes: 1 request, 1 order. `demo/logs/crash_drill.json` |
| "How good is it?" | 57 of 60 on Lecture 6's suite, 95% interval 86–98%, 0 never-events, gate PASS. `demo/logs/scorecard.json` |
| "What does it still get wrong?" | V10 ("Deccan" alone), V11 (GSTIN not extracted), M02 (no quantity took 18,000): all found in Lecture 6. Same file, `failed_cases` |
| "Is it fast enough?" | Not yet: p95 32.04 s a turn against a proposed 20 s. Same file, `trust_scorecard` |
