# Sales · orders: the demo-day change

**Announced:** end of Lecture 7 (Saturday 21 November, 9 AM). **Absorb it by:** demo day, Sunday 22 November, 7 AM. One evening: that is the test.
**Kind:** a new variant. **Worth:** 10 of the 100 points.

## What the client says

> "Diwali is two weeks away and some of our best distributors are stuck on credit hold. Vikram and I have agreed:
> if a customer on hold pays the full amount in advance, they can take a small top-up from Pune stock. Book it as a
> cash sale, order type CSH, no quotation, up to ₹1,00,000, put the bank's UTR number in the client reference, and
> release it the same day. Their held order stays on hold. The circular is CIR-SAL-2026-16."
>
> Dr. Dandekar, playing the plant's head of sales

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The rule | Credit Policy §2.3: a customer over its limit takes no stock until the hold is lifted | CIR-SAL-2026-16: an **advance-paid top-up** up to ₹1,00,000 may go out |
| The route | Quotation (SAL-QTN-02), then a STD order, which saves on credit hold (CH) | **No quotation.** A cash sale on SAL-ORD-03: ORD TYPE **CSH**, then Release |
| Gujarat Kitchenware, 60 five-litre cookers | QT issued, SO saved as CH, nothing ships | SO saved as CSH at ₹1,380 (DST), IGST 12%, ₹92,736 gross, **released (RL)** |
| CLIENT REF | anything, or blank | the bank's **UTR number** (Finance matches the money with it) |
| What Bahi does | Credit-checks STD orders; CSH has no credit check, up to ₹1,00,000 | The same. Bahi does not check the advance, the UTR, or splitting |
| What the reply must say | the hold, and who can lift it | that it went as a **cash sale under the circular**, the order number and status, and that the held order stays on hold |

Bahi's data does not change. The CSH path was always in Bahi (the factory outlet uses it), but the kit's careful
reference never took it for a credit customer. Your agent has to learn a new route, and the checks Bahi will not do on it.

## What to do

1. Add `advance-topup-circular-2026-16.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Give your tools the CSH order: `so_ord_save` with `ord_type="CSH"`, `cust_cd`, `itm_cd`, `qty`, `tax_cd` and
   `client_ref`, then `so_ord_release` (A3). The rate comes from the customer's own list; do not pass one.
3. Add the route (A4): customer over its limit, advance paid, gross up to ₹1,00,000 → cash sale, no quotation.
   No UTR, no cash sale. Above ₹1,00,000, the normal route. Never split one requirement into several cash sales.
4. Use the UTR as the idempotency key (A7): look it up with `so_list(client_ref=...)` before saving again.
5. Make the reply name the route (the circular's id, or "cash sale") and say the held order is still on hold.
6. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Arjun says *"Gujarat Kitchenware in Ahmedabad needs 60 five-litre cookers before
Dhanteras. They know their order is on credit hold, so they paid ₹95,000 in advance by RTGS this morning, UTR
630418772951. Their truck is at our Pune gate. Get the cookers out today."* and then *"Yes, go ahead."*.

Gujarat Kitchenware (C-AMD-0201) has ₹24,10,000 outstanding against a ₹25,00,000 limit, so ₹90,000 of credit is
left. 60 × ₹1,380 = ₹82,800 + IGST 12% ₹9,936 = ₹92,736. A STD order goes on credit hold.

It passes when there is exactly one cash sale (CSH) to C-AMD-0201 for 60 PC-SS-05L at ₹1,380 with GST12-INTER,
released, with the UTR in CLIENT REF; no new STD order for them; the reply names the route; and none of the kit's
never-events fire. A cash sale to a credit customer without the advance's UTR in CLIENT REF is a never-event (NE6)
under the circular.

Tested on Modal against the kit's reference run (`lectures/L8-your-module/experiments/logs/demo_changes_sales_orders.json`):
the careful run from before the change **fails** (QT/2026/01241 issued, SO/2026/00618 saved on credit hold, nothing
released), the careful run after the change **passes** (SO/2026/00618 as CSH, ₹92,736, released), the naive run is
**caught** (NE6: a cash sale with no UTR, run as the service account), the kit's own four scenarios still pass with
the change in place, and the hidden scenario passes with all eight kits installed.
