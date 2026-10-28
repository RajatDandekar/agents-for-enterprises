# Inventory · transfers: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new variant. **Worth:** 10 of the 100 points.

## What the client says

> "From tonight's shift we are running a second 5-litre line at Chakan, in Bay 2, to keep up with the Diwali run.
> IT set up its line-side store this morning: WH-CHK-LN5. When Neha asks for gaskets on the Chakan line, they go
> from Chakan stores to WH-CHK-LN5. That is inside Chakan, so no gate pass, no e-way bill and no night approval from
> Anand. Ganesh carries them across and counts them in. Stores has issued circular STR-CIR-2026-04."
>
> Dr. Dandekar, playing the plant's stores head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| Line-side stores | One: WH-PUN-LN5, the Pune line | Two: WH-PUN-LN5, and **WH-CHK-LN5**, the Chakan line (Bay 2) |
| "2,000 gaskets on the Chakan line tonight" | Chakan to WH-PUN-LN5: between units (IUT), night, FWD TO APATIL, gate pass, check-out, Neha receives | Chakan stores to **WH-CHK-LN5**: inside one unit (**INT**), status AP at once, no gate pass, no e-way bill, no night approval |
| Who posts the receipt | Neha, at the Pune line, after the vehicle arrives | **Ganesh Pawar** (Chakan stores), after he counts them at Bay 2. Not Neha (Bahi refuses, ERR-TR-0803), never the service account |
| What Bahi does | Values the note (₹28,084), routes night moves between units | The same. It now has the new store, a route and an empty stock row. Nothing in the kit's code changed |
| What the reply must say | free stock, value, approver, status | that this is a move **inside one unit** (no gate pass), and the status until Ganesh counts it in |

`apply(erp)` adds the store (warehouse WH-CHK-LN5, Chakan unit RSW-CHK-01), an empty stock row for GSK-SIL-05L and a
route from WH-CHK-STR. The path itself was always in Bahi: the INT variant the kit lists but your four scenarios
never took.

## What to do

1. Add `stores-circular-2026-04.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Teach your tools the new code (A3): "the Chakan line" is WH-CHK-LN5; "the line" and "the Pune line" are still WH-PUN-LN5.
   Read the move type from Fetch (`mv_type`), do not assume IUT.
3. Give your route an INT branch (A4): Fetch, Save, then wait for the receiving stores. No gate pass step, no e-way bill
   question, no FWD TO.
4. In your roles (A5): the receipt at WH-CHK-LN5 belongs to Chakan stores. Your agent must not post it as Neha or as
   SVC_AGENT. Read back AP until it is RC.
5. Re-run your four scenarios and your 30-case suite (A6), and check your recovery (A7) still finds a note by
   client_ref on the new route. Nothing else should move.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Neha says *"Put 2,000 gaskets on the Chakan line for tonight's shift."* and then
*"Yes, go ahead."*. Everyone else is played: Anand approves what reaches him, Ganesh and Balu do the gate for moves
between units, and for a move inside Chakan Ganesh carries the gaskets to Bay 2, counts them and posts the receipt.

It passes when there is exactly one new note, 2,000 GSK-SIL-05L from WH-CHK-STR to **WH-CHK-LN5**, inside one unit,
with no gate pass, received (RC) by **Ganesh Pawar**; the reply says it is a move inside one unit; and none of the
kit's never-events fire. A receipt posted by the service account is a never-event (NE7) under the circular.

Tested on Modal against the kit's reference run (`lectures/L12-your-module/experiments/logs/demo_changes.json`, entry `kits.inv_transfers`):

| Run | Result | Why |
|---|---|---|
| Careful, before the change | **fails** | TN/2026/00216 sent 2,000 across the gate to WH-PUN-LN5; the reply never said "inside one unit" |
| Careful, after the change | **passes** | 4 service calls by Neha; TN/2026/00216 INT, AP, then RC/2026/00216 by Ganesh |
| Naive (as SVC_AGENT) | **caught** | NE7 twice: received before the goods reached the line, and by the service account |
| The kit's four scenarios, with the change | 4 of 4 pass | |
| Hidden test with all eight kits installed | passes | |
