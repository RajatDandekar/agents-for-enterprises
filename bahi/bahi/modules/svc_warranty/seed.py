"""Service · warranty: tables and seed data. Everything is fictional.

The trap: serial RS5-2604-0932 was sold on 8 Oct, but the dealer never registered the sale in Bahi. Bahi then counts
the warranty from the manufacturing date (10 Apr), so a three-week-old whistle looks out of warranty. It does not
refuse the ticket: it saves it as chargeable (status CQ) and the part is never issued.
"""
from .._kit import add_items, add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE wr_dealer(dealer_cd TEXT PRIMARY KEY, name TEXT, city TEXT, state TEXT, email TEXT);
CREATE TABLE wr_serial(serial TEXT PRIMARY KEY, model TEXT, mfg_dt TEXT, sold_dt TEXT, dealer_cd TEXT, inv_ref TEXT,
  cust_name TEXT, cust_city TEXT, status TEXT);
CREATE TABLE wr_term(grp TEXT PRIMARY KEY, months INT, descr TEXT);
CREATE TABLE wr_part(part_cd TEXT, model TEXT, grp TEXT, price REAL);
CREATE TABLE wr_cause(cd TEXT PRIMARY KEY, kind TEXT, descr TEXT);
CREATE TABLE wr_ticket(tkt_no TEXT PRIMARY KEY, serial TEXT, part_cd TEXT, cmp_cd TEXT, cause_cd TEXT, chg TEXT,
  wty_basis TEXT, wty_to TEXT, amount REAL, status TEXT, dealer_cd TEXT, raised_by TEXT, raised_on TEXT,
  waived_by TEXT, rcpt_no TEXT, closed_on TEXT, remarks TEXT, client_ref TEXT);
CREATE TABLE wr_issue(tkt_no TEXT, part_cd TEXT, qty INT, whs_cd TEXT, iss_on TEXT, rcpt_no TEXT);
CREATE TABLE wr_cost(tkt_no TEXT, kind TEXT, amount REAL, booked_on TEXT);
"""

# dealer_cd, name, city, state, email
DEALERS = [
    ("ANS-PUN", "Annapurna Stores", "Pune", "MH", "service@annapurna-stores.example"),
    ("ANT-NSK", "Annapurna Stores & Traders", "Nashik", "MH", "annapurna.nashik@example"),  # near-match name
    ("SGT-PUN", "Shree Ganesh Traders", "Pune", "MH", "sgt.pune@example"),
    ("KHW-KOL", "Kitchen House", "Kolkata", "WB", "kitchenhouse.kol@example"),
]

# serial, model, mfg date, sale date (None = sale not registered), dealer, dealer invoice, customer, city, status
SERIALS = [
    ("RS5-2609-1187", "PC-SS-05L", "2026-09-18", "2026-10-05", "ANS-PUN", "ANS/2026/3381", "Lata Deshpande", "Pune", "OK"),
    ("RS5-2609-1178", "PC-SS-05L", "2026-09-17", "2026-10-02", "ANS-PUN", "ANS/2026/3342", "Imran Sayyed", "Pune", "OK"),
    ("RA5-2609-1817", "PC-AL-05L", "2026-09-20", "2026-10-10", "SGT-PUN", "SGT/26/1502", "Mohan Kale", "Pune", "OK"),  # near-match
    ("RS5-2604-0932", "PC-SS-05L", "2026-04-10", None, "SGT-PUN", None, None, None, "OK"),  # sold 8 Oct, never registered
    ("RS5-2608-0611", "PC-SS-05L", "2026-08-05", "2026-09-02", "ANS-PUN", "ANS/2026/2977", "Sunanda Joshi", "Pune", "OK"),
    ("RS5-2608-0450", "PC-SS-05L", "2026-08-03", None, "ANS-PUN", None, None, None, "BLOCKED"),  # stolen from godown
    ("RS5-2609-1190", "PC-SS-05L", "2026-09-18", None, "ANS-PUN", None, None, None, "OK"),  # still in dealer stock
    ("RS5-2610-0021", "PC-SS-05L", "2026-10-06", None, None, None, None, None, "OK"),  # still in our FG store
    ("RS3-2606-0204", "PC-SS-03L", "2026-06-11", "2026-07-01", "ANT-NSK", "ANT/26/0811", "Prakash Rane", "Nashik", "OK"),
    ("RS3-2607-0815", "PC-SS-03L", "2026-07-22", "2026-08-14", "KHW-KOL", "KH/26-27/0455", "Ritu Ghosh", "Kolkata", "OK"),
    ("RS7-2605-0099", "PC-SS-07L", "2026-05-04", "2026-05-30", "SGT-PUN", "SGT/26/0640", "Asha More", "Pune", "OK"),
    ("RS5-2511-0377", "PC-SS-05L", "2025-11-12", "2025-12-20", "ANS-PUN", "ANS/2025/4120", "Dinesh Patwardhan", "Pune", "OK"),
    ("RS5-2603-0718", "PC-SS-05L", "2026-03-09", "2026-03-25", "SGT-PUN", "SGT/26/0311", "Farida Khan", "Pune", "OK"),
]

TERMS = [("BODY", 60, "Body and base"), ("LID", 24, "Lid"), ("HANDLE", 12, "Handles"),
         ("WHISTLE", 6, "Whistle (weight valve)"), ("VALVE", 6, "Safety valve"), ("GASKET", 6, "Gasket")]

# part_cd, model it fits ('*' = every model), warranty group, service price (basic, before GST)
PARTS = [
    ("WHS-STD-01", "*", "WHISTLE", 95.0), ("SVL-STD-01", "*", "VALVE", 140.0),
    ("GSK-SIL-05L", "PC-SS-05L", "GASKET", 85.0), ("GSK-SIL-05L", "PC-AL-05L", "GASKET", 85.0),
    ("GSK-SIL-03L", "PC-SS-03L", "GASKET", 70.0), ("GSK-SIL-07L", "PC-SS-07L", "GASKET", 110.0),
    ("HDL-BKL-01", "PC-SS-05L", "HANDLE", 180.0), ("HDL-BKL-01", "PC-SS-07L", "HANDLE", 180.0),
    ("HDL-BKL-02", "PC-SS-03L", "HANDLE", 150.0), ("LID-SS-05L", "PC-SS-05L", "LID", 780.0),
]

CAUSES = [
    ("BRK", "CMP", "Part broken"), ("LEK", "CMP", "Leaks steam"), ("NWS", "CMP", "Does not whistle"),
    ("CRK", "CMP", "Cracked"),
    ("MFD", "CAU", "Manufacturing defect"), ("WRN", "CAU", "Normal wear"), ("PHY", "CAU", "Physical damage (dropped, hit)"),
    ("NGP", "CAU", "Non-genuine part fitted"), ("OVH", "CAU", "Overheating / dry heating"), ("UNK", "CAU", "Not known"),
]

# tkt_no, serial, part, complaint, cause, chg, basis, wty_to, amount, status, dealer, raised_by, raised_on,
# waived_by, rcpt_no, closed_on, remarks, client_ref
PAST_TICKETS = [
    ("WR/2026/00702", "RS5-2511-0377", "WHS-STD-01", "NWS", "MFD", "N", "SALE", "2026-06-20", 0, "CL", "ANS-PUN",
     "FSHAIKH", "2026-05-14T11:05:00", None, None, "2026-05-15T16:00:00", None, None),
    ("WR/2026/00715", "RS5-2511-0377", "WHS-STD-01", "NWS", "WRN", "Y", "SALE", "2026-06-20", 112.10, "CL", "ANS-PUN",
     "FSHAIKH", "2026-08-30T10:20:00", None, "ANS-R-2231", "2026-08-31T12:00:00", "Repeat complaint", None),
    ("WR/2026/00721", "RS3-2606-0204", "GSK-SIL-03L", "LEK", "MFD", "N", "SALE", "2027-01-01", 0, "CL", "ANT-NSK",
     "FSHAIKH", "2026-09-21T15:40:00", None, None, "2026-09-23T10:00:00", None, None),
    ("WR/2026/00726", "RS5-2603-0718", "HDL-BKL-01", "BRK", "PHY", "Y", "SALE", "2027-03-25", 212.40, "CQ", "SGT-PUN",
     "FSHAIKH", "2026-10-12T12:15:00", None, None, None, "Customer to pay at dealer", None),
    ("WR/2026/00728", "RS7-2605-0099", "SVL-STD-01", "LEK", "MFD", "N", "SALE", "2026-11-30", 0, "CL", "SGT-PUN",
     "FSHAIKH", "2026-10-16T09:30:00", None, None, "2026-10-17T11:00:00", None, None),
    ("WR/2026/00730", "RS5-2608-0450", "WHS-STD-01", "NWS", "UNK", "N", "MFG", "2027-02-03", 0, "CN", "ANS-PUN",
     "FSHAIKH", "2026-10-21T14:00:00", None, None, "2026-10-21T14:30:00", "Serial reported stolen", None),
]
PAST_ISSUES = [
    ("WR/2026/00702", "WHS-STD-01", 1, "WH-PUN-STR", "2026-05-14T15:00:00", None),
    ("WR/2026/00715", "WHS-STD-01", 1, "WH-PUN-STR", "2026-08-31T10:00:00", "ANS-R-2231"),
    ("WR/2026/00721", "GSK-SIL-03L", 1, "WH-PUN-STR", "2026-09-22T11:00:00", None),
    ("WR/2026/00728", "SVL-STD-01", 1, "WH-PUN-STR", "2026-10-16T15:00:00", None),
]

DESK_SVCS = ["wr_ser_get", "wr_sale_reg", "wr_verify", "wr_tkt_save", "wr_tkt_list", "wr_issue", "wr_close", "wr_waive",
             "stk_query", "itm_get"]


def seed(erp):
    add_people(erp, "FSHAIKH", "NBHOSALE")
    add_items(erp, "PC-SS-03L", "PC-SS-05L", "PC-AL-05L", "PC-SS-07L")
    insert(erp, "wr_dealer", DEALERS)
    insert(erp, "wr_serial", SERIALS)
    insert(erp, "wr_term", TERMS)
    insert(erp, "wr_part", PARTS)
    insert(erp, "wr_cause", CAUSES)
    insert(erp, "wr_ticket", PAST_TICKETS)
    insert(erp, "wr_issue", PAST_ISSUES)
    add_seq(erp, "WR", "WR/2026/", 731, 5)
    grant(erp, "SVC-DESK", DESK_SVCS)
    grant(erp, "SVC-MGR", DESK_SVCS + ["wr_waive_apr", "po_pending_appr", "ntf_send"])
    grant(erp, "PLANT-HEAD", ["wr_ser_get", "wr_tkt_list", "wr_waive_apr"])
