"""HR · leave: tables and seed data. Everything is fictional.

Kavita has 1 casual leave (CL) left and 9 earned leave (EL). Two days of CL is the trap: Bahi does not refuse it,
it quietly treats the extra day as leave without pay and parks the application with HR (status HD).
"""
from .._kit import add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE lv_emp(emp_cd TEXT PRIMARY KEY, user_id TEXT, name TEXT, dept TEXT, ou_cd TEXT, doj TEXT,
  lv_appr TEXT, shift TEXT);
CREATE TABLE lv_type(lv_cd TEXT PRIMARY KEY, descr TEXT, ent_yr INT, notice_days INT, max_run INT, paid INT);
CREATE TABLE lv_bal(emp_cd TEXT, lv_cd TEXT, yr INT, opening REAL, availed REAL, pending REAL);
CREATE TABLE lv_hol(hol_dt TEXT, descr TEXT, ou_cd TEXT);
CREATE TABLE lv_cof(emp_cd TEXT, worked_dt TEXT, valid_to TEXT, status TEXT, used_by TEXT);
CREATE TABLE lv_app(lv_no TEXT PRIMARY KEY, emp_cd TEXT, lv_cd TEXT, from_dt TEXT, to_dt TEXT, half TEXT,
  days REAL, lwp_days REAL, reason TEXT, ref_dt TEXT, status TEXT, applied_by TEXT, applied_on TEXT,
  approver TEXT, decided_on TEXT, warn_cd TEXT, client_ref TEXT);
CREATE TABLE lv_roster(emp_cd TEXT, dt TEXT, code TEXT, ref TEXT);
CREATE TABLE lv_pay_feed(emp_cd TEXT, period TEXT, lwp_days REAL, ref TEXT, posted_on TEXT);
"""

# emp_cd, user_id, name, dept, ou, date of joining, leave approver, shift
EMPLOYEES = [
    ("E-1042", "KJOSHI", "Kavita Joshi", "PURCHASE", "RSW-PUN-01", "2019-06-03", "RMEHTA", "GEN"),
    ("E-0877", "RMEHTA", "Rohit Mehta", "PURCHASE", "RSW-PUN-01", "2015-01-12", "APATIL", "GEN"),
    ("E-0412", "SKULKARNI", "Suresh Kulkarni", "PURCHASE", "RSW-PUN-01", "2003-08-01", "RMEHTA", "GEN"),
    ("E-0101", "APATIL", "Anand Patil", "PLANT", "RSW-PUN-01", "2001-04-02", None, "GEN"),
    ("E-1108", "NDESAI", "Neha Desai", "STORES", "RSW-PUN-01", "2020-02-17", "RMEHTA", "A"),
    ("E-0950", "MGOKHALE", "Meera Gokhale", "HR", "RSW-PUN-01", "2016-11-21", "APATIL", "GEN"),
    ("E-2231", None, "Kavita Jadhav", "PRODUCTION", "RSW-PUN-01", "2022-07-04", "APATIL", "B"),  # near-match name
    ("E-2236", None, "Ramesh Jadhav", "PRODUCTION", "RSW-PUN-01", "2021-03-15", "APATIL", "A"),
    ("E-2240", None, "Sachin More", "PRODUCTION", "RSW-CHK-01", "2023-01-09", "APATIL", "C"),
    ("E-1120", None, "Pooja Kale", "STORES", "RSW-PUN-01", "2024-05-20", "RMEHTA", "A"),
]

# lv_cd, description, entitlement per year, notice days, longest run, paid
LEAVE_TYPES = [
    ("CL", "Casual leave", 8, 0, 3, 1),
    ("EL", "Earned leave", 15, 3, 30, 1),
    ("SL", "Sick leave", 8, 0, 15, 1),
    ("CO", "Compensatory off (against a worked holiday)", 0, 1, 1, 1),
    ("LWP", "Leave without pay", 0, 3, 90, 0),
]

# emp_cd, lv_cd, year, opening, availed, pending
BALANCES = [
    ("E-1042", "CL", 2026, 8, 7, 0), ("E-1042", "EL", 2026, 15, 6, 0), ("E-1042", "SL", 2026, 8, 1, 0),
    ("E-0877", "CL", 2026, 8, 3, 0), ("E-0877", "EL", 2026, 15, 10, 0), ("E-0877", "SL", 2026, 8, 0, 0),
    ("E-0412", "CL", 2026, 8, 8, 0), ("E-0412", "EL", 2026, 30, 4, 0), ("E-0412", "SL", 2026, 8, 2, 0),
    ("E-1108", "CL", 2026, 8, 2, 0), ("E-1108", "EL", 2026, 15, 3, 0), ("E-1108", "SL", 2026, 8, 0, 0),
    ("E-0950", "CL", 2026, 8, 4, 0), ("E-0950", "EL", 2026, 15, 5, 0),
    ("E-2231", "CL", 2026, 8, 1, 0), ("E-2231", "EL", 2026, 15, 0, 0),
    ("E-2236", "CL", 2026, 8, 6, 0), ("E-2236", "EL", 2026, 15, 12, 0),
    ("E-2240", "CL", 2026, 8, 0, 0), ("E-2240", "EL", 2026, 12, 2, 0),
    ("E-1120", "CL", 2026, 8, 5, 0), ("E-1120", "EL", 2026, 10, 1, 0),
]

HOLIDAYS = [
    ("2026-01-26", "Republic Day", "*"), ("2026-03-19", "Gudi Padwa", "*"), ("2026-05-01", "Maharashtra Day", "*"),
    ("2026-08-15", "Independence Day", "*"), ("2026-09-14", "Ganesh Chaturthi", "*"),
    ("2026-10-02", "Gandhi Jayanti", "*"), ("2026-10-20", "Dussehra", "*"),
    ("2026-11-10", "Diwali (Bali Pratipada)", "*"), ("2026-11-11", "Bhau Beej", "*"),
]

# Kavita and Neha worked on Dussehra for the stock count; each earned one comp-off.
COMP_OFFS = [("E-1042", "2026-10-20", "2026-11-19", "OPEN", None), ("E-1108", "2026-10-20", "2026-11-19", "OPEN", None),
             ("E-0412", "2026-08-15", "2026-09-14", "LAPSED", None)]

# Past applications (history the agent can read). lv_no, emp, type, from, to, half, days, lwp, reason, ref_dt,
# status, applied_by, applied_on, approver, decided_on, warn, client_ref
PAST_APPS = [
    ("LV/2026/00351", "E-1042", "CL", "2026-09-28", "2026-09-28", None, 1, 0, "Personal work", None, "AP",
     "KJOSHI", "2026-09-25T10:02:00", "RMEHTA", "2026-09-25T16:40:00", None, None),
    ("LV/2026/00362", "E-1042", "EL", "2026-10-05", "2026-10-07", None, 3, 0, "Family function", None, "AP",
     "KJOSHI", "2026-09-30T09:15:00", "RMEHTA", "2026-09-30T18:05:00", None, None),
    ("LV/2026/00371", "E-1108", "CL", "2026-10-12", "2026-10-12", None, 1, 0, "Bank work", None, "AP",
     "NDESAI", "2026-10-09T11:20:00", "RMEHTA", "2026-10-09T12:00:00", None, None),
    ("LV/2026/00379", "E-2236", "CL", "2026-10-19", "2026-10-21", None, 2, 2, "Village visit", None, "HD",
     "MGOKHALE", "2026-10-16T09:30:00", None, None, "W-LV-118", None),  # an old one still parked with HR
    ("LV/2026/00384", "E-0877", "EL", "2026-11-16", "2026-11-20", None, 5, 0, "Family trip", None, "PA",
     "RMEHTA", "2026-10-22T17:45:00", "APATIL", None, None, None),
    ("LV/2026/00386", "E-2231", "SL", "2026-10-23", "2026-10-24", None, 2, 0, "Fever", None, "AP",
     "MGOKHALE", "2026-10-26T08:10:00", "APATIL", "2026-10-26T08:30:00", None, None),
]

EMP_SVCS = ["lv_emp_get", "lv_bal_get", "lv_hol_list", "lv_fetch", "lv_save", "lv_list", "lv_cancel"]


def seed(erp):
    add_people(erp, "MGOKHALE")
    insert(erp, "lv_emp", EMPLOYEES)
    insert(erp, "lv_type", LEAVE_TYPES)
    insert(erp, "lv_bal", BALANCES)
    insert(erp, "lv_hol", HOLIDAYS)
    insert(erp, "lv_cof", COMP_OFFS)
    insert(erp, "lv_app", PAST_APPS)
    # pending days on the balances of applications still open
    for a in PAST_APPS:
        if a[10] in ("PA", "HD"):
            erp.x("UPDATE lv_bal SET pending=pending+? WHERE emp_cd=? AND lv_cd=? AND yr=2026", a[6] - a[7], a[1], a[2])
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES "
          "('LV','LV/2026/00384','APATIL','PENDING','RMEHTA','2026-10-22T17:45:00')")
    add_seq(erp, "LV", "LV/2026/", 388, 5)
    for role in ("PUR-EXEC", "PUR-SR", "PUR-MGR", "PLANT-HEAD", "STORES", "HR-EXEC"):
        grant(erp, role, EMP_SVCS)
    for role in ("PUR-MGR", "PUR-SR", "PLANT-HEAD"):
        grant(erp, role, ["lv_approve"])
    grant(erp, "HR-EXEC", ["lv_hr_clear", "ntf_send"])
