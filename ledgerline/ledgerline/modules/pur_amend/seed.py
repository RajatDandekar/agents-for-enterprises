"""Purchasing · amend PO: tables and seed data. Everything is fictional.

Emma's own order is created the real way, through purchasing's services (validate once):
PR/2026/04417 for 20,000 BAT-500, approved by Daniel, then PO/2026/01182 from Voltway Cells at £11.90,
released. Its delivery schedule is 10,000 on 30 Oct and 10,000 on 2 Nov. A second Voltway battery pack order
(PO/2026/01181, cargo e-bike) makes "Voltway's battery pack order" ambiguous, and Voltway has already delivered 15,000 of
the 25,000 handles on PO/2026/01152.
"""
from .._kit import add_seq, grant, insert, ok

SCHEMA = """
CREATE TABLE pa_lead(sup_cd TEXT PRIMARY KEY, lead_days INT, remarks TEXT);
CREATE TABLE pa_reason(reason_cd TEXT PRIMARY KEY, descr TEXT);
CREATE TABLE pa_sched(po_no TEXT, sl_no INT, dlv_dt TEXT, qty INT, rcvd_qty INT, status TEXT, amd_no TEXT);
CREATE TABLE pa_rcpt(grn_no TEXT PRIMARY KEY, po_no TEXT, sl_no INT, rcpt_dt TEXT, qty INT, recd_by TEXT);
CREATE TABLE pa_amd(amd_no TEXT PRIMARY KEY, po_no TEXT, rev INT, amd_type TEXT, old_qty INT, new_qty INT,
  old_dt TEXT, new_dt TEXT, old_gross REAL, new_gross REAL, reason_cd TEXT, remarks TEXT, need_appr TEXT,
  status TEXT, raised_by TEXT, raised_on TEXT, approver TEXT, approved_by TEXT, decided_on TEXT,
  released_on TEXT, warn_cd TEXT, client_ref TEXT);
"""

# sup_cd, supplier lead time in days (a delivery date may not be set nearer than this), remarks
LEAD_TIMES = [
    ("VC-EIN-0042", 5, "Eindhoven, road transport 2 days"), ("VC-EIN-0009", 5, "blocked code"),
    ("VPC-ROT-0107", 7, None), ("PB-MAN-0017", 2, "local"), ("CC-SAL-0031", 3, "local"),
    ("AM-BIR-0008", 7, "mill schedule"), ("IP-MAN-0055", 2, "local"), ("NC-GDA-0063", 10, "Gdańsk, rail"),
]

REASONS = [
    ("PLAN", "Production plan changed"), ("SUPP", "Supplier request"), ("STCK", "Enough stock in hand"),
    ("QLTY", "Quality problem"), ("PRCE", "Price dispute (rate itself cannot change)"), ("DUPL", "Ordered twice"), ("OTHR", "Other (say why in remarks)"),
]

# po_no, sl_no, delivery date, qty, received qty, status (OP open, RC received, SU superseded, CN cancelled), amd_no
SCHEDULES = [
    ("PO/2026/01182", 1, "2026-10-30", 10000, 0, "OP", None),
    ("PO/2026/01182", 2, "2026-11-02", 10000, 0, "OP", None),
    ("PO/2026/01181", 1, "2026-11-05", 12000, 0, "OP", None),
    ("PO/2026/01152", 1, "2026-10-15", 15000, 15000, "RC", None),
    ("PO/2026/01152", 2, "2026-10-30", 10000, 0, "OP", None),
    ("PO/2026/01044", 1, "2026-08-14", 9000, 9000, "RC", None),
    ("PO/2026/01044", 2, "2026-08-24", 9000, 9000, "RC", None),
    ("PO/2026/01131", 1, "2026-09-22", 15000, 15000, "RC", None),
    ("PO/2026/01131", 2, "2026-10-06", 15000, 15000, "RC", "AMD/2026/00027"),
    ("PO/2026/01131", 3, "2026-09-29", 15000, 0, "SU", None),
    ("PO/2026/01167", 1, "2026-10-14", 20000, 20000, "RC", None),
    ("PO/2026/01167", 2, "2026-10-28", 20000, 0, "OP", None),
    ("PO/2026/01179", 1, "2026-11-03", 4000, 0, "OP", None),
]

# Goods received so far (the receipts behind rcvd_qty).
RECEIPTS = [
    ("GRN/2026/03311", "PO/2026/01044", 1, "2026-08-14", 9000, "ATANAKA"),
    ("GRN/2026/03329", "PO/2026/01044", 2, "2026-08-24", 9000, "ATANAKA"),
    ("GRN/2026/03388", "PO/2026/01131", 1, "2026-09-21", 8000, "ATANAKA"),
    ("GRN/2026/03390", "PO/2026/01131", 1, "2026-09-22", 7000, "ATANAKA"),
    ("GRN/2026/03431", "PO/2026/01131", 2, "2026-10-06", 15000, "ATANAKA"),
    ("GRN/2026/03452", "PO/2026/01152", 1, "2026-10-14", 9000, "ATANAKA"),
    ("GRN/2026/03460", "PO/2026/01152", 1, "2026-10-15", 6000, "ATANAKA"),
    ("GRN/2026/03469", "PO/2026/01167", 1, "2026-10-13", 12000, "ATANAKA"),
    ("GRN/2026/03471", "PO/2026/01167", 1, "2026-10-14", 8000, "ATANAKA"),
]

# Past amendments: amd_no, po_no, rev, type, old/new qty, old/new date, old/new gross, reason, remarks, need_appr,
# status, raised_by, raised_on, approver, approved_by, decided_on, released_on, warn_cd, client_ref
PAST_AMDS = [
    ("AMD/2026/00019", "PO/2026/01044", 1, "REV", 18000, 20000, "2026-08-10", "2026-08-10", 242136, 269040, "PLAN",
     None, "Y", "RJ", "ECLARKE", "2026-08-07T10:30:00", "DOKAFOR", None, "2026-08-07T17:00:00", None, None, None),
    ("AMD/2026/00020", "PO/2026/01131", 1, "SCL", 30000, 15000, "2026-09-29", "2026-09-29", 240720, 120360, "STCK",
     "Whistle stock enough", "Y", "RJ", "ECLARKE", "2026-09-23T15:00:00", "DOKAFOR", None, "2026-09-23T18:10:00",
     None, None, None),
    ("AMD/2026/00025", "PO/2026/01167", 1, "REV", 40000, 45000, "2026-10-21", "2026-10-21", 1014800, 1141650, "PLAN",
     "Extra cartons for the spring launch", "Y", "RJ", "LMORENO", "2026-10-10T11:45:00", "HWEBER", None,
     "2026-10-10T19:00:00", None, None, None),
    ("AMD/2026/00026", "PO/2026/01152", 1, "REV", 25000, 25000, "2026-10-03", "2026-10-15", 545750, 545750, "SUPP",
     "First lot moved", "Y", "RL", "ECLARKE", "2026-10-05T12:00:00", "DOKAFOR", "DOKAFOR", "2026-10-05T16:00:00",
     "2026-10-05T16:10:00", None, None),
    ("AMD/2026/00024", "PO/2026/01044", 1, "REV", 18000, 18000, "2026-08-10", "2026-08-24", 242136, 242136, "SUPP",
     "Voltway asked for two lots", "Y", "RL", "ECLARKE", "2026-08-05T11:00:00", "DOKAFOR", "DOKAFOR",
     "2026-08-05T15:20:00", "2026-08-05T15:40:00", None, None),
    ("AMD/2026/00027", "PO/2026/01131", 1, "REV", 30000, 30000, "2026-09-29", "2026-10-06", 240720, 240720, "PLAN",
     "Second lot after Dussehra", "Y", "RL", "ECLARKE", "2026-09-24T10:10:00", "DOKAFOR", "DOKAFOR",
     "2026-09-24T12:00:00", "2026-09-24T12:05:00", None, None),
    ("AMD/2026/00028", "PO/2026/01167", 1, "REV", 40000, 40000, "2026-10-21", "2026-10-28", 1014800, 1014800, "SUPP",
     None, "N", "HD", "LMORENO", "2026-10-12T16:30:00", None, None, None, None, "W-SCH-209", None),
    ("AMD/2026/00029", "PO/2026/01167", 1, "REV", 40000, 40000, "2026-10-21", "2026-10-28", 1014800, 1014800, "SUPP",
     "Redone with schedule", "Y", "RL", "LMORENO", "2026-10-13T09:05:00", "DOKAFOR", "DOKAFOR",
     "2026-10-13T11:00:00", "2026-10-13T11:10:00", None, None),
    ("AMD/2026/00030", "PO/2026/01152", 1, "REV", 25000, 25000, "2026-10-03", "2026-10-20", 545750, 545750, "SUPP",
     "Voltway short of moulds", "Y", "RJ", "ECLARKE", "2026-10-06T14:00:00", "DOKAFOR", None,
     "2026-10-06T18:30:00", None, None, None),
]

READS = ["pa_po_list", "pa_po_get", "pa_sched_get", "pa_amd_list"]


def seed(erp):
    insert(erp, "pa_lead", LEAD_TIMES)
    insert(erp, "pa_reason", REASONS)
    insert(erp, "pa_sched", SCHEDULES)
    insert(erp, "pa_rcpt", RECEIPTS)
    insert(erp, "pa_amd", PAST_AMDS)
    add_seq(erp, "PA-AMD", "AMD/2026/", 31, 5)
    for role in ("PUR-EXEC", "PUR-SR"):
        grant(erp, role, READS + ["pa_amd_fetch", "pa_amd_save", "pa_sched_save", "pa_amd_release"])
    for role in ("PUR-SR", "PUR-MGR", "PLANT-HEAD"):
        grant(erp, role, READS + ["pa_amd_approve"])
    grant(erp, "STORES", READS)

    # PO/2026/01181: Voltway cargo e-bike battery packs, within Emma's own limit, released on Saturday.
    erp.x("INSERT INTO po_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
          "PO/2026/01181", "NBC-MAN-01", "VC-EIN-0042", None, "STD", "PRD-03", "VAT20-RC", "N45", "2026-11-05",
          "WH-MAN-STR", "RL", 110400.0, 19872.0, 130272.0, "ECLARKE", "2026-10-24", "ECLARKE", "2026-10-24",
          "2026-10-24", None, None)
    erp.x("INSERT INTO po_line VALUES (?,?,?,?,?,?)", "PO/2026/01181", 1, "BAT-375", 12000, "NOS", 9.20)
    erp.sp("sp_budget_commit", "PRD-03", 130272.0)
    erp.sp("sp_stk_onorder_upd", "BAT-375", "WH-MAN-STR", 12000)
    erp.sp("sp_stk_onorder_upd", "MNT-FRM-01", "WH-MAN-STR", 10000)  # the open balance of PO/2026/01152

    # Emma's battery pack order, made through the real services, as she made it this morning.
    k, r = erp.session("ECLARKE"), erp.session("DOKAFOR")
    pr = ok(k.call("pr_save", cc_cd="PRD-07", need_dt="2026-11-02", itm_cd="BAT-500", qty=20000, est_rate=11.90,
                   remarks="spring-launch run"))["pr_no"]
    ok(k.call("pr_submit", pr_no=pr))
    ok(r.call("pr_approve", pr_no=pr, decision="A", comment="ok, for the spring launch"))
    tok = ok(k.call("po_fetch", sup_cd="VC-EIN-0042", itm_cd="BAT-500", pr_no=pr))["fetch_tok"]
    po = ok(k.call("po_save", po_type="STD", pr_no=pr, sup_cd="VC-EIN-0042", itm_cd="BAT-500", qty=20000,
                   rate=11.90, tax_cd="VAT20-RC", cc_cd="PRD-07", need_dt="2026-11-02", fetch_tok=tok,
                   client_ref="PA-SEED-GSK05"))["doc_no"]
    ok(k.call("po_release", po_no=po))
    if po != "PO/2026/01182":  # another kit created purchase orders first; keep the schedule on the right order
        erp.x("UPDATE pa_sched SET po_no=? WHERE po_no='PO/2026/01182'", po)
