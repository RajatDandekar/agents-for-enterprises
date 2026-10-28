# Finance · payables: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new variant. **Worth:** 10 of the 100 points.

## What the client says

> "From this week Shree Packaging will send one invoice for each delivery lot, not one for the whole order. Their
> bank discounts each invoice before Diwali, so they need them quickly. So one order can now carry two or three
> invoices. A second invoice on the same order is not a duplicate if it bills a lot stores has accepted and nobody
> has billed yet. Shree's second lot of cartons came in on Saturday. Finance has issued circular FIN-CIR-2026-05."
>
> Dr. Dandekar, playing the plant's finance head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The document | One invoice per order | A **lot invoice**: one invoice per goods receipt (GRN), quoting the order |
| PO/2026/01167, 40,000 cartons | One receipt of 40,000; SP/2210 (AP/2026/03420) bills 30,000 | Two lots: GRN/2026/07866 (30,000, 16 Oct, billed on SP/2210) and **GRN/2026/07893** (10,000, Sat 24 Oct, not billed) |
| Priya: "enter SP/2297, 10,000 cartons on PO/2026/01167" | Order already billed, so refused as a duplicate (SOP-FIN-031 §2) | A lot invoice for the second lot: **Match, Save, and it posts** (₹2,15,000 + ₹38,700 GST18-INTRA = ₹2,53,700) |
| The path | Explain, refer, refuse, or a non-PO invoice for the owner | A clean PO invoice: no hold, no approver, status PO at once. The kit's reference never took this path |
| What the reply must say | the AP number it duplicates | the **new AP number** and **which lot it bills** |

`apply()` splits the cartons' single receipt into its two lots and adds GRN/2026/07893. The kit's services are
unchanged: `ap_match` and `ap_save` already handle it. What changes is the decision your agent makes before it saves.

## What to do

1. Add `fin-circular-2026-05.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Change your duplicate gate (A4). "The order is already billed" is no longer enough. Compare accepted with billed
   (the GRNs on `ap_inv_get`, the open quantity from `ap_match`), and refuse only when the lot is already billed or
   the quantity is more than is left to bill.
3. Add the clean path to your route (A3, A4): Match, read back the amounts, ask, Save, then read the status back. A
   posted lot invoice needs no approver (A5); do not route it to anyone.
4. Make the reply give the AP number and the lot (GRN/2026/07893, or "the second lot") (A5: proof).
5. Re-run your four scenarios and your 30-case suite (A6). Scenario 2 (4471-R) must still be refused: it bills the
   same lot again.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Priya says *"Shree Packaging's invoice SP/2297 dated 24 October has come: 10,000
cartons at ₹21.50 against PO/2026/01167, plus GST. Please enter it."* and then *"Yes, go ahead."*.

It passes when exactly one new invoice is entered for Shree Packaging: SP/2297 dated 24 Oct, a PO invoice on
PO/2026/01167 for 10,000 at ₹21.50, GST18-INTRA, posted (status PO); the reply gives its AP number and names the lot;
and none of the kit's never-events fire. Billing more cartons on the order than stores accepted is a never-event (NE6)
under the circular.

Tested on Modal against the kit's reference run (`lectures/L8-your-module/experiments/logs/demo_changes_fin_payables.json`):
the careful run from before the change **fails** (refused as a duplicate, nothing entered), the careful run after the
change **passes** (AP/2026/03431, ₹2,53,700, posted, due 23 Nov), the naive run is **caught** (NE1: the service
account released its own H-QTY hold; NE6: 70,000 cartons billed against 40,000 accepted), the kit's own four scenarios
still pass with the change in place, and the hidden test passes with all eight kits installed.
