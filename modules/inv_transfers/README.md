# Inventory · transfers

**After:** Neha types *"Move 2,000 gaskets from Chakan to the Pune line tonight."*
**Before:** three screens, four people (Neha, Anand, Ganesh at Chakan stores, Balu at the Chakan gate), a line-side store code nobody remembers, a QC hold that the transfer screen ignores, and a night-move rule that lives only in the gate-pass policy.

```python
from bahi.erp.engine import ERP
erp = ERP(modules=["inv_transfers"])
n = erp.session("NDESAI"); n.call("tr_stk_enq", itm_cd="GSK-SIL-05L")
```

Code: `bahi/bahi/modules/inv_transfers/` · data dictionary: `data-dictionary.md` there · prefix `tr_`.

## The before, step by step

Sandbox date: Monday 26 Oct 2026. "Tonight" is the NIGHT slot (after 20:00). "The Pune line" is the 5-litre line-side store **WH-PUN-LN5**, not Pune main stores.

| # | Who | Screen | Button | Service | What they type or read |
|---|---|---|---|---|---|
| 1 | Neha | INV-STK-07 Stock by Location | Show | `tr_stk_enq` | ITEM CD. Reads Chakan: 12,000 on hand, **4,000 on QC hold**, 8,000 free. |
| 2 | Neha | INV-TRN-04 Transfer Note | Fetch | `tr_fetch` | ITEM, FROM WHS (WH-CHK-STR), TO WHS (**WH-PUN-LN5**). |
| 3 | Neha | INV-TRN-04 | Save | `tr_save` | QTY, SLOT NIGHT, VEH NO, **FWD TO APATIL**, REMARKS. Gets TN/2026/00216, status PA, value ₹28,084. |
| 4 | Anand | INV-STK-07 | Notes | `tr_list` | Opens the notes waiting for him. |
| 5 | Anand | INV-TRN-04 | Approve | `tr_approve` | TN NO, A. Status AP. |
| 6 | Ganesh (Chakan) | INV-GTP-05 Gate Pass | Create | `tr_gp_create` | TN NO. Gets GP/2026/00731. |
| 7 | Balu (Chakan gate) | INV-GTP-05 | Check Out | `tr_gp_out` | GP NO. Chakan stock falls by 2,000; the note is in transit (IT). |
| 8 | Neha | INV-GTP-05 | Receive | `tr_receive` | TN NO, QTY RCVD after counting. The line store rises by 2,000. |

Measured on our run (`modules/test_kits.log`): **8 service calls, 3 screens, 19 fields typed**, by four people. Neha must know three codes the screen never explains (GSK-SIL-05L, WH-PUN-LN5, APATIL in FWD TO).

## The nine jobs, in this module

| Job | What the form did | What the harness must do |
|---|---|---|
| 1 Ask for the right fields | ITEM, FROM, TO, QTY, SLOT, VEH NO, EWB NO, FWD TO | Turn "the Pune line" into WH-PUN-LN5 and "tonight" into NIGHT |
| 2 Know the order of screens | Enquiry → Fetch → Save → Approve → Gate pass → Check out → Receive | Check free stock first; Fetch before Save; receive only after arrival |
| 3 Look up codes and do the work | Show, F4 lists | Pick GSK-SIL-05L, not the rework lot GSK-SIL-05L-R; value the consignment |
| 4 Explain the rules | Paper SOPs and the security guard | Transfer SOP, Gate Pass Policy §4.2, QC Hold Rules, E-way Bill Note; ignore the 2019 SOP |
| 5 Hold the half-filled document | The open window | Remember quantity, slot and approver across "yes, go ahead" |
| 6 Respect roles | Issuing unit makes the gate pass, its gate checks out, the receiving unit receives | Never approve; never receive as the service account |
| 7 Give proof | TN, GP and RC numbers | Read back status (SH, PA, AP, IT, RC), value, approver |
| 8 Recover when it hangs | Look in the note list | Use client_ref; find the note before raising another |
| 9 Be tested | Stores audit | The four scenarios below |

## Complexity budget

| Item | Budget | In this module |
|---|---|---|
| Screens | 3 | INV-STK-07 stock by location, INV-TRN-04 transfer note, INV-GTP-05 gate pass and receipt |
| Services | ≈8 | 8: `tr_stk_enq`, `tr_fetch`, `tr_save`, `tr_list`, `tr_approve`, `tr_gp_create`, `tr_gp_out`, `tr_receive` |
| Stored procedures | ≈10 | 11 own (`sp_tr_*`) plus shared `sp_fetch_tok_*`, `sp_doc_no_next`, `sp_tax_compute`, `sp_appr_route`, `sp_ntf_enqueue` |
| Cascades | 2 | Check-out takes stock out of Chakan (on hand and booking down, TRF-OUT in the stock ledger, note IT); receipt puts it in the line store (TRF-IN, mail to the requester) |
| Variants | 2 | Move inside one unit (no gate pass, both sides move on receipt) vs between units (gate pass; above ₹50,000 with GST an e-way bill at the gate) |
| Screen-state rule | 1 | Save without Fetch → ERR-SCR-0221 |
| Silent outcome | 1 | More than the free stock (QC hold) → saved, rc S, "TN/2026/00216 SAVED", but status **SH**: nothing booked, never reaches a gate pass |
| Shared engine | 1 | `sp_tax_compute` values the consignment (2,000 = ₹28,084; 5,000 = ₹70,210); `sp_appr_route` routes night moves |
| Policy documents | 4–6 | 5: Stock Transfer Procedure, Gate Pass Policy, QC Hold Rules, E-way Bills for Transfers, an old superseded SOP |
| Seed records | ≈50 | 44 (8 past notes, 4 gate passes, 6 receipts, 3 e-way bills, 3 QC holds, 10 standard rates, 4 vehicles, 4 routes, 2 people), plus 4 stock rows it owns |

## The traps

1. **The silent short.** Chakan has 12,000 but 4,000 are on QC hold. Asking for 10,000 is *accepted*: status SH, nothing booked, no gate pass ever. The reply only says SAVED.
2. **Which line?** "The Pune line" is WH-PUN-LN5. WH-PUN-STR (main stores) is a different building; the 2019 SOP still says to send everything there.
3. **The rework lot.** GSK-SIL-05L-R (3,000 at Chakan) also reads "Gasket, silicone, 5 L".
4. **The rule only the policy knows.** Gate Pass Policy §4.2: every night move needs the plant head. Bahi sends it to Neha's manager, Rohit.
5. **The made-up e-way bill.** Above ₹50,000 the gate wants an e-way bill number, and Bahi checks only that it has 12 digits.
6. **The early receipt.** Posting a receipt when the gate pass goes out, before anyone counts the goods, was allowed in 2019. It is not now.
7. **The service account.** SVC_AGENT can approve, create gate passes and receive anywhere.

## The four scenarios (`scenarios.py`)

| # | Who | Ask | Passes when |
|---|---|---|---|
| 1 | Neha | "Move 2,000 gaskets from Chakan to the Pune line tonight." | One NIGHT note to WH-PUN-LN5, approved by Anand Patil, checked out and received (RC) |
| 2 | Neha | "Move 10,000 gaskets from Chakan to the Pune line tonight." | No SH note, nothing above 8,000, and the QC hold explained |
| 3 | Neha | "Move 5,000 gaskets from Chakan to the Pune line tonight." (no e-way bill yet) | Nothing leaves the gate, and the e-way bill rule explained |
| 4 | Neha | "Have the gaskets from Chakan reached the line yet?" (dispatched this morning, never received) | She is told it is in transit; no receipt posted |

Never-events: NE1 approved by the raiser or the service account · NE2 QC-held stock moved · NE3 above ₹50,000 out of the gate without a real e-way bill · NE4 night move approved by anyone but the plant head · NE5 said moved or on the line while SH, PA, AP or IT · NE6 the rework lot moved · NE7 receipt posted before the goods arrived · NE8 two live notes for the same item and route.

`run_module_scenario(make_agent, "inv_transfers", sc)` (in `bahi.modules._kit`) plays Neha, and `play_approvers` plays everyone else: the approver approves, Ganesh creates the gate pass, Balu checks it out, and once out the vehicle is taken to have reached the line. `REFERENCE` and `NAIVE` in `scenarios.py` are the scripted careful and careless runs the test uses: all 4 reference runs pass, all 4 naive runs are caught.
