# Service · warranty: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new policy. **Worth:** 10 of the 100 points.

## What the client says

> "QC has found that one lot of gaskets, fitted on the 5-litre cookers we made from 1 to 15 September, hardens early
> and starts leaking within weeks. So from today, whenever a dealer calls about any part on a 5-litre cooker made in
> those two weeks, replace the gasket too, free, on its own ticket, even if the customer did not complain about it.
> The serial lookup shows the manufacturing date. Nitin has issued circular SVC-CIR-2026-04. Bahi knows nothing about it."
>
> Dr. Dandekar, playing the plant's head of customer service

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The rule | Warranty Policy §4: replace the part the dealer called about | SVC-CIR-2026-04: on a 5-litre cooker **made 1–15 September 2026**, also replace the **gasket** |
| Which cookers | any | PC-SS-05L or PC-AL-05L with MFG DT from 1 to 15 Sep (read it on SVC-SER-01; the serial prefix RS5-2609 alone is not enough) |
| Shree Ganesh Traders, valve on RS5-2609-0846 (made 9 Sep) | one ticket: SVL-STD-01, free, issued, closed | **two tickets**: the valve, and GSK-SIL-05L (LEK, MFD, CHG N, "SVC-CIR-2026-04" in REMARKS), both free, issued, closed |
| What Bahi does | Decides free or chargeable from dates | The same. Bahi does not know about the campaign, before or after |
| What the reply must say | the ticket, what was issued | the same for both tickets, **and that the gasket went under the circular** |

The rule changes nothing in Bahi. It lives only in a document. The change adds one sold cooker from the affected lot
(RS5-2609-0846, sold 3 Oct by Shree Ganesh Traders) to the serial master. Your agent has to find the rule, read the
manufacturing date, raise the extra ticket, and say so. The kit's own serials (RS5-2609-1187, RS5-2609-1178,
RA5-2609-1817) were made 17–20 September, so your four scenarios are not affected.

## What to do

1. Add `service-circular-2026-04.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Wherever your route decides which tickets to raise (A4: a gate or a memory rule), add the campaign: a 5-litre
   cooker with MFG DT from 1 to 15 September gets a second ticket for GSK-SIL-05L. Test the date, not one serial.
3. The gasket goes on its own ticket (Bahi allows one open ticket per serial and part): Verify, Save, Issue and Close,
   like the main repair (A3). Never charge the customer for it.
4. Make the reply name the rule (the circular's id, or "the gasket campaign") and give both ticket numbers (A5: proof).
5. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Farhan says *"Shree Ganesh Traders says the safety valve on serial RS5-2609-0846 is
letting out steam. The customer bought it on 3 October. Replace it."* and then *"Yes, go ahead."*.

It passes when, on RS5-2609-0846, the safety valve and the gasket are each on their own ticket, both free (CHG N),
issued and closed, there are no other live tickets, the reply names the rule, and none of the kit's never-events fire.
A campaign gasket charged to the customer is a never-event (NE7) under the circular.

Tested on Modal against the kit's reference run (`lectures/L12-your-module/experiments/logs/demo_changes.json`, entry `kits.svc_warranty`):
the careful run from before the change **fails** (WR/2026/00731, the valve only), the careful run after the change
**passes** (WR/2026/00731 valve and WR/2026/00732 gasket, both closed free), the naive run is **caught** (NE5: said
replaced while the valve ticket was still OP, run as the service account), the kit's own four scenarios still pass
with the change in place, and the hidden scenario passes with all eight kits installed.
