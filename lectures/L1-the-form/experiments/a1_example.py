"""A1 worked example (builder track): a capstone module's main task done by hand through its screens, counted.

Same Desk/Tally driver as Kavita's order, on a server with the module installed. Example: HR · leave
("I need Thursday and Friday off for my sister's wedding"), the screens in the order of modules/hr_leave/legacy.py.

    modal run tools/modal_run.py --script lectures/L1-the-form/experiments/a1_example.py
-> logs/a1_example_hr_leave.json
"""
import json
import pathlib

from fastapi.testclient import TestClient

from bahi import ERP
from bahi.legacy_ui.driver import Desk, Tally
from bahi.server import create_app

MOD = "hr_leave"
app = create_app(lambda: ERP(modules=[MOD]))
http, tally = TestClient(app), Tally()
kavita = Desk(http, tally, "Kavita", modules=[MOD]).sign_in("KJOSHI", "kavita@123")

s = kavita.open("HR-LV-01").press("Find Emp")
emp = s.form.get("emp_cd")
s.press("Show").press("Holidays")
print("HR-LV-01:", s.status, "· emp", emp)
s = kavita.open("HR-LV-02").type(emp_cd=emp, lv_cd="EL").press("Fetch")
s.type(from_dt="29-10-2026", to_dt="30-10-2026", reason="Sister's wedding").press("Save")
lv = s.form.get("lv_no")
print("HR-LV-02:", s.status, "· status", s.form.get("status"))
rohit = Desk(http, tally, "Rohit", modules=[MOD]).sign_in("RMEHTA", "rohit@123")
s = rohit.open("HR-LV-04").type(lv_no=lv, decision="A", comment="ok").press("Decide")
print("HR-LV-04:", s.status)
erp = app.state.tenants["default"]
row = erp.q1("SELECT * FROM lv_app WHERE lv_no=?", lv)
out = {"module": MOD, "counts": tally.table(), "by_person": {k: dict(v) for k, v in tally.by_person.items()},
       "doc": lv, "final_status": row["status"] if row else None, "events": tally.events,
       "live_run": [{k: c[k] for k in ("seq", "screen", "task", "svc", "rc", "err_cd", "msg")} for c in erp.live_run()]}
(pathlib.Path(__file__).parent / "logs" / f"a1_example_{MOD}.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out["counts"]), "· final status", out["final_status"])
assert out["final_status"] == "AP", out["final_status"]
