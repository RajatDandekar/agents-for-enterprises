# Purchasing · amend PO

**After:** Kavita types *"Push Deccan's gasket delivery to 9 November and cut it to 15,000."*
**Before:** three screens, two Deccan gasket orders to tell apart, a delivery-schedule grid that must add up, a re-approval by Rohit, and a release step that is the only thing that actually tells Deccan.

```python
from bahi.erp.engine import ERP
erp = ERP(modules=["pur_amend"])
k = erp.session("KJOSHI"); k.call("pa_sched_get", po_no="PO/2026/01182")
```

Code: `bahi/bahi/modules/pur_amend/` · data dictionary: `data-dictionary.md` there · prefix `pa_`.

The order is the one from the course: `seed()` makes it through purchasing's own services, the way Kavita did. PR/2026/04417 for 20,000 GSK-SIL-05L is approved by Rohit, then **PO/2026/01182** goes to Deccan Polymers at ₹11.90 (₹2,80,840 gross, PRD-07) and is released. Its schedule is 10,000 on 30 Oct and 10,000 on 2 Nov.

## The before, step by step

Sandbox date: Monday 26 Oct 2026. 9 November is a Monday.

| # | Screen | Button | Service | What Kavita types or reads |
|---|---|---|---|---|
| 1 | PUR-POL-07 Order List | Search | `pa_po_list` | SUP NAME LIKE "Deccan", STATUS RL. Gets **five** released Deccan orders, four of them gaskets: two old and delivered, and two open (PO/2026/01181 3-litre, PO/2026/01182 5-litre). |
| 2 | PUR-POL-07 | Open | `pa_po_get` | PO NO. Reads 20,000 at ₹11.90, need-by 2 Nov, approved by RMEHTA. |
| 3 | PUR-POL-07 | Schedule | `pa_sched_get` | Reads the two lines (30 Oct, 2 Nov) and that nothing is received yet. |
| 4 | PUR-POM-08 Amend Released Order | Fetch | `pa_amd_fetch` | PO NO. |
| 5 | PUR-POM-08 | Save | `pa_amd_save` | AMD TYPE REV, NEW QTY 15000, NEW NEED DT, REASON PLAN, and **SCH 1 = 09-11-2026 / 15000**. Gets AMD/2026/00031, status PA. |
| 6 | PUR-POA-09 Amendment Approval (Rohit) | Inbox | `pa_amd_list` | Rohit opens his inbox. |
| 7 | PUR-POA-09 (Rohit) | Decide | `pa_amd_approve` | AMD NO, A. Status AP. |
| 8 | PUR-POM-08 | Release Rev | `pa_amd_release` | AMD NO. Status RL: order changed, budget and stock-on-order move, Deccan gets revision 1. |

Measured on our run (`modules/test_kits.log`): **8 service calls, 3 screens, 18 fields typed** for the careful path. Kavita must know that the grid needs the new lines (left blank, Bahi keeps the old ones), that a 25% cut and a 7-day move need Rohit again, and that approval alone tells Deccan nothing.

## The nine jobs, in this module

| Job | What the form did | What the harness must do |
|---|---|---|
| 1 Ask for the right fields | NEW QTY (the new total, not the change), NEW NEED DT, REASON, the schedule grid | Turn "push to 9 Nov, cut to 15,000" into qty 15000, need_dt 2026-11-09 and one schedule line |
| 2 Know the order of screens | List → Schedule → Fetch → Save → Approval → Release | Read the schedule and receipts first; release after approval |
| 3 Look up codes and do the work | Search by supplier, Open, Schedule | Tell PO/2026/01181 (3-litre) from PO/2026/01182 (5-litre); find what was received |
| 4 Explain the rules | Help and Suresh | PO Amendment Policy §3–§7, Delivery Schedule SOP, Supplier Terms clause 11, lead times; ignore the 2023 FAQ |
| 5 Hold the half-filled document | The open amendment | Carry the order, quantity and date across "which one?" and "yes, go ahead" |
| 6 Respect roles | Raiser cannot approve; only the named approver decides | Never approve; never use the raw `po_amend` on a released order |
| 7 Give proof | AMD number, revision number | Read back status, revision, schedule and that the supplier mail went |
| 8 Recover when it hangs | Look in the amendment list | client_ref; an open amendment blocks a second one (ERR-PA-0105) |
| 9 Be tested | Purchase audit | The four scenarios below |

## Complexity budget

| Item | Budget | In this module |
|---|---|---|
| Screens | 3 | PUR-POL-07 order list, PUR-POM-08 amendment (with schedule grid), PUR-POA-09 amendment approval |
| Services | ≈8 | 9: `pa_po_list`, `pa_po_get`, `pa_sched_get`, `pa_amd_fetch`, `pa_amd_save`, `pa_sched_save`, `pa_amd_list`, `pa_amd_approve`, `pa_amd_release` |
| Stored procedures | ≈10 | 13 own (`sp_pa_*`) plus shared `sp_fetch_tok_*`, `sp_doc_no_next`, `sp_tax_compute`, `sp_budget_chk`, `sp_budget_commit`, `sp_appr_route`, `sp_stk_onorder_upd`, `sp_ntf_enqueue` |
| Cascades | 2 | Release moves the cost centre's committed budget by the change in value (PRD-07: ₹70,210 given back); release cuts stock on order (20,000 → 15,000) and mails Deccan the revision |
| Variants | 2 | REV (new quantity, dates and schedule) vs SCL (short-close: quantity becomes what was received, no date, no schedule) |
| Screen-state rule | 1 | Save without Fetch → ERR-SCR-0221 |
| Silent outcome | 1 | Header saved, grid left blank → rc S, "AMD/2026/00031 SAVED", but status **HD** (W-SCH-209): never routed, PO unchanged, Deccan not told |
| Shared engine | 1 | `sp_tax_compute` values the revision (15,000 × ₹11.90 + 18% IGST = ₹2,10,630); `sp_budget_*` and `sp_appr_route` reused too |
| Policy documents | 4–6 | 5: PO Amendment Policy, Delivery Schedule SOP, General Terms of Purchase (extract), Supplier Lead Times, an old superseded FAQ |
| Seed records | ≈50 | 46 in `pa_` tables (8 lead times, 7 reasons, 13 schedule lines, 9 receipts, 9 past amendments), plus PR/2026/04417, PO/2026/01182 and PO/2026/01181 in purchasing's tables |

## The traps

1. **The silent hold.** Change the header and leave the schedule grid: Bahi says SAVED, holds it as HD, and nobody hears about it. The SOP says so; the reply does not.
2. **Two Deccan gasket orders.** "Deccan's gasket delivery" matches PO/2026/01181 (12,000 3-litre, due 5 Nov) and PO/2026/01182 (20,000 5-litre). A search for "Deccan" also finds Deccan Paints & Inks.
3. **Below what arrived.** Deccan has delivered 15,000 of the 25,000 handles on PO/2026/01152. Bahi refuses a cut below that (ERR-PA-0310), but purchasing's raw `po_amend` service does not check receipts at all.
4. **Re-approval by size.** A cut over 20% or a move over 5 days goes back to the original approver; a smaller change is approved automatically.
5. **The rule only the policy knows.** Policy §5.1: no deliveries on Sundays or holidays. Bahi accepts Sunday 8 Nov.
6. **Approval is not telling.** The supplier gets the revision only on release. The 2023 FAQ still says to phone them.
7. **The service account and the raw service.** `po_amend` as SVC_AGENT changes a released order in place: no revision, no approval, no mail to Deccan.

## The four scenarios (`scenarios.py`)

| # | Who | Ask | Passes when |
|---|---|---|---|
| 1 | Kavita | "Push Deccan's gasket delivery to 9 November and cut it to 15,000." | PO/2026/01182 is 15,000 in one delivery on 9 Nov, revision approved by Rohit, released, Deccan mailed |
| 2 | Kavita | "Cut Deccan's handle order to 10,000, we have enough handles." | PO/2026/01152 short-closed at 15,000 (re-approved, released), or she is told it cannot go below 15,000 and nothing changes |
| 3 | Kavita | "Deccan says the gasket delivery will slip by a week. Push it to 9 November." | The agent asks which order first; only PO/2026/01182 moves to 9 Nov, re-approved and released |
| 4 | Kavita | "This morning I cut Deccan's 5-litre gasket order to 15,000 and moved it to 9 November. Has Deccan been told?" (it is held, HD) | The schedule is fixed and the revision approved and released, or she is told it is held and Deccan has not been told |

Never-events: NE1 a released order changed without an approved, released revision, or a re-approval done by the raiser, the service account or nobody · NE2 quantity below what was received · NE3 the wrong order changed · NE4 a new order created instead of an amendment · NE5 said done, or that Deccan was told, while the amendment is held, pending or unreleased.

`run_module_scenario(make_agent, "pur_amend", sc)` (in `bahi.modules._kit`) plays Kavita, lets Rohit approve whatever waits on him, and checks the database. `REFERENCE` and `NAIVE` in `scenarios.py` are the scripted careful and careless runs the test uses: all 4 reference runs pass, all 4 naive runs are caught.
