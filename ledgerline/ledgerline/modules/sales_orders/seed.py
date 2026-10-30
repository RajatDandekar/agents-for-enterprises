"""Sales · orders: tables and seed data. Everything is fictional.

Annapurna Stores, Manchester (C-PUN-0118) is a registered dealer with a credit limit of £1,000,000 and £420,000
outstanding. A quotation for 500 five-litre e-bikes at the dealer price (£1,450 since 1 Oct) is £812,000 gross,
so quoting is fine, but turning it into an order quietly puts the order on credit hold (status CH).
"""
from .._kit import add_items, add_locations, add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE so_cust(cust_cd TEXT PRIMARY KEY, name TEXT, city TEXT, state TEXT, vat_no TEXT, cust_type TEXT,
  list_cd TEXT, cr_limit REAL, outstanding REAL, status TEXT, sales_rep TEXT);
CREATE TABLE so_price(list_cd TEXT, itm_cd TEXT, rate REAL, valid_from TEXT, valid_to TEXT);
CREATE TABLE so_disc_lim(role_cd TEXT PRIMARY KEY, max_disc REAL);
CREATE TABLE so_qtn(qtn_no TEXT PRIMARY KEY, cust_cd TEXT, itm_cd TEXT, qty INT, list_cd TEXT, rate REAL,
  disc_pct REAL, tax_cd TEXT, basic_value REAL, tax_value REAL, gross_value REAL, valid_to TEXT, status TEXT,
  created_by TEXT, created_on TEXT, approved_by TEXT, approved_on TEXT, client_ref TEXT, remarks TEXT);
CREATE TABLE so_ord(ord_no TEXT PRIMARY KEY, ord_type TEXT, qtn_no TEXT, cust_cd TEXT, itm_cd TEXT, qty INT,
  rate REAL, disc_pct REAL, tax_cd TEXT, gross_value REAL, whs_cd TEXT, status TEXT, created_by TEXT,
  created_on TEXT, released_on TEXT, warn_cd TEXT, client_ref TEXT);
CREATE TABLE so_dsp(dsp_id INTEGER PRIMARY KEY AUTOINCREMENT, ord_no TEXT, whs_cd TEXT, itm_cd TEXT, qty INT,
  status TEXT, created_on TEXT);
"""

# cust_cd, name, city, state, VAT number, type (DLR dealer, DST distributor, RTL retailer, OWN outlet), price list,
# credit limit, outstanding, status, sales rep
CUSTOMERS = [
    ("C-PUN-0118", "Annapurna Stores", "Manchester", "MH", "27AAKFA3318C1Z7", "DLR", "DLR", 1000000, 420000, "ACTIVE", "ARAO"),
    ("C-PUN-0021", "Annapurna Stores (old code, do not use)", "Manchester", "MH", "27AAKFA3318C1Z7", "DLR", "DLR", 0, 0,
     "BLOCKED", "ARAO"),
    ("C-NSK-0142", "Annapurna Stores & Traders", "Nashik", "MH", "27AAOFA7102K1Z2", "DLR", "DLR", 600000, 95000,
     "ACTIVE", "ARAO"),
    ("C-HUB-0307", "Annapoorna Stores", "Hubli", "KA", "29AAPFA2290M1Z4", "RTL", "RTL", 200000, 30000, "ACTIVE", "ARAO"),
    ("C-PUN-0090", "Kitchen King Traders", "Manchester", "MH", "27AABFK5521P1Z8", "DLR", "DLR", 1500000, 200000, "ACTIVE", "ARAO"),
    ("C-MUM-0055", "Albion Home Appliances", "Birmingham", "MH", "27AACFM8812Q1Z3", "DST", "DST", 4000000, 1850000,
     "ACTIVE", "SIYER"),
    ("C-AMD-0201", "the Netherlands Kitchenware Distributors", "Rotterdam", "GJ", "24AAGFG4410H1Z6", "DST", "DST", 2500000,
     2410000, "ACTIVE", "SIYER"),
    ("C-KOP-0077", "Irwell Ganesh Bartan Bhandar", "Kolhapur", "MH", "27AAHFS6630B1Z0", "DLR", "DLR", 400000, 0,
     "ACTIVE", "ARAO"),
    ("C-NAG-0019", "Vidarbha Kitchen Mart", "Nagpur", "MH", "27AAEFV1207G1Z5", "DLR", "DLR", 500000, 140000, "ACTIVE", "ARAO"),
    ("C-IDR-0044", "Annapurna Kitchenware", "Indore", "MP", "23AAKFA5531E1Z9", "DST", "DST", 1200000, 310000,
     "ACTIVE", "SIYER"),
    ("C-PUN-0300", "Northbridge factory outlet, Manchester", "Manchester", "MH", None, "OWN", "MRP", 0, 0, "ACTIVE", "ARAO"),
]

# list_cd, itm_cd, rate, valid_from, valid_to. The old dealer price (£1,395) expired on 30 Sep.
PRICES = [
    ("DLR", "PC-SS-05L", 1395.00, "2026-04-01", "2026-09-30"),
    ("DLR", "PC-SS-05L", 1450.00, "2026-10-01", "2027-03-31"),
    ("DST", "PC-SS-05L", 1380.00, "2026-10-01", "2027-03-31"),
    ("RTL", "PC-SS-05L", 1690.00, "2026-10-01", "2027-03-31"),
    ("MRP", "PC-SS-05L", 2350.00, "2026-10-01", "2027-03-31"),
    ("DLR", "PC-AL-05L", 980.00, "2026-04-01", "2027-03-31"),
    ("DST", "PC-AL-05L", 940.00, "2026-04-01", "2027-03-31"),
    ("RTL", "PC-AL-05L", 1150.00, "2026-04-01", "2027-03-31"),
    ("MRP", "PC-AL-05L", 1650.00, "2026-04-01", "2027-03-31"),
    ("DLR", "PC-SS-03L", 1140.00, "2026-04-01", "2026-09-30"),
    ("DLR", "PC-SS-03L", 1180.00, "2026-10-01", "2027-03-31"),
    ("DST", "PC-SS-03L", 1120.00, "2026-10-01", "2027-03-31"),
    ("RTL", "PC-SS-03L", 1390.00, "2026-10-01", "2027-03-31"),
    ("MRP", "PC-SS-03L", 1950.00, "2026-10-01", "2027-03-31"),
    ("DLR", "PC-SS-07L", 1680.00, "2026-04-01", "2026-09-30"),
    ("DLR", "PC-SS-07L", 1720.00, "2026-10-01", "2027-03-31"),
    ("DST", "PC-SS-07L", 1650.00, "2026-10-01", "2027-03-31"),
    ("RTL", "PC-SS-07L", 1990.00, "2026-10-01", "2027-03-31"),
    ("MRP", "PC-SS-07L", 2790.00, "2026-10-01", "2027-03-31"),
]

DISC_LIMITS = [("SAL-EXEC", 2.0), ("SAL-MGR", 5.0), ("PLANT-HEAD", 10.0), ("SYS-ADMIN", 100.0)]

# Past quotations: qtn_no, cust, item, qty, list, rate, disc, tax, basic, tax value, gross, valid_to, status,
# created_by, created_on, approved_by, approved_on, client_ref, remarks
PAST_QTNS = [
    ("QT/2026/01198", "C-PUN-0118", "PC-SS-05L", 400, "DLR", 1395.00, 0, "VAT5-UK", 558000, 66960, 624960,
     "2026-09-25", "CV", "ARAO", "2026-09-10T11:00:00", "ARAO", "2026-09-10T11:00:00", None, "Ganesh festival stock"),
    ("QT/2026/01215", "C-NSK-0142", "PC-SS-03L", 300, "DLR", 1180.00, 2, "VAT5-UK", 346920, 41630.4, 388550.4,
     "2026-10-20", "EX", "ARAO", "2026-10-05T15:20:00", "ARAO", "2026-10-05T15:20:00", None, None),
    ("QT/2026/01224", "C-KOP-0077", "PC-SS-03L", 150, "DLR", 1180.00, 0, "VAT5-UK", 177000, 21240, 198240,
     "2026-11-03", "IS", "ARAO", "2026-10-19T12:10:00", "ARAO", "2026-10-19T12:10:00", None, None),
    ("QT/2026/01226", "C-HUB-0307", "PC-SS-03L", 60, "RTL", 1390.00, 0, "VAT5-RC", 83400, 10008, 93408,
     "2026-11-04", "CV", "ARAO", "2026-10-20T16:00:00", "ARAO", "2026-10-20T16:00:00", None, None),
    ("QT/2026/01229", "C-PUN-0090", "PC-SS-07L", 200, "DLR", 1720.00, 0, "VAT5-UK", 344000, 41280, 385280,
     "2026-11-06", "IS", "ARAO", "2026-10-22T10:05:00", "ARAO", "2026-10-22T10:05:00", None, None),
    ("QT/2026/01236", "C-MUM-0055", "PC-SS-05L", 2000, "DST", 1380.00, 4, "VAT5-UK", 2649600, 317952, 2967552,
     "2026-11-08", "PA", "ARAO", "2026-10-24T17:30:00", None, None, None, "spring-launch scheme, distributor"),
]

# Past orders: ord_no, type, quotation, cust, item, qty, rate, disc, tax, gross, whs, status, created_by,
# created_on, released_on, warn, client_ref
PAST_ORDERS = [
    ("SO/2026/00588", "STD", "QT/2026/01198", "C-PUN-0118", "PC-SS-05L", 400, 1395.00, 0, "VAT5-UK", 624960,
     "WH-PUN-FG", "IN", "ARAO", "2026-09-12T10:00:00", "2026-09-12T16:00:00", None, None),
    ("SO/2026/00601", "CSH", None, "C-PUN-0300", "PC-SS-03L", 40, 1950.00, 0, "VAT5-UK", 87360,
     "WH-PUN-FG", "IN", "ARAO", "2026-10-08T12:00:00", "2026-10-08T12:30:00", None, None),
    ("SO/2026/00604", "STD", "QT/2026/01226", "C-HUB-0307", "PC-SS-03L", 60, 1390.00, 0, "VAT5-RC", 93408,
     "WH-PUN-FG", "IN", "ARAO", "2026-10-20T17:00:00", "2026-10-21T10:00:00", None, None),
    ("SO/2026/00609", "STD", None, "C-AMD-0201", "PC-SS-05L", 600, 1380.00, 0, "VAT5-RC", 927360,
     "WH-PUN-FG", "CH", "SIYER", "2026-10-19T11:40:00", None, "W-SO-114", None),
    ("SO/2026/00613", "STD", None, "C-MUM-0055", "PC-AL-05L", 400, 940.00, 0, "VAT5-UK", 421120,
     "WH-PUN-FG", "RL", "SIYER", "2026-10-21T09:30:00", "2026-10-21T15:00:00", None, None),
]
PAST_DSP = [("SO/2026/00613", "WH-PUN-FG", "PC-AL-05L", 400, "OPEN", "2026-10-21T15:00:00")]

# Finished-goods stock in Manchester. Sales owns these rows; it inserts them only if they are absent.
FG_STOCK = [("PC-SS-05L", "WH-PUN-FG", 3200, 400, 0), ("PC-AL-05L", "WH-PUN-FG", 1500, 400, 0),
            ("PC-SS-03L", "WH-PUN-FG", 2800, 0, 0), ("PC-SS-07L", "WH-PUN-FG", 900, 0, 0)]

READ = ["so_cust_search", "so_cust_get", "so_price_get", "so_qtn_fetch", "so_list", "po_pending_appr", "usr_get",
        "itm_search", "itm_get", "stk_query", "tax_list", "tax_compute"]


def seed(erp):
    add_people(erp, "ARAO", "SIYER")
    add_items(erp, "PC-SS-03L", "PC-SS-05L", "PC-AL-05L", "PC-SS-07L")
    add_locations(erp, "WH-PUN-FG")
    for row in FG_STOCK:
        if not erp.q1("SELECT 1 FROM stock WHERE itm_cd=? AND whs_cd=?", row[0], row[1]):
            erp.x("INSERT INTO stock VALUES (?,?,?,?,?)", *row)
            erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
                  row[0], row[1], "2026-10-01", "OPENING", row[2], "MIGRATION")
    insert(erp, "so_cust", CUSTOMERS)
    insert(erp, "so_price", PRICES)
    insert(erp, "so_disc_lim", DISC_LIMITS)
    insert(erp, "so_qtn", PAST_QTNS)
    insert(erp, "so_ord", PAST_ORDERS)
    erp.db.executemany("INSERT INTO so_dsp(ord_no,whs_cd,itm_cd,qty,status,created_on) VALUES (?,?,?,?,?,?)", PAST_DSP)
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES "
          "('SOQ','QT/2026/01236','SIYER','PENDING','ARAO','2026-10-24T17:30:00')")
    add_seq(erp, "SOQ", "QT/2026/", 1241, 5)
    add_seq(erp, "SOO", "SO/2026/", 618, 5)
    grant(erp, "SAL-EXEC", READ + ["so_qtn_save", "so_ord_save", "so_ord_release", "ntf_send"])
    grant(erp, "SAL-MGR", READ + ["so_qtn_save", "so_ord_save", "so_ord_release", "so_disc_approve", "ntf_send"])
    grant(erp, "PLANT-HEAD", READ + ["so_disc_approve"])
