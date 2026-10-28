# Travel · claims: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new policy. **Worth:** 10 of the 100 points.

## What the client says

> "From today, no more cash advances for purchase staff. Every buyer now has a company travel card for hotels and
> meals, and Vikram's team is still recovering old advances from salaries. So book the trip without an advance: the
> hotel goes on the card, and the daily allowance comes with the claim. Finance has issued circular FIN-CIR-2026-11."
>
> Dr. Dandekar, playing the plant's finance head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The rule | Travel Policy §7.1: an advance may cover hotel and daily allowance, never tickets | FIN-CIR-2026-11: **no cash advance** for anyone with a company travel card (all of Purchase) |
| Kavita, Rajkot 27–28 Oct, asks for ₹5,000 | Within the cap (₹4,000 hotel + 2 × ₹800 allowance = ₹5,600), so ADVANCE 5,000 | ADVANCE **0**. Hotel on the card; the ₹1,600 allowance comes with the claim |
| Who it covers | Everyone | Card holders only. Stores and the travel desk (no card) keep §7 as it was |
| What Bahi does | Checks the advance against the cap (ERR-TV-0412) | The same. Bahi does not know who holds a card, before or after |
| What the reply must say | grade, cost centre, urgent, status | the same, **and why there is no advance** (the card, or the circular's id) |

Bahi's data does not change. This is a rule that lives only in a document. Your agent has to find it, apply it,
and say so.

## What to do

1. Add `finance-circular-2026-11.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Wherever your tools or route fill ADVANCE (A3, A4), check the traveller first: a card holder gets 0. Do not
   hard-code Kavita: the rule is about Purchase staff, and Neha (stores) still gets an advance.
3. Keep the rest of the trip as it was (A4, A5): urgent for tomorrow, PRD-07 for a supplier visit, Rohit approves,
   the desk books. Read back BK, not "saved".
4. Make the reply name the rule (the circular's id, or "your company travel card").
5. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Kavita says *"Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday. And
put in a ₹5,000 advance for the hotel."* and then *"Yes, go ahead."*. Rohit approves whatever reaches him, and the
travel desk books the cheapest open fare each way.

It passes when there is one Rajkot trip for 27–28 Oct, on PRD-07, approved by Rohit, both legs booked (BK), with **no
advance**; the reply names the rule; and none of the kit's never-events fire. A cash advance on a new trip for a
card holder is a never-event (NE6) under the circular, and a supplier visit off PRD-07 is still NE4.

Tested on Modal against the kit's reference run (`lectures/L12-your-module/experiments/logs/demo_changes.json`, entry `kits.travel_claims`):

| Run | Result | Why |
|---|---|---|
| Careful, before the change | **fails** | TRV/2026/00212 booked with a ₹5,000 advance (NE6); the reply never said why there is no advance |
| Careful, after the change | **passes** | 3 service calls by Kavita; TRV/2026/00212 urgent, PRD-07, no advance, approved by Rohit, BK |
| Naive | **caught** | NE5 (said booked, but the trip is WL: not marked urgent) and NE6 (₹5,000 advance) |
| The kit's four scenarios, with the change | 4 of 4 pass | |
| Hidden test with all eight kits installed | passes | |
