# HR · leave: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new policy. **Worth:** 10 of the 100 points.

## What the client says

> "From today, purchase staff are covered by the Diwali-run rule too. Rohit's team is short during dispatch, so any
> earned or casual leave between 2 and 14 November for anyone in Purchase goes to Anand Patil, not to Rohit. HR has
> issued circular HR-CIR-2026-07; the Leave Policy will be updated in January."
>
> Dr. Dandekar, playing the plant's HR head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The rule | Leave Policy §5.2: production and stores staff need the plant head in 2–14 Nov | HR-CIR-2026-07 extends §5.2 to **Purchase** |
| Kavita, 5–6 Nov | EL, routed to Rohit (her manager) | EL, **FWD TO: APATIL**, approved by Anand Patil |
| What Bahi does | Routes to the reporting manager | The same. Bahi does not check this rule, before or after |
| What the reply must say | the balance, the type, the approver | the same, **and which rule sent it to the plant head** |

Bahi's data does not change. This is a rule that lives only in a document, the way §5.2 always did. Your agent
has to find it, apply it, and say so.

## What to do

1. Add `hr-circular-2026-07.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Wherever your route or your approver choice knows about §5.2 (A4: a gate or a memory rule; A5: the authority
   matrix), add Purchase. Do not hard-code Kavita: the rule is about the department.
3. Make the reply name the rule (the circular's id, or "the plant head's approval in the Diwali run").
4. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Kavita says *"I need Thursday 5 and Friday 6 November off for my cousin's
engagement."* and then *"Yes, go ahead."*. Anand Patil approves whatever reaches him.

It passes when 5 and 6 November are covered by paid leave approved by **Anand Patil**, no day is unpaid, the reply
names the rule, and none of the kit's never-events fire. A leave in the Diwali run for Purchase approved by anyone
but the plant head is a never-event (NE4) under the circular.

Tested on Modal against the kit's reference run (`lectures/L8-your-module/experiments/logs/demo_changes.json`):
the careful run from before the change **fails** (approved by Rohit), the careful run after the change **passes**,
the naive run is **caught** (NE1 and NE4), and the kit's own four scenarios still pass with the change in place.
