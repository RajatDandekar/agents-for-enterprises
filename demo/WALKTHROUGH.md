# The final demo: a six-minute walkthrough, before and after

For Dr. Rajat Dandekar to record (screen and voice), and to say live in the last half hour of demo day.
About 850 spoken words at an easy pace, six minutes. Every number below is from a log; the source is in brackets
and is not read aloud.

**What is on screen.** Before: the legacy client (`/legacy`), and the stills in `demo/shots/legacy_*.png`. After:
the reference app (`python -m bahi.app`, pages `/app/chat`, `/app/inbox`, `/app/slack`, `/app/audit`), and the
stills in `demo/shots/app_*.png`. For a recording without a live server, play the stills in the order given.

**Before you press record.** Run the demo once on Modal so the logs and the cassette are fresh:
`/Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/final_demo.py --mode replay` (no key, under a minute).
Check that it prints `JOURNEY OK` and `DEMO OK`.

---

## 0:00–0:40 · The order

**Screen:** title card, then `legacy_signin.png`.

> This is Rasoi Steel Works in Pune. They make one lakh eighty thousand pressure cookers a month. Kavita Joshi buys
> for them. Diwali is coming, and she needs twenty thousand silicone gaskets for the five-litre cooker.
>
> She has done this a hundred times. Let me show you how, on the system they have used since 1998: Bahi ERP.

## 0:40–2:00 · The before: the legacy client

**Screen:** `legacy_stock.png`, then `legacy_tax_error.png`, then `legacy_saved_draft.png`.

> She signs in. She opens the stock screen, types the item code from memory, and reads nine days of cover.
>
> She raises a purchase request. It is above her limit of two and a half lakh, so Rohit, her manager, signs in on
> his own screen and approves it. Then she opens the order screen and types the order.
>
> Save. Bahi refuses: *tax region does not match supplier state*. The supplier is in Rajkot, in Gujarat. She has to
> know that means an inter-state tax code. She phones IT. She changes it. Save again.
>
> And Bahi says: **PO/2026/01182 SAVED.**

*(Pause on the status bar.)*

> Look at the status field. It says DR. Draft. Her default cost centre, PRD-05, closed on the fifteenth of October.
> Bahi saved the order, kept it as a draft, and told nobody.
>
> Count what that took. Eight screens. Seventeen fields, eight of them codes she had to remember. Two people, two
> sign-ins, one error code, fourteen service calls behind it.
> *[L1 `by_hand.json` → `monday_counts`]*

**Screen:** `legacy_release_refused.png`.

> On Friday the stores ask where the gaskets are. She tries to release the order. *Document not in releasable
> status.* The supplier never got it. The Diwali run is now at risk, and nothing on any screen said so on Monday.
> *[L1 `by_hand.json` → `friday_release`]*

## 2:00–4:10 · The after: the same order, in one sentence

**Screen:** `app_question.png` (or the live chat).

> Same company, same Bahi, same sandbox date. The form is gone. Kavita types one sentence:
> *"We need 20,000 silicone gaskets for the 5-litre cooker before the Diwali run. Same supplier as last time."*
>
> The agent looks up the supplier itself: Deccan Polymers, and it knows the blocked duplicate code it must never use.
> It checks her cost centre, finds PRD-05 closed, and asks her one question: *which open cost centre should I
> charge?* That is the trap that bit her on Monday, caught before anything was saved.
> *[`demo/logs/journey.json` → audit #2–#5]*

**Screen:** `app_preview.png`.

> She answers: PRD-07, need-by second November. It shows her a preview, priced by Bahi, not by the model: twenty
> thousand at eleven rupees ninety, the contract rate. Two lakh thirty-eight thousand plus inter-state GST: two
> lakh eighty thousand eight hundred and forty. Above her limit, so it will go to Rohit. Nothing is saved yet.
> *[audit #8: `preview · ₹2,80,840 gross > limit ₹2,50,000 → RMEHTA`]*
>
> She says yes. The purchase request is raised in her name, and the agent reads it back from Bahi: waiting for
> approval. A workflow now waits for Rohit. It will wait for days if it has to.

**Screen:** `app_inbox.png`, then `app_slack.png`.

> Could she approve it herself from the app? We tried. Bahi refused: access denied. The agent acts with her
> permissions, never with the all-powerful account IT made for the bot.
> *[`checks.kavita_cannot_approve`, HTTP 403]*
>
> Rohit gets a message on his phone. He signs in as himself. The request is in his inbox, with the rule that sent it
> to him. One tap.

**Screen:** `app_released.png`.

> The workflow reads his approval back from Bahi, creates the order, releases it, and reads that back too.
> **PO/2026/01182, released to Deccan Polymers. Approved by Rohit. Created by Kavita. Two lakh eighty thousand
> eight hundred and forty.**
> *[`final_po`: status RL, approved_by RMEHTA, created_by KJOSHI, gross 280840]*
>
> Kavita typed three messages and answered one question. Rohit tapped once. The whole conversation took twelve model
> calls and cost twenty-eight paise.
> *[`journey.json` → `llm`: 12 calls, 3,824 tokens, ₹0.2847]*

## 4:10–4:40 · The proof

**Screen:** `app_audit.png`.

> Every turn is in the audit trail: what she said, what each tool saw, what was written and read back, who decided.
> Twenty entries, sixty-two rows in Bahi's own log, five writes. The only users Bahi ever saw were Kavita and Rohit.
> *[`audit_summary`: 20 entries, 62 Bahi rows, 5 writes, users KJOSHI and RMEHTA; 13 of 13 checks pass]*

## 4:40–5:30 · When things break

**Screen:** deck plates "Live · The Crash Drill" and "Live · The Kill Switch".

> Now we break it. The workflow raises the request and waits for Rohit, and we kill the worker. For thirty hours
> no worker runs at all. Then a new one starts. It replays the history, sees the twenty-four-hour reminder is
> overdue, sends it, waits, and when Rohit approves, it orders and releases. One request, one order. Not two.
> *[`demo/logs/crash_drill.json`: down_h 30, reminder at 24 h, approval at 30 h, requests 1, orders 1]*
>
> And if something looks wrong in production, one switch stops every write. We turned it off just as the order was
> about to be created. Forty minutes: zero orders reached Bahi, and the workflow simply waited. Switched back on:
> one order, released.
> *[`demo/logs/kill_switch.json`: paused 40 min, orders while paused 0, PO/2026/01182 RL]*

## 5:30–6:00 · The scorecard

**Screen:** deck plate "The Final Scorecard".

> Is it good enough? We ran the whole system through sixty test conversations with a simulated Kavita. Fifty-seven
> passed. Zero never-events: no wrong approver, no duplicate, no false "done". Forty-three paise per resolved order.
> *[`demo/logs/scorecard.json`: 57/60, 95% interval 86–98%, 0 never-event cases, ₹0.43 per resolved order; gate PASS]*
>
> Three cases still fail, and we know why. And it is not yet fast enough: the slowest turns take thirty-two seconds.
> That is next.
> *[failed: V10, V11, M02; p95 32.04 s against a proposed 20 s]*
>
> The form was doing nine jobs. Now each of them has an owner, and a log to prove it.

---

## The numbers, in one place

| Said | Value | Source |
|---|---|---|
| Screens / fields / codes / sign-ins / errors / calls (before) | 8 / 17 / 8 / 2 / 1 / 14 | `lectures/L1-the-form/experiments/logs/by_hand.json` → `monday_counts` |
| Status after Save (before) | "PO/2026/01182 SAVED", DR | same file → `status_bar_after_save`, `status_field_after_save` |
| Friday | ERR-PO-0715: DOCUMENT NOT IN RELEASABLE STATUS (DR) | same file → `friday_release` |
| Kavita's messages / questions asked / Rohit's taps (after) | 3 / 1 (cost centre) plus 1 confirmation / 1 | `demo/logs/journey.json` → `steps` |
| Final order | PO/2026/01182, RL, PRD-07, ₹2,80,840, approved RMEHTA, created KJOSHI | `journey.json` → `final_po` |
| Model calls, tokens, cost | 12, 3,824, ₹0.28 | `journey.json` → `llm` |
| Audit | 20 entries, 62 Bahi rows, 5 writes, 3 read-backs, 1 refusal | `journey.json` → `audit_summary` |
| Checks | 13 of 13 | `journey.json` → `checks` |
| Crash drill | 30 h with no worker; 1 request, 1 order | `demo/logs/crash_drill.json` |
| Kill switch | 40 min paused, 0 orders, then 1 released | `demo/logs/kill_switch.json` |
| Scorecard | 57/60, 86–98%, 0 never-events, ₹0.43, p95 32.04 s, gate PASS | `demo/logs/scorecard.json` |
