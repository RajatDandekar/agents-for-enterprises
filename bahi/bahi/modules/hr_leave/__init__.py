"""HR · leave. Before: leave balance, leave application, manager approval. After: one sentence.

    erp = ERP(modules=["hr_leave"])
    s = erp.session("KJOSHI"); s.call("lv_bal_get", emp_cd="E-1042")
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "hr_leave",
    "title": "HR · leave",
    "prefix": "lv_",
    "speaker": "KJOSHI",
    "after": "I need Thursday and Friday off for my sister's wedding.",
    "screens": ["HR-LV-01", "HR-LV-02", "HR-LV-04"],
    "shared_engine": "sp_appr_route (approval routing, value 0 = first manager)",
}

GLOSSARY = {
    "emp_cd": "Employee code (E-1042 is Kavita). Not the same as the Bahi user id.",
    "lv_cd": "Leave type: CL casual, EL earned, SL sick, CO compensatory off, LWP leave without pay.",
    "from_dt / to_dt": "First and last date of the leave, inclusive. Sundays and plant holidays are not counted.",
    "half": "1H = first half, 2H = second half. Only when from_dt = to_dt.",
    "ref_dt": "For CO only: the holiday the employee worked, which earned the comp-off.",
    "fwd_to": "FWD TO: sends the application to this approver instead of the default leave approver.",
    "fetch_tok": "Token from Fetch (lv_fetch). Save without it fails with ERR-SCR-0221.",
    "days / lwp_days": "Working days applied for, and how many of them are without pay.",
    "lv_appr": "The employee's default leave approver (user id).",
    "client_ref": "Free text the caller can use as an idempotency key.",
}
STATUS = {"PA": "pending approval", "HD": "held for HR (part of it is unpaid; never reaches the manager until HR clears it)",
          "AP": "approved", "RJ": "rejected or returned", "CN": "cancelled"}
ERRORS = {
    "ERR-LV-0001": "employee not found", "ERR-LV-0002": "emp code mandatory", "ERR-LV-0003": "not your employee code",
    "ERR-LV-0102": "to date before from date", "ERR-LV-0104": "no working days in range", "ERR-LV-0105": "from date in past",
    "ERR-LV-0201": "invalid leave type", "ERR-LV-0215": "not enough notice for this leave type",
    "ERR-LV-0217": "longer than this type allows at a stretch", "ERR-LV-0301": "overlaps another application",
    "ERR-LV-0410": "FWD TO user not found", "ERR-LV-0501": "application not found", "ERR-LV-0502": "not pending",
    "ERR-LV-0504": "not your approval", "ERR-LV-0505": "not held", "ERR-LV-0507": "already closed",
    "ERR-LV-0508": "leave already started", "ERR-LV-0611": "half day only for a single date", "ERR-LV-0612": "half must be 1H/2H",
    "ERR-LV-0620": "comp-off needs the worked date", "ERR-LV-0621": "no open comp-off for that date",
    "ERR-LV-0622": "worked date only for comp-off", "W-LV-118": "part of the leave saved as unpaid; held for HR",
    "ERR-SCR-0221": "Save without Fetch", "ERR-APR-0003": "self approval",
}
