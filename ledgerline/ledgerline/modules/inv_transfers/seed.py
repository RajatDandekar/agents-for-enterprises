"""Inventory · transfers: tables and seed data. Everything is fictional.

Leeds stores (WH-LDS-STR) holds 12,000 of BAT-500, but lot QC-2610 (4,000) is on QC hold, so only 8,000
is free. Asking for more than the free stock is the trap: Ledgerline does not refuse, it saves the transfer note as
SH (short) and it never goes to a gate pass.
"""
from .._kit import add_locations, add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE tr_note(tn_no TEXT PRIMARY KEY, itm_cd TEXT, qty INT, from_whs TEXT, to_whs TEXT, mv_type TEXT,
  slot TEXT, vehicle TEXT, basic REAL, gross REAL, ewb_no TEXT, status TEXT, approver TEXT, created_by TEXT,
  created_on TEXT, warn_cd TEXT, client_ref TEXT, remarks TEXT);
CREATE TABLE tr_gp(gp_no TEXT PRIMARY KEY, tn_no TEXT, gp_type TEXT, vehicle TEXT, ewb_no TEXT, status TEXT,
  created_by TEXT, created_on TEXT, out_by TEXT, out_on TEXT);
CREATE TABLE tr_rcpt(rc_no TEXT PRIMARY KEY, tn_no TEXT, qty_rcvd INT, rcvd_by TEXT, rcvd_on TEXT, remarks TEXT);
CREATE TABLE tr_ewb(ewb_no TEXT PRIMARY KEY, tn_no TEXT, gen_by TEXT, gen_on TEXT, valid_to TEXT, value REAL);
CREATE TABLE tr_qc_hold(itm_cd TEXT, whs_cd TEXT, lot TEXT, qty INT, reason TEXT, held_on TEXT, release_due TEXT,
  status TEXT);
CREATE TABLE tr_std_rate(itm_cd TEXT PRIMARY KEY, rate REAL, valid_from TEXT);
CREATE TABLE tr_vehicle(veh_no TEXT PRIMARY KEY, descr TEXT, owner TEXT, ou_cd TEXT, capacity_kg INT);
CREATE TABLE tr_route(from_whs TEXT, to_whs TEXT, km INT, transit_hrs REAL);
"""

# tn_no, item, qty, from, to, move type, slot, vehicle, basic, gross, ewb, status, approver, created_by,
# created_on, warn, client_ref, remarks
PAST_NOTES = [
    ("TN/2026/00208", "BAT-500", 3000, "WH-LDS-STR", "WH-PUN-LN5", "IUT", "DAY", "MH-14-GH-2290", 35700, 42126,
     None, "RC", None, "ATANAKA", "2026-10-12T10:05:00", None, None, "Line top-up"),
    ("TN/2026/00209", "MNT-FRM-01", 5000, "WH-MAN-STR", "WH-LDS-STR", "IUT", "DAY", "MH-12-KL-7713", 92500, 109150,
     "271009876543", "RC", None, "ATANAKA", "2026-10-14T11:20:00", None, None, "Leeds assembly"),
    ("TN/2026/00210", "BAT-500", 2500, "WH-LDS-STR", "WH-PUN-LN5", "IUT", "DAY", "MH-14-GH-2290", 29750, 35105,
     None, "RC", None, "ATANAKA", "2026-10-19T09:40:00", None, None, "Line top-up"),
    ("TN/2026/00211", "BAT-500", 6000, "WH-LDS-STR", "WH-MAN-STR", "IUT", "NIGHT", "MH-14-GH-2290", 71400, 84252,
     "271011223344", "RC", "HWEBER", "ATANAKA", "2026-10-21T15:10:00", None, None, "spring-launch run stock"),
    ("TN/2026/00212", "CHG-4A-01", 2000, "WH-MAN-STR", "WH-PUN-LN5", "INT", "DAY", None, 192000, 226560,
     None, "RC", None, "ATANAKA", "2026-10-22T08:30:00", None, None, "Line-side lids"),
    ("TN/2026/00213", "BEL-STD-01", 900, "WH-MAN-STR", "WH-PUN-LN5", "INT", "DAY", None, 6120, 7221.6,
     None, "RC", None, "ATANAKA", "2026-10-23T08:35:00", None, None, "Line-side bells"),
    ("TN/2026/00214", "MNT-RCK-02", 3000, "WH-MAN-STR", "WH-LDS-STR", "IUT", "DAY", "MH-12-KL-7713", 47250, 55755,
     None, "CN", None, "ATANAKA", "2026-10-23T12:00:00", None, None, "Not needed after all"),
    ("TN/2026/00215", "BAT-500-R", 1000, "WH-LDS-STR", "WH-MAN-STR", "IUT", "DAY", None, 6000, 7080,
     None, "AP", None, "GPAWAR", "2026-10-24T16:45:00", None, None, "Rework lot for re-inspection"),
]

# gp_no, tn_no, type, vehicle, ewb, status, created_by, created_on, out_by, out_on
PAST_GPS = [
    ("GP/2026/00718", "TN/2026/00208", "NRGP", "MH-14-GH-2290", None, "OUT", "GPAWAR", "2026-10-12T11:00:00",
     "BSALUNKE", "2026-10-12T11:30:00"),
    ("GP/2026/00721", "TN/2026/00210", "NRGP", "MH-14-GH-2290", None, "OUT", "GPAWAR", "2026-10-19T10:30:00",
     "BSALUNKE", "2026-10-19T11:00:00"),
    ("GP/2026/00726", "TN/2026/00211", "NRGP", "MH-14-GH-2290", "271011223344", "OUT", "GPAWAR",
     "2026-10-21T20:30:00", "BSALUNKE", "2026-10-21T21:15:00"),
    ("GP/2026/00729", None, "RGP", "MH-14-TX-0518", None, "OUT", "GPAWAR", "2026-10-24T10:00:00", "BSALUNKE",
     "2026-10-24T10:20:00"),  # returnable: a battery pack die sent out for polishing
]

# rc_no, tn_no, qty received, by, on, remarks
PAST_RCPTS = [
    ("RC/2026/00208", "TN/2026/00208", 3000, "ATANAKA", "2026-10-12T13:00:00", None),
    ("RC/2026/00209", "TN/2026/00209", 5000, "GPAWAR", "2026-10-14T15:30:00", None),
    ("RC/2026/00210", "TN/2026/00210", 2500, "ATANAKA", "2026-10-19T12:40:00", None),
    ("RC/2026/00211", "TN/2026/00211", 6000, "ATANAKA", "2026-10-21T23:05:00", None),
    ("RC/2026/00212", "TN/2026/00212", 2000, "ATANAKA", "2026-10-22T09:00:00", None),
    ("RC/2026/00213", "TN/2026/00213", 900, "ATANAKA", "2026-10-23T09:05:00", None),
]

# e-way bills that logistics actually generated on the government portal and recorded here
EWBS = [
    ("271009876543", "TN/2026/00209", "GPAWAR", "2026-10-14", "2026-10-15", 109150),
    ("271011223344", "TN/2026/00211", "GPAWAR", "2026-10-21", "2026-10-22", 84252),
    ("271002224466", "TN/2026/00190", "GPAWAR", "2026-09-02", "2026-09-03", 61360),
]

# item, warehouse, lot, qty, reason, held on, release due, status
QC_HOLDS = [
    ("BAT-500", "WH-LDS-STR", "QC-2610", 4000, "Hardness out of spec, lab retest", "2026-10-23", "2026-10-29", "HOLD"),
    ("MNT-FRM-01", "WH-MAN-STR", "QC-2602", 1500, "Flash on moulding", "2026-10-20", "2026-10-30", "HOLD"),
    ("BAT-500", "WH-MAN-STR", "QC-2588", 2000, "Colour variation, accepted", "2026-10-05", "2026-10-09", "RELEASED"),
]

STD_RATES = [("BAT-500", 11.90, "2026-10-01"), ("BAT-500-R", 6.00, "2026-04-01"), ("BAT-375", 9.20, "2026-04-01"),
             ("BAT-750", 14.60, "2026-04-01"), ("MNT-FRM-01", 18.50, "2026-04-01"), ("MNT-RCK-02", 15.75, "2026-04-01"),
             ("BEL-STD-01", 6.80, "2026-04-01"), ("BRK-PAD-01", 9.40, "2026-04-01"), ("CHG-4A-01", 96.00, "2026-04-01"),
             ("BOX-BIKE-01", 21.50, "2026-04-01")]

VEHICLES = [("MH-14-GH-2290", "Tempo, 1.5 t (Leeds shuttle)", "OWN", "NBC-LDS-01", 1500),
            ("MH-12-KL-7713", "Truck, 7 t", "Shivneri Transport", "NBC-MAN-01", 7000),
            ("MH-14-GH-2209", "Tempo, 1.5 t (scrap; not for stores)", "OWN", "NBC-LDS-01", 1500),
            ("MH-14-TX-0518", "Pick-up, 1 t", "OWN", "NBC-LDS-01", 1000)]

ROUTES = [("WH-LDS-STR", "WH-MAN-STR", 32, 1.5), ("WH-LDS-STR", "WH-PUN-LN5", 32, 1.5),
          ("WH-MAN-STR", "WH-LDS-STR", 32, 1.5), ("WH-MAN-STR", "WH-PUN-LN5", 0, 0.25)]

# Stock rows this module owns (inserted only if absent): the city e-bike line-side store, and the rework lot at Leeds.
OWN_STOCK = [("BAT-500", "WH-PUN-LN5", 1500, 0), ("CHG-4A-01", "WH-PUN-LN5", 1800, 0),
             ("BEL-STD-01", "WH-PUN-LN5", 700, 0), ("BAT-500-R", "WH-LDS-STR", 3000, 1000)]

STORES_SVCS = ["tr_stk_enq", "tr_fetch", "tr_save", "tr_list", "tr_gp_create", "tr_receive"]


def seed(erp):
    add_people(erp, "GPAWAR", "BSALUNKE")
    add_locations(erp, "WH-PUN-LN5")
    for itm, whs, oh, alloc in OWN_STOCK:
        if not erp.q1("SELECT 1 FROM stock WHERE itm_cd=? AND whs_cd=?", itm, whs):
            erp.x("INSERT INTO stock VALUES (?,?,?,?,0)", itm, whs, oh, alloc)
            erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
                  itm, whs, "2026-10-01", "OPENING", oh, "MIGRATION")
    insert(erp, "tr_note", PAST_NOTES)
    insert(erp, "tr_gp", PAST_GPS)
    insert(erp, "tr_rcpt", PAST_RCPTS)
    insert(erp, "tr_ewb", EWBS)
    insert(erp, "tr_qc_hold", QC_HOLDS)
    insert(erp, "tr_std_rate", STD_RATES)
    insert(erp, "tr_vehicle", VEHICLES)
    insert(erp, "tr_route", ROUTES)
    add_seq(erp, "TRN", "TN/2026/", 216, 5)
    add_seq(erp, "TRG", "GP/2026/", 731, 5)
    add_seq(erp, "TRR", "RC/2026/", 216, 5)
    grant(erp, "STORES", STORES_SVCS)
    grant(erp, "SECURITY", ["tr_list", "tr_gp_out"])
    for role in ("PUR-MGR", "PLANT-HEAD"):
        grant(erp, role, ["tr_stk_enq", "tr_list", "tr_approve"])
    for role in ("PUR-EXEC", "PUR-SR"):
        grant(erp, role, ["tr_stk_enq", "tr_list"])
