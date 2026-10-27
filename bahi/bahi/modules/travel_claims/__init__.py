"""Travel · claims. Before: trip request, booking, expense claim. After: one sentence.

    erp = ERP(modules=["travel_claims"])
    s = erp.session("KJOSHI"); s.call("tv_ent_get", to_cd="RJK")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "travel_claims",
    "title": "Travel · claims",
    "prefix": "tv_",
    "speaker": "KJOSHI",
    "after": "Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday.",
    "screens": ["TRV-REQ-01", "TRV-BKG-02", "TRV-CLM-03"],
    "shared_engine": "sp_budget_chk / sp_budget_commit (purchasing's budget engine on the trip's cost centre)",
}

GLOSSARY = {
    "trip_no": "Trip request number, TRV/2026/nnnnn.",
    "trav_id": "TRAVELLER: the user who travels. Blank = you. Only the travel desk may raise trips for others.",
    "from_cd / to_cd": "City codes: PUN Pune, RJK Rajkot, RJY Rajahmundry (not Rajkot), AMD Ahmedabad, BOM Mumbai, BRC Vadodara.",
    "out_dt / back_dt": "Travel out and back dates. Days = back - out + 1; hotel nights = days - 1.",
    "mode": "FLT-Y economy flight, FLT-J business flight, TRN-1A/2A/3A train class, BUS. Must be in your grade.",
    "cc_cd": "Cost centre that carries the trip. Fetch fills your default, which may be closed (PRD-05 is).",
    "adv_amt": "Cash advance. At most hotel cap x nights + daily allowance x days; adjusted at settlement.",
    "urgent": "URGENT Y/N. Departure less than 2 days away without Y = the request waits for the desk's next-day batch (WL).",
    "fetch_tok": "Token from Fetch (tv_ent_get with to_cd). Save without it fails with ERR-SCR-0221.",
    "est_cost": "Bahi's estimate: cheapest open fare each way + hotel cap + daily allowance. Committed to the budget on approval.",
    "leg / fare_cd / pnr": "OUT or RET, the fare picked from FARE ENQUIRY, and the ticket reference.",
    "bills": "Y if bills are attached. Local travel without bills is paid up to ₹300 a day.",
    "admissible": "What finance will pay on the claim, after caps.",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"WL": "wait-listed for the desk's next-day batch (not sent for approval, not booked)",
          "PA": "pending approval", "AP": "approved, waiting for the travel desk to book", "BK": "booked (both legs)",
          "RJ": "rejected", "CN": "cancelled", "CL": "closed (claim settled)",
          "SB": "claim submitted to finance", "ST": "claim settled"}
ERRORS = {
    "ERR-TV-0003": "not your trip", "ERR-TV-0004": "no travel grade for this user", "ERR-TV-0101": "invalid city code",
    "ERR-TV-0102": "back date before out date", "ERR-TV-0105": "out date in the past",
    "ERR-TV-0209": "cost centre closed", "ERR-TV-0301": "overlaps another trip",
    "ERR-TV-0305": "flight not allowed for this distance and grade", "ERR-TV-0310": "travel mode not in your grade",
    "ERR-TV-0412": "advance above entitlement", "ERR-TV-0501": "trip not found", "ERR-TV-0502": "trip not pending",
    "ERR-TV-0504": "not your approval", "ERR-TV-0507": "trip already closed", "ERR-TV-0508": "trip already started",
    "ERR-TV-0515": "trip not approved, cannot book", "ERR-TV-0520": "fare is not for this leg",
    "ERR-TV-0521": "fare mode differs from the trip", "ERR-TV-0522": "sold out", "ERR-TV-0523": "leg already booked",
    "ERR-TV-0702": "trip not completed", "ERR-TV-0703": "claim more than 30 days after return",
    "ERR-TV-0705": "claim already exists", "ERR-TV-0706": "more hotel nights than the trip",
    "ERR-TV-0709": "claim not found", "ERR-TV-0710": "claim not submitted",
    "W-TV-148": "less than 48 hours, not urgent: parked for the desk's next-day batch",
    "ERR-BUD-0207": "budget exceeded (shared engine)", "ERR-SCR-0221": "Save without Fetch", "ERR-APR-0003": "self approval",
}
