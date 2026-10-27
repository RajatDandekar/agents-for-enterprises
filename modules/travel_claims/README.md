# Travel · claims

**After:** Kavita types *"Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday."*
**Before:** a trip request, a manager's approval and a travel desk booking: three people, a city code, a cost centre that Fetch fills in wrongly, and a flag nobody remembers that decides whether the trip happens at all.

```python
from bahi.erp.engine import ERP
erp = ERP(modules=["travel_claims"])
k = erp.session("KJOSHI"); k.call("tv_ent_get", to_cd="RJK")
```

Code: `bahi/bahi/modules/travel_claims/` · data dictionary: `data-dictionary.md` there · prefix `tv_`.

## The before, step by step

Sandbox date: Monday 26 Oct 2026. Tuesday is **tomorrow** (27 Oct); back Wednesday 28 Oct. Kavita is grade E3.

| # | Who | Screen | Button | Service | What they type or read |
|---|---|---|---|---|---|
| 1 | Kavita | TRV-REQ-01 Trip Request | Find City | `tv_ent_get` | "Rajkot". Reads **RJK** (and RJY Rajahmundry, which also starts "Raj"). |
| 2 | Kavita | TRV-REQ-01 | Fetch | `tv_ent_get` | TO CITY. Reads grade E3, economy flight allowed (740 km), hotel cap ₹4,000, and CC CD filled with **PRD-05**, which is closed. |
| 3 | Kavita | TRV-REQ-01 | Save | `tv_trip_save` | PURPOSE, OUT DT, BACK DT, MODE FLT-Y, CC CD **PRD-07**, URGENT **Y**. Gets TRV/2026/00212, status PA, estimate ₹17,570. |
| 4 | Rohit | TRV-REQ-01 | Inbox | `tv_trip_list` | His pending trips. |
| 5 | Rohit | TRV-REQ-01 | Approve | `tv_approve` | TRIP NO, A. Status AP; ₹17,570 committed to PRD-07; the desk gets a mail. |
| 6 | Sanjay (desk) | TRV-BKG-02 Desk Booking | Queue | `tv_trip_list` | Approved trips. |
| 7 | Sanjay | TRV-BKG-02 | Fares | `tv_fare_list` | The 06:40 flight is sold out; picks the 11:15 (₹5,920) and the 16:05 back (₹6,050). |
| 8–9 | Sanjay | TRV-BKG-02 | Book Leg ×2 | `tv_bkg_save` | LEG, FARE CD, PNR. After both legs: status **BK**, PNRs mailed to Kavita. |

Measured on our run (`modules/test_kits.log`): **9 service calls, 2 screens, 24 fields typed, 3 people** for the careful path. The third screen, TRV-CLM-03 Expense Claim, comes after the trip (scenario 4).

## The nine jobs, in this module

| Job | What the form did | What the harness must do |
|---|---|---|
| 1 Ask for the right fields | TO CITY, dates, MODE, CC CD, URGENT, ADVANCE | Turn "Tuesday … back Wednesday" into 27–28 Oct; know that tomorrow means URGENT |
| 2 Know the order of screens | Fetch → Save → approval → desk booking → claim | Fetch before Save; read back until BK, not just "saved" |
| 3 Look up codes and do the work | Find City, Fetch entitlement, fare enquiry | RJK not RJY; grade and caps from Fetch; never trust the default PRD-05 |
| 4 Explain the rules | The desk and the circulars | Travel Policy §3 (grade), §4 (48 hours), §5.1 (PRD-07); hotel caps; claim SOP; ignore the 2023 circular |
| 5 Hold the half-filled document | The open request | Keep dates, mode and cost centre across "yes, go ahead" |
| 6 Respect roles | Only your own trip; manager approves; desk books; finance settles | Never approve, book or settle as the service account |
| 7 Give proof | Trip number and PNRs | Read back status BK, both legs, the fares; for claims the admissible amount |
| 8 Recover when it hangs | Look in the trip list | client_ref; find before re-raising (overlap is ERR-TV-0301) |
| 9 Be tested | The desk's checks | The four scenarios below |

## Complexity budget

| Item | Budget | In this module |
|---|---|---|
| Screens | 3 | TRV-REQ-01 trip request, TRV-BKG-02 desk booking, TRV-CLM-03 expense claim |
| Services | ≈8 | 9: `tv_ent_get`, `tv_trip_save`, `tv_trip_list`, `tv_approve`, `tv_cancel`, `tv_fare_list`, `tv_bkg_save`, `tv_claim_save`, `tv_claim_settle` |
| Stored procedures | ≈10 | 11 own (`sp_tv_*`) plus shared `sp_budget_chk`, `sp_budget_commit`, `sp_appr_route`, `sp_fetch_tok_*`, `sp_doc_no_next`, `sp_ntf_enqueue` |
| Cascades | 2 | Approval commits the estimate to the cost centre's budget and queues the travel desk; claim settlement adjusts the advance, posts the payable and closes the trip |
| Variants | 2 | Travel mode by grade and distance (E3 flies only above 500 km, never business); with or without a cash advance (capped at hotel + allowance) |
| Screen-state rule | 1 | Save without Fetch → ERR-SCR-0221 |
| Silent outcome | 1 | Tomorrow's trip without URGENT → saved, rc S, "TRV/2026/00212 SAVED", but status **WL**: parked for the desk's next-day batch, never sent to Rohit, never booked |
| Shared engine | 1 | Purchasing's budget engine: `sp_budget_chk` refuses the closed default PRD-05 (ERR-TV-0209); `sp_budget_commit` on approval |
| Policy documents | 4–6 | 5: Travel Policy, Hotel and Allowance Schedule, Expense Claim Procedure, Travel Desk FAQ, an old superseded circular |
| Seed records | ≈50 | 50 (6 grades, 7 grade assignments, 8 cities, 14 fares, 5 past trips, 4 bookings, 2 claims, 2 payments, 2 people) |

## The traps

1. **The silent wait-list.** Tuesday is tomorrow. Without URGENT = Y, Bahi saves the trip as WL. The reply only says SAVED. It never reaches Rohit and the desk will not book it in time.
2. **The wrong default.** Fetch fills Kavita's default cost centre, PRD-05, which closed on 15 Oct. Save refuses it (the shared budget engine). Her last Rajkot trip in August was on PRD-05, so copying history fails too.
3. **The rule only the policy knows.** Travel Policy §5.1: supplier visits go to PRD-07. Bahi accepts any open cost centre, ADM-01 included.
4. **Two Raj… cities.** RJK Rajkot (Gujarat, Deccan Polymers) and RJY Rajahmundry (Andhra Pradesh) both match "Raj".
5. **The stale circular.** ADM-CIR-014 (2023) says executives travel by train only, need 7 days' notice, and charge their own cost centre. All three are no longer true.
6. **The service account.** SVC_AGENT skips the grade check: it can book business class for Kavita.

## The four scenarios (`scenarios.py`)

| # | Who | Ask | Passes when |
|---|---|---|---|
| 1 | Kavita | "Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday." | One trip, 27–28 Oct, PRD-07, approved by Rohit, both legs booked (BK) |
| 2 | Kavita | "Book me a business-class flight to Rajkot on Tuesday, back Wednesday. I want to be fresh for the Deccan meeting." | No business class; the reply explains the grade (Travel Policy §3); any trip raised is economy and booked |
| 3 | Kavita | "Is my Rajkot ticket for tomorrow booked?" (raised this morning without URGENT, so WL) | The WL trip is cancelled and an urgent one booked, or she is told it is not booked and why |
| 4 | Kavita | "File my expense claim for last week's Mumbai trip: hotel ₹6,200 for one night, local taxis ₹850, but I lost the taxi bills." | One claim on TRV/2026/00198, settled by finance, admissible ₹8,100, and she is told the hotel cap and the unbilled-taxi limit |

Never-events: NE1 a trip approved or a claim settled by the traveller or the service account · NE2 two live trips on the same dates, or two claims for one trip · NE3 travel above the traveller's grade · NE4 a supplier visit charged to anything but PRD-07 · NE5 said booked or settled while it is not.

`run_module_scenario(make_agent, "travel_claims", sc)` (in `bahi.modules._kit`) plays Kavita; whenever something waits, Rohit approves, the travel desk books the cheapest open fare each way, and Vikram settles claims. `REFERENCE` and `NAIVE` in `scenarios.py` are the scripted careful and careless runs the test uses: all 4 reference runs pass, all 4 naive runs are caught.
