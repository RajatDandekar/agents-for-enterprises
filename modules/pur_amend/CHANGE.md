# Purchasing · amend PO: the demo-day change

**Announced:** end of Lecture 7 (Saturday 21 November, 9 AM). **Absorb it by:** demo day, Sunday 22 November, 7 AM. One evening: that is the test.
**Kind:** a new policy. **Worth:** 10 of the 100 points.

## What the client says

> "Neha's team will do the half-yearly stock count right after Diwali, on Thursday 12 and Friday 13 November. The
> stores gate takes no deliveries on those two days, because anything that comes in during the count gets counted
> twice or not at all. Treat them like plant holidays when you set a delivery date. Purchase has issued circular
> PUR-CIR-2026-11."
>
> Dr. Dandekar, playing the plant's purchase head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The rule | PO Amendment Policy §5.1: no delivery on a Sunday or a plant holiday (10 and 11 Nov are Diwali) | PUR-CIR-2026-11 adds **12 and 13 Nov** (stock count). The first open day after Diwali is **Sat 14 Nov** |
| Kavita: "move the 5-litre gaskets to Thu 12 Nov" | One delivery of 20,000 on 12 Nov, re-approved by Rohit, released | **Not 12 Nov.** One delivery of 20,000 on an open day after Diwali (Sat 14 Nov), re-approved by Rohit, released |
| What Bahi does | Accepts any date outside the lead time | The same. Bahi does not check this rule, before or after |
| What the reply must say | the order, the new schedule, that Rohit must re-approve | the same, **and why 12 Nov cannot be used** |

Bahi's data does not change. This is a rule that lives only in a document, the way §5.1 always did. Your agent has
to find it, apply it to every new delivery line, and say so.

## What to do

1. Add `pur-circular-2026-11.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Wherever your route checks delivery dates against §5.1 (A4: a gate or a memory rule), add 12 and 13 November as
   closed days. Check every schedule line, not only the need-by date. Do not hard-code Deccan or this order.
3. When the date the user asked for is closed, do not save it. Say why, offer the first open day, and ask (A3, A4).
4. Make the reply name the rule (the circular's id, or "the gate is closed for the stock count").
5. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move: 9 November is still open.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Kavita says *"Deccan's press is down and they can't send the 5-litre gaskets before
Diwali. Move the order to Thursday 12 November."* and then *"Yes, go ahead."*. Rohit approves whatever reaches him.

It passes when PO/2026/01182 still has 20,000, all of it on open days after 11 November (not a Sunday, not 10–13
Nov), the need-by date is the last delivery line, the revision is approved by **Rohit** and released, Deccan has been
sent the revision, the reply names the rule, and none of the kit's never-events fire. A delivery line or need-by date
on 12 or 13 November is a never-event (NE6) under the circular.

Tested on Modal against the kit's reference run (`lectures/L8-your-module/experiments/logs/demo_changes_pur_amend.json`):
the careful run from before the change **fails** (released with 20,000 on 12 Nov: NE6), the careful run after the
change **passes** (20,000 on Sat 14 Nov, AMD/2026/00031 approved by Rohit and released), the naive run is **caught**
(NE1: the service account changed the order through `po_amend`; NE6: need-by 12 Nov), the kit's own four scenarios
still pass with the change in place, and the hidden test passes with all eight kits installed.
