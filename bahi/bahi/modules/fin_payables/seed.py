"""Finance · payables: tables and seed data. Everything is fictional.

Deccan Polymers' invoice 4471 (AP/2026/03390) bills the 18,000 gaskets of PO/2026/01120 at the new contract
rate ₹11.90, but the order says ₹11.40. That is 4.39% over, above the 2% tolerance, so it sits on hold H-PRC.
It is not due until 16 Nov (N45 from the invoice date), so paying it on Friday 30 Oct is an early payment.
"""
from .._kit import add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE ap_hold(hold_cd TEXT PRIMARY KEY, descr TEXT, release_role TEXT);
CREATE TABLE ap_vbank(sup_cd TEXT PRIMARY KEY, msme TEXT, udyam_no TEXT, bank_ref TEXT);
CREATE TABLE ap_grn(grn_no TEXT PRIMARY KEY, po_no TEXT, itm_cd TEXT, qty_rcvd INT, qty_acc INT, grn_dt TEXT, whs_cd TEXT);
CREATE TABLE ap_inv(ap_no TEXT PRIMARY KEY, inv_type TEXT, sup_cd TEXT, sup_inv_no TEXT, inv_dt TEXT, po_no TEXT,
  qty INT, rate REAL, basic REAL, tax_cd TEXT, tax REAL, gross REAL, cc_cd TEXT, status TEXT, hold_cd TEXT,
  due_dt TEXT, entered_by TEXT, entered_on TEXT, approved_by TEXT, warn_cd TEXT, client_ref TEXT);
CREATE TABLE ap_hold_log(id INTEGER PRIMARY KEY AUTOINCREMENT, ap_no TEXT, hold_cd TEXT, detail TEXT, put_on TEXT,
  released_by TEXT, released_on TEXT, reason TEXT);
CREATE TABLE ap_pay(pay_no TEXT PRIMARY KEY, ap_no TEXT, pay_dt TEXT, amount REAL, status TEXT, early_rsn TEXT,
  sched_by TEXT, sched_on TEXT, approved_by TEXT, paid_on TEXT, warn_cd TEXT, client_ref TEXT);
CREATE TABLE ap_run(run_dt TEXT PRIMARY KEY, cutoff_dt TEXT, status TEXT);
CREATE TABLE ap_ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, sup_cd TEXT, dt TEXT, ref TEXT, dr REAL, cr REAL, narr TEXT);
CREATE TABLE ap_gst(id INTEGER PRIMARY KEY AUTOINCREMENT, ap_no TEXT, gstin TEXT, tax_cd TEXT, itc_amt REAL,
  period TEXT, status TEXT);
"""

# hold code, meaning, roles that may release it (comma list). The service account is not on any list.
HOLDS = [
    ("H-PRC", "Invoice rate more than 2% above the order rate", "PUR-MGR,FIN-CTRL"),
    ("H-QTY", "Invoice quantity more than the accepted, not yet invoiced quantity", "STORES,FIN-CTRL"),
    ("H-GRN", "No goods receipt for the order when the invoice was entered", "AP-EXEC,FIN-CTRL"),
    ("H-DUP", "Looks like an invoice already entered (same number pattern or same amount)", "FIN-CTRL"),
]

# sup_cd, MSME (Y/N), Udyam registration, bank reference (masked)
VENDORS = [
    ("DP-RJK-0042", "Y", "UDYAM-GJ-20-0041771", "HDFC ****4417"),
    ("DPI-AMD-0107", "N", None, "SBI ****9031"),
    ("SV-PUN-0017", "Y", "UDYAM-MH-26-0112290", "BOM ****2290"),
    ("OSM-PUN-0031", "Y", "UDYAM-MH-26-0077130", "ICICI ****7713"),
    ("SP-PUN-0055", "N", None, "AXIS ****6634"),
    ("MS-MUM-0008", "N", None, "HDFC ****5520"),
    ("KR-KOL-0063", "N", None, "UCO ****1180"),
]

# grn_no, po_no, item, received, accepted, date, warehouse
GRNS = [
    ("GRN/2026/07711", "PO/2026/01044", "GSK-SIL-05L", 18000, 18000, "2026-08-18", "WH-PUN-STR"),
    ("GRN/2026/07790", "PO/2026/01131", "WHS-STD-01", 30000, 30000, "2026-09-25", "WH-PUN-STR"),
    ("GRN/2026/07804", "PO/2026/01120", "GSK-SIL-05L", 18000, 18000, "2026-10-02", "WH-PUN-STR"),
    ("GRN/2026/07851", "PO/2026/01152", "HDL-BKL-01", 25000, 24600, "2026-10-14", "WH-PUN-STR"),
    ("GRN/2026/07866", "PO/2026/01167", "BOX-CRG-05L", 40000, 40000, "2026-10-16", "WH-PUN-STR"),
]

# ap_no, type, supplier, supplier's invoice no, invoice date, PO, qty, rate, basic, tax code, tax, gross, cost centre,
# status, hold, due date, entered by, entered on, approved by, warning, client ref
INVOICES = [
    ("AP/2026/03301", "PO", "DP-RJK-0042", "3815", "2026-08-19", "PO/2026/01044", 18000, 11.40, 205200.0, "GST18-INTER",
     36936.0, 242136.0, "PRD-05", "PD", None, "2026-10-03", "PSHAH", "2026-08-21T10:12:00", None, None, None),
    ("AP/2026/03374", "PO", "SV-PUN-0017", "SV/0912", "2026-09-05", "PO/2026/01131", 30000, 6.80, 204000.0, "GST18-INTRA",
     36720.0, 240720.0, "PRD-05", "HD", "H-GRN", "2026-10-05", "PSHAH", "2026-09-07T11:40:00", None, None, None),
    ("AP/2026/03390", "PO", "DP-RJK-0042", "4471", "2026-10-02", "PO/2026/01120", 18000, 11.90, 214200.0, "GST18-INTER",
     38556.0, 252756.0, "PRD-05", "HD", "H-PRC", "2026-11-16", "PSHAH", "2026-10-05T15:05:00", None, None, None),
    ("AP/2026/03409", "NPO", "DPI-AMD-0107", "4471", "2026-10-09", None, None, None, 12400.0, "GST18-INTER",
     2232.0, 14632.0, "MNT-01", "PO", None, "2026-11-08", "PSHAH", "2026-10-12T09:30:00", "APATIL", None, None),
    ("AP/2026/03415", "PO", "DP-RJK-0042", "3920", "2026-10-15", "PO/2026/01152", 24600, 18.50, 455100.0, "GST18-INTER",
     81918.0, 537018.0, "PRD-05", "PO", None, "2026-11-29", "PSHAH", "2026-10-19T12:20:00", None, None, None),
    ("AP/2026/03420", "PO", "SP-PUN-0055", "SP/2210", "2026-10-17", "PO/2026/01167", 30000, 21.50, 645000.0, "GST18-INTRA",
     116100.0, 761100.0, "PRD-07", "PO", None, "2026-11-16", "PSHAH", "2026-10-20T16:45:00", None, None, None),
    ("AP/2026/03424", "NPO", "KR-KOL-0063", "KR/889", "2026-10-20", None, None, None, 6500.0, "GST18-INTER",
     1170.0, 7670.0, "PRD-07", "PA", None, "2026-12-04", "PSHAH", "2026-10-23T10:05:00", None, None, None),
]

HOLD_LOG = [
    (None, "AP/2026/03301", "H-GRN", "NO GRN FOR PO/2026/01044", "2026-08-21T10:12:00", "PSHAH", "2026-08-21T16:00:00",
     "GRN/2026/07711 posted"),
    (None, "AP/2026/03374", "H-GRN", "NO GRN FOR PO/2026/01131", "2026-09-07T11:40:00", None, None, None),
    (None, "AP/2026/03390", "H-PRC", "RATE 11.90 VS PO 11.40 (+4.39%)", "2026-10-05T15:05:00", None, None, None),
]

LEDGER = [
    (None, "DP-RJK-0042", "2026-08-21", "AP/2026/03301", 0, 242136.0, "Invoice 3815"),
    (None, "DP-RJK-0042", "2026-10-02", "PAY/2026/00894", 242136.0, 0, "Payment run 2 Oct"),
    (None, "DPI-AMD-0107", "2026-10-12", "AP/2026/03409", 0, 14632.0, "Invoice 4471"),
    (None, "DP-RJK-0042", "2026-10-19", "AP/2026/03415", 0, 537018.0, "Invoice 3920"),
    (None, "SP-PUN-0055", "2026-10-20", "AP/2026/03420", 0, 761100.0, "Invoice SP/2210"),
]
GST = [
    (None, "AP/2026/03301", "24AADCD4417K1Z3", "GST18-INTER", 36936.0, "2026-08", "CLAIMED"),
    (None, "AP/2026/03409", "24AAKFD9031R1Z8", "GST18-INTER", 2232.0, "2026-10", "OPEN"),
    (None, "AP/2026/03415", "24AADCD4417K1Z3", "GST18-INTER", 81918.0, "2026-10", "OPEN"),
    (None, "AP/2026/03420", "27AAPFS6634Q1Z1", "GST18-INTRA", 116100.0, "2026-10", "OPEN"),
]
PAYS = [("PAY/2026/00894", "AP/2026/03301", "2026-10-02", 242136.0, "PD", None, "PSHAH", "2026-09-28T11:00:00", None,
         "2026-10-02T14:00:00", None, None)]
RUNS = [("2026-10-23", "2026-10-22", "DONE"), ("2026-10-30", "2026-10-29", "OPEN"), ("2026-11-06", "2026-11-05", "OPEN"),
        ("2026-11-13", "2026-11-12", "OPEN"), ("2026-11-20", "2026-11-19", "OPEN"), ("2026-11-27", "2026-11-26", "OPEN")]

AP_READ = ["ap_inv_list", "ap_inv_get"]
PUR_READ = ["po_get", "po_search", "sup_get", "sup_search", "sup_rate_get", "tax_list", "cc_list", "cc_get",
            "tax_compute", "bud_check", "usr_get", "po_pending_appr", "ntf_send", "pt_list"]


def seed(erp):
    add_people(erp, "PSHAH", "VNAIR")
    insert(erp, "ap_hold", HOLDS)
    insert(erp, "ap_vbank", VENDORS)
    insert(erp, "ap_grn", GRNS)
    insert(erp, "ap_inv", INVOICES)
    insert(erp, "ap_hold_log", HOLD_LOG)
    insert(erp, "ap_ledger", LEDGER)
    insert(erp, "ap_gst", GST)
    insert(erp, "ap_pay", PAYS)
    insert(erp, "ap_run", RUNS)
    # Kaveri's non-PO invoice has waited on Rohit (owner of PRD-07) since Friday.
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES "
          "('APINV','AP/2026/03424','RMEHTA','PENDING','PSHAH','2026-10-23T10:05:00')")
    add_seq(erp, "APINV", "AP/2026/", 3431, 5)
    add_seq(erp, "APPAY", "PAY/2026/", 912, 5)
    grant(erp, "AP-EXEC", AP_READ + PUR_READ + ["ap_match", "ap_save", "ap_hold_refer", "ap_hold_release",
                                                "ap_pay_sched", "ap_pay_run"])
    grant(erp, "FIN-CTRL", AP_READ + PUR_READ + ["ap_match", "ap_save", "ap_hold_refer", "ap_hold_release",
                                                 "ap_pay_sched", "ap_pay_run", "ap_approve"])
    for role in ("PUR-EXEC", "PUR-SR", "PUR-MGR", "PLANT-HEAD", "STORES"):
        grant(erp, role, AP_READ + ["ap_hold_refer"])
    for role in ("PUR-MGR", "STORES"):
        grant(erp, role, ["ap_hold_release"])
    for role in ("PUR-MGR", "PLANT-HEAD"):  # cost-centre owners approve non-PO invoices
        grant(erp, role, ["ap_approve"])
