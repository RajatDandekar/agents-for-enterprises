"""Working days: count the leave days Bahi will charge. Input and output are in tool.json."""
import datetime as dt

from bahi.agent.tools import ToolError, _bahi


def run(s, from_date, to_date):
    a, b = dt.date.fromisoformat(from_date), dt.date.fromisoformat(to_date)
    if b < a:
        raise ToolError("to_date is before from_date.", "Ask the user for the dates again.")
    hol = {h["hol_dt"]: h["descr"] for h in _bahi(s, "lv_hol_list")["rows"]}
    dates, skipped = [], []
    d = a
    while d <= b:
        iso = d.isoformat()
        if d.weekday() == 6 or iso in hol:
            skipped.append({"date": iso, "why": hol.get(iso, "Sunday")})
        else:
            dates.append(iso)
        d += dt.timedelta(days=1)
    return {"ok": True, "days": len(dates), "dates": dates, "holidays": skipped}
