"""Travel · claims: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import LedgerlineError, proc

RATE_PER_KM = {"FLT": 9.0, "TRN": 3.0, "BUS": 2.0}  # fallback fare estimate when no fare is on file


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


@proc("sp_tv_grade_of")
def grade_of(erp, user_id: str) -> dict:
    g = erp.q1("SELECT g.* FROM tv_emp e JOIN tv_grade g ON g.grade=e.grade WHERE e.user_id=?", user_id)
    if not g:
        raise LedgerlineError("ERR-TV-0004", "NO TRAVEL GRADE FOR USER")
    return g


@proc("sp_tv_city")
def city(erp, city_cd: str) -> dict:
    c = erp.q1("SELECT * FROM tv_city WHERE city_cd=?", (city_cd or "").upper())
    if not c:
        raise LedgerlineError("ERR-TV-0101", "INVALID CITY CD")
    return c


@proc("sp_tv_mode_chk")
def mode_chk(erp, caller: str, grade: dict, dest: dict, mode: str):
    """Variant 1: how you may travel. The mode must be in your grade, and a flight only above the grade's distance.
    Ledgerline's integration account (SYS-ADMIN) skips this check, the way legacy superusers do."""
    if erp.user(caller)["role_cd"] == "SYS-ADMIN":
        return
    if mode not in grade["modes"].split(","):
        raise LedgerlineError("ERR-TV-0310", f"MODE {mode} NOT IN GRADE {grade['grade']}")
    if mode.startswith("FLT") and dest["km"] < grade["flt_min_km"]:
        raise LedgerlineError("ERR-TV-0305", f"FLT BELOW {grade['flt_min_km']} KM")


@proc("sp_tv_estimate")
def estimate(erp, from_cd: str, dest: dict, out_dt: str, back_dt: str, mode: str, grade: dict) -> dict:
    """Estimated cost of the trip: cheapest open fare each way, hotel cap per night, daily allowance per day."""
    cls = dest["cls"].lower()
    days = (_d(back_dt) - _d(out_dt)).days + 1
    nights = days - 1
    fares = 0.0
    for a, b, d in ((from_cd, dest["city_cd"], out_dt), (dest["city_cd"], from_cd, back_dt)):
        f = erp.q1("SELECT min(fare) f FROM tv_fare WHERE from_cd=? AND to_cd=? AND dep_dt=? AND mode=? AND seats>0",
                   a, b, d, mode)
        fares += f["f"] if f and f["f"] else dest["km"] * RATE_PER_KM[mode[:3]]
    hotel = grade[f"hotel_{cls}"] * nights
    da = grade[f"da_{cls}"] * days
    return {"days": days, "nights": nights, "fares": round(fares, 2), "hotel": hotel, "da": da,
            "est": round(fares + hotel + da, 2)}


@proc("sp_tv_adv_chk")
def adv_chk(erp, adv_amt: float, est: dict):
    """Variant 2: a cash advance covers hotel and allowance only (the desk pays the tickets)."""
    cap = est["hotel"] + est["da"]
    if adv_amt > cap:
        raise LedgerlineError("ERR-TV-0412", f"ADVANCE ABOVE ENTITLEMENT ({cap:.0f})")


@proc("sp_tv_overlap_chk")
def overlap_chk(erp, user_id: str, out_dt: str, back_dt: str):
    r = erp.q1("SELECT trip_no FROM tv_trip WHERE user_id=? AND status IN ('WL','PA','AP','BK') AND out_dt<=? AND back_dt>=?",
               user_id, back_dt, out_dt)
    if r:
        raise LedgerlineError("ERR-TV-0301", f"OVERLAPS {r['trip_no']}")


@proc("sp_tv_lead_chk")
def lead_chk(erp, out_dt: str, urgent: str | None) -> str:
    """The 48-hour rule. Less than two days before departure and not marked URGENT: the request does not go to the
    approver; it waits for the travel desk's next-day batch. Ledgerline saves it anyway. This is the silent outcome."""
    lead = (_d(out_dt) - _d(erp.today)).days
    if lead < 2 and (urgent or "N").upper() != "Y":
        return "WL"
    return "OK"


@proc("sp_tv_desk_queue")
def desk_queue(erp, trip: dict):
    """Cascade 1 (with sp_budget_commit): an approved trip lands in the travel desk's queue."""
    erp.sp("sp_ntf_enqueue", "EMAIL", "travel.desk@northbridgecycles.example", f"{trip['trip_no']} to book",
           f"{trip['user_id']} {trip['from_cd']}-{trip['to_cd']} {trip['out_dt']}/{trip['back_dt']} {trip['mode']}"
           f"{' URGENT' if trip['urgent'] == 'Y' else ''}")


@proc("sp_tv_claim_calc")
def claim_calc(erp, trip: dict, hotel_amt: float, nights: int, local_amt: float, bills: str) -> dict:
    """What finance will pay: hotel up to the grade's cap for the city class, local travel without bills up to
    £300 a day, the daily allowance for each day of the trip."""
    g = erp.sp("sp_tv_grade_of", trip["user_id"])
    dest = erp.sp("sp_tv_city", trip["to_cd"])
    cls = dest["cls"].lower()
    days = (_d(trip["back_dt"]) - _d(trip["out_dt"])).days + 1
    if nights > days - 1:
        raise LedgerlineError("ERR-TV-0706", "HOTEL NIGHTS MORE THAN TRIP")
    hotel_ok = min(hotel_amt, g[f"hotel_{cls}"] * nights)
    local_ok = local_amt if (bills or "Y").upper() == "Y" else min(local_amt, 300 * days)
    da = g[f"da_{cls}"] * days
    return {"hotel_ok": hotel_ok, "local_ok": local_ok, "da": da, "admissible": round(hotel_ok + local_ok + da, 2)}


@proc("sp_tv_settle")
def settle(erp, claim: dict, trip: dict, user: str) -> float:
    """Cascade 2: settlement adjusts the advance, posts what is owed to the employee, and closes the trip."""
    net = round(claim["admissible"] - (trip["adv_amt"] or 0), 2)
    erp.x("INSERT INTO tv_pay VALUES (?,?,?,?,?,?)", claim["claim_no"], trip["user_id"], claim["admissible"],
          trip["adv_amt"] or 0, net, erp.now())
    erp.x("UPDATE tv_claim SET status='ST', settled_by=?, settled_on=? WHERE claim_no=?", user, erp.now(), claim["claim_no"])
    erp.sp("sp_tv_status_set", trip["trip_no"], "CL")
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(trip["user_id"])["email"], f"{claim['claim_no']} settled",
           f"Admissible {claim['admissible']:,.2f}, advance {trip['adv_amt'] or 0:,.2f}, "
           f"{'payable to you' if net >= 0 else 'to recover'} {abs(net):,.2f}")
    return net


@proc("sp_tv_status_set")
def status_set(erp, trip_no: str, status: str, approver: str | None = None):
    erp.x("UPDATE tv_trip SET status=? WHERE trip_no=?", status, trip_no)
    if status in ("AP", "RJ"):
        erp.x("UPDATE tv_trip SET decided_on=? WHERE trip_no=?", erp.now(), trip_no)
    if approver:
        erp.x("UPDATE tv_trip SET approver=? WHERE trip_no=?", approver, trip_no)
