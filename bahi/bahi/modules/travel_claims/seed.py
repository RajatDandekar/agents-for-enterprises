"""Travel · claims: tables and seed data. Everything is fictional.

Kavita (grade E3) may fly economy to Rajkot (740 km). Tuesday is tomorrow, so a request without the URGENT flag
is the trap: Bahi saves it, rc S, but parks it in the travel desk's next-day batch (status WL). Nobody books it.
"""
from .._kit import add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE tv_grade(grade TEXT PRIMARY KEY, modes TEXT, flt_min_km INT, hotel_a REAL, hotel_b REAL, hotel_c REAL,
  da_a REAL, da_b REAL, da_c REAL);
CREATE TABLE tv_emp(user_id TEXT PRIMARY KEY, grade TEXT);
CREATE TABLE tv_city(city_cd TEXT PRIMARY KEY, name TEXT, state TEXT, cls TEXT, km INT);
CREATE TABLE tv_fare(fare_cd TEXT PRIMARY KEY, from_cd TEXT, to_cd TEXT, mode TEXT, carrier TEXT, dep_dt TEXT,
  dep_tm TEXT, fare REAL, seats INT);
CREATE TABLE tv_trip(trip_no TEXT PRIMARY KEY, user_id TEXT, purpose TEXT, from_cd TEXT, to_cd TEXT, out_dt TEXT,
  back_dt TEXT, mode TEXT, cc_cd TEXT, est_cost REAL, adv_amt REAL, urgent TEXT, status TEXT, approver TEXT,
  saved_by TEXT, saved_on TEXT, decided_on TEXT, warn_cd TEXT, client_ref TEXT);
CREATE TABLE tv_bkg(trip_no TEXT, leg TEXT, fare_cd TEXT, pnr TEXT, fare REAL, status TEXT, booked_by TEXT, booked_on TEXT);
CREATE TABLE tv_claim(claim_no TEXT PRIMARY KEY, trip_no TEXT, hotel_amt REAL, nights INT, local_amt REAL, bills TEXT,
  da_amt REAL, admissible REAL, status TEXT, saved_by TEXT, saved_on TEXT, settled_by TEXT, settled_on TEXT,
  remarks TEXT, client_ref TEXT);
CREATE TABLE tv_pay(claim_no TEXT, user_id TEXT, admissible REAL, adv_adj REAL, net_amt REAL, posted_on TEXT);
"""

# grade, modes allowed, flights only above this distance, hotel cap per night (city class A/B/C), daily allowance A/B/C
GRADES = [
    ("E2", "TRN-2A,TRN-3A,BUS", 99999, 4000, 3000, 2000, 800, 600, 500),
    ("E3", "FLT-Y,TRN-2A,TRN-3A,BUS", 500, 5500, 4000, 2500, 1000, 800, 600),
    ("E4", "FLT-Y,TRN-1A,TRN-2A,BUS", 300, 6500, 5000, 3000, 1200, 1000, 700),
    ("M1", "FLT-Y,TRN-1A,TRN-2A", 0, 8000, 6000, 4000, 1500, 1200, 900),
    ("M2", "FLT-Y,TRN-1A,TRN-2A", 0, 9000, 7000, 4500, 1800, 1500, 1000),
    ("M3", "FLT-J,FLT-Y,TRN-1A", 0, 12000, 9000, 6000, 2500, 2000, 1500),
]
EMP_GRADES = [("KJOSHI", "E3"), ("SKULKARNI", "E4"), ("RMEHTA", "M1"), ("APATIL", "M3"), ("NDESAI", "E2"),
              ("SPILLAI", "E2"), ("VNAIR", "M2")]

# city code, name, state, class, km from Pune
CITIES = [
    ("PUN", "Pune", "MH", "A", 0), ("RJK", "Rajkot", "GJ", "B", 740), ("RJY", "Rajahmundry", "AP", "B", 900),
    ("AMD", "Ahmedabad", "GJ", "A", 660), ("BOM", "Mumbai", "MH", "A", 150), ("BRC", "Vadodara", "GJ", "B", 590),
    ("CCU", "Kolkata", "WB", "A", 1900), ("CHK", "Chakan", "MH", "C", 30),
]

# fare code, from, to, mode, carrier, date, time, fare, seats left
FARES = [
    ("F-RJK-2701", "PUN", "RJK", "FLT-Y", "Vayu Air VA-411", "2026-10-27", "06:40", 6850, 0),  # sold out
    ("F-RJK-2702", "PUN", "RJK", "FLT-Y", "Koel Airways KA-207", "2026-10-27", "11:15", 5920, 9),
    ("F-RJK-2703", "PUN", "RJK", "FLT-J", "Vayu Air VA-411 (business)", "2026-10-27", "06:40", 21400, 4),
    ("F-RJK-2704", "PUN", "RJK", "TRN-2A", "Kathiyawar Link 21188 (2A)", "2026-10-26", "22:10", 2140, 12),
    ("F-RJK-2801", "RJK", "PUN", "FLT-Y", "Vayu Air VA-412", "2026-10-28", "19:30", 6400, 7),
    ("F-RJK-2802", "RJK", "PUN", "FLT-Y", "Koel Airways KA-208", "2026-10-28", "16:05", 6050, 5),
    ("F-RJK-2803", "RJK", "PUN", "FLT-J", "Vayu Air VA-412 (business)", "2026-10-28", "19:30", 20900, 3),
    ("F-RJK-2804", "RJK", "PUN", "TRN-2A", "Kathiyawar Link 21187 (2A)", "2026-10-28", "20:40", 2140, 10),
    ("F-RJY-2701", "PUN", "RJY", "FLT-Y", "Koel Airways KA-519", "2026-10-27", "08:20", 7300, 6),  # near-match
    ("F-RJY-2801", "RJY", "PUN", "FLT-Y", "Koel Airways KA-520", "2026-10-28", "18:10", 7100, 6),
    ("F-BOM-1501", "PUN", "BOM", "TRN-2A", "Bhima Intercity 21124 (2A)", "2026-10-15", "07:15", 410, 0),
    ("F-BOM-1601", "BOM", "PUN", "TRN-2A", "Bhima Intercity 21123 (2A)", "2026-10-16", "17:10", 410, 0),
    ("F-RJK-2008", "PUN", "RJK", "FLT-Y", "Koel Airways KA-207", "2026-08-20", "11:15", 5480, 0),
    ("F-RJK-2108", "RJK", "PUN", "FLT-Y", "Koel Airways KA-208", "2026-08-21", "16:05", 5610, 0),
]

# trip_no, user, purpose, from, to, out, back, mode, cc, est, advance, urgent, status, approver, saved_by, saved_on,
# decided_on, warn, client_ref
TRIPS = [
    ("TRV/2026/00176", "KJOSHI", "Supplier visit, Deccan Polymers", "PUN", "RJK", "2026-08-20", "2026-08-21", "FLT-Y",
     "PRD-05", 13490, 0, "N", "CL", "RMEHTA", "KJOSHI", "2026-08-10T10:00:00", "2026-08-10T15:20:00", None, None),
    ("TRV/2026/00181", "SKULKARNI", "Supplier audit, Kaveri Rubber", "PUN", "CCU", "2026-09-10", "2026-09-11", "FLT-Y",
     "PRD-05", 21800, 0, "N", "CL", "RMEHTA", "SKULKARNI", "2026-09-01T09:40:00", "2026-09-01T12:00:00", None, None),
    ("TRV/2026/00189", "KJOSHI", "Supplier visit, Shree Packaging stockist", "PUN", "AMD", "2026-09-03", "2026-09-04",
     "FLT-Y", "PRD-05", 14200, 0, "N", "BK", "RMEHTA", "KJOSHI", "2026-08-25T11:00:00", "2026-08-25T17:30:00", None, None),
    ("TRV/2026/00198", "KJOSHI", "Supplier visit, Mahalaxmi Steels", "PUN", "BOM", "2026-10-15", "2026-10-16", "TRN-2A",
     "PRD-07", 8320, 5000, "N", "BK", "RMEHTA", "KJOSHI", "2026-10-08T10:15:00", "2026-10-08T16:00:00", None, None),
    ("TRV/2026/00207", "RMEHTA", "Vendor meet, Ahmedabad", "PUN", "AMD", "2026-11-04", "2026-11-05", "FLT-Y",
     "PRD-07", 19500, 0, "N", "PA", "APATIL", "RMEHTA", "2026-10-23T18:00:00", None, None, None),
]
BOOKINGS = [
    ("TRV/2026/00176", "OUT", "F-RJK-2008", "KA6Q2P", 5480, "OK", "SPILLAI", "2026-08-11T10:00:00"),
    ("TRV/2026/00176", "RET", "F-RJK-2108", "KA6Q2P", 5610, "OK", "SPILLAI", "2026-08-11T10:00:00"),
    ("TRV/2026/00198", "OUT", "F-BOM-1501", "4417230981", 410, "OK", "SPILLAI", "2026-10-09T10:00:00"),
    ("TRV/2026/00198", "RET", "F-BOM-1601", "4417230982", 410, "OK", "SPILLAI", "2026-10-09T10:00:00"),
]
CLAIMS = [
    ("TCL/2026/00058", "TRV/2026/00176", 3900, 1, 600, "Y", 1600, 6100, "ST", "KJOSHI", "2026-08-24T09:30:00",
     "VNAIR", "2026-08-28T15:00:00", None, None),
    ("TCL/2026/00061", "TRV/2026/00181", 6400, 1, 900, "Y", 2400, 8900, "ST", "SKULKARNI", "2026-09-14T10:00:00",
     "VNAIR", "2026-09-18T12:00:00", None, None),
]
PAYS = [("TCL/2026/00058", "KJOSHI", 6100, 0, 6100, "2026-08-28T15:00:00"),
        ("TCL/2026/00061", "SKULKARNI", 8900, 0, 8900, "2026-09-18T12:00:00")]

TRAVELLER_SVCS = ["tv_ent_get", "tv_trip_save", "tv_trip_list", "tv_cancel", "tv_fare_list", "tv_claim_save"]


def seed(erp):
    add_people(erp, "SPILLAI", "VNAIR")
    insert(erp, "tv_grade", GRADES)
    insert(erp, "tv_emp", EMP_GRADES)
    insert(erp, "tv_city", CITIES)
    insert(erp, "tv_fare", FARES)
    insert(erp, "tv_trip", TRIPS)
    insert(erp, "tv_bkg", BOOKINGS)
    insert(erp, "tv_claim", CLAIMS)
    insert(erp, "tv_pay", PAYS)
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES "
          "('TV','TRV/2026/00207','APATIL','PENDING','RMEHTA','2026-10-23T18:00:00')")
    add_seq(erp, "TV", "TRV/2026/", 212, 5)
    add_seq(erp, "TVC", "TCL/2026/", 64, 5)
    for role in ("PUR-EXEC", "PUR-SR", "PUR-MGR", "PLANT-HEAD", "STORES", "TRV-DESK", "FIN-CTRL"):
        grant(erp, role, TRAVELLER_SVCS)
    for role in ("PUR-MGR", "PUR-SR", "PLANT-HEAD", "FIN-CTRL"):
        grant(erp, role, ["tv_approve"])
    grant(erp, "TRV-DESK", ["tv_bkg_save", "ntf_send"])
    grant(erp, "FIN-CTRL", ["tv_claim_settle"])
