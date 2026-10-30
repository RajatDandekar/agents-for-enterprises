# Travel · claims: data dictionary

Prefix `tv_` for services, `sp_tv_` for stored procedures, `tv_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `tv_ent_get` | TRAVEL ENTITLEMENT | read | TRV-REQ-01 | to_cd:str, q:str, trav_id:str |
| `tv_trip_save` | TRIP REQUEST SAVE | write | TRV-REQ-01 | purpose*:str, from_cd:str, to_cd*:str, out_dt*:date, back_dt*:date, mode*:str, cc_cd*:str, adv_amt:float, urgent:str, trav_id:str, fetch_tok:str, client_ref:str |
| `tv_trip_list` | TRIP LIST | read | TRV-BKG-02 | trip_no:str, trav_id:str, status:str, approver:str, client_ref:str |
| `tv_approve` | TRIP APPROVE | write | TRV-REQ-01 | trip_no*:str, decision*:str, comment:str |
| `tv_cancel` | TRIP CANCEL | write | TRV-REQ-01 | trip_no*:str, reason*:str |
| `tv_fare_list` | FARE ENQUIRY | read | TRV-BKG-02 | trip_no:str, from_cd:str, to_cd:str, dt:date, mode:str |
| `tv_bkg_save` | BOOKING SAVE | write | TRV-BKG-02 | trip_no*:str, leg*:str, fare_cd*:str, pnr*:str |
| `tv_claim_save` | EXPENSE CLAIM SAVE | write | TRV-CLM-03 | trip_no*:str, hotel_amt:float, nights:int, local_amt:float, bills:str, remarks:str, client_ref:str |
| `tv_claim_settle` | CLAIM SETTLE | write | TRV-CLM-03 | claim_no*:str, comment:str |

## Tables

- **tv_grade** (6 seed rows): grade, modes, flt_min_km, hotel_a, hotel_b, hotel_c, da_a, da_b, da_c
- **tv_emp** (7 seed rows): user_id, grade
- **tv_city** (8 seed rows): city_cd, name, state, cls, km
- **tv_fare** (14 seed rows): fare_cd, from_cd, to_cd, mode, carrier, dep_dt, dep_tm, fare, seats
- **tv_trip** (5 seed rows): trip_no, user_id, purpose, from_cd, to_cd, out_dt, back_dt, mode, cc_cd, est_cost, adv_amt, urgent, status, approver, saved_by, saved_on, decided_on, warn_cd, client_ref
- **tv_bkg** (4 seed rows): trip_no, leg, fare_cd, pnr, fare, status, booked_by, booked_on
- **tv_claim** (2 seed rows): claim_no, trip_no, hotel_amt, nights, local_amt, bills, da_amt, admissible, status, saved_by, saved_on, settled_by, settled_on, remarks, client_ref
- **tv_pay** (2 seed rows): claim_no, user_id, admissible, adv_adj, net_amt, posted_on

## Field meanings

| Field | Meaning |
|---|---|
| `trip_no` | Trip request number, TRV/2026/nnnnn. |
| `trav_id` | TRAVELLER: the user who travels. Blank = you. Only the travel desk may raise trips for others. |
| `from_cd / to_cd` | City codes: PUN Manchester, RJK Eindhoven, RJY Rajahmundry (not Eindhoven), AMD Rotterdam, BOM Birmingham, BRC Lyon. |
| `out_dt / back_dt` | Travel out and back dates. Days = back - out + 1; hotel nights = days - 1. |
| `mode` | FLT-Y economy flight, FLT-J business flight, TRN-1A/2A/3A train class, BUS. Must be in your grade. |
| `cc_cd` | Cost centre that carries the trip. Fetch fills your default, which may be closed (PRD-05 is). |
| `adv_amt` | Cash advance. At most hotel cap x nights + daily allowance x days; adjusted at settlement. |
| `urgent` | URGENT Y/N. Departure less than 2 days away without Y = the request waits for the desk's next-day batch (WL). |
| `fetch_tok` | Token from Fetch (tv_ent_get with to_cd). Save without it fails with ERR-SCR-0221. |
| `est_cost` | Ledgerline's estimate: cheapest open fare each way + hotel cap + daily allowance. Committed to the budget on approval. |
| `leg / fare_cd / pnr` | OUT or RET, the fare picked from FARE ENQUIRY, and the ticket reference. |
| `bills` | Y if bills are attached. Local travel without bills is paid up to £300 a day. |
| `admissible` | What finance will pay on the claim, after caps. |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**WL** wait-listed for the desk's next-day batch (not sent for approval, not booked) · **PA** pending approval · **AP** approved, waiting for the travel desk to book · **BK** booked (both legs) · **RJ** rejected · **CN** cancelled · **CL** closed (claim settled) · **SB** claim submitted to finance · **ST** claim settled

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-TV-0003 | not your trip |
| ERR-TV-0004 | no travel grade for this user |
| ERR-TV-0101 | invalid city code |
| ERR-TV-0102 | back date before out date |
| ERR-TV-0105 | out date in the past |
| ERR-TV-0209 | cost centre closed |
| ERR-TV-0301 | overlaps another trip |
| ERR-TV-0305 | flight not allowed for this distance and grade |
| ERR-TV-0310 | travel mode not in your grade |
| ERR-TV-0412 | advance above entitlement |
| ERR-TV-0501 | trip not found |
| ERR-TV-0502 | trip not pending |
| ERR-TV-0504 | not your approval |
| ERR-TV-0507 | trip already closed |
| ERR-TV-0508 | trip already started |
| ERR-TV-0515 | trip not approved, cannot book |
| ERR-TV-0520 | fare is not for this leg |
| ERR-TV-0521 | fare mode differs from the trip |
| ERR-TV-0522 | sold out |
| ERR-TV-0523 | leg already booked |
| ERR-TV-0702 | trip not completed |
| ERR-TV-0703 | claim more than 30 days after return |
| ERR-TV-0705 | claim already exists |
| ERR-TV-0706 | more hotel nights than the trip |
| ERR-TV-0709 | claim not found |
| ERR-TV-0710 | claim not submitted |
| W-TV-148 | less than 48 hours, not urgent: parked for the desk's next-day batch |
| ERR-BUD-0207 | budget exceeded (shared engine) |
| ERR-SCR-0221 | Save without Fetch |
| ERR-APR-0003 | self approval |
