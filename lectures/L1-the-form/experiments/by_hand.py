"""Lecture 1: Kavita's order "by hand", measured.

Drives the Bahi server through its screen definitions exactly as the legacy client does (same services, same
fields, same X-Screen / X-Task headers), and counts what a person must do: screens opened, fields typed, codes
typed, characters, buttons, sign-ins, error codes. The server's live run is saved alongside.

Minutes cannot be measured without a person. We give an ESTIMATE from the keystroke-level model
(Card, Moran and Newell): 0.28 s per keystroke, 1.1 s per point-and-click, 1.35 s of thinking before each
field or button, and an assumed 2 s for the legacy client to answer each button. Waiting for Rohit and the
phone call to IT are not in it. Plates must label these minutes as an estimate.

    modal run tools/modal_run.py --script lectures/L1-the-form/experiments/by_hand.py
-> logs/by_hand.json
"""
import json
import pathlib

from fastapi.testclient import TestClient

from bahi.legacy_ui.driver import Desk, Tally
from bahi.server import create_app

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)

app = create_app()
http = TestClient(app)
erp = app.state.tenants.setdefault("default", __import__("bahi").ERP())
tally = Tally()
story = []  # (what happened, in words) for the slides


def note(s):
    story.append({"after_event": len(tally.events), "text": s})
    print("  ·", s)


# ---------------------------------------------------------------- Monday 9:40, Kavita's desk
kavita = Desk(http, tally, "Kavita")
kavita.sign_in("KJOSHI", "kavita@123")
note("Kavita signs in.")

s = kavita.open("INV-ITM-03").type(q="gasket 5").press("Search")
note(f"Item enquiry: {s.status}. Several gaskets look alike.")
s.pick(0)
item = s.form["itm_cd"]
assert item == "GSK-SIL-05L", s.rows

s = kavita.open("INV-STK-02").type(itm_cd=item)
s.press("Query")
note(f"Stock: {s.form['on_hand']} on hand, {s.form['avg_daily_issue']} a day, {s.form['cover_days']} days of cover.")
stock = dict(s.form)

s = kavita.open("PUR-PR-01").type(itm_cd=item).press("Fetch")
note(f"Request entry, Fetch: cost centre {s.form['cc_cd']} (her default), last price {s.form['est_rate']}.")
s.type(qty="20000", need_dt="02-11-2026", remarks="Diwali run").press("Save")
pr_no = s.form["pr_no"]
note(f"Save: {s.status} Estimated value {s.form['est_value']}.")
s.press("Submit")
note(f"Submit: {s.status}")
pr_frame_status = s.status

# ---------------------------------------------------------------- Rohit, at his own desk
rohit = Desk(http, tally, "Rohit")
rohit.sign_in("RMEHTA", "rohit@123")
s = rohit.open("PUR-PR-04").press("Inbox")
row = next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr_no)
s.pick(row).press("Fetch").type(decision="A", comment="ok").press("Confirm")
note(f"Rohit approves: {s.status}")

# ---------------------------------------------------------------- Kavita again: the order
s = kavita.open("PUR-POH-02").type(itm_cd=item).press("Query")
note(f"Order history: last order {s.rows[0]['po_no']} from {s.rows[0]['sup_name']} at {s.rows[0]['rate']}.")
s.pick(0)
sup = s.form["sup_cd"]

s = kavita.open("PUR-PO-01").type(pr_no=pr_no, sup_cd=sup, itm_cd=item).press("Fetch")
note(f"Order entry, Fetch: rate {s.form['rate']}, tax code {s.form['tax_cd']}, cost centre {s.form['cc_cd']}.")
s.press("Save")
err_status = s.status
note(f"Save: {s.status}")
note("She does not know what the code means and phones IT. IT says: Gujarat supplier, use GST18-INTER.")
s.type(tax_cd="GST18-INTER").press("Save")
po_no = s.form.get("po_no")
note(f"Save again: status bar '{s.status}'. The status field says {s.form.get('status')}.")
saved_status_bar, saved_status = s.status, s.form.get("status")
monday = tally.table()
monday_by_person = {k: dict(v) for k, v in tally.by_person.items()}
monday_events = len(tally.events)
monday_calls = len(erp.calls)

# ---------------------------------------------------------------- Friday: the store asks where the gaskets are
s = kavita.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
note(f"Friday, Order release: {s.status}")
friday_status = s.status

# ---------------------------------------------------------------- what the database says
po = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", pr_no)
live = erp.live_run(0)


def klm(events):
    """Keystroke-level-model estimate in minutes for a list of events (see the module docstring)."""
    secs = 0.0
    for e in events:
        if e["action"] == "open":
            secs += 1.35 + 2 * 1.1 + 2.0          # think, open the menu, click the item, screen loads
        elif e["action"] == "type":
            n = len(e["detail"].split(" = ", 1)[-1])
            secs += 1.35 + 1.1 + 0.28 * n         # think, click into the field, type
        elif e["action"] in ("press", "select"):
            secs += 1.35 + 1.1 + (2.0 if e.get("service") else 0)
    return round(secs / 60, 1)


res = {
    "what": "Kavita's gasket order placed by hand through the legacy screens (Monday), then the Friday release attempt",
    "monday_counts": monday,
    "monday_by_person": monday_by_person,
    "monday_service_calls_in_live_run": monday_calls,
    "monday_minutes_estimate_klm": klm(tally.events[:monday_events]),
    "minutes_note": "ESTIMATE (keystroke-level model), hands-on time only; excludes the phone call to IT and waiting for Rohit",
    "phone_calls_story": 1,
    "screens_visited": [e["screen"] for e in tally.events[:monday_events] if e["action"] == "open"],
    "distinct_screens": sorted({e["screen"] for e in tally.events[:monday_events] if e["action"] == "open"}),
    "documents": {"pr_no": pr_no, "po_no": po_no},
    "stock": {k: stock[k] for k in ("on_hand", "avg_daily_issue", "cover_days")},
    "pr_db": pr,
    "po_db": po,
    "status_bar_after_save": saved_status_bar,
    "status_field_after_save": saved_status,
    "tax_error": err_status,
    "pr_submit_status": pr_frame_status,
    "friday_release": friday_status,
    "final_counts_incl_friday": tally.table(),
    "story": story,
    "events": tally.events,
    "frames": tally.frames,
    "live_run": live,
    "sps_total_monday": sum(len(c["sps"]) for c in live[:monday_calls]),
}
(OUT / "by_hand.json").write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
print(json.dumps({k: res[k] for k in ("monday_counts", "monday_by_person", "monday_minutes_estimate_klm",
                                     "distinct_screens", "documents", "status_bar_after_save",
                                     "status_field_after_save", "tax_error", "friday_release",
                                     "monday_service_calls_in_live_run", "sps_total_monday")}, indent=1, default=str))
print("PO in the database:", {k: po[k] for k in ("po_no", "status", "warn_cd", "cc_cd", "gross_value", "tax_cd")})
print("\nLive run (Monday):")
for c in live[:monday_calls]:
    print(f"{c['seq']:>3} {c['screen'] or '':<11} {c['task'] or '':<9} {c['svc']:<16} {c['rc']} {c['err_cd'] or ''} {c['msg']} {c['sps']}")
